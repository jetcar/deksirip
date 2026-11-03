"""Shared script planning and validation for Russian and English Shorts."""

from __future__ import annotations

import re
import hashlib
import json
import subprocess
from math import ceil
from dataclasses import dataclass
from pathlib import Path


STANDARD_MIN_SECONDS = 15.0
STANDARD_MAX_SECONDS = 24.0
EXTENDED_MAX_SECONDS = 35.0
MIN_SCENE_SECONDS = 1.5
MAX_SCENE_SECONDS = 3.0
LOOP_SECONDS = 0.75
BEATS = ("hook", "fact", "mechanism", "payoff")


@dataclass(frozen=True)
class Scene:
    beat: str
    text: str
    seconds: float


@dataclass(frozen=True)
class ShortPlan:
    language: str
    title: str
    hook: str
    fact: str
    mechanism: str
    payoff: str
    scenes: tuple[Scene, ...]
    seconds: float
    long_form_reason: str = ""

    @property
    def body(self) -> str:
        return "\n".join((self.fact, self.mechanism, self.payoff))


def _units(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?…])\s+|\n+", text) if part.strip()]


def _split_near_middle(text: str) -> tuple[str, str]:
    words = text.split()
    if len(words) < 4:
        raise ValueError("Тезис слишком короткий: нужны факт, механизм и вывод")
    middle = len(words) // 2
    return " ".join(words[:middle]), " ".join(words[middle:])


def _legacy_beats(text: str) -> tuple[str, str, str]:
    units = _units(text)
    while len(units) < 3:
        index = max(range(len(units)), key=lambda i: len(units[i].split()))
        left, right = _split_near_middle(units[index])
        units[index:index + 1] = [left, right]
    return units[0], " ".join(units[1:-1]), units[-1]


def _chunks(text: str, max_words: int = 9, max_chars: int = 56) -> list[str]:
    words = text.split()
    if not words:
        return []
    count = max(1, ceil(len(words) / max_words), ceil(len(text) / max_chars))
    while count <= len(words):
        size, extra = divmod(len(words), count)
        groups: list[list[str]] = []
        start = 0
        for index in range(count):
            end = start + size + (1 if index < extra else 0)
            groups.append(words[start:end])
            start = end
        for index in range(1, len(groups)):
            if groups[index][0].lower().strip("—–-") in {"and", "but", "or", "а", "но", "и", "или"} and len(groups[index - 1]) > 2:
                groups[index].insert(0, groups[index - 1].pop())
        chunks = [" ".join(group) for group in groups]
        if all(len(chunk.split()) <= max_words and len(chunk) <= max_chars for chunk in chunks):
            return chunks
        count += 1
    return words


def _fit_durations(scenes: list[Scene], target: float) -> list[Scene]:
    current = sum(scene.seconds for scene in scenes) + LOOP_SECONDS
    delta = target - current
    step = 0.05 if delta >= 0 else -0.05
    guard = 0
    while abs(delta) >= 0.025 and guard < 10000:
        changed = False
        for index, scene in enumerate(scenes):
            candidate = scene.seconds + step
            if MIN_SCENE_SECONDS <= candidate <= MAX_SCENE_SECONDS:
                scenes[index] = Scene(scene.beat, scene.text, round(candidate, 2))
                delta -= step
                changed = True
                if abs(delta) < 0.025:
                    break
        if not changed:
            break
        guard += 1
    remainder = round(target - sum(scene.seconds for scene in scenes) - LOOP_SECONDS, 2)
    for index, scene in enumerate(scenes):
        if abs(remainder) < 0.005:
            break
        limit = MAX_SCENE_SECONDS if remainder > 0 else MIN_SCENE_SECONDS
        capacity = abs(limit - scene.seconds)
        change = min(abs(remainder), capacity)
        if change:
            signed = change if remainder > 0 else -change
            scenes[index] = Scene(scene.beat, scene.text, round(scene.seconds + signed, 2))
            remainder = round(remainder - signed, 2)
    return scenes


def _ensure_scene_count(scenes: list[Scene], minimum: int) -> list[Scene]:
    while len(scenes) < minimum:
        candidates = [(len(scene.text.split()), index) for index, scene in enumerate(scenes)]
        word_count, index = max(candidates)
        if word_count < 2:
            raise ValueError("Недостаточно текста для требуемой длительности")
        scene = scenes[index]
        left, right = _split_near_middle(scene.text) if word_count >= 4 else (
            scene.text.split()[0], " ".join(scene.text.split()[1:])
        )
        half = max(MIN_SCENE_SECONDS, scene.seconds / 2)
        scenes[index:index + 1] = [
            Scene(scene.beat, left, round(half, 2)),
            Scene(scene.beat, right, round(half, 2)),
        ]
    return scenes


