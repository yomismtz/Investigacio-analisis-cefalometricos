from __future__ import annotations
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog,messagebox,simpledialog,ttk
from yomceph_theme import RESEARCH_STATUS
import yornis_theme
_INSTALLED=False

def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:return
    old_cases=workspace_class._build_cases
    def build_cases(self):
        old_cases(self)
        first=self.cases_tab.winfo_children()[0] if self.cases_tab.winfo_children() else None
        bar=ttk.Frame(self.cases_tab);bar.pack(fill='x',pady=(0,6),before=first)
        self.yornis_status_buttons={}
        for key in ('complete','in_progress','pending','incomplete','excluded'):
            b=tk.Button(bar,relief='flat',bd=0,padx=10,pady=5,command=lambda k=key:self.yornis_filter_status(k));b.pack(side='left',padx=2);self.yornis_status_buttons[key]=b
        ttk.Button(bar,text=self.T('Todos','All'),command=lambda:self.yornis_filter_status('all')).pack(side='left',padx=4)
        self.refresh_status_buttons()
        adv=ttk.LabelFrame(self.cases_tab,text=self.T('Filtros avanzados','Advanced filters'),padding=5);adv.pack(fill='x',pady=(0,5),before=first)
        self.yf_sex=tk.StringVar(value='all');self.yf_age_min=tk.StringVar();self.yf_age_max=tk.StringVar();self.yf_protocol=tk.StringVar(value='all');self.yf_review=tk.BooleanVar(value=False)
        ttk.Label(adv,text=self.T('Sexo','Sex')).pack(side='left');ttk.Combobox(adv,textvariable=self.yf_sex,state='readonly',values=['all','F','M','H'],width=6).pack(side='left',padx=3)
        ttk.Label(adv,text=self.T('Edad mín.','Min age')).pack(side='left');ttk.Entry(adv,textvariable=self.yf_age_min,width=7).pack(side='left',padx=3)
        ttk.Label(adv,text=self.T('máx.','max')).pack(side='left');ttk.Entry(adv,textvariable=self.yf_age_max,width=7).pack(side='left',padx=3)
        ttk.Label(adv,text=self.T('Protocolo','Protocol')).pack(side='left');self.yf_protocol_combo=ttk.Combobox(adv,textvariable=self.yf_protocol,state='readonly',values=['all'],width=8);self.yf_protocol_combo.pack(side='left',padx=3)
        ttk.Checkbutton(adv,text=self.T('Sólo revisión','Review only'),variable=self.yf_review,command=self.refresh_cases).pack(side='left',padx=6)
        ttk.Button(adv,text=self.T('Aplicar','Apply'),command=self.refresh_cases).pack(side='left',padx=4)
    workspace_class._build_cases=build_cases
    old_menu=workspace_class._build_menu
    def build_menu(self):
        old_menu(self);menu=self.nametowidget(self['menu']);ym=tk.Menu(menu,tearoff=0);ym.add_command(label=self.T('Carpeta del estudio…','Study storage folder…'),command=lambda:self.yornis_storage_dialog());ym.add_command(label=self.T('Semilla de aleatorización…','Randomization seed…'),command=lambda:self.yornis_seed_dialog());ym.add_command(label=self.T('Sesión de reproducibilidad…','Reproducibility session…'),command=lambda:self.yornis_repro_dialog());ym.add_separator();ym.add_command(label=self.T('¿Por qué Yornis?','Why Yornis?'),command=lambda:self.yornis_about());menu.add_cascade(label='YORNIS',menu=ym)
    workspace_class._build_menu=build_menu
    old_refresh=workspace_class.refresh_cases
    def refresh(self):
        if not hasattr(self,'case_tree'):return
        self.case_tree.delete(*self.case_tree.get_children())
        if not self.study_id:return
        try:self.yf_protocol_combo['values']=['all']+[str(p['version']) for p in self.db.protocol_versions(self.study_id)]
        except Exception:pass
        sf=self.status_filter.get();sex=self.yf_sex.get() if hasattr(self,'yf_sex') and self.yf_sex.get()!='all' else None
        try:amin=float(self.yf_age_min.get().replace(',','.')) if self.yf_age_min.get().strip() else None
        except Exception:amin=None
        try:amax=float(self.yf_age_max.get().replace(',','.')) if self.yf_age_max.get().strip() else None
        except Exception:amax=None
        rows=self.db.list_cases(self.study_id,status=None if sf=='all' else sf,sex=sex,age_min=amin,age_max=amax,search=self.search_var.get(),include_excluded=True,random_order=self.randomized_order or bool(self.protocol.get('randomize_order')))
        pvfilter=self.yf_protocol.get() if hasattr(self,'yf_protocol') else 'all';review=bool(self.yf_review.get()) if hasattr(self,'yf_review') else False
        for c in rows:
            if pvfilter!='all' and str(self.db.case_protocol_version(c['id']))!=pvfilter:continue
            if review and not bool(c['review_flag']):continue
            st=RESEARCH_STATUS.get(c['status'],RESEARCH_STATUS['pending']);label=st['label_es' if self.language=='es' else 'label_en'];display_file=Path(c['image_path']).name if c['image_path'] else ''
            reason=c['exclusion_reason'] or (self.T('Revisar QC','QC review') if c['review_flag'] else '')
            self.case_tree.insert('','end',iid=str(c['id']),values=(c['case_number'],c['study_code'],c['sex'],'' if c['age'] is None else c['age'],'● '+label,display_file,reason),tags=(c['status'],))
        self.progress_label.config(text=f"{len(self.case_tree.get_children())} {self.T('registros visibles','visible records')}")
    workspace_class.refresh_cases=refresh
    def filter_status(self,key):self.status_filter.set(key);self.refresh_cases()
    workspace_class.yornis_filter_status=filter_status
    def refresh_buttons(self):
        for key,b in getattr(self,'yornis_status_buttons',{}).items():
            st=RESEARCH_STATUS[key];b.config(text='● '+st['label_es' if self.language=='es' else 'label_en'],bg=st['background'],fg=st['foreground'],activebackground=st['dot'],activeforeground='#FFFFFF')
    workspace_class.refresh_status_buttons=refresh_buttons
    workspace_class.yornis_storage_dialog=storage_dialog;workspace_class.yornis_seed_dialog=seed_dialog;workspace_class.yornis_repro_dialog=repro_dialog;workspace_class.yornis_about=about
    _INSTALLED=True

