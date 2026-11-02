# 05 — 研究决策日志

## 2026-11-02：项目启动与研究边界锁定

### 决策 D-001：唯一仓库

用户指定 https://github.com/yujian777555/kaitibaogao 作为本次开题研究唯一仓库。后续不读取其他 GitHub 仓库，不将其他项目混入本项目。

### 决策 D-002：研究主线

研究方向锁定为 Evolutionary Computation for AI Agents：演化计算是核心优化方法，Agent 是优化对象。LLM for EC 不作为本课题主线。

### 决策 D-003：开题要求

根据用户提供的河北工业大学开题报告模板，硕士正文不少于 6000 字、参考文献不少于 30 篇、外文不少于 30%、近五年文献不少于 30%，并覆盖模板规定的研究内容和排版要求。

### 决策 D-004：不提前确定题目和创新点

首轮检索已发现多个直接相关的 2025–2026 论文。当前不锁定最终题目，不宣称创新点已经成立。先完成机制级精读、重复风险审查和可证伪实验设计。

### 决策 D-005：必须区分两篇 EvoMAS

- Hu et al. (ICML 2026), Evolutionary Generation of Multi-Agent Systems；
- Wei et al. (ICML 2026), EvoMAS: Heuristics in the Loop—Evolving Smarter Agentic Workflows。

二者是不同论文，不能混为一谈。

### 决策 D-006：当前候选

优先审查：
- A：任务分布泛化 + Quality-Diversity 演化；
- B：执行过程归因 + 演化选择/变异；
暂缓：
- C：Agent 与演化算子协同适应，因为 Wei et al. 的 EvoMAS 已直接研究多策略和自适应策略选择。

### 决策 D-007：创新性判断规则

以下内容不能单独作为创新：
- 把 NSGA-II/III 接到 Agent 上；
- 普通 Pareto 多目标选择；
- 使用执行反馈引导变异；
- 采用四模块 Agent 编码；
- 仅增加反思、经验记忆或变异提示词；
- 仅提出动态算子选择。

必须提出具体机制差异、数学定义、实验假设和反例/停止条件。

## 下一次决策前必须补充的证据

1. 核心论文的算法细节、伪代码和消融；
2. 候选 A/B 的完整相关工作覆盖；
3. 与最强基线的可复现比较方案；
4. 数据集和 held-out task family 的可行性；
5. 每个创新点如何单独验证和如何形成递进关系。


## 2026-11-02 第二轮：新增 EvoTest 作为优先切入证据

### 论文事实
精读 EvoTest（ICLR 2026）正文方法与局限性章节。其 Agent 配置为 χ=(p,M,h,u)，以 Actor/Evolver 分离完成 episode-to-episode 更新，使用父代+子代候选池和 UCB 选择。J-TTL 基准包含六款 Jericho 游戏，每款 session 连续 50 个 episode，单个 episode 通常上限 110 步。

### 原文局限
作者明确指出 (1+m)+UCB 较简单，可能局部最优；同一任务中的策略存在任务特定过拟合；建议未来研究更复杂的种群 EA、QD 和程序综合。

### 新增直接/相邻文献
COvolve（GECCO 2026）、CATArena（ICML 2026）、M*（NeurIPS 2026）、E-SPL（ICML 2026 FoGen workshop）、INSPO、SkillRL、EvoTeam、Evolving Agent Teams、EvoMemBench、EvoSkills、MemEvolve、MemSkill、Live-Evo、AgentFactory、AgentEvolver、EvoFSM、Dr. Zero、MIA、ACE。

### 决策 D-008
新增候选 D：跨任务序列的演化测试时自适应。当前优先级高于 A/B/C，但未批准为最终方向。

### 决策 D-009
候选 D 不得简化为“把 (1+m) 换成 NSGA-III / MAP-Elites”。必须明确任务分布变化、行为描述符、档案迁移和 held-out 验证机制，并与 M*、MemEvolve、E-SPL、INSPO、COvolve、EvoTeam、HFlow、EvoMAS 比较。

### 决策 D-010
新增文献记录 51–72。文献总表目前为 72 条登记记录，仍非穷尽清单；下一轮必须继续追踪综述引用和国内研究。


## 2026-11-02 第三轮：直接工作密集出现，重审候选

### 新增文献
本轮新增 MOAE、SkillMOO、MOCHA、ParetoPO、AgentBreeder、TTHE、Meta-TTL、TacoMAS、Inherit-MAS、EvolveNet、CPE、DarwinX、AHE、RQGM、Certified Selective Automation、Calibrating the Evaluator、Self-Reports Are Not Verification、HGM、PCE、FreeEvolve、Group-Evolving Agents、HERA、HiveMind、FlowReasoner、TOA、SERO、Evolvability Search、Evolvability ES、噪声适应度优化综述和 F-Race 等文献。

