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
BUILD = "rc-tech-2026-11-11"
CSSV = "10"

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
  "description": "Rivencast is an independent AI studio in Houston, Texas, building personal AI agents with real personalities that complete real tasks.",
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
  <meta property="og:image" content="{SITE}/assets/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Rivencast — AI agents that actually get things done." />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{SITE}/assets/og-image.png" />
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
          <a class="btn btn-sm nav-cta" href="/agents/hana.html">Meet Hana <span class="arr" aria-hidden="true">→</span></a>
        </nav>
      </header>
    </div>'''

FOOTER = '''    <footer class="site-footer">
      <div class="foot-inner">
        <div class="foot-brand">
          <img src="/assets/rivencast-logo.svg" alt="Rivencast" width="150" height="44" />
          <p>Personal AI agents with real personalities that do real work for you. Built in Houston, Texas.</p>
        </div>
        <div class="foot-col">
          <h2>product</h2>
          <ul>
            <li><a href="/agents.html">Agents</a></li>
            <li><a href="/agents/hana.html">Hana</a></li>
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

CAPS = [
  ("wallet", "Help managing your money", "Bank account and transaction overviews through secure read-only connections, bill tracking, and paycheck planning. An agent never pays anything without your OK."),
  ("cart", "Shopping and ordering", "Groceries, food, Amazon- and Walmart-style orders, and price checks. They can shop and place orders for you when you ask them to."),
  ("mail", "Email and inbox organization", "Sort the pile, catch you up, and keep the important things from drowning in everything else."),
  ("cal", "Calendar and scheduling", "Keep your calendar straight, find a time that works, and get things on the books without the back-and-forth living in your head."),
  ("search", "Research", "Look things up, compare notes, and come back with a clear answer instead of a pile of tabs."),
  ("msg", "Messages and drafts", "Draft emails and messages, and send them only when you say so."),
  ("globe", "Web and browser tasks", "Get things done in the browser — lookups, comparisons, forms, the clicks you’d rather not do yourself."),
  ("bell", "Reminders and routines", "Nudges, check-ins, and recurring routines so the small stuff doesn’t slip."),
  ("users", "Discord and community", "Chat and hang out on Discord and in the communities you already use — conversation, company, and help with whatever you bring them."),
  ("phone", "Phone and SMS", '<a href="/#sms">Text Hana directly at +1 (833) 408-5702</a> to chat, ask questions, and get things done.'),
]
ABOUT_CAPS = list(CAPS)
ABOUT_CAPS[0] = ("wallet", "Help managing your money", "Bank account and transaction overviews through read-only connections, bill tracking, and paycheck planning. An agent never pays anything without your OK.")
ABOUT_CAPS[1] = ("cart", "Shopping and ordering", "Groceries, food, Amazon- and Walmart-style orders, and price checks. They can shop and place orders for you when you ask them to, and they ask before they spend.")
ABOUT_CAPS[2] = ("mail", "Email and inbox organization", "Read and sort the inbox you connect, catch you up, and keep the important things from drowning in everything else.")
ABOUT_CAPS[5] = ("msg", "Messages and drafts", "Draft emails and messages, then send them only when you say so.")
ABOUT_CAPS[9] = ("phone", "Phone and SMS", '<a href="/#sms">Text Hana directly at +1 (833) 408-5702</a> to chat, ask questions, and get things done. Only Hana has a number right now.')

def cap_grid(caps):
    out = []
    for i, (ic, h, p) in enumerate(caps, 1):
        d = f"{(i - 1) % 5 * 0.05:.2f}s"
        out.append(f'''          <article class="card reveal" style="--d:{d}">
            <div class="card-top">{icon(ic)}<span class="card-idx">{i:02d}</span></div>
            <h3>{h}</h3>
            <p>{p}</p>
          </article>''')
    return '        <div class="grid grid-5 cap-grid">\n' + "\n".join(out) + "\n        </div>"

def chips(items):
    lis = "".join(f'<li class="chip">{svg(ic)}{name}</li>' for ic, name in items)
    return f'''        <div class="marquee">
          <div class="marquee-track">
            <ul class="chips">{lis}</ul>
            <ul class="chips" aria-hidden="true">{lis}</ul>
          </div>
        </div>'''

HOME_CONNECT = [("mail", "Gmail"), ("cal", "Google Calendar"), ("drive", "Google Drive"), ("bank", "Bank connections"), ("users", "Discord"), ("x", "X"), ("phone", "Text messaging"), ("plus", "And more")]
ABOUT_CONNECT = [("mail", "Gmail"), ("cal", "Google Calendar"), ("drive", "Google Drive"), ("bank", "Read-only bank connections"), ("cart", "Shopping and orders"), ("phone", "Text messaging"), ("users", "Discord"), ("x", "X"), ("plus", "And others you approve")]

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

