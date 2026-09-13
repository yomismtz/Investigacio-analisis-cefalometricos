from __future__ import annotations
import json
from research_db import ResearchDB, now_iso

_INSTALLED = False

def _ensure_protocol_column(self):
    with self.connect() as con:
        cols = {r[1] for r in con.execute('PRAGMA table_info(cases)').fetchall()}
        if 'protocol_version' not in cols:
            con.execute('ALTER TABLE cases ADD COLUMN protocol_version INTEGER')

def protocol_by_version(self, study_id: int, version: int) -> dict:
    with self.connect() as con:
        row = con.execute('SELECT version,locked,config_json,created_at FROM protocol_versions WHERE study_id=? AND version=?',(study_id,int(version))).fetchone()
    if not row:
        raise KeyError(f'Protocol version {version} does not exist for study {study_id}')
    return {'version':int(row['version']),'locked':bool(row['locked']),'config':json.loads(row['config_json']),'created_at':row['created_at']}

def protocol_versions(self, study_id: int) -> list[dict]:
    with self.connect() as con:
        rows = con.execute('SELECT version,locked,config_json,created_at FROM protocol_versions WHERE study_id=? ORDER BY version',(study_id,)).fetchall()
    return [{'version':int(r['version']),'locked':bool(r['locked']),'config':json.loads(r['config_json']),'created_at':r['created_at']} for r in rows]

def case_protocol_version(self, case_id: int, preferred: int|None=None) -> int:
    row = self.case(case_id)
    if not row: raise KeyError(case_id)
    if 'protocol_version' in row.keys() and row['protocol_version']:
        return int(row['protocol_version'])
    with self.connect() as con:
        hist = con.execute('SELECT MAX(protocol_version) FROM (SELECT protocol_version FROM results WHERE case_id=? UNION ALL SELECT protocol_version FROM landmarks WHERE case_id=?)',(case_id,case_id)).fetchone()[0]
    version = int(hist or preferred or self.latest_protocol(row['study_id'])['version'] or 1)
    with self.connect() as con:
        con.execute('UPDATE cases SET protocol_version=?,updated_at=? WHERE id=?',(version,now_iso(),case_id))
    self.audit(row['study_id'],'case_protocol_pinned',case_id=case_id,protocol_version=version)
    return version

def refresh_case_status(self, case_id: int, _selected=None) -> str:
    row=self.case(case_id)
    if not row: raise KeyError(case_id)
    if not row['included']: return 'excluded'
    version=self.case_protocol_version(case_id)
    cfg=self.protocol_by_version(row['study_id'],version)['config']
    required=set(cfg.get('selected_variables') or [])
    results=self.latest_results(case_id,version)
    valid={f"{r['analysis']}::{r['measurement']}" for r in results if r['value'] is not None}
    if required and required.issubset(valid): status='complete'
    elif results or self.latest_landmarks(case_id,version): status='incomplete'
    else: status='pending'
    with self.connect() as con:
        con.execute('UPDATE cases SET status=?,updated_at=? WHERE id=?',(status,now_iso(),case_id))
    return status

def mark_in_progress(self, case_id: int):
    row=self.case(case_id)
    if not row or not row['included']: return
    version=self.case_protocol_version(case_id); stamp=now_iso()
    if row['status']=='complete':
        with self.connect() as con: con.execute('UPDATE cases SET last_opened_at=?,updated_at=? WHERE id=?',(stamp,stamp,case_id))
        self.audit(row['study_id'],'case_opened_for_review',case_id=case_id,protocol_version=version); return
    with self.connect() as con: con.execute("UPDATE cases SET status='in_progress',last_opened_at=?,updated_at=? WHERE id=?",(stamp,stamp,case_id))
    self.audit(row['study_id'],'case_analysis_started',case_id=case_id,protocol_version=version)

def duplicate_info(self, study_id:int, study_code:str='', filename:str='', file_hash:str='') -> list[str]:
    reasons=[]
    with self.connect() as con:
        if study_code and con.execute('SELECT 1 FROM cases WHERE study_id=? AND study_code=?',(study_id,study_code)).fetchone(): reasons.append('ID/código repetido')
        if file_hash and con.execute('SELECT 1 FROM cases WHERE study_id=? AND file_hash=?',(study_id,file_hash)).fetchone(): reasons.append('archivo idéntico (SHA-256)')
    return reasons

def update_study_info(self, study_id:int, title:str, researcher:str, institution:str, objective:str, blind_mode:bool):
    with self.connect() as con:
        con.execute('UPDATE studies SET title=?,researcher=?,institution=?,objective=?,blind_mode=?,updated_at=? WHERE id=?',(title.strip(),researcher.strip(),institution.strip(),objective.strip(),int(bool(blind_mode)),now_iso(),study_id))
    self.audit(study_id,'study_metadata_updated',title=title,researcher=researcher,institution=institution,objective=objective,blind_mode=bool(blind_mode))

def set_review_flag(self, case_id:int, value:bool):
    row=self.case(case_id)
    if not row: raise KeyError(case_id)
    with self.connect() as con: con.execute('UPDATE cases SET review_flag=?,updated_at=? WHERE id=?',(int(bool(value)),now_iso(),case_id))
    self.audit(row['study_id'],'case_review_flag_changed',case_id=case_id,review_flag=bool(value))

def install():
    global _INSTALLED
    if _INSTALLED:return
    old_init=ResearchDB.__init__
    def init(self,*a,**kw): old_init(self,*a,**kw); _ensure_protocol_column(self)
    ResearchDB.__init__=init
    ResearchDB.protocol_by_version=protocol_by_version
    ResearchDB.protocol_versions=protocol_versions
    ResearchDB.case_protocol_version=case_protocol_version
    ResearchDB.refresh_case_status=refresh_case_status
    ResearchDB.mark_in_progress=mark_in_progress
    ResearchDB.duplicate_info=duplicate_info
    ResearchDB.update_study_info=update_study_info
    ResearchDB.set_review_flag=set_review_flag
    old_save=ResearchDB.save_trace
    def save_trace(self,case_id,protocol_version,points,results,selected_measurements,mm_per_px=None):
        pinned=self.case_protocol_version(case_id,int(protocol_version))
        if int(protocol_version)!=pinned: raise ValueError(f'El caso está vinculado al protocolo v{pinned}; no puede guardarse como v{protocol_version}.')
        return old_save(self,case_id,pinned,points,results,selected_measurements,mm_per_px)
    ResearchDB.save_trace=save_trace
    old_restore=ResearchDB.restore_case
    def restore(self,case_id): old_restore(self,case_id); return self.refresh_case_status(case_id)
    ResearchDB.restore_case=restore
    _INSTALLED=True
