# tests/test_xkernel_basic.py

import math

from xkernel import (
    XKernel,
    XKernelConfig,
    XState,
    seed_zero,
    seed_impulse,
    trace_to_dict,
    wave_from_states,
    analytic_wave,
    ascii_wave,
)


def _check_state_shape(state: XState, size: int, dim: int) -> None:
    assert len(state.field) == size
    for row in state.field:
        assert len(row) == dim


def test_seed_zero_shape_and_values():
    cfg = XKernelConfig(size=8, dim=6, eta=0.1)
    state = seed_zero(cfg)

    assert state.step == 0
    _check_state_shape(state, size=8, dim=6)

    # all zeros
    for row in state.field:
        for v in row:
            assert v == 0.0


def test_seed_impulse_shape_and_single_nonzero():
    cfg = XKernelConfig(size=8, dim=6, eta=0.1)
    idx = 3
    comp = 2
    amp = 1.5

    state = seed_impulse(cfg, index=idx, component=comp, amplitude=amp)

    assert state.step == 0
    _check_state_shape(state, size=8, dim=6)

    nonzeros = []
    for i, row in enumerate(state.field):
        for j, v in enumerate(row):
            if v != 0.0:
                nonzeros.append((i, j, v))

    assert nonzeros == [(idx, comp, amp)]


def test_kernel_run_deterministic_and_shapes():
    cfg = XKernelConfig(size=8, dim=4, eta=0.1)
    initial = seed_impulse(cfg, index=2, component=1, amplitude=1.0)

    kernel = XKernel(cfg)

    states1 = list(kernel.run(initial, steps=5))
    states2 = list(kernel.run(initial, steps=5))

    # lengths
    assert len(states1) == 6  # initial + 5 steps
    assert len(states2) == 6

    # steps strictly increasing, shapes consistent
    for k, s in enumerate(states1):
        assert s.step == k
        _check_state_shape(s, size=cfg.size, dim=cfg.dim)

    # determinism: fields match exactly
    for s1, s2 in zip(states1, states2):
        assert s1.step == s2.step
        assert s1.field == s2.field


def test_trace_to_dict_structure():
    cfg = XKernelConfig(size=8, dim=4, eta=0.1)
    initial = seed_impulse(cfg, index=1, component=0, amplitude=1.0)
    kernel = XKernel(cfg)
    states = list(kernel.run(initial, steps=3))

    trace = trace_to_dict(states)

    assert trace["engine"] == "xkernel"
    assert "version" in trace
    assert trace["dim"] == cfg.dim
    assert trace["size"] == cfg.size
    assert len(trace["frames"]) == len(states)

    first = trace["frames"][0]
    assert first["step"] == 0
    assert "field" in first


def test_wave_from_states_normalized_range():
    cfg = XKernelConfig(size=8, dim=3, eta=0.1)
    initial = seed_impulse(cfg, index=2, component=1, amplitude=1.0)
    kernel = XKernel(cfg)
    states = list(kernel.run(initial, steps=16))

    wave = wave_from_states(states, site=2, component=1, normalize=True)

    assert len(wave.samples) == len(states)
    vals = [s.value for s in wave.samples]

    # normalization: values should be in [-1, 1] (allow tiny epsilon)
    max_abs = max(abs(v) for v in vals)
    assert max_abs <= 1.0 + 1e-9


def test_analytic_square_wave_values():
    steps = 32
    amp = 2.0
    wave = analytic_wave(
        "square",
        steps=steps,
        amplitude=amp,
        frequency=2.0,
    )

    vals = {round(s.value, 6) for s in wave.samples}
    # square wave should only take ±amplitude values
    assert vals.issubset({-amp, amp})
    assert len(wave.samples) == steps


def test_ascii_wave_dimensions():
    # simple sine wave for rendering
    wave = analytic_wave(
        "sine",
        steps=64,
        amplitude=1.0,
        frequency=1.0,
    )

    height = 10
    width = 40
    rendered = ascii_wave(wave, height=height, width=width)

    lines = rendered.splitlines()
    assert len(lines) == height
    for line in lines:
        assert len(line) == width

    # at least one '#' present
    assert any("#" in line for line in lines)
