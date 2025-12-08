from xkernel.xkernel import XKernelConfig, XKernel, seed_zero, seed_impulse


def test_zero_field_shape():
    cfg = XKernelConfig(size=8, dim=6, eta=0.1)
    state0 = seed_zero(cfg)
    assert state0.step == 0
    assert len(state0.field) == 8
    assert all(len(cell) == 6 for cell in state0.field)


def test_impulse_evolves():
    cfg = XKernelConfig(size=8, dim=6, eta=0.1)
    kernel = XKernel(cfg)
    state0 = seed_impulse(cfg, index=4, component=0, amplitude=1.0)

    states = list(kernel.run(state0, steps=3))
    assert len(states) == 4  # initial + 3 steps

    # Check that something changed after one step
    s1 = states[1]
    assert any(abs(v) > 1e-8 for cell in s1.field for v in cell)
