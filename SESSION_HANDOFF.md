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
