from __future__ import annotations

import re
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from PIL import Image, ImageDraw, ImageTk

import yornis_theme
import yornis_reference_help_v0156 as reference_help

ASSISTANT_VERSION = "0.15.7"

BIRD_PROFILES = {
    "Agaporni": {"tagline": "Tu guía cercana para aprender el flujo de Yornis.", "personality": "Claro, breve y paso a paso.", "shape": "lovebird"},
    "Tucán": {"tagline": "Te orienta con acciones rápidas y rutas directas.", "personality": "Visual y práctico.", "shape": "toucan"},
    "Pavorreal": {"tagline": "Organiza resultados, referencias y presentación.", "personality": "Ordenado y detallista.", "shape": "peacock"},
    "Ninfa": {"tagline": "Ideal para acompañar aprendizaje y revisión.", "personality": "Didáctico y tranquilo.", "shape": "cockatiel"},
    "Faisán": {"tagline": "Te ayuda a seguir protocolos y no saltar pasos.", "personality": "Metódico y directo.", "shape": "pheasant"},
    "Quetzal": {"tagline": "Conecta análisis, evidencia y contexto clínico.", "personality": "Académico y preciso.", "shape": "quetzal"},
    "Guacamaya Roja": {"tagline": "Te recuerda lo importante con señales muy visibles.", "personality": "Enérgico y claro.", "shape": "macaw-red"},
    "Guacamaya Azul": {"tagline": "Te acompaña en búsquedas, tablas y tareas complejas.", "personality": "Analítico y sereno.", "shape": "macaw-blue"},
}

