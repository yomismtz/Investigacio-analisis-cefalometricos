from __future__ import annotations
import csv, json, math
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

try:
    from PIL import Image, ImageTk, ImageOps
except Exception:
    Image = ImageTk = ImageOps = None

APP_NAME = "YomCeph Desktop"
APP_VERSION = "0.13.0 Preview"
EDU = "Uso educativo e investigación. No es un dispositivo médico ni sustituye el diagnóstico profesional."

# Geometry
def P(points, k):
    v = points.get(k)
    if v is None:
        raise KeyError(k)
    return v

def vec(a, b): return (b[0] - a[0], b[1] - a[1])
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def norm(v): return math.hypot(v[0], v[1])
def unit(v):
    n = norm(v)
    if n < 1e-9:
        raise ValueError("segmento degenerado")
    return (v[0] / n, v[1] / n)
def dist(a, b): return math.hypot(b[0] - a[0], b[1] - a[1])
def angle_between(v1, v2):
    u1, u2 = unit(v1), unit(v2)
    return math.degrees(math.acos(max(-1.0, min(1.0, dot(u1, u2)))))
def acute_lines(a, b, c, d):
    x = angle_between(vec(a, b), vec(c, d))
    return min(x, 180.0 - x)
def obtuse_lines(a, b, c, d):
    x = acute_lines(a, b, c, d)
    return 180.0 - x
def angle3(a, b, c): return angle_between(vec(b, a), vec(b, c))
def project(q, a, b):
    ab = vec(a, b)
    den = dot(ab, ab)
    if den < 1e-9:
        raise ValueError("línea degenerada")
    t = dot((q[0] - a[0], q[1] - a[1]), ab) / den
    return (a[0] + t * ab[0], a[1] + t * ab[1])
def signed_point_line(q, a, b, anterior_axis):
    pr = project(q, a, b)
    tangent = unit(vec(a, b))
    normal = (-tangent[1], tangent[0])
    ant = unit(anterior_axis)
    if dot(normal, ant) < 0:
        normal = (-normal[0], -normal[1])
    return dot((q[0] - pr[0], q[1] - pr[1]), normal)
def signed_along(q, origin, axis):
    return dot((q[0] - origin[0], q[1] - origin[1]), unit(axis))
def rotate(v, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)
def hp_axes(points):
    sn = unit(vec(P(points, "S"), P(points, "N")))
    fh = unit(vec(P(points, "Po"), P(points, "Or")))
    c1, c2 = unit(rotate(sn, 7.0)), unit(rotate(sn, -7.0))
    h = c1 if dot(c1, fh) >= dot(c2, fh) else c2
    if dot(h, fh) < 0:
        h = (-h[0], -h[1])
    v = (-h[1], h[0])
    if "Me" in points and dot(v, vec(P(points, "N"), P(points, "Me"))) < 0:
        v = (-v[0], -v[1])
    return h, v
def least_squares_line_center(lines):
    aa = ab = bb = ac = bc = 0.0
    normalized = []
    for p1, p2 in lines:
        dx, dy = vec(p1, p2)
        m = math.hypot(dx, dy)
        if m < 1e-9:
            raise ValueError("plano degenerado")
        a, b = -dy / m, dx / m
        c = -(a * p1[0] + b * p1[1])
        normalized.append((a, b, c))
        aa += a * a; ab += a * b; bb += b * b; ac += a * c; bc += b * c
    determinant = aa * bb - ab * ab
    if abs(determinant) < 1e-9:
        raise ValueError("planos casi paralelos")
    x = (-ac * bb + ab * bc) / determinant
    y = (-aa * bc + ab * ac) / determinant
    rms = math.sqrt(sum((a * x + b * y + c) ** 2 for a, b, c in normalized) / len(normalized))
    return (x, y), rms

@dataclass
class M:
    analysis: str
    name: str
    kind: str
    pts: tuple[str, ...]
    norm_text: str = ""
    lo: float | None = None
    hi: float | None = None
    unit: str = "°"

MEAS = []
def add(a, n, k, p, normtxt="", lo=None, hi=None, unit="°"):
    MEAS.append(M(a, n, k, tuple(p), normtxt, lo, hi, unit))