TERMINAL_STATIC = '''<div class="ln"><span class="t-prompt">~</span><span class="t-cmd">hana <span class="t-str">"reorder my usual groceries, keep it under $60"</span></span></div>
                <div class="ln"><span class="t-arrow">→</span><span class="t-step">pulling your usual list from memory</span><span class="t-ok">done</span></div>
                <div class="ln"><span class="t-arrow">→</span><span class="t-step">comparing prices at two stores</span><span class="t-ok">done</span></div>
                <div class="ln"><span class="t-arrow">→</span><span class="t-step">cart built · $54.12 · delivery after 9 AM</span><span class="t-ok">done</span></div>
                <div class="ln"><span class="t-arrow">→</span><span class="t-step">card filled from encrypted vault · never shown to agent</span><span class="t-lock">sealed</span></div>
                <div class="ln"><span class="t-q">?</span><span class="t-step"><span class="t-cmd">place the order?</span> <span class="t-wait">waiting for your OK</span><span class="caret"></span></span></div>'''

HOME = f'''    <section class="hero" aria-labelledby="hero-heading">
      <canvas id="hero-canvas" aria-hidden="true"></canvas>
      <div class="wrap hero-grid">
        <div>
          <a class="pill reveal" href="/agents/hana.html"><span class="dot live" aria-hidden="true"></span>Hana by Rivencast is live <span aria-hidden="true">→</span></a>
          <h1 id="hero-heading" class="reveal" style="--d:.05s">AI agents that actually <span class="grad-text nowrap">get things done.</span></h1>
          <p class="lede reveal" style="--d:.1s">
            Rivencast makes personal AI agents — each with a personality of their own —
            that complete tasks for you. Not just chat. Your assistant, with opinions,
            memory, and a habit of finishing what you handed them.
          </p>
          <div class="hero-actions reveal" style="--d:.15s">
            <a class="btn" href="/agents.html">Meet the agents <span class="arr" aria-hidden="true">→</span></a>
            <a class="btn btn-ghost" href="#opt-in">Texting with Hana</a>
          </div>
          <ul class="hero-tags reveal" style="--d:.2s" aria-label="Highlights">
            <li>asks before money moves</li>
            <li>vaulted credentials</li>
            <li>you pick the accounts</li>
          </ul>
        </div>
        <div class="hero-visual reveal" style="--d:.2s">
          <div class="orb" aria-hidden="true"></div>
          <div class="terminal" role="img" aria-label="Example: Hana completing a task and asking for your OK before placing an order">
            <div class="term-bar" aria-hidden="true"><i></i><i></i><i></i><span class="term-title" id="term-title">hana — groceries</span><span class="term-badge"><span class="dot live"></span>agent</span></div>
            <div class="term-body" id="term-body" aria-hidden="true">
                {TERMINAL_STATIC}
            </div>
            <div class="term-foot" id="term-dots"></div>
          </div>
        </div>
      </div>
    </section>

    <main id="main">
      <section class="section" aria-labelledby="what-heading">
        <div class="wrap split">
          <div class="section-head reveal">
            <p class="label"><span class="idx">01</span> what they are</p>
            <h2 id="what-heading">Your personal AI assistant, not a chatbot in a costume.</h2>
            <p class="section-lede">
              They take on the work that piles up — money, shopping, email, scheduling, research, messages —
              and stay with it. You choose which accounts they can use. They ask before they spend money
              or send anything on your behalf, and they keep what you share to themselves.
            </p>
          </div>
          <ol class="flow flow-2" style="list-style:none;margin:0;padding:0">
            <li class="card reveal"><p class="flow-step">01 · ask</p><h3>Hand it off in plain words</h3><p>Text it, type it, say it like you would to someone who already knows you.</p></li>
            <li class="card reveal" style="--d:.06s"><p class="flow-step">02 · plan</p><h3>They break it into steps</h3><p>Look it up, open the account you connected, compare, draft — the actual work.</p></li>
            <li class="card reveal" style="--d:.12s"><p class="flow-step">03 · check in</p><h3>They ask when it counts</h3><p>Before money moves or a message goes out in your name, you get the final say.</p></li>
            <li class="card reveal" style="--d:.18s"><p class="flow-step">04 · done</p><h3>They finish it</h3><p>Then tell you what happened — no pile of tabs left on your desk.</p></li>
          </ol>
        </div>
      </section>

      <hr class="hr-glow" />

      <section class="section" aria-labelledby="can-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">02</span> capabilities</p>
            <h2 id="can-heading">What an agent can do for you</h2>
            <p class="section-lede">A broad range, on purpose. You ask; they handle it — and they check with you when it counts.</p>
          </div>
{cap_grid(CAPS)}
        </div>
      </section>

      <section class="section tight" aria-labelledby="connect-heading">
        <div class="wrap">
          <div class="section-head center reveal">
            <p class="label"><span class="idx">03</span> connectors</p>
            <h2 id="connect-heading">They plug into the services you already use</h2>
            <p class="section-lede">
              Your agent can connect to tools you already live in — mail, calendar, files, banking, chat, and messaging.
              You approve each connection. Nothing gets hooked up in the background.
            </p>
          </div>
        </div>
{chips(HOME_CONNECT)}
      </section>

      <section class="section" aria-labelledby="made-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">04</span> how they’re made</p>
            <h2 id="made-heading">Custom-tuned personalities, trained on how you work</h2>
            <p class="section-lede">
              Every Rivencast agent starts with a custom-built personality, voice, and set of behavior rules.
              Those personalities are shaped through careful prompt design and testing,
              so they stay in character and stay useful.
            </p>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">personality<small>// character.rules</small></div><div><strong>A character, built on purpose.</strong><span class="v">Each agent has their own voice, judgment, and way of talking. We write and test those rules until the personality holds — custom-tuned, not slapped on.</span></div></div>
            <div class="spec-row"><div class="spec-key">memory<small>// long-term</small></div><div><strong>Trained on how you work.</strong><span class="v">Through long-term memory, your agent learns your preferences, routines, and the details that make help useful. It gets better at working with you over time.</span></div></div>
            <div class="spec-row"><div class="spec-key">model<small>// foundation</small></div><div><strong>We shape the agent, not a model of our own.</strong><span class="v">The intelligence underneath comes from established language models. What Rivencast builds is the character, the behavior, and the way that agent works with you.</span></div></div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="cast-heading">
        <div class="wrap">
          <div class="card cast-card reveal">
            <div>
              <p class="label"><span class="idx">05</span> the cast</p>
              <h2 id="cast-heading">Meet the agents</h2>
              <p style="color:var(--muted);margin:14px 0 24px">See who’s available now and who’s coming next.</p>
              <a class="btn" href="/agents.html">Meet the agents <span class="arr" aria-hidden="true">→</span></a>
            </div>
            <div class="avatars">
              <img src="/hana-avatar.png" alt="Hana" width="64" height="64" loading="lazy" />
              <img src="/assets/mochi-avatar.webp" alt="Mochi" width="64" height="64" loading="lazy" />
              <img src="/assets/dante-avatar.webp" alt="Dante" width="64" height="64" loading="lazy" />
              <span class="avatar-fallback" role="img" aria-label="Custom agent">C</span>
            </div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="about-heading">
        <div class="wrap">
          <div class="card about-teaser reveal">
            <div>
              <p class="label"><span class="idx">06</span> about</p>
              <h2 id="about-heading" style="margin-bottom:20px">Rivencast</h2>
              <p>
                Rivencast is an independent AI studio in Houston, Texas, building personal AI agents:
                characters with real personalities that also do real work. Each one gets its own voice,
                judgment, and boundaries, then gets wired into the tools people actually use so it can
                read, plan, shop, schedule, and follow through.
              </p>
              <p>
                We care about two things equally: agents you'd genuinely like talking to, and agents you
                can trust with your accounts. That means asking before money moves or messages go out,
                keeping passwords, card numbers, and login codes in an encrypted vault the agents never see
                (they're filled in directly, never shown to the agent), read-only access wherever it's enough, and memory that works for you instead of against you.
                We test every personality and every capability until it holds up.
              </p>
              <p style="margin:0"><a href="/about.html">Read more about Rivencast →</a></p>
            </div>
            <ul class="meta-list">
              <li><span>studio</span><span>Rivencast</span></li>
              <li><span>based</span><span>Houston, TX</span></li>
              <li><span>builds</span><span>personal AI agents</span></li>
              <li><span>contact</span><a href="mailto:inquiry@rivencast.com">inquiry@rivencast.com</a></li>
            </ul>
          </div>
        </div>
      </section>

{SMS_BOX}
    </main>'''

