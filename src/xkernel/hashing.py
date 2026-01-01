from __future__ import annotations

import hashlib

from .kinds import Execution
from .canonical import canonical_json_bytes


def sha256_bytes(E: Execution) -> bytes:
    return hashlib.sha256(canonical_json_bytes(E)).digest()


def sha256_hex(E: Execution) -> str:
    return hashlib.sha256(canonical_json_bytes(E)).hexdigest()


def xk_id(E: Execution) -> str:
    return f"xk:sha256:{sha256_hex(E)}"
