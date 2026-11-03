"""Render the English metals, trade, and money chapter from prepared local assets."""

from argparse import Namespace

from local_voice import REPO, command_video


def main() -> int:
    slides = sorted((REPO / "book/slides-en/04-metals-trade-money").glob("*.png"))
    if not slides:
        raise SystemExit("No chapter slides found")
    return command_video(
        Namespace(
            audio=REPO / "book/audio-en/04-metals-trade-money-kokoro-heart.wav",
            image=slides,
            output=REPO / "book/video-en/04-metals-trade-money-kokoro-heart.mp4",
            size="1920x1080",
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