GUIDES = [
    {"title": "Empezar un caso individual", "keywords": "inicio individual radiografia telerradiografia caso paciente abrir", "steps": ["En el lanzador elige «Caso individual».", "Carga la telerradiografía lateral.", "Selecciona los análisis o mediciones que necesitas.", "Marca únicamente los landmarks solicitados por Yornis.", "Revisa la calidad del trazado y calcula los resultados.", "Consulta F1 o este asistente para contextualizar las referencias."]},
    {"title": "Colocar landmarks", "keywords": "landmark punto puntos marcar trazado cefalometrico click", "steps": ["Amplía la radiografía hasta distinguir bien la estructura anatómica.", "Coloca cada landmark siguiendo el orden solicitado.", "Usa la lupa/zoom cuando el borde anatómico sea pequeño o dudoso.", "Si un punto queda mal, corrígelo antes de interpretar resultados.", "Yornis calcula a partir de coordenadas; la calidad del punto sí importa."]},
    {"title": "Corregir un punto", "keywords": "corregir mover arrastrar landmark deshacer rehacer error punto", "steps": ["Selecciona el punto que necesitas corregir.", "Arrástralo o usa la herramienta de corrección disponible en la vista.", "Comprueba que las líneas dependientes se actualicen.", "Si el cambio no era correcto, usa Deshacer; Rehacer restaura la última acción."]},
    {"title": "Calibrar una imagen", "keywords": "calibracion escala milimetros mm imagen radiografia regla", "steps": ["Usa una distancia conocida de la imagen o del dispositivo de calibración.", "Marca los extremos solicitados por la herramienta de calibración.", "Introduce la longitud real cuando Yornis la solicite.", "Verifica la escala antes de interpretar cualquier medida lineal en mm."]},
    {"title": "Calcular y revisar resultados", "keywords": "calcular resultados analisis valor referencia interpretar", "steps": ["Completa todos los landmarks requeridos por las variables seleccionadas.", "Ejecuta el cálculo y revisa que no haya avisos de geometría incompleta.", "Distingue el valor calculado de la referencia mostrada.", "Una referencia histórica o de muestra no equivale por sí sola a diagnóstico.", "Cuando existe evidencia compatible por edad/sexo, Yornis la identifica."]},
    {"title": "Usar las tablas de referencia", "keywords": "tabla tablas referencia normal norma F1 steiner downs tweed mcnamara", "steps": ["Pulsa F1 o «Referencias» para abrir las 17 tablas.", "Busca por análisis, parámetro o palabra clave.", "Lee primero la fuente y la nota metodológica.", "Usa «menor / dentro / mayor a referencia» como contexto descriptivo, no como diagnóstico automático.", "En C1–C7, vía aérea y cráneo-cervical revisa especialmente edad, sexo y método."], "action": "references"},
    {"title": "Vía aérea de McNamara", "keywords": "via aerea mcnamara superior inferior 6 8 10 12 edad", "steps": ["Abre la tabla de Vía aérea.", "Comprueba que la geometría usada corresponda al método de McNamara.", "Yornis muestra datos pediátricos publicados a 6, 8, 10 y 12 años.", "No se interpolan 7, 9 u 11 años.", "Las referencias históricas no estratificadas se mantienen claramente identificadas."], "reference_id": "via_aerea"},
    {"title": "Lordosis cervical C1–C7", "keywords": "lordosis cervical c1 c7 cuello postura 35 45 been", "steps": ["Yornis conserva el cálculo geométrico C1–C7.", "No usa 35–45° como corte universal automático.", "La ayuda muestra grupos publicados compatibles, no una tabla anual inventada.", "Para edades sin referencia compatible se debe interpretar el valor de forma descriptiva."], "reference_id": "lordosis_c1_c7"},
    {"title": "CVM y crecimiento cervical", "keywords": "cvm maduracion cervical crecimiento c2 c3 c4 estadio", "steps": ["Revisa la morfología de C2, C3 y C4 con buena visualización.", "Registra concavidades y forma vertebral según la interfaz.", "Yornis asigna el estadio a partir de las combinaciones implementadas.", "Usa el estadio como indicador de maduración y no como edad cronológica exacta."], "reference_id": "cvm"},
    {"title": "Crear un estudio de investigación", "keywords": "investigacion estudio protocolo crear cohorte base datos", "steps": ["Desde el lanzador entra en «Investigación».", "Crea o selecciona un estudio.", "Define y versiona el protocolo antes de completar casos.", "Registra criterios de inclusión/exclusión y variables necesarias.", "Completa casos con el mismo flujo y conserva el historial auditable."]},
    {"title": "Excluir un caso sin borrarlo", "keywords": "excluir exclusion caso investigacion auditoria borrar", "steps": ["Usa la acción de exclusión del modo Investigación.", "Registra el motivo de exclusión cuando corresponda.", "El caso permanece auditable; la exclusión no debe equivaler a eliminar datos silenciosamente."]},
    {"title": "Exportar resultados", "keywords": "exportar csv excel xlsx pdf spss json resultados dataset", "steps": ["Revisa que los casos y outcomes estén completos.", "Elige el formato de exportación necesario para tu análisis.", "Para SPSS utiliza la sintaxis generada junto con las variables/etiquetas.", "Para compartir datos, prioriza exportaciones pseudonimizadas y revisa el contenido antes de enviarlo."]},
    {"title": "Respaldar y restaurar", "keywords": "backup respaldo restaurar restore sqlite base datos seguridad", "steps": ["Crea un respaldo desde las herramientas del modo Investigación.", "Guarda la copia en una ubicación distinta al equipo de trabajo cuando sea posible.", "Antes de restaurar, confirma que el archivo corresponde al estudio esperado.", "Yornis valida la integridad del respaldo compatible antes de restaurarlo."]},
    {"title": "Cambiar la paleta y el asistente", "keywords": "paleta color tema ave asistente agaporni tucan pavorreal ninfa faisan quetzal guacamaya", "steps": ["En el lanzador selecciona una de las ocho tarjetas de color.", "La paleta completa cambia y el ave de esa paleta se convierte en tu asistente.", "El asistente conserva las mismas funciones; cambia su identidad visual.", "También puedes cambiar de paleta desde la ventana del asistente."]},
    {"title": "Buscar dentro de Yornis", "keywords": "buscar buscador interno ayuda tabla medicion analisis comando", "steps": ["Abre «Asistente» desde la esquina superior derecha.", "Escribe un análisis, una medición, una tabla o una tarea.", "El buscador combina guías, las 17 tablas y las mediciones del motor.", "Haz doble clic en una tabla para abrirla directamente en Referencias."]},
]

@dataclass(frozen=True)
class SearchItem:
    kind: str
    title: str
    subtitle: str
    text: str
    payload: object | None = None


def current_profile() -> dict:
    name = yornis_theme.current_theme_name()
    profile = dict(BIRD_PROFILES.get(name, BIRD_PROFILES["Agaporni"]))
    profile["name"] = name
    return profile


