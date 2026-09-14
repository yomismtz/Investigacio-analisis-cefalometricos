from __future__ import annotations
import base64
import zlib
from _yornis_quality_part00 import PART as P0
from _yornis_quality_part01 import PART as P1
from _yornis_quality_part02 import PART as P2
from _yornis_quality_part03 import PART as P3
from _yornis_quality_part04 import PART as P4
from _yornis_quality_part05 import PART as P5
from _yornis_quality_part06 import PART as P6
from _yornis_quality_part07 import PART as P7
from _yornis_quality_part08 import PART as P8
from _yornis_quality_part09 import PART as P9

_payload = P0 + P1 + P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9
exec(compile(zlib.decompress(base64.b64decode(_payload)), '<yornis_ceph_quality_v0153>', 'exec'))

# Accept standard clinical prime notation in addition to the compact internal
# names used by the inherited engine. Existing stored traces remain unchanged.
import classic_engine as _engine
_v0153_compute = _engine.compute
_CLINICAL_POINT_ALIASES = {
    "G'": "GS",
    "N'": "NS",
    "Pg'": "PgS",
    "Me'": "MeS",
    "Gn'": "GnS",
}

def _alias_safe_compute(measurement, points, mm_per_px, face_direction='right'):
    if points:
        normalized = dict(points)
        for clinical, internal in _CLINICAL_POINT_ALIASES.items():
            if internal not in normalized and clinical in normalized:
                normalized[internal] = normalized[clinical]
        points = normalized
    return _v0153_compute(measurement, points, mm_per_px, face_direction)

_engine.compute = _alias_safe_compute
