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

The approved three paragraphs, iPhone call to action, metadata, and footer live
in `site/index.html`. `site/404.html` contains the missing-address message and home
link. Each document has one inline stylesheet; keep their shared styles identical.
The ring is 40 px, with a 64% inner radius and 72 sampled cosine-gradient stops
including the matching 0/360-degree endpoints. Its focus outline sits on the
unmasked link so keyboard focus remains visible.

- `docs/WO-W01-website.md`: binding implementation order.
- `docs/PROPOSAL-2026-10-06.md`: approved proposal and owner decisions.
- `docs/mock-2026-10-06.html`: historical approved mock; never deployed.
- `docs/evidence/wo-W01/`: browser captures, Lighthouse reports, and gate output.
- `STATUS.md`: implementation status, verification, and handoff questions.

## Regenerate assets

With Python 3 and Pillow available:

```sh
python3 tools/make_assets.py
python3 tools/make_assets.py --ring-stops
```

All five deployed PNGs are generated from the committed masters in
`tools/brand-masters/`; `SOURCE.md` records their source commit. No app checkout or
font file is needed. `--ring-stops` prints the gradient stops used in both pages.

## Delivery

`.github/workflows/pages.yml` checks the site before uploading `site/` and
deploying it on a push to `main`, or a manual workflow dispatch. The deploy job
depends on the gate and uses the `github-pages` environment.

Before go-live, Claude replaces the single TestFlight placeholder in
`site/index.html` with the owner's real public join URL and reruns the gate.
Repository visibility, Pages enablement, custom-domain settings, DNS, and HTTPS
are separate owner/Claude go-live work. This work order does not change them.
There is no `CNAME` file.
