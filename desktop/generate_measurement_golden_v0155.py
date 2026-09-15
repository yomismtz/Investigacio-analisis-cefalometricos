from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

# Install layers in the same order as the application/test suite.
import yornis_ceph_quality_v0153  # noqa: F401
import research_stability_db_v0141
import yornis_storage_v015
import yornis_import_v015
import yornis_backup_v015
import research_ui
import yornis_cervical_v0152 as cv
import yornis_alignment_v0152 as al

research_stability_db_v0141.install()
yornis_storage_v015.install()
yornis_import_v015.install()
yornis_backup_v015.install()
cv.install_research(research_ui.ResearchWorkspace)
al.install_research(research_ui.ResearchWorkspace)
yornis_ceph_quality_v0153.install_research(research_ui.ResearchWorkspace)

import yornis_audit_hardening_v0154 as hard
hard.install_global()

import classic_engine as engine


def deterministic_points() -> dict[str, tuple[float, float]]:
    names: set[str] = set()
    for measurement in engine.MEASUREMENTS:
        names.update(getattr(measurement, "pts", ()) or ())
    names.update(("S", "N", "Po", "Or", "Me", "Go", "Pg", "A", "B"))
    points: dict[str, tuple[float, float]] = {}
    for i, name in enumerate(sorted(n for n in names if n), 1):
        # Stable, deliberately irregular non-degenerate geometry.
        points[name] = (
            float(i * 13 + (i % 5) * 2 + (i % 3) * 0.17),
            float(i * i * 0.37 + (i % 7) * 11 + 3 + (i % 4) * 0.13),
        )
    return points


def build_records() -> list[dict]:
    points = deterministic_points()
    records: list[dict] = []
    for index, measurement in enumerate(engine.MEASUREMENTS):
        value = float(engine.compute(measurement, points, 0.1, "right"))
        if not math.isfinite(value):
            raise RuntimeError(f"Non-finite value for {measurement.analysis} / {measurement.name}: {value}")
        records.append(
            {
                "index": index,
                "analysis": str(measurement.analysis),
                "name": str(measurement.name),
                "unit": str(getattr(measurement, "unit", "")),
                "pts": list(getattr(measurement, "pts", ()) or ()),
                "value": round(value, 10),
            }
        )
    if len(records) != 102:
        raise RuntimeError(f"Expected 102 measurements, got {len(records)}")
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": 1,
        "description": "Yornis v0.15.5 deterministic computational regression baseline; not an external clinical validation dataset.",
        "mm_per_px": 0.1,
        "face_direction": "right",
        "count": 102,
        "measurements": build_records(),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(payload['measurements'])} golden measurements to {output}")


if __name__ == "__main__":
    main()
