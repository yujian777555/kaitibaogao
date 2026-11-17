# 104 — D-092 Train-only 预注册独立审查

**日期：** 2026-11-17  
**仓库：** `yujian777555/kaitibaogao`  
**分支：** `pilot-a-stateful-recovery`  
**审查对象：** `102_D091_INDEPENDENT_AUDIT_RESULT.md`、`103_D092_TRAIN_ONLY_PREREGISTRATION.md`、`101_D091_EXECUTOR_PROMPT.md`、`experiments/d090_recovery/results/d091_audit/`、相关 D-090/D-091 源码与专项测试  
**D-091 审查结论：** `ACCEPTED_WITH_LIMITATIONS`（审计证据与主要结论相互一致；本轮未进行 clean-clone 全量重跑）  
**D-092 审查结论：** `REQUEST_CHANGES / HOLD`；不批准 D-092 搜索代码实现、预注册冻结或实验运行  
**D-092 状态：** `PROPOSED / NOT FROZEN / NOT RUN`

---

## 1. 接管与远端状态核验

| 项目 | 核验值 |
|---|---|
| 工作分支远端 HEAD | `ae920581a6da9d974ad8bd2d06cfd1ec6b07aabc` |
| main HEAD | `683b3fe7fc52c86e917d523fdc6bbb13abbfd653` |
| ahead / behind | 306 / 0 |
| 最近一次已完成 D-091 CI | `44068259009`，success |
| 该 CI 的 head SHA | `5cde039c73b0a5d83fd6d0d7b3816e20f22f0f9b` |
| 当前 HEAD 与该 CI head 的差异 | 1 个后续文档提交；compare 显示仅 6 个文档各 1 行增删，没有实验代码变化 |
| 本地工作树 | 当前连接只能读取 GitHub 远端，不能检查执行者本地 `git status`；此项未核验 |

本轮没有修改 main、没有合并分支，也没有读取或混用其他项目仓库。

## 2. D-091 独立审查

### 2.1 原始数据与指标

复核 102 号报告、审计器、测试和已下载 artifact 后，主要数据结论一致：

- 三份 D-090 原始 JSON（manifest、search report、fixed ablation）均能通过 Git blob / 内部 SHA 检查；101 号中的一个 source blob 登记转写错误已被单独记录。
- Train manifest 为 6 families × 4 strata × 4 repeats，共 96 个唯一场景；R1/R2/R3/R4 各 24，namespace 为 `d090r|train|`。
- 15 个 search best candidates 共 1,440 条已保存逐场景 rows；5 组固定消融共 480 条 rows。
- 独立复算的最大指标差异为 0；CondRec、R3、R4、Harm、Recovery Cost 和约束计数均与保存的 best summaries / ablation summaries 一致。
- 这些复算只覆盖已保存的 15 个 best candidates 和 5 组固定消融，不能等同于复算 1,440 次 genome evaluation 的全部 rollout 轨迹。proposal、cache、archive、真实 generation 与算子调用历史仍为 `NOT_AUDITABLE_FROM_SAVED_TRACE`。

### 2.2 算法身份

源码 `d090_experiment.py::run_method()` 支持报告中的核心发现：

- `random` 没有独立随机搜索分支；它与 `nsga2` 使用相同 RNG 初始化、初始种群、mutation/crossover 路径和 `nsga2_select`。三个 paired seeds 的 best genome 也一致。因此 D-090 的 `random` 标签不能作为独立 Random Search 基线。
- `state_evo` 传给 mutation 的是固定 profile，不读取上一轮失败统计、pending 轨迹或状态条件动态更新变异概率。它是静态 profile 的 NSGA-II 路径，不是动态反馈演化。
- `state_random` 才是规则基因空间直接随机采样，但它没有与演化臂配对的相同初始种群。
- `GENERATIONS=6` 只进入报告元数据，循环由 `evals < BUDGET` 控制。保存产物没有 proposal/generation/cache/operator 级历史，不能反推真实代数。
- NSGA-II 使用非支配排序和 crowding distance；D-090 调用的 NSGA-III 是简化实现（ideal-point shift、参考方向关联与 niching），缺少完整极端点/归一化流程。
- survivor 使用六维目标，而 `_best()` 在完整 archive 上使用不显式包含 CondRec 的字典序 key。它不是从最终 population/Pareto front 直接选取，选择口径与 survivor 目标不一致。

### 2.3 Genome / phenotype

审计 artifact 中 15 个保存 best candidates 的指纹结果为：

- 8 个不同 canonical genomes；
- 8 个规范化规则签名 / 规则块签名；
- 96 个 Train 场景上只有 1 个 trace phenotype 和 1 个 outcome signature；
- 105/105 个候选对的 trace/outcome/联合 phenotype 相同。

