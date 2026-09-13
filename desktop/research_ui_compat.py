from __future__ import annotations

import tkinter as tk

_INSTALLED = False


class ProtocolState(dict):
    """Dictionary that also delegates Tk's WM protocol call to the owning window.

    The first ResearchWorkspace implementation used ``protocol`` for the study
    configuration, which shadows ``tk.Tk.protocol``. Keeping this compatibility
    wrapper avoids a risky rewrite of the large Classic UI while preserving the
    public ``self.protocol`` dictionary used throughout the research workflow.
    """

    def __init__(self, owner, initial=None):
        super().__init__(initial or {})
        self._owner = owner

    def __call__(self, name=None, func=None):
        return tk.Tk.protocol(self._owner, name, func)


def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:
        return
    original_setattr = workspace_class.__setattr__

    def compatible_setattr(self, name, value):
        if name == "protocol" and isinstance(value, dict) and not isinstance(value, ProtocolState):
            value = ProtocolState(self, value)
        original_setattr(self, name, value)

    workspace_class.__setattr__ = compatible_setattr
    _INSTALLED = True
