# config.py — 4K/5K/8K Wallpaper Harvester configuration & curated presets
# System Architect & Product Owner: 0x1998e40
# Code & Implementation: Google Gemini AI

from typing import Dict, List, Any, Optional

# Resolution baselines (minimum pixel bounding box)
RESOLUTIONS: Dict[str, str] = {
    "2K": "2560x1440",
    "4K": "3840x2160",
    "5K": "5120x2880",
    "8K": "7680x4320",
}

# Aspect Ratio presets
ASPECT_RATIOS: Dict[str, Dict[str, Any]] = {
    "1": {
        "id": "standard",
        "name": "Standard (16:9, 16:10)",
        "value": "16x9,16x10",
        "desc": "Standard desktop monitors and laptops",
    },
    "2": {
        "id": "ultrawide",
        "name": "Ultrawide (21:9)",
        "value": "21x9",
        "desc": "Cinematic 21:9 panoramic curved displays",
    },
    "3": {
        "id": "super_ultrawide",
        "name": "Super Ultrawide (32:9)",
        "value": "32x9",
        "desc": "Dual-wide 32:9 extreme immersion panels",
    },
    "4": {
        "id": "any",
        "name": "Any Aspect Ratio",
        "value": None,
        "desc": "All aspect ratios without constraint",
    },
}

RATIO_ALIASES: Dict[str, Optional[str]] = {
    "standard": "16x9,16x10",
    "16:9": "16x9",
    "16x9": "16x9",
    "16:10": "16x10",
    "16x10": "16x10",
    "ultrawide": "21x9",
    "21:9": "21x9",
    "21x9": "21x9",
    "super": "32x9",
    "super_ultrawide": "32x9",
    "32:9": "32x9",
    "32x9": "32x9",
    "any": None,
    "all": None,
}

# Color palette filters for Wallhaven API
COLOR_FILTERS: Dict[str, Dict[str, Any]] = {
    "1": {
        "id": "any",
        "name": "Any Color",
        "hex": None,
        "desc": "No color filtering",
    },
    "2": {
        "id": "monochrome",
        "name": "Monochrome / B&W",
        "hex": "000000",
        "desc": "Pure black & white, grayscale contrast (000000)",
    },
    "3": {
        "id": "dracula",
        "name": "Dracula Purple",
        "hex": "660099",
        "desc": "Moody Dracula aesthetic purple (660099)",
    },
    "4": {
        "id": "cyan",
        "name": "Cyan / Neon",
        "hex": "00ffff",
        "desc": "Vibrant cyberpunk cyan & aqua (00ffff)",
    },
    "5": {
        "id": "midnight",
        "name": "Midnight Blue",
        "hex": "0066cc",
        "desc": "Deep twilight oceanic blue (0066cc)",
    },
    "6": {
        "id": "emerald",
        "name": "Emerald Green",
        "hex": "009933",
        "desc": "Lush forest & jade green (009933)",
    },
    "7": {
        "id": "crimson",
        "name": "Crimson Red",
        "hex": "cc0000",
        "desc": "Intense blood neon & crimson (cc0000)",
    },
}

COLOR_ALIASES: Dict[str, Optional[str]] = {
    "any": None,
    "none": None,
    "all": None,
    "monochrome": "000000",
    "bw": "000000",
    "black": "000000",
    "dracula": "660099",
    "purple": "660099",
    "violet": "660099",
    "cyan": "00ffff",
    "neon": "00ffff",
    "aqua": "00ffff",
    "midnight": "0066cc",
    "blue": "0066cc",
    "emerald": "009933",
    "green": "009933",
    "crimson": "cc0000",
    "red": "cc0000",
}

# Tags culled to avoid flat/low-effort wallpapers
TAG_BLACKLIST = {
    "simple background",
    "white background",
    "grey background",
    "black background",
    "pink background",
    "blue background",
    "meme",
    "sketchup",
    "lowres",
    "bad anatomy",
    "chibi",
}

# Expanded Curated Preset Profiles
PRESETS: Dict[str, Dict[str, Any]] = {
    "1": {
        "id": "cyberpunk_neon",
        "alias": "cyberpunk",
        "name": "Cyberpunk & Neon City",
        "desc": "Rainy skylines, cybernetic alleys, holographic billboards, neon noir reflections",
        "categories": "110",
        "queries": ["cyberpunk", "neon city", "cyberpunk street"],
        "sorting": "favorites",
        "top_range": "all",
    },
    "2": {
        "id": "monochrome_noir",
        "alias": "monochrome",
        "name": "Monochrome & Manga Noir",
        "desc": "High-contrast ink illustration, manga lineart, black & white silhouettes, dark shadow play",
        "categories": "010",
        "queries": ["manga", "monochrome", "ink", "noir"],
        "sorting": "favorites",
        "top_range": "all",
    },
    "3": {
        "id": "volumetric_masters",
        "alias": "vault",
        "name": "Volumetric Masterworks (WLOP & GUWEIZ)",
        "desc": "Atmospheric lighting, ethereal dusk embers, royal palace halls, katana rain noir",
        "categories": "111",
        "queries": ["wlop", "guweiz"],
        "sorting": "favorites",
        "top_range": "all",
    },
    "4": {
        "id": "emerald_nature",
        "alias": "nature",
        "name": "Primeval Forests & Emerald Nature",
        "desc": "Ancient mossy canopies, sunbeam-dappled groves, mountain tarns, thunderous waterfalls",
        "categories": "100",
        "queries": ["forest", "green nature", "waterfall", "moss trees"],
        "sorting": "favorites",
        "top_range": "all",
    },
    "5": {
        "id": "anime_skies",
        "alias": "skies",
        "name": "Anime Skies & Vast Horizons (Shinkai / Ghibli)",
        "desc": "Towering cumulus clouds, endless windy plains, twilight stars, nostalgic golden hour",
        "categories": "010",
        "queries": ["clouds", "sky landscape", "makoto shinkai", "sunset horizon"],
        "sorting": "favorites",
        "top_range": "all",
    },
    "6": {
        "id": "minimal_architecture",
        "alias": "architecture",
        "name": "Minimalist & Dark Clean Architecture",
        "desc": "Brutalist angles, dark concrete geometry, moody interior light, geometric symmetry",
        "categories": "100",
        "queries": ["architecture", "minimalist dark", "concrete brutalism", "modern interior"],
        "sorting": "favorites",
        "top_range": "all",
    },
    "7": {
        "id": "cosmic_vistas",
        "alias": "cosmic",
        "name": "Cosmic Vistas & Deep Space",
        "desc": "Nebulae rifts, celestial event horizons, ringed exoplanets, interstellar starlight",
        "categories": "100",
        "queries": ["space", "nebula", "galaxy", "deep space cosmos"],
        "sorting": "favorites",
        "top_range": "all",
    },
    "8": {
        "id": "custom_search",
        "alias": "custom",
        "name": "Custom Free Search",
        "desc": "User-defined query, artist, or tags with automated 4K/5K/8K filtering",
        "categories": "111",
        "queries": [""],
        "sorting": "favorites",
        "top_range": "all",
    },
}
