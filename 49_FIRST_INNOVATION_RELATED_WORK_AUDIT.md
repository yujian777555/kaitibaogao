# 49 — 第一项创新相关工作与新颖性边界审计

**日期：** 2026-11-06  
**范围：** 契约约束的状态化工具型 LLM Agent 恢复控制器演化  
**状态：** INITIAL LITERATURE SCAN / NOT SYSTEMATIC / NOVELTY NOT APPROVED  
**唯一仓库：** yujian777555/kaitibaogao  
**工作分支：** pilot-a-stateful-recovery

## 0. 核心结论

相关工作很多，且 2026 年已有多篇与 Agent 工具故障恢复、状态副作用、事务补偿、Agent 策略演化和 recoverability-constrained self-evolution 高度相关的研究。

因此不能把以下内容单独宣称为创新：
- Agent 工具调用超时、部分提交、延迟可见、重复副作用的故障建模；
- verify-before-retry、idempotency、Saga compensation、transaction wrapper；
- 通用 Agent tool-use prompt/workflow 的 evolutionary optimization；
- 通用 finite-state/programmatic controller synthesis；
- 在 Agent 自我修改中加入 recoverability check。

**当前可继续探索的交叉点（研究假设，不是已证实的新颖性）：**
面向有状态副作用工具的、具有明确可观察语义和工具契约的可执行恢复控制器；通过契约语义保持的类型化表示、反例/轨迹驱动的专用变异与修复算子，以及硬安全可行性优先的演化搜索，寻找跨任务/跨故障组合可泛化的恢复策略。必须与 EvoTool、EvoUndo、UndoBench/LIMBO、事务型运行时、标准 GP/EA 和形式化控制器合成基线做机制级对照。

## 1. 第一组：LLM Agent 工具调用故障、恢复与事务语义

### 1.1 UndoBench — Separating Task Competence from Recovery Capability in Tool-Using AI Agents (2026)
- 作者：Dolly Sah, Tanmay Sah, Harshul Jain, Tanya Sah
- 来源：arXiv:2610.05622，2026-10 预印本；尚按预印本处理。
- 链接：https://arxiv.org/abs/2610.05622
- 内容：36 个工作流、36 个故障场景、8 个企业域；使用相同 seed 的 counterfactual paired trials 和 effect-history/environment-state oracle；区分 nominal task competence 与 conditional recovery success。
- 关键报告：nominal competence 83.54%，conditional recovery success 46.72%；naive retry 的 duplicate external effect rate 53.33%。
- 直接相关：恢复能力单独评价、配对试验、工具状态副作用、lost acknowledgement。
- 重要细节：论文将 EvoUndo-RB1 作为恢复基线，但明确这是受 UndoBench 零权限约束的实现，没有远端状态探测或注册补偿处理器，不能当作完整 EvoUndo 的表现。
- 对本研究的约束：不能把“建立工具故障恢复 benchmark”作为主要创新；要比较更丰富的多工具状态机/多故障组合，并将算法搜索作为研究核心。UndoBench 对单条轨迹的故障注入主要为单次故障事件，其复合工作流不等于多故障级联。
- 优先精读：§3 Recovery Baselines、§4 Results、Appendix A/F、EvoUndo-RB1 的权限和补偿边界。

### 1.2 Where Does Exactly-Once Live? Model, Harness, and Tool-Contract Effects on Duplicate Side Effects in LLM Agents (2026)
- 作者：Jiapeng Li
- 来源：arXiv:2609.29095，2026-09 预印本；Microsoft Research 页面亦列出。
- 链接：https://arxiv.org/abs/2609.29095
- 内容：LIMBO 六个服务、十二种故障模式，25,930 episodes；研究 exactly-once 应由 model、harness 还是 tool contract 保证。
- 关键结论：当无即时读回且请求仍在飞行/可能重复投递时，仅靠 verification/waiting 无法保证 exactly-once；稳定 idempotency key 和 tool contract 很关键。
- 直接相关：timeout-after-commit、late commit、eventual consistency、missing read path、重复副作用。
- 对本研究的约束：恢复策略不能假设 read-after-write 总能判定隐藏提交状态；必须将工具可观察能力、幂等性和 in-flight bound 纳入策略输入/契约。

