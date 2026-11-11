/* Rivencast site interactions (rc-tech) */
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

  /* Detection console demo (illustrative) */
  const list = document.getElementById("scan-list");
  if (!list || reduce) return;
  const rows = Array.from(list.querySelectorAll(".scan-row"));
  const foot = document.querySelector(".scan-foot");
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const count = (el, to, ms) => new Promise((res) => {
    const t0 = performance.now();
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / ms);
      el.textContent = String(Math.round(to * (1 - Math.pow(1 - k, 3))));
      k < 1 ? requestAnimationFrame(tick) : res();
    };
    requestAnimationFrame(tick);
  });
  const run = async () => {
    list.classList.add("animating");
    rows.forEach((r) => r.classList.remove("on", "done"));
    if (foot) foot.classList.remove("on");
    await sleep(500);
    for (const r of rows) {
      r.classList.add("on");
      const b = r.querySelector("[data-score]");
      await count(b, +b.dataset.score, 900);
      r.classList.add("done");
      await sleep(350);
    }
    if (foot) foot.classList.add("on");
    await sleep(6000);
    run();
  };
  let started = false;
  new IntersectionObserver((en, obs) => {
    if (en[0].isIntersecting && !started) { started = true; obs.disconnect(); run(); }
  }).observe(list);
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
