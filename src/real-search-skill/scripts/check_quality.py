#!/usr/bin/env python3
"""Check a real-search workspace for minimum research completeness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FILES = ["研究计划.md", "资料索引.md", "阶段日志.md", "论文阅读队列.md", "多角色任务板.md"]
REQUIRED_DIRS = ["项目调研记录", "论文调研记录", "源码阅读记录", "网页摘录", "外部源码", "自动发现", "论文PDF", "论文正文"]
SYNTHESIS_FILES = ["调研报告.md", "学习总结.md", "落地方案.md", "MVP路线图.md", "对比矩阵.md", "质量检查报告.md"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Quality check for a real-search workspace.")
    parser.add_argument("workspace")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    checks: list[dict[str, object]] = []

    def add_check(name: str, passed: bool, evidence: str, severity: str = "pass") -> None:
        checks.append({
            "check": name,
            "passed": passed,
            "severity": severity,
            "evidence": evidence,
        })

    for name in REQUIRED_FILES:
        path = workspace / name
        add_check(f"file:{name}", path.exists(), str(path))

    for name in REQUIRED_DIRS:
        path = workspace / name
        add_check(f"dir:{name}", path.is_dir(), str(path))

    index_path = workspace / "资料索引.md"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        add_check(
            "source-index-has-evidence-levels",
            "证据等级" in text and any(level in text for level in ["A-源码/官方", "B-论文/技术报告", "C-社区/博客", "D-待验证"]),
            str(index_path),
        )
        data_rows = [line for line in text.splitlines() if line.startswith("|") and "---" not in line]
        add_check("source-index-has-entries", len(data_rows) > 1, f"{len(data_rows) - 1} source rows in {index_path}")

    queue_path = workspace / "论文阅读队列.md"
    if queue_path.exists():
        queue_text = queue_path.read_text(encoding="utf-8")
        queue_rows = [line for line in queue_text.splitlines() if line.startswith("|") and "---" not in line]
        add_check("paper-queue-has-entries", len(queue_rows) > 1, f"{len(queue_rows) - 1} paper rows in {queue_path}")

    task_board = workspace / "多角色任务板.md"
    if task_board.exists():
        text = task_board.read_text(encoding="utf-8")
        add_check(
            "task-board-has-roles",
            all(role in text for role in ["planner", "explorer", "paper-reader", "source-reader", "reviewer", "synthesizer"]),
            str(task_board),
        )

    note_count = 0
    for directory in ["项目调研记录", "论文调研记录", "网页摘录", "源码阅读记录"]:
        note_dir = workspace / directory
        if note_dir.exists():
            note_count += len([p for p in note_dir.glob("*.md") if p.is_file()])
    add_check("has-per-source-notes", note_count > 0, f"{note_count} markdown notes across note directories")

    route_count = len([p for p in (workspace / "源码阅读记录").glob("*-阅读路线.md") if p.is_file()]) if (workspace / "源码阅读记录").exists() else 0
    add_check("has-source-reading-route", route_count > 0, f"{route_count} source reading route files")

    discovery_dir = workspace / "自动发现"
    discovery_count = len([p for p in discovery_dir.glob("*") if p.is_file()]) if discovery_dir.exists() else 0
    add_check("has-auto-discovery-artifacts", discovery_count > 0, f"{discovery_count} files in {discovery_dir}")

    synthesis = [name for name in SYNTHESIS_FILES if (workspace / name).exists() and (workspace / name).stat().st_size > 20]
    add_check("has-synthesis-document", bool(synthesis), ", ".join(synthesis) if synthesis else "no non-empty synthesis document found")

    if (workspace / "项目调研记录").exists():
        risky_notes = []
        for path in (workspace / "项目调研记录").glob("*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "README" in text and "源码阅读路径" not in text:
                risky_notes.append(path.name)
        severity = "warn" if risky_notes else "pass"
        add_check("risky-readme-only-project-notes", not risky_notes, ", ".join(risky_notes) if risky_notes else "none", severity=severity)

    passed = sum(1 for item in checks if item["passed"])
    warnings = sum(1 for item in checks if item.get("severity") == "warn")
    result = {
        "workspace": str(workspace),
        "passed": passed,
        "warnings": warnings,
        "failed": len(checks) - passed,
        "total": len(checks),
        "checks": checks,
    }

    report_lines = ["# 质量检查报告", ""]
    for item in checks:
        status = "PASS" if item["passed"] else ("WARN" if item.get("severity") == "warn" else "FAIL")
        report_lines.append(f"- {status} {item['check']}：{item['evidence']}")
    report_lines.append("")
    report_lines.append(f"Summary: {passed}/{len(checks)} passed, {warnings} warnings")
    if args.write_report:
        (workspace / "质量检查报告.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in checks:
            marker = "PASS" if item["passed"] else ("WARN" if item.get("severity") == "warn" else "FAIL")
            print(f"{marker} {item['check']} - {item['evidence']}")
        print(f"Summary: {passed}/{len(checks)} passed, {warnings} warnings")

    raise SystemExit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
