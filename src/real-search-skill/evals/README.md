# Evals

本目录包含两类评测材料。

## evals.json

`evals.json` 是行为评测草稿，关注开启 skill 后是否会按深度研究工作流行动：

- 是否创建主题工作区。
- 是否生成研究计划、资料索引、阶段日志。
- 是否覆盖论文、源码、项目或官方资料。
- 是否把资料收敛成判断，而不是只堆链接。
- 是否标注证据等级和不确定项。

## trigger-evals.json

`trigger-evals.json` 是触发评测草稿，包含 should-trigger 和 should-not-trigger 查询。

应该触发：

- 深度调研
- 学习新领域
- 比较主流框架/论文/项目
- 要求 clone GitHub 读源码
- 从模糊想法走向落地方案

不应该触发：

- 单步事实查询
- 普通代码修复
- 单文件格式转换
- Git 推送/发布任务
- 与深度研究无关的轻量任务

## 后续正式评测

正式评测应按 `skill-creator` 流程进行：

1. 对每个 eval 同时跑 with-skill 和 baseline。
2. 保存输出、transcript、timing。
3. 生成 grading.json。
4. 汇总 benchmark.json。
5. 用 `eval-viewer/generate_review.py` 给用户 review。
6. 根据反馈迭代 `SKILL.md` 和 references。
