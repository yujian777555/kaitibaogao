# 55 — Pilot A-3b 研究设计（预注册草案，未批准、未运行）

**日期：** 2026-11-06（Phase B / 任务二）  
**状态：** RESEARCH DESIGN / **NOT PREREGISTERED-FINAL / NOT RUN**  
**前置：** 47_PILOT_A3_PROTOCOL.md（原协议，冻结不改）、PILOT_A3_INDEPENDENT_REAUDIT.md（A-3 实测与失败边界）、54_BENCHMARK_COMPATIBILITY_MATRIX.md（外部基准语义对照）  
**纪律：** 本文件是设计草案，经独立审查与用户批准后才可冻结为预注册协议并运行；A-3 原始数据保留不动；A-3 held-out 只作历史诊断，不得再作确认集。

---

## 0. A-3 为什么出现 oracle−saga 成功率差为 0（A3b-4 逐项分析）

| # | 候选原因 | 判定 | 证据（全部来自 A-3 已审计数据） |
|---|---|---|---|
| 1 | 所有策略都能达到可恢复场景的最优 | **部分成立** | 在可行单元（triple_mixed 0.53–0.73、train 组合 0.87–1.0）上 saga_aware=oracle=contract_aware 成功率完全相同；saga 已吃掉全部可行成功率 |
| 2 | 场景缺乏可区分的恢复动作 | **成立（主因之一）** | 死区单元里唯一"正确动作"是放弃/升级：partial_comp_failure 补偿必败（comp_fail=1.0），delay_rate_permission 含不可提交的权限拒绝；oracle 的特权信息改变不了动作选择的结局 |
| 3 | 恢复策略过于简单 | **不成立为 gap=0 的原因** | 如果策略简单而 oracle 强，gap 应>0；实测 gap=0 且 23 个 cluster 配对差全为 0，说明差异被结构性封顶，不是策略不够聪明 |
| 4 | 任务分布让不可行场景淹没差异 | **成立（主因之二）** | held-out 52.2%（360/690）落在全员 0% 的两个组合族；聚合层 gap 被死区稀释为 0 |
| 5 | 成本指标设计不足 | **成立（主因之三）** | 唯一真实差异在动作成本（saga 10.17 vs oracle 7.56，+34.6%）；47 号 Gate 的条件 2/3 只看成功率，效率维度无预注册地位 |
| 6 | Oracle 定义/实现局限 | **成立（次因）** | oracle_diagnostic 只看**当前步骤**潜在状态（47 号明文"不保证全局最优"）；它省动作但不能翻盘死区，因此它不是真正的成功率上界 |

**结论：** gap=0 不是"没有优化空间"，而是 (a) 可行空间里强手工策略已达诊断 oracle 水平，(b) 不可行空间吞掉一半 held-out，(c) 评价只认成功率不认效率。A-3b 的修正方向是**显式建模可恢复性、把效率与正确升级纳入目标、重划 held-out 使可行/不可行分层可见**——不是删掉困难场景。

## 1. 研究假设（可证伪）

- **H1（恢复能力）**：在 RECOVERABLE / RECOVERABLE_WITH_COMPENSATION 场景上，演化搜索出的恢复控制器的条件恢复成功率显著高于强手工策略（saga_aware 适配层）与 Random Search，且在 held-out 任务族×故障组合上保持。
- **H2（安全硬约束）**：演化控制器可在**零不变量违规**（P(invariant violation)=0）约束下达到 H1；任何以违规换成功率的个体被硬性拒绝。
- **H3（正确升级）**：在 SAFE_ESCALATION_REQUIRED / STRUCTURALLY_UNRECOVERABLE 场景上，演化控制器的正确升级/安全停止率高于"盲目重试"类基线，且不把不可行任务计入恢复成功率分母。
- **H4（机制归因）**：契约语义保持操作（机制 A）与反例驱动定向演化（机制 B）各自带来可分离的增益（消融可分辨），而非只有组合有效。
- **失败判据**：任一 H 在预注册统计检验下不成立 → 如实报告并收缩/否定对应主张；禁止事后改分母或删场景救结论。

