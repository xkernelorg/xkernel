# src/xkernel/viewer_scope.py
import argparse
import math
import os
import time

MODES = ("sine", "square", "triangle")


def sample_wave(mode: str, t: float, freq: float) -> float:
    phase = 2.0 * math.pi * freq * t
    s = math.sin(phase)
    if mode == "sine":
        return s
    if mode == "square":
        return 1.0 if s >= 0.0 else -1.0
    if mode == "triangle":
        # nice symmetric triangle in [-1, 1]
        return 2.0 / math.pi * math.asin(s)
    return 0.0


def build_frame(
    samples,
    width: int,
    height: int,
    persistence: int,
    history,
    use_grid: bool,
) -> list[str]:
    mid = height // 2
    amp_rows = max(1, height // 2 - 2)

    # base background
    frame = [["." for _ in range(width)] for _ in range(height)]

    # optional grid
    if use_grid:
        x_spacing = max(4, width // 8)
        for x in range(0, width, x_spacing):
            for y in range(height):
                frame[y][x] = "|"

    # center reference line
    for x in range(width):
        if use_grid and frame[mid][x] == "|":
            frame[mid][x] = "+"
        else:
            if x % 2 == 0:
                frame[mid][x] = "-"

    # decay persistence
    if history is not None:
        for y in range(height):
            row = history[y]
            for x in range(width):
                if row[x] > 0:
                    row[x] -= 1

    # draw current samples
    for x, y in enumerate(samples):
        # map y in [-1, 1] to row index
        y_clamped = max(-1.0, min(1.0, y))
        row = mid - int(round(y_clamped * amp_rows))
        row = max(0, min(height - 1, row))
        if history is not None:
            history[row][x] = persistence
        else:
            frame[row][x] = "*"

    # overlay persistence as stars
    if history is not None:
        for y in range(height):
            for x in range(width):
                if history[y][x] > 0:
                    frame[y][x] = "*"

    return ["".join(line) for line in frame]


def main() -> None:
    parser = argparse.ArgumentParser(description="ASCII toy oscilloscope")
    parser.add_argument("--mode", choices=MODES, default="sine")
    parser.add_argument("--freq", type=float, default=2.0)
    parser.add_argument("--speed", type=float, default=0.10)
    parser.add_argument("--width", type=int, default=40)
    parser.add_argument("--height", type=int, default=20)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--offset", type=float, default=0.0)
    parser.add_argument("--persistence", type=int, default=0)
    parser.add_argument("--grid", action="store_true")
    parser.add_argument(
        "--trigger",
        type=float,
        default=None,
        help="trigger level in [-1, 1] (rising edge); omit for free run",
    )
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument(
        "--steps",
        type=int,
        default=0,
        help="number of frames (0 = run forever)",
    )

    args = parser.parse_args()

    width = max(10, args.width)
    height = max(5, args.height)
    persistence = max(0, args.persistence)
    history = (
        [[0 for _ in range(width)] for _ in range(height)]
        if persistence > 0
        else None
    )

    t0 = 0.0
    dt = 1.0 / width
    step = 0

    while True:
        # generate more samples than needed when triggering so we can slide
        horizon = width * 3 if args.trigger is not None else width
        raw = [
            sample_wave(args.mode, t0 + i * dt, args.freq)
            for i in range(horizon)
        ]

        # apply gain + offset and clamp
        scaled = [
            max(-1.0, min(1.0, args.gain * y + args.offset)) for y in raw
        ]

        # simple rising-edge trigger
        if args.trigger is not None:
            level = args.trigger
            idx = None
            for i in range(1, len(scaled)):
                if scaled[i - 1] < level <= scaled[i]:
                    idx = i
                    break
            if idx is None:
                window = scaled[:width]
            else:
                if idx + width >= len(scaled):
                    idx = len(scaled) - width
                window = scaled[idx : idx + width]
        else:
            window = scaled[:width]

        lines = build_frame(
            window,
            width=width,
            height=height,
            persistence=persistence,
            history=history,
            use_grid=bool(args.grid),
        )

        os.system("clear")
        header = (
            f"toy-scope  mode={args.mode}"
            f"  freq={args.freq:.2f}"
            f"  speed={args.speed:.2f}"
            f"  size={width}x{height}"
            f"  gain={args.gain:.2f}"
            f"  off={args.offset:.2f}"
            f"  trig={args.trigger if args.trigger is not None else 'free'}"
            f"  pers={persistence}"
            f"  step={step:04d}"
        )
        print(header)
        for line in lines:
            print(line)

        step += 1
        if args.steps and step >= args.steps:
            break

        # advance time base
        t0 += args.speed * dt
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
