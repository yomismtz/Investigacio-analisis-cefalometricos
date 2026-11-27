from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yomceph_theme as base

SETTINGS_PATH = Path(os.getenv('APPDATA', str(Path.home()))) / 'YomCeph' / 'yornis_settings.json'
DEFAULT_THEME = 'Agaporni'

# Eight characteristic plumage colors for each bird. These are kept separately
# from semantic UI colors so every palette retains its exact species identity.
BIRD_COLOR_SWATCHES = {
    "Agaporni": ("#328B50", "#347DB8", "#F5D94B", "#F8F5E9", "#F29B70", "#36BDB7", "#B59BCF", "#713D70"),
    "Tucán": ("#171717", "#F4D52F", "#F28A24", "#F7F4EA", "#D94B2B", "#D9A43B", "#929292", "#365B43"),
    "Pavorreal": ("#175A9B", "#087B55", "#16A9A5", "#124B59", "#D6AD37", "#A66B36", "#684A91", "#164536"),
    "Ninfa": ("#C5C5C2", "#65676B", "#F4D64E", "#FAF9F4", "#E98143", "#E9DCC2", "#D99BA4", "#9B918A"),
    "Faisán": ("#B66A3C", "#8C2937", "#D5A63D", "#F1E2C8", "#69713B", "#315B79", "#67402D", "#292326"),
    "Quetzal": ("#087D50", "#36A96A", "#16B5A8", "#F7F4E8", "#C63B43", "#E7C94D", "#277DB0", "#064B3B"),
    "Guacamaya Roja": ("#D52E35", "#8F2029", "#F4D22E", "#F8F5EC", "#EE8425", "#1766B2", "#32834D", "#242020"),
    "Guacamaya Azul": ("#1555A0", "#55A6D9", "#F2C544", "#F8F7F0", "#4C9B50", "#28AFAF", "#718A9C", "#202329"),
    "Búho": ("#805137", "#452B25", "#C68A32", "#F0E2C9", "#C6A77F", "#D4BD99", "#89847E", "#F7F3E9"),
    "Colibrí": ("#15966D", "#20B9B1", "#2777CF", "#F8F8F0", "#7950A8", "#C34B91", "#08734F", "#164537"),
    "Flamenco": ("#F28CB5", "#E94F8B", "#F6B7C9", "#F7D9DF", "#E86A55", "#F3A47D", "#35313B", "#FFF7F3"),
    "Colorín siete colores": ("#2455C5", "#21A9D6", "#28A65A", "#E53945", "#F5D52D", "#F28B35", "#713F91", "#F5F1E6"),
    "Tángara del paraíso": ("#164FA8", "#087F65", "#24B7B0", "#F0D52C", "#E84A42", "#F28B32", "#252B38", "#F5F3E9"),
}

# Apply the eight bird colors to the existing semantic theme slots while
# retaining neutral surfaces and readable text contrast.
def _apply_bird_color_sets() -> None:
    for bird, colors in BIRD_COLOR_SWATCHES.items():
        theme = THEMES[bird]
        # Bird swatches are accents, not semantic text/surface tokens. In
        # particular, colors[7] is often cream and must never become a text
        # color on a light panel. Keep each palette's dark neutrals and pale
        # surfaces from THEMES; only map saturated plumage colors to accents.
        theme.update({
            "primary": colors[0],
            "secondary": colors[1],
            "accent": colors[2],
            "tertiary": colors[4],
            "warning": colors[5],
        })

