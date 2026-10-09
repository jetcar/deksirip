"""Upload a chapter video built by make_video.py to YouTube as a private video.

Unverified API projects can only upload private videos; switch them to public in YouTube Studio.
Setup: put the OAuth "Desktop app" client JSON at tools/client_secret.json; the first run opens
a browser to sign in and pick the book's channel, then the token is kept in tools/youtube_token.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from synthesize_audio import ROOT

TOOLS = Path(__file__).resolve().parent
CLIENT_SECRET = TOOLS / "client_secret.json"
TOKEN = TOOLS / "youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
EDUCATION = "27"


def credentials(interactive: bool) -> Credentials:
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except Exception:
            if not interactive:
                raise SystemExit("Токен YouTube истёк: запустите скрипт вручную с --login")
    if not interactive:
        raise SystemExit("Нет токена YouTube: запустите скрипт вручную с --login")
    if not CLIENT_SECRET.exists():
        raise SystemExit(f"Нет {CLIENT_SECRET.name} — скачайте OAuth-ключ типа Desktop app")
    creds = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES).run_local_server(port=0)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


def upload(stem: str, folder: Path, interactive: bool) -> str:
    video = folder / f"{stem}.mp4"
    meta = folder / f"{stem}.txt"
    thumbnail = folder / f"{stem}.png"
    record = folder / f"{stem}.uploaded.json"
    if record.exists():
        video_id = json.loads(record.read_text(encoding="utf-8"))["id"]
        print(f"Уже загружено: https://youtu.be/{video_id}")
        return video_id
    if not video.is_file() or not meta.is_file():
        raise SystemExit(f"Нет {video.name} или {meta.name} — сначала make_video.py")
    title, _, description = meta.read_text(encoding="utf-8").partition("\n")
    youtube = build("youtube", "v3", credentials=credentials(interactive))
    body = {
        "snippet": {
            "title": title.strip()[:100],
            "description": description.strip()[:5000],
            "categoryId": EDUCATION,
            "defaultLanguage": "ru",
            "defaultAudioLanguage": "ru",
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        },
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video), mimetype="video/mp4", chunksize=16 * 1024 * 1024, resumable=True),
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", flush=True)
    video_id = response["id"]
    record.write_text(json.dumps({"id": video_id, "title": title.strip()}, ensure_ascii=False), encoding="utf-8")
    if thumbnail.is_file():
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbnail))).execute()
        except Exception as error:  # custom thumbnails need a phone-verified channel
            print(f"  обложка не установлена: {error}")
    print(f"Загружено (приватно): https://youtu.be/{video_id}")
    return video_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", help="chapter file name without .md")
    parser.add_argument("--folder", type=Path, default=ROOT / "video")
    parser.add_argument("--login", action="store_true", help="allow the browser sign-in flow")
    args = parser.parse_args()
    if args.chapter:
        upload(Path(args.chapter).stem, args.folder, args.login)
    elif args.login:
        credentials(True)
        print("Вход выполнен")
    else:
        parser.error("укажите --chapter и/или --login")


if __name__ == "__main__":
    main()