def _normalize(text: str) -> str:
    text = str(text or "").casefold()
    replacements = str.maketrans("áéíóúüñ", "aeiouun")
    return re.sub(r"\s+", " ", text.translate(replacements)).strip()


def build_search_index() -> list[SearchItem]:
    items: list[SearchItem] = []
    for guide in GUIDES:
        body = " ".join(guide.get("steps", []))
        items.append(SearchItem("Guía", guide["title"], "Cómo hacerlo paso a paso", f"{guide['title']} {guide.get('keywords', '')} {body}", guide))
    for table in reference_help.TABLES:
        rows = " ".join(" ".join(map(str, row)) for row in table.get("rows", []))
        items.append(SearchItem("Tabla", table.get("title", table.get("id", "Referencia")), table.get("subtitle", "Referencia cefalométrica"), " ".join([table.get("id", ""), table.get("title", ""), table.get("subtitle", ""), table.get("source", ""), table.get("note", ""), rows]), table))
    try:
        import classic_engine as engine
        for m in engine.MEASUREMENTS:
            title = getattr(m, "name", None) or getattr(m, "key", "Medición")
            analysis = getattr(m, "analysis", "") or "Medición cefalométrica"
            norm = getattr(m, "norm_text", "") or ""
            key = getattr(m, "key", "") or ""
            items.append(SearchItem("Medición", str(title), str(analysis), f"{title} {analysis} {norm} {key}", m))
    except Exception:
        pass
    return items


def search_content(query: str, *, limit: int = 80) -> list[SearchItem]:
    index = build_search_index()
    q = _normalize(query)
    if not q:
        return index[:limit]
    tokens = [t for t in q.split(" ") if t]
    ranked: list[tuple[int, str, SearchItem]] = []
    for item in index:
        title = _normalize(item.title)
        subtitle = _normalize(item.subtitle)
        hay = _normalize(item.text)
        if not all(token in hay for token in tokens):
            continue
        score = 0
        for token in tokens:
            if title == token:
                score += 30
            if title.startswith(token):
                score += 14
            if token in title:
                score += 10
            if token in subtitle:
                score += 4
            score += min(3, hay.count(token))
        ranked.append((-score, title, item))
    ranked.sort(key=lambda x: (x[0], x[1]))
    return [item for _, _, item in ranked[:limit]]


