# Real Search Skill

`real-search-skill` 是一个面向 Codex 的深度研究工作流 skill。它用于把模糊的学习、调研、选型、找思路、读论文源码、项目构思请求，推进成一个可复盘的本地研究工作区。

它不是“快速搜索摘要”。它强调：

- 先规划，再广度搜索，再深度阅读。
- 读官方文档、论文、GitHub 源码和成熟项目。
- 把过程沉淀成本地 Markdown 文档。
- 明确区分证据、判断和不确定项。
- 最终收敛成学习路线或落地方案。

## 适合什么时候用

适合：

- “我想学习一个方向，但还说不清楚。”
- “帮我调研主流、前沿、成熟方案。”
- “不要只总结，真的看看论文和 GitHub 源码。”
- “我想做一个项目，先帮我找思路、看现有方案、形成 MVP 路线。”
- “这个领域有哪些框架/论文/产品值得看？”

不适合：

- 一句话事实查询。
- 只需要修一个 bug。
- 只需要改一个文件。
- 需要立即发布、推送、发消息到外部平台的任务。

## 仓库结构

```text
real-search-skill/
├── .claude-plugin/              # 插件/市场元数据
├── cli/                         # 轻量安装器
├── docs/                        # 使用和成熟化文档
├── examples/                    # 后续真实调研样例
├── src/real-search-skill/       # 真正可安装的 skill 本体
│   ├── SKILL.md
│   ├── scripts/                 # 确定性辅助脚本
│   ├── templates/               # 研究文档模板
│   ├── references/              # 长流程参考说明
│   └── evals/                   # 行为/触发评测草稿
├── skill.json
├── README.md
├── DESIGN.md
└── LICENSE
```

根目录的 `SKILL.md` 也保留了一份兼容副本，方便直接安装或阅读；权威 skill 本体在 `src/real-search-skill/`。

## 安装

从仓库安装到 Codex：

```bash
git clone git@github.com:Blzw23/real-search-skill.git
cd real-search-skill
python3 cli/install.py --target codex
```

覆盖安装：

```bash
python3 cli/install.py --target codex --force
```

## 使用

你可以直接说：

```text
开启 real-search-skill。我要研究一个我还不太懂的方向，希望你先规划，再搜索主流/前沿/成熟方案，读论文和源码，最后在本地生成一套中文文档。
```

默认创建：

```text
深度调研/{YYYYMMDD}-{主题}/
```

常见产物：

- `研究计划.md`
- `资料索引.md`
- `阶段日志.md`
- `项目调研记录/`
- `论文调研记录/`
- `源码阅读记录/`
- `调研报告.md`
- `落地方案.md`
- `MVP路线图.md`

## 脚本

初始化工作区：

```bash
python3 src/real-search-skill/scripts/init_workspace.py "Agent 框架调研" --mode 研究落地
```

添加资料来源：

```bash
python3 src/real-search-skill/scripts/add_source.py \
  --workspace "深度调研/20260525-Agent-框架调研" \
  --type 官方文档 \
  --name "LangGraph Docs" \
  --link "https://langchain-ai.github.io/langgraph/" \
  --evidence A-源码/官方
```

生成笔记模板：

```bash
python3 src/real-search-skill/scripts/create_note.py \
  --workspace "深度调研/20260525-Agent-框架调研" \
  --kind project \
  --title "LangGraph"
```

浅克隆仓库并记录 commit：

```bash
python3 src/real-search-skill/scripts/clone_repo.py \
  https://github.com/langchain-ai/langgraph.git \
  --workspace "深度调研/20260525-Agent-框架调研"
```

质量检查：

```bash
python3 src/real-search-skill/scripts/check_quality.py "深度调研/20260525-Agent-框架调研"
```

## 当前状态

当前版本是产品化早期版本：

- 已有可安装 skill 本体。
- 已有脚本、模板、参考文档和 eval 草稿。
- 已有插件元数据、安装器、设计说明和路线图。
- 后续需要补正式 with-skill/baseline 评测报告和更多真实 examples。

## License

MIT
