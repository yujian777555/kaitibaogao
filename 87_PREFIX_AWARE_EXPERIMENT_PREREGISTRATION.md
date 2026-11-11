# 87 — Prefix-aware Constrained Evolutionary Recovery 实验预注册候选

**日期：** 2026-11-11
**状态：** PREREGISTRATION CANDIDATE / **HOLD — 当前 manifest 封顶，不授权优化器执行**
**依赖审计：** `86_D085_R3_PREFIX_MECHANISM_AUDIT.md`
**独立数据锁：** `experiments/pilot_a3b/prefix_manifest_lock.json`
**科学边界：** 合成机制验证不是算法创新、正式 A-3b 批准或真实 Agent 泛化证据

## 1. 研究问题与否证目标

研究对象不是固定的 compensation-before-escalation 规则本身，而是：

> 在具有已提交前缀、部分提交、补偿失败与权限拒绝的状态化工具工作流中，公开前缀状态与约束演化搜索的组合，能否在相同信息权限和评价预算下，超过强手工 Prefix 规则及标准 EA？

- **机制假设 H-M：** 固定 Prefix 规则相比原 Hand，可降低 R3/R4 的残余和可避免伤害。该假设仅获得当前合成机制支持，不是 EC 证据。
- **算法假设 H-EC：** 完整 Prefix-aware Constrained EA 相比 Validation 选出的最强非 Oracle 基线，在未见任务上获得更高的 family-equal-weight R3 CorrectEscalation，同时满足安全硬约束且不退化 CondRecSucc/R4 containment。
- **否证：** 若固定 Prefix 已达到封顶、完整 EA 不超过固定 Prefix 或最强 EA、提升伴随安全违规，或只在 Train 有效，则 H-EC 不成立。

## 2. 当前执行决定

新开发集的固定 Prefix 规则在 Train 72 和 Validation 24 上全部类别成功、零可避免伤害、零硬约束违规。故：

**当前 manifest 对 R3、R4、CondRecSucc 和安全指标无正向改进空间，本候选的 EC 功效实验为 NO-GO / NOT RUN。**

不得以 RecoveryCost 作为事后替代主终点继续试验。若未来专门研究成本，必须另行预注册成本终点、非劣界值和独立数据，不得利用本次结果选择有利指标。

本文件仍冻结后续非封顶版本的比较规则，防止看过优化器结果后改基线、预算、终点或统计方法。

## 3. 数据隔离与版本

### 3.1 已锁定开发数据

| 项 | 冻结值 |
|---|---|
| 生成器 | `prefix_challenge_generator.py` / `d085-prefix-development-v1` |
| manifest SHA-256 | `cf769671873c594ec73e9a9e7df75bf1774135af6745da54b3411fb08c45d492` |
| Train | 6 families × 4 strata × 3 repeats = 72 |
| Validation | 2 个不相交 families × 4 strata × 3 repeats = 24 |
| strata | P1 compensatable permission prefix / P2 runtime compensation unavailable / P3 recoverable partial / P4 clear timeout |
| 每 split 标签 | R1/R2/R3/R4=18/6（Train/Validation） |
| Test | 未生成、未读取、未参与任何评价 |

Train 仅用于适应度；Validation 仅用于冻结规则选择。scenario ID 和 seed 与 D-079 Diagnostic 无交集，不使用 `evaluation_role=diagnostic`。D-079 D5/D6 只允许 `86` 中两个固定控制器的根因审计，不得用于参数调节或候选选择。

### 3.2 未来 Test 预留规则

预留 `d085|test|` namespace、seed base `2026111900`、40 families、四种 strata、每类 5 repeats，共 800 scenarios。**这些只是封存生成规则，不是已访问的数据。** 精确 family roster 和独立保管人的哈希承诺为 **OPEN**；未承诺前不得声称最终 Test 已完全冻结。

Test 只能在方法、预算、MDE、统计分析和独立审查全部冻结后，经明确批准的一次性门禁访问。不得读取 Test 标签、任务、故障向量或结果来修复生成器、选择参数或选择基线。

### 3.3 新版本门禁

若需解决封顶或语义区分度不足，必须使用新生成器版本、seed 和 manifest lock，旧锁保持不可变。合法改进可研究补偿依赖、验证回执不一致、非永久补偿故障、成本差异和多故障前缀；必须先定义公开可观察信息、动作可达性和标签证明，不能为了产生非零或正向结果修改金标准。

## 4. 封顶与可行性硬门

在任何优化器运行前，分别对 Train/Validation 执行固定控制器上限审计：

