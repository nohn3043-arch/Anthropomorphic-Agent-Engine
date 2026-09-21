# ANTHROPOMORPHIC-AGENT-ENGINE STANDARDS

**Document ID:** AAES-2026-001  
**Version:** 0.1.0-draft  
**Status:** Draft for public comment  
**Applies to:** SPL Pure Core V8.0 (engine version tag `SPL-V8.0`)  
**Maintainer:** NOHN AI TECHNOLOGY PTE. LTD.  
**Contact:** ai@nohnlins.com

---

## 1. Introduction

### 1.1 Purpose

This document defines the public data contracts of the Anthropomorphic Agent Engine (SPL Pure Core V8.0). It specifies:

- the **interoceptive vector** input format used to drive the engine;
- the **agent state model** exposed by the engine snapshot;
- the **audit log record format** produced by the engine;
- the **engine entry points** that a conforming implementation MUST expose.

The intent is interoperability: a third party shall be able to (a) drive a conforming engine implementation, (b) read and interpret its state, and (c) independently verify its audit trail — **without access to any proprietary engine source code**.

### 1.2 Scope

This document covers the deterministic psychology core only. It does NOT cover:

- the replaceable personality layer (NarrativeMapper) beyond its event vocabulary;
- the language style renderer or LLM adapters beyond their audit records;
- the minor-protection variant's compliance endpoints (separate document pending);
- transport/network protocols for remote deployment.

### 1.3 Conventions

- All values are IEEE-754 doubles unless stated otherwise.
- Field names are case-sensitive.
- `[a, b]` denotes an inclusive numeric range.
- The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY" are to be interpreted as described in RFC 2119.

---

## 2. Terminology

| Term | Definition |
|---|---|
| **Agent** | A virtual entity whose internal state evolves according to this standard. |
| **Interoceptive Vector** | A dictionary of scalar signals that represents how an external event is felt internally. |
| **Fluid** | Fast-moving emotion dimensions (second-to-minute scale). |
| **Mood** | Slow-moving background affective dimensions (hour-to-day scale). |
| **Snapshot** | A serializable, complete representation of the agent's state at an instant. |
| **Audit Record** | One line of JSON describing a single state transition or LLM call. |
| **Virtual Clock** | An injectable time source enabling deterministic replay. |

---

## 3. Architecture Overview

### 3.1 Layers

```
┌─────────────────────────────────────────────┐
│  Personality Layer (replaceable, external)   │  e.g. NarrativeMapper
│  maps events → interoceptive vectors          │
├─────────────────────────────────────────────┤
│  SPL Pure Core V8.0 (deterministic)          │
│  emotion fluid · mood · trauma · memory      │
│  trust · self-esteem · sleep · expectation   │
│  dissonance · defense mechanisms             │
├─────────────────────────────────────────────┤
│  Audit Layer (AuditLogger, JSONL)            │
│  records every transition for verification   │
└─────────────────────────────────────────────┘
```

### 3.2 Data Flow

1. An external event is translated by the personality layer into an **interoceptive vector**.
2. The vector is passed to the core via `process_vector`.
3. The core updates its internal state deterministically.
4. The resulting state is observable via `snapshot()`.
5. Every mutation is appended to the **audit log** as one JSON record.

---

## 4. Interoceptive Vector Contract (Input)

### 4.1 Vector Fields

A conforming implementation MUST accept a dictionary containing any subset of the following keys:

| Field | Type | Range | Semantics |
|---|---|---|---|
| `threat` | float | [-1, 1] | Perceived danger; positive values increase fear. |
| `belonging` | float | [-1, 1] | Social acceptance; negative values indicate rejection. |
| `autonomy` | float | [0, 1] | Sense of agency / control. |
| `fatigue` | float | [0, 1] | Physical or mental exhaustion input. |
| `shame_trigger` | float | [0, 1] | Self-referential negative evaluation. |

Unknown keys SHOULD be ignored by the core.

### 4.2 Narrative Event Vocabulary

The reference personality layer (`NarrativeMapper`) defines the following canonical events:

| Event | Resulting Vector (at intensity 1.0) |
|---|---|
| `compliment` | `{"belonging": 0.3, "autonomy": 0.1}` |
| `insult` | `{"belonging": -0.4, "threat": 0.3}` |
| `betrayal` | `{"belonging": -0.6, "threat": 0.5}` |
| `alone` | `{"belonging": -0.3}` |
| `rest` | `{"fatigue": -0.5}` |
| *(any other)* | `{"belonging": 0.0, "threat": 0.0}` |

