from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .fiber import Fiber


@dataclass
class Bundle:
    """Structured collection of fibers: the unit xkernel hands off."""  # noqa: D401

    fibers: Dict[str, Fiber] = field(default_factory=dict)

    def add_fiber(self, key: str, fiber: Fiber) -> None:
        self.fibers[key] = fiber

    def __len__(self) -> int:
        return len(self.fibers)

    def summary(self) -> str:
        if not self.fibers:
            return "Bundle: empty"

        any_fiber = next(iter(self.fibers.values()))
        lines = [
            "Bundle:",
            f"  fibers: {len(self.fibers)}",
            f"  filaments per fiber: {len(any_fiber)}",
            f"  steps per filament: {any_fiber.steps}",
            f"  dimension: {any_fiber.dimension}",
        ]
        return "\n".join(lines)
