from __future__ import annotations
from tkinter import messagebox
from research_export_v0141 import export_wide,export_long,export_excel,export_json,export_case_pdf

_INSTALLED=False

def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:return
    def export_wide_ui(self):
        if not self.study_id:return
        p=self.save_target('.csv','CSV')
        if p:export_wide(self.db,self.study_id,p,False);messagebox.showinfo('YomCeph',self.T('CSV de muestra válida exportado.','Valid-sample CSV exported.'))
    def export_long_ui(self):
        if not self.study_id:return
        p=self.save_target('.csv','CSV')
        if p:export_long(self.db,self.study_id,p,False)
    def export_xlsx_ui(self):
        if not self.study_id:return
        p=self.save_target('.xlsx','Excel')
        if p:export_excel(self.db,self.study_id,p);messagebox.showinfo('YomCeph',self.T('Excel exportado con versiones de protocolo y landmarks X/Y.','Excel exported with protocol versions and X/Y landmarks.'))
    def export_json_ui(self):
        if not self.study_id:return
        p=self.save_target('.json','JSON')
        if p:export_json(self.db,self.study_id,p)
    def export_case_ui(self):
        if not self.case_id:messagebox.showinfo('YomCeph',self.T('Abre un caso primero.','Open a case first.'));return
        p=self.save_target('.pdf','PDF')
        if p:export_case_pdf(self.db,self.case_id,p)
    workspace_class.export_wide=export_wide_ui;workspace_class.export_long=export_long_ui;workspace_class.export_xlsx=export_xlsx_ui;workspace_class.export_json=export_json_ui;workspace_class.export_case_report=export_case_ui
    _INSTALLED=True