### 决策 D-011：候选 D 宽泛表述 NO-GO
TTHE、Meta-TTL、TacoMAS、Inherit-MAS、EvolveNet、DarwinX 已直接覆盖跨任务测试时 Agent/harness 演化。EvoTest 保留为基础论文，但不再以“跨任务测试时演化”作为创新。

### 决策 D-012：普通多目标/技能/角色/可进化性优化不构成独立创新
MOAE、SkillMOO、MOCHA、AgentBreeder、HGM、PCE、FreeEvolve、SERO 等已覆盖这些方向的多个关键机制。

### 决策 D-013：新增候选 G 优先审查
组件交互感知的演化重组：通过配对反事实干预估计 Agent 配置组件之间的 epistasis/linkage，再指导遗传重组，重点解决现有方法的泛化 crossover / additive merge 未显式建模组件协同和拮抗关系的问题。

### 决策 D-014：候选 G 尚未通过审查
必须精读 EvoMAS、HFlow、AgentSquare、AgentBreeder、DarwinX、SERO、HiveMind、EvoCF、Optimas，确认是否已有等价机制；必须把反事实估计误差和执行成本纳入可行性判断。


## 2026-11-02 决策 D-015：确立硕士论文 2–3 创新点与独立投稿约束

用户明确要求：硕士论文必须有 2–3 个创新点，每个创新点分别形成一篇小论文投稿。该要求作为项目硬约束。

### 总题目工作稿调整
由较窄的“面向大语言模型智能体的交互感知演化重组方法研究”调整为更能覆盖完整论文的：

**《面向大语言模型智能体的交互感知演化优化方法研究》**

### 规划的三层研究
1. 任务条件化 Agent 组件交互效应估计（独立估计器论文）；
2. 交互感知演化重组算子（独立 EC 算法论文）；
3. 任务分布变化下交互结构迁移与自适应演化（条件性第三篇）。

当前目标是争取三篇，但至少必须保证前两篇各自具备独立算法贡献和独立实验。第三篇必须通过新颖性与独立性 Gate，不能为了数量凑数。

### 新增相关工作带来的限制
- MESH-Harness 已做模块槽位组合、full-covariance LinUCB、coordinate ascent 和 trace-driven module evolution；其预测均值为 additive，full covariance 主要用于共同出现统计/不确定性，需精确区分。
- ARTEMIS 已做 semantic-aware genetic operators 和 Agent 配置联合演化。
- EvoMAS 已做结构化配置空间中的反馈引导 mutation/crossover。
- AgentEvo 已做多阶段 workflow evolution、subgraph graft、prompt fusion 和 Pareto cost-performance。
- Evo-Harness 已做上下文到技能 harness 的在线编译与跨任务使用。

因此候选 G 不能未经审查直接升级为创新点二；创新点三也必须区别于 Evo-Harness、TTHE 等工作。


## 2026-11-02 决策 D-016：普通组件交互估计 NO-GO

新增直接工作：
- Liu (2026), More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding, arXiv:2605.05716：32 种组件组合、Shapley、pairwise regression 和探索性三阶交互；
- Lauziere et al. (2026), A Regression Framework for Understanding Prompt Component Impact on LLM Performance, EXPLAINABILITY 2026。

原创新点一若只是“组件交互效应估计/差分公式/交互图”，已经不足以构成独立创新。且 CCI 论文中 pairwise model 的 LOOCV 低于 main-effects model，提示简单加交互项可能过拟合。

**决策：原表述 NO-GO；修订后的预算受限、任务条件化稀疏交互发现 HOLD。**

## 2026-11-02 决策 D-017：交互驱动的约束最优混合演化 HOLD / 优先预实验

AgentSquare、ARTEMIS、Hu-EvoMAS、Wei-EvoMAS、AgentEvo、HFlow 已覆盖大量 Agent crossover/模块重组；GOMEA/LTGA/CGOMEA/DSMGA-II/LK-GOMEA 已覆盖经典 linkage learning 与 optimal mixing。

仅在提出并验证适用于 Agent 混合类型、接口/控制流依赖、随机昂贵 fitness 的实质新机制时才可能成立。不得直接把 GOMEA 套到 Agent 配置后宣称新算法。

## 2026-11-02 决策 D-018：第三创新点暂缓

跨任务 linkage 迁移与 LK-GOMEA、HFlow、EvoMAS curriculum、Evo-Harness、TTHE 等有交叉，尚未证明独立科学问题。暂不写入正式创新点，等待前两项预实验显示跨任务结构规律后再评估。

## 2026-11-02 决策 D-019：核心产出目标调整

