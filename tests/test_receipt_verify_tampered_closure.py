from xkernel import (
    StateVector,
    Step,
    Execution,
    receipt_object,
    verify_receipt,
)


def _sample_execution() -> Execution:
    return Execution(
        init=StateVector([0, 0]),
        steps=[
            Step(id="s1", delta=StateVector([1, 0]), action=1),
            Step(id="s2", delta=StateVector([0, 1]), action=1),
        ],
        final=StateVector([1, 1]),
        claims={"intent": "tamper-closure-test"},
    )


def test_verify_receipt_detects_tampered_closure_flag():
    E = _sample_execution()

    # Create a truthful receipt with a target that *does* close.
    r = receipt_object(execution=E, target=StateVector([1, 1]))
    assert r["closure"]["closed"] is True

    # Tamper: flip the closure flag while keeping the target the same.
    r["closure"]["closed"] = False

    v = verify_receipt(receipt=r, execution=E)
    assert v.ok is False
    assert v.reason == "RECEIPT_CLOSURE_MISMATCH"


def test_verify_receipt_detects_tampered_closure_target():
    E = _sample_execution()

    # Truthful receipt closes to [1,1]
    r = receipt_object(execution=E, target=StateVector([1, 1]))
    assert r["closure"]["closed"] is True

    # Tamper: change target coords so it should *not* close, but keep closed=True.
    r["closure"]["target"]["coords"] = [0, 0]
    r["closure"]["closed"] = True

    v = verify_receipt(receipt=r, execution=E)
    assert v.ok is False
    assert v.reason == "RECEIPT_CLOSURE_MISMATCH"
