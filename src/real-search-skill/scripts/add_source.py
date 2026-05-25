#!/usr/bin/env python3
"""Append one source row to 资料索引.md."""

from __future__ import annotations

import argparse
from pathlib import Path


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a source to a real-search 资料索引.md file.")
    parser.add_argument("--workspace", required=True, help="Research workspace path.")
    parser.add_argument("--type", required=True, help="Source type, e.g. 官方文档/源码/论文/博客.")
    parser.add_argument("--name", required=True, help="Source name.")
    parser.add_argument("--link", required=True, help="URL or local path.")
    parser.add_argument("--evidence", default="D-待验证", help="Evidence level.")
    parser.add_argument("--status", default="待读", help="Reading status.")
    parser.add_argument("--value", default="", help="Key value.")
    parser.add_argument("--note", default="", help="Extra note.")
    args = parser.parse_args()

    index_path = Path(args.workspace).expanduser().resolve() / "资料索引.md"
    if not index_path.exists():
        raise SystemExit(f"资料索引.md not found: {index_path}")

    row = "| {type} | {name} | {link} | {evidence} | {status} | {value} | {note} |\n".format(
        type=escape_cell(args.type),
        name=escape_cell(args.name),
        link=escape_cell(args.link),
        evidence=escape_cell(args.evidence),
        status=escape_cell(args.status),
        value=escape_cell(args.value),
        note=escape_cell(args.note),
    )
    with index_path.open("a", encoding="utf-8") as f:
        f.write(row)
    print(index_path)


if __name__ == "__main__":
    main()
