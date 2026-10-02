# 回归测试套件

SPL Pure Core V8.0 的测试套件。零依赖（仅 Python 标准库），克隆仓库即可运行。

套件分两层，互补而非重复：

| 层 | 入口 | 回答的问题 | 判据形态 |
|---|---|---|---|
| **S（确定性）** | `run_conformance.py` | 同一输入能否逐比特复现？ | 快照 SHA256 + 标量容差 |
| **R（语义契约）** | `run_regression.py` | 该发生的事有没有发生？ | 可读断言，逐条命名 |

两层缺一不可：哈希能发现"行为变了"，但它是黑箱，说不出**为什么**变；
R 组把契约写成可读断言使变化可归因，但也无法替代逐比特重放。

---

## 快速开始

```bash
python tests/run_regression.py                      # S + R 全跑，CI 门禁用这个
python tests/run_regression.py --only R3            # 只跑某一组
python tests/run_regression.py --skip-conformance   # 只跑 R 组
python tests/run_regression.py --out-dir ./reports  # 另存汇总

python tests/run_conformance.py                     # 只跑 S 组
python tests/run_conformance.py --verbose
```

退出码：`0` = 全部通过；`1` = 存在失败。

实测（Python 3.13.14 / win32，8 向量）：

```
  S1-S4  确定性 / 可重放性               PASS       25/25
  R1     防御机制语义契约                 PASS       13/13
  R2     审计状态转移归因                 PASS       33/33
  R3     心境受迫-阻尼动力学              PASS       23/23
  R4     未成年变体对齐                   PASS       42/42
  R5     规范与实现一致                   PASS       70/70
  R6     变异守卫（断言判别力）              PASS       10/10

  断言合计: 216/216 passed
```

---

## S 组：确定性与可重放性

被测声明（README `§Core`）：

> "The engine models the general human mental architecture as deterministic,
> continuous-state subsystems — **no LLM, no randomness, fully replayable**"

| 编号 | 名称 | 断言 |
|---|---|---|
| **S1** | bit-exact replay | 注入虚拟时钟后，每个向量的 `snapshot` SHA256 必须与基线**逐比特相同** |
| **S2** | repeat stability | 同一向量连跑 3 次，3 次哈希必须全同——证明没有隐藏状态在实例之间泄漏 |
| **S3** | scalar tolerance | 关键标量按 `1e-9` 容差比对。哈希对解释器/平台敏感，标量比对用于**跨环境复核** |
| **S4** | clock premise | **负向测试**：不注入时钟时，同一向量两次运行的结果**必须不同** |

### ⚠️ 时钟前提（本套件最重要的产出）

引擎的 `_now()` 在 `_clock_override is None` 时回落到 `time.time()`：

```python
def _now(self) -> float:
    if self._clock_override is not None:
        return self._clock_override
    return time.time()
```

因此：**可复现性只在显式调用 `set_clock()` 之后成立。**

`S4` 把这件事实固化成可执行断言：它被刻意设计成「**必须失败才算通过**」。

> **结论**：任何对外宣称"可复现"的材料，都必须同时声明
> "**须先注入虚拟时钟**"这一前提。否则客户接入后第一次复跑就会发现结果不一致。

### 另一个必须知道的前提

`set_clock()` **只改虚拟时钟源，不改 `last_time`**（后者是构造时的真实墙钟）。
因此注入时钟后的**首次**时间推进会算出负 `dt` 并直接早退——即"墙钟到合成原点"
之间的间隔不被结算。这是预期行为（否则会积分数年空白），但**必须显式声明**。

`run_conformance.py` 不做同步（其基线已包含该行为）。R 组通过
`_harness.fresh()` 同步 `last_time`，否则测的是错的区间。

---

## R 组：语义契约

| 编号 | 文件 | 覆盖的契约 | 断言数 |
|---|---|---|---|
| **R1** | `test_defense.py` | 被否认/被合理化的部分**真正扣除**并进入情绪流体（规范 §8.5） | 13 |
| **R2** | `test_audit_delta.py` | 审计记录携带逐字段 `delta`；数值附差值、非数值不伪造（§7.4） | 33 |
| **R3** | `test_mood_dynamics.py` | 心境为受迫-阻尼系统；步长一致性量化界（§8.2/§8.3） | 23 |
| **R4** | `test_minor_variant.py` | 未成年变体与主引擎同算法；`protective` 合规字段进入 delta | 42 |
| **R5** | `test_doc_contract.py` | `docs/agent-standard.md` 与实现不漂移 | 70 |
| **R6** | `test_mutation_guard.py` | **断言本身具有判别力** | 10 |

### R6：为什么需要变异守卫

"测试通过"只有在"**把被测行为改坏后测试变红**"时才是证据。否则断言可能恒真——
它同样会通过，却什么也没测到。

R6 从当前引擎派生 4 个变体并注入缺陷，然后要求对应测试**必须失败**：

