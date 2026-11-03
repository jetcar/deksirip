from __future__ import annotations

import unittest

from tiktok_common import expand_sentence_cues, make_captions, make_sentence_captions, srt_text


class TikTokCaptionTests(unittest.TestCase):
    def test_balances_words_without_one_word_tail(self) -> None:
        words = [
            {"start": index * 0.4, "end": (index + 1) * 0.4, "text": f"word{index}"}
            for index in range(11)
        ]
        captions = make_captions(words, 4.4)
        self.assertEqual([len(caption.text.split()) for caption in captions], [6, 5])
        self.assertEqual(captions[0].start, 0)
        self.assertEqual(captions[-1].end, 4.4)

    def test_expands_sentence_timings_and_writes_srt(self) -> None:
        words = expand_sentence_cues([{"start": 1.0, "end": 3.0, "text": "Three short words."}])
        captions = make_captions(words, 3.0)
        rendered = srt_text(captions)
        self.assertIn("00:00:00,000 --> 00:00:03,000", rendered)
        self.assertIn("Three short words.", rendered)

    def test_sentence_captions_do_not_cross_sentence_boundaries(self) -> None:
        captions = make_sentence_captions(
            [
                {"start": 0.1, "end": 1.8, "text": "First sentence ends here."},
                {"start": 2.0, "end": 4.0, "text": "Second sentence stays separate."},
            ],
            4.0,
        )
        self.assertEqual([caption.text for caption in captions], ["First sentence ends here.", "Second sentence stays separate."])


if __name__ == "__main__":
    unittest.main()
