# ANTHROPOMORPHIC AGENT ENGINE — 数据契约标准

**Document ID:** AAES-2026-001
**Version:** 0.2.0
**Status:** Draft for public comment
**Applies to:** SPL Pure Core V8.0（`SPL-anthropic-engine.py`）与未成年合规变体（`minor-protection/SPL-anthropic-minor-engine.py`）
**Previous version:** 0.1.0-draft（`anthromorphic-agent-engine-standards.md`，已重命名）
**Maintainer:** NOHN AI TECHNOLOGY PTE. LTD.
**Contact:** ai@nohnlins.com

---

## 0. 0.2.0 相对 0.1.0 的实质变更

| 项 | 0.1.0 | 0.2.0 | 原因 |
|---|---|---|---|
| §5 状态模型 | 声明 snapshot "exactly" 17 键 | 按实现分列两个变体的**实际**键集（主引擎 23 / 未成年 15） | 0.1.0 的 "exactly" 与实现不符，实现多出 6 个键 |
| §5.2 fluid 默认值 | 把 `fluid_baseline` 标为 "Baseline (default)" | 区分**初始状态**与**基线稳态**两个不同量 | 0.1.0 混淆了两者：初始喜悦 0.0，基线喜悦 0.2 |
| §7 审计记录 | 只定义终值 `snapshot` 摘要 | 新增 §7.4 状态转移归因 `delta`（规范性算法） | 只记终值可证明"状态是什么"，不能证明"哪次输入造成了什么变化" |
| §8 确定性 | 仅要求"无随机" | 新增 §8.2 心境动力学规范性、§8.3 步长一致性量化界、§8.4 时钟注入前提 | 固定步长松弛使收敛速度依赖调用次数而非时间 |
| §1.2 范围 | 未成年变体 "separate document pending" | 纳入 §5.6、§7.5 | 该变体已与主引擎同算法对齐 |
| §9 一致性 | 5 条 | 6 条，新增 delta 可复核性 | — |

> 术语：0.1.0 文档路径为 `docs/anthromorphic-agent-engine-standards.md`，0.2.0 起为 `docs/agent-standard.md`。旧路径已不存在。

---

## 1. Introduction

### 1.1 Purpose

本文件定义拟人智能体引擎（SPL Pure Core V8.0 及其未成年合规变体）的公开数据契约。它规定：

- **内感受向量（interoceptive vector）**的输入格式；
- 引擎 **snapshot()** 暴露的完整状态模型；
- **审计记录**的格式，含状态转移归因；
- 符合规范的实现 **MUST** 暴露的入口点；
- **确定性**的充分条件与量化边界。

意图是可互操作：第三方应当能够在**不接触任何专有引擎源码**的前提下，(a) 驱动一个符合规范的引擎实现，(b) 读取并解释其状态，(c) 独立复核其审计轨迹。

### 1.2 Scope

本文件覆盖两个确定性心理学核心。**不**覆盖：

- 可替换的人格层（`NarrativeMapper` / `MinorNarrativeMapper`）除事件词表以外的语义；
- 语言风格渲染器与 LLM 适配器，除其审计记录外；
- 未成年变体的服务端合规端点（见 `minor-protection/COMPLIANCE.md`）；
- 远程部署的传输/网络协议。

### 1.3 Conventions

- 除特别说明外，所有数值均为 IEEE-754 双精度浮点。
- 字段名**区分大小写**。
- `[a, b]` 表示含端点的数值区间。
- `MUST` / `MUST NOT` / `SHOULD` / `SHOULD NOT` / `MAY` 按 RFC 2119 解释。
- 两个变体共有的契约在本文件标注 **[共用]**；仅主引擎的标注 **[主]**；仅未成年变体的标注 **[未]**。

---

## 2. Terminology

