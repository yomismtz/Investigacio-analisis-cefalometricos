from __future__ import annotations

import multiprocessing

import yornis_desktop_v0154 as v154
import yornis_pdf_safe_v0155 as pdf_safe

APP_VERSION = "0.15.5 Final Hardening · HiDPI"
v154.APP_VERSION = APP_VERSION
v154.legacy.APP_VERSION = APP_VERSION
Launcher = v154.Launcher


def install_v0155_runtime_guards() -> None:
    import research_ui
    import yomceph_desktop_v130_classic as classic

    pdf_safe.install(research_ui.ResearchWorkspace)
    if hasattr(classic, "YomCephClassic") and hasattr(classic.YomCephClassic, "load_pil"):
        pdf_safe.install(classic.YomCephClassic)


def research_app(lang):
    install_v0155_runtime_guards()
    return v154.research_app(lang)


def main() -> None:
    install_v0155_runtime_guards()
    # v0.15.4 reads its APP_VERSION global dynamically, which is replaced above.
    v154.main()


if __name__ == "__main__":
    # Required by frozen Windows applications that create a spawn worker for
    # isolated PDF rendering.
    multiprocessing.freeze_support()
    main()
