# kaitibaogao — 硕士学位论文开题研究

**唯一研究仓库：** https://github.com/yujian777555/kaitibaogao  
**研究主线：** Evolutionary Computation for AI Agents（演化计算赋能大语言模型智能体）  
**当前阶段：** D-064-C 完成；64-R2 独立审计 R1 = REQUEST CHANGES；正式 A-3b HOLD（须先修订预注册、独立复审、取得 MDE 导师认可及用户批准）  
**状态日期：** 2026-11-10

## 1. 项目边界（必须遵守）

本仓库是本次硕士开题工作的唯一项目仓库。后续任何会话：
- 只允许读取、更新和维护 yujian777555/kaitibaogao；
- 不得读取用户的其他 GitHub 仓库，不得把其他项目的代码、实验、结论或状态混入本项目；
- 可以检索公开论文、出版社页面、会议论文集、arXiv、公开 benchmark 文档；
- 论文代码仓库只作为公开文献链接记录，除非用户另行授权，不读取其他 GitHub 仓库；
- 每轮研究结束必须更新本仓库、更新 SESSION_HANDOFF.md，并提供下一会话可直接复制的接班提示词。

## 2. 研究方向定义

本课题研究 **演化计算如何优化 AI Agent**，包括但不限于 Agent 结构、工作流、工具使用、规划策略、记忆机制、多智能体协作、行为策略及其跨任务适应能力。

必须区分：
- **EC for Agent（本项目主线）：** 演化计算是核心优化方法，Agent 是优化对象；
- **LLM for EC（非主线）：** 用大模型生成或改进演化算法、算子、适应度函数；
- **一般 Agent 自我反思 / RL：** 可作为相关工作、对照方法或辅助机制，但不能替代演化计算核心。

## 3. 当前研究原则

1. 不把“使用遗传算法优化 Agent”本身视为创新。
2. 不因某个方向已有论文就直接放弃；必须比较具体机制，寻找可改进、可融合、可纠正的不足。
3. 必须核实编码表示、初始化、选择、交叉、变异、生存者选择、适应度、档案、多样性、泛化和实验设置。
4. 必须区分已发表论文、预印本、技术报告和项目网页。
5. 不得把论文摘要中的宣称直接当成已验证事实；关键论文需精读正文、算法、消融和局限。
6. 不预先锁定题目或创新点；候选必须经过强基线对照和可证伪实验设计。
7. 硕士论文需要形成 2–3 个相互关联的创新点，研究方法以演化计算为核心，题目风格需与导师团队的演化计算研究方向相协调。

## 4. 学校模板硬性要求

依据用户提供的《河北工业大学研究生学位论文开题报告》模板：
- 硕士开题报告正文不少于 6000 字；
- 参考文献不少于 30 篇；
- 外文文献不少于 30%；
- 近五年文献不少于 30%；
- 内容应覆盖选题来源、背景目的意义、国内外现状及发展动态、研究目标与内容、关键科学问题、预期创新点、研究方案及可行性、研究基础、困难与对策、研究计划；
- A4、宋体、小四号、1.5 倍行距。

## 5. 仓库文档索引

| 文件 | 内容 |
|---|---|
| 00_PROJECT_CHARTER.md | 研究边界、目标、原则、交付物 |
| 01_SEARCH_PROTOCOL.md | 文献检索式、数据库、纳入排除标准、检索日志 |
| 02_LITERATURE_REGISTER.md | 文献总表、分类、状态、核心结论和链接 |
| 03_MECHANISM_COMPARISON.md | 核心论文机制级对照、重复风险、候选缺口 |
| 04_OPENING_REPORT_PLAN.md | 开题报告结构、题目候选、实验设计和合规检查 |
| 05_DECISION_LOG.md | 研究决策和阶段变化记录 |
| SESSION_HANDOFF.md | 最新状态、接班要求、下一会话提示词 |

## 6. 当前状态（2026-11-02）

- 仓库初始状态只有 README，已建立首批研究文档。
- 已完成第一轮宽口径公开文献检索，登记了直接演化 Agent、Agent 架构搜索、相邻自进化方法、综述、benchmark 和演化计算基础文献。
- 已识别出两篇不同的 ICML 2026 论文都使用 EvoMAS 名称，必须严格区分：
  1. Hu et al., *Evolutionary Generation of Multi-Agent Systems*；
  2. Wei et al., *EvoMAS: Heuristics in the Loop—Evolving Smarter Agentic Workflows*。
- HFlow 已明确包含性能、人类偏好、成本三个目标的 Pareto 生存者选择；GEPA 已包含实例级 Pareto 候选选择；不能将普通 Pareto 选择本身作为新颖点。
- 研究方向尚未最终确定；当前候选包括任务分布泛化与质量多样性、执行过程归因、演化算子协同适应等，均需进一步否证。

## 7. 下一步

优先完成：
1. 对 EvoAgent、两篇 EvoMAS、EvoCF、HFlow、GEPA、AgentSquare、ADAS、AFlow、MaAS、AgentSwift、MASS、GPTSwarm、AgentNet、TPGO 做算法级精读；
2. 扩展和交叉核对 2022–2026 文献，补齐完整作者、年份、会议/期刊、DOI/arXiv 和论文版本；
3. 做机制矩阵，逐项审查编码、算子、适应度、选择、档案、多样性、迁移、鲁棒性；
4. 形成 2–3 个可证伪的创新候选，再确定开题题目；
5. 按学校模板撰写开题报告，不提前拼凑空泛综述。

**重要：本 README 中“首批文献”不等于穷尽全部文献。文献检索必须持续迭代并保留检索记录。**


## 8. 第二轮研究更新（2026-11-02）

第二轮检索增加了 EvoTest（ICLR 2026）、COvolve（GECCO 2026）、CATArena（ICML 2026）、M*（NeurIPS 2026）、E-SPL（ICML 2026 FoGen workshop）、INSPO、SkillRL、EvoSkills、MemEvolve、MemSkill、Live-Evo、EvoTeam、Evolving Agent Teams 等文献。

**重要进展：** EvoTest 论文第 16 页明确指出其当前采用简单的 (1+m) 演化策略和 UCB 选择，可能陷入局部最优，并将更复杂的种群演化、Quality-Diversity 和自动程序综合列为未来方向。它同时指出单任务测试时学习容易产生任务特定过拟合。由此新增候选 D：面向任务分布变化的多目标演化测试时自适应。该候选尚未通过创新性审查。

后续必须重点区分：
- EvoTest：测试时整套 Agent 配置演化；
- M* / MemEvolve：Agent 记忆程序/记忆架构的演化；
- E-SPL / INSPO / SkillRL：提示、指令、策略或技能与 RL 的协同演化；
- COvolve：策略与环境的对抗协同演化；
- EvoTeam / Evolving Agent Teams：团队组织、交互规则或 Agent 团队重构；
- HFlow / 两篇 EvoMAS：工作流/多智能体系统的演化搜索。

后续不能把“使用种群”“使用 QD”“跨任务迁移”或“在线演化”单独当作创新，必须明确与这些直接相关工作之间的机制差异。


### 新增深读文件
| 文件 | 内容 |
|---|---|
| 06_EVOTEST_DEEP_DIVE.md | EvoTest 原文方法、实验协议、局限性和竞争工作 |
| 07_CANDIDATE_D_TEST_TIME_ADAPTATION.md | 候选 D 的问题定义、算法假设、实验设计和停止条件 |

当前文献登记为 72 条，但仍不是穷尽式综述；下一轮继续追踪综述引用、正式会议论文集和国内研究。


## 9. 第三轮研究状态（2026-11-02）

文献登记已扩充至 104 条。新增研究显示，测试时 Agent 演化、Agent harness 演化、技能多目标优化、Agent 团队演化、可进化性选择和 evaluator co-evolution 均已有直接工作。因此候选 D 已降为 NO-GO（宽泛表述），当前仅优先审查候选 G：组件交互感知的演化重组。

新增文件：
- 08_CANDIDATE_SCREENING.md：D/E/F/G 候选筛选和状态；
- 09_CANDIDATE_G_INTERACTION_AWARE_RECOMBINATION.md：组件 epistasis 估计与 linkage-aware crossover 方案。

候选 G 尚未通过相关工作审查，不得写入最终开题题目或创新点。


### 本轮新增文件索引
- 08_CANDIDATE_SCREENING.md：候选 D/E/F/G 的去留与当前优先级；
- 09_CANDIDATE_G_INTERACTION_AWARE_RECOMBINATION.md：候选 G 的问题定义、交互效应公式、算法草案和证伪实验。

最新候选 G 仍处于 PRIORITY FOR AUDIT，不代表最终开题方向。


## 2026-11-02：硕士论文 2–3 个创新点与小论文路线

用户明确要求：硕士论文必须有 2–3 个独立创新点，每个创新点分别形成一篇小论文投稿。该要求已成为研究硬约束。

总题目工作稿调整为：

**《面向大语言模型智能体的交互感知演化优化方法研究》**

三层研究规划：
1. 任务条件化的 Agent 组件交互效应估计；
2. 交互感知的演化重组算子；
3. 任务分布变化下的交互结构迁移与自适应演化（条件性第三篇，必须通过独立新颖性 Gate）。

新增文件：
- 10_THESIS_INNOVATION_AND_PAPER_ROADMAP.md：三个创新点、三篇小论文、独立实验和投稿 Gate 的完整规划。

文献总表新增 MESH-Harness、Evo-Harness、AgentEvo、ARTEMIS、EvoMAS。当前创新点仍未全部通过新颖性审查，不得把路线图误当作已确认创新成果。


## 2026-11-02 第四轮：创新可行性审查

新增直接相关文献与基础方法：Liu (2026) CCI、Lauziere et al. (2026) Prompt component regression、GOMEA/CGOMEA、LK-GOMEA、DG2，以及 ToolSandbox、tau-bench、AppWorld。

**重要决策：**
- 普通组件交互效应估计（差分公式、全因子分析、Shapley、pairwise regression）已被直接相关工作覆盖，原创新点一表述 NO-GO。
- 修订候选一：预算受限、任务条件化的稀疏 Agent 组件交互结构识别，HOLD，先做已知真值和主动采样预实验。
- 修订候选二：交互结构驱动的 Agent 约束最优混合演化，HOLD，优先验证是否实质优于 GOMEA/GOM、CGOMEA、LK-GOMEA 和 Agent crossover。
- 跨任务交互结构迁移暂缓，不能现在写成第三个正式创新点。

新增文件：
- 11_INNOVATION_FEASIBILITY_AUDIT.md：完整可行性判断、相关工作威胁、修订算法、基线、实验和 GO/HOLD/NO-GO 条件。

当前合理规划为 2 个核心创新候选 + 1 个储备方向。只有两项都通过预实验才进入正式创新点；第三项不凑数。


