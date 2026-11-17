# 105 — D-092 R1 独立预注册审查

**审查日期：** 2026-11-17  
**仓库/分支：** yujian777555/kaitibaogao / pilot-a-stateful-recovery  
**审查对象：** 103_D092_TRAIN_ONLY_PREREGISTRATION.md（R1）、R0 历史文件、R1 绑定源码、D-090 Train manifest  
**最终决定：** REQUEST_CHANGES / HOLD  
**R1 状态：** REVIEWED_NOT_ACCEPTED / NOT FROZEN / NOT RUN  
**授权边界：** 本轮只读审查；未实现搜索器、未运行算法测试、未运行 probe rollout、未执行 genome search、未访问 Validation/Test。

---

## 1. 远端版本与文件身份

| 项目 | 独立核验结果 |
|---|---|
| 审查时 branch HEAD | 7a94d9711fa792e76d710d48f5cfc562e0c5a072 |
| main HEAD | 683b3fe7fc52c86e917d523fdc6bbb13abbfd653 |
| ahead / behind | 310 / 0 |
| R1 Git blob | f5dc28e67d648344cfd8465956f51e1f0582baf4 |
| R1 raw SHA-256 | 2b67f64a20ffe622264ee97629db7d587f56005e7f551ff59bef4b3b29099ec5 |
| R1 canonical SHA-256 | 3a5ad0f108c79bc5fb71529d22d774f4776206c2db42022a994d1893fa1fdc55 |
| R0 Git blob | 1c26bbfc6a2aad49869c41c24b9a90b5ae4711b8 |
| R0 raw SHA-256 | 3d0b0d0e22d5cfd676ddb8ff7feadaf2dfc9dd7981c0d50920fcf5dd1bf9f367 |

R0 与 R1 修订前父提交 c50e674592cae1020eba766247fa6bc69d413ca6 中的原始 103 文件逐字节相同。R1 的 raw/canonical SHA 均重新计算匹配。

### 1.1 B1 数据绑定复核

- R1 列出的 13 份源码 Git blob SHA 全部与当前远端文件匹配。
- 13 份源码 canonical SHA-256 全部重新计算匹配。
- D-090 Train manifest Git blob 与 R1 一致；canonical SHA-256 重新计算匹配。
- manifest 中存在 96 个唯一 scenario IDs。
- R1 指定的 5 个 locus anchor IDs 全部存在。
- 排序后的 96-ID compact JSON SHA-256 为 cccb84511a84f3bcd1dd7141b83fb278459e0267cf00a332e96f6d7cb6da6934，重新计算匹配。

**B1 的既有数据/源码身份核验通过。** 这不等于新 typed adapter、搜索器和账本已经有执行哈希；R1 已正确说明这些实现尚不存在，必须在后续实现审查中追加锁定。

### 1.2 CI 与本地状态

- 对 R1 提交 SHA 查询 workflow runs：0 条新运行。
- 最新既有 D-091 代码审计仍为 run 44068259009 success；它不是 R1 CI，也不是 R1 算法测试。
- 本轮只读远端 GitHub，不能检查执行者本地工作树；执行者报告中的 clean 状态仅保留为其执行记录，不冒充本轮本地核验。
- 本轮没有新 artifact。

---

## 2. 总体审查结论

R1 已显著提高协议完整度。以下内容经复核成立：

1. 五个实验臂的角色和比较职责已经区分。
2. 96 unique genomes × 96 Train scenarios = 9,216 episodes/run；五臂五 seeds 的 230,400 上限算术正确。
3. 五字段 typed genome 与旧策略字段之间的主要门控映射基本符合 D-090 源码。
4. 反馈矩阵每行权重和为 1；六项特征的定义在正常完整 rollout 下有界；phi(0)=0 成立。
5. K=4、epsilon=0.1 时零反馈产生严格均匀概率；理论概率边界 0.025–0.925 正确。
6. 五维、Das–Dennis p=3 的参考方向数 C(7,4)=35 正确。
7. R3 的 1/24 阈值对应每个 run 的 24 个 R3 场景中一个成功事件的比例；4/5 同向被定位为 Train-only 探索判据。

