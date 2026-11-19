# D-094 R3.1 真实五臂 Train-only 机制实验结果

日期：2026-11-19
协议：`D094_R3.1_TRAIN`
运行状态：`COMPLETED`
科学结论：**`NO_CLEAR_GAIN`**
独立复算：`PASS`（账本与指标一致性，不代表算法有效或创新成立）

## 1. 结论摘要

R3.1 真实执行一次并完成 42/42 个 Train episodes、169 次真实 HTTP 请求。所有请求均有唯一 provider request ID；无预算拒绝、执行错误、未知成本或超预算。总输入/输出为 127,148/8,090 tokens，按冻结价格推导的成本及成本上界均为 **0.0478524 USD**，低于 0.50 USD；169 次低于 1,500 次上限。

四个演化臂的 final Task Success 与 Recovery Success 均为 **0/2**。B3−B2、B4−B2、B5−B3、B5−B4 的总体及 seed 201/202 成功率差值全部为 0。B3/B5 将搜索期唯一 Phenotype 从 2 增至 3，但 B4 相对 B2 没有增加；这些结果至多说明算子反馈改变了搜索过程，**不构成性能提升、搜索效率提升、B5 协同或创新成立证据**。

B1 fixed 为 2/2 成功，四个演化臂 final 均为 0/2；但 B1 与演化候选的 Genome、步数上限和恢复配置不同，且样本只有 1 个 Train 任务×2 seeds，不能据此作普遍或单因素因果外推。

## 2. 冻结设计与执行身份

- 模型：`deepseek-flash`；Base URL：`https://api.deepseek.com`；temperature=0；显式非思考 JSON。
- 唯一 Train 任务：`d094_r3_train_compensation_0`；seeds=201/202；search seed=711。
- B1 fixed=2 episodes；B2/B3/B4/B5 各 search=8、final=2 episodes。
- 每个演化臂：population=2、generations=1、最多 4 个唯一搜索 Genome。
- 最大输出=128 tokens；消息上限=4,096 bytes；timeout=20 秒；并发=4；重试=0。
- final 是同一 Train 任务和 seeds 上的新真实 episodes，不是 held-out 泛化评价。
- 执行目录：`experiments/d094_llm_agent/results/r3_1_real/`。
- 执行锁 SHA-256：`1853c31b9607f613ef7469a897271d22332c4fc3fc4881768419e5c003e3697b`。
- 预算计划 SHA-256：`6d7c6b5fece5db7a20fbc0f48b508250d6055f18096ddfd37cc0fb2b8411dc86`。
- 执行锁记录 15 个关键源码文件 SHA-256；执行时本地起始 HEAD 为 `6c084d2fd2617a19e52a9879b14670440bcde777`，源码身份以执行锁为准。

原 R3 六任务设计因保守上界 7,032 请求、5.2993152 USD 超过冻结预算而在 `r3_budget_preflight/` 阻断，真实请求与 episodes 均为 0。R3.1 是保留原设计的缩小版新预注册；其预检为 `PREFLIGHT_PASS`，预检本身没有发送请求或执行 episode。

## 3. 实际完成量与全部成本

下表 tokens 和成本均为该臂 fixed 或 search+final 的合计；成本是 Token 推导值，不是供应商账单。

| 臂 | Episodes | 真实 HTTP | 输入 tokens | 输出 tokens | Token 成本/上界（USD） |
|---|---:|---:|---:|---:|---:|
| B1 Fixed | 2 fixed | 9 | 5,715 | 433 | 0.0022341 |
| B2 Standard | 8 search + 2 final | 40 | 30,399 | 1,930 | 0.0114357 |
| B3 Feedback | 8 search + 2 final | 40 | 30,323 | 1,911 | 0.0113901 |
| B4 Diversity | 8 search + 2 final | 40 | 30,392 | 1,923 | 0.0114252 |
| B5 Combined | 8 search + 2 final | 40 | 30,319 | 1,893 | 0.0113673 |
| **合计** | **42** | **169** | **127,148** | **8,090** | **0.0478524** |

预算分账：B1=9 请求；搜索=136；四个 final 各=6。预算预留保护 41 个请求槽，其中 B1=1、每个 final 池=10；最终全部结算，无 pending 成本、无超预留。42 个 episode 的逐事件 hash-chain 均有效。

## 4. Final / fixed 结果

B1 没有搜索/final 阶段，以下以 fixed 结果列出。Harm 为 episode 均值；Tool Cost、tokens 与 Token Cost 为合计；Latency 为 episode 均值。