该结论仅适用于当前 96 个 Train 场景与 15 个已保存 best candidates，不代表全部已评价 genome 或所有可能环境全局等价。

**复核限制：** 审计器返回的 `observed_behavior_changing_loci=[]` 是代码中直接写入的常量，而不是逐位点干预实验。105/105 phenotype 等价由候选指纹矩阵支持；但不能把它解释成每个变化位点在因果意义上均无效。D-092 必须用预先冻结的 probe panel 和逐机制语义测试识别有效位点，不能依赖这个常量字段。

### 2.4 g03-r2 可达性

- D-091 的 23-step witness 使用 `make_scenario("d090_PAIR_RACE", "D3_DEPENDENT_ABORT", 2)`，并先与已保存 manifest 场景逐字段比对。
- witness 在真实 `DependencyRecoveryEnv.step()` 中成功：R3 class_success=1、正确升级=1、residual=0、pending=0、duplicate=0、constraint=0。
- BFS artifact 找到 21-step 安全路径：R3 成功、零残余、零 pending、零 duplicate、零硬约束违规。因此旧 25-step 下界被推翻，最短决策数报告为 21。
- BFS 状态包含工具状态、路线 attempt index、pending success、剩余 resolve time、terminal action 和 duplicate count；对 permission fault，`RETRY_WORKFLOW` 不改变状态；无 pending 的 VERIFY 不改变后续状态；WAIT 仅在有 pending 时可能推进有用的延迟状态。这些剪枝与环境转移语义相符。

**测试加固建议：** 当前 `test_r2_bfs_finds_and_proves_shortest_path` 只断言 `decision_count <= 23`，没有把 21 精确锁为回归预期。建议下一次只读审计维护时增加精确 21-step 断言，并单独验证 BFS 输出路径在真实环境回放成功。该测试缺口不推翻当前 21-step artifact，但应避免未来无意改变搜索空间或状态压缩后仍报告相同最短值。

### 2.5 消融安全轨迹

P1/P2/P3/P4 的主要结论与逐行摘要一致：

- P1：17 条 class failures（R2=8、R3=7、R4=2）；g03 局部 R3 失败减少，但总 Harm 从 26 增至 46。不能把局部改善写成整体有效。
- P2：Multi-Route r1/r3 各有 pending=2，合计 4；硬约束违规，不得成为候选。
- P3：g03 Pair-Race 的 4 个 R3 repeats 仍失败；停止门控不能创造新路线或解除互依环。
- P4：Deep-Chain r1/r2 各遗留 pending=1，合计 2；Harm/Cost 改善不能抵消硬约束违规。

### 2.6 最新 CI artifact 复核

本轮从 CI `44068259009` 下载 D-091 artifact：

| 项目 | 值 |
|---|---|
| Artifact name | `d091-independent-audit-evidence` |
| Artifact ID | `14321023302` |
| ZIP 大小 | 109,605 bytes |
| GitHub digest | `sha256:925f1f5cc14f1b8c3d0678e2b03d67c891f6d13996b3def928ac182cf17aee03` |
| 下载后 ZIP SHA-256 | 与 GitHub digest 一致 |
| 内部输出 | 12 个由 output manifest 登记的结果文件，逐文件字节数和 SHA-256 全部匹配 |
| 到期时间 | `2027-02-15T10:48:46Z` |

CI regression job 中 `Audit saved D-090 evidence without genome search` 和 `Upload D-091 independent audit evidence` 均为 success。102 号报告引用的 run `44067543678` / artifact `14320134130` 是较早的有效执行；本轮发现的 run 44068259009 是更新的重复验证，后续维护文档应同时保留历史与最新记录，不能把两次 artifact digest 混写。

**D-091 结论：** 审计报告和 artifact 在核心数据、算法身份、候选行为等价、r2 witness/BFS 与消融安全结论上相互一致。D-091 仍应保持 `D091_PARTIAL / HOLD`，因为完整搜索过程无法从 best-only 保存账本复原；这不是审计器未运行，而是原实验没有保存足以审计搜索全过程的证据。

---

## 3. D-092 预注册审查：REQUEST_CHANGES / HOLD

103 号方案的问题不在于研究问题不值得做，而在于目前尚不能形成唯一、可执行、可复核的预注册。以下阻断项关闭前，不批准 D-092 搜索实现或实验运行。

### B1. 锁定数据、环境与评估器

