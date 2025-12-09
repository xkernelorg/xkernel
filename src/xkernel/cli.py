from __future__ import annotations

import argparse
from .engine import XEngine, ExtrusionSpec


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="xkernel",
        description="Minimal deterministic xkernel engine",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run a simple demo extrusion")
    demo.add_argument("--fibers", type=int, default=1, help="Number of fibers")
    demo.add_argument(
        "--filaments",
        type=int,
        default=1,
        help="Number of filaments per fiber",
    )
    demo.add_argument(
        "--steps",
        type=int,
        default=16,
        help="Steps per filament",
    )
    demo.add_argument(
        "--dim",
        type=int,
        default=4,
        help="State dimension",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    if args.command == "demo":
        engine = XEngine()
        spec = ExtrusionSpec(
            fibers=args.fibers,
            filaments_per_fiber=args.filaments,
            steps=args.steps,
            dimension=args.dim,
        )
        bundle = engine.extrude(spec)

        print(bundle.summary())


if __name__ == "__main__":
    main()
