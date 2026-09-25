<p align="center">
  <img src="assets/banner.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE 横幅" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/agent-D4AF37?style=flat-square" alt="agent">
  <img src="https://img.shields.io/badge/psychology-D4AF37?style=flat-square" alt="psychology">
  <img src="https://img.shields.io/badge/spl-v8.0-D4AF37?style=flat-square" alt="spl-v8.0">
</p>

<blockquote align="center">
  <em>拟人心理 · SPL Pure Core V8.0</em>
</blockquote>

<p align="center">
[English](README.md) | 简体中文
</p>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ 关于

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">ANTHROPOMORPHIC-AGENT-ENGINE 是一个构建于 SPL Pure Core V8.0 之上的拟人心理引擎。它将认知、情绪、动机与社会行为建模为可组合的子系统，赋予 AI 智能体类人的内部状态与一致人格，从而在长期交互中产生自洽、可信、有情感共鸣的行为。</p>

<p align="center">
  <img src="assets/overview.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE 概览" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 快速开始

```bash
# 主仓库：GitHub
git clone https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine.git
# 镜像：Gitee
# git clone https://gitee.com/sjiun/Anthropomorphic-Agent-Engine.git
cd Anthropomorphic-Agent-Engine
# 纯 Python ≥3.8 —— 仅用标准库，无依赖
python "SPL-anthropic-engine.py"   # 运行引擎 / 内置演示
```

### 从 PyPI 安装

