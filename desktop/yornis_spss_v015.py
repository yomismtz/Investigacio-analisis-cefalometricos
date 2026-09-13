from __future__ import annotations
import csv,re
from pathlib import Path
from research_protocol import selected_variables

def safe_name(text,used):
    s=re.sub(r'[^A-Za-z0-9_]+','_',text).strip('_') or 'VAR';s=('V_'+s if s[0].isdigit() else s)[:60];base=s;i=2
    while s.lower() in used:s=(base[:55]+f'_{i}')[:60];i+=1
    used.add(s.lower());return s

def export_spss(db,study_id,protocol,target_sps):
    target=Path(target_sps);csv_path=target.with_suffix('.csv');variables=selected_variables(protocol.get('selected_variables') or []);used=set();mapping={v.key:safe_name(v.key,used) for v in variables}
    headers=['case_number','study_code','sex','age','status','included','protocol_version']+[mapping[v.key] for v in variables]
    with csv_path.open('w',newline='',encoding='utf-8-sig') as fh:
        w=csv.DictWriter(fh,fieldnames=headers);w.writeheader()
        for c in db.list_cases(study_id,include_excluded=True):
            pv=db.case_protocol_version(c['id']) if hasattr(db,'case_protocol_version') else protocol.get('version',1);vals={f"{r['analysis']}::{r['measurement']}":r['value'] for r in db.latest_results(c['id'],pv)}
            row={'case_number':c['case_number'],'study_code':c['study_code'],'sex':c['sex'],'age':c['age'],'status':c['status'],'included':c['included'],'protocol_version':pv}
            for v in variables:row[mapping[v.key]]=vals.get(v.key)
            w.writerow(row)
    q=str(csv_path.resolve()).replace('\\','/')
    lines=[f"GET DATA /TYPE=TXT /FILE='{q}' /ENCODING='UTF8' /DELCASE=LINE /DELIMITERS=',' /QUALIFIER='\"' /ARRANGEMENT=DELIMITED /FIRSTCASE=2 /IMPORTCASE=ALL.","CACHE.","EXECUTE."]
    for v in variables:lines.append(f"VARIABLE LABELS {mapping[v.key]} '{v.analysis}: {v.name}'.")
    lines += ["VALUE LABELS included 0 'Excluido' 1 'Incluido'.","EXECUTE."]
    target.write_text('\n'.join(lines),encoding='utf-8');db.audit(study_id,'export_spss',target=str(target),csv=str(csv_path));return str(target),str(csv_path)
