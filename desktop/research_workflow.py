from __future__ import annotations
import base64
import zlib
from _research_part00 import PART as P0
from _research_part01 import PART as P1
from _research_part02 import PART as P2
from _research_part03 import PART as P3
from _research_part04 import PART as P4

_payload = P0 + P1 + P2 + P3 + P4
_source = zlib.decompress(base64.b64decode(_payload))
exec(compile(_source, '<research_workflow>', 'exec'))

_original_install = install

def install(namespace: dict):
    # This release keeps the 0.12.x Classic interface and adds the research workflow.
    namespace['APP_VERSION'] = '0.13.1 Classic'
    return _original_install(namespace)
