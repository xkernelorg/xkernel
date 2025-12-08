"""
xkernel
-------

Minimal deterministic X-field engine + lenses.

Public API
----------
Engine:
    - XKernelConfig : configuration for the X-field kernel
    - XKernel       : deterministic update engine
    - XState        : one timestep of the X-field
    - seed_zero     : zero field initializer
    - seed_impulse  : single-impulse initializer
    - trace_to_dict : export a run as a JSON-style trace

Wave lens:
    - WaveSample, WaveHistory
    - wave_from_states : extract a scalar waveform from a run
    - analytic_wave    : generate sine/square/triangle/saw waves
    - ascii_wave       : render a waveform as ASCII
"""

from .xkernel import (
    __version__,
    ENGINE_NAME,
    XState,
    XKernelConfig,
    XKernel,
    seed_zero,
    seed_impulse,
    trace_to_dict,
)

from .lens_wave import (
    WaveSample,
    WaveHistory,
    wave_from_states,
    analytic_wave,
    ascii_wave,
)

__all__ = [
    # metadata
    "__version__",
    "ENGINE_NAME",
    # engine
    "XState",
    "XKernelConfig",
    "XKernel",
    "seed_zero",
    "seed_impulse",
    "trace_to_dict",
    # wave lens
    "WaveSample",
    "WaveHistory",
    "wave_from_states",
    "analytic_wave",
    "ascii_wave",
]
