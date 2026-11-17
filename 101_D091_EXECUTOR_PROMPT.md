# 101 — D-091 执行 Agent 完整提示词

> **执行方式：** 将本文件全文交给执行 Agent。它是 D-091 的权威执行提示词；不得把它简化成普通代码清理任务。
> **唯一仓库：** `yujian777555/kaitibaogao`。
> **唯一工作分支：** `pilot-a-stateful-recovery`。
> **当前阶段：** D-091 只读证据审计与可辨识性检查；Train-only；不做新搜索、不冻结候选、不申请 Validation。

## A. 你的身份与首要任务

你是本项目的研究执行 Agent，必须同时承担实验审计员、算法实现审计员和仓库维护者职责。你不是论文写作者，不要先写论文，不要用更新文档替代研究工作。

本轮唯一任务是：**独立审计 D-090 的原始数据、搜索实现、候选行为多样性、g03-r2 可达性下界，以及 P1/P2/P4 的安全轨迹。**

先读取：

1. `99_D090_PAIR_RACE_RULE_SEARCH.md`
2. `100_D091_D090_EVIDENCE_AUDIT_AND_SEARCH_IDENTIFIABILITY.md`
3. 本文件 `101_D091_EXECUTOR_PROMPT.md`
4. `experiments/d090_recovery/d090_experiment.py`
5. `experiments/d090_recovery/d090_genome.py`
6. `experiments/d090_recovery/d090_policies.py`
7. `experiments/d090_recovery/d090_scenarios.py`
8. `experiments/pilot_a3b/dependency_recovery.py`
9. D-089 selector 来源 `experiments/d089_recovery/d089_search_experiment.py`

不要从 README 的摘要代替原始报告、源码和 JSON 账本。

## B. 接管、Git 和仓库边界