def _draw_avatar(theme_name: str, size: int = 180) -> Image.Image:
    profile = BIRD_PROFILES.get(theme_name, BIRD_PROFILES["Agaporni"])
    t = yornis_theme.THEMES.get(theme_name, yornis_theme.THEMES["Agaporni"])
    scale = 4
    S = max(96, int(size)) * scale
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def box(x0, y0, x1, y1):
        return tuple(int(v * S) for v in (x0, y0, x1, y1))
    def pt(*vals):
        return tuple(int(v * S) for v in vals)
    d.ellipse(box(0.03, 0.03, 0.97, 0.97), fill=t["accent_soft"], outline=t["border"], width=max(4, S // 90))
    shape = profile["shape"]
    d.ellipse(box(0.28, 0.46, 0.76, 0.92), fill=t["secondary"], outline=t["secondary_dark"], width=max(4, S // 100))
    d.ellipse(box(0.25, 0.19, 0.72, 0.67), fill=t["primary"], outline=t["primary_dark"], width=max(4, S // 100))
    if shape == "toucan":
        d.polygon([pt(0.58,0.33), pt(0.95,0.42), pt(0.63,0.56)], fill=t["accent"], outline=t["primary_dark"])
        d.polygon([pt(0.63,0.44), pt(0.92,0.43), pt(0.64,0.49)], fill=t["primary_dark"])
    elif shape == "peacock":
        for x in (0.37,0.49,0.61):
            d.line([pt(0.48,0.23), pt(x,0.06)], fill=t["secondary_dark"], width=max(3,S//120))
            d.ellipse(box(x-0.035,0.025,x+0.035,0.095), fill=t["accent"], outline=t["tertiary"], width=max(3,S//140))
        d.polygon([pt(0.55,0.42), pt(0.78,0.47), pt(0.57,0.53)], fill=t["accent"])
    elif shape == "cockatiel":
        d.polygon([pt(0.39,0.22), pt(0.47,0.02), pt(0.53,0.24)], fill=t["accent"], outline=t["secondary_dark"])
        d.ellipse(box(0.50,0.43,0.62,0.55), fill=t["secondary"])
        d.polygon([pt(0.60,0.43), pt(0.79,0.48), pt(0.61,0.53)], fill=t["accent"])
    elif shape == "pheasant":
        d.polygon([pt(0.34,0.24), pt(0.42,0.10), pt(0.48,0.25)], fill=t["tertiary"])
        d.ellipse(box(0.49,0.37,0.63,0.52), fill=t["danger"])
        d.polygon([pt(0.60,0.42), pt(0.80,0.48), pt(0.61,0.53)], fill=t["accent"])
    elif shape == "quetzal":
        d.polygon([pt(0.59,0.42), pt(0.79,0.47), pt(0.60,0.53)], fill=t["accent"])
        d.polygon([pt(0.40,0.75), pt(0.46,0.98), pt(0.52,0.72)], fill=t["secondary_dark"])
        d.polygon([pt(0.50,0.76), pt(0.58,0.98), pt(0.61,0.70)], fill=t["secondary"])
    elif shape.startswith("macaw"):
        d.ellipse(box(0.42,0.31,0.66,0.58), fill="#FFF7E7")
        d.arc(box(0.43,0.34,0.63,0.55), 210, 340, fill=t["primary_dark"], width=max(3,S//120))
        d.polygon([pt(0.60,0.41), pt(0.82,0.47), pt(0.60,0.55)], fill=t["accent"], outline=t["primary_dark"])
        d.polygon([pt(0.35,0.72), pt(0.44,0.98), pt(0.51,0.72)], fill=t["secondary"])
    else:
        d.ellipse(box(0.30,0.22,0.68,0.59), fill=t["tertiary"])
        d.polygon([pt(0.60,0.41), pt(0.77,0.48), pt(0.60,0.54)], fill=t["accent"])
    d.ellipse(box(0.48,0.33,0.56,0.41), fill=t["primary_dark"])
    d.ellipse(box(0.505,0.345,0.53,0.37), fill="#FFFFFF")
    d.arc(box(0.34,0.52,0.70,0.86), 185, 345, fill=t["accent"], width=max(5,S//75))
    return im.resize((size, size), Image.Resampling.LANCZOS)


def make_avatar_photo(master, size: int = 180, theme_name: str | None = None):
    name = theme_name or yornis_theme.current_theme_name()
    return ImageTk.PhotoImage(_draw_avatar(name, size=size), master=master)


def avatar_signature(theme_name: str) -> tuple[str, str]:
    profile = BIRD_PROFILES[theme_name]
    return theme_name, profile["shape"]


def _details_for_item(item: SearchItem) -> tuple[str, str]:
    if item.kind == "Guía":
        guide = item.payload or {}
        steps = "\n".join(f"{i}. {step}" for i, step in enumerate(guide.get("steps", []), start=1))
        return item.title, steps
    if item.kind == "Tabla":
        table = item.payload or {}
        rows = table.get("rows", [])
        preview = "\n".join(" · ".join(map(str, row[:3])) for row in rows[:7])
        text = f"{table.get('subtitle','')}\n\n{preview}"
        if len(rows) > 7:
            text += f"\n… y {len(rows)-7} filas más."
        if table.get("note"):
            text += f"\n\nNota: {table['note']}"
        if table.get("source"):
            text += f"\n\nFuente principal: {table['source']}"
        return item.title, text
    m = item.payload
    analysis = getattr(m, "analysis", item.subtitle)
    norm = getattr(m, "norm_text", "") or "Sin texto de referencia disponible."
    key = getattr(m, "key", "") or ""
    text = f"Análisis: {analysis}\n"
    if key:
        text += f"Clave: {key}\n"
    text += f"\nReferencia/contexto:\n{norm}"
    return item.title, text


def refresh_assistant_button(root) -> None:
    btn = getattr(root, "_yornis_assistant_button_v0157", None)
    if btn is not None:
        try:
            btn.configure(text=f"Asistente · {yornis_theme.current_theme_name()}")
        except Exception:
            pass


def open_assistant(root, initial_query: str = "") -> None:
    profile = current_profile()
    theme_name = profile["name"]
    t = yornis_theme.THEMES[theme_name]
    win = tk.Toplevel(root)
    win.title(f"Yornis · {theme_name}, asistente virtual")
    win.transient(root)
    try:
        from yornis_display_v0152 import apply_display_quality
        apply_display_quality(win, launcher=False)
    except Exception:
        pass
    try:
        import yornis_quality_ui_v0157 as quality
        quality.apply_window(win, context="assistant")
    except Exception:
        pass
    sw, sh = max(1100, int(win.winfo_screenwidth())), max(760, int(win.winfo_screenheight()))
    width, height = min(1220, sw - 60), min(820, sh - 80)
    win.geometry(f"{width}x{height}")
    win.minsize(980, 650)

    shell = ttk.Frame(win, padding=(20, 18))
    shell.pack(fill="both", expand=True)
    left = ttk.Frame(shell, style="Assistant.Card.TFrame", padding=(18, 16))
    left.pack(side="left", fill="y", padx=(0, 16))
    right = ttk.Frame(shell)
    right.pack(side="left", fill="both", expand=True)

    avatar = make_avatar_photo(win, 190, theme_name)
    avatar_lbl = tk.Label(left, image=avatar, bg=t["panel"])
    avatar_lbl.image = avatar
    avatar_lbl.pack(pady=(2, 10))
    ttk.Label(left, text=theme_name, style="Assistant.Title.TLabel").pack()
    ttk.Label(left, text="Asistente virtual de Yornis", style="Assistant.Subtitle.TLabel").pack(pady=(2, 8))
    ttk.Label(left, text=profile["tagline"], style="Assistant.Body.TLabel", wraplength=250, justify="center").pack(pady=(0, 8))
    ttk.Label(left, text=profile["personality"], style="Assistant.Muted.TLabel", wraplength=250, justify="center").pack(pady=(0, 14))

    search_var = tk.StringVar(value=initial_query)
    ttk.Button(left, text="Abrir las 17 tablas", style="Primary.TButton", command=lambda: reference_help.open_reference_help(root)).pack(fill="x", pady=4)
    ttk.Button(left, text="¿Cómo empiezo?", style="Secondary.TButton", command=lambda: search_var.set("empezar caso individual")).pack(fill="x", pady=4)
    ttk.Button(left, text="Buscar vía aérea", style="Ghost.TButton", command=lambda: search_var.set("via aerea")).pack(fill="x", pady=4)
    ttk.Separator(left).pack(fill="x", pady=14)
    ttk.Label(left, text="Cambiar ave / paleta", style="Assistant.Heading.TLabel").pack(anchor="w", pady=(0, 7))
    palette_grid = ttk.Frame(left, style="Assistant.Card.TFrame")
    palette_grid.pack(fill="x")

    def switch_theme(name: str):
        if name == yornis_theme.current_theme_name():
            return
        yornis_theme.apply_theme(name)
        try:
            import yornis_quality_ui_v0157 as quality
            quality.apply_window(root, context="app")
        except Exception:
            pass
        refresh_assistant_button(root)
        q = search_var.get()
        win.destroy()
        try:
            root.after(40, lambda: open_assistant(root, q))
        except Exception:
            pass

    for i, name in enumerate(yornis_theme.theme_names()):
        th = yornis_theme.THEMES[name]
        selected = name == theme_name
        b = tk.Button(palette_grid, text=name, command=lambda n=name: switch_theme(n), bg=th["primary"] if selected else th["panel_alt"], fg="#FFFFFF" if selected else th["text"], activebackground=th["secondary"], activeforeground="#FFFFFF", relief="solid", bd=1, padx=6, pady=5, font=("Segoe UI Semibold", 8), cursor="hand2")
        b.grid(row=i // 2, column=i % 2, sticky="ew", padx=3, pady=3)
        palette_grid.grid_columnconfigure(i % 2, weight=1)

    ttk.Label(right, text="¿Qué necesitas hacer?", style="Title.TLabel").pack(anchor="w")
    ttk.Label(right, text="Busca una tarea, análisis, medición o tabla. El buscador funciona dentro de Yornis y no envía tu consulta a la nube.", style="Caption.TLabel", wraplength=760, justify="left").pack(anchor="w", fill="x", pady=(2, 10))
    search_row = ttk.Frame(right)
    search_row.pack(fill="x")
    search = ttk.Entry(search_row, textvariable=search_var, font=("Segoe UI", 11))
    search.pack(side="left", fill="x", expand=True)
    ttk.Button(search_row, text="Limpiar", style="Ghost.TButton", command=lambda: search_var.set("")).pack(side="left", padx=(8, 0))
    count_var = tk.StringVar()
    ttk.Label(right, textvariable=count_var, style="Caption.TLabel").pack(anchor="w", pady=(5, 7))

    results_box = ttk.Frame(right)
    results_box.pack(fill="both", expand=True)
    tree = ttk.Treeview(results_box, columns=("kind", "title", "subtitle"), show="headings", selectmode="browse")
    for col, text, width_col in (("kind", "Tipo", 90), ("title", "Resultado", 260), ("subtitle", "Contexto", 360)):
        tree.heading(col, text=text)
        tree.column(col, width=width_col, stretch=(col != "kind"))
    tree.pack(side="left", fill="both", expand=True)
    sb = ttk.Scrollbar(results_box, orient="vertical", command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=sb.set)

    detail = tk.Text(right, height=12, wrap="word", bg=t["panel"], fg=t["text"], relief="flat", highlightthickness=1, highlightbackground=t["border"], padx=12, pady=10, font=("Segoe UI", 10))
    detail.pack(fill="x", pady=(10, 0))
    detail.configure(state="disabled")
    actions = ttk.Frame(right)
    actions.pack(fill="x", pady=(8, 0))
    open_btn = ttk.Button(actions, text="Abrir", style="Primary.TButton")
    open_btn.pack(side="left")
    ttk.Button(actions, text="Referencias completas · F1", style="Ghost.TButton", command=lambda: reference_help.open_reference_help(root)).pack(side="left", padx=7)
    ttk.Button(actions, text="Cerrar", style="Ghost.TButton", command=win.destroy).pack(side="right")

    state = {"items": []}

    def selected_item():
        sel = tree.selection()
        if not sel:
            return None
        try:
            return state["items"][int(sel[0].split("_")[-1])]
        except Exception:
            return None

    def show_details(_event=None):
        item = selected_item()
        detail.configure(state="normal")
        detail.delete("1.0", "end")
        if item is None:
            detail.insert("1.0", "Selecciona un resultado para ver la ayuda.")
            open_btn.configure(state="disabled")
        else:
            title, text = _details_for_item(item)
            detail.insert("1.0", f"{title}\n\n{text}")
            open_btn.configure(state="normal")
        detail.configure(state="disabled")

    def open_selected(_event=None):
        item = selected_item()
        if item is None:
            return
        if item.kind == "Tabla":
            table = item.payload or {}
            reference_help.open_reference_help(root, initial=table.get("id"))
        elif item.kind == "Guía":
            guide = item.payload or {}
            rid = guide.get("reference_id")
            if rid:
                reference_help.open_reference_help(root, initial=rid)
            elif guide.get("action") == "references":
                reference_help.open_reference_help(root)
        else:
            show_details()

    def rebuild(*_):
        items = search_content(search_var.get())
        state["items"] = items
        for iid in tree.get_children():
            tree.delete(iid)
        for i, item in enumerate(items):
            tree.insert("", "end", iid=f"item_{i}", values=(item.kind, item.title, item.subtitle))
        count_var.set(f"{len(items)} resultados · guías + 17 tablas + mediciones")
        if items:
            tree.selection_set("item_0")
            tree.focus("item_0")
        show_details()

    open_btn.configure(command=open_selected)
    search_var.trace_add("write", rebuild)
    tree.bind("<<TreeviewSelect>>", show_details)
    tree.bind("<Double-1>", open_selected)
    win.bind("<Escape>", lambda _e: win.destroy())
    win.bind("<Control-f>", lambda _e: (search.focus_set(), "break"))
    win.bind("<Return>", open_selected)
    rebuild()
    win.after_idle(search.focus_set)


def attach_assistant_button(root, *, compact: bool = False) -> None:
    existing = getattr(root, "_yornis_assistant_button_v0157", None)
    if existing is not None:
        try:
            if existing.winfo_exists():
                refresh_assistant_button(root)
                return
        except Exception:
            pass
    btn = ttk.Button(root, text=f"Asistente · {yornis_theme.current_theme_name()}", style="Assistant.TButton", command=lambda: open_assistant(root))
    btn.place(relx=1.0, x=(-145 if compact else -178), y=14, anchor="ne")
    try:
        btn.lift()
    except Exception:
        pass
    root._yornis_assistant_button_v0157 = btn
    root.bind("<Control-k>", lambda _e: open_assistant(root), add="+")