### 1.3 Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures (2026)
- 作者：Isham Kalappurackal Mansoor, Abhishek Phadke, Pratip Rana
- 来源：arXiv:2608.02645，2026 预印本。
- 链接：https://arxiv.org/abs/2608.02645
- 内容：对工具调用加入 postcondition verification、verify-before-retry 和 idempotency keys，针对 timeout-after-dispatch、delayed visibility、partial updates 等非原子故障。
- 直接相关：我们的 verify-before-retry / contract-aware 人工策略基线。
- 对本研究的约束：这些机制是强基线或可复用原语，不能作为独立算法创新。

### 1.4 Cordon — Semantic Transactions for Tool-Using LLM Agents (2026)
- 作者：Zheng Chen et al.
- 来源：arXiv:2606.17573，2026-06 预印本。
- 链接：https://arxiv.org/abs/2606.17573
- 内容：task-scoped semantic transaction；管理 effect lineage、shadow state、effect outbox、commit/rollback/recovery/audit。
- 直接相关：跨步骤副作用、提交边界、事务恢复。
- 区别：主要是事务运行时和 containment architecture，不是通过 EC 搜索恢复控制策略。

### 1.5 Atomix — Timely, Transactional Tool Use for Reliable Agentic Workflows (2026)
- 作者：Bardia Mohammadi, Nearchos Potamitis, Lars Klein, Akhil Arora, Laurent Bindschaedler
- 来源：2026 预印本/公开论文版本。
- 链接：https://arxiv.org/abs/2602.14849
- 内容：为工具调用引入 epoch、resource frontier、progress-aware commit；abort 时追踪并补偿外部化 effects。
- 直接相关：transactional retry、依赖关系、补偿和状态提交。
- 区别：运行时事务语义，不是策略种群演化。

### 1.6 SagaLLM — Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning (PVLDB 2025)
- 作者：Edward Y. Chang, Longling Geng
- 来源：Proceedings of the VLDB Endowment, 18(12), 4874–4886, 2025。
- DOI：https://doi.org/10.14778/3750601.3750611
- 内容：Saga transaction pattern、persistent memory、automated compensation、independent validation agents。
- 直接相关：多步骤工作流和逆序补偿。
- 区别：架构与执行流程设计，不是演化恢复控制器。

### 1.7 Repair Economics for Tool-Calling LLM Agents (2026)
- 作者：Heng Li
- 来源：Zenodo 2026-10-03，预印本，页面明确标注 not peer reviewed。
- 链接：https://zenodo.org/records/23117824
- 内容：四类任务、七类故障、六种恢复策略；确定性 fault injection、server-side state grading；另有 124 个 LLM episodes。
- 直接相关：与 Pilot A/A-2 的模拟器评估、retry/validate/transaction/idempotency 对照非常接近。
- 关键报告：其确定性实验中 idempotency 策略在 60 个适用单元中成功 48 次且零 duplicate side effects；论文还报告 response validation 可能诱发重复写入。
- 对本研究的约束：Pilot A-2 的 testbed/policy matrix 本身不能声称新颖；需要检查 A-3 多步骤、多故障、任务/故障联合 shift 是否超出已有基准，并且把重点放在 EA 机制而非故障场景数量。

### 1.8 FAILING TOOLS — Benchmarking LLM Agent Recovery Under Runtime Tool Failures (2026)
- 来源：OpenReview 上匿名 ACL submission；当前检索到的是匿名投稿稿件，不能按已接收论文引用。
- 链接：https://openreview.net/pdf/2be5795add6ec19f401efc71c99e69f5dea50e1c.pdf
- 内容：stateful multi-domain APIs；availability denial、staleness、silent no-op、corrupted state、schema mismatch、compound cascades；评价 detection、recovery strategy、safety、calibration。
- 对本研究的约束：多域故障注入和 compound cascades 也已有并行基准研究；需区分其 benchmark 与本研究的算法目标。