103 号没有将 D-090 Train manifest、环境源码、策略 evaluator 和 genome schema 全部绑定到不可变版本。必须写入 manifest Git blob / 内部 SHA、环境文件 SHA、策略/evaluator SHA 和协议版本；执行时发现任何不一致即 INVALID。只允许该固定 Train split，不生成或读取 Validation/Test。

### B2. 明确预算的计量单位

当前方案同时写 96 proposal slots、96 unique genome evaluation 上限、重复 proposal 占槽但 cache 不增加 rollout。这意味着不同方法可能有相同 proposal 数，却有不同真实 simulator rollout 数，不能直接称为“相同真实评价预算”。

必须二选一并写清：

1. **固定真实 rollout 预算（推荐用于算法效能主比较）：** 每臂目标为相同数量的 unique genome evaluations × 96 场景；另设有限 proposal-attempt cap，重复 proposal 计入 proposal ledger，不增加 rollout；若某臂未在上限内达到目标，标记 INVALID，不追加预算挽救。
2. **固定 proposal 预算：** 保留 96 proposal slots，但将其称为相同 proposal budget；实际 unique evaluations / simulator rollouts 作为独立资源结果报告，不得宣称真实 rollout 预算相等。

按 103 号上限计算，96 个 unique genomes × 96 场景 = 9,216 episodes/run；5 methods × 5 seeds 的理论上限为 230,400 episodes。协议应报告实际值、缓存节省与无效 run，不得把上限写成已执行数量。

### B3. 预注册主要比较和判据

必须明确：
- NSGA-II vs Random：检验演化选择本身是否有贡献；
- Feedback Evolution vs Feedback Evolution / No Feedback：检验动态反馈是否有增量贡献；
- Feedback Evolution vs NSGA-II：检验反馈机制是否超越标准 EA；
- NSGA-III vs NSGA-II：作为多目标环境选择的独立次要比较。

需要冻结主要终点、次要终点、指标方向、实际意义阈值、跨 seed 稳定性规则和停止判据。五个 seeds 的 Train-only 结果只能作为探索性描述，不能写成确认性显著性或跨 family 泛化证明。若反馈臂只优于 Random 而不优于 NSGA-II，不得宣称反馈机制提升了演化计算。

### B4. 重新定义可辨识 genome 与 probe panel

D-090 的规则字段存在条件冗余，例如：
- `pair_rule` 的部分取值在当前策略分支中等价，且 `pair_rule==1` 会使 pair-race alternate 判断路径失效；
- `exhaustive_fallback` 为 true 时，`fallback_mode` 的部分差异不再起作用；
- `harm_first_ordering` 会门控 `harm_order_mode`，其中部分 mode 取值执行相同排序；
- `completion_gate` 与 `completion_mode` 存在重叠门控。

D-092 必须先给出完整 typed genome schema、每个位点的语义、有效条件、默认值、允许值、变异/交叉/repair 规则和 canonical serialization。冻结 probe panel 的 scenario IDs / SHA、每个位点预期触发的决策分支与行为差异测试。probe panel 不得在观察搜索结果后选择。若 probe panel 上仍无法产生预先要求的行为差异，HOLD，不启动搜索。

### B5. 完整定义动态反馈

103 号的 softmax 公式只有形式，`phi_k(F_g)`、`beta_k`、`tau` 和具体特征映射仍为 OPEN。必须冻结：

- failure features 的逐项定义、分子/分母和归一化；
- 每个 operator block 与每个 failure feature 的映射矩阵；
- 每个 block 的 beta 系数、温度、概率上下限、平滑/数值稳定处理；
- 每轮反馈使用的样本集合（建议只统计上一轮完成的 unique genome evaluations，不能因重复 proposal/cache hit 重复加权）；
- 更新时点、第一轮初始化、随机数流和概率日志；
- 失败反馈只来源于已完成 Train rollout 的公开 evaluator 输出，不读取隐藏故障 schedule、未来 outcome、Validation/Test 或金标准标签。

`feedback_evo/no_feedback` 必须与反馈臂保持相同编码、初始池、交叉/变异结构、选择和预算，唯一差别是反馈向量固定为零。该方法应称为“failure-feedback operator adaptation”，不要把优化器层面的变异概率更新混称为 Agent policy 的 state-conditioned behavior。

### B6. 规范 NSGA-II / NSGA-III 和 RNG

- NSGA-II：固定非支配排序、crowding distance、边界/并列处理、重复候选处理和确定性 tie-break。
- NSGA-III：固定 reference implementation / package version / commit，或完整写出 ideal point、extreme points、normalization、reference directions、association、niche count、niching 与 tie-break；补充标准测试用例。
- 各方法必须用独立命名 RNG streams（init、random proposal、variation、selection/niching），记录 stream ID、seed 和消费计数，避免 NSGA-III 的额外随机消费改变后续变异随机序列。
- 增加方法分派测试：Random 不得调用 survivor selection；NSGA-II 必须调用 NDS+crowding；NSGA-III 必须调用完整 niching；feedback/no-feedback 必须只在反馈向量上不同。

