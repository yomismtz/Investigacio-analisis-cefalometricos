from __future__ import annotations

import json
import os
from pathlib import Path

import yomceph_theme as base

SETTINGS_PATH = Path(os.getenv('APPDATA', str(Path.home()))) / 'YomCeph' / 'yornis_settings.json'
DEFAULT_THEME = 'Agaporni'

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
        'secondary': '#D8A82E', 'secondary_dark': '#95731D', 'accent': '#E6A0AD', 'accent_soft': '#FBE9ED',
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
}


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


def apply_theme(name: str, persist: bool = True) -> dict:
    if name not in THEMES:
        name = DEFAULT_THEME
    t = THEMES[name]
    # Mutate existing dictionaries in-place: modules that imported them keep the same references.
    p = base.PALETTE
    p.update({
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
