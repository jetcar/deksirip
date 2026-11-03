from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance


WIDTH = 832
HEIGHT = 1216
OVERLAP = 96


def cover(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def gradient_mask(width: int, height: int, overlap: int) -> Image.Image:
    mask = Image.new("L", (width, height), 255)
    pixels = mask.load()
    for y in range(min(overlap, height)):
        alpha = round(255 * y / max(overlap - 1, 1))
        for x in range(width):
            pixels[x, y] = alpha
    return mask


def compose(paths: list[Path], output: Path) -> None:
    count = len(paths)
    panel_height = (HEIGHT + OVERLAP * (count - 1) + count - 1) // count
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "black")
    y = 0

    for index, path in enumerate(paths):
        with Image.open(path) as source:
            panel = cover(source.convert("RGB"), WIDTH, panel_height)
        panel = ImageEnhance.Color(panel).enhance(0.92)
        if index == 0:
            canvas.paste(panel, (0, 0))
        else:
            canvas.paste(panel, (0, y), gradient_mask(WIDTH, panel_height, OVERLAP))
        y += panel_height - OVERLAP

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=95)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args()
    compose(args.inputs, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
