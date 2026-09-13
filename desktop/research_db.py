from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import shutil
import sqlite3
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "YomCeph"
RESEARCH_DIR = APP_DIR / "research"
DB_PATH = RESEARCH_DIR / "yomceph_research.sqlite3"
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".pdf"}
MAX_CASES = 1000


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def sha256_file(path: str | Path, block: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(block)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass
class ImportResult:
    added: int = 0
    duplicates: int = 0
    skipped: int = 0
    errors: list[str] | None = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ResearchDB:
    """Persistent research database.

    Source data (case demographics / image identity) and measurement results are
    deliberately stored in separate tables. Excluded records are retained for
    audit and are omitted only from valid-sample exports.
    """

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA journal_mode=WAL")
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def _init_schema(self):
        with self.connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS studies (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    researcher TEXT DEFAULT '',
                    institution TEXT DEFAULT '',
                    objective TEXT DEFAULT '',
                    language TEXT DEFAULT 'es',
                    blind_mode INTEGER DEFAULT 0,
                    protocol_version INTEGER DEFAULT 1,
                    protocol_locked INTEGER DEFAULT 0,
                    study_mm_per_px REAL,
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_opened_at TEXT
                );

                CREATE TABLE IF NOT EXISTS protocol_versions (
                    id INTEGER PRIMARY KEY,
                    study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
                    version INTEGER NOT NULL,
                    config_json TEXT NOT NULL,
                    locked INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE(study_id, version)
                );

                CREATE TABLE IF NOT EXISTS criteria (
                    id INTEGER PRIMARY KEY,
                    study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
                    kind TEXT NOT NULL CHECK(kind IN ('include','exclude')),
                    label TEXT NOT NULL,
                    active INTEGER DEFAULT 1,
                    position INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY,
                    study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
                    case_number INTEGER NOT NULL,
                    study_code TEXT NOT NULL,
                    sex TEXT DEFAULT '',
                    age REAL,
                    image_path TEXT DEFAULT '',
                    original_filename TEXT DEFAULT '',
                    file_hash TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'pending',
                    included INTEGER NOT NULL DEFAULT 1,
                    exclusion_reason TEXT DEFAULT '',
                    exclusion_note TEXT DEFAULT '',
                    examiner TEXT DEFAULT '',
                    case_mm_per_px REAL,
                    review_flag INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_opened_at TEXT,
                    UNIQUE(study_id, case_number),
                    UNIQUE(study_id, study_code)
                );

                CREATE INDEX IF NOT EXISTS idx_cases_study_status ON cases(study_id,status);
                CREATE INDEX IF NOT EXISTS idx_cases_hash ON cases(study_id,file_hash);

                CREATE TABLE IF NOT EXISTS case_criteria (
                    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                    criterion_id INTEGER NOT NULL REFERENCES criteria(id) ON DELETE CASCADE,
                    value INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY(case_id, criterion_id)
                );

                CREATE TABLE IF NOT EXISTS landmarks (
                    id INTEGER PRIMARY KEY,
                    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                    protocol_version INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY,
                    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                    protocol_version INTEGER NOT NULL,
                    analysis TEXT NOT NULL,
                    measurement TEXT NOT NULL,
                    value REAL,
                    unit TEXT DEFAULT '',
                    reference_text TEXT DEFAULT '',
                    interpretation TEXT DEFAULT '',
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_results_case ON results(case_id,protocol_version);

                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY,
                    study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
                    case_id INTEGER REFERENCES cases(id) ON DELETE CASCADE,
                    event TEXT NOT NULL,
                    details_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS reproducibility (
                    id INTEGER PRIMARY KEY,
                    study_id INTEGER NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
                    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                    examiner TEXT DEFAULT '',
                    round_no INTEGER DEFAULT 1,
                    selected INTEGER DEFAULT 1,
                    completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE(study_id,case_id,examiner,round_no)
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    # ---------- Audit ----------
    def audit(self, study_id: int, event: str, case_id: int | None = None, **details):
        with self.connect() as con:
            con.execute(
                "INSERT INTO audit_log(study_id,case_id,event,details_json,created_at) VALUES(?,?,?,?,?)",
                (study_id, case_id, event, json.dumps(details, ensure_ascii=False), now_iso()),
            )

    def audit_rows(self, study_id: int):
        with self.connect() as con:
            return con.execute(
                "SELECT * FROM audit_log WHERE study_id=? ORDER BY id", (study_id,)
            ).fetchall()

    # ---------- Studies / protocol ----------
    def create_study(self, title: str, researcher: str = "", institution: str = "", objective: str = "", language: str = "es", blind_mode: bool = False, notes: str = "") -> int:
        stamp = now_iso()
        with self.connect() as con:
            cur = con.execute(
                "INSERT INTO studies(title,researcher,institution,objective,language,blind_mode,notes,created_at,updated_at,last_opened_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (title.strip(), researcher.strip(), institution.strip(), objective.strip(), language, int(blind_mode), notes.strip(), stamp, stamp, stamp),
            )
            sid = int(cur.lastrowid)
        self.ensure_default_criteria(sid)
        self.audit(sid, "study_created", title=title)
        return sid

    def study(self, study_id: int):
        with self.connect() as con:
            return con.execute("SELECT * FROM studies WHERE id=?", (study_id,)).fetchone()

    def studies(self):
        with self.connect() as con:
            return con.execute(
                "SELECT s.*, (SELECT COUNT(*) FROM cases c WHERE c.study_id=s.id) AS case_count, "
                "(SELECT COUNT(*) FROM cases c WHERE c.study_id=s.id AND c.status='complete' AND c.included=1) AS complete_count "
                "FROM studies s ORDER BY COALESCE(last_opened_at,updated_at) DESC"
            ).fetchall()

    def touch_study(self, study_id: int):
        with self.connect() as con:
            con.execute("UPDATE studies SET last_opened_at=?,updated_at=? WHERE id=?", (now_iso(), now_iso(), study_id))
        self.set_setting("last_study_id", str(study_id))

    def set_setting(self, key: str, value: str):
        with self.connect() as con:
            con.execute("INSERT INTO app_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def get_setting(self, key: str, default: str = "") -> str:
        with self.connect() as con:
            row = con.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def latest_protocol(self, study_id: int) -> dict:
        with self.connect() as con:
            row = con.execute("SELECT * FROM protocol_versions WHERE study_id=? ORDER BY version DESC LIMIT 1", (study_id,)).fetchone()
        if not row:
            return {"version": 0, "locked": False, "config": {}}
        return {"version": row["version"], "locked": bool(row["locked"]), "config": json.loads(row["config_json"])}

    def save_protocol(self, study_id: int, config: dict, lock: bool = False, force_new_version: bool = False) -> int:
        current = self.latest_protocol(study_id)
        with self.connect() as con:
            study = con.execute("SELECT protocol_locked,protocol_version FROM studies WHERE id=?", (study_id,)).fetchone()
            if study is None:
                raise KeyError(study_id)
            has_valid = con.execute("SELECT 1 FROM cases WHERE study_id=? AND included=1 AND status IN ('in_progress','complete') LIMIT 1", (study_id,)).fetchone() is not None
            must_version = force_new_version or bool(study["protocol_locked"]) or has_valid or bool(current.get("locked"))
            if current["version"] == 0:
                version = 1
            elif must_version:
                version = current["version"] + 1
            else:
                version = current["version"]
            payload = json.dumps(config, ensure_ascii=False, sort_keys=True)
            if version == current["version"] and version > 0:
                con.execute("UPDATE protocol_versions SET config_json=?,locked=? WHERE study_id=? AND version=?", (payload, int(lock), study_id, version))
            else:
                con.execute("INSERT INTO protocol_versions(study_id,version,config_json,locked,created_at) VALUES(?,?,?,?,?)", (study_id, version, payload, int(lock), now_iso()))
            con.execute("UPDATE studies SET protocol_version=?,protocol_locked=?,updated_at=? WHERE id=?", (version, int(lock), now_iso(), study_id))
        self.audit(study_id, "protocol_saved", version=version, locked=lock, new_version=must_version)
        return version

    def lock_protocol(self, study_id: int):
        current = self.latest_protocol(study_id)
        if not current["version"]:
            raise ValueError("No protocol has been saved")
        with self.connect() as con:
            con.execute("UPDATE protocol_versions SET locked=1 WHERE study_id=? AND version=?", (study_id, current["version"]))
            con.execute("UPDATE studies SET protocol_locked=1,updated_at=? WHERE id=?", (now_iso(), study_id))
        self.audit(study_id, "protocol_locked", version=current["version"])

    def set_study_calibration(self, study_id: int, mm_per_px: float | None):
        with self.connect() as con:
            con.execute("UPDATE studies SET study_mm_per_px=?,updated_at=? WHERE id=?", (mm_per_px, now_iso(), study_id))
        self.audit(study_id, "study_calibration_changed", mm_per_px=mm_per_px)

    # ---------- Criteria ----------
    DEFAULT_INCLUDE = [
        "Radiografía lateral de cráneo en proyección adecuada",
        "Calidad suficiente para identificar los landmarks del protocolo",
        "Edad dentro del rango definido por el estudio",
        "Sexo registrado",
        "Cumple los criterios clínicos/demográficos del protocolo",
    ]
    DEFAULT_EXCLUDE = [
        "Calidad radiográfica insuficiente",
        "Landmarks requeridos no identificables",
        "Estructura fuera del campo radiográfico",
        "Distorsión/posición no aceptable",
        "Cirugía craneofacial previa",
        "Anomalía craneofacial excluida por el protocolo",
        "Incumple rango de edad",
        "Duplicado",
        "Otro",
    ]

    def ensure_default_criteria(self, study_id: int):
        with self.connect() as con:
            count = con.execute("SELECT COUNT(*) FROM criteria WHERE study_id=?", (study_id,)).fetchone()[0]
            if count:
                return
            pos = 0
            for kind, labels in (("include", self.DEFAULT_INCLUDE), ("exclude", self.DEFAULT_EXCLUDE)):
                for label in labels:
                    con.execute("INSERT INTO criteria(study_id,kind,label,position) VALUES(?,?,?,?)", (study_id, kind, label, pos))
                    pos += 1

    def criteria(self, study_id: int):
        with self.connect() as con:
            return con.execute("SELECT * FROM criteria WHERE study_id=? AND active=1 ORDER BY kind,position,id", (study_id,)).fetchall()

    def add_criterion(self, study_id: int, kind: str, label: str):
        if kind not in {"include", "exclude"}:
            raise ValueError(kind)
        with self.connect() as con:
            pos = con.execute("SELECT COALESCE(MAX(position),0)+1 FROM criteria WHERE study_id=?", (study_id,)).fetchone()[0]
            con.execute("INSERT INTO criteria(study_id,kind,label,position) VALUES(?,?,?,?)", (study_id, kind, label.strip(), pos))
        self.audit(study_id, "criterion_added", kind=kind, label=label)

    def set_case_criteria(self, case_id: int, values: dict[int, bool]):
        with self.connect() as con:
            for cid, value in values.items():
                con.execute("INSERT INTO case_criteria(case_id,criterion_id,value) VALUES(?,?,?) ON CONFLICT(case_id,criterion_id) DO UPDATE SET value=excluded.value", (case_id, cid, int(value)))
            row = con.execute("SELECT study_id FROM cases WHERE id=?", (case_id,)).fetchone()
        if row:
            self.audit(row[0], "case_criteria_updated", case_id=case_id, count=len(values))

    # ---------- Cases / import ----------
    def count_cases(self, study_id: int) -> int:
        with self.connect() as con:
            return int(con.execute("SELECT COUNT(*) FROM cases WHERE study_id=?", (study_id,)).fetchone()[0])

    def next_case_number(self, study_id: int) -> int:
        with self.connect() as con:
            return int(con.execute("SELECT COALESCE(MAX(case_number),0)+1 FROM cases WHERE study_id=?", (study_id,)).fetchone()[0])

    def case(self, case_id: int):
        with self.connect() as con:
            return con.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()

    def case_by_number(self, study_id: int, case_number: int):
        with self.connect() as con:
            return con.execute("SELECT * FROM cases WHERE study_id=? AND case_number=?", (study_id, case_number)).fetchone()

    def _study_folder(self, study_id: int) -> Path:
        p = RESEARCH_DIR / f"study_{study_id:04d}" / "images"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def duplicate_info(self, study_id: int, study_code: str = "", filename: str = "", file_hash: str = "") -> list[str]:
        reasons: list[str] = []
        with self.connect() as con:
            if study_code and con.execute("SELECT 1 FROM cases WHERE study_id=? AND study_code=?", (study_id, study_code)).fetchone():
                reasons.append("ID/código repetido")
            if filename and con.execute("SELECT 1 FROM cases WHERE study_id=? AND original_filename=?", (study_id, filename)).fetchone():
                reasons.append("nombre de archivo repetido")
            if file_hash and con.execute("SELECT 1 FROM cases WHERE study_id=? AND file_hash=?", (study_id, file_hash)).fetchone():
                reasons.append("archivo idéntico (SHA-256)")
        return reasons

    def add_case(self, study_id: int, study_code: str | None = None, sex: str = "", age: float | None = None, image_path: str = "", examiner: str = "", copy_image: bool = True) -> int:
        if self.count_cases(study_id) >= MAX_CASES:
            raise ValueError(f"El estudio ya contiene el máximo de {MAX_CASES} casos")
        n = self.next_case_number(study_id)
        code = (study_code or f"{n:04d}").strip()
        original_filename = Path(image_path).name if image_path else ""
        digest = sha256_file(image_path) if image_path and Path(image_path).exists() else ""
        dup = self.duplicate_info(study_id, code, original_filename, digest)
        if dup:
            raise ValueError("Duplicado: " + ", ".join(dup))
        stored = ""
        if image_path:
            src = Path(image_path)
            if copy_image:
                target = self._study_folder(study_id) / f"{n:04d}_{src.name}"
                shutil.copy2(src, target)
                stored = str(target)
            else:
                stored = str(src)
        stamp = now_iso()
        with self.connect() as con:
            cur = con.execute(
                "INSERT INTO cases(study_id,case_number,study_code,sex,age,image_path,original_filename,file_hash,examiner,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (study_id, n, code, sex, age, stored, original_filename, digest, examiner, stamp, stamp),
            )
            case_id = int(cur.lastrowid)
        self.audit(study_id, "case_added", case_id=case_id, case_number=n, code=code, filename=original_filename)
        return case_id

    def update_case_metadata(self, case_id: int, sex: str | None = None, age: float | None = None, study_code: str | None = None, examiner: str | None = None):
        row = self.case(case_id)
        if not row:
            raise KeyError(case_id)
        vals = {
            "sex": row["sex"] if sex is None else sex,
            "age": row["age"] if age is None else age,
            "study_code": row["study_code"] if study_code is None else study_code.strip(),
            "examiner": row["examiner"] if examiner is None else examiner,
        }
        with self.connect() as con:
            con.execute("UPDATE cases SET sex=?,age=?,study_code=?,examiner=?,updated_at=? WHERE id=?", (vals["sex"], vals["age"], vals["study_code"], vals["examiner"], now_iso(), case_id))
        self.audit(row["study_id"], "case_metadata_updated", case_id=case_id, **vals)

    def attach_image(self, case_id: int, image_path: str, copy_image: bool = True):
        row = self.case(case_id)
        if not row:
            raise KeyError(case_id)
        src = Path(image_path)
        digest = sha256_file(src)
        dup = self.duplicate_info(row["study_id"], filename=src.name, file_hash=digest)
        # Ignore the current row only when replacing its same image.
        with self.connect() as con:
            same = con.execute("SELECT id FROM cases WHERE study_id=? AND file_hash=?", (row["study_id"], digest)).fetchall()
            same = [r[0] for r in same if r[0] != case_id]
        if same:
            raise ValueError("La misma radiografía ya está registrada en otro caso")
        target = src
        if copy_image:
            target = self._study_folder(row["study_id"]) / f"{row['case_number']:04d}_{src.name}"
            shutil.copy2(src, target)
        with self.connect() as con:
            con.execute("UPDATE cases SET image_path=?,original_filename=?,file_hash=?,updated_at=? WHERE id=?", (str(target), src.name, digest, now_iso(), case_id))
        self.audit(row["study_id"], "image_attached", case_id=case_id, filename=src.name, sha256=digest)

    def import_files(self, study_id: int, paths: Iterable[str], metadata: dict[str, dict] | None = None, copy_images: bool = True) -> ImportResult:
        result = ImportResult()
        metadata = metadata or {}
        paths = [str(p) for p in paths if Path(p).suffix.lower() in SUPPORTED_IMAGES]
        remaining = MAX_CASES - self.count_cases(study_id)
        for path in paths[:remaining]:
            name = Path(path).name
            md = metadata.get(name, metadata.get(Path(path).stem, {}))
            code = str(md.get("id") or md.get("code") or "").strip() or None
            try:
                digest = sha256_file(path)
                dups = self.duplicate_info(study_id, code or "", name, digest)
                if dups:
                    result.duplicates += 1
                    continue
                self.add_case(study_id, study_code=code, sex=str(md.get("sex") or ""), age=self._float_or_none(md.get("age")), image_path=path, examiner=str(md.get("examiner") or ""), copy_image=copy_images)
                result.added += 1
            except Exception as exc:
                result.errors.append(f"{name}: {exc}")
                result.skipped += 1
        if len(paths) > remaining:
            result.skipped += len(paths) - remaining
            result.errors.append(f"Se alcanzó el límite de {MAX_CASES} casos")
        self.audit(study_id, "bulk_import", added=result.added, duplicates=result.duplicates, skipped=result.skipped)
        return result

    def import_folder(self, study_id: int, folder: str | Path, metadata_csv: str | None = None, copy_images: bool = True) -> ImportResult:
        folder = Path(folder)
        meta = self.read_metadata_csv(metadata_csv) if metadata_csv else {}
        files = sorted(str(p) for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGES)
        return self.import_files(study_id, files, meta, copy_images)

    @staticmethod
    def read_metadata_csv(path: str | Path) -> dict[str, dict]:
        out: dict[str, dict] = {}
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                normalized = {str(k).strip().lower(): v for k, v in row.items()}
                key = str(normalized.get("archivo") or normalized.get("file") or normalized.get("filename") or normalized.get("id") or normalized.get("codigo") or "").strip()
                if not key:
                    continue
                out[key] = {
                    "id": normalized.get("id") or normalized.get("codigo") or normalized.get("code"),
                    "sex": normalized.get("sexo") or normalized.get("sex"),
                    "age": normalized.get("edad") or normalized.get("age"),
                    "examiner": normalized.get("examinador") or normalized.get("examiner"),
                }
        return out

    @staticmethod
    def _float_or_none(v):
        try:
            return float(str(v).replace(",", ".")) if v not in (None, "") else None
        except Exception:
            return None

    def list_cases(self, study_id: int, status: str | None = None, sex: str | None = None, age_min: float | None = None, age_max: float | None = None, search: str = "", include_excluded: bool = True, random_order: bool = False):
        sql = "SELECT * FROM cases WHERE study_id=?"
        args: list = [study_id]
        if status:
            sql += " AND status=?"; args.append(status)
        if sex:
            sql += " AND sex=?"; args.append(sex)
        if age_min is not None:
            sql += " AND age>=?"; args.append(age_min)
        if age_max is not None:
            sql += " AND age<=?"; args.append(age_max)
        if search:
            sql += " AND (study_code LIKE ? OR original_filename LIKE ? OR CAST(case_number AS TEXT) LIKE ?)"
            q = f"%{search}%"; args.extend([q, q, q])
        if not include_excluded:
            sql += " AND included=1"
        sql += " ORDER BY case_number"
        with self.connect() as con:
            rows = con.execute(sql, args).fetchall()
        rows = list(rows)
        if random_order:
            random.shuffle(rows)
        return rows

    # ---------- Results / landmarks / autosave ----------
    def save_trace(self, case_id: int, protocol_version: int, points: dict[str, tuple[float, float]], results: list[dict], selected_measurements: list[str], mm_per_px: float | None = None):
        case = self.case(case_id)
        if not case:
            raise KeyError(case_id)
        with self.connect() as con:
            lv = con.execute("SELECT COALESCE(MAX(version),0)+1 FROM landmarks WHERE case_id=? AND protocol_version=?", (case_id, protocol_version)).fetchone()[0]
            rv = con.execute("SELECT COALESCE(MAX(version),0)+1 FROM results WHERE case_id=? AND protocol_version=?", (case_id, protocol_version)).fetchone()[0]
            stamp = now_iso()
            for name, (x, y) in points.items():
                con.execute("INSERT INTO landmarks(case_id,protocol_version,name,x,y,version,created_at) VALUES(?,?,?,?,?,?,?)", (case_id, protocol_version, name, float(x), float(y), lv, stamp))
            for r in results:
                con.execute(
                    "INSERT INTO results(case_id,protocol_version,analysis,measurement,value,unit,reference_text,interpretation,version,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (case_id, protocol_version, str(r.get("analysis", "")), str(r.get("measurement", "")), r.get("value"), str(r.get("unit", "")), str(r.get("reference", "")), str(r.get("interpretation", "")), rv, stamp),
                )
            if mm_per_px is not None:
                con.execute("UPDATE cases SET case_mm_per_px=?,updated_at=? WHERE id=?", (mm_per_px, stamp, case_id))
            con.execute("UPDATE cases SET last_opened_at=?,updated_at=? WHERE id=?", (stamp, stamp, case_id))
        self.refresh_case_status(case_id, selected_measurements)
        self.audit(case["study_id"], "trace_saved", case_id=case_id, landmark_version=lv, result_version=rv, landmark_count=len(points), result_count=len(results))

    def latest_landmarks(self, case_id: int, protocol_version: int) -> dict[str, tuple[float, float]]:
        with self.connect() as con:
            v = con.execute("SELECT MAX(version) FROM landmarks WHERE case_id=? AND protocol_version=?", (case_id, protocol_version)).fetchone()[0]
            if v is None:
                return {}
            rows = con.execute("SELECT name,x,y FROM landmarks WHERE case_id=? AND protocol_version=? AND version=?", (case_id, protocol_version, v)).fetchall()
        return {r["name"]: (float(r["x"]), float(r["y"])) for r in rows}

    def latest_results(self, case_id: int, protocol_version: int):
        with self.connect() as con:
            v = con.execute("SELECT MAX(version) FROM results WHERE case_id=? AND protocol_version=?", (case_id, protocol_version)).fetchone()[0]
            if v is None:
                return []
            return con.execute("SELECT * FROM results WHERE case_id=? AND protocol_version=? AND version=? ORDER BY analysis,measurement", (case_id, protocol_version, v)).fetchall()

    def mark_in_progress(self, case_id: int):
        row = self.case(case_id)
        if not row or not row["included"]:
            return
        with self.connect() as con:
            con.execute("UPDATE cases SET status='in_progress',last_opened_at=?,updated_at=? WHERE id=?", (now_iso(), now_iso(), case_id))
        self.audit(row["study_id"], "case_analysis_started", case_id=case_id)

    def refresh_case_status(self, case_id: int, selected_measurements: list[str]) -> str:
        row = self.case(case_id)
        if not row:
            raise KeyError(case_id)
        if not row["included"]:
            return "excluded"
        protocol = self.latest_protocol(row["study_id"])
        results = self.latest_results(case_id, protocol["version"])
        valid = {r["measurement"] for r in results if r["value"] is not None}
        needed = set(selected_measurements)
        if needed and needed.issubset(valid):
            status = "complete"
        elif results or self.latest_landmarks(case_id, protocol["version"]):
            status = "incomplete"
        else:
            status = "pending"
        with self.connect() as con:
            con.execute("UPDATE cases SET status=?,updated_at=? WHERE id=?", (status, now_iso(), case_id))
        return status

    def exclude_case(self, case_id: int, reason: str, note: str = ""):
        row = self.case(case_id)
        if not row:
            raise KeyError(case_id)
        with self.connect() as con:
            con.execute("UPDATE cases SET included=0,status='excluded',exclusion_reason=?,exclusion_note=?,updated_at=? WHERE id=?", (reason.strip(), note.strip(), now_iso(), case_id))
        self.audit(row["study_id"], "case_excluded", case_id=case_id, reason=reason, note=note)

    def restore_case(self, case_id: int):
        row = self.case(case_id)
        if not row:
            raise KeyError(case_id)
        with self.connect() as con:
            con.execute("UPDATE cases SET included=1,status='pending',exclusion_reason='',exclusion_note='',updated_at=? WHERE id=?", (now_iso(), case_id))
        self.audit(row["study_id"], "case_restored", case_id=case_id)

    # ---------- Progress / random / reproducibility ----------
    def progress(self, study_id: int) -> dict:
        with self.connect() as con:
            rows = con.execute("SELECT status,COUNT(*) n FROM cases WHERE study_id=? GROUP BY status", (study_id,)).fetchall()
            sx = con.execute("SELECT sex,COUNT(*) n FROM cases WHERE study_id=? AND included=1 GROUP BY sex", (study_id,)).fetchall()
            ages = con.execute("SELECT MIN(age),MAX(age),AVG(age) FROM cases WHERE study_id=? AND included=1 AND age IS NOT NULL", (study_id,)).fetchone()
        counts = {r["status"]: int(r["n"]) for r in rows}
        total = sum(counts.values())
        return {
            "total": total,
            "pending": counts.get("pending", 0),
            "in_progress": counts.get("in_progress", 0),
            "incomplete": counts.get("incomplete", 0),
            "complete": counts.get("complete", 0),
            "excluded": counts.get("excluded", 0),
            "sex": {r["sex"] or "Sin dato": int(r["n"]) for r in sx},
            "age_min": ages[0], "age_max": ages[1], "age_mean": ages[2],
        }

    def reproducibility_sample(self, study_id: int, n: int, examiner: str = "", round_no: int = 2, seed: int | None = None) -> list[int]:
        rows = self.list_cases(study_id, status="complete", include_excluded=False)
        ids = [r["id"] for r in rows]
        rng = random.Random(seed)
        rng.shuffle(ids)
        selected = ids[: max(0, min(n, len(ids)))]
        with self.connect() as con:
            for case_id in selected:
                con.execute("INSERT OR IGNORE INTO reproducibility(study_id,case_id,examiner,round_no,created_at) VALUES(?,?,?,?,?)", (study_id, case_id, examiner, round_no, now_iso()))
        self.audit(study_id, "reproducibility_sample_created", n=len(selected), examiner=examiner, round_no=round_no, seed=seed)
        return selected

    # ---------- Backup ----------
    def backup_study(self, study_id: int, target_zip: str | Path) -> str:
        target_zip = str(target_zip)
        study_folder = RESEARCH_DIR / f"study_{study_id:04d}"
        with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(self.db_path, arcname="database/yomceph_research.sqlite3")
            if study_folder.exists():
                for p in study_folder.rglob("*"):
                    if p.is_file():
                        z.write(p, arcname=str(Path("study_files") / p.relative_to(study_folder)))
        self.audit(study_id, "backup_created", target=target_zip)
        return target_zip
