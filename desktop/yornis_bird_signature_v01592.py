from __future__ import annotations

import math
import os
import struct
import threading
import wave
from pathlib import Path

import yornis_startup_audio_v0159 as startup_audio

AUDIO_SIGNATURE_VERSION = "0.15.9.2"
SAMPLE_RATE = 44100
SIGNATURE_DURATION = 1.15

# Short procedural signatures. These are intentionally synthetic identities
# inspired by each bird palette, not third-party wildlife recordings.
_SIGNATURES = {
    "Agaporni": [
        (0.06, .13, 3000, 4200, .24, 8.0),
        (0.23, .12, 3300, 4550, .22, 8.5),
        (0.39, .16, 2850, 3900, .23, 7.0),
    ],
    "Tucán": [
        (0.05, .20, 1150, 1550, .25, 3.3),
        (0.31, .18, 1250, 1850, .23, 3.8),
        (0.57, .19, 1050, 1500, .21, 3.0),
    ],
    "Pavorreal": [
        (0.05, .27, 1850, 2550, .23, 4.0),
        (0.38, .30, 2450, 1550, .24, 3.6),
        (0.76, .23, 1700, 2300, .19, 4.2),
    ],
    "Ninfa": [
        (0.05, .18, 2500, 3900, .22, 7.0),
        (0.28, .24, 3700, 2600, .20, 6.7),
        (0.59, .22, 2800, 4200, .21, 7.5),
    ],
    "Faisán": [
        (0.06, .20, 1300, 1900, .24, 4.0),
        (0.32, .16, 1650, 1200, .21, 4.8),
        (0.56, .23, 1250, 2150, .22, 3.8),
    ],
    "Quetzal": [
        (0.04, .25, 2200, 3500, .23, 5.0),
        (0.35, .25, 3350, 2250, .21, 5.2),
        (0.68, .24, 2350, 3650, .22, 5.0),
    ],
    "Guacamaya Roja": [
        (0.05, .25, 1450, 2450, .25, 5.2),
        (0.36, .23, 2300, 1500, .23, 5.5),
        (0.66, .28, 1550, 2700, .23, 5.0),
    ],
    "Guacamaya Azul": [
        (0.05, .24, 1750, 3000, .24, 5.3),
        (0.35, .22, 2950, 1850, .22, 5.6),
        (0.64, .29, 1900, 3200, .23, 5.1),
    ],
}


def _env(x: float) -> float:
    if x <= 0.0 or x >= 1.0:
        return 0.0
    return math.sin(math.pi * x) ** 1.65


def _add_chirp(buf: list[float], start: float, duration: float, f0: float, f1: float, amp: float, wobble: float) -> None:
    i0 = max(0, int(start * SAMPLE_RATE))
    n = max(1, int(duration * SAMPLE_RATE))
    phase = 0.0
    for j in range(n):
        i = i0 + j
        if i >= len(buf):
            break
        x = j / max(1, n - 1)
        curve = x * x * (3.0 - 2.0 * x)
        freq = f0 + (f1 - f0) * curve + 65.0 * math.sin(2.0 * math.pi * wobble * x)
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        tone = math.sin(phase) + 0.18 * math.sin(2.0 * phase + 0.25)
        buf[i] += amp * _env(x) * tone


def synthesize_signature(theme_name: str, volume: int | None = None) -> bytes:
    if volume is None:
        _, volume = startup_audio.settings()
    volume = max(0, min(100, int(volume)))
    total = int(SIGNATURE_DURATION * SAMPLE_RATE)
    buf = [0.0] * total
    phrase = _SIGNATURES.get(theme_name, _SIGNATURES["Agaporni"])
    for spec in phrase:
        _add_chirp(buf, *spec)
    peak = max(0.001, max(abs(v) for v in buf))
    gain = (volume / 100.0) * 0.68 / peak
    frames = bytearray()
    for v in buf:
        sample = int(max(-1.0, min(1.0, v * gain)) * 32767)
        frames.extend(struct.pack("<h", sample))
    return bytes(frames)


def signature_path(theme_name: str, volume: int | None = None) -> Path:
    if volume is None:
        _, volume = startup_audio.settings()
    safe = "".join(c if c.isalnum() else "_" for c in theme_name)
    root = Path(os.getenv("APPDATA", str(Path.home()))) / "YomCeph" / "audio"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"yornis_bird_signature_{AUDIO_SIGNATURE_VERSION}_{safe}_{int(volume)}.wav"


def ensure_signature_wav(theme_name: str, volume: int | None = None) -> Path:
    path = signature_path(theme_name, volume)
    if path.exists() and path.stat().st_size > 1000:
        return path
    frames = synthesize_signature(theme_name, volume)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(frames)
    return path


def _play(theme_name: str, volume: int) -> None:
    try:
        import winsound
        path = ensure_signature_wav(theme_name, volume)
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception:
        return


def play_bird_signature(theme_name: str, root=None) -> None:
    enabled, volume = startup_audio.settings()
    if not enabled or volume <= 0:
        return

    def launch():
        threading.Thread(
            target=_play,
            args=(theme_name, volume),
            daemon=True,
            name=f"YornisBirdSignature-{theme_name}",
        ).start()

    try:
        if root is not None:
            root.after(25, launch)
        else:
            launch()
    except Exception:
        launch()
