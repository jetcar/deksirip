"""Timing helpers for narrated TikTok videos."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from synthesize_audio import srt_time


@dataclass(frozen=True)
class Caption:
    start: float
    end: float
    text: str


def expand_sentence_cues(sentence_cues: list[dict]) -> list[dict]:
    """Approximate word timings when the voice service returns sentences only."""
    words: list[dict] = []
    for cue in sentence_cues:
        tokens = str(cue["text"]).split()
        weights = [max(1, len(token.strip(".,!?;:—–-"))) for token in tokens]
        total = sum(weights) or 1
        cursor = float(cue["start"])
        span = max(0.01, float(cue["end"]) - cursor)
        for token, weight in zip(tokens, weights):
            end = cursor + span * weight / total
            words.append({"start": cursor, "end": end, "text": token})
            cursor = end
    return words


def _balanced_groups(word_cues: list[dict], max_words: int) -> list[list[dict]]:
    count = ceil(len(word_cues) / max_words)
    size, extra = divmod(len(word_cues), count)
    groups: list[list[dict]] = []
    start = 0
    for index in range(count):
        end = start + size + (1 if index < extra else 0)
        groups.append(word_cues[start:end])
        start = end
    return groups


def make_captions(word_cues: list[dict], audio_seconds: float, max_words: int = 6) -> list[Caption]:
    if not word_cues:
        raise ValueError("Озвучка не вернула тайминги слов или предложений")
    groups = _balanced_groups(word_cues, max_words)

    captions: list[Caption] = []
    for index, group in enumerate(groups):
        cue_start = 0.0 if index == 0 else float(group[0]["start"])
        cue_end = float(groups[index + 1][0]["start"]) if index + 1 < len(groups) else audio_seconds
        captions.append(Caption(round(cue_start, 3), round(cue_end, 3), " ".join(str(cue["text"]) for cue in group)))
    validate_captions(captions, audio_seconds, max_words)
    return captions


def make_sentence_captions(sentence_cues: list[dict], audio_seconds: float, max_words: int = 6) -> list[Caption]:
    captions: list[Caption] = []
    for sentence_index, sentence in enumerate(sentence_cues):
        groups = _balanced_groups(expand_sentence_cues([sentence]), max_words)
        sentence_end = (
            float(sentence_cues[sentence_index + 1]["start"])
            if sentence_index + 1 < len(sentence_cues)
            else audio_seconds
        )
        for group_index, group in enumerate(groups):
            start = 0.0 if not captions else float(group[0]["start"])
            end = float(groups[group_index + 1][0]["start"]) if group_index + 1 < len(groups) else sentence_end
            captions.append(Caption(round(start, 3), round(end, 3), " ".join(str(cue["text"]) for cue in group)))
    validate_captions(captions, audio_seconds, max_words)
    return captions


def validate_captions(captions: list[Caption], audio_seconds: float, max_words: int = 6) -> None:
    if not captions:
        raise ValueError("Нет субтитров")
    for index, caption in enumerate(captions):
        if caption.start < 0 or caption.end <= caption.start:
            raise ValueError(f"Некорректный тайминг субтитра {index + 1}")
        if len(caption.text.split()) > max_words:
            raise ValueError(f"Субтитр {index + 1} длиннее {max_words} слов")
        if index and abs(caption.start - captions[index - 1].end) > 0.05:
            raise ValueError("Между субтитрами есть разрыв")
    if abs(captions[-1].end - audio_seconds) > 0.05:
        raise ValueError("Субтитры не покрывают озвучку целиком")


def srt_text(captions: list[Caption]) -> str:
    return "\n".join(
        f"{index}\n{srt_time(caption.start)} --> {srt_time(caption.end)}\n{caption.text}\n"
        for index, caption in enumerate(captions, start=1)
    )