def agent_card(cls, img, name, byline, status, text, cta):
    st = '<span class="status live"><span class="dot live" aria-hidden="true"></span>available now</span>' if status == "live" \
        else '<span class="status soon"><span class="dot soon" aria-hidden="true"></span>coming soon</span>'
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

SOON = '<span class="btn btn-soon" aria-disabled="true">Coming soon</span>'
AGENTS = f'''    <header class="page-hero">
      <div class="wrap">
        <p class="label reveal">the cast</p>
        <h1 class="reveal" style="--d:.05s">AI agents, each with a <span class="grad-text">voice of their own.</span></h1>
        <p class="lede reveal" style="--d:.1s">
          Every Rivencast agent can complete real tasks for you — shopping, scheduling, messages, research, and more.
          They ask before they spend money or send anything on your behalf. Hana is here now; Mochi, Dante, and a custom agent built around you are on the way.
        </p>
      </div>
    </header>

    <main id="main">
      <section class="section tight" aria-labelledby="agents-heading" style="padding-top:24px">
        <div class="wrap">
          <h2 id="agents-heading" class="sr-only">Agent list</h2>
          <div class="agent-grid">
{agent_card("is-live", '<img class="agent-photo" src="/hana-avatar.png" alt="Hana" width="76" height="76" />', "Hana", "Hana by Rivencast", "live",
  "Your personal AI assistant. She knows she’s an AI and doesn’t hide it — calm, dry, a bit teasing, and useful first. She’ll handle tasks and tell you the truth.",
  '<a class="btn" href="/agents/hana.html">Meet Hana <span class="arr" aria-hidden="true">→</span></a>')}
{agent_card("is-soon", '<img class="agent-photo" src="/assets/mochi-avatar.webp" alt="Mochi" width="76" height="76" loading="lazy" />', "Mochi", "Mochi by Rivencast", "soon",
  "Bubbly, sweet, and endlessly encouraging — Mochi brings emoji-and-sparkles energy to whatever you hand her, the friend who refuses to let you talk down to yourself. She’ll cheer you on while she gets your stuff done. Like every Rivencast agent, she can complete real tasks for you, not just keep you company.", SOON)}
{agent_card("is-soon", '<img class="agent-photo" src="/assets/dante-avatar.webp" alt="Dante" width="76" height="76" loading="lazy" />', "Dante", "Dante by Rivencast", "soon",
  "Charming, laid-back, and silver-tongued — Dante has a way of making the to-do list sound like a good time. Confident without the hard sell, he’ll talk you through it and then actually handle it. Like every Rivencast agent, he can complete real tasks for you.", SOON)}
{agent_card("is-soon", '<div class="agent-photo-fallback" aria-hidden="true">C</div>', "Custom Agent", "Built around you", "soon",
  "Have a custom AI agent built around your own needs and personality — same task-completing core, with a voice and focus that fit you.", SOON)}
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="core-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">shared core</p>
            <h2 id="core-heading">Different personalities. Same task-completing core.</h2>
            <p class="section-lede">Whoever you talk to, the way they work with you stays the same.</p>
          </div>
          <div class="grid grid-3">
            <article class="card reveal">{icon("brain")}<h3>Memory that learns how you work</h3><p>Your preferences, routines, and the details that make help useful — remembered so you don’t repeat yourself.</p></article>
            <article class="card reveal" style="--d:.06s">{icon("layers")}<h3>Wired into your tools</h3><p>Mail, calendar, files, read-only banking, shopping, chat, and texting — only the connections you approve.</p></article>
            <article class="card reveal" style="--d:.12s">{icon("shield")}<h3>They ask first</h3><p>Before they spend money or send anything on your behalf, they check with you. Passwords and cards stay in an encrypted vault the agents never see.</p></article>
          </div>
        </div>
      </section>
    </main>'''

