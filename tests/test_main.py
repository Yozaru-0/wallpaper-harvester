import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import sanitize_slug, resolve_ratio, resolve_color


class TestMainHelpers(unittest.TestCase):
    def test_sanitize_slug_windows_forbidden_chars(self):
        """Validates that colons, slashes, and wildcards are safely stripped."""
        cases = [
            ("re:zero", "custom_re_zero"),
            ("artist:wlop", "custom_artist_wlop"),
            ("fate/stay night", "custom_fate_stay_night"),
            ("nier:automata *4k*", "custom_nier_automata_4k"),
            ("test<script>|?*", "custom_test_script"),
            ("", "custom_feed"),
            ("   ", "custom_feed"),
            ("___", "custom_feed"),
            ("a" * 100, "custom_" + "a" * 64),
        ]
        for query, expected_slug in cases:
            slug = sanitize_slug(query)
            self.assertEqual(
                f"custom_{slug}",
                expected_slug,
                f"Failed for query '{query}': got 'custom_{slug}', expected '{expected_slug}'",
            )
            # Verify no forbidden Windows filename characters remain
            for forbidden in '<>:"/\\|?*':
                self.assertNotIn(forbidden, slug)

    def test_resolve_ratio(self):
        self.assertEqual(resolve_ratio(None), "16x9,16x10")
        self.assertEqual(resolve_ratio(""), "16x9,16x10")
        # Digit inputs
        self.assertEqual(resolve_ratio("1"), "16x9,16x10")
        self.assertEqual(resolve_ratio("2"), "21x9")
        self.assertEqual(resolve_ratio("3"), "32x9")
        self.assertIsNone(resolve_ratio("4"))
        # Alias inputs
        self.assertEqual(resolve_ratio("ultrawide"), "21x9")
        self.assertEqual(resolve_ratio("21:9"), "21x9")
        self.assertIsNone(resolve_ratio("any"))

    def test_resolve_color(self):
        self.assertIsNone(resolve_color(None))
        self.assertIsNone(resolve_color(""))
        # Digit inputs
        self.assertIsNone(resolve_color("1"))  # Any color
        self.assertEqual(resolve_color("2"), "000000")  # Monochrome
        self.assertEqual(resolve_color("3"), "660099")  # Dracula
        self.assertEqual(resolve_color("4"), "00ffff")  # Cyan
        # Alias inputs
        self.assertEqual(resolve_color("dracula"), "660099")
        self.assertEqual(resolve_color("cyan"), "00ffff")
        self.assertEqual(resolve_color("monochrome"), "000000")
        # Direct hex input
        self.assertEqual(resolve_color("#ff00aa"), "ff00aa")
        self.assertEqual(resolve_color("123456"), "123456")
        self.assertIsNone(resolve_color("invalid_color_value"))


    def test_cli_argument_bounds(self):
        import subprocess
        # Test threads < 1
        res = subprocess.run(
            [sys.executable, str(ROOT_DIR / "main.py"), "--preset", "1", "--threads", "0"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("--threads must be greater than or equal to 1", res.stderr)

        # Test count < 1
        res = subprocess.run(
            [sys.executable, str(ROOT_DIR / "main.py"), "--preset", "1", "--count", "0"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("--count must be greater than or equal to 1", res.stderr)


if __name__ == "__main__":
    unittest.main()
