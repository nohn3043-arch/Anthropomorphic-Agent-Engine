# -*- coding: utf-8 -*-
"""R4 · 未成年合规变体与主引擎的对齐

minor-protection 是独立实现（SPLMinorPureCore + MinorNarrativeMapper），
不是主引擎的派生。它按设计裁掉了防御机制层与创伤节点，因此：

  - R1（防御契约）不适用于本变体，那是机制级风险削减，不是缺陷
  - R2（审计 delta）、R3（心境动力学）必须与主引擎同算法
  - delta 的覆盖集差异是设计意图，MUST NOT 为消除差异而强行对齐

变体参数：负性情绪钳位 0.75、依恋上限 0.8、心理韧性 0.6。
事件词表：compliment / insult / betrayal / alone / rest（侮辱与背叛降档 60%）。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _harness import (ENGINE_PATH, MINOR_PATH, MOOD_KEYS,  # noqa: E402
                      Recorder, audit_core, displaced_mood_factory,
                      effective_rate, fresh, load_engine, main_core,
                      minor_core, partition_sensitivity)

MINOR_ONLY_SNAPSHOT = {"protective"}


def build():
    rec = Recorder("R4 未成年变体对齐")
    maj = load_engine(ENGINE_PATH, "r4_main")
    mnr = load_engine(MINOR_PATH, "r4_minor")
    MCore = main_core(maj)
    NCore = minor_core(mnr)
    nsrc = open(MINOR_PATH, "r", encoding="utf-8").read()

    # ------------------------------------------------------------------
    rec.section("1. 变体裁剪符合设计：无防御层、无创伤")
    # ------------------------------------------------------------------
    rec.check("无 _defense_hierarchy", "_defense_hierarchy" not in nsrc)
    rec.check("无 _suppression_dynamics", "_suppression_dynamics" not in nsrc)
    rec.check("无 trauma_state 字段声明",
              "trauma_state:" not in nsrc and "self.trauma_state" not in nsrc)
    rec.check("trauma_state 仅存于注释（声明已移除）",
              "trauma_state" in nsrc)
    probe = fresh(NCore, audit_enabled=False)
    rec.check("无防御仓（压抑/否认/合理化）",
              not hasattr(probe, "suppression_load")
              and not hasattr(probe, "denial_load")
              and not hasattr(probe, "rationalization_load"))
    rec.check("snapshot 独有 protective 子模型",
              MINOR_ONLY_SNAPSHOT <= set(probe.snapshot()))

    # ------------------------------------------------------------------
    rec.section("2. 心境动力学与主引擎同结构")
    # ------------------------------------------------------------------
    rec.check("存在 _mood_event_dose", hasattr(probe, "_mood_event_dose"))
    rec.check("无 MOOD_INERTIA 残留", "MOOD_INERTIA" not in nsrc)
    import inspect
    rec.check("_update_mood 接受 dt 参数",
              "dt" in inspect.signature(probe._update_mood).parameters)
    for k in ("MOOD_RATE_BASE", "MOOD_AROUSAL_GAIN", "MOOD_AROUSAL_TAU",
              "MOOD_AROUSAL_EMA", "MOOD_DOSE_PLEASANT", "MOOD_DOSE_TENSION",
              "MOOD_DOSE_VIGOR"):
        rec.check("常数 %s 与主引擎同值" % k,
                  getattr(NCore, k) == getattr(MCore, k),
                  "%r vs %r" % (getattr(NCore, k, None), getattr(MCore, k, None)))

    fine, coarse, _, _ = partition_sensitivity(
        displaced_mood_factory(NCore))
    rec.note("细分切法之间分歧 = %.3e   单步与细分 = %.3e" % (fine, coarse))
    rec.check("细分切法之间高度一致（< 1e-3）", fine < 1e-3, "%.3e" % fine)
    rec.check("单步与细分同量级收敛（< 2e-2）", coarse < 2e-2, "%.3e" % coarse)

    calm = fresh(NCore, audit_enabled=False)
    calm.process_event("rest", 1.0)
    hot = fresh(NCore, audit_enabled=False)
    for _ in range(4):
        hot.process_event("betrayal", 1.0)
    k_c, _ = effective_rate(calm, 60.0)
    k_h, _ = effective_rate(hot, 60.0)
    rec.note("速率 平静=%.8f  唤醒=%.8f  (放大 %.2fx)" % (k_c, k_h, k_h / k_c))
    rec.check("速率 k 随唤醒变化（不是常数）", k_h > k_c * 1.2)

    # ------------------------------------------------------------------
    rec.section("3. 审计 delta：四入口全覆盖")
    # ------------------------------------------------------------------
    def drive(c):
        c.process_event("betrayal", 1.0)
        c.expect("later", -0.5, 0.8)
        c.induce_dissonance(0.6, "honesty")
        c.sleep(2.0)

    recs = audit_core(NCore, "r4", drive)
    kinds = [r["event"] for r in recs]
    rec.note("事件序列: %s" % kinds)
    for want in ("process_vector", "expect", "induce_dissonance", "sleep"):
        rec.check("%s 有记录" % want, want in kinds)
    rec.check("全部记录含 delta", all("delta" in r for r in recs))
    for r in recs:
        rec.check("%s 的 delta 非空" % r["event"], len(r["delta"]) > 0,
                  "%d 字段" % len(r["delta"]))
    pv = [r for r in recs if r["event"] == "process_vector"][0]
    rec.check("delta 含 fluid.* 展开路径",
              any(k.startswith("fluid.") for k in pv["delta"]))
    rec.check("delta 含 arousal_recent", "arousal_recent" in pv["delta"])
    rec.check("snapshot 摘要含 arousal_recent",
              "arousal_recent" in pv["snapshot"])

    # ------------------------------------------------------------------
    rec.section("4. protective 非数值字段进入 delta（合规审计要点）")
    # ------------------------------------------------------------------
    b = fresh(NCore, audit=True, audit_session_id="r4bool")
    b._session_seconds = b.SESSION_LIMIT_SECONDS - 0.1
    b.process_event("compliment", 1.0)
    # 该实例未指定 log_dir，复用 harness 默认临时目录
    from _harness import read_records
    import tempfile
    latest = sorted(os.listdir(tempfile.gettempdir()))
    hit = None
    # 直接从 b 自己的审计器读取，避免依赖目录排序
    try:
        path = b.audit_logger.log_file
        import json as _json
        import io as _io
        with _io.open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    hit = _json.loads(line)
                    break
    except Exception as exc:                       # noqa: BLE001
        rec.fail("可读取未成年变体审计文件", str(exc))
    if hit is not None:
        prot = [k for k in hit["delta"] if k.startswith("protective.")]
        rec.note("protective.* 变化键: %s" % prot)
        rec.check("protective 字段变化已进入 delta", len(prot) > 0, str(prot))
        for k in prot:
            e = hit["delta"][k]
            if isinstance(e["before"], (int, float)) and \
                    not isinstance(e["before"], bool):
                continue
            rec.check("非数值条目 %s 不伪造算术差" % k, "delta" not in e, str(e))

    # ------------------------------------------------------------------
    rec.section("5. 变体参数符合规范 §5.6")
    # ------------------------------------------------------------------
    rec.check("负性情绪钳位 0.75", abs(NCore.EMOTION_CEIL_NEG - 0.75) < 1e-9,
              str(NCore.EMOTION_CEIL_NEG))
    rec.check("依恋上限 0.8", abs(NCore.ATTACH_MAX - 0.8) < 1e-9,
              str(NCore.ATTACH_MAX))
    rec.check("心理韧性 0.6", abs(probe.psychological_resilience - 0.6) < 1e-9,
              str(probe.psychological_resilience))
    rec.check("侮辱/背叛降档至 60%",
              abs(mnr.MinorNarrativeMapper.map_event("betrayal", 1.0)
                  ["belonging"] - (-0.36)) < 1e-9)

    # ------------------------------------------------------------------
    rec.section("6. 跨引擎算法一致（共有字段上）")
    # ------------------------------------------------------------------
    probe_pair = (
        {"fluid": {"喜悦": 0.1, "愤怒": 0.2}, "mood": {"愉悦": 0.5},
         "self_esteem": 0.5, "arousal_recent": 0.0,
         "protective": {"risk_level": "LOW", "crisis_flags": ["a"],
                        "rest_hint": False, "session_seconds": 1.0}},
        {"fluid": {"喜悦": 0.3, "愤怒": 0.2}, "mood": {"愉悦": 0.5},
         "self_esteem": 0.5, "arousal_recent": 0.2,
         "protective": {"risk_level": "HIGH", "crisis_flags": ["a", "b"],
                        "rest_hint": True, "session_seconds": 2.5}},
    )
    dm = maj.AuditLogger.snapshot_delta(*probe_pair)
    dn = mnr.AuditLogger.snapshot_delta(*probe_pair)
    shared = set(dm) & set(dn)
    rec.check("共有字段上的 delta 计算完全一致",
              all(dm[k] == dn[k] for k in shared),
              "共有 %d 字段" % len(shared))
    only_minor = sorted(set(dn) - set(dm))
    rec.note("minor 独有字段: %s" % only_minor)
    rec.check("minor 独有字段仅来自 protective 子模型",
              all(k.startswith("protective.") for k in only_minor), str(only_minor))
    rec.check("主引擎 DELTA_NESTED 不含 protective",
              "protective" not in maj.AuditLogger.DELTA_NESTED)

    # ------------------------------------------------------------------
    rec.section("7. 确定性")
    # ------------------------------------------------------------------
    import json
    def run():
        c = fresh(NCore, audit_enabled=False)
        c.process_event("betrayal", 1.0)
        c.idle(120.0)
        c.process_event("compliment", 1.0)
        c.sleep(1.0)
        return json.dumps(c.snapshot(), sort_keys=True, ensure_ascii=False)
    rec.check("同输入两次跑 snapshot 相同", run() == run())

    return rec


if __name__ == "__main__":
    rec = build()
    sys.exit(0 if rec.report() else 1)
