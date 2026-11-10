# 76 — Executor Prompt: R4 收尾 + Agent × EC 算法提升验证

**日期：** 2026-11-10  
**仓库：** yujian777555/kaitibaogao  
**分支：** pilot-a-stateful-recovery  
**任务身份：** Executor（直接实施，不是只写计划）  
**本轮基线：** 14a8a1bef23f3195436de0f5d1d66803f9c100e7  
**main：** 683b3fe7fc52c86e917d523fdc6bbb13abbfd653（保持不动）  
**最新 CI：** run 42793004533 @ 14a8a1b，regression success；最近完整测试记录为 run 42791224479 @ f4d8d0d，28+212=240 tests success。接手时重新核验。  
**算法候选：** 75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md  
**状态：** R4 部分实现；算法提升候选未实现、未验证；正式 A-3b = HOLD。

---

## 0. 任务目标：必须以算法性能提升为研究目标

用户明确要求尽快从基础设施维护转向真正的算法改进。你的工作不能止于修复测试、写文档或扩大实验规模。

本任务有两个相互衔接的工作流：

1. **R4 收尾：** 完成正式实验所需的统计、功效、runner、预注册和审计材料。
2. **算法提升：** 将候选 SBCG-NSGA-III 转化为可执行算法，设计强对照与消融，最终寻找可复现的性能提升证据。

核心研究问题：

> 对于有状态、多工具、存在部分提交、延迟可见、超时歧义和补偿失败的 LLM Agent，能否通过安全约束的多目标演化与分层反例引导，进化出比现有 NSGA-II/NSGA-III、随机/规则策略以及手工恢复控制器更好的恢复控制策略？

**重要：** 用户希望得到提升，但不能预设提升已经存在。不得伪造数据、挑选种子、调整终点、放宽安全约束或接触 Test 来制造显著结果。若当前候选失败，必须定位失败机制、提出可证伪的修订，再用允许的数据验证；不得把失败包装成成功。

## 1. 仓库纪律与安全边界

- 唯一仓库：yujian777555/kaitibaogao。
- 唯一工作分支：pilot-a-stateful-recovery；main 保持 683b3fe7fc52c86e917d523fdc6bbb13abbfd653，未经明确批准不合并。
- 开始时重新核验 work/main SHA、ahead/behind、最新 CI、工作区状态；不得依赖本文件中的旧 SHA。
- 只维护本仓库；不得混用 openissue、agentfotagent、EvoPareto-Agent、CausalEvo-DSH、GLEPPO 等其他仓库。
- 保留 72 号独立审计、R2/R3 历史预注册和所有负结果；不得覆盖历史记录。
- 每次实质性实现先写失败测试，再实现，再跑目标测试和完整测试。
- 每轮代码、协议、实验、统计或决策变化后，同轮更新 README、05_DECISION_LOG、SESSION_HANDOFF、NEXT_SESSION_PROMPT。
- 每个结果记录输入/输出 SHA、代码 SHA、配置、随机种子、唯一评价次数、缓存命中、命令、退出码和 CI run。
- 不得把测试通过、功效达标、代码实现或模拟器诊断说成算法增益。

### 严禁事项

在 R4 独立审计 ACCEPTED、导师认可 MDE=0.10、用户明确批准、R4 pre-flight 全通过之前：
- 不运行正式 A-3b；
- 不读取、打印、导出、分析或调参真实 Test 的逐场景标签/结果；
- 不启动 Test final evaluation；
- 不运行 Pilot B；
- 不申请或运行 A800/ARWM 训练；
- 不调用真实 LLM API；
- 不访问 UndoBench TEST；
- 不启动 ThinkingBox；
- 不合并 main。

Test 只允许使用合成 sentinel fixture 测试隔离代码，不得读取真实 Test payload。

## 2. 当前已知事实（不得重新包装）

### 2.1 R4 已有实现

当前 handoff 记录：
- 共享 Student-t / CI helper；
- 正式 family-level primary analyzer 初版和 provenance；
- H2–H5 四项 family-level paired analysis + Holm；由于缺少完整 null/partial-null 校准，全部标为 exploratory；
- Train-only evolution guard；
- 普通 evaluator 的 Test guard；
- public manifest 不向普通调用者返回 Test payload；
- atomic one-time final-evaluation gate；
- metadata-only fail-closed pre-flight；
- 最近完整测试记录 240 tests success（28 + 212），之后 CI run 42793004533 在 14a8a1b regression success。

