#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPL Pure Core V8.0 — 确定性 / 可复现性 一致性测试（Conformance Suite）

零依赖：仅使用 Python 标准库。克隆仓库后可直接运行：

    python tests/run_conformance.py
    python tests/run_conformance.py --verbose
    python tests/run_conformance.py --out-dir ./reports
    python tests/run_conformance.py --update-baseline

------------------------------------------------------------------
被测声明（README §Core）
------------------------------------------------------------------
    "The engine models the general human mental architecture as
     deterministic, continuous-state subsystems — no LLM, no randomness,
     fully replayable"

本套件把这个声明拆成四条可执行的断言，逐条判定。判定结果是二元的
（PASS / FAIL），不产生分数、不做主观解释。

------------------------------------------------------------------
测试项
------------------------------------------------------------------
S1  bit-exact replay    注入虚拟时钟后，每个向量的 snapshot SHA256
                         必须与基线逐比特相同。
S2  repeat stability    同一向量连跑 N 次，N 次哈希必须全同
                         （证明引擎没有隐藏状态在实例之间泄漏）。
S3  scalar tolerance    跨平台稳健层：关键标量按 1e-9 容差比对。
                         snapshot 哈希对解释器/平台敏感，标量比对
                         用于跨环境复核。
S4  clock premise       【负向测试】不注入时钟时，同一向量两次运行
                         的结果**必须不同**。
                         该断言被刻意设计为"必须失败才算通过"：
                         它证明 "fully replayable" 依赖 set_clock()
                         这一未在文档中声明的前提。
                         若 S4 失败（自然时钟下竟然一致），说明该前提
                         不成立，应同步修正文档。

------------------------------------------------------------------
时钟前提（重要）
------------------------------------------------------------------
引擎 `_now()` 在 `_clock_override is None` 时回落 `time.time()`。
因此**可复现性只在显式调用 `set_clock()` 之后成立**。
任何宣称"可复现"的对外材料，都必须同时声明这一前提。

退出码：0 = 全部通过；1 = 存在失败。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import sys
import time
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENGINE_PATH = ROOT / "SPL-anthropic-engine.py"
VECTORS_PATH = HERE / "conformance_vectors.json"

CLOCK_ORIGIN = 1000.0
REPEATS = 3          # S2：每向量重复次数
NATURAL_RUNS = 2     # S4：自然时钟运行次数
NATURAL_GAP = 0.05   # S4：两次自然时钟运行之间的间隔（秒），确保时间推进


# ----------------------------------------------------------------------
# 工具
# ----------------------------------------------------------------------
def load_engine(path: Path):
    """动态导入引擎（源文件名含连字符，无法用普通 import）。"""
    if not path.exists():
        sys.exit(f"[FATAL] engine not found: {path}")
    spec = importlib.util.spec_from_file_location("spl_core", path)
    mod = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)  # 静默：模块顶层有演示输出
    return mod


def snap_hash(snapshot) -> str:
    payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def execute(core, steps):
    """按向量定义回放操作序列。"""
    for op, args in steps:
        if op == "event":
            core.process_event(args[0], args[1])
        elif op == "idle":
            core.idle(args[0])
        elif op == "sleep":
            core.sleep(args[0])
        elif op == "expect":
            core.expect(args[0], args[1], args[2])
        elif op == "dissonance":
            core.induce_dissonance(args[0])
        else:
            raise ValueError(f"unknown step op: {op!r}")


def run_vector(Core, steps, clock=CLOCK_ORIGIN):
    """执行单个向量。clock=None 表示不注入时钟（走真实时钟）。"""
    core = Core(audit_enabled=False)   # 审计关闭：不写 logs/，保证零污染
    if clock is not None:
        core.set_clock(clock)
    execute(core, steps)
    return core.snapshot()


def close(a, b, tol: float) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol
    return a == b


# ----------------------------------------------------------------------
# 测试
# ----------------------------------------------------------------------
def run_suite():
    spec = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    meta = spec["meta"]
    vectors = spec["vectors"]
    tol = float(meta.get("tolerance", 1e-9))

    Core = load_engine(ENGINE_PATH).SPLPureCoreV7_3

    results = []      # (suite, vector_id, passed, detail)
    natural_hashes = []

    # ---- S1 + S2：逐比特复现 / 重复稳定 ----
    for v in vectors:
        vid = v["id"]
        baseline = v["snapshot_sha256"]

        try:
            got = snap_hash(run_vector(Core, v["steps"]))
        except Exception as exc:                              # noqa: BLE001
            results.append(("S1", vid, False, f"exception: {type(exc).__name__}: {exc}"))
            results.append(("S2", vid, False, "skipped (S1 raised)"))
            continue

        results.append(("S1", vid, got == baseline,
                        f"{got[:16]} {'==' if got == baseline else '!='} {baseline[:16]}"))

        hashes = [snap_hash(run_vector(Core, v["steps"])) for _ in range(REPEATS)]
        results.append(("S2", vid, len(set(hashes)) == 1,
                        f"{len(set(hashes))} distinct / {REPEATS} runs"))

    # ---- S3：标量容差比对 ----
    for v in vectors:
        vid = v["id"]
        got = run_vector(Core, v["steps"])
        bad = []
        for key, want in (v.get("scalars") or {}).items():
            have = got.get(key)
            if not close(have, want, tol):
                bad.append(f"{key}: {have!r} != {want!r}")
        results.append(("S3", vid, not bad, "; ".join(bad) if bad else f"all scalars within {tol:g}"))

    # ---- S4：时钟前提（负向测试）----
    probe = vectors[0]
    for i in range(NATURAL_RUNS):
        natural_hashes.append(snap_hash(run_vector(Core, probe["steps"], clock=None)))
        if i < NATURAL_RUNS - 1:
            time.sleep(NATURAL_GAP)
    distinct = len(set(natural_hashes))
    premise_holds = distinct > 1
    results.append((
        "S4", probe["id"], premise_holds,
        f"natural-clock produced {distinct}/{NATURAL_RUNS} distinct hashes "
        f"-> {'premise confirmed: replay requires set_clock()' if premise_holds else 'premise NOT observed: natural clock was reproducible'}",
    ))

    return meta, vectors, results, natural_hashes


