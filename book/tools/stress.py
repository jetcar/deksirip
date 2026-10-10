"""Russian stress marks for TTS: RUAccent places them, pronunciation.txt overrides hard words.

The neural voice honours a combining acute accent (U+0301) after the stressed vowel.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

ACUTE = "́"
DICTIONARY = Path(__file__).resolve().parent / "pronunciation.txt"


def _patch_onnx() -> None:
    """RUAccent models expect token_type_ids, which newer tokenizers no longer return."""
    import numpy as np
    import onnxruntime as ort

    original = ort.InferenceSession.run
    if getattr(original, "_token_type_patch", False):
        return

    def run(self, output_names, input_feed, *args, **kwargs):
        names = {i.name for i in self.get_inputs()}
        if "token_type_ids" in names and "token_type_ids" not in input_feed:
            input_feed = {**input_feed, "token_type_ids": np.zeros_like(input_feed["input_ids"])}
        return original(self, output_names, input_feed, *args, **kwargs)

    run._token_type_patch = True
    ort.InferenceSession.run = run


@lru_cache(maxsize=1)
def _accentizer():
    _patch_onnx()
    from ruaccent import RUAccent

    model = RUAccent()
    model.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
    return model


@lru_cache(maxsize=1)
def _overrides() -> list[tuple[re.Pattern, str]]:
    """Lines like `Абу-Хур+ейра`: the word, any case, with '+' before its stressed vowel."""
    rules = []
    if DICTIONARY.exists():
        for line in DICTIONARY.read_text(encoding="utf-8").splitlines():
            entry = line.split("#", 1)[0].strip()
            if "+" not in entry:
                continue
            plain = entry.replace("+", "")
            # RUAccent may turn е into ё, so match either
            letters = r"\+?".join("[её]" if ch in "её" else re.escape(ch) for ch in plain.lower())
            rules.append((re.compile(rf"(?<![\w+]){letters}(?!\w)", re.IGNORECASE), entry))
    return rules


def _apply_overrides(text: str) -> str:
    for pattern, entry in _overrides():
        def keep_case(match: re.Match, entry: str = entry) -> str:
            found = iter(match.group(0).replace("+", ""))
            # the dictionary decides е/ё and stress, the text decides capitals
            return "".join(
                ch if ch == "+" else (ch.upper() if next(found).isupper() else ch.lower()) for ch in entry
            )
        text = pattern.sub(keep_case, text)
    return text


VOWELS = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")


def _drop_single_vowel_stress(match: re.Match) -> str:
    """Prepositions and other one-vowel words read better unmarked ("на холме", not "на́ холме")."""
    word = match.group(0)
    return word.replace("+", "") if sum(ch in VOWELS for ch in word) <= 1 else word


def accent(text: str) -> str:
    """Return text with U+0301 after each stressed vowel."""
    marked = "\n".join(_accentizer().process_all(line) if line.strip() else line for line in text.split("\n"))
    marked = _apply_overrides(marked)
    marked = re.sub(r"[\w+]+", _drop_single_vowel_stress, marked)
    return re.sub(r"\+(\w)", rf"\1{ACUTE}", marked)


def strip(text: str) -> str:
    return text.replace(ACUTE, "").replace("+", "")
