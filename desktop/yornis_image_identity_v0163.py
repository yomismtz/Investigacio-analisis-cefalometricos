from __future__ import annotations

"""Final compatibility guards for image-scoped cervical outcomes."""

import unicodedata

from research_db import ResearchDB


def _persisted_image_identity(db, case_id: int) -> tuple[str, int]:
    """Return the persisted current image digest and positive revision."""
    case = db.case(case_id)
    if not case:
        return "", 1
    stored = str(case["file_hash"] or "").strip()
    active = ""
    resolver = getattr(db, "_active_image_hash", None)
    if callable(resolver):
        try:
            active = str(resolver(case) or "").strip()
        except Exception:
            active = ""
    image_hash = stored or active
    try:
        revision = max(1, int(case["image_revision"] or 1))
    except (TypeError, ValueError, OverflowError):
        revision = 1
    # The digest persisted by attach_image is authoritative.
    return image_hash, revision


def _protocol_version(workspace) -> int:
    try:
        return int(getattr(workspace, "protocol_version", 0) or
                   (getattr(workspace, "protocol", {}) or {}).get("version", 0) or 0)
    except Exception:
        return 0


def _bind_new_manual_rows(save, analysis: str, measurement: str):
    """Repair rows emitted by legacy save wrappers that omit image identity.

    Only rows inserted by this invocation are touched. Historical rows remain
    append-only and are never rebound to a newly attached radiograph.
    """
    def wrapped(workspace, *args, **kwargs):
        db = getattr(workspace, "db", None)
        case_id = getattr(workspace, "case_id", None)
        if db is None or not case_id:
            return save(workspace, *args, **kwargs)
        try:
            with db.connect() as con:
                before = int(con.execute(
                    "SELECT COALESCE(MAX(id),0) FROM results"
                ).fetchone()[0])
        except Exception:
            before = 0
        result = save(workspace, *args, **kwargs)
        image_hash, revision = _persisted_image_identity(db, int(case_id))
        if image_hash:
            try:
                with db.connect() as con:
                    con.execute(
                        """UPDATE results
                           SET image_hash=?, image_revision=?
                           WHERE id>? AND case_id=? AND protocol_version=?
                             AND analysis=? AND measurement=?
                             AND COALESCE(image_hash,'')=''
                             AND image_revision=?""",
                        (image_hash, revision, before, int(case_id),
                         _protocol_version(workspace), analysis, measurement, revision),
                    )
            except Exception:
                # Preserve the original save result; regression tests expose
                # any identity that could not be bound.
                pass
        return result
    wrapped.__name__ = getattr(save, "__name__", "wrapped_save")
    wrapped.__doc__ = getattr(save, "__doc__", None)
    wrapped._yornis_binds_active_image_v0163 = True
    return wrapped


def install_cervical_result_identity() -> None:
    """Ensure manual CVM/C2-C4 saves persist the active radiograph SHA256."""
    import yornis_cervical_v0152 as cervical
    import yornis_alignment_v0152 as alignment

    if not getattr(cervical._image_identity, "_yornis_persisted_image_hash_v0163", False):
        def image_identity(db, case_id: int) -> tuple[str, int]:
            return _persisted_image_identity(db, case_id)
        image_identity._yornis_persisted_image_hash_v0163 = True
        cervical._image_identity = image_identity
    alignment.cervical._image_identity = cervical._image_identity

    if not getattr(cervical._save_cvm, "_yornis_binds_active_image_v0163", False):
        cervical._save_cvm = _bind_new_manual_rows(
            cervical._save_cvm, cervical.CVM_ANALYSIS, cervical.CVM_MEASUREMENT
        )
    if not getattr(alignment._save_alignment, "_yornis_binds_active_image_v0163", False):
        alignment._save_alignment = _bind_new_manual_rows(
            alignment._save_alignment, alignment.ALIGNMENT_ANALYSIS,
            alignment.ALIGNMENT_MEASUREMENT
        )

    current = ResearchDB.latest_results
    if getattr(current, "_yornis_cervical_manual_results_v0163", False):
        return

    def canonical(value: object) -> str:
        text = unicodedata.normalize("NFKD", str(value or ""))
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return "".join(ch.lower() for ch in text if ch.isalnum())

    def latest_results(self, case_id: int, protocol_version: int):
        case = self.case(case_id)
        if not case:
            return []
        stored_hash = str(case["file_hash"] or "").strip()
        if not stored_hash:
            return current(self, case_id, protocol_version)
        try:
            revision = max(1, int(case["image_revision"] or 1))
        except (TypeError, ValueError, OverflowError):
            revision = 1

        cvm_analysis = canonical(cervical.CVM_ANALYSIS)
        cvm_measurement = canonical(cervical.CVM_MEASUREMENT)
        align_analysis = canonical(alignment.ALIGNMENT_ANALYSIS)
        align_measurement = canonical(alignment.ALIGNMENT_MEASUREMENT)

        with self.connect() as con:
            rows = con.execute(
                """SELECT r.* FROM results r
                   WHERE r.case_id=? AND r.protocol_version=?
                     AND r.image_hash=? AND r.image_revision=?
                   ORDER BY r.id DESC""",
                (case_id, protocol_version, stored_hash, revision),
            ).fetchall()

        manual = {}
        for row in rows:
            analysis = canonical(row["analysis"])
            measurement = canonical(row["measurement"])
            if (analysis == cvm_analysis or measurement == cvm_measurement
                or ("cvm" in analysis and "c2" in analysis and "c4" in analysis)
                or ("baccetti" in measurement and "cvm" in measurement)):
                item = dict(row)
                item["analysis"] = cervical.CVM_ANALYSIS
                manual.setdefault("cvm", item)
            elif (analysis == align_analysis or measurement == align_measurement
                  or ("alineacion" in analysis and "c2" in analysis and "c4" in analysis)
                  or ("alineacion" in measurement and "c2" in measurement and "c4" in measurement)):
                item = dict(row)
                item["analysis"] = alignment.ALIGNMENT_ANALYSIS
                manual.setdefault("alignment", item)

        calculated = current(self, case_id, protocol_version) or []
        combined = {}
        for row in calculated:
            try:
                if (str(row["image_hash"] or "") != stored_hash
                    or int(row["image_revision"] or 0) != revision):
                    continue
                key = (str(row["analysis"]), str(row["measurement"]), int(row["version"]))
                combined[key] = row
            except (KeyError, IndexError, TypeError, ValueError):
                continue
        for item in manual.values():
            key = (str(item["analysis"]), str(item["measurement"]), int(item["version"]))
            combined[key] = item
        return sorted(combined.values(),
                      key=lambda row: (str(row["analysis"]), str(row["measurement"])))

    latest_results._yornis_cervical_manual_results_v0163 = True
    ResearchDB.latest_results = latest_results
