from __future__ import annotations

"""Schrödinger-style lens for xkernel waveforms.

This lens does NOT modify the underlying xkernel dynamics.
It interprets a 1-D waveform as a complex-like amplitude and extracts:

- amplitude(t)  ≈ |ψ(t)|
- phase(t)      ∈ {0, π} via sign(ψ)
- probability(t) ∝ |ψ(t)|², normalized over the history
- kinetic(t)    = discrete second difference of the waveform

The goal is not to be a full quantum solver, but to provide
a clean, deterministic mapping from a WaveHistory to
Schrödinger-flavored observables.
"""

from dataclasses import dataclass
from typing import List
import math

from .lens_wave import WaveHistory


@dataclass
class SchrodingerResult:
    """Container for Schrödinger-lens interpretations.

    Attributes
    ----------
    amplitude:
        |ψ(t)| for each sample.
    phase:
        Phase in radians. Here we use a simple sign-based surrogate:
        0 for non-negative values, π for negative values.
    probability:
        Normalized |ψ|² over the entire history.
    kinetic:
        Discrete second difference of the waveform: ψ_{k-1} - 2ψ_k + ψ_{k+1}.
    """
    amplitude: List[float]
    phase: List[float]
    probability: List[float]
    kinetic: List[float]


def lens_schrodinger(wave: WaveHistory) -> SchrodingerResult:
    """Apply a Schrödinger-style lens to a WaveHistory.

    Parameters
    ----------
    wave:
        WaveHistory produced by lens_wave.wave_from_states or analytic_wave.

    Returns
    -------
    SchrodingerResult
        Amplitude, phase, probability, and kinetic arrays, all with
        the same length as `wave.samples`.
    """
    values = [s.value for s in wave.samples]
    n = len(values)

    if n == 0:
        return SchrodingerResult([], [], [], [])

    # Amplitude = |ψ|
    amplitude = [abs(v) for v in values]

    # Phase: simple sign-based approximation
    phase = [0.0 if v >= 0.0 else math.pi for v in values]

    # Probability density ∝ |ψ|^2, normalized
    prob_raw = [a * a for a in amplitude]
    Z = sum(prob_raw) or 1.0
    probability = [p / Z for p in prob_raw]

    # Discrete "kinetic" term: second difference
    kinetic: List[float] = []
    for i in range(n):
        left = values[i - 1] if i > 0 else values[i]
        center = values[i]
        right = values[i + 1] if i < n - 1 else values[i]
        kinetic.append(left - 2.0 * center + right)

    return SchrodingerResult(
        amplitude=amplitude,
        phase=phase,
        probability=probability,
        kinetic=kinetic,
    )
