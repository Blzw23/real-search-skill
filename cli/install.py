#!/usr/bin/env python3
"""Install real-search-skill into a local AI assistant skill directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "real-search-skill"


def install_codex(force: bool = False) -> Path:
    target = Path.home() / ".codex" / "skills" / "real-search-skill"
    if target.exists() and force:
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, target, dirs_exist_ok=True)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Real Search Skill.")
    parser.add_argument("--target", choices=["codex"], default="codex")
    parser.add_argument("--force", action="store_true", help="Replace existing installed files.")
    args = parser.parse_args()

    if args.target == "codex":
        target = install_codex(args.force)
        print(target)


if __name__ == "__main__":
    main()
