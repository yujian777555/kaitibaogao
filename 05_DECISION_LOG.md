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