THEMES = {
    'Agaporni': {
        'description_es': 'Púrpura, ciruela y violeta con turquesa, menta, lavanda y lila.',
        'bg': '#F8F3FC', 'panel': '#FFFDFE', 'panel_alt': '#EEE5F7', 'text': '#24162E', 'muted': '#66556E',
        'primary': '#5A246F', 'primary_dark': '#32103F', 'primary_soft': '#D9C3EE',
        'secondary': '#17A8A2', 'secondary_dark': '#0E7775', 'accent': '#65D8BC', 'accent_soft': '#DDF8F0',
        'tertiary': '#A376D2', 'warning': '#B38B50', 'danger': '#7B315C', 'canvas': '#100C15', 'border': '#D9C9E6',
    },
    'Tucán': {
        'description_es': 'Turquesa tropical, naranja, amarillo y carbón.',
        'bg': '#FFF8E8', 'panel': '#FFFDF7', 'panel_alt': '#FFF0CE', 'text': '#291E18', 'muted': '#69584D',
        'primary': '#D96816', 'primary_dark': '#7C3511', 'primary_soft': '#FFD0A3',
        'secondary': '#15AFA5', 'secondary_dark': '#08756E', 'accent': '#F4C542', 'accent_soft': '#FFF4BD',
        'tertiary': '#5C4238', 'warning': '#E99118', 'danger': '#9A431B', 'canvas': '#121211', 'border': '#E4C99B',
    },
    'Pavorreal': {
        'description_es': 'Azul pavo real, verde petróleo, violeta y oro.',
        'bg': '#F1F7FA', 'panel': '#FCFEFF', 'panel_alt': '#DCEEF1', 'text': '#102B35', 'muted': '#4E6570',
        'primary': '#15517A', 'primary_dark': '#082F4B', 'primary_soft': '#BDD6E5',
        'secondary': '#138F85', 'secondary_dark': '#08615D', 'accent': '#D6A82B', 'accent_soft': '#FAEDB6',
        'tertiary': '#573C83', 'warning': '#C98F27', 'danger': '#6C315E', 'canvas': '#08151D', 'border': '#BFD4DD',
    },
    'Ninfa': {
        'description_es': 'Gris perla, crema, amarillo suave, rosa y ciruela.',
        'bg': '#FAF8F5', 'panel': '#FFFFFF', 'panel_alt': '#F1EEE9', 'text': '#353238', 'muted': '#716A70',
        'primary': '#7A587F', 'primary_dark': '#4A344E', 'primary_soft': '#E0D2E4',
        'secondary': '#D8A82E', 'secondary_dark': '#6D5314', 'accent': '#E6A0AD', 'accent_soft': '#FBE9ED',
        'tertiary': '#9FA5A8', 'warning': '#D8A82E', 'danger': '#9A5B69', 'canvas': '#151517', 'border': '#D8D2D2',
    },
    'Faisán': {
        'description_es': 'Ciruela, borgoña, cobre, oliva y dorado.',
        'bg': '#FBF6F2', 'panel': '#FFFDFC', 'panel_alt': '#EFE3DB', 'text': '#35221F', 'muted': '#745F56',
        'primary': '#7B294B', 'primary_dark': '#48152B', 'primary_soft': '#E7BFD0',
        'secondary': '#9B5A32', 'secondary_dark': '#68371F', 'accent': '#B49B42', 'accent_soft': '#F2E9BF',
        'tertiary': '#6E7040', 'warning': '#C28B32', 'danger': '#7B294B', 'canvas': '#17110F', 'border': '#D8C1B5',
    },
    'Quetzal': {
        'description_es': 'Verde esmeralda, turquesa profundo, rojo rubí y crema.',
        'bg': '#F2FAF7', 'panel': '#FCFFFD', 'panel_alt': '#DDF3E9', 'text': '#12352D', 'muted': '#4C6B62',
        'primary': '#087D64', 'primary_dark': '#06483D', 'primary_soft': '#B9E6D8',
        'secondary': '#0BA39B', 'secondary_dark': '#08706B', 'accent': '#59CBA5', 'accent_soft': '#DDF8ED',
        'tertiary': '#BB3545', 'warning': '#B9963B', 'danger': '#A52939', 'canvas': '#071714', 'border': '#BFDCD2',
    },
    'Guacamaya Roja': {
        'description_es': 'Rojo escarlata, amarillo, azul intenso y vino.',
        'bg': '#FFF6F4', 'panel': '#FFFEFD', 'panel_alt': '#FBE5E0', 'text': '#371D22', 'muted': '#73535A',
        'primary': '#B52632', 'primary_dark': '#70141D', 'primary_soft': '#F2BBC0',
        'secondary': '#185CB7', 'secondary_dark': '#103D7B', 'accent': '#F0B82E', 'accent_soft': '#FFF0B8',
        'tertiary': '#8D2851', 'warning': '#E29B22', 'danger': '#8C1F2A', 'canvas': '#170C0F', 'border': '#E6C4C5',
    },
    'Guacamaya Azul': {
        'description_es': 'Azul cobalto, cyan, amarillo dorado y azul noche.',
        'bg': '#F1F7FD', 'panel': '#FCFEFF', 'panel_alt': '#DCEAF8', 'text': '#132A43', 'muted': '#536B82',
        'primary': '#176BB4', 'primary_dark': '#0A3C70', 'primary_soft': '#B9D8F2',
        'secondary': '#1AA6C7', 'secondary_dark': '#0C6D86', 'accent': '#F2C54D', 'accent_soft': '#FFF1BE',
        'tertiary': '#31468D', 'warning': '#DCA72F', 'danger': '#6C365F', 'canvas': '#07121E', 'border': '#B8D0E5',
    },
    'Búho': {
        'description_es': 'Ciruela nocturna, púrpura profundo, ámbar y crema.',
        'bg': '#F8F4FA', 'panel': '#FFFCFF', 'panel_alt': '#EEE5F1', 'text': '#2C2130', 'muted': '#6B5C70',
        'primary': '#493052', 'primary_dark': '#2E1C35', 'primary_soft': '#DDD0E3',
        'secondary': '#76518A', 'secondary_dark': '#553865', 'accent': '#C49A45', 'accent_soft': '#F3E8D2',
        'tertiary': '#987C54', 'warning': '#B28C43', 'danger': '#8C425B', 'canvas': '#130F17', 'border': '#D8CADC',
    },
    'Colibrí': {
        'description_es': 'Verde esmeralda, turquesa, lima y menta.',
        'bg': '#F1FAF7', 'panel': '#FCFFFD', 'panel_alt': '#DDF5E9', 'text': '#14342B', 'muted': '#526D64',
        'primary': '#087D64', 'primary_dark': '#054D40', 'primary_soft': '#BCE8D7',
        'secondary': '#16AFA5', 'secondary_dark': '#0C7E78', 'accent': '#A5D94D', 'accent_soft': '#F8F8F0',
        'tertiary': '#31A8A0', 'warning': '#B28E2D', 'danger': '#A13A56', 'canvas': '#061A17', 'border': '#B9DDD0',
    },
    'Flamenco': {
        'description_es': 'Rosa flamenco, coral, salmón, carbón y marfil.',
        'bg': '#FFF5F8', 'panel': '#FFFCFD', 'panel_alt': '#FCE4EC', 'text': '#3A202C', 'muted': '#765563',
        'primary': '#E94F8B', 'primary_dark': '#35313B', 'primary_soft': '#F7D9DF',
        'secondary': '#F28CB5', 'secondary_dark': '#C63C70', 'accent': '#E86A55', 'accent_soft': '#F6B7C9',
        'tertiary': '#F3A47D', 'warning': '#F3A47D', 'danger': '#35313B', 'canvas': '#1A1015', 'border': '#E8C6D3',
    },
    'Colorín siete colores': {
        'description_es': 'Azul, turquesa, verde, rojo, amarillo, naranja, violeta y crema.',
        'bg': '#F3F8FF', 'panel': '#FCFDFF', 'panel_alt': '#DFEDFB', 'text': '#172A48', 'muted': '#536783',
        'primary': '#2455C5', 'primary_dark': '#713F91', 'primary_soft': '#F5F1E6',
        'secondary': '#21A9D6', 'secondary_dark': '#176F98', 'accent': '#28A65A', 'accent_soft': '#F5F1E6',
        'tertiary': '#E53945', 'warning': '#F28B35', 'danger': '#713F91', 'canvas': '#0C1628', 'border': '#C4D6EA',
    },
    'Tángara del paraíso': {
        'description_es': 'Azul, esmeralda, turquesa, amarillo, rojo, naranja, carbón y marfil.',
        'bg': '#F2F8F7', 'panel': '#FCFEFD', 'panel_alt': '#DDEEEB', 'text': '#1D3036', 'muted': '#52686D',
        'primary': '#164FA8', 'primary_dark': '#252B38', 'primary_soft': '#F5F3E9',
        'secondary': '#087F65', 'secondary_dark': '#075846', 'accent': '#24B7B0', 'accent_soft': '#F5F3E9',
        'tertiary': '#E84A42', 'warning': '#F28B32', 'danger': '#252B38', 'canvas': '#0C171B', 'border': '#C2DCD6',
    },
}

