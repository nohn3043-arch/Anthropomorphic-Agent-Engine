<p align="center">
  <img src="assets/banner.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/agent-D4AF37?style=flat-square" alt="agent">
  <img src="https://img.shields.io/badge/psychology-D4AF37?style=flat-square" alt="psychology">
  <img src="https://img.shields.io/badge/spl-v8.0-D4AF37?style=flat-square" alt="spl-v8.0">
</p>

<blockquote align="center">
  <em>拟人心理 · SPL Pure Core V8.0</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ 关于

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">ANTHROPOMORPHIC-AGENT-ENGINE 是基于 SPL Pure Core V8.0 的拟人心理引擎。它将认知、情绪、动机与社交建模为可组合子系统，赋予 AI 智能体拟人化的内在状态与一致人格，使其在长期互动中呈现自洽、可信、具情感可信度的行为。</p>

<p align="center">
  <img src="assets/overview.svg" alt="ANTHROPOMORPHIC-AGENT-ENGINE overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 快速开始

```bash
# 主源：GitHub
git clone https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine.git
# 镜像：Gitee（本仓库）
# git clone https://gitee.com/sjiun/Anthropomorphic-Agent-Engine.git
cd Anthropomorphic-Agent-Engine
# 纯 Python ≥3.8——仅标准库，无需安装
python "SPL-anthropic-engine.py"   # 运行引擎 / 内置演示
```

### 从 PyPI 安装

