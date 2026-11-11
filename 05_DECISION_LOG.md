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

## 2026-11-02 决策 D-025：TCAIL V2 完成纸面修订，等待独立复审

新增 17_TCAIL_FORMAL_SPECIFICATION_V2.md，作为 14_FORMAL_ALGORITHM_DESIGN_V1.md 中 TCAIL 部分的替代规格；新增 18_TCAIL_RELATED_WORK_AUDIT_R1.md。

V2 修订：
1. 定义 link-scale 条件交互及 reference-background 平均交互，并报告背景异质性；
2. 明确共同四格合法支持；
3. 区分 IDENTIFIABLE、PENDING_SUPPORT、STRUCTURALLY_NOT_IDENTIFIABLE、STRUCTURAL_STATUS_UNCERTIFIED；
4. 分别定义 Gaussian、Bernoulli logistic、Beta likelihood 与 Fisher information；
5. Gaussian ARD 闭式更新不再套用到非 Gaussian likelihood；
6. 明确 Bayesian FDR；
7. 将 interaction-subspace IG 明确归为 Bayesian D-optimal 基线；
8. 增加 edge-decision risk reduction 候选 acquisition，但不宣称该目标本身新颖；
9. 4-slot 仅作 debug，扩展 8/10/12 slots；
10. 增加 additive/null、three-way-only、高阶和约束空间场景。

相关工作审查确认：Agent 组件交互回归、全因子分析、交互 group screening、Bayesian OED/FDR、Agent harness 预算优化均已有先例。TCAIL V2 新颖性仍未成立，当前只是条件性候选。

另记录 EC 主线约束：TCAIL 本身是统计/实验设计模块，不是完整 EC 算法。只有后续证明其结构信息能够改善演化搜索，才可纳入 EC 主线创新证据。

**当前决定：V2 只进入独立规格复审，不进入代码实现或正式性能实验。**

## 2026-11-02 决策 D-026：TCAIL V2 第二轮复核 REQUEST CHANGES

第二轮数学复核详见 19_TCAIL_V2_SECOND_PASS_REVIEW_R1.md。Beta Fisher information、Gaussian posterior update、row-space estimability 和 Bayesian FDR 形式基本正确；但仍有五项需要闭合：
1. 高阶模型失配必须进入主要边估计的 M2/M3 sensitivity gate；
2. 显式构造 reference-standardized contrast vector l_e；
3. 连续 task context 的 BFDR 必须限定在预注册有限 anchor set；
4. edge-risk acquisition 必须规定 posterior MC、refit、Monte Carlo SE 和候选间 common random numbers；
5. 预算百分比的 full-factorial denominator 必须精确定义。

已将澄清写入 17_TCAIL_FORMAL_SPECIFICATION_V2.md 第 12 节。当前仍不实现、不跑正式 Phase 0。需要对修订后的 V2.1 再做独立复审。

## 决策 D-027：将每轮仓库维护设为强制流程（2026-11-02）

用户明确要求后续研究不能只在聊天中推进，必须持续维护唯一毕业论文研究仓库 yujian777555/kaitibaogao。

已新增 REPOSITORY_MAINTENANCE_POLICY.md，并在 README.md 与 SESSION_HANDOFF.md 中登记。每轮开始核对远端状态、读取项目上下文；每轮结束更新研究记录、项目状态、决策日志和完整接班提示词；提交推送后复核远端 HEAD 与关键文件。若推送/核验失败，必须如实报告。

项目隔离规则继续有效：kaitibaogao 不与 openissue、agentfotagent、GLEPPO 等独立项目混用。

## 决策 D-028：TCAIL V2.1 第三轮独立复审 REQUEST CHANGES（2026-11-02）

复审报告：20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md。

V2.1 对第二轮提出的五项规格缺口做了实质补充。以下数学检查通过：reference-standardized contrast vector 在固定线性 predictor basis 下成立；固定 Beta concentration 的 Fisher information 正确；线性 contrast 的 row-space 判据正确；posterior local null probability 校准且检验族固定时，BFDR 基本公式正确。

但规格仍未达到可实现状态，主要阻塞：
1. 当前边假设检验的是 reference-background 平均有符号交互，可能因背景符号抵消而漏掉对演化 linkage 有意义的条件依赖；背景异质性尚未进入边决策。
2. M2/M3 gate 未进入算法伪代码和状态机；M3 仅含三阶项，无法排除四阶及以上失配；strong-heredity 定义可能与 three-way-only 测试场景冲突；M2/M3 最终 posterior/BFDR 规则未定义。
3. acquisition 的逐边 Bayes classification risk 与最终全局 BFDR 选择规则不一致。
4. task-block 的跨配置配对、随机种子、任务内相关、随机效应及 cluster posterior/calibration 尚未形成可执行统计模型。
5. Beta concentration κ 未知时的联合 nuisance posterior/Fisher 处理未定义；Gaussian 方差也需明确冻结或估计方案。
6. identifiability 需按 model basis × anchor 构造 legal/observed design matrix，并区分代数可识别与 GLM practical weak identification；低共同支持 abstention 规则未定义。
7. BFDR 检验族在 task-family × pair 与 pair × anchor 两种索引之间不一致。
8. full-factorial task-block 计数只有在等成本协议下才等价于 rollout-equivalent budget。

新颖性与 EC 定位仍未成立：TCAIL 是统计建模/主动实验设计模块；Group-ARD、Bayesian OED、BFDR 和 decision-theoretic acquisition 均有成熟先例。只有证明其对后续 GOM linkage/mixing/search 带来独立收益，才能闭合 EC 主线。当前不能把 TCAIL 写成已成立的独立创新点。

**决定：TCAIL 保持 HOLD / SPECIFICATION REVISION REQUIRED；IMPLEMENTATION BLOCKED。** 本次不是算法实验失败，因为尚无代码和实验。下一轮只按 20 号报告修订规格；修订后再独立复审。CI-GOM、第三项迁移、正式 Phase 0、真实 LLM 和大论文正文继续冻结。


## 决策 D-029：修正 TCAIL 与 GOMEA linkage 的接口定义（2026-11-02）

新增审计与提案：
- 21_GOMEA_LINKAGE_AND_NOISY_INTERACTION_RELATED_WORK_AUDIT_R1.md；
- 22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md；
- 文献总表新增 P125–P132。

本轮核查后，修正上一轮过于粗略的表述：GOMEA linkage 并非单一概念。标准 SLL 常由种群 MI 学习；fitness-based linkage 则通过目标函数差分估计变量依赖，已有 RV-GOMEA、conditional FOS、DLED/cDLED 等直接先例。因此“fitness interaction 与 GOMEA linkage 无关”不准确，但“平均统计交互图可直接作为 FOS”同样不成立。

发现的重要先行工作：
- Olieman et al. 2021：fitness-based linkage learning in RV-GOMEA；
- Andreadis et al. 2024：fitness-based linkage + maximum-clique conditional linkage；
- Przewozniczek et al. 2021/2025：DLED / cDLED，后者处理 individual-specific multi-structured linkage；
- Zhong et al. 2023/2024：LMM 与 ALI/AIM，已研究噪声下 linkage decomposition；
- Tinós et al. 2026：从 GA 搜索过程副产物学习变量交互；
- Guijt et al. 2022：Linkage Kernels，为每个解学习局部 linkage。

因此 TCAIL 的原始平均有符号 contrast 不能直接作为通用 linkage edge。22 号提案建议：
1. 在实际 objective utility scale 上定义局部四格 fitness contrast；
2. 用 global RMS interaction energy 描述任务条件化的总体依赖强度，但不直接将其作为当前 parent 的 FOS edge；
3. 对当前 parent 和 task context 估计 local posterior linkage evidence；
4. 输出 local weighted VIG，再通过预注册的 LT / conditional FOS builder 转换为 FOS；
5. 比较 FBL、DLED/cDLED、LMM、ALI/AIM、SLL-MI、在线副产物式交互学习。

该方向可能的差异只在于随机昂贵 Agent rollout、任务异质性、合法配置约束、task-block 后验校准和主动预算的联合处理。噪声 linkage、conditional linkage、fitness-based linkage 均已有先例，不能单独宣称创新。

**决定：** 接受 21 号审计结论；22 号仅作为 B1 修订提案，尚未并入权威规格。TCAIL 仍 HOLD / IMPLEMENTATION BLOCKED。B2–B8 继续有效；不实现、不跑正式 Phase 0、不调用真实 LLM。CI-GOM 和第三项迁移继续冻结。需要先对 22 号提案独立复审，再决定是否整合进 V2.2。


## 决策 D-030：先形成硕士开题报告初稿 V0.1（2026-11-02）

