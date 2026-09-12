from __future__ import annotations
import csv, json, shutil, sqlite3, sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

HOST=None
ORIG={}
INCLUSION=['Radiografía lateral de cráneo disponible','Edad cronológica disponible','Sexo registrado disponible','Calidad radiográfica suficiente para localizar landmarks','Anatomía de interés completamente visible','Radiografía sin deformación geométrica evidente','Calibración disponible cuando se requieran medidas lineales']
EXCLUSION=['Calidad radiográfica insuficiente','Movimiento, desenfoque o artefactos','Anatomía incompleta o fuera del campo','Landmarks requeridos no localizables','Calibración imposible cuando es necesaria','Radiografía duplicada','Edad fuera del rango del protocolo','Sexo fuera del protocolo','Alteración anatómica fuera de criterios']
REASONS=['Calidad radiográfica insuficiente','No fue posible localizar uno o más puntos requeridos','Movimiento / desenfoque / artefactos','Anatomía incompleta o fuera del campo','Calibración imposible','Radiografía duplicada','No cumple edad del protocolo','No cumple sexo del protocolo','Otro motivo metodológico']
SPECIAL={'Sassouni':['Arquitectura de cuatro planos'],'CVM C2–C4':['Estadio CVM registrado']}
SASS_POINTS=['Sella inf.','ACB post.','ACB ant.','PNS','ANS','Sass Oc post.','Sass Oc ant.','Mand base post.','Mand base ant.','N','Me','FE','U1i','Pg','Sp','Go']

def now(): return datetime.now().isoformat(timespec='seconds')
def tr(self,es,en): return en if getattr(self,'lang','es')=='en' else es

def arg_lang():
    for a in sys.argv[1:]:
        if a.lower().startswith('--lang='):
            v=a.split('=',1)[1].lower(); return 'en' if v.startswith('eng') or v=='en' else 'es'
    return None

def lang_path(): return HOST['APPDIR']/'language.txt'
def read_lang():
    a=arg_lang()
    if a:return a
    try:
        v=lang_path().read_text(encoding='utf-8').strip(); return v if v in ('es','en') else 'es'
    except Exception:return 'es'
def write_lang(v):
    try:lang_path().write_text(v,encoding='utf-8')
    except Exception:pass

def measure_choices(a):
    out=[m.name for m in HOST['MEASUREMENTS'] if m.analysis==a]
    for n in SPECIAL.get(a,[]):
        if n not in out:out.append(n)
    return out

def selected_names(self,a):
    if self.mode!='research':return measure_choices(a)
    p=self.study_protocol or {}; sm=(p.get('measurements') or {}).get(a)
    return list(sm) if sm is not None else measure_choices(a)

def active_measurements(self):
    return [m for m in HOST['MEASUREMENTS'] if m.analysis in self.selected_analyses and m.name in selected_names(self,m.analysis)]

def expected_results(self):
    return {(a,n) for a in self.selected_analyses for n in selected_names(self,a)}

def research_completion(self):
    expected=expected_results(self); got={(r.get('analysis'),r.get('name')) for r in self.results if r.get('display') not in ('—','')};missing=sorted(expected-got)
    return (not missing,missing)

def patched_init(self,*a,**kw):
    ORIG['__init__'](self,*a,**kw); self.lang=read_lang(); self.title(f"YomCeph Desktop · v{HOST['APP_VERSION']}"); self.build_menu(); self.show_home()

def build_menu(self): ORIG['build_menu'](self)

