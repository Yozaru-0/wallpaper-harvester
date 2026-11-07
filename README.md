# 🌌 Wallpaper Harvester

> **Universal 4K / 5K / 8K Wallpaper Engine & Windows Desktop Auto-Setter**  
> *Zero External Dependencies · Pure Python 3.8+ · Multi-Threaded · Wallhaven API Curator*

<div align="center">

[![Architect: 0x1998e400](https://img.shields.io/badge/Architect-0x1998e400-BD93F9?style=flat-square&logo=github)](https://github.com/Yozaru-0)
[![Code Engine: Google Gemini AI](https://img.shields.io/badge/Code%20Engine-Google%20Gemini%20AI%20%E2%9C%94-8E44AD?style=flat-square&logo=google)](https://gemini.google.com)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-50fa7b?style=flat-square&logo=python&logoColor=282a36)](https://www.python.org/)
[![Theme: Dracula](https://img.shields.io/badge/Theme-Dracula-282A36?style=flat-square&logo=visualstudiocode&logoColor=BD93F9)](https://draculatheme.com)
[![Resolution: 4K | 5K | 8K](https://img.shields.io/badge/Resolution-4K%20%7C%205K%20%7C%208K-ff79c6?style=flat-square)]()
[![Dependencies: Zero (Stdlib)](https://img.shields.io/badge/Dependencies-0%20(Stdlib)-8be9fd?style=flat-square)]()
[![Platform: Windows (Full) | Linux / macOS (Harvest & ZIP)](https://img.shields.io/badge/Platform-Windows%20(Full)%20%7C%20Linux%20%7C%20macOS-ffb86c?style=flat-square)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-f1fa8c?style=flat-square)](LICENSE)

</div>

---

## 🧭 Overview

Most wallpaper downloaders harvest compressed, flat images filled with artifacts and plain backgrounds. 

**Wallpaper Harvester** is a high-performance desktop engine built to curate and download master-grade, deeply atmospheric digital art. Conceived and architected by **[0x1998e40](https://github.com/0x1998e40)** and coded with **Google Gemini AI**, it queries the Wallhaven API, enforces strict resolution floors (up to 8K), filters by dominant color and aspect ratio, downloads images concurrently over a multi-worker pool, exports packs to ZIP, and sets backgrounds with a single keystroke.

---

## ⚡ Core Features

- **🛡️ Built-in Quality Guard:** Automatically culls low-effort upscales, flat backgrounds, and non-atmospheric artifacts using query-level tag blacklisting (`TAG_BLACKLIST`).
- **🖼️ Auto-Set Windows Wallpaper:** Directly applies downloaded wallpapers to your Windows desktop using the native Win32 `SystemParametersInfoW` API (`--set-wallpaper` or interactive prompt). *(Note: Harvesting and ZIP packaging work across Windows, Linux, and macOS; wallpaper auto-setting is Windows-specific).*
- **📦 Instant ZIP Export:** Packages harvested wallpaper sets into clean, compressed `.zip` archives with a single command (`--zip`).
- **🎨 Color Palette Filters:** Filter wallpapers by Wallhaven dominant colors:
  - **Monochrome / B&W** (`000000`)
  - **Dracula Purple** (`660099`)
  - **Cyan / Neon** (`00ffff`)
  - **Midnight Blue** (`0066cc`)
  - **Emerald Green** (`009933`)
  - **Crimson Red** (`cc0000`)
  - **Any / Unfiltered**
- **📐 Aspect Ratio Presets:**
  - **Standard** (16:9, 16:10) — Laptops and standard desktop monitors
  - **Ultrawide** (21:9) — Panoramic curved panels
  - **Super Ultrawide** (32:9) — Dual-wide setups
  - **Any** — Unconstrained ratios
- **⚡ Parallel Download Engine:** Multi-worker thread pool (default 6 workers), chunked streaming to temporary `.tmp` files with atomic replace, ID-based deduplication, and exponential backoff retry.
- **🔑 Wallhaven API Key Support:** Pass `--api-key` or set `WALLHAVEN_API_KEY` for higher rate limits and personal vault access.
- **🪟 Windows Terminal Hardened:** Safe Unicode / UTF-8 encoding reconfiguration for CP1251, CP866, and CP437 consoles.
- **☕ Zero Third-Party Dependencies:** 100% pure Python standard library. No `pip install` required.

---

## 🎨 Curated Presets

| # | Preset | Description |
|---|---|---|
| **1** | **Cyberpunk & Neon City** | Rainy skylines, cybernetic alleys, holographic billboards, neon noir reflections |
| **2** | **Monochrome & Manga Noir** | High-contrast ink illustration, manga lineart, black & white silhouettes, dark shadow play |
| **3** | **Volumetric Masterworks** | Atmospheric lighting, ethereal dusk embers, royal palace halls, katana rain noir (**WLOP** & **GUWEIZ**) |
| **4** | **Primeval Forests & Emerald Nature** | Ancient mossy canopies, sunbeam-dappled groves, mountain tarns, thunderous waterfalls |
| **5** | **Anime Skies & Vast Horizons** | Towering cumulus clouds, endless windy plains, twilight stars, **Makoto Shinkai** / Ghibli golden hour |
| **6** | **Minimalist & Dark Clean Architecture** | Brutalist angles, dark concrete geometry, moody interior light, geometric symmetry |
| **7** | **Cosmic Vistas & Deep Space** | Nebulae rifts, celestial event horizons, ringed exoplanets, interstellar starlight |
| **8** | **Custom Free Search** | User-defined query, artist, or tags with automated 4K/5K/8K filtering |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Yozaru-0/wallpaper-harvester.git
cd wallpaper-harvester
```

### 2. Run Interactively
```bash
python main.py
```
Launches the interactive guide:
1. Select curated preset (1–8) or type custom search.
2. Select aspect ratio (Standard 16:9, Ultrawide 21:9, Super Ultrawide 32:9, Any).
3. Select color palette filter (Monochrome, Dracula Purple, Cyan, Midnight Blue, Emerald, Crimson).
4. Select resolution baseline (4K, 5K, 8K, 2K).
5. Choose wallpaper count and destination folder (or press `G` to open Windows folder dialog).
6. Post-harvest: Prompt to package into `.zip` and auto-set desktop background.

---

## 🛠️ CLI Reference

All features can be driven via command-line flags for scripting, cron tasks, or terminal shortcuts:

```bash
# 1. Harvest 25 Cyberpunk wallpapers in 4K, export to ZIP, and set first as desktop wallpaper
python main.py --preset cyberpunk --count 25 --res 4K --zip --set-wallpaper

# 2. Harvest 15 Monochrome / Manga Noir wallpapers in 4K for Ultrawide 21:9 displays
python main.py --preset monochrome --count 15 --res 4K --ratio ultrawide

# 3. Harvest 20 Masterworks (WLOP & GUWEIZ) with Dracula Purple dominant color
python main.py --preset vault --count 20 --res 4K --color dracula

# 4. Search for an artist in 5K resolution and pick folder using native Windows GUI
python main.py --query "Makoto Shinkai" --count 10 --res 5K --gui

# 5. Harvest 30 Emerald Nature wallpapers into a custom directory
python main.py --preset nature --count 30 --res 4K --out "D:\Wallpapers\Nature"

# 6. Harvest using personal Wallhaven API key
python main.py --preset cyberpunk --count 10 --api-key "YOUR_KEY_HERE"
```

### Flags & Options

| Flag | Short | Description | Default |
|---|---|---|---|
| `--preset` | `-p` | Curated preset number `[1-8]` or alias (`cyberpunk`, `monochrome`, `vault`, `nature`, `skies`, `architecture`, `cosmic`, `custom`) | `1` |
| `--query` | `-q` | Custom artist name, query, or tags | None |
| `--count` | `-c` | Number of wallpapers to harvest | `25` |
| `--res` | `-r` | Resolution floor (`2K`, `4K`, `5K`, `8K`) | `4K` |
| `--ratio` | `-R` | Aspect ratio (`standard`, `ultrawide`, `super_ultrawide`, `any`, or menu index `1-4`) | `standard` |
| `--color` | `-C` | Dominant color filter (`any`, `monochrome`, `dracula`, `cyan`, `midnight`, `emerald`, `crimson`, 6-char hex, or index `1-7`) | `None` |
| `--out` | `-o` | Target directory for wallpapers | `~/Pictures/Wallpapers/<preset>` |
| `--gui` | | Open native Windows folder selector dialog | `False` |
| `--threads` | `-t` | Number of concurrent download worker threads | `6` |
| `--api-key` | `-k` | Wallhaven API key (or set `WALLHAVEN_API_KEY` env var) | `None` |
| `--zip` | `-z` | Package downloaded wallpapers into a `.zip` archive upon completion | `False` |
| `--set-wallpaper` | `-w` | Automatically set the first harvested wallpaper as Windows desktop background | `False` |

---

## 📂 Project Structure

```
wallpaper-harvester/
├── config.py           # Presets, color filters, aspect ratio maps, tag blacklists
├── harvester.py        # Wallhaven API client, parallel worker pool, Win32 auto-setter, ZIP engine
├── main.py             # CLI parser & interactive menu engine
├── requirements.txt    # Zero-dependency notice (100% Python Standard Library)
├── tests/              # Regression test suite (100% Python unittest stdlib)
├── .gitignore          # Caches, virtual environments, downloaded images, zip archives
├── LICENSE             # MIT License
├── AUTHORS.md          # Project authors and verified contributors
├── CODE_OF_CONDUCT.md  # Contributor Covenant 2.1 standard
├── CONTRIBUTING.md     # Development & preset contribution guide
├── SECURITY.md         # Security policy & reporting
└── README.md           # Documentation
```

---

## 👥 Authors & Attribution

* **System Architect & Product Owner:** [0x1998e400](https://github.com/Yozaru-0)
* **Code & Implementation Engine:** [Google Gemini AI](https://gemini.google.com) ✔ *(Verified AI Co-Author)*

---

## 📜 License

Distributed under the [MIT License](LICENSE). Open-source, free for personal and commercial use.
