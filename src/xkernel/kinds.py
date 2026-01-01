from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class StateVector:
    coords: List[int]
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.coords, list) or len(self.coords) == 0:
            raise ValueError("StateVector.coords must be a non-empty list[int]")
        for i, v in enumerate(self.coords):
            if isinstance(v, bool) or not isinstance(v, int):
                raise TypeError(f"StateVector.coords[{i}] must be int (got {type(v).__name__})")


@dataclass(frozen=True)
class Step:
    id: str
    delta: StateVector
    action: int = 1
    witness: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("Step.id must be a non-empty string")
        if isinstance(self.action, bool) or not isinstance(self.action, int):
            raise TypeError("Step.action must be int")


@dataclass(frozen=True)
class Execution:
    init: StateVector
    steps: List[Step]
    final: StateVector
    claims: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.steps, list):
            raise TypeError("Execution.steps must be a list[Step]")


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)