R4 仍待完成的工作，以当前代码和 CI 实际状态为准，至少核查：
1. formal runner 是否真正接入 formal_analysis，而非仅有辅助模块；
2. outcome-blind 五 composition roster 是否冻结、来源是否可审计；
3. ICC/MDE/Type-I/power 10,000 MC 重新模拟是否完成；
4. R4 preregistration 是否与真实实现逐项一致；
5. pre-flight 是否真实执行并 fail-closed；
6. 独立审计包是否完整。

不能把 240 tests 或最新 CI success 说成 R4 已全部完成。

### 2.2 当前算法负结果

75 号候选文件汇总的历史 diagnostic3 数值：

| 指标 | AB | NSGA-II | AB 相对 NSGA-II |
|---|---:|---:|---:|
| CondRecSucc（R1/R2） | 0.547170 | 0.232704 | +0.314466 |
| CorrectEscalation（R3） | 0.183908 | 0.678161 | -0.494253 |
| DamageContainment（R4） | 0.888889 | 0.962963 | -0.074074 |
| SLA violation | 0.000000 | 0.010288 | -0.010288 |
| Duplicate | 0.000000 | 0.000000 | 0 |
| Avoidable harm mean | 1.152263 | 0.497942 | +0.654321（更差） |

Hand FSM 的历史 R1/R2 CondRecSucc = 0.981132。

这些只是历史诊断数据，不是正式 40-family confirmatory 结果。准确结论是：AB 的恢复成功指标高于历史 NSGA-II，但安全升级、损害遏制和 avoidable harm 明显退化，而且没有超过 hand。不能将其称为成功算法。

## 3. 工作流 A：先完成 R4 最后阻断项

在算法 benchmark 运行前，完成 R4 收尾；不要重复已经有代码和测试证据的部分。

### A1. 做一次真实代码状态盘点

逐项对照 73 号 R4 任务书和 72 号独立审计：
- 标记已实现、已接入、已测试、已由 CI 验证、尚未实现五种状态；
- 对“已实现但未接入”的功能不得计为完成；
- 找出最短阻断路径，不再扩大无关审计范围。

### A2. 正式 runner 接线

- 正式 runner 从 frozen manifest + 原始 run ledger 调用 formal_analysis.py。
- 明确 Train/Validation/Test split 类型边界。
- 正式主分析仅使用 AB − canonical NSGA-II 的 family-equal-weight CondRecSucc。
- family-level Student-t 为唯一主检验，df=F_observed−1。
- 不得从历史 D-064-B 的 6-family diagnostic builder 生成正式结论。
- 运行 synthetic end-to-end fixture，验证从 ledger 到 family means、效应、CI、t/df/p、provenance 的真实路径。
- 不打开真实 Test 数据。

### A3. 冻结 outcome-blind composition roster

- 每个可纳入 family 的 primary composition 数必须与功效模拟假设一致（当前方案为恰好 5）。
- 5 个 composition 的选择必须仅由冻结 manifest / outcome-blind priority 决定。
- 不得按 CondRecSucc、成功率、安全结果、算法差值或 Test 结果挑选 composition。
- 少于 5 个有效 composition 的 family 进入 family_loss，不得静默删除。
- 记录每个 family 的 roster hash 和缺失模式。
- 若 5 composition 方案无法成立，先提出完整不平衡模型并重新推导功效；不得沿用固定 34×5 的旧功效声明。

### A4. 重新计算功效和 Type-I

使用与正式分析完全相同的 Student-t 函数：
- ICC = 0、0.05、0.10、0.20；
- MDE = 0.10；null μ=0；
- F=34、40，并覆盖预先声明的 family-loss 边界；
- 每族恰好 5 个 primary compositions；
- 对允许的 technical missing 进行不利情景模拟；
- 每个 key cell 至少 10,000 MC；
- 输出 power、null Type-I、MCSE、95% MC 区间、seed、配置和结果 SHA。

Type-I 未校准或 power < 0.80 时，必须如实 HOLD 或修改设计；不能反向修改 MDE 或参数凑门槛。

### A5. R4 预注册和审计包

- 新增 R4 候选预注册，不改写 R2/R3。
- 所有主要/次要终点、composition roster、缺失规则、统计函数、功效假设、预算、停止规则和 Test gate 必须与代码一致。
- H2–H5 当前全部 exploratory，除非完成相应 null/partial-null 校准并在 R4 预注册中明确批准为 confirmatory。
- 完成 pre-flight 的真实机器可读输出和人类报告；当前审批字段保持未批准。
- 形成 R4 execution report，交独立 Reviewer；Executor 不得自审自批。

## 4. 工作流 B：算法提升候选 SBCG-NSGA-III

R4 进行期间可完成机制审查、算法代码设计、合成测试和无真实 benchmark 数据的单元验证。真实 Train/Validation 算法诊断必须遵守 75 号候选中规定的审批顺序；不得为了赶进度绕过审批。