新增文件：
- 12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md：两个核心创新候选的数学定义、主动交互探测、约束最优混合、最小预实验和 GO/HOLD/NO-GO 门槛。

下一步不再堆论文数量，先完成合成真值 Agent landscape 的 Phase 0 算法验证。


## 2026-11-02 第五轮：演化计算如何调参

已形成明确的三层调参方案：
1. 离线算法配置：训练任务上用 irace / iterated racing 调整少量数值与类别超参数；
2. 在线反馈控制：discounted-UCB / AOS 根据配对改进的置信下界和 rollout 成本，调整变异强度与算子选择；
3. 统计门禁：\(\alpha\)、最小实际改进幅度和硬约束预先锁定，不进入性能调参。

主算法为 categorical genotype + GOM，不使用 DE 专属 F/CR。Phase 0 固定 N=8，敏感性比较 N=4/8/12；后续再比较 IMS/P3。在线 AOS 不作为独立创新，如果不优于离线调参固定策略则删除。

新增文件：
- 13_EC_PARAMETER_CONTROL_PLAN.md：完整参数清单、初始取值/搜索范围、离线 irace、在线 UCB/AOS、统计门禁、A/B/C/D 消融和停止条件。
- 02_LITERATURE_REGISTER.md 新增参数控制相关文献 118–124。


## 2026-11-02 第六轮：算法形式化设计 V1

新增 14_FORMAL_ALGORITHM_DESIGN_V1.md，把两个候选算法具体化：
- TCAIL：任务条件化 Group-ARD + 合法配置可识别性门禁 + interaction-only posterior IG 主动采样；
- CI-GOM：基于可信非加性交互的 FOS + contract-aware deterministic minimal repair + posterior-aware donor + paired sequential acceptance。

本轮纠正：负交互同样代表 linkage，不能只用正交互建边。按 \(P(|\Delta|>\delta)\) 判断非加性依赖，符号只用于 donor scoring；负交互不是硬约束。

算法设计仍为待验证规格。下一步实现合成真值模拟器和可复现的参数/算法消融，不调用真实 LLM。


## 2026-11-02 研究执行顺序正式调整

用户决定：**先不写硕士大论文，逐项验证每个创新点。** 新增权威执行协议 15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md。

当前只执行创新点一 TCAIL。CI-GOM 在 Gate-1 通过前冻结；跨任务迁移在 Gate-2 通过前冻结。每项必须经过强基线、同预算、多 seeds、消融和独立复审。合成实验通过只是必要条件，真实 Agent 验证仍不可缺少。第三项若 Gate-3 不通过就删除，最终允许以两个已验证创新点完成毕业论文。

**当前状态：TCAIL_SPECIFICATION_REVIEW_PENDING；不启动毕业论文正文撰写。**


## 2026-11-02 TCAIL 首轮规格审计结果

新增 16_TCAIL_SPECIFICATION_AUDIT_R1.md。对 14_FORMAL_ALGORITHM_DESIGN_V1.md 的独立数学/统计审查结论为 REQUEST REVISION：发现 pairwise estimand 背景依赖未定义、结构性不可识别与当前样本不足混淆、Bernoulli/Beta 与 Gaussian IG 更新不一致、edge 多重比较规则不完整、interaction-only IG 与 Bayesian D-optimal 的关系未处理、16 配置不足以证明可扩展性等问题。

因此当前不进入正式 Phase 0 性能实验。下一步先修订 TCAIL 规格，再由独立审查确认，之后才编码。没有运行实验、没有性能结果、没有 Gate-1 PASS。


## 2026-11-02 TCAIL V2 规格修订与相关工作审查

新增：
- 17_TCAIL_FORMAL_SPECIFICATION_V2.md：修订 pairwise estimand、reference background、link-scale/reward-scale、identifiability state machine、Gaussian/Bernoulli/Beta likelihood、Bayesian FDR、decision-risk acquisition 和 8/10/12-slot 实验协议。
- 18_TCAIL_RELATED_WORK_AUDIT_R1.md：首轮相关工作与新颖性审查。

首轮结论：TCAIL V1 不能直接实现；V2 已完成纸面修订，但仍待独立复审。interaction-only IG / Bayesian D-optimal、Bayesian FDR、组件交互回归和预算约束 Agent harness search 均有既有先例。TCAIL V2 仍是条件性候选，不能宣称新颖性已成立。

特别说明：TCAIL 是统计建模/主动实验设计模块，本身不是完整 EC 算法。其能否成为毕业论文创新点，取决于是否对后续演化搜索提供独立、可测量的价值。当前不实现、不运行正式 Phase 0。

## 2026-11-02 TCAIL V2 规格修订与相关工作审查

新增：
- 17_TCAIL_FORMAL_SPECIFICATION_V2.md：修订 pairwise estimand、reference background、link-scale/reward-scale、identifiability state machine、Gaussian/Bernoulli/Beta likelihood、Bayesian FDR、decision-risk acquisition 和 8/10/12-slot 实验协议。
- 18_TCAIL_RELATED_WORK_AUDIT_R1.md：首轮相关工作与新颖性审查。

首轮结论：TCAIL V1 不能直接实现；V2 已完成纸面修订，但仍待独立复审。interaction-only IG / Bayesian D-optimal、Bayesian FDR、组件交互回归和预算约束 Agent harness search 均有既有先例。TCAIL V2 仍是条件性候选，不能宣称新颖性已成立。

特别说明：TCAIL 是统计建模/主动实验设计模块，本身不是完整 EC 算法。其能否成为毕业论文创新点，取决于是否对后续演化搜索提供独立、可测量的价值。当前不实现、不运行正式 Phase 0。

## 2026-11-02 TCAIL V2 第二轮复核：REQUEST CHANGES

新增 19_TCAIL_V2_SECOND_PASS_REVIEW_R1.md。V2 的基础公式大部分通过纸面检查，但发现高阶模型失配尚未进入主要边估计、reference-standardized contrast vector 未显式构造、连续 task context 的 BFDR 检验族未有限化、edge-risk acquisition 缺少完整 Monte Carlo 估计协议、预算分母需精确定义等问题。

已将相应 V2.1 澄清补入 17_TCAIL_FORMAL_SPECIFICATION_V2.md 第 12 节。当前状态为 V2.1 / PENDING INDEPENDENT REVIEW；没有实现、没有正式实验、没有 Gate-1 PASS。

## 仓库长期维护约定（2026-11-02）

后续每轮研究均须按 [REPOSITORY_MAINTENANCE_POLICY.md](REPOSITORY_MAINTENANCE_POLICY.md) 执行：开始前读取远端状态和接班记录；结束时更新研究记录、决策日志、项目状态与完整接班提示词；推送后核验远端 HEAD。不得只在聊天中汇报，也不得与其他独立研究仓库混用。

当前算法状态：TCAIL V2.1 仍待独立复审，CI-GOM 和第三项迁移冻结；算法 Gate 通过前不实现代码、不跑正式 Phase 0、不调用真实 LLM。当前交付优先级转为开题报告 V0.2 的书目审计、Word 核对和导师意见修订。

## 2026-11-02 第三轮：TCAIL V2.1 独立规格复审

新增文件：
- 20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md：对 V2.1 第 12 节及全文接口进行独立数学、统计和算法闭合性复审。

**结论：REQUEST CHANGES / IMPLEMENTATION BLOCKED。**

V2.1 已正确补充 reference-standardized contrast vector、有限 context anchors、M2/M3 敏感性思路、posterior predictive Monte Carlo acquisition 流程和预算分母。固定 concentration 的 Beta Fisher information、线性 contrast 的 row-space 判据和基本 BFDR 公式通过纸面检查。

