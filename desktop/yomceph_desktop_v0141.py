from __future__ import annotations
import yomceph_desktop_v014 as base

APP_VERSION='0.14.1 Classic Research Suite'

class Launcher(base.Launcher):
    def __init__(self):
        super().__init__()
        self.ver_lbl.config(text=f'v{APP_VERSION}')

def main():
    launch=Launcher();launch.mainloop();mode=launch.choice;lang=launch.language
    if mode=='individual':
        import yomceph_desktop_v130_classic as classic
        app=classic.YomCephClassic()
        try:app.title(f'YomCeph Desktop · v{APP_VERSION} · Individual')
        except Exception:pass
        app.mainloop()
    elif mode=='research':
        import research_ui,research_ui_compat,research_enhancements
        import research_stability_db_v0141,research_stability_ui_core_v0141,research_stability_ui_perf_v0141,research_stability_export_ui_v0141
        research_ui_compat.install(research_ui.ResearchWorkspace)
        research_enhancements.install(research_ui.ResearchWorkspace)
        research_stability_db_v0141.install()
        research_stability_ui_core_v0141.install(research_ui.ResearchWorkspace,research_ui.ScrollChecks)
        research_stability_ui_perf_v0141.install(research_ui.ResearchWorkspace)
        research_stability_export_ui_v0141.install(research_ui.ResearchWorkspace)
        app=research_ui.ResearchWorkspace(lang);app.title(f'YomCeph Desktop · v{APP_VERSION}');app.mainloop()

if __name__=='__main__':main()
