from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .xkernel import XKernel


@dataclass
class Filament:
    """A 1-D history of a state vector under an XKernel."""

    states: List[List[float]] = field(default_factory=list)

    @property
    def steps(self) -> int:
        return len(self.states)

    @property
    def dimension(self) -> int:
        return len(self.states[0]) if self.states else 0

    @classmethod
    def from_xkernel(
        cls,
        kernel: XKernel,
        seed: Iterable[float],
        steps: int,
    ) -> "Filament":
        state = list(seed)
        if len(state) != kernel.dim:
            raise ValueError("seed dimension mismatch")

        history: List[List[float]] = [state]
        for _ in range(steps - 1):
            state = kernel.step(state)
            history.append(state)

        return cls(states=history)
