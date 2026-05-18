"""Generate a 560x280 Kaggle card thumbnail from the verifier rejection screenshot.

Draws a clean dark green banner with the project name, the tagline, and a
prominent verifier rejection callout. No emojis, no decorative symbols.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "kaggle_card_1120x560.png"

W, H = 1120, 560
BG_LEFT = (15, 74, 58)      # deep green
BG_RIGHT = (27, 122, 62)    # green
ACCENT_RED = (176, 0, 32)
WHITE = (255, 255, 255)
SOFT = (220, 235, 226)


def _gradient(size: tuple[int, int], left: tuple, right: tuple) -> Image.Image:
    w, h = size
    base = Image.new("RGB", (w, h), left)
    px = base.load()
    for x in range(w):
        t = x / max(w - 1, 1)
        r = int(left[0] + (right[0] - left[0]) * t)
        g = int(left[1] + (right[1] - left[1]) * t)
        b = int(left[2] + (right[2] - left[2]) * t)
        for y in range(h):
            px[x, y] = (r, g, b)
    return base


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    img = _gradient((W, H), BG_LEFT, BG_RIGHT)
    draw = ImageDraw.Draw(img)

    title_font = _load_font(108, bold=True)
    sub_font = _load_font(36)
    badge_font = _load_font(36, bold=True)
    small_font = _load_font(28)

    draw.text((68, 52), "Maitri", font=title_font, fill=WHITE)
    draw.text(
        (68, 192),
        "Safety verified maternal referral co pilot",
        font=sub_font,
        fill=SOFT,
    )
    draw.text(
        (68, 240),
        "built on Gemma 4",
        font=sub_font,
        fill=SOFT,
    )

    # Verifier rejection callout
    badge_x, badge_y, badge_w, badge_h = 68, 336, 984, 160
    draw.rounded_rectangle(
        (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
        radius=28,
        fill=ACCENT_RED,
        outline=(255, 255, 255),
        width=4,
    )
    draw.text(
        (badge_x + 36, badge_y + 24),
        "Verifier rejected the draft",
        font=badge_font,
        fill=WHITE,
    )
    draw.text(
        (badge_x + 36, badge_y + 84),
        "Unsupported claim caught before reaching the community health worker.",
        font=small_font,
        fill=WHITE,
    )

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
