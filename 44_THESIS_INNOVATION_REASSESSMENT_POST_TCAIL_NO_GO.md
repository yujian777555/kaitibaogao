# 44 — TCAIL NO-GO 后的硕士论文创新点重新评估

**日期：** 2026-11-05  
**唯一仓库：** yujian777555/kaitibaogao  
**基线：** c9231dcb4be71dcc7748380b5e876312dd22d2c5  
**状态：** DIRECTION REASSESSMENT / CANDIDATES NOT NOVELTY-APPROVED

## 0. 决策摘要

TCAIL R1 Estimator Gate 已明确失败：q macro-AUPRC 0.6736，对比 standardized contrast 0.7732，配对差 -0.0996，95% CI [-0.1139,-0.0858]；FOS F1 0.373 对比 0.729；calibration slope 0.130。Downstream GOM 未运行。因此：
- TCAIL 不再作为毕业论文核心创新点；
- 不得把 M3-only 的解盲后结果重新包装为新方法；
- CI-GOM 旧版依赖 TCAIL linkage 的规格冻结，不按旧规格继续实现；
- 保留全部失败数据，不删除、不改写为正面结果；
- 重新选择更容易定义可执行搜索空间、硬约束和真实收益指标的问题。

**新主线候选：面向状态化工具型 LLM Agent 的故障恢复策略演化与递归自我改进。**

这是研究候选，不是已证明的新颖性结论。演化计算优化的是 Agent 的恢复策略/控制器，而不是仅让 LLM 生成更多 prompt。LLM backbone 可固定并通过 API 使用；进化对象是结构化策略基因型。

## 1. 必须保留的毕业论文约束

1. 演化计算是核心方法，必须进入种群生成、变异/重组、选择和生存者更新的闭环。
2. RSI 是研究对象与运行机制：Agent 从自身执行轨迹和失败中更新后续版本，并在后续任务中验证能力提升；不要求本轮训练 LLM 基模。
3. 至少两个独立、递进的创新点，各自有独立论文问题、算法机制、强基线和实验 Gate；第三项是储备，不凑数。
4. 方法提升型论文优先。单纯系统工程、失败分类数据集、prompt 反思、普通 Pareto/NSGA-III 套用均不算算法创新。
5. 不能只证明模拟器运行成功；要证明演化机制相对标准 EA 和领域强基线有可归因收益。
6. 所有方法共享模型、工具环境、任务实例、随机种子和评价预算；硬安全不变量不可由任务成功率或低成本抵消。

## 2. 为什么原交互感知路线不再作为主线

TCAIL 的核心失败不是一个可通过简单换 merge 规则消除的小问题：
- M2/M3 conservative min 明显受模型误配影响；
- M3-only 解盲后仍输给 standardized contrast；
- FOS 恢复质量大幅落后；
- q 校准不足；
- 低支持/drift 的局部正收益不能抵消其他关键情景的显著负收益。

旧创新点二 CI-GOM 的 Oracle FOS pilot 只说明一个简化 deceptive-trap GOM 原型存在 linkage 上界价值，不说明真实 Agent 配置上能可靠学习 linkage，更不说明旧 CI-GOM 已有算法贡献。故不把 Oracle 上界误写成 CI-GOM 证据。

## 3. 最新相关工作对选题的约束

本轮快速检索发现，以下方向已明显拥挤，不能直接作为创新点：
- 通用 prompt/workflow/agent 配置演化与 Pareto 搜索：GEPA、AgentEvo、EvoAgent 等已有直接工作；
- 通用模块化工具策略的 blame-aware mutation、targeted mutation 与 diversity selection：EvoTool 已直接涉及；
- 延迟奖励下的 Agent 自进化与过程级信用分配：Q-Evolve 已采用 in-distribution critic、IQL 与过程奖励；
- skill/team 级 group-relative credit assignment：GRSE 预印本已提出执行对比式 agent-skill credit；
- 通用失败诊断、故障恢复和失败知识检索：AgentDebug、PROBE、Sentry 等已有直接研究；
- 工具故障基准和恢复评估：ToolMaze、ReliabilityBench、GUI-RobustEval 等已提供不同形式的故障/恢复评测；
- 工具调用事务治理：Cordon、DelAct 等已覆盖 commit/rollback/idempotency/replay 等 runtime 机制。

