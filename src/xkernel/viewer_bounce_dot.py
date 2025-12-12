# src/xkernel/viewer_bounce_dot.py
import argparse
import time


def simulate(points: int, steps: int, sleep: float,
             single_line: bool, restitution: float, speed: float) -> None:

    x = (points - 1) / 2.0
    v = speed

    for step in range(steps):
        x += v

        if x <= 0.0:
            x = -x
            v = -restitution * v
        elif x >= points - 1:
            x = 2 * (points - 1) - x
            v = -restitution * v

        idx = int(round(x))
        idx = max(0, min(points - 1, idx))

        chars = ["." for _ in range(points)]
        chars[idx] = "@"
        line = "|" + "".join(chars) + "|"

        if single_line:
            print("\033[2J\033[H", end="")  # Clear + move home
            print(
                f"step: {step:04d}   x={x:6.2f}   v={v:6.2f}   e={restitution:.2f}"
            )
            print()
            print(line, end="", flush=True)
        else:
            print(
                f"{step:04d} x={x:6.2f} v={v:6.2f} e={restitution:.2f} {line}"
            )

        time.sleep(sleep)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bouncing dot with restitution")
    parser.add_argument("--points", type=int, default=24)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--sleep", type=float, default=0.03)
    parser.add_argument("--single-line", action="store_true")
    parser.add_argument("--restitution", type=float, default=1.0)
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()

    simulate(
        points=args.points,
        steps=args.steps,
        sleep=args.sleep,
        single_line=args.single_line,
        restitution=args.restitution,
        speed=args.speed,
    )


if __name__ == "__main__":
    main()
