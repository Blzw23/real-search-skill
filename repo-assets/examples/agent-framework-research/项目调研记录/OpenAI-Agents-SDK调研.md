# OpenAI Agents SDK 调研

## 定位

Python agent framework，定位为 lightweight yet powerful，可构建 multi-agent workflows。它是 Python 优先项目的重要接口参照。

## 核心抽象

- `Agent`：name、instructions、model、tools、handoffs、guardrails、output_type、hooks、mcp_servers。
- `Runner`：执行 run，管理 turn、tools、handoffs、sessions、streaming。
- `Tool`：function tool、hosted tool、computer、shell、apply_patch、MCP、agents as tools。
- `Handoff`：把控制权交给另一个 agent。
- `Session`：跨 run conversation history。
- `Trace`/`Span`：记录 agent、generation、tool、handoff、guardrail。

## 运行流程

`Runner` 管理 loop：

1. 准备 model input 和工具 schema。
2. 调用模型。
3. 解析 response item。
4. 执行 function/MCP/shell/computer/apply_patch 等工具。
5. 处理 approval、interruption、guardrail。
6. 决定 final output、handoff 或继续下一 turn。

## 源码阅读路径

| 路径 | 作用 | 读到的设计 | 证据强度 |
| --- | --- | --- | --- |
| `src/agents/run_internal/run_loop.py` | 主循环 | turn preparation、tool execution、resolution 分层 | A-源码/官方 |
| `src/agents/run_internal/tool_execution.py` | 工具执行 | function/MCP/tool result 处理 | A-源码/官方 |
| `docs/tracing.md` | tracing 文档 | agent/generation/tool/handoff span | A-源码/官方 |

## 值得借鉴

- `Agent + Runner + Tool + Handoff + Guardrail + Session + Trace` 是清晰的最小公共接口。
- tracing 应是 core feature，不是临时 debug。
- agents-as-tools 与 handoff 都值得支持，但 MVP 可先做 manager-as-tool。

## 避免照搬

- 不必绑定 OpenAI hosted tools。
- 不必第一版支持 voice/realtime/computer hosted container。
- 不必追求 provider 兼容大而全。

## 不确定/待验证

- 长期 memory 更偏 session history，不等同于项目级知识库，需要自研补足。
