from __future__ import annotations

import argparse
import time
from typing import Sequence

from xkernel import XKernelConfig, XKernel, seed_impulse, seed_zero


CHARS = " .:-=+*#%@"
# index 0 → space (near zero), last char → largest magnitude


def render_line(field: Sequence[Sequence[float]], component: int = 0) -> str:
    """Render one component of the 1-D field as an ASCII line."""
    values = [cell[component] for cell in field]
    max_abs = max((abs(v) for v in values), default=1.0)
    if max_abs == 0:
        max_abs = 1.0

    line_chars = []
    for v in values:
        norm = abs(v) / max_abs  # 0..1
        idx = int(norm * (len(CHARS) - 1))
        line_chars.append(CHARS[idx])
    return "".join(line_chars)


def run_viewer(
    size: int,
    dim: int,
    eta: float,
    steps: int,
    component: int,
    impulse_index: int | None,
    impulse_component: int,
    impulse_amplitude: float,
    delay: float,
) -> None:
    cfg = XKernelConfig(size=size, dim=dim, eta=eta)
    kernel = XKernel(cfg)

    if impulse_index is None:
        state0 = seed_zero(cfg)
    else:
        state0 = seed_impulse(
            cfg,
            index=impulse_index,
            component=impulse_component,
            amplitude=impulse_amplitude,
        )

    for state in kernel.run(state0, steps=steps):
        line = render_line(state.field, component=component)
        print(f"{state.step:04d} {line}")
        if delay > 0:
            time.sleep(delay)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="xkernel-view-1d",
        description="ASCII 1D viewer for the X-field (X ∈ R^6)",
    )
    p.add_argument("--size", type=int, default=64, help="Number of cells in the field")
    p.add_argument("--dim", type=int, default=6, help="Dimension of each X-vector")
    p.add_argument("--eta", type=float, default=0.1, help="Timestep / coupling scale")
    p.add_argument("--steps", type=int, default=64, help="Number of steps to simulate")
    p.add_argument(
        "--component",
        type=int,
        default=0,
        help="Which component of X to visualize (0-based index)",
    )
    p.add_argument(
        "--impulse-index",
        type=int,
        default=32,
        help="Cell index for initial impulse (use -1 for no impulse)",
    )
    p.add_argument(
        "--impulse-component",
        type=int,
        default=0,
        help="Component index for the impulse",
    )
    p.add_argument(
        "--impulse-amplitude",
        type=float,
        default=1.0,
        help="Amplitude of the initial impulse",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=0.02,
        help="Delay (seconds) between frames; 0 for fastest",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    impulse_idx = None if args.impulse_index < 0 else args.impulse_index

    run_viewer(
        size=args.size,
        dim=args.dim,
        eta=args.eta,
        steps=args.steps,
        component=args.component,
        impulse_index=impulse_idx,
        impulse_component=args.impulse_component,
        impulse_amplitude=args.impulse_amplitude,
        delay=args.delay,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
