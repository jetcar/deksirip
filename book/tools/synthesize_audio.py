"""Create per-chapter Russian MP3 narration of the book from its Markdown files."""

from __future__ import annotations

import argparse
import asyncio
import re
import shutil
import subprocess
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


def clean(lines: list[str]) -> str:
    result = []
    for line in lines:
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
        result.append(line)
    text = "\n".join(result)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def sections(path: Path) -> list[tuple[str, str]]:
    """Split a chapter into (section title, narration text); the chapter heading opens the first one."""
    groups: list[tuple[str, list[str]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        top = re.match(r"^#\s+(.+)$", line)
        sub = re.match(r"^##\s+(.+)$", line)
        if sub or (top and not groups):
            groups.append(((sub or top).group(1).strip(), []))
        elif not groups:
            groups.append(("", []))
        groups[-1][1].append(line)
    result: list[tuple[str, str]] = []
    carry = ""
    for title, lines in groups:
        text = clean(lines)
        if len(text) < 200:  # a bare chapter heading: read it with the next section
            carry = f"{carry}\n\n{text}".strip()
            continue
        result.append((title, f"{carry}\n\n{text}".strip()))
        carry = ""
    if carry:
        result.append(("", carry))
    return result


def narration_text(path: Path) -> str:
    return "\n\n".join(text for _, text in sections(path))


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


def ffmpeg_tool(name: str) -> str:
    """Find ffmpeg/ffprobe even when PATH predates the winget install."""
    found = shutil.which(name)
    if found:
        return found
    packages = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    for candidate in packages.glob(f"Gyan.FFmpeg*/*/bin/{name}.exe"):
        return str(candidate)
    raise SystemExit(f"{name} не найден")


def duration(path: Path) -> float:
    out = subprocess.run(
        [ffmpeg_tool("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def timestamp(seconds: float) -> str:
    hours, rest = divmod(int(seconds), 3600)
    return f"{hours}:{rest // 60:02}:{rest % 60:02}" if hours else f"{rest // 60:02}:{rest % 60:02}"


async def synthesize(source: Path, voice: str, output: Path, outro: str | None) -> Path:
    """Write <chapter>.mp3 and <chapter>.chapters.txt (section timestamps for video descriptions)."""
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"{source.stem}.mp3"
    parts = sections(source)
    if outro:
        parts.append(("Поддержать проект", outro))
    jobs = [(title, chunk) for title, text in parts for chunk in chunks(text)]
    pieces: list[tuple[str, Path]] = []
    for index, (title, chunk) in enumerate(jobs, start=1):
        piece = output / f".{source.stem}.{index:03}.mp3"
        if not piece.exists() or piece.stat().st_size == 0:
            await speak(chunk, voice, piece)
        print(f"  {source.stem}: {index}/{len(jobs)}", flush=True)
        pieces.append((title, piece))
    marks: list[str] = []
    elapsed = 0.0
    previous = None
    for title, piece in pieces:
        if title and title != previous:
            marks.append(f"{timestamp(elapsed)} {title}")
            previous = title
        elapsed += duration(piece)
    with target.open("wb") as audio:
        for _, piece in pieces:
            audio.write(piece.read_bytes())
    (output / f"{source.stem}.chapters.txt").write_text("\n".join(marks) + "\n", encoding="utf-8")
    for _, piece in pieces:
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
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--outro", help="text read after the chapter, e.g. a support note")
    args = parser.parse_args()
    if bool(args.chapter) == bool(args.all):
        parser.error("укажите ровно один из параметров: --chapter или --all")
    for source in targets(args.chapter, args.all):
        if args.skip_existing and (args.output / f"{source.stem}.mp3").exists():
            continue
        print(await synthesize(source, args.voice, args.output, args.outro), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