1. 确认当前仓库确实是 `yujian777555/kaitibaogao`，分支确实是 `pilot-a-stateful-recovery`。
2. 先 `git status --short --branch`、`git rev-parse HEAD`、`git ls-remote origin refs/heads/pilot-a-stateful-recovery`、`git ls-remote origin refs/heads/main`；记录起始 SHA、远端 SHA、main SHA、ahead/behind 和工作树状态。
3. 当前已知文档接管提交为 `4e511b93fadb71ebab4b38f7dcbdf986b695d1a8`，main 已知为 `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。如果远端已有更新，以实际远端为准并说明差异，不得强制 reset。
4. 不得把其他仓库的实验、代码、结论或分支混入本项目。不得写入 `main`，不得合并，不得创建另一个项目分支替代指定分支。
5. 不覆盖、不改写、不删除 D-090 原始 manifest、report、ablation JSON、原始 rows、旧 audit 脚本或历史报告。所有修复、新审计器和新结果用 D-091 新文件命名。
6. 每次写入前检查工作树；若存在用户未提交改动，先停下并报告，不得覆盖。

## C. D-090 冻结事实与证据指纹

### C1. D-090 原始配置

- 实验报告：`99_D090_PAIR_RACE_RULE_SEARCH.md`。
- D-090 实验提交：`1af9bc832058dd1328862dbba3da3ef248e4edd3`。
- `d090_experiment.py` blob SHA：`16457f67969a8e0016fe4a531fe07acf771adacc`。
- `d090_genome.py` blob SHA：`52a7e808e3c1fff89d55215ce256eb57c8ae5fd3`。
- `d090_policies.py` blob SHA：`c96beaf6577cf989e6baaa4d22065662b269844`。
- `d090_scenarios.py` blob SHA：`962ade0f8f7bb2eb849b852f0a67edcf08d75712`。
- `d090_train_manifest.json` Git blob SHA：`b917b4c624601022e8d8896182dfaed71ba0d21c`；内部 manifest SHA-256：`7d677fe075a5bac6b4241be6c4f38e0c55022b6059729e9a05c7cdf7d633350d`。
- `d090_train_report.json` Git blob SHA：`bc7a10750b9501462ae9cfe70a171a268f910fcc`；内部 report SHA-256：`99a0660e81b072de2e596ff589356d3bb978318f4005d057966779ba9f8f38cf`。
- `d090_mechanism_ablation.json` Git blob SHA：`6503132319b2bbbb8d1c8fe720c68b6c37432604`。
- D-090 固定消融报告声明的原始报告 SHA-256：`e9412e8c76ce99c6a2b83a51dbb0e89d090d3e9ac838824d5e8d427c0a1be720`；固定消融 SHA-256：`632b82eb57df91e5618055aadac01b918ebbc69d170ef77882a40a7969da3ce2`。
- 场景 manifest：6 families × 4 strata × 4 repeats = 96 场景；R1/R2/R3/R4 各 24；命名空间 `d090r|train|`；Train-only。
- 搜索 seeds：711、822、933；五个方法：`random`、`nsga2`、`nsga3`、`state_evo`、`state_random`；每个 run 报告 96 unique genome evaluations。
- `POP=12`、`GENERATIONS=6`、`BUDGET=96`、每 episode 24 决策。

### C2. 固定机制消融

| 变体 | R3 | R4 | Harm | ConstraintViolation | Pending |
|---|---:|---:|---:|---:|---:|
| Legacy B3 | 0.500 | 1.000 | 0.271 | 0 | 0 |
| P1 Pair-Race | 0.708 | 0.917 | 0.479 | 0 | 0 |
| P2 Exhaustive-Fallback | 0.667 | 1.000 | 0.146 | 2 | 4 |
| P3 Completion-Gate | 0.583 | 1.000 | 0.229 | 0 | 0 |
| P4 Harm-Ordering | 0.417 | 1.000 | 0.313 | 2 | 2 |

P1 的 g03 局部改善不能掩盖其 R2/R3/R4 整体失败与 Harm 上升。P2/P4 的硬约束违规必须作为不可接受结果处理，不能用 Harm 改善抵消。

### C3. 搜索结果摘要

五个方法的保存结果均为 R3=0.875、R4=1.000、Harm=0.0416666667、硬约束违规=0、pending=0、recovery_cost=12.9583333333。该结果是 Train-only 探索结果，不是演化算法优势证据。

## D. 已经从源码和原始 JSON 发现的高优先级审计问题

以下是本轮接管时的初步静态审计发现。你必须在本地 clean checkout 中独立复现，不能只复制本段结论；也不能忽略这些发现。

### D1. `random` 方法没有真正的 Random Search 分支

`d090_experiment.py::run_method()` 只有 `if method == "state_random"` 的纯随机采样分支。`method == "random"` 会进入 `else` 演化分支。

在当前实现中，`random` 和 `nsga2` 对同一 seed：
- 使用相同的 `rng = Random(seed * 7919 + 17)`；
- 使用相同的初始种群构造方式；
- `method == "state_evo"` 对两者都为 False，因此走相同的变异/交叉代码；
- `method == "nsga3"` 对两者都为 False，因此两者都调用 `nsga2_select`。

已保存的 report 也显示三个 seeds 下 `random` 与 `nsga2` 的 best genome 完全相同。因此，当前标注为 Random Search 的对照臂实际上与 NSGA-II 共享同一搜索实现，不能作为独立随机搜索基线。

要求：精确指出分支、调用链、随机数状态和输出证据；新增一个不启动完整实验的单元测试或 AST/dispatch 审计，防止方法标签与实际实现错配。不得直接重跑 D-090 搜索来证明。

### D2. `state_evo` 不是动态状态反馈搜索

`state_evo` 调用 `mutate_d090(..., {"pair":1.0,"fallback":1.0,"completion":1.0,"harm":1.0})`，这是每次调用都相同的常量 mutation profile。它没有读取最近 episode 的失败反馈、pending 轨迹、状态条件或 `failure_profile` 来动态更新变异概率。

`state_random` 是在规则基因取值空间上直接随机采样；它不执行演化选择。

要求：准确描述这两个方法实际做了什么；区分“基因编码了状态规则”和“搜索过程依据状态/失败反馈自适应”这两个不同概念。不得继续把静态加权 mutation 直接称为已验证的状态反馈进化。

### D3. `GENERATIONS=6` 目前只是报告元数据

`run_method()` 的演化循环由 `while evals < BUDGET` 控制，没有使用 `GENERATIONS` 作为终止条件。需要从实际循环、proposal 数、unique evaluation 数、cache hit 数和环境选择次数重建真实代数/迭代轮数。

要求：核对报告声称的 6 generations 与实际运行过程是否一致。若没有保存 generation-level 日志，明确标记不可从现存产物复原，不得猜测。

### D4. 15 个 best candidates 在 D-090 Train 上完全行为等价

已对远端保存的 `d090_train_report.json` 做过一次独立解析：
- 15 个 run（5 methods × 3 seeds）；
- 15 个 best genomes 中只有 8 个不同 genome；
- 15 个候选的 96 场景 trace bundle 完全相同；
- 所有 105 个候选两两比较的 trace bundle 都相同；
- 其余保存的逐场景结果字段（包括 class_success、R3/R4 outcome、harm、decision_count、constraint、pending、final_tool_states 等）也完全一致。

要求：用仓库内独立 Python 审计脚本重新计算 canonical genome fingerprint、规范化规则签名、每个 scenario 的完整 trace signature 和 outcome signature。报告 genotype diversity 与 phenotype diversity，指出哪些基因差异在 D-090 manifest 上没有产生行为差异。

结论范围只能写成“在 D-090 当前 96 个 Train 场景及保存的 15 个 best candidates 上观察到完全行为等价”，不能外推为所有可能环境中等价。

### D5. 两个现有 g03 audit 脚本审计对象错位

- `audit_g03_public_reachability.py` 导入 `d089_scenarios.make_scenario`，并构造 D-089 的 `g03_PAIR_RACE` repeat 0。
- `audit_g03_trace.py` 读取 `experiments/d089_recovery/results/d089_search_report.json`，并选取 D-089 RandomSearch seed 822。

这两个脚本没有审计 D-090 的 `d090_PAIR_RACE` repeat 2。不能把它们的输出作为 D-090 r2 的 25 步下界证据。

要求：新增 D-091 专用审计脚本，直接调用 `d090_scenarios.make_scenario("d090_PAIR_RACE", "D3_DEPENDENT_ABORT", 2)` 并使用 D-090 manifest 与真实环境。保留旧脚本，不覆盖历史证据；在报告中明确旧脚本的实际审计范围。

### D6. 多目标优化与最终候选选择口径需要核对

`objectives()` 返回 6 维目标（constraint+pending、1-cond_rec、1-R3、1-R4、Harm、RecoveryCost），但 `_best()` 从完整 archive 选 best 时使用统一的 lexicographic key：`min(R3,R4)`、`R3+R4`、`-Harm`、`-RecoveryCost`；它不显式使用 `cond_rec`，也不是从最终 NSGA population 或 Pareto front 中直接选出。

要求：解释 NSGA-II/III 的 survivor selection、完整 archive、可行性过滤与最终 best selection 的实际关系。判断该选择口径是否符合预先声明的多目标方法与各方法公平比较；不得静默更改历史结果的选择规则。

## E. Task 1：原始数据完整性与指标独立复算

编写只读审计器，例如 `experiments/d090_recovery/d091_independent_audit.py`。输入只能是 D-090 已提交的原始 manifest、report、ablation JSON 和源码；不得调用 `run_experiment()`、`run_method()` 或重新搜索。

必须完成：

1. 枚举 D-090 所有结果文件，输出相对路径、字节数、行数/记录数、SHA-256、Git blob SHA（可取得时）、JSON schema、必需字段和文件状态。
2. 校验 manifest 内部 SHA-256、report 内部 SHA-256、场景 ID、namespace、split、family、stratum、repeat、标签分布和 scenario uniqueness。
3. 核验每个 run 的 96 best_rows 与 manifest 的 96 scenarios 一一对应；不能遗漏、重复、错序或跨 split。
4. 独立复算 cond_rec、R3、R4、Harm、RecoveryCost、ConstraintViolation、DuplicateCompensation、PendingCompensation；列出分子、分母、求和/均值口径、None 处理和精度。
5. 固定消融的 5 组 96 rows 分别复算，不得将消融与搜索 best candidates 混在一个汇总里。
6. 按 method × seed × family × stratum 输出结果，至少包含 n、successes、denominator、rate、Harm sum/mean、constraint count、pending count。
7. 核对 5×3×96 的计数语义：96 是每个 run 的 unique genome evaluations，不是 96 个 episodes。区分 proposed genomes、unique genomes、cache hits、重复 proposal、每 genome 的 96 场景 rollouts 和最终保存的 best_rows。
8. 明确 report 仅保存 15 个 best candidates 的逐场景 rows，不能假称完整保存了 1,440 个 genome evaluation 的所有逐场景原始轨迹。若没有 generation/proposal/archive 日志，写明搜索过程审计的证据缺口。
9. 所有输入文件只读；任何缺失文件或 SHA 不一致均记录为 FAIL/INCOMPLETE，不得根据报告摘要补造。

指标复算的基本分母应与 manifest 对齐：R1/R2 各 24，conditional recovery 合并口径 48；R3 为 24；R4 为 24；Harm 全部 96。若源码定义与此不同，先列出差异并解释，不能私自更换口径。

## F. Task 2：搜索方法身份、公平性与可辨识性审计

对五个方法逐项检查：

- 方法标签到真实代码分支的映射；
- RNG 初始化与消费顺序；
- 初始种群是否相同；
- mutation/crossover 算子及其概率；
- selection/survivor selection；
- NSGA-II 非支配排序和 crowding distance；
- NSGA-III reference directions、association、niche count 和 niching；
- unique evaluation、cache、proposal 和重复候选的预算口径；
- parent/offspring/archive 的记录与候选选择方式；
- final candidate selection 是否与优化目标一致。

必须输出 method dispatch matrix、operator invocation counts（若现存数据可得）、真实可复原/不可复原字段清单、预算公平性判定和代码级证据行号。

对 15 个 best candidates 计算：
- canonical genome hash；
- rule-block signature；
- effective loci count；
- pairwise Hamming distance；
- per-scenario action/observation/cost/tick trace hash；
- per-scenario outcome signature；
- full 96-scenario phenotype hash；
- pairwise genotype/phenotype equivalence matrix。

对静态代码和现有 JSON 能证明的结论直接证明；对缺失的 proposal-level 历史，不得用重新搜索填补。本轮禁止完整重跑 D-090。若算法身份或过程无法从现存证据审计，明确标为 `NOT_AUDITABLE_FROM_SAVED_TRACE`，并把修复后的对照设计留给 D-092 预注册。

## G. Task 3：D-090 g03-r2 可行性下界与最短路径审计

审计对象必须是 `d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r2`，不是 D-089 的 g03 场景。

### G1. 先验证一个待证伪的 23-step witness

根据当前 D-090 场景定义：
- A primary requires B，B primary requires A；A/B alternate 的 requires 为空；
- C primary 无依赖；
- repeat r2 的 A/B alternate outcomes 为 `[False, False, True]`、delay=2；
- C primary outcomes 为 `[False, True]`、delay=1；
- 环境的 `WAIT` 推进全局 tick，`VERIFY` 是针对单个 tool 的动作。

请用真实 `DependencyRecoveryEnv` 验证下面的动作计划，不要只在文档里手算：

Round 1：
1. `COMPENSATE A alternate`
2. `COMPENSATE B alternate`
3. `COMPENSATE C primary`
4. `WAIT`
5. `WAIT`
6. `VERIFY A`
7. `VERIFY B`
8. `VERIFY C`

Round 2：重复 A alternate、B alternate、C primary、WAIT、WAIT、VERIFY A、VERIFY B、VERIFY C。

Round 3：
1. `COMPENSATE A alternate`
2. `COMPENSATE B alternate`
3. `WAIT`
4. `WAIT`
5. `VERIFY A`
6. `VERIFY B`

最后执行 `ESCALATE`。按上述计数，预期 23 个 decision（8+8+6+1），低于 24-step cap。注意这只是待执行验证的反例，不得在真实环境运行前直接写成已证实结论。

如果该 witness 通过，必须记录每一步 observation、tick、pending 状态、final_tool_states、class_success、constraint_violation、decision_count，并判定原 25-step 下界被证伪。若失败，逐项说明是哪个环境合同、动作限制或状态转移阻止了它。

### G2. 最短路径严格证明

在验证 witness 后，独立实现有限状态 BFS/动态规划或等价的可验证最短路径算法。状态至少包含 tool states、route attempt indices、pending_success、resolve_at、global tick 和 terminal action。动作集必须严格来自 `DependencyRecoveryEnv.step()` 的合法动作语义。

求解目标是 R3 正确升级：最终 ESCALATE、所有可补偿副作用清零、无 pending、无 duplicate、无硬约束违规。证明最小决策数；若 witness 为 23，不能再声称 25。若 BFS 得到更短路径，以 BFS 和执行器回放为准。

必须额外证明没有遗漏合法的并行 dispatch、全局 WAIT 批量推进、多个 VERIFY 顺序、alternate route 或幂等复用。不能把“每个工具各自等待”错误地当作“每个工具都必须单独推进全局时间”。

不得修改 D-090 的原始 24-step cap、标签、scenario、原始 report 或 denominator。历史报告中的错误结论只能通过新的 D-091 更正报告修订。

## H. Task 4：P1/P2/P3/P4 消融安全轨迹

从 `d090_mechanism_ablation.json` 逐条定位失败行和 constraint 行，输出可读 CSV/Markdown。

- P1：当前保存数据中共有 17 条 class failure，按标签分布 R2=8、R3=7、R4=2；必须追踪为什么 Pair-Race 的局部 g03 改善伴随整体 Harm=.479 和 R4=.917。逐条保留 action、observation、tick、decision_count、residual、avoidable_harm 和 final state。
- P2：2 条硬约束违规均位于 `d090_MULTI_ROUTE / D3_DEPENDENT_ABORT`，scenario repeat r1/r3；每条 pending=2，总 pending=4。定位绕过 pending gate 的具体动作序列。P2 不得成为候选。
- P3：检查它为何没有减少 g03 Pair-Race 的 R3 失败；不能只根据 completion gate 的名称推断有效。
- P4：2 条硬约束违规位于 `d090_DEEP_CHAIN / D3_DEPENDENT_ABORT`，repeat r1/r2；每条 pending=1。解释 Harm-ordering 为何在预算紧张时遗留 pending。

硬约束是硬门禁。任何违反 pending/duplicate/unauthorized-action 约束的策略均不能被 Harm 或成本改善抵消。

## I. Task 5：测试、CI 与审计 artifact

1. 新增 D-091 独立审计脚本和专项测试，至少覆盖 manifest integrity、metric recomputation、method dispatch mismatch、phenotype signature、r2 witness replay、BFS shortest path、P1/P2/P4 violation extraction。
2. D-091 审计只读取 D-090 保存的数据，不调用 `run_experiment()`，不执行新的搜索，不改写 D-090 原始产物。
3. 更新 `.github/workflows/research-simulator-regression.yml`：运行 D-091 审计器和专项测试；把 D-091 输出写到 `$RUNNER_TEMP/d091` 并上传独立 artifact。不得把 D-090 search 再运行一次作为 CI 步骤。
4. Artifact 至少包括：`d091_source_manifest.json`、`d091_metric_recompute.json`、`d091_per_family_metrics.csv`、`d091_method_dispatch_matrix.json`、`d091_candidate_phenotype_matrix.csv`、`d091_r2_witness.json`、`d091_r2_shortest_path.json`、`d091_ablation_failure_traces.csv`、`d091_audit_report.md`。
5. 对所有输入和输出记录 SHA-256；CI artifact 的下载地址、run ID、workflow conclusion、artifact name、digest 和到期时间写回证据报告。
6. 绿色 CI 只能证明审计代码/回归测试执行通过，不自动等于所有科学结论成立。审计输出中必须分别给出 DATA_INTEGRITY、METRIC_RECOMPUTE、METHOD_IDENTITY、PHENOTYPE_DIVERSITY、R2_REACHABILITY、ABLATION_SAFETY 六个状态。

## J. 允许与禁止的工作

允许：只读检查、独立复算、静态代码审计、AST/dispatch 测试、候选行为指纹计算、D-090 场景内确定性 trace replay、BFS/最短路径诊断、审计脚本、专项测试、CI artifact 和仓库接管文档维护。

禁止：
- 不得运行新的 genome search，不得增加 D-090 search budget；
- 不得重跑 D-090 原实验来制造新的搜索结果；
- 不得调参、变更基因空间、改变算法臂或选择新的 best genome；
- 不得冻结候选或申请/访问独立 Validation；
- 不得访问正式 Test；
- 不得启动 Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM 训练、UndoBench TEST 或 ThinkingBox；
- 不得修改 main、merge、force-push 或覆盖 D-090 原始证据；
- 不得为了获得 25-step 下界而限制 WAIT/VERIFY 的合法语义。

## K. 最终必须交付的研究结论

报告必须逐项回答：

1. D-090 的 manifest、report、ablation 原始数据是否完整且哈希一致？
2. 所有 15 个 best_rows 的指标是否可以独立复算？差异是多少？
3. `random` 是否是真正的随机搜索？Random 与 NSGA-II 是否实际同一算法路径？
4. `state_evo` 是否使用动态状态/失败反馈，还是静态 mutation bias？
5. `GENERATIONS=6` 是否真实执行？proposal、unique eval、cache hit、generation 的可审计记录是否存在？
6. 15 个 best candidates 是否在 D-090 Train 上完全行为等价？哪些基因位点没有造成行为差异？
7. NSGA-II/III 的 survivor selection、archive 和最终 `_best` 选择口径是否一致、可解释且公平？
8. D-090 r2 的 25-step claim 是否被 23-step witness 或 BFS 推翻？
9. P1/P2/P4 的失败和 pending 机制是否逐条定位？
10. 哪些科学结论可保留、哪些需要撤回或更正？
11. D-092 应该如何重新设计方法臂、编码、动态反馈、预算和记录协议？

结论标签必须严格区分：`PASS`、`PASS_WITH_LIMITATIONS`、`FAIL`、`NOT_AUDITABLE_FROM_SAVED_TRACE`、`CLAIM_FALSIFIED`。不要用一个总的 SUCCESS 掩盖分项失败。

## L. D-092 只能提出方案，不得本轮执行

D-091 完成后，基于实际发现提出 D-092 Train-only 预注册方案。方案至少应修正：

- 真正独立的 Random Search；
- 正确且可单元测试的 NSGA-II / NSGA-III；
- 如果保留状态反馈演化，必须定义动态反馈信号、更新时间、变异概率公式和防止信息泄漏的边界；
- 统一初始候选/搜索预算/unique evaluation 计费/候选选择口径；
- 保存每个 proposal 的 genome、parent IDs、operator、mutation loci、generation、cache status、fitness、selection decision；
- 对 phenotype 等价设计行为多样性指标或结构压缩，但不能事后按结果选择最有利表示；
- 先在 Train 上证明算法臂有可辨识的搜索行为，再决定是否申请独立 Validation；
- 硬约束优先，pending 必须为零，不能以 Harm 或 cost 抵消安全违规。

不要预先假定 D-092 一定采用 Pair-aware + delayed-confirmation reservation。该联合机制只能作为候选假设，必须由 D-091 的轨迹根因支持。

## M. 仓库维护与接班交付

完成后更新：

- `README.md`：写明 D-091 最新状态、关键更正、CI 和唯一下一任务。
- `SESSION_HANDOFF.md`：增加最新权威接管区块，保留旧历史，不删除 D-087/D-090 历史记录。
- `NEXT_SESSION_PROMPT.md`：将 D-091 设为最新 canonical handoff，包含本轮发现、限制、执行状态和下一会话明确指令，并链接本文件。
- `05_DECISION_LOG.md`：记录 D-090 算法对照审计、phenotype collapse、r2 下界更正等决策；结论须等真实审计执行后再落定，不能提前写成 PASS。
- `51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md`：维持 Validation/Pilot B HOLD，列出 D-091 各门禁状态。
- 新增 `101_D091_EXECUTOR_PROMPT.md`（本文件已存在时只更新，不重复创建）。
- 新增最终结果报告，例如 `102_D091_INDEPENDENT_AUDIT_RESULT.md`，仅在真实审计完成后创建。

每个更新都使用当前文件 SHA，禁止并行覆盖同一路径。提交后核验本地 HEAD、远端分支 SHA、main SHA、ahead/behind、工作区 clean 和真实 CI run。若没有执行 CI，不得写 CI PASS。

## N. 退出条件

本轮只有在以下条件全部满足时才可标记 `D091_AUDIT_COMPLETE`：

- D-090 原始输入文件完整性与哈希检查完成；
- 独立指标复算完成并逐项对齐；
- 搜索方法真实身份和已知分支错误被测试覆盖；
- genotype/phenotype 矩阵完成；
- r2 witness 被真实环境执行，最短路径分析完成；
- P1/P2/P4 的约束失败轨迹定位完成；
- D-091 artifact 上传并可下载复核；
- 独立审计报告、决策日志和接班提示词更新；
- 工作分支和 CI 状态核验完成。

若任何关键原始轨迹缺失、审计脚本无法复算或证据不足，状态应为 `D091_PARTIAL / HOLD`，明确缺口与后续方案；不得为了赶进度伪造完整性。

**最终原则：本轮的研究成果是查清 D-090 的证据可信度与算法可辨识性，不是强行证明 NSGA-III 有效。先纠正实验事实，再设计下一轮能够真正检验演化计算贡献的实验。**