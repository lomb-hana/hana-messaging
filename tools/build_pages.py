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
BUILD = "rc-pivot-2026-11-11"
CSSV = "14"

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
  "description": "Rivencast is an independent AI studio in Houston, Texas, building an AI agent platform for bot detection. Starting with Reddit, its agents score accounts from publicly available signals and explain why in plain language, so people make the call.",
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
  <meta property="og:image:alt" content="Rivencast — AI agents that catch the bots." />
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
          <p>AI agents for bot detection. Risk scores with plain-language reasons, so people make the call. Built in Houston, Texas.</p>
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
          <div class="term-bar"><i></i><i></i><i></i><span class="term-title">rivencast — lookup</span></div>
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
NOT_AFFIL = "Rivencast is independent and not affiliated with or endorsed by Reddit. It works from publicly available data."

SCAN_ROWS = [
  ("u/example_account", 94, "high", ["account is 3 days old", "41 comments in 2 hours", "87% near-identical text across 9 subs"]),
  ("u/not_a_bot_9000", 81, "high", ["posts every 6 min, around the clock", "karma farmed in repost-heavy subs"]),
  ("u/sample_user_42", 52, "mid", ["new account, bursty activity", "links repeated in 4 threads"]),
  ("u/demo_regular", 9, "low", ["6-year-old account", "varied, human-paced history"]),
]

def scan_rows():
    out = []
    for i, (u, sc, lvl, rs) in enumerate(SCAN_ROWS):
        lab = {"high": "likely bot", "mid": "review", "low": "likely human"}[lvl]
        reasons = "".join(f"<li>{r}</li>" for r in rs)
        out.append(f'''              <div class="scan-row lvl-{lvl}" style="--s:{sc}">
                <div class="scan-top"><span class="scan-user">{u}</span><span class="scan-score"><b data-score="{sc}">{sc}</b><small>/100</small></span></div>
                <div class="scan-bar"><i></i></div>
                <div class="scan-meta"><span class="scan-tag">{lab}</span><ul class="scan-why">{reasons}</ul></div>
              </div>''')
    return "\n".join(out)

CONSOLE = f'''<div class="terminal console" role="img" aria-label="Illustrative demo: a Rivencast detection console scoring four fictional Reddit usernames with risk scores and plain-language reasons">
            <div class="term-bar" aria-hidden="true"><i></i><i></i><i></i><span class="term-title">rivencast · scan r/example</span><span class="term-badge"><span class="dot live"></span>scanning</span></div>
            <div class="term-body" aria-hidden="true">
              <div class="ln"><span class="t-prompt">~</span><span class="t-cmd">rivencast scan <span class="t-str">r/example</span> --signals public</span></div>
              <div class="ln scan-status"><span class="t-arrow">→</span><span class="t-step">reading public account history · 4 accounts</span><span class="t-ok">ok</span></div>
              <div class="scan-list" id="scan-list">
{scan_rows()}
              </div>
              <div class="ln scan-foot"><span class="t-q">?</span><span class="t-step">flagged for mod review — <span class="t-wait">people make the call</span><span class="caret"></span></span></div>
            </div>
            <p class="demo-label">illustrative demo · fictional accounts, not real results</p>
          </div>'''

SIGNALS = [
  ("clock", "Account age", "How old the account is, and how that lines up with how fast it’s acting."),
  ("pulse", "Posting cadence & timing", "Inhumanly regular intervals, round-the-clock activity, and sudden bursts."),
  ("chart", "Karma patterns", "Karma farmed fast in repost-heavy communities, or karma that doesn’t match the history."),
  ("copy", "Templated & repeated text", "The same comment, lightly reworded, dropped across threads and communities."),
  ("network", "Coordinated activity", "Groups of accounts that post, vote-bait, or reply together on a schedule."),
  ("doc", "History in context", "The account’s full public history — so one odd day doesn’t become a verdict."),
]

def signal_grid():
    return '<div class="grid grid-3 sig-grid">' + "".join(
        f'<article class="card reveal" style="--d:{(i%3)*0.06:.2f}s"><div class="card-top">{icon(ic)}<span class="card-idx">sig.{i+1:02d}</span></div><h3>{h}</h3><p>{p}</p></article>'
        for i, (ic, h, p) in enumerate(SIGNALS)) + "</div>"

