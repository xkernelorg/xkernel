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
        claims={"intent": "verify-test"},
    )


def test_verify_receipt_ok():
    E = _sample_execution()
    r = receipt_object(execution=E, target=StateVector([1, 1]))
    v = verify_receipt(receipt=r, execution=E)
    assert v.ok is True
    assert v.reason == "OK"


def test_verify_receipt_detects_exec_id_mismatch():
    E = _sample_execution()
    r = receipt_object(execution=E)
    r["execution_id"] = "xk:sha256:" + "0" * 64  # tamper
    v = verify_receipt(receipt=r, execution=E)
    assert v.ok is False
    assert v.reason == "RECEIPT_EXECUTION_ID_MISMATCH"
