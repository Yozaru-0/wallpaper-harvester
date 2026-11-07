#!/usr/bin/env python3
# main.py — 4K/5K/8K Wallpaper Harvester & Auto-Setter
# System Architect & Product Owner: 0x1998e40
# Code & Implementation: Google Gemini AI
# Zero external dependencies · Pure Python 3.8+ stdlib

import os
import sys
import re
import random
import argparse
from pathlib import Path
from typing import Optional

# Ensure Unicode / UTF-8 safe console handling on Windows (CP1251, CP866, CP437)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from config import (
    PRESETS,
    RESOLUTIONS,
    ASPECT_RATIOS,
    RATIO_ALIASES,
    COLOR_FILTERS,
    COLOR_ALIASES,
)
from harvester import (
    WallhavenClient,
    DownloadEngine,
    set_desktop_wallpaper,
    export_to_zip,
)

BANNER = r"""
  ██╗    ██╗ █████╗ ██╗     ██╗     ██████╗  █████╗ ██████╗ ███████╗██████╗ ███████╗
  ██║    ██║██╔══██╗██║     ██║     ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
  ██║ █╗ ██║███████║██║     ██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝███████╗
  ██║███╗██║██╔══██║██║     ██║     ██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗╚════██║
  ╚███╔███╔╝██║  ██║███████╗███████╗██║     ██║  ██║██║     ███████╗██║  ██║███████║
   ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝
       ATMOSPHERIC 4K/5K/8K WALLPAPER ENGINE · AUTO-SETTER · MULTI-THREADED
       System Architect & Product Owner: 0x1998e40
       Code & Implementation: Google Gemini AI
"""


def sanitize_slug(query: str, max_length: int = 64) -> str:
    """Sanitizes user query for safe directory and file creation on all OSes."""
    if not query:
        return "feed"
    # Replace whitespace and forbidden filesystem characters for Windows/Linux/macOS
    cleaned = re.sub(r'[\s<>:"/\\|?*\x00-\x1f]+', "_", query).strip(" ._")
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned[:max_length].rstrip(" ._")
    return cleaned.lower() or "feed"