# Steiner
add("Steiner", "SNA", "angle3", ["S", "N", "A"], "82° ±2°", 80, 84)
add("Steiner", "SNB", "angle3", ["S", "N", "B"], "80° ±2°", 78, 82)
add("Steiner", "ANB", "anb", ["S", "N", "A", "B"], "2° ±2°", 0, 4)
add("Steiner", "SN / Go-Gn", "acute", ["S", "N", "Go", "Gn"], "32° ±4°", 28, 36)
add("Steiner", "U1 / SN", "obtuse", ["U1i", "U1a", "S", "N"], "103° ±4°", 99, 107)
add("Steiner", "U1 / NA", "acute", ["U1i", "U1a", "N", "A"], "22° ±6°", 16, 28)
add("Steiner", "L1 / NB", "acute", ["L1i", "L1a", "N", "B"], "25° ±4°", 21, 29)
add("Steiner", "Interincisal", "obtuse", ["U1i", "U1a", "L1i", "L1a"], "131° ±4°", 127, 135)
add("Steiner", "Plano oclusal / SN", "acute", ["OcP", "OcA", "S", "N"], "14° ±3°", 11, 17)
# Downs
add("Downs", "Ángulo facial FH / N-Pg", "acute", ["Po", "Or", "N", "Pg"], "87.8° ±3.6°", 84.2, 91.4)
add("Downs", "Plano mandibular / FH", "acute", ["Go", "Me", "Po", "Or"], "21.9° ±3.2°", 18.7, 25.1)
add("Downs", "Eje Y FH / S-Gn", "acute", ["Po", "Or", "S", "Gn"], "59.4° ±3.8°", 55.6, 63.2)
add("Downs", "Plano oclusal / FH", "acute", ["OcP", "OcA", "Po", "Or"], "9.3° ±3.8°", 5.5, 13.1)
add("Downs", "L1 / plano oclusal", "obtuse", ["L1i", "L1a", "OcP", "OcA"], "104.5° ±3.5°", 101, 108)
# Tweed
add("Tweed", "FMA", "acute", ["Po", "Or", "Go", "Me"], "25° ±4°", 21, 29)
add("Tweed", "FMIA", "acute", ["Po", "Or", "L1i", "L1a"], "65° ±5°", 60, 70)
add("Tweed", "IMPA", "acute", ["L1i", "L1a", "Go", "Me"], "90° ±5°", 85, 95)
# Ricketts
add("Ricketts", "Eje facial Ba-N / Pt-Gn", "acute", ["Ba", "N", "Pt", "Gn"], "90° ±3.5°", 86.5, 93.5)
add("Ricketts", "Profundidad facial FH / N-Pg", "acute", ["Po", "Or", "N", "Pg"], "referencia dependiente de edad")
add("Ricketts", "Profundidad maxilar FH / N-A", "acute", ["Po", "Or", "N", "A"], "referencia dependiente de edad")
add("Ricketts", "Convexidad A a N-Pg", "signed_line", ["A", "N", "Pg", "Po", "Or"], "mm · signo anatómico", unit="mm")
add("Ricketts", "L1 a A-Pg", "signed_line", ["L1i", "A", "Pg", "Po", "Or"], "mm · signo anatómico", unit="mm")
add("Ricketts", "U1 a A-Pg", "signed_line", ["U1i", "A", "Pg", "Po", "Or"], "mm · signo anatómico", unit="mm")
# Bjork/Jarabak
add("Björk–Jarabak", "Ángulo silla N-S-Ar", "angle3", ["N", "S", "Ar"])
add("Björk–Jarabak", "Ángulo articular S-Ar-Go", "angle3", ["S", "Ar", "Go"])
add("Björk–Jarabak", "Ángulo gonial Ar-Go-Me", "angle3", ["Ar", "Go", "Me"], "130° ±7°", 123, 137)
add("Björk–Jarabak", "Altura facial posterior S-Go", "distance", ["S", "Go"], "mm", unit="mm")
add("Björk–Jarabak", "Altura facial anterior N-Me", "distance", ["N", "Me"], "mm", unit="mm")
add("Björk–Jarabak", "Ratio S-Go / N-Me", "ratio", ["S", "Go", "N", "Me"], "%", unit="%")
# McNamara
add("McNamara", "A a N⊥", "nperp", ["A", "N", "Po", "Or"], "mm · signo anterior/posterior", unit="mm")
add("McNamara", "Pg a N⊥", "nperp", ["Pg", "N", "Po", "Or"], "mm · signo anterior/posterior", unit="mm")
add("McNamara", "Co-A", "distance", ["Co", "A"], "mm · depende de edad/sexo", unit="mm")
add("McNamara", "Co-Gn", "distance", ["Co", "Gn"], "mm · depende de edad/sexo", unit="mm")
add("McNamara", "Diferencia Co-Gn − Co-A", "diffdist", ["Co", "Gn", "A"], "mm", unit="mm")
add("McNamara", "ANS-Me", "distance", ["ANS", "Me"], "mm · depende de edad/sexo", unit="mm")
add("McNamara", "Vía aérea superior", "distance", ["AirSupA", "AirSupP"], "medida 2D descriptiva", unit="mm")
add("McNamara", "Vía aérea inferior", "distance", ["AirInfA", "AirInfP"], "medida 2D descriptiva", unit="mm")
# Wits
add("Wits", "AO-BO", "wits", ["A", "B", "OcP", "OcA"], "positivo: AO anterior a BO; negativo: dirección Clase III", unit="mm")
# Holdaway
add("Holdaway", "Labio inferior a línea H", "signed_line", ["Li", "PgS", "Ls", "Po", "Or"], "mm", unit="mm")
add("Holdaway", "Espesor de mentón Pg-Pg'", "distance", ["Pg", "PgS"], "mm", unit="mm")
add("Holdaway", "Ángulo H N'-Pg' / Pg'-Ls", "acute", ["NS", "PgS", "PgS", "Ls"])
add("Holdaway", "Ángulo facial tejidos blandos FH / N'-Pg'", "acute", ["Po", "Or", "NS", "PgS"])
# Powell
add("Powell", "Nasofrontal", "angle3", ["GS", "NS", "Pr"], "115°–130°", 115, 130)
add("Powell", "Nasofacial", "acute", ["GS", "PgS", "NS", "Pr"], "30°–40°", 30, 40)
add("Powell", "Nasomental", "angle3", ["NS", "Pr", "PgS"], "120°–132°", 120, 132)
add("Powell", "Mentocervical", "acute", ["GS", "PgS", "MeS", "C"], "80°–95°", 80, 95)
# Burstone COGS core
add("Burstone COGS", "Convexidad N-A-Pg", "angle3", ["N", "A", "Pg"], "muestra histórica; interpretar por sexo/población")
add("Burstone COGS", "N-A // HP", "hp_along", ["N", "A", "S", "Po", "Or", "Me"], "mm", unit="mm")
add("Burstone COGS", "N-B // HP", "hp_along", ["N", "B", "S", "Po", "Or", "Me"], "mm", unit="mm")
add("Burstone COGS", "N-Pg // HP", "hp_along", ["N", "Pg", "S", "Po", "Or", "Me"], "mm", unit="mm")
add("Burstone COGS", "N-ANS ⟂ HP", "hp_perp", ["N", "ANS", "S", "Po", "Or", "Me"], "mm", unit="mm")
add("Burstone COGS", "ANS-Gn ⟂ HP", "hp_perp_pair", ["ANS", "Gn", "S", "N", "Po", "Or", "Me"], "mm", unit="mm")
add("Burstone COGS", "MP-HP", "hp_line_angle", ["Go", "Me", "S", "N", "Po", "Or"], "°")
add("Burstone COGS", "Ar-Go", "distance", ["Ar", "Go"], "mm", unit="mm")
add("Burstone COGS", "Go-Pg", "distance", ["Go", "Pg"], "mm", unit="mm")
add("Burstone COGS", "OP-HP", "hp_line_angle", ["OcP", "OcA", "S", "N", "Po", "Or"], "°")
add("Burstone COGS", "U1-NF", "acute", ["U1i", "U1a", "PNS", "ANS"], "°")
add("Burstone COGS", "L1-MP", "acute", ["L1i", "L1a", "Go", "Me"], "°")
# Legan-Burstone
add("Legan–Burstone", "Convexidad facial G'-Sn-Pg'", "angle3", ["GS", "Sn", "PgS"], "12° ±4°", 8, 16)
add("Legan–Burstone", "Nasolabial Cm-Sn-Ls", "angle3", ["Cm", "Sn", "Ls"], "102° ±8°", 94, 110)
add("Legan–Burstone", "Labio superior a Sn-Pg'", "signed_line", ["Ls", "Sn", "PgS", "Po", "Or"], "3 ±1 mm", 2, 4, "mm")
add("Legan–Burstone", "Labio inferior a Sn-Pg'", "signed_line", ["Li", "Sn", "PgS", "Po", "Or"], "2 ±1 mm", 1, 3, "mm")
add("Legan–Burstone", "Interlabial Stms-Stmi", "distance", ["Stms", "Stmi"], "2 ±2 mm", 0, 4, "mm")
add("Legan–Burstone", "Exposición U1 Stms-U1", "distance", ["Stms", "U1i"], "2 ±2 mm", 0, 4, "mm")
add("Legan–Burstone", "Ángulo cara-garganta Sn-Gn'-C", "angle3", ["Sn", "GnS", "C"], "100° ±7°", 93, 107)
# Airway and cranio-cervical
add("Vía aérea", "Superior mínima", "distance", ["AirSupA", "AirSupP"], "medida 2D descriptiva", unit="mm")
add("Vía aérea", "Inferior mínima", "distance", ["AirInfA", "AirInfP"], "medida 2D descriptiva", unit="mm")
add("Cráneo-cervical", "SN / OPT", "acute", ["S", "N", "CV2tg", "CV2ip"], "muestra publicada ≈100° ±6.9°", 93.1, 106.9)
add("Cráneo-cervical", "SN / CVT", "acute", ["S", "N", "CV2tg", "CV4ip"], "muestra publicada ≈103° ±5.7°", 97.3, 108.7)
add("Cráneo-cervical", "McGregor / odontoides", "acute", ["Occ", "PNS", "Od", "C2ai"], "96°–106°", 96, 106)

