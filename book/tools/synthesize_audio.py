"""Create per-chapter Russian MP3 narration of the book from its Markdown files."""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "audio"
MAX_CHARS = 9_000
RETRIES = 5
CHAPTER_PATTERN = re.compile(r"^(?!00-plan)\d\d-[\w-]+\.md$")


def table_line(line: str) -> str:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    cells = [cell for cell in cells if cell]
    return "; ".join(cells) + "." if cells else ""


def narration_text(path: Path) -> str:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*\|?\s*:?-{3,}", line):
            continue
        if line.lstrip().startswith("|"):
            line = table_line(line)
        heading = re.match(r"^#{1,6}\s*(.+)$", line)
        if heading:
            title = heading.group(1).strip()
            line = title if title.endswith((".", "!", "?")) else title + "."
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = re.sub(r"^\s*>\s?", "", line)
        lines.append(line)
    text = "\n".join(lines)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def chunks(text: str) -> list[str]:
    result: list[str] = []
    remaining = text
    while len(remaining) > MAX_CHARS:
        split_at = max(remaining.rfind("\n\n", 0, MAX_CHARS), remaining.rfind(". ", 0, MAX_CHARS) + 1)
        if split_at < MAX_CHARS // 2:
            split_at = MAX_CHARS
        result.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        result.append(remaining)
    return result


async def speak(text: str, voice: str, target: Path) -> None:
    for attempt in range(1, RETRIES + 1):
        try:
            await edge_tts.Communicate(text, voice=voice, rate="+0%").save(str(target))
            if target.stat().st_size > 0:
                return
        except Exception as error:  # network hiccups from the TTS service
            if attempt == RETRIES:
                raise
            print(f"  retry {attempt}: {error}")
        await asyncio.sleep(5 * attempt)
    raise RuntimeError(f"empty audio for {target.name}")


async def synthesize(source: Path, voice: str) -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / f"{source.stem}.mp3"
    parts = chunks(narration_text(source))
    pieces = []
    for index, part in enumerate(parts, start=1):
        piece = OUTPUT / f".{source.stem}.{index:03}.mp3"
        if not piece.exists() or piece.stat().st_size == 0:
            await speak(part, voice, piece)
        print(f"  {source.stem}: {index}/{len(parts)}", flush=True)
        pieces.append(piece)
    with target.open("wb") as audio:
        for piece in pieces:
            audio.write(piece.read_bytes())
    for piece in pieces:
        piece.unlink(missing_ok=True)
    return target


def targets(chapter: str | None, make_all: bool) -> list[Path]:
    if make_all:
        return sorted(path for path in ROOT.glob("*.md") if CHAPTER_PATTERN.match(path.name))
    source = ROOT / f"{Path(chapter or '').stem}.md"
    if not source.is_file():
        raise SystemExit(f"Глава не найдена: {source.name}")
    return [source]


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--voice", default="ru-RU-SvetlanaNeural")
    args = parser.parse_args()
    if bool(args.chapter) == bool(args.all):
        parser.error("укажите ровно один из параметров: --chapter или --all")
    for source in targets(args.chapter, args.all):
        if args.skip_existing and (OUTPUT / f"{source.stem}.mp3").exists():
            continue
        print(await synthesize(source, args.voice), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
