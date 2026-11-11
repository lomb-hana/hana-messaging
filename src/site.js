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

  /* Request forms: submit via FormSubmit AJAX, then go to our own thanks page.
     The normal action + _next stay as the no-JS fallback. */
  const FS_AJAX = "https://formsubmit.co/ajax/inquiry@rivencast.com";
  const FS_ERR = "Something went wrong. Try again, or email inquiry@rivencast.com.";
  document.querySelectorAll("form.js-fs").forEach((f) => {
    const b = f.querySelector(".form-submit");
    const st = f.querySelector(".form-status");
    const thanks = f.dataset.thanks || "/thanks";
    let busy = false;
    const setBusy = (on) => {
      busy = on;
      f.classList.toggle("is-sending", on);
      if (b) { b.disabled = on; on ? b.setAttribute("aria-busy", "true") : b.removeAttribute("aria-busy"); }
    };
    const fail = () => {
      setBusy(false);
      if (st) { st.classList.add("is-error"); st.textContent = FS_ERR; }
    };
    f.addEventListener("submit", async (e) => {
      if (!window.fetch) return; /* old browsers: normal form POST */
      e.preventDefault();
      if (busy) return;
      setBusy(true);
      if (st) { st.classList.remove("is-error"); st.textContent = "Sending your request. This can take a few seconds."; }
      const fd = new FormData(f);
      if ((fd.get("_honey") || "").toString().trim() !== "") { window.location.href = thanks; return; }
      const data = {};
      fd.forEach((v, k) => { if (k !== "_honey" && k !== "_next") data[k] = v; });
      try {
        const ctrl = "AbortController" in window ? new AbortController() : null;
        const timer = ctrl ? setTimeout(() => ctrl.abort(), 45000) : 0;
        const res = await fetch(FS_AJAX, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(data),
          signal: ctrl ? ctrl.signal : undefined,
        });
        clearTimeout(timer);
        let out = {};
        try { out = JSON.parse(await res.text()); } catch (_) { out = {}; }
        if (res.ok && (out.success === true || out.success === "true")) {
          window.location.href = thanks;
        } else {
          fail();
        }
      } catch (_) {
        fail();
      }
    });
    window.addEventListener("pageshow", () => { setBusy(false); if (st && !st.classList.contains("is-error")) st.textContent = ""; });
  });

  /* SMS program disclosure: open when linked directly */
  const sms = document.getElementById("sms-program");
  const openSms = () => { if (sms && location.hash === "#sms-program") { sms.open = true; } };
  openSms(); window.addEventListener("hashchange", openSms);

  /* Prefetch internal pages on intent (hover / touch / focus) */
  if (!(HTMLScriptElement.supports && HTMLScriptElement.supports("speculationrules"))) {
    const seen = new Set();
    const pre = (e) => {
      const a = e.target.closest && e.target.closest("a[href]");
      if (!a || a.origin !== location.origin || a.pathname === location.pathname || seen.has(a.pathname) || a.hasAttribute("download")) return;
      seen.add(a.pathname);
      const l = document.createElement("link");
      l.rel = "prefetch"; l.href = a.pathname; document.head.appendChild(l);
    };
    ["pointerover", "touchstart", "focusin"].forEach((ev) => document.addEventListener(ev, pre, { passive: true }));
  }

  /* 404 path echo */
  const nfPath = document.getElementById("nf-path");
  if (nfPath) nfPath.textContent = window.location.pathname;

  /* Chat-style agent demo (illustrative, not connected) */
  const demo = document.getElementById("agent-demo");
  if (!demo) return;
  const tabs = Array.from(demo.querySelectorAll('[role="tab"]'));
  const scenes = Array.from(demo.querySelectorAll(".d-scene"));
  const input = document.getElementById("demo-input");
  const box = demo.querySelector(".d-input");
  const status = document.getElementById("demo-status");
  scenes.forEach((sc) => sc.removeAttribute("hidden"));
  let cur = 0, token = 0, paused = false, onscreen = true;
  const CANCEL = {};
  const setP = (v) => tabs[cur] && tabs[cur].querySelector("i").style.setProperty("--p", v);
  const show = (i) => {
    scenes.forEach((sc, k) => {
      const was = sc.classList.contains("is-active");
      sc.classList.toggle("is-active", k === i);
      sc.classList.toggle("is-leaving", was && k !== i);
      if (k === i) sc.classList.remove("is-leaving");
    });
    tabs.forEach((t, k) => {
      t.setAttribute("aria-selected", String(k === i));
      t.tabIndex = k === i ? 0 : -1;
      t.querySelector("i").style.setProperty("--p", k === i ? (reduce ? 1 : 0) : 0);
    });
    cur = i;
    if (status) status.textContent = scenes[i].dataset.status;
  };
  const finish = (sc) => {
    sc.querySelectorAll(".d-step").forEach((el) => el.classList.add("on", "ok", "done"));
    sc.querySelectorAll("[data-score]").forEach((b) => { b.textContent = b.dataset.score; });
  };
  input.addEventListener("pointerdown", (e) => { e.preventDefault(); tabs[cur].focus(); });

  if (reduce) {
    scenes.forEach(finish);
    show(0);
    input.value = "";
    tabs.forEach((t, i) => t.addEventListener("click", () => show(i)));
  } else {
    demo.classList.add("anim");
    scenes[0].querySelectorAll(".d-step").forEach((el) => el.classList.add("on", "ok", "done"));
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const wait = async (ms, t, holdable) => {
      let left = ms;
      while (left > 0) {
        if (t !== token) throw CANCEL;
        await sleep(Math.min(left, 40));
        if (!(holdable && paused) && onscreen && !document.hidden) left -= 40;
      }
      if (t !== token) throw CANCEL;
    };
    const count = async (el, to, t) => {
      const steps = 18;
      for (let k = 1; k <= steps; k++) {
        el.textContent = String(Math.round(to * (1 - Math.pow(1 - k / steps, 3))));
        await wait(40, t);
      }
    };
    const reset = (sc) => {
      sc.querySelectorAll(".d-step").forEach((el) => el.classList.remove("on", "ok", "done"));
      sc.querySelectorAll("[data-score]").forEach((b) => { b.textContent = "0"; });
    };
    const play = async (i, t) => {
      const sc = scenes[i];
      reset(sc);
      show(i);
      const total = 13000; let el0 = 0;
      const tick = (ms) => { el0 += ms; setP(Math.min(1, el0 / total)); };
      input.value = ""; box.classList.remove("ready", "sent");
      await wait(500, t); tick(500);
      box.classList.add("typing");
      const text = sc.dataset.prompt;
      for (let k = 1; k <= text.length; k++) {
        input.value = text.slice(0, k);
        input.scrollLeft = input.scrollWidth;
        await wait(26, t); tick(26);
      }
      box.classList.add("ready");
      await wait(380, t); tick(380);
      box.classList.add("sent");
      await wait(160, t); tick(160);
      input.value = ""; box.classList.remove("typing", "ready", "sent");
      const steps = Array.from(sc.querySelectorAll(".d-step"));
      for (const el of steps) {
        el.classList.add("on");
        if (el.classList.contains("d-line")) {
          await wait(520, t); tick(520);
          el.classList.add("ok");
          await wait(120, t); tick(120);
        } else if (el.classList.contains("d-res")) {
          const b = el.querySelector("[data-score]");
          if (b) await count(b, +b.dataset.score, t); else await wait(380, t);
          tick(720);
          el.classList.add("done");
          await wait(260, t); tick(260);
        } else if (el.classList.contains("d-stats")) {
          await Promise.all(Array.from(el.querySelectorAll("[data-score]")).map((b) => count(b, +b.dataset.score, t)));
          tick(720);
          await wait(200, t); tick(200);
        } else {
          await wait(320, t); tick(320);
        }
      }
      const hold = 5200, p0 = Math.min(0.85, el0 / total);
      for (let k = 200; k <= hold; k += 200) { await wait(200, t, true); setP(p0 + (1 - p0) * (k / hold)); }
    };
    /* First paint: show scenario 1 already answered so the console is never blank,
       then move on to the typed scenarios. */
    const intro = async (t) => {
      const sc = scenes[0];
      finish(sc); show(0);
      input.value = sc.dataset.prompt;
      const hold = 3600;
      for (let k = 100; k <= hold; k += 100) { await wait(100, t, true); setP(k / hold); }
      input.value = "";
    };
    const loop = async (start, first) => {
      const t = ++token;
      let i = start;
      try {
        if (first) { await intro(t); i = 1; }
        for (;;) { await play(i, t); i = (i + 1) % scenes.length; }
      } catch (e) { if (e !== CANCEL) throw e; }
    };
    tabs.forEach((tb, i) => tb.addEventListener("click", () => loop(i)));
    demo.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") paused = true; });
    demo.addEventListener("pointerleave", () => { paused = false; });
    demo.addEventListener("focusin", () => { paused = true; });
    demo.addEventListener("focusout", (e) => { if (!demo.contains(e.relatedTarget)) paused = false; });
    let started = false;
    new IntersectionObserver((en) => {
      onscreen = en[0].isIntersecting;
      if (onscreen && !started) { started = true; loop(0, true); }
    }).observe(demo);
  }
  /* arrow keys across tabs */
  tabs.forEach((tb, i) => tb.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    const n = (i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length;
    tabs[n].focus(); tabs[n].click();
  }));
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
    const n = Math.round(Math.min(w < 640 ? 34 : 70, (w * h) / 16000));
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
  const start = () => {
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
  };
  /* start after first paint so it never competes with content */
  ("requestIdleCallback" in window) ? requestIdleCallback(start, { timeout: 1200 }) : setTimeout(start, 300);
})();