### 1.9 Loud Failures, Quiet Failures (2026)
- 作者：Obada Kraishan
- 来源：arXiv:2610.10062，2026 预印本。
- 链接：https://arxiv.org/abs/2610.10062
- 内容：工具显式错误、静默错误、schema drift 等情况下 Agent 是否发现故障、改变计划并恢复；1,920 trials / 24 multi-step tasks。
- 直接相关：失败检测和恢复行为分解。
- 区别：主要分析模型行为，不提出演化恢复控制器。

## 2. 第二组：LLM Agent 的演化策略优化与自我改进

### 2.1 EvoTool — Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection (ACL 2026)
- 作者：Shuo Yang, Caren Han, Xueqi Ma, Yan Li, Mohammad Reza Ghasemi Madani, Eduard Hovy
- 来源：ACL 2026 Long Papers，同行评审会议论文。
- 链接：https://aclanthology.org/2026.acl-long.2016/
- 内容：将 tool-use policy 分成 Planner、Selector、Caller、Synthesizer 四个 prompt 模块；用 trajectory-grounded blame attribution、feedback-guided targeted mutation、diversity-aware population selection 进行 gradient-free evolution。
- 直接相关：这是“用演化算法优化 LLM Agent 工具使用策略”的直接先行工作。
- 关键区别：EvoTool 进化的是自然语言模块 prompt；本研究候选进化的是带显式状态、动作、前置/后置条件、effect contract 的可执行 recovery FSM/program。该区别必须通过完整论文、代码和复现实验验证，不能只靠命名宣称。
- 对本研究的约束：blame-aware mutation、targeted mutation、diversity selection、通用 tool policy evolution 都不能再作为新颖性主张；EvoTool 必须进入强基线或适配基线。

### 2.2 GEPA — Reflective Prompt Evolution Can Outperform Reinforcement Learning (ICLR 2026)
- 作者：Lakshya A. Agrawal et al.
- 来源：ICLR 2026。
- 链接：https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html
- 内容：Genetic-Pareto prompt optimizer；使用轨迹、自然语言反思、prompt 更新与 Pareto frontier 组合经验。
- 区别：优化 prompt/系统级文本指令，不是契约约束的可执行恢复状态机。
- 对本研究的约束：不能声称“通过反思、Pareto archive 和 prompt evolution 改进 Agent”本身新颖。

### 2.3 EvoUndo — Recoverability-Constrained Self-Evolution for LLM Agent Harnesses (2026)
- 作者：Tanmay Sah, Dolly Sah, Harshul Jain, Tanya Sah
- 来源：arXiv:2608.28363，2026-08 预印本。
- 链接：https://arxiv.org/abs/2608.28363
- 内容：对 Agent harness 的 prompt/tool/middleware/config/resource 等自修改操作捕获 pre-state witness，合成 recovery program，并在 counterfactual harness states 上独立验证 recoverability。
- 关键语义：其 “self-evolution” 是 Agent harness 的自修改/升级过程，不等于 evolutionary computation 的 GA/GP 种群演化。论文将 forward mutation、witness、recovery program 和 effect contract 组合；修复回路主要由模型合成和 verifier feedback 驱动。
- 与本研究的区别假设：EvoUndo 关注“Agent 修改 harness 后能否恢复原状态”；本研究关注“Agent 在日常有状态工具工作流遭遇运行时故障时，如何选择 verify/retry/reconcile/compensate/escalate 等恢复动作”，并让 EC 搜索恢复控制器。
- 风险：两者都涉及 recoverability、effect contracts、counterfactual states 和 closed-loop repair，不能只用“我们使用 GA”作为充分差异；需要逐节比较其 effect semantics、policy object、search loop 和 verification protocol。

## 3. 第三组：演化计算与安全控制器合成