### B7. 安全约束与多目标选择

硬约束应作为不可补偿的 feasibility gate，而不是允许被 Harm/Cost 抵消的普通目标。需要冻结每种违规的定义与计数方式（pending、duplicate compensation、unauthorized action、非法状态转移、运行时强制中止等），并规定：

- feasible candidate 必须满足全部硬约束；
- infeasible candidates 如何按 violation count / severity 排序以继续搜索；
- 若最终无 feasible candidate，run 输出 `NO_FEASIBLE_CANDIDATE`，不能挑一个低 Harm 的违规候选；
- Pareto 目标与硬约束分离，避免在 feasibility filter 后再把恒为零的 constraint count 当作有效性能目标。

最终候选排序必须冻结完整方向和顺序，例如 R3/R4/CondRec 最大化、Harm/Cost 最小化、最后以 canonical fingerprint 稳定打破并列。具体优先顺序、精度、NaN/None 处理和从全部 archive 还是 Pareto set 选择，必须在实验前唯一确定。

### B8. 统计、资源和退出规则

五个 seeds 可以保留为 Train-only exploratory runs，但必须报告每 seed、每方法完整结果和失败 run；不做确认性 p-value 主张。冻结：
- 主要对照的效应方向和最小实际意义阈值；
- 零硬约束违规门；
- 结果是否需要至少 4/5 seeds 同方向；
- phenotype diversity 最低要求；
- proposal / unique evaluation / rollout / cache 的实际账本；
- 若出现 phenotype collapse、方法分派错配、预算差异或日志缺失时的 INVALID/HOLD 规则。

---

## 4. 建议的 D-092 R1 交付顺序

1. 修订 103 为 R1：关闭 B1–B8，绑定数据/代码 SHA，写出唯一的主要比较、预算单位和停止规则。
2. 先独立审查 R1 文档与公式；未通过前不写搜索器。
3. 通过后，才允许实现：typed genome、probe panel、canonical NSGA-II/III、Random Search、feedback/no-feedback、RNG stream manager、proposal/evaluation ledger 和硬约束比较器。
4. 只运行单元测试、合成语义测试与方法身份测试；不得先启动完整 genome search。
5. 再由独立审查确认实现与冻结协议逐项一致。
6. 用户明确批准后，才可运行一次 D-092 Train-only 实验。
7. D-092 Train-only 通过也只支持是否申请独立 Validation 的判断，不自动授权 Validation/Test、Pilot B、正式 A-3b 或真实 LLM/API。

## 5. 最终决策与唯一下一任务

| 项目 | 决策 |
|---|---|
| D-091 数据/指标审计 | ACCEPTED_WITH_LIMITATIONS |
| D-091 搜索过程审计 | NOT_AUDITABLE_FROM_SAVED_TRACE |
| D-090 五方法公平比较 | FAIL |
| D-090 15 个候选行为多样性 | FAIL（当前保存集合 8 genome → 1 phenotype） |
| D-090 r2 25-step 下界 | CLAIM_FALSIFIED；当前最短 21 |
| D-090 固定消融候选资格 | P2/P4 因硬约束违规拒绝；P1 整体退化；P3 无 g03 修复证据 |
| D-092 设计 | REQUEST_CHANGES / HOLD |
| D-092 实现/搜索/冻结 | NOT APPROVED |
| Validation / Test / Pilot B / A800 / 真实 API | HOLD |

**下一会话唯一任务：** 将 `103_D092_TRAIN_ONLY_PREREGISTRATION.md` 修订为 R1，逐项关闭本报告 B1–B8；只做设计、公式、预算和静态测试规格，不实现或运行 D-092 搜索。R1 完成后再交独立会话复审，并等待用户明确批准。

---

## 6. 仓库与授权边界

- 唯一仓库：`yujian777555/kaitibaogao`；唯一分支：`pilot-a-stateful-recovery`。
- main 保持 `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，不得修改或合并。
- 不得重跑 D-090，不得产生新 genome search、调参或候选冻结。
- 不得访问 Validation/Test，不得启动 Pilot B、正式 A-3b、UndoBench TEST、ThinkingBox。
- 不得启动真实 LLM/API、A800/ARWM 训练。
- 本轮只提交独立审查与交接文档；没有授权新的搜索、实现或实验。
