# CLI

当前 CLI 是轻量安装器，用于把 `src/real-search-skill/` 同步到本机 Codex skills 目录。

```bash
python3 cli/install.py --target codex
```

覆盖安装：

```bash
python3 cli/install.py --target codex --force
```

后续可以扩展：

- `init-workspace`
- `add-source`
- `clone-repo`
- `check-quality`