| 变体 | 注入的缺陷 | 必须失败的测试 |
|---|---|---|
| `defense_no_attenuation` | 防御输出不再进入情绪流体 | `test_defense.py` |
| `audit_no_delta` | `process_vector` 不再记录 delta | `test_audit_delta.py` |
| `mood_fixed_step` | 松弛步长退回每步固定常数 | `test_mood_dynamics.py` |
| `mood_constant_rate` | 收敛速率退回常数 | `test_mood_dynamics.py` |

变体通过纯文本替换注入，且要求每处替换**恰好命中一次**，否则中止——
确保注入的是"确定的那个缺陷"，不会误伤。

> **它已经抓到过一次。** `mood_constant_rate` 曾无法让 R3 变红，因为 R3 当时
> 用 `k = MOOD_RATE_BASE * (1 + GAIN * arousal_recent)` 复述公式来断言
> "速率随事件变化"——把实现里的 `k` 改成常数，该断言照样通过。
> 现已改为**行为判据**：固定初始状态与靶标、仅改变 `arousal_recent`，
> 观测松弛速度差。

> **写新断言时的规矩**：不要用"读实现常量、按公式算一遍、再断言公式成立"
> 的方式测试——那对公式改动恒真。要观测**行为**：给定输入，状态怎么变。

### R5 的边界

R5 校验的是"**文档与代码同步**"，不是"语义正确"。文档与实现同时写错时
R5 照样通过。语义正确性由 R1–R4 负责；R1 中那条承重断言（防御输出确实
到达 `_vector_to_fluid`）一旦为假，① 与"防御降低背景心境底噪"同时失效。

---

## 向量

`conformance_vectors.json` 内含 8 组标准向量：

| ID | 名称 | 覆盖 |
|---|---|---|
| V01 | baseline_calm | 中性基线 |
| V02 | trust_building | 正向信任建立 |
| V03 | shame_denial | 羞耻 + **否认机制** |
| V04 | betrayal_collapse | 背叛 / 信任崩塌 |
| V05 | trauma_accumulation | **创伤累积** + 否认 |
| V06 | long_isolation | 长期隔离 + 长时间空转 |
| V07 | sleep_dream | 睡眠 / 梦境加工 |
| V08 | dissonance_expectation | 认知失调 + 预期系统 |

**防御路径由 V03/V04/V05 覆盖**（其 `denial_load` / `suppression_load`
在修复前后发生过显著变化即为证据）；V06/V07/V08 不含负性事件，
不触及防御路径——这是覆盖分布的事实，不是缺陷。

### 新增向量

在 `vectors` 数组追加一项（`id` / `name` / `steps`，`scalars` 可留空），然后：

```bash
python tests/run_conformance.py --update-baseline
```

**注意**：`--update-baseline` 以当前引擎为准重写期望值。它只应用于**新增向量**；
若用它覆盖已有向量的期望值来"让测试变绿"，等同于删除测试。

---

## 基线的性质：检测器，不是判据

更新基线后，一致性套件能证明"行为变了"，**不能**证明"新行为对"。
用它测旧引擎会得到 S1 0/8——它对变更敏感，但与被验收对象同源。

> 所以语义正确性不能依赖基线自证，必须靠 R 组断言 + 外部反事实实验
> （同一脚本化序列下比较完整内核 / 机制裁剪 / 恢复创伤但只加输出过滤，
> 用人的判断做外部裁决）。

## 设计边界

- **LLM 层**：`OpenAIAdapter` / `ClaudeAdapter` / `ChainAdapter` 的输出是概率性的，
  天然不可复现。若要评测该层，应使用独立的红队 / 基准测试，不与本套件
  混用同一份结论。
- **接口连通性**：属集成范畴，由接入方验证。
- **合规端点**：属 `minor-protection` 服务层范畴。

两个套件都以 `audit_enabled=False` 构造引擎（仅 R2/R4 显式开启并写临时目录），
运行期不污染 `logs/`。

---

## 文件

| 文件 | 作用 |
|---|---|
| `run_regression.py` | **总入口**（S + R），CI 门禁 |
| `run_conformance.py` | S 组执行器（确定性） |
| `_harness.py` | 共用测试台：路径注入、时钟对齐、断言收集器 |
| `test_defense.py` | R1 防御机制语义契约 |
| `test_audit_delta.py` | R2 审计状态转移归因 |
| `test_mood_dynamics.py` | R3 心境受迫-阻尼动力学 |
| `test_minor_variant.py` | R4 未成年变体对齐 |
| `test_doc_contract.py` | R5 规范与实现一致 |
| `test_mutation_guard.py` | R6 变异守卫（断言判别力） |
| `conformance_vectors.json` | 标准向量 + 期望值 + 生成环境元数据 |
| `README.md` | 本文件 |

每个 R 文件都可独立运行：`python tests/test_defense.py`。
