# Conformance Suite — Determinism / Replayability

SPL Pure Core V8.0 的确定性一致性测试。零依赖（仅 Python 标准库），克隆仓库即可运行。

---

## 被测声明

本套件验证 README `§Core` 中的这一句：

> "The engine models the general human mental architecture as deterministic,
> continuous-state subsystems — **no LLM, no randomness, fully replayable**"

把这句声明拆成四条可执行断言，逐条判定。结果是二元的（PASS / FAIL）——
不产生分数，不做主观解释。

---

## 快速开始

```bash
python tests/run_conformance.py              # 只打印失败项与汇总
python tests/run_conformance.py --verbose     # 打印全部用例
python tests/run_conformance.py --out-dir ./reports   # 另存报告与原始结果
```

退出码：`0` = 全部通过；`1` = 存在失败。可直接用于 CI 门禁。

实测结果（Python 3.13.14 / win32，8 向量）：

```
Result: 25/25 passed    (0.13s)
```

---

## 测试项

| 编号 | 名称 | 断言 |
|---|---|---|
| **S1** | bit-exact replay | 注入虚拟时钟后，每个向量的 `snapshot` SHA256 必须与基线**逐比特相同** |
| **S2** | repeat stability | 同一向量连跑 3 次，3 次哈希必须全同——证明没有隐藏状态在实例之间泄漏 |
| **S3** | scalar tolerance | 关键标量按 `1e-9` 容差比对。哈希对解释器/平台敏感，标量比对用于**跨环境复核** |
| **S4** | clock premise | **负向测试**：不注入时钟时，同一向量两次运行的结果**必须不同** |

---

## ⚠️ 时钟前提（本套件最重要的产出）

引擎的 `_now()` 在 `_clock_override is None` 时回落到 `time.time()`：

```python
def _now(self) -> float:
    if self._clock_override is not None:
        return self._clock_override
    return time.time()
```

因此：**可复现性只在显式调用 `set_clock()` 之后成立。**

默认状态下，同一输入序列的两次运行会得到不同结果——这不是缺陷，是设计
（`set_clock` 就是为测试与回放准备的）。但**这一点此前未写入任何文档**。

`S4` 把这件事实固化成了一条可执行断言：它被刻意设计成「**必须失败才算通过**」——
自然时钟下结果不一致，即证明该前提真实存在、不可省略。

若某天 `S4` 报了 FAIL（自然时钟下竟然一致），说明前提已不成立，应同步修正文档。

> **结论**：任何对外宣称"可复现"的材料，都必须同时声明
> "**须先注入虚拟时钟**"这一前提。否则客户接入后第一次复跑就会发现结果不一致。

---

## 判据的两层

| 层 | 比什么 | 适用 |
|---|---|---|
| **逐比特** | `snapshot` 完整 SHA256 | 同一解释器 + 平台（回归、CI） |
| **容差** | 关键标量，`1e-9` | 跨解释器版本、跨操作系统 |

`conformance_vectors.json` 的 `meta.snapshot_sha256_scope` 明确记录了逐比特层的适用范围
与生成环境，避免把平台相关的结果当成通用结论。

---

## 向量

`conformance_vectors.json` 内含 8 组标准向量，覆盖主要情绪动力学区间：

| ID | 名称 | 覆盖 |
|---|---|---|
| V01 | baseline_calm | 中性基线 |
| V02 | trust_building | 正向信任建立 |
| V03 | shame_denial | 羞耻 + 否认机制 |
| V04 | betrayal_collapse | 背叛 / 信任崩塌 |
| V05 | trauma_accumulation | 创伤累积 |
| V06 | long_isolation | 长期隔离 + 长时间空转 |
| V07 | sleep_dream | 睡眠 / 梦境加工 |
| V08 | dissonance_expectation | 认知失调 + 预期系统 |

每个向量由 `steps` 描述（`event` / `idle` / `sleep` / `expect` / `dissonance`），
执行器按序回放后取 `snapshot`。

### 新增向量

在 `conformance_vectors.json` 的 `vectors` 数组里追加一项，填好 `id` / `name` / `steps`
（`scalars` 可留空），然后重算基线：

```bash
python tests/run_conformance.py --update-baseline
```

**注意**：`--update-baseline` 会以当前引擎为准重写期望值。它只能用于**新增向量**；
若用它覆盖已有向量的期望值来"让测试变绿"，等同于删除测试。已有向量的期望值**不应**
随引擎改动而变动——一旦不等，就是引擎行为发生了变化，那正是本套件要捕捉的信号。

---

## 设计边界

本套件只覆盖**确定性内核**，不含以下内容：

- **LLM 层**：`OpenAIAdapter` / `ClaudeAdapter` / `ChainAdapter` 的输出是概率性的，
  天然不可复现。若要评测该层，应使用独立的红队 / 基准测试（如 Project Moonshot），
  且不与应用本体的确定性套件混用同一份结论。
- **审计日志完整性**：`AuditLogger` 的哈希链需单独验证。
- **接口连通性**：属集成范畴，由接入方自行验证。

本套件同时以 `audit_enabled=False` 构造引擎实例，**不写 `logs/`**，保证运行零副作用。

---

## 文件

| 文件 | 作用 |
|---|---|
| `run_conformance.py` | 执行器（零依赖，可直接运行） |
| `conformance_vectors.json` | 标准向量 + 期望值 + 生成环境元数据 |
| `README.md` | 本文件 |
