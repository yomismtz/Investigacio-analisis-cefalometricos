from __future__ import annotations

import os
import struct
import threading
import wave
from pathlib import Path

import yornis_theme
import yornis_startup_audio_v0159 as base

CALL_VERSION = "0.15.9.2"
CALL_DURATION = 1.20
SAMPLE_RATE = base.SAMPLE_RATE

# Stylized, procedural signatures. These are generated locally and are not
# recordings of real animals. Each palette has a clearly different register,
# rhythm and contour so users can identify the selected bird by sound.
_BIRD_PATTERNS = {
    "Agaporni": (
        (0.04, .10, 3100, 4050, .23, 9.0),
        (0.17, .09, 3850, 3150, .20, 10.0),
        (0.31, .10, 3250, 4200, .22, 9.5),
        (0.46, .08, 4000, 3350, .19, 11.0),
        (0.62, .11, 3300, 4100, .20, 9.5),
    ),
    "Tucán": (
        (0.05, .23, 880, 1220, .30, 2.6),
        (0.34, .20, 1120, 790, .27, 2.2),
        (0.62, .23, 850, 1180, .29, 2.8),
        (0.92, .16, 1040, 820, .23, 2.5),
    ),
    "Pavorreal": (
        (0.04, .34, 1700, 920, .29, 2.1),
        (0.43, .32, 1580, 860, .27, 2.2),
        (0.82, .28, 1480, 980, .24, 2.5),
    ),
    "Ninfa": (
        (0.05, .24, 2580, 3650, .24, 5.0),
        (0.34, .20, 3520, 2920, .22, 6.0),
        (0.61, .25, 2820, 3920, .23, 5.5),
        (0.92, .16, 3720, 3150, .18, 6.5),
    ),
    "Faisán": (
        (0.05, .14, 1080, 1580, .31, 7.0),
        (0.23, .12, 1510, 900, .28, 8.0),
        (0.50, .15, 1020, 1480, .28, 7.0),
        (0.73, .12, 1420, 940, .25, 8.0),
        (0.95, .11, 1050, 1380, .22, 7.0),
    ),
    "Quetzal": (
        (0.04, .29, 2180, 3040, .20, 2.4),
        (0.38, .27, 3040, 2440, .19, 2.5),
        (0.70, .30, 2460, 3420, .20, 2.7),
        (1.03, .11, 3300, 3000, .15, 3.0),
    ),
    "Guacamaya Roja": (
        (0.04, .24, 1260, 2250, .33, 8.0),
        (0.32, .20, 2160, 1160, .31, 9.0),
        (0.59, .24, 1210, 2340, .31, 8.0),
        (0.90, .19, 2200, 1320, .27, 9.0),
    ),
    "Guacamaya Azul": (
        (0.04, .27, 1460, 2540, .31, 7.0),
        (0.36, .26, 2400, 1370, .29, 7.5),
        (0.70, .30, 1410, 2660, .30, 7.0),
        (1.03, .12, 2350, 1700, .21, 7.5),
    ),
}


def _pcm_from_buffer(buf: list[float], volume: int) -> bytes:
    peak = max(0.001, max(abs(v) for v in buf))
    gain = (max(0, min(100, int(volume))) / 100.0) * 0.72 / peak
    frames = bytearray()
    for value in buf:
        sample = int(max(-1.0, min(1.0, value * gain)) * 32767)
        frames.extend(struct.pack("<h", sample))
    return bytes(frames)


def synthesize_bird_call(theme_name: str | None = None, volume: int | None = None) -> bytes:
    theme_name = theme_name or yornis_theme.current_theme_name()
    if volume is None:
        _, volume = base.settings()
    patterns = _BIRD_PATTERNS.get(theme_name, _BIRD_PATTERNS["Agaporni"])
    buf = [0.0] * int(CALL_DURATION * SAMPLE_RATE)
    for spec in patterns:
        base._add_chirp(buf, *spec)

    # Add a soft lower harmonic to the larger birds so their signatures are
    # audibly different from the high whistles of Agaporni/Ninfa/Quetzal.
    if theme_name in {"Tucán", "Pavorreal", "Faisán", "Guacamaya Roja", "Guacamaya Azul"}:
        for start, duration, f0, f1, amp, wobble in patterns[:3]:
            base._add_chirp(buf, start, duration, f0 * .52, f1 * .52, amp * .24, max(1.5, wobble * .45))
    return _pcm_from_buffer(buf, int(volume))


def bird_call_path(theme_name: str | None = None, volume: int | None = None) -> Path:
    theme_name = theme_name or yornis_theme.current_theme_name()
    if volume is None:
        _, volume = base.settings()
    safe = "".join(c if c.isalnum() else "_" for c in theme_name)
    root = Path(os.getenv("APPDATA", str(Path.home()))) / "YomCeph" / "audio"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"yornis_bird_call_{CALL_VERSION.replace('.', '_')}_{safe}_{int(volume)}.wav"


def ensure_bird_call_wav(theme_name: str | None = None, volume: int | None = None) -> Path:
    path = bird_call_path(theme_name, volume)
    if path.exists() and path.stat().st_size > 1000:
        return path
    frames = synthesize_bird_call(theme_name, volume)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(frames)
    return path


def _play(theme_name: str, volume: int) -> None:
    try:
        import winsound
        path = ensure_bird_call_wav(theme_name, volume)
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception:
        return


def play_bird_call(root=None, *, theme_name: str | None = None) -> None:
    enabled, volume = base.settings()
    if not enabled or volume <= 0:
        return
    theme_name = theme_name or yornis_theme.current_theme_name()

    def launch():
        threading.Thread(target=_play, args=(theme_name, volume), daemon=True, name=f"YornisBirdCall-{theme_name}").start()

    try:
        if root is not None:
            root.after(45, launch)
        else:
            launch()
    except Exception:
        launch()
