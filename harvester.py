# harvester.py — Engine core for Wallhaven scraping & parallel downloading
# System Architect & Product Owner: 0x1998e40
# Code & Implementation: Google Gemini AI
# Zero third-party dependencies required · Pure Python 3.8+ stdlib

import os
import sys
import time
import json
import zipfile
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Set, Optional, Callable, Union

from config import RESOLUTIONS, TAG_BLACKLIST

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WallpaperHarvester/2.0"


@dataclass
class Wallpaper:
    id: str
    resolution: str
    url: Optional[str]
    category: str


class WallhavenClient:
    BASE_URL = "https://wallhaven.cc/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key.strip() if api_key else None

    def _request(self, endpoint: str, params: Dict[str, str], max_retries: int = 3) -> Dict:
        import urllib.request
        import urllib.parse
        import urllib.error

        headers = {"User-Agent": USER_AGENT}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            params["apikey"] = self.api_key

        qs = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}/{endpoint}?{qs}"
        req = urllib.request.Request(url, headers=headers)

        backoff = 1.5
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status == 200:
                        raw = resp.read().decode("utf-8")
                        return json.loads(raw)
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    print(f"\n[!] Wallhaven API authentication failed (HTTP {e.code}). Check your API key.")
                    return {"data": []}
                elif e.code == 429:
                    # Rate limit exceeded — perform exponential sleep
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                elif attempt < max_retries - 1:
                    time.sleep(1.0)
                    continue
                else:
                    return {"data": []}
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(1.0)
                    continue
                return {"data": []}

        return {"data": []}

    def search_candidates(
        self,
        query: str = "",
        categories: str = "110",
        sorting: str = "favorites",
        top_range: str = "all",
        atleast: str = "3840x2160",
        ratios: Optional[str] = None,
        color: Optional[str] = None,
        page: int = 1,
    ) -> List[Wallpaper]:
        params = {
            "categories": categories,
            "purity": "100",  # SFW
            "sorting": sorting,
            "atleast": atleast,
            "page": str(page),
        }

        # Quality guard: exclude tags from TAG_BLACKLIST unless explicitly searched
        user_query = query.strip() if query else ""
        user_q_lower = user_query.lower()
        excluded_tags = []
        for tag in sorted(TAG_BLACKLIST):
            if tag.lower() not in user_q_lower:
                if " " in tag:
                    excluded_tags.append(f'-"{tag}"')
                else:
                    excluded_tags.append(f"-{tag}")

        combined_q = user_query
        if excluded_tags:
            exclusions_str = " ".join(excluded_tags)
            combined_q = f"{combined_q} {exclusions_str}".strip() if combined_q else exclusions_str

        if combined_q:
            params["q"] = combined_q
        if ratios:
            params["ratios"] = ratios
        if color:
            params["colors"] = color
        if sorting == "toplist" and top_range and top_range != "all":
            params["topRange"] = top_range

        res = self._request("search", params)
        data = res.get("data", [])
        results: List[Wallpaper] = []
        for d in data:
            results.append(
                Wallpaper(
                    id=d.get("id"),
                    resolution=d.get("resolution", "unknown"),
                    url=d.get("path"),
                    category=d.get("category", "general"),
                )
            )
        return results

    def harvest_preset(
        self,
        preset: Dict,
        target_count: int,
        resolution_key: str = "4K",
        ratios: Optional[str] = "16x9,16x10",
        color: Optional[str] = None,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ) -> List[Wallpaper]:
        atleast = RESOLUTIONS.get(resolution_key, RESOLUTIONS["4K"])
        categories = preset.get("categories", "110")
        queries = preset.get("queries", [""])
        sorting = preset.get("sorting", "favorites")
        top_range = preset.get("top_range", "all")

        seen_ids: Set[str] = set()
        collected: List[Wallpaper] = []
        per_query_target = max(1, target_count // len(queries)) if queries else target_count
        query_pages: Dict[str, int] = {q: 0 for q in queries}

        # Dynamic rate limit delay: authenticated requests allow faster bursts
        delay = 0.25 if self.api_key else 1.4

        # Primary pass across all configured preset queries
        for q in queries:
            if len(collected) >= target_count:
                break
            query_collected = 0
            while query_collected < per_query_target and len(collected) < target_count:
                query_pages[q] += 1
                if query_pages[q] > 15:
                    break
                batch = self.search_candidates(
                    query=q,
                    categories=categories,
                    sorting=sorting,
                    top_range=top_range,
                    atleast=atleast,
                    ratios=ratios,
                    color=color,
                    page=query_pages[q],
                )
                if not batch:
                    break
                for wp in batch:
                    if wp.id not in seen_ids:
                        seen_ids.add(wp.id)
                        collected.append(wp)
                        query_collected += 1
                        if progress_cb:
                            progress_cb(len(collected), target_count)
                        if len(collected) >= target_count:
                            break
                time.sleep(delay)

        # Fallback pass across primary queries if target count not yet reached
        # Continues seamlessly from query_pages without skipping pages 2, 3, 4
        while len(collected) < target_count and queries:
            advanced = False
            for q in queries:
                if len(collected) >= target_count:
                    break
                query_pages[q] += 1
                if query_pages[q] > 15:
                    continue
                batch = self.search_candidates(
                    query=q,
                    categories=categories,
                    sorting=sorting,
                    top_range=top_range,
                    atleast=atleast,
                    ratios=ratios,
                    color=color,
                    page=query_pages[q],
                )
                if batch:
                    advanced = True
                    for wp in batch:
                        if wp.id not in seen_ids:
                            seen_ids.add(wp.id)
                            collected.append(wp)
                            if progress_cb:
                                progress_cb(len(collected), target_count)
                            if len(collected) >= target_count:
                                break
                time.sleep(delay)
            if not advanced:
                break

        return collected


class DownloadEngine:
    def __init__(self, max_workers: int = 6):
        self.max_workers = max(1, max_workers)

    def _download_file(self, wp: Wallpaper, dest_dir: Path, index: int, total: int) -> Dict:
        import urllib.request
        import urllib.error

        if not wp or not wp.url:
            return {
                "id": getattr(wp, "id", "unknown"),
                "status": "error",
                "bytes": 0,
                "file": "unknown",
                "path": None,
                "error": "Wallpaper URL is empty or invalid",
            }

        try:
            ext = os.path.splitext(wp.url)[1] or ".jpg"
            filename = f"{index:03d}_{wp.id}_{wp.resolution}{ext}"
            dest_path = dest_dir / filename

            # Deduplication: check if already downloaded with valid size (> 100 KB)
            # Checks both direct destination path and any existing file matching wallpaper ID
            if dest_path.exists() and dest_path.stat().st_size > 100_000:
                return {
                    "id": wp.id,
                    "status": "skipped",
                    "bytes": dest_path.stat().st_size,
                    "file": filename,
                    "path": dest_path,
                }

            matching_existing = [
                f for f in dest_dir.glob(f"*_{wp.id}_*")
                if not f.name.endswith(".tmp") and f.suffix.lower() != ".tmp"
            ]
            for existing_f in matching_existing:
                if existing_f.is_file() and existing_f.suffix.lower() != ".tmp" and existing_f.stat().st_size > 100_000:
                    return {
                        "id": wp.id,
                        "status": "skipped",
                        "bytes": existing_f.stat().st_size,
                        "file": existing_f.name,
                        "path": existing_f,
                    }

            # Download using temporary file and chunked streaming with retries
            temp_path = dest_dir / f"{filename}.tmp"
            req = urllib.request.Request(wp.url, headers={"User-Agent": USER_AGENT})
            max_retries = 3
            last_err = None

            for attempt in range(max_retries):
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        total_downloaded = 0
                        with open(temp_path, "wb") as f:
                            while True:
                                chunk = resp.read(65536)
                                if not chunk:
                                    break
                                f.write(chunk)
                                total_downloaded += len(chunk)

                        if total_downloaded < 1000:
                            raise ValueError(f"Downloaded payload incomplete ({total_downloaded} bytes)")

                        # Atomic rename: temporary file replaced into destination
                        if temp_path.exists():
                            temp_path.replace(dest_path)

                        return {
                            "id": wp.id,
                            "status": "downloaded",
                            "bytes": total_downloaded,
                            "file": filename,
                            "path": dest_path,
                        }
                except Exception as e:
                    last_err = e
                    if temp_path.exists():
                        try:
                            temp_path.unlink()
                        except Exception:
                            pass
                    if attempt < max_retries - 1:
                        time.sleep(1.0 * (attempt + 1))

            return {
                "id": wp.id,
                "status": "error",
                "bytes": 0,
                "file": filename,
                "path": dest_path,
                "error": str(last_err),
            }
        except Exception as general_err:
            return {
                "id": getattr(wp, "id", "unknown"),
                "status": "error",
                "bytes": 0,
                "file": getattr(wp, "id", "unknown"),
                "path": None,
                "error": str(general_err),
            }

    def run(self, wallpapers: List[Wallpaper], dest_dir: Path) -> Dict:
        dest_dir.mkdir(parents=True, exist_ok=True)
        total = len(wallpapers)
        completed = 0
        total_bytes = 0
        downloaded = 0
        skipped = 0
        errors = 0
        valid_files: List[Path] = []

        print(f"\n[+] Launching multi-threaded download ({self.max_workers} threads) into:")
        print(f"    {dest_dir.resolve()}\n")

        start_time = time.time()

        # Ensure terminal handles encoding safely
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_wp = {
                executor.submit(self._download_file, wp, dest_dir, idx + 1, total): wp
                for idx, wp in enumerate(wallpapers)
            }

            for future in as_completed(future_to_wp):
                res = future.result()
                completed += 1
                total_bytes += res["bytes"]

                if res["status"] in ("downloaded", "skipped") and res.get("path"):
                    valid_files.append(res["path"])

                if res["status"] == "downloaded":
                    downloaded += 1
                elif res["status"] == "skipped":
                    skipped += 1
                else:
                    errors += 1

                percent = int((completed / total) * 100) if total else 100
                bar_len = 24
                filled = int(bar_len * (completed / total)) if total else bar_len
                bar = "=" * filled + "-" * (bar_len - filled)
                size_mb = total_bytes / (1024 * 1024)
                status_str = f"[{bar}] {percent:3d}% | {completed}/{total} | {size_mb:6.1f} MB | {res['status']}: {res['file'][:24]}"
                try:
                    # Pad line with spaces to overwrite previous status characters cleanly
                    sys.stdout.write(f"\r{status_str:<80}")
                    sys.stdout.flush()
                except Exception:
                    print(f"[{completed}/{total}] {res['status']}: {res['file']}")

        # Sort files by name so index order is preserved
        valid_files.sort(key=lambda p: p.name)

        elapsed = time.time() - start_time
        print("\n\n" + "=" * 60)
        print(f"  Harvest Complete in {elapsed:.1f}s")
        print(f"  Downloaded: {downloaded} files")
        print(f"  Skipped (already present): {skipped} files")
        if errors:
            print(f"  Errors: {errors} files")
        print(f"  Total Data: {total_bytes / (1024 * 1024):.2f} MB")
        print(f"  Destination: {dest_dir.resolve()}")
        print("=" * 60)

        return {
            "total": total,
            "downloaded": downloaded,
            "skipped": skipped,
            "errors": errors,
            "bytes": total_bytes,
            "dir": str(dest_dir.resolve()),
            "files": valid_files,
        }


def set_desktop_wallpaper(image_path: Union[str, Path]) -> bool:
    """Sets the specified image as Windows desktop background via Win32 API.
    Uses SystemParametersInfoW with SPI_SETDESKWALLPAPER (20) and update flags.
    """
    path = Path(image_path).resolve()
    if not path.is_file():
        print(f"\n[!] Wallpaper image file not found: {path}")
        return False

    if sys.platform != "win32":
        print(f"\n[!] Wallpaper auto-setter is only supported on Windows (detected {sys.platform}).")
        return False

    try:
        import ctypes
        # SPI_SETDESKWALLPAPER = 20 (0x0014)
        # SPIF_UPDATEINIFILE = 0x01, SPIF_SENDCHANGE = 0x02 -> 0x03
        result = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(path), 3)
        return bool(result)
    except Exception as e:
        print(f"\n[!] Failed to set desktop wallpaper: {e}")
        return False


def export_to_zip(image_files: List[Path], zip_path: Union[str, Path]) -> Optional[Path]:
    """Compresses the harvested wallpapers into a single clean ZIP archive."""
    target = Path(zip_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    valid_files = [f for f in image_files if f.is_file() and f.stat().st_size > 0]
    if not valid_files:
        print("\n[!] No valid image files available to package into ZIP.")
        return None

    try:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in valid_files:
                zf.write(f, arcname=f.name)
        return target
    except Exception as e:
        print(f"\n[!] Failed to create ZIP archive: {e}")
        return None
