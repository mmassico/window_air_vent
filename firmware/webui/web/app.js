// Window vent web page: live state over a WebSocket, settings and history over HTTP.
// Development: serve this folder from a PC (python -m http.server) and open it with ?host=<the ESP32's address>.
'use strict';

const qs = new URLSearchParams(location.search);
const HOST = qs.get('host') || location.host;
const API = qs.get('host') ? 'http://' + HOST : '';
const $ = (id) => document.getElementById(id);
const DEG = '\u00b0';

// Theme: auto (the system's), light or dark; remembered by the browser.
let theme = 'auto';
try { theme = localStorage.getItem('theme') || 'auto'; } catch (e) { /* private mode */ }
function applyTheme() {
  if (theme === 'auto') document.documentElement.removeAttribute('data-theme');
  else document.documentElement.setAttribute('data-theme', theme);
  document.querySelectorAll('#themeSeg button').forEach((b) => b.classList.toggle('on', b.dataset.theme === theme));
}
applyTheme();

// Colours: the theme's accent and status colours, each one overridable here (kept by this browser).
const COLOURS = [
  ['--accent', 'Accent'], ['--accent2', 'Fans, open line'], ['--good', 'Good, comfortable'], ['--fair', 'Fair, dry, loud'],
  ['--poor', 'Stuffy'], ['--bad', 'High CO\u2082, maximum'], ['--warm', 'Indoor curve, simulation'], ['--cold', 'Outdoor curve, cool'],
  ['--wet', 'Humid'],
];
let colours = {};
try { colours = JSON.parse(localStorage.getItem('colours') || '{}'); } catch (e) { /* private mode */ }
function applyColours() {
  for (const [v] of COLOURS) {
    if (colours[v]) document.documentElement.style.setProperty(v, colours[v]);
    else document.documentElement.style.removeProperty(v);
  }
}
applyColours();

let S = null;               // the last live state
let settings = null;        // being edited
let saved = null;           // as saved on the device
let ws = null;

// ------------------------------------------------------------------------------------------------
// Small helpers
// ------------------------------------------------------------------------------------------------

const clone = (o) => JSON.parse(JSON.stringify(o));
const fmt = (v, d = 0) => (v === null || v === undefined || isNaN(v)) ? '--' : Number(v).toFixed(d);
const getKey = (o, k) => k.split('.').reduce((a, p) => (a ? a[p] : undefined), o);
function setKey(o, k, v) {
  const p = k.split('.');
  let a = o;
  for (let i = 0; i < p.length - 1; i++) a = a[p[i]] = a[p[i]] || {};
  a[p[p.length - 1]] = v;
}
const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
// Change the page only where a value really changed: rewriting identical text still makes the browser lay it out again.
function setText(el, v) { v = String(v); if (el.textContent !== v) el.textContent = v; }
function setHtml(el, v) { if (el._html !== v) { el._html = v; el.innerHTML = v; } }
const hhmm = (m) => String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');

let toastTimer;
function toast(msg) {
  const t = $('toast');
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.hidden = true), 2600);
}

function send(o) {
  if (ws && ws.readyState === 1) ws.send(JSON.stringify(o));
  else fetch(API + '/api/cmd', { method: 'POST', body: JSON.stringify(o) }).catch(() => toast('Not connected'));
}

// ------------------------------------------------------------------------------------------------
// Tabs
// ------------------------------------------------------------------------------------------------

function showTab() {
  const t = (location.hash || '#dash').slice(1);
  document.querySelectorAll('.tab').forEach((s) => (s.hidden = s.id !== 'tab-' + t));
  document.querySelectorAll('.tabs a').forEach((a) => a.classList.toggle('on', a.dataset.tab === t));
  if (t === 'dash') charts.forEach((c) => fitChart(c));
  if (t === 'settings') drawCurve();
}
window.addEventListener('hashchange', showTab);

// ------------------------------------------------------------------------------------------------
// Slider fields: <div class="field" data-min data-max data-step data-unit data-label>
// ------------------------------------------------------------------------------------------------

function paint(r) {
  r.style.setProperty('--p', ((r.value - r.min) / (r.max - r.min)) * 100 + '%');
}

function buildField(el, onChange) {
  const { min, max, step, unit = '', label = '' } = el.dataset;
  el.innerHTML = '<label></label><div class="val"><input type="number"><span class="unit"></span></div><input type="range">';
  el.querySelector('label').innerHTML = label;
  el.querySelector('.unit').innerHTML = unit;
  const num = el.querySelector('input[type=number]');
  const rng = el.querySelector('input[type=range]');
  for (const i of [num, rng]) { i.min = min; i.max = max; i.step = step; }
  paint(rng);
  const dec = (step.split('.')[1] || '').length;
  const clamp = (v) => Math.min(+max, Math.max(+min, v));
  rng.addEventListener('input', () => { num.value = (+rng.value).toFixed(dec); paint(rng); onChange(+rng.value, false); });
  rng.addEventListener('change', () => onChange(+rng.value, true));
  num.addEventListener('change', () => {
    const v = clamp(+num.value);
    num.value = v.toFixed(dec);
    rng.value = v;
    paint(rng);
    onChange(v, true);
  });
  el.setValue = (v) => {
    if (v === null || v === undefined) return;
    if (document.activeElement === num || el.dragging) return;
    num.value = (+v).toFixed(dec);
    rng.value = v;
    paint(rng);
  };
  rng.addEventListener('pointerdown', () => (el.dragging = true));
  window.addEventListener('pointerup', () => (el.dragging = false));
}

