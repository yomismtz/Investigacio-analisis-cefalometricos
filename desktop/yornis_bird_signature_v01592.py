from __future__ import annotations

import sys
import threading
from pathlib import Path

import yornis_startup_audio_v0159 as startup_audio

AUDIO_VERSION = "0.16.3-original-recordings"
SAMPLE_RATE = 44100
VOLUME_LEVELS = (20, 35, 50, 70, 90)

# Exact user-uploaded source recordings stored in desktop/assets.
# The build converts them to offline PCM WAV variants for Windows playback.
BIRD_AUDIO_FILES = {
    "Agaporni": "agaporni.mp3",
    "Tucán": "tucan.mp3",
    "Pavorreal": "pavo real.mp3",
    "Ninfa": "ninfa.mp3",
    "Faisán": "faisan.mp3",
    "Quetzal": "quetzal.mp3",
    "Guacamaya Roja": "guacamaya roja.mp3",
    "Guacamaya Azul": "guacamayo azul.mp3",
    "Búho": "buho real.mp3",
    "Colibrí": "colibri.mp3",
}


def _safe_name(theme_name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in theme_name)


def asset_root() -> Path:
    """Assets root in source mode and in the PyInstaller bundle."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return root / "assets"


def source_audio_path(theme_name: str) -> Path:
    """Return the original MP3 path stored in the repository."""
    filename = BIRD_AUDIO_FILES.get(theme_name)
    if filename is None:
        raise KeyError(f"Unknown Yornis bird palette: {theme_name}")
    return asset_root() / filename


def bundled_signature_path(theme_name: str, volume: int | None = None) -> Path:
    """Full uploaded recording converted to a volume-specific offline WAV."""
    if theme_name not in BIRD_AUDIO_FILES:
        raise KeyError(f"Unknown Yornis bird palette: {theme_name}")
    if volume is None:
        _, volume = startup_audio.settings()
    volume = max(0, min(100, int(volume)))
    return asset_root() / "bird_audio" / f"{_safe_name(theme_name)}_{volume}.wav"


def bundled_startup_path(theme_name: str, volume: int | None = None) -> Path:
    """Short high-energy excerpt for launch sound and the preview button."""
    if theme_name not in BIRD_AUDIO_FILES:
        raise KeyError(f"Unknown Yornis bird palette: {theme_name}")
    if volume is None:
        _, volume = startup_audio.settings()
    volume = max(0, min(100, int(volume)))
    return asset_root() / "bird_startup_audio" / f"{_safe_name(theme_name)}_{volume}.wav"


def _play(theme_name: str, volume: int) -> None:
    try:
        import winsound
        path = bundled_signature_path(theme_name, volume)
        if not path.is_file():
            return
        winsound.PlaySound(
            str(path),
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
        )
    except Exception:
        # Audio is optional; a missing device/file must never block Yornis.
        return


def play_bird_signature(theme_name: str, root=None) -> None:
    """Play the recording belonging to the clicked palette, fully offline."""
    if theme_name not in BIRD_AUDIO_FILES:
        return
    enabled, volume = startup_audio.settings()
    if not enabled or volume <= 0:
        return

    def launch():
        threading.Thread(
            target=_play,
            args=(theme_name, volume),
            daemon=True,
            name=f"YornisOriginalBirdAudio-{theme_name}",
        ).start()

    try:
        if root is not None:
            root.after(25, launch)
        else:
            launch()
    except Exception:
        launch()