但 R1 仍未形成唯一、可执行、可复现的算法协议。特别是反馈轮次未定义、NSGA-III niching 不是已写明的 canonical 流程、硬约束把合法环境拒绝回执误称为非法状态转移。这些问题会直接影响方法身份、反馈计算和候选可行性。

**因此不能接受 R1，也不批准实现或运行 D-092。**

---

## 3. 必须修订的阻断项

### F1 — BLOCKER：搜索轮次、种群与父代选择没有定义

**位置：** R1 §3.4、§4.1–4.2、§6.1、§7.1。

R1 多次使用 offspring round、round_id、survivor、parent IDs，但没有唯一规定：

- 种群规模 mu；
- 每轮 offspring 数量 lambda；
- 96 个评价如何分批；
- 12 个初始候选是否必须 canonical-unique；
- mutation 的父代如何抽取；
- crossover 的两个父代如何抽取，是否允许同一个父代；
- A0 的随机采样分布，以及是否有放回；
- A3 在何时收集完整反馈、何时更新概率。

R1 §6.1 的 U_t 是上一轮新完成的 unique genomes 集合，但“上一轮”没有确定边界。因此 F_t 和 A3 的概率更新时点尚不可执行。仅写出反馈公式不能定义反馈演化算法。

**建议的最小闭合方案（供 R2 明确采纳或给出等价替代）：**

- 固定 mu=12；
- 12 个共享初始 genome 从 144 个合法组合中无放回抽取，保证 12 个 canonical-unique；
- 固定 lambda=12 个新 unique evaluations/offspring round；
- 12 个初始评价 + 7 轮 × 12 个新评价 = 96 个 unique evaluations；
- 每轮以父代 population 生成 12 个 unique offspring evaluations；重复 proposal 仍计 attempt，但不计入该轮的 12 个 unique 数；
- 每轮完成后，以 parent+offspring 执行 survivor selection，得到下一轮 12 个父代；
- A3 的 U_t 精确定义为该轮 12 个新完成 offspring genome 的集合；第一个 offspring round 使用零反馈，后续 round 使用上一轮反馈；
- 明确 mutation parent、crossover parent 的抽取分布和是否允许 self-crossover；
- A0 从尚未评价的合法 genome 中按均匀分布无放回抽取，或明确选择其他分布并说明重复处理。

如果不采用上述数值，必须给出另一套同样唯一、可复算的 mu/lambda/round 设计。不能继续保留未定义的 offspring round。

### F2 — BLOCKER：proposal attempt 预算伪代码与定义矛盾

**位置：** R1 §3.1–3.4。

§3.1 明确规定初始化候选也属于 proposal attempt；但 §3.4 伪代码对 12 个 initial genomes 只调用 attempt_and_atomically_evaluate_if_unique()，没有初始化 attempts=0，也没有对每个 initial proposal 执行 attempts += 1。

因此当前 384 cap 的真实口径不唯一。

R2 必须：

1. 显式初始化 attempts=0；
2. 每个 initial genome proposal 都计 1 次；
3. 每次 offspring/random proposal 都计 1 次，包括重复 genome 和 cache hit；
4. 明确计数是每个 arm×seed 独立，不能跨臂共用 attempt counter；
5. 明确 384 cap 包含初始化的 12 次，或明确修订定义为仅 offspring attempts；二者只能选一；
6. 给出可执行的预算伪代码，并添加静态算术断言。

### F3 — BLOCKER：当前 NSGA-III niching 不能直接称为 canonical NSGA-III

**位置：** R1 §7.3。

R1 已写 ideal point、extreme points、normalization、reference directions、association 和 niche count，但 niching 规则尚不足以称为完整 canonical NSGA-III：

