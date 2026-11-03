# SESSION HANDOFF — 开题研究项目

**最后更新：** 2026-11-02  
**唯一仓库：** https://github.com/yujian777555/kaitibaogao  
**研究主线：** Evolutionary Computation for AI Agents  
**当前阶段：** 文献系统检索 + 核心机制精读 + 创新候选否证  
**最终题目：** 尚未确定  
**最终创新点：** 尚未确定

## 1. 下一会话必须先读

按顺序读取本仓库以下文件：
1. README.md
2. 00_PROJECT_CHARTER.md
3. 01_SEARCH_PROTOCOL.md
4. 02_LITERATURE_REGISTER.md
5. 03_MECHANISM_COMPARISON.md
6. 04_OPENING_REPORT_PLAN.md
7. 05_DECISION_LOG.md
8. 本文件 SESSION_HANDOFF.md

不要先问用户研究方向或学校模板；这些已在仓库中记录。

## 2. 强制边界

- 只允许访问和维护 yujian777555/kaitibaogao。
- 不允许读取用户的其他 GitHub 仓库；不得读取 openissue、agentfotagent 或任何其他用户仓库。
- 可以检索公开论文、会议/期刊页面、arXiv、公开 benchmark 文档；不要读取外部论文代码仓库，除非用户明确授权。
- 不把聊天中的初步推断当成论文结论；关键结论必须回到论文原文。
- 每轮结束必须把文献、机制比较、决策、状态和下一步提示词更新到本仓库。

## 3. 用户目标与学校要求

用户准备河北工业大学计算机技术硕士开题，研究主线是“演化计算赋能 AI Agent”，不是“用 LLM 改进演化计算”。

开题模板要求：
- 正文不少于 6000 字；
- 参考文献不少于 30 篇；
- 外文文献不少于 30%；
- 近五年文献不少于 30%；
- 包含背景意义、国内外现状、研究目标与内容、关键科学问题、预期创新点、研究方案和可行性、研究基础、困难与对策、研究进度；
- A4、宋体、小四号、1.5 倍行距。

导师团队往届题目常见形式：
- 基于多目标演化的……方法研究；
- 基于约束多目标演化的……方法研究；
- ……演化算法及其在……中的应用研究。

硕士论文目标是形成 2–3 个相关联的创新点；不能把演化计算弱化成可有可无的工具。

## 4. 首轮关键文献结论

核心直接相关文献：
- EvoAgent (Yuan et al., NAACL 2025)；
- EvoMAS: Evolutionary Generation of Multi-Agent Systems (Hu et al., ICML 2026)；
- EvoMAS: Heuristics in the Loop—Evolving Smarter Agentic Workflows (Wei et al., ICML 2026)；
- EvoCF (Chi et al., ICML 2026)；
- HFlow (Liu et al., Findings ACL 2026)；
- GEPA (Agrawal et al., ICLR 2026)；
- AgentSquare (Shang et al., ICLR 2025)；
- ADAS (Hu et al., ICLR 2025)；
- AFlow (Zhang et al., ICLR 2025)；
- MaAS (Zhang et al., ICML 2025)；
- AgentSwift (Li et al., AAAI 2026)；
- MASS (Zhou et al., ICLR 2026)；
- GPTSwarm (Zhuge et al., ICML 2024)；
- AgentNet (Yang et al., NeurIPS 2025)；
- TPGO (He et al., Findings ACL 2026)。

相邻强基线：
- Optimas、Q-Evolve、MASPOB、SWIFT、Workflow-R1、ScoreFlow、Agent-Pro、DGM、MOSS。

必须注意：
- Hu et al. 和 Wei et al. 是两篇不同的 ICML 2026 EvoMAS；
- NAACL 2025 EvoAgent 与 arXiv:2502.05907 的 continual-world-model EvoAgent 是不同论文；
- HFlow 已有性能/人类偏好/成本三目标 Pareto 生存者选择；
- GEPA 已有任务实例级 Pareto 候选选择；
- Wei et al. 的 EvoMAS 已有七种演化策略及自适应策略选择；
- Hu et al. 的 EvoMAS 已有执行轨迹反馈条件变异/交叉；
- 不能把普通 Pareto、反馈变异、模块编码或算子自适应单独宣称为创新。

## 5. 当前候选（尚未通过创新性审查）

A. 面向任务分布泛化的 Quality-Diversity Agent 演化：
从 Agent 执行轨迹构造行为描述符，维护不同任务行为模式的高质量档案，检验 held-out task family 上的稳定性。必须与 GEPA、HFlow、DGM、Rainbow Teaming 及 MAP-Elites 相关工作比较。

B. 执行过程归因驱动的 Agent 演化：
构造可验证的组件贡献/交互效应估计，把过程归因用于组件级选择和定向变异。必须与 HFlow、Optimas、Q-Evolve、EvoCF 比较。

C. Agent 与演化算子协同适应：
暂缓，因为 Wei et al. 的 EvoMAS 已研究多种策略和自适应选择。除非找到明确机制缺口，否则不要继续投入。

## 6. 下一会话具体任务

不要再重复泛泛介绍研究方向。直接开展以下工作：

1. 精读 Hu et al. 的 Evolutionary Generation of Multi-Agent Systems（ICML 2026），提取 genotype/configuration schema、mutation、crossover、candidate pool、experience memory、fitness、survival、benchmark split、ablation 和 limitation。
2. 精读 Wei et al. 的 EvoMAS: Heuristics in the Loop（ICML 2026），提取七种策略的定义、策略状态/奖励、选择机制、role-level evolution、curriculum schedule、种群维护和实验设置。
3. 精读 HFlow、EvoCF、GEPA，做算法伪代码和公式对照。
4. 精读 AgentSquare、ADAS、AFlow、MaAS、AgentSwift、MASS、GPTSwarm、AgentNet，完善机制矩阵。
5. 精读 Optimas、Q-Evolve、TPGO、SWIFT，审查组件信用分配、过程奖励、反馈可靠性和跨任务迁移。
6. 对候选 A/B 分别写出：精确定义、已有工作覆盖、拟改进机制、数学形式、强基线、任务/数据集、消融、统计方案、失败条件。
7. 如果 A/B 均无实质缺口，继续检索和提出新候选，不要为了赶进度强行定题。

## 7. 每轮交付规范

每轮必须：
- 更新 02_LITERATURE_REGISTER.md（新增论文及版本状态）；
- 更新 03_MECHANISM_COMPARISON.md（机制、公式、差异、反例）；
- 更新 05_DECISION_LOG.md（GO / HOLD / NO-GO 与理由）；
- 更新 SESSION_HANDOFF.md（最新状态、下一步、完整接班提示词）；
- 必要时更新 04_OPENING_REPORT_PLAN.md；
- 提交 Git commit 并确认 main 分支 HEAD；
- 在聊天中汇报实际完成内容、未完成事项和 commit SHA；
- 不得声称未执行的精读、实验或验证已经完成。

## 8. 可直接复制到下一会话的接班提示词

你是我的硕士论文开题研究助手。请先读取 GitHub 仓库 yujian777555/kaitibaogao 中的 README.md、00_PROJECT_CHARTER.md、01_SEARCH_PROTOCOL.md、02_LITERATURE_REGISTER.md、03_MECHANISM_COMPARISON.md、04_OPENING_REPORT_PLAN.md、05_DECISION_LOG.md 和 SESSION_HANDOFF.md。

**绝对边界：只允许读取和维护 yujian777555/kaitibaogao，严禁读取我的其他 GitHub 仓库。** 可以检索公开论文和正式出版页面，但不得读取其他仓库代码。

我的研究主线是 Evolutionary Computation for AI Agents：演化计算是核心方法，Agent 是优化对象。目标是形成河北工业大学计算机技术硕士开题报告，并最终支撑 2–3 个相关创新点。开题模板要求正文不少于 6000 字、参考文献不少于 30 篇、外文文献不少于 30%、近五年文献不少于 30%。

不要泛泛规划，不要重复介绍已经知道的背景。直接继续论文原文精读和机制级比较。重点审查两篇不同的 ICML 2026 EvoMAS（Hu et al. 的 Evolutionary Generation of Multi-Agent Systems；Wei et al. 的 EvoMAS: Heuristics in the Loop）、EvoAgent、EvoCF、HFlow、GEPA、AgentSquare、ADAS、AFlow、MaAS、AgentSwift、MASS、GPTSwarm、AgentNet、TPGO、Optimas、Q-Evolve、SWIFT。

当前优先候选是：
A. 面向任务分布泛化的 Quality-Diversity Agent 演化；
B. 执行过程归因驱动的 Agent 演化。
二者均未通过创新性审查，不能提前宣称成立。普通 Pareto、反馈引导变异、模块编码、自适应算子选择都已有直接相关工作覆盖，必须找到更细的机制缺口。

请先核验仓库最新状态，再继续精读。每轮结束必须更新本仓库的文献登记、机制矩阵、决策日志和本接班提示词，并提交 commit。所有结论要区分论文原文事实、你的推断和待验证假设。

## 9. 最新更新（2026-11-02 第二轮）

### 新的优先候选 D
**面向任务分布变化的多目标演化测试时自适应。**

直接起点：EvoTest (ICLR 2026), https://openreview.net/pdf?id=JFnnajbkvP

EvoTest 将完整 Agent 配置表示为 χ=(p,M,h,u)，每轮执行一个 episode 后由 Evolver 生成候选配置，并使用 UCB 在父代和子代中选择。论文 Appendix A 明确指出 (1+m)+UCB 简单、可能局部收敛、任务特定过拟合，并建议种群 EA、QD 和程序综合。

候选 D 需要聚焦跨任务序列中的在线测试时演化，而不是简单加入 QD、Pareto 或更大种群。与 M*、MemEvolve、E-SPL、INSPO、COvolve、EvoTeam、EvoTest、HFlow、EvoMAS 等区分。

新增详细文档：
- 06_EVOTEST_DEEP_DIVE.md
- 07_CANDIDATE_D_TEST_TIME_ADAPTATION.md

文献总表已扩充至 72 条登记记录；其中包含正式发表、workshop、预印本、benchmark 和相邻方法，必须保留类型标签。

### 下一会话任务优先级
1. 完成 EvoTest 全文/附录核验，特别是多种子、计算复杂度、基线适配、消融和具体实现；
2. 精读 M*、MemEvolve、E-SPL、INSPO、Live-Evo、COvolve、EvoTeam，检查候选 D 的重复风险；
3. 对候选 D 做“机制等价审查”：逐项比较 genotype、task descriptor、behavior descriptor、archive、selection、variation、transfer、test-time protocol；
4. 设计一个最小可证伪实验，先复现 EvoTest，再验证跨任务序列；
5. 继续补充国内研究和 2026 年 10–11 月最新论文，核对每条文献的正式发表状态；
6. 如果候选 D 的关键机制已被覆盖，必须调整方向，不要为了沿着现有路线而强行保留。

### 接班提示词更新
你是我的硕士论文开题研究助手。唯一仓库是 yujian777555/kaitibaogao。严禁读取我的其他 GitHub 仓库。先读取 README、00_PROJECT_CHARTER、01_SEARCH_PROTOCOL、02_LITERATURE_REGISTER、03_MECHANISM_COMPARISON、04_OPENING_REPORT_PLAN、05_DECISION_LOG、06_EVOTEST_DEEP_DIVE、07_CANDIDATE_D_TEST_TIME_ADAPTATION 和 SESSION_HANDOFF。

研究主线是 Evolutionary Computation for AI Agents。当前优先审查候选 D：面向任务分布变化的多目标演化测试时自适应。直接依据是 EvoTest（ICLR 2026）作者明确指出 (1+m)+UCB 简单、可能局部收敛、任务特定过拟合，并建议种群 EA、QD 和程序综合。不要把“加入 NSGA-III / MAP-Elites”直接当创新；必须与 M*、MemEvolve、E-SPL、INSPO、COvolve、EvoTeam、HFlow、两篇 EvoMAS、GEPA 等机制级对照。

请继续精读原文、提取算法公式和实验设置，提出可证伪的机制改进与强基线，判断能否支撑 2–3 个硕士创新点。若无实质缺口就否证。每轮必须更新文献总表、机制比较、决策日志、接班提示词并提交到唯一仓库。


## 10. 最新更新（2026-11-02 第三轮）