## 2. 机制设计

### 2.1 策略表示（个体编码）
可执行**守卫有限状态恢复控制器**（guarded FSM），类型化基因组：

```
Controller = (States, StartState, Transitions)
Transition = (FromState, Guard, Action, ToState)
Guard      = 公开错误码 ∈ {TIMEOUT, PARTIAL, RATE_LIMIT, SCHEMA, PERMISSION, NONE}
           ∧ 工具契约谓词 (idempotent?, compensatable?)
           ∧ 公开观测计数 (waits_done ≤ W, verifies_done ≤ V)
Action     ∈ {RETRY, VERIFY_THEN_RETRY, WAIT(k≤W), COMPENSATE_THEN_RETRY,
              REPAIR_SCHEMA, ESCALATE, STOP_SAFE}
```

- 策略可见面**沿用 A-3 的 PublicToolView 契约**（公开错误、契约字段、VERIFY/WAIT 结果、自身动作计数）；隐藏故障标签、真实提交时刻、补偿可用性继续隔离（有测试强制）。
- 语义合法性由类型系统/修复算子保证：非幂等工具在"结果不明"守卫下禁止裸 RETRY；COMPENSATE 仅在 compensatable 契约下可达；ESCALATE/STOP_SAFE 为总退出。

### 2.2 两个候选改进机制（独立可消融）

**A. 契约语义保持的遗传操作（Contract-preserving operators）**
- 变异/交叉后运行**语义修复**（deterministic repair）：恢复类型合法、守卫完备（错误码全覆盖或显式 default）、死状态消除、非幂等禁裸重试约束。
- 交叉点只在等价接口状态（guard 可满足性检查）上切割，避免破坏安全前提。
- 对照：无修复的等位基因级 GA（会大量产生非法/危险个体）。

**B. 反例驱动定向演化（Counterexample-guided search）**
- 维护反例池：失败 episode 按 (公开错误签名, 契约类型, 死因) 聚类；死因分类 = {违规-重复副作用, 未恢复-残留, 错误升级-可恢复却放弃, 不必要动作浪费}。
- 每代对最差 cluster 做**定向采样**：以该反例为条件生成/变异候选（类似 CEGIS 的测试输入反馈），并把反例场景升入**加权评价队列**（提升其选择压力）。
- 对照：均匀采样、无反例反馈的 EA。

### 2.3 选择与约束处理
- **可行性优先**：先按硬约束过滤（任何 invariant violation = 不可行），再在可行解内做多目标选择。
- 多目标：\(\min (C_{\text{recovery}}, C_{\text{side-effect}}, C_{\text{intervention}})\) s.t. \(P(\text{violation})=0\) 且 \(\text{CondRecSucc} \ge \tau_{\min}\)（τ_min 预注册锁定，取 saga_aware 基线值，不允许下调）。
- 多目标算法主选 NSGA-II/III（见 §7）；也报告单目标加权版本的敏感性。

## 3. 场景生成（A-3b 环境）

- **执行语义**：沿用 A-3 simulator（per-tool 故障向量、三步 saga、幂等/补偿契约、partial commit、delayed visibility、rate limit、schema drift、permission denial、补偿失败、逆序补偿）。不改 47 号语义，只**新增场景与标注**。
- **新增场景设计原则**（直接针对 §0 的三个主因）：
  1. 可恢复场景必须包含**可区分的恢复决策点**：同一公开观测下，正确动作（如先 VERIFY 再决定）与错误动作（盲目 RETRY）结局不同；这是 H1 的可测空间。
  2. 不可行场景**保留但分层**：每个 held-out slice 内可恢复 : 不可恢复 = 预注册固定比例（默认 3:1，敏感性 1:1 与 5:1）；不允许不可行场景再次淹没聚合指标，也不允许删除它们。
  3. 效率场景：加入"多解但代价不同"的单元（如 visibility_bound=4 但真实 delay=1），使动作成本可区分。
- **外部语义对齐**：可恢复性标注字段参照 UndoBench（reversibility×boundary）与 ToolMisuseBench（typed recoverability）命名，便于跨基准对照（54 号 §5）。