def show_home(self):
    self.clear_root(); self.workspace=None; p=self.palette
    outer=ttk.Frame(self,padding=28);outer.pack(fill='both',expand=True)
    if self.logo_img:ttk.Label(outer,image=self.logo_img).pack(pady=(15,5))
    ttk.Label(outer,text=tr(self,'¿Qué vamos a hacer hoy?','What are we doing today?'),style='Title.TLabel').pack(pady=8)
    ttk.Label(outer,text=tr(self,'Elige el flujo; YomCeph mostrará sólo lo necesario.','Choose the workflow; YomCeph will show only what is needed.'),style='Subtitle.TLabel').pack()
    cards=ttk.Frame(outer);cards.pack(expand=True,pady=25)
    for c,(title,desc,cmd) in enumerate([(tr(self,'👤  Caso individual','👤  Individual case'),tr(self,'Una radiografía para análisis individual.','One radiograph for individual analysis.'),self.start_individual),(tr(self,'📊  Investigación','📊  Research'),tr(self,'Protocolo, checklist, análisis/resultados, hasta 1000 radiografías y base de datos.','Protocol, checklist, analyses/outcomes, up to 1000 radiographs and database.'),self.new_research)]):
        f=tk.Frame(cards,bg=p['panel'],highlightbackground=p['border'],highlightthickness=1,width=430,height=280);f.grid(row=0,column=c,padx=15);f.grid_propagate(False)
        if self.logo_small:tk.Label(f,image=self.logo_small,bg=p['panel']).pack(anchor='w',padx=24,pady=(25,8))
        tk.Label(f,text=title,bg=p['panel'],fg=p['primary_dark'],font=('Segoe UI',self.font_size+5,'bold')).pack(anchor='w',padx=24)
        tk.Label(f,text=desc,bg=p['panel'],fg=p['muted'],wraplength=370,justify='left').pack(anchor='w',padx=24,pady=18)
        ttk.Button(f,text=tr(self,'Continuar','Continue'),style='Accent.TButton',command=cmd).pack(anchor='w',padx=24)
        if c==1:ttk.Button(f,text=tr(self,'Abrir investigación existente','Open existing study'),command=self.open_research).pack(anchor='w',padx=24,pady=8)

def open_research(self):
    con=sqlite3.connect(HOST['DB_PATH']);rows=con.execute('SELECT id,name,planned_sample,locked,updated_at FROM studies ORDER BY updated_at DESC').fetchall();con.close()
    if not rows:return messagebox.showinfo('YomCeph',tr(self,'No hay investigaciones guardadas.','No saved studies.'))
    w=tk.Toplevel(self);w.title('YomCeph · '+tr(self,'Investigaciones','Studies'));w.geometry('820x470')
    t=ttk.Treeview(w,columns=('n','lock','date'),show='tree headings');t.heading('#0',text=tr(self,'Investigación','Study'));t.heading('n',text=tr(self,'Muestra','Sample'));t.heading('lock',text=tr(self,'Protocolo','Protocol'));t.heading('date',text=tr(self,'Actualizado','Updated'));t.pack(fill='both',expand=True,padx=15,pady=15)
    for r in rows:t.insert('', 'end',iid=str(r[0]),text=r[1],values=(r[2],tr(self,'Bloqueado' if r[3] else 'Editable','Locked' if r[3] else 'Editable'),r[4]))
    def go(e=None):
        s=t.selection()
        if s:w.destroy();self.activate_study(int(s[0]))
    t.bind('<Double-1>',go);ttk.Button(w,text=tr(self,'Abrir','Open'),style='Accent.TButton',command=go).pack(pady=8)