以 **2 个核心创新候选 + 1 个有条件的扩展方向**推进。Paper 1 和 Paper 2 各自必须具备独立方法贡献和实验；第三篇不是当前承诺。完整可行性矩阵与实验 Gate 见 11_INNOVATION_FEASIBILITY_AUDIT.md。


## 2026-11-02 决策 D-020：演化参数采用离线+在线两层调节

确定主方案：
- 离线：训练任务上使用 irace/iterated racing 调节少量数值与类别超参数；
- 在线：使用 discounted-UCB/AOS，根据配对改进的置信下界和 rollout 成本，调整变异强度与算子选择；
- 统计门禁：\(\alpha\)、\(\delta_{\min}\) 和硬约束预先锁定，不进入性能调参。

主算法是 categorical GOM，不移植 DE 专属 \(F,CR\)。第一阶段固定种群 \(N=8\)，敏感性比较 \(N=4,8,12\)，后续再比较 IMS/P3。在线 AOS 不是独立创新，若不优于离线调参固定策略则删除。

详细参数定义、范围、公式、消融和停止条件见 13_EC_PARAMETER_CONTROL_PLAN.md。


## 2026-11-02 决策 D-021：正式算法设计 V1 与 FOS 规则纠正

新增 14_FORMAL_ALGORITHM_DESIGN_V1.md，定义：
- Paper 1 TCAIL：Group-ARD task-conditioned interaction model、legal-space identifiability、interaction-only posterior IG active design；
- Paper 2 CI-GOM：interaction FOS、contract-aware minimal repair、posterior-aware donor、paired sequential acceptance、可选 discounted-UCB action control。

**纠正旧规则：** linkage 反映非加性依赖，不以交互正负号决定是否建边。V1 使用 \(P(|\Delta_{ij}|>\delta_{\mathrm{link}})\) 建边，正负符号用于 donor scoring；负交互不是硬约束。

当前状态仍为 HOLD / SPECIFICATION ONLY。下一步先实现 Phase 0 合成地形和算法模拟器，完成真值恢复与同预算消融，不调用真实 LLM。


## 2026-11-02 决策 D-022：CI-GOM 序贯接受采用跨 proposal 的 alpha spending

CI-GOM 不只存在单个 proposal 内的 repeated looks，也会在整个演化运行中连续检验多个 offspring。故不能对每个 offspring 都重复使用同一个 alpha。正式方案采用 proposal index \(k\) 与 within-proposal look \(n\) 两层 alpha spending，控制跨 proposal 与序贯查看的累计错误率。任务块相关时必须以 task family/cluster 为独立统计单位。详细公式见 14_FORMAL_ALGORITHM_DESIGN_V1.md。


## 2026-11-02 决策 D-023：三个创新点按顺序独立验证，暂停大论文写作

用户明确决定：不先写毕业大论文，而是依次验证每个创新点。

执行顺序：
1. TCAIL：先做规格/统计审计，再做合成真值实验、强基线比较、消融和真实 Agent 验证。Gate-1 通过才进入下一项。
2. CI-GOM：先 Oracle linkage 上界，再 contract repair、donor、sequential acceptance 消融，最后 learned linkage 同预算端到端验证。Gate-2 通过才进入下一项。
3. 跨任务迁移：验证共享交互结构是否真实存在，再比较 from-scratch、direct transfer、selective transfer。Gate-3 未通过就删除第三创新点。

暂停硕士大论文正文撰写；不将尚未验证的算法包装成已确认创新。开题准备后续以真实研究证据为基础组织。合成实验通过不是论文成立的充分条件，必须有可信真实 Agent 任务验证。

权威协议：15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md。本决策覆盖旧 handoff 中“同时实现两个算法 Phase 0”的任务顺序。


## 2026-11-02 决策 D-024：TCAIL 首轮规格审计 REQUEST REVISION

对 14_FORMAL_ALGORITHM_DESIGN_V1.md 的 TCAIL 部分完成纸面数学/统计审查，详见 16_TCAIL_SPECIFICATION_AUDIT_R1.md。

主要阻塞：
1. pairwise contrast 依赖其他槽位背景，estimand 未定义；
2. 当前样本秩不足与合法空间结构性不可识别混淆；
3. Bernoulli/Beta likelihood 与 Gaussian posterior rank-one IG update 未统一；
4. edge threshold 缺少可执行的整体 FDR/BFDR 控制；
5. interaction-only IG 是 Bayesian D-optimal 子空间信息增益，需加入严格匹配的强基线；
6. 4-slot/16-config 只够 debug，需增加更大空间；
7. 三阶失配与 pairwise marginal edge 的含义需区分。

**决定：当前不启动正式 Phase 0 性能实验。先修订 TCAIL 规格并复审。** 没有实验结果，Gate-1 仍未通过。