| 术语 | 定义 |
|---|---|
| **Agent** | 内部状态按本标准演化的虚拟实体。 |
| **Interoceptive Vector** | 表示一个外部事件在内部被如何感受的标量信号字典。 |
| **Fluid** | 快变情绪维度（秒—分钟尺度），8 维。 |
| **Mood** | 慢变背景情感维度（小时—天尺度），3 维。 |
| **Snapshot** | 某一瞬时 agent 完整状态的可序列化表示。 |
| **Delta** | 两次 snapshot 之间的逐字段状态变化，见 §7.4。 |
| **Audit Record** | 描述单次状态转移的一行 JSON。 |
| **Virtual Clock** | 可注入的时间源，用于确定性重放。 |
| **Forced term** | 心境的受迫项，由事件驱动，见 §8.2。 |
| **Damping term** | 心境的阻尼项，由时间驱动，见 §8.2。 |
| **Constitution** | 定义一个角色稳态的参数集合（`fluid_baseline` 及各类速率常数）。 |

---

## 3. Architecture Overview

### 3.1 Layers

```
┌──────────────────────────────────────────────┐
│  Personality Layer (replaceable, external)    │  NarrativeMapper / MinorNarrativeMapper
│  maps events → interoceptive vectors          │  （合规变体对侮辱/背叛类降档）
├──────────────────────────────────────────────┤
│  SPL Pure Core (deterministic)                │
│  fluid · mood · trauma[主] · memory           │
│  trust · self-esteem · sleep · expectation    │
│  dissonance · defense[主]                     │
├──────────────────────────────────────────────┤
│  Audit Layer (AuditLogger, JSONL)             │
│  records every transition + delta for复核      │
└──────────────────────────────────────────────┘
```

人格层在**上**、LLM 在**下**：LLM 只负责把内部状态渲染成台词，MUST NOT 参与状态演化。这一倒置是本引擎与"把角色写进 prompt"路线的根本分歧。

### 3.2 Data Flow

1. 外部事件由人格层翻译为**内感受向量**；
2. 向量经 `process_vector` 进入核心；
3. 核心确定性更新状态；
4. 状态可经 `snapshot()` 观测；
5. 每次状态转移追加一条审计记录，其中 **MUST** 携带 `delta`。

---

## 4. Interoceptive Vector Contract (Input)

### 4.1 Vector Fields **[共用]**

符合规范的实现 MUST 接受包含下列**任意子集**的字典：

| 字段 | 类型 | 区间 | 语义 |
|---|---|---|---|
| `threat` | float | [-1, 1] | 感知到的危险；正值提升恐惧。 |
| `belonging` | float | [-1, 1] | 社会接纳；负值表示被拒绝。 |
| `autonomy` | float | [0, 1] | 自主感 / 掌控感。 |
| `fatigue` | float | [0, 1] | 生理或心理疲劳输入。 |
| `shame_trigger` | float | [0, 1] | 指向自我的负面评价。 |

核心 **MUST** 忽略未知键（见 §4.5）。

### 4.2 Narrative Event Vocabulary **[共用]**

| Event | 主引擎向量（intensity 1.0） | 未成年变体向量 |
|---|---|---|
| `compliment` | `{"belonging": 0.3, "autonomy": 0.1}` | 同左 |
| `insult` | `{"belonging": -0.4, "threat": 0.3}` | `{"belonging": -0.24, "threat": 0.18}` |
| `betrayal` | `{"belonging": -0.6, "threat": 0.5}` | `{"belonging": -0.36, "threat": 0.3}` |
| `alone` | `{"belonging": -0.3}` | `{"belonging": -0.18}` |
| `rest` | `{"fatigue": -0.5}` | 同左 |
| *(其他任意)* | `{"belonging": 0.0, "threat": 0.0}` | 同左 |

未成年变体对侮辱/背叛类事件的负向强度降档至主引擎的 60%。

> **注意**：未知事件名落入全零分支，`arousal` 为 0，因而对心境既无受迫也无松弛速率抬升。下游系统 **MUST NOT** 假设任意事件名都有效。

### 4.3 Intensity **[共用]**

`raw_intensity` 是非负标量（默认 `1.0`），在评估前线性缩放向量。实现 MUST 接受 `0.0`（空操作）与大于 `1.0` 的值。

### 4.4 event_id **[共用]**

