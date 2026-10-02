# -*- coding: utf-8 -*-
"""R2 · 审计状态转移归因（delta）

规范 §7.3/§7.4：审计记录 MUST 同时携带输入参数、终值状态摘要、以及
逐字段 delta。只记终值能证明"某时刻状态是什么"，不能证明"哪次输入造成了
哪些字段的多少变化"。

§7.4 的算法要点：
  - 数值条目附 delta（round 到 6 位）
  - 非数值条目只记录变化本身，MUST NOT 伪造算术差
  - 布尔 MUST NOT 被视为数值
  - fluid / mood / trauma 展开为点号路径
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _harness import (ENGINE_PATH, Recorder, audit_core, fresh,  # noqa: E402
                      load_engine, main_core)


def build():
    rec = Recorder("R2 审计状态转移归因")
    mod = load_engine(ENGINE_PATH, "r2_engine")
    Core = main_core(mod)

    # ------------------------------------------------------------------
    rec.section("1. 四个状态变更入口全部落审计记录并携带 delta")
    # ------------------------------------------------------------------
    def drive(c):
        c.process_event("insult", 1.0)
        c.expect("later", -0.5, 0.8)
        c.induce_dissonance(0.6, "honesty")
        c.sleep(2.0)

    recs = audit_core(Core, "r2", drive)
    kinds = [r["event"] for r in recs]
    rec.note("事件序列: %s" % kinds)

    for want in ("process_vector", "expect", "induce_dissonance", "sleep"):
        rec.check("%s 有审计记录" % want, want in kinds)
    rec.check("全部记录含 delta 字段", all("delta" in r for r in recs))
    for r in recs:
        rec.check("%s 的 delta 非空" % r["event"], len(r["delta"]) > 0,
                  "%d 字段" % len(r["delta"]))
    rec.check("记录含 seq/ts/engine/session 信封字段",
              all(all(k in recs[0] for k in
                      ("seq", "ts", "engine", "session", "event",
                       "input", "snapshot")) for _ in (0,)))

    pv = [r for r in recs if r["event"] == "process_vector"][0]
    rec.check("delta 含 fluid.* 展开路径",
              any(k.startswith("fluid.") for k in pv["delta"]))
    rec.check("delta 含 denial_load（防御层状态转移被记录）",
              "denial_load" in pv["delta"])
    rec.check("delta 含 arousal_recent（驱动松弛速率的状态量被覆盖）",
              "arousal_recent" in pv["delta"])
    rec.check("snapshot 摘要含 arousal_recent",
              "arousal_recent" in pv["snapshot"])

    # ------------------------------------------------------------------
    rec.section("2. delta 自洽：before + delta == after")
    # ------------------------------------------------------------------
    bad = []
    for key, e in pv["delta"].items():
        if "delta" not in e:
            continue
        if not isinstance(e["before"], (int, float)) or \
                isinstance(e["before"], bool):
            continue
        if abs(e["before"] + e["delta"] - e["after"]) > 1e-6:
            bad.append(key)
    rec.check("所有数值条目满足 before + delta == after",
              not bad, "不自洽字段=%s" % bad)
    sample = pv["delta"]["arousal_recent"]
    rec.note("样例 arousal_recent: %.6f + %.6f = %.6f"
             % (sample["before"], sample["delta"], sample["after"]))

    # ------------------------------------------------------------------
    rec.section("3. delta 只含实际发生变化的字段")
    # ------------------------------------------------------------------
    unchanged = []
    for key, e in pv["delta"].items():
        if e["before"] == e["after"]:
            unchanged.append(key)
    rec.check("不含 before == after 的空条目", not unchanged, str(unchanged))
    flat = [k for k in pv["delta"] if "." in k]
    rec.check("点号路径条目均来自已知子模型",
              all(k.split(".")[0] in mod.AuditLogger.DELTA_NESTED for k in flat))

    # ------------------------------------------------------------------
    rec.section("4. delta 覆盖集与规范 §7.4 一致")
    # ------------------------------------------------------------------
    scalar_set = set(mod.AuditLogger.DELTA_SCALARS)
    required = {"self_esteem", "energy", "fatigue", "excitation", "max_trust",
                "suppression_load", "denial_load", "rationalization_load",
                "latent_pressure", "cognitive_dissonance", "sleep_debt",
                "arousal_recent", "memory_count", "expected_count"}
    rec.check("DELTA_SCALARS 覆盖规范列出的 14 项",
              required <= scalar_set,
              "缺=%s" % sorted(required - scalar_set))
    rec.check("DELTA_NESTED 为 fluid/mood/trauma",
              set(mod.AuditLogger.DELTA_NESTED) == {"fluid", "mood", "trauma"})

    # ------------------------------------------------------------------
    rec.section("5. delta 本身可复现")
    # ------------------------------------------------------------------
    def twice(seed):
        def drive(c):
            c.process_event("insult", 1.0)
            c.induce_dissonance(0.6, "honesty")
            c.idle(120.0)
        return audit_core(Core, seed, drive)

    a = twice("rep1")
    b = twice("rep2")
    rec.check("两次相同输入的 delta 完全一致",
              a[0]["delta"] == b[0]["delta"])
    rec.check("两次相同输入的 snapshot 一致",
              a[0]["snapshot"] == b[0]["snapshot"])

    # ------------------------------------------------------------------
    rec.section("6. 非数值条目的算法行为（规范 §7.4）")
    # ------------------------------------------------------------------
    # 主引擎的 DELTA_NESTED 全为数值字段（fluid/mood/trauma 均为 float），
    # 因此非数值分支在主引擎上不会被集成触发——它由未成年变体的
    # protective 子模型集成覆盖（见 test_minor_variant.py）。
    # 此处对算法本身做单元断言。
    # ------------------------------------------------------------------
    put = mod.AuditLogger._put_delta

    d = {}
    put(d, "n", 1.0, 2.5)
    rec.check("数值条目附带 delta", d["n"]["delta"] == 1.5, str(d["n"]))

    d = {}
    put(d, "b", False, True)
    rec.check("布尔被记录", "b" in d)
    rec.check("布尔不被当作数值（无 delta 键）", "delta" not in d["b"], str(d["b"]))

    d = {}
    put(d, "s", "LOW", "HIGH")
    rec.check("字符串枚举被记录", "s" in d)
    rec.check("字符串枚举无 delta 键", "delta" not in d["s"], str(d["s"]))

    d = {}
    put(d, "l", [], ["sustained_negativity"])
    rec.check("列表变化被记录", "l" in d)
    rec.check("列表条目无 delta 键", "delta" not in d["l"], str(d["l"]))

    d = {}
    put(d, "x", 1.0, 1.0)
    rec.check("before == after 被跳过", "x" not in d)

    d = {}
    put(d, "r", 1.0, 1.0000004)
    rec.check("极小差值 round 到 6 位后仍保留 0.0 并被跳过",
              "r" not in d or d["r"].get("delta") == 0.0, str(d.get("r")))

    # 主引擎覆盖集内不应出现非数值条目
    probe = ({"fluid": {"喜悦": 0.1}, "mood": {"愉悦": 0.5},
              "trauma": {"threat": 0.2}, "self_esteem": 0.5,
              "arousal_recent": 0.0},
             {"fluid": {"喜悦": 0.3}, "mood": {"愉悦": 0.5},
              "trauma": {"threat": 0.2}, "self_esteem": 0.5,
              "arousal_recent": 0.2})
    d = mod.AuditLogger.snapshot_delta(*probe)
    rec.note("delta 键: %s" % sorted(d.keys()))
    rec.check("未变化字段被跳过（trauma/mood/自自尊）",
              not any(k.startswith(("trauma.", "mood.")) for k in d)
              and "self_esteem" not in d)
    rec.check("主引擎覆盖集产出的条目均带 delta 键",
              all("delta" in e for e in d.values()), str(d))

    # ------------------------------------------------------------------
    rec.section("7. 审计关闭时不产生副作用")
    # ------------------------------------------------------------------
    c = fresh(Core, audit_enabled=False)
    c.process_event("insult", 1.0)
    rec.check("audit_enabled=False 时无审计器",
              c.audit_logger is None or not c.audit_logger.enabled)

    return rec


if __name__ == "__main__":
    rec = build()
    sys.exit(0 if rec.report() else 1)
