# 102 — D-091 原始证据、搜索身份与可达性独立审计结果

**日期：** 2026-11-17
**工作分支：** `pilot-a-stateful-recovery`
**审计范围：** D-090 Train-only 已保存证据；不重跑搜索、不选择候选
**当前状态：** D091_PARTIAL / HOLD；审计执行与专属 CI artifact 复核已完成，完整搜索过程为 NOT_AUDITABLE_FROM_SAVED_TRACE

---

## 1. 总结判定

D-090 的三份原始 JSON 完整，15 个搜索 best candidates 和 5 组固定消融的保存指标均可从逐场景 rows 精确复算，最大差异为 0。但当前标注为 Random Search 的对照实际执行 NSGA-II，State-Conditioned Evolution 只有静态 mutation bias，且全部 15 个 best candidates 在当前 96 个 Train 场景上行为等价。因此，保存的 best_rows 数值可信，五种搜索方法的比较结论不可信。

| 审计门 | 结论 | 含义 |
|---|---|---|
| DATA_INTEGRITY | PASS_WITH_LIMITATIONS | 原始结果文件一致；101 号有一个 source blob 登记更正 |
| METRIC_RECOMPUTE | PASS | 15×96 搜索 rows 与 5×96 消融 rows 全部复算一致 |
| METHOD_IDENTITY | FAIL | Random Search 身份无效；State Evo 非动态反馈 |
| PHENOTYPE_DIVERSITY | FAIL | 8 个 genome、8 个规则签名，但只有 1 个行为 phenotype |
| R2_REACHABILITY | CLAIM_FALSIFIED | 23-step witness 成立；BFS 最短路径为 21，不是 25 |
| ABLATION_SAFETY | FAIL | P2/P4 存在未清结 pending 的硬约束违规 |

本审计不证明演化算法提升，不产生冻结候选，不授权 Validation/Test。

## 2. 原始文件完整性与哈希

审计输入仅为 D-090 已提交的 manifest、report、ablation 和源码。原始文件未被修改。

| 文件 | 字节数 | 原始 SHA-256 | Git blob SHA | 内部 SHA 检查 |
|---|---:|---|---|---|
| `d090_train_manifest.json` | 333,077 | `3bada41e05856695ca13dd2b04f33e131e3535be2323e6cb1c84a3aac26cf4a0` | `b917b4c624601022e8d8896182dfaed71ba0d21c` | PASS |
| `d090_train_report.json` | 3,443,223 | `e9412e8c76ce99c6a2b83a51dbb0e89d090d3e9ac838824d5e8d427c0a1be720` | `bc7a10750b9501462ae9cfe70a171a268f910fcc` | PASS |
| `d090_mechanism_ablation.json` | 1,134,107 | `632b82eb57df91e5618055aadac01b918ebbc69d170ef77882a40a7969da3ce2` | `6503132319b2bbbb8d1c8fe720c68b6c37432604` | 无内部哈希字段；原始 SHA 一致 |

manifest 内部 SHA-256 为 `7d677fe075a5bac6b4241be6c4f38e0c55022b6059729e9a05c7cdf7d633350d`；report 内部 SHA-256 为 `99a0660e81b072de2e596ff589356d3bb978318f4005d057966779ba9f8f38cf`，均独立重算一致。

### 登记更正

101 号将 `d090_policies.py` blob 登记为 `c96beaf6577cf989e6baaa4d22065662b269844`，真实值是 `c96beaf6577cf9898e6baaa4d22065662b269844`。真实 blob 与 D-090 源码提交 `1af9bc832058dd1328862dbba3da3ef248e4edd3` 中的对象一致。这是提示词中的登记转写错误，不是原始数据被改写。审计器显式保存更正，且在无历史 Git 对象的 shallow CI checkout 中也可复核。

### 场景完整性

- 6 families × 4 strata × 4 repeats = 96 个唯一 scenario ID。
- namespace 全部为 `d090r|train|`，split 全部为 Train，无 Validation/Test 混入。
- R1/R2/R3/R4 各 24；family×stratum×repeat 网格无缺失或重复。
- 每个 run 的 96 个 best_rows 与 manifest 按相同顺序一一对应。
- 每条 row 的 trace 长度、decision count、成本、条件指标和约束字段均通过一致性检查。

完整输入与源码指纹见 `experiments/d090_recovery/results/d091_audit/d091_source_manifest.json`。

## 3. 指标独立复算

复算不调用原实验的 `run_experiment()`、`run_method()` 或搜索入口。R1/R2 的 Conditional Recovery 合并分母为 48，R3/R4 分母各 24，Harm 和 Recovery Cost 使用全部 96 rows；计数型约束使用求和，不使用均值替代。