def select_folder_gui() -> str:
    """Opens a native Windows folder chooser dialog."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select Destination Folder for Wallpapers")
        root.destroy()
        return folder
    except Exception:
        return ""


def interactive_menu():
    print(BANNER)
    print("=" * 72)
    print("  SELECT CURATED PRESET:")
    print("=" * 72)
    for key, p in PRESETS.items():
        print(f"  [{key}] {p['name']}")
        print(f"      -> {p['desc']}")
    print("=" * 72)

    choice = input("\nEnter choice [1-8] (default: 1): ").strip() or "1"

    if choice == "8" or choice.lower() == "custom":
        query = input("\nEnter search query or artist name (e.g. 'Makoto Shinkai', 'cyberpunk'): ").strip()
        print("\nSelect Content Category:")
        print("  [1] General / Real-world / CGI")
        print("  [2] Anime & Manga (Default)")
        print("  [3] All Categories")
        cat_choice = input("Enter choice [1-3] (default: 2): ").strip() or "2"
        cat_map = {"1": "100", "2": "010", "3": "111"}
        slug = sanitize_slug(query)
        preset = {
            "id": f"custom_{slug}",
            "name": f"Custom Search: {query or 'All'}",
            "desc": f"Custom search query '{query}'",
            "categories": cat_map.get(cat_choice, "010"),
            "queries": [query] if query else [""],
            "sorting": "favorites",
            "top_range": "all",
        }
    elif choice in PRESETS:
        preset = PRESETS[choice]
    else:
        # Check alias
        found = None
        for p in PRESETS.values():
            if p.get("alias") == choice.lower():
                found = p
                break
        preset = found or PRESETS["1"]

    print(f"\n[+] Active Preset: {preset['name']}")

    # Step 2: Aspect Ratio
    print("\n" + "-" * 45)
    print("Aspect Ratio Filter:")
    print("  [1] Standard (16:9, 16:10) - Default")
    print("  [2] Ultrawide (21:9)")
    print("  [3] Super Ultrawide (32:9)")
    print("  [4] Any Aspect Ratio")
    ratio_choice = input("Select aspect ratio [1-4] or alias (default: 1): ").strip() or "1"
    ratio_val = resolve_ratio(ratio_choice)
    print(f"[+] Ratio Filter: {ratio_val or 'Any'}")

    # Step 3: Color Filter
    print("\n" + "-" * 45)
    print("Color Filter (Wallhaven API Dominant Color):")
    for ck, cv in COLOR_FILTERS.items():
        print(f"  [{ck}] {cv['name']}")
    color_choice = input("Select color filter [1-7] or alias (default: 1): ").strip() or "1"
    color_val = resolve_color(color_choice)
    print(f"[+] Color Filter: {color_val or 'None'}")

    # Step 4: Resolution Floor
    print("\n" + "-" * 45)
    print("Resolution Floor (Minimum Baseline):")
    print("  [1] 4K (3840x2160) - Recommended")
    print("  [2] 5K (5120x2880)")
    print("  [3] 8K (7680x4320)")
    print("  [4] 2K (2560x1440)")
    res_input = input("Select resolution [1-4] (default: 1): ").strip() or "1"
    res_map = {"1": "4K", "2": "5K", "3": "8K", "4": "2K"}
    resolution_key = res_map.get(res_input, "4K")
    print(f"[+] Resolution Floor: {resolution_key} ({RESOLUTIONS[resolution_key]}+)")

    # Step 5: Wallpaper Count
    count_input = input("\nHow many wallpapers to harvest? (default: 25): ").strip()
    try:
        count = int(count_input) if count_input else 25
        if count < 1:
            count = 25
    except ValueError:
        count = 25

    # Step 6: Destination folder
    default_dir = Path.home() / "Pictures" / "Wallpapers" / preset["id"]
    print(f"\nDestination folder:")
    print(f"  Default: {default_dir}")
    print("  Type custom path, press [Enter] for default, or type 'G' to pick via Windows Dialog.")
    dir_input = input("Target folder: ").strip()

    if dir_input.upper() == "G":
        print("[*] Opening Windows folder picker...")
        gui_folder = select_folder_gui()
        dest_dir = Path(gui_folder) if gui_folder else default_dir
    elif dir_input:
        dest_dir = Path(dir_input)
    else:
        dest_dir = default_dir

    api_key = os.getenv("WALLHAVEN_API_KEY")

    # Run the harvest
    harvest_result = run_harvest(
        preset=preset,
        count=count,
        resolution_key=resolution_key,
        ratio=ratio_val,
        color=color_val,
        dest_dir=dest_dir,
        api_key=api_key,
    )

    if not harvest_result or not harvest_result.get("files"):
        return

    valid_files = harvest_result["files"]

    # Step 7: Export to ZIP prompt
    print("\n" + "-" * 55)
    zip_prompt = input("Pack downloaded wallpapers into a .zip archive? [y/N] (default: N): ").strip().lower()
    if zip_prompt == "y":
        zip_path = dest_dir.parent / f"{preset['id']}_wallpapers.zip"
        created_zip = export_to_zip(valid_files, zip_path)
        if created_zip:
            size_mb = created_zip.stat().st_size / (1024 * 1024)
            print(f"[✓] Successfully exported {len(valid_files)} wallpapers to ZIP:")
            print(f"    {created_zip} ({size_mb:.2f} MB)")

    # Step 8: Auto-set Wallpaper prompt
    print("\n" + "-" * 55)
    wall_prompt = input("Set one of downloaded wallpapers as your desktop background now? [y/N] (default: N): ").strip().lower()
    if wall_prompt == "y":
        if len(valid_files) == 1:
            chosen = valid_files[0]
        else:
            print(f"\nAvailable wallpapers in harvest (1 to {len(valid_files)}):")
            for idx, f in enumerate(valid_files[:10], start=1):
                print(f"  [{idx:2d}] {f.name}")
            if len(valid_files) > 10:
                print(f"  ... and {len(valid_files) - 10} more files.")
            pick_input = input(f"\nSelect wallpaper number [1-{len(valid_files)}], 'R' for random, or 'C' to cancel (default: 1): ").strip()
            if pick_input.upper() == "C":
                print("[*] Wallpaper auto-set cancelled.")
                return
            elif pick_input.upper() == "R":
                chosen = random.choice(valid_files)
            else:
                try:
                    idx = int(pick_input) - 1
                    if 0 <= idx < len(valid_files):
                        chosen = valid_files[idx]
                    else:
                        chosen = valid_files[0]
                except ValueError:
                    chosen = valid_files[0]

        print(f"[*] Setting desktop wallpaper: {chosen.name}...")
        ok = set_desktop_wallpaper(chosen)
        if ok:
            print(f"[✓] Desktop background successfully updated with:")
            print(f"    {chosen}")
        else:
            print("[!] Could not set desktop wallpaper. Check permissions or file format.")


def run_harvest(
    preset: dict,
    count: int,
    resolution_key: str,
    dest_dir: Path,
    ratio: Optional[str] = "16x9,16x10",
    color: Optional[str] = None,
    threads: int = 6,
    api_key: Optional[str] = None,
) -> Optional[dict]:
    print("\n" + "=" * 60)
    print("  WALLPAPER HARVEST DISPATCH")
    print(f"  System Architect: 0x1998e40")
    print(f"  Code Engine:      Google Gemini AI")
    print(f"  Active Preset:    {preset['name']}")
    print(f"  Resolution Floor: {resolution_key} ({RESOLUTIONS.get(resolution_key, '4K')}+)")
    print(f"  Aspect Ratio:     {ratio or 'Any'}")
    print(f"  Color Filter:     {color or 'Any'}")
    print(f"  Harvest Target:   {count} wallpapers")
    print(f"  Output Directory: {dest_dir.resolve()}")
    if api_key:
        masked = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
        print(f"  Wallhaven API:    Authenticated ({masked})")
    else:
        print("  Wallhaven API:    Public (Rate-limited, SFW only)")
    print("=" * 60)

    client = WallhavenClient(api_key=api_key)

    print("[*] Contacting Wallhaven API index and filtering atmospheric candidates...")

    def progress_cb(current, total):
        sys.stdout.write(f"\r[*] Indexed candidates: {current}/{total} verified items...")
        sys.stdout.flush()

    wallpapers = client.harvest_preset(
        preset=preset,
        target_count=count,
        resolution_key=resolution_key,
        ratios=ratio,
        color=color,
        progress_cb=progress_cb,
    )

    print()
    if not wallpapers:
        print("[!] No matching wallpapers found with current filters.")
        print("    Tip: Try relaxing the resolution floor, color filter, or search query.")
        return None

    print(f"[+] Soundings verified: {len(wallpapers)} master-grade wallpapers queued.")

    engine = DownloadEngine(max_workers=threads)
    return engine.run(wallpapers, dest_dir)


def resolve_ratio(user_ratio: Optional[str]) -> Optional[str]:
    """Resolves aspect ratio from digit choice, alias string, or explicit value."""
    if not user_ratio:
        return "16x9,16x10"
    low = user_ratio.lower().strip()
    if low in ASPECT_RATIOS:
        return ASPECT_RATIOS[low]["value"]
    if low in RATIO_ALIASES:
        return RATIO_ALIASES[low]
    for r in ASPECT_RATIOS.values():
        if low == r["id"] or low == r["name"].lower():
            return r["value"]
    return user_ratio


def resolve_color(user_color: Optional[str]) -> Optional[str]:
    """Resolves dominant color from digit choice, alias string, or 6-char hex."""
    if not user_color:
        return None
    raw = user_color.strip()
    if raw in COLOR_FILTERS:
        return COLOR_FILTERS[raw]["hex"]
    low = raw.lower().replace("#", "")
    if low in COLOR_ALIASES:
        return COLOR_ALIASES[low]
    for c in COLOR_FILTERS.values():
        if low == c["id"] or low == c["name"].lower() or (c["hex"] and low == c["hex"].lower()):
            return c["hex"]
    # If 6-character hex string was passed directly
    if len(low) == 6 and all(ch in "0123456789abcdef" for ch in low):
        return low
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Atmospheric 4K/5K/8K Wallpaper Engine & Auto-Setter · Architected by 0x1998e40, Coded by Google Gemini AI"
    )
    preset_choices = list(PRESETS.keys()) + [p["alias"] for p in PRESETS.values()]
    parser.add_argument(
        "--preset",
        "-p",
        choices=preset_choices,
        help="Curated preset number [1-8] or alias (e.g. 'cyberpunk', 'monochrome', 'vault', 'nature', 'skies', 'architecture', 'cosmic', 'custom')",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Custom search query, artist, or tags (e.g. 'WLOP', 'Makoto Shinkai', 'neon rain')",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=25,
        help="Number of wallpapers to download (default: 25)",
    )
    parser.add_argument(
        "--res",
        "-r",
        choices=["2K", "4K", "5K", "8K"],
        default="4K",
        help="Minimum resolution floor: 2K, 4K, 5K, or 8K (default: 4K)",
    )
    parser.add_argument(
        "--ratio",
        "-R",
        type=str,
        default="standard",
        help="Aspect ratio filter: 'standard' (16:9/16:10), 'ultrawide' (21:9), 'super_ultrawide' (32:9), or 'any' (default: standard)",
    )
    parser.add_argument(
        "--color",
        "-C",
        type=str,
        default=None,
        help="Color filter: 'any', 'monochrome' (000000), 'dracula' (660099), 'cyan' (00ffff), 'midnight' (0066cc), 'emerald' (009933), 'crimson' (cc0000), or 6-char hex",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=str,
        help="Destination directory path",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Open native Windows folder picker dialog",
    )
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=6,
        help="Parallel download workers (default: 6)",
    )
    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        default=os.getenv("WALLHAVEN_API_KEY"),
        help="Wallhaven API Key for higher rate limits and personal vault access",
    )
    parser.add_argument(
        "--zip",
        "-z",
        action="store_true",
        help="Pack downloaded wallpapers into a .zip archive upon completion",
    )
    parser.add_argument(
        "--set-wallpaper",
        "-w",
        action="store_true",
        help="Automatically set the first harvested wallpaper as Windows desktop background",
    )

    args = parser.parse_args()

    # If no flags passed, launch interactive CLI menu
    if len(sys.argv) == 1:
        interactive_menu()
        return

    # Validate numeric parameters
    if args.threads < 1:
        parser.error("--threads must be greater than or equal to 1")
    if args.count < 1:
        parser.error("--count must be greater than or equal to 1")

    # Map aliases to preset dict
    preset = None
    if args.preset:
        if args.preset in PRESETS:
            preset = PRESETS[args.preset]
        else:
            for p in PRESETS.values():
                if p["alias"] == args.preset.lower():
                    preset = p
                    break

    if args.query:
        slug = sanitize_slug(args.query)
        preset = {
            "id": f"custom_{slug}",
            "name": f"Custom: {args.query}",
            "desc": f"Custom query for '{args.query}'",
            "categories": "111",
            "queries": [args.query],
            "sorting": "favorites",
            "top_range": "all",
        }
    elif not preset:
        preset = PRESETS["1"]

    # Resolve aspect ratio and color
    ratio_val = resolve_ratio(args.ratio)
    color_val = resolve_color(args.color)

    # Determine destination folder
    if args.gui:
        folder = select_folder_gui()
        dest_dir = Path(folder) if folder else (Path.home() / "Pictures" / "Wallpapers" / preset["id"])
    elif args.out:
        dest_dir = Path(args.out)
    else:
        dest_dir = Path.home() / "Pictures" / "Wallpapers" / preset["id"]

    res = run_harvest(
        preset=preset,
        count=args.count,
        resolution_key=args.res,
        dest_dir=dest_dir,
        ratio=ratio_val,
        color=color_val,
        threads=args.threads,
        api_key=args.api_key,
    )

    if not res or not res.get("files"):
        return

    valid_files = res["files"]

    if args.zip:
        zip_path = dest_dir.parent / f"{preset['id']}_wallpapers.zip"
        created_zip = export_to_zip(valid_files, zip_path)
        if created_zip:
            print(f"[✓] Created ZIP archive: {created_zip}")

    if args.set_wallpaper:
        chosen = valid_files[0]
        print(f"[*] Setting desktop wallpaper: {chosen.name}...")
        ok = set_desktop_wallpaper(chosen)
        if ok:
            print(f"[✓] Desktop background updated successfully: {chosen}")


if __name__ == "__main__":
    main()
