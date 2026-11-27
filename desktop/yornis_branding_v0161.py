from __future__ import annotations

"""YOM Dental product identity and guided calibration text."""

import io
import re
import tokenize
from tkinter import simpledialog

_BRAND_RE = re.compile(r"(?i)\\b(?:yomceph|yornis)\\b")
_CALIBRATION_TITLE_RE = re.compile(r"(?i)(calibr|mm\\s*/\\s*px|scale|escala|distancia real|real distance)")


def _brand_case(match: re.Match[str]) -> str:
    return "YOM Dental" if match.group(0).isupper() else "YOM Dental"


def rebrand_classic_source(source: str) -> str:
    """Replace legacy product names only inside user-facing Python string literals."""
    rewritten = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        string_token_types = {tokenize.STRING}
        fstring_middle = getattr(tokenize, "FSTRING_MIDDLE", None)
        if fstring_middle is not None:
            string_token_types.add(fstring_middle)
        if token.type in string_token_types:
            value = _BRAND_RE.sub(_brand_case, token.string)
            value = re.sub(r"(?i)\\bcalibrar\\s+mm\\b", "Calibrar radiografía", value)
            value = re.sub(r"(?i)\\bcalibrate\\s+mm\\b", "Calibrate radiograph", value)
            value = re.sub(r"(?i)yornis_logo\\.png", "yom_dental_logo.png", value)
            token = token._replace(string=value)
        rewritten.append(token)
    return tokenize.untokenize(rewritten)


CALIBRATION_TITLE = "Calibrar radiografía · YOM Dental"
CALIBRATION_POINT_LABELS = ("Punto calibración 1", "Punto calibración 2")

CALIBRATION_PROMPT_ES = (
    "CALIBRACIÓN EN DOS PASOS · PUNTOS DE CALIBRACIÓN\\n\\n"
    "1. Escribe la distancia REAL en milímetros entre dos referencias visibles "
    "de la radiografía (por ejemplo, 25 mm).\\n"
    "2. Pulsa Aceptar. Después marca en la radiografía, en este orden:\\n"
    "   • Punto calibración 1: primer extremo de la distancia conocida.\\n"
    "   • Punto calibración 2: segundo extremo de ESA MISMA distancia.\\n\\n"
    "Los dos puntos deben ser distintos y pertenecer a la radiografía actual. "
    "YOM Dental calculará la escala en mm/píxel. No son landmarks cefalométricos "
    "ni se incluyen en los análisis anatómicos."
)


def calibration_dialog_copy(title: str, prompt: str) -> tuple[str, str]:
    context = f"{title or ''} {prompt or ''}"
    if not _CALIBRATION_TITLE_RE.search(context):
        return title, prompt
    return CALIBRATION_TITLE, CALIBRATION_PROMPT_ES


def install_calibration_prompt() -> None:
    if getattr(simpledialog.askfloat, "_yom_dental_calibration_prompt", False):
        return
    original = simpledialog.askfloat

    def askfloat(title, prompt, *args, **kwargs):
        title, prompt = calibration_dialog_copy(str(title or ""), str(prompt or ""))
        return original(title, prompt, *args, **kwargs)

    askfloat._yom_dental_calibration_prompt = True
    simpledialog.askfloat = askfloat
