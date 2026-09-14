from __future__ import annotations
import sqlite3,tempfile,zipfile
from pathlib import Path
from research_db import ResearchDB
_INSTALLED=False

def create_backup(db,study_id,target,secret=''):
    root=db.study_root(study_id) if hasattr(db,'study_root') else Path(db.db_path).parent/f'study_{study_id:04d}'
    with tempfile.TemporaryDirectory(prefix='yornis_backup_') as td:
        snap=Path(td)/'yornis_research.sqlite3';src=sqlite3.connect(db.db_path);dst=sqlite3.connect(snap)
        try:src.backup(dst);dst.commit()
        finally:dst.close();src.close()
        files=[p for p in root.rglob('*') if p.is_file()] if root.exists() else []
        if secret:
            import pyzipper
            with pyzipper.AESZipFile(target,'w',compression=pyzipper.ZIP_DEFLATED,encryption=pyzipper.WZ_AES) as z:
                z.setpassword(secret.encode('utf-8'));z.write(snap,arcname='database/yornis_research.sqlite3')
                for p in files:z.write(p,arcname=str(Path('study_files')/p.relative_to(root)))
        else:
            with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
                z.write(snap,arcname='database/yornis_research.sqlite3')
                for p in files:z.write(p,arcname=str(Path('study_files')/p.relative_to(root)))
    db.audit(study_id,'backup_created',target=str(target),encrypted=bool(secret),sqlite_snapshot=True);return str(target)

def install():
    global _INSTALLED
    if _INSTALLED:return
    ResearchDB.yornis_backup=create_backup;_INSTALLED=True
