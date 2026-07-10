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

## 授权与许可（Licensing & Authorization）

本仓库为 **Anthropomorphic Agent Engine** 的技术展示仓库。版权所有 © 2026 Nohn AI Technology，保留一切权利。

| 使用主体 | 用途 | 授权要求 |
|---|---|---|
| 个人（自然人） | 非商业学术研究 / 学习 / 个人实验 | **免费**，须遵守 LICENSE 中的"个人研究免费许可"限制 |
| 政府机构 / 事业单位 / 企业 | 任何用途（含内部部署、产品研发、服务提供） | **须事先取得书面付费授权** |

- **个人研究者**：可依据 [LICENSE](./LICENSE) 免费用于非商业研究，但不得用于任何商业目的，亦不得为任何企业或政府组织提供服务。
- **政府 / 企业使用者**：在签署《商业授权协议》并付费前，不得复制、部署、运行、集成或分发本作品。
- **申请授权**：请联系 ai@nohnlins.com，说明使用主体性质、拟用场景与规模。

完整条款见本仓库 [LICENSE](./LICENSE) 文件。
