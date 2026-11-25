from __future__ import annotations

"""Yornis product identity and guided calibration text for v0.16.1."""

import io
import re
import tokenize
from tkinter import simpledialog

_BRAND_RE = re.compile(r"(?i)\byomceph\b")
_CALIBRATION_TITLE_RE = re.compile(r"(?i)(calibr|mm\s*/\s*px|scale|escala|distancia real|real distance)")


def _brand_case(match: re.Match[str]) -> str:
    return "YORNIS" if match.group(0).isupper() else "Yornis"


def rebrand_classic_source(source: str) -> str:
    """Rename only user-facing text literals in the compressed legacy UI source.

    Python identifiers such as YomCephClassic are deliberately untouched.
    """
    rewritten = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        string_token_types = {tokenize.STRING}
        fstring_middle = getattr(tokenize, "FSTRING_MIDDLE", None)
        if fstring_middle is not None:
            string_token_types.add(fstring_middle)
        if token.type in string_token_types:
            value = _BRAND_RE.sub(_brand_case, token.string)
            value = re.sub(r"(?i)\bcalibrar\s+mm\b", "Calibrar radiografía", value)
            value = re.sub(r"(?i)\bcalibrate\s+mm\b", "Calibrate radiograph", value)
            value = re.sub(r"(?i)\byomceph_logo\.png\b", "yornis_logo.png", value)
            token = token._replace(string=value)
        rewritten.append(token)
    return tokenize.untokenize(rewritten)


CALIBRATION_TITLE = "Calibrar radiografía · Yornis"
CALIBRATION_PROMPT_ES = (
    "CALIBRACIÓN EN DOS PASOS\n\n"
    "1. Escribe cuántos MILÍMETROS REALES hay entre dos referencias de la radiografía. "
    "Por ejemplo, si la distancia conocida es 25 mm, escribe 25.\n"
    "2. Pulsa OK para cerrar esta ventana.\n"
    "3. En la radiografía, haz clic en el primer extremo y después en el segundo "
    "extremo de ESA MISMA distancia.\n\n"
    "Yornis calculará la escala en mm/píxel a partir de los dos puntos que marques."
)


def calibration_dialog_copy(title: str, prompt: str) -> tuple[str, str]:
    """Make calibration dialogs explain the two endpoints and their real distance."""
    context = f"{title or ''} {prompt or ''}"
    if not _CALIBRATION_TITLE_RE.search(context):
        return title, prompt
    return CALIBRATION_TITLE, CALIBRATION_PROMPT_ES


def install_calibration_prompt() -> None:
    """Ensure legacy Individual mode uses the same explicit calibration wording."""
    if getattr(simpledialog.askfloat, "_yornis_calibration_prompt_v0161", False):
        return
    original = simpledialog.askfloat

    def askfloat(title, prompt, *args, **kwargs):
        title, prompt = calibration_dialog_copy(str(title or ""), str(prompt or ""))
        return original(title, prompt, *args, **kwargs)

    askfloat._yornis_calibration_prompt_v0161 = True
    simpledialog.askfloat = askfloat
