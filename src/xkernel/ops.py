from __future__ import annotations

from typing import List

from .kinds import Execution, StateVector, Step, Verdict

K_STEP_QUANTUM: int = 1  # ¤[k] := 1


def admissible_step(s: Step) -> bool:
    return s.action == K_STEP_QUANTUM


def _add_coords(a: List[int], b: List[int]) -> List[int]:
    if len(a) != len(b):
        raise ValueError(f"Dimension mismatch: {len(a)} != {len(b)}")
    return [a[i] + b[i] for i in range(len(a))]


def apply_step(st: StateVector, s: Step) -> StateVector:
    new_coords = _add_coords(st.coords, s.delta.coords)
    return StateVector(coords=new_coords, meta=dict(st.meta))


def validate_execution(E: Execution) -> Verdict:
    for idx, s in enumerate(E.steps):
        if not admissible_step(s):
            return Verdict(
                ok=False,
                reason="NON_ADMISSIBLE_STEP",
                details={"index": idx, "step_id": s.id, "action": s.action, "expected": K_STEP_QUANTUM},
            )

    st = E.init
    try:
        for s in E.steps:
            st = apply_step(st, s)
    except Exception as ex:
        return Verdict(ok=False, reason="REPLAY_ERROR", details={"error": str(ex)})

    if st.coords != E.final.coords:
        return Verdict(ok=False, reason="REPLAY_MISMATCH", details={"computed": st.coords, "declared": E.final.coords})

    return Verdict(ok=True, reason="OK", details={})


def closed(E: Execution, target: StateVector) -> bool:
    v = validate_execution(E)
    if not v.ok:
        return False
    return E.final.coords == target.coords