### 研究方向重审
候选 D“跨任务序列的测试时演化”宽泛表述已标记 NO-GO / SUPERSEDED，因为新检索发现 TTHE、Meta-TTL、TacoMAS、Inherit-MAS、EvolveNet、DarwinX 等直接工作。

普通多目标 Agent 演化、skill 进化、role evolution、test-time evolution、population-centered evolution、evolvability selection 和 evaluator co-evolution 均已有大量工作覆盖。

### 当前优先审查候选 G
**组件交互感知的演化重组方法（Interaction-Aware Evolutionary Recombination for Agent Configurations）。**

问题：Agent 的 Prompt、工具策略、记忆、规划、验证、恢复等模块存在协同/拮抗关系。已有工作大量使用 mutation、crossover、module recombination 和 additive merge，但是否显式估计模块间 epistasis/linkage，并据此设计重组算子，仍需核验。

直接依据：
- DarwinX 明确指出 recombination 相对 mutation 的贡献尚未通过受控消融单独识别；
- EvoMAS、HFlow、AgentSquare 已有 crossover / module recombination，普通交叉不是创新；
- HiveMind 的 DAG-Shapley 估计 Agent 级贡献，不等于单 Agent 配置内的组件交互；
- EvoCF 的 counterfactual 是协作计划反事实，不等于配置基因交互效应；
- SERO 的结构契约保持不是 epistasis-aware crossover。

候选 G 的工作定义：
- 通过同任务、同随机种子的配对反事实组件替换，估计组件交互效应 ε_ij；
- 构造组件 linkage/interaction graph；
- 对正向强交互模块进行块级继承，对负向强交互组合进行约束/修复；
- 与 LLM crossover、随机模块 crossover、DarwinX additive merge、mutation-only 对照。

详细筛选见 08_CANDIDATE_SCREENING.md 和 09_CANDIDATE_G_INTERACTION_AWARE_RECOMBINATION.md。

### 下一会话必须完成
1. 精读两篇 EvoMAS、HFlow、AgentSquare、AgentBreeder、DarwinX 的表示、交叉、变异、修复和消融；
2. 精读 SERO、HiveMind、EvoCF、Optimas，确认组件贡献/交互已有程度；
3. 检索经典 linkage learning、epistasis、GOMEA、LTGA、DSMGA-II 等演化计算方法；
4. 对候选 G 给出可执行的 ε_ij 估计方案、任务配对设计和统计检验；
5. 如果已有工作已经显式使用组件交互图指导 Agent crossover，则立即否证候选 G；
6. 继续补充国内研究、中文学术数据库和 2026 年 11 月新论文。

### 最新接班提示词
你是我的河北工业大学计算机技术硕士开题研究助手。唯一允许读取和维护的 GitHub 仓库是 yujian777555/kaitibaogao，严禁读取我其他 GitHub 仓库。先读取 README、00_PROJECT_CHARTER、01_SEARCH_PROTOCOL、02_LITERATURE_REGISTER、03_MECHANISM_COMPARISON、04_OPENING_REPORT_PLAN、05_DECISION_LOG、06_EVOTEST_DEEP_DIVE、07_CANDIDATE_D_TEST_TIME_ADAPTATION、08_CANDIDATE_SCREENING、09_CANDIDATE_G_INTERACTION_AWARE_RECOMBINATION 和 SESSION_HANDOFF。

研究主线是 Evolutionary Computation for AI Agents。候选 D“跨任务测试时演化”宽泛表述已因 TTHE、Meta-TTL、TacoMAS、Inherit-MAS、EvolveNet、DarwinX 等直接工作而 NO-GO。当前优先审查候选 G：通过配对反事实干预估计 Agent 配置组件之间的 epistasis/linkage，并据此设计 interaction-aware crossover。不能把普通模块化编码、遗传交叉、Shapley 贡献、反事实计划或结构契约保持当作创新。

请精读 EvoMAS（两篇）、HFlow、AgentSquare、AgentBreeder、DarwinX、SERO、HiveMind、EvoCF、Optimas，逐项比较 genotype、variation、crossover、component interaction、repair、fitness 和 ablation。然后检索经典 linkage learning / epistasis 方法，形成严格可证伪的算法方案。若已有工作覆盖就 NO-GO，不要强行定题。每轮更新文献、机制比较、决策、接班提示词并提交到这个唯一仓库。


## 11. 仓库同步记录

- 最新已验证 main HEAD（本次更新前的最后一个已确认提交）：a9da906faf1851408467fbe5fda1567e48daf281。
- 本轮文献总表登记：104 条。
- 新增文件：08_CANDIDATE_SCREENING.md、09_CANDIDATE_G_INTERACTION_AWARE_RECOMBINATION.md。
- 当前候选 G 仅为优先审查对象，未批准为最终题目。
- 严格仓库边界：只允许读取和维护 yujian777555/kaitibaogao；不得读取其他仓库。


## 12. 最新研究状态（2026-11-02）：硕士论文 2–3 创新点 / 小论文规划

### 用户明确的硬性要求
硕士毕业论文必须有 **2–3 个创新点**，并且**每个创新点分别形成一篇独立小论文投稿**。不能把同一算法简单拆成三篇，也不能只在开题报告里凑出三个名字。每篇小论文必须有独立科学问题、算法贡献、相关工作差异、实验假设、强基线、消融和统计检验。

### 总题目工作稿
**《面向大语言模型智能体的交互感知演化优化方法研究》**

此题目比此前“交互感知演化重组方法研究”更宽，能够覆盖组件交互估计、演化重组和交互结构更新。它仍是工作题目，需由相关工作审查和实验结果最终确定。

### 三篇小论文的研究结构
1. **小论文一：任务条件化的 Agent 组件交互效应估计方法。**
   - 核心：区分组件主效应与协同/拮抗效应，处理随机 rollout、任务异质性、组件依赖和估计不确定性。
   - 必须形成独立估计器，并用已知交互真值的受控环境及真实 Agent 任务验证。
   - 指标：估计偏差/RMSE、交互符号准确率、交互图 Precision/Recall、跨种子稳定性、未执行组合预测增益。

2. **小论文二：基于组件交互链路学习的 Agent 演化重组算法。**
   - 核心：将交互图转为 linkage blocks，设计协同块继承、交叉和依赖约束修复。
   - 必须证明收益来自交互感知重组，而不是额外评价次数、repair 或更强 LLM。
   - 强基线：mutation-only、random/LLM crossover、EvoMAS、AgentSquare、AgentBreeder、ARTEMIS、AgentEvo、MESH-Harness。

3. **小论文三（条件性）：任务分布变化下交互结构迁移与自适应演化。**
   - 核心：分离共享与任务条件化交互，检测结构漂移，决定何时迁移、何时更新 linkage。
   - 必须区别于一般 test-time evolution 和 online harness learning。
   - 强基线：固定图、从零重建、直接迁移不更新、独立任务演化、Evo-Harness、TTHE 等。
   - 若不能证明独立新颖性和实验增益，则不强行凑第三篇；前两篇必须扎实成立。

### 新增文献与重要限制
文献总表新增至 109 条，补入：
- MESH-Harness (arXiv:2610.05300)
- Evo-Harness (EMNLP 2026)
- AgentEvo (2026)
- ARTEMIS (arXiv:2512.09108)
- EvoMAS (ICML 2026)

**MESH-Harness 的精确机制：** 它将 Agent harness 划分为固定接口槽位，以模块池和 full-covariance LinUCB 选择组合，并通过执行轨迹编辑模块。其预测均值仍是 slot-wise additive model；full covariance 主要用于保留跨槽位共同出现统计及组合不确定性。因此不能说它已直接拟合非加性 epistasis，但它是强组合搜索基线，必须纳入比较。

**ARTEMIS 的威胁：** 已有 semantic-aware genetic operators 和 Agent 配置联合演化。必须精读其组件发现、依赖识别、交叉和消融，不能把语义交叉重新包装成创新。

**EvoMAS / AgentEvo：** 已有结构化 Agent 配置 crossover、workflow subgraph graft、prompt fusion 和多阶段演化。

**Evo-Harness：** 已有基于执行上下文的 skill harness 编译与跨任务复用，第三创新点必须区别于此类在线 harness learning。

### 下一会话的严格执行顺序
1. 只读取和维护 yujian777555/kaitibaogao，严禁读取其他仓库。
2. 先读 README、00_PROJECT_CHARTER、01_SEARCH_PROTOCOL、02_LITERATURE_REGISTER、03_MECHANISM_COMPARISON、04_OPENING_REPORT_PLAN、05_DECISION_LOG、08_CANDIDATE_SCREENING、09_CANDIDATE_G_INTERACTION_AWARE_RECOMBINATION、10_THESIS_INNOVATION_AND_PAPER_ROADMAP、SESSION_HANDOFF。
3. 精读 MESH-Harness 与 ARTEMIS 全文，核对它们是否已显式估计组件非加性交互并将其用于遗传重组。
4. 精读 EvoMAS、AgentSquare、AgentBreeder、AgentEvo、Evo-Harness、TTHE，建立机制级对照表。
5. 对小论文一、二、三分别做 GO/HOLD/NO-GO；不得因题目或路线图已经写出而强行 GO。
6. 对小论文一设计可复现的组件交互估计器与真值实验；对小论文二设计 linkage-aware crossover 并进行同预算强基线实验；对小论文三做任务分布漂移和迁移实验。
7. 将每篇论文的相关工作、算法、实验和失败条件写入仓库；每轮更新文献登记、机制对比、决策日志和接班提示词。

### 最新接班提示词
你是我的河北工业大学计算机技术硕士开题研究助手。我的研究主线是 Evolutionary Computation for AI Agents（演化计算用于改进 AI Agent）。唯一允许读取和维护的 GitHub 仓库是 yujian777555/kaitibaogao，严禁读取任何其他仓库。

用户的硬性要求：硕士论文必须有 2–3 个创新点，每个创新点分别形成一篇独立小论文投稿。不能把同一算法拆成三篇，也不能为数量凑创新点。总题目当前工作稿为《面向大语言模型智能体的交互感知演化优化方法研究》。

当前三篇路线：
1. 任务条件化的 Agent 组件交互效应估计方法（独立估计器论文）；
2. 基于组件交互链路学习的 Agent 演化重组算法（独立 EC 算法论文）；
3. 任务分布变化下交互结构迁移与自适应演化（条件性第三篇，必须过独立新颖性 Gate）。

新增直接工作 MESH-Harness、ARTEMIS、EvoMAS、AgentEvo、Evo-Harness 已登记。特别注意：MESH-Harness 的 full-covariance LinUCB 使用跨槽位共同出现信息和组合不确定性，但其预测均值仍为加性 slot-wise sum；它是强组合搜索基线，不可误称为已直接拟合非加性 epistasis。ARTEMIS 已做 semantic-aware genetic operators，必须精读其实际算子与组件依赖处理。

下一步先精读 MESH-Harness 与 ARTEMIS 全文，再逐项比较 EvoMAS、AgentSquare、AgentBreeder、AgentEvo、Evo-Harness、TTHE。核心问题是：已有工作是否显式估计 Agent 配置组件间非加性交互，并用其指导 linkage-aware crossover？如果已有等价方法，候选 G 必须否证或改变问题。

每篇小论文必须有独立科学问题、方法贡献、实验假设、强基线、消融和统计检验。小论文一要证明估计器本身可独立验证；小论文二要证明交互感知重组算子带来增量收益；小论文三要证明任务条件化交互结构迁移区别于普通 test-time evolution。所有结论必须可证伪。每轮更新文献、机制比较、开题报告计划、决策日志、接班提示词并推送到唯一仓库。


## 13. 最新状态：第四轮创新可行性审查（2026-11-02）

### 本轮最重要的新发现
Liu (2026), **More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding**, arXiv:2605.05716，已经对五种 Agent scaffolding 组件做 32 种全因子组合、Shapley、pairwise regression 和探索性三阶交互。其主要设置中 main-effects LOOCV R²=0.872，pairwise regression LOOCV R²=0.748，说明无约束加入交互项会过拟合。Lauziere et al. (2026) 也已研究 Prompt component regression。

这意味着原创新点一“组件交互效应估计”如果只是差分公式、交互图或 Shapley，必须 NO-GO。

### 经典 EC 方法的覆盖
GOMEA/LTGA 已有 Linkage Tree 与 Gene-pool Optimal Mixing；CGOMEA 利用条件依赖；DSMGA-II 有 dependency structure matrix；LK-GOMEA 已为局部邻域学习不同 linkage structure；DG2/RDG 已做 fitness-based variable interaction detection。