// ------------------------------------------------------------------------------------------------
// Settings
// ------------------------------------------------------------------------------------------------

function settingsChanged() {
  $('saveBar').hidden = JSON.stringify(settings) === JSON.stringify(saved);
  drawCurve();
}

function fillSettings() {
  document.querySelectorAll('#tab-settings [data-key]').forEach((el) => {
    const v = getKey(settings, el.dataset.key);
    if (el.classList.contains('field')) el.setValue(v);
    else if (el.type === 'checkbox') el.checked = !!v;
    else if (el.dataset.time !== undefined) el.value = hhmm(v || 0);
    else el.value = v === undefined ? '' : v;
  });
  $('motorRev').checked = settings.damper.motorDir < 0;
  settingsChanged();
}

function initSettings() {
  document.querySelectorAll('#tab-settings [data-key]').forEach((el) => {
    const key = el.dataset.key;
    if (el.classList.contains('field')) {
      buildField(el, (v) => { setKey(settings, key, v); settingsChanged(); });
    } else if (el.type === 'checkbox') {
      el.addEventListener('change', () => { setKey(settings, key, el.checked); settingsChanged(); });
    } else if (el.dataset.time !== undefined) {
      el.addEventListener('change', () => {
        const [h, m] = el.value.split(':').map(Number);
        setKey(settings, key, h * 60 + m);
        settingsChanged();
      });
    } else {
      el.addEventListener('input', () => { setKey(settings, key, el.value); settingsChanged(); });
    }
  });
  $('motorRev').addEventListener('change', () => { settings.damper.motorDir = $('motorRev').checked ? -1 : 1; settingsChanged(); });
  $('revertBtn').onclick = () => { settings = clone(saved); fillSettings(); };
  $('saveBtn').onclick = async () => {
    try {
      const r = await fetch(API + '/api/settings', { method: 'POST', body: JSON.stringify(settings) });
      if (!r.ok) throw new Error();
      saved = await r.json();
      settings = clone(saved);       // the device may have clamped some values
      fillSettings();
      toast('Saved');
    } catch (e) {
      toast('Not saved: no answer');
    }
  };
}

async function loadSettings() {
  for (;;) {
    try {
      const r = await fetch(API + '/api/settings');
      saved = await r.json();
      settings = clone(saved);
      fillSettings();
      return;
    } catch (e) {
      await new Promise((ok) => setTimeout(ok, 3000));
    }
  }
}

// ------------------------------------------------------------------------------------------------
// CO2 curve editor (SVG)
// ------------------------------------------------------------------------------------------------

const CV = { w: 640, h: 304, l: 44, r: 16, t: 54, b: 30, x0: 400 };
let curveDrag = -1;

function cvX1() { return Math.max(2000, settings ? settings.co2.maxPpm + 200 : 2000); }
function cvPx(ppm) { return CV.l + ((ppm - CV.x0) / (cvX1() - CV.x0)) * (CV.w - CV.l - CV.r); }
function cvPy(pct) { return CV.h - CV.b - (pct / 100) * (CV.h - CV.t - CV.b); }
function cvPpm(px) { return CV.x0 + ((px - CV.l) / (CV.w - CV.l - CV.r)) * (cvX1() - CV.x0); }
function cvPct(py) { return ((CV.h - CV.b - py) / (CV.h - CV.t - CV.b)) * 100; }