ANALYSES = ["Steiner", "Downs", "Tweed", "Ricketts", "Björk–Jarabak", "McNamara", "Wits", "Holdaway", "Powell", "Burstone COGS", "Legan–Burstone", "Sassouni", "Vía aérea", "Cráneo-cervical"]
SASS_POINTS = ("Sella inf.", "ACB post.", "ACB ant.", "PNS", "ANS", "Sass Oc post.", "Sass Oc ant.", "Mand base post.", "Mand base ant.", "N", "Me", "FE", "U1i", "Pg", "Sp", "Go")
POINT_HELP = {
    "S":"Sella (S)", "N":"Nasion (N)", "A":"Punto A (subespinal)", "B":"Punto B (supramental)", "Pg":"Pogonion óseo", "Gn":"Gnathion", "Go":"Gonion", "Me":"Menton", "Ar":"Articulare", "Co":"Condylion", "Po":"Porion", "Or":"Orbitale", "Ba":"Basion", "Pt":"Punto pterigoideo de Ricketts", "ANS":"Espina nasal anterior", "PNS":"Espina nasal posterior", "U1i":"Borde incisal superior", "U1a":"Ápice incisivo superior", "L1i":"Borde incisal inferior", "L1a":"Ápice incisivo inferior", "OcP":"Plano oclusal, punto posterior", "OcA":"Plano oclusal, punto anterior", "GS":"Glabella blanda G'", "NS":"Nasion blando N'", "PgS":"Pogonion blando Pg'", "MeS":"Menton blando Me'", "Pr":"Pronasale", "Ls":"Labio superior", "Li":"Labio inferior", "Sn":"Subnasale", "Cm":"Columella", "GnS":"Gnathion blando Gn'", "C":"Punto cervical", "Stms":"Stomion superior", "Stmi":"Stomion inferior", "AirSupA":"Vía aérea superior, borde anterior", "AirSupP":"Vía aérea superior, pared posterior", "AirInfA":"Vía aérea inferior, borde anterior", "AirInfP":"Vía aérea inferior, pared posterior", "CV2tg":"Tangente C2 superior", "CV2ip":"C2 posteroinferior", "CV4ip":"C4 posteroinferior", "Occ":"Base occipital para McGregor", "Od":"Ápice odontoides", "C2ai":"C2 anteroinferior"
}