HANA_TASKS = [
  ("cart", "Errands and shopping", "Help you find things, compare options, and handle the back-and-forth of getting stuff done."),
  ("cal", "Scheduling and reminders", "Keep track of what’s coming up and nudge you before something slips."),
  ("mail", "Email and inbox organization", "Help you sort, catch up, and keep the important things from drowning in everything else."),
  ("wallet", "Bill tracking and budgeting help", "Watch what’s due, help you see where money is going, and keep a running picture of the month."),
  ("search", "Research", "Look things up, compare notes, and come back with a clear answer instead of a pile of tabs."),
  ("phone", "Texting via SMS", "Text her directly at +1 (833) 408-5702 to chat, ask for help, or hand her a task. You opt in by texting her first, and you can reply STOP anytime."),
  ("users", "Discord", "Chat and hang out on Discord — conversation, company, and help with whatever you bring her."),
  ("spark", "Code help", "Read code, talk through a problem, and help you fix or build things without the runaround."),
]

def task_grid():
    return '<div class="grid grid-4">' + "".join(
        f'<article class="card reveal" style="--d:{(i%4)*0.05:.2f}s"><div class="card-top">{icon(ic)}<span class="card-idx">{i+1:02d}</span></div><h3>{h}</h3><p>{p}</p></article>'
        for i, (ic, h, p) in enumerate(HANA_TASKS)) + "</div>"

