from __future__ import annotations

import argparse
from importlib import metadata
from typing import Sequence

from . import (
    lens_einstein,
    lens_shannon,
    lens_wave,
    lens_schrodinger,
    viewer_bounce_dot,
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _call_lens_module(label: str) -> None:
    """Dispatch to the appropriate lens module.

    We keep this very lightweight and only rely on a conventional
    `main()` or `run()` function if present. That way the lenses remain
    self-contained and the CLI does not impose a heavy API.
    """
    module_map = {
        "einstein": lens_einstein,
        "shannon": lens_shannon,
        "wave": lens_wave,
        "schrodinger": lens_schrodinger,
    }

    mod = module_map[label]

    if hasattr(mod, "main") and callable(mod.main):  # type: ignore[attr-defined]
        mod.main()  # type: ignore[call-arg]
    elif hasattr(mod, "run") and callable(mod.run):  # type: ignore[attr-defined]
        mod.run()  # type: ignore[call-arg]
    else:
        print(
            f"[xkernel] Imported lens '{label}' ({mod.__name__}), "
            "but no main()/run() function is defined."
        )


def _run_bounce_dot_viewer(
    points: int,
    steps: int,
    sleep: float,
    single_line: bool,
    restitution: float,
    speed: float,
) -> None:
    """Run the bounce-dot viewer with the given parameters."""
    viewer_bounce_dot.simulate(
        points=points,
        steps=steps,
        sleep=sleep,
        single_line=single_line,
        restitution=restitution,
        speed=speed,
    )


# ---------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="xkernel",
        description="xkernel command-line interface (lenses + viewers).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- lens subcommand -------------------------------------------------
    lens_parser = subparsers.add_parser("lens", help="run a lens")
    lens_parser.add_argument(
        "name",
        choices=["einstein", "shannon", "wave", "schrodinger"],
        help="which lens to run",
    )

    # ---- viewer subcommand -----------------------------------------------
    viewer_parser = subparsers.add_parser("viewer", help="run a viewer")
    viewer_parser.add_argument(
        "name",
        choices=["bounce-dot"],
        help="which viewer to run",
    )
    viewer_parser.add_argument(
        "--points",
        type=int,
        default=40,
        help="number of positions in the 1D track (default: 40)",
    )
    viewer_parser.add_argument(
        "--steps",
        type=int,
        default=1000,
        help="number of simulation steps (default: 1000)",
    )
    viewer_parser.add_argument(
        "--sleep",
        type=float,
        default=0.02,
        help="sleep time between frames in seconds (default: 0.02)",
    )
    viewer_parser.add_argument(
        "--single-line",
        action="store_true",
        help="render in single-line mode (no scrolling)",
    )
    viewer_parser.add_argument(
        "--restitution",
        type=float,
        default=0.9,
        help="bounce restitution coefficient (default: 0.9)",
    )
    viewer_parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="initial speed of the dot (default: 1.0)",
    )

    # ---- version subcommand ----------------------------------------------
    subparsers.add_parser("version", help="show version information")

    args = parser.parse_args(argv)

    if args.command == "lens":
        _call_lens_module(args.name)

    elif args.command == "viewer":
        # currently only "bounce-dot", but the structure allows more viewers later
        if args.name == "bounce-dot":
            _run_bounce_dot_viewer(
                points=args.points,
                steps=args.steps,
                sleep=args.sleep,
                single_line=args.single_line,
                restitution=args.restitution,
                speed=args.speed,
            )
        else:
            parser.error(f"Unknown viewer '{args.name}'")

    elif args.command == "version":
        try:
            v = metadata.version("xkernel")
        except metadata.PackageNotFoundError:
            v = "unknown (not installed as a package)"
        print(f"xkernel {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
