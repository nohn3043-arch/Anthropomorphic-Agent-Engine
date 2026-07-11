##  The soul does not exist.
## The mind is not mysterious.

---

# SPL Pure Core V8.0

A deterministic, semantics‑free anthropomorphic psychology engine — the *universal* mental architecture every human shares, separated from any particular character's "soul".

---

## What It Is

A pure‑Python core that simulates emotional inertia, trauma imprinting, memory reconsolidation, suppression‑rebound, trust erosion, **plus the V8.0 additions**: a slow mood layer, self‑esteem dynamics, sleep/dream processing, an anticipatory system, cognitive dissonance, and a layered defense‑mechanism hierarchy — without knowing what an "insult" or "compliment" is.

It ingests numerical interoceptive vectors (`threat`, `belonging`, `autonomy`, `fatigue`, `shame_trigger`) and produces fluid emotional states, a slow mood background, self‑esteem, trauma nodes, and memory traces with forgetting.

**The core is the body; the mapper is the soul.** All semantics (insult, compliment, betrayal) live in the external mapper — not in the engine.

> Note on naming: the class is still exported as `SPLPureCoreV7_3` for backward compatibility; internally it is the V8.0 universal psychological architecture.

---

## V8.0 Universal Psychological Subsystems

These are **not** character self‑settings — they are the shared mental structure of every human, baked into the core:

| Subsystem | What It Models |
|---|---|
| 8‑dimension fluid field | 喜悦 · 愤怒 · 恐惧 · 信任 · 疏离 · 张力 · 愧疚 · 羞耻 — relax toward dynamic targets with adaptive viscosity |
| Mood layer | Slow background affect (愉悦 / 紧张 / 精力), ~1h half‑life, continuously modulates appraisal gain |
| Self‑esteem | `self_esteem ∈ [0,1]`; low esteem internalizes failure & amplifies threat (attribution bias) |
| Sleep / dream | `sleep(hours)` recovers energy **and** decays emotional charge / fear extinction in "dreams" |
| Anticipation | `expect()` sets future hope/threat; fulfillment → surprise, violation → disappointment |
| Cognitive dissonance | Belief–behavior conflict → tension → auto‑resolved via rationalization past threshold |
| Defense hierarchy | Denial → rationalization → repression, escalating under load |

Plus the V7 foundations: trauma nodes, memory reconsolidation, Ebbinghaus forgetting (64‑trace bounded pool), suppression‑rebound, trust‑capacity erosion, latent‑pressure avalanche, excitation/arousal, energy/fatigue metabolism.

---

## Interface

Public methods:

```python
core = SPLPureCoreV7_3(psychological_resilience=0.4)
core.set_clock(0.0)

# Inject interoceptive vector (semantics-free)
core.process_vector({"threat": 0.5, "belonging": -0.6, "fatigue": 0.1}, intensity=1.0)

# Anticipation: set expectation, later fulfilled or violated
core.expect("sign_contract", valence=0.6, confidence=0.7)

# Sleep: dream processing + fear extinction + sleep-debt repayment
core.sleep(hours=8)

# Cognitive dissonance: belief conflict -> tension -> rationalization
core.induce_dissonance(magnitude=0.5, belief_domain="loyalty")

# Full psychological snapshot
snap = core.snapshot()   # fluid, mood, self_esteem, cognitive_dissonance, sleep_debt, ...
```

The core does not recognise event names. All semantics are external (see `sujin-demo` and `feature/`).

---

## Repository Layout

```
SPL-anthropic-engine.py   # V8.0 core engine (the body)
sujin-demo                # SujinMapper + SujinAgent, 3-phase narrative demo
feature/                  # Self-setting templates for orgs/governments:
  world module.py         #   WorldModel
  bias module.py          #   BiasEngine (cognitive biases)
  Identity module.py      #   IdentityEngine (role conflicts)
  value module.py         #   ValueEngine (value weighting)
  Goal module.py          #   GoalEngine (goal受阻/达成 -> emotion)
docs/index.html           # GitHub Pages intro site (this repo's /docs)
```

`feature/` is a *template* showing enterprises/governments how to configure an anthropomorphic agent for their own scenario. It is not required to run the core.

---

## Quick Start

```bash
python sujin-demo          # run the full Sujin narrative demo
```

Or import the core directly:

```python
from SPL_anthropic_engine import SPLPureCoreV7_3
core = SPLPureCoreV7_3()
core.process_vector({"belonging": 0.5, "threat": -0.1}, 1.0)
print(core.snapshot())
```

---

## Engineering Properties

· Deterministic — same input, same output.
· Bounded memory — 64 trace cap; O(1) per call.
· No external dependencies — pure Python.
· Thread‑safe per instance.
· Serialisable — all primitive fields.

---

## Use Cases

· Game NPCs with long‑term memory and emotional inertia.
· Digital humans / virtual assistants with believable rapport.
· Psychological simulation (trauma recovery, intervention testing).
· Affective computing benchmarks.
· Interactive storytelling with character consistency.

---

## Deploy & Remotes

This repository is mirrored to two remotes:

| Remote | URL |
|---|---|
| `github` | https://github.com/NOHN-AI/Anthropomorphic-Agent-Engine.git |
| `gitee`  | https://gitee.com/lin-mingjun-hua_0/Anthropomorphic-Agent-Engine.git |

Push to both:

```bash
git push github main
git push gitee  main
```

### GitHub Pages (intro site)

The landing page lives at `docs/index.html` and is published via GitHub Pages:

**URL:** https://nohn-ai.github.io/Anthropomorphic-Agent-Engine/

To (re)enable after a fresh clone, go to the GitHub repo → **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / Folder: `/docs` → Save.** No build step is needed (static HTML, no external dependencies).

---

## Status

Version 8.0 — universal psychological architecture added on top of the V7 narrative core.

---

## Licensing & Authorization

This repository is a technical showcase for the **Anthropomorphic Agent Engine**. Copyright © 2026 Shanghai Linming Junhua Technology Co., Ltd. and NOHN AI TECHNOLOGY PTE. LTD. All rights reserved.

| User | Purpose | License Requirement |
|---|---|---|
| Individual (natural person) | Non-commercial academic research / study / personal experimentation | **Free** under the "Free Individual Research License" in [LICENSE](./LICENSE) |
| Government agency / public institution / enterprise | Any purpose (incl. internal deployment, product development, service provision) | **Requires prior written paid authorization** |

- **Individual researchers** may use the Work free of charge for non-commercial research under [LICENSE](./LICENSE), but not for any commercial purpose, nor to provide services to any enterprise or government organization.
- **Government / enterprise users** may not copy, deploy, run, integrate, or distribute the Work before signing a Commercial Authorization Agreement and paying the agreed fee.
- **Apply for authorization**:
  - International / Global: [ai@nohnlins.com](mailto:ai@nohnlins.com)
  - China: [ai@tx.nohnlins.com](mailto:ai@tx.nohnlins.com)

The licensor, governing law, and dispute resolution are determined by the user's location as set out in [LICENSE](./LICENSE): users within the PRC → Shanghai Linming Junhua Technology Co., Ltd. (laws of the PRC); users outside the PRC → NOHN AI TECHNOLOGY PTE. LTD. (laws of Singapore, SIAC arbitration).
