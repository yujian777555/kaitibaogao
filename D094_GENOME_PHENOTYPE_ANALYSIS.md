# D-094 R2 Genome 与 Phenotype 分析

## 1. 搜索覆盖与最佳候选

NSGA-II 实际评价32个唯一 Genome（初始8+3代），跨代重复评价=0。648是合法搜索空间大小，实际只探索其中32个，不能把结果外推到全部空间。

| 探索排名 | Genome SHA（前缀） | Success | Harm | Tool Cost | Token Cost USD | Latency（秒） | 配置要点 |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | `b5dbe97a0ff4` | 1.00 | 7.00 | 134.20 | 0.0480141 | 8.2261 | stepwise/retry/after_subtask/max_steps=8 |
| 2 | `a30d7978ef33` | 0.75 | 6.75 | 124.20 | 0.0397926 | 7.7541 | direct/dependency/no reflection/max_steps=5 |
| 3 | `bfd5ee7bcbed` | 0.75 | 6.75 | 124.20 | 0.0406134 | 8.1155 | verification_first/dependency/no reflection |

第一名在三个 seeds 均为12/12成功，但其最终评价因预算耗尽无效；上述排名仅用于后续复现选择，不是性能确认。完整排序位于 `results/phase2_r2/analysis.json`。

## 2. 六基因取值覆盖

| 基因 | 实际取值及 Genome 数 |
|---|---|
| planning_mode | direct=16、stepwise=11、verification_first=5 |
| recovery_mode | retry=18、dependency=11、verify=2、compensation=1 |
| reflection_trigger | after_subtask=12、none=11、after_failure=9 |
| memory_mode | structured_failures=27、compressed_summary=4、recent_trajectory=1 |
| tool_call_guard | post_plan_verify=17、strict_schema=15 |
| max_plan_steps | 3=16、5=14、8=2 |

覆盖不均，尤其 recovery/memory/max_steps。后续实验不能据此对低频取值作稳定因果结论。

## 3. 单基因行为与指标变化

以下为样本内恰好只有该基因不同的候选对；不是随机化因果估计。

| 基因 | 单基因对数 | 行为改变比例 | 平均绝对成功率差 | 平均绝对Token成本差（USD） |
|---|---:|---:|---:|---:|
| max_plan_steps | 5 | 5/5=100% | 0.4833 | 0.0124104 |
| memory_mode | 2 | 2/2=100% | 0.0000 | 0.0002193 |
| planning_mode | 11 | 10/11=90.91% | 0.1364 | 0.0024881 |
| recovery_mode | 6 | 6/6=100% | 0.2361 | 0.0047565 |
| reflection_trigger | 10 | 10/10=100% | 0.0833 | 0.0039434 |
| tool_call_guard | 7 | 7/7=100% | 0.2143 | 0.0044862 |

每个基因在部分对照中改变了真实行为。`memory_mode` 的两个对照只改变成本而没有改变成功率，说明行为变化不能自动解释为性能提升。对数很少，所有结果仅为探索性。

## 4. Phenotype 多样性与坍缩

- 32个不同 Genome 对应 **24个唯一 phenotype**，行为多样性=24/32=**0.75**。
- 没有 complete collapse（唯一 phenotype 大于1）。
- 496个不同 Genome 配对中，17对行为完全相同，占 **3.4274%**。
- 相同行为组有3组，大小分别为4、2、5。说明不同 Genome/Prompt 配置确实可能产生相同工具轨迹。
- 10/32 Genome 在三个 seeds 上产生相同逐任务 phenotype bundle。seed 会改变任务调度，因此该稳定性不能解释为 API 完全确定性。
- B2 final 的 phenotype 不具备性能意义，因为36个 episodes 都没有实际 LLM 调用。

结论：**Genome 改变能够真实改变 Phenotype，但 Prompt/配置差异并不保证行为不同。** 本轮不支持“完全行为坍缩”，也不能声称多样性机制已经带来收益。

## 5. 变异、重复与选择账本边界

- 接受的 variation events=24，其中 mutation flag=true 的 events=3。
- 实际 child-parent 基因差异计数：max_plan_steps=18、memory_mode=8、planning_mode=16、recovery_mode=14、reflection_trigger=21、tool_call_guard=18。
- **无法从现有账本分离每个基因的 mutation 次数**：未记录中间 Genome 和变异位点。这些差异包含 crossover 的贡献。
- 评价级重复=0；被拒绝的重复 proposal 未记录，proposal duplicate rate 不可审计。
- 最终 Pareto front 可复算；每代 survivor phenotype 历史未记录，不能编造选择后多样性时间序列。

这些缺口应进入 R3 的账本设计，而不是事后推断。

## 6. 研究判定

当前候选创新“基于演化计算的 LLM Agent 多目标自适应优化”同时满足“行为可改变”的探索性观察，但不满足有效配对性能验证。R2=INVALID_BUDGET，故当前判定为 **INVALID**，不是 POSITIVE_SIGNAL。

下一轮优先考虑能减少无效/重复行为搜索的失败反馈与 phenotype-aware 选择，并先解决预算预留和最终评价不能用尽预算的问题。
