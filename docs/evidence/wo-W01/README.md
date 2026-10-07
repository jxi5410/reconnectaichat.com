# WO-W01 verification, 7 October 2026

All evidence covers the committed `site/` and tools from implementation commit
`de09f116` (the full hash is recorded in the root status report). No public site
was deployed. The two local Lighthouse runs used the unchanged page, including
its intentional TestFlight placeholder.

## Browser evidence

Installed Google Chrome was driven headlessly with Playwright. Each page was
loaded at 390 x 844, 820 x 1180, and 1440 x 900, with light and dark colour schemes
emulated, English locale, and a device scale factor of 1. The twelve required
PNG captures are named `index-WIDTH-PALETTE.png` and `404-WIDTH-PALETTE.png`.
`contact-sheet.png` collects them for review.

`browser-checks.json` records the browser version, dimensions, text, styles,
focus checks, and page requests for every capture. Checks passed for:

- Exact approved three-paragraph copy and 600-weight first paragraph.
- Requested palettes, 17/18 px body, 1.5 line height, and maximum 34 em measure.
- No horizontal or vertical scrolling at the six required viewport/palette pairs.
- No scripts, no page errors, and no page requests outside localhost.
- Visible keyboard focus on the home link, CTA, and all footer links.
- Static 40 px ring; CTA transition 0.24 seconds normally and zero with reduced motion.
- Matching styles between the index and 404 documents.

At 390 px the unchanged mock footer rules produce three text rows. This is the
only visual specification conflict and is recorded as a question in `STATUS.md`.

`focus-home-390-light.png` shows the focus outline on the unmasked home anchor.
`ring-css-4x.png` is a genuine 4x Chrome rendering of the 40 px CSS ring.
`ring-comparison-4x.png` puts it beside the committed `02-ring-gradient.png`
reference, normalized to the same outer diameter. Both use the 18%-of-diameter
band and upper-left lightest point. The reference has the export script's tube
shading; the CSS ring uses the order's specified cosine-only colour blend.
The 72 evenly spaced CSS stops include both 0 and 360 degrees with identical colour.

## Lighthouse

Lighthouse 13.5.0 was downloaded into ignored `.local/npm-cache` by `npx`;
no global tools were installed. Serve the page with:

```sh
python3 -m http.server --bind 127.0.0.1 --directory site 8080
```

Desktop command, from the repository root:

```sh
CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
npm_config_cache="$PWD/.local/npm-cache" \
npx --yes lighthouse http://127.0.0.1:8080/ --preset=desktop \
  --chrome-flags='--headless --disable-background-networking' \
  --output=html --output=json \
  --output-path=docs/evidence/wo-W01/lighthouse-desktop --quiet
```

The default mobile run used the same command without `--preset=desktop` and with
`lighthouse-mobile` as its output basename. Both reports are saved as HTML and
JSON. `lighthouse-summary.json` records scores, timestamps, metrics, warnings,
and observed network requests.

| Mode | Performance | Accessibility | Best practices | SEO | Agentic browsing |
| --- | ---: | ---: | ---: | ---: | ---: |
| Desktop | 100 | 100 | 100 | 100 | 100 |
| Mobile | 100 | 100 | 100 | 100 | 100 |

Both runs have zero warnings, zero blocking time, and zero layout shift. Only
the local document and local 32 px favicon were requested. These are local
audit results; public hosting, HTTPS, and a functioning TestFlight join URL
remain go-live work.

## Gate, assets, and workflow

`gate-output.txt` is unedited stdout from `python3 tools/check.py`.
`gate-exit-code.txt` records its deliberate exit code 1. It prints exactly one
failure, for the TestFlight placeholder. `gate-tests.txt` records nine passing
test methods, including all required head fields and 23 unsafe-content cases.
The test suite proves a disposable copy with the placeholder replaced passes
silently; the real `site/` keeps the placeholder.

`asset-checks.json` records all five output sizes and SHA-256 hashes. A second
run of `tools/make_assets.py` reproduced byte-identical outputs. Shared inline
styles, the generated ring stops, the single placeholder, whitespace, and absence
of CJK in source/tools/docs/workflow text were also checked.

`workflow-review.txt` records careful review against every requirement in section 7.
`actionlint` is not installed. The workflow was not dispatched, and repository
settings and Pages enablement were not changed.
