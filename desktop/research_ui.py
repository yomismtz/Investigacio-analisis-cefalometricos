from __future__ import annotations

import json
import math
import os
import random
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

from PIL import Image, ImageOps, ImageTk

from research_db import MAX_CASES, RESEARCH_DIR, ResearchDB
from research_export import export_audit_csv, export_case_pdf, export_excel, export_json_bundle, export_long_csv, export_study_pdf, export_wide_csv
from research_protocol import EXCLUSION_REASONS_EN, EXCLUSION_REASONS_ES, analysis_catalog, compute_selected, minimum_landmarks, shared_landmark_summary, trace_qc
from yomceph_theme import PALETTE, RESEARCH_STATUS, SEMANTIC, TRACING

try:
    import fitz
except Exception:
    fitz = None

EDU_ES = "Uso educativo e investigación. No es un dispositivo médico ni sustituye el diagnóstico profesional."
EDU_EN = "Educational and research use. Not a medical device and not a substitute for professional diagnosis."

LANDMARK_HELP = {
    "S": "Sella: centro geométrico de la silla turca.", "N": "Nasion: punto más anterior de la sutura frontonasal.",
    "A": "Punto A / subespinal.", "B": "Punto B / supramental.", "Pg": "Pogonion óseo.", "Gn": "Gnathion.",
    "Go": "Gonion.", "Me": "Menton.", "Ar": "Articulare.", "Co": "Condylion.", "Po": "Porion.", "Or": "Orbitale.",
    "Ba": "Basion.", "Pt": "Punto pterigoideo.", "ANS": "Espina nasal anterior.", "PNS": "Espina nasal posterior.",
    "U1i": "Borde incisal del incisivo superior.", "U1a": "Ápice del incisivo superior.",
    "L1i": "Borde incisal del incisivo inferior.", "L1a": "Ápice del incisivo inferior.",
    "OcP": "Punto posterior del plano oclusal.", "OcA": "Punto anterior del plano oclusal.",
    "GS": "Glabella blanda G'.", "NS": "Nasion blando N'.", "PgS": "Pogonion blando Pg'.", "Sn": "Subnasale.",
    "Ls": "Labio superior.", "Li": "Labio inferior.", "Cm": "Columella.", "Stms": "Stomion superior.", "Stmi": "Stomion inferior.",
}


class ScrollChecks(ttk.Frame):
    def __init__(self, master, height=260):
        super().__init__(master)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=SEMANTIC["panel"])
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set, height=height)
        self.canvas.pack(side="left", fill="both", expand=True); self.scroll.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width))
        self.vars: dict[str, tk.BooleanVar] = {}

    def set_items(self, items: list[tuple[str, str]], selected: set[str] | None = None, command=None):
        for child in self.inner.winfo_children(): child.destroy()
        self.vars.clear(); selected = selected or set()
        for key, label in items:
            v = tk.BooleanVar(value=key in selected); self.vars[key] = v
            ttk.Checkbutton(self.inner, text=label, variable=v, command=command).pack(anchor="w", fill="x", padx=4, pady=2)

    def selected(self) -> list[str]:
        return [k for k, v in self.vars.items() if v.get()]

    def set_all(self, state: bool):
        for v in self.vars.values(): v.set(state)


