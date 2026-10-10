"""Upload a chapter video built by make_video.py to YouTube as a private video.

Unverified API projects can only upload private videos; switch them to public in YouTube Studio.
Setup: put the OAuth "Desktop app" client JSON at tools/client_secret.json; the first run opens
a browser to sign in and pick the book's channel, then the token is kept in tools/youtube_token.json.
"""

from __future__ import annotations

import argparse
import json
import time
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
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # captions
]
EDUCATION = "27"


def credentials(interactive: bool) -> Credentials:
    creds = Credentials.from_authorized_user_file(str(TOKEN)) if TOKEN.exists() else None
    if creds and not creds.has_scopes(SCOPES):  # token from before captions were added
        creds = None
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


def add_captions(youtube, video_id: str, subtitles: Path) -> None:
    youtube.captions().insert(
        part="snippet",
        body={"snippet": {"videoId": video_id, "language": "ru", "name": "Русский"}},
        media_body=MediaFileUpload(str(subtitles), mimetype="application/octet-stream"),
    ).execute()


def captions(stem: str, folder: Path, interactive: bool) -> None:
    """Attach <stem>.srt to an already uploaded video, once."""
    record = folder / f"{stem}.uploaded.json"
    subtitles = folder / f"{stem}.srt"
    if not record.exists() or not subtitles.exists():
        return
    data = json.loads(record.read_text(encoding="utf-8"))
    if data.get("captions"):
        return
    youtube = build("youtube", "v3", credentials=credentials(interactive))
    add_captions(youtube, data["id"], subtitles)
    data["captions"] = True
    record.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print("  субтитры добавлены")


PLAYLIST_TITLE = "Куда ушёл излишек — аудиокнига целиком"
PLAYLIST_DESCRIPTION = (
    "Вся аудиокнига по порядку: от введения и охотников-собирателей до наших дней. "
    "Главы добавляются по мере готовности."
)


def sync_playlist(folder: Path, interactive: bool) -> None:
    """Keep one public playlist with every uploaded chapter, in chapter order."""
    records = sorted(folder.glob("[0-9][0-9]-*.uploaded.json"))
    if not records:
        return
    youtube = build("youtube", "v3", credentials=credentials(interactive))
    store = folder / "playlist.json"
    if store.exists():
        playlist_id = json.loads(store.read_text(encoding="utf-8"))["id"]
    else:
        playlist_id = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": PLAYLIST_TITLE, "description": PLAYLIST_DESCRIPTION, "defaultLanguage": "ru"},
                "status": {"privacyStatus": "public"},
            },
        ).execute()["id"]
        store.write_text(json.dumps({"id": playlist_id}), encoding="utf-8")
        print(f"  плейлист создан: https://www.youtube.com/playlist?list={playlist_id}")
    items: dict[str, str] = {}  # video id -> playlist item id
    page = None
    while store.stat().st_mtime < time.time() - 60:  # a just-created playlist is not listable yet, and empty anyway
        response = youtube.playlistItems().list(
            part="id,contentDetails", playlistId=playlist_id, maxResults=50, pageToken=page
        ).execute()
        items.update({item["contentDetails"]["videoId"]: item["id"] for item in response["items"]})
        page = response.get("nextPageToken")
        if not page:
            break
    replaced = {old for path in folder.glob("[0-9][0-9]-*.replaced.json")
                for old in json.loads(path.read_text(encoding="utf-8"))}
    for video_id in replaced & items.keys():  # drop superseded versions from the playlist (the videos stay)
        youtube.playlistItems().delete(id=items.pop(video_id)).execute()
        print(f"  из плейлиста убрана старая версия {video_id}")
    present = set(items)
    position = 0  # chapters already in the playlist before this one
    for record in records:
        video_id = json.loads(record.read_text(encoding="utf-8"))["id"]
        if video_id in present:
            position += 1
            continue
        youtube.playlistItems().insert(
            part="snippet",
            body={"snippet": {
                "playlistId": playlist_id,
                "position": position,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }},
        ).execute()
        position += 1
        print(f"  в плейлист: {record.name.removesuffix('.uploaded.json')}")


def upload(stem: str, folder: Path, interactive: bool, replace: bool = False) -> str:
    video = folder / f"{stem}.mp4"
    meta = folder / f"{stem}.txt"
    thumbnail = folder / f"{stem}.png"
    record = folder / f"{stem}.uploaded.json"
    if record.exists() and replace:  # remember the old id so the playlist swaps it out
        history = folder / f"{stem}.replaced.json"
        old_ids = json.loads(history.read_text(encoding="utf-8")) if history.exists() else []
        old_ids.append(json.loads(record.read_text(encoding="utf-8"))["id"])
        history.write_text(json.dumps(old_ids), encoding="utf-8")
        record.unlink()
    if record.exists():
        video_id = json.loads(record.read_text(encoding="utf-8"))["id"]
        print(f"Уже загружено: https://youtu.be/{video_id}")
        captions(stem, folder, interactive)
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
    captions(stem, folder, interactive)
    print(f"Загружено (приватно): https://youtu.be/{video_id}")
    return video_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", help="chapter file name without .md")
    parser.add_argument("--folder", type=Path, default=ROOT / "video")
    parser.add_argument("--login", action="store_true", help="allow the browser sign-in flow")
    parser.add_argument("--replace", action="store_true", help="upload a new version and swap it into the playlist")
    args = parser.parse_args()
    if args.chapter:
        upload(Path(args.chapter).stem, args.folder, args.login, args.replace)
        if args.folder.resolve() == (ROOT / "video").resolve():  # chapters only, not shorts
            sync_playlist(args.folder, args.login)
    elif args.login:
        credentials(True)
        print("Вход выполнен")
    else:
        parser.error("укажите --chapter и/или --login")


if __name__ == "__main__":
    main()