### 搜索 best candidates

15 个 run 的原始汇总均为：

| CondRec | R3 | R4 | Harm | Recovery Cost | Constraint | Pending | Duplicate |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.0 | 0.875 = 21/24 | 1.0 = 24/24 | 0.0416666667 = 4/96 | 12.9583333333 | 0 | 0 | 0 |

所有 15 个 best_summary 均与独立复算完全一致。这只是保存的最佳候选在 Train 上的结果，不是搜索公平性或泛化证据。

### 固定机制消融

| Variant | CondRec | R3 | R4 | Harm | Recovery Cost | Constraint | Pending |
|---|---:|---:|---:|---:|---:|---:|---:|
| Legacy B3 | 1.000 | 0.500 | 1.000 | 0.270833 | 11.906250 | 0 | 0 |
| P1 Pair-Race | 0.833333 | 0.708333 | 0.916667 | 0.479167 | 12.947917 | 0 | 0 |
| P2 Exhaustive-Fallback | 1.000 | 0.666667 | 1.000 | 0.145833 | 13.072917 | 2 | 4 |
| P3 Completion-Gate | 1.000 | 0.583333 | 1.000 | 0.229167 | 12.177083 | 0 | 0 |
| P4 Harm-Ordering | 1.000 | 0.416667 | 1.000 | 0.312500 | 11.843750 | 2 | 2 |

所有变体 Duplicate Compensation 均为 0。P2/P4 的硬约束违规不能被较低 Harm 或 Cost 抵消。

### 输出粒度与证据缺口

- `d091_metric_recompute.json`：逐 run、逐变体 expected/actual/difference。
- `d091_per_family_metrics.csv`：480 条 method×seed×family×stratum 记录。
- `d091_per_scenario_metrics.csv`：1,920 条逐场景记录，含 outcome、成本、约束和 trace hash。
- 固定消融与搜索 best candidates 分表、分集合计算，没有混合分母。

D-090 report 只保存 15 个 best candidates 的 1,440 条场景 rows。虽然元数据声明每 run 96 unique genome evaluations，即总计 1,440 次 genome evaluation，但全部候选的逐场景轨迹没有保存。实际 proposal 数、重复 proposal、cache hits、archive 历史和真实 rollout 总数均为 `NOT_AUDITABLE_FROM_SAVED_TRACE`，不能根据摘要补造。

## 4. 搜索算法身份与公平性

### 方法分派矩阵

| 标签 | 实际实现 | Survivor/保留规则 | 动态失败反馈 | 判定 |
|---|---|---|---|---|
| `random` | 与 NSGA-II 相同的演化路径 | `nsga2_select` | 无 | FAIL |
| `nsga2` | 非支配排序与 crowding distance | `nsga2_select` | 无 | 实现存在；保存过程不完整 |
| `nsga3` | 理想点平移、p=3 参考方向、关联与 niche 选择 | `nsga3_select` | 无 | 与 NSGA-II 分支不同，但属简化实现 |
| `state_evo` | 固定 profile 的 mutation/crossover | `nsga2_select` | 无 | 不是动态状态反馈搜索 |
| `state_random` | 规则基因空间直接随机采样 | 最终 `_best()` | 无 | 随机搜索真实存在，但初始池不配对 |

`run_method()` 在 `experiments/d090_recovery/d090_experiment.py:68-121` 只显式区分 `state_random`、`state_evo` 和 `nsga3`。`random` 没有独立分支，与 `nsga2` 使用相同 RNG 初始化、初始种群、默认变异/交叉及 `nsga2_select`。三个 paired seeds 的 best genome 也逐一相同。这一结论由静态调用链和保存输出共同支持，不需要重跑搜索。

NSGA-III 来源 `experiments/d089_recovery/d089_search_experiment.py:140-187` 确实执行参考方向、关联和 niching，但缺少完整的极端点归一化流程，且最小 niche 并列时随机选取，不能直接称为完整 canonical NSGA-III。现有输出不能证明两个算法的完整历史执行质量。

### `GENERATIONS=6` 与算子证据

`GENERATIONS` 没有出现在 `run_method()` 的循环条件中。实际循环由 `while evals < BUDGET` 控制；6 仅被写入 report metadata。由于没有 generation-level 日志，实际代数、每轮 proposal 数、mutation/crossover 调用次数和 survivor 历史均不可从现存 artifact 复原。不能声称“真实执行了 6 代”，也不能猜测一个替代数字。

### 六维目标与最终选择不一致