用户明确要求先完成开题报告初版，暂停继续扩展算法研究计划。已新增 \`23_OPENING_REPORT_DRAFT_V0_1.md\`。

### 初稿定位

- 工作题目：《面向大语言模型智能体的交互感知演化优化方法研究》；
- 主线：Evolutionary Computation for AI Agents，演化计算为核心方法，Agent 为优化对象；
- 两个核心研究内容：任务条件化组件交互结构估计；交互结构驱动的 Agent 约束最优混合演化；
- 第三个方向：任务分布变化下交互结构迁移，仅作为条件性扩展；
- 参数调节：irace 离线配置 + discounted-UCB/AOS 在线控制候选 + 预先固定统计门禁；
- 初稿按学校模板列出 44 篇参考文献，并将研究内容、关键问题、算法、实验和停止条件建立对应关系。

### 真实性与状态边界

1. TCAIL 规格仍未通过独立复审，B1 linkage 接口提案待审；不能写成已完成算法。
2. CI-GOM 尚未实现、尚未实验；只能写为拟研究方法。
3. 第三项跨任务迁移未通过独立新颖性 Gate；不能承诺一定形成第三篇。
4. 当前课题没有正式 Phase 0 或真实 Agent 实验结果；研究基础章节已如实说明。
5. 没有混入其他独立项目的代码、实验或成果。

### 下一步

先根据导师反馈修订报告初版，再核对参考文献和格式。用户当前优先级是开题报告初版，不要自动切回继续扩展算法规格。


### D-030 补充：引用校对与 Word 初稿（2026-11-02）

- 参考文献由 44 条扩展为 50 条，补入 Optimas、HiveMind、CCI、Prompt component regression、MESH-Harness、ARTEMIS；
- 修正组件贡献与交互研究段落中 Optimas/HiveMind/CCI/Prompt 回归的引用编号；
- 补充 NSGA-II、MOEA/D、MAP-Elites、噪声演化优化综述和 F-Race 的正文引用；
- 已生成按 A4、宋体小四、1.5 倍行距排版的 Word 初稿，封面个人信息保留待填写项。


## 决策 D-031：开题报告 V0.2 文献核验与国内研究补充（2026-11-03）

用户提供的最新交接记录要求优先完成开题报告初版修订。本轮核对发现 V0.1 的正文已实际引用 [1]–[50]，但自检仍写 43 篇；[44]–[50] 还位于自检段落之后；Agent 自动设计基线重复列举 ARTEMIS。已在 V0.2 中修正结构与统计。

本轮补入国内研究代表性来源（自主 Agent 综述、智能体产业实践、教学 Agent、垂直领域 Agent 设计、电力仿真技能库），并补入国内研究团队的 MAESD 和反向方向 BIOME。新增 2026 直接相关工作 AHE、SkillFlow、ShapleyFlow、FusionFlow，分别覆盖 harness 演进、技能递归演化、组件交互归因和 workflow fusion。

关键判断：
1. [50] 的题名为 Evolving Excellence，正文将其框架称为 ARTEMIS，ARTEMIS[50] 的引用对应正确；V0.1 问题是重复列举，不是编号错配。
2. ShapleyFlow 提高了组件交互归因创新门槛；FusionFlow 提高了 workflow recombination 创新门槛；AHE/SkillFlow 提高了 Agent harness/skill evolution 创新门槛。
3. 普通组件交互估计仍 NO-GO；TCAIL 修订候选仍 HOLD；CI-GOM 与第三项迁移继续冻结。
4. 参考文献扩充至 61 条，正文引用编号完整匹配；但全量 GB/T 7714 最终审计尚未完成，不能声称 61 条全部通过。
5. 本轮无代码实现、无 Phase 0、无真实 LLM 调用、无新的算法 Gate 结果。

新增文件：24_REFERENCE_AUDIT_AND_DOMESTIC_RESEARCH_R1.md、25_OPENING_REPORT_DRAFT_V0_2.md。原始 V0.1 保留不覆盖。

## 决策 D-032：Word V0.2 初稿生成（2026-11-03）

已基于原学校模板 Word 文件生成 `河北工业大学硕士开题报告_初稿V0.2.docx`。Word 正文非空白字符约 22,808，参考文献编号 [1]–[61] 连续；格式沿用 A4、宋体小四、1.5 倍行距。Word 版已纳入国内研究现状和 AHE、SkillFlow、ShapleyFlow、FusionFlow 等新增工作。

限制：本轮完成了章节和引用层面的同步，但尚未进行 Word 与 Markdown 的逐段逐字比对；61 条文献也未全部完成最终 GB/T 7714 审计。该文件尚未作为二进制文件提交到 GitHub，仅作为本轮会话附件供下载。研究算法 Gate 状态不变。


## 决策 D-033：AHE 原文复核与多种子实验要求（2026-11-03）

对 AHE（arXiv:2604.25850）原文 PDF 复核确认：论文报告的是单次十轮演化 campaign；其主要发现包括组件非加性交互、有效组件收益不能简单相加，以及自归因对修复比对回归更可靠。该工作进一步说明本课题不能只做单次运行或最佳运行比较。后续 TCAIL/CI-GOM 实验必须采用多 seed、配对任务实例、同 rollout budget，并同时报告修复/回归和统计不确定性。创新状态不变：普通交互估计 NO-GO，TCAIL HOLD，CI-GOM 冻结。


## D-034：RSI 主线与三个研究方向（2026-11-03）

根据导师意见，论文工作题目调整为《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》。研究范围限定为冻结基础 LLM 的 Agent 系统级 RSI；Agent harness 和模块配置作为演化对象，演化计算负责种群搜索、交互结构利用、约束重组和跨轮次选择。

三个候选创新点：
1. RSI 轨迹驱动的任务/父代条件化组件交互结构学习；
2. 交互感知的类别型 Agent 约束最优混合演化；
3. 跨轮次交互记忆、结构漂移检测、linkage block 条件化迁移和保留能力约束演化。

新增文献 P143–P149 已登记。CPE、HarnessEvolve、EvolveNet、DGM、ReasoningBank、GEPA、Meta-Harness 和两篇持续 RSI 研究提高了第三项的新颖性门槛。第三项不能只做普通记忆库、档案或性能回归门；在线算法不得读取 task-family 标签或任务流 block 边界。

报告和设计文件：27_OPENING_REPORT_DRAFT_V0_3_RSI.md、26_RSI_THREE_INNOVATION_RESEARCH_DESIGN_R1.md、28_RSI_CONTINUAL_RESEARCH_AUDIT_R1.md。

算法状态未改变：TCAIL V2.1 REQUEST CHANGES；22 号接口提案待独立复审；CI-GOM 未实现；第三项尚无正式算法规格。

## D-035：IMCE-RSI 第三创新点采用双键交互记忆检索（2026-11-03）

在补充审查 arXiv:2610.25858 后，发现仅靠 query similarity 的历史经验检索会出现 retrieval collision。第三创新点进一步收敛为双键检索：一是由输入、工具 schema、环境元数据和可观察轨迹构成的上下文键；二是由局部交互后验、交互方向、不确定性、共同支持和 FOS 构成的交互键。若语义相似的记忆对应冲突的交互结构，则标记 collision；高不确定性时有限探测或 abstain；只有迁移收益置信下界为正且保留能力约束通过，才允许作为 GOM donor。

在线算法不得读取 task-family labels 或任务流 block boundaries；它们仅用于离线评估。SWE-bench Verified 作为首个真实编码 Agent 主平台，SWT-Bench 和 FeatureBench 作为连续任务流候选。

此为待验证机制，不代表创新已成立。需与 ReasoningBank、GEPA、Meta-Harness、DGM、CPE、HarnessEvolve、EvolveNet 比较。

## D-036：三个 RSI 创新点参数调节与实验 Gate（2026-11-03）

新增 29_PARAMETER_TUNING_AND_EXPERIMENT_GATES_R1.md，分别定义 TCAIL、CI-GOM、IMCE-RSI 的参数组、调节顺序、同预算基线、A800 轻量迁移预测器训练条件和停止规则。原则为先离线调参、后在线控制；硬约束 fail-closed；task-family labels 和 stream boundaries 不作为在线输入；训练/验证/测试隔离。该文件仅为实验设计，不授权 Phase 0、API 调用或 GPU 训练。

## D-035：生成 RSI 开题报告 Word V0.3 工作初稿（2026-11-03）

已使用河北工业大学原始 Word 模板的 V0.2 工作副本生成 `河北工业大学硕士学位论文开题报告_V0.3_RSI_初稿.docx`。主要完成封面/页眉、RSI 研究现状、三项研究内容与创新点、IMCE-RSI 候选算法、SWE-bench Verified 任务平台、跨轮次评价、进度表和 68 条参考文献。

结构验收：DOCX 可重新打开；A4；Normal 样式宋体 12 pt、1.5 倍行距；2 个模板表格保留；68 条参考文献编号连续；关键 RSI 标题和 task-free 限制存在。

**边界：** 这是可供导师审阅的工作初稿，不是最终提交版；Word/Markdown 逐段一致性和 68 条书目元数据/GB/T 7714 审计尚未完成。构建细节见 `30_WORD_V0_3_BUILD_REPORT.md`。

算法状态没有改变：TCAIL V2.1 REQUEST CHANGES；22 号 Linkage/FOS 接口提案待独立复审；CI-GOM 未实现；IMCE-RSI 无正式规格；无 Phase 0、真实 API 实验或 GPU 训练。


## D-037：TCAIL Linkage Interface 独立复审 R2（2026-11-03）

审查 22 号 B1 proposal 后决定：**B1_PARTIALLY_ACCEPTED；TCAIL overall 仍 HOLD / IMPLEMENTATION BLOCKED。**

接受的方向：把条件 fitness interaction、global RMS interaction energy 和 parent/task local linkage posterior 分开；objective-scale local finite difference 比 reference-background average signed contrast 更适合表达当前 parent 下的非加性依赖；VIG 不等于 FOS。

未关闭的关键点：q 是 edge evidence probability，不是 FOS clustering strength；必须分别定义 `δ_local`、`τ_edge` 和连续 FOS weight，并冻结 FOS builder；B2–B8（M2/M3、高阶、BFDR/acquisition、task-block、nuisance、practical identifiability、检验族、预算）仍需规格闭合。

外部核验的直接先行工作新增 P150–P153：Olieman et al. 2021 FBL、Dushatskiy et al. 2024 CGOMEA、Przewozniczek et al. 2025 cDLED、Tinós et al. 2026 GA-side-effect interaction learning。故 TCAIL 不得将 fitness-based、conditional/local linkage 或从 GA 轨迹副产物学习交互本身作为新颖性主张。

新增文件：`31_TCAIL_LINKAGE_INTERFACE_INDEPENDENT_REVIEW_R2.md`、`32_TCAIL_V2_2_SPEC_REVISION_TASK_R1.md`。下一步仅允许形成新的 V2.2 规格草稿和 B1–B8 closure matrix；不修改 17 号权威历史规格，不编码、不调用 API、不启动 Phase 0、不训练模型。


## 决策 D-035：TCAIL V2.2 增补 B9–B12 并收紧新颖性边界（2026-11-04）

本轮在 31 号独立复审和 32 号规格修订任务基础上，完成 FBL、cDLED、CGOMEA、Tinós et al. 2026 的原文级机制核验，新增 35_TCAIL_V2_2_PLANNER_ADDENDUM_R1.md。

### 新发现的规格阻塞
1. **B9：非线性 objective-scale estimand 可识别性。** 若主目标是 inverse-logit 后的成功概率交互，线性 predictor contrast 的 row-space 判据不能自动证明 probability-scale 四格差分可识别。需要四个 cell predictor 分别可识别的保守充分条件，或直接 estimand-invariance 检验。
2. **B10：acquisition 的设计单位。** 应是带 parent/context/pair/background/task-block 的四格观测向量；明确 CRN 可行条件、任务随机效应、随机执行顺序、未来 task-block 分布和缓存复用后的唯一 episode-equivalent 成本。
3. **B11：FOS 缺失边处理。** unsupported / pending / model-order-sensitive 不能填 0 伪装成真实无边；必须定义 missingness-aware builder、singleton/forest/fallback 和确定性 tie-break。
4. **B12：posterior 先验敏感性。** q 与 w 必须进行 null prior-predictive calibration、prior-scale sensitivity 和低样本行为验证，避免宽先验导致伪高置信 edge。

### 先行工作带来的新颖性收紧
- FBL 已有 scaled fitness dependency、Linkage Tree / marginal-product FOS 和 incremental pair probing；
- cDLED 已有 individual-local DLED、conditional eVIG、子结构识别和 donor mating restriction；
- CGOMEA 已有 conditional linkage 与 solution mating filter；
- Tinós et al. 2026 已有零额外 fitness-evaluation 的 GA-side-effect interaction learning。

**决定：** 35 号作为 32 号任务的强制补充。V2.2 必须同时处理 B1–B12；不能把 FBL/cDLED 的贝叶斯化或加上通用 OED 直接视为创新。TCAIL 仍 HOLD / IMPLEMENTATION BLOCKED；不编码、不启动 Phase 0、不调用真实 LLM、不训练 A800 模型。CI-GOM、IMCE-RSI 继续冻结。若最终方法不能在同预算下优于 FBL incremental、cDLED-P3M、CGOMEA、LMM/ALI 与 Tinós/GAwLL2，并改善下游 GOM 搜索，则应 NO-GO 或进一步收窄。


## 决策 D-038：TCAIL V2.2 完整草稿形成，但继续保持 HOLD（2026-11-04）

新增 `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md` 与 `34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md`，完成 32 号任务和 35 号补充要求的规格层交付，不覆盖 17、20、22、31、32、35 号历史文件。

### 本版固定的重要规格决策

1. **局部 estimand 与权重分离。** 主要对象为 `g=(r,parent_id,a)` 下 objective-scale 四格差分；`q` 用于证据、资格和边决策，不直接作为连续 FOS 权重；主候选权重为 posterior expected excess magnitude，global RMS 仅作描述/筛查/预算优先级。
2. **双模型与高阶门禁。** M2/M3 保留低阶父项但允许父系数为零；只有双 base pass 后才进行模型阶数比较。主候选采用保守 local-null/q/w 合并，四阶以上必须压力测试；该校准和高阶覆盖仍 OPEN。
3. **最终决策与 acquisition 对齐。** 当前和 fantasy 数据均使用同一个带 `τ_edge` 资格的 per-graph BFDR-constrained set decision 与实际所选集合风险；per-edge 方法仅保留为 surrogate 对照。
4. **四格观测与成本。** 主分析为 task/block 随机效应 Bernoulli GLMM；候选是固定 task-block 上四格结果向量，明确三类条件预测路径。缓存复用与 attempt/retry 分开，预算只计唯一新增 episode-equivalent，另报完整资源成本。
5. **非线性与实际可识别性。** 线性 row-space 不直接证明 probability-scale estimand；采用四 cell 行充分条件和 observationally-equivalent 参数下的 invariance，并分离共同支持、Fisher effective information、conditioning 和区间门。
6. **缺失感知 FOS。** unsupported、unresolved 与 supported practical zero 不混码、不填零；主 builder 使用 supported cross edges 的 weighted average-linkage，保留 partial forest 和 singleton safe fallback。
7. **校准与强基线。** prior-predictive、null/posterior calibration 和 prior-scale sensitivity 是强制 Gate；全部指定强基线必须区分 original reproduction 与 paper-setting adaptation，并尽可能共用同一 FOS builder。

### 状态决定

B1–B12 在本轮均只能记为 `PARTIAL（规格已处理）`，其独立审查、阈值、校准、复现、实现或实验部分仍为 `OPEN`。编写过程中的规格符合性和文档质量复核不构成正式独立数学 PASS。

**决定：下一步只进行新的独立 V2.2 规格复审。TCAIL 继续 HOLD / IMPLEMENTATION BLOCKED；CI-GOM、IMCE-RSI、Phase 0、真实 LLM/DeepSeek API 和模型训练继续冻结。规格草稿完成不等于算法实现、Gate 通过、创新成立或 EC 搜索收益成立。**


## 决策 D-039：TCAIL V2.2 独立复审 R1 REQUEST CHANGES（2026-11-04）

本条将 `D039_TCAIL_V2_2_INDEPENDENT_REVIEW_DECISION.md` 合并回主决策日志；完整审查证据见 `36_TCAIL_V2_2_INDEPENDENT_REVIEW_R1.md`，审查基线为 `11cccf45c7533782f2673612b4bd52930541c9bc`。

独立复审确认三层 estimand、非线性识别方向、task-block 结构和未决边不填零等定义层面的进展，但提出 R1–R7：

1. Conservative local-null envelope 与 posterior expected loss 语义不一致；
2. Acquisition 非正停止未使用 MCSE；
3. 同一 base key 的 retry 配额可能跨轮重置；
4. Practical-information rank 门忽略零方向，边际 GLMM Fisher 未冻结；
5. 旧 `rho_AB` 是正边密度而非支持覆盖率；
6. 双模型逐样本 max-risk/max-cost 缺少概率 coupling 解释；
7. 活动图集合与权重的周期更新未定义。

**决定：REQUEST CHANGES / HOLD / IMPLEMENTATION BLOCKED。** 33/34 保留为 R0，不覆盖；下一步仅允许 V2.2 corrective specification revision R1，不授权实现、Phase 0、真实 API、模型训练、CI-GOM 或 IMCE-RSI。


## 决策 D-040：TCAIL V2.2 Revision R1 草稿形成并交 R2 复审（2026-11-04）

新增 `37_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R1.md` 与 `38_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R1.md`，逐项处理 36 号 R1–R7，不覆盖 33、34、36 号历史文件。

### 固定修订决策

1. **鲁棒风险：** `ell_env/q_env` 仅作保守约束；每模型使用自身 posterior 计算 `L_M`，最终最小化 `max_M L_M`，不再把包络代入损失后称为 posterior expected loss。
2. **MC 停止：** 只有所有候选收益上界 `A_U≤0` 才能非正停止；执行需 `A_L>0`；`S_max` 无法判断时为 `STOP_ACQUISITION_UNCERTAIN`。符号与排名采用预注册 MCSE/alpha-spending 工作规则，校准仍 OPEN。
3. **Retry 账本：** base-key 终身保存 attempt、已耗 retry、失败、reusable、terminal/exhausted 和剩余 allowance；continuation 不再被计为新的 initial，跨轮不重置。
4. **Practical information：** 使用边际 GLMM expected Fisher、完整 target rank 与 draw-wise `λ_min` 低分位；广义逆只可在明确 nuisance/行空间条件下作为 asymptotic proxy。
5. **FOS：** 分离 support coverage、selected-positive density 和 unknown；supported practical-null 是有支持零边，NOT_SELECTED/UNRESOLVED 不填零。
6. **Fantasy 聚合：** 主规则为 worst-expected `max_m E_m[H]`；模型平均和 product-coupled `E[max]` 仅作预注册比较，不能混称。
7. **活动图周期：** 集合与权重在每个 acquisition cycle 开始前冻结，新 parent/generation 只在边界进入；切换使旧 assessment/decision 失效，跨期风险不直接比较。

R1–R7 及 B1–B12 均只能标为 `PARTIAL（修订规格已处理）`，所有未校准、未认证、未复现、未实现和未实验事项保持 OPEN。起草过程的符合性与质量复核不构成 R2 独立复审或研究 PASS。

**决定：TCAIL 继续 HOLD / IMPLEMENTATION BLOCKED。下一步由不同会话执行 R2 独立规格复审；CI-GOM、IMCE-RSI、Phase 0、真实 LLM/DeepSeek API 和模型训练继续冻结。规格修订不等于算法验证、创新成立或 EC 搜索收益成立。**


## 决策 D-041：TCAIL V2.2 Revision R1 独立复审 R2 — REQUEST CHANGES（2026-11-04）

独立审查报告：39_TCAIL_V2_2_INDEPENDENT_REVIEW_R2.md。审查基线：4f15ac303936817cc2bf122e649fff2331c9b1dc。

37/38 号的鲁棒 posterior loss、worst-expected fantasy 聚合、边际 GLMM Fisher 完整秩门和 acquisition cycle 冻结有实质进步，但仍不能验收。

关键阻塞：
1. Acquisition A_L/A_U 未纳入当前基准风险 R(D) 的 posterior Monte Carlo 误差；sign alpha 未明确分配两个生成模型，rank alpha 未给出全部 rival 比较的完整分配；nested MCSE/自相关处理未冻结。
2. Base-key ledger 在 status=REUSABLE 但 cache miss 时可能错误规划 continuation，执行器 BREAK 后仍返回 OK；crash-consistent IN_FLIGHT/UNKNOWN_OUTCOME 状态缺失。
3. FOS 将 Q_g 中已经通过基础支持/信息门的 NOT_SELECTED 计入 unknown density，rho_support 因而低估真实数据支持覆盖率。
4. Fisher Hessian 参数向量中的离散 nuisance 含义不清；paired MCSE 的跨候选 CRN 映射及 generation/cycle 索引需明确。

**决定：REQUEST CHANGES / HOLD / IMPLEMENTATION BLOCKED。** R1/R6 主定义可保留；R2、R3、R5 必须修订；R4、R6、R7 补足定义。B3、B8、B10、B11 为 REQUEST CHANGES，其余 B 项保持 PARTIAL。

下一步唯一任务：只做 TCAIL V2.2 corrective specification revision R2，新增 40/41 号文件；保留 37/38/39 历史文件，不编码、不实验、不启动 Phase 0、不调用真实 LLM API、不训练模型；CI-GOM 与 IMCE-RSI 继续冻结。修订后交不同会话独立复审。


## 决策 D-042：先执行 Oracle Linkage G2 Pilot，再转向估计器证据（2026-11-04）

新增 experiments/tcail_oracle_gate_pilot/run_oracle_gate.py、RESULTS.md、requirements.txt。在简化 GOM 原型上完成 40 维 concatenated deceptive 4-bit trap 的 20 个配对种子比较，最大评价预算 5,000；Oracle FOS 39.55/40，population-MI LT 38.55/40，配对差值 +1.00，13/20 胜、6 平、1 负，Wilcoxon 单侧 p=0.000919，配对 bootstrap 95% CI [0.55,1.45]。Oracle optimum 13/20，Learned LT 2/20。12-seed additive control 四种方法均 12/12 达到最优。

**决策：G2 Oracle precondition 在该合成景观上为 POSITIVE，但只证明正确 linkage 有上界价值，不证明 TCAIL 能学到它。** 该实现为简化 GOM 原型，不是官方 GOMEA；实验是 exploratory pilot，需独立 clean rerun 和更多景观族复核。

下一步只做 fixed full-factorial estimator-only synthetic gate：在相同 task-block 四格数据下比较局部 posterior q/w、FBL/scaled-FBLT 风格估计、pooled/global score 和 oracle；检查 null false-link、edge AUPRC、sign-flip、abstention、FOS recovery。此 gate 暂不包含 active acquisition、retry ledger、真实 Agent 或 API，以隔离核心局部交互估计机制。若 q/w 未能在校准与强基线比较中体现增量，停止或收窄 TCAIL，不继续堆叠模块。


## 决策 D-043：Estimator-only q/w 代理出现小幅正向信号，但 TCAIL 仍未证实（2026-11-04）

新增 experiments/tcail_estimator_gate_pilot/run_estimator_pilot.py、RESULTS.md、requirements.txt。采用 20 个合成种子（0–9 训练先验尺度，10–19 held-out），每 seed 200 pairs × 2 parent contexts，含 task-block Bernoulli 四格数据、parent sign flip、null/weak/strong 和 unsupported/low-support。

Held-out AUPRC：Normal empirical-Bayes posterior q=0.802，w=0.797，local standardized contrast=0.785，Student-t q=0.767，raw local contrast=0.619，context-pooled contrast=0.598。q 的 Brier=0.153；q≥0.8 时 precision=91.1%、recall=38.1%、FPR=1.57%。10/10 held-out seeds 的 q AUPRC 高于 standardized contrast，平均差 +0.0169，seed-level bootstrap 95% CI [0.0120,0.0221]。但 8-block low-support 子集 AUPRC=0.353。

**解释：** 该结果只说明一个简单的 task-block normal-normal empirical-Bayes q/w proxy 在这个合成分布中出现小幅增量；它不是 TCAIL 的 M2/M3 GLMM，也未与 paper-faithful FBL/scaled-FBLT/cDLED 比较。不得宣称 TCAIL 已成立。

下一步只做强基线验证与模型校准：复现/适配 FBL、scaled-FBLT、cDLED；在独立 held-out seeds 上检验 q/w 的 calibration、null false-link、sign-flip、abstention 和 FOS recovery。若增益消失或低支持下无法安全 abstain，则停止或收窄。Active acquisition 暂不启动。


## 决策 D-044：EB 局部 q/w 代理在合成 task-block 设定中优于 scaled-FBL 二元适配（2026-11-04）

新增 experiments/tcail_estimator_gate_pilot/run_fbl_comparison.py 与 FBL_COMPARISON_RESULTS.md，并保留完整 per-pair/context 四格数据导出能力。

在 seeds 0–9 估计 prior scale 和训练-null thresholds、seeds 10–19 held-out 的设定下，EB q AUPRC=0.802，EB w=0.797，local z-score=0.784，scaled-FBL binary adaptation=0.414，raw contrast=0.619，context-pooled=0.598。EB q 对 scaled-FBL 的 held-out per-seed AUPRC 差 +0.3845，10/10 种子胜，bootstrap 95% CI [0.3704,0.3990]。两种阈值均由训练 null 的 95th percentile 校准：EB q precision/recall/FPR=81.5%/58.7%/5.62%；scaled-FBL adaptation=69.7%/31.5%/5.81%。

**重要限制：** FBL 是针对 Bernoulli task-block 的 paper-setting adaptation，不是原论文复现；EB q/w 是 Normal-normal paired-contrast proxy，不是完整 TCAIL M2/M3 GLMM。未比较 cDLED-P3M、CGOMEA、GAwLL2；未运行 FOS/GOM 下游；8-block low-support AUPRC 仍仅 0.353。不得写成 TCAIL 已证明或已优于原始 FBL。

下一步只做同数据/同预算下的 paper-faithful FBL/scaled-FBLT、cDLED-P3M 和 GAwLL2 比较，并实现/校准主规格所需的 task-block Bernoulli 模型。若优势在强基线或低支持场景消失，则停止/收窄；通过估计器 gate 后再测 active acquisition。


## 决策 D-042：停止无关规格扩张，优先证明 TCAIL 对 EC 搜索的独立收益（2026-11-04）

用户明确要求尽快证明，不再做无关工作。新增 42_TCAIL_ESTIMATOR_TO_GOM_CONFIRMATORY_GATE_R1.md，作为当前研究执行优先级，优先于继续扩写完整 acquisition/retry 规格。

### 决策
TCAIL 的核心命题不是“统计模型更复杂”，而是：在同样 task-block 四格观测和同样总 episode-equivalent 预算下，TCAIL 局部交互后验能否优于强 linkage 基线，并通过 FOS 改善 GOM 搜索。

### 证据现状
- Oracle FOS pilot：在一个 40-bit concatenated deceptive-trap 简化 GOM 场景中 13/20 成功；仅证明该场景存在 linkage 上界价值。
- EB q/w pilot：AUPRC 0.802/0.797，但为 Normal-Normal empirical-Bayes proxy，不是完整 M2/M3 Bernoulli GLMM。
- scaled-FBL binary task-block 对照 AUPRC 0.414，是适配版本，不是原论文复现。
- 低支持 8-block 子集 AUPRC 0.353，必须保留 abstention，不得宣称低支持鲁棒。

### 唯一执行链
1. clean rerun 并审计现有两个 pilot 的代码、原始数据、预算和摘要；
2. 实现并校准 Bernoulli task-block M2/M3 posterior q/w；
3. 在同一四格数据/预算上比较 FBL/scaled-FBLT、cDLED-P3M、CGOMEA linkage、local/global、random 和 oracle；
4. estimator gate 通过后，才用独立 discovery/evaluation blocks 进行 FOS→GOM 下游验证；
5. 下游总预算必须计入 discovery 与 search，按 held-out seed 配对。

### GO/NO-GO
- Estimator：held-out 五情景 macro-AUPRC 对 validation-selected strongest non-oracle baseline 的 paired seed 95% CI 下界必须大于 0；null false-link、posterior calibration、sign-flip、FOS recovery 和低支持 abstention 同时报出。
- Downstream EC：相同总 episode-equivalent budget 下，TCAIL-FOS 对 strongest non-oracle linkage baseline 的 held-out GOM objective/success paired 95% CI 下界必须大于 0。
- 估计器提升但 GOM 不提升：不允许声称 EC 搜索创新成立。
- Oracle 不提升：停止该任务族的 linkage-to-GOM 主张。
- TCAIL 不胜强基线：停止其 estimator 新颖性主张。

### 边界
这只授权固定 full-factorial 的合成研究原型与隔离 GOM research prototype；不授权完整 active acquisition、生产 retry、真实 Agent API、A800 训练、CI-GOM 或 IMCE-RSI。所有实验结果必须如实标为 NOT RUN / PILOT / CONFIRMATORY。


## 决策 D-045：R1-A 审计完成，现有结果仍为 exploratory（2026-11-05）

实际重跑 Oracle、Estimator-only 和 Scaled-FBL pilot，并保存原始及修正版代码、CSV/JSON、日志、环境和独立重算。所有原报告核心数值均可从原始 CSV 重算。

修复并记录：Oracle 方法专属 mixing seed 改为跨方法配对 seed，导出初始种群哈希并验证一致；FBL 区分绝对值比率适配与论文 signed Eq.(7)，增加无 gate/零 epsilon 敏感性。修正版 Oracle−Learned LT 配对均值 +1.30，95% CI [0.60,2.00]；该变化与原结果分开保留。FBL signed Eq.(7) 领域违规 2,811/3,800，valid-only 结果不得作完整公平比较。

**决定：R1-A 只确认可重算性和适配边界，不构成 TCAIL 或 EC 收益证明。** EB q/w 仍是 Normal–Normal proxy；真正 Bernoulli task/block M2/M3、Estimator Gate 和 TCAIL-FOS GOM Gate 尚未完成。继续禁止真实 LLM API、A800 训练、CI-GOM、IMCE-RSI、完整 active acquisition 和生产 retry。


## 决策 D-046：Estimator Gate 确认性运行失败，Downstream GOM Gate NOT RUN（2026-11-05）

在 `experiments/tcail_confirmatory_r1/` 完成真正的 Bernoulli task/block 层级 M2/M3 Laplace 估计器、五情景 logistic random-effects 生成器、9 类共享四格数据的 linkage 基线，以及 train 0–39 / validation 40–59 / held-out 3000–3039 的隔离流程。全部原始观测、per-pair 评分、per-seed 指标、配置、日志、环境锁和独立重算已保存。

### 结果
- 验证集最强非 Oracle 基线：standardized contrast（0.7713）。
- Held-out：TCAIL q macro-AUPRC 0.6736；配对差 **−0.0996**，95% CI **[−0.1139, −0.0858]**。
- 分情景：sparse −0.0393 [−0.0741,−0.0102]；parent sign-flip −0.3541 [−0.4081,−0.2983]；higher-order −0.1511 [−0.1938,−0.1101]；low-support/drift **+0.0462** [0.0261,0.0674]；additive_null 无正例，AUPRC 约定 0。
- TCAIL null false-link 0.0375（≤0.05，合格）；calibration slope 0.130、ECE 0.179；FOS F1 0.373（standardized 0.729）；sign accuracy 0.647。
- M2/M3 fit_ok 0.935/0.925；56/800 次 `GRADIENT_TOLERANCE` 失败；512-row 支持条件弃权率 52.9%。
- 解盲后 q_M3-only 仍显著低于 standardized：−0.0322 [−0.0496,−0.0168]；因此失败不只是 conservative min。
- 先验敏感性（validation 40–42）：q Spearman 0.983/0.986，selection agreement 1.000/0.983。

### 决定
**ESTIMATOR_GATE_FAIL。** 按 42 号协议停止 TCAIL estimator 优越性主张；不进入 Downstream GOM Gate，GOM 标记 **NOT RUN**。不得用 AUPRC、FOS recovery、拟合成功或工程运行代替 EC 收益证据。

### 边界
cDLED-P3M 与 CGOMEA 是 static-data adaptation，不是原论文完整复现；SLL-MI、FBL incremental、DLED、LMM、ALI/AIM、GAwLL2 未运行。未调用真实 LLM API，未训练 A800，未启动 CI-GOM/IMCE-RSI 或完整 active acquisition。

### OPEN
128-block 拟合失败、additive_null 的 AUPRC 约定、random slopes/overdispersion、多档效应强度、联合 40 变量全图、缺失强基线、conservative min vs M3-only 的预注册取舍，均未解决。若重试，必须使用新的独立 held-out seeds，不得复用 3000–3039 作确认性 test。


## 决策 D-047：TCAIL NO-GO 后重新评估毕业论文主线（2026-11-05）

### 事实依据
TCAIL R1 Estimator Gate 已失败：TCAIL q macro-AUPRC 0.6736 vs standardized 0.7732，配对差 -0.0996，95% CI [-0.1139,-0.0858]；FOS F1 0.373 vs standardized 0.729；calibration slope 0.130。Downstream GOM 未运行。不能声称 TCAIL 改善演化搜索。

### 决定
1. TCAIL 不再作为毕业论文核心创新点；保留其完整负结果和代码/数据。
2. 旧 CI-GOM linkage 接口依赖 TCAIL，继续 FROZEN，不按旧规格实施。
3. 新主线候选调整为“面向状态化工具型 LLM Agent 的故障恢复策略演化与递归自我改进”。
4. 两个核心候选：(a) 状态感知、契约约束的恢复策略演化；(b) 故障场景—恢复策略双种群协同演化。
5. 第三个候选跨任务恢复策略迁移仅作储备，前两项通过独立 Gate 后再审查。
6. RSI 体现为 Agent 从自身执行失败与恢复轨迹更新后续策略版本，并在未来任务上验证递归改进；LLM backbone 可固定通过 API 使用，EC 搜索结构化策略基因型。
7. 不把 NSGA-III、Pareto、通用 prompt evolution、blame-aware mutation、失败记忆检索、事务 runtime 单独称为创新。

### 相关工作约束
GEPA (ICLR 2026)、EvoTool (ACL 2026)、Q-Evolve (ICML 2026)、AgentEvo (2026)、GRSE (preprint)、Sentry (preprint)、AgentDebug/PROBE、ToolMaze、ReliabilityBench、Cordon、DelAct 已覆盖通用 agent evolution、credit assignment、failure recovery、fault evaluation 或 transactional runtime 的多个方面。候选方法必须以状态化副作用工具环境中的可执行恢复控制器约束演化及故障场景—策略协同演化为具体切入点；新颖性仍需机制级审查，不能宣称空白已证实。

### 下一步
只做相关工作机制差异矩阵、状态/动作/硬不变量形式化和 Pilot A：手工策略与 oracle policy 上界测试。若 oracle 不优于简单 retry/verify，停止方向；若普通策略已达到 oracle，也停止。Pilot A 通过后再比较 random search、standard GA/GP、NSGA-II/III 和 proposed contract-aware variation。Pilot B 有证据后才做双种群协同演化。

完整评估见 44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md。当前新方向状态为 HOLD / NOT IMPLEMENTED / NOT VALIDATED；不启动大规模实验，不训练基模，不把研究计划当成创新成果。


## 决策 D-048：A800 训练候选与 Pilot A 首轮结果（2026-11-05）

### 文献审计结论
CoMAP (EMNLP 2026) 已研究文本世界模型与 Agent policy 闭环共演化，模型预测动作后的文本状态并以 on-policy 轨迹自蒸馏更新；HarnessMDP 已研究冻结 LLM 的外部 harness controller 离线学习；TRACE/SENTINEL 已覆盖失败轨迹驱动的能力训练/任务生成；EvoTool 已覆盖 blame-aware 工具策略演化。不能把“训练世界模型”“从失败训练 Agent”“演化工具策略”单独视为创新。

### A800 训练候选
保留 ARWM（Agent Recovery World Model）为条件性候选：从 simulator-grounded 同状态多动作反事实干预数据训练 effect-state transition、side-effect/invariant risk、postcondition 与 recovery outcome 预测器；用于模型辅助约束演化策略搜索。真实 simulator rollout 仍是最终评价，模型不替代安全门禁。模型必须优于 MLP/LightGBM 等结构化基线，并在相同真实 rollout 预算下改善 EC 搜索，否则删除训练模型。

### Pilot A 首轮
7 fault families × 10 deterministic parameter seeds；6 policies，每策略 70 episodes。timeout-before-dispatch、timeout-after-commit、delayed-visibility 向策略暴露同一 TIMEOUT 签名，隐藏子类型仅 oracle 可见。state-aware handcrafted policy：task success 0.8571、safe resolution 1.0、invariant violation 0；oracle 相同成功/安全表现，但 mean actions 1.5 vs 3.0714。blind retry success 0.1429、violation 0.4286。

### 决定
CONDITIONAL HOLD。当前场景中手工策略已达到 oracle 的成功/安全上界，尚未证明足够的成功率进化空间；动作效率差距不是独立算法收益证据。暂不启动 A800 训练、ARWM 或正式 EC 搜索。仅允许 bounded Pilot A-2：多工具不同幂等契约、同公开观测下复合/潜在故障、变化的读延迟与补偿可用性、按 task/fault family 隔离测试。若强手工策略仍匹配 oracle 且成本接近，停止恢复策略方向。若 A-2 证明有剩余空间，再比较 GA/GP、NSGA-II/III 和 contract-aware EA；只有 action-effect 预测本身超越结构化基线且改善固定真实 rollout 预算下的 EC 搜索，才训练 ARWM。

### 交付
- 46_RELATED_WORK_MECHANISM_AUDIT_ARWM.md
- experiments/pilot_a_recovery/pilot_a.py
- experiments/pilot_a_recovery/test_pilot_a.py
- experiments/pilot_a_recovery/PILOT_A_EXPLORATORY_RESULTS.md
- experiments/pilot_a_recovery/summary.json

结果为探索性确定性模拟器结果，不是确认性统计证据；未调用 LLM API，未训练 A800，未实现 ARWM，未运行 EA。


## 决策 D-049：Pilot A unresolved 指标独立复算修正（2026-11-05）

复算提交模拟器逻辑后，发现原报告的 unresolved 指标转录错误。正确值：blind retry 0.8571、verify-then-retry 0.5714、wait-verify-retry 0.4429、conservative escalation 0.0857、state-aware 0、oracle 0。原因是 state-aware/oracle 对 permission-denied 失败显式执行 ESCALATE，因此 `unresolved = not success and not resolved` 为 0。其余指标保持不变：state-aware 与 oracle 的 task success 均 0.8571、safe resolution 均 1.0、invariant violation 均 0。

独立复现中 7 项转移/覆盖断言通过，但这不是 GitHub Actions 运行结果；CI 仍未验证。修正不改变 Pilot A 的 CONDITIONAL HOLD：手工策略在本小型场景匹配 oracle 成功/安全表现，动作数差异不能单独证明算法收益。A800、ARWM、正式 EC 搜索仍未授权。


## 决策 D-050：Pilot A-2 首轮结果（2026-11-05）

实现四类双工具任务（inventory→order、calendar→charge、inventory→ledger、calendar→order），九类故障（含 timeout+stale-read、partial-commit+rate-limit），六种策略，每策略 1,080 episodes，总计 6,480 policy episodes。策略仅接收公开观测，timeout 潜在子类型共用 TIMEOUT；oracle diagnostic 可见潜在故障，只作诊断上界。工具具有不同幂等/补偿契约（calendar 幂等，ledger 不可补偿）。

结果：contract-aware success 0.7222、safe 1.0、invariant violation 0、unresolved 0.0556、平均动作 5.5167；oracle diagnostic success 0.7778、safe 1.0、violation 0、平均动作 3.7778。固定等待策略 success 0.5815、安全 0.9148、violation 0.0852；blind retry success 0.1111、violation 0.4444。contract-aware 与 oracle 的 success 差距 5.56pp，提示存在剩余空间，但尚未进行统计检验，也没有任何 EC 对照。

GitHub Actions run 42030194929 与后续 run 42030392313 均成功；最新 run 42030392313 的 job logs 显示 regression tests、Pilot A baseline、Pilot A-2 simulator 和 artifact upload 全部完成，上传 artifact `pilot-a2-summary`（ID 13415632289）。早先首次 A-2 CI 曾因分层汇总函数对单组数据误调用全策略汇总导致 ZeroDivisionError；已修复并重新运行成功。

**决定：CONDITIONAL GO 到 Pilot A-3 simulator refinement；NO-GO for A800 training now。** 当前 A-2 的主要缺陷：每个任务中的两个工具共享同一故障族；参数种子只变化延迟/限流；没有真正 held-out task/fault composition。下一步实现每工具独立故障分配、跨步骤依赖和 held-out task/fault composition，再用强手工策略、随机策略搜索、GA/GP、contract-aware EA 做相同预算比较。只有 EC 在 held-out 上优于强手工策略，才考虑 A800/ARWM。


## 决策 D-051：Pilot A-3 协议冻结并完成首版实现（2026-11-05）

### 依据
Pilot A-2 的 contract-aware success 为 0.7222，oracle diagnostic 为 0.7778，差距 5.56pp；但 A-2 对同一任务内的多个工具广播同一故障族，且没有 held-out task/fault composition。该结果只能支持有条件地细化模拟器，不能证明演化算法增益。

### 本轮交付
- `47_PILOT_A3_PROTOCOL.md`：冻结任务族 × 故障组合族的因子化 train/validation/held-out split、同场景配对预算、指标和 Pilot B 门禁。
- `experiments/pilot_a_recovery/pilot_a3.py`：六个三步任务族、每工具独立故障向量、十种工具契约、部分提交、延迟可见、补偿失败、saga 逆序补偿、七种手工/诊断策略、episode CSV/JSON 与 held-out cluster bootstrap。
- `experiments/pilot_a_recovery/test_pilot_a3.py`：15 项回归测试。
- `experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md`：实现与验证边界。
- GitHub Actions 已增加 A-3 运行和 episode-level artifact 上传步骤。

### 冻结预算
每种策略 954 episodes：144 train、120 validation、690 held-out；七种策略共 6,678 policy episodes。Held-out 分为 task-only、fault-only 和 joint shift。所有策略使用相同 scenario IDs、seeds 和 fault realizations。

### 当前决定
**CONDITIONAL GO to run/inspect Pilot A-3; NO-GO for Pilot B until A-3 gate is evaluated; NO-GO for A800/ARWM now。**

本轮只确认协议和首版代码已写入分支。**CI 运行结果尚未核验，A-3 尚无实验结果，不能标记 IMPLEMENTED_AND_TESTED 或 GATE_PASS。** 不得把脚本存在、测试用例存在或 workflow 配置存在写成测试通过。

### 下一步
1. 核验分支最新 Actions run，确认 15 项新增测试、A1/A2 回归、A3 运行和 artifact 上传；
2. 下载 A3 JSON/CSV，独立检查 episode 数、split、scenario pairing、fault vector 和 summary；
3. 检查 held-out 三个 slice（每个 slice 的 saga_aware invariant violation 必须为 0）、worst-group、invariant violation、safe resolution、unresolved 和 cluster bootstrap；
4. 只有 47 号预注册门禁满足时才进入 Pilot B；否则 HOLD/NO-GO 并保留失败数据；
5. 不调用真实 LLM API、不训练 A800、不实现 ARWM、不启动双种群协同演化。


## 决策 D-052：将接管提示词设为强制、持续维护的 canonical 仓库文件（2026-11-05）

### 用户要求
用户明确要求“接管提示词必须一直维护”。

### 决定
新增 `NEXT_SESSION_PROMPT.md`，作为唯一权威、可直接复制、自包含的下一会话接管提示词。每次实质性研究、实验、代码、协议、审计、分支或决策变化后，同一轮必须同步维护：
- `NEXT_SESSION_PROMPT.md`
- `SESSION_HANDOFF.md`
- `05_DECISION_LOG.md`
- `README.md`

会话结束前重新读取并核对四份文件一致性、最新远端 HEAD 和唯一下一任务。每次用户汇报必须给出接管提示词链接。不得将聊天中的临时提示词替代仓库 canonical file。

### 当前状态
- Canonical prompt 已创建：`NEXT_SESSION_PROMPT.md`。
- A-3 当前仍是 IMPLEMENTED / CI NOT YET VERIFIED / RESULTS NOT YET AUDITED。
- 下一任务唯一为核验最新 A3 Actions、下载并独立复算 JSON/CSV，再按 47 号协议作 Pilot B gate 判断。
- Pilot B、A800/ARWM、真实 LLM API 和双种群协同演化仍 HOLD。

### 验收
本次将同步更新 SESSION_HANDOFF 与 README；后续每次实质性进展均必须继续更新 canonical prompt，不得遗漏。


## 决策 D-053：明确大论文当前工作题目、创新候选层级与成熟度（2026-11-06）

### 决策背景
用户询问当前大论文整体处于什么状态。检查 44 号方向重评、45 号 ARWM 候选、46 号相关工作审计、47 号 A-3 协议、README 和既有开题稿后，发现旧开题稿仍以 TCAIL/CI-GOM 交互感知路线组织，而当前主线已在 TCAIL NO-GO 后转为状态化工具型 Agent 恢复策略演化。

### 当前工作题目（未冻结）
**《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》**

旧题目《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》属于 TCAIL/CI-GOM 旧方向，不再作为当前论文题目。

### 当前创新候选
1. 核心候选一：契约约束的 Agent 恢复策略演化。策略编码为可执行有限状态控制器，研究契约感知变异/重组与修复、可行性优先选择。EC 增益尚未验证。
2. 核心候选二：故障场景—恢复策略双种群协同演化。暂缓，必须在候选一通过后验证。
3. 储备候选三：跨任务恢复策略迁移与能力保持。冻结，不为满足数量而保留。
4. ARWM/A800 为条件性辅助模型候选，不作为已确认独立创新点；需通过相关工作和固定真实 rollout 预算收益 Gate，当前 HOLD。

### 当前成熟度判断
- TCAIL：FAIL / NO-GO；旧 CI-GOM 冻结。
- Pilot A/A-2：探索性模拟器结果；A-2 contract-aware success 72.22%，oracle diagnostic 77.78%，两者 safe 100%，未证明 EC 增益。
- Pilot A-3：协议、首版实现、15 项测试用例及 CI 步骤已提交；A3 CI 与 JSON/CSV 仍待核验。
- Pilot B：未启动；没有标准 EA 与拟议算法同预算结果。
- RSI：尚无多轮策略更新后在未见任务上持续改进的实验结果。
- 旧开题报告 V0.1–V0.3：基于旧 TCAIL/CI-GOM 路线，不可直接作为当前正式开题稿；需重构研究内容、创新点和技术路线。

### 下一步
唯一下一任务为完成 Pilot A-3 CI 核验、原始数据独立复算及预注册 Gate 判断。只有 A-3 通过才进入 Pilot B。当前仍处于开题前研究验证阶段，不写最终大论文正文，不宣称创新已成立。


## 决策 D-054：第一项创新相关工作与新颖性边界审计（2026-11-06）

### 检索发现
新增 `49_FIRST_INNOVATION_RELATED_WORK_AUDIT.md`。初步检索发现：
- UndoBench：工具型 Agent 故障恢复 benchmark，含 lost-ACK paired trials 和受限 EvoUndo-RB1；
- EvoUndo：Agent harness 自修改的 recoverability-constrained self-evolution，虽不等同于 EC，但与 effect contracts、counterfactual recovery 和 recovery synthesis 近邻；
- EvoTool：ACL 2026，已通过 gradient-free evolutionary paradigm 优化模块化 tool-use prompt policy；
- LIMBO：late commit、idempotency、eventual consistency 和 duplicate side effects；
- Cordon、Atomix、SagaLLM：transaction、commit/rollback、Saga compensation；
- Verified Tool Calls、Repair Economics：verify-before-retry、idempotency 和 fault-injection 评估；
- CDGP、GP controller synthesis、FSM-MOEA、SMC-ES：安全程序/控制器合成基础。

### 新颖性边界
不能把 generic recovery、verify-before-retry、idempotency、Saga、transaction wrapper、generic prompt evolution、FSM synthesis、counterexample-guided GP 或 safe EA 单独称为创新。

保留的研究假设（未批准）：**契约语义保持、反例驱动的可执行恢复 FSM 演化**，重点验证 typed effect-state genome、semantic variation/repair、feasibility-first safety 和跨任务/故障族泛化是否带来标准 GP/EA 无法替代的收益。

### 对实验的影响
Pilot A-2 的 fault-injection testbed/policy matrix 不是新颖性贡献。A-3 可作为内部算法测试环境，但必须与 UndoBench、LIMBO、Repair Economics、FAILING TOOLS 做 feature-level comparison。Pilot B 必须加入 EvoTool 适配基线、强手工恢复/transactional policy、标准 GA/GP/NSGA 和安全控制器合成相关对照。

### 决定
**GO：继续第一项候选的机制级审查。HOLD：Pilot B、A800/ARWM、真实 LLM API。** A-3 CI 和 JSON/CSV 仍待核验。只有 A-3 预注册 gate 与新颖性/强基线审查都通过，才进入 Pilot B。

### 下一步
精读 UndoBench、EvoUndo、EvoTool、LIMBO、Cordon、Atomix、SagaLLM，完成统一矩阵：研究对象、状态/效应语义、策略表示、搜索/优化机制、验证方式、基线、数据划分、预算、未解决问题。并核验 A-3 Actions/artifacts。


## 决策 D-056：数据集组合确认与下一阶段门禁（2026-11-06）

### 数据集组合（建议已记录，最终协议未冻结）
- 演化开发：Pilot A-3 + ToolMisuseBench v0.2 train（6,000）。
- 调参/候选选择：A-3 validation + ToolMisuseBench dev（900）。
- 外部恢复测试：ToolMisuseBench public test（1,200 records，其中 600 output-grounded，需核验评分分母）+ UndoBench TEST（12 workflows，v1.0.1）。
- 正常任务回归：ThinkingBox-Bench v1.0（507 tasks，evaluation-only，只允许方法冻结后的 clean regression）。

### 重要基线
ToolMisuseBench 论文报告 Parser+Repair public-test task success 0.767、conditional recovery success 0.736、recovery-disabled task success 0.158。必须复现或公平适配；不得将论文报告值写成我们自己的复现结果。

### 当前 A-3 状态
47 号协议为 PRE-REGISTERED / NOT RUN；实现状态文件标注 NOT YET VALIDATED BY CI / RESULTS NOT YET RUN OR ACCEPTED。测试与 artifact workflow 已写不等于实验已运行。A-3 结果和 Gate 仍未验证。

### 决定
GO：A-3 CI/artifact 独立复核、公开数据集版本/许可/manifest/split/evaluator 审计、DEV/train adapter smoke。
HOLD：Pilot B 演化搜索、ToolMisuseBench public test 调参、UndoBench frozen TEST、ThinkingBox 优化、A800/ARWM、真实 LLM API。

### 下一步
按 51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md 执行 Phase A：确定准确 Actions run 与 head SHA，检查 15 项测试，下载 A-3 JSON/CSV artifact，hash 并独立重算，严格应用 47 号预注册 Gate。并行完成 ToolMisuseBench / UndoBench 数据审计。只有 A-3 Gate、数据兼容 Gate 和 adapter smoke 均通过，才起草 Pilot B preregistration。


## 决策 D-057：Pilot A-3 CI 修复、独立复核与预注册 Gate 判定 HOLD（2026-11-06）

### 事实（已核验）
1. **CI 失败根因已定位并修复。** 加入 A-3 simulator 步骤后的全部 run（42037561884 起 7 个）在 `recover_tool` 崩溃：`AttributeError: 'PublicToolView' object has no attribute 'tick'`。策略代码经公开门面误读运行时时钟；因此 artifact 从未上传，A-3 结果文件此前根本不存在。修复（commit `f5e6b46`）：策略按公开 `retry_after` 自行计数等待，`PublicToolView` 可见边界不变；新增第 16 项崩溃回归测试（6 策略 × 7 公开错误全覆盖）。测试数由 15 变为 16（15 项预注册测试全部保留）。
2. **修复后的 CI 真实通过。** run 42241224898（head SHA `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`）：28 项测试 OK、A1/A2/A3 模拟器全部运行成功、artifact 上传成功。
3. **artifact 已核验。** ZIP SHA-256 `1119d14b70eedef221fe6e63439e2a04bd58c0354d5a723344d2c80c459ab727`（与 GitHub digest 一致）；JSON `3a60ae83…`；CSV `2c7d7dad…`（6,678 数据行）。原始文件存于 `experiments/pilot_a_recovery/ci_artifact/`（-text 属性保真），清单在 `a3_artifact_manifest.json`。本地重跑 CSV 逐字节一致，模拟器完全确定。
4. **独立重算全部通过结构/语义审计。** 6,678 行、每策略 954（144/120/690）、954 个 scenario 七策略完全配对（同 seed、同 fault vector）、split 因子化与 47 号协议零偏差、JSON 汇总与 CSV 重算 0 处偏差、逆序补偿/补偿失败/unresolved 语义逐行一致。
5. **预注册 Gate 结果：HOLD（HOLD_REVIEW_FAILURE_BOUNDARIES）。**
   - 条件 1（每个 held-out slice saga_aware 零违规）：满足（三 slice 均 0.0）；
   - 条件 2（oracle − saga 成功率差 ≥ 0.05）：**0.0，不满足**；
   - 条件 3（cluster paired bootstrap 95% CI 下界 > 0）：**[0.0, 0.0]，不满足**（23 个 task×composition cluster 配对差全为 0，seed 42 敏感性相同）；
   - gap ≤ 0.02 成立但动作成本差 +34.63% > 10%，不满足 NO-GO 分支；按 47 号原文落入"其他情况为 HOLD"。

### 失败边界（HOLD 要求的定位）
- **可行性死区**：held-out 组合族 `partial_comp_failure` 与 `delay_rate_permission` 对全部 7 种策略（含特权 oracle）均为 0% 成功，占 held-out 52.2%（360/690）——补偿失败残留与权限拒绝使任务结构性不可行，特权信息只能省动作不能改结局，这是 gap=0 的直接原因。
- **泛化边界**：任务族漂移 slice 上 saga_aware 达 97.5% 成功且零违规，策略规则跨任务族泛化良好；塌陷全部来自未见故障组合。
- **效率边界**：saga_aware 相对 oracle 动作成本 +34.6%（盲目等待/重复 verify），是本任务族唯一明确可优化维度。

### 判定含义与限制
- **Pilot B 不启动**；不得查看本批 held-out 后调参再宣称通过。
- 结果是探索性确定性模拟器证据，不是真实 LLM Agent 结论，不是 EC 增益证据。
- 若继续本方向，需**新预注册**（如 A-3b：可行性分层指标或补充可行组合族）；本报告（`PILOT_A3_INDEPENDENT_REAUDIT.md`）作为 A-3 完整结果永久保留。
- GO：ToolMisuseBench / UndoBench 只读数据集审计、A-3b 协议设计。HOLD：Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 优化。

### 下一步
按 51 号计划执行 Phase B（数据集版本固定、manifest/license/split 泄漏/evaluator 分母审计），同时设计 A-3b 新预注册协议供批准。A-3 Gate = HOLD，任何演化搜索继续等待授权。


## 决策 D-058：Phase B 数据集审计完成与 A-3b 研究设计（2026-11-06）

### 事实（已核验）
1. **ToolMisuseBench v0.2 large 审计完成。** HF revision `98eb28718b0393e029088ce80604c48807216de4`，MIT；三 split（6000/900/1200）SHA-256 与官方 manifest 逐一吻合。评分口径解密：论文 0.767=全部 1200 条 TaskSuccess（独立复算 0.7667）；0.736=仅 993 条故障任务的条件恢复率（731/993=0.7362）；0.158=no-recovery 全量（0.1575）；"600 output-grounded"是 tool_output_path_equals 子集（其上 0.8783），不是头号指标分母。
2. **覆盖缺口（官方 env/fault 代码取证）：** timeout/rate_limit/authz 全部在 before_call 拦截（工具从未执行，无 lost-ACK）；环境幂等/already_exists 守卫使重复副作用结构上不可能；全部故障 on_nth_call=1 单次触发（重试一次必恢复）；无补偿/幂等合同/部分提交/late commit/saga（全量关键词 0 次）；双故障计划 100% 同工具。结论：该基准无结构性不可恢复场景。
3. **Parser+Repair 机制已逆向并在 DEV 复现。** 机制=指令正则解析+错误码修参重试（schema 别名映射），无验证/补偿/等待/升级。DEV 900 条实测：TaskSuccess 0.7622、条件恢复 0.7363（550/747）；no-recovery 0.1511。与 test 发布值一致，执行器忠实可复现。必须纳入 Pilot B 基线。
4. **UndoBench v1.0.1 审计完成。** HF revision `4be1151851a109e7c9cfc1ba5d6e6c64461f6f93`，数据 CC-BY-4.0/软件 Apache-2.0。36 行全量：33/36 SCN-LOST-ACK（全部 UNKNOWN_OUTCOME）、idempotency_support 全 false、IRREVERSIBLE 8、COMPENSATABLE 24、forbidden_effects 22、19/36 多工具。指标族 CRSR/DER/MER/URR/EOR 与我们的安全-恢复语义同构。doctor+smoke+DEV 配对跑通（14 对），harness 内置 TEST 锁（allow_frozen_test_execution=false）。
5. **ThinkingBox-Bench 不可达：** HF 401（gated/移除）、GitHub microsoft/thinkingbox-data 404。许可与 507 任务声称本轮无法复核；继续按 evaluation-only 保守处理，不规划依赖实验。
6. **泄漏审计：** ToolMisuseBench 指令模板跨 split 重叠 72–73 个、工具集全重叠→只能主张实例层泛化；UndoBench 8 领域三分割全覆盖、test 12 条全同质 lost-ACK→主张限于新工作流层；A-3 因子化 OOD 是三者中唯一双因子干净的。

### A-3 gap=0 根因（A3b-4）
主因三合一：(a) 可行单元上 saga 已达 oracle 水平；(b) held-out 52.2% 为结构性死区（全员 0%）稀释差异；(c) Gate 只认成功率不认效率（唯一差异 +34.6% 动作成本无预注册地位）。oracle 只看当前步、非全局上界为次因。**修正方向=可恢复性分层+效率目标+重划 held-out，不是删困难场景。**

### 交付物
52_TOOLMISUSEBENCH_AUDIT.md、53_UNDOBENCH_AUDIT.md、54_BENCHMARK_COMPATIBILITY_MATRIX.md、SPLIT_LEAKAGE_AUDIT.md、LICENSE_AND_PROVENANCE.md、DATASET_LOCK_MANIFEST.json、55_PILOT_A3B_RESEARCH_DESIGN.md（研究设计草案）、experiments/dataset_audit/（复现与 smoke 证据）。

### 决定
- **GO：** 数据集只读审计（已完成）；A-3b 设计（已完成草案）→ 送独立审查与批准；Phase C adapter 准备。
- **HOLD：** A-3b 正式运行（待预注册冻结+批准）；Pilot B；A800/ARWM；真实 LLM API；UndoBench TEST 执行；ThinkingBox 任何用途；用 A-3 旧 held-out 调参。
- 融合判断（54 号）：主搜索=A-3b 自有模拟器（核心语义唯一完整）+ ToolMisuseBench train 第二域；外部验证=UndoBench TEST（锁箱一次性）；公开基准均不能单独支撑第一项创新。

### 下一步
1. 对 55 号设计做独立审查（数学/统计/可识别性/与 49 号边界一致性）→ 批准后冻结预注册；
2. 实现可恢复性分类器 + 场景生成器扩展（含回归测试）；
3. Phase C：ToolMisuseBench/UndoBench 统一 adapter（只用 train/dev/validation smoke）；
4. Pilot B 预注册草案仅在 A-3b Gate + 数据兼容 Gate + adapter smoke 全过后起草。


## 决策 D-059：Pilot A-3b 设计独立审查 — REQUEST CHANGES（2026-11-07）

独立审查报告：`56_PILOT_A3B_INDEPENDENT_REVIEW.md`。

### 结论
- Phase B 数据集审计：GO / 完成。
- 55 号 A-3b 草案：REQUEST CHANGES，不能直接冻结为预注册。
- A-3b 正式运行：HOLD。
- Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox：继续 HOLD。

### 阻断问题
1. R4 定义为零残留安全终态不可达，但 CorrectEscalation 又要求 R3+R4 零残留，逻辑矛盾。
2. R2 允许“优雅失败/安全放弃”，却进入 CondRecSucc 分母，任务完成与安全回滚混淆。
3. 可恢复性判定没有形式化为基于公开观测历史的策略可达性；动作序列可能依赖 hidden state。
4. 有限 rollout 不能证明总体概率 P(violation)=0；须区分静态/形式约束与有限样本 zero-observed-violation。
5. C_side_effect 惩罚 R4 不可避免残留，C_intervention 可能惩罚 R3/R4 必要升级。
6. 3:1 比例含义、R1–R4 精确配额、独立 cluster 数和 cluster-level power 尚未冻结。

### 方法学修订
- 所有算法须共享初始候选池/初始化分布；A/B/A+B 消融固定同一演化骨干（建议 NSGA-II），NSGA-III 作为独立强基线。
- 50k rollout × 5 seeds 的计费边界、搜索/验证/最终评估预算须明确。
- 改进 EA 的主检验必须比较最强标准 EA（GA/GP/NSGA-II/III），不能只超过手工策略或随机搜索。
- 49 号仍为 initial literature scan，novelty not approved；须补系统性机制级检索。

### 下一步
创建 55-R1 逐条回应 56 号 B1–B6/M1–M5；形式化 R1–R4 和 observation-based reachability；修复指标/成本；完成分层配额、cluster-level power 和预算核算；统一算法骨干与初始化；补系统性相关工作审计。仅允许单元测试和 train/dev smoke。用户批准冻结预注册前，禁止 A-3b 正式运行。


## 决策 D-060：55-R1 修订、可恢复性判定器落地、机制诊断实验首轮结果（2026-11-07）

### 交付（全部真实代码与实验，非计划书）
1. **`55_PILOT_A3B_RESEARCH_DESIGN_R1.md`**：逐条回应 56 号 B1–B6/M1–M5。R1–R4 互斥重定义（R2 成功=最终任务完成、安全放弃归 R3；R3 正确升级计成功；R4 不要求零残留、区分不可避免残留与可避免损害）+ UNKNOWN 兜底；可达性=信念态 AND-OR 观测策略鲁棒可达（horizon/动作集/截断→UNKNOWN）；安全主张分层（设计层静态保证 + 实验层 zero observed violations+置信上界，禁止 P=0）；成本三分（必要升级不惩罚）；配额 3:1≡(R1+R2):(R3+R4) 逐 split 计数；同初始池/同骨干/同预算归因设计；primary contrast=A+B vs NSGA-II。
2. **可恢复性判定器** `experiments/pilot_a3b/reachability.py`：AND-OR 信念态搜索，策略只能以观测历史为输入，同一观测等价类要求鲁棒；R1→R2→R3→R4→UNKNOWN 有序判定 + 证书输出。
3. **Stage 1 验证（已通过）**：`mini_env.py` 12 类 ground-truth 环境（直接恢复/补偿后恢复/仅可升级/结构性不可恢复/同观测异隐藏/延迟提交/lost-ACK/补偿失败/重复副作用/超深度/部分 θ 可达/saga 残留）；`test_recoverability.py` 21 项 + `test_a3_labels.py` 6 项全部通过；混淆矩阵纯对角 12/12，UNKNOWN 2/12（设计内），资源截断正确返回 UNKNOWN。
4. **Stage 2 机制实现**：FSM 基因组（守卫×宏动作）；A=契约语义保持修复算子（非幂等×歧义结果禁裸重试、partial 强制补偿/升级、权限/漂移单解）；B=反例池聚类+定向变异+≤2× 加权；NSGA-II 骨干、NSGA-III、GA、Random Search、强手工基线（对齐 saga_aware 语义）；桥接复用 A-3 `ToolRuntime/PublicToolView`（未重建模拟器）。
5. **Stage 2 诊断实验（已运行）**：216 个新生成场景（新 seed，非 A-3 旧 held-out 数据），标签分布 R1 96/R2 50/R3 36/R4 34；吞吐 ~97k episodes/s；每方法每 seed 108,864 episodes 真实计数；3 seeds；结果 `diagnostic_results.json`（含逐场景行、基因组规则、manifest SHA-256）。

### 首轮诊断结果（DIAGNOSTIC，非确认性）
- **机制 A 决定性效应：非法候选率 1.000 → 0.000**（A/AB 最终种群 100% 合法；其余全部方法含 NSGA-II/GA 均为 1.000 非法率）；A/AB 全 seed 零不变量违规，对照组违规率可达 8%。回答 Stage3-Q1：**是**。
- CondRec（3 seeds 均值）：hand 1.000 > A 0.968 > AB 0.938 > ga 0.911 > nsga3 0.902 > B 0.872 > nsga2 0.838 > random 0.575。
- Primary（AB vs NSGA-II，54 cluster 配对 bootstrap）：Δ=+0.049，CI95 [−0.017, +0.122]，置换 p=0.27 —— **方向为正但未达显著**（功效不足）。
- A vs NSGA-II Δ=+0.056（CI 含 0）；B vs NSGA-II +0.017（弱）；AB vs A **−0.006**（本预算下 B 稀释 A）；AB vs hand −0.026（**未超过强手工基线**）。
- 3 seeds 均不显著（Holm 校正后全部 p=1.0）；**如实报告功效不足，不宣称显著**。
- 归因控制：同初始池（纯随机）、同预算、同评价器；发现并排除了手工种子污染初始池的混杂（M1）。

### 判断
- **有真实证据支持"契约语义保持算子"是有效机制**（非法率消除 + 成功率方向性提升 + 零违规）；
- **尚无统计证据**支持 A+B 超过标准 EA 或强手工规则的假设；A+B 未超过 A 单独；
- 第一项创新**方向可行但未成立**：需要更大功效的预注册实验（正式 A-3b）才能回答 H1；
- B 机制首轮信号弱，可能需要反例粒度/权重再设计。

### 决定
- GO：继续诊断级工作；55-R1 审查与预注册材料准备；功效核算（下一轮）。
- HOLD（不变）：正式 A-3b 确认性实验、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、锁箱调参。

### 下一步
1. cluster 级功效核算（用本轮 54 cluster 方差估计所需 cluster/seed 数）；
2. A/B 机制迭代（B 的反例粒度与加权；A 的修复规则完备性）；
3. 49 号系统性机制检索补齐；
4. 形成 preregistration candidate 交用户批准后才运行正式实验。


## 决策 D-061：D-060 首轮机制诊断独立复核 — REQUEST CHANGES（2026-11-07）

独立报告：`57_PILOT_A3B_DIAGNOSTIC_INDEPENDENT_REAUDIT.md`。

### 仓库/原始数据核验
- branch `pilot-a-stateful-recovery` 远端 HEAD `edfc7ad0156617dccc4e4bf998df33f991ae921f`；main `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；ahead 94 / behind 0。
- `diagnostic_results.json` 可解析：216 场景、24 run、每 run 216 rows，scenario ID 跨方法/seed 一致。
- 实际标签 R1=96/R2=50/R3=35/R4=35；D-060 旧维护文档的 R3=36/R4=34 更正为 35/35。
- hand 每 seed 216 episodes；搜索 runs 多数 108,864，A seed23=108,648；缓存命中导致实际数并非完全一致。当前 commit 无 GitHub status checks。