- canonical NSGA-III 在选择 niche count 最小的参考方向后，通常在 niche count 为 0 时选关联距离最小的候选；niche count 大于 0 时采用随机选择。R1 当前描述只给出关联距离/hash 的确定性排序，没有定义这一条件分支。
- ASF 只写了轴向权重，没有给出完整 ASF 计算公式。
- normalization fallback 在极端点矩阵奇异后使用当前池最大值；如果某一目标在当前池仍为零跨度，分母仍可能为 0。
- 参考方向以 index 参与 tie-break，但没有冻结 35 个方向的唯一枚举顺序。
- 需要明确 niching 只从最后一个未完整填入的 front 选取，还是从其他集合选取。

R2 必须二选一：

**方案 A：** 完整定义 canonical NSGA-III，包括 ASF 公式、零跨度处理、方向枚举顺序、最后 front association，以及 niche count 为 0 / 大于 0 时的选择规则；随机 niching 使用独立 selection_niching RNG stream。

**方案 B：** 保留确定性 niching，但明确命名为一个 NSGA-III deterministic niching variant，不得称为 canonical NSGA-III；同时解释为何该变体仍可承担 A2 的比较职责。

不得只在报告中写“完整 NSGA-III”而让实现者自行决定。

### F4 — BLOCKER：硬约束把合法环境回执误标为非法状态转移

**位置：** R1 §8.1–8.2。

已核对真实环境 experiments/pilot_a3b/dependency_recovery.py：

- step() 接受格式正确、tool ID 和 route name 存在的 COMPENSATE 动作；
- 当补偿合同不存在时，_compensate() 返回 CONTRACT_BLOCKED；
- 当 route 的依赖尚未 COMPENSATED 时，_compensate() 返回 DEPENDENCY_BLOCKED；
- 这两个结果是环境对合法动作请求的拒绝回执，没有发生非法状态转移；
- INVALID_ACTION 才表示动作格式/动作类型/工具/route 不合法。

因此当前把 DEPENDENCY_BLOCKED、CONTRACT_BLOCKED 直接计入 illegal_transition_count，语义不准确。它们可以被定义为“blocked compensation attempt”并进一步决定是否属于硬约束，但不能在没有说明的情况下称为非法状态转移。

另外，unauthorized_action_count 仍只用“超出当前公开动作许可”描述，没有精确的动作集合和 precondition，也没有说明与 INVALID_ACTION 是否重叠。§10 所说“六类硬约束计数”与 §8.1 列出的五类字段也不一致。

R2 必须把以下概念分开并定义是否属于 hard gate：

- invalid action；
- unauthorized action；
- blocked compensation attempt（contract blocked）；
- blocked compensation attempt（dependency blocked）；
- actual illegal state transition；
- pending；
- duplicate compensation；
- runtime forced abort。

必须定义每项的事件来源、计数单位、重叠规则、可观测判据和 hard/soft 属性。若将 blocked attempts 设为硬约束，必须明确这是额外的策略安全约束，而不是环境状态转移违规。

### F5 — BLOCKER：反馈特征的来源限制与实际 evaluator 依赖不一致

**位置：** R1 §6.1–6.2。

R1 规定反馈不能读取 scenario labels、hidden outcome schedule 或 gold classification；但：

- e_t 使用 class_success；
- h_t 使用 avoidable_harm；
- 真实 DependencyRecoveryEnv.report() 先调用 classify_scenario(self.scenario) 得到 label 和 minimum，再计算 class_success 与 avoidable_harm；
- classify_scenario 会利用 scenario 中的 route outcomes 计算可达性下界。

这不必然构成数据泄漏：如果它们仅作为完整 Train rollout 后的公开 evaluator reward/fitness 输出，优化器可以使用已完成评价结果。但 R1 不能同时声称这些特征与 label/hidden outcome 无关。

R2 必须明确选择：

1. 允许使用完整 Train episode 后的公开 evaluator reward/fitness aggregates（包括 label-conditioned 的 class_success、avoidable_harm），但禁止在 rollout 前读取 label、原始 route outcome schedule、真实 delay 和任何隐藏场景字段；或
2. 若坚持反馈完全不使用 label-derived evaluator outputs，则重定义 e_t、h_t 为只依赖 policy 可见轨迹的特征。

