from __future__ import annotations

import threading
from pathlib import Path
from tkinter import ttk

import yornis_theme

AUDIO_VERSION = "0.16.3-original-recordings"
DEFAULT_VOLUME = 35
_PLAYED = False


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


def bundled_wav_path(theme_name: str | None = None, volume: int | None = None) -> Path:
    """Path to the matching uploaded bird recording's short offline excerpt."""
    import yornis_bird_signature_v01592 as bird_audio
    theme_name = theme_name or yornis_theme.current_theme_name()
    if volume is None:
        _, volume = settings()
    return bird_audio.bundled_startup_path(theme_name, volume)


def _play(theme_name: str, volume: int) -> None:
    try:
        import winsound
        path = bundled_wav_path(theme_name, volume)
        if not path.is_file():
            return
        winsound.PlaySound(
            str(path),
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
        )
    except Exception:
        # Audio is optional; it must never prevent the clinical application from opening.
        return


def play_startup_chorus(root=None, *, force: bool = False) -> None:
    """Play a short excerpt of the selected bird's original recording."""
    global _PLAYED
    enabled, volume = settings()
    if not enabled or volume <= 0:
        return
    if _PLAYED and not force:
        return
    _PLAYED = True
    theme_name = yornis_theme.current_theme_name()

    def launch():
        threading.Thread(
            target=_play,
            args=(theme_name, volume),
            daemon=True,
            name=f"YornisStartupBird-{theme_name}",
        ).start()

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

    # Controls are attached after every palette rebuild; remove the previous row
    # first to avoid duplicate controls accumulating across theme changes.
    old = getattr(launcher, "_yornis_sound_controls_row", None)
    if old is not None:
        try:
            if old.winfo_exists():
                old.destroy()
        except Exception:
            pass
    launcher._yornis_sound_controls_row = row

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
    ttk.Label(row, text="Grabaciones originales · funciona sin conexión", style="Caption.TLabel").pack(side="right")
