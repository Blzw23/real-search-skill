---
name: real-search-skill
description: Use this skill for long-running, evidence-backed deep research when the user wants to learn an unclear domain, find mainstream/frontier/mature approaches, compare frameworks or papers, read GitHub source, discover product/project ideas, or turn vague curiosity into local documents and an actionable plan. Trigger strongly on Chinese or English requests like 调研, 深入研究, 学习一个方向, 找主流方案, 看前沿, 找思路, 读论文源码, clone GitHub 看看, 不要只总结, 帮我从不清楚到能落地, or any request that needs sustained research rather than a quick answer.
compatibility: Codex-first. Requires local filesystem and shell access. Benefits from web search, git, GitHub access, and long-running goal/plan support. Do not perform external publishing or git push as part of this skill.
---

# Real Search Skill

Use this skill to turn vague learning, research, or project-discovery requests into a durable local research workspace. The user often does not know the right terms yet; your job is to build the map, read real sources, keep evidence, and converge toward understanding or execution.

This is not a quick web-summary skill. Prefer sustained, source-grounded work: official docs, papers, repositories, source code, examples, benchmarks, community signals, and your own synthesis.

## Operating Contract

Default behavior:

- Work in Chinese by default; preserve English technical terms when useful.
- Prefer depth over speed when the user asks for deep research or seems uncertain.
- Create local Markdown documents as the durable output, not just a chat answer.
- Search broadly first, then select high-value sources for deeper reading.
- Clone/read GitHub repositories when source-level evidence matters and the user has not forbidden it.
- Record evidence, uncertainty, and reading status continuously.
- End with judgment: what matters, what is mature, what is frontier, what to learn or build next.

Safety boundary:

- Do not push to GitHub, publish content, send messages, or write to external services as part of this skill.
- Do not modify unrelated user project code. If a demo or script is useful, create it inside the research workspace and explain why.
- Do not hide uncertainty. Mark claims as `待验证/不确定` when evidence is weak.

## Intent Capture

First infer the user's intent from context. If the user clearly asks for autonomous deep research, start directly and do not over-question.

Ask at most 1-3 questions only when the answer materially changes the research:

- Mode: `学习笔记` or `研究落地`
- Allowed sources: web search, GitHub clone, papers, paid/internal sources
- Must-cover items: frameworks, papers, companies, repos, time range, language stack

If unanswered, use these defaults:

- Mode: `研究落地`
- Depth: `深度优先`
- Output root: current working directory
- Workspace: `深度调研/{YYYYMMDD}-{主题}/`
- Source code: shallow clone only when useful, under workspace `外部源码/`
- External effects: local research only

## Workspace Setup

Create or reuse a topic workspace:

```text
深度调研/{YYYYMMDD}-{主题}/
```

Prefer the bundled initializer when this skill is installed with scripts:

```bash
python3 <skill_dir>/scripts/init_workspace.py "<topic>" --mode 研究落地 --root .
```

If scripts are unavailable, initialize these paths manually:

- `研究计划.md`
- `资料索引.md`
- `阶段日志.md`
- `论文阅读队列.md`
- `多角色任务板.md`
- `自动发现/`
- `网页摘录/`
- `项目调研记录/`
- `论文调研记录/`
- `源码阅读记录/`
- `外部源码/`

Read [references/产物结构.md](references/产物结构.md) when creating the workspace or deciding final deliverables.
For workflow details, also read:

- [references/深度调研流程.md](references/深度调研流程.md)
- [references/源码阅读清单.md](references/源码阅读清单.md)
- [references/质量门禁.md](references/质量门禁.md)

## Execution Loop

Follow this loop until the research is genuinely useful:

1. **Plan**
   - Convert the vague request into research questions.
   - Define scope, deliverables, source strategy, and checkpoints in `研究计划.md`.
   - If goal/plan tools exist and the user asked for long-running work, use them; otherwise maintain `阶段日志.md`.

