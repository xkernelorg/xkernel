from __future__ import annotations

"""Einstein-style geometric lens for xkernel waveforms.

This lens treats the waveform as encoding a 1-D "geometry" and extracts:

- curvature(t): discrete second difference (Regge-like curvature)
- strain(t):    gradient magnitude |ψ_{k+1} - ψ_{k-1}|
- energy(t):    0.5 * (gradient)^2, an energy-like quantity

All operations are purely algebraic and local in the time index.
"""

from dataclasses import dataclass
from typing import List

from .lens_wave import WaveHistory


@dataclass
class EinsteinResult:
    curvature: List[float]
    strain: List[float]
    energy: List[float]


def lens_einstein(wave: WaveHistory) -> EinsteinResult:
    """Apply an Einstein-style geometric lens to a WaveHistory.

    Parameters
    ----------
    wave:
        WaveHistory produced by lens_wave.wave_from_states or analytic_wave.

    Returns
    -------
    EinsteinResult
        curvature, strain, and energy arrays of the same length as the wave.
    """
    values = [s.value for s in wave.samples]
    n = len(values)

    if n == 0:
        return EinsteinResult([], [], [])

    curvature: List[float] = []
    strain: List[float] = []
    energy: List[float] = []

    for i in range(n):
        left = values[i - 1] if i > 0 else values[i]
        center = values[i]
        right = values[i + 1] if i < n - 1 else values[i]

        # Discrete second derivative (curvature)
        K = left - 2.0 * center + right
        curvature.append(K)

        # Strain: magnitude of gradient
        grad = right - left
        s = abs(grad)
        strain.append(s)

        # Energy-like term
        e = 0.5 * grad * grad
        energy.append(e)

    return EinsteinResult(curvature=curvature, strain=strain, energy=energy)