function drawCurve() {
  const svg = $('curve');
  if (!settings || !svg || $('tab-settings').hidden) return;
  const c = settings.co2, x1 = cvX1();
  svg.setAttribute('viewBox', `0 0 ${CV.w} ${CV.h}`);
  let h = '<g class="grid">';
  for (let p = 400; p <= x1; p += 200) h += `<line x1="${cvPx(p)}" x2="${cvPx(p)}" y1="${CV.t}" y2="${CV.h - CV.b}"/>`;
  for (let q = 0; q <= 100; q += 25) h += `<line x1="${CV.l}" x2="${CV.w - CV.r}" y1="${cvPy(q)}" y2="${cvPy(q)}"/>`;
  h += '</g><g class="axis">';
  for (let p = 400; p <= x1; p += 400) h += `<text x="${cvPx(p)}" y="${CV.h - 10}" text-anchor="middle">${p}</text>`;
  for (let q = 0; q <= 100; q += 25) h += `<text x="${CV.l - 8}" y="${cvPy(q) + 4}" text-anchor="end">${q}%</text>`;
  h += '</g>';
  h += `<rect class="band" x="${cvPx(c.targetLo)}" y="${CV.t}" width="${Math.max(0, cvPx(c.targetHi) - cvPx(c.targetLo))}" height="${CV.h - CV.t - CV.b}"/>`;
  // threshold lines, labels on two rows when they come close (left to right)
  const th = [['close', c.closePpm, 'close'], ['open', c.openPpm, 'open'], ['max', c.maxPpm, 'maximum']]
    .map(([cls, v, lab]) => [cls, cvPx(v), lab]).sort((a, b) => a[1] - b[1]);
  // lines first, then every label over them
  let prevX = -1e9, prevRow = 1, labels = '';
  for (const [cls, x, lab] of th) {
    const row = x - prevX < 60 && prevRow === 0 ? 1 : 0;
    const y = row ? CV.t - 34 : CV.t - 20;     // clear of a point at 100 %
    prevX = x;
    prevRow = row;
    h += `<line class="th ${cls}" x1="${x}" x2="${x}" y1="${y + 3}" y2="${CV.h - CV.b}"/>`;
    labels += `<text class="th-label" x="${x}" y="${y}" text-anchor="middle" fill="${cls === 'max' ? cssVar('--bad') : cls === 'open' ? cssVar('--accent2') : cssVar('--muted')}">${lab}</text>`;
  }
  const pts = c.curvePpm.map((p, i) => [cvPx(p), cvPy(c.curvePct[i])]);
  const line = [[cvPx(CV.x0), pts[0][1]], ...pts, [cvPx(x1), pts[pts.length - 1][1]]];
  const d = line.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
  h += `<path class="area" d="${d} L${cvPx(x1)} ${cvPy(0)} L${cvPx(CV.x0)} ${cvPy(0)} Z"/>`;
  h += `<path class="line" d="${d}"/>`;
  h += labels;
  pts.forEach((p, i) => (h += `<circle class="pt${i === curveDrag ? ' drag' : ''}" data-i="${i}" cx="${p[0]}" cy="${p[1]}" r="7"/>`));
  // the present CO2 reading, over everything: a guide down to the axis and a dot on the curve
  if (S && S.in.co2 !== null && S.out.curve !== null) {
    const x = cvPx(Math.min(x1, Math.max(CV.x0, S.in.co2))), y = cvPy(S.out.curve);
    h += `<line class="now-guide" x1="${x}" x2="${x}" y1="${y}" y2="${CV.h - CV.b}"/>`;
    h += `<circle class="now" cx="${x}" cy="${y}" r="5"><title>now: ${S.in.co2} ppm</title></circle>`;
  }
  if (curveDrag >= 0) {
    const [x, y] = pts[curveDrag];
    const right = x > CV.w - 140;
    h += `<text class="tip" x="${x + (right ? -14 : 14)}" y="${y - 12}" text-anchor="${right ? 'end' : 'start'}">${c.curvePpm[curveDrag]} ppm, ${c.curvePct[curveDrag]} %</text>`;
  }
  svg.innerHTML = h;
}

function initCurve() {
  const svg = $('curve');
  const toSvg = (e) => {
    const r = svg.getBoundingClientRect();
    return [((e.clientX - r.left) / r.width) * CV.w, ((e.clientY - r.top) / r.height) * CV.h];
  };
  svg.addEventListener('pointerdown', (e) => {
    if (!e.target.classList.contains('pt')) return;
    curveDrag = +e.target.dataset.i;
    svg.setPointerCapture(e.pointerId);
    drawCurve();
  });
  svg.addEventListener('pointermove', (e) => {
    if (curveDrag < 0) return;
    const [x, y] = toSvg(e);
    const c = settings.co2, i = curveDrag;
    const lo = i ? c.curvePpm[i - 1] + 10 : CV.x0;
    const hi = i < c.curvePpm.length - 1 ? c.curvePpm[i + 1] - 10 : cvX1();
    c.curvePpm[i] = Math.round(Math.min(hi, Math.max(lo, cvPpm(x))) / 10) * 10;
    c.curvePct[i] = Math.round(Math.min(100, Math.max(0, cvPct(y))));
    settingsChanged();
  });
  const end = () => { if (curveDrag >= 0) { curveDrag = -1; drawCurve(); } };
  svg.addEventListener('pointerup', end);
  svg.addEventListener('pointercancel', end);
}

// ------------------------------------------------------------------------------------------------
// Charts (uPlot): history from /api/history, then a point per live state
// ------------------------------------------------------------------------------------------------

// D.t holds the vent's history clock (seconds): real time, or model time while the simulation runs faster. The graphs
// draw each point at "now" minus its age on that clock, so at x1 they show the real time of day.
const D = { t: [], co2: [], fan: [], tin: [], tout: [], rh: [], snd: [] };
let clockNow = 0;
const charts = [];
let rangeH = 6;
try { rangeH = +(localStorage.getItem('rangeH') || 6); } catch (e) { /* private mode */ }

