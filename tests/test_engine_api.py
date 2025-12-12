from xkernel.engine import XEngine, ExtrusionSpec


def test_xengine_extrude_shapes_match_spec():
    engine = XEngine()
    spec = ExtrusionSpec(
        fibers=2,
        filaments_per_fiber=3,
        steps=4,
        dimension=4,
    )

    bundle = engine.extrude(spec)

    assert len(bundle.fibers) == 2

    any_fiber = next(iter(bundle.fibers.values()))
    assert len(any_fiber) == 3
    assert any_fiber.steps == 4
    assert any_fiber.dimension == 4