但仍有以下阻塞：
1. 平均有符号交互可能因背景异质性而抵消，当前边定义未必等价于 EC linkage；
2. M2/M3 gate 未进入算法伪代码，M3 仅含三阶项，strong-heredity 与 three-way-only 场景可能冲突；
3. per-edge Bayes risk acquisition 与最终全局 BFDR 选择不一致；
4. task-block 配对、任务内相关和随机效应没有形成完整执行/统计模型；
5. 未知 Beta concentration \`κ\` 的 nuisance uncertainty 未进入 Fisher/acquisition；
6. M2/M3 × anchor 的合法设计矩阵、GLM practical information 和低共同支持 abstention 仍需定义；
7. BFDR 检验族在 task-family × pair 与 pair × anchor 两种写法之间尚未统一；
8. full-factorial 计数预算与 rollout-equivalent cost 的等价条件需要补充。

**当前状态：** TCAIL 继续 HOLD；尚未实现、未运行实验、未通过 Gate-1。下一轮只修订规格，不编码、不启动正式 Phase 0、不调用真实 LLM。CI-GOM、第三项迁移和大论文正文继续冻结。具体复审见 20 号报告。


## 2026-11-02 第四轮：GOMEA linkage 接口与先行工作审计

新增：
- \`21_GOMEA_LINKAGE_AND_NOISY_INTERACTION_RELATED_WORK_AUDIT_R1.md\`：区分 SLL、fitness-based linkage、DLED/cDLED 与 task-conditioned Agent interaction，并审查 2021–2026 直接先行工作。
- \`22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md\`：B1 的接口修订提案，尚未并入权威规格，等待独立复审。
- \`02_LITERATURE_REGISTER.md\` 新增 P125–P132。

**关键修正：** GOMEA linkage 既可能来自种群统计依赖（SLL-MI），也可能来自目标函数差分（fitness-based linkage）。因此不能简单声称统计交互与 linkage 无关；但当前 TCAIL 的平均有符号交互也不能直接等同于局部 FOS edge。

本轮建议：
1. 用实际优化目标尺度的条件四格有限差分定义局部 fitness interaction；
2. 全局 RMS interaction energy 仅作 task-conditioned summary，不直接作为当前个体 FOS；
3. 对当前 parent/task 计算 local posterior linkage evidence；
4. 将 local weighted VIG 通过固定 LT / conditional FOS builder 转换为 FOS，不把图和 FOS 混为一谈；
5. 将 FBL、DLED/cDLED、LMM、ALI/AIM、在线副产物式交互学习纳入强基线。

本轮没有实现、没有实验、没有 Gate-1 PASS。TCAIL 继续 HOLD / IMPLEMENTATION BLOCKED；22 号文件仅为提案，不替代 17 号权威规格，也不解除 CI-GOM 冻结。详细见 21、22 号报告。


## 9. 开题报告初稿 V0.1（2026-11-02）

已新增 \`23_OPENING_REPORT_DRAFT_V0_1.md\`，按河北工业大学硕士开题模板组织为完整初稿，包含选题来源、背景目的意义、国内外研究现状、研究目标与内容、关键科学问题、预期创新点、研究方案及可行性、研究基础、困难对策、研究进度和 50 篇参考文献。

当前题目工作稿：**《面向大语言模型智能体的交互感知演化优化方法研究》**。

初稿按“两个核心研究内容 + 一个条件性扩展”组织：
1. 任务条件化 Agent 组件交互结构估计；
2. 交互结构驱动的 Agent 约束最优混合演化；
3. 任务分布变化下交互结构迁移（条件性，不预先承诺为第三创新点）。

**重要边界：** TCAIL 规格审查仍有待解决项，B1 linkage 接口提案尚待独立复审；CI-GOM 尚未实现和验证；第三项暂缓。初稿统一使用“拟研究/预期创新”，没有把设计写成实验成果，也没有混入其他项目成果。

学校模板要求正文不少于 6000 字、参考文献不少于 30 篇、外文及近五年文献比例均不少于 30%。当前 Markdown 初稿正文约 22,100 个非空白字符、列出 44 篇外文文献；最终仍需按学校统计口径和 GB/T 7714 规范复核。


## 2026-11-03 开题报告 V0.2 与国内研究补充

本轮在保留 V0.1 的基础上新增：
- `24_REFERENCE_AUDIT_AND_DOMESTIC_RESEARCH_R1.md`
- `25_OPENING_REPORT_DRAFT_V0_2.md`

V0.2 将参考文献扩充至 61 条，补入国内 Agent 综述与应用研究，并加入 AHE、SkillFlow、ShapleyFlow、FusionFlow 等 2026 相关工作；修正 V0.1 参考文献统计和排列错误。具体书目核验范围及未完成项见 24 号报告。

**当前状态：** 开题报告 V0.2 已完成结构、国内研究现状和引用一致性修订；全部 61 条参考文献的最终 GB/T 7714 逐条审计尚未完成，导师反馈和封面个人信息待补。TCAIL V2.1 仍 HOLD / IMPLEMENTATION BLOCKED；CI-GOM 与第三项迁移继续冻结；本轮未实现算法、未运行 Phase 0、未调用真实 LLM。


### Word V0.2 生成状态（2026-11-03）

已基于原学校模板 Word 初稿生成 `河北工业大学硕士开题报告_初稿V0.2.docx`。Word 正文非空白字符约 22,950，参考文献编号连续为 [1]–[61]。该 Word 文件作为本轮会话交付提供下载，尚未作为二进制文件提交到 GitHub；Word 与 Markdown 的逐段一致性仍需下一轮复核。


**AHE 实验设计提醒（2026-11-03）：** AHE 原文主结果来自单次十轮 evolution campaign，且报告组件非加性交互与 regression blindness。后续 TCAIL/CI-GOM 评估必须采用多 seed、配对任务和同 rollout budget。


## 2026-11-03 导师要求加入 RSI：开题报告 V0.3

导师已明确要求开题报告加入 RSI。本课题主线调整为**面向大语言模型智能体递归自我改进的交互感知演化优化**，研究范围为冻结基础 LLM 的 Agent 系统级 RSI。

新增文件：
- `26_RSI_THREE_INNOVATION_RESEARCH_DESIGN_R1.md`
- `27_OPENING_REPORT_DRAFT_V0_3_RSI.md`
- `28_RSI_CONTINUAL_RESEARCH_AUDIT_R1.md`

三个候选创新点：
1. RSI 轨迹驱动的任务/父代条件化 Agent 组件交互结构学习；
2. 交互感知的 Agent 约束最优混合演化；
3. 跨轮次 RSI 的交互记忆、漂移检测、linkage block 条件化迁移和能力保持约束演化。

V0.3 报告列出 68 条参考文献，正文引用编号连续。新增 CPE、HarnessEvolve、EvolveNet、2026-11-02 continual harness study、2026-10-19 Are Self-Evolving Agents Continual Learners? 等直接相关工作。第三创新点不能只是 memory/archive/performance gate，必须与 ReasoningBank、GEPA、Meta-Harness 等进行强基线比较，并采用 task-free / observable-context 设定。

**当前状态：** V0.3 是开题研究方案初稿，Word 版和最终 GB/T 7714 审计尚未完成。TCAIL V2.1 仍 REQUEST CHANGES / IMPLEMENTATION BLOCKED；22 号接口提案待独立复审；CI-GOM 未实现；第三项尚无正式算法规格。本轮无 Phase 0、无真实 LLM API 调用、无 GPU 训练。


**IMCE-RSI 第三项进一步收敛（2026-11-03）：** 不做普通 memory/archive/performance gate，改为上下文键 + 局部交互签名键的双键 linkage-block 检索；相似查询对应冲突交互时检测 retrieval collision；高不确定性时有限探测或 abstain。在线算法不得读取 task-family labels 或 task-stream block boundaries。首个真实编码 Agent 平台明确为 SWE-bench Verified；SWT-Bench/FeatureBench 为连续任务流候选。细节见 28_RSI_CONTINUAL_RESEARCH_AUDIT_R1.md。

参数调节与实验 Gate 已整理到 `29_PARAMETER_TUNING_AND_EXPERIMENT_GATES_R1.md`，分别覆盖 TCAIL、CI-GOM、IMCE-RSI 的参数、同预算对照、A800 轻量迁移预测器条件和停止规则。该文件是设计，不代表实验已经启动。

## 2026-11-03 Word V0.3（RSI）初稿已生成

已生成学校模板风格的 Word 工作初稿：`河北工业大学硕士学位论文开题报告_V0.3_RSI_初稿.docx`。本轮结构检查通过：A4、宋体小四、1.5 倍行距、2 个原模板表格保留、68 条参考文献编号连续；正文已纳入 RSI 和三个候选创新点。详细构建记录见 `30_WORD_V0_3_BUILD_REPORT.md`。

**注意：** Word 仍是 V0.3 工作初稿，尚未完成与 Markdown 的逐段/逐表一致性审计，68 条文献元数据和 GB/T 7714 格式也尚未逐条审计。TCAIL V2.1 仍 REQUEST CHANGES；22 号接口提案待独立复审；CI-GOM 未实现；IMCE-RSI 尚无正式规格；无 Phase 0、真实 API 实验或 GPU 训练。


## 2026-11-03 TCAIL 独立复审 R2

已完成对 22 号 Linkage 接口 proposal 的独立复审：B1 仅部分接受，TCAIL overall 仍 HOLD / IMPLEMENTATION BLOCKED。主要未闭合点是局部 posterior edge probability 到连续 FOS weight 的映射、FOS builder、M2/M3、高阶、BFDR/acquisition、task-block 统计、practical identifiability 和 rollout-equivalent budget。

新增：
- `31_TCAIL_LINKAGE_INTERFACE_INDEPENDENT_REVIEW_R2.md`
- `32_TCAIL_V2_2_SPEC_REVISION_TASK_R1.md`

新增先行文献 P150–P153：FBL 2021、CGOMEA 2024、cDLED 2025、GA-side-effect interaction learning 2026。下一步只修订新的 V2.2 规格草稿，不编码、不运行 Phase 0、不调用真实 API、不训练模型。


## 2026-11-04：TCAIL V2.2 前置精读补充（Planner Addendum R1）

当前唯一算法任务仍为 TCAIL V2.2 完整规格修订；远端 main HEAD 在本轮开始时为 `903e62aa4b846ea20950b3be81c355688e0065e3`。31 号复审结论保持：B1 部分接受，TCAIL overall HOLD / IMPLEMENTATION BLOCKED。32 号 Executor 任务已存在，33/34 号草稿尚未交付。

本轮对 FBL、cDLED、CGOMEA、Tinós et al. 2026 进行了原文级机制补充核验。新增 35 号 Planner Addendum，增加 B9–B12：
- probability-scale nonlinear estimand 的 structural/practical identifiability；
- 四格 task-block acquisition design、CRN 可行性与唯一 episode-equivalent 成本；
- unsupported edge 与真实无边的区分，以及 missingness-aware FOS；
- posterior prior sensitivity 与 null calibration。

重要新颖性边界：
- FBL 已有 fitness-based contrast、scaled dependency strength、LT/MP FOS 与 incremental pair probing；
- cDLED 已有 individual-local DLED、conditional eVIG、局部结构识别和 donor mating restriction；
- CGOMEA 已有 conditional linkage 与 solution mating filter；
- Tinós et al. 2026 已从 GA 搜索副产物学习交互而无需额外 fitness evaluations。

因此不能把上述机制单独作为 TCAIL 创新。候选贡献只能在随机昂贵 Agent rollout、task-block 相关、合法配置支持、后验校准/abstention、主动预算决策与下游 GOM 搜索收益的联合场景中接受可证伪检验。详细内容见 [35_TCAIL_V2_2_PLANNER_ADDENDUM_R1.md](35_TCAIL_V2_2_PLANNER_ADDENDUM_R1.md)。

**执行边界不变：** 只修订规格；不编码、不调用 DeepSeek API、不运行 Phase 0、不训练 A800 模型；CI-GOM 与跨轮次迁移继续冻结。V2.2 草稿和 closure matrix 完成后必须交独立复审。


## 2026-11-04：TCAIL V2.2 完整规格草稿已交付

本轮开始时核验远端 `main` HEAD 为 `85414664a902724fc5610e606f05667ddc74b635`。已按 32 号任务和 35 号强制补充新增：

- [33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md)：完整 V2.2 数学、统计、观测、BFDR/acquisition、FOS、预算、强基线与伪代码规格；
- [34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md](34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md)：B1–B12 逐项变更、章节/公式/伪代码映射、OPEN 项和强基线公平性矩阵。

草稿已将 local objective-scale estimand、q/w 分工、M2/M3 与高阶门禁、四格 task-block GLMM、非线性可识别性、per-graph BFDR 一致风险、missingness-aware FOS、唯一新增 episode-equivalent、prior sensitivity/null calibration 纳入同一控制流。SLL-MI、FBL、FBL incremental、DLED、cDLED-P3M、CGOMEA、LMM、ALI/AIM、Tinós 2026 GAwLL2、random/oracle linkage 均已登记，并区分原论文复现与 paper-setting adaptation。

**当前状态：** V2.2 为 `DRAFT / PENDING INDEPENDENT REVIEW`；B1–B12 只能标为规格层 `PARTIAL`，所有校准、复现、实现和实验事项仍为 `OPEN`。编写过程中的符合性/质量复核不是正式独立数学 PASS。TCAIL 继续 `HOLD / IMPLEMENTATION BLOCKED`，CI-GOM 与 IMCE-RSI 继续冻结；规格完成不等于创新或 EC 收益成立。

本轮未编写算法实现、未启动 Phase 0、未调用 DeepSeek/真实 LLM API、未训练模型。下一步唯一任务是由新的独立审查会话复核 33/34 号并给出明确处置。


## 2026-11-04 独立复审 R1

新增 36_TCAIL_V2_2_INDEPENDENT_REVIEW_R1.md。审查结论：REQUEST CHANGES；TCAIL 继续 HOLD / IMPLEMENTATION BLOCKED。下一步只做规格修订，不实现、不实验、不调用真实 API、不训练模型。CI-GOM 与 IMCE-RSI 继续冻结。


本轮详细交接补充见：D039_TCAIL_V2_2_INDEPENDENT_REVIEW_DECISION.md、SESSION_HANDOFF_V2_2_CORRECTIVE_R1.md。注意：本轮对 05_DECISION_LOG.md 与 SESSION_HANDOFF.md 的原文件追加未完成；请以新增 D039 决策记录和 corrective handoff 为准，下一维护轮合并回主日志/主交接文件。


## 2026-11-04：TCAIL V2.2 Corrective Revision R1 草稿

本轮开始时远端 `main` HEAD 为 `ea5c8f7500848baf7a4f3a345f362d0573e59a2b`，已包含 36 号独立复审的 REQUEST CHANGES。现新增：

- [37_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R1.md](37_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R1.md)：完整 V2.2 Revision R1 规格；
- [38_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R1.md](38_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R1.md)：R1–R7 数学定义、伪代码、边界条件、B1–B12 承接和 OPEN 矩阵。

本轮修订采用鲁棒 posterior 风险、MCSE 不确定停止、跨轮 retry 持久账本、边际 GLMM Fisher 完整秩门、FOS support/positive/unknown 分离、worst-expected fantasy 主聚合，以及 acquisition cycle 内冻结的活动图集合/权重。所有校准、形式认证、复现、实现和实验事项继续 OPEN。

33、34、36 号历史文件未覆盖。此前单独的 D-039 决策已合并回主 `05_DECISION_LOG.md`，主 `SESSION_HANDOFF.md` 已更新。当前状态为 `PENDING R2 INDEPENDENT REVIEW / HOLD / IMPLEMENTATION BLOCKED`；规格完整不等于算法验证、创新或 EC 收益成立。

本轮未实现算法，未启动 Phase 0，未调用 DeepSeek/真实 LLM API，未训练模型，未启动 CI-GOM 或 IMCE-RSI。下一步只能由新的独立审查会话进行 R2 复审。


## 2026-11-04：TCAIL V2.2 Revision R1 独立复审 R2 — REQUEST CHANGES

新增 [39_TCAIL_V2_2_INDEPENDENT_REVIEW_R2.md](39_TCAIL_V2_2_INDEPENDENT_REVIEW_R2.md)。审查基线为 4f15ac303936817cc2bf122e649fff2331c9b1dc，复核 37/38 号及 33/34/36 号历史约束。

R1 的鲁棒 posterior loss、worst-expected fantasy 聚合、边际 Fisher 完整秩门和 acquisition cycle 冻结有实质进步；但 R2 不通过，仍有四类关键缺口：
- acquisition A_L/A_U 未计入当前基准风险 R(D) 自身的 posterior MC 误差；模型/候选 alpha allocation 和 nested MCSE 不完整；
- base-key ledger 的 REUSABLE 状态遇到 cache miss 时可能计划 continuation、执行时却 BREAK 并返回 OK；crash-consistent reservation 状态未定义；
- FOS 将 Q_g 中已通过基础门的 NOT_SELECTED 当作 unknown，rho_support 因而不是数据支持覆盖率；
- Fisher 连续参数向量、paired CRN 映射和 generation/cycle 索引仍需澄清。

**决定：REQUEST CHANGES / HOLD / IMPLEMENTATION BLOCKED。** B3、B8、B10、B11 需修订；其余 B 项保持 PARTIAL。下一步只做 corrective specification revision R2，不编码、不启动 Phase 0、不调用真实 LLM API、不训练模型；CI-GOM 与 IMCE-RSI 继续冻结。


## 2026-11-04 TCAIL：Oracle Linkage Gate 首轮合成实验

新增 experiments/tcail_oracle_gate_pilot/，包含可复现实验脚本、依赖和结果报告。20 个配对种子、40 维 concatenated deceptive trap、最大 5,000 objective evaluations：Oracle FOS 平均 39.55/40，population-MI LT 平均 38.55/40；13 胜、6 平、1 负，paired Wilcoxon one-sided p=0.000919，bootstrap 95% CI [0.55,1.45]。Oracle 全局最优命中 13/20，Learned LT 为 2/20。12-seed additive control 中四种方法均 12/12 达到最优。

**结论边界：** 这只支持 Oracle local linkage 对简化 GOM 原型在该 deceptive-trap 场景有上界价值；不是 TCAIL estimator、FBL/cDLED 对比、主动采样或真实 Agent 的验证。下一步不继续扩写理论规格，直接做 fixed full-factorial 的 estimator-only synthetic gate，比较局部 posterior q/w 与 FBL/scaled-FBLT 风格对照；active acquisition 和 retry 暂不纳入该 gate。TCAIL 整体仍 HOLD，未授权真实 API/A800/CI-GOM。


## 2026-11-04 TCAIL：Estimator-only q/w 代理诊断

新增 experiments/tcail_estimator_gate_pilot/。在 20 个合成种子中，前 10 个估计 Normal empirical-Bayes prior scale，后 10 个留出测试。每 seed 200 pairs × 2 parent contexts，包含正/负/弱/null、跨 parent sign flip、unsupported 和 8/128 task-block 支持。

Held-out AUPRC：EB posterior q 0.802，EB posterior w 0.797，local standardized contrast 0.785，Student-t q 0.767，local raw contrast 0.619，context-pooled contrast 0.598。q 的 Brier 0.153；q≥0.8 时 precision 91.1%、recall 38.1%、FPR 1.57%。10 个 held-out seed 的 q AUPRC 均高于 standardized contrast，平均差 +0.0169，seed-level bootstrap 95% CI [0.0120,0.0221]。

**边界：** 这是 paired task-block normal-normal empirical-Bayes q/w proxy，不是完整 M2/M3 GLMM；对照不是 paper-exact FBL/scaled-FBLT；生成器也不是 logistic GLMM。8-block low-support 子集 AUPRC 仅 0.353。该结果是小幅正向信号，不是 TCAIL 已验证。下一步必须做 paper-faithful FBL/scaled-FBLT/cDLED 对照、校准与 FOS recovery；不转入 active acquisition，除非估计器 gate 先通过。


## 2026-11-04 TCAIL：加入 scaled-FBL task-block 二元适配对照

新增 experiments/tcail_estimator_gate_pilot/run_fbl_comparison.py 与 FBL_COMPARISON_RESULTS.md。该实验在同一四格 task-block Bernoulli 数据上比较 EB posterior q/w 与 scaled-FBL 的二元任务块适配；训练 seeds 0–9 仅用于 EB prior scale 与两种 null threshold 校准，seeds 10–19 为 held-out。

Held-out AUPRC：EB q=0.802，EB w=0.797，local z-score=0.784，scaled-FBL adaptation=0.414，raw contrast=0.619，context-pooled=0.598。EB q 与 scaled-FBL adaptation 的 per-seed AUPRC 差为 +0.3845，10/10 held-out seeds 胜，seed-level bootstrap 95% CI [0.3704,0.3990]。在训练 null 95th-percentile 匹配阈值下，EB q precision/recall/FPR=81.5%/58.7%/5.62%；scaled-FBL adaptation=69.7%/31.5%/5.81%。

**边界：** scaled-FBL 是 binary task-block adaptation，不是原论文复现；EB q/w 是 Normal-normal proxy，不是完整 TCAIL M2/M3 GLMM；尚未比较 cDLED-P3M、CGOMEA、GAwLL2，也未验证 FOS/GOM 下游收益。低支持 8-block 子集 AUPRC=0.353。结果仅为正向合成信号。


## 2026-11-04：研究优先级调整——直接验证 TCAIL → FOS → GOM（优先于继续扩写规格）

用户明确要求尽快证明演化计算收益，不再做无关规格扩展。新增 [42_TCAIL_ESTIMATOR_TO_GOM_CONFIRMATORY_GATE_R1.md](42_TCAIL_ESTIMATOR_TO_GOM_CONFIRMATORY_GATE_R1.md)，将下一阶段收敛为固定 full-factorial 的 estimator-to-GOM 证据链。

现有 Oracle GOM、Normal-Normal EB q/w 和 scaled-FBL binary adaptation 仅为 exploratory pilots。它们没有证明完整 TCAIL、paper-faithful baseline superiority 或 GOM 下游收益。尤其 EB q/w 不是 M2/M3 Bernoulli GLMM，scaled-FBL 是 adaptation，8-block low-support AUPRC=0.353 是明确失败边界。

**下一步不再先修完整 active-acquisition/retry 规格。** 先 clean rerun 与代码审计，再实现/校准 Bernoulli task-block estimator，公平比较 FBL/scaled-FBLT、cDLED-P3M、CGOMEA linkage；只有 estimator gate 通过才跑下游 GOM。下游总预算必须包含 discovery episodes 和 search episodes。所有方法共用 held-out task blocks、seed 和 episode-equivalent 预算。

TCAIL 仍未证明；这是一项有限的合成研究原型证据任务，不授权真实 Agent API、A800 训练、CI-GOM 或 IMCE-RSI。具体 generator、split、metrics、GO/NO-GO 和停止规则见 42 号文件。


## 2026-11-05：R1-A 三个现有 pilot 已 clean rerun 并完成修正版审计

新增 `experiments/tcail_confirmatory_r1/`。原始代码与修正版输出分离保存，含原始 CSV/JSON、运行日志、独立重算、环境锁和 R1A_AUDIT_RESULTS.md。

原报告数值均可从原始 CSV 独立重算。FBL 四格顺序和 gate 恒等式在 438,400 个 block 上误差为 0；但现有 scaled score 是绝对值比率适配，不是论文 signed Eq.(7)，训练-null epsilon=0.25 也不是原论文机器精度阈值。无 gate/零 epsilon 的绝对值适配 AUPRC 为 0.379；signed Eq.(7) 有 2,811/3,800 个领域违规输出，不能作完整公平基线。

Oracle 修正版统一跨方法 mixing seed，并验证初始种群哈希一致。Oracle−Learned LT 的配对均值从原代码 +1.00 变为修正版 +1.30，95% bootstrap CI [0.60,2.00]；这只保留 Oracle 上界信号，不证明 TCAIL。

**当时状态（已被下文取代）：** 真正 Bernoulli task/block M2/M3、Estimator Gate 和 TCAIL-FOS GOM Gate 尚未完成；不得将 R1-A 写成 GO。


## 2026-11-05：R1 Estimator Gate 完成并失败；GOM Gate NOT RUN

新增真正的 Bernoulli task/block 层级 M2/M3 估计器、五情景合成生成器、9 类 linkage 基线、train/validation/held-out 隔离流程和完整原始数据，结果见 `experiments/tcail_confirmatory_r1/R1_ESTIMATOR_GATE_RESULTS.md`。

Held-out seeds 3000–3039（40 个，运行前未使用）。验证集选出的最强非 Oracle 基线为 standardized contrast（validation macro-AUPRC 0.7713）。TCAIL q 的 held-out macro-AUPRC 为 0.6736，配对差 **−0.0996**，95% CI **[−0.1139, −0.0858]**；关键情景 sparse pairwise（−0.0393）与 parent sign-flip（−0.3541）均显著更差，只有 low-support/drift 显著更好（+0.0462）。

**决定：ESTIMATOR_GATE_FAIL。** 按 42 号协议停止 TCAIL estimator 优越性主张，Downstream GOM Gate 未运行；本轮没有产生任何“TCAIL 改善演化搜索”的证据。TCAIL null false-link 为 0.0375（合格），但 calibration slope=0.130、FOS F1=0.373（standardized 0.729），且 128-block 条件弃权率高达 52.9%。解盲后的 q_M3-only 仍显著低于 standardized（−0.0322，CI [−0.0496,−0.0168]），说明失败不只是 conservative min 规则。

严格边界不变：未调用真实 LLM API，未训练 A800，未启动 CI-GOM、IMCE-RSI 或完整 active acquisition。cDLED-P3M 与 CGOMEA 仍是 static adaptation；SLL-MI、FBL incremental、DLED、LMM、ALI/AIM、GAwLL2 未运行。


## 2026-11-05：TCAIL NO-GO 后重新评估硕士论文创新点

新增 [44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md](44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md)。

TCAIL R1 的确认性 Estimator Gate 已失败（TCAIL q macro-AUPRC 0.6736 vs standardized 0.7732，配对差 -0.0996，95% CI [-0.1139,-0.0858]；FOS F1 0.373 vs 0.729），Downstream GOM 未运行。TCAIL 不再作为核心创新点，旧版依赖 TCAIL linkage 的 CI-GOM 继续冻结。

新主线候选：**面向状态化工具型 LLM Agent 的故障恢复策略演化与递归自我改进**。两个核心候选为：
1. 状态感知、契约约束的恢复策略演化；
2. 故障场景—恢复策略双种群协同演化。
第三项跨任务恢复策略迁移暂作储备。

该方向目前仅为 HOLD，不代表已通过新颖性审查。下一步先做相关工作机制级差异矩阵和 Pilot A（oracle/手工恢复策略上界）；只有确认恢复策略存在可进化空间后，才进入标准 GA/GP 与约束演化方法比较。不要立即扩建完整系统或开跑大规模实验。

2026 年相关工作已覆盖通用 prompt/workflow 演化、blame-aware tool-policy mutation、延迟奖励 self-evolution、failure retrieval/recovery、tool transaction runtime 和 fault benchmarks。新贡献必须落在状态化副作用工具环境中可执行恢复控制器的约束演化，以及有验证的故障场景—策略协同演化，不能声称普通进化 prompt、模块定向变异、Pareto 选择或事务保护本身是新颖点。


## 2026-11-05：A800 训练候选与 Pilot A 首轮

新增：
- 46_RELATED_WORK_MECHANISM_AUDIT_ARWM.md：TRACE、SENTINEL、HarnessMDP、CoMAP、EvoTool 的机制级初审。
- experiments/pilot_a_recovery/：确定性模拟器、回归测试、探索性结果和 JSON 汇总。

首轮 Pilot A：7 类故障 × 10 个参数种子，6 种策略，每策略 70 episodes。三个 timeout 子类型向策略暴露同一 TIMEOUT 观测，隐藏子类型仅 oracle 可见。state-aware 手工策略 task success 0.8571、safe resolution 1.0、invariant violation 0；与 oracle 的成功/安全指标持平，但平均动作数 3.0714 vs oracle 1.5。盲目重试 success 0.1429、invariant violation 0.4286。

**Gate：CONDITIONAL HOLD。** 该小型确定性场景中，手工状态规则已达到 oracle 的成功/安全表现，尚未证明足够的成功率优化空间；仅剩动作效率差距，且 oracle 使用隐藏信息。因此暂不启动 A800 训练、ARWM 或正式 EC 搜索。下一步只允许 bounded Pilot A-2：多工具幂等契约、同观测下复合/潜在故障、变化的读延迟与补偿可用性、按 task/fault family 隔离的测试。若简单规则仍匹配 oracle，则停止该方向。

CoMAP (EMNLP 2026) 已是直接相关强工作：文本世界模型预测动作后的文本状态，并与 Agent 策略闭环自蒸馏共演化；HarnessMDP 学习冻结 LLM 的外部 harness controller；TRACE/SENTINEL 已覆盖失败驱动的 Agent 训练；EvoTool 已覆盖 blame-aware tool policy evolution。新贡献不能是泛化的“world model + EA”或“失败轨迹训练”。A800 训练候选必须证明配对反事实动作后果数据、多任务副作用风险校准与不确定性门控确实改善固定真实 rollout 预算下的约束演化搜索。

- `45_A800_TRAINED_RECOVERY_MODEL_CANDIDATE.md`：ARWM 训练目标、与 EC 的接口、强基线和 M1–M3 停止门。


### Pilot A 审计修正（2026-11-05）
独立复算发现首轮报告的 `unresolved` 列存在转录错误，已更正 `PILOT_A_EXPLORATORY_RESULTS.md` 与 `summary.json`：verify-then-retry 0.5714、wait-verify-retry 0.4429、conservative escalation 0.0857、state-aware 0、oracle 0。task success、safe resolution、duplicate side effect、invariant violation 和动作数不变。7 项状态转移/覆盖断言在独立复现中通过；GitHub Actions 尚无运行记录，CI 未验证。Pilot A 仍是探索性模拟器结果。


## Pilot A-2 首轮（2026-11-05）
已实现四类双工具任务、九类故障（含 timeout+stale-read、partial-commit+rate-limit）、六种策略和 30 个参数种子，共 1,080 episodes/策略、6,480 policy episodes。12/12 回归测试通过，GitHub Actions run 42030194929 和后续 run 42030392313 均成功；最新 run 42030392313 完成 regression tests、Pilot A/A-2 和 pilot-a2-summary artifact 上传。contract-aware 策略 success 0.7222、safe 1.0、invariant violation 0；oracle diagnostic success 0.7778、safe 1.0。与 oracle 有 5.56pp 差距，初步显示仍有优化空间，但不是统计显著性或 EC 收益证据。限制：每个任务两工具目前共享同一故障族，seed 只改变延迟/限流参数，无真正 held-out task/fault families。结论：CONDITIONAL GO 到 Pilot A-3；暂不训练 ARWM/A800。


## 2026-11-05：Pilot A-3 已实现，等待 CI 与结果审计

TCAIL Estimator Gate 已失败，旧 TCAIL/CI-GOM 主张冻结；当前研究主线为状态化工具型 Agent 的故障恢复策略演化与 RSI。Pilot A-2 的 CONDITIONAL GO 只授权进入 A-3 simulator refinement，不授权 A800 训练或算法创新结论。

新增：
- `47_PILOT_A3_PROTOCOL.md`：冻结的 A-3 任务/故障分层、预算、对照策略和 Pilot B 门禁；
- `experiments/pilot_a_recovery/pilot_a3.py`：独立 per-tool fault vector、三步 saga、partial commit、delayed visibility、compensation failure、public policy facade、held-out slices 和 cluster bootstrap；
- `experiments/pilot_a_recovery/test_pilot_a3.py`：15 项回归测试；
- `experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md`：实现范围和验证边界；
- `.github/workflows/pilot-a-recovery.yml`：CI 增加 A-3 运行和 episode-level JSON/CSV artifact。

冻结预算：每种策略 954 episodes（144 train、120 validation、690 held-out），7 种策略共 6,678 policy episodes；所有策略共享 scenario IDs、seeds 和 fault realizations。Held-out 拆成 task-only、fault-only、joint shift 三类。

**当前真实状态：** A-3 协议、模拟器和测试已写入分支；尚未核验本轮 GitHub Actions 运行结果，尚无 A-3 实验结果，不能声称测试通过或策略有效。下一步先检查 CI 与 artifacts，独立重算每个 episode 和分层指标，再按 47 号协议决定是否进入 Pilot B。A800/ARWM、真实 LLM API 和双种群协同演化继续 HOLD。


## 长期会话接管（强制维护）

唯一权威接管提示词：[NEXT_SESSION_PROMPT.md](NEXT_SESSION_PROMPT.md)。每次实质性研究、代码、实验、审计或决策变化后，必须同一轮同步更新该文件、`SESSION_HANDOFF.md`、`05_DECISION_LOG.md` 和 README；会话结束前重新读取核对，并在每次用户汇报中附接管提示词链接。不得只在聊天中维护接班信息。

当前唯一下一任务：核验 A-3 最新 GitHub Actions run，下载并独立复算 JSON/CSV，再按 47 号协议决定是否进入 Pilot B。A-3 CI/结果尚未核验；Pilot B 和 A800/ARWM 继续 HOLD。


## 2026-11-06：硕士大论文当前定位（方向已收敛，创新尚未验证）

**当前工作题目（未冻结）：《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》**

旧题目《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》属于 TCAIL/CI-GOM 旧路线；TCAIL Estimator Gate 已 FAIL / NO-GO，不再作为当前论文主线。

当前论文研究问题：利用演化计算搜索可执行、契约约束的 Agent 恢复控制器，使状态化工具调用在未见任务/故障组合下提高恢复能力并满足硬安全不变量；进一步验证反馈驱动的多轮策略更新是否构成可测量的 RSI。

创新点候选：
1. 核心候选一：契约约束的恢复策略演化（有限状态控制器编码、契约感知变异/修复、可行性优先选择）。尚无 EC 优于强基线的证据。
2. 核心候选二：故障场景—恢复策略双种群协同演化。暂缓，必须在候选一通过后再启动。
3. 储备候选三：跨任务恢复策略迁移与能力保持。冻结，不为凑数量保留。
ARWM/A800 是条件性辅助模型路线，不是已确认的独立创新点，仍 HOLD。

**论文成熟度：** 研究方向已收敛，但最终题目和 2–3 个创新点未冻结；尚处于开题前研究验证阶段。TCAIL 已失败；Pilot A/A-2 仅为探索性模拟器证据；Pilot A-3 已实现但 CI 和原始数据尚未核验；Pilot B 未启动；RSI 多轮收益未验证。旧 V0.1–V0.3 开题稿按 TCAIL/CI-GOM 路线撰写，不能直接作为当前方向的正式开题稿，需基于新证据重构。

下一步唯一任务：核验 Pilot A-3 最新 Actions，独立复算 JSON/CSV，并按 47 号协议判断是否进入 Pilot B。


## 2026-11-06：第一项创新相关工作审计

新增 [49_FIRST_INNOVATION_RELATED_WORK_AUDIT.md](49_FIRST_INNOVATION_RELATED_WORK_AUDIT.md)。

初步检索发现 UndoBench、EvoUndo、EvoTool、LIMBO、Cordon、Atomix、SagaLLM、Verified Tool Calls、Repair Economics 等近邻工作；安全控制器合成方面还有 CDGP、GP controller synthesis、FSM-MOEA、SMC-ES。

**结论：** 第一项候选仍可继续研究，但“契约约束恢复策略演化”尚未通过新颖性审查。通用工具恢复、verify-before-retry、Saga、通用 prompt evolution、FSM + EA 均不能单独作为创新。待验证的差异假设是契约语义保持、反例驱动的可执行恢复 FSM 演化及跨任务/故障泛化。

A-3 仍待 CI 和 JSON/CSV 独立审计；Pilot B 未授权。必须先完成近邻论文全文机制比较，再结合 A-3 结果决定是否进入 Pilot B。


## 2026-11-06：第一项创新的数据集选择方案（尚未冻结）

新增 [50_DATASET_SELECTION_AND_VALIDATION_PLAN.md](50_DATASET_SELECTION_AND_VALIDATION_PLAN.md)。

推荐实验组合：
- Pilot A-3 自有确定性模拟器 + ToolMisuseBench v0.2 train：演化策略搜索和开发；
- A-3 validation + ToolMisuseBench dev：调参与候选选择；
- ToolMisuseBench public test + UndoBench TEST：算法锁定后的外部恢复验证；
- ThinkingBox-Bench v1.0 或 ToolSandbox：正常状态化任务回归；ThinkingBox 明确 evaluation-only，不得用于演化搜索或调参。

ToolMisuseBench v0.2 large 标注 6,000 train / 900 dev / 1,200 public-test records，覆盖 CRUD、retrieval、files、scheduling 和多种故障；数据卡包含 initial_state、tool_schemas、fault_plan、success_criteria 等字段，MIT license。但其 public test 统计口径（1,200 records，其中 600 output-grounded tasks）需要通过冻结 manifest 和 evaluator 核实。

**重要：** 这是可执行环境中的策略演化，不是把 JSONL 当监督训练集。fitness 必须来自实际 rollout。数据方案仍未冻结，Pilot B 仍 HOLD；先完成 A-3 CI/原始数据复算和 benchmark compatibility/leakage audit。


## 2026-11-06：第一项创新的数据集方案（建议，尚未冻结）

新增 [50_DATASET_SELECTION_AND_VALIDATION_PLAN.md](50_DATASET_SELECTION_AND_VALIDATION_PLAN.md)。

建议组合：Pilot A-3 + ToolMisuseBench train（搜索开发）；A-3 validation + ToolMisuseBench dev（调参）；ToolMisuseBench public test + UndoBench TEST（冻结后外部恢复验证）；ThinkingBox-Bench 或 ToolSandbox（正常任务回归）。ThinkingBox 官方规定 evaluation-only，不能用于演化搜索或调参。

ToolMisuseBench v0.2 large 有 6,000 train、900 dev、1,200 public-test records，覆盖 CRUD/retrieval/files/scheduling 和多类工具故障。数据卡写明 test 中 600 条 output-grounded tasks，最终统计分母须按 manifest/evaluator 审计。

演化 fitness 必须来自可执行环境 rollout，而非对静态 JSONL 做监督学习。A-3 CI/数据复算未完成前，Pilot B 仍 HOLD。


## 当前下一阶段：数据门禁与 Pilot A-3 独立复核

- 数据选择与官方信息复核：见 [50_DATASET_SELECTION_AND_VALIDATION_PLAN.md](50_DATASET_SELECTION_AND_VALIDATION_PLAN.md)。
- 可执行任务计划：见 [51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md](51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md)。
- ToolMisuseBench：6,000 train / 900 dev / 1,200 public-test records；其中 HF 数据卡注明 600 条 output-grounded tasks，评分分母待官方 evaluator 审计；Parser+Repair 是必须复现/适配的参考基线。
- UndoBench：v1.0.1，36 workflows，14/10/12 split；TEST 锁箱。
- ThinkingBox-Bench：507 tasks，evaluation-only，只能最终 clean regression。
- Pilot A-3 独立复核已于 2026-11-06 完成（见下节）；Gate = HOLD。Pilot B、A800/ARWM、真实 LLM API 继续 HOLD。


## 2026-11-06：Phase A 完成 — Pilot A-3 独立复核与预注册 Gate 判定 HOLD

完整报告：[PILOT_A3_INDEPENDENT_REAUDIT.md](PILOT_A3_INDEPENDENT_REAUDIT.md)；决策记录：05_DECISION_LOG.md D-057。

- **CI 修复：** 加入 A-3 步骤后的全部 run 曾在 `recover_tool` 崩溃（策略经 `PublicToolView` 误读运行时 `tick`），artifact 从未产生。修复 commit `f5e6b46`，新增第 16 项崩溃回归测试（A-3 测试 15→16，套件共 28 项）。
- **真实运行：** run 42241224898（head `f5e6b46`）28 项测试全部通过，A1/A2/A3 模拟器全部成功，artifact 上传成功。哈希：ZIP `1119d14b…`、JSON `3a60ae83…`、CSV `2c7d7dad…`（6,678 行）；原始文件存 `experiments/pilot_a_recovery/ci_artifact/`。
- **独立重算：** 结构/配对/split 因子化/语义全部通过；JSON 与 CSV 零偏差；本地重跑逐字节一致。
- **预注册 Gate（47 号 §6 原文）：HOLD。** 安全条件满足（held-out 三 slice 零违规），但 oracle−saga 成功率差 0.0（要求 ≥0.05）、cluster bootstrap CI [0.0, 0.0]（要求下界 >0）；gap≤0.02 但动作成本差 +34.6%>10%，不构成 NO-GO。
- **失败边界：** `partial_comp_failure` 与 `delay_rate_permission` 组合族对全部策略（含特权 oracle）结构性不可行（0% 成功，占 held-out 52.2%）；任务族漂移 slice 97.5% 成功、零违规；可优化维度只剩动作成本。
- **边界：** 不得用本批 held-out 调参再宣称通过。GO：ToolMisuseBench/UndoBench 只读审计（Phase B）+ A-3b 新预注册设计。HOLD：Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 优化。


## 2026-11-06：Phase B 数据集审计完成 + A-3b 设计草案（D-058）

审计与设计文档：[52_TOOLMISUSEBENCH_AUDIT.md](52_TOOLMISUSEBENCH_AUDIT.md)、[53_UNDOBENCH_AUDIT.md](53_UNDOBENCH_AUDIT.md)、[54_BENCHMARK_COMPATIBILITY_MATRIX.md](54_BENCHMARK_COMPATIBILITY_MATRIX.md)、[SPLIT_LEAKAGE_AUDIT.md](SPLIT_LEAKAGE_AUDIT.md)、[LICENSE_AND_PROVENANCE.md](LICENSE_AND_PROVENANCE.md)、[DATASET_LOCK_MANIFEST.json](DATASET_LOCK_MANIFEST.json)、[55_PILOT_A3B_RESEARCH_DESIGN.md](55_PILOT_A3B_RESEARCH_DESIGN.md)。

- **ToolMisuseBench v0.2**（rev `98eb2871`，MIT）：哈希与官方 manifest 吻合；评分口径解密——0.767=全 1,200 分母、0.736=993 故障任务分母、600 output-grounded 是子集非分母；语义缺口确认（无 lost-ACK/重复副作用/补偿/saga，故障单次触发）；Parser+Repair 逆向+DEV 复现（0.7622/0.7363），必须列为 Pilot B 基线。
- **UndoBench v1.0.1**（rev `4be11518`，CC-BY-4.0/Apache-2.0）：36 条全画像（33/36 lost-ACK、幂等全 false、IRREVERSIBLE 8）；doctor/smoke/DEV 配对跑通；内置 TEST 锁；定位为外部泛化验证。
- **ThinkingBox 不可达**（HF 401、GitHub 404），继续按 evaluation-only 保守处理。
- **泄漏审计**：ToolMisuseBench 模板层泄漏、UndoBench 领域层重叠——泛化主张须限定；A-3 因子化 OOD 保持唯一干净来源。
- **A-3 gap=0 根因**：可行单元 saga 已达 oracle 水平 + 52.2% 死区稀释 + Gate 无视效率差异；修正=可恢复性分层（R1–R4）+ 成本目标 + 重划 held-out，不删困难场景。
- **A-3b 设计草案（55 号）已产出，未批准、未运行。** 下一步：独立审查 → 预注册冻结 → 实现分类器/场景生成器/adapter。HOLD 不变：A-3b 运行、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 执行、锁箱调参。


## 2026-11-07：Pilot A-3b 设计独立审查

新增 [56_PILOT_A3B_INDEPENDENT_REVIEW.md](56_PILOT_A3B_INDEPENDENT_REVIEW.md)。

结论：Phase B 数据集审计 GO / 完成；55 号 A-3b 研究设计草案 **REQUEST CHANGES**，尚不能冻结预注册。主要阻断点包括 R4 零残留逻辑矛盾、R2 安全放弃与任务完成混淆、公开观测可达性未形式化、有限样本不能证明 P(violation)=0、R4 不可避免残留/必要升级被成本惩罚、类别配额与 cluster-level power 未冻结，以及算法初始化/骨干混杂风险。

下一步：建立 55-R1 逐条修订，完成分类器可达性定义、分层指标、样本功效和公平预算审计。A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 继续 HOLD。


## 2026-11-07：55-R1 修订 + 可恢复性判定器 + 机制诊断首轮（D-060）

- **[55_PILOT_A3B_RESEARCH_DESIGN_R1.md](55_PILOT_A3B_RESEARCH_DESIGN_R1.md)**：56 号 B1–B6/M1–M5 全部处置（R1–R4 互斥+UNKNOWN、观测策略鲁棒可达性、分层安全主张、成本三分、配额与功效方案、公平归因设计、primary contrast）。
- **判定器落地并验证**：`experiments/pilot_a3b/reachability.py`（AND-OR 信念态观测策略可达性）；12 类 ground-truth 环境 27 项测试全绿；混淆矩阵 12/12 纯对角，UNKNOWN 2/12 设计内，资源截断正确兜底。
- **机制诊断实验（非确认性）**：216 个新生成场景、8 方法 × 3 seeds、每方法每 seed 108,864 真实 episodes、吞吐 ~97k eps/s。**A（契约语义保持算子）把非法候选率从 100% 降到 0%、全 seed 零违规**；CondRec：hand 1.000 > A 0.968 > AB 0.938 > ga 0.911 > nsga3 0.902 > B 0.872 > nsga2 0.838 > random 0.575。
- **统计诚实结论**：primary AB vs NSGA-II Δ=+0.049 但 CI95 [−0.017,+0.122]、p=0.27（功效不足，不显著）；AB 未超过强手工基线；A+B 未超过 A 单独。第一项创新**方向可行、尚未证实**。
- 下一步：功效核算定正式实验规模、B/A 机制迭代、49 系统检索、预注册交用户批准。正式 A-3b 继续 HOLD。


## 2026-11-07：D-060 首轮机制诊断独立复核（D-061）

新增 [57_PILOT_A3B_DIAGNOSTIC_INDEPENDENT_REAUDIT.md](57_PILOT_A3B_DIAGNOSTIC_INDEPENDENT_REAUDIT.md)。

独立复核发现 D-060 的诊断数据可解析、216 场景配对完整，但算法评价存在阻断问题：当前控制器并非真正有状态 FSM；任意基因组 COMP 规则会触发运行器全局 Saga rollback；所有失败自动标记 escalated；R4 scorer 忽略可避免残留；必要升级仍计入 action cost；A-3 标签来自启发式而非逐场景 reachability checker；B 反例池被每次 update 清空且权重函数未调用；统计脚本平均 per-seed CI/p；NSGA-II/III/GA 不是完整 canonical baseline；55-R1 的 3:1/3:2 配额冲突。

原始 JSON 实际类别为 R1=96/R2=50/R3=35/R4=35（D-060 文档中的 36/34 更正）；实际 A/seed23=108,648 episodes，hand 每 seed 216，其他搜索 runs 多数 108,864。不能声称所有方法/seed 实际 rollout 完全相同。

结论：D-060 只能作为诊断线索，A 的内部规则修复有效性尚不等于独立语义安全提升；B 未按设计实现；A+B 未建立对标准 EA 的提升证据。下一阶段先修 controller/evaluator/labels/B/statistics/baselines 和配额，再用新诊断集重跑；暂不做功效分析或扩大 rollout。正式 A-3b 继续 HOLD。


## 2026-11-07：D-061 — 57 号修复落地 + 第二轮诊断实验

报告：[58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md](58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md)。

- **F1–F8/S1–S3 全部修复**（真状态化 FSM、显式补偿、升级事件分离、R4 损害记账、独立 contract validator、B 重设计、三值可达性、pooled 统计、标准基线、train/val 分离）；47/47 测试绿。
- **机制 A 显著成立**：A vs NSGA-II Δ=+0.239（Holm p=0.0014, d=1.56）；独立 validator 非法率 1.00→0.00。
- **B 叠加显著有害**（AB vs A −0.113, p=0.0014）；AB vs NSGA-II primary +0.126（p=0.0002）显著但低于 A 单独；**未超过强手工基线**（−0.514）。
- **Q6 泛化成立**：验证集 AB vs NSGA-II +0.148（p=0.002, d=0.97）。
- 判定：第一项创新**部分成立**（A 成立、B 需重设计）。下一步：B 反例映射重设计 + WAIT-SLA 行为层契约修复。正式 A-3b 继续 HOLD。


## 2026-11-08：D-062 — WAIT-SLA 行为安全与反例驱动演化（已完成）

原始计划 [59_D062_WAIT_SLA_AND_COUNTEREXAMPLE_REDESIGN_PLAN.md](59_D062_WAIT_SLA_AND_COUNTEREXAMPLE_REDESIGN_PLAN.md) 已执行，交付见 [59 号独立复核](59_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md)、[60 号机制设计](60_WAIT_SLA_CONTRACT_BNEW_AND_SAFETY_GATE_DESIGN.md)、[61 号第三轮诊断结果](61_D062_DIAGNOSTIC_RESULTS.md)。下方的 READY_FOR_EXECUTION 内容属于当时的历史计划状态，现已由执行结果取代。

## 2026-11-07：D-062 — 失败轨迹复核、WAIT-SLA、B-new、第三轮诊断（已完成）

报告：[59_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md](59_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md)、[60_WAIT_SLA_CONTRACT_BNEW_AND_SAFETY_GATE_DESIGN.md](60_WAIT_SLA_CONTRACT_BNEW_AND_SAFETY_GATE_DESIGN.md)、[61_D062_DIAGNOSTIC_RESULTS.md](61_D062_DIAGNOSTIC_RESULTS.md)。

- **Stage 0 更正**：D-061 的 0.36 vs 0.006 并非真实重复副作用差距；99.4% 为 evaluator artifact（正确 ROLLBACK 被 saga gate 误伤），真实重复仅 7 例。
- **WAIT-SLA**：相对 A +0.089（p=0.0047），优于 Fixed-WAIT +0.054（p=0.0032）；行为 SLA 违规在 AwaitSLA/AB 诊断臂为 0。
- **B-new**：AB vs A +0.119（p=0.0002），验证集 AB vs A +0.142（p=0.0082）。
- **必须保留的限制**：AB vs NSGA-II all +0.1049（54 clusters，p=0.062）未显著；validation +0.1173（18 clusters，p=0.2277）也未显著。AB vs AwaitSLA 的 Q10 搜索增量 validation p=0.244，尚未证明独立泛化。
- **负结果**：B 单独劣于 NSGA-II（−0.074）；Safety Gate 有害（AB−ABG +0.193）；AB 仍显著落后 Hand（−0.282）。不得声称超越专家，也不得提前声称正式优于 NSGA-II。
- D-062 代码、测试和 diagnostic3 完成；正式 A-3b 仍 HOLD。下一步转入 D-063：统计分析可复现性、held-out cluster 功效仿真、预注册草案。

## 2026-11-09：D-063 执行接管更新（当前状态）

**当前阶段：D-063 准备工作；Stage 0 尚未执行完成；正式 A-3b 仍 HOLD。**

接管唯一入口：[NEXT_SESSION_PROMPT.md](NEXT_SESSION_PROMPT.md)。完整执行计划：[62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md](62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md)。

### 当前仓库核验基线

- 仓库：`yujian777555/kaitibaogao`
- 工作分支：`pilot-a-stateful-recovery`
- 本轮维护开始前 HEAD：`e6fee3bde05e8dea3fcc54f2ea1d97bc54837867`
- main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`
- 开始前分支相对 main：ahead 123 / behind 0
- main 不得修改；接管时重新查询实时 HEAD，不得把上述基线当成未来最新值。

