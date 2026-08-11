<p align="center">
  <img src="https://sourceforge.net/p/your-soulmate/git/ci/main/tree/banner.png?format=raw" alt="ANTHROPOMORPHIC-AGENT-ENGINE banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/agent--D4AF37?style=flat-square" alt="agent">
  <img src="https://img.shields.io/badge/psychology--D4AF37?style=flat-square" alt="psychology">
  <img src="https://img.shields.io/badge/spl-v8-D4AF37?style=flat-square" alt="spl-v8">
</p>

<blockquote align="center">
  <em>Anthropomorphic Psychology · SPL Pure Core V8.0</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ About

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">ANTHROPOMORPHIC-AGENT-ENGINE is an anthropomorphic psychology engine built on SPL Pure Core V8.0. It models cognition, emotion, motivation, and sociality as composable subsystems, giving AI agents anthropomorphic internal states and consistent personalities for coherent, emotionally credible behavior in long-term interactions.</p>

<p align="center">
  <img src="https://sourceforge.net/p/your-soulmate/git/ci/main/tree/assets/overview.svg?format=raw" alt="ANTHROPOMORPHIC-AGENT-ENGINE overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Quick Start

```bash
git clone git@github.com:NOHN-AI/ANTHROPOMORPHIC-AGENT-ENGINE.git
cd ANTHROPOMORPHIC-AGENT-ENGINE
# Pure Python ≥3.8 — standard library only, nothing to install
python "SPL-anthropic-engine.py"   # run the engine / bundled demo
```

### Install from PyPI

The engine is also published on PyPI as [`spl-agent-engine`](https://pypi.org/project/spl-agent-engine/):

```bash
pip install spl-agent-engine==0.1.0
```

```python
from spl_agent_engine import SPLPureCoreV7_3
core = SPLPureCoreV7_3()
core.process_vector({"belonging": 0.5, "threat": -0.1}, 1.0)
print(core.snapshot())
```

<p align="center">— ✦ —</p>

## ✦ What's Inside — SPL Pure Core V8.0

<div style="max-width:880px;margin:0 auto;padding:0 16px">

The engine models a universal human mental architecture as deterministic, continuous-state subsystems — no LLM, no randomness, fully replayable:

- **8-dimensional emotion fluid** — 喜悦 / 愤怒 / 恐惧 / 信任 / 疏离 / 张力 / 愧疚 / 羞耻, each a continuous state with its own target and baseline.
- **Trauma & memory** — trauma nodes, memory reconsolidation, Ebbinghaus-style forgetting, repression–rebound and the implicit-pressure avalanche.
- **Trust & relationships** — trust-capacity corrosion (`max_trust` decays under chronic cold treatment).
- **Metabolism of mind** — excitation–arousal, dynamic viscosity, psychological time, energy–fatigue metabolism, and a virtual clock for tests and replay.
- **V8.0 extensions** — a slow-variable *mood* layer, a *shame* dimension distinct from guilt, self-esteem dynamics, sleep/dream processing (REM consolidation + fear extinction + sleep debt), an *anticipation* system (hope / anxiety / disappointment), cognitive dissonance, and extended defense mechanisms (denial / rationalization / displacement).

</div>

## ✦ Composable Modules

<div style="max-width:880px;margin:0 auto;padding:0 16px">

| Module | File | Responsibility |
|---|---|---|
| Narrative mapper | `SPL-anthropic-engine.py` | External, user-swappable persona layer (optimism / paranoia / misanthropy) that translates events into interoceptive vectors. |
| Identity engine | `feature/Identity module.py` | Multi-identity model; identity conflict injects sustained baseline tension. |
| Goal / Value / Bias / World | `feature/*.py` | Composable drives, valuation, cognitive biases, and world-model priors. |

</div>

## ✦ Usage

<div style="max-width:880px;margin:0 auto;padding:0 16px">

The engine file uses a hyphenated name by design, so load it directly (or run it as a script):

```python
import importlib.util
spec = importlib.util.spec_from_file_location("spl_core", "SPL-anthropic-engine.py")
spl = importlib.util.module_from_spec(spec); spec.loader.exec_module(spl)

core = spl.SPLPureCoreV7_3()
# An external event is mapped to an interoceptive vector by the (swappable) persona layer
vec = spl.NarrativeMapper.map_event("insult", intensity=1.0)
# feed `vec` into `core` to evolve emotion / trust / trauma state over time
```

</div>

## ✦ Project Structure

```
ANTHROPOMORPHIC-AGENT-ENGINE/
├── SPL-anthropic-engine.py     # core engine + NarrativeMapper
├── feature/                    # Goal / Identity / bias / value / world modules
├── sujin-demo/                 # reference demo assets
├── assets/                     # banner.svg, overview.svg
└── docs/index.html
```

## ✦ Live Demo

<p align="center">
  <a href="https://your-soulmate.pages.dev/">
    <img src="https://img.shields.io/badge/Live%20Demo-your--soulmate.pages.dev-D4AF37?style=for-the-badge" alt="Live Demo">
  </a>
</p>

Try the interactive demo: **<https://your-soulmate.pages.dev/>**

<p align="center">— ✦ —</p>


## ✦ License & Authorization

This repository is **not open-source**. It uses a dual-track model: free for individual non-commercial research, paid commercial authorization required for government / enterprise. See [LICENSE](./LICENSE) for the full terms — licensor and governing law are determined by the user's location.

<p align="center">
  <a href="https://github.com/NOHN-AI">NOHN-AI</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTHROPOMORPHIC-AGENT-ENGINE</sub></p>