# Apply species swatches only after the semantic theme dictionaries exist.
_apply_bird_color_sets()

BRAND_LOGO_FILES = {
    "Agaporni": "Logo YOM Dental Agaporni Multicolor.png",
    "Tucán": "Logotipo Yom Dental Tucán en degradado tropical.png",
    "Pavorreal": "Logo dental Yom en tonos pavorreal.png",
    "Ninfa": "Logo dental Yom en paleta Ninfa.png",
    "Faisán": "Logo dental YOM con degradados Faisán.png",
    "Quetzal": "Logotipo Yom Dental quetzal.png",
    "Guacamaya Roja": "Logotipo YOM Dental Guacamaya Roja Multicolor.png",
    "Guacamaya Azul": "Logotipo Yom Dental Guacamaya Azul.png",
    "Búho": "Logo YOM Dental en tonos búho.png",
    "Colibrí": "Logo dental Yom en paleta Colibrí (2).png",
    "Flamenco": "Logotipo Dental Rosa Flamingo en 3D.png",
    "Colorín siete colores": "Logo dental Colorn de 7 colorese.png",
    "Tángara del paraíso": "Logotipo Yom DentalTángara del paraíso.png",
}


def brand_logo_path(theme_name: str | None = None) -> Path | None:
    """Return the YOM Dental logo matching a bird palette in source or frozen mode."""
    name = theme_name or current_theme_name()
    filename = BRAND_LOGO_FILES.get(name)
    if not filename:
        return None
    if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"):
        root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        return root / "assets" / "brand-logos" / filename
    return Path(__file__).resolve().parents[1] / "assets" / "bird-palettes" / "brand-logos" / filename


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_settings(data: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def current_theme_name() -> str:
    name = load_settings().get('theme', DEFAULT_THEME)
    return name if name in THEMES else DEFAULT_THEME


def landmark_radius() -> int:
    try:
        return max(1, min(6, int(load_settings().get('landmark_radius', 2))))
    except Exception:
        return 2


def set_landmark_radius(radius: int) -> None:
    s = load_settings(); s['landmark_radius'] = max(1, min(6, int(radius))); save_settings(s)



def contrast_ratio(foreground: str, background: str) -> float:
    """Return WCAG relative-luminance contrast ratio for two RGB hex colors."""
    def luminance(color: str) -> float:
        values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    first, second = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def readable_foreground(background: str) -> str:
    """Choose whichever of near-black or white gives stronger text contrast."""
    dark, light = "#000000", "#FFFFFF"
    return dark if contrast_ratio(dark, background) >= contrast_ratio(light, background) else light


def apply_theme(name: str, persist: bool = True) -> dict:
    if name not in THEMES:
        name = DEFAULT_THEME
    t = THEMES[name]
    # Mutate existing dictionaries in-place: modules that imported them keep the same references.
    p = base.PALETTE
    p.update({
        **{f'bird_color_{index + 1}': color for index, color in enumerate(BIRD_COLOR_SWATCHES[name])},
        'violet_950': t['primary_dark'], 'plum_900': t['primary_dark'], 'purple_800': t['primary'],
        'violet_700': t['primary'], 'violet_600': t['tertiary'], 'lilac_500': t['tertiary'],
        'lavender_400': t['primary_soft'], 'lavender_300': t['primary_soft'], 'lavender_200': t['panel_alt'],
        'lavender_100': t['panel_alt'], 'lavender_050': t['bg'], 'turquoise_700': t['secondary_dark'],
        'turquoise_600': t['secondary'], 'turquoise_500': t['secondary'], 'mint_500': t['accent'],
        'mint_400': t['accent'], 'mint_300': t['accent'], 'mint_200': t['accent_soft'], 'mint_100': t['accent_soft'],
        'ink': t['text'], 'ink_soft': t['muted'], 'surface': t['panel'], 'surface_alt': t['bg'],
        'border': t['border'], 'canvas_dark': t['canvas'], 'white': '#FFFFFF',
    })
    base.SEMANTIC.update({
        'app_background': t['bg'], 'panel': t['panel'], 'panel_alt': t['panel_alt'], 'primary': t['primary'],
        'primary_hover': t['primary_dark'], 'primary_soft': t['primary_soft'], 'secondary': t['secondary'],
        'secondary_hover': t['secondary_dark'], 'accent': t['accent'], 'accent_soft': t['accent_soft'],
        'text': t['text'], 'text_muted': t['muted'], 'border': t['border'], 'radiograph_canvas': t['canvas'],
    })
    base.RESEARCH_STATUS.clear()
    base.RESEARCH_STATUS.update({
        'complete': {'label_es':'Completado','label_en':'Complete','dot':t['secondary'],'background':t['accent_soft'],'foreground':t['secondary_dark']},
        'in_progress': {'label_es':'En análisis','label_en':'In progress','dot':t['tertiary'],'background':t['primary_soft'],'foreground':t['primary_dark']},
        'pending': {'label_es':'Pendiente','label_en':'Pending','dot':t['warning'],'background':t['panel_alt'],'foreground':t['text']},
        'incomplete': {'label_es':'Incompleto','label_en':'Incomplete','dot':t['primary'],'background':t['primary_soft'],'foreground':t['primary_dark']},
        'excluded': {'label_es':'Excluido','label_en':'Excluded','dot':t['danger'],'background':t['panel_alt'],'foreground':t['danger']},
    })
    base.TRACING.update({
        'landmark': t['accent'], 'landmark_active': t['secondary'], 'line_primary': t['tertiary'],
        'line_secondary': t['secondary'], 'construction': t['primary_soft'], 'label': '#FFFFFF',
        'selection_ring': t['primary'],
    })
    if persist:
        s = load_settings(); s['theme'] = name; save_settings(s)
    return t


def theme_names() -> list[str]:
    return list(THEMES)

apply_theme(current_theme_name(), persist=False)
