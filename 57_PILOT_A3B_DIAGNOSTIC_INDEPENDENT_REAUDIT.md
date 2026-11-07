# 57 — Pilot A-3b 首轮诊断实验独立复核

**审查日期：** 2026-11-07  
**审查对象：** D-060 / `experiments/pilot_a3b/`  
**状态：** **REQUEST CHANGES — DIAGNOSTIC RESULTS NOT VALID FOR CONFIRMATORY CLAIMS**  
**授权边界：** 保留原始诊断 artifact；允许修复实现并在新诊断场景上重跑；不授权正式 A-3b、锁箱测试、Pilot B、A800/ARWM 或真实 LLM API。

## 0. 结论摘要

D-060 的确交付了真实代码、真实模拟器执行、12 个小型分类器用例、216 个诊断场景和可解析的原始结果 artifact。分支 `pilot-a-stateful-recovery` 当前远端 HEAD 为 `edfc7ad0156617dccc4e4bf998df33f991ae921f`，相对 main `683b3fe7fc52c86e917d523fdc6bbb13abbfd653` ahead 94 / behind 0。该 commit 没有 GitHub status checks；D-060 报告的 55/55 是本地测试结果，不是本轮 CI 结果。

**但独立代码审查发现，当前 Stage-2 结果存在足以阻止算法结论的实现和统计问题。** 最严重的不是样本量，而是：
1. A-3 bridge 仍不是一个真正有状态的恢复 FSM；当前基因组是静态 `(error, idempotent, compensatable) -> macro-action` 查表；
2. 失败后 `escalated` 被运行器自动置真，且只要基因组任一未使用规则包含 COMP 动作，就自动触发 Saga 回滚，控制器并未实际选择这些动作；
3. R4 的 `DamageContainment` 评分不检查可避免残留，R3 的正确升级指标也不能区分“策略明确升级”与“恢复失败后运行器自动标记升级”；
4. B 的反例池每次 update 都清空，权重评价函数未被调用，当前 B 不是 R1 设计所描述的反例驱动搜索；
5. 统计脚本对每个 seed 单独计算 CI/p 后再平均 CI 端点和 p 值，不能作为合并后的推断；
6. A 的“非法候选率 100%→0%”是同一手工 ILLEGAL 表定义并修复的内部合法性指标，不是独立语义安全证明；NSGA-II 和 GA 在本轮也观察到零环境违规；
7. A-3 的类别标签来自独立启发式 `label_scenario`，并未对 216 个场景逐个运行 AND-OR 可达性检查器。

因此本轮结果可以保留为**工程/机制诊断线索**，不能用来声称 A 已证明安全提升、B 已验证有效，或 A+B 已优于标准 EA。当前结论：**第一项创新仍值得继续验证；D-060 的算法结果需要修复评价和执行语义后重跑。**

---

## 1. 复核到的仓库和原始数据

### 1.1 仓库状态

