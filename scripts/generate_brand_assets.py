#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent.parent
BRAND_DIR = ROOT / "assets" / "brand"
FONT_DIR = ROOT / "assets" / "fonts"

DISPLAY_FONT = FONT_DIR / "Tektur-Medium.ttf"
BODY_FONT = FONT_DIR / "InstrumentSans-Regular.ttf"
BODY_BOLD_FONT = FONT_DIR / "InstrumentSans-Bold.ttf"

BG = (7, 16, 27, 255)
PANEL = (12, 24, 39, 236)
PANEL_EDGE = (35, 60, 90, 255)
GRID = (50, 77, 106, 58)
ICE = (229, 239, 255, 255)
SLATE = (132, 155, 182, 255)
ORANGE = (255, 134, 56, 255)
ORANGE_SOFT = (255, 134, 56, 115)
BLUE_SOFT = (110, 164, 255, 105)


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int, spacing: int) -> None:
    for x in range(spacing, width, spacing):
        draw.line((x, 0, x, height), fill=GRID, width=1)
    for y in range(spacing, height, spacing):
        draw.line((0, y, width, y), fill=GRID, width=1)


def scale_points(points: list[tuple[float, float]], width: int, height: int) -> list[tuple[int, int]]:
    return [(round(width * x), round(height * y)) for x, y in points]


