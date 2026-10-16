#!/usr/bin/env python3
"""Regenerate every deployed image in black and white (v4 look); requires Pillow."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "tools/brand-masters"
ASSETS = ROOT / "site/assets"
PAGE, INK = (255, 255, 255), (11, 11, 12)
INNER = 0.64  # inner radius as a share of the outer radius, as in the page's ring
SUPERSAMPLE = 8


def ring_icon(size, diameter):
    """An ink ring on white, `diameter` as a share of the square, drawn large and scaled down."""
    big = size * SUPERSAMPLE
    image = Image.new("RGB", (big, big), PAGE)
    draw = ImageDraw.Draw(image)
    centre, outer = big / 2, big * diameter / 2
    draw.ellipse([centre - outer, centre - outer, centre + outer, centre + outer], fill=INK)
    inner = outer * INNER
    draw.ellipse([centre - inner, centre - inner, centre + inner, centre + inner], fill=PAGE)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def make_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    # The app icon's ring spans 592 of 1024 px; the tab icon is larger so it reads at 32 px.
    for size, diameter, filename in [(32, 0.78, "favicon-32.png"), (180, 0.578, "apple-touch-icon.png"),
                                     (192, 0.578, "favicon-192.png"), (512, 0.578, "favicon-512.png")]:
        ring_icon(size, diameter).save(ASSETS / filename)

    width, height = 1200, 630
    background = Image.new("RGB", (width, height), PAGE)
    with Image.open(MASTERS / "lockup-tight.png") as master:
        # Keep the lockup's shapes (ring and wordmark) and paint them in ink.
        alpha = master.convert("RGBA").getchannel("A")
        lockup = Image.new("RGBA", master.size, INK + (255,))
        lockup.putalpha(alpha)
        lockup_width = round(width * 0.44)
        lockup = lockup.resize((lockup_width, round(master.height * lockup_width / master.width)),
                               Image.Resampling.LANCZOS)
        background.paste(lockup, ((width - lockup.width) // 2, (height - lockup.height) // 2), lockup)
    background.save(ASSETS / "og.png")
    print("Generated 5 images in site/assets/.")


if __name__ == "__main__":
    make_assets()
