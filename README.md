

# ANTHROPOMORPHIC-AGENT-ENGINE

基于 SPL Pure Core V8.0 的人形心理学引擎

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

---

## ✦ 项目简介

ANTHROPOMORPHIC-AGENT-ENGINE 是一个基于 SPL Pure Core V8.0 的人形心理学引擎。它将认知、情感、动机和社会性建模为可组合的子系统，为 AI 智能体赋予类人的内在状态和一致的人格特征，从而在长期交互中实现情感上可信、行为上连贯的表现。

该引擎将通用的人类心理架构建模为确定性、连续状态的子系统——无需 LLM，无随机性，支持完全回放：

- **八维情感流体** — 喜悦、愤怒、恐惧、信任、疏离、张力、愧疚、羞耻，每个都是具有自身目标和基线的连续状态
- **创伤与记忆** — 创伤节点、记忆再巩固、艾宾浩斯式遗忘、压抑-反弹及隐式压力雪崩
- **信任与关系** — 信任容量腐蚀（慢性冷漠对待下 `max_trust` 会衰减）
- **心智代谢** — 唤醒-激活、动态粘度、心理时间、能量-疲劳代谢，以及用于测试和回放的虚拟时钟

<p align="center">
  <img src="assets/overview.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE overview" style="width:100%">
</p>

---

## ✦ 快速开始

### 环境要求

- Python 3.8 或更高版本
- 标准库依赖，无需安装额外包

### 安装方式

#### 方式一：直接克隆运行

```bash
git clone git@github.com:NOHN-AI/ANTHROPOMORPHIC-AGENT-ENGINE.git
cd ANTHROPOMORPHIC-AGENT-ENGINE
python "SPL-anthropic-engine.py"   # 运行引擎 / 捆绑演示
```

#### 方式二：从 PyPI 安装

