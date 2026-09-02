"""
SPL Agent Engine — Anthropomorphic Psychology Engine (SPL Pure Core V8.0)

A deterministic, continuous-state model of human mental architecture:
emotion fluid, trauma, memory, trust, energy metabolism, mood,
self-esteem, sleep/dream processing, anticipation, cognitive dissonance,
and defense mechanisms — no LLM, no randomness, fully replayable.

V8.0 增量（相对 0.1.0）：
    · 确定性审计日志（AuditLogger，本地 JSONL，失败不阻断引擎）
    · 心境层（mood）· 羞耻维度 · 自尊动态 · 睡眠/梦境加工
    · 预期系统 · 认知失调 · 扩展防御机制（否认/合理化/置换）
    · LLM 台词适配器（LLMAdapter / OpenAIAdapter / ClaudeAdapter / ChainAdapter）

Usage:
    from spl_agent_engine import SPLPureCore, NarrativeMapper
    core = SPLPureCore()
    core.process_event("insult", intensity=1.0)
    print(core.fluid)
"""

from .core import AuditLogger, SPLPureCoreV7_3, NarrativeMapper

# Canonical name for V8.0 (class name kept for backward compatibility)
SPLPureCore = SPLPureCoreV7_3

__version__ = "0.2.0"
__all__ = ["SPLPureCore", "SPLPureCoreV7_3", "NarrativeMapper", "AuditLogger"]