### 3.1 Formal Controller Synthesis via Genetic Programming (2017)
- 作者：C. F. Verdier, M. Mazo Jr.
- 来源：IFAC-PapersOnLine 50(1), 7205–7210, 2017。
- DOI：https://doi.org/10.1016/j.ifacol.2017.08.1362
- 内容：GP 与 SMT solver 结合，合成控制 Lyapunov function 和 switched state-feedback controller，并满足 reachability/safety specifications。
- 作用：证明 GP 可以用于带安全/可达性要求的可执行控制器合成。
- 区别：物理系统控制，不是工具 Agent 故障恢复。

### 3.2 Counterexample-Driven Genetic Programming: Heuristic Program Synthesis from Formal Specifications (Evolutionary Computation, 2018)
- 作者：Iwo Błądek, Krzysztof Krawiec, Jerry Swan
- DOI：https://doi.org/10.1162/evco_a_00228
- 内容：CDGP 用 SMT 对候选程序进行验证，将反例转成测试和 fitness，迭代搜索满足形式规格的程序。
- 作用：与“恢复轨迹/安全反例驱动策略演化”最相关的算法基础之一。
- 区别：通用形式化程序合成，未针对 LLM tool-effect contracts。

### 3.3 Automatic Synthesis of FSMs for Enforcing Non-functional Requirements on MPSoCs Using Multi-objective Evolutionary Algorithms (ACM TODAES, 2023)
- 作者：Khalil Esper, Stefan Wildermann, Jürgen Teich
- DOI：https://doi.org/10.1145/3617832
- 内容：使用多目标演化算法自动合成有限状态机 enforcer，以满足实时、能耗或安全等非功能要求。
- 作用：FSM + MOEA + requirement enforcement 已有先例。
- 区别：MPSoC resource/performance enforcement，不是工具调用恢复。

### 3.4 SMC-ES — Automated Synthesis of Formally Verified Control Policies (2026)
- 作者：Riccardo Curcio, Toni Mancini, Enrico Tronci
- 来源：arXiv:2607.15003，2026 预印本。
- 链接：https://arxiv.org/abs/2607.15003
- 内容：Evolutionary Strategies 与 Statistical Model Checking 结合；搜索 policy，并用统计模型检测验证性能、安全和鲁棒性，失败时生成反例继续改进。
- 作用：对“EA + statistical safety verification + counterexample feedback”是直接方法近邻。
- 区别：连续控制任务/神经网络策略，不是离散工具契约 FSM。
- 对本研究的约束：若提出安全约束演化机制，必须比较 SMC/CEGIS/形式验证反馈，而不是只比较 GA 和 NSGA。

### 3.5 Are Evolutionary Algorithms Safe Optimizers? (GECCO 2022)
- 作者：Youngmin Kim, Richard Allmendinger, Manuel López-Ibáñez
- DOI：https://doi.org/10.1145/3512290.3528818
- 内容：定义 Safe Optimization Problems，讨论不可逆安全约束下 EA 的风险，并比较 safe EA 与 safe GP 方法。
- 作用：安全约束不能简单折算成普通 fitness penalty；为硬约束门禁和安全优化基线提供方法论。

### 3.6 Verification-guided Programmatic Controller Synthesis (TACAS 2023)
- 作者：Yuning Wang, He Zhu
- DOI：https://doi.org/10.1007/978-3-031-30820-8_16
- 内容：VEL 将程序推理/验证反馈嵌入 programmatic controller synthesis，利用抽象验证的反例/安全损失指导控制器优化。
- 作用：反例引导的程序控制器优化近邻。
- 区别：使用梯度式优化和程序验证，不是 EC，不是 Agent tool recovery。

## 4. 可能的创新边界

### 4.1 不能声称新颖的内容
- “Agent 工具调用会超时并产生重复副作用”；
- “verify-before-retry 可以提高可靠性”；
- “通过 idempotency key 避免重复写入”；
- “Saga 逆序补偿”；
- “给 Agent 外围加 recovery controller”；
- “通过 GA/GP/NSGA 优化 Agent tool-use prompts”；
- “FSM 可被演化算法合成”；
- “使用形式验证/统计模型检测保障演化控制器安全”；
- “用失败轨迹做 targeted mutation”；
- “Agent self-evolution 需要 recoverability verification”。