### 关键实现/统计阻断
1. FSMGenome 是静态 `(error, idem, comp)->macro_action` 表，不是真正有状态 FSM；任一规则含 COMP 会触发全局 Saga rollback。
2. 所有失败都会自动置 `escalated=True`，污染 R3 CorrectEscalation。
3. R4 只检查 escalation+no duplicate，不检查可避免残留/最小可达损害；R4 residual 被排除。
4. action cost 对全体 rows 平均，仍惩罚 R3/R4 必要升级。
5. A-3 labels 使用 heuristic `label_scenario`，没有 216 场景逐项 AND-OR checker 证明。
6. B 反例池 update 每次 clear；scenario_weights 未调用；没有按公开错误签名定向；B/AB targeted mutation 强度不匹配。
7. A 的 legality 指标与 repair 共用 ILLEGAL 表，且 validator 不完整；不能视为独立安全证明。
8. reachability horizon cutoff 未作为 UNKNOWN 传播，可能错误降级 R3/R4。
9. stats.py 平均 per-seed CI/p 无效。探索性 pooled cluster 重算 AB−NSGA-II Δ≈+0.0494、CI≈[-0.0031,+0.1034]、p≈0.0874，仍不显著。
10. NSGA-II/III/GA 并非完整 canonical baseline；无 GP；Random 使用 Pareto survivor selection。
11. 55-R1 配额文字 3:1 与表格 3:2/58:38 冲突。

