"""Render the English temple-economies chapter from prepared local assets."""

from argparse import Namespace

from local_voice import REPO, command_video


def main() -> int:
    slides = sorted((REPO / "book/slides-en/03-temple-economies").glob("*.png"))
    if not slides:
        raise SystemExit("No chapter slides found")
    return command_video(
        Namespace(
            audio=REPO / "book/audio-en/03-temple-economies-kokoro-heart.wav",
            image=slides,
            output=REPO / "book/video-en/03-temple-economies-kokoro-heart.mp4",
            size="1920x1080",
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
