from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .filament import Filament


@dataclass
class Fiber:
    """Collection of filaments that share a common pattern or origin."""  # noqa: D401

    filaments: Dict[str, Filament] = field(default_factory=dict)

    def add_filament(self, key: str, filament: Filament) -> None:
        self.filaments[key] = filament

    def __len__(self) -> int:
        return len(self.filaments)

    @property
    def steps(self) -> int:
        if not self.filaments:
            return 0
        return next(iter(self.filaments.values())).steps

    @property
    def dimension(self) -> int:
        if not self.filaments:
            return 0
        return next(iter(self.filaments.values())).dimension

    def keys(self) -> List[str]:
        return list(self.filaments.keys())
