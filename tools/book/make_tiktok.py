"""Build narrated TikTok versions of Russian or English Shorts."""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import subprocess
from dataclasses import replace
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from make_video import font
from make_short_en import SHORTS as ENGLISH_SHORTS
from shorts_common import ShortPlan, make_plan, write_validation_manifest
from synthesize_audio import ROOT, duration, ffmpeg_tool, strip_accents
from tiktok_common import Caption, make_captions, make_sentence_captions, srt_text


VOICES = {"ru": "ru-RU-SvetlanaNeural", "en": "en-US-JennyNeural"}
SIZE = (1080, 1920)
ACCENT = (244, 190, 76)


def load_item(language: str, item_id: int) -> dict:
    if language == "en":
        items = ENGLISH_SHORTS
    else:
        items = json.loads((ROOT / "shorts" / "theses.json").read_text(encoding="utf-8"))
    try:
        return next(item for item in items if item["id"] == item_id)
    except StopIteration as error:
        raise SystemExit(f"Нет тезиса {item_id} для языка {language}") from error


def output_paths(language: str, item_id: int) -> dict[str, Path]:
    root = ROOT / ("shorts-en" if language == "en" else "shorts") / "out" / "tiktok"
    stem = f"short{'-en' if language == 'en' else ''}-{item_id:03}-tiktok"
    return {
        "root": root,
        "audio": root / f"{stem}.mp3",
        "cues": root / f"{stem}.cues.json",
        "srt": root / f"{stem}.srt",
        "video": root / f"{stem}.mp4",
        "preview": root / f"{stem}-preview.jpg",
        "thumbnail": root / f"{stem}.png",
        "metadata": root / f"{stem}.txt",
        "manifest": root / f"{stem}.validation.json",
    }


def narration(plan: ShortPlan) -> str:
    return " ".join((plan.hook, plan.fact, plan.mechanism, plan.payoff))


async def synthesize_voice(text: str, voice: str, audio: Path, cache: Path, force: bool = False) -> dict:
    if not force and audio.is_file() and cache.is_file():
        saved = json.loads(cache.read_text(encoding="utf-8"))
        if saved.get("text") == text and saved.get("voice") == voice:
            return saved

    temporary = audio.with_name(f".{audio.stem}.tmp{audio.suffix}")
    temporary.unlink(missing_ok=True)
    words: list[dict] = []
    sentences: list[dict] = []
    try:
        with temporary.open("wb") as stream:
            async for chunk in edge_tts.Communicate(text, voice=voice, rate="+8%").stream():
                if chunk["type"] == "audio":
                    stream.write(chunk["data"])
                elif chunk["type"] in {"WordBoundary", "SentenceBoundary"}:
                    cue = {
                        "start": chunk["offset"] / 10_000_000,
                        "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                        "text": strip_accents(chunk["text"]),
                    }
                    (words if chunk["type"] == "WordBoundary" else sentences).append(cue)
        if not temporary.stat().st_size:
            raise RuntimeError("сервис озвучки вернул пустой файл")
        temporary.replace(audio)
    finally:
        temporary.unlink(missing_ok=True)

    saved = {"text": text, "voice": voice, "words": words, "sentences": sentences}
    cache.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return saved


def build_audio(item: dict, language: str, force: bool = False) -> tuple[ShortPlan, list[Caption], dict[str, Path]]:
    plan = make_plan(item, language)
    paths = output_paths(language, item["id"])
    paths["root"].mkdir(parents=True, exist_ok=True)
    script = narration(plan)
    cues = asyncio.run(synthesize_voice(script, VOICES[language], paths["audio"], paths["cues"], force))
    audio_seconds = duration(paths["audio"])
    timed_plan = make_plan({**item, "seconds": audio_seconds}, language)
    captions = (
        make_captions(cues["words"], audio_seconds)
        if cues["words"]
        else make_sentence_captions(cues["sentences"], audio_seconds)
    )
    paths["srt"].write_text(srt_text(captions), encoding="utf-8")
    return replace(timed_plan, seconds=round(audio_seconds, 2)), captions, paths


def source_image(item: dict, language: str) -> Path:
    if language == "ru":
        source = ROOT / "images" / "chapters" / f"{item['chapter']}.png"
    else:
        source = Path(item.get("slide_folder", ROOT / "slides-en" / "00-intro")) / item["image"]
    if not source.is_file():
        raise SystemExit(f"Нет фонового изображения: {source}")
    return source


