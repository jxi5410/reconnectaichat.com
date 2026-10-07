#!/usr/bin/env python3
"""Exercise the deployment boundary on disposable copies, never the real site."""

import shutil
import tempfile
import unittest
from pathlib import Path

from check import ROOT, check_site


class GateTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".local"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name) / "site"
        shutil.copytree(ROOT / "site", self.site)
        self.index = self.site / "index.html"
        self.original = self.index.read_text().replace("/join/PENDING", "/join/Example1")
        self.index.write_text(self.original)

    def test_actual_site_has_only_the_deliberate_blocker(self):
        self.assertEqual(check_site(ROOT / "site"), [
            "site/index.html: PENDING placeholder must be replaced before deployment."])

    def test_ready_copy_passes_silently(self):
        self.assertEqual(check_site(self.site), [])

    def test_rejects_unsafe_or_incomplete_html(self):
        cases = [
            ("<p>\u4e2d</p>", "CJK"),
            ("<p>&#x4e2d;</p>", "CJK"),
            ("<ScRiPt></ScRiPt>", "script tag"),
            ('<p onpointerenter="alert(1)">Text</p>', "inline event handler"),
            ('<a href="java&#x09;script:alert(1)">Link</a>', "javascript:"),
            ('<a href="https://example.com/">Link</a>', "external URL"),
            ('<a href="//example.com/">Link</a>', "external URL"),
            ('<meta content="https://testflight.apple.com.evil.test/">', "external URL"),
            ('<meta content="https://testflight.apple.com@evil.test/">', "external URL"),
            ('<img src="/assets/og.png">', "missing alt"),
            ('<img alt="Ring" src="/missing.png">', "does not resolve"),
            ('<a href="/missing/">Link</a>', "does not resolve"),
            ('<a href="#missing">Link</a>', "fragment does not resolve"),
            ('<img alt="Ring" src="/%2e%2e/secret.png">', "leaves site"),
            ('<img alt="Ring" src="https://testflight.apple.com/icon.png">', "external resource"),
            ('<img alt="Ring" srcset="https://example.com/ring.png 2x">', "external URL"),
            ('<style>@import "https://example.com/site.css";</style>', "CSS imports"),
            ('<style>body { background:url(https://example.com/a.png) }</style>', "external URL"),
            ('<iframe srcdoc="Hello"></iframe>', "embedded content"),
            ("<p>PENDING</p>", "PENDING"),
            ("<p>lorem</p>", "draft marker"),
            ("<p>TODO</p>", "draft marker"),
            ("<p>FIXME</p>", "draft marker"),
        ]
        for addition, reason in cases:
            with self.subTest(reason=reason, addition=addition):
                self.index.write_text(self.original.replace("</body>", addition + "</body>"))
                self.assertTrue(any(reason in failure for failure in check_site(self.site)))

    def test_every_required_head_element_is_enforced(self):
        for line in self.original.splitlines():
            if line.strip().startswith(("<meta", "<link", "<title")):
                with self.subTest(element=line.strip()):
                    self.index.write_text(self.original.replace(line, ""))
                    self.assertTrue(any("head" in failure for failure in check_site(self.site)))

    def test_size_limit(self):
        self.index.write_text(self.original + " " * (12 * 1024))
        self.assertTrue(any("exceeds 12 KB" in failure for failure in check_site(self.site)))

    def test_other_files_are_scanned(self):
        (self.site / "robots.txt").write_text("PENDING\n\u4e2d\nFIXME\n")
        failures = check_site(self.site)
        self.assertEqual(len(failures), 3)
        self.assertTrue(all(failure.startswith("site/robots.txt:") for failure in failures))

    def test_missing_asset(self):
        (self.site / "assets/og.png").unlink()
        self.assertTrue(any("required file" in failure for failure in check_site(self.site)))

    def test_symlink_is_rejected(self):
        (self.site / "alias.html").symlink_to(self.index)
        self.assertTrue(any("symlink" in failure for failure in check_site(self.site)))

    def test_non_utf8_html_is_rejected(self):
        self.index.write_bytes(b"\xff" + self.original.encode())
        self.assertTrue(any("UTF-8" in failure for failure in check_site(self.site)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
