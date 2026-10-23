from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS_DIR = ROOT / "chapters"
OUTPUT = ROOT / "MANUSCRIPT.md"


def main() -> None:
    chapters = sorted(CHAPTERS_DIR.glob("[0-9][0-9]-*.md"))
    expected = list(range(1, 29))
    actual = [int(path.name[:2]) for path in chapters]
    if actual != expected:
        raise SystemExit(f"Expected chapters 01-28, found: {actual}")

    texts: list[str] = []
    for number, path in zip(expected, chapters, strict=True):
        text = path.read_text(encoding="utf-8").strip()
        match = re.match(r"^# Глава (\d+)\.", text)
        if not match or int(match.group(1)) != number:
            raise SystemExit(f"Invalid chapter heading: {path.name}")
        texts.append(text)

    manuscript = "# Шестой пункт\n\n" + "\n\n---\n\n".join(texts) + "\n"
    OUTPUT.write_text(manuscript, encoding="utf-8", newline="\n")
    print(f"Built {OUTPUT.name}: {len(chapters)} chapters, {len(manuscript.split())} words")


if __name__ == "__main__":
    main()