def required_points(selected):
    out = []
    for m in MEAS:
        if m.analysis in selected:
            for p in m.pts:
                if p not in out:
                    out.append(p)
    if "Sassouni" in selected:
        for p in SASS_POINTS:
            if p not in out:
                out.append(p)
    return out

def calc_measure(m, points, scale):
    pp = lambda k: P(points, k)
    k, ps = m.kind, m.pts
    if k == "angle3": return angle3(pp(ps[0]), pp(ps[1]), pp(ps[2]))
    if k == "acute": return acute_lines(pp(ps[0]), pp(ps[1]), pp(ps[2]), pp(ps[3]))
    if k == "obtuse": return obtuse_lines(pp(ps[0]), pp(ps[1]), pp(ps[2]), pp(ps[3]))
    if k == "anb": return angle3(pp("S"), pp("N"), pp("A")) - angle3(pp("S"), pp("N"), pp("B"))
    if k == "distance": return dist(pp(ps[0]), pp(ps[1])) * scale
    if k == "ratio": return 100.0 * dist(pp(ps[0]), pp(ps[1])) / dist(pp(ps[2]), pp(ps[3]))
    if k == "diffdist": return (dist(pp(ps[0]), pp(ps[1])) - dist(pp(ps[0]), pp(ps[2]))) * scale
    if k == "nperp": return signed_along(pp(ps[0]), pp(ps[1]), vec(pp("Po"), pp("Or"))) * scale
    if k == "signed_line": return signed_point_line(pp(ps[0]), pp(ps[1]), pp(ps[2]), vec(pp(ps[3]), pp(ps[4]))) * scale
    if k == "wits":
        a, b, o1, o2 = pp(ps[0]), pp(ps[1]), pp(ps[2]), pp(ps[3])
        axis = unit(vec(o1, o2))
        ao, bo = project(a, o1, o2), project(b, o1, o2)
        return dot((ao[0] - bo[0], ao[1] - bo[1]), axis) * scale
    if k.startswith("hp_"):
        h, v = hp_axes(points)
        if k == "hp_along": return abs(dot(vec(pp(ps[0]), pp(ps[1])), h)) * scale
        if k in ("hp_perp", "hp_perp_pair"): return abs(dot(vec(pp(ps[0]), pp(ps[1])), v)) * scale
        if k == "hp_line_angle": return acute_lines(pp(ps[0]), pp(ps[1]), (0.0, 0.0), h)
    raise ValueError("tipo no implementado: " + k)

