#!/usr/bin/env python3
"""Generate a heuristic source-reading route for a local repository."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

from workspace_layout import process_path


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__", ".next", ".cache"}
LANG_EXTS = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript/React",
    ".js": "JavaScript",
    ".jsx": "JavaScript/React",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".md": "Markdown",
}
MANIFESTS = {
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Makefile",
}
IMPORTANT_NAMES = {"README.md", "CONTRIBUTING.md", "ARCHITECTURE.md", "CHANGELOG.md", "LICENSE"}
KEYWORDS = {
    "入口/CLI": ["cli", "main", "__main__", "cmd", "bin"],
    "核心运行时": ["runtime", "runner", "agent", "engine", "orchestrator", "workflow", "graph"],
    "工具/插件/扩展": ["tool", "tools", "plugin", "plugins", "extension", "extensions", "skill", "mcp"],
    "状态/记忆": ["state", "memory", "store", "checkpoint", "session"],
    "观测/评测": ["trace", "tracing", "log", "logging", "eval", "benchmark", "telemetry"],
    "权限/沙箱": ["permission", "policy", "sandbox", "security", "auth"],
    "示例": ["example", "examples", "demo", "demos", "sample", "samples"],
    "测试": ["test", "tests", "spec", "specs"],
    "文档": ["doc", "docs", "guide", "guides"],
}


def iter_files(root: Path, limit: int = 5000) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.append(path)
        if len(files) >= limit:
            break
    return files


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def git_commit(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except Exception:
        return "非 git 仓库或无法读取"


def classify(files: list[Path], root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {key: [] for key in KEYWORDS}
    for path in files:
        parts = [part.lower() for part in path.relative_to(root).parts]
        stem = path.stem.lower()
        full = "/".join(parts)
        for label, words in KEYWORDS.items():
            if any(word in parts or word in stem or f"/{word}" in full for word in words):
                result[label].append(rel(path, root))
    return {key: value[:20] for key, value in result.items() if value}


def read_package_summary(path: Path) -> str:
    try:
        if path.name == "package.json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            deps = sorted((payload.get("dependencies") or {}).keys())[:12]
            dev_deps = sorted((payload.get("devDependencies") or {}).keys())[:8]
            return f"name={payload.get('name', '未知')}；scripts={list((payload.get('scripts') or {}).keys())[:8]}；deps={deps + dev_deps}"
        if path.name == "pyproject.toml":
            lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
            useful = [line for line in lines if line.startswith(("name =", "dependencies =", "[project]", "[tool.", "[build-system]"))]
            return "；".join(useful[:12])
    except Exception as exc:
        return f"读取失败：{exc}"
    return ""


def route_rows(title: str, paths: list[str], reason: str) -> list[str]:
    return [f"| {title} | `{path}` | {reason} | 候选路径/待验证 |" for path in paths[:10]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a cloned repository and propose a reading route.")
    parser.add_argument("repo_path")
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()

    repo = Path(args.repo_path).expanduser().resolve()
    if not repo.exists():
        raise SystemExit(f"仓库路径不存在：{repo}")
    files = iter_files(repo)
    language_counts = Counter(LANG_EXTS.get(path.suffix.lower(), "Other") for path in files)
    manifests = [path for path in files if path.name in MANIFESTS]
    important = [path for path in files if path.name in IMPORTANT_NAMES]
    buckets = classify(files, repo)

    rows: list[str] = []
    rows.extend(route_rows("先读项目入口", [rel(path, repo) for path in important[:8]], "理解定位、使用方式、贡献规范和版本变化。"))
    rows.extend(route_rows("再读技术栈/依赖", [rel(path, repo) for path in manifests[:12]], "判断语言、包管理、运行命令和主要依赖。"))
    for label in ["入口/CLI", "核心运行时", "工具/插件/扩展", "状态/记忆", "观测/评测", "权限/沙箱", "示例", "测试", "文档"]:
        rows.extend(route_rows(label, buckets.get(label, []), f"按 `{label}` 关键词静态匹配，需要 Codex 深读确认。"))

    manifest_notes = []
    for manifest in manifests[:8]:
        summary = read_package_summary(manifest)
        manifest_notes.append(f"- `{rel(manifest, repo)}`：{summary or '已发现，待阅读。'}")

    out_dir = process_path(args.workspace, "源码阅读记录")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{repo.name}-阅读路线.md"
    out.write_text(
        f"""# {repo.name} 源码阅读路线

## 仓库信息

| 字段 | 内容 |
| --- | --- |
| 本地路径 | {repo} |
| Commit | {git_commit(repo)} |
| 文件采样数 | {len(files)} |

## 技术栈候选

| 类型 | 文件数 |
| --- | --- |
{chr(10).join(f'| {name} | {count} |' for name, count in language_counts.most_common(12))}

## 依赖/包管理线索

{chr(10).join(manifest_notes) if manifest_notes else '- 未发现常见包管理文件。'}

## 建议阅读顺序

| 阶段 | 路径 | 为什么读 | 证据状态 |
| --- | --- | --- | --- |
{chr(10).join(rows) if rows else '| 待补充 | 待补充 | 未发现候选路径 | 待验证 |'}

## 待人工/Codex 深读确认

- 这份路线由静态文件名和目录名启发式生成，不等于已经理解调用链。
- 需要继续阅读核心文件内容，确认真实入口、核心抽象、扩展机制和测试覆盖。
- 如果只读 README，不足以作为正式源码证据。
""",
        encoding="utf-8",
    )
    print(out)


if __name__ == "__main__":
    main()
