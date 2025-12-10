from xkernel.bundle import Bundle
from xkernel.fiber import Fiber
from xkernel.filament import Filament


def test_bundle_summary_non_empty():
    filament = Filament(states=[[0.0], [1.0]])
    fiber = Fiber()
    fiber.add_filament("f0", filament)

    bundle = Bundle()
    bundle.add_fiber("fiber0", fiber)

    summary = bundle.summary()
    assert "fibers: 1" in summary
    assert "steps per filament: 2" in summary
