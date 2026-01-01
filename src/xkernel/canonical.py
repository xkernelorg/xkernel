from __future__ import annotations

import json
from typing import Any, Dict, List

from .kinds import Execution, StateVector, Step


def _assert_int_list(xs: List[int], path: str) -> None:
    if not isinstance(xs, list) or len(xs) == 0:
        raise ValueError(f"{path} must be a non-empty list[int]")
    for i, v in enumerate(xs):
        if isinstance(v, bool) or not isinstance(v, int):
            raise TypeError(f"{path}[{i}] must be int")


def _assert_jsonable(obj: Any, path: str) -> None:
    if obj is None or isinstance(obj, (str, int, bool)):
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_jsonable(v, f"{path}[{i}]")
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError(f"{path} keys must be str")
            _assert_jsonable(v, f"{path}.{k}")
        return
    raise TypeError(f"{path} contains non-JSONable type: {type(obj).__name__}")


def state_to_obj(st: StateVector) -> Dict[str, Any]:
    _assert_int_list(st.coords, "StateVector.coords")
    _assert_jsonable(st.meta, "StateVector.meta")
    return {"coords": list(st.coords), "meta": dict(st.meta)}


def step_to_obj(s: Step) -> Dict[str, Any]:
    if not isinstance(s.id, str) or not s.id:
        raise ValueError("Step.id must be non-empty string")
    if isinstance(s.action, bool) or not isinstance(s.action, int):
        raise TypeError("Step.action must be int")
    _assert_jsonable(s.witness, "Step.witness")
    return {"id": s.id, "delta": state_to_obj(s.delta), "action": int(s.action), "witness": dict(s.witness)}


def execution_to_obj(E: Execution) -> Dict[str, Any]:
    _assert_jsonable(E.claims, "Execution.claims")
    return {
        "spec": "XKERNEL_INVARIANTS_kK_SPEC_V1",
        "version": "1.0.0-draft",
        "execution": {
            "init": state_to_obj(E.init),
            "steps": [step_to_obj(s) for s in E.steps],
            "final": state_to_obj(E.final),
            "claims": dict(E.claims),
        },
    }


def canonical_json_bytes(E: Execution) -> bytes:
    obj = execution_to_obj(E)
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")