### 4.2 值得进一步验证的具体算法假设
候选研究问题可以进一步收窄为：

**在工具具有异构 effect contract、观测不完备且故障可能跨步骤组合的情况下，如何设计契约语义保持的恢复控制器表示与反例驱动演化算子，使演化过程优先搜索安全可行策略，并提升未见任务/故障组合上的恢复成功率？**

候选方法机制（必须实验验证）：
1. **Typed Effect-State Genome**：状态、动作、工具契约和前置/后置条件具有类型；策略个体是可执行 guarded FSM，而非自由文本 prompt。
2. **Contract-Semantics-Preserving Variation**：变异/重组按 effect semantics 操作；对非幂等未知提交、不可补偿操作、saga dependency 等使用语义约束，而非事后仅用 penalty。
3. **Counterexample-Guided Evolution**：从失败 episode 提取最小状态/故障反例，生成定向但不泄漏 hidden oracle state 的变异目标；与 EvoTool 的 prompt blame/targeted mutation 区分。
4. **Feasibility-First Selection with Safety Evidence**：critical invariant violation 作为硬可行性条件；在可行策略中再优化 recovery success、unresolved effects、cost 和 worst-group generalization。
5. **Cross-Family Generalization**：按任务族与故障组合族双重 held-out，防止记忆训练轨迹。

这些机制的组合目前只是待验证假设。FSM、contract、counterexample、feasibility-first、multiobjective selection 单独都已有先行研究；必须通过机制消融和强基线证明具体组合有不可替代的收益。

## 5. Pilot A-3 与文献的关系及修订要求

- Pilot A-3 的状态化多工具任务、故障注入、held-out 设计可以继续作为内部算法验证环境。
- 不应声称 A-3 的故障模拟器/恢复 benchmark 本身具有强新颖性；UndoBench、LIMBO、Repair Economics、FAILING TOOLS 已覆盖相近主题。
- A-3 的 compound fault / three-step saga / per-tool independent fault / task × composition joint shift 可能提供有用的实验难点，但必须与已有 benchmark 做 feature-level comparison。
- Pilot B 必须加入 EvoTool（可做适配基线）、verify-before-retry、idempotency/transactional runtime policy，以及 standard GP/CDGP-inspired/GA/NSGA baselines。
- 还应考虑与 SMC-ES/CEGIS-style counterexample-guided verification 思路对照。
- 在完成机制级审查前，不得冻结“contract-aware EA”作为最终创新方法名称。

## 6. 必须精读顺序

1. UndoBench (arXiv:2610.05622)：恢复基准、EvoUndo-RB1、指标与限制。
2. EvoUndo (arXiv:2608.28363)：recoverability、effect contract、counterfactual verification、recovery synthesis。
3. EvoTool (ACL 2026)：evolutionary tool-use policy、blame mutation、diversity selection。
4. Where Does Exactly-Once Live? (arXiv:2609.29095)：late commit、idempotency、工具契约边界。
5. Cordon / Atomix / SagaLLM：事务与补偿机制的系统基线。
6. CDGP (2018)、Formal Controller Synthesis via GP (2017)、FSM-MOEA (2023)、SMC-ES (2026)：算法机制基础。
7. Repair Economics (2026) 与 FAILING TOOLS submission：确认 A2/A3 benchmark overlap。

## 7. 本轮结论

**GO：继续研究第一项候选，但必须重构创新表述并进行机制级 novelty audit。**  
**HOLD：不能声称“契约约束恢复策略演化”已经新颖，也不能仅凭 A3 结果进入论文创新定稿。**  
**NO-GO：通用 Agent prompt evolution、verify-before-retry、Saga compensation、通用 FSM/安全 EA 不能单独作为创新。**

本次检索属于初步检索，不是系统综述；尚需扩展 Google Scholar / Semantic Scholar / OpenAlex / DBLP / ACM / IEEE / ACL / arXiv 的关键词和引用链检索，并检查每篇全文与官方代码。
