# -*- coding: utf-8 -*-
"""R5 · 数据契约标准与实现的一致性

规范 `docs/agent-standard.md` 里的键集、常数、入口点一旦与实现漂移，
文档就是有害的。本文件把两者绑在一起：任一侧改动而另一侧未跟进，直接失败。

**边界**：本文件校验的是"文档与代码同步"，不是"语义正确"。
文档与实现同时写错时本套件照样通过——语义正确性由 R1/R2/R3/R4 与
外部实验（反事实对照）负责。
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from _harness import (ENGINE_PATH, MINOR_PATH, STANDARD_PATH,  # noqa: E402
                      Recorder, audit_core, fresh, load_engine,
                      main_core, minor_core)

# 旧文档名按两段拼接：本文件需要检测该名称是否残留在别处，
# 若在此处写成连续字面量，扫描会命中自己而永远失败。
OLD_DOC_NAME = "anthromorphic-agent-engine-" + "standards"
TARGETS = {"main": ENGINE_PATH, "minor": MINOR_PATH}
CORE = {"main": main_core, "minor": minor_core}


def summarize_keys(mod, core_cls):
    """驱动一次事件，取审计记录里的状态摘要键序。"""
    d = tempfile.mkdtemp(prefix="aae_r5_")
    c = fresh(core_cls, audit=True, log_dir=d, audit_session_id="r5")
    c.process_event("rest", 1.0)
    from _harness import read_records
    recs = read_records(d)
    return list(recs[0]["snapshot"].keys()) if recs else []


def doc_keylists(doc, label):
    """取形如 **[主]**（N 键）：`a, b, c` 的行。"""
    pat = re.compile(r"\*\*\[%s\]\*\*（(\d+) 键）：`([^`]+)`" % label)
    return [(int(g1), [x.strip() for x in g2.split(",")])
            for g1, g2 in pat.findall(doc)]


def build():
    rec = Recorder("R5 规范与实现一致")
    if not STANDARD_PATH.exists():
        rec.fail("规范文档存在", str(STANDARD_PATH))
        return rec
    doc = open(STANDARD_PATH, "r", encoding="utf-8").read()
    mods = {t: load_engine(p, "r5_" + t) for t, p in TARGETS.items()}

    # ------------------------------------------------------------------
    rec.section("1. 键集：文档声明 vs 实际输出")
    # ------------------------------------------------------------------
    lists = {"主": doc_keylists(doc, "主"), "未": doc_keylists(doc, "未")}
    rec.check("文档中 [主] 键集行数 == 2", len(lists["主"]) == 2,
              str(len(lists["主"])))
    rec.check("文档中 [未] 键集行数 == 2", len(lists["未"]) == 2,
              str(len(lists["未"])))

    for tag in ("main", "minor"):
        label = "主" if tag == "main" else "未"
        core_cls = CORE[tag](mods[tag])
        full = list(fresh(core_cls, audit_enabled=False).snapshot().keys())
        summ = summarize_keys(mods[tag], core_cls)
        rec.note("%s  实现 snapshot %d 键 / 摘要 %d 键" % (tag, len(full),
                                                          len(summ)))
        rec.check("%s snapshot 无重复键" % tag, len(full) == len(set(full)))
        for declared_n, keys in lists[label]:
            kind = "snapshot" if len(keys) == len(full) else "摘要"
            actual = full if kind == "snapshot" else summ
            if set(keys) == set(actual) and declared_n == len(keys):
                rec.check("%s §%s 键集与实现一致（%d 键）"
                          % (tag, kind, len(keys)), True)
            else:
                rec.check("%s §%s 键集与实现一致" % (tag, kind), False,
                          "声明 %d / 文档 %d / 实现 %d  差异=%s"
                          % (declared_n, len(keys), len(actual),
                             sorted(set(keys) ^ set(actual)) or "计数不符"))

    # ------------------------------------------------------------------
    rec.section("2. delta 覆盖集：文档列出实现中的每一项")
    # ------------------------------------------------------------------
    for tag in ("main", "minor"):
        A = mods[tag].AuditLogger
        scalars, nested = list(A.DELTA_SCALARS), list(A.DELTA_NESTED)
        rec.note("%s DELTA_SCALARS(%d): %s" % (tag, len(scalars),
                                               ", ".join(scalars)))
        rec.note("%s DELTA_NESTED (%d): %s" % (tag, len(nested),
                                               ", ".join(nested)))
        for name, vals in (("DELTA_SCALARS", scalars), ("DELTA_NESTED", nested)):
            missing = [v for v in vals if v not in doc]
            rec.check("%s 文档列出 %s 全部项" % (tag, name), not missing,
                      "缺=%s" % missing)
        must = {"self_esteem", "energy", "fatigue", "excitation", "max_trust",
                "latent_pressure", "cognitive_dissonance", "sleep_debt",
                "arousal_recent", "memory_count", "expected_count"}
        rec.check("%s delta 覆盖全部 §5.7 标量" % tag, must <= set(scalars),
                  "缺=%s" % sorted(must - set(scalars)))

    # ------------------------------------------------------------------
    rec.section("3. 流体 / 心境维度与初值")
    # ------------------------------------------------------------------
    for tag in ("main", "minor"):
        c = fresh(CORE[tag](mods[tag]), audit_enabled=False)
        rec.check("%s fluid 恰 8 维" % tag, len(c.fluid) == 8, str(len(c.fluid)))
        rec.check("%s fluid 各键在文档中" % tag,
                  all(k in doc for k in c.fluid),
                  "缺=%s" % [k for k in c.fluid if k not in doc])
        rec.check("%s mood 恰 3 维" % tag, len(c.mood) == 3, str(len(c.mood)))
        rec.check("%s mood 各键在文档中" % tag,
                  all(k in doc for k in c.mood),
                  "缺=%s" % [k for k in c.mood if k not in doc])
        bl = getattr(c, "fluid_baseline", None)
        rec.check("%s 初始态与基线态不同（文档据此区分 §5.2）" % tag,
                  bl is not None and c.fluid != bl,
                  "初始喜悦=%s 基线喜悦=%s" % (c.fluid["喜悦"], bl["喜悦"]))

    # ------------------------------------------------------------------
    rec.section("4. 入口点与心境常数")
    # ------------------------------------------------------------------
    for tag in ("main", "minor"):
        c = fresh(CORE[tag](mods[tag]), audit_enabled=False)
        for m in ("process_vector", "process_event", "idle", "sleep", "expect",
                  "induce_dissonance", "snapshot", "set_clock",
                  "advance_clock"):
            rec.check("%s 暴露 §6 入口 %s" % (tag, m), hasattr(c, m))
        for k in ("MOOD_RATE_BASE", "MOOD_AROUSAL_GAIN", "MOOD_AROUSAL_TAU",
                  "MOOD_AROUSAL_EMA", "MOOD_DOSE_PLEASANT",
                  "MOOD_DOSE_TENSION", "MOOD_DOSE_VIGOR"):
            v = getattr(c, k)
            s = "%g" % v
            rec.check("%s 文档记录 %s = %s" % (tag, k, s), s in doc,
                      "文档中找不到 %s" % s)

    # ------------------------------------------------------------------
    rec.section("5. 变体差异：文档声明 vs 实现")
    # ------------------------------------------------------------------
    cm = fresh(CORE["main"](mods["main"]), audit_enabled=False)
    cn = fresh(CORE["minor"](mods["minor"]), audit_enabled=False)
    rec.check("主引擎有防御仓，未成年没有",
              hasattr(cm, "suppression_load")
              and not hasattr(cn, "suppression_load"))
    rec.check("主引擎有 trauma，未成年没有",
              hasattr(cm, "trauma_state")
              and not hasattr(cn, "trauma_state"))
    rec.check("未成年有 protective，主引擎没有",
              "protective" in cn.snapshot() and "protective" not in cm.snapshot())
    rec.check("文档声明心理韧性 0.5 / 0.6",
              abs(cm.psychological_resilience - 0.5) < 1e-9
              and abs(cn.psychological_resilience - 0.6) < 1e-9)
    rec.check("文档声明未成年负性钳位 0.75、依恋上限 0.8",
              abs(cn.EMOTION_CEIL_NEG - 0.75) < 1e-9
              and abs(cn.ATTACH_MAX - 0.8) < 1e-9)
    rec.check("文档 §5.6 声明未成年 MUST NOT 建模创伤累积",
              "MUST NOT** 建模创伤累积" in doc
              or "MUST NOT** 包含 `trauma_state`" in doc)

    # ------------------------------------------------------------------
    rec.section("6. 文档与向量元数据")
    # ------------------------------------------------------------------
    meta_path = HERE / "conformance_vectors.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8")).get("meta", {})
        rec.check("向量文件记录生成时间", "generated_at" in meta,
                  str(sorted(meta.keys())))
        rec.check("向量文件记录生成环境", "generated_with" in meta)
        rec.check("向量文件记录哈希算法", "hash" in meta)
        rec.check("向量文件记录哈希适用范围",
                  "snapshot_sha256_scope" in meta)
        rec.check("向量文件记录复现命令", "reproduce" in meta)
    else:
        rec.fail("向量文件存在", str(meta_path))

    rec.section("7. 旧文档名无残留")
    stale = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs
                   if x not in (".git", ".venv", "logs", "__pycache__")]
        for fn in files:
            if not fn.endswith((".md", ".py", ".json", ".toml")):
                continue
            p = os.path.join(root, fn)
            if p == str(STANDARD_PATH):
                continue          # 规范自身在 §0 说明旧名，属预期
            try:
                t = open(p, "r", encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if OLD_DOC_NAME in t:
                stale.append(os.path.relpath(p, ROOT))
    rec.check("无残留旧文档名引用", not stale, str(stale))
    rec.check("旧文档已不存在",
              not (ROOT / "docs" / (OLD_DOC_NAME + ".md")).exists())
    rec.check("规范文档成规模", len(doc) > 10000, "%d 字符" % len(doc))

    return rec


if __name__ == "__main__":
    rec = build()
    sys.exit(0 if rec.report() else 1)
