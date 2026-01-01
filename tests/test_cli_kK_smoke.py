import json
import subprocess
import sys
from pathlib import Path


def _run(*args: str):
    return subprocess.run([sys.executable, "-m", "xkernel.cli_kK", *args], capture_output=True, text=True)


def test_cli_validate_and_hash_and_receipt(tmp_path: Path):
    exec_path = tmp_path / "exec.json"
    target_path = tmp_path / "target.json"
    receipt_path = tmp_path / "receipt.json"

    exec_obj = {
        "execution": {
            "init": {"coords": [0, 0], "meta": {}},
            "steps": [
                {"id": "s1", "delta": {"coords": [1, 0], "meta": {}}, "action": 1, "witness": {}},
                {"id": "s2", "delta": {"coords": [0, 1], "meta": {}}, "action": 1, "witness": {}},
            ],
            "final": {"coords": [1, 1], "meta": {}},
            "claims": {},
        }
    }

    target_obj = {"coords": [1, 1], "meta": {}}

    exec_path.write_text(json.dumps(exec_obj), encoding="utf-8")
    target_path.write_text(json.dumps(target_obj), encoding="utf-8")

    # validate
    r = _run("validate", str(exec_path))
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["ok"] is True

    # hash
    r = _run("hash", str(exec_path))
    assert r.returncode == 0
    assert r.stdout.strip().startswith("xk:sha256:")

    # receipt
    r = _run("receipt", str(exec_path), "--target", str(target_path))
    assert r.returncode == 0
    receipt = json.loads(r.stdout)
    assert receipt["spec"] == "XKERNEL_RECEIPT_V1"
    assert receipt["closure"]["closed"] is True

    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    # receipt-hash
    r = _run("receipt-hash", str(receipt_path))
    assert r.returncode == 0
    assert r.stdout.strip().startswith("xr:sha256:")

    # verify
    r = _run("verify", str(receipt_path), str(exec_path))
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["ok"] is True
