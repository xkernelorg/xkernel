from __future__ import annotations

import argparse
import sys
import time
import shutil
import numpy as np

CHARS = " .:-=+*#%@"

def step_wave(u, u_prev, c2):
    u_next = np.empty_like(u)
    u_next[0] = 0.0
    u_next[-1] = 0.0
    lap = u[:-2] - 2.0 * u[1:-1] + u[2:]
    u_next[1:-1] = 2.0 * u[1:-1] - u_prev[1:-1] + c2 * lap
    return u_next

def amplitudes_to_line(u, width):
    n = u.shape[0]
    if n > width:
        idx = np.linspace(0, n - 1, width).astype(int)
        vals = u[idx]
    else:
        vals = np.interp(
            np.linspace(0, n - 1, width),
            np.arange(n),
            u,
        )
    vals = np.clip(vals, -1.0, 1.0)
    mags = np.abs(vals)
    buckets = (mags * (len(CHARS) - 1)).astype(int)
    chars = [CHARS[b] for b in buckets]
    return "".join(chars)

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--points", type=int, default=128)
    p.add_argument("--steps", type=int, default=400)
    p.add_argument("--c", type=float, default=0.25)
    p.add_argument("--dt", type=float, default=0.1)
    p.add_argument("--sleep", type=float, default=0.03)
    args = p.parse_args(argv)

    n = args.points
    c2 = (args.c * args.dt) ** 2

    u = np.zeros(n, dtype=float)
    u_prev = np.zeros_like(u)
    center = n // 2
    u[center] = 1.0
    u_prev[:] = u

    width = shutil.get_terminal_size((80, 20)).columns

    for _ in range(args.steps):
        line = amplitudes_to_line(u, width)
        sys.stdout.write("\r" + line)
        sys.stdout.flush()
        time.sleep(args.sleep)
        u_next = step_wave(u, u_prev, c2)
        u_prev, u = u, u_next

    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
