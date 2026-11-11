/* Rivencast site interactions — rc-tech */
(() => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Mobile nav */
  const btn = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (btn && nav) {
    const setOpen = (open) => {
      btn.setAttribute("aria-expanded", String(open));
      document.body.classList.toggle("nav-open", open);
    };
    btn.addEventListener("click", () => setOpen(btn.getAttribute("aria-expanded") !== "true"));
    nav.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
    window.addEventListener("resize", () => { if (window.innerWidth > 820) setOpen(false); });
  }

  /* Header state */
  const bar = document.querySelector(".topbar-wrap");
  const onScroll = () => bar && bar.classList.toggle("scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* Scroll reveal */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("in"));
  }

  /* Pointer-follow glow on cards */
  if (window.matchMedia("(hover: hover)").matches) {
    document.addEventListener("pointermove", (e) => {
      const card = e.target.closest && e.target.closest(".card");
      if (!card) return;
      const r = card.getBoundingClientRect();
      card.style.setProperty("--mx", `${e.clientX - r.left}px`);
      card.style.setProperty("--my", `${e.clientY - r.top}px`);
    }, { passive: true });
  }

  /* 404 path echo */
  const nfPath = document.getElementById("nf-path");
  if (nfPath) nfPath.textContent = window.location.pathname;

  /* Terminal demo */
  const term = document.getElementById("term-body");
  const scripts = [
    {
      title: "hana — groceries",
      cmd: "reorder my usual groceries, keep it under $60",
      steps: [
        ["pulling your usual list from memory", "done"],
        ["comparing prices at two stores", "done"],
        ["cart built · $54.12 · delivery after 9 AM", "done"],
        ["card filled from encrypted vault · never shown to agent", "lock"],
      ],
      ask: "place the order?",
    },
    {
      title: "hana — inbox",
      cmd: "clean up my inbox and tell me what matters",
      steps: [
        ["reading your connected inbox", "done"],
        ["sorting promos, receipts, and real mail", "done"],
        ["2 need you: a bill due Friday, a reply from your landlord", "done"],
        ["drafting the reply in your voice", "done"],
      ],
      ask: "send the reply?",
    },
    {
      title: "hana — calendar",
      cmd: "find a time with Sam next week and set it up",
      steps: [
        ["checking your calendar", "done"],
        ["open: Tue 2:00 PM · Thu 11:30 AM", "done"],
        ["drafting the invite for Tue 2:00 PM", "done"],
      ],
      ask: "send the invite?",
    },
  ];
  if (!term) return;
  const titleEl = document.getElementById("term-title");
  const dotsWrap = document.getElementById("term-dots");
  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
  let run = 0;
  let current = 0;

  const line = (html) => { const d = document.createElement("div"); d.className = "ln"; d.innerHTML = html; term.appendChild(d); return d; };
  const tail = (kind) => kind === "lock" ? '<span class="t-lock">sealed</span>' : '<span class="t-ok">done</span>';

  const renderStatic = (s) => {
    term.innerHTML = "";
    line(`<span class="t-prompt">~</span><span class="t-cmd">hana <span class="t-str">"${esc(s.cmd)}"</span></span>`);
    s.steps.forEach(([t, k]) => line(`<span class="t-arrow">→</span><span class="t-step">${esc(t)}</span>${tail(k)}`));
    line(`<span class="t-q">?</span><span class="t-step"><span class="t-cmd">${esc(s.ask)}</span> <span class="t-wait">waiting for your OK</span><span class="caret"></span></span>`);
  };

  const setDots = (i) => {
    if (!dotsWrap) return;
    dotsWrap.querySelectorAll("button").forEach((b, j) => b.setAttribute("aria-current", String(i === j)));
  };

  const play = async (i) => {
    const my = ++run;
    current = i;
    const s = scripts[i];
    setDots(i);
    if (titleEl) titleEl.textContent = s.title;
    if (reduce) { renderStatic(s); return; }
    term.innerHTML = "";
    const l = line('<span class="t-prompt">~</span><span class="t-cmd"></span><span class="caret"></span>');
    const cmdEl = l.querySelector(".t-cmd");
    const full = `hana "${s.cmd}"`;
    for (let c = 1; c <= full.length; c++) {
      if (my !== run) return;
      const typed = full.slice(0, c);
      const q = typed.indexOf('"');
      cmdEl.innerHTML = q < 0 ? esc(typed) : `${esc(typed.slice(0, q))}<span class="t-str">${esc(typed.slice(q))}</span>`;
      await sleep(18 + Math.random() * 38);
    }
    l.querySelector(".caret").remove();
    await sleep(380);
    for (const [t, k] of s.steps) {
      if (my !== run) return;
      const sl = line(`<span class="spin-ch">${frames[0]}</span><span class="t-step">${esc(t)}</span><span class="t-dim">…</span>`);
      const sp = sl.querySelector(".spin-ch");
      const dur = 600 + Math.random() * 700;
      const t0 = performance.now();
      let f = 0;
      while (performance.now() - t0 < dur) {
        if (my !== run) return;
        sp.textContent = frames[f++ % frames.length];
        await sleep(70);
      }
      sl.innerHTML = `<span class="t-arrow">→</span><span class="t-step">${esc(t)}</span>${tail(k)}`;
      await sleep(160);
    }
    if (my !== run) return;
    await sleep(250);
    line(`<span class="t-q">?</span><span class="t-step"><span class="t-cmd">${esc(s.ask)}</span> <span class="t-wait">waiting for your OK</span><span class="caret"></span></span>`);
    await sleep(4200);
    if (my !== run) return;
    play((i + 1) % scripts.length);
  };

  if (dotsWrap) {
    dotsWrap.innerHTML = scripts.map((s, i) => `<button type="button" aria-label="Show demo ${i + 1}: ${esc(s.title)}"></button>`).join("");
    dotsWrap.querySelectorAll("button").forEach((b, i) => b.addEventListener("click", () => play(i)));
  }
  // Start when visible
  if ("IntersectionObserver" in window) {
    let started = false;
    const tio = new IntersectionObserver((en) => {
      if (en[0].isIntersecting && !started) { started = true; play(0); tio.disconnect(); }
    });
    tio.observe(term);
  } else { play(0); }
})();

