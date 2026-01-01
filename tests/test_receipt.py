from xkernel import (
    StateVector,
    Step,
    Execution,
    receipt_object,
    receipt_json_bytes,
)


def _sample_execution() -> Execution:
    return Execution(
        init=StateVector([0, 0]),
        steps=[
            Step(id="s1", delta=StateVector([1, 0]), action=1),
            Step(id="s2", delta=StateVector([0, 1]), action=1),
        ],
        final=StateVector([1, 1]),
        claims={"intent": "receipt-test"},
    )


def test_receipt_basic_fields():
    E = _sample_execution()
    r = receipt_object(execution=E)

    assert r["spec"] == "XKERNEL_RECEIPT_V1"
    assert r["version"].startswith("1.")
    assert r["execution_id"].startswith("xk:sha256:")
    assert r["verdict"]["ok"] is True
    assert r["verdict"]["reason"] == "OK"


def test_receipt_with_closure():
    E = _sample_execution()
    target = StateVector([1, 1])

    r = receipt_object(execution=E, target=target)

    assert "closure" in r
    assert r["closure"]["closed"] is True
    assert r["closure"]["target"]["coords"] == [1, 1]


def test_receipt_is_canonical_bytes():
    E = _sample_execution()
    r1 = receipt_object(execution=E)
    r2 = receipt_object(execution=E)

    b1 = receipt_json_bytes(r1)
    b2 = receipt_json_bytes(r2)

    assert b1 == b2
    assert b1.startswith(b"{")
    assert b1.endswith(b"}")
