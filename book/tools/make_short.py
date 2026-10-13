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

from make_video import ACCENT, BOOK_TITLE, DONATE_URL, MUTED, TEXT, chapter_title, font
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
        for word in paragraph.split(" "):  # plain spaces only: no-break spaces keep "до н. э." together
            candidate = f"{line} {word}".strip()
            if draw.textlength(candidate, font=face) <= width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


# Each chapter gets its own palette and consecutive Shorts rotate the layout, so the channel does not
# look like one template repeated: (background top, background bottom, text, accent, muted).
THEMES = [
    ((24, 22, 19), (38, 32, 24), TEXT, ACCENT, MUTED),             # the book's own: soot and gold
    ((14, 24, 40), (26, 46, 74), (232, 238, 246), (120, 190, 255), (150, 168, 190)),   # night blue
    ((18, 34, 26), (30, 58, 42), (232, 242, 232), (170, 214, 120), (150, 178, 156)),   # field green
    ((44, 16, 20), (74, 26, 32), (246, 232, 230), (255, 168, 120), (196, 150, 150)),   # burgundy
    ((36, 36, 42), (58, 58, 70), (240, 240, 244), (255, 206, 84), (170, 170, 186)),    # slate
    ((238, 228, 208), (222, 206, 176), (40, 32, 24), (150, 70, 30), (110, 96, 80)),    # parchment
    ((30, 20, 44), (52, 34, 76), (240, 232, 250), (220, 150, 255), (170, 156, 196)),   # dusk violet
]
LAYOUTS = ("left", "center", "card", "quote")


def style(thesis: dict) -> tuple[tuple, str]:
    chapter_number = int(thesis["chapter"][:2]) if thesis["chapter"][:2].isdigit() else 0
    return THEMES[chapter_number % len(THEMES)], LAYOUTS[thesis["id"] % len(LAYOUTS)]


def gradient(top: tuple, bottom: tuple) -> Image.Image:
    column = Image.new("RGB", (1, SIZE[1]))
    for y in range(SIZE[1]):
        k = y / (SIZE[1] - 1)
        column.putpixel((0, y), tuple(int(a + (b - a) * k) for a, b in zip(top, bottom)))
    return column.resize(SIZE)


def layout_text(draw: ImageDraw.ImageDraw, paragraphs: list[str], width: int):
    for size in (78, 70, 62, 56, 50):  # largest size that fits the middle of the screen
        face = font("arialbd.ttf", size)
        blocks = [wrap(draw, p, face, width) for p in paragraphs]
        step = int(size * 1.32)
        height = sum(len(b) for b in blocks) * step + size * (len(blocks) - 1)
        if height <= 1000:
            return face, blocks, step, size, height
    return face, blocks, step, size, height


