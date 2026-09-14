from __future__ import annotations
from tkinter import filedialog,messagebox,ttk
from yornis_spss_v015 import export_spss
from yornis_visual_report_v015 import export_case_pdf
_INSTALLED=False

def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:return
    old_build=workspace_class._build_export
    def build(self):
        old_build(self)
        box=ttk.LabelFrame(self.export_tab,text=self.T('Yornis · exportaciones adicionales','Yornis · additional exports'),padding=8);box.pack(fill='x',pady=8)
        ttk.Button(box,text=self.T('SPSS · CSV + sintaxis .sps','SPSS · CSV + .sps syntax'),command=lambda:self.export_spss_yornis()).pack(side='left',padx=4)
        ttk.Button(box,text=self.T('PDF visual del caso','Visual case PDF'),command=lambda:self.export_case_report_yornis()).pack(side='left',padx=4)
    workspace_class._build_export=build
    def export_spss_ui(self):
        if not self.study_id:return
        p=filedialog.asksaveasfilename(defaultextension='.sps',filetypes=[('SPSS Syntax','*.sps')])
        if p:
            sps,csv=export_spss(self.db,self.study_id,self.protocol_for_export(),p);messagebox.showinfo('Yornis',self.T(f'Se generaron:\n{sps}\n{csv}',f'Generated:\n{sps}\n{csv}'),parent=self)
    def export_case_ui(self):
        if not self.case_id:messagebox.showinfo('Yornis',self.T('Abre un caso primero.','Open a case first.'),parent=self);return
        p=filedialog.asksaveasfilename(defaultextension='.pdf',filetypes=[('PDF','*.pdf')])
        if p:export_case_pdf(self.db,self.case_id,p);messagebox.showinfo('Yornis',self.T('Informe visual exportado.','Visual report exported.'),parent=self)
    workspace_class.export_spss_yornis=export_spss_ui;workspace_class.export_case_report_yornis=export_case_ui
    _INSTALLED=True