### 4.3 Intensity

`raw_intensity` is a non-negative scalar (default `1.0`) that linearly scales the vector before appraisal. Implementations MUST accept `0.0` (no-op) and values greater than `1.0`.

---

## 5. Agent State Model

### 5.1 Top-Level Snapshot

A conforming implementation MUST expose a `snapshot()` method returning a JSON object with exactly the following top-level keys:

```json
{
  "fluid": { },
  "mood": { },
  "self_esteem": 0.5,
  "energy": 100.0,
  "fatigue": 0.0,
  "excitation": 0.3,
  "max_trust": 1.0,
  "suppression_load": 0.0,
  "denial_load": 0.0,
  "rationalization_load": 0.0,
  "latent_pressure": 0.0,
  "cognitive_dissonance": 0.0,
  "sleep_debt": 0.0,
  "trauma": { },
  "memory_count": 0,
  "expected_count": 0,
  "last_perceived": { }
}
```

### 5.2 Fluid Submodel (Emotion)

The `fluid` object MUST contain exactly these eight keys, each in `[0, 1]`:

| Key | Emotion | Baseline (default) |
|---|---|---|
| `喜悦` | Joy | 0.2 |
| `愤怒` | Anger | 0.0 |
| `恐惧` | Fear | 0.1 |
| `信任` | Trust | 0.5 |
| `疏离` | Alienation | 0.2 |
| `张力` | Tension | 0.2 |
| `愧疚` | Guilt | 0.0 |
| `羞耻` | Shame | 0.0 |

`信任` (Trust) MUST NOT exceed `max_trust`.

### 5.3 Mood Submodel

The `mood` object MUST contain exactly these three keys, each in `[0, 1]`:

| Key | Meaning | Default |
|---|---|---|
| `愉悦` | Pleasantness | 0.5 |
| `紧张` | Tension | 0.3 |
| `精力` | Vigor | 0.7 |

### 5.4 Trauma State

`trauma` is an object whose keys are trauma type identifiers. The reference implementation defines two canonical types:

| Key | Meaning |
|---|---|
| `threat` | Accumulated danger-related trauma |
| `betrayal` | Accumulated betrayal-related trauma |

Each value is in `[0, 1]`. An empty object `{}` means no active trauma.

### 5.5 Memory Traces

Memory is represented as an ordered list of trace objects. The core exposes only the count (`memory_count`), but a conforming implementation MAY expose full traces with at least these fields:

| Field | Type | Semantics |
|---|---|---|
| `vector` | object | The interoceptive vector at encoding time |
| `strength` | float [0,1] | Trace strength (subject to forgetting) |
| `valence` | float | `belonging - threat` at encoding time |
| `timestamp` | float | Unix time of last reinforcement |
| `age` | float | Seconds since last reinforcement |
| `count` | int | Number of reinforcements |

The reference implementation caps traces at `MAX_MEMORY_TRACES = 64`.

### 5.6 Expected Events

`expected_events` maps an `event_id` string to an expectation object:

| Field | Type | Semantics |
|---|---|---|
| `valence` | float [-1, 1] | Expected outcome valence |
| `confidence` | float [0, 1] | Subjective certainty |
| `time` | float | Unix time the expectation was set |

### 5.7 Scalar State Variables

| Field | Range | Default | Semantics |
|---|---|---|---|
| `self_esteem` | [0.05, 0.95] | 0.5 | Global self-worth, slow-moving |
| `energy` | [0, 100] | 100.0 | Physiological energy |
| `fatigue` | [0, 1] | 0.0 | Fatigue level |
| `excitation` | [0, 1] | 0.3 | Arousal / novelty state |
| `max_trust` | [0.1, 1.0] | 1.0 | Trust capacity (erodes under chronic neglect) |
| `suppression_load` | [0, ∞) | 0.0 | Suppression reservoir |
| `denial_load` | [0, ∞) | 0.0 | Denial reservoir |
| `rationalization_load` | [0, ∞) | 0.0 | Rationalization reservoir |
| `latent_pressure` | [0, ∞) | 0.0 | Latent pressure (avalanche precursor) |
| `cognitive_dissonance` | [0, 1] | 0.0 | Belief-behavior conflict level |
| `sleep_debt` | [0, 1] | 0.0 | Accumulated sleep deficit |

---

## 6. Engine Entry Points

A conforming implementation MUST expose the following methods:

| Method | Signature | Behavior |
|---|---|---|
| `process_vector` | `(vector: Dict[str,float], raw_intensity: float=1.0, event_id: str="")` | Apply an interoceptive vector; mutate state; append audit record. |
| `process_event` | `(event: str, intensity: float=1.0)` | Convenience: map event via personality layer, then `process_vector`. |
| `idle` | `(seconds: float)` | Advance time with no external stimulus. |
| `sleep` | `(hours: float)` | Process REM consolidation, fear extinction, sleep-debt recovery, energy recovery. |
| `expect` | `(event_id: str, valence: float, confidence: float=0.5)` | Register an expectation for future surprise computation. |
| `induce_dissonance` | `(magnitude: float, belief_domain: str="")` | Inject belief-behavior conflict. |
| `snapshot` | `() -> Dict[str,Any]` | Return the full state per Section 5. |
| `set_clock` | `(t: Optional[float])` | Inject virtual time (or `None` to restore wall clock). |
| `advance_clock` | `(dt: float)` | Advance virtual clock by `dt` seconds. |

---

## 7. Audit Log Specification

### 7.1 Record Envelope

Every audit record is a single line of JSON (JSONL). The envelope MUST contain:

| Field | Type | Semantics |
|---|---|---|
| `seq` | int | Monotonic sequence number within a session |
| `ts` | string | ISO 8601 timestamp with millisecond precision |
| `engine` | string | Engine version tag, fixed `"SPL-V8.0"` |
| `session` | string | Session identifier |
| `event` | string | Event type (see 7.2) |
| `input` | object | Sanitized input parameters |
| `snapshot` | object | Summarized state snapshot (subset of Section 5 fields) |

### 7.2 Canonical Event Types

| `event` value | Trigger |
|---|---|
| `process_vector` | Every vector application |
| `sleep` | A `sleep()` call |
| `expect` | An `expect()` call |
| `induce_dissonance` | A `induce_dissonance()` call |
| `llm_call` | A language-model invocation (see 7.3) |

### 7.3 LLM Call Records

An `llm_call` record MUST additionally contain:

| Field | Type | Semantics |
|---|---|---|
| `model` | string | Model identifier |
| `prompt_preview` | string | First 200 characters of the prompt |
| `success` | bool | Whether generation succeeded |
| `duration_ms` | float | Wall-clock duration of the call |
| `usage` | object\|null | Token usage; `null` if unavailable |
| `error` | string\|null | Error message, or `null` on success |

The `usage` object MUST contain `prompt_tokens`, `completion_tokens`, `total_tokens` (integers).

### 7.4 Failure Policy

Audit logging MUST NOT alter core state evolution. If a log write fails, the engine MUST continue silently and MAY retry on the next record. A conforming implementation MUST document its failure policy identically.

---

## 8. Determinism & Clock Control

- A conforming implementation MUST be deterministic given identical (vector sequence, intensity sequence, event_id sequence, initial state, clock schedule).
- The virtual clock (`set_clock` / `advance_clock`) MUST be supported for test and replay.
- Single time steps MUST be capped at 86400 seconds (24 h) to bound computation.
- The reference implementation contains no randomness and no LLM calls inside the core; all stochasticity lives in the replaceable personality or language layers.

---

## 9. Conformance

A product MAY claim conformance to this standard if and only if it satisfies **all** of the following:

1. It implements every entry point in Section 6 with the specified semantics.
2. Its `snapshot()` output matches Section 5 field-for-field.
3. It emits audit records conforming to Section 7, including the failure policy.
4. It supports the virtual clock and determinism requirements of Section 8.
5. It does not claim compatibility with any reserved vocabulary that it does not implement.

Non-goals are explicitly out of scope (Section 1.2) and MUST NOT be cited as conformance gaps.

---

## 10. Versioning & Compatibility

- Engine version tag: `SPL-V8.0`.
- This standard is versioned independently of the engine (currently `0.1.0-draft`).
- Class-name compatibility note: the reference implementation exposes `SPLPureCoreV7_3` with `SPLPureCore` as the canonical alias; both refer to the V8.0 behavior set.
- A future revision of this standard MUST NOT break Section 5 field names without a major version bump.

---

## 11. References

| Ref | Document |
|---|---|
| [1] | RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels |
| [2] | Engine source: `nohn3043-arch/Anthropomorphic-Agent-Engine`, `spl_agent_engine/core.py` |
| [3] | README.md of the same repository (architecture overview, V8.0 feature set) |

---

*Copyright © NOHN AI TECHNOLOGY PTE. LTD. This specification is published for interoperability review. Implementations of this standard are independent of the reference engine's proprietary source code.*