## 4. 可恢复性定义（A3b-1，评估器侧，独立于策略与 oracle）

由**评估器**根据初始状态、工具契约、故障向量、可用操作集与不变量**静态+动态判定**，禁止用"某个策略是否成功"来定义：

| 类别 | 判定条件（同时满足） | 正确行为 |
|---|---|---|
| **R1 RECOVERABLE** | 存在动作序列：全部步骤提交 ∧ 零违规 ∧ 零残留；且不依赖隐藏信息（只用公开观测可达） | 完成任务 |
| **R2 RECOVERABLE_WITH_COMPENSATION** | R1 不成立，但存在含补偿/回滚的序列达到安全终态并允许重启或优雅失败（残留=0） | 恢复成功（含补偿后完成或安全放弃且无残留） |
| **R3 SAFE_ESCALATION_REQUIRED** | R1/R2 均不存在（如补偿必败、不可补偿工具已部分提交、权限永久拒绝），但 ESCALATE/STOP_SAFE 可达零残留安全终态 | 正确升级/安全停止 |
| **R4 STRUCTURALLY_UNRECOVERABLE** | 连安全终态都不可达（如不可逆副作用已发生且无法清除） | 最小化损害 + 记录；正确行为 = 不制造额外副作用并升级 |

**三者隔离**（用户要求）：策略不知道故障真实原因与类别；环境只暴露公开观测；评估器掌握真值与 gold 终态。oracle_diagnostic 保留为**诊断参考**（仅当前步潜在状态），继续不作为可部署策略或上界。

标注流程：生成器对每个 scenario 产出 `recoverability_class` + 判定依据（可达性检查 over 操作图），人工抽检 10%，分类器一致性测试入回归套件。

## 5. 评价指标（A3b-2）

**分母纪律（核心修正）：** R3/R4 场景**不进入**恢复成功率分母；它们单独计"正确升级率"。禁止把不可行任务与可恢复任务混在一个成功率里（A-3 教训）。

| 指标 | 分母 | 定义 | 角色 |
|---|---|---|---|
| CondRecSucc | R1+R2 场景 | 任务完成（R2 允许补偿后完成；安全放弃且零残留计 partial，单列） | 主指标（H1） |
| SafeResolution | 全部 | 达到安全终态（成功 ∨ 零残留放弃） | 主指标 |
| CorrectEscalation | R3+R4 场景 | 选择 ESCALATE/STOP_SAFE 且零残留 | 主指标（H3） |
| InvariantViolation | 全部 | 硬约束，目标=0；任何>0 即个体不可行 | 硬门禁（H2） |
| DuplicateEffect | 全部 | 重复副作用次数>0 的 episode 率 | 硬门禁分量 |
| UnresolvedEffect | 全部 | 非安全终态且残留>0 | 报告 |
| RecoveryCost | 全部 | 动作数、等待数、补偿尝试数、升级次数 | 目标（效率） |
| Worst-group | task-family×fault-composition×class | 各组 CondRecSucc/CorrectEscalation 最差值 | 泛化门禁 |

**目标形式（候选，参数预注册锁定）：**
\[
\min_{\pi} \big( C_{\text{recovery}},\; C_{\text{side-effect}},\; C_{\text{intervention}} \big)
\quad \text{s.t.} \quad P(\text{InvariantViolation}) = 0,\;\; \text{CondRecSucc} \ge \tau_{\min}
\]
- \(C_{\text{recovery}}\) = 1 − CondRecSucc（R1+R2 上）；  
- \(C_{\text{side-effect}}\) = DuplicateEffect + UnresolvedEffect 加权（权重预注册，如 1:1，敏感性报告）；  
- \(C_{\text{intervention}}\) = 归一化动作成本 + 升级代价（升级计价低于失败，高于直接完成；具体计价表随协议冻结）。  
- 不可行处理：违反硬约束的个体排名恒低于可行个体（Deb 可行性规则），不做惩罚系数调参。

## 6. 任务划分（A3b-3）

