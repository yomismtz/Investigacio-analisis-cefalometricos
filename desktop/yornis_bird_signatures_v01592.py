from __future__ import annotations

import math
import os
import struct
import threading
import wave
from pathlib import Path

import yornis_theme
import yornis_startup_audio_v0159 as startup_audio

SIGNATURE_VERSION = "0.15.9.2"
SAMPLE_RATE = startup_audio.SAMPLE_RATE
SIGNATURE_DURATION = 1.05

# Distinct synthesized motifs for each Yornis bird identity. These are short
# UI signatures inspired by the palette birds; they are generated locally and
# are not field recordings or claims of bioacoustic fidelity.
BIRD_SIGNATURES = {
    "Agaporni": [(0.05, .12, 2400, 3300), (0.22, .11, 3150, 2550), (0.39, .13, 2700, 3550)],
    "Tucán": [(0.06, .15, 1050, 1450), (0.28, .16, 1180, 930), (0.53, .14, 980, 1350)],
    "Pavorreal": [(0.05, .18, 1450, 2100), (0.33, .20, 1800, 2500), (0.62, .16, 1550, 2250)],
    "Ninfa": [(0.04, .11, 2750, 3900), (0.19, .10, 3600, 3000), (0.34, .10, 3000, 4100), (0.50, .12, 3350, 2700)],
    "Faisán": [(0.05, .16, 1250, 1780), (0.31, .14, 1550, 1120), (0.52, .17, 1320, 1950)],
    "Quetzal": [(0.03, .15, 2500, 3850), (0.25, .13, 3400, 2700), (0.46, .17, 2850, 4200)],
    "Guacamaya Roja": [(0.04, .18, 1350, 2350), (0.31, .16, 2250, 1500), (0.56, .18, 1600, 2550)],
    "Guacamaya Azul": [(0.04, .16, 1700, 2850), (0.27, .14, 2750, 1950), (0.49, .16, 2050, 3200)],
}


def _env(x: float) -> float:
    if x <= 0.0 or x >= 1.0:
        return 0.0
    return math.sin(math.pi * x) ** 1.65


def synthesize_signature(theme_name: str, volume: int | None = None) -> bytes:
    if theme_name not in BIRD_SIGNATURES:
        theme_name = "Agaporni"
    if volume is None:
        _, volume = startup_audio.settings()
    volume = max(0, min(100, int(volume)))
    total = int(SIGNATURE_DURATION * SAMPLE_RATE)
    buf = [0.0] * total
    for start, duration, f0, f1 in BIRD_SIGNATURES[theme_name]:
        i0 = int(start * SAMPLE_RATE)
        n = max(1, int(duration * SAMPLE_RATE))
        phase = 0.0
        for j in range(n):
            i = i0 + j
            if i >= total:
                break
            x = j / max(1, n - 1)
            curve = x * x * (3.0 - 2.0 * x)
            freq = f0 + (f1 - f0) * curve + 55.0 * math.sin(2.0 * math.pi * 5.5 * x)
            phase += 2.0 * math.pi * freq / SAMPLE_RATE
            tone = math.sin(phase) + 0.19 * math.sin(2.0 * phase + 0.3)
            buf[i] += 0.40 * _env(x) * tone
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
    return root / f"yornis_bird_signature_{SIGNATURE_VERSION}_{safe}_{int(volume)}.wav"


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


def play_signature(theme_name: str, root=None) -> None:
    enabled, volume = startup_audio.settings()
    if not enabled or volume <= 0:
        return

    def worker():
        try:
            import winsound
            path = ensure_signature_wav(theme_name, volume)
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        except Exception:
            return

    def launch():
        threading.Thread(target=worker, daemon=True, name=f"YornisBirdSignature-{theme_name}").start()

    try:
        if root is not None:
            root.after(35, launch)
        else:
            launch()
    except Exception:
        launch()
