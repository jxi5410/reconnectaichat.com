#!/usr/bin/env python3
"""Offline, standard-library deployment gate. Success is silent; failures exit 1."""

import argparse
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOSTS = {"konggu-api-production.up.railway.app", "testflight.apple.com", "reconnectaichat.com"}
DESCRIPTION = ("Reconnect is an assistant that remembers your conversations. It records the meetings "
               "you have in person, keeps every word, and answers from what was actually said.")
CJK = re.compile("[\u2e80-\u9fff\uac00-\ud7af\uf900-\ufaff\ufe30-\ufe4f\uff66-\uff9f"
                 "\U0001b000-\U0001b2ff\U00020000-\U000323af]")
URL = re.compile(r"(?:[a-z][a-z0-9+.-]*:)?//[^\s\"'<>]+", re.I)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags, self.head_tags, self.ids = [], [], set()
        self.in_head = self.in_title = self.in_style = False
        self.title = self.css = ""
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if tag == "head":
            self.in_head = True
        if self.in_head:
            self.head_tags.append((tag, attributes))
        self.in_title = tag == "title" and self.in_head or self.in_title
        self.in_style = tag == "style" or self.in_style
        if attributes.get("id"):
            self.ids.add(attributes["id"])

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if tag == "title":
            self.in_title = False
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_style:
            self.css += data


