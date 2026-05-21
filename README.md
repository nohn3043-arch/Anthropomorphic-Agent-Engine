
# SPL Audit Engine - Second‑Perspective Auditing Engine

**A verifiable, traceable, and crash‑proof “logical skeleton” for AI characters**

[![License](https://img.shields.io/badge/License-Commercial%20Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)]()

## 🧠 What is it?

The SPL Audit Engine is the engineering implementation of the **Second‑Perspective (SPL) language** in the domain of AI‑powered characters.  

It embeds into your virtual character system and performs **hardware‑grade logical verification** on every generated response and every emotional change, ensuring that the character’s behavior always stays within the predefined psychological matrix – eliminating OOC (out‑of‑character) and irrational affinity jumps.

**Core value:**  
Turn “character consistency” from a mystical art into an auditable, traceable, and fixable engineering problem.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **Real‑time Behavior Auditing (AUDIT)** | Blocks OOC utterances (e.g., intimate words in low‑affinity stage, harsh rejections in high‑affinity stage). |
| **Causal Chain Anchoring (ANCHOR)** | Records key interaction events as an immutable state chain, enabling true long‑term memory. |
| **Narrative Stripping (STRIP)** | Strips away filler words, rhetoric, and emotional noise, leaving only dry logic for consistency checks. |
| **Affinity Change Auditing** | Validates each affinity increment/decrement to prevent cheating or sudden jumps. |
| **Multi‑dimensional Psychology Matrix** | Uses **0.5 as the human baseline** for each personality dimension, dynamically amplified or suppressed through stage coefficients. |
| **Audit Log & Causal Chain Query** | Every abnormal behavior leaves a trace; operations teams can pinpoint root causes (weight issue, rule omission, or model hallucination). |
| **On‑Premise Deployment** | Zero data exfiltration, fully private – compliant with GDPR / China PIPL. |

---

## 📦 On‑Premise Deployment – Fixed‑Price Licensing

Due to privacy and compliance requirements, the engine is **only available for on‑premise deployment** – no user data is ever collected.  
Licensing is offered as **Annual Subscription** or **Perpetual License**.

**Deliverables:**

| Deliverable | Format |
|-------------|--------|
| SPL Audit Core Library | `.so` / `.dll` / Python wheel |
| Character Configuration Tool | CLI + Web console |
| Audit Log Analysis Suite | Offline scripts + visual dashboard |
| Initial Psychology Matrix & Rule Library | JSON / YAML configuration files |
| Integration Docs & Code Examples | PDF + sample repository |

**Pricing model:**

| License Type | Price Range | Target Customers |
|--------------|-------------|------------------|
| **Annual Subscription** | 30k – 80k USD / year | Platforms needing continuous support & rule updates |
| **Perpetual License** | 150k – 300k USD (one‑time) | Technically strong teams that want long‑term ownership |

> The annual fee primarily covers: **40% strategic consulting + 25% technical support + 20% software license + 15% rule‑base updates**  
> You are not just buying software – you are buying ongoing cognitive tuning and architecture guidance from the creator of the SPL language.

---

## 🧩 Quick Start (Technical Preview)

```python
from spl_audit import AICharacterProfile, SPLAuditEngine

# Create a character
ye_wanqing = AICharacterProfile(
    name="Ye Wanqing",
    age=24,
    relationship="Niece of Lu Jingchuan / secret forbidden lover",
    job_identity="CEO of Qingri Group"
)

# Configure the psychology matrix (0.5 = human baseline)
ye_wanqing.psychology_matrix = {
    "Cold & Restrained": {
        "description": "...",
        "base_weight": 0.5,
        "effective_scene": ["public", "company"]
    },
    "Pathological Indulgence": {
        "description": "...",
        "base_weight": 0.5,
        "effective_target": ["Lu Jingchuan"],
        "effective_scene": ["private"]
    }
}

# Attach the auditing engine
auditor = SPLAuditEngine(ye_wanqing)

# Generate a response and audit it
user_msg = "Come to my room tonight"
raw_reply = llm.generate(ye_wanqing.to_ai_prompt() + user_msg)
audit_report = auditor.audit_response(raw_reply)

if not audit_report["passed"]:
    final_reply = get_fallback_reply()   # override on violation
else:
    final_reply = raw_reply
```

---

📞 Business Cooperation

If you operate an AI character platform (Hoshino, Replika, Glow, Zhumengdao, etc.), please contact us for:

· Detailed technical white paper
· On‑premise evaluation kit (30‑day trial, limited to 10k concurrent characters)
· Annual subscription / perpetual license quotation

Email: nohn3043@gmail.com
X (Twitter): @nohn188728
GitHub: github.com/nohn3043/spl-audit-engine

---

© Copyright & License

This software is a commercial, closed‑source product. The source code is not open.
Any reverse engineering, redistribution, or use in competing products is strictly forbidden without a valid license.
See LICENSE for details.

---

“An AI character without auditing is just a bundle of random emotions. The SPL Audit Engine gives every character a verifiable soul.”
— Nohn, creator of the Second‑Perspective language

```