def open_protocol_editor(self,study_id=None):
    con=sqlite3.connect(HOST['DB_PATH']);row=con.execute('SELECT name,planned_sample,protocol_json,locked FROM studies WHERE id=?',(study_id,)).fetchone() if study_id else None;con.close()
    p=json.loads(row[2]) if row else {}; locked=bool(row[3]) if row else False
    w=tk.Toplevel(self);w.title('YomCeph · '+tr(self,'Protocolo de investigación','Research protocol'));w.geometry('1100x800');w.transient(self);w.grab_set()
    nb=ttk.Notebook(w);nb.pack(fill='both',expand=True,padx=12,pady=12);d=ttk.Frame(nb,padding=14);a=ttk.Frame(nb,padding=14);r=ttk.Frame(nb,padding=14);nb.add(d,text=tr(self,'1 · Datos y criterios','1 · Data & criteria'));nb.add(a,text=tr(self,'2 · Análisis y resultados','2 · Analyses & outcomes'));nb.add(r,text=tr(self,'3 · Revisar','3 · Review'))
    vals={k:tk.StringVar(value=str(p.get(k,''))) for k in ('name','planned_sample','age_min','age_max','country','institution')}; vals['name'].set(vals['name'].get() or (row[0] if row else '')); vals['planned_sample'].set(vals['planned_sample'].get() or (str(row[1]) if row else '100'))
    for i,(k,label) in enumerate([('name','Nombre'),('planned_sample','Muestra planeada (1–1000)'),('age_min','Edad mínima'),('age_max','Edad máxima'),('country','País'),('institution','Institución')]):ttk.Label(d,text=label+':').grid(row=i,column=0,sticky='w',pady=4);ttk.Entry(d,textvariable=vals[k],width=55,state='disabled' if locked else 'normal').grid(row=i,column=1,sticky='ew',pady=4)
    male=tk.BooleanVar(value=p.get('include_male',True));female=tk.BooleanVar(value=p.get('include_female',True));ttk.Checkbutton(d,text=tr(self,'Hombres','Male'),variable=male,state='disabled' if locked else 'normal').grid(row=6,column=0,sticky='w');ttk.Checkbutton(d,text=tr(self,'Mujeres','Female'),variable=female,state='disabled' if locked else 'normal').grid(row=6,column=1,sticky='w')
    inc={x:tk.BooleanVar(value=x in p.get('inclusion_checks',INCLUSION)) for x in INCLUSION};exc={x:tk.BooleanVar(value=x in p.get('exclusion_checks',EXCLUSION)) for x in EXCLUSION}
    box=ttk.Frame(d);box.grid(row=7,column=0,columnspan=2,sticky='nsew',pady=10);left=ttk.LabelFrame(box,text='Inclusión',padding=8);right=ttk.LabelFrame(box,text='Exclusión',padding=8);left.pack(side='left',fill='both',expand=True,padx=5);right.pack(side='left',fill='both',expand=True,padx=5)
    for x,v in inc.items():ttk.Checkbutton(left,text=x,variable=v,state='disabled' if locked else 'normal').pack(anchor='w')
    for x,v in exc.items():ttk.Checkbutton(right,text=x,variable=v,state='disabled' if locked else 'normal').pack(anchor='w')
    av={x:tk.BooleanVar(value=x in p.get('analyses',[])) for x in HOST['ANALYSES']}; selected={x:set((p.get('measurements') or {}).get(x,measure_choices(x))) for x in HOST['ANALYSES']}
    canvas=tk.Canvas(a,highlightthickness=0);sb=ttk.Scrollbar(a,orient='vertical',command=canvas.yview);inner=ttk.Frame(canvas);canvas.create_window((0,0),window=inner,anchor='nw');inner.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')));canvas.configure(yscrollcommand=sb.set);canvas.pack(side='left',fill='both',expand=True);sb.pack(side='right',fill='y')
    def outcomes(an):
        q=tk.Toplevel(w);q.title(an);q.geometry('720x620');f=ttk.Frame(q,padding=12);f.pack(fill='both',expand=True);ttk.Label(f,text=tr(self,'Seleccione sólo los resultados del estudio','Select only study outcomes'),style='Section.TLabel').pack(anchor='w');fr=ttk.Frame(f);fr.pack(fill='both',expand=True,pady=8);vs={n:tk.BooleanVar(value=n in selected[an]) for n in measure_choices(an)}
        for n,v in vs.items():ttk.Checkbutton(fr,text=n,variable=v,state='disabled' if locked else 'normal').pack(anchor='w')
        def ok():selected[an]={n for n,v in vs.items() if v.get()};q.destroy()
        ttk.Button(f,text='OK',style='Accent.TButton',command=ok).pack(anchor='e')
    for i,an in enumerate(HOST['ANALYSES']):
        rowf=ttk.Frame(inner);rowf.grid(row=i,column=0,sticky='ew',pady=4);ttk.Checkbutton(rowf,text=an,variable=av[an],state='disabled' if locked else 'normal').pack(side='left');ttk.Button(rowf,text=tr(self,'Resultados…','Outcomes…'),command=lambda x=an:outcomes(x)).pack(side='right')
    summary=tk.Text(r,wrap='word');summary.pack(fill='both',expand=True)
    def refresh_summary(e=None):
        ans=[x for x,v in av.items() if v.get()];summary.config(state='normal');summary.delete('1.0','end');summary.insert('end',f"{vals['name'].get()}\n\n"+tr(self,f"Muestra planeada: {vals['planned_sample'].get()} (máx. 1000)\n",f"Planned sample: {vals['planned_sample'].get()} (max 1000)\n")+'\n'.join(f'• {x}: {len(selected[x])}' for x in ans));summary.config(state='disabled')
    nb.bind('<<NotebookTabChanged>>',refresh_summary)
    def save():
        try:n=int(vals['planned_sample'].get())
        except Exception:n=0
        ans=[x for x,v in av.items() if v.get()]
        if not vals['name'].get().strip() or not 1<=n<=1000 or not ans or any(not selected[x] for x in ans):return messagebox.showwarning('YomCeph',tr(self,'Revise nombre, muestra y resultados seleccionados.','Check name, sample and selected outcomes.'),parent=w)
        proto={k:vals[k].get().strip() for k in vals};proto['planned_sample']=n;proto.update(include_male=male.get(),include_female=female.get(),inclusion_checks=[x for x,v in inc.items() if v.get()],exclusion_checks=[x for x,v in exc.items() if v.get()],analyses=ans,measurements={x:sorted(selected[x]) for x in ans})
        con=sqlite3.connect(HOST['DB_PATH']);ts=now()
        if study_id:con.execute('UPDATE studies SET name=?,planned_sample=?,protocol_json=?,updated_at=? WHERE id=?',(proto['name'],n,json.dumps(proto,ensure_ascii=False),ts,study_id));sid=study_id
        else:sid=con.execute('INSERT INTO studies(name,planned_sample,protocol_json,locked,created_at,updated_at) VALUES(?,?,?,?,?,?)',(proto['name'],n,json.dumps(proto,ensure_ascii=False),0,ts,ts)).lastrowid
        con.commit();con.close();w.destroy();self.activate_study(sid)
    ttk.Button(w,text=tr(self,'Guardar y continuar','Save & continue'),style='Accent.TButton',command=save).pack(pady=(0,12))

