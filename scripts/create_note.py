#!/usr/bin/env python3
"""Create a project/paper/source note from built-in templates."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from workspace_layout import process_path


TEMPLATES = {
    "project": """# {title}调研

## 定位

## 核心抽象

## 运行流程

## 关键运行时循环

## 工具/扩展

## 记忆/状态

## 可靠性与观测

## 权限与安全边界

## 源码阅读路径

| 路径 | 作用 | 读到的设计 | 证据强度 |
| --- | --- | --- | --- |

## 关键证据摘录

## 值得借鉴

## 避免照搬

## 不确定/待验证
""",
    "paper": """# {title}论文笔记

## 解决的问题

## 方法结构

## 实验设置

## 实验与结论

## 正文抽取质量

待补充

## 关键证据/原文位置

## 工程启发

## 局限

## 和当前目标的关系

## 不确定/待验证
""",
    "source": """# {title}资料笔记

## 来源

## 核心内容

## 关键说法

## 可用信息

## 不能单独支持什么结论

## 需要警惕

## 和当前目标的关系

## 不确定/待验证
""",
}


def safe_name(title: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "-", title.strip())
    return name.strip("-") or "未命名"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a note file for real-search research.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--kind", choices=sorted(TEMPLATES), required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()

    folders = {
        "project": "项目调研记录",
        "paper": "论文调研记录",
        "source": "网页摘录",
    }
    target_dir = process_path(args.workspace, folders[args.kind])
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{safe_name(args.title)}.md"
    if not path.exists():
        path.write_text(TEMPLATES[args.kind].format(title=args.title), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
