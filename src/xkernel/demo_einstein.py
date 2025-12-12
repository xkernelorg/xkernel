from __future__ import annotations

"""
demo_einstein.py
----------------

Engine-driven demo for the xkernel Einstein lens.

Pipeline:
    XKernel (XState history)
        → wave_from_states (wave lens)
        → lens_einstein (curvature / strain / energy)
        → ascii_wave (ASCII oscilloscope projection)
"""

from xkernel import XKernel, XKernelConfig, seed_impulse
from xkernel.lens_wave import WaveHistory, WaveSample, wave_from_states, ascii_wave
from xkernel.lens_einstein import lens_einstein


def make_wave_from_array(values, label: str) -> WaveHistory:
    """Wrap a 1-D array into a WaveHistory so ascii_wave can render it."""
    samples = [WaveSample(tick=i, value=float(v)) for i, v in enumerate(values)]
    return WaveHistory(
        samples=samples,
        meta={"lens": "einstein", "component": label},
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

    print("=== ENGINE-DRIVEN WAVE LENS ===")
    print(f"size={size}, dim={dim}, eta={eta}, site={site}, component={component}")
    print(ascii_wave(wave, height=ascii_height, width=ascii_width))

    # 4) Einstein lens
    res = lens_einstein(wave)
    print()
    print("EinsteinResult:")
    print(f"  samples = {len(res.curvature)}")
    print()

    # 5) Project curvature / strain / energy as separate waves
    curv_wave = make_wave_from_array(res.curvature, "curvature")
    strain_wave = make_wave_from_array(res.strain, "strain")
    energy_wave = make_wave_from_array(res.energy, "energy")

    print("=== CURVATURE PROJECTION ===")
    print(ascii_wave(curv_wave, height=ascii_height, width=ascii_width))
    print()

    print("=== STRAIN PROJECTION ===")
    print(ascii_wave(strain_wave, height=ascii_height, width=ascii_width))
    print()

    print("=== ENERGY PROJECTION ===")
    print(ascii_wave(energy_wave, height=ascii_height, width=ascii_width))
    print()


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