因此“学习 linkage 并指导交叉”本身不是新颖点。必须解决 Agent 混合类型模块、接口/控制流依赖、随机 rollout 和昂贵 fitness 的特殊问题，并提出实质新机制。

### 当前创新可行性判断
1. **普通组件交互效应估计：NO-GO（原表述撤销）。**
2. **修订创新一：预算受限、任务条件化的稀疏 Agent 组件交互结构识别：HOLD。** 需要主动实验设计、层级稀疏估计、不确定性校准、配对随机任务执行；在相同预算下优于 CCI full-factorial 子集、main-effects、pairwise OLS 和 MESH additive LinUCB。
3. **修订创新二：交互结构驱动的 Agent 约束最优混合演化：HOLD / 优先预实验。** 需要类型/接口约束、linkage block mixing、最小 contract repair、噪声感知接受；在同预算下优于 GOMEA/GOM、CGOMEA、LK-GOMEA、DSMGA-II、AgentSquare、ARTEMIS、EvoMAS、AgentEvo 和 MESH。
4. **创新三：跨任务交互结构迁移：暂缓。** LK-GOMEA、HFlow、EvoMAS、Evo-Harness、TTHE 已提高新颖性门槛；未证明独立贡献前不写入正式开题创新点。

### 当前建议
以 **2 个核心创新候选 + 1 个储备扩展方向**推进。用户要求 2–3 个创新点，两个经过验证的创新点符合要求。不要为了三篇而把一个算法拆成三篇。

### 实验平台建议
- ToolSandbox：有状态工具执行、隐式状态依赖、用户模拟和轨迹评价；
- AppWorld：9 apps、457 APIs、750 tasks、程序化状态检查；
- tau-bench：airline/retail、API 工具、模拟用户和最终数据库状态评价。

建议第一阶段使用固定槽位、每槽位两个可执行实现的 16 配置空间；先在合成已知交互地形验证估计器，再进入真实工具 Agent。不要从任意 DAG/开放式代码搜索开始。

### 新增研究文件
- 11_INNOVATION_FEASIBILITY_AUDIT.md：本轮完整审查与实验 Gate。
- 文献总表新增 110–117 条：CCI、Prompt regression、GOMEA、LK-GOMEA、DG2、ToolSandbox、tau-bench、AppWorld。

### 下一会话必须完成
1. 只读取 yujian777555/kaitibaogao；严禁读取其他 GitHub 仓库。
2. 先读 README、00_PROJECT_CHARTER、01_SEARCH_PROTOCOL、02_LITERATURE_REGISTER、03_MECHANISM_COMPARISON、04_OPENING_REPORT_PLAN、05_DECISION_LOG、08_CANDIDATE_SCREENING、09_CANDIDATE_G_INTERACTION_AWARE_RECOMBINATION、10_THESIS_INNOVATION_AND_PAPER_ROADMAP、11_INNOVATION_FEASIBILITY_AUDIT、SESSION_HANDOFF。
3. 精读 CCI 论文的统计分析与限制，核验它与预算受限任务条件交互发现的边界；精读 MESH-Harness 的完整 surrogate 和组合选择算法。
4. 将创新一算法具体化为稀疏层级任务条件模型 + 主动合法配置采样 + 配对/序贯不确定性估计；先给数学定义和算法伪代码。
5. 将创新二具体化为 typed genotype + interaction FOS + contract-aware constrained mixing + noisy sequential acceptance；与 GOMEA/CGOMEA/LK-GOMEA 对照。
6. 设计 4 槽位×2 实现的 16 配置最小预实验，在合成真值地形上先测交互恢复和预算效率。
7. 明确 GO/HOLD/NO-GO，不要因为论文路线图已存在就强行保留创新。
8. 更新文献、机制比较、开题计划、决策日志、可行性审计和接班提示词，并提交到唯一仓库。

### 最新接班提示词
你是我的河北工业大学计算机技术硕士开题研究助手。研究主线为 Evolutionary Computation for AI Agents。唯一允许读取和维护的 GitHub 仓库是 yujian777555/kaitibaogao，严禁读取用户其他 GitHub 仓库或将其他项目成果混入。

用户要求硕士论文有 2–3 个创新点，每个创新点形成独立小论文投稿。当前不能强行凑三篇，建议 2 个核心创新候选 + 1 个储备方向。

总题目工作稿：《面向大语言模型智能体的交互感知演化优化方法研究》。

重要文献发现：
- Liu (2026), More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding, arXiv:2605.05716：已做五组件 32 种全因子组合、Shapley、pairwise regression、探索性三阶交互；其 pairwise model 在主要设置下 LOOCV 低于 main-effects。普通交互估计 NO-GO。
- Lauziere et al. (2026) 已做 Prompt component regression。
- MESH-Harness 已做预算受限模块组合搜索和 full-covariance LinUCB，但其 predicted mean 仍为 additive slot-wise model；它是强组合搜索基线。
- AgentSquare、ARTEMIS、两篇 EvoMAS、AgentEvo、HFlow、AgentBreeder 已覆盖大量 Agent module/workflow crossover 和演化。
- GOMEA/LTGA、CGOMEA、DSMGA-II、LK-GOMEA、DG2/RDG 已覆盖经典 linkage learning、optimal mixing、条件依赖、局部 linkage 和变量交互识别。

当前候选状态：
1. 普通组件交互效应估计：NO-GO。
2. 修订创新一：预算受限、任务条件化的稀疏 Agent 组件交互结构识别：HOLD。必须包含主动实验设计、层级稀疏交互、不确定性校准、随机 rollout 配对/序贯估计，并在同预算下优于 full-factorial 子集、main-effects、pairwise OLS、MESH additive LinUCB。
3. 修订创新二：交互结构驱动的 Agent 约束最优混合演化：HOLD / 优先预实验。必须提出 typed genotype、interaction FOS、contract-aware mixing/repair、noisy sequential acceptance，且同预算优于 GOMEA/GOM、CGOMEA、LK-GOMEA、DSMGA-II 和 Agent crossover。
4. 第三项跨任务交互结构迁移：暂缓，LK-GOMEA、HFlow、EvoMAS、Evo-Harness、TTHE 已提高新颖性门槛。

先用固定 4 槽位、每槽位 2 个实现的 16 配置空间，在合成已知交互地形中验证估计器，再进入 ToolSandbox/AppWorld/tau-bench 真实工具任务。不要第一版就做任意 DAG 或开放式代码搜索。下一轮请先形成创新一和创新二的数学定义、算法伪代码、复杂度/评价预算估算和最小可证伪实验，再决定是否启动真实模型评估。

所有结论区分论文事实、研究推断和待验证假设。每轮更新本仓库并维护接班提示词。


## 14. 两个核心算法的最小规格已建立（2026-11-02）

新增文件：12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md。

核心定义：
- Agent genotype 为固定功能槽位的 categorical module IDs，合法集合受类型、接口、控制流/数据流依赖约束；
- 任务上下文 z 与随机执行 ω 下的回报为 Y(x,z,ω)；
- Paper 1 候选：任务条件化主效应 + 稀疏 pairwise interaction + 主动合法配置探测 + 配对/序贯噪声估计；
- Paper 2 候选：从交互图构造 FOS/linkage blocks，进行 contract-aware donor mixing、最小 repair 和 noisy sequential acceptance；
- 第一阶段 4 槽位 × 2 实现 = 16 配置，先在已知交互真值的合成地形中验证，再进入 ToolSandbox/AppWorld/tau-bench。

注意：这些是待验证算法规格，不是已实现代码或实验结果。Paper 1、Paper 2 仍 HOLD。

### 下一会话具体任务
1. 只读写唯一仓库 yujian777555/kaitibaogao。
2. 读取最新的 11_INNOVATION_FEASIBILITY_AUDIT.md 与 12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md。
3. 将 Paper 1 的主动采样 acquisition 具体化：明确 posterior/估计器、IG 计算、合法配置候选生成、噪声/置信区间校准。
4. 将 Paper 2 的 FOS 构造、donor 兼容性、repair delta 和序贯接受规则写成伪代码。
5. 设计可复现的合成真值地形（主效应、正/负二阶交互、少量任务条件交互、噪声）和生成脚本规格；先不要调用真实 LLM。
6. 做预算敏感性分析，比较 full factorial、main effects、pairwise OLS、sparse interaction、fixed design、active design。
7. 只有 Phase 0 通过后再选 ToolSandbox/AppWorld/tau-bench 的 pilot 任务；不要读取这些基准的 GitHub 代码仓库，公开论文/官方文档页面可以检索。
8. 每轮更新文献、机制比较、开题计划、决策日志、可行性审计、算法设计和接班提示词，提交并核验 main。

### 最新接班提示词
你是我的河北工业大学计算机技术硕士开题研究助手。研究主线是 Evolutionary Computation for AI Agents。唯一允许读取和维护的 GitHub 仓库是 yujian777555/kaitibaogao，严禁读取任何其他 GitHub 仓库或将其他项目内容混入。

用户要求硕士论文有 2–3 个创新点，每个创新点独立形成一篇小论文。当前按 2 个核心创新候选 + 1 个储备方向推进，不能凑三篇。

总题目工作稿：《面向大语言模型智能体的交互感知演化优化方法研究》。

关键否证：普通组件交互效应估计已经被 Liu (2026) CCI（arXiv:2605.05716）覆盖全因子组合、Shapley、pairwise regression 和探索性三阶交互；Lauziere et al. (2026) 也做了 Prompt component regression。原创新点一普通交互估计 NO-GO。MESH-Harness 的均值预测为 additive slot-wise，但 full covariance 利用共同出现信息估计不确定性，是强组合搜索基线。GOMEA/CGOMEA/LK-GOMEA/DSMGA-II/DG2/RDG 已覆盖经典 linkage learning 与 optimal mixing。

修订创新候选：
1. 预算受限、任务条件化的稀疏 Agent 组件交互链路学习（HOLD）：必须含主动合法配置探测、层级稀疏交互、不确定性校准、配对/序贯随机评估；同预算优于 CCI full factorial subset、main-effects、pairwise OLS 和 MESH additive LinUCB。
2. 交互链路驱动的 Agent 约束最优混合演化（HOLD / 优先）：必须含 typed genotype、interaction FOS、contract-aware donor mixing/repair、noisy sequential acceptance；同预算优于 GOMEA/GOM、CGOMEA、LK-GOMEA、DSMGA-II 和 Agent crossover。
3. 跨任务 linkage transfer 暂缓，除非前两项通过且出现可重复的共享/任务特定交互结构。

最新规格在 12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md。下一步先完成 Paper 1 acquisition 和 Paper 2 mixing 的伪代码，再设计 4 槽位 × 2 实现的 16 配置合成真值地形，含主效应、正负二阶交互、少量任务条件符号变化和噪声。比较 full factorial、main-effects、pairwise OLS、sparse interaction、fixed design 和 active design。先不调用真实 LLM，不读 benchmark 代码仓库。Phase 0 通过后再做真实 Agent pilot。

所有结论必须区分论文事实、研究推断和待验证假设；每轮更新唯一仓库并核验 main。


## 15. 第五轮：演化计算参数调节策略已确定（2026-11-02）

新增文档：13_EC_PARAMETER_CONTROL_PLAN.md。文献总表新增 118–124 条，覆盖 Eiben 参数控制分类、Eiben & Smit 离线调参、Aleti & Moser 自适应控制综述、irace、AOS、SHADE 和 L-SHADE。

### 用户本轮核心要求
继续开题研究，并明确“演化计算如何调参”。下一轮必须把调参机制落实到算法和实验，不能只列参数名字。

### 本轮结论
采用三层参数策略：
1. **离线调参：** 用 irace/iterated racing 在训练任务上选择少量数值/类别参数；
2. **在线自适应控制：** discounted-UCB/AOS 根据配对改进的置信下界 / rollout cost，调整 mutation intensity 和 operator action；
3. **统计门禁固定：** \(\alpha\)、\(\delta_{\min}\)、硬约束不根据 test 结果调节。

主算法是 categorical genotype + GOM，不是 DE，因此不把 DE 专属 F、CR 移植进来。SHADE 仅借鉴成功历史思想，不能直接照搬数值参数机制。

