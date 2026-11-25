from __future__ import annotations

import os
import shutil
from pathlib import Path

APP_ROOT = Path(os.getenv("APPDATA", str(Path.home())))
LEGACY_APP_DIR = APP_ROOT / "YomCeph"
APP_DIR = APP_ROOT / "Yornis"


def _copy_missing_files(source: Path, destination: Path) -> tuple[int, int]:
    """Merge a legacy folder without overwriting any newer Yornis data."""
    copied = 0
    preserved = 0
    for item in sorted(source.rglob("*")):
        relative = item.relative_to(source)
        target = destination / relative
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            preserved += 1
            continue
        shutil.copy2(item, target)
        copied += 1
    return copied, preserved


def _rename_legacy_database(directory: Path) -> bool:
    """Rename the old database and its SQLite sidecars only when safe."""
    research = directory / "research"
    old_db = research / "yomceph_research.sqlite3"
    new_db = research / "yornis_research.sqlite3"
    if not old_db.exists() or new_db.exists():
        return False
    old_db.rename(new_db)
    for suffix in ("-wal", "-shm"):
        old_sidecar = Path(str(old_db) + suffix)
        new_sidecar = Path(str(new_db) + suffix)
        if old_sidecar.exists() and not new_sidecar.exists():
            old_sidecar.rename(new_sidecar)
    return True


def migrate_legacy_app_dir(
    legacy_dir: str | Path = LEGACY_APP_DIR,
    new_dir: str | Path = APP_DIR,
) -> dict[str, int | bool]:
    """Move old YomCeph data to Yornis, preserving existing destination files.

    If Yornis already exists, only missing files are copied; nothing in the
    destination is overwritten and the old directory remains as a safety copy.
    """
    legacy = Path(legacy_dir)
    destination = Path(new_dir)
    if legacy.resolve() == destination.resolve():
        return {"moved": False, "copied": 0, "preserved": 0, "database_renamed": False}
    if not legacy.exists():
        renamed = _rename_legacy_database(destination)
        return {"moved": False, "copied": 0, "preserved": 0, "database_renamed": renamed}

    moved = False
    copied = 0
    preserved = 0
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            legacy.rename(destination)
            moved = True
        except OSError:
            copied, preserved = _copy_missing_files(legacy, destination)
    else:
        copied, preserved = _copy_missing_files(legacy, destination)

    renamed = _rename_legacy_database(destination)
    return {
        "moved": moved,
        "copied": copied,
        "preserved": preserved,
        "database_renamed": renamed,
    }


# Run before any Yornis component opens its database or settings file.
MIGRATION_RESULT = migrate_legacy_app_dir()
