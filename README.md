

# ANTHROPOMORPHIC-AGENT-ENGINE

<p align="center">
  <img src="banner.png" alt="ANTHROPOMORPHIC-AGENT-ENGINE banner" style="width:100%">
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

ANTHROPOMORPHIC-AGENT-ENGINE is an anthropomorphic psychology engine built on SPL Pure Core V8.0. It models cognition, emotion, motivation, and sociality as composable subsystems, giving AI agents anthropomorphic internal states and consistent personalities for coherent, emotionally credible behavior in long-term interactions.

<p align="center">
  <img src="assets/overview.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE overview" style="width:100%">
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
| Goal engine | `feature/Goal module.py` | Composable goal management with importance, urgency, and difficulty tracking. |
| Value engine | `feature/value module.py` | Core value evaluation and emotional amplification system. |
| Bias engine | `feature/bias module.py` | Cognitive bias profiles (optimistic, paranoid, depressive) that modulate perception and memory. |
| World model | `feature/world module.py` | World prior models (optimistic, pessimistic, traumatized) influencing expectations and interpretations. |

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

### Core API Reference

**SPLPureCoreV7_3** — Main engine class

- `process_vector(interoceptive_vec, delta_time)` — Process an interoceptive vector and advance time
- `snapshot()` — Get the current state of all subsystems

**NarrativeMapper** — Event to vector translation

- `map_event(event: str, intensity: float) -> Dict[str, float]` — Map natural language events to interoceptive vectors

### Module Usage Examples

```python
# Goal Engine
from feature.Goal module import sujin_goals
goal_engine = sujin_goals()
goal_engine.add_goal("complete_task", importance=0.8, urgency=0.6)
primary = goal_engine.get_primary_goal()

# Identity Engine  
from feature.Identity module import sujin_identity
identity_engine = sujin_identity()

# Value Engine
from feature.value module import sujin_values
value_engine = sujin_values()
emotions = value_engine.evaluate_event("success")

# Bias Profiles
from feature.bias module import paranoid_bias, optimistic_bias
bias_engine = BiasEngine(profile=optimistic_bias())

# World Models
from feature.world import optimistic_world, pessimistic_world
world = optimistic_world()
```

</div>

## ✦ Project Structure

```
ANTHROPOMORPHIC-AGENT-ENGINE/
├── SPL-anthropic-engine.py       # Core engine + NarrativeMapper (main entry point)
├── feature/                      # Composable psychological modules
│   ├── Goal module.py            # Goal management and motivation system
│   ├── Identity module.py        # Multi-identity and identity conflict handling
│   ├── bias module.py            # Cognitive bias profiles and application
│   ├── value module.py           # Core values and emotional amplification
│   └── world module.py           # World model priors and expectations
├── sujin-demo/                   # Reference demo assets
├── assets/                       # Banner and overview diagrams
│   ├── banner.svg
│   └── overview.svg
├── docs/
│   └── index.html               # Interactive documentation
├── spl_engine_demo.ipynb        # Jupyter notebook demo
├── IMDA_AI_Verify_Causal_Audit_Report.pdf
├── LICENSE
└── README.md
```

## ✦ Architecture Overview

The engine follows a modular architecture where each subsystem can be used independently or composed together:

### Core Subsystems

1. **SPLPureCoreV7_3** — Central processing hub that orchestrates all subsystems, maintains continuous emotional states, and manages time evolution.

2. **NarrativeMapper** — Translates external events (natural language descriptions) into interoceptive vectors that the core engine can process.

3. **Goal Engine** — Manages agent goals with attributes like importance, urgency, difficulty, and dependencies. Provides conflict detection and emotion generation.

4. **Identity Engine** — Models multiple identities within an agent, handling identity conflicts that generate sustained psychological tension.

5. **Value Engine** — Evaluates events against core values and amplifies emotional responses based on value relevance.

6. **Bias Engine** — Applies cognitive bias profiles to perception and memory, including paranoid, optimistic, and depressive biases.

7. **World Model** — Represents the agent's expectations about the world, influencing how events are interpreted.

</div>

<p align="center">— ✦ —</p>

## ✦ License & Authorization

<div style="max-width:880px;margin:0 auto;padding:0 16px">

This repository is **not open-source**. It uses a dual-track model: free for individual non-commercial research, paid commercial authorization required for government / enterprise. See [LICENSE](./LICENSE) for the full terms — licensor and governing law are determined by the user's location.

</div>

<p align="center">
  <a href="https://github.com/NOHN-AI">NOHN-AI</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:lin@secondai.top">lin@secondai.top</a>
</p>
<p align="center"><sub>NOHN AI · ANTHROPOMORPHIC-AGENT-ENGINE</sub></p>