### B1. 先确认算法问题确实存在于当前代码

检查：
- experiments/pilot_a3b/a3_bridge.py 的 evaluate_controller() 目标向量；
- experiments/pilot_a3b/ea.py 的 safety_battery_pass()；
- CounterexamplePool.targeted_mutate() 的 failure signature 采样；
- run_evolution() 的最终个体选择逻辑；
- hand FSM 是否进入各 EA 臂共享的初始化/精英档案；
- 目标指标是否在日志中计算却未进入优化或约束。

逐项给出源代码位置、调用链、现有测试和可复现反例。不能只重复 75 号文档中的推测。

### B2. 候选算法：Safety-Balanced Counterexample-Guided NSGA-III

实现候选名：**SBCG-NSGA-III**。采用模块化开关，能独立消融三种机制。

**机制 M1：五维安全感知 Pareto 目标**
- f1 = 1 − CondRecSucc；
- f2 = AvoidableHarm；
- f3 = UnnecessaryActionCost；
- f4 = 1 − CorrectEscalation；
- f5 = 1 − DamageContainment。
- Duplicate、SLA violation、invariant violation 等预先定义的硬约束不得作为可补偿目标。
- 五维参考方向、目标归一化、不可行个体处理和可行性优先级必须明确。
- 不允许通过提高 CondRecSucc 抵消安全约束失败。

**机制 M2：分层反例引导变异**
- 按 task family × failure signature × safety class 分层。
- 防止全局 most-common 单一失败类型垄断变异预算。
- 为稀有/高风险层设置 outcome-blind 的最低抽样概率或有界权重。
- 变异优先作用于训练 trace 中被触发且可定位的基因。
- 记录每层样本量、抽样概率、实际抽中次数、基因命中率、修复成功率和新增有效个体比例。
- 优化器可在 Train 离线使用训练标签计算适应度；部署控制器不得读取隐藏标签、真实故障真值或未来状态。

**机制 M3：Hand-anchor 精英继承 + Pareto 决策**
- Hand FSM 可作为共享初始精英候选，但所有需要比较的 EA 臂必须获得完全相同的初始候选池、预算和评价机会。
- 设置单独的 no-hand-seed 消融，量化 hand seed 本身的贡献。
- 精英档案按可行性、family 覆盖、Pareto dominance 和去重维护。
- 禁止 min(sum(objectives)) 或任何未预注册等权标量化。
- Validation 候选选择使用冻结的安全可行性优先规则、Pareto rank 和预先定义的 tie-break；没有满足安全要求的候选就返回 HOLD，不得放宽约束。

### B3. 强基线与消融矩阵

至少包含：
1. Hand FSM；
2. Random Search / random recovery；
3. Rule-based；
4. Reflection；
5. canonical NSGA-II；
6. canonical NSGA-III；
7. matched-objective NSGA-II（与 SBCG 使用相同五维目标、初始化和预算）；
8. A（Contract Repair）；
9. AB（当前方法）；
10. SBCG-NSGA-III；
11. M1 ablation：去掉五维安全目标；
12. M2 ablation：去掉分层反例采样；
13. M3 ablation：去掉 hand-seed / elite archive。

若资源或预注册不允许一次性运行全部臂，先做 Train-only 机制筛查，再冻结最有信息量的比较；不得在 Validation/Test 结果出来后删掉表现不利的对照臂。

公平性要求：
- 相同任务/场景/seed 配对；
- 相同唯一 simulator evaluation / rollout budget；
- 相同可用信息与数据访问权限；
- 记录 cache hit，不能把缓存命中重复算成新的唯一评价；
- 对比 NSGA-II 与 NSGA-III 时，使用 matched-objective 版本隔离优化器差异；
- 对比 hand seed 时，除 no-hand-seed 消融外，其余 EA 臂共享同一初始精英候选。

### B4. 评价指标和成功判据

候选方法必须同时报告：
- CondRecSucc；
- CorrectEscalation；
- DamageContainment；
- Duplicate；
- SLA violation；
- invariant violation；
- AvoidableHarm；
- UnnecessaryActionCost；
- feasible-front coverage / hypervolume（明确 reference point）；
- 跨 seed 稳定性和 family 异质性。

成功必须同时满足：
1. 相对 matched-objective NSGA-II，CondRecSucc 有可复现改善；
2. R3/R4 安全指标不出现预先定义的不可接受退化；
3. 硬约束不被违反；
4. 相对 Hand FSM 展示安全可行的 Pareto 改善，或如实承认未超过 Hand；
5. 消融能证明 M1/M2/M3 的独立贡献；
6. 结果不是更大预算、不同初始化或额外信息造成。