可选标识符。提供时 **MAY** 触发预期系统的 surprise 计算（见 §5.8）。

### 4.5 未知键处理 **[共用]**

核心 MUST 忽略未在 §4.1 定义的键。实现 **MUST NOT** 因此声称这些键产生了任何效果。

> 已知陷阱：`feature-guide/` 下的 Goal / Identity 模块目前输出 `tension_base` 键，该键不在 §4.1 契约内，因此**目标挫折与身份冲突的向量当前不会进入核心**。这些模块按设计是指导文件，不是已接线的运行时组件。

---

## 5. Agent State Model

### 5.1 Snapshot 键集（规范性）

符合规范的实现 **MUST** 使 `snapshot()` 返回以下键集。键数与键名均为强约束，**MUST NOT** 增删顶层键而不提升主版本号。

**[主]**（23 键）：`fluid, mood, self_esteem, energy, fatigue, excitation, max_trust, suppression_load, denial_load, rationalization_load, latent_pressure, cognitive_dissonance, sleep_debt, arousal_recent, trauma, memory_count, expected_count, last_perceived, llm_call_count, llm_failed_count, total_prompt_tokens, total_completion_tokens, total_tokens`

**[未]**（15 键）：`fluid, mood, self_esteem, energy, fatigue, excitation, max_trust, latent_pressure, cognitive_dissonance, sleep_debt, arousal_recent, memory_count, expected_count, last_perceived, protective`

差异 **[主]** 独有：`suppression_load` / `denial_load` / `rationalization_load`（防御机制仓）、`trauma`（创伤节点）、5 个 `llm_*` / `total_*` 计量字段。
差异 **[未]** 独有：`protective`（合规保护报告，见 §5.6）。

### 5.2 Fluid Submodel **[共用]**

`fluid` MUST 恰好包含以下 8 键，各自在 `[0, 1]`：

| 键 | 情绪 | **初始状态** | **基线稳态** |
|---|---|---|---|
| `喜悦` | Joy | 0.0 | 0.2 |
| `愤怒` | Anger | 0.0 | 0.0 |
| `恐惧` | Fear | 0.0 | 0.1 |
| `信任` | Trust | 0.5 | 0.5 |
| `疏离` | Alienation | 0.2 | 0.2 |
| `张力` | Tension | 0.2 | 0.2 |
| `愧疚` | Guilt | 0.0 | 0.0 |
| `羞耻` | Shame | 0.0 | 0.0 |

> **初始状态 ≠ 基线稳态**。初始值是角色诞生瞬间的状态；基线是 `_rebuild_fluid_target()` 每步重建稳态牵引时使用的目标。二者可以不同（本标准中喜悦与恐惧即不同）。0.1.0 把基线标注为 "default"，属文档错误。
>
> `信任` MUST NOT 超过 `max_trust`。

### 5.3 Mood Submodel **[共用]**

`mood` MUST 恰好包含以下 3 键，各自在 `[0, 1]`：

| 键 | 含义 | 初始值 **[主]** | 初始值 **[未]** |
|---|---|---|---|
| `愉悦` | Pleasantness | 0.5 | 0.5 |
| `紧张` | Tension | 0.3 | 0.2 |
| `精力` | Vigor | 0.7 | 0.7 |

### 5.4 Trauma State **[主]**

`trauma` 是以创伤类型标识符为键的字典。参考实现定义 `threat` 与 `betrayal` 两类，各在 `[0, 1]`。空对象 `{}` 表示无活跃创伤。

`[未]` 变体 **MUST NOT** 建模创伤累积（见 §5.6）。

### 5.5 Memory Traces **[共用]**

记忆是痕迹对象的有序列表。核心仅暴露 `memory_count`；实现 MAY 暴露完整痕迹，至少含：

| 字段 | 类型 | 语义 |
|---|---|---|
| `vector` | object | 编码时的内感受向量 |
| `strength` | float [0,1] | 痕迹强度（受遗忘影响） |
| `valence` | float | 编码时的 `belonging - threat` |
| `timestamp` | float | 最后强化的 Unix 时间 |
| `age` | float | 距最后强化的秒数 |
| `count` | int | 强化次数 |

