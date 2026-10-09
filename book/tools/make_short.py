"""Build a vertical YouTube Short: one thesis from the book as text over background music.

Theses live in shorts/theses.json as a list of {"id", "chapter", "title", "text", "used"};
lines of "text" are separate paragraphs, the last one is the punchline shown in the accent colour.
Music: MP3 files downloaded from the YouTube Studio Audio Library into shorts/music/;
an optional <track>.txt next to a file holds the attribution line the license requires.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from make_video import ACCENT, BACKGROUND, BOOK_TITLE, DONATE_URL, MUTED, TEXT, chapter_title, font
from synthesize_audio import ROOT, duration, ffmpeg_tool

SHORTS = ROOT / "shorts"
THESES = SHORTS / "theses.json"
MUSIC = SHORTS / "music"
OUTPUT = SHORTS / "out"
SIZE = (1080, 1920)
MARGIN = 110


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if draw.textlength(candidate, font=face) <= width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def frame(thesis: str, chapter: str, target: Path) -> None:
    image = Image.new("RGB", SIZE, BACKGROUND)
    draw = ImageDraw.Draw(image)
    width = SIZE[0] - 2 * MARGIN
    draw.text((MARGIN, 190), BOOK_TITLE, font=font("arialbd.ttf", 58), fill=ACCENT)
    draw.rectangle((MARGIN, 290, MARGIN + 140, 298), fill=ACCENT)
    paragraphs = [p for p in thesis.split("\n") if p.strip()]
    for size in (78, 70, 62, 56, 50):  # largest size that fits the middle of the screen
        face = font("arialbd.ttf", size)
        blocks = [wrap(draw, p, face, width) for p in paragraphs]
        step = int(size * 1.32)
        gap = size
        height = sum(len(b) for b in blocks) * step + gap * (len(blocks) - 1)
        if height <= 1050:
            break
    y = 380 + (1050 - height) // 2
    for index, block in enumerate(blocks):
        colour = TEXT if index == 0 else ACCENT  # the closing line carries the point
        for line in block:
            draw.text((MARGIN, y), line, font=face, fill=colour)
            y += step
        y += gap
    small = font("arial.ttf", 40)
    for index, line in enumerate(wrap(draw, chapter, small, width)[:2]):
        draw.text((MARGIN, 1560 + index * 52), line, font=small, fill=MUTED)
    draw.text((MARGIN, 1700), "Полная глава — на канале", font=font("arialbd.ttf", 44), fill=ACCENT)
    image.save(target)


def pick_track(seed: str) -> Path:
    tracks = sorted(MUSIC.glob("*.mp3"))
    if not tracks:
        raise SystemExit(f"Нет музыки в {MUSIC} — скачайте треки из фонотеки YouTube Studio")
    return random.Random(seed).choice(tracks)


def chapter_link(chapter: str) -> str:
    record = ROOT / "video" / f"{chapter}.uploaded.json"
    if record.exists():
        return f"https://youtu.be/{json.loads(record.read_text(encoding='utf-8'))['id']}"
    return ""


def build(thesis: dict) -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    stem = f"short-{thesis['id']:03}"
    chapter = thesis["chapter"]
    title = chapter_title(ROOT / f"{chapter}.md")
    image = OUTPUT / f"{stem}.png"
    video = OUTPUT / f"{stem}.mp4"
    frame(thesis["text"], title, image)

    seconds = max(15, min(45, len(thesis["text"]) / 9 + 5))  # time to read the text twice, calmly
    track = pick_track(stem)
    track_length = duration(track)
    start = random.Random(stem).uniform(0, max(0.0, track_length - seconds - 1))
    fade_out = seconds - 2
    subprocess.run(
        [
            ffmpeg_tool("ffmpeg"), "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", "30", "-i", str(image),
            "-ss", f"{start:.1f}", "-i", str(track),
            "-filter_complex",
            f"[0:v]fade=t=in:st=0:d=0.8,fade=t=out:st={seconds - 0.8:.1f}:d=0.8,format=yuv420p[v];"
            f"[1:a]volume=0.8,afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out:.1f}:d=2[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{seconds:.1f}",
            "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart", str(video),
        ],
        check=True,
    )

    attribution_file = track.with_suffix(".txt")
    attribution = attribution_file.read_text(encoding="utf-8").strip() if attribution_file.exists() else ""
    link = chapter_link(chapter)
    lines = [
        f"{thesis.get('title') or thesis['text'].split(chr(10))[-1]} #Shorts"[:100],
        thesis["text"],
        "",
        f"{BOOK_TITLE}. {title}" + (f": {link}" if link else " — полная глава на канале."),
        f"Поддержать проект: {DONATE_URL}",
        "",
        "Текст подготовлен с помощью ИИ по замыслу автора канала.",
    ]
    if attribution:
        lines += ["", f"Музыка: {attribution}"]
    (OUTPUT / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(video)
    return video


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, help="thesis id; default: the first unused one")
    parser.add_argument("--mark-used", action="store_true")
    args = parser.parse_args()
    theses = json.loads(THESES.read_text(encoding="utf-8"))
    pending = [t for t in theses if (t["id"] == args.id if args.id else not t.get("used"))]
    if not pending:
        raise SystemExit("Нет неиспользованных тезисов")
    thesis = pending[0]
    build(thesis)
    if args.mark_used:
        thesis["used"] = True
        THESES.write_text(json.dumps(theses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"short-{thesis['id']:03}")


if __name__ == "__main__":
    main()