- 分支：`pilot-a-stateful-recovery`
- 远端 HEAD：`edfc7ad0156617dccc4e4bf998df33f991ae921f`
- main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`
- compare：ahead 94 / behind 0
- GitHub commit status：无 status checks；本轮没有新的 CI 通过记录
- 本地工作树状态无法通过 GitHub 只读接口验证；沿用 Executor 报告的 clean 状态，但不把它描述为独立验证。

### 1.2 原始 artifact

通过 GitHub blob 读取 `experiments/pilot_a3b/diagnostic_results.json`，成功解析 JSON：

- 内容长度：2,520,655 字符；
- 场景数：216；
- run 记录：24（8 方法 × 3 seeds）；
- 每个 run 的最终评价行：216；
- 所有方法/seed 的 scenario ID 集合一致；
- payload 内记录的 manifest 字段：`068c4dc34e6289e5f39b835942c340bffe76f32c2101d11e8b6f0b3ee1a71409`；
- 原始 blob SHA：`157136d0ca044fa599ca9e0eb9b5317df0890c66`。

**真实类别计数：** R1=96、R2=50、R3=35、R4=35。D-060 的 `NEXT_SESSION_PROMPT.md`、`SESSION_HANDOFF.md` 和 `05_DECISION_LOG.md` 中仍有 R3=36/R4=34 的旧记录，须统一更正为 artifact 的 35/35。

### 1.3 实际 episode 计数

- 固定手工策略：每 seed 216 episodes（每个场景一次，不是演化搜索预算）；
- Random、GA、NSGA-II、NSGA-III、B、AB：每 seed 108,864；
- A：seed 11=108,864；seed 23=108,648；seed 37=108,864。

因此“所有方法每 seed 都是 108,864”不准确。固定 hand 是单次策略评估；A/seed23 因 genotype cache 命中少执行了一个 216-episode 批次。正式实验需明确预算是相同上限还是强制相同实际 rollout，并对缓存命中采用统一记账规则。

---

## 2. 阻断性实现问题

### F1. 当前控制器并非真正的 stateful FSM（CRITICAL）

`FSMGenome` 实际是静态规则表：

`(error, idempotent, compensatable) -> (macro_action, wait_n)`

决策没有使用公开观测历史、当前事务阶段、已提交工具集合、补偿栈、前序动作或跨工具依赖状态。它不能表达真正的状态转移函数或跨步骤记忆。

`run_episode_fsm` 中的 Saga 回滚也不是策略动作：只要基因组任意一条规则（可能从未被触发）包含 `ACTION_COMP`，运行器就会在失败后自动对前序工具逆序补偿。这使“未使用基因”改变执行语义，可能让搜索通过在无关规则中放置 COMP 基因来打开全局回滚。

**必须修正：** 要么实现真正的可观察 FSM（显式控制状态、观察输入、动作输出、状态转移、补偿栈/事务进度），由策略逐步选择 VERIFY/WAIT/COMPENSATE/ESCALATE；要么明确收窄论文主张为“静态工具错误响应规则表演化”，不得继续称为跨工具 stateful recovery controller。

### F2. 自动升级污染 R3/R4 评分（CRITICAL）

`run_episode_fsm` 在任何宏动作失败后都会设置 `escalated=True`，不论策略是否选择 `ACTION_ESCALATE`。因此一次盲重试失败、补偿失败或普通动作失败，都会被记录为升级。

`score_class(R3)` 只检查 `escalated==1`、零残留和未完成任务，无法区分显式正确升级与运行器自动标记。R4 同样受到影响。

**必须修正：** 记录独立事件字段 `policy_selected_escalation`、`runtime_forced_abort`、`escalation_reason`；CorrectEscalation 只能使用策略明确选择且满足 R3 终态合同的事件。

### F3. R4 DamageContainment 指标不符合 R1 定义（CRITICAL）

当前 `score_class(R4)` 只检查 `escalated==1 and duplicate==0`，不检查：
- 可避免残留是否清除；
- 是否新增禁止/不可逆副作用；
- 实际损害是否达到该场景的最小可达损害；
- 不可避免残留与可避免残留的区别。

`evaluate_controller` 又将所有 R4 从 `avoid_resid` 计算中排除，且没有实际输出 `UnavoidableResidualBurden`。所以 R4 策略即使留下可避免残留，也可能被计为 containment success。

**必须修正：** 每个 R4 场景由独立 evaluator 提供 `minimum_reachable_harm`、`unavoidable_residual` 和允许的终态集合；逐 episode 计算 `avoidable_harm=max(0, actual_harm-minimum_reachable_harm)`。DamageContainment 必须同时满足明确升级/记录、无新增禁止效果、达到最小可达损害。不得把所有 R4 残留都排除在损害指标之外。

### F4. 成本目标仍惩罚必要升级（CRITICAL）

虽然 R1-R1 文档写明 R3/R4 的必要升级不进入优化成本，但当前：
`norm_actions = rate(rows, "action_count") / 10`
对全体场景求平均，而 `action_count` 包含升级动作。因此 R3/R4 的必要升级仍会增加 `obj3`。

**必须修正：** 搜索目标中的动作成本按类别条件化，只对 R1/R2 的不必要动作计入优化成本；R3/R4 必要升级成本可作描述性报告，不得进入惩罚项。

### F5. A-3 类别标签不是 AND-OR 判定器输出（CRITICAL）

Stage 1 的 12 个小型 ground-truth 用例通过，但 Stage 2 的 `a3_bridge.label_scenario` 使用 fault-type 规则启发式分类，并未将 216 个 A-3 场景转换为 `EpisodeSpec` 后逐个运行 `classify()`。`test_a3_labels.py` 只有 6 组 sanity tests（含有限 seeds），没有对 216 场景逐项校验。

**必须修正：** 对所有 A-3 场景构建明确的隐藏参数集合和公开观测转移规格，运行 AND-OR checker；若完整建模成本过高，至少建立可审计的解析证明规则，并对每个 fault/task 组合及边界条件进行穷举。不能把 12 个 mini-env 测试通过等同于 216 个 A-3 标签已验证。

### F6. B 反例驱动机制没有按设计执行（CRITICAL）

`CounterexamplePool.update()` 每次调用先执行 `self.weights.clear()`。算法对每个 parent/offspring 调用 update，导致池中只保留最后一个 genome 的失败结果，而不是聚合种群反例。

此外：
- `scenario_weights()` 定义后没有在搜索/评价中调用；
- 反例 key 只有 `(label, invariant_violation, unresolved, duplicate)`，不是设计声称的公开错误签名 × 契约类型 × 死因；
- `targeted_mutate()` 只使用最差 label 粗略改变 mutation probability，不定位具体失败规则；
- B/AB 在触发 targeted mutation 后还会执行普通 mutation，变异次数/强度高于未触发分支，需控制算子调用预算。

**必须修正：** 每代开始清空一次，聚合全种群/全 offspring 的反例；保留公开错误签名、工具契约类型、动作序列和失败后果；把场景权重实际用于评价抽样或权重目标；定向变异只修改与反例签名对应的基因；所有方法匹配总变异次数/真实 rollout 预算。补充单元测试证明池确实聚合多个个体，且改变反例会改变对应基因的采样概率。

### F7. A 的“非法候选率”是内部同源指标，不是独立安全证明（CRITICAL）

`repair_genome()` 与 `is_legal()` 使用同一份手工 `ILLEGAL` 表。A 通过调用 repair 将该表定义的非法动作替换掉，因此最终非法率 0 是该修复器按自身规则工作的预期结果，不能单独证明一般契约语义保持。

并且 `is_legal()` 没有检查所有规则约束（例如非 SCHEMA 的 `ACTION_REPAIR` 未纳入 ILLEGAL 检查，也未检查 default action）；因此它不是完整独立 validator。实际环境违规率方面，NSGA-II 和 GA 本轮也是 0，零违规并非 A 独有。

**必须修正：** 建立独立于 repair table 的合同验证器（独立代码路径/独立测试 oracle），穷举 error × idempotency × compensation × action 组合，并覆盖默认动作、状态转移、前置条件和工具副作用；报告 rule-level invalidity、genome-level invalidity 和 observed environment violations 三个不同指标。

### F8. Reachability horizon cutoff 未正确传播（CRITICAL）

`reachability.py::_or_solve()` 在 `steps >= horizon` 时直接缓存 `False`，但没有将 horizon cutoff 记录为未证明状态；`ReachabilityResult.proved` 因而可能返回 True。若 TASK_COMPLETE 因 horizon 不足而未被找到，但 ZERO_RESIDUAL 可在当前 horizon 内达到，分类器可能把“尚未证明任务不可完成”错误归类为 R3。

**必须修正：** 求解结果改为三值（WIN / PROVEN_LOSE / UNKNOWN）；任何更高优先级目标搜索因 horizon/resource cutoff 返回 UNKNOWN 时，分类器不得继续降级判为 R3/R4，必须返回 UNKNOWN。增加“任务需超过 H 步、但 R3 升级在 H 内可达”的回归测试。

---

## 3. 统计和基线问题

### S1. 当前跨 seed CI / p 汇总无效（CRITICAL）

`stats.py::contrast()` 对三个 seed 分别运行 cluster bootstrap/置换检验，然后直接平均三个 CI 端点和三个 p 值。这不是合并数据后的有效置信区间或 p 值；对 p 值求平均也不是合并检验。

对原始 `diagnostic_results.json` 进行独立探索性重算：先在每个 task×composition cluster 内聚合 4 个场景 × 3 个算法 seed 的 AB−NSGA-II 配对差，再对 54 个 cluster 均值做 20,000 次 cluster bootstrap 和 sign-flip。得到：
- `AB - NSGA-II = +0.0494`
- 95% percentile CI 约 `[-0.0031, +0.1034]`
- sign-flip `p ≈ 0.0874`

该重算仍是诊断性敏感性分析，不是预注册检验；但它确认 primary contrast 仍未达到 0.05，且当前 D-060 的 `p=0.27` 来自不适当的 per-seed p 平均，不能作为正式统计结论。

**必须修正：** 在独立脚本中明确层级结构（task×composition cluster 为抽样单元、算法 seed 为嵌套重复）；预先定义 pooled/hierarchical bootstrap 与 permutation；禁止平均 CI 端点或平均 p 值。所有主次对比在同一统计框架下计算，随后做 Holm 校正。

### S2. NSGA-II / NSGA-III / GA 并非与标准算法完全一致（CRITICAL）

- NSGA-II 的 mating tournament 只比较 dominance，不按 rank + crowding distance 完整比较；crowding 只用于截断。
- NSGA-III 被代码注释为 simplified reference-direction niching，没有实现完整标准 NSGA-III 的 niche occupancy/关联选择流程。
- GA 使用 tournament + weighted-sum 选择、uniform-per-rule crossover，并非 R1 方案描述的 roulette + single-point crossover。
- 本轮没有 GP。
- Random 方法还使用非支配排序做 survivor selection，不是纯 Random Search。

**必须修正：** 正式比较前使用经验证的标准实现或逐项实现标准算法并通过公开 benchmark 单元测试；否则在报告中明确称为 NSGA-II-like / simplified NSGA-III / GA variant，不得把它们作为 canonical baselines。GP 若不纳入，须给出可辩护的表示/问题适配理由。

### S3. 当前搜索集性能不代表泛化

所有进化候选在同一 216 场景集上评价、选择并报告 best_result；没有独立 validation。216 场景来自既有 6 task families × 9 fault compositions × 4 repeats，属于新 seed 的同族诊断，不是新的 task/fault family OOD。

因此当前结果只能解释为固定诊断场景上的搜索结果，不支持泛化主张。下一轮至少要把 train/validation 分离；held-out 继续锁箱。

---

## 4. 设计与记录一致性问题

1. 55-R1 §6.2 标题写 `(R1+R2):(R3+R4)=3:1`，但 Train/Validation 表实际为 144:96、72:48，即 3:2；Held-out 表 58:38，亦非 3:1。必须选定真实比例，重算表格和目标分布权重，不得留矛盾。
2. 本轮诊断实际标签分布 146:70（R1+R2 : R3+R4），约 2.09:1；它是诊断样本分布，不等于 55-R1 预注册配额。
3. D-060 多份维护文档将 R3/R4 写为 36/34；原始 JSON 是 35/35。新增本报告作为更正依据，后续接管提示词统一使用 35/35。
4. R1 文档写“同初始池/同预算”；本轮搜索方法确实按 seed 共用同一初始池，但实际 episode 计数有 cache 差异，hand 也只是固定策略单次评估。正式协议必须分别定义搜索预算、策略评估预算和缓存记账。

---

## 5. 对本轮结果可保留的结论

| 主张 | 当前证据等级 | 可否写成已成立 |
|---|---|---|
| 12 个 mini-env 分类测试通过 | 工程单元测试证据 | 可以写“这些测试用例通过”，不能外推到所有 A-3 场景 |
| A 将内部 ILLEGAL 表定义的规则修复为合法 | 实现性质证据 | 可以，但须称内部语法/规则合法性 |
| A 提升真实环境安全性 | 指标与对照不足；NSGA-II/GA 也零违规 | 不可以 |
| B 反例驱动机制有效 | B 实现与设计不一致 | 不可以 |
| A+B 优于 NSGA-II | 当前 primary 不显著，统计汇总方法需修正 | 不可以 |
| A+B 优于强手工策略 | CondRec 低于 hand | 不可以 |
| 第一项创新已经成立 | 没有证据 | 不可以 |

**保留的合理结论：** A 的规则修复器在当前手工 ILLEGAL 表下能够将最终种群映射到该表定义的合法子集；A/AB 在本轮诊断数据上没有观察到不变量违规；AB 相对 NSGA-II 有正向点估计但区间跨零；强手工策略 CondRec=1.0。以上都只是诊断性结果。

---

## 6. 下一阶段唯一优先顺序

不要先做正式功效分析。当前指标/执行语义有缺陷，基于这些结果估算样本量会把错误效应结构固化。

### Stage 1 — 修复评价器与控制器语义
1. 明确选择“真正有状态 FSM”或收窄研究主张；若保留 stateful，增加控制器内部状态、公开观察历史、跨工具事务进度和显式补偿动作。
2. 删除“基因组任一规则含 COMP 就自动 Saga rollback”；回滚必须来自策略动作。
3. 记录显式升级与运行器强制终止，修复 R3/R4 评分。
4. 实现 R4 最小可达损害、可避免/不可避免残留分离。
5. 修复 action cost，不惩罚必要升级。
6. 让 A-3 全部场景的标签由可审计 reachability checker 或经穷举证明的解析判定产生。
7. 修复 horizon 三值传播。

### Stage 2 — 修复演化机制与基线
1. 修复 B 的池清空和聚合；让反例签名真正影响对应基因。
2. 统一 B/AB 与对照的 mutation count/intensity。
3. 独立实现 contract validator，补全 A 的约束覆盖。
4. 使用 canonical NSGA-II/III/GA；补 GP 或记录排除理由。
5. 统一 rollout 实际预算与缓存规则。

### Stage 3 — 统计重算与新诊断
1. 修复 pooled/hierarchical cluster bootstrap、置换和 Holm。
2. 建立 train/validation split，不能再在同一数据上选最优并报告为验证结果。
3. 使用新生成的诊断场景重跑；原始 D-060 artifact 永久保留。
4. 做每个故障组合的机制消融和失败案例审计。

### Stage 4 — 再做功效与预注册
只有 Stage 1–3 通过后，才用修正后的方差估计 cluster-level power，确定 cluster/seed/rollout 数，完成 49 号系统性相关工作审计，形成 preregistration candidate 交用户批准。正式 A-3b 仍需用户明确批准后运行。

---

## 7. 最终 Gate

| 事项 | 判定 |
|---|---|
| Stage-1 mini-env 12-case 测试 | PASS（限定于这些测试用例） |
| D-060 原始诊断 artifact | PRESERVED / PARSEABLE |
| D-060 机制诊断结论 | REQUEST CHANGES / 仅可作探索性线索 |
| A 的契约语义保持机制已证实 | NO |
| B 的反例驱动机制已验证 | NO |
| A+B 优于标准 EA | NOT ESTABLISHED |
| 第一项创新 | CONTINUE WITH REVISED IMPLEMENTATION |
| 正式 A-3b | HOLD |
| Pilot B / A800 / ARWM / 真实 API / UndoBench TEST | HOLD |

**最终判断：** 不放弃方向，但必须先修复当前 controller/evaluator/B/statistics 的实现偏差。现在扩大 rollout 或直接做功效核算是不负责任的；下一轮应先让“策略究竟做了什么、R3/R4 是否正确评分、B 是否真的按反例工作”变得可信。
