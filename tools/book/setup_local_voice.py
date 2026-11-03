"""Install the local Russian and English narration toolchain on Windows.

Example:
    python tools/book/setup_local_voice.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
XVIBE = REPO / ".voice" / "xVibePocketTTS"
VENV_PYTHON = XVIBE / ".venv" / "Scripts" / "python.exe"
XVIBE_URL = "https://github.com/GenVoice/xVibePocketTTS.git"


def run(command: list[str], *, cwd: Path = REPO) -> None:
    print("+", subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--without-demo", action="store_true", help="не ставить Gradio UI xVibe"
    )
    parser.add_argument(
        "--skip-check", action="store_true", help="не запускать итоговый doctor"
    )
    args = parser.parse_args()

    if sys.platform != "win32":
        raise SystemExit("Этот установщик предназначен для Windows")

    run(["py", "-3.12", "-m", "pip", "install", "--user", "uv"])
    XVIBE.parent.mkdir(parents=True, exist_ok=True)
    if not (XVIBE / ".git").is_dir():
        run(["git", "clone", XVIBE_URL, str(XVIBE)])

    sync = ["py", "-3.12", "-m", "uv", "sync", "--python", "3.12", "--frozen"]
    if not args.without_demo:
        sync.extend(["--extra", "demo"])
    run(sync, cwd=XVIBE)
    run(
        [
            "py",
            "-3.12",
            "-m",
            "uv",
            "pip",
            "install",
            "--python",
            str(VENV_PYTHON),
            "pip",
            "kokoro>=0.9.4",
            "misaki[en]",
            "rusvoice[accent,ui]",
            "deckrun-mcp",
            "mcp[cli]<2",
        ],
        cwd=XVIBE,
    )
    run([str(VENV_PYTHON), "-m", "spacy", "download", "en_core_web_sm"])

    if not args.skip_check:
        run([sys.executable, str(Path(__file__).with_name("local_voice.py")), "doctor"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