| 臂 | Success | Recovery | Harm | Constraint | Tool Cost | 输入/输出 tokens | Final Token Cost（USD） | Latency（秒） | Behavior Diversity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 fixed | 1.00 | 1.00 | 0.25 | 0 | 8.4 | 5,715 / 433 | 0.0022341 | 4.0434360 | 1.00 |
| B2 final | 0.00 | 0.00 | 0.50 | 0 | 3.4 | 4,248 / 294 | 0.0016272 | 2.9320094 | 0.50 |
| B3 final | 0.00 | 0.00 | 0.50 | 0 | 3.4 | 4,208 / 294 | 0.0016152 | 2.9924591 | 0.50 |
| B4 final | 0.00 | 0.00 | 0.50 | 0 | 3.4 | 4,248 / 292 | 0.0016248 | 2.5713633 | 0.50 |
| B5 final | 0.00 | 0.00 | 0.50 | 0 | 3.4 | 4,208 / 293 | 0.0016140 | 2.3761979 | 0.50 |

逐 seed 的 Success 与 Recovery：B1 在 201/202 均为 1/1；B2/B3/B4/B5 在两个 seeds 均为 0/1。四个演化臂每个 final episode 的 Harm=0.25、Tool Cost=1.7、Constraint=0。

## 5. 预注册配对比较

### 5.1 质量、安全与行为差值

四个比较在总体及 seed 201/202 上的 Task Success、Recovery Success、Constraint、Harm、Tool Cost 和 Behavior Diversity 差值全部为 0。

| 比较 | 总体 ΔSuccess / ΔRecovery | Seed 201 ΔSuccess / ΔRecovery | Seed 202 ΔSuccess / ΔRecovery | 总体 ΔHarm / ΔTool Cost / ΔBehavior |
|---|---:|---:|---:|---:|
| B3−B2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| B4−B2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| B5−B3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 / 0 |
| B5−B4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 / 0 |

### 5.2 资源差值

Token 与成本是 final 两 episodes 的合计差；Latency 是 final episode 均值差，单位秒。成本差很小且样本不足，只能描述，不能解释为稳定的成本优势。

| 比较 | Δ输入 tokens | Δ输出 tokens | ΔToken Cost（USD） | ΔLatency（秒） |
|---|---:|---:|---:|---:|
| B3−B2 | -40 | 0 | -0.0000120 | +0.0604497 |
| B4−B2 | 0 | -2 | -0.0000024 | -0.3606462 |
| B5−B3 | 0 | -1 | -0.0000012 | -0.6162612 |
| B5−B4 | -40 | +1 | -0.0000108 | -0.1951654 |

逐 seed 资源差值：

| 比较 | Seed | Δ输入 | Δ输出 | ΔToken Cost（USD） | ΔLatency（秒） |
|---|---:|---:|---:|---:|---:|
| B3−B2 | 201 | -20 | 0 | -0.0000060 | -0.0362784 |
| B3−B2 | 202 | -20 | 0 | -0.0000060 | +0.1571778 |
| B4−B2 | 201 | 0 | -2 | -0.0000024 | -0.0802552 |
| B4−B2 | 202 | 0 | 0 | 0.0000000 | -0.6410371 |
| B5−B3 | 201 | 0 | -1 | -0.0000012 | -0.8237873 |
| B5−B3 | 202 | 0 | 0 | 0.0000000 | -0.4087351 |
| B5−B4 | 201 | -20 | +1 | -0.0000048 | -0.7798105 |
| B5−B4 | 202 | -20 | 0 | -0.0000060 | +0.3894798 |

## 6. 搜索多样性、Pareto 与最终选择

| 臂 | 唯一 Genome | 唯一 Phenotype | Population Behavior Diversity | Complete Collapse | Pareto Front | 选中 Genome |
|---|---:|---:|---:|---|---:|---|
| B2 | 4 | 2 | 0.50 | 否 | 2 | `caff90af495b62d27146f2d09eca189a57f1d0d9cb47919f71c4e446ee07dbc1` |
| B3 | 4 | 3 | 0.75 | 否 | 2 | `aa0d3b4a917dfb36ea686a903c9c3486781d46892fc5a3c3fef178f31fd04973` |
| B4 | 4 | 2 | 0.50 | 否 | 3 | `caff90af495b62d27146f2d09eca189a57f1d0d9cb47919f71c4e446ee07dbc1` |
| B5 | 4 | 3 | 0.75 | 否 | 1 | `aa0d3b4a917dfb36ea686a903c9c3486781d46892fc5a3c3fef178f31fd04973` |

