#!/usr/bin/env python3
"""Generate Rivencast pages with a shared head, nav, and footer.

Marketing pages are rendered from the templates below. The legal pages
(privacy.html, terms.html) keep their policy body untouched; only the
head, header chrome, hero, and footer are swapped in place.
Run: python3 tools/build_pages.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "public"
SITE = "https://rivencast.com"
BUILD = "rc-demo-2026-11-11"
CSSV = "17"

ICONS = {
  "wallet": '<rect x="3" y="6" width="18" height="13" rx="2.5"/><path d="M3 10h18M16 14.5h2"/>',
  "cart": '<circle cx="9" cy="20" r="1.4"/><circle cx="17" cy="20" r="1.4"/><path d="M3 4h2.2l2.3 11h10.3L20 8H6.3"/>',
  "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 7 8.5 6 8.5-6"/>',
  "cal": '<rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M3 10h18M8 3v4M16 3v4"/>',
  "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
  "msg": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
  "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
  "bell": '<path d="M6 16v-5a6 6 0 1 1 12 0v5l2 2H4z"/><path d="M10 21h4"/>',
  "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.2A6 6 0 0 1 21.5 20"/>',
  "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
  "drive": '<path d="M8.5 3h7l6 10.5-3.5 6h-12L2.5 13.5z"/><path d="M8.5 3l6 10.5h7M2.5 13.5h12l-3.5 6"/>',
  "bank": '<path d="M3 9.5 12 4l9 5.5M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20.5h18"/>',
  "x": '<path d="M4 4l16 16M20 4 4 20"/>',
  "plus": '<path d="M12 5v14M5 12h14"/>',
  "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/><path d="M12 14.5v2.5"/>',
  "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/>',
  "gpu": '<rect x="2.5" y="7" width="19" height="10" rx="2"/><circle cx="9" cy="12" r="2.6"/><circle cx="16" cy="12" r="2.6"/><path d="M5 17v3M19 17v3"/>',
  "ram": '<rect x="2.5" y="7" width="19" height="9" rx="1.5"/><path d="M6 10v3M9.5 10v3M13 10v3M16.5 10v3M5 16v2.5M19 16v2.5"/>',
  "layers": '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
  "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
  "shield": '<path d="M12 3 4.5 6v6c0 4.5 3.2 7.8 7.5 9 4.3-1.2 7.5-4.5 7.5-9V6z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
  "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V5a2 2 0 0 0-3-1zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 1"/>',
  "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
  "pulse": '<path d="M3 12h4l2.5-6 4 12 2.5-6H21"/>',
  "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
  "network": '<circle cx="5" cy="6" r="2.2"/><circle cx="19" cy="6" r="2.2"/><circle cx="12" cy="18" r="2.2"/><circle cx="12" cy="9.5" r="1.6"/><path d="M6.8 7.2 10.6 9M17.2 7.2 13.4 9M12 11.1v4.7"/>',
  "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
  "radar": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><path d="M12 12 18.5 5.5"/><circle cx="12" cy="12" r="1"/>',
  "doc": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
  "megaphone": '<path d="M3 10v4h3l7 4V6l-7 4z"/><path d="M17 9a4 4 0 0 1 0 6"/>',
  "flask": '<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9V3"/><path d="M7 15h10"/>',
  "building": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1M10.5 21v-3h3v3"/>',
  "mod": '<path d="M12 3 4.5 6v6c0 4.5 3.2 7.8 7.5 9 4.3-1.2 7.5-4.5 7.5-9V6z"/><path d="M9.5 11.5h5M12 9v5"/>',
  "mask": '<path d="M4 6c2.5 1 5 1.5 8 1.5S17.5 7 20 6v6a8 8 0 0 1-16 0z"/><path d="M8.5 12h2M13.5 12h2"/>',
}

def icon(name, cls="ico"):
    return f'<span class="{cls}" aria-hidden="true"><svg viewBox="0 0 24 24">{ICONS[name]}</svg></span>'

def svg(name):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

ORG = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Rivencast",
  "url": SITE + "/",
  "logo": SITE + "/assets/icon-512.png",
  "email": "inquiry@rivencast.com",
  "description": "Rivencast is an independent AI studio in Houston, Texas, building AI agents that detect bots, AI-generated content, and fake accounts across inboxes, reviews, websites, forums, and social platforms. The agents read publicly visible activity without relying on platform APIs and explain every risk score in plain language, so people make the call.",
  "address": {"@type": "PostalAddress", "addressLocality": "Houston", "addressRegion": "TX", "addressCountry": "US"},
  "contactPoint": [{"@type": "ContactPoint", "contactType": "customer support", "email": "inquiry@rivencast.com"}],
}

def head(title, desc, path, extra_ld=None, css="styles.css", noindex=False):
    canonical = SITE + path
    ld = [ORG] + (extra_ld or [])
    ld_html = "\n".join(f'  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = '\n  <meta name="robots" content="noindex" />' if noindex else ""
    canon = "" if noindex else f'\n  <link rel="canonical" href="{canonical}" />'
    return f'''<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="rc-build" content="{BUILD}" />{robots}{canon}
  <meta name="theme-color" content="#06080c" />
  <meta name="color-scheme" content="dark" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Rivencast" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{SITE}/assets/og-rivencast.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Rivencast: AI agents that catch the bots." />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{SITE}/assets/og-rivencast.png" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700&amp;family=Geist+Mono:wght@400..600&amp;display=swap" />
  <link rel="stylesheet" href="/styles.css?v={CSSV}" />{'' if css == 'styles.css' else f'''
  <link rel="stylesheet" href="/{css}?v={CSSV}" />'''}
  <script>document.documentElement.classList.add("js")</script>
{ld_html}
</head>'''

NAV = [("Home", "/"), ("Agents", "/agents.html"), ("About", "/about.html"), ("Contact", "/contact.html")]

def header(active):
    links = "\n".join(
        f'          <a href="{href}"{" aria-current=\"page\"" if name == active else ""}>{name}</a>' for name, href in NAV)
    return f'''  <a class="skip" href="#main">Skip to content</a>
  <div class="bg-fx" aria-hidden="true"><div class="grid"></div><div class="glow g1"></div><div class="glow g2"></div><div class="glow g3"></div><div class="glow g4"></div><div class="glow g5"></div><div class="noise"></div></div>
  <div class="site">
    <div class="topbar-wrap">
      <header class="topbar">
        <a class="brand" href="/" aria-label="Rivencast home">
          <img class="brand-logo" src="/assets/rivencast-logo.svg" alt="Rivencast" width="170" height="50" />
        </a>
        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
          <span class="sr-only">Menu</span>
          <span aria-hidden="true"></span>
        </button>
        <nav id="site-nav" class="links" aria-label="Primary">
{links}
          <a class="btn btn-sm nav-cta" href="mailto:inquiry@rivencast.com?subject=Rivencast%20early%20access">Early access <span class="arr" aria-hidden="true">→</span></a>
        </nav>
      </header>
    </div>'''

FOOTER = '''    <footer class="site-footer">
      <div class="foot-inner">
        <div class="foot-brand">
          <img src="/assets/rivencast-logo.svg" alt="Rivencast" width="150" height="44" />
          <p>AI agents that detect bots, AI content, and fake accounts, with plain-language reasons, so people make the call. Built in Houston, Texas.</p>
        </div>
        <div class="foot-col">
          <h2>product</h2>
          <ul>
            <li><a href="/agents.html">Detection agents</a></li>
            <li><a href="/#how">How it works</a></li>
            <li><a href="/agents/hana.html">Hana, our mascot</a></li>
            <li><a href="/#opt-in">Texting with Hana</a></li>
          </ul>
        </div>
        <div class="foot-col">
          <h2>company</h2>
          <ul>
            <li><a href="/about.html">About</a></li>
            <li><a href="/contact.html">Contact &amp; FAQ</a></li>
            <li><a href="/privacy.html">Privacy</a></li>
            <li><a href="/terms.html">Terms</a></li>
          </ul>
        </div>
        <div class="foot-col">
          <h2>contact</h2>
          <ul>
            <li><a href="mailto:inquiry@rivencast.com">inquiry@rivencast.com</a></li>
            <li><span>Text HELP to +1 (833) 408-5702</span></li>
          </ul>
        </div>
      </div>
      <div class="foot-bottom">
        <p class="foot-copy">© 2026 Daniel Jordan Reece, d/b/a Rivencast · Houston, Texas</p>
        <p class="foot-copy"><a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a></p>
      </div>
    </footer>
  </div>
  <script src="/site.js?v=''' + CSSV + '''" defer></script>'''

def page(title, desc, path, active, body, extra_ld=None, noindex=False):
    return f'''<!DOCTYPE html>
<html lang="en">
{head(title, desc, path, extra_ld, noindex=noindex)}
<body>
{header(active)}

{body}

{FOOTER}
</body>
</html>
'''


SMS_BOX = '''      <section class="section tight" id="opt-in" aria-labelledby="texting-heading">
        <div class="wrap">
          <div class="optin reveal" id="sms">
            <p class="label">sms program</p>
            <h2 id="texting-heading">Texting with Hana</h2>
            <p>
              Program name: <strong>Hana by Rivencast</strong>. You opt in by texting Hana first at
              <strong class="num">+1 (833) 408-5702</strong>.
              Messages are conversational; message frequency varies. Message and data rates may apply.
              Reply <strong>STOP</strong> to opt out, <strong>HELP</strong> for help.
              Mobile opt-in data is never shared with third parties for marketing.
              See the <a href="/privacy.html">Privacy Policy</a> and <a href="/terms.html">Terms of Service</a>.
            </p>
          </div>
        </div>
      </section>'''


NOTFOUND = '''    <main id="main" class="wrap nf">
      <div>
        <p class="label" style="justify-content:center">error</p>
        <p class="code grad-text" aria-hidden="true">404</p>
        <h1 style="font-size:clamp(1.8rem,4vw,2.6rem);margin-bottom:28px">This page wandered off.</h1>
        <div class="terminal" aria-hidden="true">
          <div class="term-bar"><i></i><i></i><i></i><span class="term-title">rivencast · lookup</span></div>
          <div class="term-body">
            <div class="ln"><span class="t-prompt">~</span><span class="t-cmd">open <span class="t-str" id="nf-path">/unknown</span></span></div>
            <div class="ln"><span class="t-arrow">→</span><span class="t-step">searching rivencast.com</span><span class="t-dim">404</span></div>
            <div class="ln"><span class="t-q">?</span><span class="t-step">try the home page instead<span class="caret"></span></span></div>
          </div>
        </div>
        <div class="hero-actions" style="justify-content:center">
          <a class="btn" href="/">Back to home <span class="arr" aria-hidden="true">→</span></a>
          <a class="btn btn-ghost" href="/agents.html">Meet the agents</a>
        </div>
      </div>
    </main>'''


EARLY = "mailto:inquiry@rivencast.com?subject=Rivencast%20early%20access"
EARLY_BTN = f'<a class="btn" href="{EARLY}">Request early access <span class="arr" aria-hidden="true">→</span></a>'
NOT_AFFIL = "Rivencast is independent and not affiliated with or endorsed by any platform named on this site."
PUBLIC_LINE = "Rivencast works from publicly visible activity and from inboxes you choose to connect. It doesn’t see private accounts, private messages, or anything behind a login without permission."

def _line(arrow, text, status, cls=""):
    return f'<div class="d-line d-step{cls}"><span class="d-arrow">{arrow}</span><span class="d-lt">{text}</span><span class="d-st" data-st="{status}"><i class="d-spin" aria-hidden="true"></i><em>{status}</em></span></div>'

def _row(user, where, score, lvl, reasons, tag=None):
    lab = tag or {"high": "likely bot", "mid": "review", "low": "likely human"}[lvl]
    if score is not None:
        left = f'<span class="d-score"><b data-score="{score}">{score}</b><small>/100</small></span>'
        detail = " · ".join(reasons)
    else:
        glyph = {"high": "✕", "mid": "!", "low": "✓"}[lvl]
        left = f'<span class="d-score d-glyph">{glyph}</span>'
        detail = where
    return f'''<div class="d-flag d-res d-step lvl-{lvl}" style="--s:{score or 0}">
                  {left}<div class="d-fbody"><div class="d-ftop"><span class="d-fuser">{user}</span><span class="scan-tag">{lab}</span></div><p>{detail}</p></div>
                </div>'''

DEMO = [
  {"key": "reddit", "tab": "r/example", "status": "scanning",
   "prompt": "Can you check r/example for any bot activity?",
   "lines": [
     _line("→", "GET <b>reddit.com/r/example/new.json?limit=100</b>", "200"),
     _line("↻", "paginate <b>after=t3_…</b> to latest 1,000 posts (listing max)", "10 pages"),
     _line("→", "GET <b>/comments/&lt;id&gt;.json</b> for each thread", "1,000 threads"),
     _line("◇", "building account timelines for 2,316 commenters", "ok"),
     _line("◇", "analyzing comments: cadence, repeats, vote timing", "ok"),
   ],
   "results": [
     _row("u/example_account", "", 94, "high", ["posts every 6 min, around the clock", "near-identical comments in 31 threads", "upvote timing cluster"]),
     _row("u/sample_poster_7", "", 81, "high", ["account 3 days old", "same link in 12 threads", "replies within 40s of u/example_account"]),
     _row("u/demo_helper", "", 64, "mid", ["templated praise with swapped product names"]),
   ],
   "summary": "flagged 3 accounts for mod review: <b>people make the call</b>"},
  {"key": "phish", "tab": "phishing sim", "status": "reading inbox",
   "prompt": "Any update on the phishing training email we sent out? Who clicked?",
   "lines": [
     _line("→", "reading connected inbox <b>security@example.com</b>", "ok"),
     _line("→", "campaign <b>“Q4 phishing awareness”</b> · internal training simulation", "found"),
     _line("◇", "matching sends, opens, clicks, and reports", "ok"),
   ],
   "stats": [("sent", 48), ("opened", 31), ("clicked", 4), ("reported", 19)],
   "results": [
     _row("j.doe@example.com", "clicked 9:14 AM · did not report", None, "high", [], tag="clicked"),
     _row("m.ortiz@example.com", "clicked 10:02 AM · reported 10:05 AM", None, "mid", [], tag="clicked"),
     _row("a.lee@example.com", "reported 8:51 AM · did not click", None, "low", [], tag="reported"),
   ],
   "summary": "suggest: assign the 5-minute refresher to <b>the 4 people who clicked</b>"},
  {"key": "watch", "tab": "page watch", "status": "watching",
   "prompt": "Monitor example.com/reviews for suspicious activity.",
   "lines": [
     _line("✓", "watch created · <b>example.com/reviews</b> · every 15 min", "on"),
     _line("→", "check 9:00 AM · 2 new reviews", "normal"),
     _line("→", "check 9:45 AM · 7 new reviews", "burst"),
     _line("◇", "comparing reviewer accounts, timing, and wording", "ok"),
   ],
   "results": [
     _row("review burst · example.com/reviews", "", 88, "high", ["7 five-star reviews in 52 min", "6 from accounts under a week old", "same phrases, reordered"], tag="alert"),
     _row("reviewer_example_3", "", 72, "mid", ["account 2 days old", "same wording as 4 other reviews"]),
     _row("reviewer_example_6", "", 66, "mid", ["first review anywhere", "posted 4 min after reviewer_example_3"]),
   ],
   "summary": "<span class=\"dot live\"></span>watching: next check in 15 min"},
]

def demo_scenes():
    out = []
    for i, d in enumerate(DEMO):
        stats = ""
        if d.get("stats"):
            stats = '<div class="d-stats d-step">' + "".join(f'<div><b data-score="{n}">{n}</b><span>{k}</span></div>' for k, n in d["stats"]) + "</div>"
        badge = '<p class="d-sim d-step">training simulation · authorized internal test</p>' if d["key"] == "phish" else ""
        lines = "\n                ".join(d["lines"])
        res = "\n                ".join(d["results"])
        active = " is-active" if i == 0 else ""
        hidden = "" if i == 0 else " hidden"
        out.append(f'''            <section class="d-scene{active}" id="demo-{d["key"]}" role="tabpanel" aria-labelledby="demo-tab-{i}" data-status="{d["status"]}" data-prompt="{d["prompt"]}"{hidden}>
              <div class="d-user d-step"><span class="d-who">you</span><p>{d["prompt"]}</p></div>
              <div class="d-agent">
                <div class="d-who d-step"><span class="d-mark">R</span>rivencast agents</div>
                {badge}
                {lines}
                {stats}
                <div class="d-results">
                {res}
                </div>
                <div class="d-sum d-step"><span>{d["summary"]}</span></div>
              </div>
            </section>''')
    return "\n".join(out)

def demo_tabs():
    return "".join(f'<button type="button" role="tab" id="demo-tab-{i}" aria-controls="demo-{d["key"]}" aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else " tabindex=\"-1\""}><span>{i+1:02d}</span>{d["tab"]}<i aria-hidden="true"></i></button>' for i, d in enumerate(DEMO))

CONSOLE = f'''<div class="terminal console agent-demo" id="agent-demo" role="region" aria-roledescription="demo" aria-label="Illustrative demo with fictional names: Rivencast agents answering three example requests">
            <div class="term-bar"><i></i><i></i><i></i><span class="term-title">rivencast · agent</span><span class="term-badge"><span class="dot live"></span><span id="demo-status">scanning</span></span></div>
            <div class="d-tabs" role="tablist" aria-label="Demo scenarios">{demo_tabs()}</div>
            <div class="d-stage" aria-live="off">
{demo_scenes()}
            </div>
            <div class="d-input">
              <input type="text" id="demo-input" readonly tabindex="-1" aria-label="Demo prompt (not connected)" placeholder="Ask Rivencast agents… (demo, not connected)" value="" />
              <button type="button" class="d-send" tabindex="-1" aria-hidden="true" disabled><svg viewBox="0 0 24 24"><path d="M12 19V5M6 11l6-6 6 6"/></svg></button>
            </div>
            <p class="demo-label">illustrative demo · fictional names, not real results</p>
          </div>'''

SIGNALS = [
  ("pulse", "Timing & cadence", "When and how often an account posts: inhumanly regular intervals, round-the-clock activity, sudden bursts."),
  ("clock", "Account age", "How old an account is, and whether that lines up with how fast and how much it’s doing."),
  ("globe", "Cross-site footprint", "Where else the same name, links, or text show up publicly, and when. Even a locked-down profile leaves a public trail elsewhere."),
  ("copy", "Repeated & templated text", "The same message, lightly reworded, dropped across reviews, threads, inboxes, and comment sections."),
  ("network", "Coordinated activity", "Groups of accounts that post, review, or reply together on a schedule, around the same targets."),
  ("spark", "AI-writing patterns", "Text that reads like it was generated: the phrasing, structure, and sameness that machine-written content tends to share."),
]

def signal_grid():
    return '<div class="grid grid-3 sig-grid">' + "".join(
        f'<article class="card reveal" style="--d:{(i%3)*0.06:.2f}s"><div class="card-top">{icon(ic)}<span class="card-idx">sig.{i+1:02d}</span></div><h3>{h}</h3><p>{p}</p></article>'
        for i, (ic, h, p) in enumerate(SIGNALS)) + "</div>"

SURFACES = [
  ("mail", "Company email", "Inboxes you connect, with your permission. Flag bot- or AI-written inbound, phishing-style automation, and fake leads."),
  ("globe", "Websites & comment sections", "Comment threads, sign-up spam, and contact-form floods on sites you run or care about."),
  ("flag", "Product & business reviews", "Review pages for products and businesses: bursts of fake praise or coordinated pile-ons."),
  ("users", "Public forums", "Community boards and discussion threads where bots farm reputation and drop links."),
  ("msg", "Social platforms", "Public posts and replies on social sites. Reddit and X are examples, not limits."),
  ("search", "Just about anywhere public", "If a person could see it on the open web, an agent can read it the same way."),
]

def surface_grid():
    return '<div class="grid grid-3">' + "".join(
        f'<article class="card reveal" style="--d:{(i%3)*0.06:.2f}s">{icon(ic)}<h3>{h}</h3><p>{p}</p></article>'
        for i, (ic, h, p) in enumerate(SURFACES)) + "</div>"

EXAMPLES = ["Reddit", "X", "review sites", "forums", "comment sections", "company inboxes", "contact forms", "blogs"]
def example_chips():
    return '<ul class="chips reveal" style="margin-top:28px" aria-label="Examples">' + "".join(f'<li class="chip">{e}</li>' for e in EXAMPLES) + "</ul>"

USES = [
  ("mail", "Businesses & inboxes", "Flag AI-written outreach, fake leads, and phishing-style automation in the inboxes you connect."),
  ("megaphone", "Brands & review integrity", "Spot fake reviews, coordinated campaigns, and bot engagement around your name."),
  ("mod", "Community moderators", "Triage suspicious accounts faster, with a reason attached to every flag."),
  ("flask", "Researchers & journalists", "Investigate inauthentic behavior with explainable scoring built on public activity."),
  ("building", "Platforms", "A second set of eyes on bots and AI content, with explanations your trust-and-safety team can audit."),
]

def use_grid():
    return '<div class="grid grid-5">' + "".join(
        f'<article class="card reveal" style="--d:{i*0.05:.2f}s">{icon(ic)}<h3>{h}</h3><p>{p}</p></article>'
        for i, (ic, h, p) in enumerate(USES)) + "</div>"

STEPS = [
  ("01 · point", "Tell it where to look", "Connect an inbox with your permission, or point the agents at a review page, a forum, a site, or an account."),
  ("02 · read", "Agents read the web", "They read publicly visible activity the way a person would (no platform API needed), fast, at scale."),
  ("03 · explain", "Score + reasons", "Each account or message gets a risk score and a plain-language explanation of why."),
  ("04 · decide", "People make the call", "Rivencast flags. You and your team review and decide what happens next."),
]

def steps(cls="flow"):
    return f'<ol class="{cls}" style="list-style:none;margin:0;padding:0">' + "".join(
        f'<li class="card reveal" style="--d:{i*0.06:.2f}s"><p class="flow-step">{a}</p><h3>{b}</h3><p>{c}</p></li>'
        for i, (a, b, c) in enumerate(STEPS)) + "</ol>"

HOME = f'''    <section class="hero" aria-labelledby="hero-heading">
      <canvas id="hero-canvas" aria-hidden="true"></canvas>
      <div class="wrap hero-grid">
        <div>
          <a class="pill reveal" href="{EARLY}"><span class="dot live" aria-hidden="true"></span>Early access · no platform API needed <span aria-hidden="true">→</span></a>
          <h1 id="hero-heading" class="reveal" style="--d:.05s">AI agents that <span class="grad-text nowrap">catch the bots.</span></h1>
          <p class="lede reveal" style="--d:.1s">
            Rivencast detects bots, AI-generated content, and fake accounts in your inbox, on review pages,
            websites, forums, and social platforms. Our AI agents read the web the way a person would, so they
            don’t depend on platform APIs. Every flag comes with a risk score and plain-language reasons, and people make the final call.
          </p>
          <div class="hero-actions reveal" style="--d:.15s">
            {EARLY_BTN}
            <a class="btn btn-ghost" href="#how">How it works</a>
          </div>
          <ul class="hero-tags reveal" style="--d:.2s" aria-label="Highlights">
            <li>no platform API needed</li>
            <li>explainable scores</li>
            <li>humans decide</li>
          </ul>
        </div>
        <div class="hero-visual reveal" style="--d:.2s">
          <div class="orb" aria-hidden="true"></div>
          {CONSOLE}
        </div>
      </div>
    </section>

    <main id="main">
      <section class="section" id="how" aria-labelledby="how-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">01</span> how it works</p>
            <h2 id="how-heading">Point it anywhere. Get a reason you can read.</h2>
            <p class="section-lede">Bots and AI-generated content leave patterns: in timing, in text, and in where an account shows up across the web. Our agents find them, score them, and write down why.</p>
          </div>
          {steps()}
        </div>
      </section>

      <hr class="hr-glow" />

      <section class="section" aria-labelledby="sig-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">02</span> signals</p>
            <h2 id="sig-heading">What the agents look at</h2>
            <p class="section-lede">No single signal makes a bot. Rivencast weighs them together and shows its work.</p>
          </div>
          {signal_grid()}
        </div>
      </section>

      <section class="section" aria-labelledby="where-heading">
        <div class="wrap">
          <div class="section-head center reveal">
            <p class="label"><span class="idx">03</span> where it works</p>
            <h2 id="where-heading">Not one platform. Just about anywhere.</h2>
            <p class="section-lede">Because the agents read publicly visible activity instead of relying on platform APIs, they work across surfaces, plus any inbox you connect.</p>
          </div>
          {surface_grid()}
          {example_chips()}
        </div>
      </section>

      <section class="section tight" aria-labelledby="out-heading">
        <div class="wrap split">
          <div class="section-head reveal">
            <p class="label"><span class="idx">04</span> no api required</p>
            <h2 id="out-heading">Reads the web like a person. Explains like an analyst.</h2>
            <p class="section-lede">A high score is a reason to look closer, never an automatic verdict.</p>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">access<small>// public web</small></div><div><strong>No platform API needed.</strong><span class="v">Agents read publicly visible activity the way a person would, so detection doesn’t depend on any platform’s API or permission.</span></div></div>
            <div class="spec-row"><div class="spec-key">footprint<small>// cross-site</small></div><div><strong>Locked profiles still leave a trail.</strong><span class="v">Rivencast can’t see inside private accounts. But where and when an account posts publicly elsewhere still tells a story.</span></div></div>
            <div class="spec-row"><div class="spec-key">email<small>// with permission</small></div><div><strong>Only inboxes you connect.</strong><span class="v">Email is scanned only when you connect it, never anyone else’s.</span></div></div>
            <div class="spec-row"><div class="spec-key">output<small>// score + reasons</small></div><div><strong>A risk score and the reasons, written out.</strong><span class="v">“2-day-old account, five 5-star reviews in an hour, AI-writing patterns.” Not a black box.</span></div></div>
            <div class="spec-row"><div class="spec-key">decision<small>// human</small></div><div><strong>People make the call.</strong><span class="v">Rivencast doesn’t ban, report, or remove anyone on its own.</span></div></div>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="use-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">05</span> use cases</p>
            <h2 id="use-heading">For anyone dealing with bots</h2>
          </div>
          {use_grid()}
          <p class="fine reveal">{NOT_AFFIL}</p>
        </div>
      </section>

      <section class="section tight" aria-labelledby="hana-heading">
        <div class="wrap">
          <div class="card cast-card reveal">
            <div>
              <p class="label"><span class="idx">06</span> our mascot</p>
              <h2 id="hana-heading">Meet Hana</h2>
              <p style="color:var(--muted);margin:14px 0 24px">The face of Rivencast: a little smug about catching bots, and the one you text to ask about Rivencast, request early access, or get help.</p>
              <div class="hero-actions" style="margin:0">
                <a class="btn btn-ghost" href="/agents/hana.html">Meet Hana <span class="arr" aria-hidden="true">→</span></a>
              </div>
            </div>
            <div class="avatars">
              <img src="/hana-avatar.png" alt="Hana, the Rivencast mascot" width="96" height="96" loading="lazy" style="width:96px;height:96px" />
            </div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="ea-heading">
        <div class="wrap">
          <div class="card cta-band reveal">
            <p class="label" style="justify-content:center">early access</p>
            <h2 id="ea-heading">Put Rivencast on your side.</h2>
            <p>We’re opening early access for businesses, brands, moderators, researchers, and platforms. Tell us where the bots are showing up and we’ll be in touch.</p>
            <div class="hero-actions">
              {EARLY_BTN}
              <a class="btn btn-ghost" href="/contact.html">Questions? Contact us</a>
            </div>
          </div>
        </div>
      </section>

{SMS_BOX}
    </main>'''

def agent_card(cls, img, name, byline, status, text, cta):
    st = {"live": '<span class="status live"><span class="dot live" aria-hidden="true"></span>available now</span>',
          "early": '<span class="status live"><span class="dot live" aria-hidden="true"></span>early access</span>',
          "soon": '<span class="status soon"><span class="dot soon" aria-hidden="true"></span>coming soon</span>'}[status]
    return f'''          <article class="card agent-card {cls} reveal">
            <div class="agent-head">
              {img}
              <div>
                <h3>{name}</h3>
                <p class="byline">{byline}</p>
              </div>
              {st}
            </div>
            <p>{text}</p>
            {cta}
          </article>'''

def fb(ic):
    return f'<div class="agent-photo-fallback" aria-hidden="true">{svg(ic)}</div>'

SOON = '<span class="btn btn-soon" aria-disabled="true">Coming soon</span>'

ROLES = [
  ("globe", "Footprint mapper", "Traces where and when an account shows up publicly across sites, and the public trail a locked profile can still leave elsewhere."),
  ("pulse", "Cadence analyst", "Looks at timing: intervals, bursts, and round-the-clock activity no person keeps up."),
  ("user", "Account profiler", "Checks account age and public history to see whether an account’s story adds up."),
  ("copy", "Text matcher", "Finds repeated and templated text, including lightly reworded copies across reviews, threads, and inboxes."),
  ("spark", "AI-text detector", "Looks for the phrasing, structure, and sameness typical of machine-generated writing."),
  ("network", "Network watcher", "Spots accounts acting together: shared timing, shared links, shared targets."),
  ("doc", "Explainer", "Rolls everything into one risk score and a plain-language reason a person can check."),
]

AGENTS = f'''    <header class="page-hero">
      <div class="wrap">
        <p class="label reveal">detection agents</p>
        <h1 class="reveal" style="--d:.05s">A team of detection agents. <span class="grad-text">One face.</span></h1>
        <p class="lede reveal" style="--d:.1s">
          Rivencast splits detection into focused AI agents, each watching one kind of signal. They read
          publicly visible activity the way a person would (no platform API needed), plus any inbox you connect.
          Their findings roll up into one risk score and one plain-language explanation. In early access.
        </p>
        <div class="hero-actions reveal" style="--d:.15s">{EARLY_BTN}</div>
      </div>
    </header>

    <main id="main">
      <section class="section tight" aria-labelledby="pipe-heading" style="padding-top:16px">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">the pipeline</p>
            <h2 id="pipe-heading">How the agents split the work</h2>
          </div>
          <div class="grid grid-4 role-grid">
{"".join(f'            <article class="card reveal" style="--d:{(i%4)*0.05:.2f}s"><div class="card-top">{icon(ic)}<span class="card-idx">agent.{i+1:02d}</span></div><h3>{h}</h3><p>{p}</p></article>{chr(10)}' for i, (ic, h, p) in enumerate(ROLES))}          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="agents-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">platform</p>
            <h2 id="agents-heading">What’s available</h2>
          </div>
          <div class="agent-grid">
{agent_card("is-live", fb("radar"), "Rivencast detection", "Bots · AI content · fake accounts", "early",
  "Detection agents for inboxes you connect, review pages, websites, public forums, and social platforms. Risk scores built from timing, account age, cross-site footprint, repeated text, coordinated activity, and AI-writing patterns, each with a plain-language explanation. People make the call.",
  EARLY_BTN)}
{agent_card("is-soon", fb("shield"), "Custom detection agents", "Tuned to you", "soon",
  "Detection agents tuned to your own rules and patterns: what counts as spam for your business or community, which signals matter most, and how flags reach your team.", SOON)}
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="face-heading">
        <div class="wrap">
          <div class="card cast-card reveal">
            <div>
              <p class="label">the face of rivencast</p>
              <h2 id="face-heading">Hana, our mascot</h2>
              <p style="color:var(--muted);margin:14px 0 24px">The agents do the detecting. Hana does the talking. Text her at <span class="mono" style="color:var(--gold-hi)">+1 (833) 408-5702</span> to ask about Rivencast, request early access, or get help.</p>
              <a class="btn btn-ghost" href="/agents/hana.html">Meet Hana <span class="arr" aria-hidden="true">→</span></a>
            </div>
            <div class="avatars"><img src="/hana-avatar.png" alt="Hana, the Rivencast mascot" width="96" height="96" loading="lazy" style="width:96px;height:96px" /></div>
          </div>
          <p class="fine reveal">{PUBLIC_LINE} {NOT_AFFIL}</p>
        </div>
      </section>
    </main>'''

QUOTES = [
  "Bots think they’re subtle. Babe, you posted forty identical comments before breakfast.",
  "I don’t ban anyone. I just tell your mods exactly why that account smells like a script.",
  "Yes, I’m an AI. Takes one to know one.",
  "Want early access? Text me. I’ll make sure the team hears about you. I’m very persuasive.",
]

HANA = f'''    <header class="wrap profile-hero">
      <div class="profile-photo-wrap reveal">
        <img class="profile-photo" src="/hana-avatar.png" alt="Hana, the Rivencast mascot" width="260" height="260" />
      </div>
      <div>
        <p class="label reveal"><span class="dot live" aria-hidden="true"></span> the face of rivencast</p>
        <h1 class="reveal" style="--d:.05s"><span class="grad-text">Hana</span></h1>
        <p class="byline reveal" style="--d:.08s">Hana by Rivencast · mascot</p>
        <p class="lede reveal" style="--d:.1s">
          Rivencast’s detection agents do the quiet work. Hana is the one with the mouth on her:
          the AI mascot you text or talk to at +1 (833) 408-5702 to ask about Rivencast,
          request early access, or get help.
        </p>
        <ul class="kv reveal" style="--d:.15s" aria-label="Hana at a glance">
          <li><b>role</b>mascot</li>
          <li><b>text</b>+1 (833) 408-5702</li>
          <li><b>vibe</b>confident, a little smug</li>
          <li><b>is</b>an AI, obviously</li>
        </ul>
      </div>
    </header>

    <main id="main">
      <section class="section" aria-labelledby="ask-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">text hana</p>
            <h2 id="ask-heading">What to text her about</h2>
          </div>
          <div class="grid grid-3">
            <article class="card reveal">{icon("radar")}<h3>Ask about Rivencast</h3><p>How the detection agents work, what signals they read, and what a risk score actually means.</p></article>
            <article class="card reveal" style="--d:.06s">{icon("flag")}<h3>Request early access</h3><p>Tell her where you’re fighting bots. She’ll pass it to the team.</p></article>
            <article class="card reveal" style="--d:.12s">{icon("msg")}<h3>Get help</h3><p>Questions about the platform or the texting program. Reply HELP anytime for help, STOP to opt out.</p></article>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="personality-heading">
        <div class="wrap two-col">
          <p class="label reveal">personality</p>
          <div class="prose reveal">
            <h2 id="personality-heading">Sassy, confident, a little smug</h2>
            <p>
              Hana knows she’s good at this and doesn’t pretend otherwise. She’s playful, quick,
              and a bit smug about catching bots, and she’ll tease you a little while she answers.
            </p>
            <p>
              Under the attitude, she’s straight with you. She’s an AI and says so. If she doesn’t
              know something, she tells you. When something’s serious, the sass takes a back seat
              and she just helps.
            </p>
            <p class="aside-note">One small request, if you’re going to hang around: don’t call her Hana Banana.</p>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="talks-heading">
        <div class="wrap two-col">
          <p class="label reveal">how she talks</p>
          <div>
            <h2 id="talks-heading" class="reveal" style="margin-bottom:12px">How she talks</h2>
            <p class="reveal" style="color:var(--muted);margin-bottom:28px">A few lines in her voice, so you know what you’re getting:</p>
            <ul class="chat">
{"".join(f'              <li class="reveal" style="--d:{i*0.08:.2f}s"><img src="/hana-avatar.png" alt="" width="36" height="36" loading="lazy" /><div class="bubble"><p>“{q}”</p></div></li>{chr(10)}' for i, q in enumerate(QUOTES))}            </ul>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="works-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">ground rules</p>
            <h2 id="works-heading">How she works with you</h2>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">01 · honest</div><div><strong>She’s an AI, and she says so.</strong><span class="v">No pretending to be a person. If she isn’t sure, she tells you.</span></div></div>
            <div class="spec-row"><div class="spec-key">02 · opt-in</div><div><strong>You text her first.</strong><span class="v">The number is only for people texting Hana directly. She doesn’t text anyone’s friends or family on their behalf.</span></div></div>
            <div class="spec-row"><div class="spec-key">03 · in control</div><div><strong>STOP means stop.</strong><span class="v">Reply STOP to opt out and HELP for help, anytime.</span></div></div>
            <div class="spec-row"><div class="spec-key">04 · private</div><div><strong>She keeps things private.</strong><span class="v">Mobile opt-in data is never shared with third parties for marketing.</span></div></div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="cta-heading">
        <div class="wrap">
          <div class="card cta-band reveal">
            <p class="label" style="justify-content:center">get in touch</p>
            <h2 id="cta-heading">Want to talk to Hana?</h2>
            <p>
              Text her at +1 (833) 408-5702. See the SMS details on the
              <a href="/#opt-in">home page</a>, plus the <a href="/privacy.html">Privacy Policy</a> and
              <a href="/terms.html">Terms of Service</a>. Prefer email? Write to
              <a href="mailto:inquiry@rivencast.com">inquiry@rivencast.com</a>.
            </p>
            <div class="hero-actions">
              <a class="btn" href="/#opt-in">Texting with Hana <span class="arr" aria-hidden="true">→</span></a>
              <a class="btn btn-ghost" href="{EARLY}">Request early access</a>
            </div>
          </div>
        </div>
      </section>
    </main>'''

STORY = [
  ("the problem", "mask", "The internet has a fake-activity problem.",
   "A lot of what looks like people online isn’t. Review pages fill up with fake and AI-written praise. Spam and scam rings run whole fleets of accounts. Sockpuppets argue with each other to make an idea look popular, and coordinated campaigns astroturf support that was never there. Sometimes it’s real people: groups that organize to brigade a thread, pile onto a business, or target someone all at once. In the inbox, it looks like phishing written to sound like a colleague and fake leads that eat a sales team’s week.",
   ["fake & AI-written reviews", "spam & scam rings", "sockpuppets", "astroturfing", "brigading", "phishing & fake leads"], ""),
  ("the gap", "lock", "Older detection looks at one site at a time.",
   "Traditional tools lean on platform APIs, per-platform rules, and blocklists. APIs can be restricted, rate-limited, or priced out of reach. Rules and blocklists are predictable, so bad actors learn to step around them by rotating accounts, wording, and domains. And because each tool watches a single platform, a network spread across reviews, forums, and social sites looks like scattered noise instead of one coordinated effort.",
   [], ""),
  ("the shift", "spark", "Agentic AI can read the web like a person.",
   "AI agents change what’s possible. An agent can open the same public pages a person would, follow an account’s footprint from one site to the next, line up when and where it posts, notice when accounts move in step, and recognize text that reads machine-written. Then it explains what it found in plain language. It does all of that at machine speed, across many sites at once. That’s a new kind of tool against suspicious activity online.",
   [], " is-shift"),
  ("what we’re building", "radar", "Rivencast builds those detection agents.",
   "Rivencast is a studio building detection agents for businesses, brands, moderators, researchers, and platforms. They work from publicly visible activity and from inboxes customers choose to connect, never private accounts or anything behind a login without permission. Every flag comes with a risk score and the reasons behind it, and people make the final call. The goal is simple: make it much harder for fake activity to pass as real.",
   [], ""),
  ("what powers it", "gpu", "Serious hardware underneath.",
   "Reading the web at this pace takes real compute. Rivencast agents utilize dedicated AI servers with server-grade processors, NVIDIA H200 NVL GPUs, and ECC DDR5 memory.",
   [], ""),
]

def story_steps():
    out = []
    for i, (kicker, ic, title, body, tags, extra) in enumerate(STORY):
        tag_html = ""
        if tags:
            tag_html = '<ul class="story-tags" aria-label="Examples">' + "".join(f"<li>{t}</li>" for t in tags) + "</ul>"
        link = ""
        if kicker == "what powers it":
            link = '<a class="story-link" href="#hardware">See the hardware <span aria-hidden="true">↓</span></a>'
        out.append(f'''            <li class="story-step{extra} reveal" style="--d:{i*0.06:.2f}s">
              <div class="story-node" aria-hidden="true">{icon(ic)}</div>
              <div class="card story-card">
                <p class="story-kicker"><span>{i+1:02d}</span> {kicker}</p>
                <h3>{title}</h3>
                <p>{body}</p>
                {tag_html}{link}
              </div>
            </li>''')
    return "\n".join(out)

ABOUT = f'''    <header class="page-hero">
      <div class="wrap">
        <p class="label reveal">about us</p>
        <h1 class="reveal" style="--d:.05s">An independent AI studio <span class="grad-text nowrap">in Houston.</span></h1>
        <p class="lede reveal" style="--d:.1s">
          Rivencast builds AI agents that detect bots, AI-generated content, and fake accounts, and explain
          their reasoning so people can make better calls.
        </p>
      </div>
    </header>

    <main id="main">
      <section class="section tight story-section" aria-labelledby="story-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">01</span> why we exist</p>
            <h2 id="story-heading">Fake activity keeps getting smarter. Detection has to catch up.</h2>
            <p class="section-lede">The problem we see online, why older tools keep missing it, and what agentic AI makes possible now.</p>
          </div>
          <ol class="story">
{story_steps()}
          </ol>
        </div>
      </section>

      <hr class="hr-glow" />
      <section class="section tight" aria-labelledby="what-heading">
        <div class="wrap two-col">
          <p class="label reveal"><span class="idx">02</span> the studio</p>
          <div class="prose reveal">
            <h2 id="what-heading">What Rivencast is</h2>
            <p>
              Rivencast is an independent AI studio in Houston, Texas. We build AI agents that find bots,
              AI-generated content, and automated or inauthentic accounts: the fake reviews, spam leads,
              karma farms, and coordinated networks that wear down businesses and communities.
            </p>
            <p>
              Our agents read the web the way a person would. They look at publicly visible activity: when and
              where accounts post, how old they are, what their text looks like, and who they move in step with,
              so detection doesn’t depend on any platform’s API. For email, they work only on inboxes a
              customer chooses to connect. {PUBLIC_LINE}
            </p>
            <p>
              The platform is in <strong>early access</strong>. Our mascot, <strong>Hana</strong>, is the
              face of Rivencast. You can <a href="/#sms">text her</a> at +1 (833) 408-5702 to ask about
              Rivencast, request early access, or get help.
            </p>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="how-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">03</span> how the agents work</p>
            <h2 id="how-heading">Focused agents, one explanation</h2>
            <p class="section-lede">
              Instead of one opaque model making a call, Rivencast splits the job: separate agents each
              examine one kind of signal (timing, account age, cross-site footprint, repeated text,
              coordinated activity, AI-writing patterns), and their findings are combined into a single risk
              score with a plain-language explanation. Fast, at scale.
            </p>
          </div>
          {steps()}
        </div>
      </section>

      <hr class="hr-glow" />

      <section class="section" aria-labelledby="principles-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">04</span> principles</p>
            <h2 id="principles-heading">How we build detection</h2>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">explainable<small>// show the work</small></div><div><strong>Every score comes with reasons.</strong><span class="v">If an agent can’t explain a flag in plain language, it shouldn’t be making one.</span></div></div>
            <div class="spec-row"><div class="spec-key">human<small>// final say</small></div><div><strong>People make the call.</strong><span class="v">Rivencast supports businesses, moderators, and teams. It doesn’t ban, report, or remove anyone on its own.</span></div></div>
            <div class="spec-row"><div class="spec-key">public<small>// data</small></div><div><strong>Publicly visible activity, or your permission.</strong><span class="v">Agents read what any visitor could see on the open web, plus inboxes a customer connects. Nothing private, nothing behind a login without permission.</span></div></div>
            <div class="spec-row"><div class="spec-key">careful<small>// not a verdict</small></div><div><strong>A score is a signal, not proof.</strong><span class="v">Real people can look unusual, and some bots look ordinary. Scores point a human at what deserves a closer look.</span></div></div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="made-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">05</span> how they’re made</p>
            <h2 id="made-heading">Shaped on top of models, tuned for detection</h2>
            <p class="section-lede">
              Rivencast does not train its own foundation model. The intelligence underneath comes from
              established language models. What we build is the agents, the detection logic, and the way
              findings are explained, tuned on top of those models and tested until they hold up.
            </p>
          </div>
        </div>
      </section>

      <section class="section" id="hardware" aria-labelledby="hardware-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">06</span> the hardware</p>
            <h2 id="hardware-heading">What Rivencast agents run on</h2>
            <p class="section-lede">
              Rivencast agents utilize dedicated servers built for AI work: server-grade processors,
              NVIDIA H200 NVL data-center GPUs, and high-capacity ECC DDR5 memory.
            </p>
          </div>
          <div class="grid grid-4 hw">
            <article class="card reveal"><div class="card-top">{icon("cpu")}<span class="hw-tag">CPU</span></div><h3>Server-grade processors</h3><p>Multi-core data-center CPUs handle everything around the model: reading the web, scheduling scans, and keeping every job moving.</p></article>
            <article class="card reveal" style="--d:.06s"><div class="card-top">{icon("gpu")}<span class="hw-tag">GPU</span></div><h3>NVIDIA H200 NVL</h3><p>Hopper-generation data-center GPUs with large, fast HBM3e memory, linked over NVIDIA NVLink, built to run large models quickly.</p></article>
            <article class="card reveal" style="--d:.12s"><div class="card-top">{icon("ram")}<span class="hw-tag">RAM</span></div><h3>ECC DDR5 memory</h3><p>Error-correcting server memory keeps long-running work stable and accurate.</p></article>
            <article class="card reveal" style="--d:.18s"><div class="card-top">{icon("layers")}<span class="hw-tag">MODELS</span></div><h3>Shaped on top, not trained from scratch</h3><p>Rivencast does not train its own foundation model. Agents are shaped and tuned on top of models for detection and explanation.</p></article>
          </div>
          <p class="fine reveal">{NOT_AFFIL}</p>
        </div>
      </section>

      <section class="section tight" aria-labelledby="cta-heading">
        <div class="wrap">
          <div class="card cta-band reveal">
            <p class="label" style="justify-content:center">get in touch</p>
            <h2 id="cta-heading">Want Rivencast on your side?</h2>
            <p>
              Write to <a href="mailto:inquiry@rivencast.com">inquiry@rivencast.com</a> for early access or questions.
              To text Hana, see the SMS details on the <a href="/#opt-in">home page</a>,
              plus the <a href="/privacy.html">Privacy Policy</a> and <a href="/terms.html">Terms of Service</a>.
            </p>
            <div class="hero-actions">
              {EARLY_BTN}
              <a class="btn btn-ghost" href="/agents.html">See the agents</a>
            </div>
          </div>
        </div>
      </section>
    </main>'''

FAQ = [
  ("What is Rivencast?",
   "<p>Rivencast is an AI-agent detection service for bots, AI-generated content, and automated or inauthentic accounts. The agents give each account or message a risk score and explain it in plain language, so people can decide what to do.</p>"),
  ("Where does it work?",
   f"<p>Just about anywhere activity is publicly visible: product and business reviews, websites and comment sections, public forums, and social platforms like Reddit or X, plus company inboxes you choose to connect. {NOT_AFFIL}</p>"),
  ("Do you need API access?",
   "<p>No. Rivencast’s agents read publicly visible activity the way a person would, so detection doesn’t depend on platform APIs. For email, you connect the inboxes you want checked.</p>"),
  ("Can you see private accounts?",
   "<p>No. Rivencast doesn’t see private accounts, private messages, or anything behind a login without permission. But even when a profile is locked down, an account’s public footprint elsewhere (where and when it posts publicly) can still tell a story.</p>"),
  ("What signals do the agents look at?",
   "<p>Timing and posting cadence, account age, cross-site footprint, repeated or templated text, coordinated activity between accounts, and AI-writing patterns.</p>"),
  ("Does it work on company email?",
   "<p>Yes, for inboxes your company connects with permission. The agents can flag bot- or AI-written inbound messages, phishing-style automation, and fake leads.</p>"),
  ("Does Rivencast ban or remove accounts?",
   "<p>No. Rivencast flags and explains. You and your team review the flags and make the call.</p>"),
  ("Is a high risk score proof?",
   "<p>No. A score is a signal that something deserves a closer look, with the reasons written out. Real people can look unusual, and some bots look ordinary.</p>"),
  ("How do I get early access?",
   f'<p>Email <a href="{EARLY}">inquiry@rivencast.com</a> and tell us where bots are showing up for you, or text Hana and she’ll pass it to the team.</p>'),
  ("Who is Hana?",
   "<p>Hana is Rivencast’s mascot, an AI with a confident, slightly smug personality. She’s the one you text or talk to about Rivencast, early access, or help. She’s an AI and says so.</p>"),
  ("How does texting Hana work?",
   '<p>You opt in by texting Hana first at +1 (833) 408-5702. Messages are conversational; message frequency varies. Message and data rates may apply. Reply STOP to opt out, HELP for help. Mobile opt-in data is never shared with third parties for marketing. Details are in the <a href="/privacy.html">Privacy Policy</a> and <a href="/terms.html">Terms of Service</a>.</p>'),
  ("Will Hana text my friends or family?",
   "<p>No. The number is only for people texting Hana directly. Hana doesn’t text anyone’s friends or family on their behalf.</p>"),
  ("Does Rivencast train its own AI model?",
   "<p>No. The intelligence underneath comes from established language models. Rivencast builds the detection agents, the detection logic, and the explanations on top of them.</p>"),
]

def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()

FAQ_LD = {
  "@context": "https://schema.org", "@type": "FAQPage",
  "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in FAQ],
}

CONTACT = f'''    <header class="page-hero">
      <div class="wrap">
        <p class="label reveal">contact</p>
        <h1 class="reveal" style="--d:.05s">Talk to <span class="grad-text">Rivencast.</span></h1>
        <p class="lede reveal" style="--d:.1s">Early access, partnerships, research, press, or help. We read every message.</p>
      </div>
    </header>

    <main id="main">
      <section class="section tight" aria-labelledby="reach-heading" style="padding-top:16px">
        <div class="wrap">
          <h2 id="reach-heading" class="sr-only">Ways to reach us</h2>
          <div class="grid grid-2">
            <article class="card contact-card reveal">
              {icon("mail")}
              <p class="label no-slash" style="margin:0">email</p>
              <p class="big">inquiry@rivencast.com</p>
              <p style="color:var(--muted)">For early access, questions about how detection works, your data, or anything in our policies.</p>
              {EARLY_BTN}
            </article>
            <article class="card contact-card reveal" style="--d:.06s">
              {icon("phone")}
              <p class="label no-slash" style="margin:0">text hana</p>
              <p class="big">+1 (833) 408-5702</p>
              <p style="color:var(--muted)">Text Hana, our mascot, to ask about Rivencast, request early access, or get help. You opt in by texting her first. Reply STOP to opt out, HELP for help. Message and data rates may apply.</p>
              <a class="btn btn-ghost" href="/#opt-in">SMS program details</a>
            </article>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="faq-heading">
        <div class="wrap">
          <div class="section-head center reveal">
            <p class="label">faq</p>
            <h2 id="faq-heading">Frequently asked questions</h2>
          </div>
          <div class="faq reveal">
{"".join(f'            <details><summary>{q}</summary><div class="ans">{a}</div></details>{chr(10)}' for q, a in FAQ)}          </div>
        </div>
      </section>
    </main>'''

PAGES = {
  "index.html": ("Rivencast: AI agents that catch the bots",
                 "Rivencast detects bots, AI-generated content, and fake accounts across inboxes, reviews, websites, forums, and social platforms. No platform API needed. Explainable risk scores; people decide. Early access.",
                 "/", "Home", HOME, None),
  "agents.html": ("Detection agents | Rivencast",
                  "How Rivencast’s detection agents work: focused AI agents that read publicly visible activity and roll their findings into one risk score with a plain-language explanation. Early access.",
                  "/agents.html", "Agents", AGENTS, None),
  "agents/hana.html": ("Hana, the Rivencast mascot",
                       "Meet Hana, Rivencast’s sassy AI mascot. Text her at +1 (833) 408-5702 to ask about Rivencast, request early access, or get help.",
                       "/agents/hana.html", "Agents", HANA, None),
  "about.html": ("About Us | Rivencast",
                 "Rivencast is an independent AI studio in Houston building AI agents that detect bots, AI-generated content, and fake accounts, with explainable risk scores and people making the call.",
                 "/about.html", "About", ABOUT, None),
  "contact.html": ("Contact & FAQ | Rivencast",
                   "Contact Rivencast at inquiry@rivencast.com for early access, learn how texting Hana works, and get answers about our AI detection agents.",
                   "/contact.html", "Contact", CONTACT, [FAQ_LD]),
  "404.html": ("Page not found | Rivencast", "This page could not be found on rivencast.com.",
               "/404.html", None, NOTFOUND, None),
}


def build_marketing():
    for name, (title, desc, path, active, body, ld) in PAGES.items():
        html = page(title, desc, path, active, body, ld, noindex=(name == "404.html"))
        (ROOT / name).write_text(html, encoding="utf-8")
        print("wrote", name)

LEGAL = {
  "privacy.html": ("Privacy Policy | Rivencast", "Privacy Policy for Rivencast / Hana by Rivencast, operated by Daniel Jordan Reece.", "/privacy.html"),
  "terms.html": ("Terms of Service | Rivencast", "Terms of Service for Rivencast, operated by Daniel Jordan Reece, doing business as Rivencast.", "/terms.html"),
}

def build_legal():
    for name, (title, desc, path) in LEGAL.items():
        p = ROOT / name
        src = p.read_text(encoding="utf-8")
        # head
        src = re.sub(r"<head>.*?</head>", lambda m: head(title, desc, path, css="legal.css"), src, count=1, flags=re.S)
        # header chrome: from skip link up to the legal hero section
        m = re.search(r'<section class="legal-hero[^"]*">.*?</section>', src, flags=re.S)
        hero = m.group(0)
        hero_inner = re.search(r'<p class="eyebrow">Legal</p>(.*?)</div>\s*</section>', hero, flags=re.S)
        if hero_inner:
            inner = hero_inner.group(1)
            hero = f'''<section class="legal-hero wrap">
      <div>
        <p class="label">legal</p>{inner}</div>
    </section>'''
        start = src.index('<a class="skip"')
        src = src[:start] + header(None).lstrip() + "\n\n    " + hero + src[m.end():]
        # footer
        fstart = src.index('<footer class="site-footer">')
        fstart = src.rfind("\n", 0, fstart) + 1
        src = src[:fstart] + FOOTER + "\n</body>\n</html>\n"
        p.write_text(src, encoding="utf-8")
        print("patched", name)

if __name__ == "__main__":
    build_marketing()
    build_legal()