USES = [
  ("mod", "Moderators", "Triage new accounts and suspicious threads faster, with a reason attached to every flag instead of a gut feeling."),
  ("megaphone", "Brands", "Spot coordinated campaigns and fake engagement around your name before you respond to them as if they were real people."),
  ("flask", "Researchers", "Study inauthentic behavior with consistent, explainable scoring built from publicly available signals."),
  ("building", "Platforms & communities", "Add a second set of eyes on bot activity, with explanations your trust-and-safety team can audit."),
]

def use_grid():
    return '<div class="grid grid-4">' + "".join(
        f'<article class="card reveal" style="--d:{i*0.06:.2f}s">{icon(ic)}<h3>{h}</h3><p>{p}</p></article>'
        for i, (ic, h, p) in enumerate(USES)) + "</div>"

STEPS = [
  ("01 · collect", "Public signals in", "Agents read publicly available account data: age, history, timing, karma, and text."),
  ("02 · analyze", "Patterns scored", "Each signal is checked against bot-like patterns, alone and across accounts."),
  ("03 · explain", "Reasons attached", "Every account gets a risk score and a plain-language explanation of why."),
  ("04 · decide", "People make the call", "Rivencast flags. Moderators and teams review and decide what happens next."),
]

def steps(cls="flow"):
    return f'<ol class="{cls}" style="list-style:none;margin:0;padding:0">' + "".join(
        f'<li class="card reveal" style="--d:{i*0.06:.2f}s"><p class="flow-step">{a}</p><h3>{b}</h3><p>{c}</p></li>'
        for i, (a, b, c) in enumerate(STEPS)) + "</ol>"

