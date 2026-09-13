from __future__ import annotations
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog,messagebox,ttk
_INSTALLED=False

def run_import(app,paths,metadata=None):
    if not paths:return
    w=tk.Toplevel(app);w.title(app.T('Importando radiografías','Importing radiographs'));w.transient(app);w.grab_set();w.geometry('520x190');cancel=threading.Event();text=tk.StringVar(value='0 / 0');detail=tk.StringVar(value=app.T('Preparando…','Preparing…'));bar=ttk.Progressbar(w,mode='determinate');ttk.Label(w,textvariable=text,font=('Segoe UI',13,'bold')).pack(pady=(18,5));bar.pack(fill='x',padx=22,pady=5);ttk.Label(w,textvariable=detail).pack(pady=4);ttk.Button(w,text=app.T('Cancelar','Cancel'),command=cancel.set).pack(pady=8)
    def progress(i,total,result):
        def ui():bar['maximum']=max(1,total);bar['value']=i;text.set(f'{i} / {total}');detail.set(app.T(f'Agregadas {result.added} · duplicadas {result.duplicates} · omitidas {result.skipped}',f'Added {result.added} · duplicates {result.duplicates} · skipped {result.skipped}'))
        app.after(0,ui)
    def worker():
        result=app.db.import_files_progress(app.study_id,paths,metadata or {},True,progress,cancel)
        def done():
            try:w.grab_release();w.destroy()
            except Exception:pass
            app.refresh_cases();app.refresh_dashboard();messagebox.showinfo('Yornis',app.T(f'Importación terminada.\nAgregadas: {result.added}\nDuplicadas: {result.duplicates}\nOmitidas: {result.skipped}',f'Import finished.\nAdded: {result.added}\nDuplicates: {result.duplicates}\nSkipped: {result.skipped}'),parent=app)
        app.after(0,done)
    threading.Thread(target=worker,daemon=True).start()

def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:return
    def import_files(self):
        if not self.require_study():return
        files=filedialog.askopenfilenames(filetypes=[('Radiografías','*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pdf'),('Todos','*.*')]);run_import(self,list(files)) if files else None
    def import_folder(self):
        if not self.require_study():return
        folder=filedialog.askdirectory();
        if not folder:return
        csv_path=filedialog.askopenfilename(title=self.T('CSV de metadatos opcional (Cancelar para omitir)','Optional metadata CSV (Cancel to skip)'),filetypes=[('CSV','*.csv')]);meta=self.db.read_metadata_csv(csv_path) if csv_path else {};allowed={'.png','.jpg','.jpeg','.bmp','.tif','.tiff','.pdf'};paths=sorted(str(p) for p in Path(folder).iterdir() if p.is_file() and p.suffix.lower() in allowed);run_import(self,paths,meta)
    workspace_class.import_files=import_files;workspace_class.import_folder=import_folder;_INSTALLED=True
