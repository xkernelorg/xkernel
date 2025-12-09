from xkernel.xkernel import XKernel
from xkernel.filament import Filament


def test_filament_from_xkernel_produces_expected_steps():
    kernel = XKernel(dim=2)
    seed = [0.0, 0.0]
    filament = Filament.from_xkernel(kernel, seed, steps=5)

    assert filament.steps == 5
    assert filament.dimension == 2
    assert filament.states[0] == seed
