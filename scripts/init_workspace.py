#!/usr/bin/env python3
"""Create a deep-research workspace with standard Chinese documents."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def slugify_topic(topic: str) -> str:
    topic = topic.strip()
    topic = re.sub(r"[\\/:*?\"<>|]+", "-", topic)
    topic = re.sub(r"\s+", "-", topic)
    return topic.strip("-") or "未命名主题"


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a real-search research workspace.")
    parser.add_argument("topic", help="Research topic, Chinese or English.")
    parser.add_argument("--mode", choices=["学习笔记", "研究落地"], default="研究落地")
    parser.add_argument("--root", default=".", help="Output root directory. Default: current directory.")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"), help="Date prefix, YYYYMMDD.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    workspace = root / "深度调研" / f"{args.date}-{slugify_topic(args.topic)}"
    workspace.mkdir(parents=True, exist_ok=True)

    for directory in ["网页摘录", "项目调研记录", "论文调研记录", "源码阅读记录", "外部源码"]:
        (workspace / directory).mkdir(exist_ok=True)

    write_if_missing(
        workspace / "研究计划.md",
        f"""# 研究计划

## 主题

{args.topic}

## 模式

{args.mode}

## 目标

- 

## 用户背景与约束

- 

## 关键问题

1. 
2. 
3. 

## 调研范围

- 官方文档：
- 论文/技术报告：
- 开源项目：
- 产品/社区资料：

## 阶段安排

1. 广度扫描
2. 深度阅读
3. 对比分析
4. 收敛报告

## 风险与不确定项

- 
""",
    )

    write_if_missing(
        workspace / "资料索引.md",
        """# 资料索引

| 类型 | 名称 | 链接/路径 | 证据等级 | 阅读状态 | 关键价值 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
""",
    )

    write_if_missing(
        workspace / "阶段日志.md",
        f"""# 阶段日志

## {datetime.now().strftime('%Y-%m-%d %H:%M')} 初始化

- 已完成：创建研究工作区。
- 新发现：
- 判断变化：
- 待验证：
- 下一步：
""",
    )

    if args.mode == "学习笔记":
        write_if_missing(workspace / "学习总结.md", "# 学习总结\n\n")
        write_if_missing(workspace / "下一步学习计划.md", "# 下一步学习计划\n\n")
    else:
        write_if_missing(workspace / "调研报告.md", "# 调研报告\n\n")
        write_if_missing(workspace / "对比矩阵.md", "# 对比矩阵\n\n")
        write_if_missing(workspace / "落地方案.md", "# 落地方案\n\n")
        write_if_missing(workspace / "MVP路线图.md", "# MVP路线图\n\n")

    print(workspace)


if __name__ == "__main__":
    main()