HOME = f'''    <section class="hero" aria-labelledby="hero-heading">
      <canvas id="hero-canvas" aria-hidden="true"></canvas>
      <div class="wrap hero-grid">
        <div>
          <a class="pill reveal" href="{EARLY}"><span class="dot live" aria-hidden="true"></span>Early access · Reddit first <span aria-hidden="true">→</span></a>
          <h1 id="hero-heading" class="reveal" style="--d:.05s">AI agents that <span class="grad-text nowrap">catch the bots.</span></h1>
          <p class="lede reveal" style="--d:.1s">
            Rivencast is a bot-detection platform run by AI agents. Starting with Reddit, our agents read
            publicly available account signals and return a risk score with a plain-language explanation —
            so moderators and teams can make the call with the reasons in front of them.
          </p>
          <div class="hero-actions reveal" style="--d:.15s">
            {EARLY_BTN}
            <a class="btn btn-ghost" href="#how">How it works</a>
          </div>
          <ul class="hero-tags reveal" style="--d:.2s" aria-label="Highlights">
            <li>public data only</li>
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
            <h2 id="how-heading">From public signals to a reason you can read.</h2>
            <p class="section-lede">Bots leave patterns. Our agents look for them across an account’s public footprint, score what they find, and write down why — in words a moderator can check in seconds.</p>
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

      <section class="section tight" aria-labelledby="out-heading">
        <div class="wrap split">
          <div class="section-head reveal">
            <p class="label"><span class="idx">03</span> what you get</p>
            <h2 id="out-heading">A score, a reason, and the final say.</h2>
            <p class="section-lede">Rivencast is built to support human judgment, not replace it. A high score is a reason to look closer — never an automatic verdict.</p>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">risk_score<small>// 0–100</small></div><div><strong>A risk score per account.</strong><span class="v">How bot-like the account’s public behavior looks, so you can sort the queue.</span></div></div>
            <div class="spec-row"><div class="spec-key">explanation<small>// plain language</small></div><div><strong>The reasons, written out.</strong><span class="v">“3-day-old account, 41 comments in 2 hours, mostly near-identical text.” Not a black box.</span></div></div>
            <div class="spec-row"><div class="spec-key">decision<small>// human</small></div><div><strong>People make the call.</strong><span class="v">Moderators and teams review flags and decide. Rivencast doesn’t ban, report, or remove anyone.</span></div></div>
            <div class="spec-row"><div class="spec-key">data<small>// public only</small></div><div><strong>Publicly available data.</strong><span class="v">{NOT_AFFIL}</span></div></div>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="use-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">04</span> use cases</p>
            <h2 id="use-heading">Built for the people cleaning up</h2>
          </div>
          {use_grid()}
        </div>
      </section>

      <section class="section tight" aria-labelledby="hana-heading">
        <div class="wrap">
          <div class="card cast-card reveal">
            <div>
              <p class="label"><span class="idx">05</span> our mascot</p>
              <h2 id="hana-heading">Meet Hana</h2>
              <p style="color:var(--muted);margin:14px 0 24px">The face of Rivencast — a little smug about catching bots, and the one you text to ask about the platform, request early access, or get help.</p>
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
            <h2 id="ea-heading">Bring Rivencast to your community.</h2>
            <p>We’re opening early access for moderators, brands, researchers, and platforms. Tell us where you’re fighting bots and we’ll be in touch.</p>
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
  ("user", "Account profiler", "Reads account age, karma, and public history to see whether an account’s story adds up."),
  ("pulse", "Cadence analyst", "Looks at when and how often an account posts — intervals, bursts, and round-the-clock activity."),
  ("copy", "Text matcher", "Finds templated and repeated text, including lightly reworded copies across threads."),
  ("network", "Network watcher", "Spots accounts acting together: shared timing, shared links, shared targets."),
  ("doc", "Explainer", "Turns the findings into a risk score and a plain-language reason a moderator can check."),
]

AGENTS = f'''    <header class="page-hero">
      <div class="wrap">
        <p class="label reveal">detection agents</p>
        <h1 class="reveal" style="--d:.05s">A team of detection agents. <span class="grad-text">One face.</span></h1>
        <p class="lede reveal" style="--d:.1s">
          Rivencast splits bot detection into focused AI agents, each watching one kind of signal in publicly
          available data. Their findings roll up into one risk score and one plain-language explanation.
          Reddit first, in early access.
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
          <div class="grid grid-5 role-grid">
{"".join(f'            <article class="card reveal" style="--d:{i*0.05:.2f}s"><div class="card-top">{icon(ic)}<span class="card-idx">agent.{i+1:02d}</span></div><h3>{h}</h3><p>{p}</p></article>{chr(10)}' for i, (ic, h, p) in enumerate(ROLES))}          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="agents-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">platform</p>
            <h2 id="agents-heading">What’s available</h2>
          </div>
          <div class="agent-grid">
{agent_card("is-live", fb("radar"), "Reddit bot detection", "Rivencast platform", "early",
  "Detection agents scoring Reddit accounts from publicly available signals — account age, posting cadence and timing, karma patterns, templated text, and coordinated activity — each with a plain-language explanation. Moderators and teams make the call.",
  EARLY_BTN)}
{agent_card("is-soon", fb("shield"), "Custom detection agents", "For your community", "soon",
  "Detection agents tuned to your community’s own rules and patterns — what counts as spam where you are, which signals matter most, and how flags reach your moderators.", SOON)}
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="face-heading">
        <div class="wrap">
          <div class="card cast-card reveal">
            <div>
              <p class="label">the face of rivencast</p>
              <h2 id="face-heading">Hana, our mascot</h2>
              <p style="color:var(--muted);margin:14px 0 24px">The agents do the detecting. Hana does the talking — text her at <span class="mono" style="color:var(--gold-hi)">+1 (833) 408-5702</span> to ask about Rivencast, request early access, or get help.</p>
              <a class="btn btn-ghost" href="/agents/hana.html">Meet Hana <span class="arr" aria-hidden="true">→</span></a>
            </div>
            <div class="avatars"><img src="/hana-avatar.png" alt="Hana, the Rivencast mascot" width="96" height="96" loading="lazy" style="width:96px;height:96px" /></div>
          </div>
          <p class="fine reveal">{NOT_AFFIL}</p>
        </div>
      </section>
    </main>'''

QUOTES = [
  "Bots think they’re subtle. Babe, you posted forty identical comments before breakfast.",
  "I don’t ban anyone. I just tell your mods exactly why that account smells like a script.",
  "Yes, I’m an AI. Takes one to know one.",
  "Want early access? Text me. I’ll make sure the team hears about you — I’m very persuasive.",
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
          Rivencast’s detection agents do the quiet work. Hana is the one with the mouth on her —
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
              and a bit smug about catching bots — and she’ll tease you a little while she answers.
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
              Text her at +1 (833) 408-5702 — see the SMS details on the
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

ABOUT = f'''    <header class="page-hero">
      <div class="wrap">
        <p class="label reveal">about us</p>
        <h1 class="reveal" style="--d:.05s">An independent AI studio <span class="grad-text nowrap">in Houston.</span></h1>
        <p class="lede reveal" style="--d:.1s">
          Rivencast builds AI agents for bot detection — agents that read public signals, score
          accounts, and explain their reasoning so people can make better calls.
        </p>
      </div>
    </header>

    <main id="main">
      <section class="section tight" aria-labelledby="what-heading">
        <div class="wrap two-col">
          <p class="label reveal"><span class="idx">01</span> the studio</p>
          <div class="prose reveal">
            <h2 id="what-heading">What Rivencast is</h2>
            <p>
              Rivencast is an independent AI studio in Houston, Texas. We build AI agents that detect
              bots — the spam accounts, karma farms, and coordinated networks that wear down online communities.
            </p>
            <p>
              We’re starting with Reddit. Our agents work from publicly available data: how old an
              account is, when and how often it posts, how its karma was earned, whether its text is
              templated or repeated, and whether it moves in step with other accounts. {NOT_AFFIL}
            </p>
            <p>
              The platform is in <strong>early access</strong>. Our mascot, <strong>Hana</strong>, is the
              face of Rivencast — you can <a href="/#sms">text her</a> at +1 (833) 408-5702 to ask about
              the platform, request early access, or get help.
            </p>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="how-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">02</span> how the agents work</p>
            <h2 id="how-heading">Focused agents, one explanation</h2>
            <p class="section-lede">
              Instead of one opaque model making a call, Rivencast splits the job: separate agents each
              examine one kind of signal, then their findings are combined into a single risk score and
              written up as a plain-language explanation.
            </p>
          </div>
          {steps()}
        </div>
      </section>

      <hr class="hr-glow" />

      <section class="section" aria-labelledby="principles-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">03</span> principles</p>
            <h2 id="principles-heading">How we build detection</h2>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">explainable<small>// show the work</small></div><div><strong>Every score comes with reasons.</strong><span class="v">If an agent can’t explain a flag in plain language, it shouldn’t be making one.</span></div></div>
            <div class="spec-row"><div class="spec-key">human<small>// final say</small></div><div><strong>People make the call.</strong><span class="v">Rivencast supports moderators and teams. It doesn’t ban, report, or remove anyone on its own.</span></div></div>
            <div class="spec-row"><div class="spec-key">public<small>// data</small></div><div><strong>Publicly available data.</strong><span class="v">The agents work from what any visitor could see on a public profile or thread.</span></div></div>
            <div class="spec-row"><div class="spec-key">careful<small>// not a verdict</small></div><div><strong>A score is a signal, not proof.</strong><span class="v">Real people can look unusual, and some bots look ordinary. Scores are built to point a human at what deserves a closer look.</span></div></div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="made-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">04</span> how they’re made</p>
            <h2 id="made-heading">Shaped on top of models, tuned for detection</h2>
            <p class="section-lede">
              Rivencast does not train its own foundation model. The intelligence underneath comes from
              established language models. What we build is the agents, the detection logic, and the way
              findings are explained — tuned on top of those models and tested until they hold up.
            </p>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="hardware-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">05</span> the hardware</p>
            <h2 id="hardware-heading">What Rivencast agents run on</h2>
            <p class="section-lede">
              Rivencast agents utilize dedicated servers built for AI work: server-grade processors,
              NVIDIA H200 NVL data-center GPUs, and high-capacity ECC DDR5 memory.
            </p>
          </div>
          <div class="grid grid-4 hw">
            <article class="card reveal"><div class="card-top">{icon("cpu")}<span class="hw-tag">CPU</span></div><h3>Server-grade processors</h3><p>Multi-core data-center CPUs handle everything around the model: collecting public signals, scheduling scans, and keeping every job moving.</p></article>
            <article class="card reveal" style="--d:.06s"><div class="card-top">{icon("gpu")}<span class="hw-tag">GPU</span></div><h3>NVIDIA H200 NVL</h3><p>Hopper-generation data-center GPUs with large, fast HBM3e memory, linked over NVIDIA NVLink, built to run large models quickly.</p></article>
            <article class="card reveal" style="--d:.12s"><div class="card-top">{icon("ram")}<span class="hw-tag">RAM</span></div><h3>ECC DDR5 memory</h3><p>Error-correcting server memory keeps long-running work stable and accurate.</p></article>
            <article class="card reveal" style="--d:.18s"><div class="card-top">{icon("layers")}<span class="hw-tag">MODELS</span></div><h3>Shaped on top, not trained from scratch</h3><p>Rivencast does not train its own foundation model. Agents are shaped and tuned on top of models for detection and explanation.</p></article>
          </div>
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
   "<p>Rivencast is a bot-detection platform run by AI agents. The agents read publicly available account signals, give each account a risk score, and explain the score in plain language so moderators and teams can decide what to do.</p>"),
  ("Which platforms does it work with?",
   f"<p>Reddit first. Rivencast works from publicly available data. {NOT_AFFIL}</p>"),
  ("What signals do the agents look at?",
   "<p>Account age, posting cadence and timing, karma patterns, templated or repeated text, coordinated activity between accounts, and the account’s public history in context.</p>"),
  ("Does Rivencast ban or remove accounts?",
   "<p>No. Rivencast flags and explains. Moderators and teams review the flags and make the call.</p>"),
  ("Is a high risk score proof that an account is a bot?",
   "<p>No. A score is a signal that an account deserves a closer look, with the reasons written out. Real people can look unusual, and some bots look ordinary.</p>"),
  ("How do I get early access?",
   f'<p>Email <a href="{EARLY}">inquiry@rivencast.com</a> and tell us about your community, brand, or project — or text Hana and she’ll pass it to the team.</p>'),
  ("Who is Hana?",
   "<p>Hana is Rivencast’s mascot — an AI with a confident, slightly smug personality. She’s the one you text or talk to about Rivencast, early access, or help. She’s an AI and says so.</p>"),
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
        <p class="lede reveal" style="--d:.1s">Early access, partnerships, research, press, or help — we read every message.</p>
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
  "index.html": ("Rivencast — AI agents that catch the bots",
                 "Rivencast is a bot-detection platform run by AI agents. Starting with Reddit, it scores accounts from publicly available signals and explains why in plain language. Early access.",
                 "/", "Home", HOME, None),
  "agents.html": ("Detection agents — Rivencast",
                  "How Rivencast’s detection agents work: focused AI agents that read public signals and roll their findings into one risk score with a plain-language explanation. Reddit first, early access.",
                  "/agents.html", "Agents", AGENTS, None),
  "agents/hana.html": ("Hana — the Rivencast mascot",
                       "Meet Hana, Rivencast’s sassy AI mascot. Text her at +1 (833) 408-5702 to ask about Rivencast, request early access, or get help.",
                       "/agents/hana.html", "Agents", HANA, None),
  "about.html": ("About Us — Rivencast",
                 "Rivencast is an independent AI studio in Houston building AI agents for bot detection, with explainable risk scores and humans making the call.",
                 "/about.html", "About", ABOUT, None),
  "contact.html": ("Contact & FAQ — Rivencast",
                   "Contact Rivencast at inquiry@rivencast.com for early access, learn how texting Hana works, and get answers about our bot-detection agents.",
                   "/contact.html", "Contact", CONTACT, [FAQ_LD]),
  "404.html": ("Page not found — Rivencast", "This page could not be found on rivencast.com.",
               "/404.html", None, NOTFOUND, None),
}


def build_marketing():
    for name, (title, desc, path, active, body, ld) in PAGES.items():
        html = page(title, desc, path, active, body, ld, noindex=(name == "404.html"))
        (ROOT / name).write_text(html, encoding="utf-8")
        print("wrote", name)

LEGAL = {
  "privacy.html": ("Privacy Policy — Rivencast", "Privacy Policy for Rivencast / Hana by Rivencast, operated by Daniel Jordan Reece.", "/privacy.html"),
  "terms.html": ("Terms of Service — Rivencast", "Terms of Service for Rivencast, operated by Daniel Jordan Reece, doing business as Rivencast.", "/terms.html"),
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
