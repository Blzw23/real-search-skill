#!/usr/bin/env python3
"""Check a real-search workspace for minimum research completeness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FILES = ["研究计划.md", "资料索引.md", "阶段日志.md"]
REQUIRED_DIRS = ["项目调研记录", "论文调研记录", "源码阅读记录", "网页摘录", "外部源码"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Quality check for a real-search workspace.")
    parser.add_argument("workspace")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    checks: list[dict[str, object]] = []

    for name in REQUIRED_FILES:
        path = workspace / name
        checks.append({"check": f"file:{name}", "passed": path.exists(), "evidence": str(path)})

    for name in REQUIRED_DIRS:
        path = workspace / name
        checks.append({"check": f"dir:{name}", "passed": path.is_dir(), "evidence": str(path)})

    index_path = workspace / "资料索引.md"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        checks.append({
            "check": "source-index-has-evidence-levels",
            "passed": "证据等级" in text and any(level in text for level in ["A-源码/官方", "B-论文/技术报告", "C-社区/博客", "D-待验证"]),
            "evidence": str(index_path),
        })

    passed = sum(1 for item in checks if item["passed"])
    result = {
        "workspace": str(workspace),
        "passed": passed,
        "failed": len(checks) - passed,
        "total": len(checks),
        "checks": checks,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in checks:
            marker = "PASS" if item["passed"] else "FAIL"
            print(f"{marker} {item['check']} - {item['evidence']}")
        print(f"Summary: {passed}/{len(checks)} passed")

    raise SystemExit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
