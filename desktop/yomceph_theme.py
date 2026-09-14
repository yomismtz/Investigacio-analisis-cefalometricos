"""YomCeph Desktop visual design tokens.

Canonical palette for the Classic desktop line. The UI should stay inside the
purple / lilac / lavender / plum / violet family with mint and turquoise
accents. Status colors intentionally avoid dominant red.
"""

PALETTE = {
    # Core purples
    "violet_950": "#2B123F",
    "plum_900": "#3D1B4F",
    "purple_800": "#55246F",
    "violet_700": "#6D35A4",
    "violet_600": "#7C48C5",
    "lilac_500": "#9B6BD3",
    "lavender_400": "#B99AE5",
    "lavender_300": "#CDB7EE",
    "lavender_200": "#DDD0F4",
    "lavender_100": "#EEE7F8",
    "lavender_050": "#F8F4FC",

    # Mint / turquoise accents
    "turquoise_700": "#127C78",
    "turquoise_600": "#17958D",
    "turquoise_500": "#20AFA4",
    "mint_500": "#45C7A5",
    "mint_400": "#66D7B9",
    "mint_300": "#8BE4CB",
    "mint_200": "#B6EFDF",
    "mint_100": "#DCF8EF",

    # Neutral values compatible with the palette
    "ink": "#21182A",
    "ink_soft": "#54485E",
    "surface": "#FFFDFE",
    "surface_alt": "#F8F4FC",
    "border": "#D9CCE6",
    "canvas_dark": "#100D16",
    "white": "#FFFFFF",
}

SEMANTIC = {
    "app_background": PALETTE["lavender_050"],
    "panel": PALETTE["surface"],
    "panel_alt": PALETTE["lavender_100"],
    "primary": PALETTE["violet_700"],
    "primary_hover": PALETTE["purple_800"],
    "primary_soft": PALETTE["lavender_200"],
    "secondary": PALETTE["turquoise_600"],
    "secondary_hover": PALETTE["turquoise_700"],
    "accent": PALETTE["mint_500"],
    "accent_soft": PALETTE["mint_100"],
    "text": PALETTE["ink"],
    "text_muted": PALETTE["ink_soft"],
    "border": PALETTE["border"],
    "radiograph_canvas": PALETTE["canvas_dark"],
}

# Research database status language.
# Complete is deliberately mint/turquoise; review/excluded stay in the purple
# family so the product never becomes a red-alert dashboard.
RESEARCH_STATUS = {
    "pending": {
        "label_es": "Pendiente",
        "label_en": "Pending",
        "dot": PALETTE["lavender_400"],
        "background": PALETTE["lavender_100"],
        "foreground": PALETTE["purple_800"],
    },
    "in_progress": {
        "label_es": "En análisis",
        "label_en": "In progress",
        "dot": PALETTE["lilac_500"],
        "background": PALETTE["lavender_200"],
        "foreground": PALETTE["violet_950"],
    },
    "complete": {
        "label_es": "Completo",
        "label_en": "Complete",
        "dot": PALETTE["mint_500"],
        "background": PALETTE["mint_100"],
        "foreground": PALETTE["turquoise_700"],
    },
    "incomplete": {
        "label_es": "Incompleto",
        "label_en": "Incomplete",
        "dot": PALETTE["violet_600"],
        "background": PALETTE["lavender_100"],
        "foreground": PALETTE["purple_800"],
    },
    "excluded": {
        "label_es": "Excluido",
        "label_en": "Excluded",
        "dot": PALETTE["plum_900"],
        "background": "#F1E6F2",
        "foreground": PALETTE["plum_900"],
    },
}

# Landmark / tracing visualization. These remain high-contrast over a dark
# radiograph without leaving the requested family.
TRACING = {
    "landmark": PALETTE["mint_400"],
    "landmark_active": PALETTE["mint_300"],
    "line_primary": PALETTE["lilac_500"],
    "line_secondary": PALETTE["turquoise_500"],
    "construction": PALETTE["lavender_300"],
    "label": PALETTE["white"],
    "selection_ring": PALETTE["violet_600"],
}

ALLOWED_FAMILY_NAMES = (
    "morado", "menta", "turquesa", "lila", "lavanda", "púrpura", "ciruela", "violeta"
)