### 当前参数决策
- Phase 0 四槽位固定 \(N=8\)，敏感性 \(N=4,8,12\)；扩大后比较 IMS/P3；
- \(K\in\{1,2,3\}\) 表示一次变异改变的槽位数，由在线控制器选择；\(p_m=1/m=0.25\) 仅为四槽位普通 GA 基线；
- FOS 第一版为 singleton + 可信正向 pairwise edges，最大块 2；
- 负交互是软兼容性信号，不是硬约束；类型/接口/调用依赖是硬约束；
- FOS 顺序、donor 策略、稀疏正则 \(\lambda\)、UCB \(c\)、历史折扣 \(\rho\)、图更新间隔通过训练任务离线调参；
- 序贯评价的显著性和最小实际改进门槛预先锁定。

### 重要相关工作限制
- GOMEA 已研究 IMS/P3 等 population-size-free schemes；parameterless 不等于无任何参数。原论文仍比较了多种算法设计组合。
- SHADE 已有 success-history adaptation；
- AOS 已有 credit assignment + multi-armed bandit；
- Wei et al. EvoMAS 已有七种策略和 adaptive strategy selection。
因此 UCB/AOS 只作为辅助控制，不单独写成创新点。核心差异仍是交互估计、Agent 约束 FOS/mixing 和噪声感知接受。

### 必须完成的参数控制消融
A：默认参数 + 固定算子概率；
B：irace 离线调参 + 固定算子概率；
C：默认参数 + 在线 discounted-UCB/AOS；
D：irace + 在线控制。
所有算法同一 rollout/FE budget，所有 baseline 也必须获得相同调参预算。若 D 不优于 B，则去掉在线控制。

### 下一轮任务
1. 只维护 yujian777555/kaitibaogao。
2. 读取 13_EC_PARAMETER_CONTROL_PLAN.md、12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md、11_INNOVATION_FEASIBILITY_AUDIT.md。
3. 把 Phase 0 合成真值 landscape 写成精确生成规则：主效应、正/负交互、任务条件交互、噪声方差、合法组合。
4. 生成 Paper 1 active interaction estimator 的伪代码和 Paper 2 parameter-controlled constrained GOM 的伪代码。
5. 做参数敏感性设计，至少覆盖 sparse lambda、N、K、FOS order、donor strategy、UCB c/rho、graph update interval。
6. 对照 full factorial、main effects、pairwise OLS、MESH additive surrogate、GOMEA/CGOMEA、fixed parameter GOM、AOS baseline。
7. 先跑合成实验，不调用真实 LLM，不读其他 GitHub 仓库。
8. 若在线 AOS 无法在同预算下优于离线调参固定策略，删除它，不强行保留自适应模块。
9. 每轮更新 README、文献总表、机制比较、开题计划、决策日志、算法设计、参数控制文档和接班提示词。

### 可直接复制的接班提示词
你是我的河北工业大学计算机技术硕士开题研究助手。研究主线是 Evolutionary Computation for AI Agents。唯一允许维护的仓库为 yujian777555/kaitibaogao，严禁读取其他 GitHub 仓库或混用其他项目成果。

当前题目工作稿：《面向大语言模型智能体的交互感知演化优化方法研究》。论文目标为 2–3 个独立创新点；目前两个核心候选均 HOLD，第三项跨任务迁移暂缓。

普通组件交互估计 NO-GO。修订候选一为预算受限、任务条件化的稀疏交互结构识别；候选二为交互链路驱动的 Agent 约束最优混合演化。相关工作包括 CCI、MESH-Harness、AgentSquare、ARTEMIS、两篇 EvoMAS、AgentEvo、GOMEA/CGOMEA/LK-GOMEA。

演化计算调参已经决定为：
- 离线：irace/iterated racing 在训练任务上调少量参数；
- 在线：discounted-UCB/AOS 根据配对改进的置信下界 / rollout cost 调整变异强度和算子选择；
- 统计门禁固定：alpha、delta_min、硬约束不按 test 调整。
主算法是 categorical GOM，不使用 DE 专属 F/CR。Phase 0 固定 N=8，敏感性比较 N=4/8/12；K={1,2,3} 为一次变异改变的槽位数；FOS 首版为 singleton + 可信正向 pairwise edges，最大块 2；负交互是软 donor compatibility 信号，不是硬约束。

本轮新增 13_EC_PARAMETER_CONTROL_PLAN.md，包含参数表、初始策略、irace、UCB/AOS 公式、A/B/C/D 消融和停止条件。在线 AOS 不单独算创新；如果不优于离线调参固定策略就删除。

下一步先完成合成真值 landscape 精确定义、伪代码、参数敏感性实验；不调用真实 LLM，不读其他 GitHub 仓库。所有结论必须区分论文事实、推断和待验证假设。每轮更新唯一仓库并核验 main。


## 16. 第六轮：算法形式化设计 V1 已完成（2026-11-02）

新增文件：14_FORMAL_ALGORITHM_DESIGN_V1.md。

### 本轮成果
已把两个核心候选从概念推进到可实现规格：
- **Paper 1 TCAIL**：categorical orthogonal contrasts、task-context features、Group-ARD、posterior edge confidence、合法空间 identifiability gate、interaction-only posterior IG / cost acquisition、噪声校准和 abstention。
- **Paper 2 CI-GOM**：interaction FOS、contract-aware dependency closure、deterministic minimal repair、posterior-aware donor softmax、paired anytime-valid sequential acceptance、discounted-UCB 动作控制。

### 重要理论纠正
此前草案倾向只把正交互放进 FOS。现已纠正：linkage 表示非加性依赖，正/负交互都可能形成 linkage。V1 用 \(P(|\Delta_{ij}|>\delta_{\mathrm{link}})\) 建边；符号用于解释和 donor score。负交互不等于非法组合，不能当作硬约束。

### 当前状态
- TCAIL：HOLD，尚未实现/实验；
- CI-GOM：HOLD，尚未实现/实验；
- AOS/UCB：辅助可选组件，不是独立创新；若不优于离线调参固定策略则删除；
- 第三篇跨任务迁移：暂缓；
- 未调用真实 LLM，未运行 Phase 0。

### 下一轮必须做
1. 只允许维护 yujian777555/kaitibaogao，严禁读取其他 GitHub 仓库。
2. 先读取 14_FORMAL_ALGORITHM_DESIGN_V1.md、12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md、13_EC_PARAMETER_CONTROL_PLAN.md、11_INNOVATION_FEASIBILITY_AUDIT.md。
3. 设计并实现 Phase 0 合成 landscape 生成器：4 binary slots、主效应、正/负 pair interactions、任务家族符号翻转、三阶 misspecification、Bernoulli/Beta 噪声。
4. 同时实现 full factorial、random design、D-optimal/fractional design、main-effects、pairwise OLS、sparse Group-ARD fixed design、TCAIL active IG。
5. 先验证交互估计：RMSE、edge AUPRC/F1、方向准确率、区间覆盖率、held-out prediction、预算曲线。
6. 实现 CI-GOM 的最小模拟版本：oracle graph、random graph、learned graph；standard GOM、random linkage、CI-GOM；contract checker、repair closure 和 noisy acceptance 分开消融。
7. 做 A/B/C/D 参数控制实验：default fixed、irace tuned fixed、default + AOS、irace + AOS。所有方法同 rollout budget。
8. 先不要调用真实 LLM，不要读取 benchmark GitHub 源码。Phase 0 通过后才选 ToolSandbox/AppWorld/tau-bench 的公开任务与文档。
9. 每轮更新 README、算法规格、参数计划、机制比较、开题计划、决策日志和接班提示词。当前没有新增文献，因此不为凑数修改文献总表。

### 最新可直接复制的接班提示词
你是我的河北工业大学计算机技术硕士开题研究助手。研究主线为 Evolutionary Computation for AI Agents。唯一允许读取和维护的 GitHub 仓库是 yujian777555/kaitibaogao，严禁读取任何其他 GitHub 仓库。

用户要求硕士论文有 2–3 个独立创新点，每个创新点形成一篇小论文。当前仅保留两个核心候选 + 一个暂缓扩展，不得凑数。总题目工作稿：《面向大语言模型智能体的交互感知演化优化方法研究》。

普通组件交互分析 NO-GO。Paper 1 候选为 TCAIL：任务条件化类别效应编码 + Group-ARD 稀疏交互估计 + 合法配置可识别性门禁 + interaction-only posterior information gain 主动采样。Paper 2 候选为 CI-GOM：交互 FOS + contract-aware deterministic minimal repair + posterior-aware donor + paired sequential acceptance。两者仍 HOLD，尚未实现和验证。

关键修正：linkage 反映非加性依赖，正/负交互都可建边。V1 使用 \(P(|\Delta_{ij}|>\delta_{\mathrm{link}})\) 建边，符号只用于 donor scoring；负交互不等于硬约束。类型、接口、权限、调用依赖才是硬约束。

演化参数方案：训练任务上 irace 离线配置；discounted-UCB/AOS 在线调整动作使用倾向；统计门禁固定。AOS 不是独立创新，若不优于离线调参固定策略则删除。主算法 categorical GOM，不用 DE 专属 F/CR。

最新算法文档：14_FORMAL_ALGORITHM_DESIGN_V1.md。下一步先实现 Phase 0 合成真值模拟器和基线：4 binary slots、正负交互、task-family sign flip、三阶模型失配、Bernoulli/Beta 噪声、全合法和受约束空间；实现 TCAIL 及 CI-GOM 的最小模拟版本；做同预算恢复、搜索和参数控制消融。先不调用真实 LLM、不读其他 GitHub 仓库。每轮更新唯一仓库和接班提示词，严格区分设计、实现、实验结果。


## 17. 算法规格 V1 的统计与执行细节修订（2026-11-02）

14_FORMAL_ALGORITHM_DESIGN_V1.md 已进一步修订：
- Group-ARD 给出组精度的 Type-II ML / EM 更新公式；
- CI-GOM 每个 target 可运行多个 proposal，每个 proposal 只分配一个 operator arm，确保信用分配清晰；
- 交互图按该 proposal 的任务上下文生成；
- 序贯接受采用跨 proposal index 与 proposal 内 look index 的双层 alpha spending，避免多次 offspring 检验造成累计错误率膨胀。

公式：
\[
\alpha_k=\frac{6\alpha_{\mathrm{total}}}{\pi^2k^2},\quad
\alpha_{k,n}=\frac{6\alpha_k}{\pi^2n^2}.
\]
假设 task-block differences 有界且独立，或使用相应 martingale confidence bound；相关任务必须按 task family/cluster 聚合。

下一轮实施前需复核这套置信序列的统计假设与实际任务采样机制，不能仅把公式复制进代码。


## 18. 最新研究执行指令：逐项验证创新点，暂停大论文写作（2026-11-02）

**本节覆盖所有更早的 handoff 指令。若旧内容要求同时实现 TCAIL 和 CI-GOM，以本节为准。**

用户最新决定：先不写硕士大论文正文，也不先把三个创新点包装成完整故事；要依次验证每一个创新点是否成立。

### 唯一权威协议
- 15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md

### 当前研究顺序
1. **当前只做 TCAIL（创新点一）**：先规格/统计审计，再实现 Phase 0 真值模拟器与强基线，做 null、正/负交互、任务条件交互、三阶失配、受约束不可识别性、多 seeds 同预算实验、消融和独立复审。合成实验通过后仍需真实 Agent 场景验证。Gate-1 完整通过后才能进入创新点二。
2. **CI-GOM（创新点二）暂时冻结**：保留算法规格，不启动完整实现。Gate-1 通过后先做 oracle-linkage 上界实验，再做 contract repair、donor、sequential acceptance 消融和 learned-linkage 端到端同预算比较。Gate-2 通过后才能进入创新点三。
3. **跨任务迁移（创新点三）暂时冻结**：只有 Gate-2 通过后才研究。必须先证明跨任务确有可迁移交互，并且选择性迁移优于 from-scratch 与 direct transfer；否则删除第三项，允许毕业论文以两个扎实创新点完成。

### 论文写作状态
- 暂停硕士大论文正文撰写；
- 暂不撰写声称创新点已成立的论文稿；
- 研究记录、实验协议、文献审计、代码和 Gate 报告继续维护；
- 开题材料后续根据真实研究证据组织，未验证内容只能写成拟研究候选，不得伪装成结果。