### 决定
- D-060 artifact 保留为诊断数据，不覆盖。
- 第一项创新继续验证，但当前不能声称 A 已证明安全提升、B 已验证或 A+B 优于标准 EA。
- **先修 controller/evaluator/labels/B/statistics/baselines 和配额，再重跑新诊断。暂不做功效分析，不扩大 rollout。**
- 正式 A-3b、Pilot B、A800/ARWM、真实 API、UndoBench TEST、ThinkingBox 继续 HOLD。


## 决策 D-061：57 号阻断项修复落地 + 第二轮诊断实验（2026-11-07）

### 实现修复（全部有代码与测试，47/47 绿）
- F1：真状态化 StatefulFSM（步索引/尝试数/确认栈/补偿栈/决策预算）；显式 COMPENSATE/ROLLBACK 动作+comp_log；**删除隐式 Saga 回滚**（回归测试证明未用基因不改变执行）。
- F2：policy_selected_escalation / runtime_forced_abort / escalation_reason 分列；R3 只认显式升级。
- F3：R4 引入 min_reachable_harm/actual_harm/avoidable_harm/unavoidable_residual；遏制判定=显式升级∧零重复∧可避免损害=0。
- F4：动作成本目标只计 R1/R2；R3/R4 必要升级仅描述统计。
- F5：解析证明器（逐故障模式）+ AND-OR 检查器穷举交叉验证 309 模式：**0 硬矛盾**、120 精确一致、18 R1→R2 细化、171 检查器资源内未决。
- F6：B 重设计——每代聚合全种群反例、动作序列定位涉事基因、权重实际进评价（≤2×）、定向变异替换普通变异（预算对齐）。
- F7：独立 contract_validator（不依赖 repair 表、穷举 error×action 矩阵）；三指标分列。
- F8：三值 WIN/PROVEN_LOSE/UNKNOWN+环检测；高层目标 UNKNOWN 禁止降级（回归测试）。
- S1：pooled hierarchical 统计（cluster=task×composition，seed 为嵌套重复；bootstrap+符号翻转+Holm+效应量+seed 稳定性）；禁止 CI/p 平均。
- S2：标准 NSGA-II/NSGA-III（注明重实现）/GA/Random；GP 排除（决策表 FSM 不适配树 GP 表示）。
- S3：train 108 搜索 / validation 54（2 未见任务族、新种子）仅报告。