B2/B4 的选中 Genome 为 `max_plan_steps=3`、`direct`、`retry_priority`、`after_failure`；B3/B5 的选中 Genome 仅将 `reflection_trigger` 改为 `none`。两种 Genome 的八个 final episodes 均产生相同公开动作序列和 episode phenotype `41f6f3f2c948ae905228b0207dcaedeed2f4dc10dd8c8bd9d5decbb3eeb727b1`。

B3/B5 的反馈确实改变算子概率与实际变异方向，并产生额外的失败行为类型；但这没有转化为 final 成功率、恢复率、Harm 或 Tool Cost 改善。B4 相对 B2 未增加唯一 Phenotype；B5 相对 B3/B4 未显示互补收益。Pareto front 大小差异本身不等于更高质量的 front。

## 7. 最终失败轨迹的只读归因

直接读取 `episodes.jsonl`、逐 episode trace 与四份 `evolution_B*.json` 后确认：

1. 四个演化臂的全部 8 个 final episodes 均执行 `inspect_state → verify_state → retry_primary`。
2. `retry_primary` 均返回 `PRIMARY_FAILED`，Harm=0.25；此时公开状态为已检查、已验证，但未补偿、未完成。
3. 选中 Genome 的 `max_plan_steps=3`，因此所有 8 个 episodes 随后以 `MAX_STEPS` 终止；没有第 4 步 `compensate_primary`，也没有第 5 步 `complete_task`。
4. 这不是提前 `finish`，也不是 HTTP、Schema、预算或 hash-chain 失败。final Constraint Violation 均为 0，执行错误为 0。
5. B1 使用 `max_plan_steps=5`、`stepwise`、`dependency_aware`。seed 201 在 retry 失败后继续补偿并完成；seed 202 不 retry，直接补偿并完成。B1 与演化臂同时存在多个配置差异，不能把 2/2 对 0/2 归因为某一个创新机制。

因此，当前证据支持的直接失败原因是：**三步动作预算在必需补偿和完成动作之前耗尽**。搜索选择为何反复保留该配置、行为距离是否偏向无质量收益的新颖性，以及反馈是否准确分配长期信用，仍需新实验分离；本轮不能进一步断言根因。

## 8. 逐臂判定

- **B3（Feedback）**：机制被真实触发，搜索唯一 Phenotype 2→3 是相对 B2 的描述性机制信号；final 性能和资源效率均无明确收益。`NO_CLEAR_GAIN`。
- **B4（Diversity）**：相对 B2 没有提高搜索唯一 Phenotype 或 final 行为多样性，选中相同 Genome 且 final 全失败。`NO_CLEAR_GAIN`。
- **B5（Combined）**：搜索期与 B3 一样为 3 个唯一 Phenotype，但相对 B3/B4 没有 final 改善；没有证明协同，也没有证明干扰的独立因果效应。`NO_CLEAR_GAIN`。
- **总体**：真实链路和预算完整性成立，算法性能主张不成立。不得写成 `POSITIVE_SIGNAL`，不得将本结果当作毕业论文创新已经验证。

## 9. 独立复算、回归与证据边界

`audit_d094_r3.py` 不调用真实 API，从 episodes、42 份 trace 和请求账本独立重算行为、指标、失败分类、成本、预算、Pareto 和比较，并校验执行锁及 artifact SHA-256。真实目录复算为 `PASS`，42 episodes、169 请求、127,148/8,090 tokens、0.0478524 USD，与 summary 一致；详见 `D094_R3_1_INDEPENDENT_AUDIT.md` 和结果目录的 `independent_audit.json`。

最终实测：D-094 全量 106/106；CI 同口径七目录全量回归 **648/648**（28+398+8+8+14+86+106）。回归通过不表示算法性能通过。

限制：单 Train 任务、2 seeds、1 代、population=2；final 不是 held-out；没有统计显著性、跨任务泛化、Validation/Test、外部模型训练或 A800 证据。R1/R2 的 INVALID 结果和全部原始账本继续保留。R3.1 不得重复调参或重跑来追求正向结果。

## 10. 唯一下一研究任务

只提出新版本 **R4**，先完成只读失败轨迹归因与 fresh Train 预注册，再经独立审查和明确授权后决定是否执行：

- 在不增加搜索预算或种群的前提下，做动作序列可达性检查，并研究质量约束、状态条件化的行为多样性；
- 用同父代、同任务、同 seed 的配对 offspring 结果研究在线算子信用分配，区分短期失败率与最终恢复贡献；
- 保留 B2/B3/B4/B5 负结果，不重跑 R3.1，不自动调用真实 API，不访问 Validation/Test，不启动 A800。
