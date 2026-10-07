#!/usr/bin/env python3
"""Regenerate every deployed image from the committed masters; requires Pillow."""

import argparse
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "tools/brand-masters"
ASSETS = ROOT / "site/assets"


def ring_stops():
    """72 evenly spaced stops, including the identical 0/360-degree seam."""
    light, dark = (185, 208, 251), (95, 132, 230)
    stops = []
    for sample in range(72):
        angle = sample * 360 / 71
        blend = (1 - math.cos(math.radians(angle - 315))) / 2
        color = "#" + "".join(f"{round(a + (b - a) * blend):02X}" for a, b in zip(light, dark))
        position = f"{angle:.6f}".rstrip("0").rstrip(".") if sample else "0"
        stops.append(f"{color} {position}deg")
    return ",\n      ".join(stops)


def make_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    with Image.open(MASTERS / "01-app-icon-light.png") as master:
        assert master.size == (1024, 1024)
        for size, filename in [(32, "favicon-32.png"), (180, "apple-touch-icon.png"),
                               (192, "favicon-192.png"), (512, "favicon-512.png")]:
            master.convert("RGB").resize((size, size), Image.Resampling.LANCZOS).save(ASSETS / filename)

    width, height = 1200, 630
    page, glow = (247, 249, 252), (220, 230, 252)
    # Match radial-gradient(90% 55% at 50% -20%, glow 0%, transparent 70%).
    pixels = []
    for y in range(height):
        for x in range(width):
            radius = math.hypot((x + 0.5 - width * 0.5) / (width * 0.9),
                                (y + 0.5 + height * 0.2) / (height * 0.55))
            alpha = max(0, 1 - radius / 0.7)
            pixels.append(tuple(round(bg + (fg - bg) * alpha) for bg, fg in zip(page, glow)))
    background = Image.new("RGB", (width, height))
    background.putdata(pixels)
    with Image.open(MASTERS / "lockup-tight.png") as master:
        lockup_width = round(width * 0.44)
        lockup = master.convert("RGBA").resize(
            (lockup_width, round(master.height * lockup_width / master.width)), Image.Resampling.LANCZOS)
        background.paste(lockup, ((width - lockup.width) // 2, (height - lockup.height) // 2), lockup)
    background.save(ASSETS / "og.png")
    print("Generated 5 images in site/assets/.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ring-stops", action="store_true", help="Print the 72 inline CSS ring stops.")
    args = parser.parse_args()
    if args.ring_stops:
        print(ring_stops())
    else:
        make_assets()
