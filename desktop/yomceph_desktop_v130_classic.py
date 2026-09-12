from __future__ import annotations
import base64
import zlib
from _classic_ui_part00 import PART as P0
from _classic_ui_part01 import PART as P1
from _classic_ui_part02 import PART as P2
from _classic_ui_part03 import PART as P3
from _classic_ui_part04 import PART as P4

_payload = P0 + P1 + P2 + P3 + P4
_source = zlib.decompress(base64.b64decode(_payload))
_text = _source.decode('utf-8')
_marker = "if __name__=='__main__':"
_patch = "\nimport research_workflow as _research_workflow\n_research_workflow.install(globals())\n\n"
if _marker not in _text:
    raise RuntimeError('YomCeph Classic entry point not found')
_patched_source = _text.replace(_marker, _patch + _marker, 1).encode('utf-8')
exec(compile(_patched_source, '<yomceph_desktop_v131_classic>', 'exec'))
