"""Animate one approved keyframe with local Wan 2.2 5B.

Example:
    python tools/book/animate_wan22.py --image book/shorts/out/tiktok/short-045-keyframes/scene-01-gifts.png --output book/shorts/out/tiktok/short-045-wan22-scene-01.mp4
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from animate_tiktok_scenes import (
    convert_to_mp4,
    request_json,
    saved_webm,
    wait_for_completion,
)


ROOT = Path(__file__).resolve().parents[2]
COMFY_ROOT = Path(r"C:\AI\ComfyUI_windows_portable\ComfyUI")

DEFAULT_PROMPT = (
    "Stylized cinematic 3D cartoon, late fifteenth-century Calicut royal court. "
    "Vasco da Gama presents modest European gifts: folded cloth, hats, metal washbasins, "
    "coral, sugar and honey. He opens both hands and speaks with hopeful confidence. "
    "The Indian courtiers exchange amused glances and begin to smile. Cloth edges and "
    "hanging decorations move gently in a warm sea breeze. Subtle natural body motion, "
    "expressive faces, slow stable camera push-in. Preserve the exact characters, faces, "
    "costumes, composition and colors of the source image."
)

NEGATIVE_PROMPT = (
    "static image, frozen pose, camera shake, fast camera motion, morphing, melting, "
    "warped face, changing identity, changing costume, duplicate people, extra limbs, "
    "bad hands, flicker, jitter, motion smear, text, letters, watermark, photorealistic, "
    "live action, flat 2D illustration, anime, low quality, oversaturated"
)


def workflow(
    image: str,
    prompt: str,
    prefix: str,
    seed: int,
    width: int,
    height: int,
    length: int,
    fps: float,
    steps: int,
    denoise: float,
) -> dict:
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "wan2.2_ti2v_5B_fp16.safetensors",
                "weight_dtype": "default",
            },
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "wan",
                "device": "default",
            },
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "wan2.2_vae.safetensors"},
        },
        "4": {
            "class_type": "LoadImage",
            "inputs": {"image": image},
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["2", 0]},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": NEGATIVE_PROMPT, "clip": ["2", 0]},
        },
        "7": {
            "class_type": "Wan22ImageToVideoLatent",
            "inputs": {
                "vae": ["3", 0],
                "start_image": ["4", 0],
                "width": width,
                "height": height,
                "length": length,
                "batch_size": 1,
            },
        },
        "8": {
            "class_type": "ModelSamplingSD3",
            "inputs": {"model": ["1", 0], "shift": 8.0},
        },
        "9": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["8", 0],
                "seed": seed,
                "steps": steps,
                "cfg": 5.0,
                "sampler_name": "uni_pc",
                "scheduler": "simple",
                "positive": ["5", 0],
                "negative": ["6", 0],
                "latent_image": ["7", 0],
                "denoise": denoise,
            },
        },
        "10": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["9", 0], "vae": ["3", 0]},
        },
        "11": {
            "class_type": "SaveWEBM",
            "inputs": {
                "images": ["10", 0],
                "filename_prefix": prefix,
                "codec": "vp9",
                "fps": fps,
                "crf": 20.0,
            },
        },
    }


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--comfy-root", type=Path, default=COMFY_ROOT)
    parser.add_argument("--seed", type=int, default=14980501)
    parser.add_argument("--width", type=int, default=480)
    parser.add_argument("--height", type=int, default=832)
    parser.add_argument("--length", type=int, default=49)
    parser.add_argument("--fps", type=float, default=16.0)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--denoise", type=float, default=1.0)
    args = parser.parse_args()

    source = args.image.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if args.width % 32 or args.height % 32 or (args.length - 1) % 4:
        raise ValueError("width/height must be multiples of 32; length must be 1 + 4n")
    if not 0.0 < args.denoise <= 1.0:
        raise ValueError("denoise must be greater than 0 and no more than 1")

    request_json(f"{args.server}/system_stats")
    input_folder = args.comfy_root / "input" / "deksirip" / "wan22"
    input_folder.mkdir(parents=True, exist_ok=True)
    comfy_image = input_folder / source.name
    shutil.copy2(source, comfy_image)
    relative_image = comfy_image.relative_to(args.comfy_root / "input").as_posix()

    destination = args.output.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    prefix = f"deksirip/wan22/{destination.stem}"
    prompt_id = request_json(
        f"{args.server}/prompt",
        {
            "prompt": workflow(
                relative_image,
                args.prompt,
                prefix,
                args.seed,
                args.width,
                args.height,
                args.length,
                args.fps,
                args.steps,
                args.denoise,
            )
        },
    )["prompt_id"]
    print(f"Wan 2.2 prompt: {prompt_id}", flush=True)
    entry = wait_for_completion(args.server, prompt_id, timeout=7200)
    source_video = saved_webm(entry, args.comfy_root / "output", destination.stem)
    convert_to_mp4(source_video, destination)
    print(destination, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
