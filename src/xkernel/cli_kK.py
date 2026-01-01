from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from .kinds import StateVector, Step, Execution
from .ops import validate_execution
from .hashing import xk_id
from .receipt import receipt_object, verify_receipt
from .receipt_hashing import receipt_id as receipt_id_fn


def _die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "rb") as f:
            raw = f.read()
        obj = json.loads(raw.decode("utf-8"))
    except FileNotFoundError:
        _die(f"FILE_NOT_FOUND: {path}")
    except UnicodeDecodeError:
        _die(f"NOT_UTF8_JSON: {path}")
    except json.JSONDecodeError as e:
        _die(f"INVALID_JSON: {path}: {e}")
    if not isinstance(obj, dict):
        _die(f"ROOT_NOT_OBJECT: {path}")
    return obj


def _require_keys(obj: Dict[str, Any], keys: List[str], where: str) -> None:
    for k in keys:
        if k not in obj:
            _die(f"MISSING_KEY: {where}.{k}")


def _parse_state(obj: Dict[str, Any], where: str) -> StateVector:
    _require_keys(obj, ["coords", "meta"], where)
    coords = obj["coords"]
    meta = obj["meta"]
    if not isinstance(coords, list) or len(coords) == 0:
        _die(f"BAD_COORDS: {where}.coords")
    for i, v in enumerate(coords):
        if isinstance(v, bool) or not isinstance(v, int):
            _die(f"BAD_COORD: {where}.coords[{i}] (must be int)")
    if not isinstance(meta, dict):
        _die(f"BAD_META: {where}.meta (must be object)")
    return StateVector(coords=list(coords), meta=dict(meta))


def _parse_step(obj: Dict[str, Any], where: str) -> Step:
    _require_keys(obj, ["id", "delta", "action", "witness"], where)
    sid = obj["id"]
    delta = obj["delta"]
    action = obj["action"]
    witness = obj["witness"]

    if not isinstance(sid, str) or not sid:
        _die(f"BAD_STEP_ID: {where}.id")
    if not isinstance(delta, dict):
        _die(f"BAD_DELTA: {where}.delta (must be object)")
    if isinstance(action, bool) or not isinstance(action, int):
        _die(f"BAD_ACTION: {where}.action (must be int)")
    if not isinstance(witness, dict):
        _die(f"BAD_WITNESS: {where}.witness (must be object)")

    return Step(id=sid, delta=_parse_state(delta, f"{where}.delta"), action=int(action), witness=dict(witness))


def _parse_execution_file(path: str) -> Execution:
    root = _load_json(path)

    # Accept either a "wrapped" object produced by execution_to_obj(...)
    # or a bare execution object.
    if "execution" in root:
        ex = root["execution"]
        if not isinstance(ex, dict):
            _die("BAD_EXECUTION: root.execution (must be object)")
        exec_obj = ex
    else:
        exec_obj = root

    _require_keys(exec_obj, ["init", "steps", "final", "claims"], "execution")

    init = exec_obj["init"]
    steps = exec_obj["steps"]
    final = exec_obj["final"]
    claims = exec_obj["claims"]

    if not isinstance(init, dict):
        _die("BAD_INIT: execution.init (must be object)")
    if not isinstance(final, dict):
        _die("BAD_FINAL: execution.final (must be object)")
    if not isinstance(steps, list):
        _die("BAD_STEPS: execution.steps (must be array)")
    if not isinstance(claims, dict):
        _die("BAD_CLAIMS: execution.claims (must be object)")

    step_objs: List[Step] = []
    for i, s in enumerate(steps):
        if not isinstance(s, dict):
            _die(f"BAD_STEP: execution.steps[{i}] (must be object)")
        step_objs.append(_parse_step(s, f"execution.steps[{i}]"))

    return Execution(
        init=_parse_state(init, "execution.init"),
        steps=step_objs,
        final=_parse_state(final, "execution.final"),
        claims=dict(claims),
    )


def _parse_target_file(path: str) -> StateVector:
    root = _load_json(path)
    return _parse_state(root, "target")


def _parse_receipt_file(path: str) -> Dict[str, Any]:
    root = _load_json(path)
    return root


def _emit_json(obj: Any) -> None:
    print(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="xkernel-kK", add_help=True)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_val = sub.add_parser("validate", help="Validate execution (k=1 + replay match).")
    p_val.add_argument("execution_json")

    p_hash = sub.add_parser("hash", help="Print execution content-address (xk:sha256:...).")
    p_hash.add_argument("execution_json")

    p_rec = sub.add_parser("receipt", help="Emit receipt JSON for execution (optional target closure).")
    p_rec.add_argument("execution_json")
    p_rec.add_argument("--target", dest="target_json", default=None)

    p_ver = sub.add_parser("verify", help="Verify receipt integrity against an execution.")
    p_ver.add_argument("receipt_json")
    p_ver.add_argument("execution_json")

    p_rh = sub.add_parser("receipt-hash", help="Print receipt content-address (xr:sha256:...).")
    p_rh.add_argument("receipt_json")

    args = p.parse_args(argv)

    if args.cmd == "validate":
        E = _parse_execution_file(args.execution_json)
        v = validate_execution(E)
        _emit_json({"ok": v.ok, "reason": v.reason, "details": v.details})
        return 0 if v.ok else 1

    if args.cmd == "hash":
        E = _parse_execution_file(args.execution_json)
        print(xk_id(E))
        return 0

    if args.cmd == "receipt":
        E = _parse_execution_file(args.execution_json)
        target = _parse_target_file(args.target_json) if args.target_json else None
        r = receipt_object(execution=E, target=target)
        _emit_json(r)
        return 0

    if args.cmd == "verify":
        r = _parse_receipt_file(args.receipt_json)
        E = _parse_execution_file(args.execution_json)
        v = verify_receipt(receipt=r, execution=E)
        _emit_json({"ok": v.ok, "reason": v.reason, "details": v.details})
        return 0 if v.ok else 1

    if args.cmd == "receipt-hash":
        r = _parse_receipt_file(args.receipt_json)
        print(receipt_id_fn(r))
        return 0

    _die("UNKNOWN_CMD")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
