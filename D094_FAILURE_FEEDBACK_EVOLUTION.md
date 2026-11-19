# D-094 失败反馈驱动演化（B3）算法规格与合成证据

状态：`IMPLEMENTED / UNIT_TESTED / SYNTHETIC_VALIDATED`；未独立复核、未获真实实验批准、未运行 R3、没有性能提升信号。

## 1. 反馈控制流

`已完成 Train 候选 → 公开失败分类 → 归一化失败特征 → 六算子概率 → variation → 新 Genome → 真实评价`。

初始反馈为零。每次候选完整评价后，其公开 failure profile 成为下一 proposal 的反馈状态；不读取未来结果、隐藏标签、evaluator 内部数据或 Validation/Test。B3 只改变算子选择， survivor 仍为标准 NSGA-II。

## 2. 失败分类与分母

| 失败特征 | 公开判定 | 归一化分母 |
|---|---|---|
| planning_failure | PREMATURE_FINISH | episodes |
| tool_call_failure | Schema拒绝或未知/不可用工具 | 工具结果/拒绝事件 |
| dependency_failure | DEPENDENCY、COMPENSATION_REQUIRED、PRIMARY_RECOVERY_REQUIRED | 工具结果/拒绝事件 |
| recovery_failure | retry/recover/compensate 工具失败 | recovery attempts |
| verification_failure | 实际 verify 工具失败 | verification attempts |
| task_incompletion | 非 COMPLETED | episodes |
| unnecessary_tool_call | 同一 episode 重复成功调用同一工具 | 成功工具调用 |

原始 counts、denominators、rates 全部保存。每个 rate 必须在 `[0,1]`。API 基础设施错误不得伪装成 planning failure；可单独保留 execution error。

## 3. 算子集合与映射假设

六个算子：planning、recovery、memory、verification、tool guard mutation 和 crossover。

- planning mutation：等概率选择 `planning_mode` 或 `max_plan_steps`；
- recovery mutation：`recovery_mode`；
- memory mutation：`memory_mode`；
- verification mutation：`reflection_trigger`；
- tool guard mutation：`tool_call_guard`；
- crossover：两个合法父代逐基因交叉。

映射矩阵的行顺序与上述算子一致，列顺序与失败分类表一致：

| 算子 | 权重向量（planning/tool/dependency/recovery/verification/incompletion/unnecessary） |
|---|---|
| planning | (1, 0, 0, 0, 0, 0.5, 0.25) |
| recovery | (0, 0, 0.25, 1, 0, 0.5, 0) |
| memory | (0.25, 0, 0, 0, 0, 0.25, 0.5) |
| verification | (0, 0.25, 0.5, 0, 1, 0, 0) |
| tool guard | (0, 1, 0.5, 0, 0.25, 0, 0) |
| crossover | (0, 0, 0, 0, 0, 0.25, 0) |

这些是待验证的映射假设，不是已成立结论。

## 4. 冻结反馈公式

对每个算子 \(k\)：

\[
\phi_k(F)=\frac{\sum_j W_{kj}r_j(F)}{\sum_j W_{kj}}
\]

\[
p_k=(1-\epsilon)\frac{\exp(\beta\phi_k/\tau)}{\sum_l\exp(\beta\phi_l/\tau)}+\frac{\epsilon}{K}
\]

其中 \(K=6\)、\(\beta=2\)、\(\tau=0.25\)、\(\epsilon=0.1\)。实现先减最大 logit 再指数，避免溢出。概率和为1，每个概率至少 \(\epsilon/6\)。零反馈时全部 \(\phi_k=0\)，严格退化为均匀分布。

对照：

- 固定控制：六个算子均匀概率；
- 随机控制：随机置换动态概率，保持概率多重集合相同；
- B3：真实失败反馈+上述探索下限；
- B5：B3 概率 + B4 survivor，不增加第三套参数。

## 5. 每次更新的账本

`d094_adaptive_evolution.py` 保存：

- profile counts/denominators/rates；
- 当前六算子概率、实际 operator 和 proposal ordinal；
- parent Genome hashes、中间 Genome、offspring Genome/hash；
- 实际 mutation locus、before/after value；
- duplicate proposal 及 `REJECTED_WITHOUT_EVALUATION`；
- 每代 survivor Genome/Phenotype、三种多样性；
- 每次反馈更新对应的已评价 Genome。

B2 不读取反馈，B3 不启用行为选择，B4 不启用动态反馈，B5 才组合二者。

## 6. 测试与合成证据

- 失败分类、分母和隐藏字段拒绝均有单元测试。
- 零反馈精确均匀；recovery failure 提高 recovery mutation；tool failure 提高 tool guard mutation。
- 随机置换保持概率多重集合；非法 tau/epsilon 被拒绝。
- 合成演化中固定、反馈、行为、组合臂均完成8次唯一评价；重复 proposal 有记录且不重复评价。
- 合成 fixture 没有证明反馈减少评价数或提高真实成功率，亦无真实 Pareto 改善证据。

因此 B3 的“自适应”目前只表示已实现并测试了动态概率机制，不表示它具有性能优势。R3 必须检验无效变异、找到有效 Genome 所需评价数、最终性能、反馈偏置和 API 成本。
