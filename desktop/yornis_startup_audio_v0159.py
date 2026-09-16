from __future__ import annotations

import math
import os
import random
import struct
import threading
import wave
from pathlib import Path

from tkinter import ttk

import yornis_theme

AUDIO_VERSION = "0.15.9"
SAMPLE_RATE = 44100
DURATION = 2.8
DEFAULT_VOLUME = 35
_PLAYED = False

_THEME_FINALE = {
    "Agaporni": (2100, 3300),
    "Tucán": (1250, 2200),
    "Pavorreal": (1700, 2750),
    "Ninfa": (2400, 3700),
    "Faisán": (1450, 2350),
    "Quetzal": (2250, 3600),
    "Guacamaya Roja": (1550, 2650),
    "Guacamaya Azul": (1850, 3050),
}


def settings() -> tuple[bool, int]:
    data = yornis_theme.load_settings()
    enabled = bool(data.get("startup_bird_sound", True))
    try:
        volume = int(data.get("startup_bird_volume", DEFAULT_VOLUME))
    except Exception:
        volume = DEFAULT_VOLUME
    return enabled, max(0, min(100, volume))


def save_settings(*, enabled: bool | None = None, volume: int | None = None) -> None:
    data = yornis_theme.load_settings()
    if enabled is not None:
        data["startup_bird_sound"] = bool(enabled)
    if volume is not None:
        data["startup_bird_volume"] = max(0, min(100, int(volume)))
    yornis_theme.save_settings(data)


def _env(x: float) -> float:
    if x <= 0.0 or x >= 1.0:
        return 0.0
    return math.sin(math.pi * x) ** 1.7


def _add_chirp(buf: list[float], start: float, duration: float, f0: float, f1: float, amp: float, wobble: float = 5.0) -> None:
    i0 = max(0, int(start * SAMPLE_RATE))
    n = max(1, int(duration * SAMPLE_RATE))
    phase = 0.0
    for j in range(n):
        i = i0 + j
        if i >= len(buf):
            break
        x = j / max(1, n - 1)
        curve = x * x * (3.0 - 2.0 * x)
        freq = f0 + (f1 - f0) * curve + 75.0 * math.sin(2.0 * math.pi * wobble * x)
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        tone = math.sin(phase) + 0.22 * math.sin(2.0 * phase + 0.4)
        buf[i] += amp * _env(x) * tone


def synthesize_chorus(theme_name: str | None = None, volume: int | None = None) -> bytes:
    theme_name = theme_name or yornis_theme.current_theme_name()
    if volume is None:
        _, volume = settings()
    volume = max(0, min(100, int(volume)))
    total = int(DURATION * SAMPLE_RATE)
    buf = [0.0] * total

    # Deterministic flock: several independent calls with different registers.
    flock = [
        (0.08, 0.22, 1900, 3150, .16, 5.5),
        (0.20, 0.18, 2550, 1850, .12, 7.0),
        (0.38, 0.25, 1350, 2450, .13, 4.0),
        (0.58, 0.19, 2800, 3900, .10, 8.0),
        (0.76, 0.28, 1650, 2950, .15, 5.0),
        (1.02, 0.18, 3200, 2300, .10, 7.5),
        (1.18, 0.30, 1450, 2600, .15, 4.5),
        (1.43, 0.20, 2350, 3550, .12, 6.0),
        (1.65, 0.27, 1750, 3050, .14, 5.5),
        (1.88, 0.18, 3000, 2250, .09, 8.5),
    ]
    for spec in flock:
        _add_chirp(buf, *spec)

    # A short signature phrase for the currently selected bird/palette.
    f0, f1 = _THEME_FINALE.get(theme_name, _THEME_FINALE["Agaporni"])
    _add_chirp(buf, 2.10, .24, f0, f1, .18, 5.0)
    _add_chirp(buf, 2.36, .27, f1 * .88, f0 * 1.12, .16, 6.5)

    peak = max(0.001, max(abs(v) for v in buf))
    gain = (volume / 100.0) * 0.72 / peak
    frames = bytearray()
    for v in buf:
        sample = int(max(-1.0, min(1.0, v * gain)) * 32767)
        frames.extend(struct.pack("<h", sample))
    return bytes(frames)


def wav_path(theme_name: str | None = None, volume: int | None = None) -> Path:
    theme_name = theme_name or yornis_theme.current_theme_name()
    if volume is None:
        _, volume = settings()
    safe = "".join(c if c.isalnum() else "_" for c in theme_name)
    root = Path(os.getenv("APPDATA", str(Path.home()))) / "YomCeph" / "audio"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"yornis_bird_chorus_{AUDIO_VERSION}_{safe}_{int(volume)}.wav"


def ensure_wav(theme_name: str | None = None, volume: int | None = None) -> Path:
    path = wav_path(theme_name, volume)
    if path.exists() and path.stat().st_size > 1000:
        return path
    frames = synthesize_chorus(theme_name, volume)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(frames)
    return path


def _play(theme_name: str, volume: int) -> None:
    try:
        import winsound
        path = ensure_wav(theme_name, volume)
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception:
        # Audio is decorative; never block or crash Yornis if the sound device is unavailable.
        return


def play_startup_chorus(root=None, *, force: bool = False) -> None:
    global _PLAYED
    enabled, volume = settings()
    if not enabled or volume <= 0:
        return
    if _PLAYED and not force:
        return
    _PLAYED = True
    theme_name = yornis_theme.current_theme_name()

    def launch():
        threading.Thread(target=_play, args=(theme_name, volume), daemon=True, name="YornisBirdChorus").start()

    try:
        if root is not None:
            root.after(280, launch)
        else:
            launch()
    except Exception:
        launch()


def attach_sound_controls(launcher) -> None:
    if not hasattr(launcher, "main"):
        return
    enabled, volume = settings()
    row = ttk.Frame(launcher.main)
    row.pack(fill="x", pady=(10, 0))

    launcher.startup_sound_var = getattr(launcher, "startup_sound_var", None) or __import__("tkinter").BooleanVar(value=enabled)
    launcher.startup_volume_var = getattr(launcher, "startup_volume_var", None) or __import__("tkinter").IntVar(value=volume)

    def persist_enabled():
        save_settings(enabled=launcher.startup_sound_var.get())

    def persist_volume(_event=None):
        save_settings(volume=launcher.startup_volume_var.get())

    ttk.Checkbutton(row, text="🐦 Sonido de inicio", variable=launcher.startup_sound_var, command=persist_enabled).pack(side="left")
    ttk.Label(row, text="Volumen", style="Caption.TLabel").pack(side="left", padx=(16, 6))
    combo = ttk.Combobox(row, state="readonly", width=6, textvariable=launcher.startup_volume_var, values=(20, 35, 50, 70, 90))
    combo.pack(side="left")
    combo.bind("<<ComboboxSelected>>", persist_volume)
    ttk.Button(row, text="Probar canto", style="Ghost.TButton", command=lambda: play_startup_chorus(launcher, force=True)).pack(side="left", padx=(8, 0))
    ttk.Label(row, text="2–3 s · generado localmente · sin grabaciones externas", style="Caption.TLabel").pack(side="right")
