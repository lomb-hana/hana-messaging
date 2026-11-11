# rivencast.com

Static marketing site for Rivencast (Daniel Jordan Reece, d/b/a Rivencast), including the Hana by Rivencast SMS program disclosures. Hosted on Render as a static site that serves the `public/` folder.

## Layout

| Path | What it is |
| --- | --- |
| `tools/build_pages.py` | The generator. Page templates, shared head/header/footer, and the asset pipeline live here. |
| `src/styles.css` | Site stylesheet (source). Minified, purged, and inlined into every page at build time. |
| `src/site.js` | Site script (source): nav, scroll reveal, request forms (FormSubmit AJAX), hero demo, particles. |
| `src/legal.css` | Extra styles for the Privacy and Terms pages (source). |
| `public/` | The built site that Render serves. HTML here is generated, so edit the templates instead. |
| `public/privacy.html`, `public/terms.html` | Legal pages. Only their head, header and footer are regenerated; the policy text is edited by hand only. |
| `public/assets/` | Fonts (self-hosted Geist, Latin subset), images (WebP), icons, OG image. |
| `render.yaml` | Render Blueprint, including cache and security headers. |

## Build

Requirements: Python 3 and Node.js (the build calls `npx esbuild` and `npx purgecss`).

```bash
python3 tools/build_pages.py
```

Then preview locally:

```bash
python3 -m http.server 8765 --directory public
# open http://localhost:8765/
```

Locally, use the `.html` URLs (for example `/about.html`). Render also serves the pretty URLs (`/about`).

Before committing, check:

- No em dashes: `grep -rnP '\x{2014}|&(mdash|#8212);' public src tools` should print nothing.
- Change the `BUILD` value in `tools/build_pages.py` so the live deploy is easy to confirm (`<meta name="rc-build">`).

## Deploy

Render auto-deploys every push to `main`. There is no build step on Render (`buildCommand: echo static`), so always commit the rebuilt `public/` together with your source changes.

```bash
git add -A && git commit -m "..." && git push origin main
curl -s https://rivencast.com/ | grep rc-build   # confirm the new BUILD is live
```

Cloudflare caches HTML for up to 5 minutes (`s-maxage=300`), so a page can be a few minutes behind right after a deploy.

## Forms

`/request-access` and `/hana-access` post to FormSubmit (`inquiry@rivencast.com`). With JavaScript, `src/site.js` sends them through FormSubmit's AJAX endpoint and redirects to `/thanks?form=early` or `/thanks?form=hana`. Without JavaScript, the normal form POST plus `_next` is the fallback. Please don't send test submissions from automation.

## Render settings (dashboard)

- **Headers:** `render.yaml` defines long-lived caching for `/assets/fonts/*`, `/site.js`, `/legal.css` and one week for images in `/assets/`. If this service is not managed by a Blueprint, add the same rules under Settings > Headers.
- **404 page:** Render already serves `public/404.html` with a real 404 status for unknown paths. Do not add a `/*` rewrite to `/404.html`; that would answer unknown URLs with status 200.