def activate_study(self,sid):
    con=sqlite3.connect(HOST['DB_PATH']);row=con.execute('SELECT name,protocol_json FROM studies WHERE id=?',(sid,)).fetchone();con.close()
    if not row:return
    self.mode='research';self.active_study_id=sid;self.active_study_name=row[0];self.study_protocol=json.loads(row[1]);self.selected_analyses=set(self.study_protocol.get('analyses') or []);self.new_case(reset_view=False);self.build_workspace();self.after(100,self.open_database_browser)

def apply_analysis_selection(self):
    if not self.workspace:return
    pts=[]
    for m in active_measurements(self):
        for k in m.pts:
            if k not in pts:pts.append(k)
        if m.kind.startswith('hp_'):
            for k in ('S','N','Po','Or','Me'):
                if k not in pts:pts.append(k)
    if 'Sassouni' in self.selected_analyses and 'Arquitectura de cuatro planos' in selected_names(self,'Sassouni'):
        for k in SASS_POINTS:
            if k not in pts:pts.append(k)
    self.landmarks=pts;self.current_index=min(self.current_index,max(0,len(pts)-1));self.refresh_point_list();self.analysis_label.config(text=', '.join(a for a in HOST['ANALYSES'] if a in self.selected_analyses));self.update_references_tab();self.redraw()

def open_analysis_selector(self):
    if self.mode=='research' and self.active_study_id:return self.open_protocol_editor(self.active_study_id)
    return ORIG['open_analysis_selector'](self)

def calculate(self):
    ORIG['calculate'](self)
    if self.mode!='research':return
    keep=expected_results(self);self.results=[r for r in self.results if (r.get('analysis'),r.get('name')) in keep];self.render_results();self.render_qc();self.render_summary()

def evaluate_research_eligibility(self):
    p=self.study_protocol or {};reasons=[]
    try:age=float(self.metadata.get('age',''))
    except Exception:age=None;reasons.append('Edad incompleta o no válida')
    try:
        if age is not None and str(p.get('age_min','')).strip() and age<float(p['age_min']):reasons.append('Edad menor que el mínimo del protocolo')
        if age is not None and str(p.get('age_max','')).strip() and age>float(p['age_max']):reasons.append('Edad mayor que el máximo del protocolo')
    except Exception:pass
    sex=self.metadata.get('sex','')
    if sex=='male' and not p.get('include_male',True):reasons.append('Sexo fuera del protocolo')
    if sex=='female' and not p.get('include_female',True):reasons.append('Sexo fuera del protocolo')
    missing=[k for k in self.landmarks if k not in self.points]
    if missing:reasons.append(f'Landmarks faltantes: {len(missing)}')
    if any(m.unit=='mm' for m in active_measurements(self)) and not self.mm_per_px:reasons.append('Falta calibración para mediciones lineales')
    complete,miss=research_completion(self)
    if miss:reasons.append(f'Resultados faltantes: {len(miss)}')
    if any(x.startswith('Edad') or x.startswith('Sexo') for x in reasons):return 'excluded',reasons
    return ('included',[]) if not reasons else ('incomplete',reasons)

