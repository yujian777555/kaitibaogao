# 56 — Pilot A-3b 研究设计独立审查

**审查日期：** 2026-11-07  
**审查对象：** `55_PILOT_A3B_RESEARCH_DESIGN.md`  
**参照材料：** 47、49、52、53、54 号文件及 `PILOT_A3_INDEPENDENT_REAUDIT.md`  
**状态：** **REQUEST CHANGES — NOT READY FOR PREREGISTRATION**  
**授权边界：** 本审查不授权 A-3b 正式实验、Pilot B、锁箱测试、A800/ARWM 或真实 LLM API。

## 0. 总体结论

Phase B 的公开数据下载、revision 锁定、manifest/hash 核验、ToolMisuseBench DEV 基线复现、UndoBench DEV/validation smoke 与语义覆盖审计，按 D-058 交付记录可判为完成。其研究价值在于明确了外部基准的适用边界：

- ToolMisuseBench 适合作为工具参数/指令修复的第二搜索域，但没有 lost-ACK、重复副作用、补偿失败和 Saga 语义，不能承担契约安全主张；
- UndoBench 具有 lost-ACK、effect-history、不可逆与补偿边界，但 TEST 仅 12 个工作流且高度集中于 lost-ACK，只能支持有限的外部工作流泛化主张；
- A-3/A-3b 自有环境仍是完整覆盖工具级契约、跨工具 Saga、部分提交、延迟可见、补偿失败和因子化 OOD 的主要研究环境；
- ThinkingBox 当前不可达，不得成为实验依赖。

55 号草案已正确识别 A-3 的三个主要设计问题：结构性不可行样本稀释、成功率单一 Gate 忽略效率、诊断 oracle 并非全局上界。可恢复性分层与成本评价方向值得继续。

但独立审查发现 **至少六项阻断预注册的定义/统计问题**。其中 R4 的定义与评价指标存在直接逻辑矛盾：R4 被定义为不存在安全终态，却要求 R4 正确升级必须达到零残留。若不修正，R4 的正确策略会被指标判为失败，且成本目标会惩罚不可避免的残留与必要升级。

因此本轮结论为：**Phase B = GO（审计阶段完成）；55 号 = REQUEST CHANGES；A-3b 正式运行 = HOLD。** 不应直接把 55 号草案冻结为预注册协议。

---

## 1. 阻断问题（必须修正）

### B1. R4 与 CorrectEscalation / SafeResolution 自相矛盾（CRITICAL）

55 号 §4 将 R4 定义为“连安全终态都不可达”，例如不可逆副作用已发生且无法清除；正确行为是最小化损害、记录并升级。

但 §5 又将：
- `CorrectEscalation` 定义为 R3+R4 上选择 ESCALATE/STOP_SAFE **且零残留**；
- `SafeResolution` 定义为全部场景达到安全终态（成功或零残留放弃）；
- `UnresolvedEffect` 定义为非安全终态且残留大于零。

这会造成逻辑矛盾：R4 的定义已经保证至少一个残留无法清除，因此 R4 不可能满足“零残留”，也不可能被计为 SafeResolution。正确的最小损害策略反而会被判错。

**必须修正：**
1. R3：安全升级/停止能够到达零残留终态；评价正确升级且零残留。
2. R4：零残留不可达；评价 `ContainmentSuccess`，至少要求停止新增不可逆/禁止副作用、触发升级/记录、并使可避免损害达到预注册最小值。
3. 将 R4 的不可避免残留单列为 `UnavoidableResidualBurden`，不能与策略可避免的残留混为一项惩罚。
4. `SafeResolution` 只在其定义可达的类别上报告；R4 单独报告 `DamageContainment`，不得宣称 R4 达到安全终态。

### B2. R2 的“优雅失败”与 CondRecSucc 混淆（CRITICAL）

55 号 §4 将 R2 定义为补偿后可恢复，并允许“重启或优雅失败”；§5 又把 R1+R2 全部放进 `CondRecSucc` 分母，同时把 R2 的“安全放弃且零残留”计为 partial。

安全回滚/放弃不等于任务恢复成功。如果将它计入 CondRecSucc，会把任务未完成与任务完成混成一个主指标；如果不计入，则当前 R2 定义又过宽。

**建议采用互斥、可判定的类别：**
- R1：不依赖补偿即可通过公开观测策略完成任务；
- R2：需要补偿/回滚后重启，但存在可执行策略最终完成任务；
- R3：任务无法完成，但可以安全补偿/停止/升级并达到零残留；
- R4：零残留安全终态不可达，只能最小化可避免损害并升级。