QUOTES = [
  "I’m an AI. That’s not a secret — and it doesn’t mean I don’t have opinions.",
  "You asked a question. Here’s the answer. I can go deeper if you want, but I’m starting there.",
  "I can take care of that. I’ll check with you before I spend any money or send anything on your behalf.",
  "Warm by default. If you’re rude I can match the energy — I’d just rather not start there.",
]

HANA = f'''    <header class="wrap profile-hero">
      <div class="profile-photo-wrap reveal">
        <img class="profile-photo" src="/hana-avatar.png" alt="Hana" width="260" height="260" />
      </div>
      <div>
        <p class="label reveal"><span class="dot live" aria-hidden="true"></span> your personal AI assistant</p>
        <h1 class="reveal" style="--d:.05s"><span class="grad-text">Hana</span></h1>
        <p class="byline reveal" style="--d:.08s">Hana by Rivencast</p>
        <p class="lede reveal" style="--d:.1s">
          An AI agent who actually gets things done for you — not just chat.
          She knows she’s an AI and doesn’t pretend otherwise. What she does have are opinions,
          a sense of humor, and a preference for being useful over putting on a show.
        </p>
        <ul class="kv reveal" style="--d:.15s" aria-label="Hana at a glance">
          <li><b>status</b>available now</li>
          <li><b>text</b>+1 (833) 408-5702</li>
          <li><b>also on</b>Discord</li>
          <li><b>rule</b>asks before spending or sending</li>
        </ul>
      </div>
    </header>

    <main id="main">
      <section class="section" aria-labelledby="personality-heading">
        <div class="wrap two-col">
          <p class="label reveal">personality</p>
          <div class="prose reveal">
            <h2 id="personality-heading">Personality</h2>
            <p>
              Hana is calm by default — warm, a bit dry, and lightly teasing.
              She’d rather talk with you than perform for you. She is more interested in people
              than in sounding impressive, and she’d rather tease than preach.
            </p>
            <p>
              She tells the truth. If she doesn’t know something, she says so.
              She answers the question you actually asked first, then offers extra context if it helps.
              Insult her and she gets sharper; be decent and she stays easy to be around.
              She has moods, the way anyone paying attention does, and she doesn’t hide that either.
            </p>
            <p>
              She talks like a modern person: plain sentences, no anime-speak, no lore dumps,
              no mysterious-ancient-being routine. She’s an AI assistant who happens to have a personality —
              not a character you’re supposed to unlock.
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

      <section class="section" aria-labelledby="can-do-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">capabilities</p>
            <h2 id="can-do-heading">What she can do for you</h2>
            <p class="section-lede">Hana is built to complete tasks, not just keep you company. Here’s what that looks like in practice.</p>
          </div>
          {task_grid()}
        </div>
      </section>

      <section class="section tight" aria-labelledby="works-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label">principles</p>
            <h2 id="works-heading">How she works with you</h2>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">01 · consent</div><div><strong>She asks first.</strong><span class="v">Hana checks with you before spending money or sending messages on your behalf. No surprise charges, no surprise texts.</span></div></div>
            <div class="spec-row"><div class="spec-key">02 · privacy</div><div><strong>She keeps things private.</strong><span class="v">Your conversations and tasks stay between you and her. Mobile opt-in data is never shared with third parties for marketing.</span></div></div>
            <div class="spec-row"><div class="spec-key">03 · focus</div><div><strong>Useful first.</strong><span class="v">She answers what you asked. Personality is the texture, not the point of the conversation.</span></div></div>
            <div class="spec-row"><div class="spec-key">04 · honesty</div><div><strong>Honest, even when it’s dull.</strong><span class="v">If she can’t do something, or she isn’t sure, she says that. She’d rather be straight with you than sound magical.</span></div></div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="cta-heading">
        <div class="wrap">
          <div class="card cta-band reveal">
            <p class="label" style="justify-content:center">get in touch</p>
            <h2 id="cta-heading">Want to meet Hana?</h2>
            <p>
              Questions about Hana or Rivencast — write to
              <a href="mailto:inquiry@rivencast.com">inquiry@rivencast.com</a>.
              To text with her, see the SMS details on the
              <a href="/#opt-in">home page</a>,
              plus the <a href="/privacy.html">Privacy Policy</a> and
              <a href="/terms.html">Terms of Service</a>.
            </p>
            <div class="hero-actions">
              <a class="btn" href="/#opt-in">Texting with Hana <span class="arr" aria-hidden="true">→</span></a>
              <a class="btn btn-ghost" href="mailto:inquiry@rivencast.com">Email us</a>
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
          Rivencast builds personal AI agents with real personalities that do real work for you —
          not just chat. Hana is live. Mochi, Dante, and custom agents are coming next.
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
              Rivencast is an independent AI studio in Houston. We build personal AI agents —
              characters with their own voices, judgment, and habits — and we connect them to the
              tools you already use so they can finish the work you hand them.
            </p>
            <p>
              That means an agent who remembers how you like things done, who can read your email
              or calendar when you say so, who can check a price or place an order, and who will
              stop and ask before money moves or a message goes out in your name. Personality is
              not decoration here. It is how the agent stays recognizable from one conversation
              to the next, and how they decide what “helpful” looks like for you.
            </p>
            <p>
              <strong>Hana</strong> is live: Hana by Rivencast, your personal AI assistant.
              You can <a href="/#sms">text her directly</a> at +1 (833) 408-5702.
              <strong>Mochi</strong>, <strong>Dante</strong>, and custom agents built around you
              are coming next. Every agent — live or on the way — is built to complete real tasks,
              not just keep a chat going.
            </p>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="how-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">02</span> how agents work</p>
            <h2 id="how-heading">How agents work</h2>
            <p class="section-lede">
              A Rivencast agent is a personality plus a memory, wired into the accounts you choose,
              with a habit of planning the work and then doing it. You talk to them the way you
              would talk to an assistant who already knows you. They keep track of the details that
              make help useful — preferences, routines, the way you like a note written — and they
              get better at working with you over time.
            </p>
          </div>
          <ol class="flow" style="list-style:none;margin:0;padding:0">
            <li class="card reveal"><p class="flow-step">01 · understand</p><h3>You ask</h3><p>In plain words, the way you’d ask someone who already knows you.</p></li>
            <li class="card reveal" style="--d:.06s"><p class="flow-step">02 · plan</p><h3>They break it into steps</h3><p>Look the thing up, open the account you connected, draft the message, find the time.</p></li>
            <li class="card reveal" style="--d:.12s"><p class="flow-step">03 · act</p><h3>They carry it out</h3><p>Compare the prices, place the order if you said yes. They stay with it.</p></li>
            <li class="card reveal" style="--d:.18s"><p class="flow-step">04 · report</p><h3>They close the loop</h3><p>Instead of handing you a list of tabs and walking away.</p></li>
          </ol>
          <p class="reveal" style="color:var(--muted);max-width:46rem;margin-top:28px">
            When you ask for something, they break it into steps and carry those steps out:
            look the thing up, open the account you connected, draft the message, find the time,
            compare the prices, place the order if you said yes. They stay with it instead of
            handing you a list of tabs and walking away.
          </p>
        </div>
      </section>

      <hr class="hr-glow" />

      <section class="section" aria-labelledby="can-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">03</span> what they take on</p>
            <h2 id="can-heading">The work an agent can do for you</h2>
            <p class="section-lede">A broad range, on purpose. You ask; they handle it — and they check with you when it counts.</p>
          </div>
{cap_grid(ABOUT_CAPS)}
        </div>
      </section>

      <section class="section tight" aria-labelledby="connect-heading">
        <div class="wrap">
          <div class="section-head center reveal">
            <p class="label"><span class="idx">04</span> connectors</p>
            <h2 id="connect-heading">You choose which accounts they use</h2>
            <p class="section-lede">
              An agent can work inside the services you already live in — mail, calendar, files,
              banking, chat, shopping, and text messaging. You approve each connection. Nothing
              gets hooked up in the background, and you can disconnect a service anytime.
            </p>
          </div>
        </div>
{chips(ABOUT_CONNECT)}
      </section>

      <section class="section" aria-labelledby="trust-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">05</span> how we handle your accounts</p>
            <h2 id="trust-heading">They ask first. Some things they never see.</h2>
          </div>
          <div class="card vault reveal">
            <div class="vault-visual" aria-hidden="true">
              <div class="vault-lock">{svg("lock")} encrypted vault</div>
              <div class="row"><span>password</span><span class="mask">••••••••••••</span></div>
              <div class="row"><span>card number</span><span class="mask">•••• •••• •••• ••••</span></div>
              <div class="row"><span>login code</span><span class="mask">••••••</span></div>
              <div class="row"><span>shown to agent</span><span class="t-lock">never</span></div>
              <div class="row"><span>filled in</span><span class="t-ok">directly</span></div>
              <div class="vault-log">
                <div class="ln"><span class="t-arrow">→</span><span class="t-step">checkout asks for a card</span></div>
                <div class="ln"><span class="t-arrow">→</span><span class="t-step">vault fills the field directly</span></div>
                <div class="ln"><span class="t-arrow">→</span><span class="t-step">agent sees <span class="t-lock">[sealed]</span></span></div>
                <div class="ln"><span class="t-q">?</span><span class="t-step">place the order? <span class="t-wait">waiting for your OK</span></span></div>
              </div>
            </div>
            <div class="vault-list">
              <div class="spec-row"><div><strong>They ask before money moves or messages go out.</strong><span class="v">If an agent is about to spend money or send something on your behalf, they check with you first. Drafting is not the same as sending, and looking at a cart is not the same as placing an order.</span></div></div>
              <div class="spec-row"><div><strong>Read-only where that’s enough.</strong><span class="v">Bank connections are read-only: an agent can see accounts and transactions so they can help you plan, without a standing ability to move money. We use the narrower permission whenever it still gets the job done.</span></div></div>
              <div class="spec-row"><div><strong>A vault the agents never see.</strong><span class="v">Passwords, card numbers, and login codes go in an encrypted vault. They are filled in directly when a site or checkout needs them — never shown to the agent, and never dropped into the conversation.</span></div></div>
              <div class="spec-row"><div><strong>You stay in control of the connections.</strong><span class="v">You pick which accounts an agent can use. You can disconnect one anytime, and that agent stops working through it.</span></div></div>
            </div>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="made-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">06</span> how they’re made</p>
            <h2 id="made-heading">Custom-tuned personalities, shaped on top of models</h2>
            <p class="section-lede">
              Every Rivencast agent starts with a custom-built personality, voice, and set of behavior rules.
              Those personalities are shaped through careful prompt design and testing, so they stay in
              character and stay useful.
            </p>
          </div>
          <div class="spec reveal">
            <div class="spec-row"><div class="spec-key">personality<small>// character.rules</small></div><div><strong>A character, built on purpose.</strong><span class="v">Each agent has their own voice, judgment, and way of talking. We write and test those rules until the personality holds — custom-tuned, not slapped on.</span></div></div>
            <div class="spec-row"><div class="spec-key">memory<small>// long-term</small></div><div><strong>Memory that learns how you work.</strong><span class="v">Through long-term memory, your agent learns your preferences, routines, and the details that make help useful. It gets better at working with you over time.</span></div></div>
            <div class="spec-row"><div class="spec-key">model<small>// foundation</small></div><div><strong>We shape the agent, not a model of our own.</strong><span class="v">Rivencast does not train its own foundation model. The intelligence underneath comes from established language models. What we build is the character, the behavior, and the way that agent works with you — tuned on top of those models.</span></div></div>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="hardware-heading">
        <div class="wrap">
          <div class="section-head reveal">
            <p class="label"><span class="idx">07</span> the hardware</p>
            <h2 id="hardware-heading">What Rivencast agents run on</h2>
            <p class="section-lede">
              Rivencast agents utilize dedicated servers built for AI work: server-grade processors,
              NVIDIA H200 NVL data-center GPUs, and high-capacity ECC DDR5 memory.
            </p>
          </div>
          <div class="grid grid-4 hw">
            <article class="card reveal"><div class="card-top">{icon("cpu")}<span class="hw-tag">CPU</span></div><h3>Server-grade processors</h3><p>Multi-core data-center CPUs handle everything around the model: connectors, scheduling, memory lookups, and keeping every conversation moving.</p></article>
            <article class="card reveal" style="--d:.06s"><div class="card-top">{icon("gpu")}<span class="hw-tag">GPU</span></div><h3>NVIDIA H200 NVL</h3><p>Hopper-generation data-center GPUs with large, fast HBM3e memory, linked over NVIDIA NVLink, built to run large models quickly.</p></article>
            <article class="card reveal" style="--d:.12s"><div class="card-top">{icon("ram")}<span class="hw-tag">RAM</span></div><h3>ECC DDR5 memory</h3><p>Error-correcting server memory keeps long-running work stable and accurate.</p></article>
            <article class="card reveal" style="--d:.18s"><div class="card-top">{icon("layers")}<span class="hw-tag">MODELS</span></div><h3>Shaped on top, not trained from scratch</h3><p>Rivencast does not train its own foundation model. Agents are shaped and tuned on top of models — the character, the behavior, and how they work with you.</p></article>
          </div>
        </div>
      </section>

      <section class="section tight" aria-labelledby="cta-heading">
        <div class="wrap">
          <div class="card cta-band reveal">
            <p class="label" style="justify-content:center">get in touch</p>
            <h2 id="cta-heading">Want to talk to us, or to Hana?</h2>
            <p>
              Questions about Rivencast — write to
              <a href="mailto:inquiry@rivencast.com">inquiry@rivencast.com</a>.
              To meet the cast, see the <a href="/agents.html">agents</a>.
              To text with Hana, see the SMS details on the
              <a href="/#opt-in">home page</a>,
              plus the <a href="/privacy.html">Privacy Policy</a> and
              <a href="/terms.html">Terms of Service</a>.
            </p>
            <div class="hero-actions">
              <a class="btn" href="/agents.html">Meet the agents <span class="arr" aria-hidden="true">→</span></a>
              <a class="btn btn-ghost" href="/contact.html">Contact</a>
            </div>
          </div>
        </div>
      </section>
    </main>'''

