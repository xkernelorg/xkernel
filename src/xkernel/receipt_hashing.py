from __future__ import annotations

import hashlib
from typing import Any, Dict

from .receipt import receipt_json_bytes


def receipt_sha256_bytes(receipt: Dict[str, Any]) -> bytes:
    """
    Hash the canonical receipt bytes (sorted keys, no whitespace, UTF-8).
    """
    return hashlib.sha256(receipt_json_bytes(receipt)).digest()


def receipt_sha256_hex(receipt: Dict[str, Any]) -> str:
    """
    Hex digest of sha256(receipt_json_bytes(receipt)).
    """
    return hashlib.sha256(receipt_json_bytes(receipt)).hexdigest()


def receipt_id(receipt: Dict[str, Any]) -> str:
    """
    Content-addressed receipt ID.
    Namespaced so it doesn't collide with execution IDs.

    Example: xr:sha256:<hex>
    """
    return f"xr:sha256:{receipt_sha256_hex(receipt)}"
