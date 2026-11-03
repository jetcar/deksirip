"""Animate approved TikTok storyboard frames with local ComfyUI LTX-Video."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from synthesize_audio import ROOT, ffmpeg_tool


NEGATIVE = (
    "low quality, worst quality, photorealistic, live action, flat 2D drawing, anime, "
    "text, letters, watermark, logo, gore, blood, exposed corpse, deformed face, "
    "bad anatomy, extra fingers, fused hands, duplicate people, flicker, jitter, "
    "camera shake, motion smear, melting objects"
)

PROMPTS = (
    "A polished stylized 3D animated medieval comedy in a vertical portrait frame. "
    "A tired young peasant worker in a green tunic stands in the foreground, blinking "
    "and looking uneasy. Behind him a wooden plague cart rolls slowly past with covered "
    "shapes under white cloth, no gore and nothing exposed. A light wind moves his tunic "
    "and the village banners. Slow camera push-in, expressive face, warm cinematic light, "
    "family-friendly 3D cartoon. Preserve the character, costume, layout and colors.",
    "A polished stylized 3D animated medieval comedy in a vertical portrait frame. "
    "The same young worker in a green tunic stands between two wealthy landowners, one in "
    "red and one in blue. Both angrily lean toward him, raise bags of coins, point and glare "
    "at each other while trying to outbid one another. The worker looks surprised, then "
    "quietly pleased. Subtle camera orbit, exaggerated facial expressions, family-friendly "
    "3D cartoon. Preserve the characters, costumes, layout and colors.",
    "A polished stylized 3D animated medieval comedy in a vertical portrait frame. "
    "The red and blue landowners now stand together before a stern royal official. They "
    "complain with dramatic hand gestures and point toward the worker visible in a doorway. "
    "The official listens, nods, then reaches for a quill beside a parchment and royal seal. "
    "There is no bribe and no money changes hands. Slow sideward camera move, expressive "
    "faces, family-friendly 3D cartoon. Preserve the composition and colors.",
    "A polished stylized 3D animated medieval comedy in a vertical portrait frame. "
    "The royal official proudly raises a new parchment law. Behind him the red and blue "
    "landowners still wave coin bags at the same worker in green. The worker gives a broad "
    "shrug, grins and takes a small step toward the camera while the official becomes "
    "confused. Comic timing, subtle camera pull-back, exaggerated emotions, family-friendly "
    "3D cartoon. Preserve the characters, composition and colors.",
)


def request_json(url: str, payload: dict | None = None, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def workflow(image: str, prompt: str, prefix: str, seed: int, checkpoint: str, encoder: str) -> dict:
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": encoder, "type": "ltxv", "device": "default"},
        },
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["2", 0]}},
        "5": {"class_type": "LoadImage", "inputs": {"image": image}},
        "6": {
            "class_type": "LTXVImgToVideo",
            "inputs": {
                "positive": ["3", 0], "negative": ["4", 0], "vae": ["1", 2],
                "image": ["5", 0], "width": 512, "height": 896, "length": 97,
                "batch_size": 1, "strength": 1.0,
            },
        },
        "7": {
            "class_type": "LTXVConditioning",
            "inputs": {"positive": ["6", 0], "negative": ["6", 1], "frame_rate": 24.0},
        },
        "8": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "9": {
            "class_type": "LTXVScheduler",
            "inputs": {
                "steps": 30, "max_shift": 2.05, "base_shift": 0.95,
                "stretch": True, "terminal": 0.1, "latent": ["6", 2],
            },
        },
        "10": {
            "class_type": "SamplerCustom",
            "inputs": {
                "model": ["1", 0], "add_noise": True, "noise_seed": seed, "cfg": 3.0,
                "positive": ["7", 0], "negative": ["7", 1], "sampler": ["8", 0],
                "sigmas": ["9", 0], "latent_image": ["6", 2],
            },
        },
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["1", 2]}},
        "12": {
            "class_type": "SaveWEBM",
            "inputs": {
                "images": ["11", 0], "filename_prefix": prefix,
                "codec": "vp9", "fps": 24.0, "crf": 20.0,
            },
        },
    }


def wait_for_completion(server: str, prompt_id: str, timeout: int = 3600) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        history = request_json(f"{server}/history/{prompt_id}")
        entry = history.get(prompt_id)
        if entry:
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status, ensure_ascii=False))
            if status.get("completed"):
                return entry
        time.sleep(3)
    raise TimeoutError(f"ComfyUI не завершил prompt {prompt_id} за {timeout} секунд")


def saved_webm(entry: dict, output_dir: Path, prefix: str) -> Path:
    for node in entry.get("outputs", {}).values():
        for value in node.values():
            if not isinstance(value, list):
                continue
            for item in value:
                if isinstance(item, dict) and str(item.get("filename", "")).endswith(".webm"):
                    return output_dir / item.get("subfolder", "") / item["filename"]
    matches = sorted(output_dir.glob(f"{prefix}_*.webm"), key=lambda path: path.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"ComfyUI не сохранил WEBM для {prefix}")
    return matches[-1]


def convert_to_mp4(source: Path, destination: Path) -> None:
    temporary = destination.with_name(f".{destination.stem}.tmp.mp4")
    temporary.unlink(missing_ok=True)
    try:
        subprocess.run(
            [
                ffmpeg_tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(source),
                "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(temporary),
            ],
            check=True,
        )
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path,
        default=ROOT / "shorts" / "out" / "tiktok" / "local-cartoon-ref",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=ROOT / "shorts" / "out" / "tiktok" / "short-044-cartoon-scenes",
    )
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--comfy-root", type=Path, default=Path(r"C:\AI\ComfyUI_windows_portable\ComfyUI"))
    parser.add_argument("--checkpoint", default="ltx-video-2b-v0.9.5.safetensors")
    parser.add_argument("--encoder", default="t5xxl_fp8_e4m3fn_scaled.safetensors")
    parser.add_argument("--start", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--limit", type=int, choices=range(1, 5))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    request_json(f"{args.server}/system_stats")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_folder = args.comfy_root / "input" / "deksirip" / "tiktok-044"
    input_folder.mkdir(parents=True, exist_ok=True)
    output_folder = args.comfy_root / "output"
    selected = list(range(args.start, 5))
    if args.limit:
        selected = selected[: args.limit]

    for index in selected:
        source = args.source_dir / f"scene-{index:02}_00001_.png"
        destination = args.output_dir / f"scene-{index:02}.mp4"
        if destination.exists() and not args.force:
            print(f"✓ {destination} (уже существует)", flush=True)
            continue
        if not source.is_file():
            raise FileNotFoundError(source)
        comfy_image = input_folder / source.name
        shutil.copy2(source, comfy_image)
        relative_image = comfy_image.relative_to(args.comfy_root / "input").as_posix()
        prefix = f"deksirip/tiktok-044/scene-{index:02}"
        prompt_id = request_json(
            f"{args.server}/prompt",
            {"prompt": workflow(relative_image, PROMPTS[index - 1], prefix, 135100 + index, args.checkpoint, args.encoder)},
        )["prompt_id"]
        print(f"… scene-{index:02}: {prompt_id}", flush=True)
        entry = wait_for_completion(args.server, prompt_id)
        source_video = saved_webm(entry, output_folder, f"scene-{index:02}")
        convert_to_mp4(source_video, destination)
        print(f"✓ {destination}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