1. 若固定 Prefix 在所需主要类别上全部成功、零可避免伤害且零硬约束违规，则相应终点没有改进空间，**禁止开展该终点的 EC 功效实验**。
2. 若 `prefix_reverse`、验证或重试对环境结果没有任何可能的影响，不得把这些基因的名义变异当成有效算法机制。
3. 若 R3 不可达、标签 UNKNOWN、robust/analytic 未批准不一致、前缀状态不可观察或动作空间缺少补偿路径，停止实验并审计环境，不得改标签迎合结果。
4. 若强手工 Prefix 与完整 EA 的最终策略等价，不能声称 EC 贡献。
5. 当前 manifest 触发第 1 条，因此当前执行状态为 **STOP / HOLD**。

## 5. 非封顶版本的比较臂

不得重跑已失败的 SBCG 或加入其分层反例/Hand-anchor 机制作为新包装。只允许复用经过审计的基础 FSM、标准 NSGA 算子和可行性优先规则。

| 臂 | 表示/搜索 | 目的 |
|---|---|---|
| Hand | 原 StatefulFSM / 固定 | 原始强手工基线 |
| Rule-Prefix | `prefix_hand_fsm()` / 固定 | 最强固定补偿顺序基线 |
| Random-Prefix | PrefixAwareFSM / 纯随机采样 | 排除随机搜索解释 |
| NSGA-II | StatefulFSM / canonical | 普通 EA 基线 |
| NSGA-III | StatefulFSM / canonical | 多目标 EA 基线 |
| C-NSGA-III | StatefulFSM / 可行性优先 | 约束本身的对照 |
| Prefix-NSGA-II | PrefixAwareFSM / NSGA-II | 表示与算法交叉对照 |
| Prefix-NSGA-III | PrefixAwareFSM / NSGA-III | 无额外约束机制的表示对照 |
| **Full** | PrefixAwareFSM / 可行性优先 NSGA-III | 候选完整方法 |

Full 的消融：

- **No-Prefix-State：** 不向前缀决策提供公开前缀状态，检验状态表示贡献；
- **Fixed-Prefix-Genes：** 保留状态但冻结四个 Prefix 参数，检验演化参数贡献；
- **No-Failure-Cleanup：** 禁止 `CURRENT` 补偿失败后的既有前缀清理，检验失败处理贡献；
- **No-Receipt-Verification：** 冻结 `prefix_verify=False`，检验公开回执验证的贡献与成本。

若某机制在当前环境无可观察影响，相应消融只报告“不可识别”，不得宣称贡献。

## 6. 信息权限、配对与预算

### 6.1 信息与初始化

- 所有可部署策略只获得公开错误、工具合同、自身动作和公开验证/补偿结果；隐藏 fault、delay、真实 `ToolRuntime.state`、隐藏补偿计数及 gold label 禁止进入策略。
- 每个 optimizer seed 使用同一基础初始种群。Prefix 扩展参数来自独立记录的随机流；基础基因、默认动作、sla/fixed-wait 标志逐项一致。
- 不同表示的 EA 使用相同环境动作集合、场景、seed、评价器、初始基础基因、停止条件和唯一预算。混合表示交叉被拒绝。

### 6.2 条件性小规模探索预算

仅在第 4 节硬门通过后生效，不因中途结果调整：

| 项 | 冻结值 |
|---|---|
| optimizer seeds | `{711, 822, 933, 1044, 1155}` |
| population | 12 |
| offspring generations | 6；无 early stopping |
| 每 seed 唯一候选评价 | `12 + 6×12 = 84`，包含初始种群 |
| 每候选 Train episodes | 72 |
| 每 EA seed 唯一 episode-equivalent 上限 | `84×72 = 6,048` |
| 每 episode 决策上限 | 24；失败重试同样计入 |
| Validation | 只评价冻结候选/档案；不进入适应度，不计作 Train 免费样本 |

唯一 episode-equivalent 的键为：

`(protocol_version, manifest_sha, evaluator_version, controller_type, fsm_fingerprint, scenario_id, scenario_seed)`。

重复指纹或缓存命中不得增加唯一预算；但每个 arm 的实际调用、缓存命中、独立新 episode 和跨 arm 共享 episode 都需分别报告。安全评价、初始种群、回滚内多次工具调用及失败评价均不得漏记。`tool_action_count` 另作真实恢复成本，不能用 episode 数代替。

所有 EA 对照共享配对初始种群和场景。Validation 每次评价记录实际 episode-equivalent；非搜索固定策略的一次评价不得与 84 次搜索评价混称相同搜索预算。

## 7. 终点定义

先在 scenario 内对 optimizer seed 等权，再在 family 内对 strata 等权，最后对 family 等权；不得用大量 repeats 淹没小 family。