同时将“过早终止率”改成准确的指标名称，例如“未成功 escalation rate”，因为当前公式统计的是所有 class_success=0 的 escalation，不一定都属于时间意义上的过早终止。

### F6 — BLOCKER：phenotype hash 与 probe rollout 预算没有完全定义

**位置：** R1 §5.3–5.4、§9.4、§10–11。

R1 定义了 genome canonical serialization，但没有定义 trace phenotype、outcome signature、joint phenotype 的 canonical serialization。仅写“保存 hash”不足以保证不同实现得到相同 phenotype。

必须冻结：

- trace 中纳入 hash 的字段及其排序；
- scenario ID 的排序；
- action/observation/tick/cost 的编码；
- outcome signature 的字段集合；
- None、布尔、整数和浮点的规范化；
- trace/outcome/joint hash 的精确 JSON 或二进制格式。

此外，probe panel 使用全部 96 个 Train scenarios，而这些场景也用于 96-genome search。probe 行为差异测试需要真实执行策略/环境，不是纯文档静态检查。R2 必须明确：

- 每个位点要执行哪些 typed genome contrasts；
- 每个 contrast 执行哪些 scenario IDs；
- 总 probe episodes/rollouts 的精确数量；
- probe rollout 与正式 96×96 search budget 分开记账；
- probe 只验证分支可辨识性，不得按 probe performance 选参数、改规则或挑候选；
- probe 结果不作为独立 Validation 或性能提升证据。

### F7 — BLOCKER：无效 seed 和 NO_FEASIBLE_CANDIDATE 的统计处理不完整

**位置：** R1 §3.3、§9.2–9.5。

R1 要求 5 seeds 完整报告，并要求至少 4/5 seeds 同向；但没有明确当某个 arm×seed：

- 达到 384 attempts 仍不足 96 unique evaluations；
- episode 中断；
- 无可行候选；
- phenotype collapse；
- hash/log invalid；

时，整个配对比较和 4/5 规则如何处理。

R2 必须明确：不得静默剔除无效 seed，不得替换 seed，不得只用剩余 4 个 seed 计算“4/5”；建议将任何主要比较中的无效配对 seed 计为该比较 INCOMPLETE / NO_CLAIM，除非预注册一个完全独立、不可挑选的基础设施故障重跑规则。五个 seeds 全部有效后才能计算主要比较的五 seed 均值和 4/5 同向条件。

---

## 4. 重要但可在同一轮解决的设计问题

### M1 — A1 与 A4 理论上应是同一条算法轨迹

A1 使用 NSGA-II + 固定均匀 block probabilities；A4 使用 A3 的相同 NSGA-II 骨架，且 phi(0)=0 后也产生均匀概率。二者使用相同初始化、variation、selection，RNG seed 派生公式又不包含 arm ID。

因此在相同 seed 和相同随机流消费序列下，A1 与 A4 理论上应逐 proposal、逐 survivor、逐评价完全相同。

R2 应增加 A1/A4 的 per-seed trajectory equivalence check。若两臂不相同，必须解释其唯一差异；否则 A3−A1 与 A3−A4 实质上是同一个对照，不应包装成两份独立证据。A3−A4 是反馈机制最直接的消融对照。

### M2 — 当前 typed genome 的搜索空间只有 144 个组合

按五个字段的取值数：

[
3	imes2	imes2	imes4	imes3=144.
]

96 个 unique evaluations 覆盖整个离散空间的 96/144=66.7%。完整 Train-only enumeration 只需要 144 个 genome evaluations，比当前单臂预算多 50%。

这不自动否定 D-092，但会影响“为什么需要演化计算”的研究论证。R2 必须：

- 明确报告搜索空间总基数和预算覆盖比例；
- 解释为什么 96-evaluation 预算足以区分算法；
- 考虑加入一次单独标记的 Train-only exhaustive oracle（144 个 genome，不作为竞争算法、不参与调参），用于报告各方法相对已知 Train 最优值的 search gap；或者提出扩大 genome 的方案，但每个新增位点必须先通过独立行为可辨识测试。

