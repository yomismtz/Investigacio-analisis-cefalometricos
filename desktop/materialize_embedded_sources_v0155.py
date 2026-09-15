from __future__ import annotations

"""Materialize legacy compressed Python wrappers before tests and packaging.

Historical Yornis development branches used base64+zlib payload wrappers to move
large source files through constrained editing channels. They are deterministic,
but runtime exec() is undesirable in a public scientific application.

This build-time tool replaces the known wrappers with ordinary UTF-8 Python
source in the GitHub Actions workspace. The distributed executable therefore
contains compiled ordinary modules rather than self-decoding exec() loaders.
"""

import ast
import base64
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = (
    "classic_engine.py",
    "yomceph_desktop_v130_classic.py",
    "yornis_ceph_quality_v0153.py",
    "yornis_audit_hardening_v0154.py",
)


def _part_value(module_name: str) -> str:
    path = ROOT / f"{module_name}.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PART":
                    value = ast.literal_eval(node.value)
                    if not isinstance(value, str):
                        raise TypeError(f"PART is not text in {path}")
                    return value
    raise RuntimeError(f"PART not found in {path}")


def _decode_parts(source: str) -> str:
    modules = re.findall(r"^from\s+([A-Za-z0-9_]+)\s+import\s+PART\s+as\s+P\d+", source, flags=re.M)
    if not modules:
        raise RuntimeError("No PART modules found")
    payload = "".join(_part_value(name) for name in modules)
    return zlib.decompress(base64.b64decode(payload, validate=True)).decode("utf-8")


def _decode_literal(source: str) -> str:
    match = re.search(r"base64\.b64decode\((['\"])([A-Za-z0-9+/=]+)\1", source)
    if not match:
        raise RuntimeError("Embedded literal payload not found")
    payload = match.group(2)
    return zlib.decompress(base64.b64decode(payload, validate=True)).decode("utf-8")


def _tail_after_exec(source: str) -> str:
    lines = source.splitlines()
    for index, line in enumerate(lines):
        if line.lstrip().startswith("exec(compile("):
            return "\n".join(lines[index + 1 :]).strip()
    return ""


def materialize(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    if "exec(compile(" not in source:
        return False

    if "_classic_ui_part" in source:
        decoded = _decode_parts(source)
        marker = "if __name__=='__main__':"
        patch = "\nimport research_workflow as _research_workflow\n_research_workflow.install(globals())\n\n"
        if marker not in decoded:
            raise RuntimeError("Classic UI entry point marker not found")
        rendered = decoded.replace(marker, patch + marker, 1)
    elif "import PART as P" in source:
        decoded = _decode_parts(source)
        tail = _tail_after_exec(source)
        rendered = decoded.rstrip() + "\n"
        if tail:
            rendered += "\n" + tail + "\n"
    else:
        decoded = _decode_literal(source)
        tail = _tail_after_exec(source)
        rendered = decoded.rstrip() + "\n"
        if tail:
            rendered += "\n" + tail + "\n"

    if "exec(compile(" in rendered or "zlib.decompress(base64" in rendered:
        raise RuntimeError(f"Runtime loader remained after materialization: {path.name}")

    compile(rendered, str(path), "exec")
    path.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"materialized {path.name}: {len(source)} -> {len(rendered)} chars")
    return True


def main() -> None:
    changed = []
    for name in TARGETS:
        path = ROOT / name
        if not path.exists():
            raise FileNotFoundError(path)
        if materialize(path):
            changed.append(name)

    if len(changed) != len(TARGETS):
        raise RuntimeError(f"Expected to materialize {len(TARGETS)} wrappers, materialized {changed}")

    for name in TARGETS:
        text = (ROOT / name).read_text(encoding="utf-8")
        if "exec(compile(" in text:
            raise RuntimeError(f"exec loader remains in {name}")
    print("Yornis embedded-source materialization OK:", ", ".join(changed))


if __name__ == "__main__":
    main()
