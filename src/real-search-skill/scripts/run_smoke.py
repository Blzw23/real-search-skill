#!/usr/bin/env python3
"""Run a local smoke test for the real-search skill package."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a smoke test for the real-search skill.")
    parser.add_argument("--workspace", default=None, help="Optional workspace path. Defaults to a temp dir.")
    parser.add_argument("--topic", default="Smoke 测试")
    parser.add_argument("--example", default=str(ROOT.parent.parent / "repo-assets" / "examples" / "agent-framework-research"))
    args = parser.parse_args()

    root = Path(args.workspace).expanduser().resolve() if args.workspace else Path(tempfile.mkdtemp(prefix="real-search-smoke-")).resolve()
    root.mkdir(parents=True, exist_ok=True)

    run(["python3", str(ROOT / "scripts" / "init_workspace.py"), args.topic, "--mode", "研究落地", "--root", str(root), "--date", "20260525"])
    target = root / "深度调研" / "20260525-Smoke-测试"
    if not target.exists():
        candidates = sorted((root / "深度调研").glob("*")) if (root / "深度调研").exists() else []
        target = candidates[0] if candidates else root

    run(["python3", str(ROOT / "scripts" / "discover_sources.py"), args.topic, "--workspace", str(target)])
    run(["python3", str(ROOT / "scripts" / "add_source.py"), "--workspace", str(target), "--type", "官方文档", "--name", "Example", "--link", "https://example.com", "--evidence", "A-源码/官方"])
    run(["python3", str(ROOT / "scripts" / "create_note.py"), "--workspace", str(target), "--kind", "project", "--title", "Example Project"])
    run(["python3", str(ROOT / "scripts" / "create_note.py"), "--workspace", str(target), "--kind", "paper", "--title", "Example Paper"])
    paper_pdf = target / "Smoke Paper.pdf"
    paper_pdf.write_bytes(b"%PDF-1.4\n% Smoke test placeholder\n%%EOF\n")
    run(["python3", str(ROOT / "scripts" / "process_paper.py"), str(paper_pdf), "--workspace", str(target), "--title", "Smoke Paper"])
    example = Path(args.example).expanduser().resolve()
    if example.exists():
        run(["python3", str(ROOT / "scripts" / "analyze_repo.py"), str(example), "--workspace", str(target)])
        report = example / "调研报告.md"
        if report.exists():
            shutil.copy2(report, target / "examples-调研报告.md")
    (target / "调研报告.md").write_text("# 调研报告\n\n## 摘要\n\nSmoke test synthesis.\n", encoding="utf-8")

    run(["python3", str(ROOT / "scripts" / "check_quality.py"), str(target), "--write-report"])
    print(target)


if __name__ == "__main__":
    main()