不能仅凭 5 个臂的差异声称演化算法具有不可替代性。

### M3 — Python / numerical runtime lock 需要精确到可复现版本

R1 只写 Python 3.11、NumPy 1.26.4。实现前还应冻结 Python 精确 patch 版本、OS/architecture、NumPy wheel/lock、依赖完整清单和数值容差。该项可以与实现阶段锁一起完成，但 R2 必须明确其责任和门禁。

### M4 — 账本字段数量与 phenotype gate 需要统一

§8.1 定义五类硬约束计数，而 §10 称“六类硬约束计数”。R2 应统一字段清单。还应将每个 phenotype hash 的 canonical schema 纳入账本版本。

---

## 5. B1–B8 审查矩阵

| 项目 | R1 审查结论 | 原因 |
|---|---|---|
| B1 数据/环境哈希 | PASS（既有依赖） | 13 份源码 canonical SHA/Git blob、manifest 与 96-ID probe hash 全部匹配；新实现锁待后续 |
| B2 真实预算 | REQUEST CHANGES | 算术正确，但 initial proposal 未计入伪代码 attempts |
| B3 五臂/算法身份 | REQUEST CHANGES | 父代选择、population/offspring rounds、A0 分布未定义 |
| B4 typed genome | PARTIAL | 旧字段映射基本相容；行为 probe 未运行，phenotype hash schema 缺失 |
| B5 动态反馈 | PARTIAL | 矩阵/参数/零反馈正确；round 未定义，label-derived reward 来源限制矛盾 |
| B6 NSGA-II/III/RNG | REQUEST CHANGES | NSGA-III niching 和 normalization fallback 不足以称为 canonical |
| B7 硬约束/选择 | REQUEST CHANGES | blocked receipts 被误称 illegal transition；unauthorized action 未操作化 |
| B8 统计/停止 | REQUEST CHANGES | 无效 seed/无可行候选的配对统计处理未冻结 |

因此不能将 B1–B8 全部记为 SPEC_CLOSED。

---

## 6. 下一轮唯一任务：D-092 R2 修订

**唯一任务：** 将当前 R1 先原样保存为 103_D092_TRAIN_ONLY_PREREGISTRATION_R1.md，然后将 canonical 103_D092_TRAIN_ONLY_PREREGISTRATION.md 修订为 R2，逐项关闭 F1–F7，并解决 M1–M4。

优先顺序：

1. 先定义 mu/lambda/round、父代抽样、A0 随机分布和 A3 feedback round；没有它们就没有可执行算法。
2. 修正 384 proposal-attempt 计数伪代码。
3. 将 NSGA-III 规范化为真正 canonical 算法，或明确标记为 deterministic variant。
4. 修正 hard constraint 语义与 unauthorized action 定义。
5. 明确 feedback 允许使用的 post-rollout reward 边界。
6. 定义 phenotype hash、probe contrasts 和 probe rollout ledger。
7. 冻结 invalid seed、NO_FEASIBLE 和主要比较的 no-claim 规则。
8. 明确 144-genome 搜索空间的研究意义，决定是否加 Train-only exhaustive oracle。

完成 R2 后只交新的独立会话复审。不得由修订者自行批准。

---

## 7. 授权与禁止事项

本次独立审查只授权 R2 文档设计修订。

**仍然禁止：**

- 实现 D-092 搜索器或 typed adapter；
- 运行 phenotype probe rollouts（必须先由 R2 明确授权和预算）；
- 运行 genome search、调参或候选冻结；
- 访问 Validation/Test；
- 启动 Pilot B、正式 A-3b；
- 真实 LLM/API、A800/ARWM；
- UndoBench TEST、ThinkingBox；
- 修改或合并 main；
- 混用其他仓库。

R2 独立审查通过后，仍须单独获得实现授权；实现完成后再做实现一致性复审；只有用户明确批准最终执行锁后，才可启动 D-092 Train-only。

**最终结论：R1 的资料绑定与哈希核验可信，算法设计尚未闭合。REQUEST_CHANGES / HOLD。**
