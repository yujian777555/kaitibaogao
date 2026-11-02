# kaitibaogao — 硕士学位论文开题研究

**唯一研究仓库：** https://github.com/yujian777555/kaitibaogao  
**研究主线：** Evolutionary Computation for AI Agents（演化计算赋能大语言模型智能体）  
**当前阶段：** 开题研究 / 文献系统检索与机制审查  
**状态日期：** 2026-11-02

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
