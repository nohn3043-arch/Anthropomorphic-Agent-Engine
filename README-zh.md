<p align="center">
  <img src="https://img.shields.io/badge/anthropomorphic-ai-D4AF37?style=flat-square" alt="anthropomorphic-ai">
  <img src="https://img.shields.io/badge/spl-pure--core-v8.0-D4AF37?style=flat-square" alt="spl-pure-core-v8.0">
  <img src="https://img.shields.io/badge/personality-engineering-D4AF37?style=flat-square" alt="personality-engineering">
  <img src="https://img.shields.io/badge/agent-D4AF37?style=flat-square" alt="agent">
</p>

<blockquote align="center">
  <em>确定性拟人心理学引擎 · SPL Pure Core V8.0</em>
</blockquote>

<p align="center">
[English](README.md) | 简体中文
</p>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ 关于

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">
<strong>拟人 Agent 引擎（Anthropomorphic Agent Engine）</strong>，代号 <strong>SPL Pure Core V8.0</strong>——一个完全确定性的拟人化心理模拟引擎。它不是概率式的聊天机器人，而是一套<strong>人格工程系统</strong>：通过分层心理架构（自我 / 情感 / 认知 / 记忆 / 价值观）、状态机驱动的情绪响应、注意力与感知门控、以及记忆巩固与遗忘机制，构建一个可预测、可审计、可配置的「人格内核」。
</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">
每一次情绪反应、每一个决策、每一段记忆，都有可追溯的因果链。相同的输入 + 相同的初始状态 = 完全相同的输出。
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 核心思想

- **确定性而非概率** —— 输出由状态 + 规则严格决定，没有随机性，可复现。
- **分层而非扁平** —— 心理活动按层次组织（感知 → 注意 → 情感 → 认知 → 决策 → 行动），层间有清晰接口。
- **动态而非静态** —— 情绪会衰减、记忆会巩固、关系会演化，一切随时间变化。
- **可审计而非黑盒** —— 每次状态变更都有原因可追溯，支持第二视角因果审计。
- **可配置而非固定** —— 人格参数可通过配置文件调整，快速塑造不同性格。
- **自主而非被动** —— 有内在动机与需求驱动，不只是响应外部输入。

<p align="center">— ✦ —</p>

## ✦ 架构

```
┌─────────────────────────────────────────────────────┐
│                  人格内核（Self Core）                │
│          自我意识  ·  身份认同  ·  存在叙事            │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│  情感层   │  认知层   │  记忆层   │  价值观层  │  动机层  │
│ 情绪状态 │ 思维模式 │ 长/短/工作│ 道德判断  │ 需求驱动 │
│ 心境背景 │ 推理策略 │ 巩固/遗忘│ 优先级    │ 目标设定 │
│ 表情生成 │ 注意力   │ 联想检索  │ 信念体系  │ 意志强度 │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│                  感知 / 行动 接口层                   │
│    感知门控  ·  注意力分配  ·  行动输出  ·  语言生成    │
├─────────────────────────────────────────────────────┤
│                  时间 / 能量系统                      │
│         生物钟  ·  精力值  ·  疲劳  ·  恢复            │
├─────────────────────────────────────────────────────┤
│                  因果审计层（可插拔）                  │
│      叙事剥离  ·  假设透视  ·  状态锚定  ·  责任追溯    │
└─────────────────────────────────────────────────────┘
```

<p align="center">— ✦ —</p>

## ✦ 快速开始

```bash
# 主仓库：GitHub
git clone https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine.git
# 镜像：Gitee
# git clone https://gitee.com/nohn-ecosystem/your-soulmate.git
cd Anthropomorphic-Agent-Engine
pip install -r requirements.txt          # 仅需标准库，无额外依赖
python demo.py                           # 交互式对话演示
```

## 使用示例

```python
from spl_core import PersonalityEngine, PersonalityProfile

# 定义人格（五维 + 子维度）
profile = PersonalityProfile({
    "openness": 0.72,          # 开放性
    "conscientiousness": 0.68, # 尽责性
    "extraversion": 0.45,      # 外向性
    "agreeableness": 0.81,     # 宜人性
    "neuroticism": 0.35,       # 神经质
    "sub": {
        "trust": 0.88,
        "altruism": 0.82,
        "compliance": 0.75,
        "modesty": 0.62,
        "tender_mindedness": 0.80,
    }
})

# 创建引擎
agent = PersonalityEngine(profile, name="阿雅斯", gender="female")

# 感知输入 → 内部处理 → 行动输出
stimulus = {"type": "speech", "source": "用户", "content": "你今天过得怎么样？", "emotion": "friendly"}
response = agent.perceive(stimulus).think().act()
print(response["text"])
print(f"情绪：{response['emotion']}（强度 {response['intensity']:.2f}）")

# 时间推进 → 情绪自然衰减
agent.tick(minutes=30)
```

<p align="center">— ✦ —</p>

## ✦ 核心模块

