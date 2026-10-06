/* Demo Console page: polls the console API and the proxied backends, renders
   both diagnostic paths, the topology, the log and the runner. No framework. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const S = { cfg: null, health: {}, docker: null, stats: null, frozen: false, lastTs: null, lastChange: 0,
    lastSpeedOk: 0, logSeq: 0, run: null, selCheck: null };

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
  const put = (url, data) => call(url, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) }, 2500);
  const del = (url) => call(url, { method: "DELETE" }, 2500);
  const post = (url) => call(url, { method: "POST" }, 2500);

  // paths built from /api/config
  const P = {
    sovd: (item) => `/proxy/sovd${S.cfg.sovd.base}/v1/${S.cfg.sovd.entity}` + (item ? `/data/${item}` : ""),
    sovdFaults: () => `/proxy/sovd${S.cfg.sovd.base}/v1/${S.cfg.sovd.entity}/faults`,
    cdaFaults: () => `/proxy/cda${S.cfg.cda.base}/components/${S.cfg.cda.ecu}/faults`,
    simDtc: () => `/proxy/sim/${S.cfg.sim.ecu}/dtc/${S.cfg.sim.fault_memory}`,
  };

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
  function bitStrip(d) {
    return `<div class="bits">${BITS.map((n, i) => `<span class="${d.set[7 - i] ? "on" : ""}" title="bit ${7 - i}: ${BITS[7 - i]}">b${7 - i}</span>`).join("")}</div>`;
  }
  function faultCard(code, name, status, extra) {
    const d = decode(status);
    return `<div class="fault ${d.set[0] ? "failing" : ""}"><div class="head"><span class="code">${esc(code)}</span><span class="hex">${d.hex}</span></div>
      <div class="name">${esc(name || "")}${extra ? " · " + esc(extra) : ""}</div>${bitStrip(d)}<div class="summary">${esc(d.summary)}</div></div>`;
  }
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

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
      el.title = h ? (h.error || (svc === "cda" && h.token_error ? "token: " + h.token_error : "")) : "";
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
      const okAll = exp.every(([, v]) => v);
      el.className = "pill " + (exp.length === 0 ? "up" : okAll ? "up" : "down");
      el.querySelector("b").textContent = exp.length ? `${exp.filter(([, v]) => v).length}/${exp.length}` : "ok";
      el.title = d.containers.map((c) => `${c.name}: ${c.state}`).join("\n") || "no containers";
    }
    renderTopo();
  }
  async function pollStats() {
    const r = await call("/api/stats");
    S.stats = r.json;
    const s = S.stats, rates = (s && s.rates) || {};
    const keys = Object.keys(rates);
    const fmt = (k) => (k in rates ? `${rates[k].toFixed(1)}/s` : "—");
    $("r-sensor").textContent = fmt(keys[0]);
    $("r-sovd").textContent = keys[1] ? fmt(keys[1]) : "";
    $("stats-meta").textContent = !s || !s.ok ? `stats.json: ${s && s.error ? s.error : "no data"}` :
      `stats.json: ${s.age_s > 2 ? "STALE " : ""}${s.age_s}s old · ` + keys.map((k) => `${k} ${rates[k].toFixed(1)}/s`).join(" · ");
    renderTopo();
  }
  async function pollSpeed() {
    const r = await call(P.sovd(S.cfg.sovd.items.speed), {}, 1000);
    const d = r.ok && r.json && r.json.data, now = performance.now();
    if (d && typeof d === "object") {
      S.lastSpeedOk = now;
      if (d.ts !== S.lastTs) { S.lastTs = d.ts; S.lastChange = now; }
      $("speed").textContent = typeof d.value === "number" ? d.value.toFixed(1) : String(d.value);
      $("speed-unit").textContent = d.unit || "";
    } else if (now - S.lastSpeedOk > 2000) { $("speed").textContent = "—"; }
    const age = S.lastTs === null ? null : now - S.lastChange;
    const stale = age === null || age > 1000 || now - S.lastSpeedOk > 2000;
    $("speed").classList.toggle("stale", stale);
    $("speed-age").className = "age" + (stale ? " stale" : "");
    $("speed-age").textContent = age === null ? "no data" : now - S.lastSpeedOk > 2000 ? "SOVD not answering" :
      age > 1000 ? `no new sample for ${(age / 1000).toFixed(1)} s` : `age ${Math.round(age)} ms`;
    renderTopo();
  }
  async function pollDebounce() {
    const r = await call(P.sovd(S.cfg.sovd.items.debounce), {}, 1000);
    const d = r.ok && r.json && r.json.data;
    if (!d || typeof d !== "object") return;
    if (typeof d.frozen === "boolean") setFrozen(d.frozen);
    document.querySelectorAll("#deb-states span").forEach((el) => el.classList.toggle("on", el.dataset.state === d.state));
    const c = Number(d.counter) || 0, t = Number(d.threshold) || 1;
    $("deb-count").textContent = `${d.state || "?"} · ${c} / ${t}`;
    const bar = $("deb-bar"); bar.style.width = `${Math.min(100, 100 * c / t)}%`; bar.classList.toggle("full", c >= t);
  }
  async function pollScoreFaults() {
    const r = await call(P.sovdFaults(), {}, 1000);
    const items = r.ok && r.json && r.json.items;
    if (!Array.isArray(items)) { $("score-fault-meta").textContent = r.status === 404 ? "faults resource not implemented (#156)" : "no answer"; return; }
    $("score-fault-meta").textContent = `${items.length} fault${items.length === 1 ? "" : "s"} · #156 model`;
    $("score-faults").innerHTML = items.length ? items.map((f) => faultCard(f.code, f.display || f.fault_name, f.status, f.severity != null ? `severity ${f.severity}` : "")).join("")
      : `<div class="empty">no fault reported</div>`;
  }
  async function pollCdaFaults() {
    const r = await call(P.cdaFaults(), {}, 2500);
    const items = r.ok && r.json && r.json.items;
    if (!Array.isArray(items)) { $("cda-fault-meta").textContent = r.status === 401 ? "unauthorized" : r.status ? `HTTP ${r.status}` : "no answer"; return; }
    $("cda-fault-meta").textContent = `${items.length} DTC${items.length === 1 ? "" : "s"} · read over DoIP`;
    $("cda-faults").innerHTML = items.length ? items.map((f) => faultCard(f.display_code || f.code, f.fault_name, f.status, f.scope)).join("")
      : `<div class="empty">fault memory empty</div>`;
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
      row.innerHTML = `<span class="t">${ts}</span><span class="b">${esc(e.backend)}</span><span>${esc(e.method)}</span><span class="p" title="${esc(e.path)}">${esc(e.path)}</span>` +
        `<span class="s ${bad ? "bad" : "ok"}">${e.status || "ERR"}</span><span class="ms">${e.ms} ms</span>`;
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
    const now = performance.now();
    const fresh = S.lastTs !== null && now - S.lastChange <= 1000 && now - S.lastSpeedOk <= 2000;
    const flowing = S.stats && S.stats.ok && S.stats.age_s <= 2 && Object.values(S.stats.rates || {}).some((v) => v > 0);
    const cls = (id, state) => { $(id).setAttribute("class", "link " + state); };
    const node = (id, state) => { const el = $(id); el.setAttribute("class", "node" + (el.id === "n-console" ? " self" : "") + (state ? " " + state : "")); };
    node("n-score", known("sovd") ? (up("sovd") ? "up" : "down") : "");
    node("n-cda", known("cda") ? (up("cda") ? "up" : "down") : "");
    node("n-sim", known("sim") ? (up("sim") ? "up" : "down") : "");
    node("n-sensor", up("sovd") ? (fresh ? "up" : "down") : "");
    cls("l-sensor", !known("sovd") ? "idle" : !up("sovd") ? "down" : fresh && (flowing || !S.stats || !S.stats.ok) ? "up" : "hold");
    cls("l-sovd", !known("sovd") ? "idle" : up("sovd") ? "up" : "down");
    cls("l-cda", !known("cda") ? "idle" : up("cda") ? "up" : "down");
    cls("l-doip", !known("cda") || !known("sim") ? "idle" : up("cda") && up("sim") ? "up" : "down");
    $("l-simctl").setAttribute("class", "link ctl" + (up("sim") ? " up" : ""));
    const dk = (id, name) => {
      const d = S.docker; let txt = "Docker ?";
      if (d && d.available) { const hit = d.containers.find((c) => c.name.includes(name)); txt = hit ? `Docker ${hit.state}` : "no container"; }
      else if (d) txt = "Docker n/a";
      $(id).textContent = txt;
    };
    dk("d-cda", "cda"); dk("d-sim", "sim");
  }

  // ------------------------------------------------------------ actions
  function setFrozen(v) {
    S.frozen = v;
    const b = $("btn-freeze");
    b.textContent = v ? "Unfreeze sensor" : "Freeze sensor";
    b.classList.toggle("on", v);
  }
  function toast(msg, err) {
    const t = $("toast"); t.textContent = msg; t.className = "toast" + (err ? " err" : ""); t.hidden = false;
    clearTimeout(t._h); t._h = setTimeout(() => { t.hidden = true; }, 2500);
  }
  async function freeze() {
    const want = !S.frozen;
    const r = await put(P.sovd(S.cfg.sovd.items.freeze), { data: want });
    if (r.ok) { setFrozen(want); toast(want ? "Sensor frozen: watch the debounce" : "Sensor released"); }
    else toast(`Freeze failed: ${r.error || "HTTP " + r.status}`, true);
  }
  async function inject() {
    const code = $("dtc-code").value.trim().toUpperCase(), mask = $("dtc-status").value;
    if (!/^([PCBU][0-9A-F]{6}|[0-9A-F]{6})$/.test(code)) return toast("Code: 6 hex digits, or a letter P/C/B/U + 6 hex digits", true);
    const r = await put(P.simDtc(), { id: code, statusMask: mask, emissionsRelated: false });
    r.ok ? toast(`DTC ${code} injected with 0x${mask}`) : toast(`Inject failed: ${r.error || "HTTP " + r.status}`, true);
  }
  async function clearAll() {
    const r = await del(P.simDtc());
    r.ok ? toast("Fault memory cleared") : toast(`Clear failed: ${r.error || "HTTP " + r.status}`, true);
  }
  async function runChecks() {
    const r = await post("/api/run");
    if (r.status === 409) return toast("Already running", true);
    if (!r.ok) return toast(`Could not start: ${r.error || "HTTP " + r.status}`, true);
    S.selCheck = null; toast("Running 13 checks"); pollRun();
  }

  // ------------------------------------------------------------ runner view
  function renderRun() {
    const run = S.run, res = run.results || [];
    $("btn-run").disabled = !!run.running;
    const box = $("checks");
    box.innerHTML = "";
    for (let i = 1; i <= 13; i++) {
      const r = res.find((x) => x.num === i);
      const el = document.createElement("div");
      el.className = "check " + (r ? (r.ok ? "pass" : "fail") : run.running && res.length === i - 1 ? "running" : "") + (S.selCheck === i ? " sel" : "");
      el.textContent = i; el.title = r ? `${r.name}: ${r.detail}` : "";
      el.onclick = () => { S.selCheck = S.selCheck === i ? null : i; renderRun(); };
      box.appendChild(el);
    }
    const passed = res.filter((r) => r.ok).length;
    $("run-meta").textContent = run.running ? `running · ${res.length} / 13 done` :
      res.length ? `${passed} / ${res.length} passed${run.finished ? " · " + new Date(run.finished * 1000).toTimeString().slice(0, 8) : ""}` : "13 checks · not run yet";
    const shown = S.selCheck ? res.filter((r) => r.num === S.selCheck) : res;
    $("check-detail").innerHTML = shown.length ? shown.map((r) =>
      `<div class="row ${r.ok ? "pass" : "fail"}"><span>${r.num}</span><span>${esc(r.name)}<br><span class="d">${esc(r.detail)}</span></span><span class="d">${r.ms} ms</span></div>`).join("")
      : run.running ? "…" : "Press <b>Run 13 checks</b> before every dry run.";
  }

  // ------------------------------------------------------------ start
  async function main() {
    const r = await call("/api/config");
    S.cfg = r.json;
    if (!S.cfg) { toast("Console API not reachable", true); return setTimeout(main, 2000); }
    $("dtc-code").value = S.cfg.demo_dtc.code;
    $("dtc-status").value = S.cfg.demo_dtc.mask;
    document.querySelector('.pill[data-svc="sovd"] small').textContent = ":" + S.cfg.sovd.url.split(":").pop();
    document.querySelector('.pill[data-svc="cda"] small').textContent = ":" + S.cfg.cda.url.split(":").pop();
    document.querySelector('.pill[data-svc="sim"] small').textContent = ":" + S.cfg.sim.url.split(":").pop();
    $("btn-freeze").onclick = freeze; $("btn-inject").onclick = inject; $("btn-clear").onclick = clearAll; $("btn-run").onclick = runChecks;
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.ctrlKey || e.metaKey) return;
      ({ f: freeze, i: inject, c: clearAll, r: runChecks }[e.key.toLowerCase()] || (() => { }))();
    });
    setInterval(() => { $("clock").textContent = new Date().toTimeString().slice(0, 8); }, 500);
    loop(pollHealth, 1000); loop(pollDocker, 5000); loop(pollStats, 1000);
    loop(pollSpeed, 300); loop(pollDebounce, 300); loop(pollScoreFaults, 500); loop(pollCdaFaults, 1000); loop(pollLog, 1000);
    pollRun();
  }
  main();
})();
