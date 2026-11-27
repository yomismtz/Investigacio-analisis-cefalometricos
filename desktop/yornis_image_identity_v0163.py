from __future__ import annotations

"""Final compatibility guards for image-scoped cervical outcomes."""

import unicodedata

from research_db import ResearchDB


def _persisted_image_identity(db, case_id: int) -> tuple[str, int]:
    """Return the persisted current image digest and positive revision.

    The cases.file_hash column is the authoritative image identity: attach_image
    calculates it from the newly attached file and advances image_revision in
    the same transaction. Legacy adapters may return an empty value from
    _active_image_hash; that must not erase the persisted identity.
    """
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
    image_hash = active or stored
    try:
        revision = max(1, int(case["image_revision"] or 1))
    except (TypeError, ValueError, OverflowError):
        revision = 1
    # Never bind a result to a conflicting, transient disk hash. The stored
    # digest is established when the image is attached and remains canonical.
    if stored and active and active != stored:
        image_hash = stored
    return image_hash, revision


def install_cervical_result_identity() -> None:
    """Ensure manual CVM/C2-C4 saves persist the active radiograph SHA256."""
    import yornis_cervical_v0152 as cervical
    import yornis_alignment_v0152 as alignment

    if not getattr(cervical._image_identity, "_yornis_persisted_image_hash_v0163", False):
        def image_identity(db, case_id: int) -> tuple[str, int]:
            return _persisted_image_identity(db, case_id)

        image_identity._yornis_persisted_image_hash_v0163 = True
        cervical._image_identity = image_identity

    if not getattr(alignment.cervical._image_identity, "_yornis_persisted_image_hash_v0163", False):
        alignment.cervical._image_identity = cervical._image_identity

    # Install the database result guard after all earlier compatibility layers
    # have been imported, so manual qualitative results are not suppressed by
    # the legacy landmark-only requirement.
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
            if (
                analysis == cvm_analysis
                or measurement == cvm_measurement
                or ("cvm" in analysis and "c2" in analysis and "c4" in analysis)
                or ("baccetti" in measurement and "cvm" in measurement)
            ):
                item = dict(row)
                item["analysis"] = cervical.CVM_ANALYSIS
                manual.setdefault("cvm", item)
            elif (
                analysis == align_analysis
                or measurement == align_measurement
                or ("alineacion" in analysis and "c2" in analysis and "c4" in analysis)
                or ("alineacion" in measurement and "c2" in measurement and "c4" in measurement)
            ):
                item = dict(row)
                item["analysis"] = alignment.ALIGNMENT_ANALYSIS
                manual.setdefault("alignment", item)

        # Keep the existing engine-derived results only if they are bound to
        # the exact same image and revision. This filters any legacy wrapper's
        # unscoped output, without requiring cervical outcomes to have landmarks.
        calculated = current(self, case_id, protocol_version) or []
        combined = {}
        for row in calculated:
            try:
                if (
                    str(row["image_hash"] or "") != stored_hash
                    or int(row["image_revision"] or 0) != revision
                ):
                    continue
                key = (str(row["analysis"]), str(row["measurement"]), int(row["version"]))
                combined[key] = row
            except (KeyError, IndexError, TypeError, ValueError):
                continue
        for item in manual.values():
            key = (str(item["analysis"]), str(item["measurement"]), int(item["version"]))
            combined[key] = item
        return sorted(
            combined.values(),
            key=lambda row: (str(row["analysis"]), str(row["measurement"])),
        )

    latest_results._yornis_cervical_manual_results_v0163 = True
    ResearchDB.latest_results = latest_results
