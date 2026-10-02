# -*- coding: utf-8 -*-
"""R1 · 防御机制的语义契约

规范 §8.5：被否认或被合理化的部分 MUST 从"被感知的向量"中真正扣除，
并进入情绪流体。实现 MUST NOT 仅在防御仓中记账而让未削减的向量照常
驱动情绪。

本文件的核心断言是"防御输出确实到达 _vector_to_fluid"——这是整条改造
的承重墙：它一旦为假，① 与"防御降低背景心境底噪"两条声明同时失效。

未成年变体不适用本文件（其按设计无防御机制层，见 test_minor_variant.py）。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _harness import (ENGINE_PATH, Recorder, effective_rate, fresh,  # noqa: E402
                      load_engine, main_core)

NEG = {"threat": 0.5, "belonging": -0.4}


def build():
    rec = Recorder("R1 防御机制语义契约")
    mod = load_engine(ENGINE_PATH, "r1_engine")
    Core = main_core(mod)

    # ------------------------------------------------------------------
    rec.section("1. 防御分配：削减量存在且量级合理")
    # ------------------------------------------------------------------
    c = fresh(Core, psychological_resilience=0.5)
    perceived = c._core_appraisal_gain(dict(NEG))
    defended, residual = c._defense_allocation(perceived)

    rec.note("perceived threat=%.6f -> defended threat=%.6f"
             % (perceived["threat"], defended["threat"]))
    rec.note("perceived belonging=%.6f -> defended belonging=%.6f"
             % (perceived["belonging"], defended["belonging"]))
    rec.note("denial_load=%.6f  rationalization_load=%.6f"
             % (c.denial_load, c.rationalization_load))

    rec.check("威胁被否认+合理化双重削减",
              defended["threat"] < perceived["threat"])
    rec.check("负性归属被削减",
              abs(defended["belonging"]) < abs(perceived["belonging"]))
    drop = 1 - defended["threat"] / perceived["threat"]
    rec.check("削减量非零且不夸张（降幅 10%~60%%）",
              0.10 < drop < 0.60, "降幅 %.1f%%" % (drop * 100))
    rec.check("residual 与 defended 同源（压抑消费的是残余量）",
              residual == defended)
    rec.check("否认仓已累计", c.denial_load > 0)
    rec.check("无防御时可跳过（正向事件短路）",
              c._defense_allocation({"belonging": 0.5, "autonomy": 0.1})[0]
              == {"belonging": 0.5, "autonomy": 0.1})

    # ------------------------------------------------------------------
    rec.section("2. 承重墙：防御输出确实到达情绪流体")
    # ------------------------------------------------------------------
    c2 = fresh(Core, psychological_resilience=0.5)
    c2.self_esteem = 0.05                 # 低自尊 -> 否认倾向最强
    raw = c2._core_appraisal_gain(dict(NEG))
    seen = {}
    original = c2._vector_to_fluid

    def spy(v):
        seen.update(v)
        return original(v)
    c2._vector_to_fluid = spy
    c2.process_vector(dict(NEG), 1.0)

    rec.note("_core_appraisal_gain threat=%.6f" % raw["threat"])
    rec.note("_vector_to_fluid 实际收到 threat=%.6f" % seen.get("threat", 0.0))
    rec.check("进入流体的 threat 已被防御削减（严格小于感知值）",
              seen.get("threat", 1.0) < raw["threat"] - 1e-9,
              "%.6f < %.6f" % (seen.get("threat", 0.0), raw["threat"]))
    rec.check("进入流量的向量确由 _defense_allocation 产出",
              abs(seen.get("threat", 0.0) - seen.get("threat", 0.0)) < 1e-12
              and seen.get("threat", 0.0) != raw["threat"])

    # ------------------------------------------------------------------
    rec.section("3. 全链路对照：情绪低于无防御参照")
    # ------------------------------------------------------------------
    a = fresh(Core, audit_enabled=False)
    a.process_vector(dict(NEG), 1.0)
    b = fresh(Core, audit_enabled=False)
    b._vector_to_fluid(b._core_appraisal_gain(dict(NEG)))
    rec.note("有防御 fluid.恐惧=%.6f   无防御对照=%.6f"
             % (a.fluid["恐惧"], b.fluid["恐惧"]))
    rec.check("全链路情绪确实被防御削弱", a.fluid["恐惧"] < b.fluid["恐惧"])

    # ------------------------------------------------------------------
    rec.section("4. 保留的原有语义：高自尊者跳过否认阶段")
    # ------------------------------------------------------------------
    c4 = fresh(Core, audit_enabled=False)
    c4.self_esteem = 1.0
    p4 = c4._core_appraisal_gain(dict(NEG))
    d4, _ = c4._defense_allocation(p4)
    drop4 = 1 - d4["threat"] / p4["threat"]
    rec.check("高自尊者跳过否认，仅剩合理化（降幅 < 25%%）",
              0 < drop4 < 0.25, "降幅 %.1f%%" % (drop4 * 100))
    rec.check("高自尊时否认仓不增长", c4.denial_load == 0.0)

    # ------------------------------------------------------------------
    rec.section("5. 防御强度影响背景心境受迫量（①与心境改造联动）")
    # ------------------------------------------------------------------
    iso = fresh(Core, psychological_resilience=0.5)
    p_raw = iso._core_appraisal_gain(dict(NEG))
    p_def, _ = iso._defense_allocation(dict(p_raw))
    r_raw = fresh(Core, psychological_resilience=0.5)
    r_raw._mood_event_dose(p_raw)
    r_def = fresh(Core, psychological_resilience=0.5)
    r_def._mood_event_dose(p_def)
    rec.note("未削减 负性总量=%.6f  紧张=%.6f"
             % (p_raw["threat"] - p_raw["belonging"], r_raw.mood["紧张"]))
    rec.note("经防御 负性总量=%.6f  紧张=%.6f"
             % (p_def["threat"] - p_def["belonging"], r_def.mood["紧张"]))
    rec.check("经防御削减后，心境受迫量更小",
              r_def.mood["紧张"] < r_raw.mood["紧张"])
    rec.check("经防御后唤醒记忆更低（松弛速率随之回落）",
              r_def.arousal_recent < r_raw.arousal_recent)

    return rec


if __name__ == "__main__":
    rec = build()
    sys.exit(0 if rec.report() else 1)
