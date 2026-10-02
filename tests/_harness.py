# -*- coding: utf-8 -*-
"""回归测试共用测试台。零依赖（仅标准库）。

与 run_conformance.py 的分工：
  run_conformance.py  测"确定性"——同一输入能否逐比特复现
  本目录 R 系列       测"语义契约"——该发生的事有没有发生

两者互补：哈希能测出行为变了，但说不出为什么变；R 系列把契约写成
可读断言，使行为变化可归因。
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# 环境变量注入：供 R6 变异守卫把被测引擎换成临时目录里的变体。
# 缺省指向仓库内的引擎。
ENGINE_PATH = Path(os.environ.get("AAE_ENGINE")
                   or (ROOT / "SPL-anthropic-engine.py"))
MINOR_PATH = Path(os.environ.get("AAE_MINOR")
                  or (ROOT / "minor-protection" / "SPL-anthropic-minor-engine.py"))
STANDARD_PATH = Path(os.environ.get("AAE_STANDARD")
                     or (ROOT / "docs" / "agent-standard.md"))

CLOCK_ORIGIN = 1000.0

# 稳定排序的键集合（跨平台可复现）
MOOD_KEYS = ("愉悦", "紧张", "精力")


def load_engine(path, name="engine_mod"):
    """动态导入引擎（源文件名含连字符，无法用普通 import）。"""
    path = Path(path)
    if not path.exists():
        raise SystemExit("[FATAL] engine not found: %s" % path)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)      # 静默：模块顶层可能有演示输出
    return mod


def main_core(mod):
    return mod.SPLPureCoreV7_3


def minor_core(mod):
    return mod.SPLMinorPureCore


def fresh(core_cls, clock=CLOCK_ORIGIN, audit=False, log_dir=None, **kw):
    """构造一个注入虚拟时钟的核心实例。

    规范 §8.4：set_clock() 只改虚拟时钟源，不改 last_time（后者是构造时的
    墙钟）。不同步的话首次 _advance_time 会算出负 dt 并直接早退，重放起点
    与预期不符。run_conformance.py 不做同步（其基线已包含该行为），本目录
    的契约测试必须同步，否则测的是错的区间。
    """
    kw.setdefault("audit_enabled", audit)
    if log_dir is not None:
        kw["audit_log_dir"] = log_dir
    c = core_cls(**kw)
    if clock is not None:
        c.set_clock(clock)
        c.last_time = clock
    return c


def read_records(log_dir):
    """读取审计目录下全部 JSONL 记录。"""
    out = []
    for name in sorted(os.listdir(log_dir)):
        if not name.endswith(".jsonl"):
            continue
        with io.open(os.path.join(log_dir, name), "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    return out


def audit_core(core_cls, session_id, drive, **kw):
    """构造开启审计的核心，执行 drive(core)，返回全部审计记录。"""
    d = tempfile.mkdtemp(prefix="aae_r_")
    c = fresh(core_cls, audit=True, log_dir=d, audit_session_id=session_id, **kw)
    drive(c)
    return read_records(d)


def partition_sensitivity(make_core, seconds=3600.0, parts=3600):
    """实测步长敏感性。

    返回 (细切法之间的分歧, 单步与细分之间的分歧, 两端的心境值)。

    make_core 是一个无参工厂，返回已注入时钟的核心实例。
    注意：本函数实测，不接受任何"旧实现参考值"作为常量——那种常量无法
    证明当前实现的性质，且历史上曾因来自坏探针而给出错误数字。
    """
    a = make_core()
    a.idle(seconds)

    b = make_core()
    for _ in range(parts):
        b.idle(seconds / parts)

    c = make_core()
    mid = 60
    for _ in range(max(1, int(seconds // mid))):
        c.idle(mid)

    keys = MOOD_KEYS
    fine = max(abs(b.mood[k] - c.mood[k]) for k in keys)
    coarse = max(abs(a.mood[k] - b.mood[k]) for k in keys)
    return fine, coarse, {k: a.mood[k] for k in keys}, {k: b.mood[k] for k in keys}


def displaced_mood_factory(core_cls, **kw):
    """返回一个把心境推离靶标的工厂，用于观测松弛。"""
    def factory():
        c = fresh(core_cls, **kw)
        c.mood["愉悦"] = 0.95
        c.mood["紧张"] = 0.80
        c.mood["精力"] = 0.30
        return c
    return factory


class Recorder:
    """收集断言结果。二元判定，不产生分数。"""

    def __init__(self, title):
        self.title = title
        self.total = 0
        self.passed = 0
        self.failures = []
        self.lines = []

    def section(self, name):
        self.lines.append("")
        self.lines.append("-" * 74)
        self.lines.append(name)
        self.lines.append("-" * 74)

    def check(self, name, cond, detail=""):
        self.total += 1
        ok = bool(cond)
        if ok:
            self.passed += 1
        else:
            self.failures.append(name)
        self.lines.append("  [%s] %s%s"
                          % ("PASS" if ok else "FAIL", name,
                             ("  -> " + detail) if detail else ""))
        return ok

    def note(self, text):
        self.lines.append("  %s" % text)

    def fail(self, name, detail=""):
        return self.check(name, False, detail)

    def report(self, verbose=False):
        for ln in self.lines:
            print(ln)
        print()
        if self.failures:
            print("  %s: %d/%d passed -- FAILED: %s"
                  % (self.title, self.passed, self.total,
                     ", ".join(self.failures)))
        else:
            print("  %s: %d/%d passed" % (self.title, self.passed, self.total))
        return not self.failures

    def as_dict(self):
        return {"title": self.title, "total": self.total,
                "passed": self.passed, "failures": self.failures}


def effective_rate(core, dt=60.0):
    """按规范 §8.2 复算一次有效松弛速率 k 与该 dt 下的 alpha。"""
    import math
    k = (core.MOOD_RATE_BASE
         * (1.0 + core.MOOD_AROUSAL_GAIN * core.arousal_recent))
    return k, 1.0 - math.exp(-k * dt)


def main_guard(run):
    """把一个 build_recorder 风格的函数包装成标准 main()。"""
    rec = run()
    ok = rec.report(verbose=False)
    sys.exit(0 if ok else 1)