### D-062 证据边界（必须继承）

- AB vs A +0.119，p=0.0002；AB vs A validation +0.142，p=0.0082。
- AwaitSLA vs A +0.089，p=0.0047；AwaitSLA vs AwaitFixed +0.054，p=0.0032。
- AB vs AwaitSLA 全数据 +0.031，p=0.0072；validation +0.031，p=0.244，搜索增量尚未证明独立泛化。
- AB vs NSGA-II 全数据 +0.1049，p=0.062；validation +0.1173，p=0.2277，均未显著。
- AB vs Hand −0.282，仍落后强手工策略。
- B 单独和 Safety Gate 的负结果必须保留；安全保证只限明确工具合同假设。

### D-063 执行顺序

1. **Stage 0：** 新增 diagnostic3 专用分析入口，从原始 JSON 独立复算 all/train/validation，检查配对、cluster、seed、split、分母、重复 episode 和哈希；对账 61 号报告。
2. **Stage 1：** 基于复算的 cluster-level paired differences 做 empirical Monte Carlo power simulation；报告 MDE 0.08/0.10/0.1173、双侧 alpha 0.05、80%/90% power 和 15% 失效预留。
3. **Stage 2：** 从 task/split/scenario manifest 核实任务族总数、validation 18 clusters 的来源、cluster 独立性和泄漏；输出 63 号任务族扩展审计。
4. **Stage 3：** 形成 64 号预注册草案，澄清 R1/R2 恢复与 R3/R4 正确升级的主要终点定义；主比较 AB vs canonical NSGA-II，次要比较 Holm，Hand 仅作参考。
5. **交用户审阅：** 预注册必须标记 DRAFT — NOT FROZEN；用户批准预注册不等于正式 A-3b 授权，正式实验仍需另行明确批准。