因此不能提出“进化 prompt”“按失败模块定向变异”“记忆失败经验”“加入 Pareto 选择”“工具调用加事务保护”作为独立创新。可探索的差异必须落在：**状态化副作用工具环境中的恢复策略作为可执行有限状态控制器，由约束演化算法搜索；并进一步让策略种群与有效故障场景共同演化，以检验对未知故障的泛化。**

## 4. 新候选总题目

优先工作题目：

**《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》**

英文工作译名：Evolutionary Recovery Policy Optimization and Recursive Self-Improvement for Stateful Tool-Using LLM Agents.

题目须经导师认可和后续文献审计后再冻结。它比旧题目更聚焦，但不能先写成既定结论。

## 5. 两个核心创新候选

### 创新候选一 / 小论文一：状态感知、契约约束的 Agent 恢复策略演化

**研究问题**

当 Agent 使用工具执行有状态副作用操作时，超时、部分提交、延迟可见、重复请求、权限错误或 schema drift 会使“直接重试/反思”产生重复副作用或错误状态。能否把恢复过程表示为结构化策略，并用演化计算搜索出同时满足安全不变量和任务恢复目标的策略？

**进化个体**

将恢复策略编码为带守卫条件的有限状态控制器/决策表，而不是自由文本 prompt。可观察状态至少包含：
- effect status：NOT_DISPATCHED / IN_FLIGHT / COMMITTED / PARTIAL / UNKNOWN_OUTCOME；
- failure signature：timeout、rate limit、schema mismatch、stale read、partial response、permission failure 等；
- retry/idempotency status；
- precondition/postcondition verification result；
- retry allowance 与任务阶段。

动作集合候选：
- verify/read-after-write；
- refresh/reconcile state；
- retry only-if-idempotent；
- replan with updated observation；
- compensate/rollback；
- escalate/abstain。

实际状态字段和动作必须依据环境接口冻结；不允许策略读取隐藏 oracle 标签。

**演化机制候选**
1. 类型化、带前置/后置条件的 policy genome；
2. 对 state-transition rule / policy subgraph 执行变异与重组；
3. contract-aware feasibility repair，只允许修复到满足状态机与安全不变量的策略；
4. feasibility-first survivor selection：任何 critical invariant violation 均不可由高成功率补偿；
5. 在可行策略集合内优化恢复成功率、未解决率、恢复代价和正常任务回归。

注意：有限状态控制器、contract repair、NSGA-III 或 Pareto archive 单独都不是创新。必须证明提出的状态语义编码/可行变异/选择机制相对普通 GA/GP/NSGA 和手工策略的独立收益。

**核心假设 H1**
在相同 Agent backbone、工具环境和 rollout 预算下，状态感知约束演化策略相较固定 retry、ReAct/Reflexion、Sentry/AgentDebug 类恢复基线以及普通 GA/NSGA 搜索，能够提高故障后的任务恢复成功率，同时将重复副作用和安全不变量违反维持在预注册硬门限内。

**必要基线**
- fixed retry / exponential backoff；
- verify-before-retry / read-before-write rule policy；
- ReAct / Reflexion；
- Sentry 或可复现的 failure-playbook retrieval baseline；
- AgentDebug/PROBE 类诊断后指导恢复基线（按可复现实现标明）；
- random policy search；
- standard GA/GP；
- NSGA-II/III feasibility-first；
- proposed constrained evolutionary recovery controller；
- oracle policy 只作为上界。

**指标**
- task recovery success；
- duplicate side-effect rate；
- invariant violation rate（硬门禁）；
- unresolved/UNKNOWN_OUTCOME handling accuracy；
- false recovery / harmful retry rate；
- recovery steps、额外 tool/API calls、token 与 wall-clock；
- 正常无故障任务回归；
- 按 fault type/severity/dispatch stage 分层。