2. **Search Broadly**
   - Find official docs, repos, papers, surveys, benchmarks, examples, and mature products.
   - Build a candidate list before deep-reading one item.
   - Record each source in `资料索引.md` with evidence level and reading status.
   - Use the bundled discovery helper and source logger when useful.
   - Treat auto-discovered search entries as best-effort leads, not formal evidence. Generated search pages, product pages, and community results stay `D-待验证` or `C-社区/博客` until verified against official docs, paper text, or source code.
   - For community/forum signals, prefer no-login-accessible sources such as Hacker News, GitHub Issues/Discussions, Lobsters, Dev.to, old Reddit, V2EX search, and 掘金. Skip sources that only expose snippets or block useful reading behind login.

3. **Select Deep Sources**
   - Prioritize user-mentioned items, official sources, active high-impact repos, foundational papers, recent surveys, benchmark/eval work, and lightweight alternatives.
   - For each selected project or paper, create a dedicated Chinese note.

4. **Read Real Materials**
   - For projects: read README, docs, examples, architecture/concepts, core runtime, extension points, permission/sandbox, memory/state, trace/log/eval, and tests.
   - For papers: capture problem, method, experiments, limits, engineering implications, and relation to the user's goal.
   - When PDF extraction is missing, low quality, or likely scanned, mark it as `待 OCR/待人工阅读` and do not imply the paper has been fully read.
   - Use the bundled paper, repo, and note helpers when helpful.

5. **Synthesize Frequently**
   - After each meaningful batch, update `阶段日志.md`.
   - For long runs, create or refresh `多角色任务板.md` so Codex can switch between planner/explorer/paper-reader/source-reader/reviewer/synthesizer.
   - Use the bundled stage-log helper when it saves time.
   - Tell the user what was learned, what changed, and what is next.
   - Convert raw notes into comparison tables and judgments; do not leave a pile of links.

6. **Converge**
   - For `学习笔记`, produce a learning path, concept map, paper/source notes, and next study plan.
   - For `研究落地`, produce a research report, comparison matrix, opportunity/risk analysis, landing proposal, and MVP roadmap.

## Evidence Rules

Use evidence levels consistently:

- `A-源码/官方`: official docs, source code, standards, release notes.
- `B-论文/技术报告`: papers, surveys, technical reports, benchmarks.
- `C-社区/博客`: tutorials, discussions, personal blogs, videos.
- `D-待验证`: search snippets, unverifiable claims, second-hand statements.

Formal conclusions must cite or point to their supporting source in `资料索引.md`, a local note, or a source path. If evidence is missing, write `待验证/不确定`.

## Output Requirements

Every serious run should leave behind:

- A plan
- A source index
- Stage logs
- Per-source notes
- A synthesis document
- A clear next step

Do not finish with only chat prose unless the user explicitly asks for a lightweight answer.

For detailed templates, read only the relevant reference:

- [references/产物结构.md](references/产物结构.md)
- [references/深度调研流程.md](references/深度调研流程.md)
- [references/源码阅读清单.md](references/源码阅读清单.md)
- [references/质量门禁.md](references/质量门禁.md)

## Completion Gate

Before claiming completion, verify:

- Required files exist in the workspace.
- `资料索引.md` distinguishes official docs, papers, source code, and secondary material.
- Cloned repositories record URL, commit hash, and key files read.
- Notes include judgments, not only excerpts.
- `论文阅读队列.md` and `多角色任务板.md` exist when the run needs long-form research.
- `check_quality.py` passes hard structure checks and surfaces warnings for shallow evidence/content risks.
- When the topic is important or the report will guide decisions, run `check_quality.py --write-review` and have the reviewer role work through `内容复核清单.md`. Use `--strict-content` only when content warnings should block completion.
- Final synthesis answers the user's original uncertainty.
- External publishing/push actions were not performed by default.
- If the work is too large for one turn, leave a clear continuation state in `阶段日志.md` and tell the user exactly what remains.
