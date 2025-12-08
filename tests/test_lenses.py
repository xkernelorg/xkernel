import math

from xkernel import XKernel, XKernelConfig, seed_impulse
from xkernel.lens_wave import wave_from_states
from xkernel.lens_schrodinger import lens_schrodinger, SchrodingerResult
from xkernel.lens_einstein import lens_einstein, EinsteinResult
from xkernel.lens_shannon import lens_shannon, ShannonResult


def _make_wave():
    cfg = XKernelConfig(size=8, dim=3, eta=0.1)
    initial = seed_impulse(cfg, index=3, component=1, amplitude=1.0)
    kernel = XKernel(cfg)
    states = list(kernel.run(initial, steps=32))
    wave = wave_from_states(states, site=3, component=1, normalize=True)
    return wave


def test_schrodinger_lens_basic():
    wave = _make_wave()
    result = lens_schrodinger(wave)
    n = len(wave.samples)

    assert isinstance(result, SchrodingerResult)
    assert len(result.amplitude) == n
    assert len(result.phase) == n
    assert len(result.probability) == n
    assert len(result.kinetic) == n

    # probability is normalized
    assert math.isclose(sum(result.probability), 1.0, rel_tol=1e-6, abs_tol=1e-6)


def test_einstein_lens_basic():
    wave = _make_wave()
    result = lens_einstein(wave)
    n = len(wave.samples)

    assert isinstance(result, EinsteinResult)
    assert len(result.curvature) == n
    assert len(result.strain) == n
    assert len(result.energy) == n

    # energy and strain should be non-negative
    assert all(e >= 0.0 for e in result.energy)
    assert all(s >= 0.0 for s in result.strain)


def test_shannon_lens_basic():
    wave = _make_wave()
    result = lens_shannon(wave)
    n = len(wave.samples)

    assert isinstance(result, ShannonResult)
    assert len(result.probability) == n
    assert len(result.entropy_series) == n

    # probability normalized
    assert math.isclose(sum(result.probability), 1.0, rel_tol=1e-6, abs_tol=1e-6)

    # entropy should be non-negative (for finite discrete distributions)
    assert result.entropy >= 0.0
