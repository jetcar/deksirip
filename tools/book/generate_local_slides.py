"""Generate 16:9 slideshow images with a local ComfyUI server."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


NEGATIVE = (
    "text, letters, typography, watermark, logo, caption, poster, infographic, "
    "low resolution, blurry, distorted hands, extra fingers, duplicate people, "
    "cartoon, anime, oversaturated"
)


def request_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def workflow(
    prompt: str,
    prefix: str,
    seed: int,
    checkpoint: str,
    width: int = 1216,
    height: int = 704,
) -> dict:
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 28,
                "cfg": 5.5,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": checkpoint},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": NEGATIVE, "clip": ["4", 1]},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": prefix, "images": ["8", 0]},
        },
    }


def wait_for_image(server: str, prompt_id: str) -> dict:
    while True:
        history = request_json(f"{server}/history/{prompt_id}")
        entry = history.get(prompt_id)
        if entry:
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status, ensure_ascii=False))
            images = entry.get("outputs", {}).get("9", {}).get("images", [])
            if images:
                return images[0]
        time.sleep(2)


def download_image(server: str, image: dict, destination: Path) -> None:
    query = urllib.parse.urlencode(
        {
            "filename": image["filename"],
            "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        }
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with (
        urllib.request.urlopen(f"{server}/view?{query}", timeout=60) as response,
        destination.open("wb") as output,
    ):
        output.write(response.read())


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--checkpoint", default="RealVisXL_V5.0_fp16.safetensors")
    parser.add_argument("--size", default="1216x704")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    width, height = (int(value) for value in args.size.lower().split("x", maxsplit=1))

    request_json(f"{args.server}/system_stats")
    slides = json.loads(args.plan.read_text(encoding="utf-8"))
    if args.limit is not None:
        slides = slides[: args.limit]

    for index, slide in enumerate(slides, start=1):
        destination = args.output_dir / f"{slide['id']}.png"
        if destination.exists() and not args.force:
            print(f"✓ {destination} (уже существует)")
            continue
        prefix = f"deksirip/{args.plan.stem}/{slide['id']}"
        payload = {
            "prompt": workflow(
                slide["prompt"],
                prefix,
                int(slide.get("seed", 4300 + index)),
                args.checkpoint,
                width,
                height,
            )
        }
        prompt_id = request_json(f"{args.server}/prompt", payload)["prompt_id"]
        image = wait_for_image(args.server, prompt_id)
        download_image(args.server, image, destination)
        print(f"✓ {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
