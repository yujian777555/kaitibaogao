# kaitibaogao — 硕士学位论文开题研究

**唯一研究仓库：** https://github.com/yujian777555/kaitibaogao  
**研究主线：** Evolutionary Computation for AI Agents（演化计算赋能大语言模型智能体）  
**当前阶段：** 开题研究 / 文献系统检索与机制审查  
**状态日期：** 2026-11-04

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
