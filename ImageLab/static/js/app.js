const $ = (s) => document.querySelector(s);
const state = { tools: [], tool: null, file: null, params: {}, originalUrl: null, resultUrl: null, controller: null, timer: null };

async function init() {
  const res = await fetch("/api/tools");
  state.tools = await res.json();
  renderTools();
  selectTool(state.tools[0].id);
}

function renderTools() {
  const nav = $("#tools");
  nav.innerHTML = "";
  state.tools.forEach((t) => {
    const b = document.createElement("button");
    b.className = "tool";
    b.dataset.id = t.id;
    b.textContent = t.name;
    b.onclick = () => selectTool(t.id);
    nav.appendChild(b);
  });
}

function selectTool(id) {
  state.tool = state.tools.find((t) => t.id === id);
  document.querySelectorAll(".tool").forEach((b) => b.classList.toggle("active", b.dataset.id === id));
  $("#toolName").textContent = state.tool.name;
  $("#toolDesc").textContent = state.tool.description;
  resetParams();
}

function resetParams() {
  state.params = Object.fromEntries(state.tool.params.map((p) => [p.name, p.default]));
  renderControls();
  schedule(0);
}

function renderControls() {
  const box = $("#controls");
  box.innerHTML = "";
  state.tool.params.forEach((p) => {
    const field = document.createElement("div");
    field.className = "field";
    const label = document.createElement("label");
    const val = document.createElement("span");
    label.textContent = p.label;
    let input;

    if (p.type === "select") {
      input = document.createElement("select");
      p.options.forEach((o) => input.add(new Option(o, o)));
      input.value = p.default;
    } else if (p.type === "bool") {
      input = document.createElement("input");
      input.type = "checkbox";
      input.checked = p.default;
    } else {
      input = document.createElement("input");
      input.type = "range";
      input.min = p.min;
      input.max = p.max;
      input.step = p.step ?? 1;
      input.value = p.default;
      val.textContent = p.default;
    }

    input.addEventListener("input", () => {
      let v = input.type === "checkbox" ? input.checked : input.value;
      if (p.type === "int") v = parseInt(v, 10);
      if (p.type === "float") v = parseFloat(v);
      state.params[p.name] = v;
      if (input.type === "range") val.textContent = v;
      schedule();
    });

    label.append(val);
    field.append(label, input);
    box.append(field);
  });
}

function schedule(delay = 200) {
  clearTimeout(state.timer);
  state.timer = setTimeout(process, delay);
}

async function process() {
  if (!state.file || !state.tool) return;
  state.controller?.abort();
  const controller = (state.controller = new AbortController());

  const form = new FormData();
  form.append("file", state.file);
  form.append("params", JSON.stringify(state.params));
  $("#status").textContent = "processing...";

  try {
    const res = await fetch(`/api/process/${state.tool.id}`, { method: "POST", body: form, signal: controller.signal });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(typeof err.detail === "string" ? err.detail : "Invalid request");
    }
    const blob = await res.blob();
    if (state.resultUrl) URL.revokeObjectURL(state.resultUrl);
    state.resultUrl = URL.createObjectURL(blob);
    $("#result").src = state.resultUrl;
    $("#status").textContent = "";
    $("#downloadBtn").disabled = false;
  } catch (e) {
    if (e.name === "AbortError") return;
    $("#status").textContent = "";
    toast(e.message);
  }
}

function loadFile(file) {
  if (!file.type.startsWith("image/")) return toast("Please choose an image file");
  if (file.size > 10 * 1024 * 1024) return toast("Image too large (max 10 MB)");
  state.file = file;
  if (state.originalUrl) URL.revokeObjectURL(state.originalUrl);
  state.originalUrl = URL.createObjectURL(file);
  $("#original").src = state.originalUrl;
  $("#dropzone").hidden = true;
  $("#viewer").hidden = false;
  $("#changeBtn").hidden = false;
  $("#resetBtn").disabled = false;
  schedule(0);
}

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 3000);
}

$("#browse").onclick = () => $("#file").click();
$("#changeBtn").onclick = () => $("#file").click();
$("#file").onchange = (e) => e.target.files[0] && loadFile(e.target.files[0]);
$("#resetBtn").onclick = resetParams;
$("#downloadBtn").onclick = () => {
  const a = document.createElement("a");
  a.href = state.resultUrl;
  a.download = `${state.tool.id}.png`;
  a.click();
};

["dragenter", "dragover"].forEach((ev) =>
  window.addEventListener(ev, (e) => { e.preventDefault(); document.body.classList.add("dragging"); }));
["dragleave", "drop"].forEach((ev) =>
  window.addEventListener(ev, (e) => { e.preventDefault(); document.body.classList.remove("dragging"); }));
window.addEventListener("drop", (e) => e.dataTransfer.files[0] && loadFile(e.dataTransfer.files[0]));
window.addEventListener("paste", (e) => e.clipboardData.files[0] && loadFile(e.clipboardData.files[0]));

// ---------- compare slider ----------
const compare = $("#compare");
let dragging = false;

function setPos(clientX) {
  const r = compare.getBoundingClientRect();
  const p = Math.min(100, Math.max(0, ((clientX - r.left) / r.width) * 100));
  compare.style.setProperty("--pos", p + "%");
}
compare.addEventListener("pointerdown", (e) => {
  if (compare.classList.contains("side")) return;
  dragging = true;
  compare.setPointerCapture(e.pointerId);
  setPos(e.clientX);
});
compare.addEventListener("pointermove", (e) => dragging && setPos(e.clientX));
compare.addEventListener("pointerup", () => (dragging = false));

function setMode(side) {
  compare.classList.toggle("side", side);
  $("#modeSlider").classList.toggle("active", !side);
  $("#modeSide").classList.toggle("active", side);
}
$("#modeSlider").onclick = () => setMode(false);
$("#modeSide").onclick = () => setMode(true);

// ---------- histograms ----------
function histogram(img) {
  const c = document.createElement("canvas");
  c.width = img.naturalWidth;
  c.height = img.naturalHeight;
  const ctx = c.getContext("2d");
  ctx.drawImage(img, 0, 0);
  const d = ctx.getImageData(0, 0, c.width, c.height).data;   // RGBA
  const h = new Array(256).fill(0);
  for (let i = 0; i < d.length; i += 4) {
    h[Math.round(0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2])]++;
  }
  return h;
}

function stats(h) {
  const n = h.reduce((a, v) => a + v, 0);
  const mean = h.reduce((a, v, k) => a + k * v, 0) / n;
  const sd = Math.sqrt(h.reduce((a, v, k) => a + v * (k - mean) ** 2, 0) / n);
  return `μ ${mean.toFixed(0)} · σ ${sd.toFixed(0)}`;
}

function drawHist(canvas, h) {
  const ctx = canvas.getContext("2d");
  const { width: w, height: ht } = canvas;
  ctx.clearRect(0, 0, w, ht);
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent");
  const max = Math.max(...h);
  const bw = w / 256;
  h.forEach((v, k) => {
    const bh = (v / max) * (ht - 4);
    ctx.fillRect(k * bw, ht - bh, bw, bh);
  });
}

function updateHist(img, canvas, statEl) {
  const h = histogram(img);
  drawHist(canvas, h);
  statEl.textContent = stats(h);
}
$("#original").addEventListener("load", () => updateHist($("#original"), $("#histOrig"), $("#statOrig")));
$("#result").addEventListener("load", () => updateHist($("#result"), $("#histRes"), $("#statRes")));
init();
