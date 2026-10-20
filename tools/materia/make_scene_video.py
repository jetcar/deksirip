"""Build a chapter video from one static image per Markdown scene."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "novel-materia"
SCENE_SPLIT = re.compile(r"^\s*(?:---|\*\*\*)\s*$", re.MULTILINE)
SRT_CUE = re.compile(
    r"(?ms)^\d+[ \t]*\n(\d\d:\d\d:\d\d,\d{3}) --> \d\d:\d\d:\d\d,\d{3}[ \t]*\n(.+?)(?=\n\n|\Z)"
)


def seconds(timestamp: str) -> float:
    hours, minutes, rest = timestamp.split(":")
    value, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(value) + int(millis) / 1000


def normalize(text: str) -> str:
    text = text.replace("‑", "-").replace("ё", "е").replace("Ё", "Е")
    return re.sub(r"[^0-9a-zа-я]+", " ", text.lower()).strip()


def cue_start(lead: str, cues: list[tuple[float, str]], after: float) -> float | None:
    return next(
        (
            stamp
            for stamp, cue in cues
            if stamp > after
            and (lead.startswith(cue) or cue.startswith(lead[:40]))
        ),
        None,
    )


def scene_lead(scene: str) -> str:
    lines = [line.strip() for line in scene.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("#"):
            continue
        cleaned = re.sub(r"[*_`]", "", line)
        if cleaned:
            return cleaned
    raise ValueError("Пустая сцена в рукописи")


def duration(audio: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def timeline(chapter: Path, subtitles: Path, audio: Path, images: Path) -> list[dict[str, object]]:
    scenes = [part.strip() for part in SCENE_SPLIT.split(chapter.read_text(encoding="utf-8")) if part.strip()]
    cues = [(seconds(stamp), normalize(text)) for stamp, text in SRT_CUE.findall(subtitles.read_text(encoding="utf-8"))]
    pictures = sorted(images.glob("*.png"))
    if len(pictures) != len(scenes):
        raise ValueError(f"Сцен: {len(scenes)}, изображений: {len(pictures)}")

    starts = [0.0]
    for scene in scenes[1:]:
        lead = normalize(scene_lead(scene))
        match = cue_start(lead, cues, starts[-1])
        if match is None:
            raise ValueError(f"Не найден таймкод для: {scene_lead(scene)[:80]}")
        starts.append(match)

    ends = starts[1:] + [duration(audio)]
    if any(end <= start for start, end in zip(starts, ends)):
        raise ValueError("Таймкоды сцен должны строго возрастать")
    return [
        {
            "scene": index,
            "image": picture.name,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(end - start, 3),
            "lead": scene_lead(scene),
        }
        for index, (picture, scene, start, end) in enumerate(zip(pictures, scenes, starts, ends), start=1)
    ]


def build_video(folder: Path, items: list[dict[str, object]], audio: Path, subtitles: Path, target: Path) -> None:
    style = (
        "FontName=DejaVu Sans,FontSize=15,PrimaryColour=&H00DCE8EE,OutlineColour=&H00161412,"
        "BorderStyle=1,Outline=1.2,Shadow=0,MarginV=34,MarginL=60,MarginR=60"
    )
    escaped_subtitles = str(subtitles).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    with tempfile.TemporaryDirectory() as work:
        concat = Path(work) / "scenes.ffconcat"
        lines = ["ffconcat version 1.0"]
        for item in items:
            image = (folder / "images" / str(item["image"])).resolve().as_posix().replace("'", "'\\''")
            lines.extend((f"file '{image}'", f"duration {item['duration']}"))
        last = (folder / "images" / str(items[-1]["image"])).resolve().as_posix().replace("'", "'\\''")
        lines.append(f"file '{last}'")
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat),
                "-i", str(audio), "-vf",
                f"scale=1920:1080,setsar=1,subtitles='{escaped_subtitles}':force_style='{style}'",
                "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-crf", "26", "-r", "4",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-t", str(items[-1]["end"]),
                "-shortest", "-movflags", "+faststart",
                str(target),
            ],
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", required=True, help="chapter stem from chapters/")
    parser.add_argument("--timeline-only", action="store_true")
    args = parser.parse_args()

    stem = Path(args.chapter).stem
    folder = ROOT / "scene-video" / stem
    items = timeline(
        ROOT / "chapters" / f"{stem}.md",
        ROOT / "media" / f"{stem}.srt",
        ROOT / "media" / f"{stem}.mp3",
        folder / "images",
    )
    target = folder / "timeline.json"
    target.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)
    if args.timeline_only:
        return
    video = folder / f"{stem}-scenes.mp4"
    build_video(folder, items, ROOT / "media" / f"{stem}.mp3", ROOT / "media" / f"{stem}.srt", video)
    print(video)


if __name__ == "__main__":
    main()