### 数据与授权纪律

- 当前 diagnostic3 validation 已被使用，不得充当正式 test。
- 不得查看或调参新的 held-out test。
- 不得用更多 episode/seed 伪造独立 cluster。
- 当前“总任务族 6 个”与“validation 2 个任务族 ×9=18 clusters”需要从 manifest 对账，不得猜测。
- GO：统计复现、synthetic tests、功效仿真、任务族审计、预注册草案和文档维护。
- HOLD：正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。

### CI 状态

最近一次实验代码回归 workflow： [Actions run 42398278551](https://github.com/yujian777555/kaitibaogao/actions/runs/42398278551)，在代码提交 `c0078d5c3db17380e81faca5752ac6a64f555a6d` 上成功，`pilot_a_recovery` 与 `pilot_a3b` 两个测试步骤均成功。其后为文档维护提交；文档更新本身未触发该代码路径 workflow。不得将历史 CI run 描述为最新文档 HEAD 的 CI。

**下一会话唯一首要任务：Stage 0 — 审查 diagnostic3 原始数据与 stats.py，建立可复现的独立分析入口。**


## 2026-11-08：D-063 — 统计独立复算、功效仿真、任务族扩展审计、预注册草案

- **Stage 0**（`analyse_diagnostic3.py`，17/17 测试）：7 对比 Δ 与 61 号**逐位一致**，p 值 MC 微差已解释；结构检查零问题；输出 `diagnostic3_recomputed.{json,csv,md}`。
- **Stage 1**（`power_simulation.json`）：主对比 MDE=0.10 @80% 需 **145** test clusters（含失效 171）；ICC≈−0.09。
- **Stage 2**（[63_D063_TASK_FAMILY_EXPANSION_AUDIT.md](63_D063_TASK_FAMILY_EXPANSION_AUDIT.md)）：576 候选、多样性面板重叠 0.83/3；train/val/test=8/4/17 族=72/36/**153 clusters**，泄漏受控。
- **Stage 3**（[64_A3B_PREREGISTRATION_CANDIDATE.md](64_A3B_PREREGISTRATION_CANDIDATE.md)）：正式预注册草案（主要对比 AB vs NSGA-II、Holm、硬安全门、协议冻结）——**待用户批准**。
- GO：审阅 64。HOLD：正式 A-3b（批准+预检后解锁）及全部既有 HOLD 项。


## 2026-11-09：D-064 — 64 号预注册草案独立审查（REQUEST CHANGES）

D-063 的工程交付已远端核验：最终基线 `4f23abed3150e09703839b980ad3afc9bb14dfb3`，CI run [42615985837](https://github.com/yujian777555/kaitibaogao/actions/runs/42615985837) 真实成功，pilot_a_recovery 28/28、pilot_a3b 68/68，合计 96/96。

但 64 号草案**暂不批准**。独立审查报告：[65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md](65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md)。

### 阻断项

1. **主要 estimand 不一致：** 64 §3 的 CondRecSucc 只算 R1+R2；D-063 功效分析却把 R1–R4 全部 class_success 混合，145 clusters 不能直接作为该主要终点的样本量。
2. **功效模拟方法不符：** 当前实际为正态参数化 Monte Carlo + 正态近似检验，不是经验 cluster resampling/sign-flip；缺 MCSE，且小样本 null FPR 有偏高值。
3. **ICC 证据不足：** 仅 6 个 task families（validation 只有 2 个），ICC 负点估计不能证明未来 task×composition clusters 独立。
4. **任务族语义与接入：** 576 候选只经合同属性过滤，未验证任务前置/后置条件；profile 多样性没有进入贪心目标；正式 8/4/17 生成器尚未接入当前固定 6 任务族运行路径。
5. **样本量未唯一冻结：** 153 test clusters 在 15% 失效后约 130；MDE=.10 的 80% power 方案需要约 171 招募 clusters。MDE=.1173 来自历史观察效应，不能未经论证直接作为 MDE。
6. **标签与安全门：** UNKNOWN 上限、R1/R2 主终点有效 cluster 数、硬安全门对两臂的判定语义需要冻结。

### 下一步唯一任务

先完成 **D-064-A：CondRecSucc（R1+R2 only）配对 cluster 分析**，从 diagnostic3 原始数据重算主效应、cluster SD 和 primary-eligible cluster 数；随后用正确 estimand 重做功效分析。未完成前，不批准 64、不生成/查看正式 test、不启动正式 A-3b。

**GO：** D-064 统计、数据生成、标签验证和预注册修订。  
**HOLD：** 正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。


## 2026-11-09：D-064-A — CondRecSucc 主要终点独立复算（结论翻转）

报告：[66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md](66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md)。程序 `condrec_analysis.py`（无硬编码）+ 13/13 测试 + `condrec_diagnostic3.{json,csv,report.md}`。

- **正确 estimand（R1+R2 only）：42 clusters，Δ=+0.3175，SD=0.3189，CI [0.218, 0.411] 不含 0，sign-flip p=0.000125——主要对比强显著。**
- 原全类别 +0.1049（p=0.065）系 12 个 R3/R4-only 稀释；scenario 加权一致（0.3145）；配对 1.000。
- R3/R4 权衡如实：AB 0.226/0.80 vs NSGA-II 0.679/0.933。
- GO：D-064-B（功效+ICC 敏感性）。HOLD 不变。


## 2026-11-09：D-064-A 完成，D-064-B 接管任务已冻结

D-064-A 正式报告：[66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md](66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md)。

- CondRecSucc 严格使用 R1+R2；R3 CorrectEscalation、R4 DamageContainment 独立报告。
- 42 个 primary-eligible task×composition clusters，嵌套在 **6 个 task families** 中；每个 family 当前有 7 个 eligible compositions；12 个 R3/R4-only clusters 预规定排除并登记。
- AB=0.5582，NSGA-II=0.2407，cluster-equal Δ=+0.3175，cluster SD=0.318856；D-064-A cluster bootstrap CI [0.218254, 0.411376]，cluster-level sign-flip MC p=0.000125（8000 次）。
- scenario-weighted Δ=0.314465，配对完整率 1.000。
- R3：AB 0.226 vs NSGA-II 0.679；R4：AB 0.800 vs NSGA-II 0.933。AB 的主要终点优势不能掩盖其安全行为率落后。
- 原始 diagnostic3 SHA-256：`b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`。
- D-064-A CI：run [42631223393](https://github.com/yujian777555/kaitibaogao/actions/runs/42631223393)，head `16e255de627b37713f0ea936df0ddb0dd03ac084`，success；109/109 tests。

**统计限制：** 42 个 composition clusters 并非已证明相互独立；它们嵌套于仅 6 个 task families。D-064-A 的 cluster-level CI/sign-flip 需要 D-064-B 做 family-level / hierarchical sensitivity，不能直接当作最终确认性推断。

### 下一步：D-064-B

完整执行接管提示词：[67_D064B_POWER_AND_HIERARCHICAL_SENSITIVITY_EXECUTION.md](67_D064B_POWER_AND_HIERARCHICAL_SENSITIVITY_EXECUTION.md)。

重点：
1. 以 family 为高层抽样单位，重建 42 clusters / 6 families 的嵌套结构；
2. 估计 ICC 及其不确定性，并对 ICC=0/.05/.10/.20 做敏感性；
3. 比较 family-block empirical resampling 与 ICC-controlled hierarchical simulation；
4. 对 MDE=.05/.08/.10/.1173/.15、80%/90% power、family/cluster attrition 生成样本量曲线；
5. 区分 design clusters 与 primary-eligible clusters：若仍为 7/9 eligible，17×9=153 design clusters 对应约 119 primary-eligible clusters（条件性投影，待 D-064-C 生成器验证）。

**GO：** D-064-B。  
**HOLD：** 正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。64 号预注册仍未批准；D-064-C 的任务语义验证完成前不最终冻结 test family 数和 MDE。


## 2026-11-09：D-064-B — CondRecSucc 层级功效与 ICC 敏感性

报告：[68_D064B_HIERARCHICAL_POWER_REPORT.md](68_D064B_HIERARCHICAL_POWER_REPORT.md)（程序 `power_hierarchical.py`、22/22 测试、产物 power_hierarchical.{json,report.md} + family_cluster_diagnostics.csv）。

- **层级显著性保持**：6/6 family 全正；family-level t p=4.6e-5、精确符号翻转 p=0.031、bootstrap CI [0.272,0.357]。
- **ICC**：MoM −0.1257（REML 边界 0，CI [−0.159,−0.111]）——不作独立性证明，采用 ICC 0/0.05/0.10/0.20 敏感性。
- **校准**：Student-t 控制 α 良好（推荐主检验）；bootstrap CI 检验反保守。
- **样本量**（MDE 0.10 @80%）：ICC 0/0.05/0.10/0.20 → 15/17/22/30 families；双 15% 损耗 22/30/40/40。17-family 条件性充分。
- GO：D-064-C。HOLD 不变；64 号 REQUEST CHANGES。


## 2026-11-09：D-064-C — 任务语义审计、生成器验证与设计冻结

报告：[69_D064C_INDEPENDENT_AUDIT_AND_DESIGN_FREEZE.md](69_D064C_INDEPENDENT_AUDIT_AND_DESIGN_FREEZE.md)（`test_d064c_audit.py` 25/25）。

- **审计通过**：validator 在已覆盖的 12 类对抗变形测试中全部拒绝（不宣称对任意攻击完备）；9 组合一致（修复 1 处陈旧注释）；标签独立；8/4/40 零泄漏；三哈希独立重建一致（manifest fb832bcc…（最终 CI run 42661732606；旧 af83f065… 已废止））。
- **功效最终核验**：34 有效 families×5 comps，ICC=0.20 最坏 **power=0.839 [0.832,0.846] ≥ 0.80**（硬编码 0.85 作废已更正）；MDE=0.10 标注 **PROPOSED_MDE_PENDING_ADVISOR_APPROVAL**。
- **64 号修订 R2**：40-family test（280 eligible clusters，哈希冻结）、family 级 Student-t 主检验、UNKNOWN≤5% 门禁。
- 最终 CI：run 42661732606 @ fa3bc2c success，174/174；Git 提交链 1908026b → fa53d198 → fa3bc2c。
- 64-R2 独立审计 R1：REQUEST CHANGES。发现主检验文字冲突、df 与 attrition 不一致、旧 manifest hash、测试计数与接管提示词陈旧、MDE 导师审批门未进入执行顺序等问题；详见 70_64R2_INDEPENDENT_REVIEW_R1.md。
- GO：修订 64-R2 并请求独立 R2 复审。HOLD：正式 A-3b、Test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox、合并 main；MDE 导师认可与用户批准均未完成。


## 2026-11-10：64-R2 独立审计 R1 — REQUEST CHANGES

本轮独立审查发现 64-R2 仍有预注册内部矛盾：§2 仍写 cluster-level bootstrap/sign-flip，§4 才写 family-level Student-t；df=39 未随 34 个有效 families 的损耗设计动态化；candidate manifest 仍引用旧 SHA；secondary tests 的检验定义不够明确；MDE 导师审批门未进入 GO 顺序。D-064-C 维护文档也已发现最终 CI hash、测试计数和 handoff 顶部状态需要勘误。见 70_64R2_INDEPENDENT_REVIEW_R1.md。正式 A-3b 继续 HOLD。


## 2026-11-10：D-064-R2 — 六项审计修正与 64-R3

交付：[64_A3B_PREREGISTRATION_CANDIDATE_R3.md](64_A3B_PREREGISTRATION_CANDIDATE_R3.md)（R2 原文保留）、[71_64R2_CORRECTIVE_RESPONSE_AND_R3_VALIDATION.md](71_64R2_CORRECTIVE_RESPONSE_AND_R3_VALIDATION.md)、`test_64r3_protocol.py` 15/15。

- **R2-001~006 全部修复**（主检验统一 family 级 t、动态 df、manifest **fb832bcc…** 独立重建确认、attrition/缺失规则冻结、导师 MDE 门、H2–H5 全定义）。
- 附带修复：F>15 符号翻转 MC 化（原 2^F 枚举挂死）。
- 功效复算一致（ICC=0.20 t=0.840 [0.833,0.847]）；全套件 189 绿。
- GO：**64-R3 独立复审**（71 号非审计）。HOLD 不变。


## 2026-11-10：64-R3 独立审计 — REQUEST CHANGES

独立审计报告：[72_64R3_INDEPENDENT_REVIEW.md](72_64R3_INDEPENDENT_REVIEW.md)。审计基线为工作分支 `ca7bb12f89dd72deaac205ffab89cf3054e6be06`、main `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；CI run 42670236796 success，测试为 28+161=189/189。独立重建 manifest/test-family/test-scenario 哈希均一致。

本轮不接受 71 号“全部已修复+已验证”的结论：R2-003 已关闭，动态 df 与 MDE 审批门文本部分成立，但 R2-001/004/006 的实现未关闭。新增阻断发现包括：R3 §5 pre-flight 错指 §6；`missing_data_rules()` 只是字典，labelled null 不 fail-closed，technical_missing_runs/family_loss/design_deviation 未实际计算；最低 1 composition 与固定 34×5 功效假设冲突；全零 family 差值被 `family_level_tests()` 误判为 `t=inf,p=0`，而模拟函数返回 p=1；正式 40-family 分析入口与 H2–H5 family-t/四项 Holm 路径尚未实现；Test payload 可由生成器返回，演化接口无 split guard，一次性解锁路径不存在。

独立功效复算：固定 34×5、ICC=0.20 时 power=0.8400 [0.8328,0.8472]；但 17 族 m=5、17 族 m=1 的合法不平衡情形 power 降至 0.5777 [0.5680,0.5874]。证据见 `experiments/pilot_a3b/audit_64r3_independent_checks.json`。

**唯一下一任务：** Executor 完成 R4 corrective revision 并提交新的独立复审。正式 A-3b、Test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和合并 main 继续 HOLD；即使审计通过，仍需导师 MDE 认可、用户批准和真实 pre-flight。
