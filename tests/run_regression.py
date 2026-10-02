# -*- coding: utf-8 -*-
"""回归套件总入口 —— CI 门禁用。

一次运行覆盖两组互补的断言：

  S 组（run_conformance.py）  确定性 / 可重放性
      S1 逐比特重放  S2 重复稳定  S3 标量容差  S4 时钟前提（负向）

  R 组（本目录）                语义契约
      R1 防御机制语义契约          test_defense.py
      R2 审计状态转移归因          test_audit_delta.py
      R3 心境受迫-阻尼动力学       test_mood_dynamics.py
      R4 未成年变体对齐            test_minor_variant.py
      R5 规范与实现一致            test_doc_contract.py
      R6 变异守卫（断言判别力）    test_mutation_guard.py

两组缺一不可：
  S 组能发现"行为变了"，但说不出"为什么变"；哈希是黑箱。
  R 组把契约写成可读断言，使变化可归因；但无法替代逐比特重放。
  R6 保证 R 组不会退化成恒真断言——注入缺陷后 R 组必须变红。

退出码：0 = 全部通过；1 = 存在失败。
"""
from __future__ import annotations

import argparse
import io
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

R_SUITE = [
    ("R1", "test_defense.py", "防御机制语义契约"),
    ("R2", "test_audit_delta.py", "审计状态转移归因"),
    ("R3", "test_mood_dynamics.py", "心境受迫-阻尼动力学"),
    ("R4", "test_minor_variant.py", "未成年变体对齐"),
    ("R5", "test_doc_contract.py", "规范与实现一致"),
    ("R6", "test_mutation_guard.py", "变异守卫（断言判别力）"),
]
S_SCRIPT = "run_conformance.py"


def run_script(script, env_extra=None):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if env_extra:
        env.update(env_extra)
    p = subprocess.run([sys.executable, str(HERE / script)],
                       capture_output=True, env=env, text=True,
                       encoding="utf-8", errors="replace", cwd=str(ROOT))
    out = (p.stdout or "") + (p.stderr or "")
    counts = parse_counts(out)
    return p.returncode, out, counts


def parse_counts(out):
    """从子脚本输出里抽出断言计数与失败项名。

    两种输出格式都要认：
      "  R3 心境…: 23/23 passed"              （R 组）
      "  Result: 25/25 passed    (0.10s)"     （run_conformance.py）
    """
    total = passed = None
    for m in re.finditer(r"(\d+)\s*/\s*(\d+)\s*passed", out):
        passed, total = int(m.group(1)), int(m.group(2))
    fails = []
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("[FAIL]"):
            fails.append(s[7:].strip())
    return {"total": total, "passed": passed, "failures": fails}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="SPL 引擎回归套件：确定性(S1-S4) + 语义契约(R1-R6)")
    ap.add_argument("--verbose", action="store_true", help="打印全部子套件输出")
    ap.add_argument("--out-dir", default=None, help="写汇总报告到该目录")
    ap.add_argument("--skip-conformance", action="store_true",
                    help="只跑 R 组，跳过 S 组")
    ap.add_argument("--only", default=None,
                    help="只跑指定子套件，如 R3 或 S")
    args = ap.parse_args(argv)

    results = []
    report = []

    def banner(text):
        print()
        print("=" * 78)
        print(text)
        print("=" * 78)

    jobs = []
    if not args.skip_conformance and (args.only in (None, "S")):
        jobs.append(("S1-S4", S_SCRIPT, "确定性 / 可重放性"))
    for rid, script, title in R_SUITE:
        if args.only in (None, rid):
            jobs.append((rid, script, title))

    if not jobs:
        print("[FATAL] 没有匹配的子套件: --only %s" % args.only)
        return 2

    for rid, script, title in jobs:
        banner("%s  %s  (%s)" % (rid, title, script))
        code, out, counts = run_script(script)
        print(out.rstrip())
        results.append((rid, title, code == 0, counts))
        report.append("=" * 78)
        report.append("%s  %s  ->  %s" % (rid, title,
                                          "PASS" if code == 0 else "FAIL"))
        report.append(out.rstrip())
        report.append("")

    banner("汇总")
    ok_all = True
    tot_p = tot_t = 0
    for rid, title, ok, counts in results:
        p, t = counts["passed"], counts["total"]
        if p is not None and t is not None:
            tot_p += p
            tot_t += t
            detail = "%d/%d" % (p, t)
        else:
            detail = "-"
        print("  %-6s %-24s %-10s %s"
              % (rid, title, "PASS" if ok else "FAIL", detail))
        if counts["failures"]:
            for f in counts["failures"]:
                print("           - %s" % f)
        ok_all = ok_all and ok
    if tot_t:
        print()
        print("  断言合计: %d/%d passed" % (tot_p, tot_t))
    print()
    print("  总体: %s" % ("全部通过" if ok_all else "存在失败"))

    if args.out_dir:
        out = Path(args.out_dir).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        (out / "regression_report.txt").write_text(
            "\n".join(report), encoding="utf-8")
        (out / "regression_results.json").write_text(
            __import__("json").dumps(
                {"results": [{"id": r[0], "title": r[1], "ok": r[2],
                              "counts": r[3]} for r in results],
                 "all_passed": ok_all},
                ensure_ascii=False, indent=2),
            encoding="utf-8")
        print("\n  报告已写入 -> %s" % out)

    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