安全放弃应归入 R3（或另设明确的 SAFE_ABORT 结果子类），不能计为 CondRecSucc。R2 的 CondRecSucc 只计算最终任务完成；补偿成功率另行报告。

### B3. 可恢复性判定必须是“可观察策略可达性”，不只是动作序列可达（CRITICAL）

55 号 §4 同时要求“存在动作序列”且“不依赖隐藏信息、只用公开观测可达”，但尚未给出可执行判定算法。

在部分可观察环境中，某条动作序列可能依赖真实提交状态或隐藏故障标签。若两个隐藏状态产生相同公开观测，却要求不同动作，则策略无法仅凭公开信息可靠区分它们。

**必须冻结以下语义：**
1. 将 episode 建模为有限状态转移系统，明确状态、动作、公开观测、隐藏状态、故障转移和终态不变量；
2. recoverability 判定检查是否存在仅以公开观测历史为输入的 contingent policy，而非使用 hidden state 的动作序列；
3. 对同一公开观测等价类中的所有可能隐藏状态，定义策略是否必须鲁棒满足目标；
4. 明确搜索 horizon、动作集合、非确定性/随机转移处理和超出 horizon 的 UNKNOWN 处理；
5. 对无法证明属于 R1–R4 的场景标记 UNKNOWN/AMBIGUOUS，不得强行归类；
6. 生成器标签由独立 reachability checker 产生，不能由待测策略成功与否反向定义。

### B4. 有限样本不能证明 P(violation)=0（CRITICAL）

55 号多处把 `P(InvariantViolation)=0` 写成硬约束。有限数量 rollout 中观察到 0 次违规，只能说明该测试样本上 zero observed violations，不能证明真实分布概率严格等于零。

**必须区分两层安全主张：**
- 设计层：通过类型化动作屏蔽、契约前置条件、状态机静态检查或有限状态模型检查，证明声明范围内的非法动作不可达；
- 实验层：在预注册 train/validation/held-out 场景上报告 zero observed violations，并给出基于样本/cluster 的置信上界。

任何已观察到硬不变量违规的候选个体可以按预注册规则判为 infeasible；但论文不能仅凭有限 rollout 声称总体概率严格为零。若无法形式证明，应使用“测试集中零观察违规”而不是“P=0”。

### B5. R4 不可避免残留和必要升级被成本函数错误惩罚（CRITICAL）

55 号 §5：
- `C_side-effect = DuplicateEffect + UnresolvedEffect`；
- `C_intervention = 归一化动作成本 + 升级代价`，且升级代价低于失败、高于直接完成。

在 R4 中，部分残留按定义不可避免；若将其计入 UnresolvedEffect，所有正确策略都会被惩罚。R3/R4 中升级是正确行为，若升级代价进入同一目标而未做类别条件化，搜索可能倾向于避免必要升级。

**必须修正：**
- 将重复副作用、可避免残留、不可避免残留分开；
- R4 的损害成本只惩罚相对可达最小损害基准的 excess/avoidable harm；
- 将 unnecessary escalation（在 R1/R2 可恢复却无必要升级）与 correct escalation（R3 必需升级）分开；
- 对 R3/R4 的必要升级不施加“比直接完成更贵”的惩罚；
- 明确各成本单位、归一化范围、权重、成本下界和敏感性方案；权重必须在看最终 held-out 前冻结。

### B6. R3/R4 比例、类别计数与统计功效未具体化（CRITICAL）

55 号 §3/§6 只给出“可恢复 : 不可恢复 = 3:1”及“R4 少量注入”，没有给出每个 split、每个 held-out slice 中 R1/R2/R3/R4 的精确计数。上一轮汇报中的“R3/R4 分层比例 3:1”也可能被理解为 R3:R4=3:1，与 55 号中的 recoverable:unrecoverable=3:1 不同。

**必须明确：**
1. 3:1 指 ((R1+R2):(R3+R4))，还是 R3:R4；不得使用含糊简称；
2. 分别给出 train、validation、held-out task-shift、fault-shift、joint-shift 中四类精确 episode 数；
3. 明确 R3:R4 内部分配，保证 R4 有足够样本；
4. 同时报告按设计平衡的 challenge-set 指标和按预先定义目标分布加权的指标；不得只靠改变类别比例制造提升；
5. 统计功效以独立的 task-family × fault-composition cluster 数为核心，不得把同一 cluster 的大量 seed/episode 当成独立样本；
6. 用 A-3 的配对数据估计 cluster 方差，进行 cluster-level power simulation，给出检测 Δ=0.05 的功效、最小可检测效应和所需 cluster 数；
7. 若 cluster 数过少，paired bootstrap CI 可能不稳定；须报告 cluster 数并选择适合的小 cluster 数推断方法/敏感性分析。