| 模块 | 说明 |
|---|---|
| **self/** | 自我意识内核 —— 身份叙事、自我概念、存在状态 |
| **emotion/** | 情感系统 —— 基本情绪（喜/怒/哀/惧/惊/厌）、复杂情绪（羞愧/内疚/骄傲…）、心境背景、表情映射 |
| **cognition/** | 认知系统 —— 注意力、感知门控、思维模式、推理策略、启发式与偏差（可配置） |
| **memory/** | 记忆系统 —— 感觉登记 / 工作记忆 / 短期记忆 / 长期记忆 / 情节记忆 / 语义记忆；巩固、遗忘、联想检索 |
| **values/** | 价值观系统 —— 道德判断、信念体系、优先级排序、认知失调处理 |
| **motivation/** | 动机系统 —— 需求层级（生理/安全/归属/尊重/自我实现）、目标设定、意志强度、延迟满足 |
| **perception/** | 感知系统 —— 多通道输入（言语/视觉/听觉/触觉）、门控、注意力分配 |
| **action/** | 行动系统 —— 语言生成、情绪表达、行为决策、动作序列 |
| **temporal/** | 时间系统 —— 生物钟、精力/疲劳、睡眠周期、长期老化 |
| **audit/** | 因果审计（可插拔）—— 与第二视角 GCAE 集成，全链路可追溯 |

<p align="center">— ✦ —</p>

## ✦ 确定性保证

引擎输出完全由以下因素决定，不含任何随机源：

1. **初始人格配置**（`PersonalityProfile`）
2. **当前内部状态**（情绪 / 记忆 / 精力 / 关系…）
3. **外部输入序列**（感知刺激的顺序与内容）
4. **时间推进量**（tick 数）

给定完全相同的这四项，输出位对位一致。

- **可复现 bug 报告** —— 只需附带初始配置 + 输入序列 + tick 数。
- **可审计决策** —— 每次状态变更都登记因果链，支持事后追溯。
- **无「幻觉」** —— 不会产生配置与输入之外的内容。

<p align="center">— ✦ —</p>

## ✦ 与 LLM 的关系

本引擎 **不包含** 任何大型语言模型。它是一个纯规则的心理状态机。两种典型用法：

| 模式 | 说明 |
|---|---|
| **独立运行** | 直接用内置语言模板生成响应；适合嵌入式 / 低资源 / 强可审计场景 |
| **LLM 增强** | 将引擎的内部状态（情绪 / 记忆 / 意图）作为上下文注入 LLM，由 LLM 负责自然语言生成，引擎负责人格一致性与因果审计 |

LLM 增强模式下，引擎扮演「人格控制器 + 审计闸门」的角色：

```
用户输入 → [感知层] → [情感/认知/记忆/动机] → 意图 + 情绪状态 → [LLM] → 自然语言 → [审计校验] → 输出
                                    ↑                                              ↓
                                    └──── 记忆巩固 / 情绪更新 / 关系演化 ────────────┘
```

<p align="center">— ✦ —</p>

## ✦ 配置人格

见 [`personalities/`](personalities/) 目录中的示例：

- `default.json` —— 默认中性人格
- `ayas.json` —— 阿雅斯（温柔知性型）
- `marcus.json` —— 马库斯（理性严谨型）
- `lin.json` —— 林（活泼好奇型）

自定义人格：复制任一模板，调整各维度数值（0.0 – 1.0）即可。

<p align="center">— ✦ —</p>

## ✦ 项目结构

```
Anthropomorphic-Agent-Engine/
├── spl_core/
│   ├── __init__.py
│   ├── engine.py              # 主引擎 PersonalityEngine
│   ├── profile.py             # 人格配置 PersonalityProfile
│   ├── self/                  # 自我意识内核
│   ├── emotion/               # 情感系统
│   ├── cognition/             # 认知系统
│   ├── memory/                # 记忆系统
│   ├── values/                # 价值观系统
│   ├── motivation/            # 动机系统
│   ├── perception/            # 感知系统
│   ├── action/                # 行动系统
│   ├── temporal/              # 时间系统
│   └── audit/                 # 因果审计（与 GCAE 集成）
├── personalities/             # 预置人格模板
├── demo.py                    # 交互式演示
├── tests/                     # 单元测试
├── requirements.txt
└── README.md
```

<p align="center">— ✦ —</p>

## ✦ 生态

Anthropomorphic Agent Engine 是 NOHN AI 生态的一员 —— 围绕第二视角因果审计与确定性执行构建的项目家族：

| 项目 | 仓库 | 定位 |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | 全球认知审计引擎 —— 五算子因果审计核心（IMDA 95/100） |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective)（`Intelligent-Decision-Hub--Nomos` 分支） | 可审计确定性决策中心（IMDA 95/100） |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | 硬件因果审计可信计算单元（TCU） |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | 虚拟世界与元宇宙基础设施（宪法 / 法律 / 桥梁） |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | 长篇叙事一致性引擎 |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 —— 带因果审计的联邦稳定互操作协议 |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | 确定性拟人心理学引擎（SPL Pure Core V8.0） |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI 生态官方落地页 |

<p align="center">— ✦ —</p>

## ✦ 许可与授权

本仓库 **不是开源软件**。双轨模式：个人非商业研究免费；政府 / 企业使用需付费商业许可。详见 [LICENSE](./LICENSE)。

| 用户 | 用途 | 许可要求 |
|---|---|---|
| 个人（自然人） | 非商业学术研究 / 学习 / 个人实验 | **免费**，依据 [LICENSE](./LICENSE) 中「个人免费研究许可」 |
| 政府机构 / 事业单位 / 企业 | 任何用途（含内部部署、产品开发、服务提供） | **必须事先签署付费商业许可** |

- **个人研究者** 可免费用于非商业研究，但不得用于任何商业目的，也不得向任何企业或政府机构提供服务。
- **政府 / 企业用户** 在签署商业许可协议并支付约定费用前，不得复制、部署、运行、集成或分发本作品。
- **许可申请**：国际 / 全球 — [ai@nohnlins.com](mailto:ai@nohnlins.com) · 中国 — [lin@secondai.top](mailto:lin@secondai.top)

许可方、适用法律与争议解决依用户所在地按 [LICENSE](./LICENSE) 执行：中国境内 → 上海林明钧华科技有限公司（适用中国法律）；中国境外 → NOHN AI TECHNOLOGY PTE. LTD.（适用新加坡法律，SIAC 仲裁）。

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTHROPOMORPHIC AGENT ENGINE</sub></p>
