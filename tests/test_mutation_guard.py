# -*- coding: utf-8 -*-
"""R6 · 变异守卫：断言必须具有判别力

"测试通过"只有在"把被测行为改坏后测试变红"时才是证据。
否则断言可能恒真——它同样会通过，却什么也没测到。

本文件从当前引擎派生出若干变体（mutant），逐一注入缺陷，然后验证：
**对应的 R 系列测试必须失败。** 若某变体注入后测试依然全绿，说明对应的
断言没有判别力，必须修断言或修文档，而不是接受这份"绿灯"。

变体注入用纯文本替换，并要求每处替换恰好命中一次，否则中止——
这样注入的是"确定的那个缺陷"，不会误伤。
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _harness import ENGINE_PATH, Recorder  # noqa: E402


def make_mutant(old, new, tag):
    """把引擎复制到临时目录并注入一处缺陷，返回路径。"""
    src = open(ENGINE_PATH, "r", encoding="utf-8", newline="").read()
    n = src.count(old)
    if n != 1:
        raise SystemExit("[FATAL] mutant %s: pattern hit %d times (need 1)\n%r"
                         % (tag, n, old[:80]))
    out = os.path.join(tempfile.gettempdir(), "aae_mutant_%s.py" % tag)
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(src.replace(old, new))
    return out


# (标签, 目标测试文件, 旧文本, 新文本, 缺陷描述)
MUTANTS = [
    (
        "defense_no_attenuation",
        "test_defense.py",
        "        self._vector_to_fluid(defended)\r\n",
        "        self._vector_to_fluid(perceived)\r\n",
        "防御输出不再进入情绪流体（退回改造前的缺陷①）",
    ),
    (
        "audit_no_delta",
        "test_audit_delta.py",
        "                after,\r\n"
        "                delta=AuditLogger.snapshot_delta(before, after),\r\n"
        "            )\r\n"
        "\r\n"
        "    # ==================================================================\r\n"
        "    # 公共入口 2：空转 / 独处时间\r\n",
        "                after,\r\n"
        "            )\r\n"
        "\r\n"
        "    # ==================================================================\r\n"
        "    # 公共入口 2：空转 / 独处时间\r\n",
        "process_vector 的审计记录不再携带 delta（退回改造前的缺陷③）",
    ),
    (
        "mood_fixed_step",
        "test_mood_dynamics.py",
        "        alpha = 1.0 - math.exp(-k * dt)\r\n",
        "        alpha = self.MOOD_RATE_BASE\r\n",
        "松弛步长退回每步固定常数（步长敏感性回归）",
    ),
    (
        "mood_constant_rate",
        "test_mood_dynamics.py",
        "        k = self.MOOD_RATE_BASE * (1.0 + self.MOOD_AROUSAL_GAIN\r\n"
        "                                   * self.arousal_recent)\r\n",
        "        k = self.MOOD_RATE_BASE\r\n",
        "收敛速率退回常数，不再随事件唤醒变化",
    ),
]


def run_test_against(script, engine_path):
    env = dict(os.environ)
    env["AAE_ENGINE"] = str(engine_path)
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run([sys.executable, str(HERE / script)],
                       capture_output=True, env=env, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def build():
    rec = Recorder("R6 变异守卫（断言判别力）")

    rec.section("0. 基线：未注入缺陷时全部 R 测试必须通过")
    for script in ("test_defense.py", "test_audit_delta.py",
                   "test_mood_dynamics.py", "test_minor_variant.py"):
        code, _ = run_test_against(script, ENGINE_PATH)
        rec.check("%s 在正确实现上通过" % script, code == 0, "exit=%d" % code)

    rec.section("1. 注入缺陷后，对应测试必须失败")
    for tag, script, old, new, desc in MUTANTS:
        try:
            mutant = make_mutant(old, new, tag)
        except SystemExit as exc:
            rec.check("注入 %s" % tag, False, str(exc))
            continue
        code, out = run_test_against(script, mutant)
        rec.note("%-24s %s" % (tag, desc))
        rec.check("%-24s → %s 失败" % (tag, script), code != 0,
                  "exit=%d%s" % (code, "" if code != 0
                                 else "  (断言无判别力！)"))

    rec.section("2. 变异守卫的自我检查")
    rec.check("共 %d 个变体" % len(MUTANTS), len(MUTANTS) >= 4)
    rec.check("变体覆盖三类改造（防御/审计/心境）",
              len({m[1] for m in MUTANTS}) >= 3)

    return rec


if __name__ == "__main__":
    rec = build()
    sys.exit(0 if rec.report() else 1)