function fitChart(u) {
  const w = u.root.parentElement.clientWidth;
  if (w > 0) u.setSize({ width: w, height: u.height });
}

function axisStyle() {
  return { stroke: cssVar('--muted'), grid: { stroke: cssVar('--line'), width: 1 }, ticks: { stroke: cssVar('--line') } };
}

function makeCharts() {
  const acc = cssVar('--accent'), acc2 = cssVar('--accent2'), warm = cssVar('--warm'), cold = cssVar('--cold');
  const band = cssVar('--good');
  const w = $('chartCo2').clientWidth || 600;
  const targetBand = (u) => {
    if (!settings) return;
    const y0 = u.valToPos(settings.co2.targetHi, 'ppm', true), y1 = u.valToPos(settings.co2.targetLo, 'ppm', true);
    u.ctx.save();
    u.ctx.fillStyle = band + '22';
    u.ctx.fillRect(u.bbox.left, y0, u.bbox.width, y1 - y0);
    u.ctx.restore();
  };
  const co2 = new uPlot({
    width: w, height: 230,
    cursor: { drag: { x: false, y: false } },
    scales: { x: { time: true }, ppm: { range: (u, lo, hi) => [Math.min(400, lo ?? 400), Math.max(1200, (hi ?? 1200) + 50)] }, pct: { range: [0, 100] } },
    series: [
      {},
      { label: 'CO\u2082', scale: 'ppm', stroke: acc, width: 2, value: (u, v) => (v == null ? '--' : v.toFixed(0) + ' ppm') },
      { label: 'Fans', scale: 'pct', stroke: acc2, width: 1, fill: acc2 + '26', paths: uPlot.paths.stepped({ align: 1 }), value: (u, v) => (v == null ? '--' : v.toFixed(0) + ' %') },
    ],
    axes: [{ ...axisStyle() }, { ...axisStyle(), scale: 'ppm', size: 50 }, { ...axisStyle(), scale: 'pct', side: 1, grid: { show: false }, size: 44, values: (u, v) => v.map((x) => x + '%') }],
    hooks: { drawAxes: [targetBand] },
  }, [D.t, D.co2, D.fan], $('chartCo2'));
  const temp = new uPlot({
    width: w, height: 200,
    cursor: { drag: { x: false, y: false } },
    scales: { x: { time: true }, C: { range: (u, lo, hi) => [Math.floor((lo ?? 0) - 1), Math.ceil((hi ?? 25) + 1)] }, pct: { range: [0, 100] } },
    series: [
      {},
      { label: 'Indoor', scale: 'C', stroke: warm, width: 2, value: (u, v) => (v == null ? '--' : v.toFixed(1) + ' ' + DEG + 'C') },
      { label: 'Outdoor', scale: 'C', stroke: cold, width: 2, value: (u, v) => (v == null ? '--' : v.toFixed(1) + ' ' + DEG + 'C') },
      { label: 'Humidity', scale: 'pct', stroke: cssVar('--muted'), width: 1, dash: [4, 4], value: (u, v) => (v == null ? '--' : v.toFixed(0) + ' %') },
    ],
    axes: [{ ...axisStyle() }, { ...axisStyle(), scale: 'C', size: 50, values: (u, v) => v.map((x) => x + DEG) }, { ...axisStyle(), scale: 'pct', side: 1, grid: { show: false }, size: 44, values: (u, v) => v.map((x) => x + '%') }],
  }, [D.t, D.tin, D.tout, D.rh], $('chartTemp'));
  const snd = new uPlot({
    width: w, height: 160,
    cursor: { drag: { x: false, y: false } },
    scales: { x: { time: true }, dB: { range: (u, lo, hi) => [Math.min(30, Math.floor((lo ?? 30) / 10) * 10), Math.max(80, Math.ceil((hi ?? 80) / 10) * 10)] } },
    series: [
      {},
      { label: 'Outdoor sound', scale: 'dB', stroke: cssVar('--poor'), width: 1.5, value: (u, v) => (v == null ? '--' : v.toFixed(0) + ' dB') },
    ],
    axes: [{ ...axisStyle() }, { ...axisStyle(), scale: 'dB', size: 50 }],
  }, [D.t, D.snd], $('chartSnd'));
  charts.push(co2, temp, snd);
}

function rebuildCharts() {
  charts.splice(0).forEach((u) => u.destroy());
  makeCharts();
  redrawCharts();
}

function redrawCharts() {
  if (!charts.length || $('tab-dash').hidden) return;
  const now = Date.now() / 1000;
  const x = D.t.map((c) => now - (clockNow - c));
  charts[0].setData([x, D.co2, D.fan], false);
  charts[1].setData([x, D.tin, D.tout, D.rh], false);
  if (!$('chartSnd').hidden) charts[2].setData([x, D.snd], false);
  for (const u of charts) if (!u.root.parentElement.hidden) u.setScale('x', { min: now - rangeH * 3600, max: now });
}

