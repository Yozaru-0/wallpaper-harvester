import unittest
import sys
from pathlib import Path

# Ensure root project directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import (
    RESOLUTIONS,
    ASPECT_RATIOS,
    RATIO_ALIASES,
    COLOR_FILTERS,
    COLOR_ALIASES,
    TAG_BLACKLIST,
    PRESETS,
)


class TestConfig(unittest.TestCase):
    def test_resolutions_structure(self):
        self.assertIn("4K", RESOLUTIONS)
        self.assertEqual(RESOLUTIONS["4K"], "3840x2160")
        for key, val in RESOLUTIONS.items():
            self.assertRegex(val, r"^\d+x\d+$")

    def test_presets_api_compliance(self):
        """Ensures that no preset uses invalid API combinations like sorting=toplist and top_range=all."""
        valid_top_ranges = {"1d", "3d", "1w", "1M", "3M", "6M", "1y"}
        for pid, preset in PRESETS.items():
            self.assertIn("id", preset)
            self.assertIn("name", preset)
            self.assertIn("queries", preset)
            self.assertIn("categories", preset)
            self.assertIn("sorting", preset)

            if preset.get("sorting") == "toplist":
                self.assertIn(
                    preset.get("top_range"),
                    valid_top_ranges,
                    f"Preset {pid} has invalid top_range '{preset.get('top_range')}' for toplist sorting",
                )

    def test_tag_blacklist_not_empty(self):
        self.assertGreater(len(TAG_BLACKLIST), 0)
        self.assertIn("simple background", TAG_BLACKLIST)


if __name__ == "__main__":
    unittest.main()