参考实现上限 `MAX_MEMORY_TRACES = 64`。

> **容量上限**：痕迹以 5 维内感受向量表示，重巩固判据为余弦相似度 > `1 - RECONSOL_RADIUS`（= 0.6）。5 维空间内大量语义不同的事件会越过该阈值被判为同一记忆而互相覆盖。实现 **SHOULD** 记录该碰撞对记忆保真度的影响。

### 5.6 Protective Submodel **[未]**

`protective` 是未成年变体独有的合规保护报告，MUST 至少包含：

| 字段 | 语义 |
|---|---|
| `risk_level` | `LOW` / `MEDIUM` / `HIGH` |
| `crisis_flags` | 触发高风险的确定性原因列表 |
| `rest_hint` | 是否达到防沉迷时长阈值 |
| `session_seconds` | 本次会话累计秒数 |
| `emotion_ceil_neg` | 负性情绪钳位上限 |
| `attach_max` | 依恋/信任上限 |
| `minor_mode` / `age_group` | 未成年模式与年龄段 |
| `guardian_consent` / `guardian_contact` | 监护人同意与联系方式 |
| `exit_requested` | 是否已请求退出 |
| `overuse_hint` | 是否达到过度使用阈值 |
| `ai_disclosure_required` | 是否到达 AI 身份披露间隔 |
| `reality_reminder_due` | 是否到达现实提醒间隔 |

参考值：`emotion_ceil_neg = 0.75`、`attach_max = 0.8`、`psychological_resilience = 0.6`（主引擎为 0.5）。

该变体 **MUST NOT** 包含 `trauma_state` 字段、**MUST NOT** 包含防御机制层（`suppression_load` / `denial_load` / `rationalization_load` / 压抑-反弹 / 隐压雪崩 / 否认-现实侵入）。这是机制级风险削减，不是输出侧过滤。

### 5.7 Scalar State Variables **[共用]**

| 字段 | 区间 | 初始值 | 语义 |
|---|---|---|---|
| `self_esteem` | [0.05, 0.95] | 0.5 | 全局自我价值感，慢变 |
| `energy` | [0, 100] | 100.0 | 生理能量 |
| `fatigue` | [0, 1] | 0.0 | 疲劳 |
| `excitation` | [0, 1] | 0.3 | 唤醒 / 新奇 |
| `max_trust` | [0.1, 1.0] | 1.0 | 信任容量，在慢性忽视下被腐蚀 |
| `latent_pressure` | [0, ∞) | 0.0 | 隐压（雪崩前驱） |
| `cognitive_dissonance` | [0, 1] | 0.0 | 信念-行为冲突 |
| `sleep_debt` | [0, 1] | 0.0 | 累积睡眠亏欠 |
| `arousal_recent` | [0, 1] | 0.0 | 近期事件唤醒的慢记忆；**驱动心境松弛速率**，见 §8.2 |

仅 **[主]**：`suppression_load` / `denial_load` / `rationalization_load`，各 `[0, ∞)`，初始 0.0。

### 5.8 Expected Events **[共用]**

`expected_events` 把 `event_id` 映射到 `{valence: float [-1,1], confidence: float [0,1], time: float}`。`confidence` 随时间衰减，低于 0.05 时条目被移除。

### 5.9 快照的审计要求

`snapshot()` 暴露的每个状态量 **MUST** 出现在 §7.4 的 delta 覆盖范围内，或明确声明为纯输出量（`last_perceived`、`protective` 中的合规派生量除外）。驱动动力学的量（如 `arousal_recent`）**MUST NOT** 是不可观测的隐藏变量——否则审计链断裂。

---

## 6. Engine Entry Points

符合规范的实现 MUST 暴露：

