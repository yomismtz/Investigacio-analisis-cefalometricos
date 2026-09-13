from __future__ import annotations
import random
from pathlib import Path
from research_db import RESEARCH_DIR, ResearchDB, now_iso
_INSTALLED=False

def migrate(db):
    with db.connect() as con:
        cols={r[1] for r in con.execute('PRAGMA table_info(studies)').fetchall()}
        if 'storage_root' not in cols: con.execute("ALTER TABLE studies ADD COLUMN storage_root TEXT DEFAULT ''")
        if 'random_seed' not in cols: con.execute('ALTER TABLE studies ADD COLUMN random_seed INTEGER DEFAULT 15031992')

def set_storage_root(db,study_id,root):
    root=str(Path(root).expanduser().resolve()) if root else ''
    if root:Path(root).mkdir(parents=True,exist_ok=True)
    with db.connect() as con:con.execute('UPDATE studies SET storage_root=?,updated_at=? WHERE id=?',(root,now_iso(),study_id))
    db.audit(study_id,'storage_root_changed',storage_root=root)

def study_root(db,study_id):
    s=db.study(study_id);root=str(s['storage_root'] or '').strip() if s and 'storage_root' in s.keys() else ''
    return Path(root)/f'Yornis_study_{study_id:04d}' if root else RESEARCH_DIR/f'study_{study_id:04d}'

def study_folder(db,study_id):
    p=db.study_root(study_id)/'images';p.mkdir(parents=True,exist_ok=True);return p

def set_random_seed(db,study_id,seed):
    with db.connect() as con:con.execute('UPDATE studies SET random_seed=?,updated_at=? WHERE id=?',(int(seed),now_iso(),study_id))
    db.audit(study_id,'random_seed_changed',seed=int(seed))

def random_seed(db,study_id):
    try:return int(db.study(study_id)['random_seed'])
    except Exception:return 15031992

def install():
    global _INSTALLED
    if _INSTALLED:return
    old=ResearchDB.__init__
    def init(self,*a,**kw):old(self,*a,**kw);migrate(self)
    ResearchDB.__init__=init;ResearchDB.set_storage_root=set_storage_root;ResearchDB.study_root=study_root;ResearchDB._study_folder=study_folder;ResearchDB.set_random_seed=set_random_seed;ResearchDB.random_seed=random_seed
    _INSTALLED=True