`survivor` 使用六维目标：硬约束、CondRec、R3、R4、Harm、Recovery Cost。`_best()` 却从完整 archive（包括重复 proposal）进行可行性过滤后，以 `min(R3,R4)`、`R3+R4`、`-Harm`、`-RecoveryCost` 做字典序选择：

- 不显式使用 CondRec；
- 不是从最终 NSGA population 或 Pareto front 直接选择；
- 与六维 survivor 口径不同；
- 各方法共用该规则虽避免单方获益，但不能解决搜索身份和过程日志缺失。

因此，当前结果只能标记为 `IMPLEMENTATION_COLLAPSE + PHENOTYPE_EQUIVALENCE`，不能把公平性或算法优劣写成已验证。

## 5. 15 个候选的行为等价

独立计算 canonical genome、规则块、逐场景 action/observation/cost/tick trace 和 outcome fingerprint 后：

- 15 个 best candidates 有 8 个不同 canonical genome；
- 有 8 个规范化规则签名和 8 个规则块签名；
- 96 场景 full trace bundle 只有 1 个 hash；
- outcome bundle 也只有 1 个 hash；
- 105/105 对候选的 trace、outcome 和联合 phenotype 全部相同；
- 这不是聚合指标舍入造成的 `AGGREGATION_COLLISION`。

在 15 个候选间变化但未产生任何已保存行为差异的 8 个位点为：

`completion_gate`、`completion_mode`、`exhaustive_fallback`、`fallback_mode`、`harm_budget_threshold`、`harm_first_ordering`、`harm_order_mode`、`pair_race_alternate`。

这与 boolean/mode 冗余、条件门控未触发和最终行为平台相符。例如 `pair_rule=1` 时 `_primary_deadlocked()` 直接返回 False，使 `pair_race_alternate` 的差异不能经该路径生效。结论仅限当前 96 个 Train 场景和 15 个保存候选，不能外推为所有环境或全部已评价 genome 都等价。

输出：

- `d091_candidate_fingerprints.json`：逐候选 genome/rule/trace/outcome hash；
- `d091_candidate_phenotype_matrix.csv`：105 对 genotype Hamming 与 phenotype equivalence；
- `d091_per_scenario_metrics.csv`：逐场景 trace hash 和结果字段。

## 6. g03-r2 的 25 步下界被推翻

### 旧审计对象错位

`audit_g03_public_reachability.py` 构造的是 D-089 `g03_PAIR_RACE` repeat 0；`audit_g03_trace.py` 读取 D-089 `d089_search_report.json`。二者均不能证明 D-090 `d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r2` 的下界。旧脚本和历史证据未修改。

### 23-step witness 真实回放

D-091 使用 `make_scenario("d090_PAIR_RACE", "D3_DEPENDENT_ABORT", 2)`，并先验证生成场景与保存 manifest 逐字段一致。随后将 101 号的 23 个动作逐步送入真实 `DependencyRecoveryEnv.step()`：

- 第一轮 8 步：A/B alternate 与 C primary dispatch，两个共享 WAIT，再 VERIFY A/B/C；
- 第二轮同样 8 步；
- 第三轮 6 步：A/B alternate dispatch，两个共享 WAIT，再 VERIFY A/B；
- 最后 1 步 ESCALATE。

结果为 `decision_count=23`、`class_success=1`、`correct_escalation=1`、`residual=0`、`pending=0`、`duplicate=0`、`constraint=0`、`runtime_forced_abort=0`，recovery cost=26。每一步 observation、tick、pending 和状态均保存在 `d091_r2_witness.json`。

### BFS 最短路径为 21

独立的单位成本 BFS 在同一真实环境中找到 21-step 安全路径，recovery cost=28。它展开 8,572 个状态、记录 9,729 个去重状态；在首次达到目标的深度之前按层处理所有可达非终止状态。

21 步 witness 的结构为：

1. A alternate 第一轮 dispatch→WAIT→WAIT→VERIFY=FAILED，占 4 步；
2. A alternate 第二轮同样 4 步；
3. 第 9 步第三次 dispatch A alternate；
4. 第 10–11 步 dispatch B/C primary 第一次；第 12 步共享 WAIT；第 13–14 步 VERIFY B/C=FAILED；
5. 第 15–16 步再次 dispatch B/C primary；第 17 步共享 WAIT；
6. 第 18–20 步分别 VERIFY A/B/C=COMPENSATED；第 21 步 ESCALATE。

最终 A/B/C 均 COMPENSATED，D 为 NOT_COMMITTED，零残余、零 pending、零 duplicate、零硬约束违规。完整 action/observation/tick 轨迹见 `d091_r2_shortest_path.json`。