def copy_rx(self,src,cid):
    folder=HOST['APPDIR']/'cases'/HOST['safe_case_id'](cid);folder.mkdir(parents=True,exist_ok=True);dst=folder/('radiograph'+Path(src).suffix.lower());shutil.copy2(src,dst);return str(dst)

def import_radiographs(self,refresh=None):
    files=filedialog.askopenfilenames(title=tr(self,'Seleccionar radiografías (hasta 1000)','Select radiographs (up to 1000)'),filetypes=[('Radiografías','*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.pdf'),('Todos','*.*')])
    if not files:return
    con=sqlite3.connect(HOST['DB_PATH']);current=con.execute('SELECT COUNT(*) FROM cases WHERE research_study_id=?',(self.active_study_id,)).fetchone()[0];room=max(0,1000-current);files=list(files)[:room]
    for src in files:
        base=HOST['safe_case_id'](Path(src).stem);cid=base;i=2
        while con.execute('SELECT 1 FROM cases WHERE case_id=?',(cid,)).fetchone():cid=f'{base}_{i}';i+=1
        meta={'case_id':cid,'age':'','sex':'','country':(self.study_protocol or {}).get('country',''),'source_filename':Path(src).name};stored=copy_rx(self,src,cid);ts=now()
        con.execute('INSERT INTO cases(case_id,research_study_id,mode,metadata_json,analysis_json,points_json,results_json,image_path,stored_image_path,mm_per_pixel,face_direction,eligibility,eligibility_reasons_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(cid,self.active_study_id,'research',json.dumps(meta,ensure_ascii=False),json.dumps(sorted(self.selected_analyses)),'{}','[]',src,stored,None,'right','pending','[]',ts,ts))
    con.commit();con.close()
    if refresh:refresh()

def add_manual_research_case(self,refresh=None):
    cid=simpledialog.askstring('YomCeph',tr(self,'Número / ID del caso:','Case number / ID:'),parent=self)
    if not cid:return
    cid=HOST['safe_case_id'](cid);age=simpledialog.askstring('YomCeph',tr(self,'Edad en años:','Age in years:'),parent=self) or '';sex=simpledialog.askstring('YomCeph',tr(self,'Sexo registrado: male / female','Recorded sex: male / female'),parent=self) or ''
    meta={'case_id':cid,'age':age,'sex':sex.lower(),'country':(self.study_protocol or {}).get('country','')};ts=now();con=sqlite3.connect(HOST['DB_PATH'])
    try:con.execute('INSERT INTO cases(case_id,research_study_id,mode,metadata_json,analysis_json,points_json,results_json,image_path,stored_image_path,mm_per_pixel,face_direction,eligibility,eligibility_reasons_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(cid,self.active_study_id,'research',json.dumps(meta,ensure_ascii=False),json.dumps(sorted(self.selected_analyses)),'{}','[]','','',None,'right','pending','[]',ts,ts));con.commit()
    except sqlite3.IntegrityError:messagebox.showwarning('YomCeph',tr(self,'Ese ID ya existe.','That ID already exists.'))
    con.close()
    if refresh:refresh()

def edit_meta(self,cid,refresh=None):
    con=sqlite3.connect(HOST['DB_PATH']);row=con.execute('SELECT metadata_json FROM cases WHERE case_id=?',(cid,)).fetchone()
    if not row:con.close();return
    m=json.loads(row[0] or '{}');m['age']=simpledialog.askstring('YomCeph','Edad / Age:',initialvalue=m.get('age',''),parent=self) or m.get('age','');m['sex']=(simpledialog.askstring('YomCeph','Sexo / Sex (male/female):',initialvalue=m.get('sex',''),parent=self) or m.get('sex','')).lower();con.execute('UPDATE cases SET metadata_json=?,updated_at=? WHERE case_id=?',(json.dumps(m,ensure_ascii=False),now(),cid));con.commit();con.close()
    if refresh:refresh()

def exclude_case(self,cid,refresh=None):
    if not cid:return
    q=tk.Toplevel(self);q.title(tr(self,'Motivo de exclusión','Exclusion reason'));v=tk.StringVar(value=REASONS[0]);ttk.Combobox(q,textvariable=v,values=REASONS,state='readonly',width=62).pack(padx=15,pady=15)
    def ok():
        con=sqlite3.connect(HOST['DB_PATH']);con.execute("UPDATE cases SET eligibility='excluded',eligibility_reasons_json=?,updated_at=? WHERE case_id=?",(json.dumps([v.get()],ensure_ascii=False),now(),cid));con.commit();con.close();q.destroy();refresh and refresh()
    ttk.Button(q,text='OK',style='Accent.TButton',command=ok).pack(pady=(0,15))

def restore_case(self,cid,refresh=None):
    con=sqlite3.connect(HOST['DB_PATH']);con.execute("UPDATE cases SET eligibility='pending',eligibility_reasons_json='[]',updated_at=? WHERE case_id=?",(now(),cid));con.commit();con.close();refresh and refresh()

def open_database_browser(self):
    if self.mode!='research' or not self.active_study_id:return ORIG['open_database_browser'](self)
    w=tk.Toplevel(self);w.title('YomCeph · '+tr(self,'Base de investigación','Research database'));w.geometry('1240x720');f=ttk.Frame(w,padding=12);f.pack(fill='both',expand=True);ttk.Label(f,text=self.active_study_name,style='Title.TLabel').pack(anchor='w');sub=ttk.Label(f,style='Subtitle.TLabel');sub.pack(anchor='w')
    t=ttk.Treeview(f,columns=('status','sex','age','file','reason'),show='tree headings');t.heading('#0',text=tr(self,'Número','Number'));t.heading('status',text=tr(self,'Estado','Status'));t.heading('sex',text=tr(self,'Sexo','Sex'));t.heading('age',text=tr(self,'Edad','Age'));t.heading('file',text=tr(self,'Radiografía','Radiograph'));t.heading('reason',text=tr(self,'Motivo / nota','Reason / note'));t.pack(fill='both',expand=True,pady=8);t.tag_configure('complete',foreground='#18864B');t.tag_configure('excluded',foreground='#B33A3A');t.tag_configure('incomplete',foreground='#C47A00');t.tag_configure('pending',foreground='#6D6576')
    def refresh():
        t.delete(*t.get_children());con=sqlite3.connect(HOST['DB_PATH']);rows=con.execute('SELECT case_id,metadata_json,stored_image_path,image_path,eligibility,eligibility_reasons_json FROM cases WHERE research_study_id=? ORDER BY id',(self.active_study_id,)).fetchall();con.close();comp=exc=0
        for cid,mj,stored,image,elig,rj in rows:
            m=json.loads(mj or '{}');rs=json.loads(rj or '[]');tag='complete' if elig=='included' else ('excluded' if elig=='excluded' else ('incomplete' if elig=='incomplete' else 'pending'));comp+=elig=='included';exc+=elig=='excluded';t.insert('', 'end',iid=cid,text=cid,values=('● '+({'included':'Completo','excluded':'Excluido','incomplete':'Incompleto'}.get(elig,'Pendiente')),m.get('sex',''),m.get('age',''),m.get('source_filename') or Path(stored or image or '').name,'; '.join(rs[:2])),tags=(tag,))
        sub.config(text=f"{tr(self,'Cargadas','Loaded')}: {len(rows)} · 🟢 {comp} · {tr(self,'Pendientes','Pending')}: {len(rows)-comp-exc} · 🔴 {exc}")
    refresh();btn=ttk.Frame(f);btn.pack(fill='x');sel=lambda:(t.selection()[0] if t.selection() else None)
    def open_sel(e=None):
        c=sel()
        if c:w.destroy();self.load_case_from_database(c)
    t.bind('<Double-1>',open_sel);ttk.Button(btn,text=tr(self,'Abrir / trazar','Open / trace'),style='Accent.TButton',command=open_sel).pack(side='left',padx=3);ttk.Button(btn,text=tr(self,'Edad/sexo','Age/sex'),command=lambda:edit_meta(self,sel(),refresh) if sel() else None).pack(side='left',padx=3);ttk.Button(btn,text=tr(self,'Cargar radiografías','Load radiographs'),command=lambda:import_radiographs(self,refresh)).pack(side='left',padx=3);ttk.Button(btn,text=tr(self,'Agregar manual','Add manual'),command=lambda:add_manual_research_case(self,refresh)).pack(side='left',padx=3);ttk.Button(btn,text=tr(self,'Excluir','Exclude'),command=lambda:exclude_case(self,sel(),refresh)).pack(side='right',padx=3);ttk.Button(btn,text=tr(self,'Reintegrar','Restore'),command=lambda:restore_case(self,sel(),refresh)).pack(side='right',padx=3);ttk.Button(btn,text=tr(self,'Exportar válidos','Export valid'),command=self.export_research_csv).pack(side='right',padx=3)

def update_db_counter(self):
    try:
        con=sqlite3.connect(HOST['DB_PATH'])
        if self.mode=='research' and self.active_study_id:tot=con.execute('SELECT COUNT(*) FROM cases WHERE research_study_id=?',(self.active_study_id,)).fetchone()[0];ok=con.execute("SELECT COUNT(*) FROM cases WHERE research_study_id=? AND eligibility='included'",(self.active_study_id,)).fetchone()[0];self.db_var.set(f'Base: {ok}/{tot} completos')
        else:self.db_var.set('Base: '+str(con.execute('SELECT COUNT(*) FROM cases').fetchone()[0])+' casos')
        con.close()
    except Exception:pass

def export_research_csv(self):
    f=filedialog.asksaveasfilename(defaultextension='.csv',initialfile='YomCeph_investigacion.csv',filetypes=[('CSV','*.csv')])
    if not f:return
    con=sqlite3.connect(HOST['DB_PATH']);cases=con.execute('SELECT case_id,metadata_json,eligibility,eligibility_reasons_json,updated_at FROM cases WHERE research_study_id=? ORDER BY id',(self.active_study_id,)).fetchall();meas=con.execute('SELECT case_id,name,display_value FROM measurements').fetchall();con.close();md={}
    for c,n,v in meas:md.setdefault(c,{})[n]=v
    names=sorted({n for d in md.values() for n in d});valid=[c for c in cases if c[2]=='included']
    with open(f,'w',newline='',encoding='utf-8-sig') as h:
        w=csv.writer(h);w.writerow(['case_id','age','sex','country','updated_at']+names)
        for cid,mj,e,rj,dt in valid:m=json.loads(mj or '{}');w.writerow([cid,m.get('age',''),m.get('sex',''),m.get('country',''),dt]+[md.get(cid,{}).get(n,'') for n in names])
    audit=str(Path(f).with_name(Path(f).stem+'_auditoria.csv'))
    with open(audit,'w',newline='',encoding='utf-8-sig') as h:
        w=csv.writer(h);w.writerow(['case_id','age','sex','eligibility','reasons','updated_at'])
        for cid,mj,e,rj,dt in cases:m=json.loads(mj or '{}');w.writerow([cid,m.get('age',''),m.get('sex',''),e,'; '.join(json.loads(rj or '[]')),dt])

def install(ns):
    global HOST;HOST=ns;ns['APP_VERSION']='0.13.1 Classic';cls=ns['YomCephClassic']
    for n in ('__init__','build_menu','show_home','open_research','open_protocol_editor','activate_study','apply_analysis_selection','open_analysis_selector','calculate','evaluate_research_eligibility','open_database_browser','update_db_counter','export_research_csv'):ORIG[n]=getattr(cls,n)
    cls.__init__=patched_init;cls.build_menu=build_menu;cls.show_home=show_home;cls.open_research=open_research;cls.open_protocol_editor=open_protocol_editor;cls.activate_study=activate_study;cls.apply_analysis_selection=apply_analysis_selection;cls.open_analysis_selector=open_analysis_selector;cls.calculate=calculate;cls.evaluate_research_eligibility=evaluate_research_eligibility;cls.open_database_browser=open_database_browser;cls.update_db_counter=update_db_counter;cls.export_research_csv=export_research_csv;cls.import_radiographs=import_radiographs;cls.add_manual_research_case=add_manual_research_case;cls.exclude_research_case=exclude_case;cls.restore_research_case=restore_case;cls.edit_research_case_metadata=edit_meta;cls.research_completion=research_completion;cls.active_measurements=active_measurements;cls.selected_measurement_names=selected_names