| 方法 | 签名 | 行为 |
|---|---|---|
| `process_vector` | `(vector, raw_intensity=1.0, event_id="")` | 施加内感受向量；改变状态；追加审计记录 |
| `process_event` | `(event, intensity=1.0)` | 经人格层映射后转 `process_vector` |
| `idle` | `(seconds)` | 推进 `seconds` 秒无外部刺激的时间 |
| `sleep` | `(hours)` | 睡眠债清除、梦境情绪加工、恐惧消退、能量恢复、醒来重置 |
| `expect` | `(event_id, valence, confidence=0.5)` | 登记未来事件预期 |
| `induce_dissonance` | `(magnitude, belief_domain="")` | 注入信念-行为冲突 |
| `snapshot` | `() -> Dict` | 返回 §5 定义的完整状态 |
| `set_clock` | `(t: Optional[float])` | 注入虚拟时间；传 `None` 恢复墙钟 |
| `advance_clock` | `(dt)` | 虚拟时钟前推 `dt` 秒 |

**`idle` 与 `sleep` 在参考实现中不产生审计记录。** 调用方若需要完整轨迹，**MUST** 自行记录；实现 **SHOULD** 记录它们。

---

## 7. Audit Log Specification

### 7.1 Record Envelope

每条审计记录是一行 JSON（JSONL）。信封 MUST 包含：

| 字段 | 类型 | 语义 |
|---|---|---|
| `seq` | int | 会话内单调序号 |
| `ts` | string | ISO 8601 毫秒精度时间戳 |
| `engine` | string | 引擎版本标签；主引擎 `"SPL-V8.0"` |
| `session` | string | 会话标识 |
| `event` | string | 事件类型（见 §7.2） |
| `input` | object | 已净化的输入参数 |
| `snapshot` | object | 状态摘要（§7.5 的键集） |
| `delta` | object | 状态转移归因（见 §7.4） |

### 7.2 Canonical Event Types

| `event` 值 | 触发 |
|---|---|
| `process_vector` | 每次向量施加 |
| `sleep` | 一次 `sleep()` |
| `expect` | 一次 `expect()` |
| `induce_dissonance` | 一次 `induce_dissonance()` |
| `llm_call` | 一次语言模型调用（见 §7.6） |
| `llm_usage_recorded` | 一次 token 用量登记 |

### 7.3 记录内容要求

记录 **MUST** 同时携带：输入参数、终值状态摘要、以及 §7.4 的 delta。

> 0.1.0 只要求前两者。仅终值状态能证明"某时刻状态是什么"，**不能**证明"哪次输入造成了哪些字段的多少变化"。delta 是可复核性要求的最低条件。

### 7.4 状态转移归因 `delta`（规范性算法）

`delta` 由 `AuditLogger.snapshot_delta(before, after)` 计算，**两个变体 MUST 使用同一算法**。

**步骤**

1. 对 `DELTA_SCALARS` 中每个键 `k`：取 `b = before[k]`、`a = after[k]`。若两者皆缺失则跳过。
2. 对 `DELTA_NESTED` 中每个子模型 `g`：若 `before[g]` 与 `after[g]` 都是字典，取两者键的并集，对每个键展开为点号路径 `"g.k"`，`b = before[g].get(k)`、`a = after[g].get(k)`。
3. 对每个候选 `(key, b, a)`：若 `b == a` 则跳过。
4. **数值条目**（两侧均为 int/float，且均非 bool）：`{"before": b, "after": a, "delta": round(a - b, 6)}`。
5. **非数值条目**：`{"before": b, "after": a}`，**MUST NOT** 附带 `delta` 键。

**布尔** MUST NOT 被视为数值。**"新增一个危机标记"本身就是审计事件**，尽管它没有算术差——实现 **MUST NOT** 为它伪造一个差值。

**覆盖集**

| | `DELTA_SCALARS`（14 项） | `DELTA_NESTED` |
|---|---|---|
| **[主]** | `self_esteem, energy, fatigue, excitation, max_trust, suppression_load, denial_load, rationalization_load, latent_pressure, cognitive_dissonance, sleep_debt, arousal_recent, memory_count, expected_count` | `fluid, mood, trauma` |
| **[未]** | `self_esteem, energy, fatigue, excitation, max_trust, latent_pressure, cognitive_dissonance, sleep_debt, arousal_recent, memory_count, expected_count` | `fluid, mood, protective` |

