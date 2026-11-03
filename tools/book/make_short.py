"""Build a Russian vertical Short using the hook → fact → mechanism → payoff scheme."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import replace
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from make_video import ACCENT, BOOK_TITLE, DONATE_URL, MUTED, TEXT, chapter_title, font
from shorts_common import Scene, ShortPlan, make_plan, render_timeline, validate_plan, write_validation_manifest
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
        for word in paragraph.split(" "):
            candidate = f"{line} {word}".strip()
            if draw.textlength(candidate, font=face) <= width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


THEMES = [
    ((24, 22, 19), (38, 32, 24), TEXT, ACCENT, MUTED),
    ((14, 24, 40), (26, 46, 74), (232, 238, 246), (120, 190, 255), (150, 168, 190)),
    ((18, 34, 26), (30, 58, 42), (232, 242, 232), (170, 214, 120), (150, 178, 156)),
    ((44, 16, 20), (74, 26, 32), (246, 232, 230), (255, 168, 120), (196, 150, 150)),
    ((36, 36, 42), (58, 58, 70), (240, 240, 244), (255, 206, 84), (170, 170, 186)),
    ((238, 228, 208), (222, 206, 176), (40, 32, 24), (150, 70, 30), (110, 96, 80)),
    ((30, 20, 44), (52, 34, 76), (240, 232, 250), (220, 150, 255), (170, 156, 196)),
]
BEAT_LABELS = {"hook": "СРАЗУ К СУТИ", "fact": "ФАКТ", "mechanism": "ПОЧЕМУ", "payoff": "ВЫВОД", "loop": ""}


def style(thesis: dict) -> tuple:
    chapter_number = int(thesis["chapter"][:2]) if thesis["chapter"][:2].isdigit() else 0
    return THEMES[chapter_number % len(THEMES)]


def gradient(top: tuple, bottom: tuple) -> Image.Image:
    column = Image.new("RGB", (1, SIZE[1]))
    for y in range(SIZE[1]):
        ratio = y / (SIZE[1] - 1)
        column.putpixel((0, y), tuple(int(a + (b - a) * ratio) for a, b in zip(top, bottom)))
    return column.resize(SIZE).convert("RGBA")


def fit_scene_text(draw: ImageDraw.ImageDraw, text: str, width: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in (112, 100, 90, 80, 72, 64, 56):
        face = font("arialbd.ttf", size)
        lines = wrap(draw, text, face, width)
        if len(lines) <= 2:
            return face, lines
    raise ValueError(f"Текст не помещается в две строки: {text!r}")


def illustrated_scene_frame(thesis: dict, scene: Scene, index: int, path: Path) -> None:
    frames = thesis["art_frames"]
    key = "hook" if scene.beat == "loop" else scene.beat
    source = ROOT / frames[key]
    if not source.is_file():
        raise FileNotFoundError(f"Нет утверждённого кадра: {source}")
    with Image.open(source) as artwork:
        base = artwork.convert("RGB").resize(SIZE, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(base)
    face, lines = fit_scene_text(draw, scene.text, SIZE[0] - 2 * MARGIN)
    step = int(face.size * 1.23)
    y = 215
    colour = ACCENT if scene.beat == "payoff" else TEXT
    for line in lines:
        draw.text(
            (SIZE[0] // 2, y), line, font=face, fill=colour, anchor="mt",
            stroke_width=5, stroke_fill=(9, 29, 28),
        )
        y += step
    save_image(base, path, quality=95)


def scene_frame(thesis: dict, plan: ShortPlan, scene: Scene, index: int, chapter: str, path: Path) -> None:
    if thesis.get("art_frames"):
        display_scene = scene
        if scene.beat == "loop":
            display_scene = Scene("loop", thesis.get("loop_text") or plan.scenes[0].text, scene.seconds)
        illustrated_scene_frame(thesis, display_scene, index, path)
        return
    top, bottom, text, accent, muted = style(thesis)
    if index % 2:
        top, bottom = bottom, top
    base = gradient(top, bottom)
    draw = ImageDraw.Draw(base)

    shape_x = -180 if index % 2 else 650
    shape_y = 180 + (index % 3) * 250
    draw.ellipse((shape_x, shape_y, shape_x + 620, shape_y + 620), fill=accent + (28,))
    draw.rounded_rectangle((72, 360, SIZE[0] - 72, 1380), radius=56, fill=(0, 0, 0, 52))

    label = BEAT_LABELS[scene.beat]
    if label:
        draw.text((MARGIN, 235), label, font=font("arialbd.ttf", 42), fill=accent)
        draw.rectangle((MARGIN, 305, MARGIN + 150 + index * 22, 313), fill=accent)

    face, lines = fit_scene_text(draw, scene.text, SIZE[0] - 2 * MARGIN - 40)
    step = int(face.size * 1.25)
    y = 780 - (len(lines) - 1) * step // 2
    colour = accent if scene.beat in {"payoff", "loop"} else text
    for line in lines:
        draw.text((SIZE[0] / 2, y), line, font=face, fill=colour, anchor="mm", stroke_width=2,
                  stroke_fill=(0, 0, 0, 90))
        y += step

    if index:
        draw.text((MARGIN, 1540), BOOK_TITLE, font=font("arialbd.ttf", 36), fill=muted)
        draw.text((MARGIN, 1600), chapter[:52], font=font("arial.ttf", 34), fill=muted)
    if scene.beat == "payoff":
        draw.text((MARGIN, 1700), "Связанная глава — на канале", font=font("arialbd.ttf", 40), fill=accent)

    dot_y = 1800
    for dot in range(len(plan.scenes)):
        colour_dot = accent if dot == index else muted
        radius = 9 if dot == index else 6
        x = MARGIN + dot * 34
        draw.ellipse((x - radius, dot_y - radius, x + radius, dot_y + radius), fill=colour_dot)
    save_image(base.convert("RGB"), path, quality=95)


def storyboard(scene_paths: list[Path], target: Path) -> None:
    thumb_size = (270, 480)
    columns = 4
    rows = (len(scene_paths) + columns - 1) // columns
    sheet = Image.new("RGB", (thumb_size[0] * columns, thumb_size[1] * rows), (12, 12, 12))
    for index, path in enumerate(scene_paths):
        thumb = Image.open(path).convert("RGB").resize(thumb_size, Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((index % columns) * thumb_size[0], (index // columns) * thumb_size[1]))
    save_image(sheet, target, quality=90)


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


def metadata(plan: ShortPlan, chapter: str, track: Path) -> str:
    title = chapter_title(ROOT / f"{chapter}.md")
    link = chapter_link(chapter)
    lines = [
        f"{plan.title} #Shorts"[:100],
        plan.body,
        "",
        f"{BOOK_TITLE}. {title}" + (f": {link}" if link else " — полная глава на канале."),
        "Telegram: https://t.me/kuda_ushel_izlishek",
        f"Поддержать проект: {DONATE_URL}",
        "",
        "Текст подготовлен с помощью ИИ по замыслу автора канала.",
    ]
    attribution_file = track.with_suffix(".txt")
    if attribution_file.exists():
        lines.extend(("", f"Музыка: {attribution_file.read_text(encoding='utf-8').strip()}"))
    return "\n".join(lines) + "\n"


def cleanup(scene_paths: list[Path]) -> None:
    folder = scene_paths[0].parent if scene_paths else None
    for path in scene_paths:
        path.unlink(missing_ok=True)
    if folder and folder.exists():
        folder.rmdir()


def save_image(image: Image.Image, destination: Path, **save_options) -> None:
    temporary = destination.with_name(f".{destination.stem}.tmp{destination.suffix}")
    temporary.unlink(missing_ok=True)
    image.save(temporary, **save_options)
    temporary.replace(destination)


def save_thumbnail(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        save_image(image, destination)


def plan_for_thesis(thesis: dict) -> ShortPlan:
    plan = make_plan(thesis, "ru")
    timings = thesis.get("scene_seconds")
    scene_texts = thesis.get("scene_texts")
    if timings is not None:
        if scene_texts is not None:
            if len(scene_texts) != len(timings):
                raise ValueError("Число экранных фраз не совпадает с числом длительностей")
            beats = []
            cursor = 0
            for beat in ("hook", "fact", "mechanism", "payoff", "loop"):
                target = plan.hook if beat == "loop" else getattr(plan, beat)
                assembled = ""
                while assembled != target and cursor < len(scene_texts):
                    assembled = f"{assembled} {scene_texts[cursor]}".strip()
                    if not target.startswith(assembled):
                        raise ValueError(f"Экранный текст не совпадает с блоком {beat}")
                    beats.append(beat)
                    cursor += 1
                if assembled != target:
                    raise ValueError(f"Неполный экранный текст блока {beat}")
            if cursor != len(scene_texts):
                raise ValueError("Лишние экранные фразы")
            scenes = tuple(Scene(beat, text, float(seconds)) for beat, text, seconds in zip(beats, scene_texts, timings))
        else:
            if len(timings) != len(plan.scenes):
                raise ValueError("Число длительностей не совпадает с числом сцен")
            scenes = tuple(Scene(scene.beat, scene.text, float(seconds)) for scene, seconds in zip(plan.scenes, timings))
        plan = replace(plan, scenes=scenes, seconds=round(sum(scene.seconds for scene in scenes), 2))
        validate_plan(plan)
    return plan


def build(thesis: dict, preview_only: bool = False) -> Path:
    plan = plan_for_thesis(thesis)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    stem = f"short-{thesis['id']:03}"
    chapter = thesis["chapter"]
    chapter_name = chapter_title(ROOT / f"{chapter}.md")
    scene_dir = OUTPUT / f".{stem}-scenes"
    scene_dir.mkdir(exist_ok=True)
    scene_paths = [scene_dir / f"scene-{index:02}.png" for index in range(len(plan.scenes))]
    for index, (scene, path) in enumerate(zip(plan.scenes, scene_paths)):
        scene_frame(thesis, plan, scene, index, chapter_name, path)

    thumbnail = OUTPUT / f"{stem}.png"
    save_thumbnail(scene_paths[0], thumbnail)
    preview = OUTPUT / f"{stem}-preview.jpg"
    storyboard(scene_paths, preview)
    track = pick_track(stem)
    meta = OUTPUT / f"{stem}.txt"
    meta.write_text(metadata(plan, chapter, track), encoding="utf-8")
    if preview_only:
        cleanup(scene_paths)
        print(preview)
        return preview

    video = OUTPUT / f"{stem}.mp4"
    track_length = duration(track)
    start = random.Random(stem).uniform(0, max(0.0, track_length - plan.seconds - 1))
    voice = ROOT / thesis["voice_audio"] if thesis.get("voice_audio") else None
    if voice and not voice.is_file():
        raise FileNotFoundError(f"Нет озвучки: {voice}")
    try:
        render_timeline(
            scene_paths, plan, track, video, ffmpeg_tool("ffmpeg"),
            music_start=start, video_fades=not bool(thesis.get("art_frames")), voice=voice,
        )
        write_validation_manifest(
            OUTPUT / f"{stem}.validation.json", video, meta, plan, ffmpeg_tool("ffprobe")
        )
    finally:
        cleanup(scene_paths)
    print(video)
    return video


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", type=int, help="thesis id; default: the first unused one")
    parser.add_argument("--mark-used", action="store_true")
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.mark_used and (args.preview_only or args.validate_only):
        parser.error("--mark-used разрешён только после полного рендера и проверки")
    theses = json.loads(THESES.read_text(encoding="utf-8"))
    pending = [thesis for thesis in theses if thesis["id"] == args.id] if args.id else [
        thesis for thesis in theses if not thesis.get("used")
    ]
    if not pending:
        raise SystemExit("Нет подходящих тезисов")
    thesis = pending[0]
    plan = plan_for_thesis(thesis)
    if args.validate_only:
        print(f"short-{thesis['id']:03}: {plan.seconds:.2f} с, {len(plan.scenes)} сцен")
        return
    build(thesis, preview_only=args.preview_only)
    if args.mark_used:
        thesis["used"] = True
        THESES.write_text(json.dumps(theses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"short-{thesis['id']:03}")


if __name__ == "__main__":
    main()
