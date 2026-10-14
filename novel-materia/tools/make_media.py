"""Narrate a chapter of «Материальный вопрос» with offline RHVoice and build an MP3, subtitles and a video.

Needs `RHVoice-test` with the Russian voices (Debian/Ubuntu: `apt install rhvoice rhvoice-russian`),
ffmpeg with libass, and Pillow. Everything runs locally, no network service is used.

    python novel-materia/tools/make_media.py --chapter 01-minus-sorok-sem-tysyach
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
import textwrap
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "chapters"
OUTPUT = ROOT / "media"
BOOK_TITLE = "Материальный вопрос"
BOOK_SUBTITLE = "Роман · аудиокнига"
FONTS = Path("/usr/share/fonts/truetype")
SIZE = (1920, 1080)
BACKGROUND = (22, 24, 28)
ACCENT = (205, 160, 92)
TEXT = (238, 232, 220)
MUTED = (150, 146, 138)

SENTENCE_PAUSE = 0.28
PARAGRAPH_PAUSE = 0.7
SECTION_PAUSE = 1.6
CUE_CHARS = 110


def blocks(source: Path) -> list[tuple[str, str]]:
    """The chapter as ("heading" | "paragraph" | "break", text) in reading order."""
    result: list[tuple[str, str]] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            result.append(("paragraph", " ".join(paragraph)))
            paragraph.clear()

    for line in source.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
        elif stripped.startswith("#"):
            flush()
            result.append(("heading", stripped.lstrip("#").strip()))
        elif re.fullmatch(r"-{3,}|\*{3,}", stripped):
            flush()
            result.append(("break", ""))
        else:
            paragraph.append(stripped)
    flush()
    return result


def clean(text: str) -> str:
    text = text.replace("**", "").replace("*", "").replace("`", "")
    return re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)


def sentences(paragraph: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])(?:»)?\s+(?=[—«А-ЯЁA-Z0-9\"(])", clean(paragraph))
    return [part.strip() for part in parts if part.strip()]


def heading_speech(heading: str) -> str:
    """«Глава 1. Минус…» is read as «Глава первая. Минус…»."""
    ordinals = ["", "первая", "вторая", "третья", "четвёртая", "пятая", "шестая", "седьмая", "восьмая", "девятая", "десятая",
                "одиннадцатая", "двенадцатая", "тринадцатая", "четырнадцатая", "пятнадцатая", "шестнадцатая",
                "семнадцатая", "восемнадцатая", "девятнадцатая", "двадцатая"]
    ordinals += ["двадцать " + word for word in ordinals[1:9]]
    match = re.match(r"Глава\s+(\d+)\.\s*(.+)", heading)
    if match and int(match.group(1)) < len(ordinals):
        return f"Глава {ordinals[int(match.group(1))]}. {match.group(2)}"
    return heading


def speak(text: str, voice: str, rate: int, target: Path) -> Path:
    subprocess.run(
        ["RHVoice-test", "-p", voice, "-r", str(rate), "-o", str(target)],
        input=text.encode("utf-8"), check=True, capture_output=True,
    )
    return target


def caption_parts(text: str, start: float, end: float) -> list[tuple[float, float, str]]:
    """Long sentences become several captions, sharing the sentence's time by length."""
    count = -(-len(text) // CUE_CHARS)
    width = -(-len(text) // count) + 12  # balanced parts, no one-word tail
    parts = textwrap.wrap(text, width, break_long_words=False) or [text]
    total = sum(len(part) for part in parts)
    span = end - start
    result = []
    for part in parts:
        finish = start + span * len(part) / total
        result.append((start, finish, part))
        start = finish
    return result


def srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, rest = divmod(millis, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    return f"{hours:02}:{minutes:02}:{rest // 1000:02},{rest % 1000:03}"


def narrate(source: Path, voice: str, rate: int, output: Path) -> tuple[Path, Path, float]:
    """Write <stem>.mp3 and <stem>.srt; return their paths and the duration."""
    items: list[tuple[str, float]] = []  # (spoken text, pause after it)
    for kind, text in blocks(source):
        if kind == "heading":
            items.append((heading_speech(text), PARAGRAPH_PAUSE * 1.5))
        elif kind == "break":
            if items:
                items[-1] = (items[-1][0], SECTION_PAUSE)
        else:
            spoken = sentences(text)
            for index, sentence in enumerate(spoken):
                items.append((sentence, PARAGRAPH_PAUSE if index == len(spoken) - 1 else SENTENCE_PAUSE))

    with tempfile.TemporaryDirectory() as work:
        work_dir = Path(work)
        with ThreadPoolExecutor() as pool:
            pieces = list(pool.map(
                lambda job: speak(job[1][0], voice, rate, work_dir / f"{job[0]:05}.wav"), enumerate(items)
            ))
        with wave.open(str(pieces[0])) as first:
            params = first.getparams()
        joined = work_dir / "chapter.wav"
        cues: list[tuple[float, float, str]] = []
        elapsed = 0.0
        with wave.open(str(joined), "wb") as out:
            out.setparams(params)
            for (text, pause), piece in zip(items, pieces):
                with wave.open(str(piece)) as part:
                    frames = part.readframes(part.getnframes())
                length = len(frames) / (params.sampwidth * params.framerate)
                cues.extend(caption_parts(text, elapsed, elapsed + length))
                out.writeframes(frames)
                silence = int(pause * params.framerate)
                out.writeframes(b"\0" * silence * params.sampwidth)
                elapsed += length + silence / params.framerate
        output.mkdir(parents=True, exist_ok=True)
        audio = output / f"{source.stem}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(joined),
             "-c:a", "libmp3lame", "-b:a", "64k", "-ar", "24000", "-ac", "1", str(audio)],
            check=True,
        )
    subtitles = output / f"{source.stem}.srt"
    subtitles.write_text(
        "\n".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n" for i, (a, b, t) in enumerate(cues, start=1)),
        encoding="utf-8",
    )
    return audio, subtitles, elapsed


def chapter_title(source: Path) -> str:
    for kind, text in blocks(source):
        if kind == "heading":
            return text
    return source.stem


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def thimble(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float) -> None:
    """A simple thimble: a domed body with rows of dimples and a rim."""
    width, height = int(260 * scale), int(330 * scale)
    draw.rounded_rectangle((x, y, x + width, y + height), radius=int(120 * scale), fill=(70, 66, 60))
    draw.rectangle((x, y + height - int(120 * scale), x + width, y + height), fill=(70, 66, 60))
    draw.rectangle((x - int(10 * scale), y + height - int(34 * scale), x + width + int(10 * scale), y + height), fill=ACCENT)
    step = int(34 * scale)
    for row, top in enumerate(range(y + int(50 * scale), y + height - int(60 * scale), step)):
        offset = step // 2 if row % 2 else 0
        for left in range(x + int(28 * scale) + offset, x + width - int(24 * scale), step):
            draw.ellipse((left, top, left + int(12 * scale), top + int(12 * scale)), fill=(40, 38, 35))


def cover(title: str, target: Path) -> None:
    image = Image.new("RGB", SIZE, BACKGROUND)
    draw = ImageDraw.Draw(image)
    left = 140
    draw.rectangle((left, 220, left + 12, 760), fill=ACCENT)
    draw.text((left + 60, 210), BOOK_TITLE, font=font("dejavu/DejaVuSerif-Bold.ttf", 88), fill=TEXT)
    draw.text((left + 60, 336), BOOK_SUBTITLE, font=font("dejavu/DejaVuSans.ttf", 42), fill=MUTED)
    y = 500
    for line in textwrap.wrap(title, width=26):
        draw.text((left + 60, y), line, font=font("dejavu/DejaVuSerif-Bold.ttf", 66), fill=ACCENT)
        y += 86
    thimble(draw, 1500, 400, 0.95)
    image.save(target)


def video(audio: Path, subtitles: Path, image: Path, target: Path) -> None:
    style = ("FontName=DejaVu Sans,FontSize=15,PrimaryColour=&H00DCE8EE,OutlineColour=&H00161412,"
             "BorderStyle=1,Outline=1.2,Shadow=0,MarginV=34,MarginL=60,MarginR=60")
    escaped = str(subtitles).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "4", "-i", str(image), "-i", str(audio),
         "-vf", f"subtitles='{escaped}':force_style='{style}'",
         "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", str(target)],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", required=True, help="file name in chapters/, with or without .md")
    parser.add_argument("--voice", default="aleksandr-hq")
    parser.add_argument("--rate", type=int, default=125, help="RHVoice speech rate in percent")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--no-video", action="store_true")
    args = parser.parse_args()

    source = CHAPTERS / f"{Path(args.chapter).stem}.md"
    if not source.is_file():
        raise SystemExit(f"Глава не найдена: {source}")
    audio, subtitles, seconds = narrate(source, args.voice, args.rate, args.output)
    print(f"{audio} ({seconds / 60:.1f} мин)")
    print(subtitles)
    if args.no_video:
        return
    image = args.output / f"{source.stem}.png"
    cover(chapter_title(source), image)
    target = args.output / f"{source.stem}.mp4"
    video(audio, subtitles, image, target)
    print(target)


if __name__ == "__main__":
    main()
