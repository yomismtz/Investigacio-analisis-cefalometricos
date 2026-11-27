from __future__ import annotations
"""Radiograph viewport patch: scrollable source-image canvas and larger magnifier."""
import tkinter as tk

_INSTALLED = False
_ORIGINAL_CREATE_IMAGE = tk.Canvas.create_image
_ORIGINAL_TOPLEVEL_TITLE = tk.Toplevel.title

def _refresh(canvas):
    try:
        bounds = canvas.bbox("all")
        if bounds:
            canvas.configure(scrollregion=bounds)
    except tk.TclError:
        pass

def _scroll_x(canvas, event):
    try:
        canvas.xview_scroll(-1 if event.delta > 0 else 1, "units")
    except tk.TclError:
        pass
    return "break"

def _scroll_y(canvas, event):
    try:
        canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
    except tk.TclError:
        pass
    return "break"

def _attach_viewport(canvas):
    if getattr(canvas, "_yornis_viewport_attached", False):
        return
    try:
        parent = canvas.master
        hbar = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        vbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set,
                         xscrollincrement=20, yscrollincrement=20, confine=False)
        # Overlay to preserve the application's existing geometry manager.
        hbar.place(relx=0, rely=1, relwidth=1, anchor="sw", height=14)
        vbar.place(relx=1, rely=0, relheight=1, anchor="ne", width=14)
        hbar.lift()
        vbar.lift()
        canvas._yornis_hscrollbar = hbar
        canvas._yornis_vscrollbar = vbar
        canvas._yornis_viewport_attached = True
        canvas.bind("<Configure>", lambda _e: _refresh(canvas), add="+")
        canvas.bind("<Shift-MouseWheel>", lambda e: _scroll_x(canvas, e), add="+")
        canvas.bind("<MouseWheel>", lambda e: _scroll_y(canvas, e), add="+")
        canvas.after_idle(lambda: _refresh(canvas))
    except (tk.TclError, AttributeError):
        return

def _create_image(self, *args, **kwargs):
    item = _ORIGINAL_CREATE_IMAGE(self, *args, **kwargs)
    try:
        bounds = self.bbox(item)
        # Only the large radiograph viewport gets scrollbars; small logos,
        # thumbnails and the magnifier's cropped preview remain untouched.
        if bounds and (bounds[2] - bounds[0]) >= 600 and (bounds[3] - bounds[1]) >= 400:
            _attach_viewport(self)
            self.after_idle(lambda: _refresh(self))
    except tk.TclError:
        pass
    return item

def _toplevel_title(self, *args):
    result = _ORIGINAL_TOPLEVEL_TITLE(self, *args)
    if args:
        title = str(args[0]).casefold()
        if any(word in title for word in ("lupa", "magnifier", "zoom", "ampliación", "ampliacion")):
            try:
                self.minsize(520, 440)
                self.geometry("640x520")
            except tk.TclError:
                pass
    return result

def install():
    global _INSTALLED
    if _INSTALLED:
        return
    tk.Canvas.create_image = _create_image
    tk.Toplevel.title = _toplevel_title
    _INSTALLED = True
