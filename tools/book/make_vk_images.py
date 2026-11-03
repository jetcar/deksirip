"""Avatar and cover for the VK community, in the palette of the YouTube covers."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from make_video import ACCENT, BACKGROUND, BOOK_SUBTITLE, BOOK_TITLE, MUTED, TEXT, font
from synthesize_audio import ROOT

OUT = ROOT / "social" / "vk"


def wheat(image: Image.Image, x: float, y_top: float, y_bottom: float, grain: float, colour) -> None:
    """A stylised ear of wheat — the book's unit of account: stem, paired grains, awns."""
    draw = ImageDraw.Draw(image)
    draw.line((x, y_top + grain, x, y_bottom), fill=colour, width=max(2, int(grain * 0.14)))
    w, h = int(grain * 0.62), int(grain * 1.25)
    rows = 6
    for row in range(rows):
        cy = y_top + grain * 1.2 + row * grain * 0.95
        for side in (-1, 1):
            seed = Image.new("RGBA", (h * 2, h * 2), (0, 0, 0, 0))
            ImageDraw.Draw(seed).ellipse((h - w / 2, h - h / 2, h + w / 2, h + h / 2), fill=colour)
            seed = seed.rotate(-side * 30, resample=Image.BICUBIC)
            cx = x + side * grain * 0.42
            image.paste(seed, (int(cx - h), int(cy - h)), seed)
            # awn: a thin line from the grain tip, outward and up
            tip = (cx + side * grain * 0.3, cy - grain * 0.5)
            draw.line((tip, (tip[0] + side * grain * 0.9, tip[1] - grain * 1.6)), fill=colour, width=max(1, int(grain * 0.06)))
    top = Image.new("RGBA", (h * 2, h * 2), (0, 0, 0, 0))
    ImageDraw.Draw(top).ellipse((h - w / 2, h - h / 2, h + w / 2, h + h / 2), fill=colour)
    image.paste(top, (int(x - h), int(y_top + grain * 0.35 - h)), top)
    draw.line((x, y_top - grain * 0.25, x, y_top - grain * 1.9), fill=colour, width=max(1, int(grain * 0.06)))


def avatar() -> Path:
    size = 800
    image = Image.new("RGB", (size, size), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.ellipse((70, 70, size - 70, size - 70), outline=ACCENT, width=14)
    wheat(image, size / 2, 230, 650, 50, ACCENT)
    path = OUT / "avatar.png"
    image.save(path)
    return path


def cover() -> Path:
    width, height = 1920, 768
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    # everything important stays in the centre, which VK keeps on phones too
    title_font = font("arialbd.ttf", 104)
    sub_font = font("arial.ttf", 42)
    line_font = font("arialbd.ttf", 40)
    title_w = draw.textlength(BOOK_TITLE, font=title_font)
    left = (width - title_w) / 2 + 40
    wheat(image, left - 95, 250, 540, 32, ACCENT)
    draw.text((left, 230), BOOK_TITLE, font=title_font, fill=TEXT)
    draw.text((left, 365), BOOK_SUBTITLE, font=sub_font, fill=MUTED)
    draw.rectangle((left, 445, left + 160, 453), fill=ACCENT)
    draw.text((left, 480), "Аудиокнига · новая глава каждый день в 18:00", font=line_font, fill=ACCENT)
    path = OUT / "cover.png"
    image.save(path)
    return path


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print(avatar())
    print(cover())
