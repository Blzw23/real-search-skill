#!/usr/bin/env python3
"""Shared workspace layout helpers for real-search scripts."""

from __future__ import annotations

from pathlib import Path


PROCESS_FILES = [
    "研究计划.md",
    "资料索引.md",
    "阶段日志.md",
    "论文阅读队列.md",
    "多角色任务板.md",
    "内容复核清单.md",
    "质量检查报告.md",
]

PROCESS_DIRS = [
    "网页摘录",
    "自动发现",
    "项目调研记录",
    "论文调研记录",
    "源码阅读记录",
    "外部源码",
    "论文PDF",
    "论文正文",
]

FINAL_FILES = [
    "调研报告.md",
    "对比矩阵.md",
    "落地方案.md",
    "MVP路线图.md",
    "学习总结.md",
    "下一步学习计划.md",
]

MATERIALS_DIR = "工作材料"


def resolve_workspace(workspace: str | Path) -> Path:
    return Path(workspace).expanduser().resolve()


def materials_root(workspace: str | Path) -> Path:
    workspace_path = resolve_workspace(workspace)
    nested = workspace_path / MATERIALS_DIR
    return nested if nested.exists() else workspace_path


def ensure_materials_root(workspace: str | Path) -> Path:
    workspace_path = resolve_workspace(workspace)
    nested = workspace_path / MATERIALS_DIR
    nested.mkdir(parents=True, exist_ok=True)
    return nested


def process_path(workspace: str | Path, *parts: str) -> Path:
    return materials_root(workspace).joinpath(*parts)


def final_path(workspace: str | Path, name: str) -> Path:
    return resolve_workspace(workspace) / name
