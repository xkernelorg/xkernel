from __future__ import annotations

"""
lens_wave.py
------------

Waveform lens for the xkernel engine.

This module does NOT change xkernel dynamics.
It provides *views* of histories as 1-D waveforms, plus simple analytic
wave generators (sine, square, triangle, saw).

Core ideas
----------
- XKernel run: Iterable[XState] with step = tick.
- Wave lens: map each XState to a single scalar sample y_k.
- WaveHistory: ordered samples + metadata.

Example usage
-------------
from xkernel import XKernel, XKernelConfig, seed_impulse
from xkernel.lens_wave import wave_from_states, ascii_wave

cfg = XKernelConfig(size=16, dim=6, eta=0.1)
initial = seed_impulse(cfg, index=3, component=0, amplitude=1.0)
kernel = XKernel(cfg)

states = list(kernel.run(initial, steps=128))

wave = wave_from_states(states, site=3, component=0, normalize=True)
print(ascii_wave(wave, height=12))

# Analytic square wave:
from xkernel.lens_wave import analytic_wave

sq = analytic_wave("square", steps=64, amplitude=1.0, frequency=2.0)
print(ascii_wave(sq, height=10))
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple
import math

from .xkernel import XState


# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WaveSample:
    """
    One sample of a waveform.

    - tick: integer tick index (k = 0, 1, 2, …)
    - value: scalar sample y_k
    """
    tick: int
    value: float

    def to_dict(self) -> Dict[str, Any]:
        return {"tick": self.tick, "value": self.value}


@dataclass
class WaveHistory:
    """
    1-D waveform over integer ticks.

    - samples: ordered list of WaveSample in increasing tick order
    - meta: metadata about origin (engine, site, component, type, etc.)
    """

    samples: List[WaveSample]
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": self.meta,
            "samples": [s.to_dict() for s in self.samples],
        }

    def ticks(self) -> List[int]:
        return [s.tick for s in self.samples]

    def values(self) -> List[float]:
        return [s.value for s in self.samples]


# ---------------------------------------------------------------------------
# Wave lens on XKernel states
# ---------------------------------------------------------------------------


def wave_from_states(
    states: Iterable[XState],
    *,
    site: int = 0,
    component: int = 0,
    normalize: bool = False,
    meta: Optional[Dict[str, Any]] = None,
) -> WaveHistory:
    """
    Interpret a sequence of XState objects as a 1-D waveform by
    extracting a single (site, component) value at each tick.

    Parameters
    ----------
    states : iterable of XState
        Typically produced by XKernel.run(...).
    site : int
        Lattice index i to sample.
    component : int
        Component index k within the X-vector.
    normalize : bool
        If True, rescale values to lie in [-1, 1] based on max |value|.
    meta : dict, optional
        Extra metadata fields to store in the WaveHistory.

    Returns
    -------
    WaveHistory
    """
    samples: List[WaveSample] = []
    for s in states:
        if not s.field:
            continue
        if not (0 <= site < len(s.field)):
            raise IndexError(f"site {site} out of range for field size {len(s.field)}")
        vec = s.field[site]
        if not (0 <= component < len(vec)):
            raise IndexError(f"component {component} out of range for dim {len(vec)}")
        value = float(vec[component])
        samples.append(WaveSample(tick=s.step, value=value))

    if not samples:
        return WaveHistory(samples=[], meta=meta or {"lens": "wave", "source": "empty"})

    values = [s.value for s in samples]
    if normalize:
        max_abs = max(abs(v) for v in values) or 1.0
        samples = [
            WaveSample(tick=s.tick, value=s.value / max_abs) for s in samples
        ]

    base_meta: Dict[str, Any] = {
        "lens": "wave",
        "source": "xkernel",
        "site": site,
        "component": component,
        "normalized": normalize,
    }
    if meta:
        base_meta.update(meta)

    return WaveHistory(samples=samples, meta=base_meta)


# ---------------------------------------------------------------------------
# Analytic waveform generator
# ---------------------------------------------------------------------------

WaveKind = Literal["sine", "square", "triangle", "saw"]


def analytic_wave(
    kind: WaveKind,
    *,
    steps: int,
    amplitude: float = 1.0,
    frequency: float = 1.0,
    phase: float = 0.0,
    duty: float = 0.5,
    meta: Optional[Dict[str, Any]] = None,
) -> WaveHistory:
    """
    Generate an analytic waveform over integer ticks.

    Parameters
    ----------
    kind : "sine" | "square" | "triangle" | "saw"
        Type of waveform.
    steps : int
        Number of samples (ticks).
    amplitude : float
        Peak absolute value.
    frequency : float
        Cycles per total steps (i.e. f = cycles / steps).
    phase : float
        Phase offset in radians for sine-based shapes.
    duty : float
        Duty cycle for square wave (0 < duty < 1), fraction of period at +amp.

    Returns
    -------
    WaveHistory
    """
    if steps <= 0:
        return WaveHistory(samples=[], meta={"lens": "wave", "source": "analytic-empty"})

    samples: List[WaveSample] = []

    for k in range(steps):
        # normalized time in [0, 1)
        t = k / float(steps)
        # phase argument in radians (for sine-based)
        theta = 2.0 * math.pi * frequency * t + phase

        if kind == "sine":
            y = amplitude * math.sin(theta)

        elif kind == "square":
            # square from sine + duty
            # use raw phase to determine position in period
            period_pos = (frequency * t + phase / (2.0 * math.pi)) % 1.0
            y = amplitude if period_pos < duty else -amplitude

        elif kind == "triangle":
            # triangle from saw: 0 → 1 ramp, then reflect
            period_pos = (frequency * t + phase / (2.0 * math.pi)) % 1.0
            tri = 2.0 * abs(2.0 * period_pos - 1.0) - 1.0  # in [-1, 1]
            y = amplitude * tri

        elif kind == "saw":
            period_pos = (frequency * t + phase / (2.0 * math.pi)) % 1.0
            saw = 2.0 * period_pos - 1.0  # ramp from -1 to 1
            y = amplitude * saw

        else:
            raise ValueError(f"unknown wave kind: {kind!r}")

        samples.append(WaveSample(tick=k, value=y))

    base_meta: Dict[str, Any] = {
        "lens": "wave",
        "source": "analytic",
        "kind": kind,
        "steps": steps,
        "amplitude": amplitude,
        "frequency": frequency,
        "phase": phase,
        "duty": duty,
    }
    if meta:
        base_meta.update(meta)

    return WaveHistory(samples=samples, meta=base_meta)


# ---------------------------------------------------------------------------
# ASCII helper (simple viewer on top of the lens)
# ---------------------------------------------------------------------------


def ascii_wave(
    wave: WaveHistory,
    *,
    height: int = 12,
    width: Optional[int] = None,
) -> str:
    """
    Render a WaveHistory as a compact ASCII oscilloscope.

    Parameters
    ----------
    wave : WaveHistory
        Waveform to render.
    height : int
        Number of rows (vertical resolution).
    width : int, optional
        Number of columns. If None, uses len(samples).

    Returns
    -------
    str
        Multiline string which can be printed directly.
    """
    samples = wave.samples
    if not samples:
        return "<empty wave>"

    values = [s.value for s in samples]
    v_min = min(values)
    v_max = max(values)
    if v_max == v_min:
        v_max = v_min + 1.0  # avoid division by zero

    n = len(samples)
    cols = width if width is not None else n

    # Resample or truncate to desired width
    if cols <= 0:
        return "<empty wave>"

    if cols == n:
        vs = values
    else:
        vs = []
        for c in range(cols):
            idx = int(round(c * (n - 1) / (cols - 1)))
            vs.append(values[idx])

    # map values to row indices (0 = top)
    rows = [[" " for _ in range(cols)] for _ in range(height)]
    for c, v in enumerate(vs):
        norm = (v - v_min) / (v_max - v_min)
        r = height - 1 - int(round(norm * (height - 1)))
        rows[r][c] = "#"

    return "\n".join("".join(row) for row in rows)