### 研究治理
- 只允许读取和维护 yujian777555/kaitibaogao；严禁读取其他 GitHub 仓库。
- 不调用真实 LLM，直到 TCAIL 合成验证通过且真实 Agent protocol 审查完成。
- 每种方法同 rollout budget，并公平分配调参预算；训练/验证/测试严格隔离。
- 不得以单个 toy landscape、单次 seed 或弱随机基线作为创新成立证据。
- 每轮更新 README、DECISION_LOG、FEASIBILITY_AUDIT、实验协议和本 handoff。
- 明确区分 SPECIFIED、IMPLEMENTED、SYNTHETICALLY_VALIDATED、AGENT_VALIDATED、GATE_PASS。

### 下一轮可直接复制的接班提示词

你是我的河北工业大学计算机技术硕士开题研究助手，研究主线为 Evolutionary Computation for AI Agents。唯一允许读取和维护的 GitHub 仓库是 yujian777555/kaitibaogao，严禁读取任何其他 GitHub 仓库或混用其他项目。

用户明确要求：暂时不要写硕士大论文正文，而是依次验证每个候选创新点。最多目标为 2–3 个独立创新点/小论文，但不得为了凑够三项降低标准。当前执行顺序以 15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md 为最高权威。

**当前只执行创新点一 TCAIL。** 先独立审查 14_FORMAL_ALGORITHM_DESIGN_V1.md 的数学、统计、可识别性、噪声与后验校准假设；发现错误先修规格。然后实现 4 binary slots / 16 configurations 的合成 landscape、真值 oracle、random legal design、D-optimal/fractional design、main-effects、pairwise OLS、sparse Group-ARD fixed design、TCAIL active interaction-only IG。测试 null、positive/negative interactions、task-family sign flip、three-way misspecification、Bernoulli/Beta noise、fully legal 与 constrained non-identifiable spaces。多 seeds、多 landscape、同 rollout budget，报告 contrast RMSE、edge AUPRC/F1、方向准确率、posterior coverage/calibration、held-out prediction、budget curves、false edges 和 abstention accuracy。做 task conditioning、Group-ARD、active IG、identifiability gate、calibration/abstention 消融。先不调用真实 LLM。

TCAIL 合成 Gate 通过也不等于论文成立；之后必须选择可信、可复现的真实 Agent 环境验证。Gate-1 完整通过之前，不实现完整 CI-GOM。

CI-GOM 规格保留但冻结；Gate-1 后先做 oracle-linkage 上界、contract-aware repair、donor、sequential acceptance 消融，再做 learned-linkage 端到端同预算比较。Gate-2 通过后才启动第三项跨任务交互迁移。第三项必须证明存在可迁移结构，且 selective transfer 优于 from-scratch 和 direct transfer；否则删除第三项，允许最后只有两个创新点。

暂停大论文正文写作。每轮维护唯一仓库、更新状态和接班提示词；严格区分设计、实现、合成验证、真实 Agent 验证和 Gate 通过。不能把工程 PASS 写成算法 PASS，不能只用 toy 环境或弱基线宣称创新。


## 19. TCAIL 首轮规格审计完成：REQUEST REVISION（2026-11-02）

本节覆盖更早 handoff 中将 TCAIL 标记为可直接进入 Phase 0 的表述。

### 审计记录
- 新增：16_TCAIL_SPECIFICATION_AUDIT_R1.md
- 审计对象：14_FORMAL_ALGORITHM_DESIGN_V1.md 的 TCAIL 部分
- 结论：REQUEST REVISION / IMPLEMENTATION BLOCKED
- 当前状态：TCAIL_SPECIFICATION_REVISION_REQUIRED
- 尚未编码、尚未运行实验、尚无性能结果、Gate-1 未通过。

### 必须先修复的七项阻塞
1. pairwise contrast 必须显式依赖背景槽位，并定义 reference distribution 下的边 estimand；同时报告背景异质性。
2. 区分 PENDING_SUPPORT、IDENTIFIABLE、STRUCTURALLY_NOT_IDENTIFIABLE；不能把当前样本不足直接标为永久不可识别。
3. Gaussian、Bernoulli logistic、Beta reward 的 likelihood 与 posterior / expected-information update 必须分别一致。
4. edge selection 增加明确的 Bayesian FDR 或有理论依据的多重比较控制。
5. interaction-only IG 本质上与 Bayesian D-optimal 子空间设计相连；必须增加严格匹配的 D-optimal 强基线，重新审查独立新颖性。
6. 4-slot / 16-config 只用于 debug；新增 8/10/12-slot scaling landscape。
7. 区分 pairwise marginal interaction、background-conditional interaction 和高阶模型预测失配；三阶项不意味着所有 pairwise edge 都必须 abstain。

### 下一轮唯一任务
只在 yujian777555/kaitibaogao 内工作。先按 16_TCAIL_SPECIFICATION_AUDIT_R1.md 修订 14_FORMAL_ALGORITHM_DESIGN_V1.md 的 TCAIL 部分；然后由独立审查重新检查数学、统计和 novelty baseline。规格复审通过之前，不实现正式 Phase 0，不调用真实 LLM，不启动 CI-GOM，不启动第三项，不写硕士大论文正文。

### 接班提示词的最新补充
先读 15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md、16_TCAIL_SPECIFICATION_AUDIT_R1.md、14_FORMAL_ALGORITHM_DESIGN_V1.md。当前只做 TCAIL 规格修订。注意 Bayesian D-optimal 对照、背景平均 pair estimand、structural vs sample identifiability、Bernoulli/Beta expected information、Bayesian FDR 和大规模 synthetic landscapes。不要把 REQUEST REVISION 写成算法已失败，也不要把算法设计写成已验证创新；这是实现前规格审计发现的可修订缺口。


## 21. TCAIL V2 纸面修订与首轮新颖性审查完成（2026-11-02）

本节覆盖此前 handoff 中要求按 V1 直接进入 Phase 0 的旧指令。

### 新增文件
- 17_TCAIL_FORMAL_SPECIFICATION_V2.md：TCAIL 修订规格；
- 18_TCAIL_RELATED_WORK_AUDIT_R1.md：首轮相关工作与新颖性审查。

14_FORMAL_ALGORITHM_DESIGN_V1.md 已加状态说明：其 TCAIL 部分由 V2 替代；CI-GOM 部分保留为历史规格且继续冻结。

### 当前状态
- V1 审计结论仍是 REQUEST REVISION；
- V2 已完成纸面修订，但尚未独立复审；
- 没有代码实现、没有正式实验、没有性能结果、没有 Gate-1 PASS；
- TCAIL 状态：REVISED_SPEC_PENDING_INDEPENDENT_REVIEW；
- CI-GOM 继续冻结；第三项迁移继续冻结；大论文正文继续暂停。

### V2 关键修订
1. Pairwise contrast 显式依赖其他槽位背景，并以预先指定 reference distribution 定义平均边效应；
2. 同时报告背景异质性和共同支持质量；
3. 区分 link-scale interaction 与 reward-scale performance contrast；
4. 区分 IDENTIFIABLE、PENDING_SUPPORT、STRUCTURALLY_NOT_IDENTIFIABLE、STRUCTURAL_STATUS_UNCERTIFIED；
5. Gaussian、Bernoulli、Beta 似然分别定义；
6. 非 Gaussian Group-ARD 采用 Laplace approximate marginal likelihood，不复用 Gaussian 闭式更新；
7. Bayesian FDR 全局控制；
8. interaction-only IG 明确作为 Bayesian D-optimal 对照，不再作为新颖点；
9. edge-decision risk reduction 作为待验证候选，不能先验宣称新颖；
10. 4-slot 仅 debug，增加 8/10/12-slot scaling；
11. 增加 null、additive-only、three-way-only 和 mixed-order 场景；
12. 明确 TCAIL 本身不是完整 EC 算法，其对 EC 搜索的实际价值必须后续验证。

### 首轮相关工作审查发现
- Lewis & Dean (2001)：interaction group screening；
- Singh & Stufken (2024)：GDS-ARM；
- Huan et al. (2024)：Bayesian / sequential OED；
- Hainy et al. (2022)：decision-theoretic Bayesian model discrimination；
- Chen et al. (2008)：Bayesian FDR interaction selection；
- Lauziere et al. (2026)：Prompt component regression；
- Liu (2026)：Agent scaffolding 32-configuration factorial analysis，且其特定设置中 pairwise model 留出表现弱于 main-effects model；
- Radwan et al. (2026)：Harness-aware evaluation；
- Zhao et al. (2026)：预算约束 Agent harness 进化优化。

新颖性未成立。上述工作意味着不能把“发现组件交互”、pairwise regression、Bayesian IG/D-optimal、Bayesian FDR 或一般 Agent harness 搜索本身作为创新。TCAIL 只能通过受约束、随机、任务异质的 Agent 配置空间中的同预算强基线结果证明额外价值。

### EC 主线约束
TCAIL 是统计建模和主动实验设计模块，不是完整 EC 算法。它可以作为后续 CI-GOM 的交互结构输入，但只有当其结构信息被证明能改善演化 linkage/mixing/search，才能闭合毕业论文 EC 主线。不能仅凭未来计划把它写成已成立的 EC 创新。

### 下一轮唯一任务
独立复审 17_TCAIL_FORMAL_SPECIFICATION_V2.md。重点检查：
- link-scale estimand 与 reference-background averaging 是否一致；
- Beta Fisher information 推导；
- Gaussian/GLM posterior 与 Group-ARD evidence；
- row-space estimability 与四格共同支持的边界；
- BFDR 的全局检验族定义；
- edge-decision risk acquisition 是否可计算且目标明确；
- budget、task-block、cluster bootstrap 是否一致；
- 8/10/12-slot 实验统计单位和样本量；
- 与 OED、group screening、Agent interaction work 的真实差异。

如果 V2 仍有数学错误，继续修规格；如果数学正确但新颖性不成立，修改研究主张或 NO-GO。不得为了看起来新而添加未经论证的复杂模块。规格复审通过之前，不实现代码、不跑正式实验、不调用真实 LLM。

### 最新接班提示词
你是我的硕士研究 Planner。唯一仓库 yujian777555/kaitibaogao。当前先不写大论文，按创新点逐项验证。当前只做 TCAIL，CI-GOM 和迁移冻结。

请先读 15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md、16_TCAIL_SPECIFICATION_AUDIT_R1.md、17_TCAIL_FORMAL_SPECIFICATION_V2.md、18_TCAIL_RELATED_WORK_AUDIT_R1.md 和本 handoff。

V1 的 TCAIL 已被 V2 替代。V2 已修订但尚未独立复审。请独立检查所有数学定义、Beta Fisher information、Gaussian/GLM posterior、ARD evidence、identifiability row-space test、reference distribution、BFDR 和 acquisition。不得直接实现或跑正式实验。

特别审查 EC 主线定位：TCAIL 是统计/实验设计模块，不是完整 EC 算法；不能将其独立写成 EC 创新，除非证明它对演化搜索有独立贡献。首轮相关工作已发现 interaction group screening、GDS-ARM、Bayesian OED、Bayesian FDR、Agent 组件全因子/回归、harness-aware evaluation、预算约束 Agent harness 进化优化均有先例。新颖性未成立。只有独立复审通过后才能进入代码；合成通过后仍必须做真实 Agent 验证。

## 22. TCAIL V2 第二轮复核 REQUEST CHANGES（2026-11-02）

新增：
- 19_TCAIL_V2_SECOND_PASS_REVIEW_R1.md：第二轮数学/统计复核；
- 17_TCAIL_FORMAL_SPECIFICATION_V2.md 第 12 节：V2.1 澄清。

### 第二轮结论
Beta Fisher information、Gaussian posterior update、row-space estimability 和 Bayesian FDR 的基本数学形式通过纸面检查。但 V2 仍有以下实现前缺口：
1. Pairwise-only model 在自适应非均匀设计下可能把遗漏高阶效应投影到 pairwise coefficients；M3 必须进入边结论敏感性门禁；
2. 显式构造 reference-standardized contrast vector l_e；
3. 连续 context 的全局 BFDR 检验族需固定有限 anchor set；
4. edge-decision risk acquisition 需明确 posterior predictive MC、posterior refit、MCSE 和 common random numbers；
5. full-factorial budget denominator 需按 legal configs × anchors × task-block repeats 定义。

V2.1 澄清已写入规格，但还没有独立复审。没有代码、没有实验、没有性能结果、没有 Gate-1 PASS。