# ----------------------------------------------------------------------
# 报告
# ----------------------------------------------------------------------
SUITE_TITLES = {
    "S1": "bit-exact replay (snapshot SHA256 == baseline)",
    "S2": "repeat stability (no cross-instance state leak)",
    "S3": "scalar tolerance (cross-platform robust layer)",
    "S4": "clock-injection premise (NEGATIVE test — must differ to pass)",
}


def render(meta, vectors, results, natural_hashes, verbose: bool, elapsed: float) -> str:
    by_id = {v["id"]: v["name"] for v in vectors}
    lines = []
    lines.append("SPL Pure Core V8.0 — Determinism / Replayability Conformance")
    lines.append("=" * 72)
    lines.append(f"engine      : {ENGINE_PATH.name}")
    lines.append(f"vectors     : {VECTORS_PATH.relative_to(ROOT)} ({len(vectors)})")
    lines.append(f"python      : {sys.version.split()[0]} ({sys.platform})")
    lines.append(f"clock       : injected, origin={meta.get('clock_origin')}")
    lines.append(f"generated   : {meta.get('generated_at')} with {meta.get('generated_with')}")
    lines.append(f"finished    : {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append("")

    for suite in ("S1", "S2", "S3", "S4"):
        rs = [r for r in results if r[0] == suite]
        if not rs:
            continue
        passed = sum(1 for r in rs if r[2])
        lines.append(f"[{suite}] {SUITE_TITLES[suite]}   ({passed}/{len(rs)})")
        for _, vid, ok, detail in rs:
            mark = "PASS" if ok else "FAIL"
            if ok and not verbose and suite != "S4":
                continue
            lines.append(f"   [{mark}] {vid} {by_id.get(vid, ''):<26} {detail}")
        if suite == "S4":
            lines.append(f"   natural-clock hashes: {', '.join(h[:16] for h in natural_hashes)}")
        lines.append("")

    total = len(results)
    passed = sum(1 for r in results if r[2])
    lines.append("=" * 72)
    lines.append(f"  Result: {passed}/{total} passed    ({elapsed:.2f}s)")
    lines.append("")
    lines.append("  Note: 'fully replayable' requires an explicit set_clock() call.")
    lines.append("        Without it _now() falls back to time.time() and results differ.")
    lines.append("        This premise must accompany any external reproducibility claim.")
    return "\n".join(lines)


def update_baseline(meta, vectors):
    Core = load_engine(ENGINE_PATH).SPLPureCoreV7_3
    for v in vectors:
        snap = run_vector(Core, v["steps"])
        v["snapshot_sha256"] = snap_hash(snap)
        v["scalars"] = {
            k: snap[k] for k in v.get("scalars", {}) if k in snap
        } or {k: snap[k] for k in sorted(snap) if isinstance(snap[k], (int, float))}
    VECTORS_PATH.write_text(
        json.dumps({"meta": meta, "vectors": vectors}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[baseline updated] {VECTORS_PATH}")


# ----------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="SPL Pure Core V8.0 determinism / replayability conformance suite"
    )
    ap.add_argument("--verbose", action="store_true", help="print every case, not only failures")
    ap.add_argument("--out-dir", default=None, help="write report + raw results into this directory")
    ap.add_argument("--update-baseline", action="store_true",
                    help="recompute expected hashes from the current engine (use with care)")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:                                     # noqa: BLE001
            pass

    if not VECTORS_PATH.exists():
        sys.exit(f"[FATAL] vectors not found: {VECTORS_PATH}")

    t0 = time.perf_counter()
    meta, vectors, results, natural_hashes = run_suite()

    if args.update_baseline:
        update_baseline(meta, vectors)
        return 0

    elapsed = time.perf_counter() - t0
    report = render(meta, vectors, results, natural_hashes, args.verbose, elapsed)
    print(report)

    if args.out_dir:
        out = Path(args.out_dir).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        (out / "conformance_report.txt").write_text(report, encoding="utf-8")
        raw = {
            "meta": meta,
            "python": sys.version,
            "platform": sys.platform,
            "elapsed_seconds": round(elapsed, 3),
            "natural_clock_hashes": natural_hashes,
            "cases": [
                {"suite": s, "vector": vid, "passed": ok, "detail": d}
                for s, vid, ok, d in results
            ],
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r[2]),
                "failed": sum(1 for r in results if not r[2]),
            },
        }
        (out / "conformance_results.json").write_text(
            json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n  report written -> {out}")

    return 0 if all(r[2] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
