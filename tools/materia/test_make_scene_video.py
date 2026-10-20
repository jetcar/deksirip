import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from make_scene_video import cue_start


class CueStartTests(unittest.TestCase):
    def test_skips_duplicate_cue_before_previous_scene(self) -> None:
        cues = [
            (10.0, "дома шуруп встретил"),
            (100.0, "мама позвонила"),
            (120.0, "дома шуруп встретил меня"),
        ]

        self.assertEqual(
            cue_start("дома шуруп встретил меня", cues, after=100.0),
            120.0,
        )


if __name__ == "__main__":
    unittest.main()