安全非劣界值、硬约束阈值、目标方向和 hypervolume reference point 必须在查看 Validation 结果之前冻结。没有可信领域依据的阈值不得拍脑袋设定；可先将安全终点独立报告，不做未经论证的合成评分。

### B5. 避免 Validation 过拟合

- 所有机制开发、超参数搜索和失败分析优先限制在 Train。
- Validation 只能按冻结规则做候选选择/停止，不得进入 EA 适应度池。
- 对候选版本、参数、检查次数、验证调用次数完整记账。
- 不得反复查看 Validation 后无限调整算法，再把同一 Validation 当作独立泛化证据。
- 正式 Test 继续锁定，直到一次性 final-evaluation gate 获批。
- Train/Validation 探索性结果不得冒充正式 confirmatory 论文结果。

### B6. 如果第一版仍然没有提升

不得停止在“实现成功”。按以下顺序定位：
1. 目标函数是否遗漏关键安全行为；
2. 硬约束是否可行且过严/过松；
3. 反例分层是否真正提高稀有安全 failure coverage；
4. 变异是否命中可影响失败的基因；
5. hand seed 是否造成搜索早熟；
6. NSGA-III 参考方向是否适配五目标及当前种群规模；
7. 最终 Pareto 选择规则是否选出泛化更好的候选；
8. 评价预算是否足以区分策略。

每次只改一个可归因机制，保留失败版本和消融对照。不得通过换指标、挑 seed、缩小任务集、查看 Test 或删掉失败臂来制造提升。

若 SBCG-NSGA-III 经预注册的 Train/Validation 诊断仍不优于 matched-objective NSGA-II 或安全可行性不足，提交明确 NO-GO，并提出下一个机制级候选；不能把当前候选强行写成创新点。

## 5. 资源与训练边界

- 暂不引入 A800、ARWM 或真实 LLM API。
- 先验证控制器演化机制本身有增益，再讨论训练一个 failure-risk / recoverability predictor 是否能减少昂贵 rollout。
- 若以后考虑 A800 训练，必须先提出独立可证伪假设、训练数据来源、泄漏边界、固定 simulator rollout 预算下的增益指标和消融；另行申请，不得自动启动。
- 当前重点是 Agent 的恢复策略被 EC 改进，而不是把论文转成纯 MetaBBO 或单纯训练基模。

## 6. 必须交付的成果

R4：
- R4 预注册候选；
- 正式 runner 接线和端到端 synthetic 测试；
- 34×5 / ICC 网格功效与 Type-I 10,000 MC 原始 JSON、配置、seed、MCSE、CI；
- 机器可读 pre-flight 和报告；
- R4 execution report；
- CI / clean-clone / hashes 证据；
- READY_FOR_INDEPENDENT_REVIEW 状态，不得自行标记 ACCEPTED。

算法：
- SBCG-NSGA-III 机制设计与源代码审计；
- 可配置实现和单元测试；
- M1/M2/M3 独立消融开关；
- matched-objective NSGA-II/NSGA-III 对照实现；
- 预算/seed/信息访问公平性检查；
- Train-only exploratory runner（审批满足后才可运行）；
- Validation 一次性选择报告；
- 每个 family、seed、failure stratum 的原始结果和汇总；
- 明确 GO / MODIFY / NO-GO 的算法结论。

维护：
- 更新 README、05_DECISION_LOG、SESSION_HANDOFF、NEXT_SESSION_PROMPT；
- 新增阶段执行报告，记录真实状态和唯一下一任务；
- 不覆盖 72、73、75 等历史文件。

## 7. 汇报格式

每轮必须按以下格式汇报：

1. 仓库起始/最终 SHA、分支 ahead/behind、main 是否未变、工作区状态；
2. 本轮完成的 R4 阻断项及尚未完成项；
3. 本轮算法机制改动（文件、函数、行为变化）；
4. 新增测试、真实测试数、CI run/结论；
5. Train/Validation/Test 数据访问边界；
6. 每臂唯一评价次数、预算、seed、cache hit；
7. CondRecSucc、安全终点、harm、cost、效应量和区间；
8. 相对强基线和消融的结论；
9. 科学结论：支持 / 不支持 / 尚不能判断；
10. 唯一下一步任务；
11. README、decision log、handoff、NEXT_SESSION_PROMPT 的更新证据。

**最终原则：先把 R4 做到可审计，再用严格对照找到真正有效的演化机制。研究目标是得到可复现的算法提升；证据不支持时必须如实报告，不得制造成功。**