引擎也已发布到 PyPI，包名 [`spl-agent-engine`](https://pypi.org/project/spl-agent-engine/)：

```bash
pip install spl-agent-engine==0.1.0
```

```python
from spl_agent_engine import SPLPureCoreV7_3
core = SPLPureCoreV7_3()
core.process_vector({"belonging": 0.5, "threat": -0.1}, 1.0)
print(core.snapshot())
```

<p align="center">— ✦ —</p>

## ✦ 核心内容 — SPL Pure Core V8.0

<div style="max-width:880px;margin:0 auto;padding:0 16px">

引擎将通用人类心智架构建模为确定性、连续状态子系统——无 LLM、无随机性、完全可重放：

- **8 维情绪流体**——喜悦 / 愤怒 / 恐惧 / 信任 / 疏离 / 张力 / 愧疚 / 羞耻，每维为带自身目标与基线的连续状态。
- **创伤与记忆**——创伤节点、记忆再巩固、艾宾浩斯式遗忘、压抑–回弹与内隐压力雪崩。
- **信任与关系**——信任容量腐蚀（慢性冷遇使 `max_trust` 衰减）。
- **心智代谢**——兴奋–唤醒、动态黏度、心理时间、能量–疲劳代谢，以及用于测试与重放的虚拟时钟。
- **V8.0 扩展**——慢变量*情绪*层、独立于愧疚的*羞耻*维度、自尊动力学、睡眠 / 梦境处理（REM 巩固 + 恐惧消退 + 睡眠债）、*预期*系统（希望 / 焦虑 / 失望）、认知失调，以及扩展防御机制（否认 / 合理化 / 置换）。

</div>

## ✦ 可组合模块

<div style="max-width:880px;margin:0 auto;padding:0 16px">

| 模块 | 文件 | 职责 |
|---|---|---|
| 叙事映射器 | `SPL-anthropic-engine.py` | 外部、可替换的人格层（乐观 / 偏执 / 厌世），将事件翻译为内感受向量。 |
| 身份引擎 | `feature/Identity module.py` | 多身份模型；身份冲突注入持续基线张力。 |
| 目标 / 价值 / 偏见 / 世界 | `feature/*.py` | 可组合驱力、估值、认知偏见与世界模型先验。 |
| 语言风格渲染 | `feature/language style.py` | 将内部状态翻译为"角色该怎么说话"的风格指令 / 台词渲染。 |
| 对话演示服务 | `feature/spl-chat-server.py` | 零依赖本地对话服务（标准库 http.server），可选人格直接对话。 |

</div>

<p align="center">— ✦ —</p>

## ✦ 使用

<div style="max-width:880px;margin:0 auto;padding:0 16px">

引擎文件按设计使用连字符命名，直接加载（或作为脚本运行）：

```python
import importlib.util
spec = importlib.util.spec_from_file_location("spl_core", "SPL-anthropic-engine.py")
spl = importlib.util.module_from_spec(spec); spec.loader.exec_module(spl)

core = spl.SPLPureCoreV7_3()
# 外部事件由（可替换的）人格层映射为内感受向量
vec = spl.NarrativeMapper.map_event("insult", intensity=1.0)
# 将 `vec` 馈入 `core`，随时间演化情绪 / 信任 / 创伤状态
```

</div>

<p align="center">— ✦ —</p>

## ✦ 项目结构

```
ANTHROPOMORPHIC-AGENT-ENGINE/
├── SPL-anthropic-engine.py     # 核心引擎 + NarrativeMapper
├── feature/                    # Goal / Identity / value / world / bias / language-style 模块
│   ├── spl-chat-server.py      # 本地对话演示服务（零依赖）
│   └── language-style-demo.py  # 台词风格渲染演示
├── sujin-demo/                 # 参考演示素材
├── assets/                     # banner.svg, overview.svg
└── docs/index.html
```

<p align="center">— ✦ —</p>

## ✦ 在线演示

<p align="center">
  <a href="https://www.nohnlins.com/your-soulmate/">
    <img src="https://img.shields.io/badge/Live%20Demo-nohnlins.com%2Fyour--soulmate-D4AF37?style=for-the-badge" alt="Live Demo">
  </a>
</p>

交互式演示：**<https://www.nohnlins.com/your-soulmate/>**

<p align="center">— ✦ —</p>

## ✦ 未成年合规保护版（minor-protection）

面向 **未成年人（&lt;18）情感陪伴**场景的合规弱化变体，位于 `minor-protection/`，零第三方依赖（纯标准库）。它把主引擎 `SPLPureCoreV7_3` 做**机制级降险**而非输出端加壳，并内建一套可演示的未成年合规骨架。

> ⚠️ 合规声明：本目录为**研究 / 演示用合规骨架**，用于展示未成年人情感陪伴所应具备的保护能力与数据机制；正式对外提供服务前，须完成法务审查、DPIA / 安全评估 / 算法备案，并接入真实监护人通知通道与地区化危机资源。

### 与主引擎的差异（机制降险）

| 维度 | 主引擎 `SPL-anthropic-engine.py` | 未成年版 `minor-protection/` |
|---|---|---|
| 创伤节点 / 创伤累积 | 建模 | 移除（不模拟创伤） |
| 爆发机制（压抑-反弹 / 隐压雪崩 / 否认-现实侵入） | 建模 | 移除，代之以温和泄放 |
| 羞耻对自尊侵蚀 | 完整 | 增益 ×0.4，阈值抬升至 0.7 |
| 负面情绪钳位 | 1.0 | 0.75 |
| 依恋 / 信任封顶 | 1.0 | 0.8 |
| 自尊下限 | 0.0 | 0.15（负向冲击 ×0.5） |
| 人格选项 | 全 | 不含 intimate / confrontational |

### 四层保护

- **L0 年龄识别 + 监护人同意**：首会话强制选择年龄段；不满 14 周岁须监护人知情同意（`/api/consent`），记录同意时间戳与关系声明，并勾选服务协议 / 隐私告知。
- **L1 输入守门**：红线词库（自伤自杀 / 暴力暴恐 / 违法诱导 / 隐私套取 / 未成年亲密告白）命中 → 硬中断 + 危机话术（`gate_crisis`）。
- **L2 引擎弱化**：见上表机制降险。
- **L3 危机信号**：`protective.risk_level == HIGH` → 关怀话术 + 监护人通知标记 + webhook 回调 + 转介统计（`_guardian_notify`）。

### 合规能力清单（对照条文 / 法域）

| 能力 | 对应条款 / 法域 | 实现 |
|---|---|---|
| 年龄识别 + &lt;14 岁监护人同意 | 《办法》第14/17条 · COPPA | `/api/consent` |
| 监护人 / 紧急联系人登记 | 《办法》第12条 | `/api/guardian/register` |
| 危机真实通知（webhook / 短信 / 邮件） | 《办法》第13条 | `_guardian_notify` + `_post_webhook` |
| 危机转介统计（年度报告聚合） | CA/CO/GA/OR/WA | `/api/referrals` + `referrals.jsonl` |
| AI 生成标识（每小时） | 《办法》第18条 · CT/GA/HI/WA | `AI_DISCLOSE_INTERVAL=3600` |
| 现实提醒 / 时长限制 | 《办法》第14/18条 | 会话级 banner + rest_hint |
| 数据复制 / 删除 / 留存期清理 | 《办法》第16条 · GDPR Art.17 | `/api/export` `/api/delete` `cleanup_expired_logs` |
| 输入守门 + 输出守门 | 《办法》第8/13条 | `gate_crisis` + `gate_output` |
| 便捷退出 | 《办法》第19条 | `/api/logout` |
| 服务协议 + 儿童隐私告知 | 《办法》第12条 · COPPA | `/api/terms` |
| 申诉 / 举报入口 | 《办法》第21条 | `/api/complain` |
| 日志脱敏落盘 | 《办法》第16/17条 | `_mask` |
| 适用性披露 | CA SB 243 | 新会话首条 banner |

### 运行

```bash
cd minor-protection
python "SPL-anthropic-minor-server.py"     # 默认 http://localhost:8788
```

主要 API：

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/chat` | POST | 对话（自动走四层保护） |
| `/api/consent` | POST | 年龄确认 + 监护人同意 + 协议勾选 |
| `/api/guardian/register` | POST | 登记监护人 / 紧急联系人（webhook 等） |
| `/api/guardian/block` | POST | 监护人屏蔽角色 |
| `/api/state` | GET | 监护人使用概览 |
| `/api/export` `/api/delete` | GET/POST | 数据复制 / 删除 |
| `/api/logout` | POST | 便捷退出 |
| `/api/terms` | GET | 服务协议与隐私告知 |
| `/api/referrals` | GET | 危机转介统计 |
| `/api/complain` | POST | 申诉 / 举报 |

### 已知边界与合规声明

- 年龄与监护人同意目前为**用户自报 + 声明**，未接权威身份 / 监护人验证——正式商用须接入实名与监护人核验。
- 危机热线索引可配置（环境变量 `SPL_MINOR_CRISIS_HOTLINE`，默认 12356，可改 988 等）。
- 输出守门针对内置占位台词与接入方 LLM 产出一致生效；接真实 LLM 时建议再叠加服务端内容审核。
- 本版为合规能力骨架，不代表已完成法域内全部监管义务。

<p align="center">— ✦ —</p>

## ✦ 生态

ANTHROPOMORPHIC-AGENT-ENGINE 是 NOHN AI 生态的一员——围绕第二视角因果审计与确定性执行构建的项目家族：

| 项目 | 仓库 | 定位 |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | 全局认知审计引擎——五算子因果审计内核（IMDA 95/100） |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective)（`Intelligent-Decision-Hub--Nomos` 分支） | 可审计确定性决策中心（IMDA 95/100） |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | 硬件因果审计可信计算单元（TCU） |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | 虚拟世界与元宇宙基础设施（宪法 / 法律 / 桥梁） |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | 长篇叙事一致性引擎 |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0——带因果审计的联邦稳定互操作协议 |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | 确定性拟人心理引擎（SPL Pure Core V8.0） |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI 生态官方落地页 |

<p align="center">— ✦ —</p>

## ✦ 许可与授权

本仓库**非开源**，采用双轨模式：个人非商业研究免费；政府 / 企业需付费商业授权。详见 [LICENSE](./LICENSE) 完整条款——许可人与适用法律按用户所在地确定。

- **申请授权**：国际 / 全球 — [ai@nohnlins.com](mailto:ai@nohnlins.com) · 中国 — [lin@secondai.top](mailto:lin@secondai.top)

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTHROPOMORPHIC-AGENT-ENGINE</sub></p>
