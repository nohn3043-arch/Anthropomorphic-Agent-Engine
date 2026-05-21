# SPL-Anthropic-Engine
Standard anthropic agent template powered by SPL audit engine. Generate high-quality AI characters in minutes with consistent personality. It eliminates OOC, irrational emotional shifts and memory loss via causal anchoring and full-logic auditing. A reliable underlying framework for AI companions, virtual humans and interactive narrative products. 

# SPL Audit Engine - 第二视角审计引擎

**为 AI 角色赋予可审计、可追溯、防失控的“逻辑骨架”**

[![License](https://img.shields.io/badge/License-Commercial%20Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)]()

## 🧠 这是什么？

SPL Audit Engine 是 **第二视角（Second‑Perspective）语言** 在 AI 角色领域的工程化实现。  
它嵌入您的虚拟角色系统，在每次生成回复、每一次情感变化时进行 **硬件级的逻辑校验**，确保角色行为始终符合预设的心理矩阵，杜绝 OOC（Out‑Of‑Character）和情感跳变。

**核心价值：**  
将“角色一致性”从玄学变成可审计、可追溯、可修复的工程问题。

---

## 🚀 主要功能

| 功能模块 | 说明 |
|----------|------|
| **实时行为审计 (AUDIT)** | 拦截不符合当前亲密度阶段的亲密称呼、生硬拒绝等 OOC 言行 |
| **因果链锚定 (ANCHOR)** | 记录关键互动事件，形成不可篡改的状态链，实现真正的长期记忆 |
| **叙事剥离 (STRIP)** | 剥离废话、修辞、情绪噪声，提取干逻辑用于一致性校验 |
| **亲密度变化审计** | 校验每次 affinity 增减的合理性，防止作弊或跳变 |
| **多维度心理矩阵** | 以 **0.5 为人类基准** 的人格维度，通过阶段系数动态放大/压抑 |
| **审计日志 & 因果链查询** | 所有异常行为留痕，运营可精确定位根因（权重问题 / 规则遗漏 / 模型幻觉） |
| **本地化部署** | 零数据回传，完全私有化，符合 GDPR / 个保法 |

---

## 📦 本地化部署 – 一口价授权

因隐私合规要求，本引擎 **仅支持本地化部署**，不收集任何用户数据。  
授权模式为 **年度订阅** 或 **永久买断**，核心交付物包括：

| 交付物 | 形式 |
|--------|------|
| SPL 审计核心库 | `.so` / `.dll` / Python wheel |
| 角色配置管理工具 | CLI + Web 控制台 |
| 审计日志分析套件 | 离线脚本 + 可视化看板 |
| 初始心理矩阵 & 规则库 | JSON / YAML 配置文件 |
| 集成文档 & 示例代码 | PDF + 示例仓库 |

**价格模型：**

| 授权模式 | 价格区间 | 适用客户 |
|----------|----------|----------|
| **年度授权** | 30 万 ~ 80 万 / 年 | 需要持续技术支持和规则更新的平台 |
| **永久授权** | 150 万 ~ 300 万 | 技术实力强，希望长期自持 |

> 费用主要构成：**40% 战略咨询 + 25% 技术支持 + 20% 软件许可 + 15% 规则库更新**  
> 您购买的不仅仅是软件，更是 SPL 语言创造者对您角色系统的持续调优与认知赋能。

---

## 🧩 快速开始（技术预览）

```python
from spl_audit import AICharacterProfile, SPLAuditEngine

# 创建角色
ye_wanqing = AICharacterProfile(
    name="叶婉清",
    age=24,
    relationship="陆景川的侄女 / 无法公开的背德恋人",
    job_identity="清日集团会长"
)

# 配置心理矩阵（0.5 为人类基准）
ye_wanqing.psychology_matrix = {
    "高冷克制": {"description": "...", "base_weight": 0.5, "effective_scene": ["公开场合"]},
    "病态纵容": {"description": "...", "base_weight": 0.5, "effective_target": ["陆景川"], "effective_scene": ["私密空间"]}
}

# 挂载审计引擎
auditor = SPLAuditEngine(ye_wanqing)

# 生成回复并审计
user_msg = "今晚来我房间"
raw_reply = llm.generate(ye_wanqing.to_ai_prompt() + user_msg)
audit_report = auditor.audit_response(raw_reply)

if not audit_report["passed"]:
    # 拦截违规输出，使用兜底回复
    final_reply = get_fallback_reply()
else:
    final_reply = raw_reply