该引擎也已发布到 PyPI，名称为 [`spl-agent-engine`](https://pypi.org/project/spl-agent-engine/)：

```bash
pip install spl-agent-engine==0.1.0
```

安装后可使用以下代码快速测试：

```python
from spl_agent_engine import SPLPureCoreV7_3
core = SPLPureCoreV7_3()
core.process_vector({"belonging": 0.5, "threat": -0.1}, 1.0)
print(core.snapshot())
```

---

## ✦ V8.0 扩展功能

在 V8.0 版本中，引擎新增了以下高级功能：

- **慢变量情绪层** — 超越即时情感波动的长期情绪趋势
- **羞耻维度** — 与愧疚区分开的独立羞耻情感维度
- **自尊动态** — 自尊心的变化与调节机制
- **睡眠/梦境处理** — REM 巩固、恐惧消退与睡眠债务
- **预期系统** — 希望、焦虑、失望等预期情感
- **认知失调** — 认知冲突的检测与处理
- **扩展防御机制** — 否认、合理化、置换等心理防御手段

---

## ✦ 可组合模块

引擎采用模块化设计，各子系统可独立使用或组合使用：

| 模块 | 文件 | 职责 |
|------|------|------|
| 叙事映射器 | `SPL-anthropic-engine.py` | 外部可替换的人格层（乐观/偏执/厌世），将事件转换为内感受向量 |
| 身份引擎 | `feature/Identity module.py` | 多身份模型；身份冲突注入持续的基线张力 |
| 目标引擎 | `feature/Goal module.py` | 可组合的目标管理，跟踪重要性、紧迫性和难度 |
| 价值引擎 | `feature/value module.py` | 核心价值评估和情感放大系统 |
| 偏误引擎 | `feature/bias module.py` | 认知偏误配置（乐观、偏执、抑郁），调节感知和记忆 |
| 世界模型 | `feature/world module.py` | 世界先验模型（乐观、悲观、创伤），影响期望和解释 |

---

## ✦ 使用方法

### 核心 API

引擎文件使用带连字符的名称设计，可直接加载（或作为脚本运行）：

```python
import importlib.util
spec = importlib.util.spec_from_file_location("spl_core", "SPL-anthropic-engine.py")
spl = importlib.util.module_from_spec(spec); spec.loader.exec_module(spl)

core = spl.SPLPureCoreV7_3()
# 外部事件通过（可替换的）人格层映射为内感受向量
vec = spl.NarrativeMapper.map_event("insult", intensity=1.0)
# 将 `vec` 传入 `core` 以演化情感/信任/创伤状态
```

#### SPLPureCoreV7_3 — 主引擎类

| 方法 | 说明 |
|------|------|
| `process_vector(interoceptive_vec, delta_time)` | 处理内感受向量并推进时间 |
| `snapshot()` | 获取所有子系统的当前状态 |

#### NarrativeMapper — 事件向量化

| 方法 | 说明 |
|------|------|
| `map_event(event: str, intensity: float) -> Dict[str, float]` | 将自然语言事件映射为内感受向量 |

### 模块使用示例

```python
# 目标引擎
from feature.Goal module import sujin_goals
goal_engine = sujin_goals()
goal_engine.add_goal("complete_task", importance=0.8, urgency=0.6)
primary = goal_engine.get_primary_goal()

# 身份引擎  
from feature.Identity module import sujin_identity
identity_engine = sujin_identity()

# 价值引擎
from feature.value module import sujin_values
value_engine = sujin_values()
emotions = value_engine.evaluate_event("success")

# 偏误配置
from feature.bias module import paranoid_bias, optimistic_bias
bias_engine = BiasEngine(profile=optimistic_bias())

# 世界模型
from feature.world import optimistic_world, pessimistic_world
world = optimistic_world()
```

---

## ✦ 项目结构

```
ANTHROPOMORPHIC-AGENT-ENGINE/
├── SPL-anthropic-engine.py       # 核心引擎 + NarrativeMapper（主入口）
├── feature/                      # 可组合心理学模块
│   ├── Goal module.py            # 目标管理与动机系统
│   ├── Identity module.py        # 多身份与身份冲突处理
│   ├── bias module.py            # 认知偏误配置与应用
│   ├── value module.py           # 核心价值与情感放大
│   └── world module.py           # 世界模型先验与期望
├── sujin-demo/                   # 参考演示资源
├── assets/                       # 横幅和概览图
│   ├── banner.svg
│   └── overview.svg
├── docs/                         # 交互式文档
│   └── index.html
├── spl_engine_demo.ipynb         # Jupyter Notebook 演示
├── IMDA_AI_Verify_Causal_Audit_Report.pdf
├── LICENSE
└── README.md
```

---

## ✦ 架构概述

引擎遵循模块化架构，每个子系统都可以独立使用或组合在一起：

### 核心子系统

1. **SPLPureCoreV7_3** — 中央处理中枢，协调所有子系统，维护连续的情感状态，并管理时间演化

2. **NarrativeMapper** — 将外部事件（自然语言描述）转换为内核可处理的内感受向量

3. **Goal Engine** — 管理智能体目标，包括重要性、紧迫性、难度和依赖项。提供冲突检测和情感生成

4. **Identity Engine** — 建模智能体内的多身份，处理产生持续心理张力的身份冲突

5. **Value Engine** — 根据核心价值评估事件，并根据价值相关性放大情感反应

6. **Bias Engine** — 应用认知偏误配置到感知和记忆，包括偏执、乐观和抑郁偏误

7. **World Model** — 表示智能体对世界的期望，影响事件的解释方式

---

## ✦ 在线演示

<p align="center">
  <a href="https://your-soulmate.pages.dev/">
    <img src="https://img.shields.io/badge/在线演示-your--soulmate.pages.dev-D4AF37?style=for-the-badge" alt="Live Demo">
  </a>
</p>

体验交互式演示：**https://your-soulmate.pages.dev/**

---

## ✦ 许可证与授权

本仓库**并非开源软件**。采用双轨模式：个人非商业研究免费使用，政府/企业商业使用需付费授权。完整条款请参阅 [LICENSE](./LICENSE) 文件——许可人和适用法律由用户所在地决定。

---

<p align="center">
  <a href="https://github.com/NOHN-AI">NOHN-AI</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:lin@secondai.top">lin@secondai.top</a>
</p>
<p align="center"><sub>NOHN AI · ANTHROPOMORPHIC-AGENT-ENGINE</sub></p>