def wrap_caption(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or draw.textlength(candidate, font=face) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def caption_frame(source: Path, caption: Caption, index: int, total: int, language: str, target: Path) -> None:
    with Image.open(source) as original:
        centering = ((0.32, 0.5), (0.5, 0.42), (0.68, 0.5))[index % 3]
        base = ImageOps.fit(original.convert("RGB"), SIZE, Image.Resampling.LANCZOS, centering=centering)
    base = ImageEnhance.Contrast(base).enhance(1.12).filter(ImageFilter.GaussianBlur(0.35)).convert("RGBA")
    shade = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(SIZE[1]):
        alpha = int(25 + 115 * max(0, (y - 780) / 1140))
        shade_draw.line((0, y, SIZE[0], y), fill=(0, 0, 0, alpha))
    base.alpha_composite(shade)
    draw = ImageDraw.Draw(base)

    face = font("arialbd.ttf", 78)
    lines = wrap_caption(draw, caption.text, face, 840)
    if len(lines) > 2:
        face = font("arialbd.ttf", 66)
        lines = wrap_caption(draw, caption.text, face, 840)
    if len(lines) > 2:
        raise ValueError(f"Субтитр не помещается в две строки: {caption.text}")
    line_height = int(face.size * 1.22)
    box_height = line_height * len(lines) + 92
    box = (72, 1265 - box_height // 2, SIZE[0] - 110, 1265 + box_height // 2)
    draw.rounded_rectangle(box, radius=34, fill=(3, 4, 7, 188), outline=(255, 255, 255, 38), width=2)
    y = 1265 - line_height * (len(lines) - 1) / 2
    for line in lines:
        draw.text((SIZE[0] / 2 - 18, y), line, font=face, fill=(255, 255, 255), anchor="mm",
                  stroke_width=2, stroke_fill=(0, 0, 0, 170))
        y += line_height
    draw.rectangle((72, box[1] - 18, 72 + int((SIZE[0] - 182) * (index + 1) / total), box[1] - 10), fill=ACCENT)
    if index:
        label = "ИСТОРИЯ ЭКОНОМИКИ" if language == "ru" else "ECONOMIC HISTORY"
        draw.text((72, 120), label, font=font("arialbd.ttf", 32), fill=(255, 255, 255, 180))
    save_image(base.convert("RGB"), target, quality=95)


def save_image(image: Image.Image, destination: Path, **options) -> None:
    temporary = destination.with_name(f".{destination.stem}.tmp{destination.suffix}")
    temporary.unlink(missing_ok=True)
    image.save(temporary, **options)
    temporary.replace(destination)


def storyboard(frames: list[Path], target: Path) -> None:
    thumb = (270, 480)
    columns = 4
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGB", (thumb[0] * columns, thumb[1] * rows), (10, 10, 10))
    for index, path in enumerate(frames):
        with Image.open(path) as image:
            sheet.paste(image.convert("RGB").resize(thumb, Image.Resampling.LANCZOS),
                        ((index % columns) * thumb[0], (index // columns) * thumb[1]))
    save_image(sheet, target, quality=90)


def build_visuals(item: dict, language: str, captions: list[Caption], paths: dict[str, Path]) -> list[Path]:
    folder = paths["root"] / f".{paths['video'].stem}-frames"
    folder.mkdir(exist_ok=True)
    source = source_image(item, language)
    frames = [folder / f"frame-{index:02}.png" for index in range(len(captions))]
    for index, (caption, target) in enumerate(zip(captions, frames)):
        caption_frame(source, caption, index, len(captions), language, target)
    with Image.open(frames[0]) as image:
        save_image(image, paths["thumbnail"])
    storyboard(frames, paths["preview"])
    return frames


def pick_music(seed: str) -> Path:
    tracks = sorted((ROOT / "shorts" / "music").glob("*.mp3"))
    if not tracks:
        raise SystemExit("Нет фоновой музыки в book/shorts/music")
    return random.Random(seed).choice(tracks)


def write_metadata(plan: ShortPlan, target: Path) -> None:
    hashtags = "#история #экономика #образование" if plan.language == "ru" else "#history #economics #education"
    target.write_text(f"{plan.title}\n{plan.payoff}\n\n{hashtags}\n", encoding="utf-8")


def render_video(
    frames: list[Path], captions: list[Caption], plan: ShortPlan, paths: dict[str, Path]
) -> None:
    timeline = frames[0].parent / f".{paths['video'].stem}.ffconcat"
    lines = ["ffconcat version 1.0"]
    for frame, caption in zip(frames, captions):
        lines.extend((f"file '{frame.name}'", f"duration {caption.end - caption.start:.3f}"))
    lines.append(f"file '{frames[-1].name}'")
    timeline.write_text("\n".join(lines) + "\n", encoding="utf-8")

    music = pick_music(paths["video"].stem)
    music_start = random.Random(paths["video"].stem).uniform(
        0, max(0.0, duration(music) - plan.seconds - 1)
    )
    temporary = paths["video"].with_name(f".{paths['video'].stem}.tmp.mp4")
    temporary.unlink(missing_ok=True)
    video_filter = (
        "[0:v]fps=30,"
        "zoompan=z='1.035+0.012*sin(on/38)':"
        "x='iw/2-(iw/zoom/2)+7*sin(on/47)':"
        "y='ih/2-(ih/zoom/2)+7*cos(on/53)':d=1:s=1080x1920:fps=30,"
        f"fade=t=in:st=0:d=0.12,fade=t=out:st={plan.seconds - 0.25:.2f}:d=0.25,format=yuv420p[v];"
        f"[1:a]volume=1.0,apad,atrim=0:{plan.seconds:.2f}[voice];"
        f"[2:a]volume=0.10,atrim=0:{plan.seconds:.2f}[music];"
        "[voice][music]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[a]"
    )
    try:
        subprocess.run(
            [
                ffmpeg_tool("ffmpeg"), "-y", "-loglevel", "error",
                "-f", "concat", "-safe", "0", "-i", str(timeline),
                "-i", str(paths["audio"]),
                "-stream_loop", "-1", "-ss", f"{music_start:.2f}", "-i", str(music),
                "-filter_complex", video_filter,
                "-map", "[v]", "-map", "[a]", "-t", f"{plan.seconds:.2f}",
                "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k",
                "-movflags", "+faststart", str(temporary),
            ],
            check=True,
        )
        temporary.replace(paths["video"])
    finally:
        timeline.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)


def animated_scenes(folder: Path) -> list[Path]:
    scenes = sorted(
        path
        for pattern in ("scene-*.mp4", "scene-*.mov", "scene-*.webm")
        for path in folder.glob(pattern)
    )
    if len(scenes) < 4:
        raise SystemExit(f"В {folder} нужно минимум четыре анимированные сцены scene-*.*")
    return scenes[:4]


def subtitle_filter_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def extract_video_previews(video: Path, paths: dict[str, Path], seconds: float) -> None:
    folder = paths["root"] / f".{video.stem}-preview-frames"
    folder.mkdir(exist_ok=True)
    frames = [folder / f"frame-{index:02}.jpg" for index in range(4)]
    try:
        for index, target in enumerate(frames):
            timestamp = min(seconds - 0.2, 0.25 + index * max(0.5, (seconds - 1.0) / 4))
            subprocess.run(
                [
                    ffmpeg_tool("ffmpeg"), "-y", "-loglevel", "error", "-ss", f"{timestamp:.2f}",
                    "-i", str(video), "-frames:v", "1", "-q:v", "2", str(target),
                ],
                check=True,
            )
        with Image.open(frames[0]) as image:
            save_image(image.convert("RGB"), paths["thumbnail"])
        storyboard(frames, paths["preview"])
    finally:
        for frame in frames:
            frame.unlink(missing_ok=True)
        folder.rmdir()


def render_animated_video(
    scene_folder: Path, plan: ShortPlan, paths: dict[str, Path]
) -> None:
    scenes = animated_scenes(scene_folder)
    loop_seconds = plan.scenes[-1].seconds
    body_seconds = plan.seconds - loop_seconds
    scene_seconds = body_seconds / len(scenes)
    inputs = scenes + [scenes[0]]
    input_args = [argument for scene in inputs for argument in ("-i", str(scene))]
    filters: list[str] = []
    for index, scene in enumerate(scenes):
        source_seconds = max(0.1, duration(scene))
        speed = scene_seconds / source_seconds
        filters.append(
            f"[{index}:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,trim=0:{source_seconds:.3f},"
            f"setpts={speed:.8f}*(PTS-STARTPTS),format=yuv420p[v{index}]"
        )
    filters.append(
        f"[{len(scenes)}:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,setsar=1,trim=0:{loop_seconds:.3f},"
        f"setpts=PTS-STARTPTS,format=yuv420p[v{len(scenes)}]"
    )
    labels = "".join(f"[v{index}]" for index in range(len(inputs)))
    subtitles = subtitle_filter_path(paths["srt"])
    filters.append(
        f"{labels}concat=n={len(inputs)}:v=1:a=0,"
        f"subtitles='{subtitles}':force_style='FontName=Arial,FontSize=11,Bold=1,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,BorderStyle=1,Outline=3,"
        f"Shadow=0,Alignment=2,MarginL=18,MarginR=18,MarginV=70',"
        f"fade=t=in:st=0:d=0.10,fade=t=out:st={plan.seconds - 0.18:.2f}:d=0.18[v]"
    )

    music = pick_music(paths["video"].stem)
    music_start = random.Random(paths["video"].stem).uniform(
        0, max(0.0, duration(music) - plan.seconds - 1)
    )
    voice_input = len(inputs)
    music_input = voice_input + 1
    filters.extend(
        (
            f"[{voice_input}:a]volume=1.0,apad,atrim=0:{plan.seconds:.2f}[voice]",
            f"[{music_input}:a]volume=0.10,atrim=0:{plan.seconds:.2f}[music]",
            "[voice][music]amix=inputs=2:duration=first:dropout_transition=0,"
            "alimiter=limit=0.95[a]",
        )
    )
    temporary = paths["video"].with_name(f".{paths['video'].stem}.tmp.mp4")
    temporary.unlink(missing_ok=True)
    try:
        subprocess.run(
            [
                ffmpeg_tool("ffmpeg"), "-y", "-loglevel", "error", *input_args,
                "-i", str(paths["audio"]), "-stream_loop", "-1", "-ss", f"{music_start:.2f}",
                "-i", str(music), "-filter_complex", ";".join(filters),
                "-map", "[v]", "-map", "[a]", "-t", f"{plan.seconds:.2f}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(temporary),
            ],
            check=True,
        )
        temporary.replace(paths["video"])
        extract_video_previews(paths["video"], paths, plan.seconds)
    finally:
        temporary.unlink(missing_ok=True)


def cleanup_frames(frames: list[Path]) -> None:
    folder = frames[0].parent if frames else None
    for frame in frames:
        frame.unlink(missing_ok=True)
    if folder and folder.exists():
        for temporary in folder.glob(".*.tmp.*"):
            temporary.unlink(missing_ok=True)
        folder.rmdir()


def build_video(
    item: dict, language: str, plan: ShortPlan, captions: list[Caption], paths: dict[str, Path],
    scene_folder: Path | None = None,
) -> Path:
    write_metadata(plan, paths["metadata"])
    if scene_folder:
        render_animated_video(scene_folder, plan, paths)
    else:
        frames = build_visuals(item, language, captions, paths)
        try:
            render_video(frames, captions, plan, paths)
        finally:
            cleanup_frames(frames)
    write_validation_manifest(paths["manifest"], paths["video"], paths["metadata"], plan, ffmpeg_tool("ffprobe"))
    return paths["video"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=("ru", "en"), default="ru")
    parser.add_argument("--id", type=int, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--audio-only", action="store_true")
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--force-audio", action="store_true")
    parser.add_argument("--scene-folder", type=Path)
    args = parser.parse_args()
    item = load_item(args.lang, args.id)
    if args.validate_only:
        plan = make_plan(item, args.lang)
        print(f"{narration(plan)}\n{plan.seconds:.2f}s planned")
        return
    plan, captions, paths = build_audio(item, args.lang, args.force_audio)
    print(f"{paths['audio']}\n{paths['srt']}\n{plan.seconds:.2f}s, {len(captions)} captions")
    if args.audio_only:
        return
    if args.preview_only:
        frames = build_visuals(item, args.lang, captions, paths)
        cleanup_frames(frames)
        print(paths["preview"])
        return
    print(build_video(item, args.lang, plan, captions, paths, args.scene_folder))


if __name__ == "__main__":
    main()
