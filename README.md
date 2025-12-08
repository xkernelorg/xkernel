# 🌀 xkernel
### Minimal Deterministic X-Field Engine with Lens Architecture  
Version: 0.1.0  
Engine: `XKernel`

---

## Overview

**xkernel** is a lightweight, deterministic computational engine for evolving
1-D lattices of real-valued vectors.  
Each lattice site holds an **X-vector** in ℝ⁶ (configurable), and each timestep
applies a strictly local, strictly deterministic update rule of the form:

\[
X_i(t+1) = X_i(t) \, + \, \eta \left( 
A\,X_i(t) \, + \, B\,[X_{i-1}(t) + X_{i+1}(t)]
\right)
\]

- Completely deterministic  
- Pure Python, zero dependencies  
- Full state export to JSON  
- Extensible **lens system** (waveforms, geometric views, etc.)  
- Clean, stable API suitable for embedding in larger systems  
- Used as a computational substrate for EuMech, DAT, GTORC, and waveform viewers

---

## Project Structure

```
xkernel/
├── README.md
├── pyproject.toml
├── src/
│   └── xkernel/
│       ├── __init__.py          # clean public API
│       ├── xkernel.py           # core engine
│       ├── lens_wave.py         # waveform lens (sine/square/triangle/saw)
│       └── viewer_bounce_dot.py # simple ASCII bounce visualization
└── tests/
    └── test_xkernel_basic.py    # basic engine tests
```

---

## Installation

Editable install (recommended for development):

```bash
pip install -e .
```

Verify:

```bash
python -c "from xkernel import XKernelConfig; print(XKernelConfig())"
```

---

## Core API

### Create a configuration

```python
from xkernel import XKernelConfig

cfg = XKernelConfig(size=64, dim=6, eta=0.1)
```

### Seed an initial state

```python
from xkernel import seed_zero, seed_impulse

initial = seed_impulse(cfg, index=3, component=0, amplitude=1.0)
```

### Run the engine

```python
from xkernel import XKernel

kernel = XKernel(cfg)
states = list(kernel.run(initial, steps=128))
```

### Export a trace to JSON (for viewers / logs)

```python
from xkernel import trace_to_dict

trace = trace_to_dict(states)
```

---

## Waveform Lens (`lens_wave.py`)

The wave lens interprets a 1-D X-kernel evolution as a **time-indexed waveform**.

Extract a waveform from a given site/component:

```python
from xkernel import wave_from_states, ascii_wave

wave = wave_from_states(states, site=3, component=0, normalize=True)
print(ascii_wave(wave, height=10))
```

Generate analytic waveforms:

```python
from xkernel import analytic_wave

sq = analytic_wave("square", steps=64, amplitude=1.0, frequency=2.0)
print(ascii_wave(sq, height=12))
```

Supported analytic wave types:
- `"sine"`
- `"square"`
- `"triangle"`
- `"saw"`

---

## Viewer Example (`viewer_bounce_dot.py`)

Run an ASCII bounce-dot simulation:

```bash
python -m xkernel.viewer_bounce_dot --points 24 --steps 2000 --sleep 0.02 --single-line --restitution .8
```

Single-line oscilloscope mode:

```bash
python -m xkernel.viewer_bounce_dot --points 20 --steps 400 --speed 1.2```

---

## Philosophy

**xkernel** is designed as a *substrate*:  
a minimal, deterministic, composable engine that can support multiple high-level
interpretations (lenses):

- Waveform lens  
- Euclidean Mechanics lens  
- DAT (Discrete Action Theory) lens  
- GTORC coherence lens  
- Visualization lenses  

The kernel never changes — the *lens* changes the meaning.

This makes `xkernel` ideal for research environments that require clean,
interpretable dynamical systems.

---

## Tests

Run the included tests:

```bash
pytest -q
```

---

## Versioning

This package uses semantic versioning.

Current release:

```
v0.1.0 — clean API, engine core, wave lens, ASCII viewers
```

Tag a new release:

```bash
git commit -am "Release v0.1.0"
git tag -a v0.1.0 -m "xkernel v0.1.0 initial stable release"
git push && git push --tags
```

---

## License

Currently unpublished. All rights reserved by project owner.

---

## Future Directions

- Real-time oscilloscope viewer  
- FFT lens (frequency-domain interpretation)  
- Geometry & coherence lenses  
- Multi-channel waveform viewers  
- WASM/Browser viewer backend  
- GPU-accelerated lattice kernel  

---

## Credits

Engine design and geometry concepts: **Scott Cave**  
Lens architecture: **EuMech / GTORC project**
