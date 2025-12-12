from __future__ import annotations

"""
demo_schrodinger.py
-------------------

Engine-driven demo for the xkernel Schrödinger lens.

Pipeline:
    XKernel (XState history)
        → wave_from_states (wave lens)
        → lens_schrodinger (complex amplitude / phase, etc.)
        → ascii_wave (ASCII oscilloscope projection)
"""

from xkernel import XKernel, XKernelConfig, seed_impulse
from xkernel.lens_wave import WaveHistory, WaveSample, wave_from_states, ascii_wave
from xkernel.lens_schrodinger import lens_schrodinger


def make_wave_from_array(values, label: str) -> WaveHistory:
    """Wrap a 1-D array into a WaveHistory so ascii_wave can render it."""
    samples = [WaveSample(tick=i, value=float(v)) for i, v in enumerate(values)]
    return WaveHistory(
        samples=samples,
        meta={"lens": "schrodinger", "component": label},
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

    print("=== ENGINE-DRIVEN WAVE LENS (Schrödinger demo) ===")
    print(f"size={size}, dim={dim}, eta={eta}, site={site}, component={component}")
    print(ascii_wave(wave, height=ascii_height, width=ascii_width))

    # 4) Schrödinger lens
    res = lens_schrodinger(wave)
    print()
    print("SchrodingerResult:")
    # Adjust these fields to whatever your actual result object exposes
    # (e.g. amplitude, phase, real, imag)
    try:
        n = len(res.amplitude)
    except AttributeError:
        # Fallback if the API is slightly different
        n = len(getattr(res, "values", []))
    print(f"  samples = {n}")
    print()

    # 5) Project amplitude / phase / real / imag as separate waves
    # These attribute names are a reasonable guess; tweak if your API differs.
    series = []

    if hasattr(res, "amplitude"):
        series.append(("amplitude", res.amplitude))
    if hasattr(res, "phase"):
        series.append(("phase", res.phase))
    if hasattr(res, "real"):
        series.append(("real", res.real))
    if hasattr(res, "imag"):
        series.append(("imag", res.imag))

    for label, values in series:
        wave_proj = make_wave_from_array(values, label)
        print(f"=== {label.upper()} PROJECTION ===")
        print(ascii_wave(wave_proj, height=ascii_height, width=ascii_width))
        print()


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
