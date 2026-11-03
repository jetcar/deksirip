"""Build English Shorts using the hook → fact → mechanism → payoff scheme."""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from make_video import font
from shorts_common import (
    LOOP_SECONDS,
    MAX_SCENE_SECONDS,
    MIN_SCENE_SECONDS,
    Scene,
    ShortPlan,
    make_plan,
    render_timeline,
    write_validation_manifest,
)
from synthesize_audio import ROOT, duration, ffmpeg_tool, srt_time


SIZE = (1080, 1920)
MARGIN = 86
ACCENT = (229, 179, 86)
TEXT = (248, 245, 238)
MUTED = (205, 205, 205)
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLEH3118f0jFk"
MUSIC = ROOT / "shorts" / "music"
OUTPUT = ROOT / "shorts-en" / "out"
SLIDES = ROOT / "slides-en" / "00-intro"
BEAT_LABELS = {"hook": "THE QUESTION", "fact": "THE FACT", "mechanism": "WHY", "payoff": "THE POINT", "loop": ""}


SHORTS = [
    {
        "id": 1,
        "title": "Why Didn't the 15-Hour Workweek Arrive?",
        "image": "02-keynes-prediction.png",
        "text": (
            "Machines, energy, and knowledge now allow us to produce many times more "
            "in an hour than in Keynes's day.\n"
            "Yet the promised liberation never came.\n"
            "Where did the difference go?"
        ),
    },
    {
        "id": 2,
        "title": "What Actually Creates Wealth?",
        "image": "05-where-surplus-goes.png",
        "text": (
            "Wealth is created not by accumulation in itself, but by what the surplus "
            "is invested in.\n"
            "Tools, knowledge, and trust—\n"
            "or palaces, wars, and rents."
        ),
    },
    {
        "id": 3,
        "title": "When an Economy Runs but Goes Nowhere",
        "image": "10-wasteful.png",
        "text": (
            "Wasteful spending consumes resources without increasing productivity "
            "or the well-being of the majority.\n"
            "It is like an engine idling:\n"
            "fuel burns while the vehicle stands still."
        ),
    },
    {
        "id": 4,
        "title": "How Did the First Economy Work?",
        "image": "01-kalahari-band.png",
        "slide_folder": ROOT / "slides-en" / "01-hunter-gatherers",
        "banner": "THE FIRST ECONOMY",
        "chapter_title": "Chapter 1: Hunter-Gatherers",
        "text": (
            "No money. No bosses. No warehouses.\n"
            "And yet, there was an economy.\n"
            "People shared food—even with those who had gone nowhere that day.\n"
            "So how did they decide who got what?"
        ),
    },
    {
        "id": 5,
        "title": "More Food, Harder Lives?",
        "image": "02-grinding-grain.png",
        "slide_folder": ROOT / "slides-en" / "02-neolithic",
        "banner": "THE NEOLITHIC REVOLUTION",
        "chapter_title": "Chapter 2: The Neolithic Revolution",
        "cta_line1": "Tap Related Video for Chapter 2",
        "cta_line2": "Full audiobook playlist in description",
        "text": (
            "Agriculture made it possible to feed dozens of times more people from the same land.\n"
            "But at first, it brought not relief but harder work,\n"
            "a poorer and more monotonous diet, and new diseases.\n"
            "Who received the benefit of this new power?"
        ),
    },
    {
        "id": 6,
        "title": "Did Hunter-Gatherers Really Work Less?",
        "image": "06-gathering-food.png",
        "slide_folder": ROOT / "slides-en" / "01-hunter-gatherers",
        "banner": "THE FIRST ECONOMY",
        "chapter_title": "Chapter 1: Hunter-Gatherers",
        "text": (
            "Anthropologist Richard Lee expected to find a desperate struggle for survival.\n"
            "Instead, the Ju/’hoansi adults he studied spent two or three days a week getting food.\n"
            "The rest went to family, visits, conversation, dancing—and sleep.\n"
            "A striking finding, though one still debated by researchers."
        ),
    },
    {
        "id": 7,
        "title": "Why Share the Biggest Catch?",
        "image": "05-hunt-cooperation.png",
        "slide_folder": ROOT / "slides-en" / "01-hunter-gatherers",
        "banner": "A BANK WITHOUT MONEY",
        "chapter_title": "Chapter 1: Hunter-Gatherers",
        "text": (
            "A successful hunt could feed the whole camp—but meat spoiled quickly.\n"
            "Sharing today's surplus helped secure a share tomorrow, when luck ran out.\n"
            "No warehouse. No currency. Just a network of mutual obligations."
        ),
    },
    {
        "id": 8,
        "title": "The Hunter Wasn't the Boss",
        "image": "07-sharing-meal.png",
        "slide_folder": ROOT / "slides-en" / "01-hunter-gatherers",
        "banner": "SHARING AND POWER",
        "chapter_title": "Chapter 1: Hunter-Gatherers",
        "text": (
            "Among many hunter-gatherers, a large kill was shared by strict custom.\n"
            "The hunter could not simply keep it—or turn success into authority.\n"
            "Sharing was insurance, but also a way to stop wealth becoming power."
        ),
    },
    {
        "id": 9,
        "title": "Did Farming Make Life Harder?",
        "image": "02-grinding-grain.png",
        "slide_folder": ROOT / "slides-en" / "02-neolithic",
        "banner": "THE FARMING PARADOX",
        "chapter_title": "Chapter 2: The Neolithic Revolution",
        "cta_line1": "Tap Related Video for Chapter 2",
        "cta_line2": "Full audiobook playlist in description",
        "text": (
            "Early farming could feed far more people from the same land.\n"
            "But skeletons often show harder labor, narrower diets, and more disease.\n"
            "Agriculture expanded the population before it improved ordinary lives."
        ),
    },
    {
        "id": 10,
        "title": "Why Was Grain a Source of Power?",
        "image": "10-grain-and-power.png",
        "slide_folder": ROOT / "slides-en" / "02-neolithic",
        "banner": "GRAIN BECAME POWER",
        "chapter_title": "Chapter 2: The Neolithic Revolution",
        "cta_line1": "Tap Related Video for Chapter 2",
        "cta_line2": "Full audiobook playlist in description",
        "text": (
            "Wild food had to be eaten or shared quickly. Grain was different.\n"
            "It could be counted, stored, guarded, and distributed months later.\n"
            "The person who controlled the granary could begin to control everyone around it."
        ),
    },
    {
        "id": 11,
        "title": "Why Did Villages Build Granaries?",
        "image": "06-granary-storage.png",
        "slide_folder": ROOT / "slides-en" / "02-neolithic",
        "banner": "THE FIRST FOOD RESERVE",
        "chapter_title": "Chapter 2: The Neolithic Revolution",
        "cta_line1": "Tap Related Video for Chapter 2",
        "cta_line2": "Full audiobook playlist in description",
        "text": (
            "A granary protected the harvest from damp, rodents, and a hungry season.\n"
            "It also let a village coordinate seed, reserves, and shared labor.\n"
            "Storage reduced risk, but it created a new question: who controls the surplus?"
        ),
    },
    {
        "id": 12,
        "title": "The Bronze Age Needed Global Trade",
        "image": "01-bronze-was-not-local.png",
        "single_image": "single-meaningful.png",
        "slide_folder": ROOT / "shorts-en" / "storyboards" / "short-en-012",
        "scene_images": {
            "hook": "01-bronze-was-not-local.png",
            "fact": "02-copper-and-tin-ratio.png",
            "mechanism": "03-tin-traveled-far.png",
            "payoff": "04-bronze-age-supply-chain.png",
        },
        "screen_texts": {
            "hook": "BRONZE WASN'T LOCAL",
            "fact": "10 TONS COPPER / 1 TON TIN",
            "mechanism": "TIN TRAVELED 3,000+ KM",
            "payoff": "A BRONZE AGE SUPPLY CHAIN",
        },
        "chapter_title": "Chapter 4: Metals, Trade, and Money",
        "cta_line1": "Tap Related Video for Chapter 4",
        "local_voice": True,
        "subtitle_only": True,
        "hook": "Bronze looked local. It wasn't.",
        "fact": "One ship near Uluburun carried ten tons of copper and one ton of tin—the exact recipe for bronze.",
        "mechanism": "Some tin had traveled more than three thousand kilometers.",
        "payoff": "The Bronze Age ran on supply chains long before the phrase existed.",
    },
    {
        "id": 13,
        "title": "Why Did Iron Beat Better Bronze?",
        "image": "01-iron-looked-worse.png",
        "single_image": "single-meaningful.png",
        "slide_folder": ROOT / "shorts-en" / "storyboards" / "short-en-013",
        "scene_images": {
            "hook": "01-iron-looked-worse.png",
            "fact": "02-bronze-needed-tin.png",
            "mechanism": "03-iron-ore-everywhere.png",
            "payoff": "04-cheap-tools-spread.png",
        },
        "screen_texts": {
            "hook": "IRON WAS WORSE",
            "fact": "BRONZE NEEDED RARE TIN",
            "mechanism": "IRON ORE WAS EVERYWHERE",
            "payoff": "CHEAP TOOLS BEAT ELITE WEAPONS",
        },
        "chapter_title": "Chapter 4: Metals, Trade, and Money",
        "cta_line1": "Tap Related Video for Chapter 4",
        "local_voice": True,
        "subtitle_only": True,
        "hook": "Early iron was often worse than bronze.",
        "fact": "But bronze needed rare tin from distant trade routes, while iron ore was available almost everywhere.",
        "mechanism": "A cheaper tool that reaches thousands of farmers can change more lives",
        "payoff": "than a superior weapon locked in a palace arsenal.",
    },
    {
        "id": 14,
        "title": "The First Coins Hid a Tax",
        "image": "01-coin-hidden-profit.png",
        "single_image": "single-meaningful.png",
        "slide_folder": ROOT / "shorts-en" / "storyboards" / "short-en-014",
        "scene_images": {
            "hook": "01-coin-hidden-profit.png",
            "fact": "02-natural-electrum.png",
            "mechanism": "03-diluted-alloy.png",
            "payoff": "04-exchange-and-extraction.png",
        },
        "screen_texts": {
            "hook": "THE FIRST COINS HID A PROFIT",
            "fact": "NATURAL ELECTRUM: 70% GOLD",
            "mechanism": "COINS: ABOUT 55%",
            "payoff": "EASIER TRADE. EASIER EXTRACTION.",
        },
        "chapter_title": "Chapter 4: Metals, Trade, and Money",
        "cta_line1": "Tap Related Video for Chapter 4",
        "local_voice": True,
        "subtitle_only": True,
        "hook": "Coins made trade easier—but the first ones may have hidden a profit for the king.",
        "fact": "Natural Lydian electrum was about seventy percent gold.",
        "mechanism": "Early coins contained about fifty-five percent, yet circulated at full value.",
        "payoff": "Money lowered the cost of exchange—and of extraction.",
    },
]


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=face) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_scene_text(draw: ImageDraw.ImageDraw, text: str, width: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in (108, 98, 88, 78, 70, 62, 54):
        face = font("arialbd.ttf", size)
        lines = wrap(draw, text, face, width)
        if len(lines) <= 2:
            return face, lines
    raise ValueError(f"Text does not fit in two lines: {text!r}")


def fit_subtitle_text(draw: ImageDraw.ImageDraw, text: str, width: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in (78, 72, 66, 60, 54):
        face = font("arialbd.ttf", size)
        lines = wrap(draw, text, face, width)
        if len(lines) <= 2:
            return face, lines
    raise ValueError(f"Subtitle does not fit in two lines: {text!r}")


def background(path: Path, index: int, static: bool = False) -> Image.Image:
    source = Image.open(path).convert("RGB")
    centering = (0.5, 0.5) if static else ((0.34, 0.5) if index % 2 == 0 else (0.66, 0.5))
    sharp = ImageOps.fit(source, SIZE, method=Image.Resampling.LANCZOS, centering=centering)
    if not static and index % 3 == 2:
        sharp = ImageOps.mirror(sharp)
    return ImageEnhance.Contrast(sharp).enhance(1.08).convert("RGBA")


def scene_source(item: dict, scene: Scene) -> Path:
    beat = "hook" if scene.beat == "loop" else scene.beat
    image = item.get("single_image") or item.get("scene_images", {}).get(beat, item["image"])
    source = Path(item.get("slide_folder", SLIDES)) / image
    if not source.is_file():
        raise FileNotFoundError(f"Missing scene image: {source}")
    return source


def scene_frame(item: dict, plan: ShortPlan, scene: Scene, index: int, path: Path) -> None:
    source = scene_source(item, scene)
    base = background(source, index, static=bool(item.get("single_image")))
    draw = ImageDraw.Draw(base)

    shade = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(900, 1770):
        distance = abs(y - 1370) / 470
        alpha = int(115 * max(0.0, 1.0 - distance))
        shade_draw.line((0, y, SIZE[0], y), fill=(0, 0, 0, alpha))
    base.alpha_composite(shade)
    draw = ImageDraw.Draw(base)

    subtitle_only = bool(item.get("subtitle_only"))
    label = "" if subtitle_only else BEAT_LABELS[scene.beat]
    if label:
        draw.text((MARGIN, 220), label, font=font("arialbd.ttf", 42), fill=ACCENT)
        draw.rectangle((MARGIN, 290, MARGIN + 140 + index * 20, 298), fill=ACCENT)

    beat = "hook" if scene.beat == "loop" else scene.beat
    if subtitle_only:
        display_text = "" if scene.beat == "loop" else scene.text
    else:
        display_text = item.get("screen_texts", {}).get(beat, scene.text)
    if display_text:
        fitter = fit_subtitle_text if subtitle_only else fit_scene_text
        face, lines = fitter(draw, display_text, SIZE[0] - 2 * MARGIN - 42)
        step = int(face.size * 1.25)
        y = (1470 if subtitle_only else 1320) - (len(lines) - 1) * step // 2
        colour = TEXT if subtitle_only else (ACCENT if scene.beat in {"payoff", "loop"} else TEXT)
        for line in lines:
            draw.text((SIZE[0] / 2, y), line, font=face, fill=colour, anchor="mm", stroke_width=7,
                      stroke_fill=(0, 0, 0, 235))
            y += step

    if index and not subtitle_only:
        draw.text((MARGIN, 1535), item.get("chapter_title", "Where Did the Surplus Go?"),
                  font=font("arial.ttf", 34), fill=MUTED)
        draw.text((MARGIN, 1590), "Sele", font=font("arialbd.ttf", 38), fill=MUTED)
    if scene.beat == "payoff" and not subtitle_only:
        draw.text((MARGIN, 1690), item.get("cta_line1", "Watch the related chapter"),
                  font=font("arialbd.ttf", 38), fill=ACCENT)

    if not subtitle_only:
        dot_y = 1800
        for dot in range(len(plan.scenes)):
            colour_dot = ACCENT if dot == index else MUTED
            radius = 9 if dot == index else 6
            x = MARGIN + dot * 34
            draw.ellipse((x - radius, dot_y - radius, x + radius, dot_y + radius), fill=colour_dot)
    save_image(base.convert("RGB"), path, quality=95)


def storyboard(scene_paths: list[Path], target: Path) -> None:
    thumb_size = (270, 480)
    columns = 4
    rows = (len(scene_paths) + columns - 1) // columns
    sheet = Image.new("RGB", (thumb_size[0] * columns, thumb_size[1] * rows), (12, 12, 12))
    for index, path in enumerate(scene_paths):
        thumb = Image.open(path).convert("RGB").resize(thumb_size, Image.Resampling.LANCZOS)
        sheet.paste(thumb, ((index % columns) * thumb_size[0], (index // columns) * thumb_size[1]))
    save_image(sheet, target, quality=90)


def pick_track(seed: str) -> Path:
    tracks = sorted(MUSIC.glob("*.mp3"))
    if not tracks:
        raise SystemExit(f"No music found in {MUSIC}")
    return random.Random(seed).choice(tracks)


def metadata(item: dict, plan: ShortPlan) -> str:
    return "\n".join(
        [
            f"{plan.title} #Shorts"[:100],
            plan.body,
            "",
            f"Continue with {item.get('chapter_title', 'Where Did the Surplus Go?')}: {PLAYLIST_URL}",
            "Full audiobook playlist and related chapters are available on the channel.",
            "#EconomicHistory #Economics",
        ]
    ) + "\n"


def cleanup(scene_paths: list[Path]) -> None:
    folder = scene_paths[0].parent if scene_paths else None
    for path in scene_paths:
        path.unlink(missing_ok=True)
    if folder and folder.exists():
        folder.rmdir()


def save_image(image: Image.Image, destination: Path, **save_options) -> None:
    temporary = destination.with_name(f".{destination.stem}.tmp{destination.suffix}")
    temporary.unlink(missing_ok=True)
    image.save(temporary, **save_options)
    temporary.replace(destination)


def save_thumbnail(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        save_image(image, destination)


def narration(plan: ShortPlan) -> str:
    return " ".join((plan.hook, plan.fact, plan.mechanism, plan.payoff))


def synthesize_local_voice(text: str, audio: Path) -> tuple[Path, list[dict]]:
    script = audio.with_suffix(".narration.txt")
    cues_path = audio.with_suffix(".cues.json")
    if (
        audio.is_file()
        and script.is_file()
        and cues_path.is_file()
        and script.read_text(encoding="utf-8").strip() == text
    ):
        cues = json.loads(cues_path.read_text(encoding="utf-8"))
        if all(
            cue.get("words")
            and cue.get("sync_version") == 2
            and cue.get("max_word_gap") == 0.18
            and cue.get("max_silence") == 0.18
            for cue in cues
        ):
            return audio, cues
    script.write_text(text + "\n", encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("local_voice.py")),
            "synthesize",
            "--lang",
            "en",
            "--voice",
            "af_heart",
            "--speed",
            "0.96",
            "--pause",
            "0.02",
            "--trim-silence",
            "--max-word-gap",
            "0.18",
            "--max-silence",
            "0.18",
            "--text-file",
            str(script),
            "--output",
            str(audio),
            "--cues-output",
            str(cues_path),
        ],
        check=True,
    )
    return audio, json.loads(cues_path.read_text(encoding="utf-8"))


def token_text(words: list[dict]) -> str:
    text = " ".join(word["text"] for word in words)
    for punctuation in (".", ",", "!", "?", ";", ":", "%"):
        text = text.replace(f" {punctuation}", punctuation)
    for suffix in ("'s", "'t", "'re", "'ve", "'ll", "'d", "'m"):
        text = text.replace(f" {suffix}", suffix)
    return text.strip()


def split_cue(cue: dict) -> list[dict]:
    timeline_end = cue.get("timeline_end", cue["end"])
    if timeline_end - cue["start"] <= MAX_SCENE_SECONDS:
        return [{**cue, "text": token_text(cue.get("words", [])) or cue["text"]}]
    words = cue.get("words", [])
    candidates = []
    for index in range(1, len(words)):
        punctuation = words[index]["text"] in {".", ",", "!", "?", ";", ":", "%"}
        split_at = words[index]["start"]
        left = split_at - cue["start"]
        right = timeline_end - split_at
        if MIN_SCENE_SECONDS <= left <= MAX_SCENE_SECONDS and right >= MIN_SCENE_SECONDS:
            left_words = words[:index + 1] if punctuation else words[:index]
            right_words = words[index + 1:] if punctuation else words[index:]
            if left_words and right_words:
                candidates.append((abs(left - 2.25), split_at, left_words, right_words))
    if not candidates:
        raise ValueError(f"Cannot split synchronized cue: {cue['text']!r}")
    for _, split_at, left_words, right_words in sorted(candidates):
        left_cue = {
            "start": cue["start"],
            "end": split_at,
            "text": token_text(left_words),
            "words": left_words,
        }
        right_cue = {
            "start": split_at,
            "end": cue["end"],
            "timeline_end": timeline_end,
            "text": token_text(right_words),
            "words": right_words,
        }
        try:
            return [left_cue, *split_cue(right_cue)]
        except ValueError:
            continue
    raise ValueError(f"Cannot split synchronized cue: {cue['text']!r}")


def synchronized_plan(plan: ShortPlan, cues: list[dict]) -> tuple[ShortPlan, list[dict]]:
    if not cues:
        raise ValueError("Kokoro returned no synchronization cues")
    merged = {
        "start": cues[0]["start"],
        "end": cues[-1]["end"],
        "timeline_end": cues[-1]["end"],
        "text": " ".join(cue["text"] for cue in cues),
        "words": [word for cue in cues for word in cue.get("words", [])],
    }
    segments = split_cue(merged)
    beat_names = ("hook", "fact", "mechanism", "payoff")
    beat_texts = (plan.hook, plan.fact, plan.mechanism, plan.payoff)
    thresholds = []
    total = 0
    for text in beat_texts:
        total += len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))
        thresholds.append(total)
    expanded: list[tuple[Scene, dict]] = []
    consumed = 0
    for segment in segments:
        count = sum(word["text"].strip(".,!?;:%") != "" for word in segment.get("words", []))
        midpoint = consumed + count / 2
        beat_index = next(
            (index for index, threshold in enumerate(thresholds) if midpoint <= threshold),
            len(beat_names) - 1,
        )
        expanded.append((Scene(beat_names[beat_index], segment["text"], 0.0), segment))
        consumed += count
    scenes: list[Scene] = []
    synchronized_cues: list[dict] = []
    for index, (scene, cue) in enumerate(expanded):
        end = expanded[index + 1][1]["start"] if index + 1 < len(expanded) else cue["end"]
        scenes.append(Scene(scene.beat, cue["text"], round(end - cue["start"], 3)))
        synchronized_cues.append({**cue, "end": end})
    scenes.append(Scene("loop", "", LOOP_SECONDS))
    synchronized = ShortPlan(
        language=plan.language,
        title=plan.title,
        hook=plan.hook,
        fact=plan.fact,
        mechanism=plan.mechanism,
        payoff=plan.payoff,
        scenes=tuple(scenes),
        seconds=round(sum(scene.seconds for scene in scenes), 3),
        long_form_reason=plan.long_form_reason,
    )
    return synchronized, synchronized_cues


def write_srt(cues: list[dict], target: Path) -> None:
    blocks: list[str] = []
    for index, cue in enumerate(cues, start=1):
        blocks.append(
            f"{index}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{cue['text']}\n"
        )
    target.write_text("\n".join(blocks), encoding="utf-8")


def build(item: dict, preview_only: bool = False) -> Path:
    plan = make_plan(item, "en")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    stem = f"short-en-{item['id']:03}"
    voice = None
    if item.get("local_voice") and not preview_only:
        voice, cues = synthesize_local_voice(narration(plan), OUTPUT / f"{stem}-voice.wav")
        plan, cues = synchronized_plan(plan, cues)
        write_srt(cues, OUTPUT / f"{stem}.srt")
    scene_dir = OUTPUT / f".{stem}-scenes"
    scene_dir.mkdir(exist_ok=True)
    scene_paths = [scene_dir / f"scene-{index:02}.png" for index in range(len(plan.scenes))]
    for index, (scene, path) in enumerate(zip(plan.scenes, scene_paths)):
        scene_frame(item, plan, scene, index, path)

    thumbnail = OUTPUT / f"{stem}.png"
    save_thumbnail(scene_paths[0], thumbnail)
    preview = OUTPUT / f"{stem}-preview.jpg"
    storyboard(scene_paths, preview)
    meta = OUTPUT / f"{stem}.txt"
    meta.write_text(metadata(item, plan), encoding="utf-8")
    if preview_only:
        cleanup(scene_paths)
        print(preview)
        return preview

    track = pick_track(stem)
    video = OUTPUT / f"{stem}.mp4"
    track_length = duration(track)
    start = random.Random(stem).uniform(0, max(0.0, track_length - plan.seconds - 1))
    try:
        render_timeline(
            scene_paths,
            plan,
            track,
            video,
            ffmpeg_tool("ffmpeg"),
            music_start=start,
            voice=voice,
        )
        write_validation_manifest(
            OUTPUT / f"{stem}.validation.json", video, meta, plan, ffmpeg_tool("ffprobe")
        )
    finally:
        cleanup(scene_paths)
    print(video)
    return video


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", type=int, choices=[item["id"] for item in SHORTS])
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    selected = [item for item in SHORTS if args.id is None or item["id"] == args.id]
    for item in selected:
        plan = make_plan(item, "en")
        if args.validate_only:
            print(f"short-en-{item['id']:03}: {plan.seconds:.2f}s, {len(plan.scenes)} scenes")
        else:
            build(item, preview_only=args.preview_only)


if __name__ == "__main__":
    main()
