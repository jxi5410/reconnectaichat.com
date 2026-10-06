# WO-W01 — reconnectaichat.com, the one-screen site

Status: READY for implementation. Orchestrator: Claude. Implementer: Codex. Owner decisions recorded 6–7 October 2026 (see `docs/PROPOSAL-2026-10-06.md` §8).

## 0. Where you work

- Repository: `jxi5410/reconnectaichat.com` on GitHub (private until go-live, when it becomes public so GitHub Pages can serve it). Local clone: `/Users/jiexi/Reconnect/website-repo`. If that directory does not exist yet, create it with `git init -b main`, make an empty initial commit, and work there; Claude adds the GitHub remote and pushes later. If it exists, use it as is.
- Start by copying `/Users/jiexi/Reconnect/website/PROPOSAL-2026-10-06.md`, `WO-W01-website.md` and `mock-2026-10-06.html` into `docs/` in the repo (first commit on `main` if the repo is new).
- Branch: create `wo-W01` from `main`. Commit as you go, push the branch if a remote exists, and finish with the exact commit hash in `STATUS.md` at the repo root. Do not merge; Claude reviews and merges.
- Do not modify anything under `/Users/jiexi/Reconnect/main` or any other checkout. You may **read** `/Users/jiexi/Reconnect/main/docs/brand/` (logo masters, `README.md`) and `/Users/jiexi/Reconnect/main/tools/brand/export_logo.py` (the ring's exact geometry and colours).
- Hard stops (stop and write the question in `STATUS.md` instead of guessing): anything that needs an account, a secret, DNS, a purchase, GitHub settings, or a change to the app repository.

## 1. What to build

A single-screen website in the shape of instinct.com: a small mark top-left, three paragraphs, one text link as the only call to action, a footer. Nothing else: no navigation, no screenshots, no feature grid, no pricing, no forms, no cookie banner, no analytics, no JavaScript.

The reference is `docs/mock-2026-10-06.html` in this repo (approved by the owner). Build the real page from it. Differences from the mock are listed in §3.

Repository layout:

```
site/                 everything that is deployed, as-is
  index.html
  404.html
  robots.txt
  sitemap.xml
  assets/
    favicon-32.png  favicon-192.png  favicon-512.png  apple-touch-icon.png (180)
    og.png          (1200×630)
tools/
  make_assets.py    regenerates site/assets from the brand masters (Pillow)
  check.py          the gate described in §6; exit 1 on any failure
.github/workflows/pages.yml
docs/               proposal, this order, the mock, evidence
README.md           how to preview locally, how to run the gate, where the copy lives
STATUS.md           your report (commit, gates, questions)
```

## 2. The page, element by element

**Mark.** The Reconnect ring, 40 px, top-left, a link to `/` with `aria-label="Reconnect home"`. Draw it in CSS, not an image: a `conic-gradient` on a round element, cut to a band with a radial `mask`. Geometry and colour are the brand's (`docs/brand/README.md` in the app repo): closed ring, band thickness 18 % of the outer diameter (so the inner radius is 64 % of the outer radius), colour blended around the circumference from `#B9D0FB` to `#5F84E6` by a cosine blend with the lightest point at upper-left (315° clockwise from the top) and the darkest at lower-right (135°). Generate 72 evenly spaced stops from `mix(light, dark, (1 − cos(θ − 315°)) / 2)`, make the first and last stop identical so there is no seam, and inline them. The mock uses 9 approximate stops; replace them with the sampled 72. The ring does not animate.

**Prose.** Three paragraphs, verbatim from the mock, first one bold. Do not add, remove or reorder claims. You may fix punctuation only. Copy, for reference:

> **Reconnect is an assistant that remembers your conversations. It records the meetings you have in person, keeps every word as it was said, and writes down what was decided and who promised what.**
>
> Ask it anything afterwards. What did we agree on pricing? When does the pilot start? What did Maya think about the timeline? It answers from what was actually said, and every answer shows the exact line so you can check it. Your own notes stay separate from the record, so it never puts words in anyone's mouth.
>
> Nothing you capture expires. Every meeting stays searchable for as long as you want it, on the free plan too. It is built for people whose important conversations happen away from a desk.

**Call to action.** One link, text "Get Reconnect for iPhone", with the gradient underline from the mock (ring colours, thickens on hover and focus, no transition under `prefers-reduced-motion`). Its `href` is the TestFlight public link, which the owner has not created yet. Put the placeholder `https://testflight.apple.com/join/PENDING` in exactly one place, and make `tools/check.py` fail while `PENDING` remains, so `main` cannot deploy until Claude swaps in the real link.

**Footer.** Left: `Copyright © 2026 Reconnect`. Right: `Privacy policy` → `https://konggu-api-production.up.railway.app/privacy`, `Terms of service` → `https://konggu-api-production.up.railway.app/terms` (both return 200 today and are the URLs the App Store listing uses), then the text `hello@reconnectaichat.com` as a `mailto:` link. Those two external hosts are the only external links allowed on the page.

**404.** `site/404.html`: the mark, one line "There is nothing at this address.", a link "Back to Reconnect" to `/`. Same styles.

## 3. Differences from the mock

- Remove the Google Fonts `<link>` and the `Inter` entries. Font stack is `-apple-system, system-ui, "Segoe UI", Roboto, sans-serif` only. No web fonts, no third-party requests of any kind.
- The mock has no `<head>`; the real page is a complete HTML5 document, `lang="en"`, with the head in §4.
- The mock's `href="#"` placeholders become the real targets above.
- The mock's theme hooks (`data-theme`) are not needed; keep only the `prefers-color-scheme` media query for the Night palette. Tokens stay as in the mock: light page `#F7F9FC` with the `#DCE6FC` top glow, text `#1F2A44` / `#5B6270`, link `#2D5BC7`; Night page `#0A0D14` with the `#172442` glow, text `#E7EBF3` / `#9AA3B5`, link `#7FA3F5`.
- Keep everything else: 18 px body (17 px under 520 px wide), 1.5 line height, 34 em measure, the prose vertically centred on desktop and near the top on phones, the footer wrapping to two lines on narrow screens, visible focus states.

## 4. Head

```
<title>Reconnect</title>
<meta name="description" content="Reconnect is an assistant that remembers your conversations. It records the meetings you have in person, keeps every word, and answers from what was actually said.">
<link rel="canonical" href="https://reconnectaichat.com/">
<meta property="og:type" content="website">  og:title "Reconnect"  og:description (same as above)
<meta property="og:url" content="https://reconnectaichat.com/">
<meta property="og:image" content="https://reconnectaichat.com/assets/og.png">  og:image:width 1200  og:image:height 630  og:image:alt "The Reconnect ring and wordmark"
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F7F9FC" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0A0D14" media="(prefers-color-scheme: dark)">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">   (and 192, 512)
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="viewport" content="width=device-width, initial-scale=1">
```

All CSS inline in one `<style>`. `index.html` must stay under 12 KB.

## 5. Assets

`tools/make_assets.py` (Python 3, Pillow, numpy if you want it) regenerates every file in `site/assets/` from the brand masters, so nothing is hand-edited:

- Favicons and the apple-touch-icon: the light app-icon master `01-app-icon-light.png` (opaque, square, 1024²) resized with Lanczos to 32, 180, 192 and 512 px.
- `og.png` 1200×630: the page background (`#F7F9FC` with the same faint `#DCE6FC` glow at the top), and `lockup-tight.png` (ring + "Reconnect") centred at about 44 % of the width. Nothing else on it.

Copy the masters you use into `tools/brand-masters/` with a one-line `SOURCE.md` naming the app-repo path and commit they came from, so the script runs without the app repo. Commit the generated outputs too.

## 6. Gate: `tools/check.py`

Runs locally and in CI before every deploy. Exit 1, with one line per failure, on any of:

- any CJK character anywhere under `site/`;
- any `<script` tag, inline event handler, or `javascript:` URL;
- any external URL other than the three allowed hosts (`konggu-api-production.up.railway.app`, `testflight.apple.com`, `reconnectaichat.com`) in `href`, `src` or `content` attributes;
- the string `PENDING` anywhere under `site/`;
- an `<img>` without `alt`;
- an internal link or asset reference that does not resolve to a file under `site/`;
- `index.html` over 12 KB, or any missing head element from §4;
- `lorem`, `TODO`, `FIXME` anywhere under `site/`.

Include a tiny `tools/serve.sh` (or a README line) for local preview with `python3 -m http.server --directory site 8080`.

## 7. Deploy workflow: `.github/workflows/pages.yml`

- Triggers: `push` to `main`, and `workflow_dispatch`.
- Permissions: `contents: read`, `pages: write`, `id-token: write`. Concurrency group `pages`, cancel-in-progress true.
- Job `check`: checkout, `python3 tools/check.py`.
- Job `deploy` (needs `check`, environment `github-pages`): `actions/configure-pages@v5`, `actions/upload-pages-artifact@v3` with `path: site`, `actions/deploy-pages@v4`. Pin the major versions shown.
- No `CNAME` file; the custom domain and HTTPS are set in repository settings by Claude at go-live. Do not enable Pages yourself (hard stop).

## 8. Evidence: `docs/evidence/wo-W01/`

- Screenshots of `/` and `/404.html` at 390×844, 820×1180 and 1440×900, each in light and dark (`prefers-color-scheme` emulated). Use Playwright with the installed Google Chrome, as `website-bakeoff/gpt-6/capture.mjs` in the workspace does, or Playwright's Chromium. Name them `index-390-light.png` and so on.
- A Lighthouse run of `index.html` served locally (`npx lighthouse http://127.0.0.1:8080/ --preset=desktop` and the default mobile run), saved as HTML. Target 100 in every category; report the actual numbers. If Lighthouse cannot run on this Mac, say so in `STATUS.md` and skip it; do not install global tooling to force it.
- `tools/check.py` output, clean.
- A 4× zoom crop of the ring next to `02-ring-gradient.png` from the brand masters, so the review can compare the band width and the lightest point.

## 9. Acceptance

1. The page reads exactly like §2 in both palettes at all three widths; nothing scrolls horizontally; the prose measure is at most 34 em.
2. `tools/check.py` passes except for the deliberate `PENDING` failure, which is the only line it prints.
3. No request leaves the page except to the three allowed hosts, and only when a link is clicked.
4. The workflow file validates (`actionlint` if available, otherwise careful reading) and would deploy `site/` on a push to `main`.
5. `STATUS.md` lists: branch and commit, what was run with results, anything in this order you could not do and why, and the two lines Claude must change at go-live (the TestFlight link; nothing else).

## 10. Not in this order

Pricing page, screenshots, a Mac mention, Chinese, analytics, a sign-in link, moving the privacy and terms pages onto this domain, any animation of the ring, the hero loop from `website-bakeoff`.
