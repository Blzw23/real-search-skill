# Real Search Skill

`real-search-skill` 是一个面向 Codex 的深度研究工作流 skill。它用于把模糊的学习、调研、选型、找思路、读论文源码、项目构思请求，推进成一个可复盘的本地研究工作区。

## 核心亮点

当你对一个方向还没搞清楚，但希望知道这个领域的常见框架、成熟实践、前沿论文和真实项目经验时，`real-search-skill` 会把问题拆成一个长期研究过程：先建立领域地图，再读官方文档、论文和真实项目源码，最后沉淀成可复盘的本地资料库。

它解决的是普通模型搜索最容易出现的“走马观花”问题：不只扫一遍 README、不只摘几段介绍，而是进一步看项目技术栈、核心模块、扩展机制、源码路径和论文脉络，让你在调研过程中真正学会这个领域。

## 当前实现状态

这个亮点已经在 skill 的工作流、模板和辅助脚本里落地：它会要求先规划、建立资料索引、区分证据等级、创建项目/论文/源码笔记，必要时浅克隆 GitHub 仓库并记录 commit、阅读路径和关键发现。

当前它不是一个无人值守的后台爬虫或论文机器人；“长期看很多论文、仔细读源码”的能力，主要通过 Codex 的长程执行、Goal/Plan 支持、阶段日志和质量门禁来保证。也就是说，它已经能把模型从“只看 README 的快速摘要”拉到“有证据、有路径、有复盘的深度研究流程”，但每次研究的深度仍取决于用户给的时间、网络/工具权限和当轮执行范围。

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
├── benchmarks/                  # 结构化评测记录
├── examples/                    # 真实调研样例
├── src/real-search-skill/       # 真正可安装的 skill 本体
│   ├── SKILL.md
│   ├── scripts/                 # 确定性辅助脚本
│   ├── templates/               # 研究文档模板
│   ├── references/              # 长流程参考说明
│   └── evals/                   # 行为/触发评测草稿
├── scripts/                     # 根目录兼容副本
├── templates/                   # 根目录兼容副本
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

追加阶段日志：

```bash
python3 src/real-search-skill/scripts/update_stage_log.py \
  --workspace "深度调研/20260525-Agent-框架调研" \
  --stage "框架深读" \
  --done "读完 OpenAI Agents SDK;读完 LangGraph" \
  --findings "Agent 是 runtime 不是 prompt wrapper"
```

自动资料发现：

```bash
python3 src/real-search-skill/scripts/discover_sources.py "Agent 框架调研" --workspace "深度调研/20260525-Agent-框架调研"
```

论文处理：

```bash
python3 src/real-search-skill/scripts/process_paper.py https://arxiv.org/abs/2210.03629 --workspace "深度调研/20260525-Agent-框架调研"
```

源码路线分析：

```bash
python3 src/real-search-skill/scripts/analyze_repo.py /path/to/repo --workspace "深度调研/20260525-Agent-框架调研"
```

多角色任务板：

```bash
python3 src/real-search-skill/scripts/create_role_tasks.py --workspace "深度调研/20260525-Agent-框架调研" --topic "Agent 框架调研"
```

烟测：

```bash
python3 src/real-search-skill/scripts/run_smoke.py --topic "Agent 框架调研" --workspace /tmp/real-search-skill-smoke
```

质量检查：

```bash
python3 src/real-search-skill/scripts/check_quality.py "深度调研/20260525-Agent-框架调研"
```

## 当前状态

当前版本已经是成熟可用的研究型 skill：

- 已有可安装 skill 本体和根目录兼容副本。
- 已有脚本、模板、参考文档和 eval 草稿。
- 已有自动发现、论文处理、源码阅读路线、多角色任务板和 smoke runner。
- 已有插件元数据、安装器、设计说明和路线图。
- 已有结构化 benchmark 记录和真实 example。
- 后续主要是继续打磨正式 with-skill/baseline 评测展示，而不是补基础能力。

## License

MIT