/* Hero particle network */
(() => {
  const cv = document.getElementById("hero-canvas");
  if (!cv || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const ctx = cv.getContext("2d");
  let w, h, dpr, pts = [], raf = 0, visible = true;
  const resize = () => {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    const r = cv.getBoundingClientRect();
    w = r.width; h = r.height;
    cv.width = w * dpr; cv.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.round(Math.min(70, (w * h) / 16000));
    pts = Array.from({ length: n }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.22, vy: (Math.random() - 0.5) * 0.22,
      r: Math.random() * 1.3 + 0.4, t: Math.random() < 0.18,
    }));
  };
  const step = () => {
    ctx.clearRect(0, 0, w, h);
    for (const p of pts) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;
    }
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        const a = pts[i], b = pts[j];
        const dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
        if (d2 < 15000) {
          ctx.strokeStyle = `rgba(215,181,122,${0.12 * (1 - d2 / 15000)})`;
          ctx.lineWidth = 0.7;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
      }
    }
    for (const p of pts) {
      ctx.fillStyle = p.t ? "rgba(143,224,221,0.8)" : "rgba(246,230,196,0.7)";
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
    }
    raf = visible ? requestAnimationFrame(step) : 0;
  };
  resize();
  window.addEventListener("resize", () => { resize(); });
  new IntersectionObserver((en) => {
    visible = en[0].isIntersecting;
    if (visible && !raf) raf = requestAnimationFrame(step);
  }).observe(cv);
  document.addEventListener("visibilitychange", () => {
    visible = !document.hidden;
    if (visible && !raf) raf = requestAnimationFrame(step);
  });
  raf = requestAnimationFrame(step);
})();
