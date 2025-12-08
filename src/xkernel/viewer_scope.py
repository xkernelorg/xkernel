import argparse
import math
import sys
import time
from typing import List

RAMP = " .:-=+*#%@"

def level_to_char(v: float) -> str:
    if v <= 0.0:
        return " "
    if v >= 1.0:
        return RAMP[-1]
    idx = int(v * (len(RAMP) - 1) + 0.5)
    if idx < 0:
        idx = 0
    elif idx >= len(RAMP):
        idx = len(RAMP) - 1
    return RAMP[idx]


def parse_size(size: str) -> tuple[int, int]:
    try:
        w_s, h_s = size.lower().split("x")
        return int(w_s), int(h_s)
    except Exception:
        return 60, 20


def sample_wave(angle: float, mode: str) -> float:
    if mode == "sine":
        return math.sin(angle)
    if mode == "square":
        return 1.0 if math.sin(angle) >= 0.0 else -1.0
    if mode == "triangle":
        return 2.0 / math.pi * math.asin(math.sin(angle))
    if mode == "saw":
        a = (angle + math.pi) % (2.0 * math.pi) - math.pi
        return a / math.pi
    return math.sin(angle)


def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def map_amp_to_row(val: float, height: int) -> int:
    val = clamp(val, -1.0, 1.0)
    mid = height // 2
    amp = max(1.0, (height - 2) * 0.5)
    y = int(round(mid - val * amp))
    if y < 0:
        y = 0
    elif y >= height:
        y = height - 1
    return y


def make_buffer(width: int, height: int) -> List[List[float]]:
    return [[0.0 for _ in range(width)] for _ in range(height)]


def decay_buffer(buf: List[List[float]], pers: float) -> None:
    if pers <= 0.0:
        for y in range(len(buf)):
            row = buf[y]
            for x in range(len(row)):
                row[x] = 0.0
        return
    factor = clamp(pers, 0.01, 0.99)
    for y in range(len(buf)):
        row = buf[y]
        for x in range(len(row)):
            row[x] *= factor


def draw_time_scope(args: argparse.Namespace) -> None:
    width, height = parse_size(args.size)
    buf = make_buffer(width, height)
    phase = 0.0
    step = 0
    freq = args.freq
    freq2 = args.freq2
    mode = args.mode
    baseline_row = map_amp_to_row(args.off, height)

    try:
        while True:
            step += 1
            if args.trig == "free":
                phase += 2.0 * math.pi * freq * args.speed
            elif args.trig == "roll":
                phase += 2.0 * math.pi * freq * args.speed * 0.3
            else:
                phase = 0.0

            phase = math.fmod(phase, 2.0 * math.pi)

            decay_buffer(buf, args.pers)

            w_den = float(max(1, width - 1))
            for x in range(width):
                frac = x / w_den
                angle = phase + 2.0 * math.pi * freq * frac
                v1 = args.gain * sample_wave(angle, mode) + args.off
                y1 = map_amp_to_row(v1, height)
                buf[y1][x] = 1.0

                if freq2 > 0.0:
                    angle2 = phase * (freq2 / freq if freq != 0.0 else 1.0) + 2.0 * math.pi * freq2 * frac + args.phase2
                    v2 = args.gain2 * sample_wave(angle2, mode) + args.off2
                    y2 = map_amp_to_row(v2, height)
                    buf[y2][x] = 1.0

            sys.stdout.write("\x1b[H\x1b[2J")
            header = (
                f"toy-scope  mode={mode}  freq={freq:.2f}"
                f"  speed={args.speed:.2f}  size={width}x{height}"
                f"  gain={args.gain:.2f}  off={args.off:.2f}"
                f"  trig={args.trig}  pers={args.pers:.2f}"
                f"  step={step:04d}"
            )
            if freq2 > 0.0:
                header += f"\nch2: freq2={freq2:.2f} gain2={args.gain2:.2f} off2={args.off2:.2f} phase2={args.phase2:.2f}"
            sys.stdout.write(header + "\n\n")

            for y in range(height):
                row_vals = buf[y]
                line_chars = []
                for x in range(width):
                    ch = level_to_char(row_vals[x])
                    if ch == " ":
                        ch = "."
                    line_chars.append(ch)

                if y == baseline_row:
                    for x in range(0, width, 2):
                        if line_chars[x] == ".":
                            line_chars[x] = "-"
                sys.stdout.write("".join(line_chars) + "\n")

            sys.stdout.flush()
            time.sleep(args.speed)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        sys.stdout.flush()


def draw_lissajous(args: argparse.Namespace) -> None:
    width, height = parse_size(args.size)
    buf = make_buffer(width, height)
    phase = 0.0
    step = 0
    freq_x = args.freq
    freq_y = args.liss_ratio * args.freq

    try:
        while True:
            step += 1
            decay_buffer(buf, args.pers)

            points = max(width * 4, 200)
            for i in range(points):
                t = phase + 2.0 * math.pi * i / points
                x_val = math.sin(2.0 * math.pi * freq_x * t)
                y_val = math.sin(2.0 * math.pi * freq_y * t + args.liss_phase)
                x = int(round((x_val + 1.0) * 0.5 * (width - 1)))
                y = int(round((1.0 - (y_val + 1.0) * 0.5) * (height - 1)))
                buf[y][x] = 1.0

            sys.stdout.write("\x1b[H\x1b[2J")
            header = (
                f"toy-scope  mode=lissajous  fx={freq_x:.2f}  fy={freq_y:.2f}"
                f"  ratio={args.liss_ratio:.2f}  speed={args.speed:.2f}"
                f"  size={width}x{height}  pers={args.pers:.2f}  step={step:04d}"
            )
            sys.stdout.write(header + "\n\n")

            for y in range(height):
                row_vals = buf[y]
                line_chars = []
                for x in range(width):
                    ch = level_to_char(row_vals[x])
                    if ch == " ":
                        ch = "."
                    line_chars.append(ch)
                sys.stdout.write("".join(line_chars) + "\n")

            sys.stdout.flush()
            phase += args.speed
            phase = math.fmod(phase, 2.0 * math.pi)
            time.sleep(args.speed)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        sys.stdout.flush()


def main() -> None:
    parser = argparse.ArgumentParser(prog="xkernel.viewer_scope", description="ASCII toy oscilloscope")
    parser.add_argument("--mode", choices=["sine", "square", "triangle", "saw", "lissajous"], default="sine")
    parser.add_argument("--freq", type=float, default=3.0)
    parser.add_argument("--freq2", type=float, default=0.0)
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--off", type=float, default=0.0)
    parser.add_argument("--gain2", type=float, default=1.0)
    parser.add_argument("--off2", type=float, default=0.0)
    parser.add_argument("--phase2", type=float, default=0.0)
    parser.add_argument("--speed", type=float, default=0.08)
    parser.add_argument("--size", type=str, default="60x20")
    parser.add_argument("--trig", choices=["free", "lock", "roll"], default="free")
    parser.add_argument("--pers", type=float, default=0.0)
    parser.add_argument("--liss-ratio", type=float, default=2.0)
    parser.add_argument("--liss-phase", type=float, default=math.pi / 2.0)

    args = parser.parse_args()

    if args.mode == "lissajous":
        draw_lissajous(args)
    else:
        draw_time_scope(args)


if __name__ == "__main__":
    main()
