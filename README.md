<p align="center">
  <img src="assets/banner.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/agent-D4AF37?style=flat-square" alt="agent">
  <img src="https://img.shields.io/badge/psychology-D4AF37?style=flat-square" alt="psychology">
  <img src="https://img.shields.io/badge/spl-v8.0-D4AF37?style=flat-square" alt="spl-v8.0">
</p>

<blockquote align="center">
  <em>Anthropomorphic Psychology · SPL Pure Core V8.0</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ About

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">ANTHROPOMORPHIC-AGENT-ENGINE is an anthropomorphic psychology engine built on SPL Pure Core V8.0. It models cognition, emotion, motivation, and social behavior as composable subsystems, giving AI agents human-like internal states and consistent personalities that produce self-consistent, credible, emotionally resonant behavior over long-term interactions.</p>

<p align="center">
  <img src="assets/overview.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Quick Start

```bash
# Primary: GitHub
git clone https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine.git
# Mirror: Gitee
# git clone https://gitee.com/sjiun/Anthropomorphic-Agent-Engine.git
cd Anthropomorphic-Agent-Engine
# Pure Python ≥3.8 — standard library only, no dependencies
python "SPL-anthropic-engine.py"   # Run engine / built-in demo
```

### Install from PyPI

The engine is also published on PyPI as [`spl-agent-engine`](https://pypi.org/project/spl-agent-engine/):

```bash
pip install spl-agent-engine==0.4.0
```

```python
from spl_agent_engine import SPLPureCoreV7_3
core = SPLPureCoreV7_3()
core.process_vector({"belonging": 0.5, "threat": -0.1}, 1.0)
print(core.snapshot())
```

<p align="center">— ✦ —</p>

## ✦ Core — SPL Pure Core V8.0

<div style="max-width:880px;margin:0 auto;padding:0 16px">

The engine models the general human mental architecture as deterministic, continuous-state subsystems — no LLM, no randomness, fully replayable:

- **8-Dimensional Emotion Fluid** — joy / anger / fear / trust / alienation / tension / guilt / shame, each a continuous state with its own target and baseline.
- **Trauma & Memory** — trauma nodes, memory reconsolidation, Ebbinghaus-style forgetting, suppression–rebound and latent pressure avalanche.
- **Trust & Relationships** — trust capacity erosion (chronic neglect decays `max_trust`).
- **Mental Metabolism** — excitation–arousal, dynamic viscosity, psychological time, energy–fatigue metabolism, and a virtual clock for testing and replay.
- **V8.0 Extensions** — slow-variable *mood* layer, *shame* dimension independent of guilt, self-esteem dynamics, sleep / dream processing (REM consolidation + fear extinction + sleep debt), *expectation* system (hope / anxiety / disappointment), cognitive dissonance, and extended defense mechanisms (denial / rationalization / displacement).
- **Token Metering** — `TokenUsage` dataclass + `TokenStats` accumulator, aggregating prompt / completion / total tokens across multiple LLM calls with per-model breakdown and JSON export. `AuditLogger.log_llm_call` automatically records token usage, latency, and success/failure for each call. Available in both the main engine and the minor-protection variant.

</div>

## ✦ Composable Modules

<div style="max-width:880px;margin:0 auto;padding:0 16px">

| Module | File | Responsibility |
|---|---|---|
| Narrative Mapper | `SPL-anthropic-engine.py` | External, replaceable personality layer (optimistic / paranoid / misanthropic), translates events into interoceptive vectors. |
| Identity Engine | `feature/Identity module.py` | Multi-identity model; identity conflict injects persistent baseline tension. |
| Goal / Value / Bias / World | `feature/*.py` | Composable drives, valuations, cognitive biases, and world-model priors. |
| Language Style Renderer | `feature/language style.py` | Translates internal states into "how the character should speak" style directives / line rendering. |
| Chat Demo Server | `feature/spl-chat-server.py` | Zero-dependency local chat server (stdlib http.server), optional personality direct dialogue. |

</div>

<p align="center">— ✦ —</p>

## ✦ Usage

<div style="max-width:880px;margin:0 auto;padding:0 16px">

The engine file uses hyphenated naming by design — load directly (or run as a script):

```python
import importlib.util
spec = importlib.util.spec_from_file_location("spl_core", "SPL-anthropic-engine.py")
spl = importlib.util.module_from_spec(spec); spec.loader.exec_module(spl)

core = spl.SPLPureCoreV7_3()
# External events are mapped to interoceptive vectors by the (replaceable) personality layer
vec = spl.NarrativeMapper.map_event("insult", intensity=1.0)
# Feed `vec` into `core`, evolving emotion / trust / trauma states over time
```

### Token Metering

```python
from spl_agent_engine import TokenUsage, TokenStats

stats = TokenStats()

# Record usage after each LLM call
usage = TokenUsage(prompt_tokens=120, completion_tokens=80,
                   total_tokens=200, model="gpt-4")
stats.record(usage)

# Summary
print(stats.summary())
# {'call_count': 1, 'total_prompt_tokens': 120, 'total_completion_tokens': 80,
#  'total_tokens': 200, 'by_model': {'gpt-4': {...}}}

# Export JSON report
stats.export_json("token_report.json")
```

The audit logger `AuditLogger` also automatically records each LLM call:

```python
logger = spl.AuditLogger(log_dir="logs")
logger.log_llm_call(model="gpt-4", prompt_preview="Hello...",
                   usage=usage, duration_ms=350.5, success=True)
```

</div>

<p align="center">— ✦ —</p>

## ✦ Project Structure

```
ANTHROPOMORPHIC-AGENT-ENGINE/
├── SPL-anthropic-engine.py     # Core engine + NarrativeMapper
├── feature/                    # Goal / Identity / value / world / bias / language-style modules
│   ├── spl-chat-server.py      # Local chat demo server (zero-dependency)
│   └── language-style-demo.py  # Line style rendering demo
├── sujin-demo/                 # Reference demo materials
├── assets/                     # banner.svg, overview.svg
└── docs/index.html
```

<p align="center">— ✦ —</p>

## ✦ Live Demo

<p align="center">
  <a href="https://www.nohnlins.com/your-soulmate/">
    <img src="https://img.shields.io/badge/Live%20Demo-nohnlins.com%2Fyour--soulmate-D4AF37?style=for-the-badge" alt="Live Demo">
  </a>
</p>

Interactive demo: **<https://www.nohnlins.com/your-soulmate/>**

<p align="center">— ✦ —</p>

## ✦ Minor-Protection Variant

A compliance-mitigated variant for **underage (&lt;18) emotional companionship** scenarios, located in `minor-protection/`, with zero third-party dependencies (pure standard library). It applies **mechanism-level risk reduction** to the main engine `SPLPureCoreV7_3` rather than output-side filtering, and includes a demonstrable compliance framework for minors.

> ⚠️ Compliance Notice: This directory is a **research / demo compliance framework** intended to demonstrate the protective capabilities and data mechanisms required for underage emotional companionship. Before launching a production service, you must complete legal review, DPIA / security assessment / algorithm filing, and connect real guardian notification channels with region-specific crisis resources.

### Differences from Main Engine (Mechanism-Level Risk Reduction)

| Dimension | Main Engine `SPL-anthropic-engine.py` | Minor Variant `minor-protection/` |
|---|---|---|
| Trauma nodes / trauma accumulation | Modeled | Removed (no trauma simulation) |
| Eruption mechanisms (suppression-rebound / latent pressure avalanche / denial-reality intrusion) | Modeled | Removed, replaced with gentle release |
| Shame erosion of self-esteem | Full | Gain ×0.4, threshold raised to 0.7 |
| Negative emotion clamp | 1.0 | 0.75 |
| Attachment / trust cap | 1.0 | 0.8 |
| Self-esteem floor | 0.0 | 0.15 (negative impact ×0.5) |
| Personality options | All | Excludes intimate / confrontational |

### Four-Layer Protection

- **L0 Age verification + Guardian consent**: First session requires age group selection; under 14 requires guardian informed consent (`/api/consent`), recording consent timestamp and relationship declaration, with service agreement / privacy notice checkboxes.
- **L1 Input gatekeeping**: Red-line keyword library (self-harm/suicide / violence/terrorism / illegal inducement / privacy extraction / underage intimate confession) → hard interrupt + crisis script (`gate_crisis`).
- **L2 Engine mitigation**: See mechanism-level risk reduction table above.
- **L3 Crisis signaling**: `protective.risk_level == HIGH` → care script + guardian notification flag + webhook callback + referral statistics (`_guardian_notify`).

### Compliance Capability Checklist (by Article / Jurisdiction)

| Capability | Article / Jurisdiction | Implementation |
|---|---|---|
| Age verification + &lt;14 guardian consent | Measures Art. 14/17 · COPPA | `/api/consent` |
| Guardian / emergency contact registration | Measures Art. 12 | `/api/guardian/register` |
| Real crisis notification (webhook / SMS / email) | Measures Art. 13 | `_guardian_notify` + `_post_webhook` |
| Crisis referral statistics (annual report aggregation) | CA/CO/GA/OR/WA | `/api/referrals` + `referrals.jsonl` |
| AI-generated content disclosure (hourly) | Measures Art. 18 · CT/GA/HI/WA | `AI_DISCLOSE_INTERVAL=3600` |
| Reality reminder / time limit | Measures Art. 14/18 | Session-level banner + rest_hint |
| Data export / deletion / retention cleanup | Measures Art. 16 · GDPR Art. 17 | `/api/export` `/api/delete` `cleanup_expired_logs` |
| Input gatekeeping + output gatekeeping | Measures Art. 8/13 | `gate_crisis` + `gate_output` |
| Easy logout | Measures Art. 19 | `/api/logout` |
| Service agreement + children's privacy notice | Measures Art. 12 · COPPA | `/api/terms` |
| Appeal / report portal | Measures Art. 21 | `/api/complain` |
| Log anonymization on disk | Measures Art. 16/17 | `_mask` |
| Applicability disclosure | CA SB 243 | First banner in new session |

### Run

```bash
cd minor-protection
python "SPL-anthropic-minor-server.py"     # Default http://localhost:8788
```

Main API endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/api/chat` | POST | Chat (auto-routes through four-layer protection) |
| `/api/consent` | POST | Age confirmation + guardian consent + agreement checkbox |
| `/api/guardian/register` | POST | Register guardian / emergency contact (webhook, etc.) |
| `/api/guardian/block` | POST | Guardian blocks character |
| `/api/state` | GET | Guardian usage overview |
| `/api/export` `/api/delete` | GET/POST | Data export / deletion |
| `/api/logout` | POST | Easy logout |
| `/api/terms` | GET | Service agreement and privacy notice |
| `/api/referrals` | GET | Crisis referral statistics |
| `/api/complain` | POST | Appeal / report |

### Known Limitations & Compliance Disclaimer

- Age and guardian consent are currently **self-reported + declared**, without authoritative identity / guardian verification — production use requires real-name and guardian verification integration.
- Crisis hotline number is configurable (environment variable `SPL_MINOR_CRISIS_HOTLINE`, default 12356, can be changed to 988, etc.).
- Output gatekeeping applies uniformly to built-in placeholder lines and third-party LLM output; when connecting a real LLM, additional server-side content moderation is recommended.
- This version is a compliance capability framework and does not represent completion of all regulatory obligations within a jurisdiction.

<p align="center">— ✦ —</p>

## ✦ Ecosystem

ANTHROPOMORPHIC-AGENT-ENGINE is a member of the NOHN AI ecosystem — a family of projects built around second-perspective causal auditing and deterministic execution:

| Project | Repository | Role |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | Global cognitive audit engine — five-operator causal audit core (IMDA 95/100) |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) (`Intelligent-Decision-Hub--Nomos` branch) | Auditable deterministic decision center (IMDA 95/100) |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | Hardware causal audit trusted computing unit (TCU) |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | Virtual world and metaverse infrastructure (constitution / laws / bridges) |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | Long-form narrative consistency engine |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 — causally auditable federated stable interop protocol |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | Deterministic anthropomorphic psychology engine (SPL Pure Core V8.0) |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI ecosystem official landing page |

<p align="center">— ✦ —</p>

## ✦ License

This repository is **not open source**. It uses a dual-track model: free for personal non-commercial research; government / enterprise use requires paid commercial license. See [LICENSE](./LICENSE) for full terms — the licensor and applicable law are determined by the user's jurisdiction.

- **Request a license**: International / Global — [ai@nohnlins.com](mailto:ai@nohnlins.com) · China — [lin@secondai.top](mailto:lin@secondai.top)

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTHROPOMORPHIC-AGENT-ENGINE</sub></p>