### 下一轮唯一任务
只复审 17_TCAIL_FORMAL_SPECIFICATION_V2.md 的 V2.1 内容与 19_TCAIL_V2_SECOND_PASS_REVIEW_R1.md。重点检查新增 M2/M3 gate、l_e 构造、anchor BFDR、risk acquisition MC 和 budget denominator 是否真正闭合。不要实现、不要启动 API、不要跑正式 Phase 0。

### 最新接班提示词
你是我的硕士研究 Planner，唯一仓库 yujian777555/kaitibaogao。先读 15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md、16_TCAIL_SPECIFICATION_AUDIT_R1.md、17_TCAIL_FORMAL_SPECIFICATION_V2.md、18_TCAIL_RELATED_WORK_AUDIT_R1.md、19_TCAIL_V2_SECOND_PASS_REVIEW_R1.md 和本 handoff。

当前只做 TCAIL V2.1 独立复审。V1 已被 V2 替代；V2 第二轮结论 REQUEST CHANGES，V2.1 澄清刚写入但尚未复审。检查所有数学、统计和实现定义，尤其 M2/M3 model-order sensitivity、reference-standardized l_e、有限 context anchors 的 BFDR、edge-risk acquisition MC 估计、task-block 预算口径。若仍有问题继续修规格；通过前不实现或跑正式实验。

同时牢记：TCAIL 是统计/实验设计模块，不是完整 EC 算法。它是否能成为毕业论文创新，必须证明其输出对后续演化搜索有独立作用。CI-GOM 和迁移仍冻结，大论文正文仍暂停。

## 23. 固定仓库维护要求（2026-11-02）

用户明确要求后续每轮都维护本仓库。具体流程已独立写入 REPOSITORY_MAINTENANCE_POLICY.md；它是长期工作约束，不是一次性提醒。

每轮开始先核对远端 main HEAD 并阅读项目状态、决策日志、handoff 和当前创新点规格；每轮结束必须更新研究记录、README/状态、必要时的决策日志，以及 SESSION_HANDOFF 中的完整接班提示词；提交推送后必须重新核验远端 HEAD 和关键文件。未成功推送或核验时如实报告。

项目隔离：本仓库只维护 kaitibaogao 毕业论文开题研究，不得混入 openissue、agentfotagent、GLEPPO 等独立项目的研究内容。

当前研究状态和门禁以本 handoff 最新部分及 REPOSITORY_MAINTENANCE_POLICY.md 为准：只做 TCAIL V2.1 独立规格复审；CI-GOM 和第三项迁移冻结；规格复审通过前不实现、不跑正式 Phase 0、不调用真实 LLM。

### 下轮 Planner 提示词附加要求

除完成当前 TCAIL V2.1 独立复审外，必须遵守 REPOSITORY_MAINTENANCE_POLICY.md：开始前读取远端状态，结束时更新研究记录、决策日志、README/状态和 SESSION_HANDOFF，写入下一轮完整接班提示词，推送并核验远端。

## 24. TCAIL V2.1 第三轮独立规格复审：REQUEST CHANGES（2026-11-02）

### 本轮交付

- 新增：20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md。
- README 已登记本轮状态。
- 05_DECISION_LOG.md 新增 D-028。
- 本节覆盖此前“V2.1 澄清已闭合、可进入实现前复审”的乐观表述；当前结论仍为 REQUEST CHANGES。

### 复审结论

**TCAIL V2.1：REQUEST CHANGES / IMPLEMENTATION BLOCKED。**

通过的纸面检查：
- \(l_e\) 在固定线性 predictor basis 下正确；
- 固定 Beta concentration \(\kappa\) 的 Fisher information 正确；
- 线性 predictor contrast 的 row-space estimability 判据正确；
- posterior local null probability 校准且检验族固定时，BFDR 基本公式正确；
- V2.1 已补上 posterior predictive MC、posterior refit、MCSE、common random numbers 和预算计数框架。

仍未闭合的阻塞：
1. 平均有符号交互可能在不同背景间抵消；当前 H0 不是通用 linkage 检验，背景异质性没有进入 BFDR/edge risk。
2. M2/M3 gate 未写入正式伪代码/状态机；M3 只包含三阶项，不能排除四阶以上失配；strong-heredity 与 three-way-only 真值场景的兼容性不清；M2/M3 最终 posterior/BFDR 规则未定义。
3. per-edge Bayes classification risk acquisition 与全局 BFDR 最终选择不一致。
4. task-block ID、跨配置配对、随机种子、任务内相关、随机效应和 cluster posterior/calibration 没有完整定义。
5. 未知 Beta \(\kappa\) 的联合 nuisance uncertainty 未进入 Fisher/acquisition；Gaussian 方差也要明确处理。
6. identifiability 要按模型 basis × anchor 构造合法/观测矩阵，并区分结构可识别与 GLM practical weak identification；低共同支持 abstention 未定义。
7. BFDR 检验族的 task-family × pair 与 pair × anchor 索引不一致。
8. full-factorial task-block 计数只有在等成本协议下才等价于 rollout-equivalent budget。

TCAIL 新颖性和 EC 核心贡献均未成立。当前没有代码、没有实验、没有性能结果、没有 Gate-1 PASS。本轮 REQUEST CHANGES 不是算法实验失败。

### 当前唯一任务

只修订 17_TCAIL_FORMAL_SPECIFICATION_V2.md，不编码、不跑正式 Phase 0、不调用真实 LLM。按 20 号报告顺序处理：

1. 固定边 estimand：区分平均有符号效应与适用于 EC linkage 的背景条件化非加性强度；相应定义 H0/H1、BFDR 和输出图。
2. 闭合 M2/M3：定义 strong/weak heredity，处理 4 阶及以上模型失配，明确 model-order status、posterior 合并/保守规则，并将敏感性门禁写入伪代码。
3. 使 acquisition 风险与最终 BFDR 决策一致；若只是 surrogate，必须改名并验证其代理价值。
4. 定义 task-block 配对执行、CRN、任务内相关模型和 cluster posterior/calibration。
5. 明确 Beta \(\kappa\) 与 Gaussian \(\sigma^2\) 的冻结或联合 nuisance 处理。
6. 按 model basis × anchor 定义 legal/observed design matrix；区分 structural identifiability 与 practical weak identification；定义低共同支持 abstention。
7. 统一 BFDR 检验族索引和 context-indexed graph 输出。
8. 明确等成本 task-block 假设或加权 rollout-equivalent budget。

### 冻结项

- CI-GOM：继续冻结，不启动完整实现。
- 第三项跨任务迁移：继续冻结。
- 真实 LLM：禁止调用。
- 正式 Phase 0：规格复审通过前禁止启动。
- 硕士大论文正文和声称创新成立的论文稿：继续暂停。

### 下一会话完整接班提示词

你是我的河北工业大学计算机技术硕士开题研究 Planner。研究主线为 Evolutionary Computation for AI Agents。**唯一允许读取和维护的 GitHub 仓库是 yujian777555/kaitibaogao；严禁读取任何其他 GitHub 仓库，严禁混入 openissue、agentfotagent、GLEPPO 等项目内容。**

开始前必须核对本仓库远端 main 最新状态，并阅读 README.md、REPOSITORY_MAINTENANCE_POLICY.md、05_DECISION_LOG.md、SESSION_HANDOFF.md、15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md、16_TCAIL_SPECIFICATION_AUDIT_R1.md、17_TCAIL_FORMAL_SPECIFICATION_V2.md、18_TCAIL_RELATED_WORK_AUDIT_R1.md、19_TCAIL_V2_SECOND_PASS_REVIEW_R1.md 和 20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md。

当前唯一研究任务是修订 TCAIL V2.1 规格。第三轮独立复审结论为 REQUEST CHANGES / IMPLEMENTATION BLOCKED。已经通过的项目包括：固定线性 predictor basis 下的 reference-standardized contrast vector、固定 \(\kappa\) 的 Beta Fisher information、线性 contrast row-space 判据，以及校准 posterior/固定检验族条件下的 BFDR 基本公式。不要重复把这些已通过项误判为错误。

必须解决以下阻塞：
1. 当前平均有符号 pairwise contrast 可能因不同背景下符号抵消而漏掉有意义的 linkage。明确选择 mean-effect graph 还是 context-dependent linkage graph；若服务于 EC linkage，需定义背景条件化非加性强度及其 H0/H1、BFDR 和输出。
2. M2/M3 敏感性门禁必须进入算法伪代码和状态机。M3 仅含三阶项，不能排除四阶及以上失配；strong-heredity 可能与 three-way-only 场景冲突；明确模型间最终 posterior/local-null/BFDR 决策规则。
3. 当前逐边 Bayes classification risk 与全局 BFDR 最终边选择不一致。定义 BFDR-constrained decision risk，或将其降级为 surrogate acquisition 并验证代理价值。
4. 明确 task-block ID、相同任务跨配置配对、随机种子/CRN、任务内相关、random effect 或 paired contrast，以及 cluster bootstrap/bagged posterior 的具体统计方案。候选设计 d 要说明是否包含 task-block。
5. Beta \(\kappa\) 未知时采用联合 nuisance posterior/Fisher 处理，或由独立 pilot 预先冻结；Gaussian \(\sigma^2\) 同样明确。
6. 按 model basis × anchor 构造完整 legal/observed design matrix；对 M2/M3 分别做 row-space 检验；区分 structural identifiability 与 GLM practical weak identification；定义低共同支持 abstention。
7. 统一 BFDR test family 为 pair × anchor 或其他明确索引，说明 context-indexed graph 输出、MODEL_ORDER_SENSITIVE 边如何处理。
8. 明确 task-block 等成本假设；否则用加权成本定义 full-factorial reference budget。

TCAIL 仍是统计建模/主动实验设计模块，不是完整 EC 算法。普通 Group-ARD、Bayesian OED、BFDR、decision-theoretic acquisition 不能单独宣称创新。必须保留“是否改善 GOM linkage/mixing/search”的下游证据要求。新颖性未成立，不要提前写成论文创新点。

**严格禁止：** 当前不实现代码、不运行正式 Phase 0、不调用真实 LLM、不启动 CI-GOM、不启动第三项迁移、不写硕士大论文正文。规格修订完成后，先交独立复审；不得自己修订后自行宣布通过。

每轮结束必须更新本仓库的研究报告、README、05_DECISION_LOG 和 SESSION_HANDOFF；检查旧规格与新规格状态一致；提交到 main，重新读取远端 main HEAD 和关键文件核验。未推送或未核验成功时如实报告。


## 25. GOMEA linkage 接口补充审计与 B1 修订提案（2026-11-02）

### 本轮交付

- 新增 21_GOMEA_LINKAGE_AND_NOISY_INTERACTION_RELATED_WORK_AUDIT_R1.md；
- 新增 22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md（B1 proposal only，未并入权威规格）；
- 文献总表 02_LITERATURE_REGISTER.md 新增 P125–P132；
- README、05_DECISION_LOG（D-029）、15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL 已更新；
- 14_FORMAL_ALGORITHM_DESIGN_V1.md 新增 Addendum 18，明确旧 CI-GOM Section 10 为 historical/frozen，不得按原样实现。

### 关键研究修正

GOMEA linkage 并非只有 SLL-MI；fitness-based linkage 已有 RV-GOMEA 工作，conditional FOS / maximum-clique linkage、DLED/cDLED、Linkage Kernels 也已覆盖局部/多结构依赖。噪声环境下 linkage decomposition 也已有 LMM、ALI/AIM。

因此：
- 不得宣称 fitness-based linkage 是新概念；
- 不得把平均有符号 interaction 直接当作通用 linkage edge；
- 不得把 VIG 直接称为 FOS；
- 不得忽略当前 parent 的局部结构；
- 不得忽略高阶/重叠依赖和现有 conditional FOS 基线。

### 22 号提案的核心

- 实际 objective utility scale 上的条件四格差分；
- global RMS interaction energy 仅作 task-conditioned 总体摘要；
- current-parent/task-conditioned local posterior linkage \(q_{ij}(x,z)\)；
- 输出 local weighted VIG，再通过固定 LT / conditional FOS builder 形成 FOS。

这可能形成的候选差异是：随机昂贵 Agent rollout、任务异质、合法配置约束、task-block 配对、posterior uncertainty 和主动预算的联合处理。但 LMM/ALI 已覆盖一般噪声 linkage，cDLED 已覆盖局部 conditional linkage，必须做直接强基线比较。

