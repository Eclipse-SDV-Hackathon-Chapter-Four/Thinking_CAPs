// Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2 (Zenoh input)
// Developed mainly with Claude (Anthropic), model Claude Fable 5.1.
// Created: 2026-10-06 · Latest version: 2026-10-07 (v2.1: console views + SOVD gateway block for the PR #40 contract)
// Goal: Page logic: polls the console API, renders both diagnostic paths, the gateway block, the signal workflow, the topology, the log and the runner.
/* Page logic: polls the console API (vehicle, sovd, faults, auto, stats, health) and the proxied
   CDA, renders both diagnostic paths, the vehicle link, the gateway block with its bridge,
   the automatic DTC, the topology, the log and the runner. No framework. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const CHECKS_N = 13;
  const S = { cfg: null, health: {}, docker: null, stats: null, link: null, speed: null, f1: null, sovd: null, auto: null,
    autoSeq: null, autoFlash: 0, bridgeSeq: null, bridgeFlash: 0, logSeq: 0, run: null, selCheck: null };

  // ------------------------------------------------------------ http
  async function call(url, opts = {}, ms = 1500) {
    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), ms);
    try {
      const r = await fetch(url, { cache: "no-store", signal: ctl.signal, ...opts });
      let json = null;
      const ct = r.headers.get("content-type") || "";
      if (ct.includes("json")) { try { json = await r.json(); } catch (_) { json = null; } }
      return { ok: r.ok, status: r.status, json };
    } catch (e) {
      return { ok: false, status: 0, json: null, error: e.name === "AbortError" ? "timeout" : String(e) };
    } finally { clearTimeout(t); }
  }
  const post = (url, body, ms = 4000) => call(url, { method: "POST", headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined }, ms);

  // ------------------------------------------------------------ status byte
  const BITS = ["testFailed", "testFailedThisOperationCycle", "pendingDTC", "confirmedDTC",
    "testNotCompletedSinceLastClear", "testFailedSinceLastClear", "testNotCompletedThisOperationCycle", "warningIndicatorRequested"];
  const SNAKE = ["test_failed", "test_failed_this_operation_cycle", "pending_dtc", "confirmed_dtc",
    "test_not_completed_since_last_clear", "test_failed_since_last_clear", "test_not_completed_this_operation_cycle", "warning_indicator_requested"];
  const WORDS = ["failing", "failed this cycle", "pending", "confirmed", "not completed since clear", "failed since clear", "not completed this cycle", "warning indicator"];
  function decode(status) {
    let raw = null;
    if (typeof status === "number") raw = status & 0xff;
    else if (typeof status === "string") { const n = parseInt(status.replace(/^0x/i, ""), 16); raw = isNaN(n) ? null : n & 0xff; }
    else if (status && typeof status === "object") {
      if (typeof status.mask === "string") { const n = parseInt(status.mask.replace(/^0x/i, ""), 16); raw = isNaN(n) ? null : n & 0xff; }
      if (raw === null) { raw = 0; SNAKE.forEach((k, i) => { if (status[k] || status[BITS[i]]) raw |= 1 << i; }); }
    }
    const set = BITS.map((_, i) => raw !== null && !!((raw >> i) & 1));
    return { raw, hex: raw === null ? "—" : "0x" + raw.toString(16).toUpperCase().padStart(2, "0"), set,
      summary: set.some(Boolean) ? WORDS.filter((_, i) => set[i]).join(", ") : "no bits set" };
  }
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  function bitStrip(d) {
    return `<div class="bits">${BITS.map((n, i) => `<span class="${d.set[7 - i] ? "on" : ""}" title="bit ${7 - i}: ${BITS[7 - i]}">b${7 - i}</span>`).join("")}</div>`;
  }
  function faultCard(code, name, status, extra, badge, cls) {
    const d = decode(status);
    const klass = cls !== undefined ? cls : (d.set[0] ? "failing" : "");
    return `<div class="fault ${klass}"><div class="head"><span class="code">${esc(code)}${badge ? ` <em class="badge">${esc(badge)}</em>` : ""}</span><span class="hex">${d.hex}</span></div>
      <div class="name">${esc(name || "")}${extra ? " · " + esc(extra) : ""}</div>${bitStrip(d)}<div class="summary">${esc(d.summary)}</div></div>`;
  }
  const fmtAge = (ms) => ms === null || ms === undefined ? "—" : ms < 1000 ? `${ms} ms ago` : `${(ms / 1000).toFixed(1)} s ago`;
  const STAGE_CLS = { passed: "ok", prefailed: "warn", failed: "bad", prepassed: "warn" };
  const STATE_CLS = { active: "ok", standby: "warn", unavailable: "bad" };

  // ------------------------------------------------------------ signal workflow (bottom-left block)
  // Derives events from state transitions of what the page already polls: link, speed, F1 monitor,
  // gateway fault status, tester faults, automation, CDA fault memory. Nothing is stored server-side.
  const flow = (() => {
    const F = { link: undefined, moving: undefined, deb: undefined, gw: undefined, cruise: undefined, faults: null, dtcs: null,
      unack: 0, buf: [], audio: null, pending: 0, WIN_S: 40, MAX: 80, lastDraw: 0 };
    const stamp = () => { const t = new Date(); return t.toTimeString().slice(0, 8) + "." + String(t.getMilliseconds()).padStart(3, "0"); };
    function add(kind, msg, cls = "") {
      const box = $("events");
      if (box.firstElementChild && box.firstElementChild.classList.contains("empty")) box.innerHTML = "";
      const row = document.createElement("div");
      row.className = `ev ${kind} ${cls}`.trim();
      row.innerHTML = `<span class="t">${stamp()}</span><span class="k">${esc(kind)}</span><span class="m" title="${esc(msg)}">${esc(msg)}</span>`;
      box.prepend(row);
      while (box.children.length > F.MAX) box.removeChild(box.lastChild);
    }
    const step = (id, text, cls) => { const el = $(id); el.querySelector("span").textContent = text; el.className = "step" + (cls ? " " + cls : "") + (id === "st-dtc" && F.unack ? " alarm" : ""); };
    const arrows = (on) => document.querySelectorAll(".step-arrow").forEach((a) => a.classList.toggle("on", on));

    // --- sound. Browsers allow audio only after a user gesture on the page: every click or key
    // unlocks the AudioContext, an alarm raised before that is played as soon as it is unlocked.
    const soundOn = () => $("flow-sound").checked;
    function soundState() {
      const el = $("sound-state"), ac = F.audio;
      let cls = "off", txt = "off";
      if (!window.AudioContext) { txt = "not available"; }
      else if (!soundOn()) { txt = "off"; }
      else if (ac && ac.state === "running") { cls = "ok"; txt = F.pending ? "playing…" : "ready"; }
      else { cls = "warn"; txt = F.pending ? "ALARM WAITING · click the page" : "click the page once to enable"; }
      el.className = "sound-state " + cls; el.textContent = txt;
    }
    function unlock() {
      if (!window.AudioContext) return soundState();
      if (!F.audio) { try { F.audio = new AudioContext(); } catch (_) { F.audio = null; return soundState(); } }
      const ac = F.audio;
      if (ac.state !== "running") ac.resume().then(() => { soundState(); if (F.pending && soundOn()) { F.pending = 0; tone("alarm"); } }).catch(() => { });
      soundState();
    }
    function tone(kind) {
      const ac = F.audio;
      if (!ac || ac.state !== "running") return false;
      const notes = kind === "alarm" ? [[880, 0], [1320, 0.15], [880, 0.45], [1320, 0.6]] : [[880, 0], [1320, 0.12]];
      const t0 = ac.currentTime + 0.02, gain = kind === "alarm" ? 0.3 : 0.15;
      for (const [hz, at] of notes) {
        const o = ac.createOscillator(), g = ac.createGain();
        o.type = "square"; o.frequency.value = hz;
        g.gain.setValueAtTime(0.0001, t0 + at);
        g.gain.exponentialRampToValueAtTime(gain, t0 + at + 0.015);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + at + 0.14);
        o.connect(g).connect(ac.destination); o.start(t0 + at); o.stop(t0 + at + 0.15);
      }
      return true;
    }
    function beep() {
      if (!soundOn()) return;
      unlock();
      if (!tone("alarm")) F.pending++;
      soundState();
    }
    function ack() {
      if (!F.unack) return;
      F.unack = 0; F.pending = 0; $("dtc-count").hidden = true;
      document.querySelectorAll(".ev.new").forEach((e) => e.classList.remove("new"));
      $("st-dtc").classList.remove("alarm");
      $("flow-meta").textContent = "DTCs acknowledged";
      soundState();
    }
    function alarm(msg) {
      F.unack++;
      const c = $("dtc-count"); c.textContent = F.unack; c.hidden = false;
      $("st-dtc").classList.add("alarm");
      $("flow-meta").textContent = `${F.unack} DTC${F.unack > 1 ? "s" : ""} failing in the ECU · click step 5 or press A`;
      add("dtc", msg, "new");
      beep();
    }

    // --- scope: sweep display (like a patient monitor). One screen = WIN_S seconds, the trace stays
    // in place and only the cursor moves. Lane 1: samples/s of the vehicle link. Lane 2: speed in km/h.
    function sample(sp, link) {
      const now = performance.now() / 1000;
      F.buf.push({ t: now, v: sp && typeof sp.value === "number" && !sp.stale ? sp.value : null,
        rate: link && typeof link.rate_hz === "number" ? link.rate_hz : null, live: !!(link && link.state === "live") });
      while (F.buf.length && now - F.buf[0].t > F.WIN_S - 1.2) F.buf.shift();
    }
    function draw() {
      const cv = $("scope"), w = cv.clientWidth, h = cv.clientHeight;
      if (!w || !h) return;
      const dpr = window.devicePixelRatio || 1;
      if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
      const g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
      const now = performance.now() / 1000, W = F.WIN_S, x = (t) => ((t % W) / W) * w;
      const pad = 8, lane1 = { top: 16, h: Math.round(h * 0.3) }, lane2 = { top: lane1.top + lane1.h + 18, h: h - (lane1.top + lane1.h + 18) - pad };
      const mono = "11px Consolas, 'Cascadia Mono', Menlo, monospace";
      g.strokeStyle = "rgba(255,255,255,.07)"; g.lineWidth = 1;
      for (let s = 0; s < W; s += 10) { const gx = Math.round((s / W) * w) + 0.5; g.beginPath(); g.moveTo(gx, 0); g.lineTo(gx, h); g.stroke(); }
      [lane1, lane2].forEach((l) => { g.beginPath(); g.moveTo(0, l.top + l.h + 0.5); g.lineTo(w, l.top + l.h + 0.5); g.stroke(); });
      const rates = F.buf.map((p) => p.rate).filter((r) => typeof r === "number"), speeds = F.buf.map((p) => p.v).filter((v) => typeof v === "number");
      const rMax = Math.max(20, Math.ceil(Math.max(0, ...rates) / 10) * 10), vMax = Math.max(10, Math.ceil(Math.max(0, ...speeds) / 10) * 10);
      const bw = Math.max(2, (0.3 / W) * w);
      for (const p of F.buf) {
        const bx = x(p.t);
        if (p.live && typeof p.rate === "number") { g.fillStyle = "#3fb36f"; const bh = Math.max(2, (Math.min(p.rate, rMax) / rMax) * lane1.h); g.fillRect(bx, lane1.top + lane1.h - bh, bw, bh); }
        else { g.fillStyle = "#e2553f"; g.fillRect(bx, lane1.top + lane1.h - 3, bw, 3); }
      }
      g.strokeStyle = "#3fa9a9"; g.lineWidth = 2.5; g.lineJoin = "round"; g.beginPath();
      let prevX = -1, pen = false;
      for (const p of F.buf) {
        if (typeof p.v !== "number") { pen = false; continue; }
        const px = x(p.t), py = lane2.top + lane2.h - (p.v / vMax) * lane2.h;
        if (pen && px >= prevX) g.lineTo(px, py); else g.moveTo(px, py);
        pen = true; prevX = px;
      }
      g.stroke();
      const cx = x(now);
      g.fillStyle = "#222d3b"; g.fillRect(cx, 0, Math.max(6, (1.2 / W) * w), h);
      g.fillStyle = "#eef2f6"; g.fillRect(cx, 0, 2, h);
      const last = F.buf[F.buf.length - 1];
      g.font = mono; g.textAlign = "left"; g.fillStyle = "#7f8ea0";
      g.fillText(`signal  ${last && last.live && typeof last.rate === "number" ? last.rate.toFixed(0) + " samples/s" : "no samples"}  · scale ${rMax}/s`, pad, 12);
      g.fillText(`speed  ${last && typeof last.v === "number" ? last.v.toFixed(1) + " km/h" : "stale"}  · scale ${vMax} km/h`, pad, lane2.top - 5);
      g.textAlign = "right"; g.fillText(`${W} s`, w - pad, 12);
    }
    function frame(ts) {
      if (ts - F.lastDraw > 90) { F.lastDraw = ts; draw(); }
      requestAnimationFrame(frame);
    }

    // --- observers, one per poller
    function onLink(link, err) {
      const st = link ? link.state : (err || "no answer");
      const cls = st === "live" ? "ok" : st === "lost" || st === "error" || !link ? "bad" : "warn";
      step("st-signal", link ? (st === "live" ? `LIVE · ${Math.round(link.rate_hz)}/s` : st.toUpperCase()) : st, cls);
      arrows(st === "live");
      if (F.link === undefined) { F.link = st; add("signal", `page connected · vehicle link ${st}${link ? ` · ${link.samples} samples so far` : ""}`, "base"); return; }
      if (st === F.link) return;
      const msg = { live: `samples arriving again · ${link ? Math.round(link.rate_hz) : "?"}/s`, lost: `no sample for > ${link ? link.timeout_ms : "?"} ms · link LOST`,
        waiting: "connected to the vehicle, no sample yet", connecting: "looking for the vehicle" }[st] || `link ${st}`;
      add("signal", msg, st === "lost" || st === "error" ? "bad" : "");
      F.link = st;
    }
    function onSpeed(sp, link) {
      const v = sp && typeof sp.value === "number" && !sp.stale ? sp.value : null;
      sample(sp, link);
      const moving = v === null ? null : v > 0.5;
      step("st-speed", !sp ? "no answer" : sp.value === null ? "no value" : `${sp.value.toFixed(1)} km/h${sp.stale ? " STALE" : moving ? "" : " · stopped"}`,
        !sp || sp.value === null ? "bad" : sp.stale ? "warn" : "ok");
      if (moving === null) return;
      if (F.moving === undefined) { F.moving = moving; return; }
      if (moving !== F.moving) add("speed", moving ? `vehicle moving · ${v.toFixed(1)} km/h` : "vehicle stopped");
      F.moving = moving;
    }
    function onMonitor(f1, link, gwFault) {
      const armed = link && link.monitor_armed;
      const gs = gwFault ? gwFault.status : null;
      step("st-monitor", `F1 ${f1.state} ${f1.counter}/${f1.threshold} · gateway ${gs || "?"}${armed ? " · F2 armed" : ""}`,
        f1.state === "FAILED" || gs === "failed" ? "bad" : f1.state === "PASSED" && (gs === "passed" || !gs) ? "ok" : "warn");
      if (F.deb === undefined) F.deb = f1.state;
      else if (f1.state !== F.deb) { add("monitor", `F1 ${F.deb} → ${f1.state}${f1.last_reason && f1.state !== "PASSED" ? ` · ${f1.last_reason}` : ""}`, f1.state === "FAILED" ? "bad" : ""); F.deb = f1.state; }
      if (gs) {
        if (F.gw === undefined) F.gw = gs;
        else if (gs !== F.gw) { add("monitor", `gateway ${gwFault.fault || "fault"} ${F.gw} → ${gs}`, gs === "failed" ? "bad" : ""); F.gw = gs; }
      }
    }
    function onCruise(state) {
      if (!state) return;
      if (F.cruise === undefined) F.cruise = state;
      else if (state !== F.cruise) { add("monitor", `cruise_state ${F.cruise} → ${state}`, state === "unavailable" ? "bad" : ""); F.cruise = state; }
    }
    function onBridge(events) {
      for (const e of events) add("auto", `console → gateway: PUT speed_sensor_stuck ${e.stuck} (${e.reason})` + (e.ok ? ` · ${e.status} in ${e.ms} ms` : ` · FAILED: ${e.error}`), e.ok ? "" : "bad");
    }
    function onScoreFaults(items) {
      const now = {};
      items.forEach((f) => { now[f.code] = { stage: f.stage, q: !!f.qualified_failed, hex: decode(f.status).hex, avail: f.available !== false }; });
      const failing = Object.entries(now).filter(([, d]) => d.q).map(([c]) => c);
      const pre = Object.entries(now).filter(([, d]) => !d.q && d.stage === "prefailed").map(([c]) => c);
      step("st-fault", failing.length ? `${failing.join(" + ")} failed` : pre.length ? `${pre.join(" + ")} prefailed` : `none failing · ${items.length} known`,
        failing.length ? "bad" : pre.length ? "warn" : "ok");
      if (F.faults === null) { F.faults = now; return; }
      for (const [code, d] of Object.entries(now)) {
        const was = F.faults[code];
        if (!was) { add("fault", `${code} reported · ${d.stage} · status ${d.hex}`, d.q ? "bad" : ""); continue; }
        if (was.stage === d.stage && was.hex === d.hex && was.avail === d.avail) continue;
        if (d.q && !was.q) add("fault", `${code} qualified FAILED · status ${d.hex}`, "bad");
        else if (!d.q && was.q) add("fault", `${code} healed · ${d.stage} · status ${d.hex}${d.hex !== "0x00" ? " (stored)" : ""}`);
        else if (d.stage !== was.stage) add("fault", `${code} ${was.stage} → ${d.stage} · status ${d.hex}`, d.stage === "prefailed" ? "" : "");
        else if (!d.avail && was.avail) add("fault", `${code}: source not readable (gateway down?)`, "bad");
        else add("fault", `${code} status ${was.hex} → ${d.hex}`);
      }
      for (const code of Object.keys(F.faults)) if (!now[code]) add("fault", `${code} cleared`);
      F.faults = now;
    }
    function onAuto(events) {
      for (const e of events) add("auto", e.change === "reset" ? "reset · fault memory, switch and ECU memory cleared" :
        `console → ECU: ${e.fault} ${e.change} → DTC ${e.dtc} 0x${e.mask}` + (e.ok ? ` · read back ${e.readback} via CDA in ${e.readback_ms} ms` : ` · FAILED: ${e.error}`), e.ok ? "" : "bad");
    }
    function onDtcs(active) {
      const now = {};
      active.forEach((f) => { now[String(f.display_code || f.code).toUpperCase()] = decode(f.status); });
      const codes = Object.keys(now), failing = codes.filter((c) => now[c].set[0]);
      step("st-dtc", codes.length ? `${failing.length} failing · ${codes.length} stored · ${codes.join(" ")}` : "none stored", failing.length ? "bad" : codes.length ? "warn" : "ok");
      if (F.dtcs === null) { F.dtcs = now; if (codes.length) add("dtc", `ECU memory at start: ${codes.map((c) => `${c} ${now[c].hex}`).join(", ")}`, "base"); return; }
      for (const [code, d] of Object.entries(now)) {
        const was = F.dtcs[code];
        if (d.set[0] && !(was && was.set[0])) alarm(`DTC ${code} FAILING in the ECU memory · ${d.hex} ${d.summary} · via CDA`);
        else if (!was) add("dtc", `DTC ${code} stored in the ECU memory · ${d.hex} ${d.summary}`);
        else if (was.raw !== d.raw) add("dtc", `DTC ${code} status ${was.hex} → ${d.hex}${d.set[0] ? "" : " · no longer failing, stays stored"}`);
      }
      for (const code of Object.keys(F.dtcs)) if (!now[code]) add("dtc", `DTC ${code} cleared from the ECU memory`);
      F.dtcs = now;
    }
    function onReset() { add("info", "reset requested from the page"); }
    function init() {
      $("st-dtc").onclick = ack;
      for (const ev of ["pointerdown", "keydown", "touchstart"]) document.addEventListener(ev, unlock, true);
      $("flow-sound").addEventListener("change", () => { if (soundOn()) { unlock(); tone("test"); } soundState(); });
      unlock();
      requestAnimationFrame(frame);
    }
    return { onLink, onSpeed, onMonitor, onCruise, onBridge, onScoreFaults, onAuto, onDtcs, onReset, ack, init, add };
  })();

  // ------------------------------------------------------------ pollers
  function loop(fn, ms) { (async function tick() { try { await fn(); } catch (_) { } setTimeout(tick, ms); })(); }

  async function pollHealth() {
    const r = await call("/api/health");
    S.health = r.json || {};
    for (const svc of ["sovd", "cda", "sim"]) {
      const h = S.health[svc], el = document.querySelector(`.pill[data-svc="${svc}"]`);
      const cls = !h ? "unknown" : h.up ? (svc === "cda" && !h.token ? "warn" : "up") : "down";
      el.className = "pill " + cls;
      el.querySelector("b").textContent = !h ? "—" : h.up ? `${Math.round(h.ms)} ms` : (h.status ? `HTTP ${h.status}` : "down");
      el.title = h ? (h.error || (svc === "cda" && h.token_error ? "token: " + h.token_error : "") || (svc === "sovd" && h.base_uri ? `SOVD ${h.sovd_version} · ${h.base_uri}` : "")) : "";
    }
    renderTopo();
  }
  async function pollDocker() {
    const r = await call("/api/docker", {}, 6000);
    S.docker = r.json;
    const el = $("docker"), d = S.docker;
    if (!d || !d.available) { el.className = "pill unknown"; el.querySelector("b").textContent = "n/a"; el.title = (d && d.error) || ""; }
    else {
      const exp = Object.entries(d.expected_running || {});
      el.className = "pill " + (exp.every(([, v]) => v) ? "up" : "down");
      el.querySelector("b").textContent = exp.length ? `${exp.filter(([, v]) => v).length}/${exp.length}` : "ok";
      el.title = d.containers.map((c) => `${c.name}: ${c.state}`).join("\n") || "no containers";
    }
    renderTopo();
  }
  async function pollStats() {
    const r = await call("/api/stats");
    S.stats = r.json;
    const s = S.stats, rates = (s && s.rates) || {};
    $("r-sovd").textContent = "sovd_requests" in rates ? `${rates.sovd_requests.toFixed(1)}/s` : "—";
    $("stats-meta").textContent = !s || !s.ok ? `counters: ${s && s.error ? s.error : "no data"}` :
      "counters: " + ["vehicle_samples", "gateway_polls", "bridge_writes"].filter((k) => k in rates).map((k) => `${k} ${rates[k].toFixed(1)}/s`).join(" · ") + (s.cycle_error ? ` · ERROR ${s.cycle_error}` : "");
  }
  async function pollVehicle() {
    const r = await call("/api/vehicle", {}, 1000);
    const v = r.ok && r.json ? r.json : null;
    S.link = v && v.link && typeof v.link === "object" ? v.link : null;
    S.speed = v && v.speed ? v.speed : null;
    S.f1 = v && v.f1 ? v.f1 : null;
    // link
    const st = S.link ? S.link.state : (r.status ? `HTTP ${r.status}` : "no answer");
    const chip = $("link-state");
    chip.textContent = String(st).toUpperCase();
    chip.className = "chip " + ({ live: "ok", lost: "bad", error: "bad", waiting: "warn", connecting: "warn" }[st] || "");
    const pill = $("pill-vehicle");
    pill.className = "pill " + (st === "live" ? "up" : st === "lost" || st === "error" ? "down" : S.link ? "warn" : "unknown");
    pill.querySelector("b").textContent = S.link ? (st === "live" ? `${S.link.rate_hz}/s` : st) : "—";
    pill.title = S.link ? (S.link.error || `${S.link.key} · ${(S.link.endpoints || []).join(", ")}`) : "";
    if (S.link) {
      $("link-key").textContent = S.link.key;
      $("link-rate").textContent = `${S.link.rate_hz} samples/s`;
      $("link-age").textContent = fmtAge(S.link.age_ms) + (st === "lost" ? `  (> ${S.link.timeout_ms} ms)` : "");
      $("link-raw").textContent = S.link.last_raw === null ? "—" : `"${S.link.last_raw}"` + (S.link.last_error ? `  (${S.link.last_error})` : "");
      $("link-count").textContent = `${S.link.samples} · ${S.link.invalid_samples} bad`;
      $("link-ep").textContent = (S.link.endpoints || []).join(", ") + ` · peers ${S.link.peers} · routers ${S.link.routers}` + (S.link.error ? ` · ${S.link.error}` : "");
      $("r-zenoh").textContent = `${S.link.rate_hz}/s`;
    }
    flow.onLink(S.link, r.status ? `HTTP ${r.status}` : "console not answering");
    // speed (what the vehicle sends, as the console observer sees it)
    const el = $("speed"), age = $("speed-age");
    flow.onSpeed(S.speed, S.link);
    if (!S.speed) { el.textContent = "—"; el.classList.add("stale"); age.className = "age stale"; age.textContent = "console not answering"; }
    else {
      el.textContent = typeof S.speed.value === "number" ? S.speed.value.toFixed(1) : "—";
      $("speed-unit").textContent = S.speed.unit || "km/h";
      el.classList.toggle("stale", !!S.speed.stale);
      age.className = "age" + (S.speed.stale ? " stale" : "");
      age.textContent = S.speed.value === null ? "no valid sample yet" : S.speed.stale ? `STALE · last valid ${fmtAge(S.speed.age_ms)}` : `age ${S.speed.age_ms} ms`;
      $("speed-src").textContent = `${S.speed.source || ""} → console observer`;
    }
    // F1 monitor
    if (S.f1) {
      const d = S.f1;
      document.querySelectorAll("#deb-states span").forEach((x) => x.classList.toggle("on", x.dataset.state === d.state));
      const c = Number(d.counter) || 0, t = Number(d.threshold) || 1;
      $("deb-count").textContent = `${d.fault || ""} · ${d.state || "?"} · ${c} / ${t} · range ${(d.range_kmh || []).join("–")} km/h · verdict → gateway switch`;
      const bar = $("deb-bar"); bar.style.width = `${Math.min(100, 100 * c / t)}%`; bar.classList.toggle("full", c >= t);
      $("deb-reason").textContent = d.last_reason ? `last failing sample: ${d.last_reason}` : "";
      const gwFault = S.sovd && S.sovd.items && S.sovd.items.fault ? S.sovd.items.fault.data : null;
      flow.onMonitor(d, S.link, gwFault);
    }
    renderTopo();
  }
  async function pollSovd() {
    const r = await call("/api/sovd", {}, 1000);
    S.sovd = r.ok && r.json ? r.json : null;
    const g = S.sovd;
    const it = (role) => (g && g.items && g.items[role] ? g.items[role].data : null);
    const set = (id, text, cls, sub) => { const el = $(id); el.querySelector("b").textContent = text; el.className = "gw-item" + (cls ? " " + cls : ""); if (sub !== undefined) el.querySelector("small").textContent = sub; };
    if (!g || !g.reachable) {
      ["gw-speed", "gw-state", "gw-fault", "gw-switch"].forEach((id) => set(id, "—", "bad"));
      $("gw-meta").textContent = g ? `${g.url} · not reachable: ${g.error || "no answer"}` : "console not answering";
      $("gw-contract").textContent = "DOWN"; $("gw-contract").className = "chip bad";
      $("gw-bridge").textContent = "bridge: gateway not reachable";
      return;
    }
    const sp = it("speed"), st = it("state"), fs = it("fault"), sw = it("switch");
    set("gw-speed", sp && typeof sp.value === "number" ? `${sp.value.toFixed(1)} ${sp.unit || "km/h"}` : "—", "", "gateway sensor (cruise.rs)");
    set("gw-state", st && st.state ? st.state : "—", st ? STATE_CLS[st.state] || "" : "", st && st.set_speed !== undefined ? `set speed ${st.set_speed}` : "read-only");
    set("gw-fault", fs && fs.status ? fs.status : "—", fs ? STAGE_CLS[fs.status] || "" : "", fs ? `${fs.fault || "fault"} · test_failed ${fs.test_failed} · confirmed ${fs.confirmed}` : "TimeBased debounce");
    set("gw-switch", sw ? (sw.stuck ? "stuck = true" : "stuck = false") : "—", sw ? (sw.stuck ? "bad" : "ok") : "", "rw · PUT by the bridge");
    flow.onCruise(st && st.state);
    const c = g.contract || {};
    const chip = $("gw-contract");
    if (c.checked) { chip.textContent = c.ok ? "CONTRACT OK" : "CONTRACT ?"; chip.className = "chip " + (c.ok ? "ok" : "bad"); chip.title = c.ok ? `component ${g.component} · items ${(c.items || []).join(", ")}` : (c.error || `missing: ${(c.missing || []).join(", ")}`); }
    $("gw-meta").textContent = `${g.url}${g.base}/v1/components/${g.component} · poll ${Math.round((S.cfg.sovd.poll_s || 0.2) * 1000)} ms · debounce ${g.debounce_ms.failed}/${g.debounce_ms.passed} ms`;
    const br = g.bridge || {};
    $("gw-bridge").textContent = !br.enabled ? "bridge: off (FAULT_BRIDGE=0) · the switch is only driven by hand" :
      `bridge: verdict ${br.wanted ? "FAULTY" : "ok"} → switch ${br.gateway_stuck === null ? "?" : br.gateway_stuck}` +
      (br.in_sync === false ? " · NOT IN SYNC" : br.in_sync ? " · in sync" : "") + ` · ${br.writes} writes` + (br.last_error ? ` · last error: ${br.last_error}` : "");
    if (S.bridgeSeq === null) S.bridgeSeq = br.seq || 0;
    const fresh = (br.events || []).filter((e) => e.seq > S.bridgeSeq);
    if (fresh.length) { S.bridgeFlash = performance.now(); flow.onBridge(fresh); S.bridgeSeq = br.seq; }
    renderTopo();
  }
  async function pollFaults() {
    const r = await call("/api/faults", {}, 1000);
    const items = r.ok && r.json && Array.isArray(r.json.items) ? r.json.items : null;
    if (!items) { $("score-fault-meta").textContent = r.status ? `HTTP ${r.status}` : "console not answering"; return; }
    items.sort((a, b) => ((b.qualified_failed ? 1 : 0) - (a.qualified_failed ? 1 : 0)) || String(a.code).localeCompare(String(b.code)));
    const failing = items.filter((f) => f.qualified_failed).length;
    flow.onScoreFaults(items);
    $("score-fault-meta").textContent = `${items.length} faults · ${failing} failed · F1 from the gateway, F2 from the console`;
    $("score-faults").innerHTML = items.map((f) => {
      const src = f.source && f.source.startsWith("sovd") ? "gateway" : "console";
      const extra = `${f.stage}${f.cruise_state ? " · cruise " + f.cruise_state : ""}${f.console_f1 && src === "gateway" ? " · console F1 " + f.console_f1 : ""}` +
        `${f.occurrences ? " · occurrences " + f.occurrences : ""}${f.available === false ? " · SOURCE NOT READABLE" : ""}`;
      const cls = f.qualified_failed ? "failing" : f.stage === "prefailed" || f.stage === "prepassed" ? "pre" : "";
      return faultCard(f.code, f.display, f.status, extra, src, cls);
    }).join("") || `<div class="empty">no fault reported</div>`;
  }
  async function pollAuto() {
    const r = await call("/api/auto");
    const a = r.json;
    if (!a) { $("auto-meta").textContent = "console API not answering"; return; }
    S.auto = a;
    $("auto-meta").textContent = !a.enabled ? "off (AUTO_DTC=0)" : a.running ? (a.error ? `error: ${a.error}` : `on · ${a.polls} polls · follows the qualified result`) : "not running";
    const rows = Object.entries(a.state || {}).map(([code, st]) => {
      const cls = st.failing ? "bad" : st.ecu_mask ? "warn" : "ok";
      const what = st.failing ? `set 0x${st.ecu_mask || a.mask_active}` : st.ecu_mask ? `stored 0x${st.ecu_mask}` : "idle";
      return `<div class="auto-row"><span class="code">${esc(code)}</span><span class="arrow">→</span><span class="code">${esc(st.dtc)}</span>
        <span class="chip ${cls}">${esc(what)}</span><span class="muted">${esc(st.display || "")}</span></div>`;
    });
    $("auto-rows").innerHTML = rows.join("") || `<div class="empty">no mapping</div>`;
    const evs = (a.events || []).filter((e) => e.change !== "reset");
    const last = evs[evs.length - 1];
    $("auto-last").innerHTML = last ? `<span class="${last.ok ? "ok" : "bad"}">${esc(eventText(last))}</span>` : "no automatic change yet";
    if (S.autoSeq === null) S.autoSeq = a.seq;
    const fresh = (a.events || []).filter((x) => x.seq > S.autoSeq);
    for (const e of fresh.filter((x) => x.change !== "reset")) { toast(eventText(e), !e.ok, 4500); S.autoFlash = performance.now(); }
    flow.onAuto(fresh);
    S.autoSeq = a.seq;
    renderTopo();
  }
  function eventText(e) {
    const when = new Date(e.t * 1000).toTimeString().slice(0, 8);
    const what = e.change === "failing" ? `${e.fault} confirmed → ECU DTC ${e.dtc} set 0x${e.mask}` : `${e.fault} healed → ECU DTC ${e.dtc} stored 0x${e.mask}`;
    return `${when} · ${what} · ` + (e.ok ? `read back ${e.readback} via CDA in ${e.readback_ms} ms` : `FAILED: ${e.error}`);
  }
  async function pollCdaFaults() {
    const r = await call(`/proxy/cda${S.cfg.cda.base}/components/${S.cfg.cda.ecu}/faults`, {}, 2500);
    const items = r.ok && r.json && r.json.items;
    if (!Array.isArray(items)) { $("cda-fault-meta").textContent = r.status === 401 ? "unauthorized" : r.status ? `HTTP ${r.status}` : "no answer"; return; }
    const active = (f) => decode(f.status).set.some(Boolean);
    const owned = new Set(Object.values((S.cfg.auto_dtc || {}).map || {}).map((c) => c.toUpperCase()));
    const on = items.filter(active), off = items.filter((f) => !active(f));
    flow.onDtcs(on);
    $("cda-fault-meta").textContent = `${on.length} active DTC${on.length === 1 ? "" : "s"}` + (off.length ? ` · ${off.length} inactive` : "") + " · read over DoIP";
    const card = (f) => { const code = String(f.display_code || f.code).toUpperCase(); return faultCard(code, f.fault_name, f.status, f.scope, owned.has(code) ? "auto" : ""); };
    $("cda-faults").innerHTML = (on.length ? on.map(card).join("") : `<div class="empty">no active DTC</div>`)
      + off.map((f) => card(f).replace('class="fault ', 'class="fault inactive ')).join("");
  }
  async function pollLog() {
    if ($("log-pause").checked) return;
    const r = await call(`/api/log?since=${S.logSeq}`);
    if (!r.json) return;
    const box = $("log");
    for (const e of r.json.entries) {
      S.logSeq = e.seq;
      const t = new Date(e.t * 1000), ts = t.toTimeString().slice(0, 8) + "." + String(t.getMilliseconds()).padStart(3, "0");
      const bad = e.error || e.status >= 400 || e.status === 0;
      const row = document.createElement("div");
      row.className = "l" + (bad ? " err" : "");
      row.innerHTML = `<span class="t">${ts}</span><span class="o">${esc(e.origin || "check")}</span><span class="b">${esc(e.backend)}</span><span>${esc(e.method)}</span>` +
        `<span class="p" title="${esc(e.path)}">${esc(e.path)}</span><span class="s ${bad ? "bad" : "ok"}">${e.status || "ERR"}</span><span class="ms">${e.ms} ms</span>`;
      if (e.error) row.title = e.error;
      box.appendChild(row);
    }
    while (box.children.length > 50) box.removeChild(box.firstChild);
    if (r.json.entries.length) box.scrollTop = box.scrollHeight;
  }
  async function pollRun() {
    const r = await call("/api/run");
    if (r.json) { S.run = r.json; renderRun(); }
    if (S.run && S.run.running) setTimeout(pollRun, 400);
  }

  // ------------------------------------------------------------ topology
  function renderTopo() {
    const h = S.health, up = (k) => !!(h[k] && h[k].up), known = (k) => !!h[k];
    const st = S.link ? S.link.state : null;
    const cls = (id, state) => { $(id).setAttribute("class", "link " + state); };
    const node = (id, state) => { const el = $(id); el.setAttribute("class", "node" + (el.id === "n-console" ? " self" : "") + (state ? " " + state : "")); };
    node("n-vehicle", st === "live" ? "up" : st === "lost" || st === "error" ? "down" : "");
    node("n-gateway", known("sovd") ? (up("sovd") ? "up" : "down") : "");
    node("n-cda", known("cda") ? (up("cda") ? "up" : "down") : "");
    node("n-sim", known("sim") ? (up("sim") ? "up" : "down") : "");
    cls("l-zenoh", !st ? "idle" : st === "live" ? "up" : st === "lost" || st === "error" ? "down" : "hold");
    cls("l-sovd", !known("sovd") ? "idle" : up("sovd") ? "up" : "down");
    cls("l-cda", !known("cda") ? "idle" : up("cda") ? "up" : "down");
    cls("l-doip", !known("cda") || !known("sim") ? "idle" : up("cda") && up("sim") ? "up" : "down");
    $("l-auto").setAttribute("class", "link ctl" + (up("sim") ? " up" : "") + (performance.now() - S.autoFlash < 3000 ? " flash" : ""));
    $("l-bridge").setAttribute("class", "link ctl" + (up("sovd") ? " up" : "") + (performance.now() - S.bridgeFlash < 3000 ? " flash" : ""));
    if (S.link) $("n-vehicle-sub").textContent = st === "live" ? `${S.link.rate_hz}/s · Zenoh` : st || "—";
    if (S.sovd && S.sovd.reachable) { const fs = S.sovd.items && S.sovd.items.fault ? S.sovd.items.fault.data : null; $("n-gateway-sub").textContent = `PR #40 · ${S.sovd.component} · ${fs ? fs.status : "?"}`; }
    const dk = (id, name) => {
      const d = S.docker; let txt = "Docker ?";
      if (d && d.available) { const hit = d.containers.find((c) => c.name.includes(name)); txt = hit ? `Docker ${hit.state}` : "no container"; }
      else if (d) txt = "Docker n/a";
      $(id).textContent = txt;
    };
    dk("d-cda", "cda"); dk("d-sim", "sim");
  }

  // ------------------------------------------------------------ actions
  function toast(msg, err, ms = 2500) {
    const t = $("toast"); t.textContent = msg; t.className = "toast" + (err ? " err" : ""); t.hidden = false;
    clearTimeout(t._h); t._h = setTimeout(() => { t.hidden = true; }, ms);
  }
  async function resetFaults() {
    flow.onReset();
    const r = await post("/api/reset");
    r.ok ? toast("Fault memory forgotten · gateway switch back · ECU memory cleared · automatic DTC re-armed")
      : toast(`Reset incomplete: ${r.json ? JSON.stringify(r.json) : r.error || "HTTP " + r.status}`, true, 5000);
  }
  async function setSwitch(stuck) {
    const r = await post("/api/switch", { stuck });
    if (r.ok) { toast(`PUT speed_sensor_stuck = ${stuck} accepted (${r.json ? r.json.status : ""}) · watch the gateway debounce`); flow.add("auto", `page → gateway: PUT speed_sensor_stuck ${stuck} (test only)`); }
    else toast(`PUT refused: ${r.json ? r.json.error || JSON.stringify(r.json) : r.error || "HTTP " + r.status}`, true, 5000);
  }
  async function runChecks() {
    const r = await post("/api/run");
    if (r.status === 409) return toast("Already running", true);
    if (!r.ok) return toast(`Could not start: ${r.error || "HTTP " + r.status}`, true);
    S.selCheck = null; toast(`Running ${CHECKS_N} checks`); pollRun();
  }

  // ------------------------------------------------------------ runner view
  function renderRun() {
    const run = S.run, res = run.results || [];
    $("btn-run").disabled = !!run.running;
    const box = $("checks");
    box.innerHTML = "";
    for (let i = 1; i <= CHECKS_N; i++) {
      const r = res.find((x) => x.num === i);
      const el = document.createElement("div");
      el.className = "check " + (r ? (r.ok ? "pass" : "fail") : run.running && res.length === i - 1 ? "running" : "") + (S.selCheck === i ? " sel" : "");
      el.textContent = i; el.title = r ? `${r.name}: ${r.detail}` : "";
      el.onclick = () => { S.selCheck = S.selCheck === i ? null : i; renderRun(); };
      box.appendChild(el);
    }
    const passed = res.filter((r) => r.ok).length;
    $("run-meta").textContent = run.running ? `running · ${res.length} / ${CHECKS_N} done` :
      res.length ? `${passed} / ${res.length} passed${run.finished ? " · " + new Date(run.finished * 1000).toTimeString().slice(0, 8) : ""}` : `${CHECKS_N} checks · not run yet`;
    const shown = S.selCheck ? res.filter((r) => r.num === S.selCheck) : res;
    $("check-detail").innerHTML = shown.length ? shown.map((r) =>
      `<div class="row ${r.ok ? "pass" : "fail"}"><span>${r.num}</span><span>${esc(r.name)}<br><span class="d">${esc(r.detail)}</span></span><span class="d">${r.ms} ms</span></div>`).join("")
      : run.running ? "…" : `Press <b>Run ${CHECKS_N} checks</b> before every dry run.`;
  }

  // ------------------------------------------------------------ start
  async function main() {
    const r = await call("/api/config");
    S.cfg = r.json;
    if (!S.cfg) { toast("Console API not reachable", true); return setTimeout(main, 2000); }
    document.querySelector('.pill[data-svc="sovd"] small').textContent = ":" + S.cfg.sovd.url.split(":").pop();
    document.querySelector('.pill[data-svc="cda"] small').textContent = ":" + S.cfg.cda.url.split(":").pop();
    document.querySelector('.pill[data-svc="sim"] small').textContent = ":" + S.cfg.sim.url.split(":").pop();
    $("link-key").textContent = S.cfg.vehicle.key;
    document.querySelectorAll("#gw-items .k").forEach((el, i) => { el.textContent = [S.cfg.sovd.items.speed, S.cfg.sovd.items.state, S.cfg.sovd.items.fault, S.cfg.sovd.items.switch][i]; });
    $("btn-reset").onclick = resetFaults; $("btn-run").onclick = runChecks;
    $("btn-stuck-on").onclick = () => setSwitch(true); $("btn-stuck-off").onclick = () => setSwitch(false);
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.ctrlKey || e.metaKey || e.altKey) return;
      ({ c: resetFaults, r: runChecks, a: flow.ack }[e.key.toLowerCase()] || (() => { }))();
    });
    flow.init();
    setInterval(() => { $("clock").textContent = new Date().toTimeString().slice(0, 8); }, 500);
    loop(pollHealth, 1000); loop(pollDocker, 5000); loop(pollStats, 1000); loop(pollVehicle, 300);
    loop(pollSovd, 300); loop(pollFaults, 500); loop(pollAuto, 700); loop(pollCdaFaults, 1000); loop(pollLog, 1000);
    pollRun();
  }
  main();
})();
