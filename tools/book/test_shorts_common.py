from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from shorts_common import LOOP_SECONDS, make_plan, require_current_validation


class ShortPlanTests(unittest.TestCase):
    def test_legacy_russian_text_becomes_timed_beats(self) -> None:
        plan = make_plan(
            {
                "title": "Почему после чумы запретили рост зарплат?",
                "text": (
                    "После чумы работников стало мало. Английский статут велел платить по старым ставкам.\n"
                    "Закон не смог отменить дефицит рабочих рук."
                ),
            },
            "ru",
        )
        self.assertEqual(plan.hook, "Почему после чумы запретили рост зарплат?")
        self.assertEqual(plan.scenes[-1].beat, "loop")
        self.assertEqual(plan.scenes[-1].seconds, LOOP_SECONDS)
        self.assertGreaterEqual(plan.seconds, 15)
        self.assertLessEqual(plan.seconds, 24)
        self.assertTrue(all(scene.seconds <= 3 for scene in plan.scenes[:-1]))

    def test_explicit_english_schema(self) -> None:
        plan = make_plan(
            {
                "title": "Why Did Grain Become Power?",
                "hook": "Grain changed who held power.",
                "fact": "Unlike wild food, grain could be stored for months.",
                "mechanism": "Stored food could be counted, guarded, and rationed.",
                "payoff": "Control the granary, and you could control the village.",
            },
            "en",
        )
        self.assertEqual({scene.beat for scene in plan.scenes}, {"hook", "fact", "mechanism", "payoff", "loop"})

    def test_long_english_sentence_splits_into_balanced_scenes(self) -> None:
        plan = make_plan(
            {
                "title": "Why Did Granaries Matter?",
                "hook": "Why did granaries matter?",
                "fact": "A granary protected the harvest from damp, rodents, and a hungry season.",
                "mechanism": "Stored grain could support specialists and shared labor.",
                "payoff": "The granary turned survival into organized power.",
            },
            "en",
        )
        fact_scenes = [scene.text for scene in plan.scenes if scene.beat == "fact"]
        self.assertGreaterEqual(len(fact_scenes), 2)
        self.assertTrue(all(len(text) <= 56 for text in fact_scenes))
        self.assertTrue(all(text.split()[0].lower() not in {"and", "but", "or"} for text in fact_scenes))

    def test_english_rejects_cyrillic(self) -> None:
        with self.assertRaisesRegex(ValueError, "кириллицу"):
            make_plan(
                {
                    "title": "Why grain?",
                    "hook": "Why grain?",
                    "fact": "Grain stored well.",
                    "mechanism": "Но storage created control.",
                    "payoff": "The granary became power.",
                },
                "en",
            )

    def test_extended_duration_requires_reason(self) -> None:
        item = {
            "title": "Почему это произошло?",
            "hook": "Почему это произошло?",
            "fact": "Первый конкретный факт объясняет ставку.",
            "mechanism": "Причина связывает решение с результатом.",
            "payoff": "Вывод меняет понимание исходного вопроса.",
            "seconds": 28,
        }
        with self.assertRaisesRegex(ValueError, "long_form_reason"):
            make_plan(item, "ru")
        item["long_form_reason"] = "Нужно сохранить точную цитату"
        self.assertAlmostEqual(make_plan(item, "ru").seconds, 28, places=1)

    def test_upload_validation_is_bound_to_exact_video(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            video = Path(folder) / "short.mp4"
            manifest = Path(folder) / "short.validation.json"
            video.write_bytes(b"approved video")
            manifest.write_text(
                json.dumps({"passed": True, "video_sha256": hashlib.sha256(video.read_bytes()).hexdigest()}),
                encoding="utf-8",
            )
            require_current_validation(video, manifest)
            video.write_bytes(b"changed video")
            with self.assertRaisesRegex(ValueError, "устарела"):
                require_current_validation(video, manifest)


if __name__ == "__main__":
    unittest.main()