def storage_dialog(app):
    if not app.study_id:return
    folder=filedialog.askdirectory(title=app.T('Carpeta donde guardar esta investigación','Folder for this study'))
    if folder:
        app.db.set_storage_root(app.study_id,folder);free=''
        try:
            import shutil
            total,used,avail=shutil.disk_usage(folder);free=f"\n{app.T('Espacio disponible','Available space')}: {avail/1024**3:.1f} GB"
        except Exception:pass
        messagebox.showinfo('Yornis',app.T('Carpeta del estudio actualizada.','Study folder updated.')+free,parent=app)

def seed_dialog(app):
    if not app.study_id:return
    current=app.db.random_seed(app.study_id);seed=simpledialog.askinteger('Yornis',app.T('Semilla de aleatorización (mismo valor = mismo orden):','Randomization seed (same value = same order):'),initialvalue=current,parent=app)
    if seed is not None:app.db.set_random_seed(app.study_id,seed);app.refresh_cases()

def repro_dialog(app):
    if not app.study_id:return
    n=simpledialog.askinteger('Yornis',app.T('Número de casos completos a repetir:','Number of complete cases to repeat:'),minvalue=1,maxvalue=1000,parent=app)
    if not n:return
    examiner=simpledialog.askstring('Yornis',app.T('Examinador:','Examiner:'),parent=app) or '';round_no=simpledialog.askinteger('Yornis',app.T('Ronda (2 para intraobservador):','Round (2 for intra-observer):'),initialvalue=2,minvalue=1,parent=app) or 2;seed=app.db.random_seed(app.study_id);ids=app.db.reproducibility_sample(app.study_id,n,examiner,round_no,seed)
    root=app.db.study_root(app.study_id) if hasattr(app.db,'study_root') else Path.home();root.mkdir(parents=True,exist_ok=True);manifest=root/f'repro_R{round_no}_{examiner or "examiner"}.json';manifest.write_text(json.dumps({'study_id':app.study_id,'examiner':examiner,'round_no':round_no,'seed':seed,'case_ids':ids},ensure_ascii=False,indent=2),encoding='utf-8');messagebox.showinfo('Yornis',app.T(f'Sesión creada con {len(ids)} casos.\n{manifest}',f'Session created with {len(ids)} cases.\n{manifest}'),parent=app)

def about(app):
    messagebox.showinfo('¿Por qué Yornis?',app.T('Y = Yom\nOrnis = ave (del griego órnis)\n\nYornis une la identidad de Yom Dental Análisis con la idea de vuelo, precisión y visión científica.\n\nCiencia que vuela más alto.','Y = Yom\nOrnis = bird (Greek órnis)\n\nYornis joins Yom Dental Análisis with flight, precision and scientific vision.\n\nScience that flies higher.'),parent=app)