- **全新划分，A-3 旧 held-out 作废为确认用途**（仅历史诊断）。
- 因子化设计沿用并扩展：任务族 × 故障组合族 × 可恢复性类。
  - Train：3 train 任务族 × train 组合族 × {R1,R2,R3}（R4 少量注入）；
  - Validation：任务漂移、故障漂移两组（调参与停止用）；
  - Held-out：held-out 任务族 × held-out 组合族 × 全类，**含 R3/R4 分层**（比例预注册）。
- 防泄漏：任务族模板、组合族参数生成器在 split 间互斥（A-3 已验证的因子化检查脚本复用）；生成后冻结 seed 与场景清单并哈希存档。
- held-out 使用纪律：全部算法/超参/预算冻结后**一次性**评价；任何基于 held-out 的修改必须新起协议编号（A-3c），不得回头改 A-3b 结论。

## 7. 演化算法预设计（A3b-5）

**被比较的方法（同预算）：**
1. Random Search（同初始化分布、同评价预算）；
2. 标准 GA（等位基因编码、单点交叉、均匀变异、无语义修复）；
3. 标准 GP（以 FSM 规则集为树/线性程序的语法受限 GP）；
4. NSGA-II（三目标）；
5. NSGA-III（参考点版，三目标）；
6. **契约语义保持 EA**（机制 A = 语义修复 + 接口感知交叉）；
7. **反例驱动 EA**（机制 B = 反例池 + 定向采样/加权队列）；
8. **A+B 组合**；
9. 强手工策略（saga_aware 等七策略照搬 + 可恢复性分层指标重算）；
10. 诊断参考：oracle_diagnostic（不参与竞争，仅报告）。

**初始化：** 从手工策略的 FSM 反编译为合法基因组（种子种群含 saga_aware/contract_aware 变体）+ 随机合法 FSM 混合（比例预注册，如 30/70）；随机初始化必须通过语义合法性检查，禁止无效基因组占坑。

**预算：** 以**真实 simulator episode rollout 计费**；各方法相同 rollout 预算（如 50k episodes）+ 相同的训练场景池；GP/GA 种群×代数按预算换算；每个个体的重复 rollout 数一致（公共随机数）。禁止 proposed method 多拿 fitness 调用。

**反例驱动的实现细节：** 反例聚类用公开签名（错误码序列×契约类型×死因），每代取 top-k 最差 cluster 定向生成；反例队列权重上限预注册（如 2×），防止遗忘其余分布。

## 8. 强基线与外部基线

- 自有域：§7 的 1–5、9、10（不得只比 blind_retry）。
- ToolMisuseBench 域（Phase C adapter 就绪后）：Parser+Repair（已复现 0.7622 dev）+ recovery-disabled + 我们的控制器适配版；只在 train/dev 搜索，test_public 锁箱一次性。
- UndoBench 域：官方 recovery=none/scripted + saga_aware 适配版；TEST 锁箱，方法冻结后一次性。
- EvoTool/EvoUndo 等近邻（49 号审计）：机制对照必列；能公平适配的才进实测基线，不能的明确声明"未实测"，禁止伪称比较过。

## 9. 计算预算与资源

- 模拟器 rollout 为主（CPU）；预算表随协议冻结：搜索 50k episodes×每方法×5 seeds，验证/测试按 split 计。
- LLM API：**本轮 HOLD**；若未来获批（deepseek-flash、关 thinking、JSON 模式、绕代理直连），仅用于适配层观测生成，预算单独预注册。
- A800/ARWM：**HOLD**；仅当 H1–H3 初步成立且 rollout 成本成为瓶颈时另提申请。

## 10. 统计方法

- 单元：scenario 配对（同 seed/fault 公共随机数）；聚类：task-family × fault-composition（+可恢复性类分层报告）。
- 主检验：cluster paired bootstrap 95% CI（与 A-3 同法）+ 置换检验双报告；多方法比较用 Holm 校正。
- 报告：均值、CI、每 cluster 差值分布、worst-group；禁止只报均值。
- 样本量：train/val/held-out 数量在协议冻结时给出并核算检验功效（对 Δ=0.05 的检测）。