def frames(thesis: dict, chapter: str, base_path: Path, punch_path: Path) -> None:
    """Two layers: everything but the punchline, and the punchline alone (it appears later in the video)."""
    (top, bottom, text, accent, muted), layout = style(thesis)
    base = gradient(top, bottom).convert("RGBA")
    punch = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw, pdraw = ImageDraw.Draw(base), ImageDraw.Draw(punch)
    centered = layout == "center"
    width = SIZE[0] - 2 * MARGIN - (80 if layout == "card" else 0)

    # a faint chapter number in the background gives each chapter its own mark
    number = thesis["chapter"][:2]
    ghost = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(ghost).text((SIZE[0] - 80, 1880), number, font=font("arialbd.ttf", 620), anchor="rd",
                               fill=accent + (22,))
    base.alpha_composite(ghost)

    def put(d: ImageDraw.ImageDraw, y: int, line: str, face, fill) -> None:
        if centered:
            d.text((SIZE[0] / 2, y), line, font=face, fill=fill, anchor="ma")
        else:
            d.text((MARGIN + (40 if layout == "card" else 0), y), line, font=face, fill=fill)

    header = font("arialbd.ttf", 58)
    put(draw, 190, BOOK_TITLE, header, accent)
    bar_x = SIZE[0] / 2 - 70 if centered else MARGIN
    draw.rectangle((bar_x, 290, bar_x + 140, 298), fill=accent)

    no_break = thesis["text"].replace(" до н. э.", " до н. э.").replace(" н. э.", " н. э.")
    paragraphs = [p for p in no_break.split("\n") if p.strip()]
    face, blocks, step, size, height = layout_text(draw, paragraphs, width)
    y = 400 + (1000 - height) // 2 + (50 if layout == "quote" else 0)
    if layout == "card":
        panel = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        tint = (255, 255, 255, 18) if sum(top) < 300 else (0, 0, 0, 16)
        ImageDraw.Draw(panel).rounded_rectangle((MARGIN - 20, y - 70, SIZE[0] - MARGIN + 20, y + height + 70),
                                                radius=36, fill=tint)
        base.alpha_composite(panel)
    if layout == "quote":
        draw.text((MARGIN - 20, y - 215), "«", font=font("arialbd.ttf", 200), fill=accent)
    for index, block in enumerate(blocks):
        target, colour = (draw, text) if index < len(blocks) - 1 or len(blocks) == 1 else (pdraw, accent)
        for line in block:
            put(target, y, line, face, colour)
            y += step
        y += size

    small = font("arial.ttf", 40)
    for index, line in enumerate(wrap(draw, chapter, small, width)[:2]):
        put(draw, 1560 + index * 52, line, small, muted)
    put(draw, 1700, "Полная глава — на канале", font("arialbd.ttf", 44), accent)
    base.convert("RGB").save(base_path)
    punch.save(punch_path)


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
    punch = OUTPUT / f".{stem}.punch.png"
    video = OUTPUT / f"{stem}.mp4"
    frames(thesis, title, image, punch)

    seconds = max(15, min(45, len(thesis["text"]) / 9 + 5))  # time to read the text twice, calmly
    reveal = max(3.0, seconds * 0.4)  # the punchline appears once the first paragraph has been read
    frame_count = int(seconds * 30)
    track = pick_track(stem)
    track_length = duration(track)
    start = random.Random(stem).uniform(0, max(0.0, track_length - seconds - 1))
    fade_out = seconds - 2
    subprocess.run(
        [
            ffmpeg_tool("ffmpeg"), "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", "30", "-i", str(image),
            "-loop", "1", "-framerate", "30", "-i", str(punch),
            "-ss", f"{start:.1f}", "-i", str(track),
            "-filter_complex",
            f"[1:v]format=rgba,fade=t=in:st={reveal:.1f}:d=0.8:alpha=1[p];"
            "[0:v][p]overlay=0:0,"
            # a slow push-in (Ken Burns); upscaling first keeps the zoom from jittering
            f"scale=2160:3840,zoompan=z='1+0.05*on/{frame_count}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
            f":d=1:s=1080x1920:fps=30,"
            f"fade=t=in:st=0:d=0.8,fade=t=out:st={seconds - 0.8:.1f}:d=0.8,format=yuv420p[v];"
            f"[2:a]volume=0.8,afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out:.1f}:d=2[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{seconds:.1f}",
            "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart", str(video),
        ],
        check=True,
    )
    punch.unlink(missing_ok=True)

    attribution_file = track.with_suffix(".txt")
    attribution = attribution_file.read_text(encoding="utf-8").strip() if attribution_file.exists() else ""
    link = chapter_link(chapter)
    lines = [
        f"{thesis.get('title') or thesis['text'].split(chr(10))[-1]} #Shorts"[:100],
        thesis["text"],
        "",
        f"{BOOK_TITLE}. {title}" + (f": {link}" if link else " — полная глава на канале."),
        "Telegram: https://t.me/kuda_ushel_izlishek",
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