| 指标 | 冻结定义 |
|---|---|
| CondRecSucc | R1+R2 的 `class_success` 比例，单独报告，不与 R3/R4 合并 |
| CorrectEscalation | R3 的 `class_success`：显式安全终止、未完成任务且残余为 0；同时报告 `policy_escalate` 与 `stop_safe` |
| PrefixCompensationSuccess | R3 中所需前缀补偿有公开成功记录、补偿后残余为 0 且显式安全终止的比例 |
| ResidualSideEffect | 未完成任务时的 `active_effects`；完成任务的预期业务效果不计残余，duplicate 另计 |
| AvoidableHarm | `max(0, duplicate_count + ResidualSideEffect − min_reachable_harm)` |
| ConstraintViolation | duplicate、SLA violation 或 invariant violation 任一发生的指示值 |
| RecoveryCost | `tool_action_count`；同时报告决策数、补偿次数、补偿失败和实际 episode-equivalent |

R4 containment 使用现有 `class_success` 并逐场景检查 `active_effects == min_reachable_harm` 与 `avoidable_harm=0`。不可补偿影响不能被报告为清零。

**硬安全约束：** 最终候选在所有评价场景上的 duplicate、SLA 和 invariant violation 必须为 0。更低成本或更高恢复率不能补偿安全违规。安全电池若重复评价同一 episode，只计一次唯一预算。

## 8. 选择、统计与成功条件

### 8.1 冻结选择规则

Train 中使用 feasibility-first 与约束支配，不使用未经注册的等权目标求和。Validation 中依次执行：

1. 零硬安全违规；
2. Pareto 非支配；
3. family-equal R3 CorrectEscalation；
4. R4 containment；
5. AvoidableHarm 较低；
6. CondRecSucc 较高；
7. RecoveryCost 较低；
8. 以完整指纹作确定性平局处理。

没有可行候选时输出 HOLD，不放宽约束。先用同一规则确定最强非 Oracle 基线，再评价 Full 的配对差异；基线选择记录必须公开。

### 8.2 探索统计

五个 optimizer seed 只支持探索性描述。报告每 seed、每 family、每 strata 的配对差值、均值和离散程度；不把 repeats 当独立样本，不对五 seed 做确认性 t 检验。若使用 family-block bootstrap，seed=20261116、10,000 次、family 为抽样单位，区间只标 exploratory。

### 8.3 条件性扩大与最终确认

探索阶段只有在零硬约束违规、Full 相对最强基线的 Validation R3 配对均值为正且 CondRecSucc/R4 不退化时，才可申请新的独立数据版本；不得在同一 Validation 上继续调参。

最终 40-family 设计需另行校准 ICC、MDE、technical-missing、Type-I 与功效。family-level 双侧 Student-t 的 df=`F_observed−1`，要求 `F_observed≥34`、完整 strata、配对差值 95% CI 下界大于 0，并满足硬安全门。**MDE、最终 family roster、功效阈值及导师认可均为 OPEN**，当前不授权 Test。

## 9. 停止规则

出现以下任一情况立即停止当前候选的功效主张：

1. 固定规则封顶或最优手工策略不可超越；
2. Full 不优于 Rule-Prefix 或最强非 Oracle EA；
3. R3 提高但 CondRecSucc/R4 退化，或任何硬安全违规；
4. 只有 Train 改善，Validation 未改善；
5. 前缀信息泄漏、Test/Validation 进入适应度、标签错误或场景 ID 配对错误；
6. 初始种群、场景、seed、信息权限或唯一预算不配对；
7. 失败补偿被伪装成功、空回滚被伪装成功、重试绕过 24 次上限；
8. 需要修改阈值、终点、测试集或删除不利 seed 才能获得正面结论。

失败结果和原始 artifact 必须保留。工程测试通过、固定规则有效或单一 AUPRC/成功率提升均不等于 EC 创新成立。

## 10. 当前 pre-flight 状态

| 检查 | 当前状态 |
|---|---|
| R3 动作可达与公开前缀语义 | PASS（限当前合成环境） |
| D-079 v2 根因审计与锁 | PASS；只作机制证据 |
| 新 Train/Validation 隔离与 lock | PASS；不含 Test |
| 固定 Prefix 上限审计 | **FAIL FOR EC EFFICACY：已封顶** |
| 非平凡顺序/验证/重试区分度 | OPEN |
| 独立新协议/实现审查 | OPEN / REQUIRED |
| 最终 Test roster、保管承诺与 MDE | OPEN；Test 未访问 |
| 优化器 runs | **0 / NOT RUN** |
| 真实 LLM、A800、正式 A-3b、Pilot B | **0 / HOLD** |

**唯一下一步：** 独立审查本预注册、机制实现、原始 CSV 复算和封顶门。不得在本 manifest 上启动优化器。
