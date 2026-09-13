from __future__ import annotations
import shutil
from pathlib import Path
from research_db import MAX_CASES, ImportResult, ResearchDB, now_iso, sha256_file
_INSTALLED=False

def add_case(db,study_id,study_code=None,sex='',age=None,image_path='',examiner='',copy_image=True):
    if db.count_cases(study_id)>=MAX_CASES:raise ValueError(f'El estudio ya contiene el máximo de {MAX_CASES} casos')
    n=db.next_case_number(study_id);code=(study_code or f'{n:04d}').strip();src=Path(image_path) if image_path else None
    original=src.name if src else '';digest=sha256_file(src) if src and src.exists() else ''
    dup=db.duplicate_info(study_id,code,original,digest)
    if dup:raise ValueError('Duplicado: '+', '.join(dup))
    stored=''
    if src:
        if copy_image:
            target=db._study_folder(study_id)/f'YC_{n:04d}{src.suffix.lower() or ".img"}';shutil.copy2(src,target);stored=str(target)
        else:stored=str(src)
    stamp=now_iso()
    with db.connect() as con:
        cur=con.execute('INSERT INTO cases(study_id,case_number,study_code,sex,age,image_path,original_filename,file_hash,examiner,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(study_id,n,code,sex,age,stored,original,digest,examiner,stamp,stamp));cid=int(cur.lastrowid)
    db.audit(study_id,'case_added',case_id=cid,case_number=n,code=code,source_filename=original,stored_filename=Path(stored).name if stored else '',anonymized=bool(copy_image));return cid

def import_progress(db,study_id,paths,metadata=None,copy_images=True,callback=None,cancel_event=None):
    result=ImportResult();metadata=metadata or {};allowed={'.png','.jpg','.jpeg','.bmp','.tif','.tiff','.pdf'};paths=[str(p) for p in paths if Path(p).suffix.lower() in allowed]
    remaining=MAX_CASES-db.count_cases(study_id);chosen=paths[:remaining]
    for idx,path in enumerate(chosen,1):
        if cancel_event and cancel_event.is_set():result.skipped+=len(chosen)-idx+1;break
        name=Path(path).name;md=metadata.get(name,metadata.get(Path(path).stem,{}));code=str(md.get('id') or md.get('code') or '').strip() or None
        try:
            digest=sha256_file(path)
            if db.duplicate_info(study_id,code or '',name,digest):result.duplicates+=1
            else:db.add_case(study_id,code,str(md.get('sex') or ''),db._float_or_none(md.get('age')),path,str(md.get('examiner') or ''),copy_images);result.added+=1
        except Exception as exc:result.errors.append(f'{name}: {exc}');result.skipped+=1
        if callback:callback(idx,len(chosen),result)
    if len(paths)>remaining:result.skipped+=len(paths)-remaining;result.errors.append(f'Se alcanzó el límite de {MAX_CASES} casos')
    db.audit(study_id,'bulk_import',added=result.added,duplicates=result.duplicates,skipped=result.skipped,anonymized=bool(copy_images));return result

def install():
    global _INSTALLED
    if _INSTALLED:return
    ResearchDB.add_case=add_case;ResearchDB.import_files_progress=import_progress;_INSTALLED=True
