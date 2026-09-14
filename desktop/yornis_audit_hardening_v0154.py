from __future__ import annotations
import base64, hashlib, zlib
from _yornis_audit154_part00 import PART as P0
from _yornis_audit154_part01 import PART as P1
from _yornis_audit154_part02 import PART as P2
from _yornis_audit154_part03 import PART as P3
from _yornis_audit154_part04 import PART as P4
from _yornis_audit154_part05 import PART as P5
from _yornis_audit154_part06 import PART as P6

_payload = P0 + P1 + P2 + P3 + P4 + P5 + P6
assert hashlib.sha256(_payload.encode('ascii')).hexdigest() == '0b0829d63af132860d5937ca1a5315d3daec7a7748a67ae5951616542bf4bdcc', 'v0.15.4 payload checksum mismatch'
exec(compile(zlib.decompress(base64.b64decode(_payload, validate=True)), '<yornis_audit_hardening_v0154>', 'exec'))
