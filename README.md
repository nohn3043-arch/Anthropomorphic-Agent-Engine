##  The soul does not exist.  
## The mind is not mysterious. 

---

SPL Pure Core V7.3

A deterministic, semantics‑free personality dynamics engine.

---

What It Is

A 300‑line Python core that simulates emotional inertia, trauma imprinting, memory reconsolidation, suppression‑rebound, and trust erosion — without knowing what an "insult" or "compliment" is.

It takes three numerical dimensions (threat, belonging, fatigue) and produces fluid emotional states, trauma nodes, and memory traces with forgetting.

The core is the body; the mapper is the soul.

---

Core Mechanisms

Mechanism What It Does
7‑dimension fluid field Joy, anger, fear, trust, alienation, tension, guilt — relax towards dynamic targets with adaptive viscosity.
Trauma nodes Form when threat exceeds resilience‑weighted threshold; bias future fluid targets.
Memory reconsolidation Old traces reactivate on similar input; safety (trust × (1‑fear)) determines whether they weaken or strengthen.
Forgetting curve Exponential decay (I·e^(−λt)); weak traces pruned; bounded pool (64 traces) with importance‑based eviction.
Suppression–rebound Suppressed negative emotions accumulate; burst when load exceeds threshold — with cooldown.
Trust capacity erosion Each negative belonging shock multiplies max_trust (e.g., ×0.92); recovery is logarithmic and partial.
Latent pressure avalanche Threat and belonging deficits accumulate; release when threshold met — with cooldown.

---

Interface

One public method:

```python
def process_vector(vector: Dict[str, float], intensity: float = 1.0)
```

Where vector may contain any of: "threat", "belonging", "fatigue".

The core does not recognise event names. All semantics (insult, compliment, betrayal) are external.

---

Personality Customisation

Swap the external mapper. Same core, different soul:

```python
class ParanoidMapper:
    def map_event(event, intensity):
        if event == "praise":
            return {"threat": 0.4, "belonging": 0.1}   # "they're mocking me"
        if event == "criticism":
            return {"threat": 0.8, "belonging": -0.5}  # "they're attacking me"

class SecureMapper:
    def map_event(event, intensity):
        if event == "praise":
            return {"belonging": 0.3, "threat": -0.1}  # "they appreciate me"
        if event == "criticism":
            return {"belonging": -0.1, "threat": 0.1}  # "they're helping me"
```

---

Engineering Properties

· Deterministic — same input, same output.
· Bounded memory — 64 trace cap; O(1) per call.
· No external dependencies — pure Python.
· Thread‑safe per instance.
· Serialisable — all primitive fields.

---

Quick Start

```python
core = SPLPureCoreV7_3(psychological_resilience=0.4)
core.process_vector({"threat": 0.5, "belonging": -0.6})
print(core.snapshot())
```

---

Use Cases

· Game NPCs with long‑term memory and emotional inertia.
· Digital humans / virtual assistants with believable rapport.
· Psychological simulation (trauma recovery, intervention testing).
· Affective computing benchmarks.
· Interactive storytelling with character consistency.

---

Status

Version 7.3 — stable, feature‑complete for narrative‑driven applications.

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