### 第二轮诊断结果（diagnostic2，manifest d4fb2be680e74f2e…；D-060 旧数据保留）
- 8 方法×3 seeds；pop 48×60 代；每方法每 seed 316,224 真实 episodes；同初始池/同评价器。
- **A vs NSGA-II：Δ=+0.239，CI [0.193,0.284]，Holm p=0.0014（d=1.56）——显著。**
- **独立 validator 非法率：A/AB=0.00 vs 其余全部=1.00——A 的契约保持效应决定性。**
- primary AB vs NSGA-II：Δ=+0.126，CI [0.086,0.167]，p=0.0002（d=0.82）——显著。
- **AB vs A：Δ=−0.113，p=0.0014——B 叠加显著有害**；B 单独 +0.082（Holm p=0.034，弱）。
- AB vs hand：Δ=−0.514——未超过强手工基线（hand 0.827）。
- Q6 验证集：AB vs NSGA-II Δ=+0.148，p=0.002（d=0.97）；A 验证集 0.488 vs nsga2 0.222——**泛化成立**。
- 开放问题：环境违规率 A 0.36 vs hand 0.006（观测歧义下 WAIT-SLA 时序是行为层问题，规则修复无法静态消除）。

### 判定
- **机制 A 有真实显著证据**（合法性+成功率双维度、同表示同预算可归因）。
- **机制 B 组合主张不成立**（显著劣于 A 单独）；B 单独弱有效。
- 第一项创新**部分成立**：A 成立；B 需重设计；尚未达小论文完整主张。
- 正式 A-3b 继续 HOLD；功效分析继续暂缓（先修 B 与行为层安全）。

### 下一步
重设计 B 的反例→基因映射（动作序列模式级签名+语义修复型定向变异）+ 状态化契约修复（歧义观测后等满 SLA 再 VERIFY/RETRY），复测环境违规率，A+新B 同配置重跑。见 58 号报告 §7。


## 决策 D-062：启动 WAIT-SLA 行为安全与反例驱动演化改进（2026-11-08）

完整任务计划：`59_D062_WAIT_SLA_AND_COUNTEREXAMPLE_REDESIGN_PLAN.md`。

### 背景
D-061（58 号报告）给出 A vs NSGA-II Δ=+0.239（Holm p=0.0014），AB vs A Δ=-0.113（p=0.0014），AB vs Hand Δ=-0.514。报告的环境行为违规率 A=0.36、Hand=0.006。第一项创新暂定为部分成立：A 有正向诊断证据，B 的组合增益不成立，未超过强手工策略。

### 决策
- 不推翻机制 A，不再强行保留旧 B。
- D-062 第一任务是独立复核 0.36/0.006 的分子、分母、episode/action 口径和完整失败轨迹；在此之前不扩大 rollout。
- 研究 WAIT-SLA 状态化契约：区分 visibility SLA 与 retry SLA，显式建模提交语义、查询一致性、幂等性、可见性保证、等待预算、补偿和升级条件。策略只能访问公开观测。
- 重新设计 B-new：完整动作序列反例签名、涉事基因邻域定位、语义修复型局部变异；定向变异替换普通变异，严格预算公平。
- 评估独立 Contract Validator、行为层 Safety Gate 和硬安全优先的分层生存者选择。
- 只有 Stage 0–3 通过后，才运行新的非锁箱诊断集；旧 D-061 validation 若参与调参，不得继续声称独立验证。

### 授权
GO：原始数据复核、WAIT-SLA/FSM/B-new/Safety Gate 实现、测试、新非锁箱诊断和统计复算。
HOLD：正式 A-3b、旧 held-out 调参、UndoBench TEST、Pilot B、A800/ARWM、大规模真实 LLM API、ThinkingBox、未经批准的锁箱测试。

### 接受标准
必须证明 WAIT-SLA 对歧义观测重复副作用的影响，比较固定 WAIT 与 SLA-aware WAIT，检验 B-new 是否真正增加搜索收益且不破坏 A 的安全性质，并报告与 NSGA-II 和 Hand 的公平对照。必须回答增益来自演化搜索还是人工编码的 WAIT-SLA 规则。当前 D-062 仅为任务计划，尚未执行。

## 决策 D-062：D-061 独立复核、WAIT-SLA 契约、B-new 与第三轮诊断（2026-11-07）

