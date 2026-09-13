from __future__ import annotations
import tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from research_protocol import selected_variables
import yornis_theme

def annotated_image(db,case_id,target):
    c=db.case(case_id);pv=db.case_protocol_version(case_id);points=db.latest_landmarks(case_id,pv);proto=db.protocol_by_version(c['study_id'],pv)['config'];im=Image.open(c['image_path']).convert('RGB');draw=ImageDraw.Draw(im,'RGBA');theme=yornis_theme.THEMES[yornis_theme.current_theme_name()]
    def rgb(h,a=255):h=h.lstrip('#');return tuple(int(h[i:i+2],16) for i in (0,2,4))+(a,)
    line=rgb(theme['tertiary'],95);dot=rgb(theme['accent'],235);ring=rgb(theme['primary'],235)
    seen=set()
    for v in selected_variables(proto.get('selected_variables') or []):
        ps=[points[p] for p in v.points if p in points]
        for a,b in zip(ps,ps[1:]):
            key=tuple(sorted((a,b)))
            if key not in seen:draw.line([a,b],fill=line,width=1);seen.add(key)
    r=2
    for name,(x,y) in points.items():
        draw.ellipse((x-r,y-r,x+r,y+r),fill=dot,outline=ring,width=1);draw.text((x+5,y-9),name,fill=(255,255,255,230))
    im.thumbnail((1600,1600),Image.Resampling.LANCZOS);im.save(target,quality=92);return target

def export_case_pdf(db,case_id,path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image as RLImage
    c=db.case(case_id);study=db.study(c['study_id']);pv=db.case_protocol_version(case_id);rows=db.latest_results(case_id,pv);styles=getSampleStyleSheet();theme=yornis_theme.THEMES[yornis_theme.current_theme_name()];doc=SimpleDocTemplate(path,pagesize=A4,rightMargin=28,leftMargin=28,topMargin=30,bottomMargin=30);story=[Paragraph('Yornis — Yom Dental Análisis',styles['Title']),Paragraph(f"Estudio: {study['title']} · Caso: {c['study_code']} · Protocolo v{pv}",styles['BodyText']),Spacer(1,8)]
    with tempfile.TemporaryDirectory(prefix='yornis_report_') as td:
        if c['image_path'] and Path(c['image_path']).exists() and not str(c['image_path']).lower().endswith('.pdf'):
            img=annotated_image(db,case_id,Path(td)/'annotated.jpg');ri=RLImage(str(img));ri._restrictSize(520,340);story += [ri,Spacer(1,8)]
        data=[['Análisis','Medición','Valor','Unidad','Referencia']]
        for r in rows:data.append([r['analysis'],r['measurement'],'' if r['value'] is None else f"{r['value']:.3f}",r['unit'],r['reference_text']])
        t=Table(data,repeatRows=1,colWidths=[82,145,55,45,190]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(theme['primary'])),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.25,colors.HexColor(theme['border'])),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),7)]));story += [t,Spacer(1,8),Paragraph('Yom Dental Análisis · Uso educativo y de investigación. El QC es técnico/geométrico y no equivale a validación clínica.',styles['Italic'])];doc.build(story)
    db.audit(c['study_id'],'export_case_pdf_yornis',case_id=case_id,target=path,protocol_version=pv);return path
