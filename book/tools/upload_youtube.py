"""Upload a chapter video built by make_video.py to YouTube, public or scheduled by the release queue.

Setup: put the OAuth "Desktop app" client JSON at tools/client_secret.json; the first run opens
a browser to sign in and pick the book's channel, then the token is kept in tools/youtube_token.json.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from synthesize_audio import CHAPTER_PATTERN, ROOT

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
    """Keep one public playlist with every released chapter, in chapter order.

    Queued chapters stay out until their release time: a private video still shows up as an empty row.
    """
    now = datetime.now().astimezone()
    uploaded = sorted(folder.glob("[0-9][0-9]-*.uploaded.json"))
    if not uploaded:
        return

    def released(record: Path) -> bool:
        release = chapter_release(record.name.removesuffix(".uploaded.json"))
        return release is None or release <= now

    records = [record for record in uploaded if released(record)]
    queued = {json.loads(record.read_text(encoding="utf-8"))["id"] for record in uploaded if not released(record)}
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
    for video_id in queued & items.keys():
        youtube.playlistItems().delete(id=items.pop(video_id)).execute()
        print(f"  из плейлиста убрана глава из очереди {video_id}")
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


# Release queue: chapters 00-02 are public; from 03 on, one chapter a day at 18:00 local time,
# and each Short the day after its chapter (and after the previous Short) at 12:00.
FIRST_QUEUED_CHAPTER = 3
QUEUE_START = date(2026, 10, 12)
CHAPTER_HOUR = 18
SHORT_HOUR = 12
SHORTS_SCHEDULE = ROOT / "shorts" / "schedule.json"


def chapter_order() -> list[str]:
    return sorted(path.stem for path in ROOT.glob("*.md") if CHAPTER_PATTERN.match(path.name))


def local_time(day: date, hour: int) -> datetime:
    return datetime.combine(day, dtime(hour)).astimezone()  # the OS applies the local DST offset


def chapter_release(stem: str) -> datetime | None:
    """When a chapter goes public; None means it is public already."""
    order = chapter_order()
    if stem not in order or order.index(stem) < FIRST_QUEUED_CHAPTER:
        return None
    return local_time(QUEUE_START + timedelta(days=order.index(stem) - FIRST_QUEUED_CHAPTER), CHAPTER_HOUR)


def short_release(stem: str) -> datetime:
    schedule = json.loads(SHORTS_SCHEDULE.read_text(encoding="utf-8")) if SHORTS_SCHEDULE.exists() else {}
    if stem in schedule:
        return datetime.fromisoformat(schedule[stem])
    theses = json.loads((ROOT / "shorts" / "theses.json").read_text(encoding="utf-8"))
    chapter = next(t["chapter"] for t in theses if f"short-{t['id']:03}" == stem)
    chapter_day = chapter_release(chapter)
    day = max(
        (chapter_day.date() + timedelta(days=1)) if chapter_day else date.today(),
        max((datetime.fromisoformat(v).date() + timedelta(days=1) for v in schedule.values()), default=date.today()),
        date.today() if datetime.now().hour < SHORT_HOUR else date.today() + timedelta(days=1),
    )
    release = local_time(day, SHORT_HOUR)
    schedule[stem] = release.isoformat()
    SHORTS_SCHEDULE.write_text(json.dumps(schedule, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return release


def release_status(stem: str, folder: Path) -> dict:
    """privacyStatus/publishAt for a new or rescheduled video."""
    release = short_release(stem) if stem.startswith("short-") else chapter_release(stem)
    if release is None or release <= datetime.now().astimezone() + timedelta(minutes=15):
        return {"privacyStatus": "public"}
    return {"privacyStatus": "private", "publishAt": release.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def reschedule_chapters(folder: Path, interactive: bool) -> None:
    """Apply the release queue to every uploaded chapter."""
    youtube = build("youtube", "v3", credentials=credentials(interactive))
    for record in sorted(folder.glob("[0-9][0-9]-*.uploaded.json")):
        stem = record.name.removesuffix(".uploaded.json")
        video_id = json.loads(record.read_text(encoding="utf-8"))["id"]
        current = youtube.videos().list(part="status", id=video_id).execute()["items"][0]["status"]
        status = {
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": current.get("containsSyntheticMedia", True),
            "embeddable": current.get("embeddable", True),
            "license": current.get("license", "youtube"),
            "publicStatsViewable": current.get("publicStatsViewable", True),
            **release_status(stem, folder),
        }
        try:
            youtube.videos().update(part="status", body={"id": video_id, "status": status}).execute()
        except HttpError as error:
            if "invalidPublishAt" not in str(error):
                raise
            # YouTube refuses publishAt on a video that was ever public: hide it, release_due() opens it later
            status.pop("publishAt")
            youtube.videos().update(part="status", body={"id": video_id, "status": status}).execute()
            status["publishAt"] = f"{chapter_release(stem):%Y-%m-%d %H:%M} (откроет --release-due)"
        print(f"  {stem}: {status.get('publishAt', status['privacyStatus'])}")


def release_due(folder: Path, interactive: bool) -> None:
    """Make public every queued chapter whose release time has come (for videos YouTube cannot schedule)."""
    youtube = build("youtube", "v3", credentials=credentials(interactive))
    now = datetime.now().astimezone()
    for record in sorted(folder.glob("[0-9][0-9]-*.uploaded.json")):
        stem = record.name.removesuffix(".uploaded.json")
        release = chapter_release(stem)
        if release and release > now:
            continue
        video_id = json.loads(record.read_text(encoding="utf-8"))["id"]
        current = youtube.videos().list(part="status", id=video_id).execute()["items"][0]["status"]
        if current["privacyStatus"] == "public" or current.get("publishAt"):
            continue
        status = {key: current[key] for key in ("embeddable", "license", "publicStatsViewable") if key in current}
        status.update(privacyStatus="public", selfDeclaredMadeForKids=False,
                      containsSyntheticMedia=current.get("containsSyntheticMedia", True))
        youtube.videos().update(part="status", body={"id": video_id, "status": status}).execute()
        print(f"  открыто: {stem} https://youtu.be/{video_id}")
    sync_playlist(folder, interactive)  # released chapters, including ones YouTube published on schedule


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
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
            **release_status(stem, folder),
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
    when = body["status"].get("publishAt", "сразу")
    print(f"Загружено: https://youtu.be/{video_id} — публикация: {when}")
    return video_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", help="chapter file name without .md")
    parser.add_argument("--folder", type=Path, default=ROOT / "video")
    parser.add_argument("--login", action="store_true", help="allow the browser sign-in flow")
    parser.add_argument("--replace", action="store_true", help="upload a new version and swap it into the playlist")
    parser.add_argument("--reschedule", action="store_true", help="apply the release queue to uploaded chapters")
    parser.add_argument("--release-due", action="store_true", help="make public the queued chapters that are due")
    args = parser.parse_args()
    if args.reschedule:
        reschedule_chapters(args.folder, args.login)
    elif args.release_due:
        release_due(args.folder, args.login)
    elif args.chapter:
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