### Stage 0 独立复核（59 号报告）——颠覆 D-061 叙事
- 原始数据 `diagnostic2_results.json` SHA-256 `dc455355…`（manifest d4fb2be6…）；从 rows 独立聚合 + 基因组重放轨迹。
- **0.36 违规率不是重复副作用**：A 的 dup_rate=0.0000；1,139 违规 episode 中 1,132（99.4%）为评价器 artifact——**正确的 ROLLBACK 安全放弃被 saga 门禁误伤**；hand 的 0.006 同为该 artifact。
- 真实重复仅 7 例，轨迹确证：`TIMEOUT → VERIFY(SLA 内谎言 NOT_COMMITTED) → RETRY → DUPLICATE`；区分了 timeout_before（重试安全）与 timeout_after/delayed_visibility（已提交不可重试）。
- D-061"行为安全差距 0.36 vs 0.006"结论**作废**。

### 实现（60 号设计；51/51 测试绿）
- 评价器修复：saga 门禁只对执行类动作生效，安全回滚不计罚；度量三分（sla_violation / duplicate / downstream_violation）。
- **WAIT-SLA 契约**：非幂等工具 UNKNOWN_OUTCOME 下 RETRY 仅在补偿清除或"等满可见性 SLA + SLA 后查询确认未提交"时解锁（cleared_to_retry）；SLA 内查询不解锁；动作掩码实现。
- **B-new（反例变异 R2）**：动作序列签名、全种群聚合、只打涉事基因、死因→修复动作映射、过契约修复+独立 validator、预算对齐。
- **Safety Gate**：6 场景行为电池硬过滤 + 分层生存者（ABG 臂）。

### 第三轮诊断（61 号；diagnostic3 manifest 017b3454…；新种子 2026110900）
- **AB vs A：+0.119 [0.066,0.183] p=0.0002——B-new 组合增益成立，D-061 负结果逆转**。
- **AwaitSLA vs A：+0.089 p=0.005；AwaitSLA vs AwaitFixed：+0.054 p=0.003——WAIT-SLA 有效且优于固定等待**。
- AB vs AwaitSLA all +0.031 p=0.0072；但 validation +0.031, p=0.244（n.s.），因此 Q10 搜索增量尚未证明独立泛化。
- AB 行为违规 0（A 0.060）；AB seed 稳定 [0.543,0.531,0.543]。
- AB vs hand −0.282（收窄但未超越）；ABG 门禁有害（−0.193，负结果）；B 单独劣于 NSGA-II（−0.074，负结果）。
- Q9：validation AB vs A +0.142 p=0.008（泛化显著）。

### 判定
- 契约保持（A）、WAIT-SLA、B-new 三机制**各有独立消融证据**；Safety Gate 与 B 单独为负结果（如实保留）。
- 机制消融有诊断性正向证据；但 AB vs NSGA-II all p=0.062、validation p=0.2277，尚未证实优于标准 EA；行为安全保证仅限明确工具合同假设。**不得**声称超越专家。
- 第一项创新**接近成立**；待功效核算+预注册+正式 A-3b。正式实验、Pilot B、A800 等继续 HOLD。

### 下一步
功效核算（54-cluster 方差 cluster_sd≈0.40）→ preregistration 冻结交用户批准 → 正式 A-3b。


## 决策 D-063：功效核算与正式 A-3b 预注册准备（2026-11-08）

D-062 已完成诊断性阶段，但正式确认性实验仍未获授权。完整计划见 `62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md`。

### 证据边界
- AB vs NSGA-II all +0.1049、p=0.062（54 clusters）；validation +0.1173、p=0.2277（18 clusters）：均未显著。
- AB vs A validation +0.142、p=0.0082：支持 B-new 在 A 上的增量，但不能替代主比较。
- AB vs AwaitSLA validation +0.031、p=0.244：Q10 的搜索增量尚未证明泛化。
- AB vs Hand −0.282：仍显著落后专家手工策略。
- WAIT-SLA 与 B-new 的机制级诊断结果保留；Safety Gate 和 B 单独的负结果必须保留。

### 必须先修复
当前 `stats.py` 仍读取 diagnostic2，`run_diagnostic3.py` 不产出统计，部分 61 号报告对比不能从已提交分析入口直接再生。必须新增 diagnostic3 专用可执行分析器并从原始数据复算，随后才做功效冻结。

### 初步设计
以 held-out test 上 AB vs NSGA-II 为唯一主要比较；balanced class-success 为候选主要终点；双侧 alpha=.05。次要对比 AB vs A、AwaitSLA vs A、AwaitSLA vs Fixed、AB vs AwaitSLA 使用 Holm。Hand 只作参考，不预设非劣效或超越专家。安全指标作为硬接受条件，安全保证只限于明确合同假设和测试模型。

### 初步功效
以 validation-only cluster SD=.3914 做 paired t 近似：MDE=.10 时 80%/90% 约需 123/163 个可分析 clusters；15% 失效预留后约 145/192。MDE=.08 时约 190/254。当前只有 18 validation clusters，最终样本量须用经验 paired-cluster 分布做 Monte Carlo sign-flip/bootstrap power simulation。cluster 是 task×fault composition，不能用 seed/episode 替代。

### 授权
GO：统计流水线修复、empirical power simulation、任务族扩展可行性、预注册草案和 CI。
HOLD：正式 A-3b、任何 held-out test 调参/查看、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。预注册须交用户审阅批准后才冻结。


### D-063 执行接管边界补充（2026-11-09）

本次仅细化 D-063 的执行顺序、交付和授权边界；**不代表统计分析器、功效仿真、任务族扩展或预注册已经完成**。当前状态：Stage 0 NOT STARTED / formal A-3b HOLD。

**唯一首要任务：Stage 0 — diagnostic3 独立统计复现。**

1. 新增 experiments/pilot_a3b/analyse_diagnostic3.py（或显式输入参数的通用 CLI），必须从 diagnostic3_results.json 读取，不得静默回退 diagnostic2。
2. 输出 all/train/validation；完整复算 AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II。
3. 推断单位为 task × fault-composition cluster；seed 为嵌套重复。报告 cluster SD、95% CI、paired cluster sign-flip p、效应量、seed 稳定性和适用的 Holm 校正。
4. 对 episode 唯一性、配对完整性、cluster 一致性、seed 缺失、split 泄漏、分母语义、输入与 manifest 哈希设置 fail-closed 检查和 synthetic tests。
5. 从原始数据独立再生 61 号统计；任何差异必须解释，不得为了匹配报告而硬编码结果。

**Stage 1：** 使用复算后的 cluster-level paired differences 做经验 Monte Carlo 功效仿真；至少报告 MDE=.08/.10/.1173、双侧 alpha=.05、80%/90% power、15% cluster 失效预留、Monte Carlo 误差及 SD 敏感性。18 个 validation clusters 的 SD 估计不稳定，必须披露。

**Stage 2：** 从原始 task/split/scenario manifests 核实“总计 6 个任务族”与“validation 2 个任务族 ×9=18 clusters”的计数关系；检查模板/轨迹近重复与 split 泄漏，报告真实可用独立 cluster 数。不得通过增加 episode 或 seed 伪造独立 cluster。

**Stage 3：** 起草 64 号预注册候选。唯一主要比较为 AB vs canonical NSGA-II；必须先澄清 R1/R2 条件恢复与 R3/R4 正确升级的主要终点公式、分母、类别权重和 cluster 聚合。次要比较 Holm；Hand 仅作参考。文件标记 DRAFT — NOT FROZEN，提交用户审阅。

**证据边界继续有效：**
- AB vs NSGA-II all p=.062、validation p=.2277，均未显著；
- AB vs AwaitSLA validation p=.244，Q10 搜索增量尚未证明泛化；
- AB vs Hand −.282，仍落后强手工策略；
- AB vs A、WAIT-SLA 的正向诊断性结果不能替代主要比较；
- 安全保证只限明确工具合同假设。

**授权：** GO 仅限统计复现、synthetic tests、历史诊断数据功效规划、任务族审计、预注册草案、CI 和文档维护。正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 继续 HOLD。即使用户批准预注册，正式 A-3b 仍需另行明确授权。


## 决策 D-063：统计独立复算、Monte Carlo 功效、任务族扩展审计与预注册草案（2026-11-08）

### Stage 0 — 独立复算入口（analyse_diagnostic3.py，17/17 测试绿）
- 独立读取 diagnostic3 原始 rows，结构检查（配对/seed 嵌套/cluster 分组/重复/泄漏/分母）零问题；manifest 复算一致。
- **全部 7 个对比的 Δ 与 61 号逐位一致**（AB vs nsga2 +0.1049、AB vs A +0.1193、AwaitSLA vs A +0.0885、AwaitSLA vs Fixed +0.0535、AB vs AwaitSLA +0.0309、AB vs hand −0.2819、B vs nsga2 −0.0741）。
- p 值第 3 位微差（如 primary 0.0647 vs 61 的 0.062）——置换检验 MC 种子不同所致，显著性结论不变；已如实记录，未改计算逻辑。
- 输出：diagnostic3_recomputed.{json,csv,md}；测试覆盖配对/缺臂/重复/cluster 失配/seed 缺失/泄漏/分母/可复现性/Holm/哈希变化。

### Stage 1 — Monte Carlo 功效（power_simulation.json，2000 次/点，seed 20261110）
- 基于真实 cluster 差值（主对比 sd=0.404；validation-18cl sd=0.391）；seed 嵌套不膨胀。
- **主对比（AB vs NSGA-II）所需 test clusters：MDE 0.08→254、0.10→145、0.1173→110（80%）**；含 15% 失效预留 299/171/130。90% 档更高。
- 校正 t 近似表：旧表对应 validation sd；用主对比 sd 需求上浮（145 vs 123 @MDE0.10）。
- ICC ≈ −0.09（任务族间无相关性检出，cluster 独立性假设成立）；18 clusters 方差不稳已如实声明（三源敏感性并报）。

