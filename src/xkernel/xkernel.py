from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class XKernelConfig:
    """Configuration for the default XKernel rule.

    This is intentionally simple and agnostic: it just shifts a vector in ℝ^d
    by a fixed linear rule:

        s_{t+1} = s_t + eta * w

    where w is a fixed weight vector derived from `weights`.
    """  # noqa: D401

    eta: float = 0.1
    weights: List[float] | None = None

    def normalized(self, dim: int) -> "XKernelConfig":
        if self.weights is None:
            return XKernelConfig(eta=self.eta, weights=[1.0] * dim)
        if len(self.weights) != dim:
            raise ValueError("weights length must match dimension")
        return self


class XKernel:
    """Deterministic X-kernel update rule.

    The "meaning" of the coordinates is left to downstream consumers.
    """  # noqa: D401

    def __init__(self, dim: int, config: XKernelConfig | None = None) -> None:
        self._dim = dim
        self._config = (config or XKernelConfig()).normalized(dim)

    @property
    def dim(self) -> int:
        return self._dim

    def step(self, state: Iterable[float]) -> list[float]:
        """Advance one step with a deterministic linear rule."""
        state_list = list(state)
        if len(state_list) != self._dim:
            raise ValueError("state dimension mismatch")

        weights = self._config.weights or [1.0] * self._dim
        eta = self._config.eta
        return [x + eta * w for x, w in zip(state_list, weights)]