function pushPoint(t, co2, fan, tin, tout, rh, snd) {
  D.t.push(t); D.co2.push(co2); D.fan.push(fan); D.tin.push(tin); D.tout.push(tout); D.rh.push(rh); D.snd.push(snd);
  const cut = t - 24 * 3600;
  let n = 0;
  while (n < D.t.length && D.t[n] < cut) n++;
  if (n) for (const k in D) D[k].splice(0, n);
}

async function loadHistory() {
  try {
    const r = await fetch(API + '/api/history');
    const buf = await r.arrayBuffer();
    const v = new DataView(buf);
    const count = v.getUint32(0, true), size = v.getUint32(12, true);
    clockNow = Math.max(clockNow, v.getUint32(8, true));
    const val = (o, k) => { const x = v.getInt16(o, true); return x === -32768 ? null : x / k; };
    for (const k in D) D[k].length = 0;
    for (let i = 0; i < count; i++) {
      const o = 16 + i * size;
      pushPoint(v.getUint32(o, true), val(o + 4, 1), v.getUint8(o + 14), val(o + 6, 10), val(o + 8, 10), val(o + 10, 10), val(o + 12, 10));
    }
    redrawCharts();
  } catch (e) {
    setTimeout(loadHistory, 5000);
  }
}

// ------------------------------------------------------------------------------------------------
// Live state
// ------------------------------------------------------------------------------------------------

const LIMITS = [
  [1, 'Cold outside'], [2, 'Too cold: closed'], [4, 'Warmer outside'], [8, 'Free cooling'], [16, 'Quiet hours'],
  [32, 'Loud outside'], [64, 'CO\u2082 maximum'], [128, 'No CO\u2082 reading'], [256, 'Holding'], [512, 'Room cool'],
];

function co2Level(v) {
  if (v === null) return ['--', cssVar('--muted')];
  if (v <= 800) return ['Good', cssVar('--good')];
  if (v <= 1000) return ['Fair', cssVar('--fair')];
  if (v <= 1400) return ['Stuffy', cssVar('--poor')];
  return ['High', cssVar('--bad')];
}