def draw_trace(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    for x, y in points[:-1]:
        radius = max(3, width // 5)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_glow(base: Image.Image, points: list[tuple[int, int]], color: tuple[int, int, int, int], width: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.line(points, fill=color, width=width, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(6, width // 4)))
    base.alpha_composite(glow)


def draw_mark(base: Image.Image, with_panel: bool = False) -> None:
    width, height = base.size
    draw = ImageDraw.Draw(base)

    if with_panel:
        pad = max(24, width // 14)
        draw.rounded_rectangle(
            (pad, pad, width - pad, height - pad),
            radius=width // 5,
            fill=PANEL,
            outline=PANEL_EDGE,
            width=max(2, width // 120),
        )
        draw_grid(draw, width, height, max(48, width // 10))

    left_outer = scale_points([(0.22, 0.16), (0.36, 0.39), (0.50, 0.82)], width, height)
    left_inner = scale_points([(0.33, 0.18), (0.43, 0.43), (0.50, 0.71)], width, height)
    right_inner = scale_points([(0.67, 0.18), (0.57, 0.43), (0.50, 0.71)], width, height)
    right_outer = scale_points([(0.78, 0.16), (0.64, 0.39), (0.50, 0.82)], width, height)
    center_signal = scale_points([(0.50, 0.12), (0.50, 0.26), (0.50, 0.48)], width, height)
    sweep_box = (
        round(width * 0.18),
        round(height * 0.06),
        round(width * 0.82),
        round(height * 0.54),
    )

    draw_glow(base, left_outer, BLUE_SOFT, max(18, width // 18))
    draw_glow(base, right_outer, ORANGE_SOFT, max(18, width // 18))
    draw_glow(base, center_signal, (220, 236, 255, 100), max(12, width // 28))

    draw_trace(draw, left_outer, ICE, max(14, width // 22))
    draw_trace(draw, left_inner, (123, 187, 255, 230), max(8, width // 34))
    draw_trace(draw, right_inner, (255, 194, 128, 235), max(8, width // 34))
    draw_trace(draw, right_outer, ORANGE, max(14, width // 22))
    draw_trace(draw, center_signal, ICE, max(6, width // 48))

    draw.arc(sweep_box, start=202, end=338, fill=(96, 136, 189, 210), width=max(4, width // 64))
    draw.arc(sweep_box, start=214, end=328, fill=(255, 147, 72, 170), width=max(2, width // 96))

    core_x, core_y = round(width * 0.50), round(height * 0.82)
    outer = max(18, width // 24)
    inner = max(8, width // 52)
    draw.ellipse((core_x - outer, core_y - outer, core_x + outer, core_y + outer), fill=(255, 147, 72, 36), outline=ORANGE)
    draw.ellipse((core_x - inner, core_y - inner, core_x + inner, core_y + inner), fill=ICE)

    for px, py in [(0.18, 0.22), (0.82, 0.22), (0.26, 0.64), (0.74, 0.64), (0.50, 0.10)]:
        x, y = round(width * px), round(height * py)
        r = max(3, width // 120)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=ORANGE if px > 0.5 else ICE)


def create_logo_mark() -> None:
    image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    draw_mark(image)
    image.save(BRAND_DIR / "logo-mark.png")


def create_wordmark() -> None:
    image = Image.new("RGBA", (1800, 560), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    mark = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    draw_mark(mark, with_panel=True)
    image.alpha_composite(mark, (28, 72))

    headline = font(DISPLAY_FONT, 170)
    meta = font(BODY_BOLD_FONT, 34)
    small = font(BODY_FONT, 24)

    draw.text((494, 110), "VOX", font=headline, fill=ICE)
    draw.text((928, 110), "CPM", font=headline, fill=ORANGE)
    draw.text((500, 298), "TOKENIZER-FREE MULTILINGUAL TTS", font=meta, fill=SLATE)
    draw.line((500, 348, 1456, 348), fill=(62, 90, 124, 255), width=3)
    draw.text((500, 384), "VOICE DESIGN // CONTROLLABLE CLONING // 48KHZ AUDIO", font=small, fill=(166, 185, 209, 255))
    image.save(BRAND_DIR / "logo-wordmark.png")


def create_favicons() -> None:
    base = Image.new("RGBA", (512, 512), BG)
    draw_mark(base, with_panel=True)
    base.save(BRAND_DIR / "favicon.png")
    base.resize((180, 180), Image.Resampling.LANCZOS).save(BRAND_DIR / "apple-touch-icon.png")
    base.resize((32, 32), Image.Resampling.LANCZOS).save(BRAND_DIR / "favicon-32x32.png")
    base.resize((16, 16), Image.Resampling.LANCZOS).save(BRAND_DIR / "favicon-16x16.png")
    base.save(BRAND_DIR / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


def create_social_card() -> None:
    width, height = 1200, 630
    image = Image.new("RGBA", (width, height), BG)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((32, 32, width - 32, height - 32), radius=38, outline=(31, 52, 80, 255), width=4)
    draw_grid(draw, width, height, 72)
    draw.ellipse((-130, -180, 420, 370), fill=(14, 27, 45, 255))
    draw.ellipse((760, 310, 1330, 880), fill=(10, 20, 35, 255))

    mark = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    draw_mark(mark, with_panel=True)
    image.alpha_composite(mark, (84, 106))

    headline = font(DISPLAY_FONT, 74)
    subhead = font(BODY_BOLD_FONT, 30)
    body = font(BODY_FONT, 24)

    draw.text((570, 132), "VOXCPM2", font=headline, fill=ICE)
    draw.text((570, 224), "Tokenizer-free multilingual TTS", font=subhead, fill=ORANGE)
    draw.line((570, 278, 1076, 278), fill=(61, 92, 126, 255), width=3)
    draw.text((570, 320), "30 languages, voice design, controllable cloning,", font=body, fill=(181, 198, 220, 255))
    draw.text((570, 356), "48kHz output, and a direct path to continuous", font=body, fill=(181, 198, 220, 255))
    draw.text((570, 392), "speech representations.", font=body, fill=(181, 198, 220, 255))
    draw.text((570, 444), "GitHub / Docs / Playground / Audio Samples", font=body, fill=SLATE)
    draw.text((570, 508), "voxcpm.space", font=subhead, fill=ICE)
    image.save(BRAND_DIR / "social-card.png")


def main() -> None:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    create_logo_mark()
    create_wordmark()
    create_favicons()
    create_social_card()
    print(f"Brand assets generated in {BRAND_DIR}")


if __name__ == "__main__":
    main()
