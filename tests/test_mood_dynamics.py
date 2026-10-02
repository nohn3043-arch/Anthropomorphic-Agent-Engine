# -*- coding: utf-8 -*-
"""R3 · 心境动力学（受迫-阻尼结构）

规范 §8.2：心境 MUST 实现为受迫-阻尼系统，MUST NOT 使用"每次调用走固定
步长"的实现。

  受迫（事件驱动）  _mood_event_dose(v)   按事件唤醒度把心境推离靶标
  阻尼（时间驱动）  _update_mood(dt)      按 dt 一致地把心境拉回靶标
  收敛速率          k = MOOD_RATE_BASE * (1 + GAIN * arousal_recent)
  松弛步长          alpha = 1 - exp(-k * dt)

§8.3 给出量化界：细切法之间差异 < 1e-3，单步与细分之间残差 < 2e-2。
残差不可归零——靶标由流体推出而流体同步演化，向移动靶标松弛无闭式精确解。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _harness import (ENGINE_PATH, MOOD_KEYS, Recorder,  # noqa: E402
                      displaced_mood_factory, effective_rate,
                      fresh, load_engine, main_core,
                      partition_sensitivity)


def build():
    rec = Recorder("R3 心境受迫-阻尼动力学")
    mod = load_engine(ENGINE_PATH, "r3_engine")
    src = open(ENGINE_PATH, "r", encoding="utf-8").read()
    Core = main_core(mod)

    # ------------------------------------------------------------------
    rec.section("1. 结构：受迫项与阻尼项分离，且无固定步长常数")
    # ------------------------------------------------------------------
    rec.check("存在 _mood_event_dose（受迫项）", hasattr(Core, "_mood_event_dose")
              or hasattr(mod, "_mood_event_dose") or
              hasattr(fresh(Core), "_mood_event_dose"))
    rec.check("无 MOOD_INERTIA 残留", "MOOD_INERTIA" not in src)
    import inspect
    params = inspect.signature(fresh(Core)._update_mood).parameters
    rec.check("_update_mood 接受 dt 参数", "dt" in params)
    for k in ("MOOD_RATE_BASE", "MOOD_AROUSAL_GAIN", "MOOD_AROUSAL_TAU",
              "MOOD_AROUSAL_EMA", "MOOD_DOSE_PLEASANT", "MOOD_DOSE_TENSION",
              "MOOD_DOSE_VIGOR"):
        rec.check("常数 %s 存在" % k, hasattr(Core, k),
                  str(getattr(Core, k, None)))
    rec.check("arousal_recent 为可观测状态量（出现在 snapshot 中）",
              "arousal_recent" in fresh(Core).snapshot())

    # ------------------------------------------------------------------
    rec.section("2. 步长一致性（规范 §8.3 的量化界）")
    # ------------------------------------------------------------------
    fine, coarse, one_step, many_step = partition_sensitivity(
        displaced_mood_factory(Core))
    for k in MOOD_KEYS:
        rec.note("%s  1x3600s=%.9f  3600x1s=%.9f" % (k, one_step[k],
                                                     many_step[k]))
    rec.note("细分切法之间分歧 = %.3e" % fine)
    rec.note("单步与细分分歧   = %.3e" % coarse)
    rec.check("细分切法之间高度一致（< 1e-3）", fine < 1e-3, "%.3e" % fine)
    rec.check("单步与细分同量级收敛（< 2e-2）", coarse < 2e-2, "%.3e" % coarse)

    # ------------------------------------------------------------------
    rec.section("3. 收敛速率由事件动态算出，不是常数")
    # ------------------------------------------------------------------
    # 行为判据，不是公式复述。
    # 若在此处复述 k = MOOD_RATE_BASE * (1 + GAIN * arousal_recent)，
    # 则把 k 改成常数后该断言仍会通过——它对公式改动恒真。
    # 变异守卫 test_mutation_guard.py 的 mood_constant_rate 变体
    # 正是为此存在：它要求本节在 k 退回常数时必须变红。
    # ------------------------------------------------------------------
    def relax_with(arousal):
        """同一初始状态与同一靶标，仅 arousal_recent 不同，观测松弛量。"""
        c = fresh(Core, audit_enabled=False)
        c.mood["愉悦"] = 0.95
        c.arousal_recent = arousal
        c.idle(120.0)
        return c.mood["愉悦"]

    lo = relax_with(0.0)
    hi = relax_with(1.0)
    rec.note("同一起点 0.95，空转 120s：低唤醒 -> %.6f   高唤醒 -> %.6f"
             % (lo, hi))
    rec.check("仅 arousal_recent 不同即产生可观测的松弛速度差（行为判据）",
              hi < lo - 1e-6, "高唤醒比低唤醒多回稳 %.6f" % (lo - hi))

    calm = fresh(Core, audit_enabled=False)
    calm.process_event("rest", 1.0)
    hot = fresh(Core, audit_enabled=False)
    for _ in range(4):
        hot.process_event("betrayal", 1.0)
    rec.note("平静 arousal_recent=%.6f   唤醒 arousal_recent=%.6f"
             % (calm.arousal_recent, hot.arousal_recent))
    rec.check("事件驱动项确实抬高 arousal_recent",
              hot.arousal_recent > calm.arousal_recent * 3)
    k_c, a_c = effective_rate(calm, 60.0)
    k_h, a_h = effective_rate(hot, 60.0)
    rec.note("按规范公式复算：k %.8f -> %.8f   alpha(60s) %.8f -> %.8f"
             % (k_c, k_h, a_c, a_h))
    rec.check("实现常数与规范 §8.2 公式自洽（此项为规范一致性，非行为判据）",
              k_h > k_c > 0 and a_h > a_c > 0)

    # ------------------------------------------------------------------
    rec.section("4. 语义：强情绪更易消退")
    # ------------------------------------------------------------------
    def after_idle(events):
        c = fresh(Core, audit_enabled=False)
        for _ in range(events):
            c.process_event("betrayal", 1.0)
        c.mood["愉悦"] = 0.95
        c.mood["紧张"] = 0.90
        c.idle(120.0)
        return c

    hot_a = after_idle(5)
    cold_a = after_idle(0)
    rec.note("回稳 120s 后 愉悦  高唤醒=%.6f  无事件=%.6f"
             % (hot_a.mood["愉悦"], cold_a.mood["愉悦"]))
    rec.check("强情绪更易消退（高唤醒回稳更接近靶标）",
              hot_a.mood["愉悦"] < cold_a.mood["愉悦"])

    # ------------------------------------------------------------------
    rec.section("5. 唤醒记忆随时间消散，速率回落至基础值")
    # ------------------------------------------------------------------
    d = fresh(Core, audit_enabled=False)
    d.process_event("betrayal", 1.0)
    before = d.arousal_recent
    d.idle(1800.0)
    after = d.arousal_recent
    k_after, _ = effective_rate(d, 60.0)
    rec.note("唤醒记忆 事件后=%.6f  30 分钟后=%.6f" % (before, after))
    rec.check("唤醒记忆随时间消散", after < before * 0.5)
    rec.check("消散后速率回到基础值 5%% 以内",
              abs(k_after - Core.MOOD_RATE_BASE) < Core.MOOD_RATE_BASE * 0.05,
              "k=%.8f base=%.8f" % (k_after, Core.MOOD_RATE_BASE))

    # ------------------------------------------------------------------
    rec.section("6. 受迫与阻尼职责分离")
    # ------------------------------------------------------------------
    # 纯阻尼：靶标不动时，时间推进应单调拉回
    p = fresh(Core, audit_enabled=False)
    p.mood["愉悦"] = 0.95
    v0 = p.mood["愉悦"]
    p.idle(300.0)
    v1 = p.mood["愉悦"]
    rec.check("无事件时心境向靶标回稳", v1 < v0, "%.6f -> %.6f" % (v0, v1))

    # 纯受迫：单个事件应直接位移心境
    q = fresh(Core, audit_enabled=False)
    t_before = q.mood["紧张"]
    q._mood_event_dose({"threat": 0.5, "belonging": -0.4})
    t_after = q.mood["紧张"]
    rec.check("单个事件直接位移心境（受迫项不依赖时间）",
              t_after > t_before, "%.6f -> %.6f" % (t_before, t_after))

    # dt=0 时阻尼项必须是空操作
    z = fresh(Core, audit_enabled=False)
    z.mood["愉悦"] = 0.95
    z._update_mood(dt=0.0)
    rec.check("dt=0 时阻尼项为空操作", abs(z.mood["愉悦"] - 0.95) < 1e-12,
              "%.12f" % z.mood["愉悦"])

    # 空操作向量不产生受迫
    n = fresh(Core, audit_enabled=False)
    n._mood_event_dose({"belonging": 0.0, "threat": 0.0})
    rec.check("全零向量不产生心境受迫", n.arousal_recent == 0.0)

    return rec


if __name__ == "__main__":
    rec = build()
    sys.exit(0 if rec.report() else 1)
