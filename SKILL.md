---
name: real-search-skill
description: Use this skill whenever the user wants deep, real research into an unclear topic, learning direction, technical field, framework ecosystem, paper trail, product space, or implementation idea. It turns vague curiosity into a long-running, evidence-backed local research workspace with plans, source indexes, paper/code notes, comparisons, reports, and optional landing-to-build proposals. Trigger on phrases like "调研", "深入研究", "学习这个领域", "找主流方案", "看看前沿", "帮我找思路", "我说不清楚但想搞懂", "从论文/源码/项目里总结", or when the user asks to clone/read GitHub projects and produce many documents over time.
compatibility: Codex-first. Requires local filesystem and shell access; benefits from web search, git, GitHub access, and long-running goal/plan support.
---

# Real Search Skill

这个 skill 的目标不是快速搜索摘要，而是把“我还说不清楚，但想真正搞懂、找主流、看前沿、读源码、最后能落地”的模糊需求，推进成一套可复盘的本地研究资料库。

默认语言使用中文，必要术语保留英文。默认深度优先，可以长时间执行、联网检索、阅读论文和官方文档、浅克隆 GitHub 仓库、逐步总结并写大量本地文档。

## 边界

默认只做研究和本地文档：

- 可以创建本地主题工作区、写 Markdown/HTML/索引/笔记。
- 可以使用 web、终端、git clone、包管理器的只读查询、源码阅读、测试性运行。
- 可以在用户明确授权的当前研究目录下载外部源码。
- 不默认推送 GitHub、不发布文章、不发消息到外部平台、不调用会产生外部写入的 API。
- 不改动用户无关项目代码；如果研究需要写 demo 或验证脚本，放在主题工作区内并说明用途。

## 启动判断

先理解用户真正想获得什么。如果用户已经明确要求“全自动、长时间、深度调研”，直接开始，不要用过多问题打断。

只在高影响信息缺失时问 1-3 个问题，例如：

- 产物偏 `学习笔记` 还是 `研究落地`？
- 是否允许联网搜索和 shallow clone GitHub 仓库？
- 是否有必须覆盖的框架、论文、公司、技术栈或时间范围？

如果用户没有回答，采用默认值：

- 模式：`研究落地`
- 强度：`深度优先`
- 输出：当前项目下 `深度调研/{YYYYMMDD}-{主题}/`
- 源码：只浅克隆必要仓库到主题工作区的 `外部源码/`

## 工作流

### 1. 建立长程任务

如果运行环境支持 goal/plan，就使用它们承载长程目标和阶段状态；如果不支持，用 `研究计划.md`、`阶段日志.md` 和 checklist 模拟。

创建主题工作区，并初始化：

- `研究计划.md`
- `资料索引.md`
- `阶段日志.md`
- `网页摘录/`
- `项目调研记录/`
- `论文调研记录/`
- `源码阅读记录/`
- `外部源码/`

详细结构见 [references/产物结构.md](references/产物结构.md)。

### 2. 先广度，再深度

第一轮先建立地图：

- 找主流项目、成熟框架、重要论文、官方文档、代表性博客/技术报告。
- 用资料索引记录来源、链接、访问日期、证据等级、阅读状态。
- 先做 10-20 个候选对象的粗对比，避免过早陷入单点。

第二轮再深读：

- 对重点项目 shallow clone 或 sparse checkout。
- 优先读 README、docs、examples、核心 runtime、扩展点、权限/安全、trace/log、memory/eval、测试。
- 每个重点项目写独立中文笔记，必须包含“定位、核心抽象、运行流程、扩展机制、可靠性、安全边界、可借鉴、避免照搬”。

详细流程见 [references/深度调研流程.md](references/深度调研流程.md)。

### 3. 论文和源码都要落到判断

论文笔记不要只摘摘要，要回答：

- 论文解决什么问题？
- 方法结构是什么？
- 和工程系统有什么关系？
- 哪些结论可迁移，哪些只适用于实验设置？
- 对用户当前目标有什么启发？

源码笔记不要只列文件，要说明：

- 核心路径为什么是核心路径。
- 抽象如何组织。
- 运行时如何流动。
- 扩展点和边界在哪里。
- 值得复用的设计和不应照搬的复杂度。

源码阅读清单见 [references/源码阅读清单.md](references/源码阅读清单.md)。

### 4. 阶段性总结

每完成一个阶段，更新 `阶段日志.md`：

- 已读内容
- 新发现
- 判断变化
- 不确定项
- 下一步

长任务中要频繁向用户给简短进展，不要等最后才出现。

### 5. 收敛产物

如果模式是 `学习笔记`，最终产出：

- `学习路线.md`
- `概念地图.md`
- `论文与源码笔记汇总.md`
- `阶段复盘.md`
- `下一步学习计划.md`

如果模式是 `研究落地`，最终产出：

- `调研报告.md`
- `对比矩阵.md`
- `机会与风险.md`
- `落地方案.md`
- `MVP路线图.md`

正式结论必须能追溯到资料索引、论文、官方文档或源码路径。无法确认的地方写明“待验证/不确定”。

## 质量门禁

完成前逐项检查：

- 是否有 `研究计划.md` 和 `资料索引.md`？
- 是否区分了官方文档、论文、源码、二手文章？
- 是否记录了 clone 的仓库 URL、commit、阅读路径？
- 是否有逐项笔记，而不只是最终摘要？
- 是否把资料堆砌收敛成判断？
- 是否写清楚“不确定/待验证”？
- 是否没有执行外部推送/发布？

详细检查表见 [references/质量门禁.md](references/质量门禁.md)。

## 常用命令模式

优先使用快速、可追溯的命令：

```bash
rg --files
rg "keyword"
git clone --depth=1 --filter=blob:none <repo-url> 外部源码/<name>
git -C 外部源码/<name> rev-parse --short HEAD
git -C 外部源码/<name> sparse-checkout set <paths>
```

大仓库先 shallow clone；必要时 sparse checkout；不要把外部源码默认视为最终要提交的内容。

## 输出风格

写给未来会继续学习和落地的自己：

- 中文清楚、结构稳定、判断明确。
- 术语保留英文，首次出现时解释。
- 每个文档都能独立阅读，也能通过 `资料索引.md` 串起来。
- 不用“看起来不错”代替证据。
- 不为了凑文档而写空话；每份文档都要减少下一次理解成本。
