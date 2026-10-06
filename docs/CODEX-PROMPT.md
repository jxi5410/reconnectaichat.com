# Prompt for Codex — WO-W01 reconnectaichat.com

Copy everything below the line into Codex.

---

Implement work order WO-W01: the one-screen website for reconnectaichat.com.

Read, in this order, before writing anything:
1. `/Users/jiexi/Reconnect/website/WO-W01-website.md` — the order. It is complete and binding.
2. `/Users/jiexi/Reconnect/website/PROPOSAL-2026-10-06.md` — the approved proposal and the owner's decisions (§8).
3. `/Users/jiexi/Reconnect/website/mock-2026-10-06.html` — the approved mock. The real page is built from it with the differences listed in the order's §3.
4. `/Users/jiexi/Reconnect/main/docs/brand/README.md` and `/Users/jiexi/Reconnect/main/tools/brand/export_logo.py` — read only, for the ring's exact geometry and colours.

Work only in `/Users/jiexi/Reconnect/website-repo`, a clone of `jxi5410/reconnectaichat.com` whose `main` already holds the proposal, order and mock under `docs/`. Branch `wo-W01` from `main`, commit as you go, and push the branch. Never modify `/Users/jiexi/Reconnect/main` or any other checkout.

Deliver everything in the order's §1 layout: `site/` (index, 404, robots, sitemap, assets), `tools/make_assets.py`, `tools/check.py`, `.github/workflows/pages.yml`, `README.md`, `docs/evidence/wo-W01/` with the screenshots, Lighthouse report and gate output, and `STATUS.md` with the final commit hash.

Rules that override anything you would normally do: no JavaScript, no web fonts, no third-party requests, no analytics, no Chinese characters anywhere, no new claims in the copy, no accounts, no DNS, no GitHub settings, no Pages enablement. The TestFlight link stays as the `PENDING` placeholder and the gate must fail on it; that is intended. If anything in the order cannot be done, stop on that item, write the question in `STATUS.md`, and finish the rest.

Report back with the branch, the commit hash, the gate output, and the Lighthouse numbers.