def make_plan(item: dict, language: str) -> ShortPlan:
    if language not in {"ru", "en"}:
        raise ValueError(f"Неподдерживаемый язык: {language}")
    title = str(item.get("title", "")).strip()
    hook = str(item.get("hook") or title).strip()
    explicit = [str(item.get(beat, "")).strip() for beat in BEATS[1:]]
    if any(explicit):
        if not all(explicit):
            raise ValueError("Для новой схемы нужны все поля: fact, mechanism, payoff")
        fact, mechanism, payoff = explicit
    else:
        fact, mechanism, payoff = _legacy_beats(str(item.get("text", "")).strip())

    scenes: list[Scene] = []
    for beat, text in zip(BEATS, (hook, fact, mechanism, payoff)):
        for chunk in _chunks(text):
            words = len(chunk.split())
            seconds = max(MIN_SCENE_SECONDS, min(MAX_SCENE_SECONDS, words / 2.8 + 0.55))
            scenes.append(Scene(beat, chunk, round(seconds, 2)))

    requested = item.get("seconds")
    natural = sum(scene.seconds for scene in scenes) + LOOP_SECONDS
    target = float(requested) if requested is not None else max(STANDARD_MIN_SECONDS, min(STANDARD_MAX_SECONDS, natural))
    scenes = _ensure_scene_count(scenes, max(5, ceil((target - LOOP_SECONDS) / MAX_SCENE_SECONDS)))
    scenes = _fit_durations(scenes, target)
    scenes.append(Scene("loop", hook, LOOP_SECONDS))
    seconds = round(sum(scene.seconds for scene in scenes), 2)
    plan = ShortPlan(
        language=language,
        title=title,
        hook=hook,
        fact=fact,
        mechanism=mechanism,
        payoff=payoff,
        scenes=tuple(scenes),
        seconds=seconds,
        long_form_reason=str(item.get("long_form_reason", "")).strip(),
    )
    validate_plan(plan)
    return plan


def validate_plan(plan: ShortPlan) -> None:
    errors: list[str] = []
    if not plan.title or len(plan.title) > 100:
        errors.append("заголовок должен содержать 1–100 символов")
    for beat in BEATS:
        if not getattr(plan, beat).strip():
            errors.append(f"пустой блок {beat}")
    if plan.seconds < STANDARD_MIN_SECONDS:
        errors.append(f"длительность меньше {STANDARD_MIN_SECONDS:g} секунд")
    if plan.seconds > STANDARD_MAX_SECONDS and not plan.long_form_reason:
        errors.append("длительность больше 24 секунд без long_form_reason")
    if plan.seconds > EXTENDED_MAX_SECONDS:
        errors.append(f"длительность больше {EXTENDED_MAX_SECONDS:g} секунд")
    if len(plan.scenes) < 5:
        errors.append("нужно минимум пять визуальных сцен, включая петлю")
    if plan.scenes[-1].beat != "loop" or not 0.5 <= plan.scenes[-1].seconds <= 1.0:
        errors.append("последняя сцена должна быть петлёй длиной 0,5–1 секунда")
    for scene in plan.scenes[:-1]:
        if not MIN_SCENE_SECONDS <= scene.seconds <= MAX_SCENE_SECONDS:
            errors.append(f"сцена {scene.beat} длится {scene.seconds:g} секунды")
        if len(scene.text) > 82 or len(scene.text.split()) > 12:
            errors.append(f"слишком длинный экранный текст: {scene.text!r}")
    body = " ".join((plan.title, plan.hook, plan.body))
    letters = [char for char in body if char.isalpha()]
    cyrillic = sum("а" <= char.lower() <= "я" or char.lower() == "ё" for char in letters)
    if plan.language == "ru" and (not letters or cyrillic / len(letters) < 0.6):
        errors.append("русский сценарий должен преимущественно состоять из кириллицы")
    if plan.language == "en" and cyrillic:
        errors.append("английский сценарий содержит кириллицу")
    if errors:
        raise ValueError("; ".join(errors))