该引擎也已发布至 PyPI：[`spl-agent-engine`](https://pypi.org/project/spl-agent-engine/)：

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

## ✦ 内核 —— SPL Pure Core V8.0

<div style="max-width:880px;margin:0 auto;padding:0 16px">

该引擎将人类通用心智架构建模为确定性的连续状态子系统 —— 无 LLM、无随机性、完全可回放。

> **可复现性前提。**"完全可回放"仅在通过 `core.set_clock(t)` 注入虚拟时钟**之后**成立。若不注入，`_now()` 会回退到 `time.time()`，同一输入序列的两次运行将产生不同结果。任何对外声称的可复现性都必须声明此前提。该前提由 [`tests/`](./tests/) 断言 —— 用例 S1–S4，其中包含一个*要求*自然时钟不可复现的反向测试。

- **八维情绪流体** —— 喜悦 / 愤怒 / 恐惧 / 信任 / 疏离 / 紧张 / 内疚 / 羞耻，各自是一个带独立目标值与基线的连续状态。
- **创伤与记忆** —— 创伤节点、记忆再巩固、艾宾浩斯式遗忘、压抑–反弹与潜在压力雪崩。
- **信任与关系** —— 信任容量侵蚀（长期忽视会衰减 `max_trust`）。
- **心智代谢** —— 兴奋–唤醒、动态黏度、心理时间、能量–疲劳代谢，以及用于测试与回放的虚拟时钟。
- **V8.0 扩展** —— 慢变量*心境*层、独立于内疚的*羞耻*维度、自尊动力学、睡眠 / 梦境处理（REM 巩固 + 恐惧消退 + 睡眠债）、*期望*系统（希望 / 焦虑 / 失望）、认知失调，以及扩展的防御机制（否认 / 合理化 / 置换）。
- **Token 计量** —— `TokenUsage` 数据类 + `TokenStats` 累加器，跨多次 LLM 调用聚合 prompt / completion / total token，含逐模型明细与 JSON 导出。`AuditLogger.log_llm_call` 会自动记录每次调用的 token 用量、时延与成败。主引擎与未成年人保护变体中均可用。

</div>

## ✦ 可组合模块

<div style="max-width:880px;margin:0 auto;padding:0 16px">

| 模块 | 文件 | 职责 |
|---|---|---|
| 叙事映射器 | `SPL-anthropic-engine.py` | 外部可替换的人格层（乐观 / 偏执 / 厌世），将事件转译为内感受向量。 |
| 身份引擎 | `feature/Identity module.py` | 多重身份模型；身份冲突会注入持续的基线紧张。 |
| 目标 / 价值 / 偏差 / 世界 | `feature/*.py` | 可组合的驱动力、价值评估、认知偏差与世界模型先验。 |
| 语言风格渲染器 | `feature/language style.py` | 将内部状态转译为"角色该如何说话"的风格指令 / 台词渲染。 |
| 聊天演示服务器 | `feature/spl-chat-server.py` | 零依赖本地聊天服务器（stdlib http.server），可选人格直接对话。 |

</div>

<p align="center">— ✦ —</p>

## ✦ 使用

<div style="max-width:880px;margin:0 auto;padding:0 16px">

引擎文件有意采用连字符命名 —— 直接加载（或作为脚本运行）：

```python
import importlib.util
spec = importlib.util.spec_from_file_location("spl_core", "SPL-anthropic-engine.py")
spl = importlib.util.module_from_spec(spec); spec.loader.exec_module(spl)

core = spl.SPLPureCoreV7_3()
# 外部事件由（可替换的）人格层映射为内感受向量
vec = spl.NarrativeMapper.map_event("insult", intensity=1.0)
# 将 `vec` 送入 `core`，随时间演化情绪 / 信任 / 创伤状态
```

### Token 计量

```python
from spl_agent_engine import TokenUsage, TokenStats

stats = TokenStats()

# 每次 LLM 调用后记录用量
usage = TokenUsage(prompt_tokens=120, completion_tokens=80,
                   total_tokens=200, model="gpt-4")
stats.record(usage)

# 汇总
print(stats.summary())
# {'call_count': 1, 'total_prompt_tokens': 120, 'total_completion_tokens': 80,
#  'total_tokens': 200, 'by_model': {'gpt-4': {...}}}

# 导出 JSON 报告
stats.export_json("token_report.json")
```

审计日志器 `AuditLogger` 也会自动记录每次 LLM 调用：

```python
logger = spl.AuditLogger(log_dir="logs")
logger.log_llm_call(model="gpt-4", prompt_preview="Hello...",
                   usage=usage, duration_ms=350.5, success=True)
```

</div>

<p align="center">— ✦ —</p>

## ✦ 项目结构

```
ANTHROPOMORPHIC-AGENT-ENGINE/
├── SPL-anthropic-engine.py     # 核心引擎（SPL Pure Core V8.0）、NarrativeMapper、
│                               #   AuditLogger / TokenStats、LLM 适配器接口
├── feature/                    # 可组合模块（集成侧配置）
│   ├── Goal module.py          #   目标图 · 冲突水平 · 情绪向量
│   ├── Identity module.py      #   身份节点 · 强度 · 冲突
│   ├── bias module.py          #   评价偏差剖面（偏执 / 乐观 / 抑郁）
│   ├── value module.py         #   核心价值观威胁 · 情绪放大
│   ├── world module.py         #   信念模型 · 预测误差
│   └── language style.py       #   LanguageStyleEngine —— 为 LLM 渲染 prompt_injection
├── tests/                      # 确定性 / 可回放性一致性套件（零依赖）
│   ├── run_conformance.py      #   运行器：python tests/run_conformance.py
│   ├── conformance_vectors.json  # 标准向量 + 期望哈希
│   └── README.md               #   套件文档，含时钟前提
├── minor-protection/           # 未成年人保护变体（年龄闸门 + 四层保护）
│   ├── SPL-anthropic-minor-engine.py
│   └── SPL-anthropic-minor-server.py
├── docs/                       # 公开规范：anthromorphic-agent-engine-standards.md
├── assets/                     # banner.svg / overview.svg（+ .png 导出）
├── sujin-demo                  # 参考演示脚本（单文件，无 LLM 调用）
├── logs/                       # 运行期审计日志（JSONL，未纳入版本控制）
├── banner.png
├── IMDA_AI_Verify_Causal_Audit_Report.pdf
└── LICENSE
```

<p align="center">— ✦ —</p>

## ✦ 在线演示

<p align="center">
  <a href="https://www.nohnlins.com/your-soulmate/">
    <img src="https://img.shields.io/badge/Live%20Demo-nohnlins.com%2Fyour--soulmate-D4AF37?style=for-the-badge" alt="Online Demo">
  </a>
</p>

交互式演示：**<https://www.nohnlins.com/your-soulmate/>**

<p align="center">— ✦ —</p>

## ✦ 未成年人保护变体

一个面向**未成年（&lt;18）情感陪伴**场景的合规缓解变体，位于 `minor-protection/`，零第三方依赖（纯标准库）。它对主引擎 `SPLPureCoreV7_3` 施加**机制级风险削减**，而非输出侧过滤，并包含一套可演示的未成年人合规框架。

> ⚠️ 合规提示：本目录是**研究 / 演示性质的合规框架**，旨在演示未成年人情感陪伴所需的保护能力与数据机制。启动生产服务前，你必须完成法律审查、DPIA / 安全评估 / 算法备案，并接入真实监护人通知渠道与地区特定的危机资源。

### 与主引擎的差异（机制级风险削减）

| 维度 | 主引擎 `SPL-anthropic-engine.py` | 未成年人变体 `minor-protection/` |
|---|---|---|
| 创伤节点 / 创伤累积 | 已建模 | 移除（不模拟创伤） |
| 爆发机制（压抑-反弹 / 潜在压力雪崩 / 否认-现实侵入） | 已建模 | 移除，替换为温和释放 |
| 羞耻对自尊的侵蚀 | 完整 | 增益 ×0.4，阈值提高至 0.7 |
| 负向情绪钳制 | 1.0 | 0.75 |
| 依恋 / 信任上限 | 1.0 | 0.8 |
| 自尊下限 | 0.0 | 0.15（负向影响 ×0.5） |
| 人格选项 | 全部 | 排除亲密 / 对抗类 |

### 四层保护

- **L0 年龄核验 + 监护人同意**：首次会话需选择年龄段；14 岁以下需监护人知情同意（`/api/consent`），记录同意时间戳与关系声明，并勾选服务协议 / 隐私告知。
- **L1 输入把关**：红线关键词库（自伤/自杀 / 暴力恐怖 / 违法诱导 / 隐私套取 / 未成年亲密告白）→ 硬中断 + 危机话术（`gate_crisis`）。
- **L2 引擎缓解**：见上方机制级风险削减表。
- **L3 危机信号**：`protective.risk_level == HIGH` → 关怀话术 + 监护人通知标记 + webhook 回调 + 转介统计（`_guardian_notify`）。

### 合规能力清单（按条款 / 法域）

| 能力 | 条款 / 法域 | 实现 |
|---|---|---|
| 年龄核验 + 14 岁以下监护人同意 | Measures Art. 14/17 · COPPA | `/api/consent` |
| 监护人 / 紧急联系人登记 | Measures Art. 12 | `/api/guardian/register` |
| 真实危机通知（webhook / 短信 / 邮件） | Measures Art. 13 | `_guardian_notify` + `_post_webhook` |
| 危机转介统计（年报聚合） | CA/CO/GA/OR/WA | `/api/referrals` + `referrals.jsonl` |
| AI 生成内容披露（每小时） | Measures Art. 18 · CT/GA/HI/WA | `AI_DISCLOSE_INTERVAL=3600` |
| 现实提醒 / 时长限制 | Measures Art. 14/18 | 会话级横幅 + rest_hint |
| 数据导出 / 删除 / 留存清理 | Measures Art. 16 · GDPR Art. 17 | `/api/export` `/api/delete` `cleanup_expired_logs` |
| 输入把关 + 输出把关 | Measures Art. 8/13 | `gate_crisis` + `gate_output` |
| 便捷登出 | Measures Art. 19 | `/api/logout` |
| 服务协议 + 儿童隐私告知 | Measures Art. 12 · COPPA | `/api/terms` |
| 申诉 / 举报入口 | Measures Art. 21 | `/api/complain` |
| 磁盘日志匿名化 | Measures Art. 16/17 | `_mask` |
| 适用性披露 | CA SB 243 | 新会话首屏横幅 |

### 运行

```bash
cd minor-protection
python "SPL-anthropic-minor-server.py"     # 默认 http://localhost:8788
```

主要 API 端点：

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/chat` | POST | 聊天（自动经四层保护路由） |
| `/api/consent` | POST | 年龄确认 + 监护人同意 + 协议勾选 |
| `/api/guardian/register` | POST | 登记监护人 / 紧急联系人（webhook 等） |
| `/api/guardian/block` | POST | 监护人拉黑角色 |
| `/api/state` | GET | 监护人用量总览 |
| `/api/export` `/api/delete` | GET/POST | 数据导出 / 删除 |
| `/api/logout` | POST | 便捷登出 |
| `/api/terms` | GET | 服务协议与隐私告知 |
| `/api/referrals` | GET | 危机转介统计 |
| `/api/complain` | POST | 申诉 / 举报 |

### 已知局限与合规免责

- 年龄与监护人同意目前为**自述 + 声明**，不含权威身份 / 监护人核验 —— 生产使用需接入实名与监护人核验。
- 危机热线号码可配置（环境变量 `SPL_MINOR_CRISIS_HOTLINE`，默认 12356，可改为 988 等）。
- 输出把关对内建占位台词与第三方 LLM 输出统一生效；接入真实 LLM 时，建议追加服务端内容审核。
- 本版本是合规能力框架，不代表已完成某一法域内的全部监管义务。

<p align="center">— ✦ —</p>

## ✦ 生态

ANTHROPOMORPHIC-AGENT-ENGINE 是 NOHN AI 生态的一员 —— 一个围绕第二视角因果审计与确定性执行构建的项目家族：

| 项目 | 仓库 | 角色 |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | 全局认知审计引擎 —— 五算子因果审计内核（IMDA 95/100） |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective)（`Intelligent-Decision-Hub--Nomos` 分支） | 可审计的确定性决策中枢（IMDA 95/100） |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | 硬件因果审计可信计算单元（TCU） |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | 虚拟世界与元宇宙基础设施（宪法 / 法律 / 桥） |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | 长篇叙事一致性引擎 |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 —— 带因果审计的联邦稳定互操作协议 |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | 确定性拟人心理引擎（SPL Pure Core V8.0） |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI 生态官方落地页 |

<p align="center">— ✦ —</p>

## ✦ 许可

本仓库**并非开源**。它采用双轨模式：个人非商业研究免费；政府 / 企业使用需付费商业许可。完整条款见 [LICENSE](./LICENSE) —— 许可方与适用法律由用户所在法域决定。

- **申请许可**：国际 / 全球 —— [ai@nohnlins.com](mailto:ai@nohnlins.com) · 中国 —— [lin@secondai.top](mailto:lin@secondai.top)

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTHROPOMORPHIC-AGENT-ENGINE</sub></p>
