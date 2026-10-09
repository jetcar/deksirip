"""Turn a narrated chapter into a YouTube-ready MP4 with a cover image and a description file."""

from __future__ import annotations

import argparse
import re
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from synthesize_audio import ROOT, ffmpeg_tool

BOOK_TITLE = "Куда ушёл излишек"
BOOK_SUBTITLE = "История экономики от охотников-собирателей до наших дней"
DONATE_URL = "https://buymeacoffee.com/ownerless"
FONTS = Path("C:/Windows/Fonts")
SIZE = (1920, 1080)
BACKGROUND = (24, 22, 19)
ACCENT = (214, 170, 92)
TEXT = (236, 230, 218)
MUTED = (160, 152, 138)


def chapter_title(source: Path) -> str:
    for line in source.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#\s+(.+)$", line)
        if heading:
            return heading.group(1).strip()
    return source.stem


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def cover(title: str, target: Path) -> None:
    image = Image.new("RGB", SIZE, BACKGROUND)
    draw = ImageDraw.Draw(image)
    left = 140
    draw.rectangle((left, 250, left + 12, 830), fill=ACCENT)
    draw.text((left + 60, 250), BOOK_TITLE, font=font("arialbd.ttf", 110), fill=TEXT)
    draw.text((left + 60, 395), BOOK_SUBTITLE, font=font("arial.ttf", 44), fill=MUTED)
    y = 560
    for line in textwrap.wrap(title, width=38):
        draw.text((left + 60, y), line, font=font("arialbd.ttf", 72), fill=ACCENT)
        y += 92
    draw.text((left + 60, 960), "Аудиокнига", font=font("arial.ttf", 36), fill=MUTED)
    image.save(target)


def description(title: str, chapters: Path) -> str:
    marks = chapters.read_text(encoding="utf-8").strip() if chapters.exists() else ""
    return f"""{BOOK_TITLE}. {title}

Аудиокнига об истории экономики — от охотников-собирателей до мира автоматизации. Главный вопрос книги: куда общество направляло свой излишек — в инструменты, знание и доверие или в дворцы, войны и ренту? Что развивало экономику, что разрушало, а что было пустой тратой.

Содержание:
{marks}

Поддержать проект: {DONATE_URL}

Замысел и тезис — автора канала; текст подготовлен с помощью ИИ, озвучка — синтезированным голосом. Возможны ошибки — пишите о них в комментариях.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--audio-dir", type=Path, default=ROOT / "audio" / "v2")
    parser.add_argument("--output", type=Path, default=ROOT / "video")
    args = parser.parse_args()

    stem = Path(args.chapter).stem
    source = ROOT / f"{stem}.md"
    audio = args.audio_dir / f"{stem}.mp3"
    if not audio.is_file():
        raise SystemExit(f"Нет аудио: {audio}")
    args.output.mkdir(parents=True, exist_ok=True)
    title = chapter_title(source)
    image = args.output / f"{stem}.png"
    video = args.output / f"{stem}.mp4"
    cover(title, image)
    (args.output / f"{stem}.txt").write_text(description(title, args.audio_dir / f"{stem}.chapters.txt"), encoding="utf-8")
    subprocess.run(
        [
            ffmpeg_tool("ffmpeg"), "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", "1", "-i", str(image), "-i", str(audio),
            "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(video),
        ],
        check=True,
    )
    print(video)


if __name__ == "__main__":
    main()
