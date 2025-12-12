from __future__ import annotations

from dataclasses import dataclass

from .xkernel import XKernel, XKernelConfig
from .filament import Filament
from .fiber import Fiber
from .bundle import Bundle


@dataclass(frozen=True)
class ExtrusionSpec:
    """Specification for a bundle extrusion."""  # noqa: D401

    fibers: int
    filaments_per_fiber: int
    steps: int
    dimension: int
    eta: float = 0.1


class XEngine:
    """Top-level orchestration API for xkernel."""  # noqa: D401

    def __init__(self, config: XKernelConfig | None = None) -> None:
        self._config = config or XKernelConfig()

    def _seed_for(
        self,
        dim: int,
        fiber_idx: int,
        filament_idx: int,
    ) -> list[float]:
        """Deterministic but agnostic seed generator."""
        base = fiber_idx * 1000 + filament_idx
        return [(base + i) / 100.0 for i in range(dim)]

    def extrude(self, spec: ExtrusionSpec) -> Bundle:
        """Extrude a bundle matching the given spec."""
        kernel_config = XKernelConfig(
            eta=spec.eta,
            weights=self._config.weights,
        )
        kernel = XKernel(dim=spec.dimension, config=kernel_config)
        bundle = Bundle()

        for f_idx in range(spec.fibers):
            fiber = Fiber()
            for k in range(spec.filaments_per_fiber):
                seed = self._seed_for(spec.dimension, f_idx, k)
                filament = Filament.from_xkernel(
                    kernel=kernel,
                    seed=seed,
                    steps=spec.steps,
                )
                filament_key = f"f{f_idx}_φ{k}"
                fiber.add_filament(filament_key, filament)
            fiber_key = f"fiber_{f_idx}"
            bundle.add_fiber(fiber_key, fiber)

        return bundle
