# Benchmarks

这里记录 `real-search-skill` 的评测材料。

## 当前评测状态

`iteration-1/` 是第一轮结构化评测，用于把评测标准、断言和改进方向固化下来。

重要说明：

- 本轮没有冒充已经完成独立子代理的 with-skill/baseline 执行。
- 本轮使用“脚本能力 + skill 指令覆盖 + 真实案例回放”的方式做可复现评测。
- 后续正式成熟评测应启动独立执行器，分别运行 with-skill 和 baseline，保存 transcript、outputs、timing，再生成 benchmark。
- `repo-assets/examples/agent-framework-research/` 已经作为真实案例样例存在，可用于理解一次完整研究最终会留下什么。
- `src/real-search-skill/scripts/run_smoke.py` 可生成最小本地烟测工作区，验证工作流骨架。

## 正式评测目标

正式评测应证明：

- skill 会创建本地研究工作区，而不是只给聊天回答。
- skill 会维护资料索引、阶段日志、项目/论文/源码笔记。
- skill 会记录证据等级和不确定项。
- skill 会使用脚本减少重复工作。
- skill 会从资料收敛到判断和下一步方案。
