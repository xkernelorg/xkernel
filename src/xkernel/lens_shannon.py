from __future__ import annotations

"""Shannon information lens for xkernel waveforms.

Interprets the absolute value of the waveform as an unnormalized
"mass" distribution, then constructs:

- probability(t): normalized |ψ(t)| over the history
- entropy:        Shannon entropy H = -Σ p log p
- entropy_series: per-sample contribution -p log p
"""

from dataclasses import dataclass
from typing import List
import math

from .lens_wave import WaveHistory


@dataclass
class ShannonResult:
    probability: List[float]
    entropy: float
    entropy_series: List[float]


def lens_shannon(wave: WaveHistory) -> ShannonResult:
    """Apply a Shannon-information lens to a WaveHistory.

    Parameters
    ----------
    wave:
        WaveHistory produced by lens_wave.wave_from_states or analytic_wave.

    Returns
    -------
    ShannonResult
        probability, total entropy, and per-sample entropy contribution.
    """
    values = [abs(s.value) for s in wave.samples]
    n = len(values)

    if n == 0:
        return ShannonResult([], 0.0, [])

    Z = sum(values) or 1.0
    probability = [v / Z for v in values]

    # Shannon entropy H = -Σ p log p
    entropy = -sum(p * math.log(p) for p in probability if p > 0.0)

    # Per-sample contributions
    entropy_series: List[float] = []
    for p in probability:
        entropy_series.append(-(p * math.log(p)) if p > 0.0 else 0.0)

    return ShannonResult(
        probability=probability,
        entropy=entropy,
        entropy_series=entropy_series,
    )
