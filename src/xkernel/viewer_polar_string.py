from __future__ import annotations

import argparse
import math
import time
from typing import List


ASCII_RAMP = " .:-=+*#%@"  # low → high amplitude


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m xkernel.viewer_polar_string",
        description="ASCII vibrating circular string (polar coordinates semantic)",
    )
    p.add_argument(
        "--points",
        type=int,
        default=64,
        help="Number of points on the string (lattice size)",
    )
    p.add_argument(
        "--steps",
        type=int,
        default=120,
        help="Number of time steps to simulate",
    )
    p.add_argument(
        "--c2",
        type=float,
        default=0.1,
        help="Wave speed squared (stability requires c2 <= 1.0)",
    )
    p.add_argument(
        "--impulse-index",
        type=int,
        default=None,
        help="Index to seed an initial impulse (default: center of ring)",
    )
    p.add_argument(
        "--mode",
        type=str,
        choices=["impulse", "sine"],
        default="impulse",
        help="Initial condition: impulse or single sine mode",
    )
    p.add_argument(
        "--sine-mode",
        type=int,
        default=1,
        help="Mode number for sine initial condition (mode k around the ring)",
    )
    p.add_argument(
        "--pause",
        type=float,
        default=0.0,
        help="Optional pause in seconds between frames (0 = no delay)",
    )
    return p


def seed_initial(
    n: int,
    mode: str,
    impulse_index: int | None,
    sine_mode: int,
) -> List[float]:
    """Initial displacement u(t=0, i). Velocity is zero (u_prev = u_curr)."""
    u = [0.0] * n

    if mode == "impulse":
        idx = impulse_index if impulse_index is not None else n // 2
        idx %= n
        u[idx] = 1.0
        return u

    # Sine mode on a ring: u[i] = sin(k * phi_i), phi_i = 2π i / n
    k = max(1, sine_mode)
    for i in range(n):
        phi = 2.0 * math.pi * i / n
        u[i] = math.sin(k * phi)
    return u


def step_wave_periodic(u_prev: List[float], u_cur: List[float], c2: float) -> List[float]:
    """One time step of the 1D wave equation on a ring.

    u_next[i] = 2 u_cur[i] - u_prev[i] + c2 * (u_cur[i-1] - 2 u_cur[i] + u_cur[i+1])
    with periodic boundaries: index -1 → n-1, n → 0.
    """
    n = len(u_cur)
    u_next = [0.0] * n
    for i in range(n):
        left = u_cur[i - 1] if i > 0 else u_cur[n - 1]
        right = u_cur[i + 1] if i + 1 < n else u_cur[0]
        lap = left - 2.0 * u_cur[i] + right
        u_next[i] = 2.0 * u_cur[i] - u_prev[i] + c2 * lap
    return u_next


def value_to_char(x: float) -> str:
    """Map amplitude to an ASCII character."""
    # Symmetric around zero, clamp to [-1, 1]
    a = max(-1.0, min(1.0, x))
    a = abs(a)
    idx = int(a * (len(ASCII_RAMP) - 1) + 1e-9)
    return ASCII_RAMP[idx]


def render_frame(step: int, u: List[float]) -> str:
    """Return one line of ASCII for the current frame."""
    chars = "".join(value_to_char(v) for v in u)
    return f"{step:04d}  {chars}"


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)

    n = args.points
    steps = args.steps
    c2 = args.c2

    # --- polar semantics (not needed numerically, but good to keep explicit)
    # phi[i] = 2π i / n
    # radial displacement r[i](t) = 1 + u[i](t)

    u_cur = seed_initial(n, args.mode, args.impulse_index, args.sine_mode)
    u_prev = u_cur[:]  # zero initial velocity

    for t in range(steps):
        line = render_frame(t, u_cur)
        print(line)
        u_next = step_wave_periodic(u_prev, u_cur, c2)
        u_prev, u_cur = u_cur, u_next

        if args.pause > 0.0:
            time.sleep(args.pause)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
