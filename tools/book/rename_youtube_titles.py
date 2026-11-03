"""Move the book title to the end of uploaded chapter titles.

Run from the repository root: python tools/book/rename_youtube_titles.py [--apply]
Without --apply, show the planned changes without contacting YouTube.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from synthesize_audio import ROOT

FOLDER = ROOT / "video"
BOOK_TITLE = "Куда ушёл излишек"
PREFIX = f"{BOOK_TITLE}. "


def planned() -> list[tuple[Path, dict, str]]:
    changes = []
    for record in sorted(FOLDER.glob("[0-9][0-9]-*.uploaded.json")):
        data = json.loads(record.read_text(encoding="utf-8"))
        old = data["title"]
        if old.startswith(PREFIX):
            new = f"{old[len(PREFIX):]} — {BOOK_TITLE}"
        elif old.endswith(f" — {BOOK_TITLE}"):
            new = old  # allow a retry after a partially completed run
        else:
            raise SystemExit(f"Неожиданное название в {record.name}: {old}")
        if len(new) > 100:
            raise SystemExit(f"Название длиннее 100 символов: {new}")
        meta = record.with_name(record.name.replace(".uploaded.json", ".txt"))
        if meta.read_text(encoding="utf-8").splitlines()[0] != old:
            raise SystemExit(f"Название в {meta.name} отличается от записи о загрузке")
        changes.append((record, data, new))
    return changes


def apply(changes: list[tuple[Path, dict, str]]) -> None:
    from googleapiclient.discovery import build
    from upload_youtube import credentials

    youtube = build("youtube", "v3", credentials=credentials(False, "jetcarq"))
    ids = ",".join(data["id"] for _, data, _ in changes)
    response = youtube.videos().list(part="snippet", id=ids, maxResults=50).execute()
    snippets = {item["id"]: item["snippet"] for item in response["items"]}
    for record, data, new in changes:
        video_id = data["id"]
        snippet = snippets.get(video_id)
        if snippet is None or snippet["title"] not in (data["title"], new):
            raise SystemExit(f"Название на YouTube отличается: {record.name} ({video_id})")
    for record, data, new in changes:
        video_id = data["id"]
        snippet = snippets[video_id]
        if snippet["title"] != new:
            body = {key: snippet[key] for key in (
                "description", "categoryId", "tags", "defaultLanguage", "defaultAudioLanguage"
            ) if key in snippet}
            body["title"] = new
            youtube.videos().update(part="snippet", body={"id": video_id, "snippet": body}).execute()
        meta = record.with_name(record.name.replace(".uploaded.json", ".txt"))
        _, separator, description = meta.read_text(encoding="utf-8").partition("\n")
        meta.write_text(new + separator + description, encoding="utf-8")
        data["title"] = new
        record.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"{record.name}: {new}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="rename the YouTube videos and local metadata")
    args = parser.parse_args()
    changes = planned()
    if args.apply:
        apply(changes)
    else:
        for record, _, new in changes:
            print(f"{record.name}: {new}")
        print(f"План: {len(changes)} видео. Для применения: --apply")


if __name__ == "__main__":
    main()
