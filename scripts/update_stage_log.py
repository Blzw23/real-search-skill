#!/usr/bin/env python3
"""Append a structured entry to 阶段日志.md."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from workspace_layout import process_path


def bullet_lines(text: str) -> str:
    items = [item.strip() for item in text.split(";") if item.strip()]
    if not items:
        return "- "
    return "\n".join(f"- {item}" for item in items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a structured stage-log entry.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--done", default="")
    parser.add_argument("--findings", default="")
    parser.add_argument("--changes", default="")
    parser.add_argument("--uncertain", default="")
    parser.add_argument("--next", default="")
    args = parser.parse_args()

    log_path = process_path(args.workspace, "阶段日志.md")
    if not log_path.exists():
        raise SystemExit(f"阶段日志.md not found: {log_path}")

    entry = f"""

## {datetime.now().strftime('%Y-%m-%d %H:%M')} {args.stage}

### 已完成

{bullet_lines(args.done)}

### 新发现

{bullet_lines(args.findings)}

### 判断变化

{bullet_lines(args.changes)}

### 待验证

{bullet_lines(args.uncertain)}

### 下一步

{bullet_lines(getattr(args, 'next'))}
"""
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)
    print(log_path)


if __name__ == "__main__":
    main()