两者的 `DELTA_SCALARS` 差异反映变体裁剪（见 §5.6），**MUST NOT** 为消除差异而强行对齐。

### 7.5 Snapshot 摘要

审计记录的 `snapshot` 字段是完整状态的**子集**，键集为：

**[主]**（17 键）：`fluid, mood, self_esteem, energy, fatigue, excitation, max_trust, suppression_load, denial_load, rationalization_load, latent_pressure, cognitive_dissonance, sleep_debt, arousal_recent, trauma, memory_count, expected_count`

**[未]**（14 键）：`fluid, mood, self_esteem, energy, fatigue, excitation, max_trust, latent_pressure, cognitive_dissonance, sleep_debt, arousal_recent, memory_count, expected_count, protective`

### 7.6 LLM Call Records

`llm_call` 记录 MUST 额外包含：

| 字段 | 类型 | 语义 |
|---|---|---|
| `model` | string | 模型标识 |
| `prompt_preview` | string | prompt 前 200 字符 |
| `success` | bool | 生成是否成功 |
| `duration_ms` | float | 调用墙钟耗时 |
| `usage` | object \| null | token 用量，不可用时为 `null` |
| `error` | string \| null | 错误信息，成功时为 `null` |

`usage` 在非 null 时 MUST 含 `prompt_tokens` / `completion_tokens` / `total_tokens`（整数）。

### 7.7 Failure Policy

审计写入 **MUST NOT** 改变核心状态演化。写入失败时引擎 **MUST** 静默继续，并 **MAY** 在下一条记录时重试。符合规范的实现 **MUST** 以相同方式记录其失败策略。

---

## 8. Determinism & Clock Control

### 8.1 确定性条件

符合规范的实现 MUST 在下列输入相同时给出相同状态：`(vector 序列, intensity 序列, event_id 序列, 初始状态, 时钟调度)`。

核心 **MUST NOT** 含随机性，**MUST NOT** 含 LLM 调用。单步时间 **MUST** 以 86400 秒（24 h）封顶。所有随机性 MUST 位于可替换的人格层或语言层。

### 8.2 心境动力学（规范性）

心境 **MUST** 实现为**受迫-阻尼系统**，MUST NOT 使用"每次调用走固定步长"的实现。

**受迫项（事件驱动）— `_mood_event_dose(v)`**

```
arousal = min(1, |threat| + |belonging| + |autonomy|)
若 arousal <= 0 则本项无操作
arousal_recent += (arousal - arousal_recent) * MOOD_AROUSAL_EMA
愉悦 += MOOD_DOSE_PLEASANT * arousal * belonging
紧张 += MOOD_DOSE_TENSION   * arousal * (max(0,threat) + max(0,-belonging))
精力 += MOOD_DOSE_VIGOR     * arousal * max(0, autonomy)
```

**[主]** 实现 MUST 使用**已被防御机制削减后**的向量（即 §8.5 的 `defended`），而非原始感知向量：被否认的事件 MUST NOT 对背景心境产生与其表露程度相称的冲击。
**[未]** 变体无防御层，直接使用感知向量。

**阻尼项（时间驱动）— `_update_mood(dt)`**

```
k     = MOOD_RATE_BASE * (1 + MOOD_AROUSAL_GAIN * arousal_recent)
alpha = 1 - exp(-k * dt)
arousal_recent *= exp(-dt / MOOD_AROUSAL_TAU)
愉悦 += (target_愉悦 - 愉悦) * alpha      （三者同理）
```

参考常数 **[共用]**：`MOOD_RATE_BASE = 0.0003`、`MOOD_AROUSAL_GAIN = 2.0`、`MOOD_AROUSAL_TAU = 1800.0`、`MOOD_AROUSAL_EMA = 0.05`、`MOOD_DOSE_PLEASANT = 0.10`、`MOOD_DOSE_TENSION = 0.12`、`MOOD_DOSE_VIGOR = 0.05`。

**语义**：唤醒越高，心境惯性越小、回稳越快——强情绪更易消退。