def classify(m, value):
    if m.lo is None or m.hi is None:
        return "Descriptivo / interpretar con la referencia indicada"
    if value < m.lo:
        return "Por debajo de la referencia adoptada"
    if value > m.hi:
        return "Por encima de la referencia adoptada"
    return "Dentro de la referencia adoptada"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} · v{APP_VERSION}")
        self.geometry("1500x900")
        self.minsize(1080, 700)
        self.image = None; self.photo = None; self.image_path = ""
        self.zoom = 1.0; self.offx = 0.0; self.offy = 0.0
        self.points = {}; self.history = []; self.selected = {"Steiner"}; self.landmarks = []; self.current_index = 0
        self.mm_per_px = None; self.calib_mode = False; self.calib_clicks = []; self.project_path = None; self.results = []
        self.drag_point = None; self.pan_start = None
        self._style(); self._build(); self.apply_selection(); self.after(200, lambda: self.open_selector(startup=True))

    def _style(self):
        s = ttk.Style(self)
        try: s.theme_use("vista")
        except Exception: pass
        s.configure("Title.TLabel", font=("Segoe UI", 16, "bold")); s.configure("Section.TLabel", font=("Segoe UI", 10, "bold"))

    def _build(self):
        top = ttk.Frame(self, padding=6); top.pack(fill="x")
        for text, cmd in [("Abrir radiografía", self.open_image), ("Análisis…", self.open_selector), ("Calibrar mm", self.start_calibration), ("Deshacer", self.undo), ("Ajustar", self.fit), ("Guardar proyecto", self.save_project), ("Abrir proyecto", self.load_project), ("Calcular", self.calculate), ("Exportar CSV", self.export_csv)]:
            ttk.Button(top, text=text, command=cmd).pack(side="left", padx=3)
        ttk.Label(top, text=f"v{APP_VERSION}").pack(side="right", padx=8)
        body = ttk.Panedwindow(self, orient="horizontal"); body.pack(fill="both", expand=True)
        left = ttk.Frame(body, padding=8); center = ttk.Frame(body); right = ttk.Frame(body, padding=8)
        body.add(left, weight=1); body.add(center, weight=4); body.add(right, weight=2)
        ttk.Label(left, text="Análisis seleccionados", style="Section.TLabel").pack(anchor="w")
        self.analysis_lbl = ttk.Label(left, text="", wraplength=240); self.analysis_lbl.pack(fill="x", pady=(2, 8))
        ttk.Label(left, text="Landmarks", style="Section.TLabel").pack(anchor="w")
        self.list = tk.Listbox(left, exportselection=False); self.list.pack(fill="both", expand=True); self.list.bind("<<ListboxSelect>>", self.pick_list)
        self.point_help = ttk.Label(left, text="", wraplength=250); self.point_help.pack(fill="x", pady=6)
        self.progress = ttk.Label(left, text=""); self.progress.pack(fill="x")
        self.canvas = tk.Canvas(center, bg="#08090d", highlightthickness=0, cursor="crosshair"); self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click); self.canvas.bind("<B1-Motion>", self.on_drag); self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.pan_begin); self.canvas.bind("<B3-Motion>", self.pan_move); self.canvas.bind("<MouseWheel>", self.on_wheel); self.canvas.bind("<Configure>", lambda e: self.redraw())
        tabs = ttk.Notebook(right); tabs.pack(fill="both", expand=True)
        rtab = ttk.Frame(tabs); qtab = ttk.Frame(tabs); tabs.add(rtab, text="Resultados"); tabs.add(qtab, text="QC")
        self.tree = ttk.Treeview(rtab, columns=("value", "ref", "interp"), show="tree headings")
        self.tree.heading("#0", text="Medición"); self.tree.heading("value", text="Valor"); self.tree.heading("ref", text="Referencia"); self.tree.heading("interp", text="Interpretación")
        self.tree.column("#0", width=220); self.tree.column("value", width=95); self.tree.column("ref", width=180); self.tree.column("interp", width=220); self.tree.pack(fill="both", expand=True)
        self.qc = tk.Text(qtab, wrap="word", state="disabled", font=("Segoe UI", 10)); self.qc.pack(fill="both", expand=True)
        bottom = ttk.Frame(self, padding=(8, 4)); bottom.pack(fill="x")
        self.status = ttk.Label(bottom, text=EDU); self.status.pack(side="left")
        self.calib_lbl = ttk.Label(bottom, text="Sin calibrar"); self.calib_lbl.pack(side="right")

    def open_selector(self, startup=False):
        w = tk.Toplevel(self); w.title("Seleccionar análisis"); w.transient(self); w.grab_set(); w.geometry("460x640")
        ttk.Label(w, text="Selecciona uno o varios análisis", style="Title.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(w, text="Sólo se pedirán los landmarks necesarios para lo seleccionado.", wraplength=420).pack(anchor="w", padx=14, pady=(0, 8))
        box = ttk.Frame(w); box.pack(fill="both", expand=True, padx=14); vars_ = {}
        for a in ANALYSES:
            v = tk.BooleanVar(value=a in self.selected); vars_[a] = v; ttk.Checkbutton(box, text=a, variable=v).pack(anchor="w", pady=3)
        row = ttk.Frame(w); row.pack(fill="x", padx=14, pady=12)
        def all_on():
            for v in vars_.values(): v.set(True)
        def accept():
            sel = {a for a, v in vars_.items() if v.get()}
            if not sel:
                messagebox.showwarning("Análisis", "Selecciona al menos uno.", parent=w); return
            self.selected = sel; self.apply_selection(); w.destroy()
        ttk.Button(row, text="Seleccionar todo", command=all_on).pack(side="left")
        ttk.Button(row, text="Aplicar", command=accept).pack(side="right")
        if not startup: ttk.Button(row, text="Cancelar", command=w.destroy).pack(side="right", padx=6)

    def apply_selection(self):
        self.landmarks = required_points(self.selected)
        self.current_index = min(self.current_index, max(0, len(self.landmarks) - 1))
        self.list.delete(0, "end")
        for p in self.landmarks: self.list.insert("end", p)
        if self.landmarks: self.list.selection_set(self.current_index)
        self.analysis_lbl.config(text=", ".join(a for a in ANALYSES if a in self.selected)); self.update_progress(); self.redraw()

    def pick_list(self, e=None):
        s = self.list.curselection()
        if s: self.current_index = s[0]; self.update_progress()

    def update_progress(self):
        if not self.landmarks: return
        cur = self.landmarks[self.current_index]; placed = sum(p in self.points for p in self.landmarks)
        self.progress.config(text=f"{placed}/{len(self.landmarks)} colocados · actual: {cur}"); self.point_help.config(text=POINT_HELP.get(cur, cur))

    def open_image(self):
        if Image is None:
            messagebox.showerror("Dependencia", "Pillow no está disponible."); return
        f = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"), ("PDF", "*.pdf"), ("Todos", "*.*")])
        if not f: return
        try:
            if f.lower().endswith(".pdf"):
                import fitz
                doc = fitz.open(f); pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                self.image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples); doc.close()
            else:
                self.image = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
            self.image_path = f; self.points.clear(); self.history.clear(); self.mm_per_px = None; self.calib_lbl.config(text="Sin calibrar"); self.fit(); self.status.config(text=f"Radiografía: {Path(f).name}")
        except Exception as e:
            messagebox.showerror("Abrir radiografía", str(e))

    def fit(self):
        if not self.image: return
        self.update_idletasks(); cw = max(1, self.canvas.winfo_width()); ch = max(1, self.canvas.winfo_height())
        self.zoom = min(cw / self.image.width, ch / self.image.height) * 0.95; self.offx = (cw - self.image.width * self.zoom) / 2; self.offy = (ch - self.image.height * self.zoom) / 2; self.redraw()

    def img_to_canvas(self, p): return (self.offx + p[0] * self.zoom, self.offy + p[1] * self.zoom)
    def canvas_to_img(self, x, y): return ((x - self.offx) / self.zoom, (y - self.offy) / self.zoom)

    def redraw(self):
        self.canvas.delete("all")
        if self.image:
            w = max(1, int(self.image.width * self.zoom)); h = max(1, int(self.image.height * self.zoom))
            im = self.image.resize((w, h), Image.Resampling.LANCZOS); self.photo = ImageTk.PhotoImage(im); self.canvas.create_image(self.offx, self.offy, anchor="nw", image=self.photo)
        for label, p in self.points.items():
            if label not in self.landmarks: continue
            x, y = self.img_to_canvas(p); r = 5
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#43d6ba", outline="white", width=1); self.canvas.create_text(x+8, y-8, text=label, anchor="sw", fill="white", font=("Segoe UI", 9, "bold"))
        if len(self.calib_clicks) == 1:
            x, y = self.img_to_canvas(self.calib_clicks[0]); self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="gold")

    def nearest(self, x, y):
        best = None; best_d = 14.0
        for k, p in self.points.items():
            if k not in self.landmarks: continue
            cx, cy = self.img_to_canvas(p); d = math.hypot(cx-x, cy-y)
            if d < best_d: best, best_d = k, d
        return best

    def on_click(self, e):
        if not self.image: return
        p = self.canvas_to_img(e.x, e.y)
        if self.calib_mode:
            self.calib_clicks.append(p)
            if len(self.calib_clicks) == 2:
                px = dist(*self.calib_clicks)
                if px > 1:
                    self.mm_per_px = self._pending_mm / px; self.calib_lbl.config(text=f"Calibrado: {self.mm_per_px:.5f} mm/px")
                self.calib_mode = False; self.calib_clicks = []; self.status.config(text="Calibración guardada. " + EDU)
            self.redraw(); return
        near = self.nearest(e.x, e.y)
        if near:
            self.drag_point = near; self.history.append((near, self.points.get(near)))
        elif self.landmarks:
            k = self.landmarks[self.current_index]; self.history.append((k, self.points.get(k))); self.points[k] = p; self.drag_point = k
            if self.current_index < len(self.landmarks) - 1:
                self.current_index += 1; self.list.selection_clear(0, "end"); self.list.selection_set(self.current_index); self.list.see(self.current_index)
        self.update_progress(); self.redraw()

    def on_drag(self, e):
        if self.drag_point and self.image:
            self.points[self.drag_point] = self.canvas_to_img(e.x, e.y); self.redraw()
    def on_release(self, e): self.drag_point = None; self.update_progress()
    def pan_begin(self, e): self.pan_start = (e.x, e.y, self.offx, self.offy)
    def pan_move(self, e):
        if not self.pan_start: return
        x, y, ox, oy = self.pan_start; self.offx = ox + e.x - x; self.offy = oy + e.y - y; self.redraw()
    def on_wheel(self, e):
        if not self.image: return
        factor = 1.12 if e.delta > 0 else 1 / 1.12; before = self.canvas_to_img(e.x, e.y)
        self.zoom = max(0.05, min(8.0, self.zoom * factor)); self.offx = e.x - before[0] * self.zoom; self.offy = e.y - before[1] * self.zoom; self.redraw()
    def undo(self):
        if not self.history: return
        k, old = self.history.pop()
        if old is None: self.points.pop(k, None)
        else: self.points[k] = old
        self.redraw(); self.update_progress()

    def start_calibration(self):
        if not self.image:
            messagebox.showinfo("Calibración", "Abra primero una radiografía."); return
        mm = simpledialog.askfloat("Calibración", "Longitud real entre los dos puntos (mm):", minvalue=0.1, maxvalue=1000, parent=self)
        if not mm: return
        self._pending_mm = mm; self.calib_mode = True; self.calib_clicks = []; self.status.config(text="Calibración: haga clic en los dos extremos de la referencia conocida.")

    def project_data(self):
        return {"app_version": APP_VERSION, "image_path": self.image_path, "selected_analyses": sorted(self.selected), "points": self.points, "mm_per_px": self.mm_per_px}

    def save_project(self):
        f = self.project_path or filedialog.asksaveasfilename(defaultextension=".yomceph.json", filetypes=[("Proyecto YomCeph", "*.yomceph.json"), ("JSON", "*.json")])
        if not f: return
        try:
            Path(f).write_text(json.dumps(self.project_data(), ensure_ascii=False, indent=2), encoding="utf-8"); self.project_path = f; self.status.config(text="Proyecto guardado: " + Path(f).name)
        except Exception as e: messagebox.showerror("Guardar", str(e))

    def load_project(self):
        f = filedialog.askopenfilename(filetypes=[("Proyecto YomCeph", "*.yomceph.json *.json")])
        if not f: return
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8")); self.selected = set(d.get("selected_analyses") or ["Steiner"]); self.apply_selection(); self.points = {k: tuple(v) for k, v in (d.get("points") or {}).items()}; self.mm_per_px = d.get("mm_per_px"); self.image_path = d.get("image_path") or ""
            if self.image_path and Path(self.image_path).exists():
                if self.image_path.lower().endswith(".pdf"):
                    import fitz
                    doc = fitz.open(self.image_path); pix = doc[0].get_pixmap(matrix=fitz.Matrix(2,2), alpha=False); self.image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples); doc.close()
                else:
                    self.image = ImageOps.exif_transpose(Image.open(self.image_path)).convert("RGB")
                self.fit()
            self.project_path = f; self.calib_lbl.config(text=(f"Calibrado: {self.mm_per_px:.5f} mm/px" if self.mm_per_px else "Sin calibrar")); self.update_progress(); self.redraw()
        except Exception as e: messagebox.showerror("Abrir proyecto", str(e))

    def quality_checks(self):
        issues = []; selected_meas = [m for m in MEAS if m.analysis in self.selected]
        if any(m.unit == "mm" for m in selected_meas) and not self.mm_per_px:
            issues.append("⚠ Hay mediciones lineales seleccionadas y la radiografía no está calibrada; esas mediciones se mostrarán como no calculables.")
        keys = [k for k in self.landmarks if k in self.points]
        for i, a in enumerate(keys):
            for b in keys[i+1:]:
                if dist(self.points[a], self.points[b]) < 3:
                    issues.append(f"⚠ {a} y {b} están casi superpuestos (<3 px). Revise el trazado.")
        seen = set()
        for m in selected_meas:
            pairs = []
            if m.kind in ("acute", "obtuse", "hp_line_angle"): pairs = [(m.pts[0], m.pts[1]), (m.pts[2], m.pts[3])]
            elif m.kind == "angle3": pairs = [(m.pts[0], m.pts[1]), (m.pts[1], m.pts[2])]
            for a, b in pairs:
                if a in self.points and b in self.points and dist(self.points[a], self.points[b]) < 4 and (a, b) not in seen:
                    issues.append(f"⚠ Segmento {a}-{b} demasiado corto para una geometría estable."); seen.add((a,b))
        missing = [p for p in self.landmarks if p not in self.points]
        if missing: issues.append(f"ℹ Trazado parcial: faltan {len(missing)} landmarks. Sólo se calcularán mediciones completas.")
        if not issues: issues = ["✓ Sin alertas geométricas básicas. Esto no equivale a validación clínica del trazado."]
        return issues

    def sassouni_result(self, scale):
        if "Sassouni" not in self.selected: return None
        need = SASS_POINTS[:9]
        if not all(k in self.points for k in need): return ("Sassouni", "Arquitectura 4 planos", "—", "Descriptivo", "Faltan planos arquitectónicos")
        try:
            basal = (P(self.points, "Sella inf."), P(self.points, "ACB ant.")); pal = (P(self.points, "PNS"), P(self.points, "ANS")); oc = (P(self.points, "Sass Oc post."), P(self.points, "Sass Oc ant.")); mand = (P(self.points, "Mand base post."), P(self.points, "Mand base ant."))
            _, rms = least_squares_line_center([basal, pal, oc, mand]); bp = acute_lines(*basal, *pal); pm = acute_lines(*pal, *mand); unit_ = "mm" if self.mm_per_px else "px"
            return ("Sassouni", "Arquitectura 4 planos", f"RMS {rms * scale:.2f} {unit_}; Δangular {abs(bp-pm):.1f}°", "Sassouni 1955", "Convergencia geométrica; sin inventar umbral universal")
        except Exception as e: return ("Sassouni", "Arquitectura 4 planos", "—", "Descriptivo", str(e))

    def calculate(self):
        self.results = []; scale = self.mm_per_px or 1.0
        for m in MEAS:
            if m.analysis not in self.selected or not all(k in self.points for k in m.pts): continue
            if m.unit == "mm" and not self.mm_per_px:
                self.results.append((m.analysis, m.name, "—", m.norm_text, "Requiere calibración")); continue
            try:
                v = calc_measure(m, self.points, scale); self.results.append((m.analysis, m.name, f"{v:.2f} {m.unit}", m.norm_text, classify(m, v)))
            except Exception as e: self.results.append((m.analysis, m.name, "—", m.norm_text, "No calculable: " + str(e)))
        sr = self.sassouni_result(scale)
        if sr: self.results.append(sr)
        self.tree.delete(*self.tree.get_children()); groups = {}
        for a, n, v, ref, interp in self.results:
            if a not in groups: groups[a] = self.tree.insert("", "end", text=a, open=True, values=("", "", ""))
            self.tree.insert(groups[a], "end", text=n, values=(v, ref, interp))
        issues = self.quality_checks(); self.qc.config(state="normal"); self.qc.delete("1.0", "end"); self.qc.insert("end", "Control de calidad técnico\n\n" + "\n\n".join(issues) + "\n\n" + EDU); self.qc.config(state="disabled")
        self.status.config(text=f"{len(self.results)} resultados calculados/parciales · {len(issues)} mensajes QC")

    def export_csv(self):
        if not self.results: self.calculate()
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not f: return
        try:
            with open(f, "w", newline="", encoding="utf-8-sig") as fh:
                w = csv.writer(fh); w.writerow(["YomCeph Desktop", APP_VERSION]); w.writerow(["Uso", EDU]); w.writerow([]); w.writerow(["tipo", "analisis", "medicion", "valor", "referencia", "interpretacion", "x_px", "y_px"])
                for a, n, v, ref, interp in self.results: w.writerow(["resultado", a, n, v, ref, interp, "", ""])
                for k in self.landmarks:
                    if k in self.points: w.writerow(["landmark", "", k, "", "", "", f"{self.points[k][0]:.3f}", f"{self.points[k][1]:.3f}"])
                w.writerow(["calibracion", "", "mm_per_px", self.mm_per_px or "", "", "", "", ""])
            self.status.config(text="CSV de investigación exportado: " + Path(f).name)
        except Exception as e: messagebox.showerror("Exportar CSV", str(e))

if __name__ == "__main__":
    App().mainloop()
