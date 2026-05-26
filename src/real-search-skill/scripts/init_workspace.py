#!/usr/bin/env python3
"""Create a deep-research workspace with standard Chinese documents."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from workspace_layout import FINAL_FILES, PROCESS_DIRS, ensure_materials_root


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
    materials = ensure_materials_root(workspace)

    for directory in PROCESS_DIRS:
        (materials / directory).mkdir(exist_ok=True)

    write_if_missing(
        materials / "研究计划.md",
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

## 深读目标

- 至少确认 2-4 个高价值深读对象，不满足时写清原因。
- 论文线尽量区分“只读摘要/已看正文/需复读”。
- 源码线至少记录关键入口、核心模块、扩展点或明确写出暂未读到。

## 阶段安排

1. 广度扫描
2. 第一轮收敛
3. 第二轮深度阅读
4. 对比分析
5. 收敛报告

## 风险与不确定项

- 
""",
    )

    write_if_missing(
        materials / "资料索引.md",
        """# 资料索引

| 类型 | 名称 | 链接/路径 | 证据等级 | 阅读状态 | 关键价值 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
""",
    )

    write_if_missing(
        materials / "阶段日志.md",
        f"""# 阶段日志

## {datetime.now().strftime('%Y-%m-%d %H:%M')} 初始化

- 已完成：创建研究工作区。
- 新发现：
- 判断变化：
- 待验证：
- 下一步：
""",
    )

    write_if_missing(
        materials / "论文阅读队列.md",
        """# 论文阅读队列

| 状态 | 标题 | 链接 | PDF/本地路径 | 引用 | 备注 |
| --- | --- | --- | --- | --- | --- |
""",
    )

    write_if_missing(
        materials / "多角色任务板.md",
        """# 多角色任务板

## 说明

- planner：定义研究问题和范围。
- explorer：发现资料。
- paper-reader：处理论文。
- source-reader：分析源码。
- reviewer：检查证据和浅读风险。
- synthesizer：收敛判断。

## 当前阻塞

- 待补充
""",
    )

    if args.mode == "学习笔记":
        write_if_missing(workspace / "学习总结.md", "# 学习总结\n\n")
        write_if_missing(workspace / "下一步学习计划.md", "# 下一步学习计划\n\n")
    else:
        write_if_missing(
            workspace / "调研报告.md",
            """# 调研报告

## 主题

## 先说结论

## 证据基础

- 官方/源码：
- 论文/技术报告：
- 商用产品/社区：

## 商用品与成熟做法

## 开源/源码深读

## 论文脉络与关键分歧

## 反例与不成立路径

## 对当前项目的设计启发

## 风险、局限与待验证

## 下一步
""",
        )
        write_if_missing(workspace / "对比矩阵.md", "# 对比矩阵\n\n")
        write_if_missing(workspace / "落地方案.md", "# 落地方案\n\n")
        write_if_missing(workspace / "MVP路线图.md", "# MVP路线图\n\n")

    write_if_missing(
        workspace / "README-如何查看这份调研.md",
        f"""# 如何查看这份调研

## 最终交付

{chr(10).join(f"- `{name}`" for name in FINAL_FILES if (workspace / name).name)}

## 工作材料

- 所有给模型持续工作的材料统一放在 `工作材料/`。
- 包括研究计划、资料索引、阶段日志、自动发现、论文/项目/源码笔记、PDF、外部源码、复核清单。
- 如果最终报告里的结论需要追证据，请回到 `工作材料/` 里找对应来源。
""",
    )

    print(workspace)


if __name__ == "__main__":
    main()