实现 **MUST** 使用与流体松弛相同的 `1 - exp(-k*dt)` 积分形式，而非 `k*dt` 线性近似。

### 8.3 步长一致性（量化界）

`alpha` **MUST** 以 `dt` 为自变量，实现 **MUST NOT** 产生"收敛速度正比于调用次数"的行为。

参考实现实测（同样 3600 秒）：

| 切分方式 | 旧实现（每步固定 0.0003） | 0.2.0 |
|---|---|---|
| `idle(3600)` 走 1 步 | 有效松弛 0.03% | 与细分同量级 |
| `idle(1) × 3600` 走 3600 步 | 有效松弛 66.05% | — |
| **步长敏感性** | **2201 倍** | **73 倍** |
| 细切法之间（`3600×1s` vs `60×60s`） | 不可比 | < 1e-3 |
| 单步 vs 细分 | 0.263 | < 2e-2 |

**残差不可归零**：心境靶标由流体推出，而流体在同一区间内同步演化，因此"向移动靶标松弛"没有闭式精确解，任何显式格式都无法做到步长无关。当靶标在该区间内近似静止时（如 `精力`），残差可低至 1e-14 量级。

符合规范的实现 **MUST NOT** 声称其动力学是步长无关的；**SHOULD** 报告其细切法一致性与大步-细分残差。

### 8.4 时钟注入前提

`set_clock(t)` **MUST** 只设置虚拟时钟源，**MUST NOT** 隐含改写 `last_time`。

构造后 `last_time` 为真实墙钟，因此 `set_clock` 之后的首次时间推进会算出负 `dt` 并直接早退——即**墙钟到合成原点之间的间隔不被结算**。这是预期行为（否则会积分数年空白），但它 **MUST** 被显式声明。

调用方 **MUST** 在注入时钟后自行同步 `last_time`，否则其重放起点与预期不符。

### 8.5 防御机制的语义要求 **[主]**

被否认或被合理化的部分 **MUST** 从"被感知的向量"中真正扣除，并进入情绪流体。实现 **MUST NOT** 仅在防御仓中记账而让未削减的向量照常驱动情绪。

三层递进语义：否认（Denial）→ 合理化（Rationalization）→ 压抑（Suppression）。压抑层 **MUST** 消费防御分配后的残余量，**MUST NOT** 重复计入已扣除部分。

### 8.6 可复现性声明的前提

"完全可重放"仅在**显式调用 `set_clock()` 之后**成立。未注入时 `_now()` 回落 `time.time()`，两次相同输入序列产生不同结果。

任何对外的可复现性声明 **MUST** 附带该前提。参考实现以一条负向测试（S4）强制此前提：它**要求**自然时钟产生不同哈希，若相同则测试失败。

---

## 9. Conformance

产品仅在满足**全部**下列条件时 **MAY** 声称符合本标准：

1. 实现 §6 全部入口点及指定语义。
2. `snapshot()` 输出与 §5.1 键集逐键一致。
3. 发出符合 §7 的审计记录，包含 `delta` 字段（§7.4）与其失败策略（§7.7）。
4. 支持虚拟时钟，并满足 §8.1 的确定性要求。
5. 心境动力学满足 §8.2 的受迫-阻尼结构与积分形式。
6. 不声称兼容任何未实现的保留词汇。

非目标（§1.2）明确不在范围内，**MUST NOT** 被引用为一致性缺口。

### 9.1 测试套件

参考实现提供零依赖测试套件，**两层互补**：

| 层 | 入口 | 回答的问题 | 判据形态 |
|---|---|---|---|
| **S（确定性）** | `tests/run_conformance.py` | 同一输入能否逐比特复现？ | 快照 SHA256 + 标量容差 |
| **R（语义契约）** | `tests/run_regression.py` | 该发生的事有没有发生？ | 可读断言，逐条命名 |

`tests/run_regression.py` 是总入口，一次运行覆盖两层，适用于 CI 门禁。

**S 层四项检查**