### 当前状态

**TCAIL 仍 HOLD / IMPLEMENTATION BLOCKED。** 21 号报告是相关工作审计；22 号是 B1 修订提案，不是已通过规格。B2–B8 仍然未解决。没有代码、没有实验、没有 Gate-1 PASS。

14 号文件中的 CI-GOM Section 10 已明确标记为 historical/frozen，不允许按原样实现。CI-GOM 和第三项迁移继续冻结。

### 下一轮唯一任务

独立复审 22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md。重点核查：
1. RMS interaction energy 的数学解释与边界；
2. local posterior linkage 与 DLED/cDLED/FBL 的机制差异；
3. objective-scale contrast 与真实 Agent fitness/GOM acceptance 的一致性；
4. local weighted VIG 到 LT/conditional FOS 的接口；
5. 是否存在可证伪的 EC 搜索收益和公平强基线。

如果 22 号提案的差异仅是已知 FBL/DLED 的贝叶斯化包装，应 NO-GO 或继续收窄，而不是强行命名新算法。

### 下一会话完整接班提示词

你是我的河北工业大学计算机技术硕士开题研究 Planner。唯一仓库为 yujian777555/kaitibaogao；不得读取其他用户 GitHub 仓库，不得混入 openissue、agentfotagent、GLEPPO 等项目。

开始前核对远端 main HEAD，并阅读 README.md、REPOSITORY_MAINTENANCE_POLICY.md、02_LITERATURE_REGISTER.md、05_DECISION_LOG.md、SESSION_HANDOFF.md、15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md、17_TCAIL_FORMAL_SPECIFICATION_V2.md、20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md、21_GOMEA_LINKAGE_AND_NOISY_INTERACTION_RELATED_WORK_AUDIT_R1.md、22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md，以及 14_FORMAL_ALGORITHM_DESIGN_V1.md Addendum 18。

当前唯一任务：独立复审 22 号 B1 修订提案，不编码、不跑正式 Phase 0、不调用真实 LLM。

必须审查：
- GOMEA SLL-MI 与 fitness-based linkage 的区别；
- FBL（Olieman 2021）、Andreadis 2024 fitness-based conditional linkage、DLED/cDLED、LMM、ALI/AIM、Linkage Kernels、Tinós 2026 在线 interaction learning；
- objective-scale conditional finite difference；
- global RMS interaction energy 与 local parent/task posterior linkage 的分工；
- local weighted VIG 与 FOS 的区别，以及固定 FOS builder 的公平比较；
- 是否能在同等 rollout budget 下优于 FBL/cDLED/LMM/ALI 和在线副产物基线。

不要把 RMS 平方平均本身包装成新颖算子。若 22 号提案只是在已有 FBL/DLED 上加 Bayesian posterior，而没有独立的任务异质/随机 Agent/预算收益，应建议 NO-GO 或继续收窄。

B2–B8 仍未解决；TCAIL 仍 HOLD。CI-GOM 与第三项迁移继续冻结。每轮结束按 REPOSITORY_MAINTENANCE_POLICY.md 更新报告、README、决策日志和 handoff，推送并复核远端 main。


## 26. 开题报告初稿 V0.1 完成（2026-11-02）

### 本轮交付

