"""Start local ComfyUI while avoiding a known hanging Windows WMI query."""

from __future__ import annotations

import argparse
import faulthandler
import os
import platform
import runpy
import subprocess
import sys
from collections import namedtuple
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--comfy-root",
        type=Path,
        default=Path(r"C:\AI\ComfyUI_windows_portable"),
    )
    parser.add_argument("--port", type=int, default=8188)
    args = parser.parse_args()

    entrypoint = args.comfy_root / "ComfyUI" / "main.py"
    embedded_python = args.comfy_root / "python_embeded" / "python.exe"
    if not entrypoint.is_file():
        raise SystemExit(f"ComfyUI не найден: {entrypoint}")
    if not embedded_python.is_file():
        raise SystemExit(f"Встроенный Python ComfyUI не найден: {embedded_python}")
    if Path(sys.executable).resolve() != embedded_python.resolve():
        return subprocess.call(
            [
                str(embedded_python),
                "-s",
                str(Path(__file__).resolve()),
                "--comfy-root",
                str(args.comfy_root),
                "--port",
                str(args.port),
            ],
            cwd=args.comfy_root,
        )

    # Python 3.13 can hang in platform._wmi_query() on some Windows systems.
    # PyTorch only needs these stable values while loading its DLLs.
    uname_result = namedtuple(
        "uname_result", "system node release version machine processor"
    )
    fixed_uname = uname_result(
        "Windows", "localhost", "10", "10.0", "AMD64", "AMD64"
    )
    platform.uname = lambda: fixed_uname
    platform.machine = lambda: "AMD64"
    platform.system = lambda: "Windows"
    platform.release = lambda: "10"
    platform.version = lambda: "10.0"
    platform.processor = lambda: "AMD64"
    platform.node = lambda: "localhost"
    platform.win32_ver = lambda: ("10", "10.0", "", "")

    os.chdir(args.comfy_root)
    sys.path.insert(0, str(entrypoint.parent))
    faulthandler.dump_traceback_later(30, repeat=True)
    sys.argv = [
        str(entrypoint),
        "--windows-standalone-build",
        "--disable-auto-launch",
        "--offline",
        "--port",
        str(args.port),
    ]
    runpy.run_path(str(entrypoint), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
