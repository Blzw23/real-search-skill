# real-search-skill

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

## 默认输出

每次深度调研默认创建：

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
- `网页摘录/`
- `外部源码/`
- `调研报告.md`
- `学习总结.md`
- `落地方案.md`
- `MVP路线图.md`

## 两种模式

`学习笔记` 模式：

- 学习路线
- 概念地图
- 论文和源码笔记
- 阶段复盘
- 下一步学习计划

`研究落地` 模式：

- 调研报告
- 对比矩阵
- 机会与风险
- 项目方案
- MVP 路线图

如果用户不指定，默认使用 `研究落地`。

## 安装

复制本仓库到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
git clone git@github.com:Blzw23/real-search-skill.git ~/.codex/skills/real-search-skill
```

如果已经安装过：

```bash
cd ~/.codex/skills/real-search-skill
git pull
```

## 文件结构

```text
real-search-skill/
├── SKILL.md
├── README.md
├── evals/
│   ├── evals.json
│   └── trigger-evals.json
└── references/
    ├── 产物结构.md
    ├── 深度调研流程.md
    ├── 源码阅读清单.md
    └── 质量门禁.md
```

## 当前状态

当前版本是经过结构化整理的早期版本。它包含可执行的 workflow、参考模板和 eval 草稿。正式的 with-skill/baseline 子代理评测可以后续继续补。