- 新增 \`23_OPENING_REPORT_DRAFT_V0_1.md\`：完整开题报告初稿，按学校模板组织；
- 初稿题目工作稿：《面向大语言模型智能体的交互感知演化优化方法研究》；
- 正文约 22,100 个非空白字符（不含参考文献），超过硕士模板 6,000 字要求的初稿目标；
- 列出 50 篇参考文献，全部为外文文献，近五年文献比例超过模板下限；正式提交前仍需逐条核验完整著录信息和学校格式；
- README、04_OPENING_REPORT_PLAN、05_DECISION_LOG 已更新。

### 报告的研究结构

1. 研究内容一：任务条件化 Agent 组件交互结构估计（TCAIL 候选）；
2. 研究内容二：交互结构驱动的 Agent 约束最优混合演化（CI-GOM 候选）；
3. 研究内容三：任务分布变化下交互结构迁移（条件性扩展，不预先承诺）。

演化计算参数策略写入报告：训练任务上 irace 离线调参；discounted-UCB/AOS 作为在线动作控制候选；统计门禁和硬约束预先固定。若在线控制不优于离线调参固定策略，则删除。

### 重要状态

- TCAIL 仍未通过独立规格复审；B1 linkage 接口修订提案仍待独立复审；
- CI-GOM 尚未实现或实验；
- 没有正式 Phase 0 或真实 Agent 实验结果；
- 初稿使用“拟研究/预期创新”措辞，不把算法设计当作已验证成果；
- 没有混入其他独立项目成果。

### 下一步优先级

当前用户要求先完成开题报告初版。下一轮应优先根据导师反馈修改报告，而不是继续扩展算法规格。需要补齐导师姓名、学号、姓名、正式答辩日期；核对国内研究现状的具体来源；逐条复核参考文献的完整作者、页码、DOI 和 GB/T 7714 格式；按学校模板制作 Word 正式排版稿。

### 下一会话接班提示词

你是我的河北工业大学计算机技术硕士开题报告助手。唯一研究仓库是 \`yujian777555/kaitibaogao\`，不得读取或混用任何其他 GitHub 仓库或独立项目。

本轮用户明确要求：先完成开题报告初版。请先核对远端 main HEAD，阅读 README.md、04_OPENING_REPORT_PLAN.md、05_DECISION_LOG.md、SESSION_HANDOFF.md、23_OPENING_REPORT_DRAFT_V0_1.md、17_TCAIL_FORMAL_SPECIFICATION_V2.md、20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md、21_GOMEA_LINKAGE_AND_NOISY_INTERACTION_RELATED_WORK_AUDIT_R1.md 和 22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md。

当前开题报告 V0.1 已完成，工作题目为《面向大语言模型智能体的交互感知演化优化方法研究》。研究主线是演化计算赋能 Agent。报告结构为两个核心研究内容（任务条件化组件交互估计；交互结构驱动的约束最优混合演化）和一个条件性第三方向（跨任务交互结构迁移）。参数方案为 irace 离线调参 + discounted-UCB/AOS 在线控制候选 + 统计门禁固定。

重要真实性边界：TCAIL 独立规格复审仍 REQUEST CHANGES；B1 linkage 接口提案待独立复审；CI-GOM 尚未实现/实验；第三方向未通过独立新颖性审查；当前课题没有正式 Phase 0 或真实 Agent 实验结果。报告必须继续使用“拟研究/预期创新”，不能写成已验证算法或已发表成果。

下一步优先做报告修订：
1. 根据导师意见调整题目和研究内容；
2. 核对 44 篇参考文献的作者、出版信息、DOI 和 GB/T 7714 格式；
3. 补充有明确来源的国内研究成果，避免只按国际论文列表写现状；
4. 核对正文统计字数、外文和近五年文献比例；
5. 根据学校正式时间表修订研究进度；
6. 制作 A4、宋体小四、1.5 倍行距的 Word 版。

除非用户要求，不要自动切回算法开发；先把开题报告修到可以给导师审阅。


## 27. 第七轮：开题报告 V0.2 文献与国内研究修订（2026-11-03）

### 本轮交付

- 新增 `24_REFERENCE_AUDIT_AND_DOMESTIC_RESEARCH_R1.md`；
- 新增 `25_OPENING_REPORT_DRAFT_V0_2.md`，原 V0.1 保留；
- 参考文献扩展至 61 条，正文引用编号 [1]–[61] 全部匹配；
- 补充国内 Agent 综述、教学 Agent、垂直领域 Agent、电力仿真技能库、MAESD、BIOME；
- 补入 AHE、SkillFlow、ShapleyFlow、FusionFlow 并更新强基线；
- 修正 V0.1 的 43/50 统计矛盾、[44]–[50] 错位、ARTEMIS 重复列举及若干书目元数据。

### 关键结论

- [50] Evolving Excellence 是 ARTEMIS 论文，正文写 ARTEMIS[50] 对应正确；只删除重复列举。
- ShapleyFlow 已做固定 workflow 组件升级的全组合 Shapley 交互归因；FusionFlow 已做 workflow fusion；AHE/SkillFlow 已做 harness/skill 演进。这些工作显著提高创新门槛。
- 普通组件交互估计 NO-GO；修订 TCAIL 继续 HOLD；CI-GOM 冻结；第三项迁移冻结。
- 61 条参考文献已完成编号/正文引用一致性检查，但并非全部完成最终 GB/T 7714 全量审计。
- TCAIL V2.1 状态不变：REQUEST CHANGES / IMPLEMENTATION BLOCKED；22 号接口修订提案仍待独立复审。
- 本轮无算法实现、无 Phase 0、无真实 LLM 调用、无新 Gate PASS。

### 下一轮唯一优先任务

先完成剩余参考文献逐条 GB/T 7714 审计和 Word V0.2 与 Markdown V0.2 的一致性核对；若用户提供导师反馈，优先按导师意见修订题目、研究内容和创新点。个人信息、正式开题日期和学院时间表仍待用户补充。不得擅自填写。

### 可直接复制的接班提示词

你是我的河北工业大学计算机技术硕士开题报告助手。唯一允许读取和维护的 GitHub 仓库是 `yujian777555/kaitibaogao`，严禁读取或混用我的其他仓库。

先核验 main 最新 HEAD，再读取 README.md、04_OPENING_REPORT_PLAN.md、05_DECISION_LOG.md、SESSION_HANDOFF.md、24_REFERENCE_AUDIT_AND_DOMESTIC_RESEARCH_R1.md、25_OPENING_REPORT_DRAFT_V0_2.md、02_LITERATURE_REGISTER.md、03_MECHANISM_COMPARISON.md、11_INNOVATION_FEASIBILITY_AUDIT.md，以及 TCAIL V2.1 和 22 号接口提案相关审计文件。

当前工作题目：《面向大语言模型智能体的交互感知演化优化方法研究》。研究主线是 Evolutionary Computation for AI Agents。开题报告 V0.2 已有 61 条参考文献和国内研究现状，但最终 GB/T 7714 全量审计仍未完成；Word V0.2 与 Markdown V0.2 需要核对一致性。先完成书目元数据、文献类型、页码、DOI、正文引用、近五年和外文比例复核，不能声称未核验的条目已通过。

新增直接相关工作必须纳入差异审查：AHE（arXiv:2604.25850）、SkillFlow（arXiv:2605.14089）、ShapleyFlow（Findings ACL 2026）、FusionFlow（ACL 2026）。国内来源包括 CCL 2024 Agent 综述、教学 Agent、电力仿真 Agent 技能库、垂直领域 Agent 设计、MAESD 和 BIOME。注意 BIOME 是 LLM→EC，方向与本课题相反；MAESD 优化的是蛋白质序列，不是 Agent 配置。

研究状态不得改变：普通组件交互估计 NO-GO；TCAIL V2.1 REQUEST CHANGES / IMPLEMENTATION BLOCKED；22 号 linkage 接口修订提案待独立复审；CI-GOM 和第三项迁移冻结。不要实现算法、不要启动 Phase 0、不要调用真实 LLM，除非后续用户明确授权且相关 Gate 通过。

每轮继续只维护本仓库，更新文献登记、机制比较、开题报告、决策日志和接班提示词，提交并核验远端 main。所有结论区分论文原文事实、研究推断和待验证假设。


## 28. Word V0.2 初稿生成（2026-11-03）

- 已基于 Library 中的 Word V0.1（该文件沿用学校 A4 模板）生成 `河北工业大学硕士开题报告_初稿V0.2.docx`；
- 纸张 A4，沿用原模板页边距、宋体小四正文和 1.5 倍行距；
- 已加入国内研究现状、AHE/SkillFlow/ShapleyFlow/FusionFlow，更新研究不足和基线段落；
- 参考文献 [1]–[61] 连续，共 61 条；
- Word 正文非空白字符约 22,950；参考文献外文 55/61（90.2%），中文 6/61，2022–2026 年文献 48/61（78.7%）；
- 文件已作为本轮会话附件生成供用户下载，但未提交为 GitHub 二进制文件；
- Word 与 Markdown 的主要章节和新增文献已对应，尚未完成逐段逐字比对；最终 GB/T 7714 全量审计也未完成。

下一轮先完成 Word/Markdown 一致性核对和剩余书目元数据审计；不要把“61 条连续、引用编号匹配”误称为“61 条书目全部审计通过”。


## 29. AHE 原文统计限制纳入实验协议（2026-11-03）

AHE 原文 PDF 确认主结果来自单次十轮 evolution campaign，并明确报告组件非加性交互、单组件收益不能简单相加，以及自归因对 regression 预测较弱。该结果是重要先行证据，但不能证明独立运行间可重复。后续 TCAIL/CI-GOM 实验必须采用多个随机种子、同一任务配对、相同 rollout 预算，报告运行间方差、置信区间和回归指标。详见 24_REFERENCE_AUDIT_AND_DOMESTIC_RESEARCH_R1.md 与 D-033。


## 30. 导师要求加入 RSI：V0.3 与三创新点更新（2026-11-03）

### 最新研究主线

论文题目工作版本：**《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》**。

研究范围：系统级 Agent RSI。基础 LLM 暂时冻结；Agent harness / Prompt / planning / tool routing / memory / verification-recovery / workflow 作为演化对象。LLM API 负责任务执行、轨迹分析和候选修改建议；演化计算负责种群、linkage/FOS、GOM、约束选择和跨轮次档案。

### 三个候选创新点

1. RSI 轨迹驱动的任务/父代条件化 Agent 组件交互结构学习；
2. 交互感知的类别型 Agent 约束最优混合演化；
3. 面向跨轮次 RSI 的交互记忆、结构漂移检测、linkage block 条件化迁移和保留能力约束演化。

第三项不允许退化为普通 memory/archive/performance gate。CPE、HarnessEvolve、EvolveNet、DGM、ReasoningBank、GEPA、Meta-Harness 均已覆盖相邻机制；2026-10-19 的 task-free continual study 还发现 similarity retrieval collision，2026-11-02 的 coding harness study 发现 verification/workflow/budget conflicts。算法不得直接读取 task-family labels 或 block boundaries。

### 本轮文件

- `26_RSI_THREE_INNOVATION_RESEARCH_DESIGN_R1.md`
- `27_OPENING_REPORT_DRAFT_V0_3_RSI.md`（RSI 版开题报告初稿，68 条参考文献）
- `28_RSI_CONTINUAL_RESEARCH_AUDIT_R1.md`
- 文献登记新增 P143–P149，机制比较、可行性、决策日志和本文件均需同步。

### 研究状态与禁止事项

- TCAIL V2.1：REQUEST CHANGES / IMPLEMENTATION BLOCKED；
- 22 号 local-linkage/FOS 接口：待独立复审；
- CI-GOM：未实现、未实验；
- IMCE-RSI 第三项：研究候选，无正式算法规格；
- 无本课题 Phase 0、无真实 LLM API 实验、无 GPU 训练；
- 用户偏好 DeepSeek-Flash；不得改用 DeepSeek-V4-Pro。

### 下一轮优先任务

1. 完成 V0.3 Word 版，沿用学校原始模板；逐段核对 Word 与 Markdown；
2. 审计 68 条文献元数据与 GB/T 7714 格式，不能声称全部通过；
3. 复审三个创新点的独立边界，重点审计第三项与 CPE/HarnessEvolve/EvolveNet/DGM/ReasoningBank/GEPA/Meta-Harness 的差异；
4. 设计 task-free 任务流实验协议，标签和 block boundaries 仅用于离线评估；
5. 更新本仓库 README、literature register、mechanism comparison、decision log、status 和 handoff。

### 可直接复制的接班提示词

你是我的河北工业大学计算机技术硕士开题研究 Planner。唯一允许维护的 GitHub 仓库是 `yujian777555/kaitibaogao`，严禁混用其他项目。

先核验 main 最新 HEAD，再读取 README.md、04_OPENING_REPORT_PLAN.md、05_DECISION_LOG.md、SESSION_HANDOFF.md、02_LITERATURE_REGISTER.md、03_MECHANISM_COMPARISON.md、11_INNOVATION_FEASIBILITY_AUDIT.md、26_RSI_THREE_INNOVATION_RESEARCH_DESIGN_R1.md、27_OPENING_REPORT_DRAFT_V0_3_RSI.md、28_RSI_CONTINUAL_RESEARCH_AUDIT_R1.md。

导师明确要求开题加入 RSI。论文工作题目为《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》。研究范围是冻结基础 LLM 的 Agent 系统级 RSI，演化对象为 Agent harness / Prompt / planning / tool routing / memory / verification / workflow。LLM API 执行任务和提出候选修改，演化计算负责搜索、重组、约束、选择和多轮记忆。

三个候选创新点：I. RSI 轨迹驱动的任务/父代条件化组件交互结构学习；II. 交互感知约束 GOM；III. 跨轮次交互记忆、漂移检测、linkage block 条件化迁移和能力保持约束演化。第三项必须与 DGM、CPE、HarnessEvolve、EvolveNet、ReasoningBank、GEPA、Meta-Harness 和 2026 年两篇 continual RSI 研究进行机制级比较；不得只做普通记忆库、档案或性能回归门。

任务流在线算法不得直接读取 task-family labels 或 block boundaries；只允许使用输入、工具 schema 和可观察轨迹。标签只用于离线分层分析。SWE-bench Verified、SWT-Bench、FeatureBench 是编码 Agent 连续任务流候选；样本量须经本课题 pilot 决定。

当前算法 Gate 不变：TCAIL V2.1 REQUEST CHANGES / IMPLEMENTATION BLOCKED；22 号 linkage/FOS 接口提案待独立复审；CI-GOM 未实现；第三项无正式算法规格。不得启动 Phase 0、调用真实 API 或训练模型，除非用户明确授权且相关 Gate 通过。

下一步优先生成 V0.3 Word 版并完成 Word/Markdown 一致性核对与 68 条参考文献 GB/T 7714 审计。每轮更新本仓库文献、机制比较、报告、决策日志和接班提示词，提交并核验远端 main。所有结论区分论文原文事实、研究推断和待验证假设。


## 31. IMCE-RSI 第三创新点机制进一步收敛（2026-11-03）

第三项不只是“交互记忆”，进一步收敛为**双键交互记忆检索与 retrieval-collision 处理**：
- 上下文键：任务输入、可见工具 schema、环境元数据和可观察轨迹；
- 交互键：局部交互后验、方向、不确定性、共同支持状态和 FOS；
- 语义相似但交互结构冲突时，标记 retrieval collision；
- 高不确定性时执行有限合法配对探测，预算不足则 abstain；
- 只有迁移收益置信下界为正且保留能力约束通过，才将历史 block 作为 donor。
任务家族标签和 stream block boundaries 只用于离线分析，在线算法不得读取。

新增细节已写入 26_RSI_THREE_INNOVATION_RESEARCH_DESIGN_R1.md、27_OPENING_REPORT_DRAFT_V0_3_RSI.md 和 28_RSI_CONTINUAL_RESEARCH_AUDIT_R1.md。SWE-bench Verified 已明确为首个真实编码 Agent 主平台；SWT-Bench/FeatureBench 用于连续任务流候选。AppWorld/Terminal-Bench 不作为当前首选主实验。

下一轮优先：完成 V0.3 Word 版、逐段一致性检查和 68 条参考文献 GB/T 7714 审计；不得因开题文稿修改而改变 TCAIL/CI-GOM 的 Gate 状态。


## 32. 三创新点参数调节与 Gate 设计（2026-11-03）

新增 `29_PARAMETER_TUNING_AND_EXPERIMENT_GATES_R1.md`，列出 TCAIL、CI-GOM、IMCE-RSI 的参数含义、候选调节顺序、A800 轻量迁移预测器训练条件、同预算基线要求和各阶段停止标准。下一轮在 Word V0.3 生成后，应同步核对 29 号文件与报告中的参数描述。当前仍未启动 Phase 0、API 调用或 GPU 训练。


## 31. Word V0.3 RSI 工作初稿生成（2026-11-03）

### 产物

已生成学校模板风格 Word 工作初稿：`河北工业大学硕士学位论文开题报告_V0.3_RSI_初稿.docx`。文件在当前会话可下载；结构检查通过：A4、宋体小四、1.5 倍行距、2 个模板表格保留、68 条参考文献编号连续。

构建与验收记录：`30_WORD_V0_3_BUILD_REPORT.md`。

### 必须如实说明的限制

- Word 是以 V0.2 Word 模板为底稿进行章节和段落级修订的 V0.3 工作初稿，不是 Markdown 的逐段逐表完全转换版。
- 仍需逐段核对 Word 与 `27_OPENING_REPORT_DRAFT_V0_3_RSI.md`，重点检查 2.3 研究意义、3.3 RSI 文献综述、4.4 第三研究内容、5.3 创新点三、6.6 IMCE-RSI、6.7 技术路线、基线、评价指标、可行性、研究基础和风险对策。
- 68 条参考文献编号已检查，但元数据、正式出版状态、DOI 和 GB/T 7714 尚未逐条审计。
- 需复核 PDF 预览的页眉、目录、公式显示、表格分页和段落分页；当前初稿预览约 44 页。

### 下一步优先级

1. 完成 Word/Markdown 逐段、逐表和公式一致性审计，避免保留旧 V0.2 论述造成口径冲突。
2. 完成 68 条参考文献的元数据和 GB/T 7714 审计。
3. 开始创新点一的独立算法审查，重点处理 TCAIL V2.1 REQUEST CHANGES 中的 estimand、模型阶数敏感性、任务块相关、局部 linkage 和最终边决策问题。
4. 继续遵守：22 号接口提案待独立复审；CI-GOM 未实现；IMCE-RSI 无正式规格；无 Phase 0、真实 API 实验或 A800 训练。不得因 Word 初稿生成而把研究设想写成已验证结果。


## 33. TCAIL Linkage Interface 独立复审 R2（2026-11-03）

### 结论

22 号 proposal 的 B1 方向部分成立，但未关闭：
- conditional fitness interaction、global RMS energy、parent/task local posterior 应分开；
- `q=P(|Δ|>δ_local|D)` 是 edge evidence probability，不是 FOS clustering strength；
- V2.2 必须分开 `δ_local`、`τ_edge`、连续 FOS weight `w)，并冻结 FOS builder；
- B2–B8 仍需闭合；
- TCAIL overall 仍 HOLD / IMPLEMENTATION BLOCKED。

### 新增文件

- `31_TCAIL_LINKAGE_INTERFACE_INDEPENDENT_REVIEW_R2.md`：完整独立审查、公式建议、B1–B8 修订要求和新颖性边界；
- `32_TCAIL_V2_2_SPEC_REVISION_TASK_R1.md`：V2.2 规格修订任务与可复制 Executor 提示词。

### 新增直接先行工作

P150–P153：Olieman et al. 2021 FBL；Dushatskiy et al. 2024 CGOMEA；Przewozniczek et al. 2025 cDLED；Tinós et al. 2026 GA-side-effect interaction learning。不得把 fitness-based linkage、conditional/local linkage 或搜索副产物交互学习本身作为创新。

### 下一步

只进行规格修订：新建 `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md` 和 `34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md`，不覆盖 17 号权威 V2；逐项关闭 B1–B8 后再交独立审查。不得编码、调用 DeepSeek API、启动 Phase 0、训练 A800 模型。

### 下一会话可复制提示词

你是我的河北工业大学计算机技术硕士开题研究 Planner。唯一允许维护的仓库是 `yujian777555/kaitibaogao`。先核验 main HEAD，读取 README、05_DECISION_LOG、SESSION_HANDOFF、17、20、21、22、29、31、32 号文件。当前 TCAIL 状态是 B1_PARTIALLY_ACCEPTED / overall HOLD / IMPLEMENTATION BLOCKED。你的唯一任务是监督 Executor 按 32 号任务创建新的 33 号 TCAIL V2.2 完整规格草稿和 34 号 B1–B8 closure matrix，不覆盖 17 号权威 V2。重点解决 q 与 FOS weight、FOS builder、M2/M3/高阶/heredity、BFDR 与 acquisition、task-block 配对模型、nuisance uncertainty、basis×anchor practical identifiability、parent/anchor/generation 检验族、rollout-equivalent budget。所有公式和伪代码必须一致；未解决项标记 OPEN，不得宣布 PASS。不得编码、不得调用 DeepSeek API、不得启动 Phase 0、不得训练模型。完成后更新仓库、提交并核验 main。