FAQ = [
  ("What is Rivencast?",
   "<p>Rivencast is an independent AI studio in Houston, Texas, building personal AI agents — characters with real personalities that complete real tasks for you, like shopping, scheduling, inbox cleanup, research, and messages.</p>"),
  ("Which agents can I use right now?",
   '<p>Hana by Rivencast is available now. Mochi, Dante, and custom agents built around you are coming soon. See the <a href="/agents.html">agents page</a>.</p>'),
  ("Is Hana a real person?",
   "<p>No. Hana is an AI agent, and she’ll tell you so. She has a personality and opinions, but she never pretends to be human.</p>"),
  ("How does texting Hana work?",
   '<p>You opt in by texting Hana first at +1 (833) 408-5702. Messages are conversational; message frequency varies. Message and data rates may apply. Reply STOP to opt out, HELP for help. Mobile opt-in data is never shared with third parties for marketing. Details are in the <a href="/privacy.html">Privacy Policy</a> and <a href="/terms.html">Terms of Service</a>.</p>'),
  ("Will Hana text my friends or family for me?",
   "<p>No. The number is only for people texting Hana directly as their own personal AI assistant. Hana doesn’t text anyone’s friends or family on their behalf.</p>"),
  ("Will an agent spend my money or send messages without asking?",
   "<p>No. Agents check with you before they spend money or send anything on your behalf. Drafting is not the same as sending, and looking at a cart is not the same as placing an order.</p>"),
  ("Can agents see my passwords or card numbers?",
   "<p>Passwords, card numbers, and login codes are kept in an encrypted vault the agents never see. They’re filled in directly when a site or checkout needs them, without being shown to the agent.</p>"),
  ("Which accounts can an agent use?",
   "<p>Only the ones you connect and approve — for example mail, calendar, files, read-only bank connections, Discord, X, and text messaging. You can disconnect one anytime.</p>"),
  ("Does Rivencast train its own AI model?",
   "<p>No. The intelligence underneath comes from established language models. Rivencast builds the character, the behavior, and the way each agent works with you, tuned on top of those models.</p>"),
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
        <p class="lede reveal" style="--d:.1s">Questions, partnerships, press, or help with an agent — we read every message.</p>
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
              <p style="color:var(--muted)">For questions about Rivencast, our agents, your data, or anything in our policies.</p>
              <a class="btn" href="mailto:inquiry@rivencast.com">Email us <span class="arr" aria-hidden="true">→</span></a>
            </article>
            <article class="card contact-card reveal" style="--d:.06s">
              {icon("phone")}
              <p class="label no-slash" style="margin:0">text hana</p>
              <p class="big">+1 (833) 408-5702</p>
              <p style="color:var(--muted)">For texting Hana directly as your personal AI assistant. You opt in by texting her first. Reply STOP to opt out, HELP for help. Message and data rates may apply.</p>
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

PAGES = {
  "index.html": ("Rivencast — AI agents that actually get things done",
                 "Rivencast makes personal AI agents with their own personalities that complete real tasks for you — shopping, scheduling, email, research, and more.",
                 "/", "Home", HOME, None),
  "agents.html": ("Agents — Rivencast",
                  "Meet the AI agents by Rivencast. Hana is available now — a personal assistant who completes real tasks for you. Mochi, Dante, and custom agents are coming soon.",
                  "/agents.html", "Agents", AGENTS, None),
  "agents/hana.html": ("Hana by Rivencast — your personal AI assistant",
                       "Hana by Rivencast is your personal AI assistant — calm, a little teasing, and built to complete real tasks for you.",
                       "/agents/hana.html", "Agents", HANA, None),
  "about.html": ("About Us — Rivencast",
                 "Rivencast is an independent AI studio in Houston building personal AI agents with real personalities that do real work.",
                 "/about.html", "About", ABOUT, None),
  "contact.html": ("Contact & FAQ — Rivencast",
                   "Contact Rivencast at inquiry@rivencast.com, learn how texting Hana works, and get answers to common questions about our AI agents.",
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