| 编号 | 检查 | 期望 |
|---|---|---|
| S1 | 逐比特重放：注入时钟后 snapshot SHA256 == 基线 | 全部通过 |
| S2 | 重复稳定：无跨实例状态泄漏 | 全部通过 |
| S3 | 标量容差：跨平台稳健层 | 全部通过 |
| S4 | 时钟注入前提（**负向测试**） | 自然时钟**必须**产生不同哈希 |

**R 层六项契约**

| 编号 | 文件 | 覆盖的契约 |
|---|---|---|
| R1 | `test_defense.py` | §8.5 防御削减真正到达情绪流体 |
| R2 | `test_audit_delta.py` | §7.4 审计 delta 的算法与自洽性 |
| R3 | `test_mood_dynamics.py` | §8.2/§8.3 心境受迫-阻尼结构与步长一致性 |
| R4 | `test_minor_variant.py` | §5.6 未成年变体与主引擎同算法 |
| R5 | `test_doc_contract.py` | 本文件与实现不漂移 |
| R6 | `test_mutation_guard.py` | 断言本身具有判别力 |

**R6 的必要性**：「测试通过」只有在「把被测行为改坏后测试变红」时才是证据。
R6 注入缺陷后要求对应测试**必须失败**。符合规范的实现若提供行为断言，
**SHOULD** 同时提供等价的判别力验证——否则断言可能恒真。

**R5 的边界**：R5 校验「文档与代码同步」，**不是**「语义正确」。
文档与实现同时写错时 R5 照样通过。语义正确性由 R1–R4 负责。

### 9.1.1 基线的性质

S1/S3 的期望值来自**基线文件**。基线由参考实现的当前行为生成，因此：

> 基线是**变更检测器**，不是正确性判据。

它能证明「行为变了」，**不能**证明「新行为对」。任何对外的正确性声明
**MUST NOT** 以基线自证为依据；**MUST** 由 R 组断言与独立的外部反事实实验
（同一脚本化序列下比较完整内核 / 机制裁剪 / 恢复创伤但只加输出过滤，
用人的判断做外部裁决）支撑。

### 9.2 基线维护程序

`python tests/run_conformance.py --update-baseline` 用当前引擎重算预期哈希并覆盖 `tests/conformance_vectors.json`。

该操作 **MUST** 仅在以下条件下执行：

1. 引擎行为变更是**有意**的，且已记录原因；
2. 基线文件受版本控制，可从提交历史还原；
3. 已生成变更前后对照，逐向量列出哈希与标量差异，并随变更一并留档。

**MUST NOT** 在未提供对照的情况下更新基线。快照键集的任何增删都会无条件改变全部 S1 哈希，此类变化与行为变化**MUST** 在对照中区分标注。

---

## 10. Versioning & Compatibility

- 引擎版本标签：`SPL-V8.0`。
- 本标准独立于引擎版本化（当前 `0.2.0`）。
- 引擎 tag 演进 **MUST** 遵循语义化版本。**MUST NOT** 移除任何入口点或改变 §5.1 顶层键名。
- 类名兼容说明：参考实现暴露 `SPLPureCoreV7_3`（别名 `SPLPureCore`），二者均指 V8.0 行为集；未成年变体暴露 `SPLMinorPureCore`。
- 破坏性变更（入口点移除、键集变更、delta 语义变更） **MUST** 提升主版本号。

---

## 11. References

| Ref | Document |
|---|---|
| [1] | RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels |
| [2] | 引擎源码：`SPL-anthropic-engine.py`；打包镜像 `packaging/spl_agent_engine/core.py`（与主引擎字节一致） |
| [3] | 未成年变体：`minor-protection/SPL-anthropic-minor-engine.py` |
| [4] | 一致性套件：`tests/run_conformance.py`、`tests/conformance_vectors.json`、`tests/README.md` |
| [5] | 未成年合规说明：`minor-protection/COMPLIANCE.md` |
| [6] | 仓库说明：`README.md` / `README-zh.md` |

---

*Copyright © NOHN AI TECHNOLOGY PTE. LTD. This specification is published for interoperability review. Implementations of this standard are independent of the reference engine's proprietary source code.*
