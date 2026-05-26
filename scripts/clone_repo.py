#!/usr/bin/env python3
"""Shallow clone a repository into 外部源码 and record metadata."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from workspace_layout import process_path


def repo_name(url: str) -> str:
    name = url.rstrip("/").split("/")[-1]
    name = re.sub(r"\.git$", "", name)
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name) or "repo"


def run(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone a GitHub repo for real-search research.")
    parser.add_argument("url")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--name", default=None)
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    target_root = process_path(workspace, "外部源码")
    target_root.mkdir(parents=True, exist_ok=True)
    target = target_root / (args.name or repo_name(args.url))

    if not target.exists():
        subprocess.run(
            ["git", "clone", "--depth=1", "--filter=blob:none", args.url, str(target)],
            check=True,
        )

    commit = run(["git", "rev-parse", "--short", "HEAD"], cwd=target)
    meta = process_path(workspace, "源码阅读记录", f"{target.name}-metadata.md")
    meta.parent.mkdir(parents=True, exist_ok=True)
    meta.write_text(
        f"""# {target.name} 源码记录

| 字段 | 内容 |
| --- | --- |
| 仓库 | {args.url} |
| 本地路径 | {target} |
| Commit | {commit} |
| Clone 策略 | `git clone --depth=1 --filter=blob:none` |

## 已读路径

| 路径 | 作用 | 备注 |
| --- | --- | --- |

## 待验证

- 
""",
        encoding="utf-8",
    )
    print(target)


if __name__ == "__main__":
    main()