**Gate-1**
先在确定性 stateful simulator + fault injection 上验证。只有同时满足：
- 安全不变量无违规（或达到事先定义的 fail-closed 认证门）；
- recovery success 对最强非 Oracle 基线有配对 held-out 优势；
- 额外成本没有抵消实际收益；
- 机制消融证明状态感知变异/契约约束并非普通 GA 即可替代；
才进入真实 LLM API 驱动的模拟工具 Agent 验证。

### 创新候选二 / 小论文二：故障场景—恢复策略双种群协同演化

**研究问题**

固定 fault injection 集合会使恢复策略过拟合已知故障；单纯随机生成故障又可能产生无效、重复或不具代表性的场景。能否让恢复策略种群与有效故障场景种群共同演化，使策略面对不断暴露的新弱点，同时避免只对极端或无效故障过拟合？

**双种群表示**
- Recovery population：创新点一中的可执行恢复策略。
- Fault-scenario population：由可验证故障语法生成的场景，包含 fault type、trigger stage、duration、visibility delay、partial-effect pattern、retry semantics 等；场景必须满足可达性、合法性和可复现性。

**协同演化机制候选**
1. 恢复策略在固定回归档案 + 当前挑战场景上评价；
2. 故障场景以暴露策略失效、场景有效性和行为多样性为目标；
3. 使用历史挑战档案避免 coevolution cycling / forgetting；
4. 使用独立 held-out fault families 检验泛化；
5. 对极端但不现实、不可达或违反工具语义的场景进行硬过滤。

**核心假设 H2**
在相同场景生成预算和策略评价预算下，双种群协同演化相较固定故障集、随机 fault curriculum 和单边 adversarial scenario search，能够提高未见故障族上的最差组恢复率，并减少安全违规，而不是只提高训练挑战集分数。

**必要基线**
- fixed fault suite；
- random fault curriculum；
- severity curriculum；
- one-sided adversarial scenario evolution；
- policy-only EA；
- standard competitive coevolution；
- proposed archive/validity-aware coevolution。

**指标**
- held-out fault-family recovery；
- worst-group success / lower-tail success；
- scenario validity/reachability；
- scenario diversity与重复率；
- catastrophic invariant violation；
- policy forgetting / normal-task regression；
- coevolution cycling 与 archive coverage；
- 同预算下的 policy 与 scenario evaluations。

**Gate-2**
只有 Gate-1 通过后启动。若双种群方法不能优于固定/随机/单边场景搜索，第二创新点 NO-GO，不为了凑两篇而保留。

## 6. 第三个创新点（储备，不进入当前核心计划）

**跨任务恢复策略迁移与能力保持。**

研究已进化恢复规则能否按可观察的故障状态签名和工具语义迁移到新任务，同时识别负迁移并保护旧任务能力。

该方向与 Sentry 的条件化故障知识检索、Q-Evolve 的跨环境策略学习、MetaSkill-Evolve 的双时间尺度 skill/meta-skill 演化有明显重叠。只有在前两项通过后，且证明“演化策略迁移”优于检索、直接迁移和从头进化，才列为第三篇。否则删除。

## 7. 研究对象、RSI 和 EC 核心的关系

- **Agent：** 使用 LLM API 的工具型 Agent；LLM backbone 固定，避免把基模训练混入研究。
- **RSI：** Agent 从自己的失败轨迹和恢复结果中更新恢复控制器；下一代 Agent 继承改进后的策略，并在后续任务分布中检验是否持续改进。必须同时报告正常任务能力是否回退。
- **EC：** 对结构化恢复策略进行种群搜索、变异、重组、约束修复和生存者选择；第二项进一步将故障场景也作为演化种群。EC 是产生和筛选策略改进的核心机制，而非外部装饰。
- **安全：** 工具副作用和状态一致性是硬约束，不作为可被其他目标补偿的普通 Pareto 目标。

## 8. 可行性排序与决策

