#!/usr/bin/env python3
"""Move process files into 工作材料 while keeping final deliverables at workspace root."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from workspace_layout import MATERIALS_DIR, PROCESS_DIRS, PROCESS_FILES, ensure_materials_root, resolve_workspace


def move_if_present(src: Path, dst: Path) -> None:
    if not src.exists() or src == dst:
        return
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate an existing real-search workspace into the 工作材料 layout.")
    parser.add_argument("workspace")
    args = parser.parse_args()

    workspace = resolve_workspace(args.workspace)
    materials = ensure_materials_root(workspace)

    for name in PROCESS_FILES:
        move_if_present(workspace / name, materials / name)

    for name in PROCESS_DIRS:
        move_if_present(workspace / name, materials / name)

    readme = workspace / "README-如何查看这份调研.md"
    if not readme.exists():
        readme.write_text(
            f"""# 如何查看这份调研

## 最终交付

- 根目录下的 `调研报告.md`、`对比矩阵.md`、`落地方案.md`、`MVP路线图.md` 是给人直接看的结果。

## 工作材料

- 所有过程文件已经整理到 `{MATERIALS_DIR}/`。
- 包括研究计划、资料索引、阶段日志、自动发现、论文/项目/源码笔记、PDF、外部源码和复核清单。
""",
            encoding="utf-8",
        )

    print(workspace)


if __name__ == "__main__":
    main()
