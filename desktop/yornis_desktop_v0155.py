from __future__ import annotations

# v0.15.5 is a maintenance/evidence release over the audited v0.15.4 stack.
# Calculation geometry is preserved. Age/sex references are only applied when
# the published measurement is compatible; missing ages are not interpolated.
import yornis_desktop_v015 as legacy
import yornis_audit_hardening_v0154 as hardening
import yornis_evidence_v0155 as evidence

reference_help = evidence.reference_help
APP_VERSION = "0.15.5 Research Suite · Evidence by Age/Sex"
legacy.APP_VERSION = APP_VERSION
Launcher = legacy.Launcher


def research_app(lang):
    import research_ui, research_ui_compat, research_enhancements
    import research_stability_db_v0141, research_stability_ui_core_v0141, research_stability_ui_perf_v0141, research_stability_export_ui_v0141
    import yornis_storage_v015, yornis_import_v015, yornis_background_import_v015, yornis_research_controls_v015, yornis_ui_theme_v015, yornis_export_ui_v015, yornis_backup_v015, yornis_backup_ui_v015

    research_ui_compat.install(research_ui.ResearchWorkspace)
    research_enhancements.install(research_ui.ResearchWorkspace)
    research_stability_db_v0141.install()
    yornis_storage_v015.install()
    yornis_import_v015.install()
    yornis_backup_v015.install()
    research_stability_ui_core_v0141.install(research_ui.ResearchWorkspace, research_ui.ScrollChecks)
    research_stability_ui_perf_v0141.install(research_ui.ResearchWorkspace)
    research_stability_export_ui_v0141.install(research_ui.ResearchWorkspace)
    yornis_background_import_v015.install(research_ui.ResearchWorkspace)
    yornis_research_controls_v015.install(research_ui.ResearchWorkspace)
    yornis_ui_theme_v015.install(research_ui.ResearchWorkspace)
    yornis_export_ui_v015.install(research_ui.ResearchWorkspace)
    yornis_backup_ui_v015.install(research_ui.ResearchWorkspace)
    legacy.yornis_clinical_audit_v0151.install(research_ui.ResearchWorkspace)
    legacy.yornis_cervical_v0152.install_research(research_ui.ResearchWorkspace)
    legacy.yornis_alignment_v0152.install_research(research_ui.ResearchWorkspace)
    legacy.yornis_ceph_quality_v0153.install_research(research_ui.ResearchWorkspace)
    hardening.install_research(research_ui.ResearchWorkspace)
    # Evidence layer goes last so older compatibility layers cannot restore a
    # previous reference or universal cut-off during application startup.
    evidence.install()

    app = research_ui.ResearchWorkspace(lang)
    app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION}")
    legacy.display.apply_display_quality(app, launcher=False)
    reference_help.attach_help_button(app)
    return app


def main():
    evidence.install()
    launch = Launcher()
    reference_help.attach_help_button(launch, compact=True)
    launch.mainloop()
    mode = launch.choice
    lang = launch.language
    if mode == "individual":
        import yomceph_desktop_v130_classic as classic
        legacy.yornis_cervical_v0152.install_individual(classic.YomCephClassic)
        legacy.yornis_alignment_v0152.install_individual(classic.YomCephClassic)
        legacy.yornis_ceph_quality_v0153.install_individual(classic.YomCephClassic)
        hardening.install_individual(classic.YomCephClassic)
        evidence.install()
        app = classic.YomCephClassic()
        app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION} · Individual")
        legacy.display.apply_display_quality(app, launcher=False)
        reference_help.attach_help_button(app)
        app.mainloop()
    elif mode == "research":
        research_app(lang).mainloop()


if __name__ == "__main__":
    main()
