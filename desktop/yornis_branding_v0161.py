from __future__ import annotations

import io
import tokenize


def rebrand_python_string_literals(source: str) -> str:
    """Replace legacy product branding in Python string literals only.

    Identifiers such as YomCephClassic and import paths remain intact for
    compatibility; visible titles, dialogs, help text and resource filenames
    become Yornis.
    """
    rewritten = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.STRING:
            value = token.string.replace("YomCeph", "Yornis")
            value = value.replace("yomceph_logo.png", "yornis_logo.png")
            token = token._replace(string=value)
        rewritten.append(token)
    return tokenize.untokenize(rewritten)