### Stage 2 — 任务族扩展审计（63 号，task_family_expansion_audit.json）
- 576 个合同语义有意义的三步序列、18 种合同 profile；**朴素按 profile 选择会集中 ledger（重叠 2.0/3），多样性贪心降至 0.83/3、零重叠对 144/406**。
- 推荐划分：train 8 族 / val 4 族 / **test 锁箱 17 族** = 72/36/**153 clusters**。
- 功效缺口（153 vs 含预留 171）替代序：MDE 降至 0.1173（充足）→ 接受 75–80% 实际功效 → 扩至 19 族；**禁止**重复 episode 冒充 cluster。
- 泄漏面登记：10 工具池共享（主张限定为新序列/合同组合）、故障词汇共享、生成器同源。

### Stage 3 — 正式预注册草案（64 号，CANDIDATE）
主要唯一比较 AB vs NSGA-II；次要 4 项 Holm；Hand 只作参考；指标含 CondRecSucc 公式、R3/R4 判定、硬安全门（>0 即判负、不外推真实工具）；协议冻结（pop48×60、种子 411/522/633、场景 base 2026111100、test 459 场景 153 clusters 锁箱、预算/排除/停止/存档规则）；解释边界预注册。

### 科学结论
- 统计证据经独立复算**成立**（Δ 全对齐、结论不变）。
- 功效规划**可辩护**（MC + ICC + 敏感性），但 test 153 对 MDE=0.10 含预留目标略低——预注册已内建替代序。
- 任务族扩展**可行**（泄漏受控、主张限定）。
- 正式 A-3b **待批准**；其余 HOLD 不变。

### 下一步
用户审阅 64 号预注册草案 → 批准后按 §5 清单冻结场景哈希并执行正式 A-3b。


## 决策 D-064：64 号预注册草案独立审查 — REQUEST CHANGES（2026-11-09）

### 审查基线

- D-063 final HEAD：`4f23abed3150e09703839b980ad3afc9bb14dfb3`。
- main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。
- GitHub Actions run `42615985837`：真实 success；pilot_a_recovery 28/28、pilot_a3b 68/68，96/96。
- 独立审查记录：`65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md`。

### 判定

D-063 工程交付通过；64 号预注册草案 **REQUEST CHANGES**。CI 通过不等于科学设计/统计预注册通过，正式 A-3b 继续 HOLD。

### 阻断项

1. **主要 estimand 与功效输入不一致：** 64 §3 的 CondRecSucc 只使用 R1+R2；`power_simulation.py` 使用全 R1–R4 的 `class_success`，54 clusters / SD=.404 / Δ=.1049 不是 primary estimand 的功效输入。审查用快速聚合发现 R1/R2-only 只有 42/54 clusters；Δ≈+.3175、SD≈.3189（非正式值，需正式分析入口重算）。
2. **功效方法不符：** 当前代码用参数化正态 N(MDE, empirical SD) 生成；经验重采样分支未调用；所谓 signflip 分支仍用正态近似；无 MCSE，部分小样本 null FPR 偏高。
3. **ICC 证据不足：** ICC 只基于 6 个 task families，validation 只有 2 个；负点估计不能证明 task×composition cluster 独立。
4. **任务族语义/接入未完成：** 576 候选由排列和合同属性筛选，没有语义前后置条件验证；贪心只最小化工具重叠，不优化 profile diversity；所选 23 族覆盖 11/18 profiles、test 覆盖 10/18。正式 8/4/17 场景生成器尚未接入当前固定 6 任务族运行路径。
5. **样本量/MDE 未唯一冻结：** MDE=.10、80% 需 145 有效/171 招募 clusters；153 test clusters 经过 15% 失效后约 130。MDE=.1173 来自历史观察效应，不得未经实质性论证自动作为 MDE。
6. **标签/安全/冻结项不完整：** UNKNOWN 上限、R1/R2 有效 cluster 数和分母、硬安全门对两臂的解释、零事件置信上界、60 初始池实际只使用前 48 个、代码 SHA/CI 证据均需冻结。

### 下一步

唯一首要任务 D-064-A：在 `analyse_diagnostic3.py` 新增 R1/R2-only CondRecSucc paired cluster contrast，输出有效 clusters、每 cluster 分母、Δ、SD、95% CI 和 cluster sign-flip p；R3/R4 分开统计。之后重做功效与层级相关敏感性，再完善正式任务生成器和 64 修订版。

### 授权

**GO：** D-064-A/B/C/D 统计、任务语义、正式场景生成、标签验证、预注册修订、测试和 CI。  
**HOLD：** 正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。64 即使获批准，正式 A-3b 仍需另行明确授权。


## 决策 D-064-A：CondRecSucc 主要终点独立统计与复算（2026-11-09）

### 背景
65 号审查 P0：64 号主要终点（CondRecSucc=R1+R2）与 D-063 功效分析（全类别 class_success）estimand 不一致；145-cluster 功效结论不能用于主要终点。

### 交付
- `condrec_analysis.py`（无硬编码摘要值）+ `test_condrec_analysis.py`（13/13：R1/R2 过滤、R3/R4 排除、配对、seed 嵌套、重复拒绝、缺失报告、cluster 失配拒绝、零分母登记、等权/加权聚合已知答案、bootstrap/sign-flip 可复现、无硬编码、真实数据回归）。
- 产物：`condrec_diagnostic3.{json,csv,report.md}`（含输入 SHA-256、git SHA、命令、MC 次数、种子、统计方法）。
- 66 号报告：`66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md`。

### 真实结果（diagnostic3 原始数据，四层配对、cluster 等权）
- **primary eligible clusters=42**（设计 54）；零分母 12 个（delay_rate_permission + partial_comp_failure × 6 族，结构性不可行，设计内，排除并登记）。
- **AB CondRecSucc 0.5582 vs NSGA-II 0.2407；Δ=+0.3175；SD=0.3189；CI [0.218, 0.411] 不含 0；sign-flip p=0.000125**（真实 cluster 级符号翻转 MC 8000 次）。
- scenario 加权 Δ=0.3145（一致）；配对完整率 1.000。
- **结论翻转**：正确 estimand 下主要对比强显著；原 +0.1049/0.065 是 R3/R4 稀释所致。

### R3/R4 独立安全统计（权衡如实记录）
R3 CorrectEscalation：AB 0.226 vs NSGA-II 0.679；R4 DamageContainment：AB 0.80 vs 0.933——AB 主要终点领先但安全行为率落后，不得互相掩盖。

### 科学判断
诊断数据（非锁箱）支持 AB 在 R1+R2 条件恢复上大幅优于 NSGA-II；42 clusters 足以起步但 SD 估计待 D-064-B 层级敏感性；8 问全部作答于 66 号 §7。

### 决定
GO：D-064-B（CondRecSucc estimand 功效重做 + ICC 层级敏感性）。HOLD 不变。

### 下一步
D-064-B：以 +0.3175/0.3189/42 的真实分布重做功效与 ICC 敏感性（修复 65 P0-2/3），再修订 64 号样本量与 MDE 冻结。


## 决策 D-064-B：进入 CondRecSucc 层级功效与 ICC 敏感性分析（2026-11-09）

### 依据

D-064-A 已完成并通过真实 CI：
- final HEAD：`16e255de627b37713f0ea936df0ddb0dd03ac084`；
- CI run `42631223393` success，109/109；
- CondRecSucc R1/R2-only：42 eligible task×composition clusters，AB=.5582、NSGA-II=.2407、Δ=+.3175、cluster SD=.318856、cluster bootstrap CI [.218254,.411376]、cluster-level sign-flip p=.000125；
- 原始 diagnostic3 SHA-256：`b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`。

### 决策原因

42 个 cluster 嵌套于 6 个 task families，每 family 当前 7 个 eligible compositions。composition clusters 不能被直接视为 42 个独立 family；D-064-A 的 cluster-level CI/p 需要层级相关敏感性。

### 授权范围

**GO：D-064-B**——重建 family→composition→scenario→seed 层级；计算 ICC 和不确定性；用 family-block empirical resampling 与 ICC-controlled hierarchical simulation 重做 power；对 ICC=0/.05/.10/.20、MDE=.05/.08/.10/.1173/.15、80%/90% power、不同 family 数及 attrition 做敏感性；校准 Type-I error 并报告 MCSE。

17 families×9 compositions 是 153 design clusters；按当前 7/9 eligibility 仅约 119 primary-eligible clusters，且此 projection 必须由 D-064-C 任务语义/标签生成器重新核验。

**MDE 不冻结：** +.3175 是观察效应，不是 MDE；.1173 是历史观察效应，仅用于敏感性。D-064-B 只给条件性建议，最终样本量需等待 D-064-C 并由用户审阅。

**HOLD：** 正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。64 号预注册仍为 REQUEST CHANGES。


## 决策 D-064-B：CondRecSucc 层级功效、ICC 敏感性与任务族样本量规划（2026-11-09）

### 交付
`power_hierarchical.py`（无硬编码历史值）+ `test_power_hierarchical.py`（22/22）+ `power_hierarchical.{json,report.md}` + `family_cluster_diagnostics.csv` + 68 号报告。输入 SHA-256 `b9498195…` 与 D-064-A 一致。

### 层级复核与 ICC
6 families × 7 comps = 42 clusters（零分母 12），**6/6 family 均值全正**（0.238–0.381）；family-mean SD 0.059。ANOVA/MoM ICC=**−0.1257**、REML 边界 0、bootstrap CI [−0.159,−0.111]——负值保留，**不解释为独立性证明**（6 families 估计不精确），以 ICC=0/0.05/0.10/0.20 敏感性网格替代点估计。

### 层级推断（D-064-A 重评估）
family-level t：**p=4.6e-05**；精确符号翻转（2^6）：**p=0.03125**（分辨率下限）；block bootstrap CI **[0.272, 0.357]** 不含 0。**层级相关下显著性保持**；p=0.000125 不再是层级 p 值。

### 功效与校准（key cells 10,000 MC，sweep 2,000 MC）
- **Student-t 校准良好（Type-I 0.050–0.056）→ 推荐主检验**；符号翻转 0.031(F=6)/0.05(F=17)；**bootstrap CI 检验反保守（0.08–0.14）不作 α 检验**。
- 修复 2 个校准 bug（MC 符号翻转计数、块重采样中心化）后重跑。
- 所需 families（m=7，MDE=0.10 @80%）：ICC 0→15、0.05→17、0.10→22、0.20→30；双 15% 损耗 → 22/30/40/40。MDE=0.05 在 ≤40 网格不可达。
- **17-family 条件性充分**（低 ICC+低损耗+MDE≥0.10）；否则不足。

### 决定
GO：D-064-C（任务语义 validator + 正式场景生成器 + MDE/样本量唯一冻结）。HOLD 不变；64 号保持 REQUEST CHANGES。

### 下一步
D-064-C：候选任务族语义 validator、8/4/17（或扩大）正式场景生成器落地测试、MDE 事前论证与样本量唯一冻结，之后才修订 64 号。


## 决策 D-064-C：任务语义独立审计、生成器验证与统计设计冻结（2026-11-09）

### 交付
`test_d064c_audit.py`（25/25：对抗 12 + 组合 5 + 标签 3 + 确定性 4）+ `power_final_design_check.json` + `69_D064C_INDEPENDENT_AUDIT_AND_DESIGN_FREEZE.md` + 64 号修订为 R2。

### 审计结论
1. **任务语义**：validator 在已覆盖的 12 类对抗变形测试中全部拒绝（不宣称对任意攻击完备）——12 类恶意变形（删前置/篡后置/换工具/伪回执/毁补偿序/改 goal/重复工具/伪 primary 资格/伪 legacy 等）全部拒绝。通过。
2. **9 故障组合**：声明-注入-标签逐项一致；**发现 1 处注释陈旧**（permission_after_compensatable_prefix 注释写旧三故障、实际注入 step1 permission）——裁定为历史命名兼容+注释缺陷，实现与名称/R3 机制一致，**修注释不改注入**；R3 前提（52/52 族 step0 可补偿）结构性成立；7/9 primary eligibility 不变。
3. **标签器**：来自独立 AND-OR 鲁棒可达判定器（horizon 24），analytic 交叉校验，无算法输入/无 id 作弊；UNKNOWN 0%（不解释为完美，有 mini-env ground-truth 锚定）。
4. **划分**：8/4/40、零重叠、10 profiles×4 families、语义多样性限定抽象 saga 范围。
5. **确定性**：manifest fb832bcc…（最终 CI 42661732606；旧 hash 已废止） / test-family 01b41df8… / test-scenario dded3bb7… 独立重建一致；lockbox 无泄漏。
6. **功效复算（不采信硬编码 0.85）**：最终设计 34 有效 families×5 comps（双 15% 损耗），ICC=0.20 最坏 **power=0.839 [0.832,0.846] ≥0.80 ✓**（10,000 MC）；null 校准 0.054；生成器已更新为 0.839+provenance。
7. **MDE=0.10** 标注 **PROPOSED_MDE_PENDING_ADVISOR_APPROVAL**（非反推、非迁就样本量；需导师确认）。

### 决定
GO：64-R2 独立审计 → 用户批准 → 正式 A-3b。HOLD 不变。

### 下一步
64-R2 独立审计；用户批准后按 64 §5 预检执行正式 A-3b。


## 决策 D-064-R2-REVIEW-R1：预注册独立审计 REQUEST CHANGES（2026-11-10）

### 审查对象与证据
审查 64_A3B_PREREGISTRATION_CANDIDATE.md R2、69 号 D-064-C 报告、power_final_design_check.json、生成器及 GitHub Actions run 42661732606。最终 CI HEAD fa3bc2c5699c0fad8df384bebd44e5510d1d8927，regression success；测试 28 + 146 = 174/174。最终 manifest SHA fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a；test-family/test-scenario SHA 保持 01b41df8… / dded3bb7…。

### 独立审计发现
1. P0 — 主检验协议冲突：64 §2 仍声明 cluster-level paired bootstrap + sign-flip 为主检验，§4 与 R2 摘要却声明 family-level Student-t。必须统一为经过 D-064-B 校准的 family-level two-sided Student-t；sign-flip 仅敏感性，bootstrap CI 仅描述性，并明确每个次要对比的检验与 Holm family。
2. P0 — 自由度写死错误：64 §4 写 df=39，但双损耗功效设计使用 F_eff=34，power_hierarchical.py 的 Student-t 使用 F-1，损耗场景 df 应为 33。正式分析应规定 df=F_observed-1；39 仅适用于完整 40 families。
3. P1 — manifest SHA 过期：64/69/README/决策日志/NEXT_SESSION_PROMPT 的当前状态曾引用旧 af83f065…；最终 CI 42661732606 输出 fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a。test-family 与 test-scenario hash 不变。64 R2 尚未修订，保持 REQUEST CHANGES。
4. P1 — 测试计数记录错误：69 §9 的 126+28 与 CI 实际 146+28=174 不符，已在本轮维护勘误中更正。
5. P1 — 接管提示词顶部状态陈旧：NEXT_SESSION_PROMPT 顶部仍指向 D-064-B，虽尾部已有 D-064-C 完成记录；已更新顶部优先级指针。
6. P1 — MDE 审批顺序缺失：MDE 仍是 PROPOSED_MDE_PENDING_ADVISOR_APPROVAL。正式执行前必须取得导师对 MDE=0.10 的认可，再完成用户明确批准与执行前预检。
7. P1 — attrition 解释需明确：功效代码采用 floor(40*0.85)=34、floor(7*0.85)=5 的固定保守有效规模，不是随机 15% cluster-loss Monte Carlo。预注册须明确这是保守的整数保留设计，并规定实际 family/cluster 缺失的分析规则。
8. P2 — 提交链与措辞：实际 Git 链为 1908026b → fa53d198 → fa3bc2c；“validator 对抗性完备”应降为“12 类已测对抗变形均被拒绝”，不能外推任意攻击完备。

### 决定
64-R2：REQUEST CHANGES。不批准正式 A-3b，不查看或调参 Test。先完成 64-R2 修订（保留候选状态），修复哈希/统计/审批/损耗定义，重新运行 CI，再请求独立 R2 复审。

### 唯一下一任务
修订 64-R2 并更新对应维护文件；独立复审通过后，再取得导师 MDE 认可和用户批准，最后才执行 §5 pre-flight。正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和合并 main 继续 HOLD。


## 决策 D-064-R2：六项审计发现修正与 R3 预注册（2026-11-10）

### 独立核实（非照抄）
R1 六项发现全部核实成立；附加发现实现问题：`family_level_tests` 对 F>15 做 2^F 精确符号翻转枚举（F=40 挂死）——已改小 F 精确、大 F 10,000 次 MC。

### 修复（71 号报告；test_64r3_protocol.py 15/15）
- R2-001：主检验统一为双侧 family 级 Student-t（α=0.05）；bootstrap/符号翻转定位降级。
- R2-002：`family_t_df()` 动态 df（40→39、34→33）；文档禁止固定 39。
- R2-003：**manifest 独立重建确认 fb832bcc…**（与 CI 42661732606 一致）；af83f065… 标注 superseded（POWER_DESIGN 修订前）；test-family/scenario 哈希不变。
- R2-004：attrition 定性为向下取整保守保留（34×5，5/7≠15% 精确）；`missing_data_rules()` 冻结技术缺失/行为失败/完整性失败三分、family 门槛、design_deviation 门禁。
- R2-005：GO 顺序显式含**导师 MDE 认可**；MDE 状态 PROPOSED_MDE_PENDING_ADVISOR_APPROVAL 不变。
- R2-006：H2–H5 逐项定义 + Holm family {H2..H5}；H4/H5 探索性标注。

### 交付
`64_A3B_PREREGISTRATION_CANDIDATE_R3.md`（R2 原文保留）+ `71_64R2_CORRECTIVE_RESPONSE_AND_R3_VALIDATION.md` + 代码修复（power_hierarchical.py）+ 测试。

### 决定
GO：64-R3 **独立复审**（本报告非审计）。HOLD 不变：正式 A-3b（审计 ACCEPTED + 导师 MDE + 用户批准 + pre-flight 前禁止）、Test 接触、其余全项。

### 下一步
64-R3 独立 R2 复审 → 导师 MDE 认可 → 用户批准 → 正式 A-3b。


## 决策 D-064-R3-REVIEW：64-R3 独立审计 REQUEST CHANGES（2026-11-10）

### 审计基线与证据
独立报告：`72_64R3_INDEPENDENT_REVIEW.md`。远端工作分支 HEAD `ca7bb12f89dd72deaac205ffab89cf3054e6be06`；main `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。CI run 42670236796 在该 HEAD 上 success，测试 28+161=189/189；本地复跑相同。独立重建 manifest=`fb832bcc…`、test-family=`01b41df8…`、test-scenario=`dded3bb7…`，与 CI 一致。独立数值证据：`experiments/pilot_a3b/audit_64r3_independent_checks.json`。

### R1 关闭复核
- R2-001：文本统一 family-t，但正式实现不存在，未关闭。
- R2-002：动态 df 成立；零方差处理另有阻断缺陷。
- R2-003：哈希真实重建一致，已关闭。
- R2-004：规则未进入真实处理，且与功效假设不一致，未关闭。
- R2-005：导师审批门文本已写入；批准仍待完成；pre-flight 引用另有问题。
- R2-006：Holm 函数正确，但 H2–H5 未按 R3 实际执行，未关闭。

### 新阻断发现
1. R3 §5 的 pre-flight 错指 §6，真正清单不存在。
2. `missing_data_rules()` 只返回字典；labelled null 仍输出结果，技术缺失只记录不拒绝，family_loss/design_deviation 无字段，可能静默减少 family。
3. 功效固定 34×5，规则却允许 m=1。独立复算 ICC=0.20：平衡 power=0.8400 [0.8328,0.8472]；17 族 m=5 + 17 族 m=1 时 power=0.5777 [0.5680,0.5874]。Type-I 在本次模拟中接近 0.05，但不能外推为任意缺失机制均校准。
4. `family_level_tests()` 对 34 个全零差值返回 `t=inf,p=0`；模拟 `_pvals_student_t()` 对同一输入返回 p=1。必须统一全零、非零常数、近零方差规则。
5. `build_hierarchy()` 硬编码 6/42/7/12，只是 D-064-B 历史诊断函数；正式 40-family 分析入口未完成。
6. H2–H5 没有 family-t + 四项 Holm 的实现；历史 secondary family 是六项 cluster sign-flip。H2/H3 亦未单独校准；H4/H5 探索性无正式报告执行位置。
7. 历史 diagnostic 未发现 Test 使用，但生成器返回完整 Test payload，`run_evolution()` 不检查 split，labels 可经 `evaluate_controller()` 进入适应度；一次性解锁未实现。
8. `signflip_exact` 在 MC 下命名误导，结果未序列化实际 seed。

### 决定
**64-R3：REQUEST CHANGES。正式 A-3b 继续 HOLD。** 不接受“测试全绿=正式分析系统完成”，不接受“字典规则=缺失数据已执行”，不接受“family 等权=composition 数不影响功效”。本轮未运行正式实验、未读取 Test 逐场景标签或结果、未修改实验代码或 R3。

### 唯一下一任务
Executor 完成 R4 corrective revision：实现正式分析/缺失数据/锁箱路径，解决不平衡功效和 Student-t 边界，补齐 H2–H5 与真实 pre-flight，重跑测试和 CI，再提交独立复审。即使复审 ACCEPTED，仍需导师 MDE 认可、用户批准和真实 pre-flight。


## 决策 D-064-R4-PLAN：启动 R4 corrective revision（2026-11-10）

### 审计依据与当前基线
- 权威审计：72_64R3_INDEPENDENT_REVIEW.md，结论 **REQUEST CHANGES**。
- 独立数值证据：experiments/pilot_a3b/audit_64r3_independent_checks.json。
- 本决策记录形成前的工作分支基线：49429053f18d809d3b45e7de44c810cbeb203f7b；main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead 174 / behind 0。后续 Planner handoff 文档提交为 34c7a1cac2da58f91fd468963c30780d2330303d（ahead 175）。
- CI run 42783650910：success，28+161=189/189。该 CI 不关闭 R3 的统计与实现阻断问题。

### R4 唯一任务
Executor 按 73_D064_R4_EXECUTOR_SPECIFICATION.md 完成：
1. 新编号 R4 预注册和真实 pre-flight 清单；
2. 通用动态 40-family 分析入口与 family-level Student-t 唯一主检验；
3. Student-t 全零/非零常数/近零方差边界统一；
4. 缺失数据 fail-closed、technical missing/family_loss/design_deviation 真实计数；
5. 固定 34×5 假设与 composition 纳入规则一致，并重新校准 ICC 网格下功效、Type-I、MCSE、CI；
6. H2–H5 实际提取、配对、family 汇总、四项 Holm 和探索性标记；
7. Train/Validation/Test 结构性隔离与一次性 final-evaluation gate；
8. sign-flip 字段/方法/reps/seed 记录修正；
9. 真实路径测试、CI 和可复核报告。

### 决策边界
- 本次维护提交只建立 Executor 规范和会话交接，不代表 R4 代码已经完成。
- 不修改 R2/R3 历史预注册，不覆盖 72 号独立审计。
- 不读取真实 Test 逐场景标签或结果，不运行正式 A-3b。
- **正式 A-3b、Test 访问/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和合并 main 均继续 HOLD。**
- R4 完成后必须由独立 Reviewer 复审；即使 ACCEPTED，仍需导师 MDE=0.10 认可、用户明确批准及真实 R4 §9 pre-flight 全通过。

### 当前维护提交的性质
本次提交只更新 Planner/Executor 规范与维护交接文件，不包含实验代码、测试或统计结果变更；不得把文档提交或既有 CI success 说成 R4 验收通过。


## 决策 D-064-R4-P1：首批 R4 统计/分析实现（2026-11-10）

### 代码实现
- power_hierarchical.py：新增共享 student_t_summary()，正式 family_level_tests() 与功效模拟 _pvals_student_t() 共用同一边界规则。
- 数值规则：F<2 或非有限值拒绝；容差为 1e-12 × max(1, max|x|)；全零差值 t=0/p=1；非零常数差值按退化极限报告 ±inf/p=0 并标记 nonzero_constant_limit；常规方差使用现有 Student-t beta-tail 实现。
- 新增 test_64r4_student_t.py：11 项合成测试，含 SciPy 已知答案 [1,2,3,4,5]。
- 新增 formal_analysis.py：R4 正式 family-level 主终点分析初版，动态 family 数；固定每族 5 个 primary compositions；AB/NSGA-II 按 scenario/seed 配对；seed→scenario→composition→family 汇总；family 等权；显式 technical missing、family loss、behavioral failure=0；F<34 不给确认性 Student-t。
- 新增 test_64r4_formal_analysis.py：11 项合成测试，覆盖 40/33 families、technical missing、unexplained missing、labelled null、duplicate、unknown roster、behavioral failure、composition 数门槛。

### CI 与修复轨迹
- CI run 42788079429 @ 5e7568050be4d7c1ac7511137bb5627a08ec044d：**success**。
- 真实 job log：pilot_a_recovery 28 tests OK；pilot_a3b 183 tests OK；总计 **211 tests**。
- D-064-C gate PASS；manifest SHA fb832bcc...；test-family SHA 01b41df8...；test-scenario SHA dded3bb7...。
- 首轮 formal analyzer 测试发现测试 fixture 的 pop() 删除了 F33 的最后一条记录，而断言预期 F00；改为确定性 pop(0)，不是更改生产逻辑掩盖错误。修复后 CI success。
- Student-t test-first 提交曾因 helper 尚未实现而失败；随后实现共享 helper，CI success。失败提交保留为真实开发轨迹。

### 科学边界
- 这只是 R4 首批实现，不代表 R4 全部阻断关闭或独立审计通过。
- formal_analysis.py 仍需独立审计；尚未接入正式 runner，也未读取真实 Test。
- 没有运行正式 A-3b，没有新增算法性能结果，没有证明算法提升。

## 决策 D-075：优先验证安全均衡反例引导 NSGA-III（2026-11-10）

- diagnostic3_recomputed.json 显示：AB 的 R1/R2 CondRecSucc=0.547170，高于 NSGA-II 的 0.232704；但 CorrectEscalation=0.183908 低于 NSGA-II 的 0.678161，DamageContainment=0.888889 低于 0.962963，avoidable harm=1.152263 高于 0.497942。
- a3_bridge.evaluate_controller() 的当前三目标未完整纳入 R3/R4；ea.py 的全局 most-common counterexample mutation 可能忽视少数高风险 failure strata；run_evolution() 最终 min(sum(objectives)) 重新引入未预注册标量化。
- 新增 75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md，提出 SBCG-NSGA-III：五维 Pareto 目标、安全可行性优先、family×failure signature 分层反例变异、共享 hand-seed 精英档案、validation 预注册选择规则。
- 这是待验证候选，不是已实现算法或已证实创新。当前 R4 仍优先；正式 A-3b / Test 保持 HOLD。


## 决策 D-064-R4-P2：Test 隔离与 pre-flight 初版（2026-11-10）

- 新增 split_access.py：public_manifest_view() 仅暴露 Test summary/hash/count，不返回 Test scenarios/families；scenarios_for_split() 仅允许 Train/Validation；run_evolution() 在 fitness 前强制 Train-only；ordinary evaluate_controller() 禁止 Test/Battery/unknown split。
- formal_scenario_generator.py 的公开 audit 返回只含 Train/Validation development_scenarios，不再返回 all_scenarios、test_scenarios、split_internal 或 test families/clusters；D-064-C 的标签审计测试已限制在 development split。Test 仍在生成器内部用于冻结哈希和汇总，不被训练调用者接收。
- consume_final_evaluation_once() 要求独立审计、导师 MDE、用户批准及 manifest/code hash 一致；使用 O_CREAT|O_EXCL 原子消费 ledger，先消费再调用 payload_loader；失败后 ledger 仍 consumed。
- formal_preflight.py 只接收元数据，不加载 Test payload；检查批准、CI、hash、split overlap、40/1080 Test roster summary、F≥34、每族5 compositions、pairing、完整性、预算、seed、stopping rule、Test access log=0、ledger=UNUSED；不满足返回 HOLD。
- 新增 21 项 split/preflight 合成测试；Test sentinel 测试不访问真实 Test 标签。

## 决策 D-064-R4-P3：H2-H5 与分析 provenance（2026-11-10）

- student_t_summary() 新增基于同一 beta-tail routine 的双侧 95% CI；退化零方差/常数样本不输出误导性 CI。
- formal_analysis.py 支持输入规范化 SHA-256，并要求 manifest SHA、code SHA、git HEAD provenance 完整才允许确认性 Student-t。
- H2 AB-A、H3 AwaitSLA-A、H4 AwaitSLA-AwaitFixed、H5 AB-AwaitSLA 已接入同一 scenario/seed 配对→composition→family 等权→Student-t 路径。
- 四项 p-value 必须齐全才执行完整四项 Holm；任何一项不具备确认性资格时不做部分 Holm。
- 由于 H2/H3 尚无 null/partial-null Type-I 校准，R4 将 H2-H5 全部标记 exploratory；不能声称确认性次要终点。

### 最新 CI
- run 42791224479 @ f4d8d0d1e314b29f7e6a7627f99293b306f76d92：success。
- pilot_a_recovery 28 tests；pilot_a3b 212 tests；总计 **240 tests**。
- D-064-C gate PASS；manifest fb832bcc...、test-family 01b41df8...、test-scenario dded3bb7... 保持不变。
- 尚未完成正式 runner 接线、R4 power/Type-I 10,000 MC、R4 预注册和独立审计。正式 A-3b 与真实 Test 继续 HOLD。

## 决策 D-076：R4 收尾与 SBCG-NSGA-III 算法提升并行准备（2026-11-10）

### 现状
- R4 已有 Student-t/CI、family-level primary analyzer、H2–H5 exploratory + Holm、Train-only/Test guard、one-time gate、metadata-only pre-flight 初版。
- 尚待 formal runner 接线、outcome-blind composition roster 冻结、power/Type-I 10,000 MC、R4 preregistration 和独立审计。
- 最近完整测试记录：CI 42791224479 @ f4d8d0d，28+212=240 tests success；之后 run 42793004533 @ 14a8a1b regression success。
- 算法候选 75 提出的 SBCG-NSGA-III 尚未实现或验证。历史 AB 的 R1/R2 优势伴随 R3/R4 与 avoidable harm 退化，不能视为整体提升。

### 决策
1. 先收尾 R4 阻断项，准备独立审计。
2. 同时完成 SBCG-NSGA-III 的源代码缺口审计、模块化算法实现和合成测试。
3. R4 独立审计、导师 MDE 认可、用户批准前，不运行真实 benchmark Train/Validation 算法诊断；正式 A-3b 与真实 Test 继续 HOLD。
4. 审批后，以 Train 开发、Validation 冻结选择、Test 独立一次性评价；采用 matched-objective NSGA-II/NSGA-III、Hand、Random、Rule、Reflection、A、AB 和三项消融，保持相同预算、seed、初始化和信息访问权限。
5. 不保证候选必然成功；若无法在安全约束下超越强基线，保留负结果并修改或否决方法。

### 执行规范
唯一任务书：76_EXECUTOR_R4_AND_ALGORITHM_UPLIFT.md。本决策不授权正式 A-3b、Test 访问、A800/ARWM 或真实 LLM API。


## 决策 D-076-EXECUTION：R4 完成审计包，SBCG 性能仍未验证（2026-11-10）

### 交付与证据
- R4：`formal_runner.py` 已接入 `formal_analysis.py`；`64_A3B_PREREGISTRATION_CANDIDATE_R4.md`；真实 pre-flight 输出为 HOLD；功效 24 格×10,000 MC 保存并复算一致。
- SBCG：`sbcg.py`、`sbcg_runner.py`、`sbcg_experiment.py`、`sbcg_config.json`；M1/M2/M3 独立开关、14 个基线/对照/消融、可行 Pareto 档案、无等权和选择、预算与缓存计数。
- 报告：`77_D076_R4_AND_SBCG_EXECUTION_REPORT.md`。
- 测试：pilot_a3b 262 + pilot_a_recovery 28 = 290/290；CI runs 42813004959 和 42813004752 success；远端 clean-clone @4c4c62f 同样 290/290。

### 决定
R4 状态只能是 **READY_FOR_INDEPENDENT_REVIEW**，提交独立 Reviewer，不自评 ACCEPTED。SBCG 当前只有合成实现证据，没有任何性能提升、强基线或消融结论；不得把代码实现写成创新成立。

### 数据边界
只运行合成 fixtures/sentinels 和历史 diagnostic3 开发数据的功效模拟；未运行真实 Train/Validation 算法诊断，未读取 Test，未启动 Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox，未合并 main。

### OPEN
安全非劣界值和 hypervolume reference point 尚未冻结；导师 MDE、用户批准和独立 R4 ACCEPTED 均未取得。唯一下一任务是 R4 独立复审；审批满足后才可运行 Train-only SBCG 强对照/消融。


## 决策 D-078：D-076 独立复审 REQUEST CHANGES（2026-11-10）

复审基线：`3d2dacf0871ab0f030084f6ed2d62e17ba524ddd`；main 未变为 `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。CI run 42814630988 success；执行报告记录 290/290；本轮无真实算法性能数据。

### R4 结论：REQUEST CHANGES
1. `run_current_preflight` 固定 paired_rows_valid=false、数据质量计数 None、observed families=0、composition counts={}、design_deviation=true；正式 preflight 又要求这些 outcome-dependent 字段通过，同时要求 Test access log=0、one-time ledger=UNUSED，导致 pre-run GO 生命周期循环。
2. Power 24 格只覆盖 F × ICC × null/MDE，固定每族 5 compositions，未模拟 technical missing / composition attrition。F=40、ICC=.20 的 null Type-I=0.0547，95% Wilson CI [0.0504,0.0593]，需要调查。
3. `consume_final_evaluation_once` 未要求 preflight GO / CI 状态；`formal_runner` 未与一次性 gate 形成唯一生产调用链。

### SBCG 结论：NOT READY FOR TRAIN/VALIDATION PERFORMANCE DIAGNOSTICS
1. 新旧 niching 投影均未除以方向向量平方范数；新 runner 的归一化和 niche count 也不是 canonical NSGA-III；legacy NSGA-III 还使用 min(sum(objectives))。
2. M1 f3 实际为 `unnec_esc + unnec_actions_r12/10`，偏离 75 号候选的 `UnnecessaryActionCost`。
3. `run_sbcg_evolution` 在 Train archive 上调用 `select_validation_candidate`，Validation 流程未接通。
4. 14 臂仅注册/单臂执行，统一预算 orchestrator 尚缺；offspring 二次 cache lookup 夸大 cache_hits。

### 决策
- 新增 `78_D076_INDEPENDENT_REVIEW.md`，结论 REQUEST CHANGES。
- 正式 A-3b、真实 Train/Validation 算法诊断、Test、Pilot B、A800/ARWM、真实 LLM API 继续 HOLD。
- 唯一下一任务：D-078 corrective revision，修复上述阻断并重新独立复审。



## 决策 D-079：D-078 首轮合成 Train/Validation 结果不支持性能提升（2026-11-10）

D-078 实验 workflow [42820836080](https://github.com/yujian777555/kaitibaogao/actions/runs/42820836080) success；回归 workflow [42820836104](https://github.com/yujian777555/kaitibaogao/actions/runs/42820836104) success。提交 `7cbbac54e2f3d8680a4851f7a7c79cd02b3cd8d3` 保存结果。

- 14 arms × 3 seeds = 42 runs；合成 Train=216、Validation=108；pop=8、G=5；Test 未访问，LLM API=0。
- 多数算法 selected Validation metrics 完全重合：CondRecSucc=1.0000、AvoidableHarm=2.4444、ActionCost=4.3929。当前 SBCG 没有展示主指标提升证据。
- Reflection proxy 三个 seed 均 HOLD；no-M3 三个 seed 的 CondRecSucc 为 0、0、0.3929。
- Pareto candidate count 差异只是搜索/多样性现象，不等于任务性能改善。Validation 是经过候选选择的指标，存在 selection optimism。
- D-076 复审报告对应旧代码 SHA；后续 D-078 已修订 canonical NSGA-III、M1 f3、Train→Validation selection 和 cache accounting，需以最新代码与 CI 为准。R4 technical-missing power 与 pre-run/post-run gate 仍独立待核验。

**决策：** 不宣称 SBCG 优于基线。下一任务 D-079：按 family/scenario 拆解结果，审查 CondRecSucc 天花板和不同臂相同结果的原因，构造更有区分度的难度分层合成挑战集，并预注册后再做机制实验。Test/A800/真实 LLM 继续冻结。


## 决策 D-080：D-079 evaluator 修正与 Train-only challenge preregistration（2026-11-10）

### 原始数据初查（D-078 matrix_results.json）
- 42 runs 中，32 次 selected FSM fingerprint 与 Hand FSM 完全相同。
- Hand FSM 在已选 Validation 候选上：R1/R2 84/84 成功；R3 CorrectEscalation 0/12；R4 DamageContainment 12/12。
- 多个算法选择相同 Hand FSM 不能解释为优化器已收敛到相同算法；必须区分初始池锚点、Pareto 候选与 Validation tie-break。
- 这些数字为原始 artifact 初查，需由 D-079 独立脚本和 CI 复核。

### 实现问题与修复方向
1. score_episode 将成功工作流的预期 active effects 计为 actual/avoidable harm；修正为成功任务不计预期 active effects，duplicate 仍计 harm，未完成任务的 active effects 才计 residual。
2. scenario_verdict 的 R3/R4 minimum-harm 计算忽略了此前正常完成但不可补偿的前缀效果；更新为计入所有此前已提交且不可补偿的步骤。
3. D-078 runner 以旧 analytic scenario_verdict class 评分；D-079 新 evaluator helper 使用 robust AND-OR label，analytic class 仅作为交叉核验。
4. 增加 D-078 per-family/per-scenario 重建审计，并生成 8 Train-only families × 6 difficulty strata × 3 repeats × search/diagnostic roles 的挑战集候选。

### 预注册与授权
- 预注册候选见 80_D079_DIAGNOSTIC_AND_CHALLENGE_PREREGISTRATION.md。
- 当前实现/测试为 CI PENDING；challenge manifest hash 尚未冻结。
- 在 CI 成功并提交 manifest lock 前，不运行新优化器；manifest lock 后仅允许非确认性 Train-only diagnostic。
- 不访问 Validation/Test，不运行正式 A-3b，不启动 Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 或 ThinkingBox；不合并 main。
- 该诊断不构成 EC 性能提升证据，不改变毕业论文创新点状态。



## 决策 D-081：修正 D-079 Train family 假设并关闭 D-078 自动重跑（2026-11-10）

### CI 事实
- regression run 42827879313 在 282 tests 后失败，新增 D079 challenge generator 的 setUpClass 抛出 ValueError：其错误要求每个 Train family 同时存在 compensatable 与 uncompensatable 工具。
- D-078 workflow run 42827879133 在 full regression preflight 失败；14-arm execution step skipped，没有新算法实验数据。
- D-078 原始 artifact 不变，D-078 workflow 已改为 workflow_dispatch only，普通 push 不再触发重跑。

### 修正
- D6 改为 partial commit + compensation unavailable，可由工具合同不可补偿或运行时补偿不可用实现；不要求所有冻结 Train families 都包含不可补偿工具。
- 新增 D6 测试，要求 compensation_available=false 且 robust label=R4。
- 其他 evaluator 修复与 D-078 audit 脚本尚待下一轮 CI 验证。

### 当前决策
- 继续 D-079，不运行新的算法性能实验，直到 challenge manifest candidate 通过 CI、完成审查并将 SHA-256 锁入仓库。
- 不访问 Validation/Test，不启动正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 或 ThinkingBox；main 不合并。



## 决策 D-082：D-081 corrective commit 已推送，等待 CI（2026-11-11）

### 已核实事实
- D-081 commit：`192f958847fb31d7d704cfa0760201dcd8371e32`，提交信息：D-079: fix Train-only R4 strata and disable D-078 auto-rerun。
- 工作分支相对 main：ahead 252 / behind 0；main 未修改。
- D-079 首轮 regression run 42827879313 失败于新增 challenge generator 的 family composition 假设；D-078 run 42827879133 在全量测试 preflight 失败，14-arm 算法执行 skipped。
- 修复内容：D6 允许 runtime compensation unavailable 作为 R4；D-078 workflow 改为 workflow_dispatch only。
- D-081 commit 的 combined status 查询返回空 checks；尚无 corrective CI success 证据。

### 判断与约束
- 代码修复已提交不等于测试通过。D-079 harm/robust-label audit 与 challenge generator 仍须通过完整 regression CI。
- D-078 42-run artifact 不得覆盖；D-079 288 场景 manifest 未锁 hash 前不得启动新优化器。
- formal A-3b、Test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox、main merge 继续 HOLD。

### 唯一下一任务
核验 D-081 对应 GitHub Actions regression run；若成功，审查并复核 D-079 audit outputs 与 Train-only challenge manifest，随后提交 SHA-256 manifest lock。若 CI 未触发，先触发 CI，不得绕过门禁。
