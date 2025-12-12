from __future__ import annotations

"""
demo_shannon.py
---------------

Engine-driven demo for the xkernel Shannon lens.

Pipeline:
    XKernel (XState history)
        → wave_from_states (wave lens)
        → lens_shannon (information metrics)
        → ascii_wave (ASCII oscilloscope projections)
"""

from xkernel import XKernel, XKernelConfig, seed_impulse
from xkernel.lens_wave import WaveHistory, WaveSample, wave_from_states, ascii_wave
from xkernel.lens_shannon import lens_shannon


def make_wave_from_array(values, label: str) -> WaveHistory:
    """Wrap a 1-D array into a WaveHistory so ascii_wave can render it."""
    samples = [WaveSample(tick=i, value=float(v)) for i, v in enumerate(values)]
    return WaveHistory(
        samples=samples,
        meta={"lens": "shannon", "component": label},
    )


def run_demo(
    *,
    size: int = 16,
    dim: int = 6,
    eta: float = 0.1,
    site: int = 3,
    component: int = 0,
    steps: int = 128,
    ascii_height: int = 12,
    ascii_width: int = 64,
) -> None:
    # 1) Build engine + initial condition
    cfg = XKernelConfig(size=size, dim=dim, eta=eta)
    initial = seed_impulse(cfg, index=site, component=component, amplitude=1.0)
    kernel = XKernel(cfg)

    # 2) Generate XState history
    states = list(kernel.run(initial, steps=steps))

    # 3) Wave lens: pick one (site, component) track
    wave = wave_from_states(
        states,
        site=site,
        component=component,
        normalize=True,
    )

    print("=== ENGINE-DRIVEN WAVE LENS (Shannon demo) ===")
    print(f"size={size}, dim={dim}, eta={eta}, site={site}, component={component}")
    print(ascii_wave(wave, height=ascii_height, width=ascii_width))

    # 4) Shannon lens
    res = lens_shannon(wave)
    print()
    print("ShannonResult:")
    attrs = [a for a in dir(res) if not a.startswith("_")]
    print("  fields:", ", ".join(attrs))
    print()

    # 5) Only plot list/tuple-valued fields (skip scalar entropy)
    series: list[tuple[str, list[float]]] = []

    for name in ("entropy_series", "probability"):
        if hasattr(res, name):
            val = getattr(res, name)
            if isinstance(val, (list, tuple)) and len(val) > 1:
                # ensure numeric
                try:
                    float(val[0])
                    series.append((name, val))
                except (TypeError, ValueError):
                    pass

    if not series:
        print("No numeric series found to project.")
        return

    # 6) Project each series as an ASCII wave
    for label, values in series:
        wave_proj = make_wave_from_array(values, label)
        print(f"=== {label.upper()} PROJECTION ===")
        print(ascii_wave(wave_proj, height=ascii_height, width=ascii_width))
        print()


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
