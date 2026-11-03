"""Local Russian and English narration pipeline.

Examples:
    python tools/book/local_voice.py doctor
    python tools/book/local_voice.py explain --text "Ст+арый з+амок закрыт на зам+ок."
    python tools/book/local_voice.py synthesize --text-file chapter.txt --output chapter.wav
    python tools/book/local_voice.py video --audio chapter.wav --image slide-1.png --output chapter.mp4
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
XVIBE = REPO / ".voice" / "xVibePocketTTS"
VENV_PYTHON = XVIBE / ".venv" / "Scripts" / "python.exe"
DECKRUN = XVIBE / ".venv" / "Scripts" / "deckrun-mcp.exe"


def media_tool(name: str) -> str | None:
    """Find FFmpeg tools even when the current process has a stale PATH."""
    found = shutil.which(name)
    if found:
        return found
    packages = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    for candidate in packages.glob(f"Gyan.FFmpeg*/*/bin/{name}.exe"):
        return str(candidate)
    return None


def stabilize_windows_platform() -> None:
    """Avoid a hanging platform._wmi_query() before importing PyTorch."""
    if sys.platform != "win32":
        return
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


def activate_environment() -> None:
    if not VENV_PYTHON.is_file():
        raise SystemExit("Окружение не найдено: python tools/book/setup_local_voice.py")
    if Path(sys.executable).resolve() != VENV_PYTHON.resolve():
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        raise SystemExit(
            subprocess.call(
                [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]],
                env=environment,
            )
        )


def input_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text.strip()
    text = args.text_file.read_text(encoding="utf-8").strip()
    return clean_markdown(text) if args.text_file.suffix.lower() == ".md" else text


def clean_markdown(text: str) -> str:
    result: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or re.match(r"^\s*\|?\s*:?-{3,}", line):
            continue
        if line.lstrip().startswith("|"):
            cells = [
                cell.strip()
                for cell in line.strip().strip("|").split("|")
                if cell.strip()
            ]
            line = "; ".join(cells) + ("." if cells else "")
        heading = re.match(r"^#{1,6}\s*(.+)$", line)
        if heading:
            title = heading.group(1).strip()
            line = title if title.endswith((".", "!", "?")) else title + "."
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = re.sub(r"^\s*>\s?", "", line)
        result.append(line)
    cleaned = "\n".join(result).replace("**", "").replace("*", "").replace("`", "")
    cleaned = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", cleaned)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def normalize_english_text(text: str) -> str:
    return text.translate(
        str.maketrans(
            {
                "“": '"',
                "”": '"',
                "‘": "'",
                "’": "'",
                "—": ", ",
                "–": "-",
                "…": "...",
                "\u00a0": " ",
            }
        )
    )


def split_tts_fragments(text: str, tokenizer, max_tokens: int = 40):
    def token_count(value: str) -> int:
        return int(tokenizer(value).tokens.shape[1])

    def split_sentence(sentence: str) -> list[str]:
        if token_count(sentence) <= max_tokens:
            return [sentence]
        remaining = sentence.split()
        result: list[str] = []
        while remaining:
            end = 1
            for candidate in range(1, len(remaining) + 1):
                if token_count(" ".join(remaining[:candidate])) > max_tokens - 1:
                    break
                end = candidate
            if end < len(remaining):
                for candidate in range(end, max(1, end - 8), -1):
                    if re.search(r"[,;:]$", remaining[candidate - 1]):
                        end = candidate
                        break
            fragment = " ".join(remaining[:end]).rstrip(" ,;:")
            remaining = remaining[end:]
            if remaining and not fragment.endswith((".", "!", "?")):
                fragment += "."
            result.append(fragment)
        return result

    fragments: list[tuple[str, float]] = []
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    for paragraph_index, paragraph in enumerate(paragraphs):
        normalized = re.sub(r"\s+", " ", paragraph)
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", normalized)
            if sentence.strip()
        ]
        for sentence_index, sentence in enumerate(sentences):
            pieces = split_sentence(sentence)
            for piece_index, piece in enumerate(pieces):
                last_piece = piece_index == len(pieces) - 1
                last_sentence = sentence_index == len(sentences) - 1
                last_paragraph = paragraph_index == len(paragraphs) - 1
                if last_piece and last_sentence and not last_paragraph:
                    pause = 0.35
                elif last_piece:
                    pause = 0.18
                else:
                    pause = 0.08
                fragments.append((piece, pause))
    return fragments


def trace_text(text: str):
    from rusvoice.layers import apply

    trace = apply(text, lang="ru", accent=True)
    if not trace.text:
        raise SystemExit("Пустой текст после подготовки")
    return trace


async def deckrun_check() -> tuple[list[str], int]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command=str(DECKRUN), args=[])
    async with (
        stdio_client(params) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        tools = [tool.name for tool in (await session.list_tools()).tools]
        result = await session.call_tool("get_slide_format", {})
        if getattr(result, "isError", False):
            raise RuntimeError("Deckrun get_slide_format вернул ошибку")
        text = "\n".join(
            item.text
            for item in result.content
            if getattr(item, "type", None) == "text"
        )
        if not text:
            raise RuntimeError("Deckrun get_slide_format вернул пустой ответ")
        return tools, len(text)


def command_doctor(args: argparse.Namespace) -> int:
    activate_environment()
    failures: list[str] = []

    trace = trace_text("Ст+арый з+амок закрыт на зам+ок.")
    if trace.warnings:
        failures.extend(trace.warnings)
    else:
        print(f"✓ RUAccent: {trace.text}")

    try:
        from xvibe_pocket_tts import RussianTTS  # noqa: F401

        print("✓ xVibePocketTTS: импортируется")
    except Exception as error:  # noqa: BLE001 - doctor must report arbitrary import failures
        failures.append(f"xVibePocketTTS: {error}")

    try:
        from kokoro import KPipeline  # noqa: F401

        print("✓ Kokoro: импортируется")
    except Exception as error:  # noqa: BLE001 - doctor must report arbitrary import failures
        failures.append(f"Kokoro: {error}")

    ffmpeg = media_tool("ffmpeg")
    if ffmpeg:
        print(f"✓ FFmpeg: {ffmpeg}")
    else:
        failures.append("FFmpeg не найден в PATH")

    if not args.skip_deckrun:
        try:
            tools, size = asyncio.run(deckrun_check())
            print(f"✓ Deckrun MCP: {', '.join(tools)}; get_slide_format={size} байт")
        except Exception as error:  # noqa: BLE001 - aggregate transport and server failures
            failures.append(f"Deckrun MCP: {error}")

    for failure in failures:
        print(f"✗ {failure}", file=sys.stderr)
    return 1 if failures else 0


def command_explain(args: argparse.Namespace) -> int:
    activate_environment()
    trace = trace_text(input_text(args))
    if args.json:
        print(
            json.dumps(
                {
                    "source": trace.source,
                    "text": trace.text,
                    "changes": [
                        {
                            "layer": change.layer,
                            "before": change.before,
                            "after": change.after,
                        }
                        for change in trace.changes
                    ],
                    "warnings": trace.warnings,
                    "skipped": trace.skipped,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"вход:  {trace.source}")
        print(f"выход: {trace.text}")
        for warning in trace.warnings:
            print(f"⚠️ {warning}")
    return 1 if trace.warnings else 0


def command_synthesize(args: argparse.Namespace) -> int:
    activate_environment()
    stabilize_windows_platform()
    source_text = input_text(args)
    if args.lang == "ru":
        trace = trace_text(source_text)
        if trace.warnings:
            for warning in trace.warnings:
                print(f"✗ {warning}", file=sys.stderr)
            return 1
        prepared_text = trace.text
    else:
        prepared_text = normalize_english_text(source_text)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    prepared = args.output.with_suffix(".prepared.txt")
    prepared.write_text(prepared_text + "\n", encoding="utf-8")

    import soundfile as sf
    import torch

    if args.lang == "en":
        from kokoro import KPipeline

        voice = args.voice or "af_heart"
        lang_code = "b" if voice.startswith("b") else "a"
        pipeline = KPipeline(lang_code=lang_code, device="cpu")
        audio_parts = []
        cues = []
        elapsed_samples = 0
        pause_samples = round(24_000 * args.pause)
        for index, result in enumerate(
            pipeline(
                prepared_text,
                voice=voice,
                speed=args.speed,
                split_pattern=r"\n+",
            ),
            start=1,
        ):
            if result.audio is None:
                continue
            part = result.audio.detach().float().cpu()
            timed_tokens = [
                token for token in (result.tokens or [])
                if token.start_ts is not None and token.end_ts is not None
            ]
            word_timings = [
                {"start": token.start_ts, "end": token.end_ts, "text": token.text}
                for token in timed_tokens
            ]
            if args.max_word_gap is not None and len(word_timings) > 1:
                cuts = []
                for previous, following in zip(word_timings, word_timings[1:]):
                    gap = following["start"] - previous["end"]
                    if gap > args.max_word_gap:
                        margin = args.max_word_gap / 2
                        cuts.append((previous["end"] + margin, following["start"] - margin))
                if cuts:
                    pieces = []
                    cursor = 0
                    for cut_start, cut_end in cuts:
                        start_sample = round(cut_start * 24_000)
                        end_sample = round(cut_end * 24_000)
                        pieces.append(part[cursor:start_sample])
                        cursor = end_sample
                    pieces.append(part[cursor:])
                    part = torch.cat(pieces)

                    def adjusted(timestamp: float) -> float:
                        removed = sum(
                            max(0.0, min(timestamp, cut_end) - cut_start)
                            for cut_start, cut_end in cuts
                        )
                        return timestamp - removed

                    word_timings = [
                        {
                            **word,
                            "start": adjusted(word["start"]),
                            "end": adjusted(word["end"]),
                        }
                        for word in word_timings
                    ]
            if args.max_silence is not None and len(part) > 1:
                active = torch.nonzero(part.abs() > 0.01, as_tuple=False).flatten()
                cuts = []
                keep_samples = round(args.max_silence * 24_000)
                for position in torch.nonzero(
                    active[1:] - active[:-1] > keep_samples,
                    as_tuple=False,
                ).flatten().tolist():
                    gap_start = int(active[position]) + 1
                    gap_end = int(active[position + 1])
                    remove = gap_end - gap_start - keep_samples
                    if remove > 0:
                        cut_start = gap_start + keep_samples // 2
                        cuts.append((cut_start / 24_000, (cut_start + remove) / 24_000))
                if cuts:
                    pieces = []
                    cursor = 0
                    for cut_start, cut_end in cuts:
                        start_sample = round(cut_start * 24_000)
                        end_sample = round(cut_end * 24_000)
                        pieces.append(part[cursor:start_sample])
                        cursor = end_sample
                    pieces.append(part[cursor:])
                    part = torch.cat(pieces)

                    def silence_adjusted(timestamp: float) -> float:
                        removed = sum(
                            max(0.0, min(timestamp, cut_end) - cut_start)
                            for cut_start, cut_end in cuts
                        )
                        return timestamp - removed

                    word_timings = [
                        {
                            **word,
                            "start": silence_adjusted(word["start"]),
                            "end": silence_adjusted(word["end"]),
                        }
                        for word in word_timings
                    ]
            trim_start = 0
            trim_end = len(part)
            if args.trim_silence and word_timings:
                active = torch.nonzero(part.abs() > 0.01, as_tuple=False).flatten()
                if len(active):
                    trim_start = max(0, int(active[0]) - round(0.02 * 24_000))
                    trim_end = min(len(part), int(active[-1]) + round(0.04 * 24_000))
                part = part[trim_start:trim_end]
            trim_offset = trim_start / 24_000
            trimmed_seconds = len(part) / 24_000
            start = elapsed_samples / 24_000
            elapsed_samples += len(part)
            cues.append(
                {
                    "start": start,
                    "end": elapsed_samples / 24_000,
                    "text": result.graphemes.strip(),
                    "sync_version": 2,
                    "max_word_gap": args.max_word_gap,
                    "max_silence": args.max_silence,
                    "words": [
                        {
                            "start": start + max(0.0, word["start"] - trim_offset),
                            "end": start + min(
                                trimmed_seconds,
                                max(0.0, word["end"] - trim_offset),
                            ),
                            "text": word["text"],
                        }
                        for word in word_timings
                    ],
                }
            )
            audio_parts.append(part)
            audio_parts.append(torch.zeros(pause_samples))
            elapsed_samples += pause_samples
            print(f"  фрагмент {index}", flush=True)
        if not audio_parts:
            raise SystemExit("Kokoro не создал аудио")
        audio = torch.cat(audio_parts[:-1])
        sample_rate = 24_000
        engine = f"Kokoro {voice}"
        if args.cues_output:
            args.cues_output.parent.mkdir(parents=True, exist_ok=True)
            args.cues_output.write_text(
                json.dumps(cues, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    else:
        from xvibe_pocket_tts import RussianTTS

        voice = args.voice or "male_deep"
        voice = Path(voice) if Path(voice).is_file() else voice
        tts = RussianTTS(
            device="cpu",
            temperature=args.temperature,
            eos_threshold=args.eos_threshold,
            auto_accent=False,
        )
        audio = tts.generate(
            prepared_text, voice=voice, auto_accent=False, seed=args.seed
        )
        sample_rate = tts.sample_rate
        engine = f"xVibe {voice}"
    sf.write(args.output, audio.numpy(), sample_rate)
    print(f"✓ {args.output} ({len(audio) / sample_rate:.2f} с; {engine})")
    print(f"✓ подготовленный текст: {prepared}")
    return 0


def audio_duration(path: Path) -> float:
    ffprobe = media_tool("ffprobe")
    if not ffprobe:
        raise SystemExit("ffprobe не найден в PATH")
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def command_video(args: argparse.Namespace) -> int:
    ffmpeg = media_tool("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg не найден в PATH")
    width, height = (int(value) for value in args.size.lower().split("x", maxsplit=1))
    duration = audio_duration(args.audio)
    segment = duration / len(args.image) + 0.1
    command = [ffmpeg, "-y", "-loglevel", "error"]
    for image in args.image:
        command.extend(
            ["-loop", "1", "-framerate", "30", "-t", f"{segment:.3f}", "-i", str(image)]
        )
    command.extend(["-i", str(args.audio)])

    filters = [
        f"[{index}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{index}]"
        for index in range(len(args.image))
    ]
    if len(args.image) == 1:
        video_label = "[v0]"
    else:
        joined = "".join(f"[v{index}]" for index in range(len(args.image)))
        filters.append(f"{joined}concat=n={len(args.image)}:v=1:a=0[vout]")
        video_label = "[vout]"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            video_label,
            "-map",
            f"{len(args.image)}:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(args.output),
        ]
    )
    subprocess.run(command, check=True)
    print(f"OK {args.output} ({duration:.2f} sec, {len(args.image)} slides)")
    return 0


def add_text_input(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--text-file", type=Path)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser(
        "doctor", help="проверить RUAccent, xVibe, FFmpeg и Deckrun"
    )
    doctor.add_argument(
        "--skip-deckrun", action="store_true", help="не обращаться к сети"
    )
    doctor.set_defaults(func=command_doctor)

    explain = commands.add_parser(
        "explain", help="показать подготовленный текст до синтеза"
    )
    add_text_input(explain)
    explain.add_argument("--json", action="store_true")
    explain.set_defaults(func=command_explain)

    synthesize = commands.add_parser(
        "synthesize", help="подготовить текст и создать WAV на CPU"
    )
    add_text_input(synthesize)
    synthesize.add_argument("--output", type=Path, required=True)
    synthesize.add_argument("--voice")
    synthesize.add_argument("--lang", choices=("ru", "en"), default="ru")
    synthesize.add_argument("--speed", type=float, default=0.96)
    synthesize.add_argument("--pause", type=float, default=0.22)
    synthesize.add_argument("--cues-output", type=Path)
    synthesize.add_argument("--trim-silence", action="store_true")
    synthesize.add_argument("--max-word-gap", type=float)
    synthesize.add_argument("--max-silence", type=float)
    synthesize.add_argument("--seed", type=int, default=42)
    synthesize.add_argument("--temperature", type=float, default=0.5)
    synthesize.add_argument("--eos-threshold", type=float, default=-1.0)
    synthesize.set_defaults(func=command_synthesize)

    video = commands.add_parser(
        "video", help="собрать MP4 из изображений и локальной озвучки"
    )
    video.add_argument("--audio", type=Path, required=True)
    video.add_argument("--image", type=Path, action="append", required=True)
    video.add_argument("--output", type=Path, required=True)
    video.add_argument("--size", default="1920x1080")
    video.set_defaults(func=command_video)
    return result


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
