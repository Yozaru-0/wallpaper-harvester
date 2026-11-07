import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from harvester import (
    Wallpaper,
    WallhavenClient,
    DownloadEngine,
    set_desktop_wallpaper,
    export_to_zip,
)


class TestHarvester(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="wh_test_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_wallpaper_dataclass(self):
        wp = Wallpaper(id="abc123", resolution="3840x2160", url="https://example.com/art.jpg", category="anime")
        self.assertEqual(wp.id, "abc123")
        self.assertEqual(wp.resolution, "3840x2160")

    def test_wallhaven_client_api_key_header(self):
        client = WallhavenClient(api_key="TEST_API_KEY_123")
        self.assertEqual(client.api_key, "TEST_API_KEY_123")

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = b'{"data": []}'
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            res = client._request("search", {"q": "neon"})
            self.assertEqual(res, {"data": []})

            # Verify Request object created with headers
            self.assertTrue(mock_urlopen.called)
            req = mock_urlopen.call_args[0][0]
            self.assertEqual(req.headers.get("X-api-key"), "TEST_API_KEY_123")

    def test_search_candidates_tag_blacklist_query(self):
        client = WallhavenClient()
        with patch.object(client, "_request", return_value={"data": []}) as mock_request:
            client.search_candidates(query="cyberpunk", categories="110")
            mock_request.assert_called_once()
            call_params = mock_request.call_args[0][1]
            q_param = call_params.get("q", "")
            self.assertTrue(q_param.startswith("cyberpunk"))
            self.assertIn('-"simple background"', q_param)
            self.assertIn("-meme", q_param)

    def test_pagination_fallback_no_skipping_pages(self):
        """Verifies that fallback pagination in harvest_preset covers sequential pages without skipping 2, 3, 4."""
        client = WallhavenClient()
        requested_pages = []

        def mock_search_candidates(**kwargs):
            page = kwargs.get("page", 1)
            query = kwargs.get("query", "")
            requested_pages.append((query, page))
            # Return 1 unique wallpaper per page
            return [Wallpaper(id=f"{query}_{page}", resolution="3840x2160", url="http://x.com/a.jpg", category="general")]

        preset = {
            "id": "test_preset",
            "name": "Test Preset",
            "queries": ["q1", "q2"],
            "categories": "100",
            "sorting": "favorites",
            "top_range": "all",
        }

        with patch.object(client, "search_candidates", side_effect=mock_search_candidates), patch("time.sleep"):
            results = client.harvest_preset(preset=preset, target_count=5)
            self.assertEqual(len(results), 5)
            # Pages for q1 and q2 must start at 1, then proceed to 2, 3 without jumping to 5
            q1_pages = [page for (q, page) in requested_pages if q == "q1"]
            self.assertEqual(q1_pages, [1, 2, 3])

    def test_wallhaven_client_auth_failure_401(self):
        import urllib.error
        client = WallhavenClient(api_key="INVALID_KEY")
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test.com", code=401, msg="Unauthorized", hdrs={}, fp=None
            )
            res = client._request("search", {"q": "test"})
            self.assertEqual(res, {"data": []})
            # Verify it did not retry 3 times on 401
            self.assertEqual(mock_urlopen.call_count, 1)

    def test_download_file_null_url_safe(self):
        engine = DownloadEngine(max_workers=2)
        wp = Wallpaper(id="null_test", resolution="3840x2160", url=None, category="general")
        res = engine._download_file(wp, self.temp_dir, 1, 1)
        self.assertEqual(res["status"], "error")
        self.assertIn("empty or invalid", res["error"])

    def test_download_file_deduplication_by_id(self):
        engine = DownloadEngine(max_workers=2)
        # Create an existing file with matching ID and size > 100 KB
        dummy_file = self.temp_dir / "001_art123_3840x2160.jpg"
        dummy_file.write_bytes(b"A" * 105_000)

        # Also create a .tmp file that must NOT be treated as a valid existing file
        tmp_dummy = self.temp_dir / "002_art999_3840x2160.jpg.tmp"
        tmp_dummy.write_bytes(b"B" * 120_000)

        wp = Wallpaper(id="art123", resolution="3840x2160", url="http://example.com/art123.jpg", category="general")
        # Try downloading with a different index prefix 005
        res = engine._download_file(wp, self.temp_dir, 5, 10)
        self.assertEqual(res["status"], "skipped")
        self.assertEqual(res["file"], dummy_file.name)

        # Wallpaper with art999 should not be skipped because only .tmp exists, it will download
        wp999 = Wallpaper(id="art999", resolution="3840x2160", url="http://example.com/art999.jpg", category="general")
        with patch("urllib.request.urlopen") as mock_url:
            mock_resp = MagicMock()
            mock_resp.read.side_effect = [b"X" * 105_000, b""]
            mock_url.return_value.__enter__.return_value = mock_resp
            res999 = engine._download_file(wp999, self.temp_dir, 2, 10)
            self.assertEqual(res999["status"], "downloaded")
            self.assertEqual(res999["file"], "002_art999_3840x2160.jpg")

    def test_download_file_chunked_atomic_rename(self):
        engine = DownloadEngine(max_workers=2)
        wp = Wallpaper(id="stream123", resolution="3840x2160", url="http://example.com/stream.jpg", category="general")

        mock_payload = b"X" * 150_000
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.side_effect = [mock_payload[:65536], mock_payload[65536:], b""]
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            res = engine._download_file(wp, self.temp_dir, 1, 1)
            self.assertEqual(res["status"], "downloaded")
            self.assertEqual(res["bytes"], 150_000)
            self.assertTrue((self.temp_dir / "001_stream123_3840x2160.jpg").is_file())
            # Ensure temporary .tmp file is cleanly removed
            self.assertFalse((self.temp_dir / "001_stream123_3840x2160.jpg.tmp").exists())

    def test_export_to_zip_empty_list_returns_none(self):
        res = export_to_zip([], self.temp_dir / "empty.zip")
        self.assertIsNone(res)

    def test_export_to_zip_valid_files(self):
        f1 = self.temp_dir / "file1.jpg"
        f1.write_bytes(b"content1")
        f2 = self.temp_dir / "file2.jpg"
        f2.write_bytes(b"content2")

        zip_target = self.temp_dir / "output.zip"
        res = export_to_zip([f1, f2], zip_target)
        self.assertIsNotNone(res)
        self.assertTrue(zip_target.is_file())

    def test_set_desktop_wallpaper_non_existent_file(self):
        res = set_desktop_wallpaper(self.temp_dir / "does_not_exist.jpg")
        self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