| 方向 | EC 核心程度 | 实验可控性 | 新颖性风险 | 当前判断 |
|---|---:|---:|---:|---|
| 状态感知恢复策略演化 | 高 | 高 | 中 | **优先预研 / HOLD** |
| 故障场景—策略协同演化 | 很高 | 中高 | 中高 | **第二候选 / HOLD** |
| 跨任务策略迁移 | 高 | 中 | 高 | **储备 / FROZEN** |
| 通用 Agent 组件交互估计（TCAIL） | 高 | 已有实证失败 | 高 | **NO-GO** |
| 旧版 TCAIL-linkage CI-GOM | 高 | 依赖失败的估计器 | 高 | **FROZEN / 不按旧规格实施** |
| 通用 blame-aware mutation / Pareto prompt evolution | 中 | 高 | 很高 | **不选** |

## 9. 最小验证顺序：先证明问题和算法上界

不要立即实现完整系统。先用一个小而可证伪的实验决定方向：

**Pilot A：恢复策略是否存在可进化空间？**
- 构造 6–8 类 stateful tool failure；
- 实现 5–8 个手工恢复策略 + oracle recovery policy；
- 在相同任务/初态/故障注入/随机种子下运行；
- 确认 oracle 与合理策略之间存在可测量差距；
- 若简单规则已经达到 oracle，停止此方向。

**Pilot B：EC 是否能学到有效策略？**
- 比较 fixed best rule、random search、standard GA/GP、NSGA-II/III、proposed contract-aware variation；
- 相同 policy evaluation budget；
- held-out task/fault seeds；
- 主指标为安全门通过后的恢复成功率；
- 若 proposed 机制不优于标准 GA/GP，不能把它写成算法创新。

**Pilot C：协同演化是否值得？**
- 只有 Pilot B 有正向证据后；
- 对比 fixed/random/adversarial/co-evolved fault scenarios；
- 重点看 held-out fault family 的 worst-group recovery，而不是训练挑战集分数。

## 10. 立即停止规则

- 若 oracle recovery policy 没有优于简单 retry/verify：停止该任务族。
- 若普通 GA/GP 与 proposed constraint-aware EA 无差异：删除算法新颖性主张。
- 若恢复成功提升但出现 critical side-effect violation：NO-GO。
- 若 coevolution 只提高训练场景表现、不提高 held-out fault families：第二项 NO-GO。
- 若旧任务能力显著退化：不能宣称 RSI 递归改进成功。
- 不允许查看 held-out 后调参；每轮确认性实验使用全新独立 seeds。

## 11. 本轮执行边界与下一步

本文件只完成创新方向重评，不代表任何新算法已经成立。下一步应先完成：
1. 对 EvoTool、GEPA、Q-Evolve、GRSE、Sentry、AgentDebug/PROBE、ToolMaze、ReliabilityBench、Cordon、DelAct 的机制级差异矩阵；
2. 明确 stateful tool failure 的有限状态空间、可观察变量和硬不变量；
3. 完成 Pilot A 的 oracle/handcrafted policy 上界测试；
4. Pilot A 通过后再做 Pilot B。

不立即启动 Pilot B/C，不训练 LLM 基模，不调用 A800 训练。若后续使用 LLM API，固定模型版本与调用配置，并将所有方法的 API/rollout 预算配平。保持 kaitibaogao 为唯一毕业论文维护仓库。

## 12. 本轮相关工作入口

- GEPA (ICLR 2026)：https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html
- EvoTool (ACL 2026)：https://syang2000.github.io/ACL_2026_EvoTool/
- Q-Evolve (ICML 2026)：https://proceedings.mlr.press/v306/zhang26au.html
- AgentEvo (2026)：https://link.springer.com/article/10.1007/s40747-026-02325-0
- GRSE (arXiv preprint, 2026)：https://arxiv.org/abs/2610.27227
- Sentry (arXiv preprint, 2026)：https://arxiv.org/abs/2610.02994
- ToolMaze (arXiv, 2026)：https://arxiv.org/abs/2606.05806
- ReliabilityBench (arXiv, 2026)：https://arxiv.org/abs/2601.06112
- Cordon (arXiv, 2026)：https://arxiv.org/abs/2606.17573
- DelAct (IWQoS 2026)：https://doi.org/10.1109/IWQoS70441.2026.11661202

**最终状态：** TCAIL = NO-GO；新主线 = Stateful Agent Recovery Policy Evolution / RSI（HOLD）；两个核心候选均需 Gate，第三项冻结。
