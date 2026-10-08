"""Create per-chapter Russian MP3 narration from the manuscript Markdown files."""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "chapters"
OUTPUT = ROOT / "audio"
MAX_CHARS = 9_000


def narration_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def chunks(text: str) -> list[str]:
    result: list[str] = []
    remaining = text
    while len(remaining) > MAX_CHARS:
        split_at = max(remaining.rfind("\n\n", 0, MAX_CHARS), remaining.rfind(". ", 0, MAX_CHARS))
        if split_at < MAX_CHARS // 2:
            split_at = MAX_CHARS
        result.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        result.append(remaining)
    return result


async def synthesize(source: Path, voice: str) -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / f"{source.stem}.mp3"
    pieces = []
    for index, part in enumerate(chunks(narration_text(source)), start=1):
        piece = OUTPUT / f".{source.stem}.{index}.mp3"
        await edge_tts.Communicate(part, voice=voice, rate="-8%").save(str(piece))
        pieces.append(piece)
    with target.open("wb") as audio:
        for piece in pieces:
            audio.write(piece.read_bytes())
    for piece in pieces:
        piece.unlink(missing_ok=True)
    return target


def targets(chapter: str | None, make_all: bool) -> list[Path]:
    if make_all:
        return sorted(CHAPTERS.glob("*.md"))
    stem = Path(chapter or "").stem
    source = CHAPTERS / f"{stem}.md"
    if not source.is_file():
        raise SystemExit(f"Глава не найдена: {source.name}")
    return [source]


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--voice", default="ru-RU-SvetlanaNeural")
    args = parser.parse_args()
    if bool(args.chapter) == bool(args.all):
        parser.error("укажите ровно один из параметров: --chapter или --all")
    for source in targets(args.chapter, args.all):
        target = await synthesize(source, args.voice)
        print(target)


if __name__ == "__main__":
    asyncio.run(main())
