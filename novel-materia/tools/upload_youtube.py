"""Upload the chapter videos of «Материальный вопрос» to YouTube and keep them in their own playlist.

Uses the same OAuth client and token as the first book (book/tools/client_secret.json and
book/tools/youtube_token.json), so the channel login is shared. The token can also come from the
YOUTUBE_TOKEN_JSON environment variable (its JSON content), which lets a non-interactive job upload.

    pip install google-api-python-client google-auth-oauthlib
    python novel-materia/tools/upload_youtube.py --login --all      # first run: browser sign-in, every chapter
    python novel-materia/tools/upload_youtube.py --chapter 15-noch-v-laboratorii

What was uploaded is recorded in novel-materia/media/<stem>.uploaded.json and media/playlist.json;
commit them so the next run (anywhere) does not upload a chapter twice.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from make_media import BOOK_TITLE, CHAPTERS, OUTPUT, blocks, chapter_title

REPO = Path(__file__).resolve().parents[2]
CLIENT_SECRET = REPO / "book" / "tools" / "client_secret.json"
TOKEN = REPO / "book" / "tools" / "youtube_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # captions, playlists
]
ENTERTAINMENT = "24"
PLAYLIST_TITLE = f"{BOOK_TITLE} — аудиокнига"
BOOK_DESCRIPTION = (
    "«Материальный вопрос» — роман-аудиокнига. Тимофей еле сводит концы с концами, пока не находит "
    "напёрсток, дающий власть над веществом. Вместо того чтобы сражаться со злом, он чинит, делает, "
    "меняет и считает — и пытается понять, как эта сила работает, и научить ей других. "
    "Комедия с элементами эротики, 18+. Озвучено синтезатором речи RHVoice."
)


def credentials(interactive: bool) -> Credentials:
    inline = os.environ.get("YOUTUBE_TOKEN_JSON")
    if inline:
        creds = Credentials.from_authorized_user_info(json.loads(inline), SCOPES)
    else:
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.valid:
        return creds
    if creds and creds.refresh_token:
        creds.refresh(Request())
        if not inline:
            TOKEN.write_text(creds.to_json(), encoding="utf-8")
        return creds
    if not interactive:
        raise SystemExit("Нет токена YouTube: запустите с --login (нужен браузер)")
    if not CLIENT_SECRET.exists():
        raise SystemExit(f"Нет {CLIENT_SECRET} — скачайте OAuth-ключ типа Desktop app")
    creds = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES).run_local_server(port=0)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


def teaser(source: Path, limit: int = 600) -> str:
    """The chapter's opening paragraphs, up to about `limit` characters."""
    text = ""
    for kind, paragraph in blocks(source):
        if kind != "paragraph":
            continue
        text = f"{text}\n\n{paragraph}" if text else paragraph
        if len(text) >= limit:
            break
    return text.replace("*", "")


def upload(youtube, stem: str, privacy: str) -> str:
    record = OUTPUT / f"{stem}.uploaded.json"
    if record.exists():
        video_id = json.loads(record.read_text(encoding="utf-8"))["id"]
        print(f"{stem}: уже загружено https://youtu.be/{video_id}")
        return video_id
    video = OUTPUT / f"{stem}.mp4"
    if not video.is_file():
        raise SystemExit(f"Нет {video} — сначала make_media.py")
    source = CHAPTERS / f"{stem}.md"
    title = f"{BOOK_TITLE}. {chapter_title(source)}"
    description = f"{teaser(source)}\n\n—\n{BOOK_DESCRIPTION}"
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "categoryId": ENTERTAINMENT,
                "defaultLanguage": "ru",
                "defaultAudioLanguage": "ru",
                "tags": ["аудиокнига", "роман", BOOK_TITLE],
            },
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True},
        },
        media_body=MediaFileUpload(str(video), mimetype="video/mp4", chunksize=16 * 1024 * 1024, resumable=True),
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {stem}: {int(status.progress() * 100)}%", flush=True)
    video_id = response["id"]
    record.write_text(json.dumps({"id": video_id, "title": title}, ensure_ascii=False) + "\n", encoding="utf-8")
    cover = OUTPUT / f"{stem}.png"
    if cover.is_file():
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(cover))).execute()
        except Exception as error:  # custom thumbnails need a phone-verified channel
            print(f"  обложка не установлена: {error}")
    subtitles = OUTPUT / f"{stem}.srt"
    if subtitles.is_file():
        youtube.captions().insert(
            part="snippet",
            body={"snippet": {"videoId": video_id, "language": "ru", "name": "Русский"}},
            media_body=MediaFileUpload(str(subtitles), mimetype="application/octet-stream"),
        ).execute()
    print(f"{stem}: загружено https://youtu.be/{video_id}")
    return video_id


def sync_playlist(youtube, privacy: str) -> None:
    """One playlist for the book with every uploaded chapter in chapter order."""
    store = OUTPUT / "playlist.json"
    if store.exists():
        playlist_id = json.loads(store.read_text(encoding="utf-8"))["id"]
    else:
        playlist_id = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": PLAYLIST_TITLE, "description": BOOK_DESCRIPTION, "defaultLanguage": "ru"},
                "status": {"privacyStatus": privacy},
            },
        ).execute()["id"]
        store.write_text(json.dumps({"id": playlist_id}) + "\n", encoding="utf-8")
        print(f"плейлист создан: https://www.youtube.com/playlist?list={playlist_id}")
        time.sleep(5)  # a just-created playlist is not writable for a moment
    present: set[str] = set()
    page = None
    while True:
        response = youtube.playlistItems().list(
            part="contentDetails", playlistId=playlist_id, maxResults=50, pageToken=page
        ).execute()
        present |= {item["contentDetails"]["videoId"] for item in response["items"]}
        page = response.get("nextPageToken")
        if not page:
            break
    for position, record in enumerate(sorted(OUTPUT.glob("[0-9][0-9]-*.uploaded.json"))):
        video_id = json.loads(record.read_text(encoding="utf-8"))["id"]
        if video_id in present:
            continue
        youtube.playlistItems().insert(
            part="snippet",
            body={"snippet": {
                "playlistId": playlist_id,
                "position": position,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }},
        ).execute()
        print(f"  в плейлист: {record.name.removesuffix('.uploaded.json')}")
    print(f"плейлист: https://www.youtube.com/playlist?list={playlist_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--chapter", help="chapter file name, with or without .md")
    target.add_argument("--all", action="store_true", help="every chapter that has a video and is not uploaded yet")
    parser.add_argument("--login", action="store_true", help="allow the browser sign-in flow")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="public")
    args = parser.parse_args()

    youtube = build("youtube", "v3", credentials=credentials(args.login))
    stems = ([Path(args.chapter).stem] if args.chapter
             else sorted(path.stem for path in OUTPUT.glob("[0-9][0-9]-*.mp4")))
    for stem in stems:
        upload(youtube, stem, args.privacy)
    sync_playlist(youtube, args.privacy)


if __name__ == "__main__":
    main()
