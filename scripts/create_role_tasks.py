#!/usr/bin/env python3
"""Create a Codex-run multi-role task board for real-search."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


ROLES = [
    (
        "planner",
        "把模糊目标改写成研究问题、范围、交付物和阶段计划。",
        ["确认主题边界", "写/更新研究计划", "定义资料来源策略", "设定本阶段完成标准"],
    ),
    (
        "explorer",
        "广度发现框架、论文、产品、基准、awesome list 和官方文档。",
        ["运行或补充自动资料发现", "去重候选来源", "建立对比维度", "挑选深读对象"],
    ),
    (
        "paper-reader",
        "阅读论文正文，把方法、实验、局限映射到工程启发。",
        ["维护论文阅读队列", "处理 PDF/元数据", "写论文笔记", "标注未读正文或弱证据"],
    ),
    (
        "source-reader",
        "clone/分析项目源码，找技术栈、入口、核心模块和扩展点。",
        ["维护外部源码", "生成源码阅读路线", "深读核心文件", "记录 commit 和阅读路径"],
    ),
    (
        "reviewer",
        "检查是否走马观花、是否只看 README、结论是否有证据支撑。",
        ["运行质量检查", "找证据缺口", "标注待验证", "要求补读关键来源"],
    ),
    (
        "synthesizer",
        "把资料收敛成学习路线、调研报告、选型建议或 MVP 方案。",
        ["更新阶段日志", "写对比矩阵", "提炼判断", "给出下一步行动"],
    ),
]


def task_lines(tasks: list[str]) -> str:
    return "\n".join(f"- [ ] {task}" for task in tasks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a multi-role task board for Codex-driven research.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--topic", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    board = workspace / "多角色任务板.md"
    role_blocks = []
    for role, mission, tasks in ROLES:
        role_blocks.append(
            f"""## {role}

职责：{mission}

{task_lines(tasks)}

产出：

- 
"""
        )

    board.write_text(
        f"""# 多角色任务板

## 主题

{args.topic}

## 说明

这些不是独立后台 agent，而是 Codex 在长程调研中按角色切换执行的任务剧本。每完成一批任务，都要更新 `阶段日志.md`，并把证据写入对应笔记或资料索引。

创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

{chr(10).join(role_blocks)}

## 当前阻塞

- 

## 下一轮建议

- 
""",
        encoding="utf-8",
    )
    print(board)


if __name__ == "__main__":
    main()
