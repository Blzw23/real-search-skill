#!/usr/bin/env python3
"""Check a real-search workspace for minimum research completeness."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_FILES = ["研究计划.md", "资料索引.md", "阶段日志.md", "论文阅读队列.md", "多角色任务板.md"]
REQUIRED_DIRS = ["项目调研记录", "论文调研记录", "源码阅读记录", "网页摘录", "外部源码", "自动发现", "论文PDF", "论文正文"]
SYNTHESIS_FILES = ["调研报告.md", "学习总结.md", "落地方案.md", "MVP路线图.md", "对比矩阵.md", "质量检查报告.md"]
EVIDENCE_MARKERS = ["A-源码/官方", "B-论文/技术报告", "C-社区/博客", "D-待验证", "证据等级"]
UNCERTAINTY_MARKERS = ["待验证", "不确定", "局限", "风险", "假设"]
NEXT_STEP_MARKERS = ["下一步", "路线图", "MVP", "落地", "行动项", "后续"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def markdown_files(directory: Path) -> list[Path]:
    return sorted([p for p in directory.glob("*.md") if p.is_file()]) if directory.exists() else []


def has_source_path(text: str) -> bool:
    path_like = re.search(r"(?:src|lib|app|packages|tests|examples|docs|scripts|README)\S*", text, re.I)
    return bool(path_like or "源码阅读路径" in text or "关键文件" in text or "源码路径" in text)


def add_content_warning(add_check, name: str, passed: bool, evidence: str) -> None:
    add_check(name, passed, evidence, severity="warn" if not passed else "pass")


def write_review_checklist(workspace: Path, checks: list[dict[str, object]]) -> Path:
    warnings = [item for item in checks if not item["passed"] and item.get("severity") == "warn"]
    lines = [
        "# 内容复核清单",
        "",
        "这份清单给 reviewer 角色使用，用于人工/Codex 复核“看起来完整”的调研是否真的有证据支撑。",
        "",
        "## 自动发现的内容风险",
        "",
    ]
    if warnings:
        for item in warnings:
            lines.append(f"- [ ] {item['check']}：{item['evidence']}")
    else:
        lines.append("- 暂无自动发现的内容 warning。")
    lines.extend([
        "",
        "## Reviewer 复核问题",
        "",
        "- [ ] 最终报告的关键结论是否能追溯到官方文档、论文正文或源码路径？",
        "- [ ] 是否存在只看 README 或二手博客就下结论的段落？",
        "- [ ] 每个项目/框架笔记是否记录了技术栈、入口文件、核心模块或插件扩展点？",
        "- [ ] 每篇论文笔记是否说明了方法、局限、工程启发，以及和当前目标的关系？",
        "- [ ] 自动发现的搜索入口是否已经被二次验证，而不是直接进入正式结论？",
        "- [ ] PDF 正文抽取质量低、疑似扫描版或待 OCR 的论文，是否被标注为待人工阅读？",
        "- [ ] 报告是否写清了不确定项、风险、下一步动作或 MVP 路线？",
    ])
    target = workspace / "内容复核清单.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Quality check for a real-search workspace.")
    parser.add_argument("workspace")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-review", action="store_true")
    parser.add_argument("--strict-content", action="store_true", help="Treat content heuristic warnings as failures.")
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
        text = read_text(index_path)
        add_check(
            "source-index-has-evidence-levels",
            "证据等级" in text and any(level in text for level in ["A-源码/官方", "B-论文/技术报告", "C-社区/博客", "D-待验证"]),
            str(index_path),
        )
        data_rows = [line for line in text.splitlines() if line.startswith("|") and "---" not in line]
        add_check("source-index-has-entries", len(data_rows) > 1, f"{len(data_rows) - 1} source rows in {index_path}")

    queue_path = workspace / "论文阅读队列.md"
    if queue_path.exists():
        queue_text = read_text(queue_path)
        queue_rows = [line for line in queue_text.splitlines() if line.startswith("|") and "---" not in line]
        add_check("paper-queue-has-entries", len(queue_rows) > 1, f"{len(queue_rows) - 1} paper rows in {queue_path}")

    task_board = workspace / "多角色任务板.md"
    if task_board.exists():
        text = read_text(task_board)
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
            text = read_text(path)
            if "README" in text and "源码阅读路径" not in text:
                risky_notes.append(path.name)
        severity = "warn" if risky_notes else "pass"
        add_check("risky-readme-only-project-notes", not risky_notes, ", ".join(risky_notes) if risky_notes else "none", severity=severity)

    synthesis_paths = [workspace / name for name in SYNTHESIS_FILES if (workspace / name).exists() and (workspace / name).is_file()]
    synthesis_text = "\n".join(read_text(path) for path in synthesis_paths)
    if synthesis_paths:
        add_content_warning(
            add_check,
            "content-synthesis-has-evidence-markers",
            any(marker in synthesis_text for marker in EVIDENCE_MARKERS),
            ", ".join(path.name for path in synthesis_paths),
        )
        add_content_warning(
            add_check,
            "content-synthesis-has-source-references",
            bool(re.search(r"https?://|`[^`]+`|资料索引|项目调研记录|论文调研记录|源码阅读记录", synthesis_text)),
            ", ".join(path.name for path in synthesis_paths),
        )
        add_content_warning(
            add_check,
            "content-synthesis-has-uncertainty",
            any(marker in synthesis_text for marker in UNCERTAINTY_MARKERS),
            ", ".join(path.name for path in synthesis_paths),
        )
        add_content_warning(
            add_check,
            "content-synthesis-has-next-actions",
            any(marker in synthesis_text for marker in NEXT_STEP_MARKERS),
            ", ".join(path.name for path in synthesis_paths),
        )

    project_notes = markdown_files(workspace / "项目调研记录")
    if project_notes:
        missing_paths = [path.name for path in project_notes if not has_source_path(read_text(path))]
        add_content_warning(
            add_check,
            "content-project-notes-have-source-paths",
            not missing_paths,
            ", ".join(missing_paths) if missing_paths else "all project notes mention source paths/key files",
        )

    paper_notes = markdown_files(workspace / "论文调研记录")
    if paper_notes:
        missing_fields: list[str] = []
        required_sections = ["工程启发", "局限", "和当前目标的关系"]
        for path in paper_notes:
            text = read_text(path)
            missing = [section for section in required_sections if section not in text]
            if missing:
                missing_fields.append(f"{path.name} 缺少 {'/'.join(missing)}")
            if "正文抽取质量" not in text:
                missing_fields.append(f"{path.name} 缺少正文抽取质量")
        add_content_warning(
            add_check,
            "content-paper-notes-have-engineering-review",
            not missing_fields,
            "; ".join(missing_fields) if missing_fields else "all paper notes include engineering/limits/relevance fields",
        )

    if args.write_review:
        review_path = write_review_checklist(workspace, checks)
        add_check("content-review-checklist-written", review_path.exists(), str(review_path))

    passed = sum(1 for item in checks if item["passed"])
    warnings = sum(1 for item in checks if not item["passed"] and item.get("severity") == "warn")
    hard_failures = [item for item in checks if not item["passed"] and item.get("severity") != "warn"]
    strict_failures = [item for item in checks if not item["passed"] and item.get("severity") == "warn"] if args.strict_content else []
    result = {
        "workspace": str(workspace),
        "passed": passed,
        "warnings": warnings,
        "failed": len(hard_failures) + len(strict_failures),
        "hard_failed": len(hard_failures),
        "strict_content": args.strict_content,
        "total": len(checks),
        "checks": checks,
    }

    report_lines = ["# 质量检查报告", ""]
    for item in checks:
        status = "PASS" if item["passed"] else ("WARN" if item.get("severity") == "warn" else "FAIL")
        report_lines.append(f"- {status} {item['check']}：{item['evidence']}")
    report_lines.append("")
    report_lines.append(f"Summary: {passed}/{len(checks)} passed, {warnings} warnings, {len(hard_failures)} hard failures")
    if args.strict_content and warnings:
        report_lines.append("Strict content mode: content warnings are treated as failures.")
    if args.write_report:
        (workspace / "质量检查报告.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in checks:
            marker = "PASS" if item["passed"] else ("WARN" if item.get("severity") == "warn" else "FAIL")
            print(f"{marker} {item['check']} - {item['evidence']}")
        print(f"Summary: {passed}/{len(checks)} passed, {warnings} warnings, {len(hard_failures)} hard failures")
        if args.strict_content and warnings:
            print("Strict content mode: content warnings are treated as failures.")

    raise SystemExit(1 if hard_failures or strict_failures else 0)


if __name__ == "__main__":
    main()
