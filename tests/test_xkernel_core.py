from xkernel.xkernel import XKernel, XKernelConfig


def test_xkernel_step_dimension_preserved():
    kernel = XKernel(dim=4, config=XKernelConfig(eta=0.5))
    state = [0.0, 0.0, 0.0, 0.0]
    next_state = kernel.step(state)
    assert len(next_state) == 4
    assert next_state == [0.5, 0.5, 0.5, 0.5]