def check_site(site):
    site = site.resolve()
    failures, documents = [], {}

    def fail(path, message):
        line = f"site/{path.relative_to(site).as_posix()}: {message}"
        if line not in failures:
            failures.append(line)

    required = ["index.html", "404.html", "robots.txt", "sitemap.xml", "assets/favicon-32.png",
                "assets/favicon-192.png", "assets/favicon-512.png", "assets/apple-touch-icon.png", "assets/og.png"]
    for name in required:
        if not (site / name).is_file():
            fail(site / name, "required file is missing.")

    for path in sorted(site.rglob("*")):
        if path.is_symlink():
            fail(path, "symlinks are not deployable site files.")
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in {".js", ".mjs", ".cjs", ".woff", ".woff2", ".ttf", ".otf"}:
            fail(path, "JavaScript and web font files are forbidden.")
        raw = path.read_bytes()
        if b"PENDING" in raw:
            fail(path, "PENDING placeholder must be replaced before deployment.")
        if re.search(rb"lorem|TODO|FIXME", raw, re.I):
            fail(path, "draft marker (lorem, TODO or FIXME).")
        try:
            source = raw.decode("utf-8")
        except UnicodeDecodeError:
            # Generated PNGs are binary, not Unicode documents.
            if path.suffix.lower() != ".png":
                fail(path, "site text must be UTF-8.")
            continue
        decoded = unescape(source)
        if CJK.search(decoded):
            fail(path, "CJK character is forbidden.")
        if "PENDING" in decoded:
            fail(path, "PENDING placeholder must be replaced before deployment.")
        if re.search(r"lorem|TODO|FIXME", decoded, re.I):
            fail(path, "draft marker (lorem, TODO or FIXME).")
        if re.search(r"<\s*script", decoded, re.I):
            fail(path, "script tag is forbidden.")
        if re.search(r"javascript\s*:", decoded, re.I):
            fail(path, "javascript: URL is forbidden.")
        if path.suffix.lower() == ".html":
            documents[path] = Document(source)

    def reference(path, value, resource=False):
        value = value.strip()
        normalized = re.sub(r"[\x00-\x20]", "", value)
        if normalized.lower().startswith("javascript:"):
            fail(path, "javascript: URL is forbidden.")
            return
        try:
            url = urlsplit(normalized)
        except ValueError:
            fail(path, f"invalid URL: {value}")
            return
        if url.scheme == "mailto" and not resource:
            if value != "mailto:hello@reconnectaichat.com":
                fail(path, "unexpected mailto link.")
            return
        if url.netloc or url.scheme:
            if url.scheme not in ("", "https") or url.hostname not in ALLOWED_HOSTS or url.username or url.password:
                fail(path, f"external URL is not allowed: {value}")
                return
            if url.hostname != "reconnectaichat.com":
                if resource:
                    fail(path, f"external resource request is forbidden: {value}")
                return
        target_path = unquote(url.path)
        target = site / target_path.lstrip("/") if target_path.startswith("/") else path.parent / target_path
        if not target_path:
            target = path
        target = target.resolve()
        if not target.is_relative_to(site):
            fail(path, f"internal reference leaves site/: {value}")
            return
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            fail(path, f"internal reference does not resolve: {value}")
        elif url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids:
            fail(path, f"internal fragment does not resolve: {value}")

    for path, doc in documents.items():
        for tag, attrs in doc.tags:
            for name, value in attrs.items():
                if name.startswith("on"):
                    fail(path, f"inline event handler is forbidden: {name}")
                if value and re.sub(r"\s", "", value).lower().startswith("javascript:"):
                    fail(path, "javascript: URL is forbidden.")
                if name in {"href", "src", "content", "poster", "action"} and value is not None:
                    if name == "content":
                        for found in URL.findall(value):
                            reference(path, found)
                        if not URL.search(value) and (attrs.get("property") in {"og:image", "og:url"}
                                                     or attrs.get("name") == "twitter:image"):
                            reference(path, value)
                    else:
                        reference(path, value, resource=name != "href" or tag != "a")
                if name == "srcset" and value:
                    for candidate in value.split(","):
                        if candidate.strip():
                            reference(path, candidate.strip().split()[0], resource=True)
            if tag == "img" and "alt" not in attrs:
                fail(path, "img element is missing alt text.")
            if tag in {"iframe", "object", "embed", "script"} or "srcdoc" in attrs:
                fail(path, f"active embedded content is forbidden: {tag}")
            if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
                fail(path, "meta refresh is forbidden.")
        css = doc.css + "\n" + "\n".join(attrs.get("style", "") or "" for _, attrs in doc.tags)
        if re.search(r"@import|@font-face", css, re.I):
            fail(path, "CSS imports and web fonts are forbidden.")
        for value in re.findall(r"url\(\s*['\"]?(.*?)['\"]?\s*\)", css, re.I):
            reference(path, value, resource=True)

    index = site / "index.html"
    if index.is_file() and index.stat().st_size > 12 * 1024:
        fail(index, f"index.html exceeds 12 KB ({index.stat().st_size} bytes).")
    if index in documents:
        doc = documents[index]
        expected = [
            ("meta", {"name": "description", "content": DESCRIPTION}),
            ("link", {"rel": "canonical", "href": "https://reconnectaichat.com/"}),
            ("meta", {"property": "og:type", "content": "website"}),
            ("meta", {"property": "og:title", "content": "Reconnect"}),
            ("meta", {"property": "og:description", "content": DESCRIPTION}),
            ("meta", {"property": "og:url", "content": "https://reconnectaichat.com/"}),
            ("meta", {"property": "og:image", "content": "https://reconnectaichat.com/assets/og.png"}),
            ("meta", {"property": "og:image:width", "content": "1200"}),
            ("meta", {"property": "og:image:height", "content": "630"}),
            ("meta", {"property": "og:image:alt", "content": "The Reconnect ring and wordmark"}),
            ("meta", {"name": "twitter:card", "content": "summary_large_image"}),
            ("meta", {"name": "theme-color", "content": "#F7F9FC", "media": "(prefers-color-scheme: light)"}),
            ("meta", {"name": "theme-color", "content": "#0A0D14", "media": "(prefers-color-scheme: dark)"}),
            ("link", {"rel": "apple-touch-icon", "href": "/assets/apple-touch-icon.png"}),
            ("meta", {"name": "viewport", "content": "width=device-width, initial-scale=1"}),
            ("meta", {"charset": "utf-8"}),
        ] + [("link", {"rel": "icon", "type": "image/png", "sizes": f"{size}x{size}",
                       "href": f"/assets/favicon-{size}.png"}) for size in (32, 192, 512)]
        for tag, attrs in expected:
            if not any(t == tag and all(a.get(k) == v for k, v in attrs.items()) for t, a in doc.head_tags):
                fail(index, f"missing or incorrect head element: {tag} {attrs}")
        if doc.title.strip() != "Reconnect":
            fail(index, "missing or incorrect head title.")
        if not any(tag == "html" and attrs.get("lang") == "en" for tag, attrs in doc.tags):
            fail(index, "html lang must be en.")
        if sum(tag == "style" for tag, _ in doc.tags) != 1:
            fail(index, "exactly one inline style element is required.")
        if not index.read_text().lstrip().lower().startswith("<!doctype html>"):
            fail(index, "HTML5 doctype is required.")
    return failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "site", help="Site root; defaults to this repo's site/.")
    failures = check_site(parser.parse_args().site)
    for failure in failures:
        print(failure)
    raise SystemExit(1 if failures else 0)