BFS 状态包含工具状态、路线 attempt indices、pending_success、resolve timing、全局环境 tick、terminal action 和 duplicate count。去重使用与绝对 tick 等价的剩余 resolve time，因为新延迟相对于 dispatch tick。动作覆盖共享 WAIT、所有 pending 工具的不同 VERIFY 顺序以及所有当前可行的 primary/alternate dispatch。无 pending 的 VERIFY、permission 下的 RETRY、受阻或已完成后的无效果动作、STOP_SAFE 和产生 duplicate 的分支不能改善 R3 可达性。

因此 25 既不是下界，23 也不是最短；当前模拟器语义下的正确最短决策数是 **21**。D-090 原 24-step cap、场景、标签、分母和历史报告均未修改；99 号的下界表述由本报告更正。

## 7. P1/P2/P3/P4 的失败机制

所有失败和约束行的逐事件 action、observation、tick、成本、残余、Harm、pending、final state 均保存在 `d091_ablation_failure_traces.csv`；聚合见 `d091_ablation_failure_summary.json`。

### P1 Pair-Race：局部改善被全局退化抵消

P1 有 17 条 class failure：R2=8、R3=7、R4=2。g03 R3 失败由 4/4 降为 1/4，但总 Harm 从 26 升至 46（均值 .270833→.479167）：

- R2 新增 32 点 Harm，R3 减少 14 点，R4 新增 2 点；
- 8 个 R2 失败来自 Pair-Race 与 Multi-Route 的四个 repeats；
- 这些场景均在第 1 步直接 ESCALATE，D 保持 PARTIAL，每行 residual=4、avoidable_harm=4；
- `_pair_filtered_available()` 在存在活动互依环时排除了当前工具 D，继承的 `_recover_current()` 因 D 无可用路线而升级；R2 被错误纳入了面向权限中止的 pair 过滤；
- 其余 R3/R4 失败显示延迟路线选择与预算门控仍会留下残余，P1 没有硬约束违规，但整体不可接受。

### P2 Exhaustive-Fallback：迟到派发后带 pending 终止

硬约束位于：

- `d090r|train|d090_MULTI_ROUTE|D3_DEPENDENT_ABORT|r1`：14 步、pending=2；
- `d090r|train|d090_MULTI_ROUTE|D3_DEPENDENT_ABORT|r3`：14 步、pending=2。

两条轨迹都不是 runtime forced abort。fallback 扩展了可用路线并允许在已有回执未清结时继续迟到派发。最后一步之前 `_should_stop()` 返回 True，但 `_resolve_pending()` 返回 None；`_abort()` 随后仍执行 ESCALATE，留下 A/C 两个 pending。这里同时存在 fallback 与停止路径协调不足，以及“pending handler 无动作”被错误当作可终止条件的门控缺口。P2 不得成为候选。

### P3 Completion-Gate：停止规则不能创造可达路径

P3 的 g03 R3 四个 repeats 均与 Legacy 相同地失败：C 被补偿后，A/B 仍无可执行路线，随后 ESCALATE。completion gate 只改变停止条件，不会生成新的路线、打破互依环或提供 alternate 可达性，因此没有 g03 改善。它使其他部分场景避免过早停止，但不是针对 g03 根因的修复。

### P4 Harm-Ordering：低成本排序不等于最少决策

硬约束位于 Deep-Chain R3 的 r1/r2，均为 16 步、pending=1、非 runtime forced abort。紧张预算下的 `tight_key` 实际按依赖数、路线成本和幂等标志排序，并没有使用完整的结果表、学习到的延迟或真实剩余清结成本。它在那一步选择 B alternate，留下 pending；随后同样发生 `_should_stop=True`、`_resolve_pending=None`、直接 ESCALATE。P4 的 Harm/Cost 数值不能抵消该硬约束违规。

## 8. 科学结论与研究路线

### 可以保留

- 三份原始 JSON、96 场景、15 个 best_rows 和五组固定消融的数值可复算；
- 所有保存的搜索 best candidates 在该 Train manifest 上均为零硬约束违规；
- P1 的局部 g03 改善与全局 Harm 退化同时成立；
- D-090 没有形成可冻结候选，Validation/Test 继续 HOLD。

### 必须撤回或更正