def render_timeline(
    scene_paths: list[Path],
    plan: ShortPlan,
    music: Path,
    output: Path,
    ffmpeg: str,
    *,
    music_start: float = 0.0,
    music_volume: float = 0.55,
    video_fades: bool = True,
    voice: Path | None = None,
) -> None:
    if len(scene_paths) != len(plan.scenes):
        raise ValueError("Число кадров не совпадает с числом сцен")
    timeline = scene_paths[0].parent / f".{output.stem}.ffconcat"
    temporary = output.with_name(f".{output.stem}.tmp{output.suffix}")
    temporary.unlink(missing_ok=True)
    lines = ["ffconcat version 1.0"]
    for path, scene in zip(scene_paths, plan.scenes):
        lines.extend((f"file '{path.name}'", f"duration {scene.seconds:.2f}"))
    lines.append(f"file '{scene_paths[-1].name}'")
    timeline.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        fades = (
            f"fade=t=in:st=0:d=0.15,fade=t=out:st={plan.seconds - 0.3:.2f}:d=0.3,"
            if video_fades else ""
        )
        inputs = (
            ["-i", str(voice), "-stream_loop", "-1", "-ss", f"{music_start:.2f}", "-i", str(music)]
            if voice else ["-stream_loop", "-1", "-ss", f"{music_start:.2f}", "-i", str(music)]
        )
        audio_filter = (
            f"[1:a]volume=1.0,apad,atrim=0:{plan.seconds:.2f}[voice];"
            f"[2:a]volume=0.10,atrim=0:{plan.seconds:.2f}[music];"
            "[voice][music]amix=inputs=2:duration=first:dropout_transition=0,"
            "alimiter=limit=0.95[a]"
            if voice else
            f"[1:a]volume={music_volume},atrim=0:{plan.seconds:.2f},"
            f"afade=t=in:st=0:d=0.4,afade=t=out:st={plan.seconds - 1.0:.2f}:d=1[a]"
        )
        subprocess.run(
            [
                ffmpeg, "-y", "-loglevel", "error",
                "-f", "concat", "-safe", "0", "-i", str(timeline),
                *inputs,
                "-filter_complex",
                f"[0:v]fps=30,scale=1080:1920,"
                f"{fades}"
                "format=yuv420p[v];"
                f"{audio_filter}",
                "-map", "[v]", "-map", "[a]", "-t", f"{plan.seconds:.2f}",
                "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k",
                "-movflags", "+faststart", str(temporary),
            ],
            check=True,
        )
        temporary.replace(output)
    finally:
        timeline.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_video(video: Path, plan: ShortPlan, ffprobe: str) -> dict:
    result = subprocess.run(
        [
            ffprobe, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
            "-of", "json", str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    probe = json.loads(result.stdout)
    streams = probe.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    if not video_stream or (video_stream.get("width"), video_stream.get("height")) != (1080, 1920):
        raise ValueError("готовый ролик должен иметь размер 1080×1920")
    if not any(stream.get("codec_type") == "audio" for stream in streams):
        raise ValueError("в готовом ролике нет аудиодорожки")
    actual = float(probe["format"]["duration"])
    if abs(actual - plan.seconds) > 0.35:
        raise ValueError(f"длительность MP4 {actual:.2f} не совпадает с планом {plan.seconds:.2f}")
    return {"duration": round(actual, 3), "width": 1080, "height": 1920}


def validate_metadata(metadata: Path, plan: ShortPlan) -> None:
    content = metadata.read_text(encoding="utf-8").strip()
    title, separator, description = content.partition("\n")
    if not separator or not title.strip() or not description.strip():
        raise ValueError("метаданные должны содержать заголовок и уникальное описание")
    if len(title.strip()) > 100:
        raise ValueError("заголовок метаданных длиннее 100 символов")
    letters = [char for char in content if char.isalpha()]
    cyrillic = sum("а" <= char.lower() <= "я" or char.lower() == "ё" for char in letters)
    if plan.language == "ru" and (not letters or cyrillic / len(letters) < 0.45):
        raise ValueError("метаданные русского ролика не прошли проверку языка")
    if plan.language == "en" and cyrillic:
        raise ValueError("метаданные английского ролика содержат кириллицу")


def write_validation_manifest(
    manifest: Path,
    video: Path,
    metadata: Path,
    plan: ShortPlan,
    ffprobe: str,
) -> None:
    validate_plan(plan)
    validate_metadata(metadata, plan)
    media = validate_video(video, plan, ffprobe)
    data = {
        "schema_version": 1,
        "passed": True,
        "language": plan.language,
        "seconds": plan.seconds,
        "scene_count": len(plan.scenes),
        "max_scene_seconds": max(scene.seconds for scene in plan.scenes[:-1]),
        "video_sha256": _sha256(video),
        "media": media,
    }
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_current_validation(video: Path, manifest: Path) -> dict:
    if not manifest.is_file():
        raise ValueError(f"нет {manifest.name} — ролик не прошёл новую проверку")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not data.get("passed") or data.get("video_sha256") != _sha256(video):
        raise ValueError("проверка ролика устарела или относится к другому MP4")
    return data
