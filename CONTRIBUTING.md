# Contributing to Wallpaper Harvester 🌌

Thank you for your interest in contributing! This project is maintained with strict technical standards to ensure all wallpapers harvested meet the highest atmospheric and volumetric fidelity.

---

## 📜 Principles & Standards

1. **Resolution Baseline:**
   - All default presets enforce a strict baseline of **3840×2160 (4K)** or higher.
   - Presets targeting ultrawide (21:9) or super ultrawide (32:9) setups must maintain their proper ratio filters.

2. **Quality & Atmospheric Depth:**
   - Any new preset must include curated queries and tag filters that strip away flat/plain backgrounds, monochrome cutouts, and low-effort upscales.
   - Add forbidden tags to `TAG_BLACKLIST` in `config.py` if new artifact patterns emerge.

3. **Zero Dependency Core:**
   - The engine core must remain 100% runnable using only the **Python Standard Library** (Python 3.8+).
   - Auto-setting wallpapers uses native `ctypes` on Windows without third-party tools.
   - Exporting to ZIP utilizes Python's built-in `zipfile` module.

---

## 🛠️ How to Add a New Preset

To introduce a new curated preset, edit `config.py`:

```python
PRESETS["9"] = {
    "id": "your_preset_id",
    "alias": "your_alias",
    "name": "Your Preset Display Name",
    "desc": "Short description of the atmospheric aesthetic",
    "categories": "010",  # 100=General, 010=Anime, 110=General+Anime, 111=All
    "queries": ["tag1", "tag2"],
    "sorting": "favorites",  # 'favorites', 'toplist', 'hot'
    "top_range": "all",
}
```

---

## 🚀 Development Workflow

1. Fork the repository.
2. Create your feature branch:
   ```bash
   git checkout -b feature/new-preset
   ```
3. Test your changes locally:
   ```bash
   python main.py --preset your_preset_id --count 2 --res 4K
   ```
4. Commit your changes with clean, descriptive commit messages:
   ```bash
   git commit -m "Add Cyberpunk Mecha preset to config"
   ```
5. Push to your branch and open a Pull Request.

---

## ⚖️ Code of Conduct

All contributors and participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