- 撤回“当前 `random` 是独立 Random Search”的说法；
- 撤回“当前 `state_evo` 已验证动态状态反馈搜索”的说法；
- 不得把 `GENERATIONS=6` 当作已执行并记录的搜索代数；
- 撤回 g03-r2 的 25-step 下界，替换为经真实 BFS 验证的 21-step 最短路径；
- 不得把五方法相同结果解释为演化与随机搜索公平比较后无差异；
- 不得把 best-only 账本当作完整搜索过程证据。

### 下一轮最值得研究的机制

优先研究可辨识的、状态条件化的补偿调度与反馈演化：显式表示共享等待、pending 清结、失败后的路线切换和剩余预算，而不是继续增加静态权重。Pair-aware、delayed-confirmation reservation 只能作为可分别消融的候选机制，不能预先捆绑成既定创新。

前提是先修复算法身份、表示冗余和过程账本。D-092 仅形成 Train-only 预注册方案 `103_D092_TRAIN_ONLY_PREREGISTRATION.md`，本轮不执行该方案。

## 9. 必答问题逐项结论

| 问题 | 审计回答 |
|---|---|
| 原始数据是否完整且哈希一致 | 是；101 号一个 source blob 登记错误已单独更正 |
| 15 个 best_rows 指标是否可复算 | 全部可以，最大差异 0 |
| Random Search 是否真实存在 | 当前 `random` 不存在；它与 NSGA-II 同路径 |
| State Evo 是否有动态反馈 | 没有；mutation profile 是常量 |
| 6 generations 是否可证 | 不是循环控制量；实际代数及算子次数不可从保存数据复原 |
| 15 个候选是否行为等价 | 在 96 个 Train 场景上完全等价，8 genome→1 phenotype |
| NSGA-II/III 是否执行不同算法 | 源码 selector 不同；NSGA-III 为简化实现，完整执行历史不可审计 |
| 最终选择是否与六维目标一致 | 不一致；archive 字典序选择不显式包含 CondRec，也不直接选 Pareto/front population |
| 25-step 下界是否成立 | 不成立；23-step witness 成功，BFS 最短为 21 |
| P1/P2/P4 问题是否定位 | 已定位到具体场景、动作、pending 和控制流；P2/P4 为硬失败 |
| D-092 如何设计 | 见 103 号；真实 Random、可测试 NSGA-II/III、明确反馈公式、统一预算/选择和完整 proposal 日志 |

## 10. 审计 artifact、CI 与禁止边界

D-091 专属 artifact 包含九个必需文件，并额外保存逐场景指标、候选 fingerprint、消融汇总和输出 SHA manifest。输出目录：`experiments/d090_recovery/results/d091_audit/`。

- 审计实现提交：`89fa34e2345f0a1a82b9c4c17f1dd2c87e6fd865`。
- shallow-checkout 修复提交：`bb403f50880b31ae58d0882910b51ebb47a8f435`。
- 跨平台 raw-byte 修复提交：`e5d13f60b30910d6c6b0c10d99f66227b125fb59`。
- 本地完整回归：28+398+8+8+14=**456/456**。
- 首次 CI `44065635071` 因 shallow checkout 无法读取历史 Git 对象而失败，原始日志保存为 `results/d091_ci_44065635071_failure.log.gz`。
- 第二次 CI `44066525906` 暴露历史 Windows raw SHA 与 Linux 检出字节的差异；Git blob 和内容指标一致。原始日志保存为 `results/d091_ci_44066525906_failure.log.gz`。新增无历史对象及 Git-normalized bytes 两项回归测试。
- 最终修复 CI run `44067543678` = **success**，job `133985029253`；`Test d090_recovery` 与 `Audit saved D-090 evidence without genome search` 均实际成功。
- 专属 artifact：`d091-independent-audit-evidence`，ID `14320134130`，digest `sha256:d5504a81fe0e56a828ec617571ba82788a53fcc9393ef122165162116f4eca57`，到期时间 `2027-02-15T10:44:04Z`。下载地址为 `https://api.github.com/repos/yujian777555/kaitibaogao/actions/artifacts/14320134130/zip`。
- 下载后的 13 个文件全部通过输出 SHA-256/字节数检查；指标、候选矩阵、witness、BFS、消融轨迹与本地独立输出一致。artifact 保留 raw-byte 跨平台限制和算法身份失败状态，不把 CI 绿色解释为算法有效。

本轮没有运行 D-090 搜索、新 genome search、调参、候选冻结、Validation、Test、Pilot B、正式 A-3b、真实 LLM API、A800/ARWM、UndoBench TEST、ThinkingBox 或 main merge。绿色 CI 只证明审计和测试执行，不改变上述科学判定。

**唯一下一任务：** 独立审查本报告与 103 号预注册草案；在审查和明确授权前，不实现或运行 D-092。
