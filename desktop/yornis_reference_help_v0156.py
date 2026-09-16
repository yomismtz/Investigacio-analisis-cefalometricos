from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import yornis_reference_help_v0154 as base
import yornis_theme
import yornis_quality_ui_v0156 as quality

TABLES = base.TABLES
DISCLAIMER = base.DISCLAIMER


def validate_tables() -> None:
    base.validate_tables()


def _display_quality(win) -> None:
    try:
        from yornis_display_v0152 import apply_display_quality
        apply_display_quality(win, launcher=False)
    except Exception:
        pass


def _matches(table: dict, query: str) -> bool:
    if not query:
        return True
    q = query.casefold()
    hay = [table.get("title", ""), table.get("subtitle", ""), table.get("source", ""), table.get("note", "")]
    for row in table.get("rows", []):
        hay.extend(str(x) for x in row[:3])
    return q in " ".join(hay).casefold()


def open_reference_help(root, initial: str | None = None) -> None:
    validate_tables()
    t = yornis_theme.THEMES[yornis_theme.current_theme_name()]

    win = tk.Toplevel(root)
    win.title("Yornis · Referencias cefalométricas")
    win.transient(root)
    _display_quality(win)
    quality.apply_window(win, context="reference_help")

    try:
        sw, sh = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
    except Exception:
        sw, sh = 1440, 900
    width = min(max(1120, int(sw * 0.90)), max(1120, sw - 36))
    height = min(max(720, int(sh * 0.90)), max(720, sh - 50))
    win.geometry(f"{width}x{height}")
    win.minsize(980, 640)

    # Header
    header = ttk.Frame(win, padding=(22, 18, 22, 12))
    header.pack(fill="x")
    left_head = ttk.Frame(header)
    left_head.pack(side="left", fill="x", expand=True)
    ttk.Label(left_head, text="Referencias cefalométricas", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        left_head,
        text="17 tablas · referencias históricas, de muestra y por edad/sexo cuando existe evidencia compatible",
        style="Caption.TLabel",
    ).pack(anchor="w", pady=(3, 0))
    ttk.Button(header, text="Cerrar  Esc", style="Ghost.TButton", command=win.destroy).pack(side="right", padx=(12, 0))

    notice = tk.Frame(win, bg=t["accent_soft"], highlightthickness=1, highlightbackground=t["border"])
    notice.pack(fill="x", padx=22, pady=(0, 12))
    tk.Label(
        notice,
        text="ⓘ  " + DISCLAIMER,
        bg=t["accent_soft"], fg=t["text"], font=("Segoe UI", 9), justify="left",
        wraplength=max(780, width - 90), padx=14, pady=10,
    ).pack(fill="x")

    # Legend language deliberately says reference, not diagnosis.
    legend = ttk.Frame(win, padding=(22, 0, 22, 10))
    legend.pack(fill="x")
    legend_items = (
        ("↓ Menor a referencia", "#FFF3BF"),
        ("≈ Dentro de referencia", "#DDF6E8"),
        ("↑ Mayor a referencia", "#F8DDE5"),
    )
    for text, color in legend_items:
        chip = tk.Label(legend, text=text, bg=color, fg=t["text"], padx=10, pady=5, font=("Segoe UI Semibold", 9))
        chip.pack(side="left", padx=(0, 8))

    body = ttk.Panedwindow(win, orient="horizontal")
    body.pack(fill="both", expand=True, padx=22, pady=(0, 18))
    sidebar = ttk.Frame(body, padding=(0, 0, 12, 0))
    content = ttk.Frame(body, padding=(12, 0, 0, 0))
    body.add(sidebar, weight=0)
    body.add(content, weight=1)

    ttk.Label(sidebar, text="Buscar tabla o medida", style="Heading.TLabel").pack(anchor="w", pady=(0, 6))
    search_var = tk.StringVar()
    search = ttk.Entry(sidebar, textvariable=search_var, width=32)
    search.pack(fill="x", pady=(0, 10))
    count_var = tk.StringVar()
    ttk.Label(sidebar, textvariable=count_var, style="Caption.TLabel").pack(anchor="w", pady=(0, 6))

    list_frame = ttk.Frame(sidebar)
    list_frame.pack(fill="both", expand=True)
    lst = tk.Listbox(list_frame, width=34, exportselection=False)
    lst.pack(side="left", fill="both", expand=True)
    sb = ttk.Scrollbar(list_frame, orient="vertical", command=lst.yview)
    sb.pack(side="right", fill="y")
    lst.configure(yscrollcommand=sb.set)

    toolbar = ttk.Frame(content)
    toolbar.pack(fill="x", pady=(0, 8))
    title_var = tk.StringVar()
    subtitle_var = tk.StringVar()
    title_box = ttk.Frame(toolbar)
    title_box.pack(side="left", fill="x", expand=True)
    ttk.Label(title_box, textvariable=title_var, style="Heading.TLabel").pack(anchor="w")
    ttk.Label(title_box, textvariable=subtitle_var, style="Caption.TLabel").pack(anchor="w", pady=(2, 0))
    font_size = tk.IntVar(value=10)
    zoom_var = tk.StringVar(value="100%")
    ttk.Button(toolbar, text="A−", width=4, style="Ghost.TButton", command=lambda: change_font(-1)).pack(side="right", padx=2)
    ttk.Button(toolbar, text="A+", width=4, style="Ghost.TButton", command=lambda: change_font(1)).pack(side="right", padx=2)
    ttk.Label(toolbar, textvariable=zoom_var, width=7, anchor="center").pack(side="right", padx=5)

    canvas_frame = ttk.Frame(content)
    canvas_frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(canvas_frame, bg=t["panel"], highlightthickness=1, highlightbackground=t["border"])
    ybar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    xbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")
    canvas_frame.rowconfigure(0, weight=1)
    canvas_frame.columnconfigure(0, weight=1)

    table_host = tk.Frame(canvas, bg=t["border"])
    window_id = canvas.create_window((0, 0), window=table_host, anchor="nw")

    info = ttk.Frame(content, padding=(0, 10, 0, 0))
    info.pack(fill="x")
    note_var = tk.StringVar()
    source_var = tk.StringVar()
    note_lbl = ttk.Label(info, textvariable=note_var, wraplength=max(680, width - 470), justify="left", style="Panel.TLabel")
    note_lbl.pack(fill="x")
    source_lbl = ttk.Label(info, textvariable=source_var, wraplength=max(680, width - 470), justify="left", style="Muted.TLabel")
    source_lbl.pack(fill="x", pady=(4, 0))

    nav = ttk.Frame(content, padding=(0, 8, 0, 0))
    nav.pack(fill="x")
    prev_btn = ttk.Button(nav, text="← Anterior", style="Ghost.TButton")
    next_btn = ttk.Button(nav, text="Siguiente →", style="Ghost.TButton")
    prev_btn.pack(side="left")
    next_btn.pack(side="left", padx=6)

    column_widths = (180, 135, 85, 285, 265, 285)
    filtered = list(range(len(TABLES)))
    state = {"filtered_index": 0}

    def cell(parent, text, row, col, bg, *, bold=False, header=False):
        fs = font_size.get()
        font = ("Segoe UI Semibold" if (bold or header) else "Segoe UI", fs + (1 if header else 0))
        justify_left = col in (0, 3, 4, 5)
        label = tk.Label(
            parent, text=str(text), bg=bg, fg=t["text"], font=font,
            justify="left" if justify_left else "center", anchor="w" if justify_left else "center",
            wraplength=max(90, column_widths[col] - 18), padx=9, pady=8,
        )
        label.grid(row=row, column=col, sticky="nsew", padx=(1 if col else 0), pady=(1 if row else 0))
        parent.grid_columnconfigure(col, minsize=column_widths[col])

    def render_table():
        if not filtered:
            title_var.set("Sin resultados")
            subtitle_var.set("Prueba otra palabra de búsqueda.")
            note_var.set("")
            source_var.set("")
            for child in table_host.winfo_children():
                child.destroy()
            return
        state["filtered_index"] = max(0, min(state["filtered_index"], len(filtered) - 1))
        table = TABLES[filtered[state["filtered_index"]]]
        title_var.set(table["title"].title())
        subtitle_var.set(table.get("subtitle", "Referencia cefalométrica"))
        for child in table_host.winfo_children():
            child.destroy()
        headers = (
            table.get("first", "Parámetro"), "Referencia", "DE",
            "Menor a referencia", "Dentro de referencia", "Mayor a referencia",
        )
        header_bg = (t["panel_alt"], t["panel_alt"], t["panel_alt"], "#FFF3BF", "#DDF6E8", "#F8DDE5")
        for c, text in enumerate(headers):
            cell(table_host, text, 0, c, header_bg[c], header=True)
        row_bg = (t["panel"], t["panel"], t["panel"], "#FFF9DE", "#EEF9F2", "#FCEBF0")
        for r, values in enumerate(table["rows"], start=1):
            for c, text in enumerate(values):
                cell(table_host, text, r, c, row_bg[c], bold=(c == 0))
        note_var.set(table.get("note", ""))
        source_var.set("Fuente principal · " + table["source"])
        table_host.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        lst.selection_clear(0, "end")
        lst.selection_set(state["filtered_index"])
        lst.see(state["filtered_index"])
        prev_btn.configure(state="normal" if state["filtered_index"] > 0 else "disabled")
        next_btn.configure(state="normal" if state["filtered_index"] < len(filtered) - 1 else "disabled")

    def rebuild_list(*_):
        nonlocal filtered
        q = search_var.get().strip()
        filtered = [i for i, table in enumerate(TABLES) if _matches(table, q)]
        lst.delete(0, "end")
        for i in filtered:
            name = TABLES[i]["title"].replace("ANÁLISIS DE ", "").title()
            lst.insert("end", name)
        count_var.set(f"{len(filtered)} de {len(TABLES)} tablas")
        state["filtered_index"] = 0
        render_table()

    def select_from_list(_event=None):
        sel = lst.curselection()
        if sel:
            state["filtered_index"] = sel[0]
            render_table()

    def move(delta):
        if not filtered:
            return
        state["filtered_index"] = max(0, min(len(filtered) - 1, state["filtered_index"] + delta))
        render_table()

    def change_font(delta):
        font_size.set(max(8, min(15, font_size.get() + delta)))
        zoom_var.set(f"{int(round(font_size.get() / 10 * 100))}%")
        render_table()

    def resize_canvas(event):
        bbox = canvas.bbox(window_id)
        if bbox:
            natural = max(sum(column_widths), bbox[2] - bbox[0])
            canvas.itemconfigure(window_id, width=max(event.width - 4, natural))

    prev_btn.configure(command=lambda: move(-1))
    next_btn.configure(command=lambda: move(1))
    search_var.trace_add("write", rebuild_list)
    lst.bind("<<ListboxSelect>>", select_from_list)
    canvas.bind("<Configure>", resize_canvas)
    win.bind("<Escape>", lambda _e: win.destroy())
    win.bind("<Control-plus>", lambda _e: change_font(1))
    win.bind("<Control-minus>", lambda _e: change_font(-1))
    win.bind("<Control-f>", lambda _e: (search.focus_set(), "break"))

    rebuild_list()
    if initial:
        key = initial.casefold()
        for pos, idx in enumerate(filtered):
            table = TABLES[idx]
            if key in {table.get("id", "").casefold(), table.get("title", "").casefold()}:
                state["filtered_index"] = pos
                render_table()
                break
    win.after_idle(search.focus_set)


def attach_help_button(root, *, compact: bool = False) -> None:
    if getattr(root, "_yornis_reference_help_button_v0156", None) is not None:
        return
    text = "Referencias" if compact else "Referencias · F1"
    btn = ttk.Button(root, text=text, style="Ghost.TButton", command=lambda: open_reference_help(root))
    btn.place(relx=1.0, x=-18, y=14, anchor="ne")
    try:
        btn.lift()
    except Exception:
        pass
    root._yornis_reference_help_button_v0156 = btn
    root.bind("<F1>", lambda _e: open_reference_help(root), add="+")