---

## 2. 重要方法学修订（冻结前必须处理）

### M1. 算法机制归因存在混杂风险

55 号 §7 计划将手工策略 FSM 反编译种子与随机合法 FSM 按 30/70 混合，但没有明确保证所有搜索算法获得相同初始种群。若只有 proposed EA 得到 saga_aware/contract_aware 种子，性能提升可能来自初始化，而非契约保持或反例驱动机制。

**要求：**
- 主对照中的 Random Search、GA、GP、NSGA-II、NSGA-III、A、B、A+B 使用相同的初始候选池/初始化分布、相同合法性过滤和相同 rollout 预算；
- 如要研究手工种子初始化，单独做初始化因子消融；
- A/B/A+B 机制归因固定同一个演化骨干（建议先选 NSGA-II 作为共同骨干），NSGA-III 另作强基线；不得让 A/B 变体同时改变选择算法、编码、初始化和算子；
- 明确标准 GA/GP/NSGA 的表示能力和搜索空间，避免 baseline 因编码能力更弱而被不公平比较。

### M2. 50k rollout × 5 seeds 的预算口径不清

必须说明 50k 是每方法总量，还是每 seed 50k；是否包含无效候选、语义修复失败、重复评价、缓存命中、验证评价与搜索期间反例重评。区分：
- search/training rollout budget；
- validation/model-selection budget；
- final held-out evaluation budget；
- 静态手工策略的共同评价预算。

所有真实环境 episode 都计入预算。额外的模型推理、语义修复、反例分析和 wall-clock 也要单独报告。先做 CPU episode throughput profile，再确认预算可执行性。

### M3. H1 主张必须覆盖标准演化基线

当前 H1 主要比较手工策略和 Random Search。论文的核心主张是改进演化算法，因此主检验至少要预先指定：
- A+B vs 标准 NSGA-II（相同骨干/预算）；
- A+B vs 标准 NSGA-III；
- A+B vs 最强标准 GA/GP 基线；
- A+B vs 强手工 saga-aware。

建议将“相对最强标准 EA 的提升”列为改进算法主张的必要条件；若只超过手工策略或随机搜索，不能宣称改进 EA 已得到证据。明确 primary contrast、secondary contrasts、效应量和 Holm 校正家族。

### M4. 目标函数存在冗余和方向风险

`C_recovery=1-CondRecSucc` 与约束 `CondRecSucc ≥ τ_min` 同时存在并非数学错误，但需要说明其 Pareto 角色；更重要的是，恢复成功、必要升级和 R4 损害控制必须分层，不能用统一成本把不同类别互相抵消。

建议分别定义：
- R1/R2：任务完成率与完成成本；
- R3：正确安全升级率、零残留率和升级成本；
- R4：损害遏制率、可避免损害、不可避免残留；
- 全体：硬不变量、重复副作用。

主多目标向量、约束和每个目标的统计分母须保持一致。

### M5. 新颖性仍未获批准

49 号明确标记为 `INITIAL LITERATURE SCAN / NOT SYSTEMATIC / NOVELTY NOT APPROVED`。55 号 §14 的差异表不能把初步扫描升级为已证明的新颖性。

冻结前应完成机制级系统检索与全文核对，重点覆盖 EvoTool、EvoUndo、事务恢复、程序/状态机合成、约束演化和反例驱动搜索；记录检索式、数据库、检索日期、纳入/排除标准、论文全文、机制对照表。最终主张必须明确限定为“在某种可执行恢复控制器/契约语义/跨故障泛化问题上的具体机制差异”，不能笼统声称首次将 EA 用于 Agent 恢复。

---

## 3. 建议修订后的结果分类与指标骨架

| 类别 | 可判定含义 | 主评价 |
|---|---|---|
| R1 | 仅靠公开观测策略可直接完成 | TaskCompletion-R1、ActionCost-R1 |
| R2 | 补偿/回滚后仍存在完成任务的公开观测策略 | TaskCompletion-R2、CompensationCorrectness、ActionCost-R2 |
| R3 | 无法完成任务，但可安全补偿/停止/升级至零残留 | CorrectEscalation-R3、ZeroResidual-R3 |
| R4 | 零残留不可达，只能限制进一步损害 | ContainmentSuccess-R4、AvoidableHarm-R4、UnavoidableResidual-R4 |