class ResearchWorkspace(tk.Tk):
    def __init__(self, language="es"):
        super().__init__()
        self.language = language if language in {"es", "en"} else "es"
        self.db = ResearchDB()
        self.study_id: int | None = None
        self.protocol: dict = {}
        self.case_id: int | None = None
        self.image = None; self.photo = None; self.image_path = ""
        self.zoom = 1.0; self.offx = 0.0; self.offy = 0.0
        self.points: dict[str, tuple[float,float]] = {}; self.undo_stack=[]; self.redo_stack=[]
        self.landmarks: list[str] = []; self.landmark_index = 0; self.dragging = None
        self.calibration_mode = False; self.calibration_clicks=[]; self.pending_mm=0.0
        self.mm_per_px: float | None = None
        self.thumbnail_photo = None; self.magnifier_photo = None
        self.randomized_order = False
        self.title("YomCeph Desktop · v0.14 Classic Research Suite")
        self.geometry("1540x940"); self.minsize(1180, 720)
        self.configure(bg=SEMANTIC["app_background"])
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._style(); self._build_menu(); self._build(); self._bindings(); self.after(120, self.start_screen)

    def T(self, es: str, en: str) -> str:
        return es if self.language == "es" else en

    def _style(self):
        s=ttk.Style(self)
        try: s.theme_use("vista")
        except Exception: pass
        s.configure("TFrame", background=SEMANTIC["app_background"])
        s.configure("Panel.TFrame", background=SEMANTIC["panel"])
        s.configure("Title.TLabel", background=SEMANTIC["app_background"], foreground=PALETTE["violet_950"], font=("Segoe UI",18,"bold"))
        s.configure("Heading.TLabel", background=SEMANTIC["panel"], foreground=PALETTE["purple_800"], font=("Segoe UI",11,"bold"))
        s.configure("Muted.TLabel", background=SEMANTIC["panel"], foreground=PALETTE["ink_soft"], font=("Segoe UI",9))
        s.configure("Primary.TButton", font=("Segoe UI",10,"bold"))
        s.configure("Mint.TButton", font=("Segoe UI",10,"bold"))
        s.configure("Treeview", rowheight=27, font=("Segoe UI",9))
        s.configure("Treeview.Heading", font=("Segoe UI",9,"bold"))

    def _build_menu(self):
        m=tk.Menu(self)
        f=tk.Menu(m,tearoff=0); f.add_command(label=self.T("Nueva investigación","New study"),command=self.new_study); f.add_command(label=self.T("Abrir/continuar investigación","Open/resume study"),command=self.choose_study); f.add_separator(); f.add_command(label=self.T("Respaldar investigación…","Back up study…"),command=self.backup); f.add_separator(); f.add_command(label=self.T("Salir","Exit"),command=self.on_close); m.add_cascade(label=self.T("ARCHIVO","FILE"),menu=f)
        r=tk.Menu(m,tearoff=0); r.add_command(label=self.T("Bloquear protocolo","Lock protocol"),command=self.lock_protocol); r.add_command(label=self.T("Muestra de reproducibilidad…","Reproducibility sample…"),command=self.repro_sample); r.add_command(label=self.T("Orden aleatorio","Random order"),command=self.toggle_random); r.add_command(label=self.T("Revisar trazado","Review tracing"),command=self.start_review); m.add_cascade(label=self.T("INVESTIGACIÓN","RESEARCH"),menu=r)
        h=tk.Menu(m,tearoff=0); h.add_command(label=self.T("Ayuda de atajos (F1)","Shortcut help (F1)"),command=self.show_help); h.add_command(label=self.T("Acerca de YomCeph","About YomCeph"),command=self.about); m.add_cascade(label=self.T("AYUDA","HELP"),menu=h)
        self.config(menu=m)

    def _build(self):
        top=ttk.Frame(self,padding=(10,8)); top.pack(fill="x")
        ttk.Label(top,text="YomCeph",style="Title.TLabel").pack(side="left")
        self.study_label=ttk.Label(top,text=self.T("Sin investigación abierta","No study open")); self.study_label.pack(side="left",padx=18)
        self.progress_label=ttk.Label(top,text=""); self.progress_label.pack(side="right",padx=8)
        self.tabs=ttk.Notebook(self); self.tabs.pack(fill="both",expand=True,padx=8,pady=(0,6))
        self.dashboard=ttk.Frame(self.tabs,padding=10); self.protocol_tab=ttk.Frame(self.tabs,padding=10); self.cases_tab=ttk.Frame(self.tabs,padding=10); self.trace_tab=ttk.Frame(self.tabs,padding=6); self.export_tab=ttk.Frame(self.tabs,padding=10)
        self.tabs.add(self.dashboard,text=self.T("Resumen","Dashboard")); self.tabs.add(self.protocol_tab,text=self.T("Protocolo","Protocol")); self.tabs.add(self.cases_tab,text=self.T("Base de datos","Database")); self.tabs.add(self.trace_tab,text=self.T("Trazado","Tracing")); self.tabs.add(self.export_tab,text=self.T("Exportar","Export"))
        self._build_dashboard(); self._build_protocol(); self._build_cases(); self._build_trace(); self._build_export()
        bottom=ttk.Frame(self,padding=(10,5)); bottom.pack(fill="x"); ttk.Label(bottom,text=self.T(EDU_ES,EDU_EN),foreground=PALETTE["ink_soft"]).pack(side="left"); self.status=ttk.Label(bottom,text=""); self.status.pack(side="right")

    def _build_dashboard(self):
        self.resume_frame=ttk.LabelFrame(self.dashboard,text=self.T("Continuar","Resume"),padding=12); self.resume_frame.pack(fill="x",pady=(0,10))
        self.resume_text=ttk.Label(self.resume_frame,text=self.T("No hay una investigación reciente.","No recent study.")); self.resume_text.pack(side="left")
        ttk.Button(self.resume_frame,text=self.T("Continuar","Resume"),command=self.resume_last).pack(side="right")
        cards=ttk.Frame(self.dashboard); cards.pack(fill="x"); self.card_labels={}
        for key,label in [("total",self.T("Total","Total")),("complete",self.T("Completos","Complete")),("pending",self.T("Pendientes","Pending")),("in_progress",self.T("En análisis","In progress")),("incomplete",self.T("Incompletos","Incomplete")),("excluded",self.T("Excluidos","Excluded"))]:
            box=ttk.LabelFrame(cards,text=label,padding=12); box.pack(side="left",fill="x",expand=True,padx=4); v=ttk.Label(box,text="0",font=("Segoe UI",20,"bold")); v.pack(); self.card_labels[key]=v
        self.chart=tk.Canvas(self.dashboard,height=180,bg=SEMANTIC["panel"],highlightthickness=1,highlightbackground=SEMANTIC["border"]); self.chart.pack(fill="x",pady=10)
        actions=ttk.Frame(self.dashboard); actions.pack(fill="x"); ttk.Button(actions,text=self.T("Nueva investigación","New study"),command=self.new_study).pack(side="left",padx=4); ttk.Button(actions,text=self.T("Abrir investigación","Open study"),command=self.choose_study).pack(side="left",padx=4); ttk.Button(actions,text=self.T("Ir a casos pendientes","Go to pending cases"),command=lambda:self.show_status("pending")).pack(side="left",padx=4)

    def _build_protocol(self):
        p=self.protocol_tab
        info=ttk.LabelFrame(p,text=self.T("Datos de investigación","Study information"),padding=8); info.pack(fill="x")
        self.study_vars={k:tk.StringVar() for k in ("title","researcher","institution","objective","examiner")}
        labels=[("title",self.T("Título","Title")),("researcher",self.T("Investigador","Researcher")),("institution",self.T("Institución","Institution")),("objective",self.T("Objetivo","Objective")),("examiner",self.T("Examinador por defecto","Default examiner"))]
        for i,(k,l) in enumerate(labels): ttk.Label(info,text=l).grid(row=i//2,column=(i%2)*2,sticky="w",padx=4,pady=3); ttk.Entry(info,textvariable=self.study_vars[k],width=48).grid(row=i//2,column=(i%2)*2+1,sticky="ew",padx=4,pady=3)
        info.columnconfigure(1,weight=1); info.columnconfigure(3,weight=1)
        self.blind_var=tk.BooleanVar(); self.random_var=tk.BooleanVar(); self.study_calib_var=tk.StringVar()
        ttk.Checkbutton(info,text=self.T("Modo ciego durante el trazado","Blind mode while tracing"),variable=self.blind_var).grid(row=3,column=0,columnspan=2,sticky="w",padx=4)
        ttk.Checkbutton(info,text=self.T("Orden aleatorio de casos","Randomize case order"),variable=self.random_var).grid(row=3,column=2,columnspan=2,sticky="w",padx=4)
        ttk.Label(info,text=self.T("Calibración del estudio mm/px","Study calibration mm/px")).grid(row=4,column=0,sticky="w",padx=4,pady=3); ttk.Entry(info,textvariable=self.study_calib_var,width=18).grid(row=4,column=1,sticky="w",padx=4)
        body=ttk.Panedwindow(p,orient="horizontal"); body.pack(fill="both",expand=True,pady=8)
        crit=ttk.LabelFrame(body,text=self.T("Criterios checklist","Checklist criteria"),padding=6); varsbox=ttk.LabelFrame(body,text=self.T("Análisis y resultados","Analyses and outcomes"),padding=6); body.add(crit,weight=2); body.add(varsbox,weight=3)
        ctop=ttk.Frame(crit); ctop.pack(fill="x"); ttk.Button(ctop,text=self.T("+ Inclusión","+ Inclusion"),command=lambda:self.add_criterion("include")).pack(side="left",padx=2); ttk.Button(ctop,text=self.T("+ Exclusión","+ Exclusion"),command=lambda:self.add_criterion("exclude")).pack(side="left",padx=2)
        self.criteria_list=tk.Listbox(crit,height=18); self.criteria_list.pack(fill="both",expand=True,pady=5)
        self.analysis_combo=ttk.Combobox(varsbox,state="readonly"); self.analysis_combo.pack(fill="x",pady=4); self.analysis_combo.bind("<<ComboboxSelected>>",lambda e:self.populate_measure_checks())
        self.measure_checks=ScrollChecks(varsbox,height=310); self.measure_checks.pack(fill="both",expand=True)
        row=ttk.Frame(varsbox); row.pack(fill="x",pady=4); ttk.Button(row,text=self.T("Seleccionar todo este análisis","Select all in this analysis"),command=lambda:self.measure_checks.set_all(True)).pack(side="left"); ttk.Button(row,text=self.T("Quitar todo","Clear"),command=lambda:self.measure_checks.set_all(False)).pack(side="left",padx=4)
        self.protocol_summary=ttk.Label(varsbox,text="",wraplength=520); self.protocol_summary.pack(fill="x",pady=5)
        foot=ttk.Frame(p); foot.pack(fill="x"); ttk.Button(foot,text=self.T("Guardar protocolo","Save protocol"),command=self.save_protocol,style="Primary.TButton").pack(side="left",padx=3); ttk.Button(foot,text=self.T("Bloquear protocolo","Lock protocol"),command=self.lock_protocol).pack(side="left",padx=3); self.lock_label=ttk.Label(foot,text=""); self.lock_label.pack(side="right")
        self.catalog=analysis_catalog(); self.selected_variable_keys:set[str]=set()
        self.analysis_combo["values"]=list(self.catalog); 
        if self.catalog: self.analysis_combo.current(0); self.populate_measure_checks()

    def _build_cases(self):
        p=self.cases_tab
        tools=ttk.Frame(p); tools.pack(fill="x",pady=(0,6))
        ttk.Button(tools,text=self.T("Cargar radiografías…","Import radiographs…"),command=self.import_files).pack(side="left",padx=2); ttk.Button(tools,text=self.T("Cargar carpeta…","Import folder…"),command=self.import_folder).pack(side="left",padx=2); ttk.Button(tools,text=self.T("Importar datos CSV…","Import metadata CSV…"),command=self.import_metadata_csv).pack(side="left",padx=2); ttk.Button(tools,text=self.T("Agregar manual","Add manually"),command=self.add_manual).pack(side="left",padx=2)
        self.search_var=tk.StringVar(); ttk.Entry(tools,textvariable=self.search_var,width=22).pack(side="right",padx=4); ttk.Label(tools,text=self.T("Buscar","Search")).pack(side="right")
        self.search_var.trace_add("write",lambda *_:self.refresh_cases())
        self.status_filter=tk.StringVar(value="all"); sf=ttk.Combobox(tools,textvariable=self.status_filter,state="readonly",values=["all","pending","in_progress","incomplete","complete","excluded"],width=14); sf.pack(side="right",padx=5); sf.bind("<<ComboboxSelected>>",lambda e:self.refresh_cases())
        split=ttk.Panedwindow(p,orient="horizontal"); split.pack(fill="both",expand=True)
        left=ttk.Frame(split); right=ttk.LabelFrame(split,text=self.T("Caso seleccionado","Selected case"),padding=8); split.add(left,weight=4); split.add(right,weight=1)
        cols=("num","code","sex","age","status","file","reason")
        self.case_tree=ttk.Treeview(left,columns=cols,show="headings",selectmode="browse")
        for c,t,w in [("num","#",50),("code","ID",100),("sex",self.T("Sexo","Sex"),70),("age",self.T("Edad","Age"),70),("status",self.T("Estado","Status"),110),("file",self.T("Radiografía","Radiograph"),230),("reason",self.T("Motivo","Reason"),220)]: self.case_tree.heading(c,text=t); self.case_tree.column(c,width=w,anchor="w")
        sy=ttk.Scrollbar(left,orient="vertical",command=self.case_tree.yview); self.case_tree.configure(yscrollcommand=sy.set); self.case_tree.pack(side="left",fill="both",expand=True); sy.pack(side="right",fill="y")
        self.case_tree.bind("<<TreeviewSelect>>",self.on_case_select); self.case_tree.bind("<Double-1>",lambda e:self.open_selected_case())
        for key,style in RESEARCH_STATUS.items(): self.case_tree.tag_configure(key,foreground=style["foreground"])
        self.preview=tk.Label(right,bg=PALETTE["canvas_dark"],width=30,height=12); self.preview.pack(fill="x",pady=4)
        self.case_meta=ttk.Label(right,text="",wraplength=270); self.case_meta.pack(fill="x",pady=4)
        ttk.Button(right,text=self.T("Abrir para análisis","Open for tracing"),command=self.open_selected_case,style="Primary.TButton").pack(fill="x",pady=3); ttk.Button(right,text=self.T("Editar edad/sexo/ID","Edit age/sex/ID"),command=self.edit_selected_meta).pack(fill="x",pady=3); ttk.Button(right,text=self.T("Marcar excluido…","Mark excluded…"),command=self.exclude_selected).pack(fill="x",pady=3); ttk.Button(right,text=self.T("Restaurar incluido","Restore included"),command=self.restore_selected).pack(fill="x",pady=3)

    def _build_trace(self):
        p=self.trace_tab; split=ttk.Panedwindow(p,orient="horizontal"); split.pack(fill="both",expand=True)
        left=ttk.Frame(split,padding=5); center=ttk.Frame(split); right=ttk.Frame(split,padding=5); split.add(left,weight=1); split.add(center,weight=5); split.add(right,weight=2)
        self.trace_case_title=ttk.Label(left,text=self.T("Sin caso abierto","No case open"),style="Heading.TLabel"); self.trace_case_title.pack(fill="x")
        self.trace_meta=ttk.Label(left,text="",wraplength=230); self.trace_meta.pack(fill="x",pady=4)
        ttk.Label(left,text=self.T("Landmarks requeridos","Required landmarks"),style="Heading.TLabel").pack(anchor="w",pady=(8,2))
        self.landmark_list=tk.Listbox(left,exportselection=False); self.landmark_list.pack(fill="both",expand=True); self.landmark_list.bind("<<ListboxSelect>>",self.pick_landmark)
        self.landmark_help=ttk.Label(left,text="",wraplength=230); self.landmark_help.pack(fill="x",pady=5)
        row=ttk.Frame(left); row.pack(fill="x"); ttk.Button(row,text="←",command=lambda:self.step_landmark(-1)).pack(side="left",expand=True,fill="x"); ttk.Button(row,text="→",command=lambda:self.step_landmark(1)).pack(side="left",expand=True,fill="x")
        self.canvas=tk.Canvas(center,bg=SEMANTIC["radiograph_canvas"],highlightthickness=0,cursor="crosshair"); self.canvas.pack(fill="both",expand=True)
        self.canvas.bind("<Button-1>",self.canvas_click); self.canvas.bind("<B1-Motion>",self.canvas_drag); self.canvas.bind("<ButtonRelease-1>",self.canvas_release); self.canvas.bind("<Button-3>",self.pan_begin); self.canvas.bind("<B3-Motion>",self.pan_move); self.canvas.bind("<MouseWheel>",self.zoom_wheel); self.canvas.bind("<Motion>",self.update_magnifier); self.canvas.bind("<Configure>",lambda e:self.redraw())
        self.pan_state=None
        self.magnifier=tk.Canvas(right,width=260,height=190,bg=PALETTE["canvas_dark"],highlightthickness=1,highlightbackground=SEMANTIC["border"]); self.magnifier.pack(fill="x",pady=3)
        ttk.Button(right,text=self.T("Ajustar imagen","Fit image"),command=self.fit_image).pack(fill="x",pady=2); ttk.Button(right,text=self.T("Calibrar caso","Calibrate case"),command=self.start_calibration).pack(fill="x",pady=2); self.calib_label=ttk.Label(right,text=self.T("Sin calibrar","Not calibrated")); self.calib_label.pack(fill="x",pady=4)
        ttk.Separator(right).pack(fill="x",pady=5); ttk.Button(right,text=self.T("Deshacer Ctrl+Z","Undo Ctrl+Z"),command=self.undo).pack(fill="x",pady=2); ttk.Button(right,text=self.T("Rehacer Ctrl+Y","Redo Ctrl+Y"),command=self.redo).pack(fill="x",pady=2); ttk.Button(right,text=self.T("Revisar puntos","Review points"),command=self.start_review).pack(fill="x",pady=2); ttk.Button(right,text=self.T("Control de calidad","Quality control"),command=self.show_qc).pack(fill="x",pady=2); ttk.Button(right,text=self.T("Calcular y guardar","Calculate & save"),command=self.calculate_and_save,style="Primary.TButton").pack(fill="x",pady=4); ttk.Button(right,text=self.T("Excluir caso…","Exclude case…"),command=self.exclude_current).pack(fill="x",pady=2)
        self.trace_progress=ttk.Label(right,text=""); self.trace_progress.pack(fill="x",pady=5)
        self.results_tree=ttk.Treeview(right,columns=("value","unit"),show="tree headings",height=12); self.results_tree.heading("#0",text=self.T("Resultado","Result")); self.results_tree.heading("value",text=self.T("Valor","Value")); self.results_tree.heading("unit",text=self.T("Unidad","Unit")); self.results_tree.column("#0",width=180); self.results_tree.column("value",width=70); self.results_tree.column("unit",width=50); self.results_tree.pack(fill="both",expand=True)

    def _build_export(self):
        p=self.export_tab
        ttk.Label(p,text=self.T("Exportación y respaldo","Export and backup"),style="Title.TLabel").pack(anchor="w",pady=(0,10))
        grid=ttk.Frame(p); grid.pack(anchor="nw")
        buttons=[(self.T("CSV ancho · listo para SPSS/R/Jamovi","Wide CSV · SPSS/R/Jamovi ready"),self.export_wide),(self.T("CSV largo","Long CSV"),self.export_long),(self.T("Excel completo","Complete Excel"),self.export_xlsx),(self.T("JSON respaldo de datos","JSON data bundle"),self.export_json),(self.T("Auditoría CSV","Audit CSV"),self.export_audit),(self.T("Informe PDF de investigación","Study PDF report"),self.export_study_report),(self.T("Informe PDF del caso actual","Current case PDF"),self.export_case_report),(self.T("Respaldo ZIP con base e imágenes","ZIP backup with DB and images"),self.backup)]
        for i,(label,cmd) in enumerate(buttons): ttk.Button(grid,text=label,command=cmd,width=44).grid(row=i//2,column=i%2,padx=5,pady=5,sticky="ew")
        ttk.Label(p,text=self.T("Los datos originales, resultados, landmarks y auditoría se mantienen separados. Los casos excluidos permanecen disponibles para auditoría.","Original data, results, landmarks and audit are stored separately. Excluded cases remain available for audit."),wraplength=850).pack(anchor="w",pady=14)

    def _bindings(self):
        self.bind("<F1>",lambda e:self.show_help()); self.bind("<Control-z>",lambda e:self.undo()); self.bind("<Control-y>",lambda e:self.redo()); self.bind("<space>",lambda e:self.step_landmark(1)); self.bind("<Left>",lambda e:self.step_landmark(-1)); self.bind("<Right>",lambda e:self.step_landmark(1)); self.bind("<plus>",lambda e:self.zoom_center(1.12)); self.bind("<minus>",lambda e:self.zoom_center(1/1.12)); self.bind("<Return>",lambda e:self.calculate_and_save() if self.tabs.index(self.tabs.select())==3 else None)

    # ---------- startup/study ----------
    def start_screen(self):
        studies=self.db.studies(); last=self.db.get_setting("last_study_id")
        if last:
            try:
                s=self.db.study(int(last)); p=self.db.progress(int(last)) if s else None
                if s and p: self.resume_text.config(text=f"{s['title']} — {p['complete']}/{p['total']} {self.T('completos','complete')}")
            except Exception: pass
        if not studies: self.new_study()

    def new_study(self):
        w=tk.Toplevel(self); w.title(self.T("Nueva investigación","New study")); w.transient(self); w.grab_set(); w.geometry("520x430")
        fields={k:tk.StringVar() for k in ("title","researcher","institution","objective")}
        for i,(k,l) in enumerate([("title",self.T("Título","Title")),("researcher",self.T("Investigador","Researcher")),("institution",self.T("Institución","Institution")),("objective",self.T("Objetivo","Objective"))]): ttk.Label(w,text=l).pack(anchor="w",padx=14,pady=(10 if i==0 else 4,2)); ttk.Entry(w,textvariable=fields[k]).pack(fill="x",padx=14)
        blind=tk.BooleanVar(); ttk.Checkbutton(w,text=self.T("Modo ciego","Blind mode"),variable=blind).pack(anchor="w",padx=14,pady=10)
        def create():
            if not fields["title"].get().strip(): messagebox.showwarning("YomCeph",self.T("Escribe un título.","Enter a title."),parent=w); return
            sid=self.db.create_study(fields["title"].get(),fields["researcher"].get(),fields["institution"].get(),fields["objective"].get(),self.language,blind.get()); w.destroy(); self.load_study(sid); self.tabs.select(self.protocol_tab)
        ttk.Button(w,text=self.T("Crear investigación","Create study"),command=create,style="Primary.TButton").pack(pady=16)

    def choose_study(self):
        rows=self.db.studies()
        if not rows: self.new_study(); return
        w=tk.Toplevel(self); w.title(self.T("Abrir investigación","Open study")); w.transient(self); w.grab_set(); w.geometry("720x430")
        tree=ttk.Treeview(w,columns=("title","progress","date"),show="headings"); tree.heading("title",text=self.T("Investigación","Study")); tree.heading("progress",text=self.T("Progreso","Progress")); tree.heading("date",text=self.T("Último acceso","Last opened")); tree.pack(fill="both",expand=True,padx=10,pady=10)
        for r in rows: tree.insert("","end",iid=str(r["id"]),values=(r["title"],f"{r['complete_count']}/{r['case_count']}",r["last_opened_at"] or ""))
        def open_():
            s=tree.selection();
            if s: w.destroy(); self.load_study(int(s[0]))
        ttk.Button(w,text=self.T("Abrir","Open"),command=open_,style="Primary.TButton").pack(pady=(0,10)); tree.bind("<Double-1>",lambda e:open_())

    def resume_last(self):
        sid=self.db.get_setting("last_study_id")
        if sid and self.db.study(int(sid)): self.load_study(int(sid))
        else: self.choose_study()

    def load_study(self, study_id:int):
        self.study_id=study_id; self.db.touch_study(study_id); s=self.db.study(study_id); latest=self.db.latest_protocol(study_id); self.protocol=latest["config"] or {}; self.protocol["version"]=latest["version"]
        self.study_label.config(text=f"{s['title']} · v{latest['version'] or 1}")
        for k in self.study_vars: self.study_vars[k].set(s[k] if k in s.keys() else self.protocol.get(k,""))
        self.blind_var.set(bool(s["blind_mode"])); self.study_calib_var.set("" if s["study_mm_per_px"] is None else str(s["study_mm_per_px"])); self.random_var.set(bool(self.protocol.get("randomize_order")))
        self.selected_variable_keys=set(self.protocol.get("selected_variables") or []); self.refresh_criteria(); self.populate_measure_checks(); self.update_protocol_summary(); self.refresh_cases(); self.refresh_dashboard(); self.lock_label.config(text=self.T("🔒 Protocolo bloqueado","🔒 Protocol locked") if s["protocol_locked"] else self.T("Protocolo editable","Protocol editable")); self.status.config(text=self.T("Investigación cargada","Study loaded"))

    # ---------- protocol ----------
    def refresh_criteria(self):
        self.criteria_list.delete(0,"end")
        if not self.study_id: return
        for r in self.db.criteria(self.study_id): self.criteria_list.insert("end",f"{'☑' if r['kind']=='include' else '☒'} {r['label']}")

    def add_criterion(self, kind):
        if not self.study_id: return
        text=simpledialog.askstring("YomCeph",self.T("Escribe el criterio:","Enter criterion:"),parent=self)
        if text: self.db.add_criterion(self.study_id,kind,text); self.refresh_criteria()

    def populate_measure_checks(self):
        if not hasattr(self,"analysis_combo"): return
        analysis=self.analysis_combo.get(); items=[]
        for v in self.catalog.get(analysis,[]): items.append((v.key,v.name))
        self.measure_checks.set_items(items,self.selected_variable_keys,command=self.on_measure_toggle)
        self.update_protocol_summary()

    def on_measure_toggle(self):
        analysis=self.analysis_combo.get()
        for v in self.catalog.get(analysis,[]):
            if self.measure_checks.vars.get(v.key) and self.measure_checks.vars[v.key].get(): self.selected_variable_keys.add(v.key)
            else: self.selected_variable_keys.discard(v.key)
        self.update_protocol_summary()

    def update_protocol_summary(self):
        s=shared_landmark_summary(sorted(self.selected_variable_keys)); self.protocol_summary.config(text=self.T(f"{s['measurement_count']} resultados · {s['analysis_count']} análisis · {s['unique_landmark_count']} landmarks únicos ({s['shared_landmark_count']} compartidos)",f"{s['measurement_count']} outcomes · {s['analysis_count']} analyses · {s['unique_landmark_count']} unique landmarks ({s['shared_landmark_count']} shared)"))

    def collect_protocol(self):
        if not self.study_id: return {}
        criteria=self.db.criteria(self.study_id); mm=None
        try: mm=float(self.study_calib_var.get().replace(",",".")) if self.study_calib_var.get().strip() else None
        except Exception: pass
        return {"title":self.study_vars["title"].get(),"researcher":self.study_vars["researcher"].get(),"institution":self.study_vars["institution"].get(),"objective":self.study_vars["objective"].get(),"examiner":self.study_vars["examiner"].get(),"blind_mode":self.blind_var.get(),"randomize_order":self.random_var.get(),"study_mm_per_px":mm,"selected_variables":sorted(self.selected_variable_keys),"selected_analyses":list(dict.fromkeys(k.split("::",1)[0] for k in sorted(self.selected_variable_keys))),"required_landmarks":minimum_landmarks(sorted(self.selected_variable_keys)),"include_criteria":[r["label"] for r in criteria if r["kind"]=="include"],"exclude_criteria":[r["label"] for r in criteria if r["kind"]=="exclude"]}

    def save_protocol(self):
        if not self.study_id: return
        self.on_measure_toggle(); cfg=self.collect_protocol()
        if not cfg["selected_variables"]: messagebox.showwarning("YomCeph",self.T("Selecciona al menos un resultado.","Select at least one outcome.")); return
        latest=self.db.latest_protocol(self.study_id); version=self.db.save_protocol(self.study_id,cfg,lock=False,force_new_version=bool(latest["locked"])); self.db.set_study_calibration(self.study_id,cfg["study_mm_per_px"]); self.protocol=cfg|{"version":version}; self.study_label.config(text=f"{cfg['title']} · v{version}"); self.refresh_cases(); self.status.config(text=self.T("Protocolo guardado","Protocol saved"))

    def lock_protocol(self):
        if not self.study_id:return
        if not self.db.latest_protocol(self.study_id)["version"]: self.save_protocol()
        if messagebox.askyesno("YomCeph",self.T("¿Bloquear el protocolo? Los cambios posteriores crearán una nueva versión.","Lock protocol? Later changes will create a new version.")):
            self.db.lock_protocol(self.study_id); self.lock_label.config(text=self.T("🔒 Protocolo bloqueado","🔒 Protocol locked"))

    # ---------- import/database ----------
    def require_study(self):
        if not self.study_id: messagebox.showinfo("YomCeph",self.T("Abre o crea una investigación.","Open or create a study.")); return False
        return True

    def import_files(self):
        if not self.require_study():return
        files=filedialog.askopenfilenames(filetypes=[("Radiografías","*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pdf"),("Todos","*.*")])
        if not files:return
        r=self.db.import_files(self.study_id,files); self.refresh_cases(); self.refresh_dashboard(); messagebox.showinfo("YomCeph",self.T(f"Agregadas: {r.added}\nDuplicadas: {r.duplicates}\nOmitidas: {r.skipped}",f"Added: {r.added}\nDuplicates: {r.duplicates}\nSkipped: {r.skipped}"))

    def import_folder(self):
        if not self.require_study():return
        folder=filedialog.askdirectory();
        if not folder:return
        csv_path=filedialog.askopenfilename(title=self.T("CSV de metadatos opcional (Cancelar para omitir)","Optional metadata CSV (Cancel to skip)"),filetypes=[("CSV","*.csv")])
        r=self.db.import_folder(self.study_id,folder,csv_path or None); self.refresh_cases(); self.refresh_dashboard(); messagebox.showinfo("YomCeph",f"{self.T('Agregadas','Added')}: {r.added}\n{self.T('Duplicadas','Duplicates')}: {r.duplicates}\n{self.T('Omitidas','Skipped')}: {r.skipped}")

    def import_metadata_csv(self):
        if not self.require_study():return
        path=filedialog.askopenfilename(filetypes=[("CSV","*.csv")]);
        if not path:return
        meta=self.db.read_metadata_csv(path); updated=0
        for c in self.db.list_cases(self.study_id,include_excluded=True):
            md=meta.get(c["original_filename"],meta.get(Path(c["original_filename"]).stem,meta.get(c["study_code"],{})))
            if md: self.db.update_case_metadata(c["id"],sex=str(md.get("sex") or c["sex"]),age=self.db._float_or_none(md.get("age")) if md.get("age") not in (None,"") else c["age"],study_code=str(md.get("id") or c["study_code"]),examiner=str(md.get("examiner") or c["examiner"])); updated+=1
        self.refresh_cases(); messagebox.showinfo("YomCeph",self.T(f"Se actualizaron {updated} registros.",f"Updated {updated} records."))

    def add_manual(self):
        if not self.require_study():return
        w=tk.Toplevel(self); w.title(self.T("Agregar caso","Add case")); w.transient(self); w.grab_set(); vs={k:tk.StringVar() for k in ("code","sex","age")}
        for k,l in [("code","ID"),("sex",self.T("Sexo H/M","Sex M/F")),("age",self.T("Edad","Age"))]: ttk.Label(w,text=l).pack(anchor="w",padx=12,pady=(8,2)); ttk.Entry(w,textvariable=vs[k]).pack(fill="x",padx=12)
        image_var=tk.StringVar(); ttk.Label(w,text=self.T("Radiografía (opcional)","Radiograph (optional)")).pack(anchor="w",padx=12,pady=(8,2)); row=ttk.Frame(w); row.pack(fill="x",padx=12); ttk.Entry(row,textvariable=image_var).pack(side="left",fill="x",expand=True); ttk.Button(row,text="…",command=lambda:image_var.set(filedialog.askopenfilename())).pack(side="left")
        def add():
            try:self.db.add_case(self.study_id,vs["code"].get() or None,vs["sex"].get(),self.db._float_or_none(vs["age"].get()),image_var.get()); w.destroy(); self.refresh_cases(); self.refresh_dashboard()
            except Exception as e:messagebox.showerror("YomCeph",str(e),parent=w)
        ttk.Button(w,text=self.T("Agregar","Add"),command=add,style="Primary.TButton").pack(pady=12)

    def refresh_cases(self):
        if not hasattr(self,"case_tree"):return
        self.case_tree.delete(*self.case_tree.get_children())
        if not self.study_id:return
        sf=self.status_filter.get(); rows=self.db.list_cases(self.study_id,status=None if sf=="all" else sf,search=self.search_var.get(),include_excluded=True,random_order=self.randomized_order or bool(self.protocol.get("randomize_order")))
        for c in rows:
            style=RESEARCH_STATUS.get(c["status"],RESEARCH_STATUS["pending"]); status_label=style["label_es" if self.language=="es" else "label_en"]
            self.case_tree.insert("","end",iid=str(c["id"]),values=(c["case_number"],c["study_code"],c["sex"],"" if c["age"] is None else c["age"],"● "+status_label,c["original_filename"],c["exclusion_reason"]),tags=(c["status"],))
        self.progress_label.config(text=f"{len(rows)} {self.T('registros visibles','visible records')}")

    def selected_case_id(self):
        s=self.case_tree.selection(); return int(s[0]) if s else None

    def on_case_select(self,e=None):
        cid=self.selected_case_id();
        if not cid:return
        c=self.db.case(cid); self.case_meta.config(text=f"#{c['case_number']} · {c['study_code']}\n{self.T('Sexo','Sex')}: {c['sex'] or '—'} · {self.T('Edad','Age')}: {c['age'] if c['age'] is not None else '—'}\n{self.T('Estado','Status')}: {c['status']}\n{c['original_filename']}")
        self.preview.config(image=""); self.thumbnail_photo=None
        if c["image_path"] and Path(c["image_path"]).exists():
            try:
                im=self.load_pil(c["image_path"]); im.thumbnail((270,210)); self.thumbnail_photo=ImageTk.PhotoImage(im); self.preview.config(image=self.thumbnail_photo)
            except Exception:pass

    def edit_selected_meta(self):
        cid=self.selected_case_id();
        if not cid:return
        c=self.db.case(cid); code=simpledialog.askstring("YomCeph","ID:",initialvalue=c["study_code"],parent=self); 
        if code is None:return
        sex=simpledialog.askstring("YomCeph",self.T("Sexo:","Sex:"),initialvalue=c["sex"],parent=self); age=simpledialog.askfloat("YomCeph",self.T("Edad:","Age:"),initialvalue=c["age"],parent=self)
        try:self.db.update_case_metadata(cid,sex=sex or "",age=age,study_code=code); self.refresh_cases()
        except Exception as e:messagebox.showerror("YomCeph",str(e))

    def exclude_selected(self):
        cid=self.selected_case_id();
        if cid:self.exclude_case_dialog(cid)
    def restore_selected(self):
        cid=self.selected_case_id();
        if cid:self.db.restore_case(cid); self.refresh_cases(); self.refresh_dashboard()
    def show_status(self,status):self.status_filter.set(status);self.tabs.select(self.cases_tab);self.refresh_cases()
    def toggle_random(self):self.randomized_order=not self.randomized_order;self.refresh_cases()

    # ---------- tracing ----------
    def load_pil(self,path):
        if str(path).lower().endswith(".pdf"):
            if fitz is None: raise RuntimeError("PyMuPDF no disponible")
            doc=fitz.open(path); pix=doc[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False); im=Image.frombytes("RGB",[pix.width,pix.height],pix.samples); doc.close(); return im
        return ImageOps.exif_transpose(Image.open(path)).convert("RGB")

    def open_selected_case(self):
        cid=self.selected_case_id();
        if cid:self.open_case(cid)

    def open_case(self,cid:int):
        if not self.study_id:return
        latest=self.db.latest_protocol(self.study_id); self.protocol=latest["config"] or self.protocol; self.protocol["version"]=latest["version"]
        if not self.protocol.get("selected_variables"):messagebox.showwarning("YomCeph",self.T("Primero guarda el protocolo y selecciona resultados.","Save the protocol and select outcomes first."));return
        c=self.db.case(cid)
        if not c["image_path"] or not Path(c["image_path"]).exists():
            p=filedialog.askopenfilename(filetypes=[("Radiografías","*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pdf")])
            if not p:return
            self.db.attach_image(cid,p); c=self.db.case(cid)
        try:self.image=self.load_pil(c["image_path"]); self.image_path=c["image_path"]
        except Exception as e:messagebox.showerror("YomCeph",str(e));return
        self.case_id=cid; self.landmarks=minimum_landmarks(self.protocol["selected_variables"]); self.points=self.load_autosave(cid) or self.db.latest_landmarks(cid,self.protocol["version"]); self.landmark_index=0; self.undo_stack=[]; self.redo_stack=[]
        s=self.db.study(self.study_id); self.mm_per_px=c["case_mm_per_px"] or s["study_mm_per_px"]
        self.db.mark_in_progress(cid); self.landmark_list.delete(0,"end")
        for p in self.landmarks:self.landmark_list.insert("end",p)
        if self.landmarks:self.landmark_list.selection_set(0)
        self.trace_case_title.config(text=f"#{c['case_number']} · {c['study_code']}")
        if bool(s["blind_mode"]):self.trace_meta.config(text=self.T("Modo ciego activo: edad/sexo ocultos","Blind mode active: age/sex hidden"))
        else:self.trace_meta.config(text=f"{self.T('Sexo','Sex')}: {c['sex'] or '—'} · {self.T('Edad','Age')}: {c['age'] if c['age'] is not None else '—'}")
        self.calib_label.config(text=(f"{self.mm_per_px:.6f} mm/px" if self.mm_per_px else self.T("Sin calibrar","Not calibrated"))); self.tabs.select(self.trace_tab); self.fit_image(); self.update_trace_progress(); self.calculate_preview()

    def fit_image(self):
        if self.image is None:return
        self.update_idletasks(); w=max(100,self.canvas.winfo_width());h=max(100,self.canvas.winfo_height());self.zoom=min(w/self.image.width,h/self.image.height)*.96;self.offx=(w-self.image.width*self.zoom)/2;self.offy=(h-self.image.height*self.zoom)/2;self.redraw()
    def image_to_canvas(self,p):return(self.offx+p[0]*self.zoom,self.offy+p[1]*self.zoom)
    def canvas_to_image(self,x,y):return((x-self.offx)/self.zoom,(y-self.offy)/self.zoom)
    def redraw(self):
        self.canvas.delete("all")
        if self.image is not None:
            w=max(1,int(self.image.width*self.zoom));h=max(1,int(self.image.height*self.zoom));im=self.image.resize((w,h),Image.Resampling.LANCZOS);self.photo=ImageTk.PhotoImage(im);self.canvas.create_image(self.offx,self.offy,anchor="nw",image=self.photo)
        for k,p in self.points.items():
            if k not in self.landmarks:continue
            x,y=self.image_to_canvas(p);r=5 if k!=self.current_landmark() else 7;fill=TRACING["landmark_active"] if k==self.current_landmark() else TRACING["landmark"]
            self.canvas.create_oval(x-r,y-r,x+r,y+r,fill=fill,outline=TRACING["selection_ring"],width=2);self.canvas.create_text(x+8,y-8,text=k,fill=TRACING["label"],anchor="sw",font=("Segoe UI",9,"bold"))
        if len(self.calibration_clicks)==1:
            x,y=self.image_to_canvas(self.calibration_clicks[0]);self.canvas.create_oval(x-6,y-6,x+6,y+6,fill=PALETTE["mint_300"])
    def current_landmark(self):return self.landmarks[self.landmark_index] if self.landmarks else ""
    def pick_landmark(self,e=None):
        s=self.landmark_list.curselection();
        if s:self.landmark_index=s[0];self.update_trace_progress();self.redraw();self.center_on_current()
    def step_landmark(self,delta):
        if not self.landmarks:return
        self.landmark_index=max(0,min(len(self.landmarks)-1,self.landmark_index+delta));self.landmark_list.selection_clear(0,"end");self.landmark_list.selection_set(self.landmark_index);self.landmark_list.see(self.landmark_index);self.update_trace_progress();self.redraw();self.center_on_current()
    def update_trace_progress(self):
        if not self.landmarks:return
        k=self.current_landmark();self.landmark_help.config(text=LANDMARK_HELP.get(k,k));placed=sum(x in self.points for x in self.landmarks);self.trace_progress.config(text=f"{placed}/{len(self.landmarks)} · {k}")
    def nearest_point(self,x,y):
        best=None;bd=14
        for k,p in self.points.items():
            if k not in self.landmarks:continue
            cx,cy=self.image_to_canvas(p);d=math.hypot(cx-x,cy-y)
            if d<bd:best=k;bd=d
        return best
    def canvas_click(self,e):
        if self.image is None:return
        p=self.canvas_to_image(e.x,e.y)
        if self.calibration_mode:
            self.calibration_clicks.append(p)
            if len(self.calibration_clicks)==2:
                d=math.dist(*self.calibration_clicks);self.mm_per_px=self.pending_mm/d if d>0 else None;self.calibration_mode=False;self.calibration_clicks=[];self.calib_label.config(text=f"{self.mm_per_px:.6f} mm/px" if self.mm_per_px else self.T("Sin calibrar","Not calibrated"));self.autosave()
            self.redraw();return
        near=self.nearest_point(e.x,e.y);k=near or self.current_landmark()
        if not k:return
        old=self.points.get(k);self.undo_stack.append((k,old,p));self.redo_stack.clear();self.points[k]=p;self.dragging=k
        if near is None and self.landmark_index<len(self.landmarks)-1:self.step_landmark(1)
        self.autosave();self.update_trace_progress();self.redraw()
    def canvas_drag(self,e):
        if self.dragging and self.image is not None:self.points[self.dragging]=self.canvas_to_image(e.x,e.y);self.redraw()
    def canvas_release(self,e):
        if self.dragging:self.autosave();self.dragging=None;self.update_trace_progress()
    def pan_begin(self,e):self.pan_state=(e.x,e.y,self.offx,self.offy)
    def pan_move(self,e):
        if self.pan_state:x,y,ox,oy=self.pan_state;self.offx=ox+e.x-x;self.offy=oy+e.y-y;self.redraw()
    def zoom_wheel(self,e):
        if self.image is None:return
        before=self.canvas_to_image(e.x,e.y);factor=1.12 if e.delta>0 else 1/1.12;self.zoom=max(.05,min(10,self.zoom*factor));self.offx=e.x-before[0]*self.zoom;self.offy=e.y-before[1]*self.zoom;self.redraw()
    def zoom_center(self,factor):
        if self.image is None:return
        cx=self.canvas.winfo_width()/2;cy=self.canvas.winfo_height()/2;before=self.canvas_to_image(cx,cy);self.zoom=max(.05,min(10,self.zoom*factor));self.offx=cx-before[0]*self.zoom;self.offy=cy-before[1]*self.zoom;self.redraw()
    def center_on_current(self):
        k=self.current_landmark();
        if not k or k not in self.points:return
        x,y=self.points[k];self.offx=self.canvas.winfo_width()/2-x*self.zoom;self.offy=self.canvas.winfo_height()/2-y*self.zoom;self.redraw()
    def update_magnifier(self,e):
        if self.image is None:return
        x,y=self.canvas_to_image(e.x,e.y);r=max(20,int(70/self.zoom));box=(max(0,int(x-r)),max(0,int(y-r)),min(self.image.width,int(x+r)),min(self.image.height,int(y+r)))
        try:
            crop=self.image.crop(box).resize((260,190),Image.Resampling.LANCZOS);self.magnifier_photo=ImageTk.PhotoImage(crop);self.magnifier.delete("all");self.magnifier.create_image(130,95,image=self.magnifier_photo);self.magnifier.create_line(125,95,135,95,fill=PALETTE["mint_300"],width=2);self.magnifier.create_line(130,90,130,100,fill=PALETTE["mint_300"],width=2)
        except Exception:pass
    def undo(self):
        if not self.undo_stack:return
        k,old,new=self.undo_stack.pop();self.redo_stack.append((k,old,new));self.points.pop(k,None) if old is None else self.points.__setitem__(k,old);self.autosave();self.redraw();self.update_trace_progress()
    def redo(self):
        if not self.redo_stack:return
        k,old,new=self.redo_stack.pop();self.undo_stack.append((k,old,new));self.points[k]=new;self.autosave();self.redraw();self.update_trace_progress()
    def start_calibration(self):
        if self.image is None:return
        mm=simpledialog.askfloat("YomCeph",self.T("Distancia real entre los dos puntos (mm):","Real distance between the two points (mm):"),minvalue=.01,parent=self)
        if mm:self.pending_mm=mm;self.calibration_mode=True;self.calibration_clicks=[];self.status.config(text=self.T("Marca los dos extremos de la referencia.","Click both ends of the reference."))
    def autosave_path(self,cid):
        p=RESEARCH_DIR/f"study_{self.study_id:04d}"/"autosave";p.mkdir(parents=True,exist_ok=True);return p/f"case_{cid:04d}.json"
    def autosave(self):
        if not self.case_id:return
        data={"case_id":self.case_id,"protocol_version":self.protocol.get("version"),"points":self.points,"mm_per_px":self.mm_per_px,"landmark_index":self.landmark_index};self.autosave_path(self.case_id).write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
    def load_autosave(self,cid):
        p=self.autosave_path(cid)
        if not p.exists():return {}
        try:
            d=json.loads(p.read_text(encoding="utf-8"));
            if d.get("protocol_version")!=self.protocol.get("version"):return {}
            self.mm_per_px=d.get("mm_per_px") or self.mm_per_px;return {k:tuple(v) for k,v in d.get("points",{}).items()}
        except Exception:return {}
    def calculate_preview(self):
        self.results_tree.delete(*self.results_tree.get_children())
        if not self.case_id:return []
        c=self.db.case(self.case_id);results=compute_selected(self.protocol.get("selected_variables",[]),self.points,self.mm_per_px,sex=c["sex"],age=c["age"])
        groups={}
        for r in results:
            a=r["analysis"];groups.setdefault(a,self.results_tree.insert("","end",text=a,open=True,values=("","")));val="—" if r["value"] is None else f"{r['value']:.2f}";self.results_tree.insert(groups[a],"end",text=r["measurement"],values=(val,r["unit"]))
        return results
    def show_qc(self):
        if not self.case_id:return
        issues=trace_qc(self.protocol.get("selected_variables",[]),self.points,self.mm_per_px);messagebox.showinfo(self.T("Control de calidad","Quality control"),"\n\n".join(("✓ " if x["level"]=="ok" else "◆ ")+x["message"] for x in issues))
    def calculate_and_save(self):
        if not self.case_id:return
        results=self.calculate_preview();issues=trace_qc(self.protocol.get("selected_variables",[]),self.points,self.mm_per_px)
        blocking=[x for x in issues if x["level"]!="ok"]
        self.db.save_trace(self.case_id,self.protocol["version"],self.points,results,[k.split("::",1)[1] for k in self.protocol.get("selected_variables",[])],self.mm_per_px)
        status=self.db.case(self.case_id)["status"];self.refresh_cases();self.refresh_dashboard();self.autosave()
        if status=="complete":messagebox.showinfo("YomCeph",self.T("Caso completo. Se marcó automáticamente en verde menta.","Case complete. It was automatically marked mint green."))
        else:messagebox.showwarning("YomCeph",self.T("El caso se guardó pero aún no cumple todos los resultados del protocolo.","The case was saved but does not yet contain every protocol outcome."))
    def start_review(self):
        if not self.case_id or not self.landmarks:return
        self.landmark_index=0;self.step_landmark(0);self.status.config(text=self.T("Modo revisión: usa ←/→ para recorrer landmarks.","Review mode: use ←/→ to move through landmarks."))
    def exclude_current(self):
        if self.case_id:self.exclude_case_dialog(self.case_id)
    def exclude_case_dialog(self,cid):
        reasons=EXCLUSION_REASONS_ES if self.language=="es" else EXCLUSION_REASONS_EN
        w=tk.Toplevel(self);w.title(self.T("Excluir caso","Exclude case"));w.transient(self);w.grab_set();var=tk.StringVar(value=reasons[0]);
        ttk.Label(w,text=self.T("Motivo documentado:","Documented reason:")).pack(anchor="w",padx=12,pady=(12,4));combo=ttk.Combobox(w,textvariable=var,values=reasons,state="readonly",width=55);combo.pack(padx=12);ttk.Label(w,text=self.T("Observación:","Note:")).pack(anchor="w",padx=12,pady=(10,4));note=tk.Text(w,width=60,height=5);note.pack(padx=12)
        def do():self.db.exclude_case(cid,var.get(),note.get("1.0","end").strip());w.destroy();self.refresh_cases();self.refresh_dashboard();messagebox.showinfo("YomCeph",self.T("Caso retirado de la muestra válida y conservado en auditoría.","Case removed from the valid sample and retained in audit."))
        ttk.Button(w,text=self.T("Confirmar exclusión","Confirm exclusion"),command=do).pack(pady=12)

    # ---------- dashboard/export ----------
    def refresh_dashboard(self):
        if not self.study_id:return
        p=self.db.progress(self.study_id)
        for k,l in self.card_labels.items():l.config(text=str(p.get(k,0)))
        self.chart.delete("all");keys=["complete","pending","in_progress","incomplete","excluded"];colors=[RESEARCH_STATUS[k]["dot"] for k in keys];vals=[p[k] for k in keys];mx=max(vals+[1]);w=max(500,self.chart.winfo_width() or 900);bar=(w-80)/len(keys)
        for i,(k,v,c) in enumerate(zip(keys,vals,colors)):
            x=45+i*bar;y2=150;y1=y2-(110*v/mx);self.chart.create_rectangle(x,y1,x+bar*.55,y2,fill=c,outline="");self.chart.create_text(x+bar*.27,y1-10,text=str(v),fill=PALETTE["ink"]);self.chart.create_text(x+bar*.27,165,text=RESEARCH_STATUS[k]["label_es" if self.language=="es" else "label_en"],fill=PALETTE["ink_soft"],font=("Segoe UI",8))
    def protocol_for_export(self):
        p=self.db.latest_protocol(self.study_id);return (p["config"] or {})|{"version":p["version"]}
    def save_target(self,ext,label):return filedialog.asksaveasfilename(defaultextension=ext,filetypes=[(label,"*"+ext)])
    def export_wide(self):
        if not self.study_id:return
        p=self.save_target(".csv","CSV");
        if p:export_wide_csv(self.db,self.study_id,self.protocol_for_export(),p,False);messagebox.showinfo("YomCeph",self.T("CSV de muestra válida exportado.","Valid-sample CSV exported."))
    def export_long(self):
        p=self.save_target(".csv","CSV");
        if p:export_long_csv(self.db,self.study_id,self.protocol_for_export(),p,False)
    def export_xlsx(self):
        p=self.save_target(".xlsx","Excel");
        if p:export_excel(self.db,self.study_id,self.protocol_for_export(),p)
    def export_json(self):
        p=self.save_target(".json","JSON");
        if p:export_json_bundle(self.db,self.study_id,p)
    def export_audit(self):
        p=self.save_target(".csv","CSV");
        if p:export_audit_csv(self.db,self.study_id,p)
    def export_study_report(self):
        p=self.save_target(".pdf","PDF");
        if p:export_study_pdf(self.db,self.study_id,self.protocol_for_export(),p)
    def export_case_report(self):
        if not self.case_id:messagebox.showinfo("YomCeph",self.T("Abre un caso primero.","Open a case first."));return
        p=self.save_target(".pdf","PDF");
        if p:export_case_pdf(self.db,self.case_id,self.protocol_for_export(),p)
    def backup(self):
        if not self.study_id:return
        p=self.save_target(".zip","ZIP");
        if p:self.db.backup_study(self.study_id,p);messagebox.showinfo("YomCeph",self.T("Respaldo creado.","Backup created."))
    def repro_sample(self):
        if not self.study_id:return
        n=simpledialog.askinteger("YomCeph",self.T("Número de casos completos para repetir:","Number of complete cases to repeat:"),minvalue=1,maxvalue=MAX_CASES,parent=self)
        if n:
            ex=simpledialog.askstring("YomCeph",self.T("Examinador:","Examiner:"),parent=self) or "";ids=self.db.reproducibility_sample(self.study_id,n,ex);messagebox.showinfo("YomCeph",self.T(f"Se seleccionaron {len(ids)} casos aleatoriamente.",f"Randomly selected {len(ids)} cases."))
    def show_help(self):messagebox.showinfo("YomCeph",self.T("Atajos:\nCtrl+Z deshacer\nCtrl+Y rehacer\nEspacio/→ siguiente landmark\n← landmark anterior\n+/- zoom\nEnter calcular/guardar\nF1 ayuda","Shortcuts:\nCtrl+Z undo\nCtrl+Y redo\nSpace/→ next landmark\n← previous landmark\n+/- zoom\nEnter calculate/save\nF1 help"))
    def about(self):messagebox.showinfo("YomCeph","YomCeph Desktop v0.14 Classic Research Suite\n\n"+self.T(EDU_ES,EDU_EN))
    def on_close(self):
        if self.case_id:self.autosave()
        self.destroy()


def run_research(language="es"):
    app=ResearchWorkspace(language);app.mainloop()

if __name__=="__main__":run_research()
