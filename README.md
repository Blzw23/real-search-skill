# Real Search Skill

`real-search-skill` 是一个面向 Codex 的深度研究工作流 skill。它用于把模糊的学习、调研、选型、找思路、读论文源码、项目构思请求，推进成一个可复盘的本地研究工作区。

## 核心亮点

当你对一个方向还没搞清楚，但希望知道这个领域的常见框架、成熟实践、前沿论文和真实项目经验时，`real-search-skill` 会把问题拆成一个长期研究过程：先建立领域地图，再读官方文档、论文和真实项目源码，最后沉淀成可复盘的本地资料库。

它解决的是普通模型搜索最容易出现的“走马观花”问题：不只扫一遍 README、不只摘几段介绍，而是进一步看项目技术栈、核心模块、扩展机制、源码路径和论文脉络，让你在调研过程中真正学会这个领域。

## 它适合解决什么问题

适合这些场景：

- 你想学习一个新方向，但还不知道该从哪些关键词、论文、框架开始。
- 你想知道某个领域的主流方案、成熟项目、前沿方法和代表论文。
- 你不想只要几段搜索摘要，而是希望真的读官方文档、论文和 GitHub 源码。
- 你正在构思一个项目，希望先看现有方案，再形成差异化判断和 MVP 路线。
- 你需要把一次长时间研究沉淀成本地 Markdown 文档，后续可以继续接着读、接着做。

不适合这些场景：

- 一句话事实查询。
- 普通代码修复或单文件编辑。
- 只需要快速列几个链接。
- 需要后台定时运行、自动发布或外部写入的任务。

## 一次典型工作流

`real-search-skill` 会把一次模糊研究拆成可持续推进的过程：

1. 先理解你的目标，必要时只问少量关键问题。
2. 创建主题研究工作区，写下研究计划、资料索引和阶段日志。
3. 广度搜索官方文档、论文、仓库、产品、benchmark 和社区资料。
4. 选择高价值来源深读，必要时 shallow clone GitHub 仓库。
5. 对论文、项目和源码分别写中文笔记，记录证据等级和不确定项。
6. 阶段性综合，形成对比矩阵、调研报告、学习路线或落地方案。

它是依附 Codex 的深度研究工作流，不是无人值守后台爬虫。长程能力来自 Codex 的持续执行、Goal/Plan、阶段日志和质量门禁。

## 输出产物

默认工作区类似：

```text
深度调研/{YYYYMMDD}-{主题}/
├── 研究计划.md
├── 资料索引.md
├── 阶段日志.md
├── 论文阅读队列.md
├── 多角色任务板.md
├── 自动发现/
├── 网页摘录/
├── 项目调研记录/
├── 论文调研记录/
├── 源码阅读记录/
├── 外部源码/
├── 调研报告.md
└── 落地方案.md
```

不同任务会有不同产物。学习型任务更偏学习路线、概念地图、论文笔记；落地型任务更偏对比矩阵、机会分析、项目方案和 MVP 路线图。

## 使用方式

在 Codex 中，长程研究建议用 Goal 启动：

```text
/goal 使用 real-search-skill 深度调研 Agent 框架基座，先规划，再搜索主流、前沿、成熟方案，读论文和 GitHub 源码，最后沉淀中文调研报告和落地方案。
```

也可以直接触发：

```text
开启 real-search-skill。我要研究一个我还不太懂的方向，希望你先规划，再搜索主流/前沿/成熟方案，读论文和源码，最后在本地生成一套中文文档。
```

当运行环境支持 Goal/Plan 时，skill 会优先用它们管理长程任务；如果没有这些能力，就用 `研究计划.md`、`阶段日志.md` 和本地 checklist 记录进度，方便下一轮继续。

## CLI 辅助能力

这些脚本是给 Codex 或高级用户调用的确定性辅助工具，用来减少重复劳动。日常使用时，你通常只需要在对话里开启 skill，不需要手动逐个运行脚本。

| 能力 | 作用 |
| --- | --- |
| 初始化研究工作区 | 创建计划、索引、日志、笔记目录和默认产物结构 |
| 自动发现资料 | 根据主题生成候选来源，整理到 `自动发现/` 和 `资料索引.md` |
| 处理论文 | 记录论文元数据、阅读队列、PDF/正文抽取状态和笔记草稿 |
| clone 仓库 | shallow clone GitHub 项目并记录 URL、commit 和来源信息 |
| 分析源码阅读路线 | 根据目录、语言、入口、测试和扩展点生成建议阅读路径 |
| 生成多角色任务板 | 把长程研究拆成 planner、explorer、paper-reader、source-reader、reviewer、synthesizer 等角色任务 |
| 质量检查 | 检查资料索引、证据等级、源码阅读、论文队列和浅度风险 |
| smoke 验证 | 生成最小样例工作区，验证 skill 的主要脚本链路 |

常用命令示例：

```bash
python3 src/real-search-skill/scripts/init_workspace.py "Agent 框架调研" --mode 研究落地
python3 src/real-search-skill/scripts/check_quality.py "深度调研/20260525-Agent-框架调研"
```

更多脚本可以在 `src/real-search-skill/scripts/` 中查看。

## 安装

从 GitHub 安装到 Codex：

```bash
git clone git@github.com:Blzw23/real-search-skill.git
cd real-search-skill
python3 cli/install.py --target codex
```

覆盖安装：

```bash
python3 cli/install.py --target codex --force
```

安装后，本体会进入你的 Codex skills 目录。后续在对话中说“开启 real-search-skill”或描述深度调研需求即可触发。

## 仓库结构

```text
real-search-skill/
├── .claude-plugin/              # 插件/市场元数据
├── cli/                         # 轻量安装器
├── src/real-search-skill/       # 权威 skill 本体
│   ├── SKILL.md
│   ├── scripts/                 # 确定性辅助脚本
│   ├── templates/               # 研究文档模板
│   ├── references/              # 长流程参考说明
│   └── evals/                   # 行为/触发评测材料
├── repo-assets/
│   ├── docs/                    # 使用和成熟化文档
│   ├── benchmarks/              # 结构化评测记录
│   └── examples/                # 真实调研样例
├── scripts/                     # 根目录兼容副本
├── templates/                   # 根目录兼容副本
├── SKILL.md                     # 根目录兼容副本
├── skill.json
└── README.md
```

`src/real-search-skill/` 是权威 skill 本体；根目录的 `SKILL.md`、`scripts/`、`templates/` 保留为兼容入口，方便直接阅读或安装。不会被安装器使用、但对仓库展示有帮助的文档、评测和样例，统一放在 `repo-assets/` 下。

## License

MIT