function arcPath(f0, f1) {
  const p = (f) => {
    const a = Math.PI * (1 - f);
    return [100 + 80 * Math.cos(a), 110 - 80 * Math.sin(a)];
  };
  const [x0, y0] = p(f0), [x1, y1] = p(f1);
  return `M${x0.toFixed(1)} ${y0.toFixed(1)} A80 80 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
}

function kv(el, rows) {
  setHtml(el, rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join(''));
}

function uptime(s) {
  const d = Math.floor(s / 86400), h = Math.floor(s / 3600) % 24, m = Math.floor(s / 60) % 60;
  return (d ? d + ' d ' : '') + h + ' h ' + String(m).padStart(2, '0') + ' min';
}

function onState(s) {
  S = s;
  $('simBadge').hidden = !s.sim.on;
  setText($('clock'), s.time ? s.time.slice(11, 16) : '');
  $('clock').hidden = !s.time;

  // mode
  document.querySelectorAll('#modeSeg button').forEach((b) => b.classList.toggle('on', b.dataset.mode === s.mode));
  setText($('boostLeft'), s.mode === 'boost' ? Math.ceil(s.boostLeft / 60) + ' min' : '');
  $('manualCard').hidden = s.mode !== 'manual';

  // CO2 gauge: 400 to 2000 ppm over the half circle
  const co2 = s.in.co2;
  const f = (v) => Math.min(1, Math.max(0, (v - 400) / 1600));
  const [lab, col] = co2Level(co2);
  setText($('co2'), fmt(co2));
  setText($('co2Label'), lab);
  $('co2Label').style.color = col;
  $('gArc').setAttribute('d', co2 === null ? '' : arcPath(0, Math.max(0.005, f(co2))));
  $('gArc').style.stroke = col;
  if (settings) $('gBand').setAttribute('d', arcPath(f(settings.co2.targetLo), f(settings.co2.targetHi)));
  const a = Math.PI * (1 - f(co2 ?? 400));
  $('gDot').setAttribute('cx', 100 + 80 * Math.cos(a));
  $('gDot').setAttribute('cy', 110 - 80 * Math.sin(a));
  setText($('reason'), s.out.reason.replace(/CO2/g, 'CO\u2082'));
  // limits as chips; "loud outside" shows in the sound tile instead
  setHtml($('limits'), LIMITS.filter(([b]) => b !== 32 && s.out.limits & b).map(([, t]) => `<span class="chip on">${t}</span>`).join(''));
  $('sndChip').hidden = !(s.out.limits & 32);

  // tiles
  setText($('tin'), fmt(s.in.tin, 1));
  setText($('rh'), fmt(s.in.rh));
  // humidity: its own tile when the sound tile is there too (an even count), else inside the indoor tile
  const sound = s.hw.audio || s.sim.on;
  $('rhTile').hidden = !sound;
  $('rhInline').hidden = sound;
  if (settings) {                                     // temperature bar: blue below the target range, green in it, yellow above
    const t = settings.temp, lo = t.tinMin - 6, hi = t.tinMax + 6;
    const pos = (v) => Math.min(100, Math.max(0, ((v - lo) / (hi - lo)) * 100));
    const a = pos(t.tinMin), b = pos(t.tinMax);
    setText($('tinSub'), 'Target: ' + fmt(t.tinMin) + ' to ' + fmt(t.tinMax) + ' ' + DEG + 'C');
    $('tinBar').title = fmt(lo) + ' to ' + fmt(hi) + ' ' + DEG + 'C';
    $('tinBar').style.background = `linear-gradient(90deg, color-mix(in srgb, ${cssVar('--cold')} 60%, transparent) 0 ${a}%, `
      + `color-mix(in srgb, ${cssVar('--good')} 60%, transparent) ${a}% ${b}%, color-mix(in srgb, ${cssVar('--fair')} 60%, transparent) ${b}% 100%)`;
    if (s.in.tin !== null) {
      $('tinMark').style.left = pos(s.in.tin) + '%';
      $('tinMark').style.background = s.in.tin < t.tinMin ? cssVar('--cold') : s.in.tin > t.tinMax ? cssVar('--fair') : cssVar('--good');
    }
  }
  if (s.in.rh !== null) {
    const [word, col] = s.in.rh < 30 ? ['Dry', cssVar('--fair')] : s.in.rh > 60 ? ['Humid', cssVar('--wet')] : ['Comfortable', cssVar('--good')];
    const left = Math.min(100, Math.max(0, s.in.rh)) + '%';
    for (const id of ['rhWord', 'rhInWord']) { setText($(id), word); $(id).style.color = col; }
    for (const id of ['rhMark', 'rhInMark']) { $(id).style.left = left; $(id).style.background = col; }
    setText($('rhIn'), fmt(s.in.rh));
    let dew = '';
    if (s.in.tin !== null && s.in.rh > 0) {           // dew point (Magnus formula)
      const g = Math.log(s.in.rh / 100) + (17.62 * s.in.tin) / (243.12 + s.in.tin);
      dew = ', dew point ' + fmt((243.12 * g) / (17.62 - g), 1) + ' ' + DEG + 'C';
    }
    setText($('rhDew'), dew);
  }
  setText($('tout'), fmt(s.in.tout, 1));
  setText($('toutSub'), s.in.tout !== null && s.in.tin !== null
    ? (s.in.tout >= s.in.tin ? fmt(s.in.tout - s.in.tin, 1) + ' ' + DEG + 'C warmer' : fmt(s.in.tin - s.in.tout, 1) + ' ' + DEG + 'C cooler')
    : '\u00a0');
  const openDeg = settings ? settings.damper.openDeg : 90;
  const ang = s.damper.angle;
  $('dDisc').style.transform = `rotate(${90 - (ang ?? 0) * (90 / openDeg)}deg)`;
  setText($('dState'), s.damper.fault ? 'Fault' : ang === null ? 'No encoder'
    : s.damper.moving ? (s.damper.target > ang ? 'Opening' : 'Closing') : ang > openDeg / 2 ? 'Open' : 'Closed');
  setText($('dAngle'), ang === null ? '--' : fmt(ang) + DEG + (s.damper.moving ? ' \u2192 ' + fmt(s.damper.target) + DEG : ''));
  setText($('fan'), fmt(s.out.fan));
  setText($('rpm0'), s.fans[0].rpm);
  setText($('rpm1'), s.fans[1].rpm);
  $('fanBar').style.width = s.out.fan + '%';
  $('sndTile').hidden = !sound;
  if ($('chartSnd').hidden === sound) {
    $('chartSnd').hidden = !sound;
    if (sound && charts[2]) fitChart(charts[2]);
  }
  setText($('snd'), fmt(s.in.snd));
  if (settings) {                                     // sound bar: 30 to 100 dB, green to the threshold, yellow above
    const n = settings.noise, pos = (v) => Math.min(100, Math.max(0, ((v - 30) / 70) * 100));
    const th = pos(n.db), loud = s.in.snd !== null && s.in.snd >= n.db;
    setText($('sndSub'), 'Threshold: ' + fmt(n.db) + ' dB' + (n.enabled ? '' : ' (control off)'));
    $('sndBar').style.background = `linear-gradient(90deg, color-mix(in srgb, ${cssVar('--good')} 60%, transparent) 0 ${th}%, `
      + `color-mix(in srgb, ${cssVar('--fair')} 60%, transparent) ${th}% 100%)`;
    if (s.in.snd !== null) {
      $('sndMark').style.left = pos(s.in.snd) + '%';
      $('sndMark').style.background = loud ? cssVar('--fair') : cssVar('--good');
    }
  }
  if (settings && !$('manualCard').hidden) {
    $('manOpen').checked = settings.mode.manualOpen;
    $('manPct').setValue(settings.mode.manualPct);
  }

  // charts: a point per state, on the history clock
  if (s.clock < clockNow - 5) {               // the vent restarted: its clock began again
    clockNow = s.clock;
    loadHistory();
  } else if (s.clock > clockNow || !D.t.length) {
    clockNow = s.clock;
    pushPoint(s.clock, s.in.co2, s.out.fan, s.in.tin, s.in.tout, s.in.rh, s.in.snd);
    redrawCharts();
  }
  if (!$('tab-settings').hidden && curveDrag < 0) drawCurve();

  // developer
  $('simOn').checked = s.sim.on;
  document.querySelectorAll('#simModeSeg button').forEach((b) => b.classList.toggle('on', +b.dataset.model === (s.sim.model ? 1 : 0)));
  document.querySelectorAll('#simSpeedSeg button').forEach((b) => b.classList.toggle('on', +b.dataset.speed === s.sim.speed));
  $('simSpeedRow').hidden = !s.sim.model;
  document.querySelectorAll('.field.sim').forEach((el) => {
    el.setValue(s.sim[el.dataset.sim]);
    const off = !s.sim.on || (el.dataset.manual !== undefined && s.sim.model) || (el.dataset.model !== undefined && !s.sim.model);
    el.classList.toggle('disabled', off);
  });
  kv($('outKv'), [
    ['Mode', s.mode + (s.bootMode !== s.mode ? ' (then ' + s.bootMode + ')' : '')],
    ['CO\u2082 curve', fmt(s.out.curve) + ' %'],
    ['Demand', fmt(s.out.demand) + ' %'],
    ['Fans', fmt(s.out.fan) + ' %: intake ' + s.fans[0].pct + ' % (duty ' + s.fans[0].duty + '), exhaust ' + s.fans[1].pct + ' % (duty ' + s.fans[1].duty + ')'],
    ['Damper', (s.out.open ? 'open' : 'closed') + ', ' + fmt(s.damper.angle, 1) + DEG + ' (target ' + fmt(s.damper.target) + DEG + ')'],
  ]);
  const chip = (ok, t) => `<span class="chip ${ok ? 'ok' : 'no'}">${t}</span>`;
  setHtml($('hwChips'), chip(s.hw.scd, 'SCD40') + chip(s.hw.enc, 'AS5600') + chip(s.hw.magnet, 'magnet') + chip(s.hw.tmc, 'TMC2209')
    + chip(s.hw.tout, 'DS18B20 out') + (s.hw.audio ? chip(s.hw.mic, 'microphone') : chip(s.hw.tin, 'DS18B20 in')));
  kv($('hwKv'), [
    ['12 V supply', fmt(s.hw.v12, 1) + ' V'],
    ['Encoder', s.hw.enc ? s.hw.encRaw + ' raw, ' + fmt(s.hw.hwAngle, 1) + DEG : '--'],
    ['Loop, longest', fmt(s.sys.loopMaxMs, 1) + ' ms'],
    ['Free memory', Math.round(s.sys.heap / 1024) + ' kB RAM, ' + Math.round(s.sys.psram / 1048576 * 10) / 10 + ' MB PSRAM'],
  ]);
  if (s.log && s.log.length) {
    const el = $('log');
    const atEnd = el.scrollTop + el.clientHeight >= el.scrollHeight - 4;
    el.textContent += s.log.join('\n') + '\n';
    if (el.textContent.length > 20000) el.textContent = el.textContent.slice(-15000);
    if (atEnd) el.scrollTop = el.scrollHeight;
  }

  // system
  kv($('netKv'), [
    ['Network', s.net.ssid || '(none)'],
    ['Status', s.net.sta ? 'joined, ' + s.net.rssi + ' dBm' : s.net.ap ? 'setup network open' : 'not joined'],
    ['Address', s.net.ip ? `<a href="http://${s.net.ip}/">${s.net.ip}</a>` : '--'],
    ['Name', `<a href="http://${s.net.host}.local/">${s.net.host}.local</a>`],
    ['Pages open', s.net.clients],
  ]);
  kv($('sysKv'), [
    ['Firmware', 'window-vent webui ' + s.sys.ver],
    ['Local time', s.time || 'not set (no NTP yet)'],
    ['Up for', uptime(s.uptime)],
    ['Audio mode', s.hw.audio ? 'yes (microphone on GPIO 3)' : 'no'],
  ]);
}

// ------------------------------------------------------------------------------------------------
// WebSocket
// ------------------------------------------------------------------------------------------------

function connect() {
  const conn = $('conn');
  ws = new WebSocket('ws://' + HOST + '/ws');
  ws.onopen = () => { conn.textContent = 'Live'; conn.className = 'badge ok'; };
  ws.onclose = () => {
    conn.textContent = 'Offline';
    conn.className = 'badge err';
    setTimeout(connect, 2000);
  };
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.type === 'state') onState(m);
    else if (m.type === 'error') toast(m.msg);
  };
}

// ------------------------------------------------------------------------------------------------
// Start
// ------------------------------------------------------------------------------------------------

function init() {
  document.querySelectorAll('#modeSeg button').forEach((b) => (b.onclick = () => send({ cmd: 'mode', mode: b.dataset.mode })));
  document.querySelectorAll('#rangeSeg button').forEach((b) => {
    b.classList.toggle('on', +b.dataset.h === rangeH);
    b.onclick = () => {
      rangeH = +b.dataset.h;
      try { localStorage.setItem('rangeH', rangeH); } catch (e) { /* private mode */ }
      document.querySelectorAll('#rangeSeg button').forEach((x) => x.classList.toggle('on', x === b));
      redrawCharts();
    };
  });

  buildField($('manPct'), (v, done) => {
    if (!done) return;
    settings.mode.manualPct = saved.mode.manualPct = v;
    send({ cmd: 'manual', pct: v });
  });
  $('manOpen').addEventListener('change', () => {
    settings.mode.manualOpen = saved.mode.manualOpen = $('manOpen').checked;
    send({ cmd: 'manual', open: $('manOpen').checked });
  });

  initSettings();
  initCurve();

  // developer: simulation
  let simTimer = null, simPending = {};
  document.querySelectorAll('.field.sim').forEach((el) => buildField(el, (v) => {
    simPending[el.dataset.sim] = v;
    if (!simTimer) simTimer = setTimeout(() => { send({ cmd: 'sim', ...simPending }); simPending = {}; simTimer = null; }, 120);
  }));
  $('simOn').addEventListener('change', () => send({ cmd: 'sim', on: $('simOn').checked }));
  document.querySelectorAll('#simModeSeg button').forEach((b) => (b.onclick = () => send({ cmd: 'sim', model: b.dataset.model === '1' })));
  document.querySelectorAll('#simSpeedSeg button').forEach((b) => (b.onclick = () => send({ cmd: 'sim', speed: +b.dataset.speed })));
  $('encZeroBtn').onclick = () => { if (confirm('Take the damper\'s present position as closed (0' + DEG + ')?')) send({ cmd: 'encZero' }); };

  // system
  if (API) $('setupLink').href = API + '/setup';
  $('forgetBtn').onclick = () => { if (confirm('Erase the Wi-Fi network? The setup network opens at the next restart.')) send({ cmd: 'forgetWifi' }); };
  $('rebootBtn').onclick = () => { if (confirm('Restart the vent controller?')) send({ cmd: 'reboot' }); };

  document.querySelectorAll('#themeSeg button').forEach((b) => (b.onclick = () => {
    theme = b.dataset.theme;
    try { localStorage.setItem('theme', theme); } catch (e) { /* private mode */ }
    applyTheme();
    rebuildCharts();
    drawCurve();
  }));
  applyTheme();
  const palette = $('palette');
  const repaint = () => { rebuildCharts(); drawCurve(); if (S) onState(S); };
  const saveColours = () => { try { localStorage.setItem('colours', JSON.stringify(colours)); } catch (e) { /* private mode */ } };
  palette.innerHTML = COLOURS.map(([v, lab]) => `<label class="swatch"><input type="color" data-var="${v}"><span>${lab}</span></label>`).join('');
  const fillPalette = () => palette.querySelectorAll('input').forEach((i) => (i.value = cssVar(i.dataset.var)));
  fillPalette();
  palette.querySelectorAll('input').forEach((i) => i.addEventListener('input', () => {
    colours[i.dataset.var] = i.value;
    applyColours();
    saveColours();
    repaint();
  }));
  $('resetColours').onclick = () => { colours = {}; saveColours(); applyColours(); fillPalette(); repaint(); };
  $('saveColours').onclick = async () => {          // the full set, defaults included, so another browser gets them all
    const all = {};
    for (const [v] of COLOURS) all[v] = cssVar(v);
    try {
      const r = await fetch(API + '/api/ui', { method: 'POST', body: JSON.stringify({ colours: all }) });
      toast(r.ok ? 'Colours saved on the vent' : 'Not saved');
    } catch (e) {
      toast('Not saved: no answer');
    }
  };
  $('loadColours').onclick = async () => {
    try {
      const ui = await (await fetch(API + '/api/ui')).json();
      if (!ui.colours) { toast('No colours saved on the vent yet'); return; }
      colours = {};
      for (const [v] of COLOURS) if (/^#[0-9a-f]{6}$/i.test(ui.colours[v] || '')) colours[v] = ui.colours[v];
      saveColours();
      applyColours();
      fillPalette();
      repaint();
      toast('Colours loaded from the vent');
    } catch (e) {
      toast('Not loaded: no answer');
    }
  };
  matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => { if (theme === 'auto') rebuildCharts(); });

  makeCharts();
  let chartW = 0;                                     // refit on width changes only (a legend rewrapping changes the height)
  new ResizeObserver(() => {
    const w = $('chartCo2').clientWidth;
    if (w !== chartW) { chartW = w; charts.forEach(fitChart); }
  }).observe($('chartCo2'));
  showTab();
  loadSettings();
  loadHistory();
  connect();
}

init();
