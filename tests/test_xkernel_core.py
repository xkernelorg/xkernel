import pytest
from xkernel import (
    StateVector,
    Step,
    Execution,
    validate_execution,
    closed,
)

def test_valid_execution_closes():
    init = StateVector(coords=[0, 0], meta={})
    step = Step(
        id="s1",
        delta=StateVector(coords=[1, 1], meta={}),
        action=1,
        witness={},
    )
    final = StateVector(coords=[1, 1], meta={})

    E = Execution(
        init=init,
        steps=[step],
        final=final,
        claims={},
    )

    v = validate_execution(E)
    assert v.ok is True
    assert closed(E, final) is True


def test_non_admissible_step_rejected():
    init = StateVector(coords=[0, 0], meta={})
    bad_step = Step(
        id="bad",
        delta=StateVector(coords=[1, 1], meta={}),
        action=2,   # violates k = 1
        witness={},
    )
    final = StateVector(coords=[1, 1], meta={})

    E = Execution(
        init=init,
        steps=[bad_step],
        final=final,
        claims={},
    )

    v = validate_execution(E)
    assert v.ok is False
    assert v.reason == "NON_ADMISSIBLE_STEP"
