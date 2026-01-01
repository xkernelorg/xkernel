from xkernel import (
    StateVector,
    Step,
    Execution,
    receipt_object,
    receipt_sha256_hex,
    receipt_id,
)


def _sample_execution() -> Execution:
    return Execution(
        init=StateVector([0, 0]),
        steps=[
            Step(id="s1", delta=StateVector([1, 0]), action=1),
            Step(id="s2", delta=StateVector([0, 1]), action=1),
        ],
        final=StateVector([1, 1]),
        claims={"intent": "receipt-hash-test"},
    )


def test_receipt_hash_is_deterministic():
    E = _sample_execution()
    r1 = receipt_object(execution=E, target=StateVector([1, 1]))
    r2 = receipt_object(execution=E, target=StateVector([1, 1]))

    h1 = receipt_sha256_hex(r1)
    h2 = receipt_sha256_hex(r2)

    assert h1 == h2
    assert receipt_id(r1).startswith("xr:sha256:")
    assert receipt_id(r1).endswith(h1)


def test_receipt_hash_changes_on_tamper():
    E = _sample_execution()
    r = receipt_object(execution=E, target=StateVector([1, 1]))
    h1 = receipt_sha256_hex(r)

    # Tamper with receipt contents (flip closure flag)
    r["closure"]["closed"] = False
    h2 = receipt_sha256_hex(r)

    assert h1 != h2