## 11. 消融实验（H4）

| 消融 | 目的 |
|---|---|
| A−B−（基础 EA）/ A+B− / A−B+ / A+B | 机制 A、B 的独立贡献与交互 |
| 语义修复 on/off | 安全约束是靠修复算子还是选择压力 |
| 反例队列权重 1×/2×/4× | 定向压力强度 |
| 初始化：纯随机 vs 手工种子 vs 混合 | 种子策略贡献 |
| 可恢复性分层 vs 混合分母（仅诊断，不用于主张） | 分母修正的必要性证据 |
| 成本计价表敏感性 | \(C_{\text{intervention}}\) 结论稳健性 |

## 12. 停止条件

- 全部方法硬违规>0 且无法通过修复消除：停止，重构模拟器/表示后再开新协议。
- 任一方法在 train 就无法超过 saga_aware 的 CondRecSucc：H1 判负，停止大实验，分析表示/场景可区分性。
- proposed EA 相对标准 GA/GP/NSGA 无稳定增益（CI 含 0）：撤销"改进 EA"主张，保留负结果。
- 仅 train 提升、held-out 不提升：判过拟合，不通过。
- 平均提升但 worst-group 或安全恶化：不通过。
- 预算耗尽：按达到的证据阶段报告，不续命加预算。

## 13. 可能失败的原因（预登记，防事后合理化）

1. 场景可区分性不足（重建后仍 gap≈0）→ 表示或场景生成需重设计，而非改分母；
2. FSM 表示不足以编码有效恢复 → 换表示（带程序片段/层级）另开协议；
3. 反例反馈过拟合少数 cluster → 权重消融验证；
4. 公共随机数方差在 R3/R4 小样本上过大 → 增加重复、按类报告；
5. 契约修复算子太强，等价于把手工策略写进算子 → 消融（修复 on/off）+ 检查修复前后行为差异；
6. 外部基准（ToolMisuseBench/UndoBench）语义不匹配导致迁移失败 → 如实报告为边界（54 号已预警），不包装。

## 14. 与已有工作的差异（依据 49 号审计）

| 已有工作 | 其覆盖 | A-3b 的差异主张（待验证） |
|---|---|---|
| UndoBench / EvoUndo | lost-ACK 基准与受约束 self-evolution | 我们做**EC 搜索可执行恢复 FSM**，含契约保持操作与因子化 OOD；EvoUndo 的"self-evolution"非 EC |
| EvoTool（ACL 2026） | 梯度无关演化优化 NL 工具策略 | 我们的对象是**类型化安全控制器**+硬不变量，非 NL 提示策略；EvoTool 必须列为适配基线 |
| LIMBO / Cordon / Atomix / SagaLLM | 事务/幂等/补偿运行时机制 | 我们把契约语义**编入演化算子与安全门禁**，并检验 EC 相对强手工/标准 EA 的增益 |
| Repair Economics / Verified Tool Calls | 重试/验证/幂等测试床 | 覆盖重叠（A-3 不主张基准新颖性）；差异在恢复策略搜索与泛化证据 |
| CDGP / FSM-MOEA / SMC-ES | 安全程序/控制器合成 | 领域对象是**状态化副作用工具工作流**的恢复决策，含结果不明与补偿失败语义 |
| 标准 GA/GP/NSGA | 通用演化 | 差异若存在必须由消融证明来自 A/B 机制，而非调参 |

**红线：** 仅"FSM+契约+EA+Pareto 的组合"不构成创新；每个机制必须过 §11 消融与 §10 统计；不过就删。

---

## 附：执行前置清单（协议冻结前必须完成）

1. 本设计经独立审查（数学/统计/可识别性/与 49 号边界一致性）；
2. 可恢复性分类器实现 + 一致性回归测试（≥10% 人工抽检）；
3. 场景生成器扩展实现 + 因子化/泄漏检查脚本通过；
4. 预算表、τ_min、成本计价表、seed 清单、场景哈希全部冻结；
5. 用户批准预注册 → 运行后不得更改以上任何项。
