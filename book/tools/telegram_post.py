"""Post to the book's Telegram channel through its bot.

Setup: the bot token in tools/telegram_token.txt; the bot is an admin of the channel with posting rights.
  --text FILE                 post a prepared message (Telegram HTML)
  --pending                   list released chapters not yet announced
  --chapter STEM --summary S  announce a released chapter and remember it
"""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path

import requests

from synthesize_audio import ROOT
from upload_youtube import chapter_order, chapter_release

TOOLS = Path(__file__).resolve().parent
TOKEN = TOOLS / "telegram_token.txt"
CHANNEL = "@kuda_ushel_izlishek"
VIDEO = ROOT / "video"
PLAYLIST_URL = "https://www.youtube.com/playlist?list=" + (
    json.loads((VIDEO / "playlist.json").read_text())["id"] if (VIDEO / "playlist.json").exists() else ""
)


def send(text: str) -> int:
    token = TOKEN.read_text(encoding="utf-8").strip()
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": CHANNEL, "text": text, "parse_mode": "HTML", "link_preview_options": {"is_disabled": False}},
        timeout=60,
    ).json()
    if not response.get("ok"):
        raise SystemExit(f"Telegram: {response.get('description')}")
    return response["result"]["message_id"]


def chapter_title(stem: str) -> str:
    for line in (ROOT / f"{stem}.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return stem


def pending() -> list[str]:
    """Chapters whose release time has passed, uploaded, and not announced yet."""
    now = datetime.now().astimezone()
    result = []
    for stem in chapter_order():
        release = chapter_release(stem)
        record = VIDEO / f"{stem}.uploaded.json"
        if release and release <= now and record.exists() and not (VIDEO / f"{stem}.announced").exists():
            result.append(stem)
    return result


def announce(stem: str, summary: str) -> None:
    marker = VIDEO / f"{stem}.announced"
    if marker.exists():
        print(f"Уже анонсировано: {stem}")
        return
    video_id = json.loads((VIDEO / f"{stem}.uploaded.json").read_text(encoding="utf-8"))["id"]
    title = re.sub(r"^Глава\s+(\d+)\.\s*", r"Глава \1. ", chapter_title(stem))
    text = (
        f"🎧 <b>{html.escape(title)}</b>\n\n"
        f"{html.escape(summary.strip())}\n\n"
        f"▶️ https://youtu.be/{video_id}\n"
        f"Вся книга по порядку: {PLAYLIST_URL}\n\n"
        "Что спорно, где ошибки, о чём рассказать подробнее — пишите в комментариях."
    )
    message_id = send(text)
    marker.write_text(json.dumps({"message_id": message_id, "at": datetime.now().isoformat(timespec="minutes")}), encoding="utf-8")
    print(f"Анонс отправлен: {stem} (сообщение {message_id})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=Path)
    parser.add_argument("--pending", action="store_true")
    parser.add_argument("--chapter")
    parser.add_argument("--summary")
    args = parser.parse_args()
    if args.text:
        print(f"Отправлено: сообщение {send(args.text.read_text(encoding='utf-8').strip())}")
    elif args.pending:
        print("\n".join(pending()) or "нет")
    elif args.chapter and args.summary:
        announce(Path(args.chapter).stem, args.summary)
    else:
        parser.error("укажите --text, --pending или --chapter с --summary")


if __name__ == "__main__":
    main()
