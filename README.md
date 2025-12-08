# 🌀 xkernel
### Minimal Deterministic X-Field Engine with Modular Lens Architecture
Version: **0.2.0**
Engine: `XKernel`

---

## Overview

**xkernel** is a lightweight, deterministic computational engine for evolving  
**1-D lattices of real-valued vectors**.

Each lattice site holds an **X-vector** in ℝ⁶ (configurable).  
Each timestep applies a strictly local, strictly deterministic update rule:

\[
X_i(t+1) = X_i(t) \\;+\; \eta\Big(A X_i(t) \\;+\; B\,[X_{i-1}(t) + X_{i+1}(t)]\Big)
\]

Key properties:

- **Deterministic**: no randomness, fully reproducible  
- **Pure Python**, zero dependencies  
- **Stable JSON trace export**  
- **Modular lens system**: different higher-level interpretations of the same dynamics  
- **Used as a computational substrate** for EuMech, DAT, GTORC, waveform viewers, and geometric analysis  
- **Includes Einstein / Schrödinger / Shannon information lenses**

---

## Project Structure

```
xkernel/
├── README.md
├── pyproject.toml
├── src/
│   └── xkernel/
│       ├── xkernel.py             # core deterministic engine
│       ├── cli.py                 # command-line entry points
│       ├── lens_wave.py           # waveform lens (analytic + engine-driven)
│       ├── lens_einstein.py       # curvature / strain / energy lens
│       ├── lens_schrodinger.py    # amplitude / phase decomposition lens
│       ├── lens_shannon.py        # entropy-based information lens
│       ├── viewer_bounce_dot.py   # ASCII simulation viewer
│       ├── demo_einstein.py       # engine → wave → Einstein projection
│       ├── demo_schrodinger.py    # engine → wave → Schrödinger projection
│       └── demo_shannon.py        # engine → wave → Shannon projection
└── tests/
    ├── test_xkernel_basic.py      # kernel correctness
    └── test_lenses.py             # lens correctness
```

---

## Installation

Development install:

```bash
pip install -e .
```

Verify:

```bash
python -c "from xkernel import XKernelConfig; print(XKernelConfig())"
```

---

## Core API

### Configuration

```python
from xkernel import XKernelConfig
cfg = XKernelConfig(size=64, dim=6, eta=0.1)
```

### Seeding initial conditions

```python
from xkernel import seed_zero, seed_impulse
initial = seed_impulse(cfg, index=3, component=0, amplitude=1.0)
```

### Running the engine

```python
from xkernel import XKernel
kernel = XKernel(cfg)
states = list(kernel.run(initial, steps=128))
```

### Exporting a trace

```python
from xkernel import trace_to_dict
trace = trace_to_dict(states)
```

---

# Lenses

## Waveform Lens (`lens_wave.py`)

Turn engine history into a **1-D waveform**:

```python
from xkernel import wave_from_states, ascii_wave
wave = wave_from_states(states, site=3, component=0, normalize=True)
print(ascii_wave(wave, height=10))
```

Generate analytic waves:

```python
from xkernel import analytic_wave
sq = analytic_wave("square", steps=64, amplitude=1.0, frequency=2.0)
```

Supported analytic types:

- "sine"
- "square"
- "triangle"
- "saw"

---

## Einstein Lens (`lens_einstein.py`)

Projects a waveform into:

- **Curvature**
- **Strain**
- **Energy**

Demo:

```bash
python -m xkernel.demo_einstein
```

---

## Schrödinger Lens (`lens_schrodinger.py`)

Complex decomposition:

- **Amplitude**
- **Phase**

Demo:

```bash
python -m xkernel.demo_schrodinger
```

---

## Shannon Lens (`lens_shannon.py`)

Information-theoretic projection:

- **entropy_series**
- **probability**
- **entropy** (scalar)

Demo:

```bash
python -m xkernel.demo_shannon
```

---

# Viewer Example (`viewer_bounce_dot.py`)

ASCII simulation mode:

```bash
python -m xkernel.viewer_bounce_dot --points 24 --steps 2000 --sleep 0.02
```

---

# Tests

```bash
pytest -q
```

---

# Versioning

```
v0.2.0 — added full lens demo suite (Einstein, Schrödinger, Shannon)
```

---

# License

All rights reserved by project owner.

---

# Credits

Engine design & geometry direction: **Scott Cave**  
Lens architecture: **EuMech / GTORC Suite**