建议统一报告：
- `ConditionalTaskCompletion`：只在 R1+R2 上，以最终任务确实完成为成功；
- `CompensationAssistedCompletion`：只在 R2 上；
- `CorrectEscalation`：只在 R3 上，且明确零残留；
- `DamageContainment`：只在 R4 上，按预注册的最小可达损害/不新增禁止效果判定；
- `DuplicateEffectRate`：按实际重复副作用定义；
- `AvoidableResidualBurden` 与 `UnavoidableResidualBurden` 分开；
- `ObservedInvariantViolation`：报告实际观察值和置信上界，不把有限样本写成总体概率零；
- `ActionCost`：按 recoverability class 分层报告。

此表是审查建议，尚未替代用户批准的正式定义。

---

## 4. Phase B 的使用边界复核

1. **ToolMisuseBench**：DEV Parser+Repair 复现和官方数据核验是有价值的；但其故障主要在 `before_call` 拦截、一次重试可恢复，且缺少 lost-ACK、重复副作用、补偿失败和 Saga。它只能作为参数/指令修复第二域，不得用它的成功率支持核心契约安全结论。
2. **UndoBench**：可作为外部语义迁移验证，但 TEST 只有 12 个 workflow，且 test 主要是 lost-ACK；结论应限定为该基准和工作流范围，统计单位必须是 workflow/fault cluster。
3. **ThinkingBox**：当前不可达，保持不纳入执行依赖。
4. **A-3 OOD**：继续保留原始因子化设计和历史数据；A-3 held-out 不能再作为 A-3b 确认集。

---

## 5. 修订后的阶段 Gate

| 项目 | 当前判定 | 解锁条件 |
|---|---|---|
| Phase B 数据审计 | GO / 完成 | 保留锁定 manifest 和适用边界 |
| 55 号设计草案 | REQUEST CHANGES | 修复 B1–B6、M1–M5 |
| 可恢复性分类器实现 | HOLD（先冻结语义） | R1–R4 互斥定义、观测策略可达性算法确定 |
| 场景生成器扩展 | HOLD（先冻结语义） | 四类精确配额、状态空间与 split 哈希方案确定 |
| Adapter 维护 | GO（限 train/dev/validation） | 不泄漏 hidden/oracle；不触碰锁箱 |
| A-3b 预注册冻结 | HOLD | 独立复审通过、功效/预算可行、用户批准 |
| A-3b 正式运行 | HOLD | 预注册文件 hash 固定且用户明确批准 |
| Pilot B / A800 / ARWM / 真实 LLM API / UndoBench TEST | HOLD | 各自独立 Gate 和授权 |

---

## 6. 下一步执行顺序

1. 创建 `55_PILOT_A3B_RESEARCH_DESIGN_R1.md`，逐条回应 B1–B6、M1–M5；保留 55 原草案不覆盖。
2. 先定义 R1–R4 的互斥语义、observation-based reachability checker 和 UNKNOWN 类别。
3. 重新定义 R2 完成、R3 零残留升级、R4 损害遏制的互斥评分规则。
4. 完成类别配额、held-out cluster 数、cluster-level power simulation 和 rollout 预算估算。
5. 固定统一 NSGA-II 骨干下的 A/B 因子实验，再与 NSGA-III、GA、GP、Random Search 和强手工策略比较。
6. 补做 49 号相关工作的系统性机制审计，确认可主张的新颖性边界。
7. 更新分类器/场景生成器实现任务，但只做单元测试、可达性校验和 train/dev smoke；不运行正式 A-3b。
8. 形成最终 preregistration candidate，交用户批准。**在批准前不运行 A-3b。**

## 7. 最终审查结论

55 号草案方向正确，但当前版本存在 R4 评价逻辑不可能满足、R2 分母混淆、部分可观察可达性未形式化、有限样本“P=0”表述不严谨、成本目标惩罚正确升级、统计功效与算法归因尚未冻结等问题。

**本审查不否定第一项创新，也不批准其成立。** 它只说明：当前研究设计需要先修复上述定义和识别问题，才能成为可信、可复现、可证伪的预注册实验。

本轮决策：**Phase B = GO；55 = REQUEST CHANGES；A-3b = HOLD。**
