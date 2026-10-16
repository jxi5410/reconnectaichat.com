# reconnectaichat.com

The Reconnect website: one screen, system fonts, inline CSS, and no JavaScript,
analytics, web fonts, or external resource requests. Only `site/` is deployed.

## Preview

From this repository, run:

```sh
python3 -m http.server --directory site 8080
```

Open `http://127.0.0.1:8080/` or `http://127.0.0.1:8080/404.html`.
The palette follows the system's light/dark appearance. No build step is needed.

## Check

```sh
python3 tools/check.py
python3 tools/test_check.py
```

The gate uses Python's standard library, prints one line per failure, and exits 1
if anything fails. Success is silent. The intentional TestFlight placeholder in
`site/index.html` is currently its only failure and blocks the Pages deploy job.
The test suite exercises the gate on temporary copies in ignored `.local/`.

## Copy and styles

The page copy (four paragraphs, the iPhone call to action), metadata, and footer
live in `site/index.html`. The 16 October 2026 update (voice-first lead, one
"coming next" line, black and white) is recorded in `docs/update-2026-10-16.md`.
`site/404.html` contains the missing-address message and home link. Each document
has one inline stylesheet; keep their shared styles identical. The ring is a 40 px
circle in ink with a 64% inner radius (a 7.2 px border). There is no accent colour.

- `docs/update-2026-10-16.md`: the owner's choices for the current copy and look.
- `docs/WO-W01-website.md`: binding implementation order.
- `docs/PROPOSAL-2026-10-06.md`: approved proposal and owner decisions.
- `docs/mock-2026-10-06.html`: historical approved mock; never deployed.
- `docs/evidence/wo-W01/`: browser captures, Lighthouse reports, and gate output.
- `STATUS.md`: implementation status, verification, and handoff questions.

## Regenerate assets

With Python 3 and Pillow available:

```sh
python3 tools/make_assets.py
```

The four icons are drawn as an ink ring on white. The share image paints the
ring-and-wordmark lockup in `tools/brand-masters/lockup-tight.png` in ink.

## Delivery

`.github/workflows/pages.yml` checks the site before uploading `site/` and
deploying it on a push to `main`, or a manual workflow dispatch. The deploy job
depends on the gate and uses the `github-pages` environment.

Before go-live, Claude replaces the single TestFlight placeholder in
`site/index.html` with the owner's real public join URL and reruns the gate.
Repository visibility, Pages enablement, custom-domain settings, DNS, and HTTPS
are separate owner/Claude go-live work. This work order does not change them.
There is no `CNAME` file.
