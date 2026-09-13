from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import yomceph_desktop_v014 as base
import yornis_theme

APP_VERSION='0.15.0 Research Suite'

class Launcher(base.Launcher):
    def __init__(self):
        yornis_theme.apply_theme(yornis_theme.current_theme_name(),persist=False);super().__init__();self.geometry('920x720');self.minsize(840,680);self.title('Yornis · Yom Dental Análisis');self.title_lbl.config(text='Yornis');self.ver_lbl.config(text=f'Yom Dental Análisis · v{APP_VERSION}');self._add_yornis_panel()
    def refresh_text(self):
        base.Launcher.refresh_text(self)
        if hasattr(self,'title_lbl'):self.title_lbl.config(text='Yornis')
        if hasattr(self,'note'):self.note.config(text=self.tr('Ciencia que vuela más alto · análisis cefalométrico e investigación.','Science that flies higher · cephalometric analysis and research.'))
    def _add_yornis_panel(self):
        row=ttk.Frame(self.main);row.pack(fill='x',pady=(2,6));ttk.Label(row,text=self.tr('Tema inspirado en aves:','Bird-inspired theme:')).pack(side='left',padx=4);cb=ttk.Combobox(row,state='readonly',values=yornis_theme.theme_names(),width=20);cb.set(yornis_theme.current_theme_name());cb.pack(side='left');cb.bind('<<ComboboxSelected>>',lambda e:self._theme(cb.get()))
        why=ttk.LabelFrame(self.main,text=self.tr('¿Por qué Yornis?','Why Yornis?'),padding=6);why.pack(fill='x',padx=20,pady=4)
        for head,text in [('Y','Yom'),('ORNIS',self.tr('Ave · raíz clásica','Bird · classical root')),('VUELO',self.tr('Precisión y visión','Precision and vision')),('CIENCIA',self.tr('Tecnología que inspira','Technology that inspires'))]:
            f=ttk.Frame(why,padding=5);f.pack(side='left',fill='both',expand=True,padx=3);ttk.Label(f,text=head,font=('Segoe UI',10,'bold')).pack();ttk.Label(f,text=text,wraplength=160).pack()
    def _theme(self,name):
        yornis_theme.apply_theme(name);self.note.config(text=self.tr(f'Tema {name} seleccionado. Se aplicará a Yornis.',f'{name} theme selected. It will apply to Yornis.'))

def research_app(lang):
    import research_ui,research_ui_compat,research_enhancements
    import research_stability_db_v0141,research_stability_ui_core_v0141,research_stability_ui_perf_v0141,research_stability_export_ui_v0141
    import yornis_storage_v015,yornis_import_v015,yornis_background_import_v015,yornis_research_controls_v015,yornis_ui_theme_v015,yornis_export_ui_v015,yornis_backup_v015,yornis_backup_ui_v015
    research_ui_compat.install(research_ui.ResearchWorkspace);research_enhancements.install(research_ui.ResearchWorkspace);research_stability_db_v0141.install();yornis_storage_v015.install();yornis_import_v015.install();yornis_backup_v015.install();research_stability_ui_core_v0141.install(research_ui.ResearchWorkspace,research_ui.ScrollChecks);research_stability_ui_perf_v0141.install(research_ui.ResearchWorkspace);research_stability_export_ui_v0141.install(research_ui.ResearchWorkspace);yornis_background_import_v015.install(research_ui.ResearchWorkspace);yornis_research_controls_v015.install(research_ui.ResearchWorkspace);yornis_ui_theme_v015.install(research_ui.ResearchWorkspace);yornis_export_ui_v015.install(research_ui.ResearchWorkspace);yornis_backup_ui_v015.install(research_ui.ResearchWorkspace)
    app=research_ui.ResearchWorkspace(lang);app.title(f'Yornis · Yom Dental Análisis · v{APP_VERSION}');return app

def main():
    launch=Launcher();launch.mainloop();mode=launch.choice;lang=launch.language
    if mode=='individual':
        import yomceph_desktop_v130_classic as classic
        app=classic.YomCephClassic();app.title(f'Yornis · Yom Dental Análisis · v{APP_VERSION} · Individual');app.mainloop()
    elif mode=='research':research_app(lang).mainloop()

if __name__=='__main__':main()
