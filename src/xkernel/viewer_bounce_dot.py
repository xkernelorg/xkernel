# src/xkernel/viewer_bounce_dot.py
import argparse
import sys
import time


def frame(pos: int, n: int) -> str:
    chars = ['.'] * n
    chars[pos] = '@'
    return "|" + "".join(chars) + "|"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--points", type=int, default=16)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--sleep", type=float, default=0.03)
    parser.add_argument("--single-line", action="store_true")
    args = parser.parse_args()

    pos = 0
    direction = 1

    # Clear screen and print initial layout
    if args.single_line:
        sys.stdout.write("\033[2J\033[H")  # clear screen + move to home
        sys.stdout.write("step: 0000\n")
        sys.stdout.write("\n")
        sys.stdout.write(frame(pos, args.points) + "\n")
        sys.stdout.flush()

    for step in range(args.steps):
        line = frame(pos, args.points)

        if args.single_line:
            # Move cursor to top of screen (home)
            sys.stdout.write("\033[H")
            sys.stdout.write(f"step: {step:04d}\n")
            sys.stdout.write("\n")
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"{step:04d} {line}\n")
            sys.stdout.flush()

        time.sleep(args.sleep)

        pos += direction
        if pos <= 0:
            pos = 0
            direction = 1
        elif pos >= args.points - 1:
            pos = args.points - 1
            direction = -1


if __name__ == "__main__":
    main()
