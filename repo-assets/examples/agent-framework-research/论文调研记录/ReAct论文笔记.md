# ReAct 论文笔记

论文：ReAct: Synergizing Reasoning and Acting in Language Models  
链接：https://arxiv.org/abs/2210.03629

## 解决的问题

传统 prompting 往往把 reasoning 和 acting 分开。ReAct 把 reasoning trace 和 task-specific actions 交错生成，让模型一边思考、一边调用外部环境，再根据 observation 更新计划。

## 方法结构

典型格式：

```text
Thought: ...
Action: ...
Observation: ...
Thought: ...
Action: ...
Observation: ...
Final Answer: ...
```

这不只是 prompt 格式，而是现代 agent loop 的最小范式。

## 工程启发

- `Thought` 不一定暴露给最终用户，但 trace 中应该保留决策事件。
- `Action` 应进入标准 tool call 结构，而不是自然语言自由文本。
- `Observation` 应经过裁剪、结构化和错误分类后回到模型。
- 每轮都应写 trace：输入、模型输出、tool call、tool result、状态变化。

## 局限

- ReAct 缺少系统级权限、重试、持久状态。
- 对复杂长任务，需要和 checkpoint、memory、reflection、subagent 结合。

## 和当前目标的关系

轻量 Agent 基座的 MVP loop 可以从 ReAct 抽象出 plan/action/observation/final，但要增加 trace、permission、retry 和 memory。
