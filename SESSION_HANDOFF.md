## 0E. 最新权威接管状态（2026-11-11，D-081 corrective commit）

- 工作仓库：yujian777555/kaitibaogao；分支 pilot-a-stateful-recovery；main 683b3fe7fc52c86e917d523fdc6bbb13abbfd653。
- 最新代码修正提交：192f958847fb31d7d704cfa0760201dcd8371e32（D-079: fix Train-only R4 strata and disable D-078 auto-rerun）；相对 main ahead 252 / behind 0。
- D-079 首轮 regression run 42827879313 在 282 tests 后失败，原因是 D6 generator 错误要求每个 Train family 同时包含 compensatable 和 uncompensatable tools。D-078 run 42827879133 在全量测试 preflight 失败，算法执行 skipped；没有新算法数据。
- D-081 修复已推送：D6 可在没有 contract-level uncompensatable tool 时，以 compensatable tool + runtime compensation unavailable 构造 R4；新增 D6 回归测试。D-078 workflow 改为 workflow_dispatch only，避免普通 push 重跑已完成的 pilot。
- D-081 combined status 当前返回空 statuses；corrective CI 尚未核实成功。D-078 原始数据未覆盖。
- 当前唯一任务：核验 D-081 regression CI。CI 通过后读取 D-079 audit/challenge artifacts，逐项审查 288 Train-only scenarios、R1-R4 label distribution、UNKNOWN/disagreement、scenario ID/role pairing、manifest SHA；提交 manifest lock 后才可申请新的 Train-only exploratory diagnostic。
- 不运行正式 A-3b，不访问 Test，不运行 Pilot B，不启动 A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox；不合并 main。D-076 R4 的 technical-missing power 和 pre-run/post-run gate 仍未关闭。

---

# SESSION HANDOFF — 开题研究项目

## 0C. 最新权威状态（2026-11-10，D-079 corrective diagnostics）

- 接管前远端 work HEAD：2b7903749efd46426672467a1a7d82dce221928d；main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead 250 / behind 0。提交后重新查询。
- D-078：14 arms × 3 seeds = 42 runs；Train 216、Validation 108；CI 42820836080 和 42820836104 success；Test outcomes 未读取。
- D-079 原始数据初查：32/42 次 selected FSM 与 Hand FSM fingerprint 完全相同；Hand R1/R2=84/84、R3 correct escalation=0/12、R4 containment=12/12。
- D-079 已准备 evaluator harm 修复、robust label evaluator helper、D-078 per-family/per-scenario audit、8-family × 6-strata × 3-repeat × 2-role Train-only challenge generator、测试和预注册文件；CI 尚待验证。
- 挑战集候选共288个 Train-only scenarios，search/diagnostic 各144；manifest hash 待 CI 生成并锁定；没有启动新算法运行。
- 唯一下一任务：核验 D-079 CI 与候选 manifest，锁定 manifest hash 后，才可启动新的 Train-only exploratory mechanism diagnostic。正式 A-3b、Test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 继续 HOLD。

## 0B. 最新独立复审状态（2026-11-10，覆盖 D-076 执行报告中的 READY_FOR_INDEPENDENT_REVIEW）

- D-076 执行提交：`3d2dacf0871ab0f030084f6ed2d62e17ba524ddd`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；复审前 ahead 227 / behind 0。
- CI run 42814630988 success；执行报告记录 290/290。复审未重新运行测试，也未运行真实 benchmark。
- 独立复审结论见 `78_D076_INDEPENDENT_REVIEW.md`：**R4 REQUEST CHANGES；SBCG NOT READY FOR TRAIN/VALIDATION PERFORMANCE DIAGNOSTICS**。
- 主要阻断：pre-flight pre-run/post-run lifecycle circularity；power 未模拟 technical missing，F=40/ICC=.20 Type-I=0.0547 [0.0504,0.0593]；one-time gate 未闭合到生产分析入口；NSGA-III niching 投影公式/normalization/niche count 非 canonical；M1 f3 公式偏离 75 号候选；Validation 选择仍在 Train archive 上；budget/cache 统计需修复。
- **当前唯一任务：D-078 corrective revision**，先修复 78 号报告列出的阻断项并重新提交独立复审。
- 正式 A-3b、真实 Train/Validation 性能诊断、Test、Pilot B、A800/ARWM、真实 LLM API 继续 HOLD。没有任何新算法性能数据。


## 0A. 最新权威状态（2026-11-10，覆盖下文旧状态）

- D-076 已完成 R4 正式 runner、五 composition 核验、24 格 10,000 MC 功效、R4 预注册与真实 HOLD pre-flight；R4 = **READY_FOR_INDEPENDENT_REVIEW**，不是 ACCEPTED。
- SBCG-NSGA-III 已实现 M1/M2/M3、14 个对照/消融接口、预算/缓存计数和合成测试；**性能 NOT RUN，尚不能判断是否提升**。
- 实现提交：32b6914b08075775c0d9000fb7b80392c33ec26e；证据提交：e92e9af964edd6963baed41b48a24073e34f99f8；功效写回/clean-clone：4c4c62fb7213868c3c8fa98f1bdd5b83edc77212；main 保持 683b3fe7fc52c86e917d523fdc6bbb13abbfd653。
- 本地与 clean-clone 均为 262+28=290 tests OK；CI regression 42813004959 与 R4 power 42813004752 success。
- 真实 Train/Validation 算法诊断未运行，Test 未读取；pre-flight 因独立审计、导师 MDE、用户批准和正式 outcome ledger 未满足而 HOLD。
- 唯一任务：将 `64_A3B_PREREGISTRATION_CANDIDATE_R4.md` 与 `77_D076_R4_AND_SBCG_EXECUTION_REPORT.md` 交独立 Reviewer。只有 ACCEPTED、导师 MDE、用户批准和真实 pre-flight 后，才可冻结安全非劣/hypervolume 规则并运行 Train-only 强对照。

**最后更新：** 2026-11-10（D-076 R4/SBCG 实现与验证）
**唯一仓库：** https://github.com/yujian777555/kaitibaogao
**研究主线：** Evolutionary Computation for AI Agents
**当前阶段：** R4 READY_FOR_INDEPENDENT_REVIEW；SBCG synthetic-tested、性能未验证；正式 A-3b HOLD
**最终题目：** 尚未确定  
**最终创新点：** 尚未确定

## 0. 最新权威状态与唯一任务（2026-11-10）

- R3 权威审计：72_64R3_INDEPENDENT_REVIEW.md = **REQUEST CHANGES**。
- 最近一次代码/测试核验 HEAD：f4d8d0d1e314b29f7e6a7627f99293b306f76d92；main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead 207 / behind 0。
- CI 42791224479 @ f4d8d0d：success；pilot_a_recovery 28 + pilot_a3b 212 = **240 tests**；D-064-C hashes unchanged and PASS.
- R4 已实现：Student-t/CI、动态 family-level primary analyzer + provenance、H2–H5 四项配对分析与 Holm（全 exploratory）、Train-only evolution guard、ordinary evaluator Test guard、public manifest Test payload removal、atomic one-time gate、metadata-only fail-closed pre-flight。
- R4 尚未完成：正式 runner 接线、功效/Type-I 10,000 MC 重算、R4 预注册、独立审计。
- 算法提升候选：75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md；现有 AB 仍有 R3/R4/harm trade-off，SBCG-NSGA-III 未实现或验证。
- **唯一执行优先级：** 完成 R4 power/Type-I、正式预注册和真实路径接线，交独立 Reviewer。不得读取真实 Test 标签/结果，不运行正式 A-3b。
- 正式 A-3b 仍 HOLD，须独立审计 ACCEPTED、导师 MDE=0.10 认可、用户明确批准和 R4 pre-flight 全通过。

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


## 34. TCAIL V2.2 Planner Addendum R1（2026-11-04）

本节覆盖上一节“仅处理 B1–B8”的 Executor 指令：**V2.2 当前必须处理 B1–B12**。唯一仓库仍为 `yujian777555/kaitibaogao`；本轮开始时远端 main HEAD 为 `903e62aa4b846ea20950b3be81c355688e0065e3`。

### 新增文档
- `35_TCAIL_V2_2_PLANNER_ADDENDUM_R1.md`：FBL/cDLED/CGOMEA/Tinós 原文机制精读、新增 B9–B12、强基线和执行要求。

### 本轮原文级结论
- FBL 已有 fitness-based contrast、scaled dependency strength、LT/MP FOS、incremental pair probing；
- cDLED 已有 individual-local DLED、conditional eVIG、局部子结构识别和 donor mating restriction，且其原文报告 DLED 分解成本在部分问题上达到 5%–78%；
- CGOMEA 已有 conditional linkage 与 solution mating filter；
- Tinós et al. 2026 已有 GA-side-effect interaction learning，无需额外 fitness evaluations。

### 新增 B9–B12
- B9：objective-scale probability interaction 是 inverse-link 后的非线性 estimand；row-space 线性 contrast 检验不足以自动证明其可识别；
- B10：acquisition design 必须是四格 task-block 观测向量，明确 CRN 可行性、任务随机效应和缓存后的唯一 episode-equivalent cost；
- B11：unsupported edge 不得填 0；明确 missingness-aware FOS、forest/singleton/fallback；
- B12：posterior q/w 需 prior sensitivity 和 null calibration，防止低样本宽先验造成伪高置信。

### 下一会话唯一任务
监督 Executor 按 32 号任务 + 35 号补充创建：
1. `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md`（完整规格）；
2. `34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md`（B1–B12 逐项矩阵）。

不得覆盖 17 号 V2 权威历史文件、20 号 REQUEST CHANGES 复审、22 号 B1 proposal、31 号独立复审、32 号执行任务或 35 号 Planner Addendum。每项需标明 PASS/PARTIAL/OPEN 和对应章节/公式/伪代码位置。若某项需要新增假设，显式写出并给出可证伪测试；不得默认其成立。

### 严格禁止
- 不编码 TCAIL/CI-GOM；
- 不运行正式 Phase 0；
- 不调用 DeepSeek API；
- 不训练 A800 模型；
- 不启动 CI-GOM 或 IMCE-RSI；
- 不把规格草稿写成已验证算法或已成立创新。

完成 33/34 后必须交独立审查；审查者不得是刚刚撰写该规格的同一 Planner 会话。若 V2.2 只是 FBL/cDLED 的 Bayesian/OED 包装，或没有同预算下游 GOM 增益，应 NO-GO/继续收窄。


## 35. TCAIL V2.2 Executor 完整草稿已交付（2026-11-04）

本节覆盖此前“创建 33/34 号”的下一步指令。当前唯一任务是**由新的独立审查会话复核 V2.2**，不是开始实现。

### 本轮开始状态与交付

- 本轮开始及克隆基线的远端 `main` HEAD：`85414664a902724fc5610e606f05667ddc74b635`。
- 新增 `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md`：完整规格，含统一数学定义、观测/成本模型、非线性门禁、M2/M3 与高阶、per-graph BFDR、constrained-risk acquisition、missingness-aware FOS、完整伪代码、校准、强基线和 Gate。
- 新增 `34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md`：B1–B12 逐项映射、跨机制一致性、强基线 original/adaptation 和 OPEN 清单。
- 更新 README 与 05_DECISION_LOG（D-038）；17、20、22、31、32、35 号历史文件未覆盖。

### 当前真实状态

- B1–B12：均为 `PARTIAL（规格已处理）`，不是独立研究 PASS；每项尚需的审查、校准、复现、实现或实验在 34 号中标为 `OPEN`。
- 编写过程中已做规格符合性和文档质量复核，并修正 fantasy 生成、条件随机效应、缓存/重试成本、Fisher 维度、双模型状态、BFDR 风险语义和 Monte Carlo 控制流。这些只是起草过程检查，不得冒充正式独立数学复审。
- TCAIL：`DRAFT / PENDING INDEPENDENT REVIEW / HOLD / IMPLEMENTATION BLOCKED`。
- CI-GOM、IMCE-RSI：继续冻结。
- 未编写算法实现，未启动 Phase 0，未调用 DeepSeek/真实 LLM API，未训练模型；无性能结果、无 Gate-1 PASS。
- 独立新颖性、真实 Agent 有效性和 EC 搜索收益均 `NOT ESTABLISHED`；规格完成不等于创新成立。

### 下一轮独立审查重点

1. 检查 objective-scale nonlinear estimand 的充分条件、invariance 充要条件、GLMM nuisance 认证和 practical-information 公式是否正确且可执行。
2. 检查每模型 base state 与每边 joint state 是否穷尽，结构冲突/零支持是否绝不进入采样或高置信图，高阶失败边界是否诚实。
3. 检查 model-specific 双 fantasy、双重拟合、max-risk/max-cost 是否有明确概率意义；其校准和计算可行性必须保持 OPEN，不能因公式完整而接受为定理。
4. 检查最终 BFDR 集合、近似最优风险、acquisition、FOS 和预算是否使用同一状态与成本；逐图 BFDR 不得推出全局 FDR。
5. 检查四格 task-block、缓存键、唯一新增 episode、失败/重试和实际资源账是否无重复或漏计。
6. 检查全部强基线及 original-paper reproduction 与 paper-setting adaptation 是否足以排除 FBL/cDLED/CGOMEA/GAwLL2 等先行机制的包装。

### 可直接复制的独立审查接班提示词

你是 `yujian777555/kaitibaogao` 的独立数学、统计与 EC 规格审查者。唯一允许读取和维护的仓库是 `yujian777555/kaitibaogao`，不得读取其他项目仓库。先核验远端 `main` HEAD，再读取 README、05_DECISION_LOG、SESSION_HANDOFF、17、20、21、22、29、31、32、33、34、35 号文件。

你的唯一任务是对 `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md` 和 `34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md` 做正式独立复审，并形成新的审查报告。不要把 34 号记录的起草过程复核当作独立 PASS，也不要因 B1–B12 有文字条款就自动关闭它们。

逐项审查 B1–B12 的数学正确性、统计校准前提、EC linkage/FOS 语义和伪代码可执行性；特别检查 probability-scale 非线性可识别性、task/block GLMM、M2/M3 与高阶、model-specific acquisition 与最终 BFDR 的一致性、unsupported edge 的 missingness-aware FOS、唯一新增 episode-equivalent、prior sensitivity/null calibration 和所有强基线。对每个问题给出 ACCEPT / REQUEST CHANGES 及具体章节/公式/伪代码证据；未解决项保持 OPEN。

严格禁止：不编写 TCAIL/CI-GOM 实现，不启动 Phase 0，不调用 DeepSeek/真实 LLM API，不训练模型，不启动 CI-GOM 或 IMCE-RSI。不得把规格完成、文档静态检查或审查通过等同于创新成立；即使规格审查通过，后续实现和合成/真实/下游 EC Gate 仍须分别验证。完成后按 REPOSITORY_MAINTENANCE_POLICY.md 更新审查报告、README、05_DECISION_LOG 和 SESSION_HANDOFF，提交并核验远端 main。


## 36. TCAIL V2.2 独立复审 R1 与 Corrective Revision R1（2026-11-04）

本节覆盖此前所有要求复审 33/34 或继续创建 37/38 的旧指令。当前唯一任务是**由新的独立会话对 37/38 号进行 R2 复审**，不是实现算法。

### 远端基线与历史审查

- 本轮开始远端 `main` HEAD：`ea5c8f7500848baf7a4f3a345f362d0573e59a2b`。
- `36_TCAIL_V2_2_INDEPENDENT_REVIEW_R1.md` 对 33/34 给出 REQUEST CHANGES，提出 R1–R7。
- `D039_TCAIL_V2_2_INDEPENDENT_REVIEW_DECISION.md` 和 `SESSION_HANDOFF_V2_2_CORRECTIVE_R1.md` 是相应补充记录；D-039 已合并回主 `05_DECISION_LOG.md`。
- 33、34、36 号及其审查基线均未覆盖。

### 本轮交付

1. `37_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R1.md`：完整 V2.2 Revision R1 规格，包含数学定义、状态机、完整伪代码、主控制流、参数表和 OPEN 清单。
2. `38_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R1.md`：R1–R7 逐项修订、公式/伪代码/边界映射、B1–B12 承接和一致性矩阵。
3. README、05_DECISION_LOG（D-039/D-040）和本交接文件已更新。

### R1–R7 当前处置

- R1：`ell_env/q_env` 只作保守约束；最终风险为各模型自身 posterior loss 的 `max_M`，鲁棒集合优化无证书则 fail-closed。
- R2：使用模型内 MCSE、`A_U/A_L` 与预注册 alpha-spending；点估计不再直接触发非正停止，无法判断时为 `STOP_ACQUISITION_UNCERTAIN`。
- R3：base-key 终身 retry/continuation/terminal/exhausted 状态持久化，fantasy 与真实执行共用规则。
- R4：使用边际 GLMM expected Fisher、nuisance/PSD guard、完整 target rank 和 draw-wise `λ_min` 低分位；广义逆不再冒充 posterior covariance。
- R5：support coverage、selected-positive density、unknown density 分离，known-zero 与 NA 不再混淆。
- R6：主规则为 worst-expected model objective；model-average 和 product-coupled envelope 分开报告，不混用 MCSE。
- R7：活动图集合/权重在 cycle 内冻结，新图只在边界进入，切换立即使旧 assessment/decision 失效。

所有项仍为 `PARTIAL（修订规格已处理）`，不是独立数学 PASS。所有阈值、校准、形式认证、强基线复现、实现和实验继续 OPEN。独立新颖性、真实 Agent 有效性和 EC 搜索收益仍 NOT ESTABLISHED。

### 当前禁止事项

- 不编写 TCAIL/CI-GOM 实现；
- 不启动 Phase 0；
- 不调用 DeepSeek 或其他真实 LLM API；
- 不训练模型；
- 不启动 CI-GOM 或 IMCE-RSI；
- 不把起草复核、规格完整或文档静态检查写成算法验证或创新成立。

TCAIL 继续 `HOLD / IMPLEMENTATION BLOCKED`；CI-GOM 和 IMCE-RSI 继续冻结。

### 可直接复制的 R2 独立审查接班提示词

你是 `yujian777555/kaitibaogao` 的新独立数学、统计与 EC 规格审查者。唯一允许读取和维护的仓库是 `yujian777555/kaitibaogao`，不得读取其他项目仓库。先核验远端 `main` HEAD，再读取 README、05_DECISION_LOG、SESSION_HANDOFF、33、34、36、37、38 号以及 31、32、35 号历史约束文件。

你的唯一任务是对 `37_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R1.md` 与 `38_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R1.md` 做正式 R2 独立复审，并形成新的审查报告。不要把 38 号中的起草过程复核当作独立 PASS，也不要因 R1–R7 有规格条款就自动关闭它们。

逐项检查：R1 鲁棒集合与每模型损失；R2 MCSE 区间方向、非正停止、正收益资格和重复查看；R3 多轮 retry/continuation/terminal 账本；R4 边际 GLMM Fisher、Schur 条件、完整秩和 draw-wise 分位门；R5 support/positive/unknown 与 FOS 更新；R6 worst-expected/model-average/product coupling 及 MCSE；R7 活动图集合、权重、cycle ID 和旧快照失效。检查公式、状态机、伪代码和主控制流是否一致，并检查 B1–B12 的 OPEN 项是否被保留。

对每个问题给出 ACCEPT / REQUEST CHANGES 及具体章节、公式和伪代码证据；未解决项保持 OPEN。不要实现算法、启动 Phase 0、调用真实 LLM API、训练模型或启动 CI-GOM/IMCE-RSI。规格审查通过也不等于创新成立；后续实现、合成、真实 Agent 和下游 EC Gate 仍须分别验证。完成后按 REPOSITORY_MAINTENANCE_POLICY.md 更新审查报告、README、05_DECISION_LOG 和 SESSION_HANDOFF，提交并核验远端 main。


## 37. TCAIL V2.2 Revision R1 独立复审 R2 — REQUEST CHANGES（2026-11-04）

### 审查基线与交付
- R2 审查基线：4f15ac303936817cc2bf122e649fff2331c9b1dc。
- 新增 39_TCAIL_V2_2_INDEPENDENT_REVIEW_R2.md。
- README 已更新；决策记录为 D-041。
- 37/38 号规格与矩阵未修改；33/34/36 号历史文件未修改。

### 结论
**REQUEST CHANGES / HOLD / IMPLEMENTATION BLOCKED。**

已接受的规格进步：R1 的 max_M L_M 鲁棒决策、worst-expected max_m E_m[H] 主聚合、边际 GLMM Fisher 完整 target-rank 门、acquisition cycle 冻结原则。

仍需修订：
1. **R2-A：** A_L/A_U 必须纳入当前基准风险 R(D) 的 posterior MCSE、优化误差和数值误差；若有精确证书则明确给出。
2. **R2-B：** sign alpha 明确分配两个模型、N 个候选和所有 looks；rank alpha 明确分配所有候选/rival comparisons；定义 PRE_REGISTERED_MC_Z。
3. **R2-C：** 说明 posterior/fantasy draws 的 IID 或 MCMC 性质；对自相关、nested posterior fitting、quadrature 和 solver error 给出 MCSE/误差处理。
4. **R3-A：** REUSABLE 状态但 cache miss 必须 fail-closed 或从不可变 attempt record 安全重建；不得被计划为 retry continuation 后由执行器 BREAK 并返回 OK。
5. **R3-B：** 明确执行前持久化 attempt reservation/IN_FLIGHT；崩溃恢复使用 UNKNOWN_OUTCOME/reconciliation，不得复用 attempt ID 或漏计成本。
6. **R4-A：** Fisher Hessian 的参数向量只含连续可微参数；离散 nuisance 需边际化或逐状态计算。
7. **R5-A：** 将 NOT_SELECTED 与 UNRESOLVED 分开；NOT_SELECTED 属于 Q_g，已经通过基础支持/信息门，不能直接计为 unknown。分别定义 data-support coverage 和 similarity-resolved coverage。
8. **R6-A：** 冻结跨候选计算层 CRN 的底层随机变量映射，或不使用 paired MCSE。
9. **R7-A：** generation/RSI-round index 与 acquisition-cycle index 使用不同符号，并定义两者映射。

B3、B8、B10、B11 为 REQUEST CHANGES；其余 B1/B2/B4/B5/B6/B7/B9/B12 保持 PARTIAL。所有校准、认证、实现和实验继续 OPEN。

### 下一轮唯一任务
只做 **TCAIL V2.2 corrective specification revision R2**，创建：
- 40_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R2.md
- 41_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R2.md

保留 37/38/39 号及所有历史文件，不覆盖。每个修订必须同步公式、伪代码、状态机和边界反例；未校准事项保持 OPEN。完成后交不同会话进行下一轮独立复审。

### 可直接复制的 Executor 提示词

你是 yujian777555/kaitibaogao 项目的规格修订 Executor。唯一仓库是该仓库 main，不得混入 openissue、agentfotagent、GLEPPO 或其他项目。

先核验远端 main HEAD，读取 README、05_DECISION_LOG、SESSION_HANDOFF、REPOSITORY_MAINTENANCE_POLICY，以及 33、34、36、37、38、39 号文件和相关 31、32、35 号历史约束。

唯一任务：依据 39 号独立复审报告，对 TCAIL V2.2 做 corrective specification revision R2，创建 40 号完整规格和 41 号变更/闭合矩阵。不得覆盖 33/34/36/37/38/39 历史文件。

必须修复：
- 当前基准风险 R(D) 的 MCSE/数值/优化误差纳入 acquisition A_L/A_U；
- sign alpha 对两个生成模型、所有候选和 look 的完整分配；
- rank alpha 对所有 rival comparisons 的完整分配，并定义 PRE_REGISTERED_MC_Z；
- posterior/fantasy IID 或 MCMC 抽样条件、autocorrelation、nested MCSE 和 quadrature/solver error；
- REUSABLE ledger 与 cache miss 的 fail-closed/recovery；
- 外部执行前的 durable attempt reservation、IN_FLIGHT、UNKNOWN_OUTCOME 和 crash reconciliation；
- Fisher Hessian 的连续可微参数向量与离散 nuisance 处理；
- NOT_SELECTED、SUPPORTED_PRACTICAL_NULL、SELECTED_SUPPORTED、UNRESOLVED 四类边的分离，重新定义 data-support coverage 与 similarity-resolved coverage；
- paired MCSE 的底层 CRN 映射；
- generation index 与 acquisition-cycle index 的分离。

要求所有公式、状态机、伪代码和主控制流跨章节一致；每项给出边界反例；所有经验校准保持 OPEN；不得把规格修订写成算法 PASS。

严格禁止：不写算法实现、不启动 Phase 0、不调用 DeepSeek/真实 LLM API、不训练模型、不启动 CI-GOM 或 IMCE-RSI。完成后更新 README、05_DECISION_LOG、SESSION_HANDOFF，提交并推送 main，重新核验远端 HEAD 和文件内容，返回完整 SHA 与验证结果。


## 38. TCAIL 研究转向证据优先（2026-11-04）

用户明确要求尽快证明方法，不再进行无关规格扩展。当前只围绕 TCAIL 的核心可证伪链条推进。

### 已有证据：Oracle Linkage Gate
- 实验目录：experiments/tcail_oracle_gate_pilot/
- 20 个配对种子，40 维 deceptive 4-bit trap，最大 5,000 objective evaluations。
- Oracle FOS：39.55/40；population-MI LT：38.55/40；配对 Wilcoxon 单侧 p=0.000919；配对 bootstrap 95% CI [0.55,1.45]。
- Oracle 13/20 达到全局最优；Learned LT 2/20。
- 12-seed additive control 中四种方法均 12/12 达到最优。
- 解释边界：简化 GOM 原型上的 Oracle 上界试验；不是 TCAIL estimator 的结果，也不是正式 GOMEA/真实 Agent 结果。

### 下一步唯一实验
执行 fixed full-factorial estimator-only synthetic gate，暂不引入 active acquisition/retry：
1. 生成 parent-conditioned、task-block Bernoulli 四格结果；包括 null、弱/强交互、正负方向和 parent/task sign flip、unsupported/low-support。
2. 对所有估计器提供完全相同的四格 task-block 数据和成本。
3. 比较 local posterior q/w、FBL/scaled-FBLT adaptation、pooled/global interaction score 和 oracle。
4. 报告 edge AUPRC、null false-link rate、方向/翻转恢复、posterior calibration、abstention、FOS recovery。
5. 只有 TCAIL q/w 在校准且同预算优于强基线后，才进入 active acquisition 对照；若无增量，停止或收窄。

不得把本轮 Oracle 结果写成 TCAIL 已验证。继续不调用真实 LLM API、不训练 A800 模型、不启动 CI-GOM/IMCE-RSI。不要再先写大规格；只实现并运行上述最小估计器实验，结果必须记录每个 seed 和原始数据。


## 39. TCAIL 估计器证据优先：第二轮小型诊断（2026-11-04）

新增实验目录 experiments/tcail_estimator_gate_pilot/，含脚本、结果和依赖。

实验使用 20 个种子，0–9 只估计 Normal empirical-Bayes prior scale，10–19 作为 held-out；每个 seed 200 个 pair × 2 parent contexts。四格 Bernoulli 结果在 task-block 内配对，含 positive/negative/weak/null、parent sign flip、unsupported 和 low support。

Held-out 结果：
- EB posterior q AUPRC 0.802；EB posterior w 0.797；
- local standardized contrast 0.785；Student-t q 0.767；
- raw local contrast 0.619；context-pooled contrast 0.598；
- q Brier 0.153；q≥0.8 precision 91.1%、recall 38.1%、FPR 1.57%；
- q AUPRC 在 10 个 held-out seed 均高于 standardized contrast，平均差 +0.0169，bootstrap 95% CI [0.0120,0.0221]；
- 低支持 8-block 子集 AUPRC 0.353，不能据此放松 abstention 门。

**严格解释：** 这是 paired task-block normal-normal empirical-Bayes proxy，不是完整 TCAIL M2/M3 GLMM；不是 paper-exact FBL/scaled-FBLT/cDLED 对照；生成器也不是 logistic GLMM。仅为小幅正向研究信号。

### 下一步唯一任务
不要写更多规格，不要启动 acquisition。只做 paper-faithful 强基线和校准：
1. 复现/适配 FBL 与 scaled-FBLT，另加 cDLED-P3M 对照；
2. 所有方法使用相同 task-block 四格数据、相同预算和相同 held-out seeds；
3. 进行 posterior calibration、null false-link、sign-flip、abstention 和 FOS recovery；
4. 保留每 pair/context 原始四格数据及每 seed 结果；
5. 若 EB q/w 不能稳定优于强基线，或低支持下不能安全 abstain，则停止/收窄 TCAIL；
6. 只有估计器 gate 通过后，才设计 active acquisition 对照。

当前 TCAIL 仍 HOLD；未实现完整 GLMM、未调用真实 LLM API、未训练 A800、未启动 CI-GOM/IMCE-RSI。


## 40. TCAIL 与 scaled-FBL task-block 适配的直接合成比较（2026-11-04）

新增 experiments/tcail_estimator_gate_pilot/run_fbl_comparison.py 与 FBL_COMPARISON_RESULTS.md。脚本保留每个 pair/context 的原始四格 block outcomes、block contrasts、模型输入和 held-out 指标。

### Held-out 结果
- EB q AUPRC 0.802；EB w 0.797；
- local z-score 0.784；
- scaled-FBL binary task-block adaptation 0.414；
- raw contrast 0.619；context-pooled 0.598。
- EB q 对 scaled-FBL 的 per-seed AUPRC 差 +0.3845，10/10 held-out seeds 胜，bootstrap 95% CI [0.3704,0.3990]。
- 训练 null 95th-percentile matched thresholds：EB q precision/recall/FPR 81.5%/58.7%/5.62%；scaled-FBL 69.7%/31.5%/5.81%。
- 8-block low-support AUPRC 0.353，仍是明显失败边界。

### 结论边界
这是正向合成信号，但 scaled-FBL 是二元 task-block adaptation，不是原论文 reproduction；EB q/w 是 Normal-normal proxy，不是完整 TCAIL M2/M3 GLMM。还未比较 cDLED-P3M、CGOMEA、GAwLL2；还未验证 FOS/GOM 下游收益。不得宣称 TCAIL 已证明。

### 下一步唯一任务
1. 做 paper-faithful FBL/scaled-FBLT 复现或清楚标注适配差异；
2. 加入 cDLED-P3M 与 GAwLL2 的直接基线；
3. 用相同 task-block 原始四格数据和成本比较；
4. 实现并校准完整 Bernoulli task-block 模型，保留 held-out seeds；
5. 测试低支持 abstention 和 FOS recovery；
6. 只有估计器 gate 通过，才转 active acquisition。

不再扩写规格，不先启动 active acquisition，不调用真实 Agent API、不训练 A800、不启动 CI-GOM/IMCE-RSI。


## 41. 当前唯一优先任务：TCAIL estimator-to-GOM confirmatory evidence（2026-11-04）

用户明确要求“抓紧证明，不要做不相关的事情”。本节覆盖此前继续修订完整 acquisition/retry 规格的优先级；不要再先写 40/41 号规格来延长文档循环。

### 当前仓库基线
- 本轮实验 pilot 已在当前 main：experiments/tcail_oracle_gate_pilot/、experiments/tcail_estimator_gate_pilot/。
- 详细确认性协议：42_TCAIL_ESTIMATOR_TO_GOM_CONFIRMATORY_GATE_R1.md。
- 研究决策：D-042。
- 现有结果仍是 exploratory，不是 TCAIL 证明。

### 已有 pilot 的正确解释
1. Oracle FOS 在 40-bit deceptive trap 简化 GOM 上 13/20 成功，支持该特定任务有可利用 linkage 上界；不是 TCAIL estimator 证据，也不是 official GOMEA 结果。
2. EB q/w AUPRC 0.802/0.797；模型是 Normal-Normal EB proxy，不是指定的 M2/M3 Bernoulli task-block GLMM。
3. scaled-FBL binary adaptation AUPRC 0.414；不是原论文复现。当前 epsilon gate 与 local four-cell contrast 同源，需审计其与原 FBL tolerance 的映射。
4. 8-block low-support AUPRC 0.353，必须作为失败边界，支持不足时 abstain。
5. 两个 pilot 均需 clean rerun，不能只引用 README 汇总。

### 下一轮 Executor 唯一任务
按 42 号文件执行，不要写新的大段理论：
1. clean rerun 现有 Oracle 和 estimator pilots，校验 raw CSV/JSON/报告；
2. 审计 FBL 公式、cell 顺序、epsilon gate、随机种子、初始评价预算和停止规则；
3. 建立 logistic task/block random-effects Bernoulli generator，计算 probability-scale 真值四格差分；
4. 实现并校准 Bernoulli task-block M2/M3 posterior q/w；
5. 在相同四格 observations、held-out seeds 和 episode-equivalent budget 下比较 FBL/scaled-FBLT、cDLED-P3M、CGOMEA linkage、local contrast、global pooling、random、oracle；
6. 完成 Estimator Gate 后，才执行独立 discovery/evaluation blocks 上的 FOS→GOM 下游 Gate，并把 discovery cost 计入总预算。

### 强制报告
- 所有 per-seed/per-pair/per-context/per-block 原始数据；
- posterior q calibration、Brier、AUPRC、null false-link、sign-flip recovery；
- low-support risk-coverage/abstention；
- FOS pair co-clustering recovery；
- GOM held-out objective/success 与总 episode-equivalent 成本；
- baseline reproduction/adaptation 边界；
- 配置、环境、Git SHA、命令、日志和 clean rerun 结果。

### GO/NO-GO
- Estimator：五情景 macro-AUPRC 相对 validation-selected strongest non-oracle baseline 的 paired seed 95% CI 下界 > 0；并检查 null、sign-flip、calibration、FOS 和 low-support abstention。
- Downstream：同总 episode-equivalent budget 下，TCAIL-FOS 的 held-out GOM objective/success 相对 strongest non-oracle linkage baseline 的 paired 95% CI 下界 > 0。
- 若 estimator 提升但 GOM 不提升，不得声称 EC 搜索创新。
- Oracle 无收益则停止该任务族 linkage-to-GOM 主张。
- TCAIL 不胜强基线则停止其 estimator 新颖性主张。

### 执行边界
只允许 CPU 合成实验和隔离 GOM research prototype。不得调用真实 LLM API，不训练 A800，不启动 CI-GOM 或 IMCE-RSI。不要把此授权解释为完整 active acquisition、生产 retry 或 Phase 0 获批。

### 可直接复制的 Executor 提示词

你是 yujian777555/kaitibaogao 的实验 Executor。唯一仓库是该仓库 main。先核验最新远端 HEAD，读取 README、05_DECISION_LOG、SESSION_HANDOFF、REPOSITORY_MAINTENANCE_POLICY、42 号协议，以及现有两个 pilot 的全部脚本、requirements、原始结果和报告。

用户要求尽快证明 TCAIL 的 EC 收益。不要继续扩写完整 acquisition/retry 规格，不要做与 estimator→FOS→GOM 证据链无关的工作。

严格按 42 号协议执行：
A. clean rerun 两个 pilot；审计公式、预算、seed、cell 顺序、统计检验和原始数据一致性。发现错误先修复并记录。
B. 构建 logistic task/block Bernoulli generator，确保 ground truth 是 probability-scale 四格差分；覆盖 additive/null、sparse pairwise、parent sign-flip、overlapping/higher-order、low-support/drift。
C. 实现 Bernoulli task-block M2/M3 posterior q/w，做 posterior calibration、null calibration、prior sensitivity、abstention；不得用 Normal-Normal proxy 冒充正式 TCAIL。
D. 同预算比较 FBL/scaled-FBLT、cDLED-P3M、CGOMEA linkage、local/global、random、oracle；严格标明原论文复现与适配。
E. Estimator Gate 通过后才做独立 discovery/evaluation blocks 的 FOS→GOM；总预算包含 discovery 与 search。
F. 按 42 号 GO/NO-GO 规则作结论。失败也要如实报告，不得调阈值直到通过，不得查看 held-out 后再改方法。

维护要求：全部 raw data、per-seed results、配置、依赖、Git SHA、命令和日志入仓库；更新 README、05_DECISION_LOG、SESSION_HANDOFF，提交推送并复核远端。未完成事项明确标记 NOT RUN。严禁真实 LLM API、A800 训练、CI-GOM、IMCE-RSI 和完整 active acquisition。


## 42. R1-A 实际运行与修正版审计已完成（2026-11-05）

当前实验目录：`experiments/tcail_confirmatory_r1/`。必须先读 `R1A_AUDIT_RESULTS.md`、原始/修正版 reconciliation JSON 和环境锁，不得只引用旧报告。

### 实际运行和数据

- 原始 Oracle、Estimator-only、Scaled-FBL 三个脚本均已在隔离 Python 3.10.1 环境实际运行；原始与修正版输出分别位于 `r1a_original_code/` 和 `r1a_corrected/`。
- 所有原报告核心指标均可从原始 CSV 独立重算；FBL 四格顺序、contrast 和 gate 在 438,400 个 block 上误差为 0。
- 修正版 Oracle 使用相同跨方法 mixing seed，初始种群哈希一致；Oracle−Learned LT 配对均值 +1.30，bootstrap 95% CI [0.60,2.00]。这只证明该原型的 Oracle 上界价值。
- FBL 绝对值适配无 gate/零 epsilon AUPRC=0.379；signed Eq.(7) 有 2,811/3,800 个领域违规，valid-only 结果不是完整公平基线。
- EB q/w 仍是 Normal–Normal proxy，不是 TCAIL Bernoulli M2/M3。

### 当前结论和下一步

R1-A 不是 GO。Estimator Gate、真正 TCAIL 和 TCAIL-FOS GOM Gate 均未完成。下一阶段必须实际实现并校准 Bernoulli task/block 层级 M2/M3，按 42 号运行 train/validation/test 和强基线比较；只有 Estimator Gate 通过才可进入 TCAIL-FOS GOM Gate。失败和低支持结果必须保留。

严格边界不变：禁止真实 LLM API、A800 训练、CI-GOM、IMCE-RSI、完整 active acquisition 和生产 retry。每阶段保存原始数据、日志、配置、环境、每 seed 结果和统计输出，更新 README、05_DECISION_LOG、SESSION_HANDOFF，提交并核验远端 main。


## 43. R1 Estimator Gate 确认性运行完成：FAIL，GOM NOT RUN（2026-11-05）

### 当前状态
- 真正的 Bernoulli task/block M2/M3 Laplace 估计器、五情景生成器和 9 类基线已实现并实际运行。
- Held-out 3000–3039（40 seeds）未参与开发。结果：TCAIL q macro-AUPRC 0.6736 vs standardized 0.7732；配对差 −0.0996，95% CI [−0.1139,−0.0858]。
- 关键情景 sparse（−0.0393）与 parent sign-flip（−0.3541）显著更差；只有 low-support/drift 显著更好（+0.0462）。
- **ESTIMATOR_GATE_FAIL。** Downstream GOM Gate **NOT RUN**；没有 EC 收益证据。

### 必读文件
1. `experiments/tcail_confirmatory_r1/R1_ESTIMATOR_GATE_RESULTS.md`（完整结果、失败机制、边界、OPEN）。
2. `experiments/tcail_confirmatory_r1/results/summary.json`、`stage_summary.json`、`independent_recompute.json`、`posthoc_diagnostics.json`。
3. `experiments/tcail_confirmatory_r1/experiment_config.json`（冻结配置与 held-out 范围）。
4. `experiments/tcail_confirmatory_r1/R1A_AUDIT_RESULTS.md`（pilot 审计与基线边界）。
5. `42_TCAIL_ESTIMATOR_TO_GOM_CONFIRMATORY_GATE_R1.md`（协议与停止规则）。

### 已确认的事实
- TCAIL null false-link 0.0375（合格）；calibration slope 0.130、ECE 0.179，概率不可直接使用。
- FOS F1 0.373，显著低于 standardized 0.729。
- 56/800 次拟合 `GRADIENT_TOLERANCE` 失败；512-row 支持弃权率 52.9%。
- 解盲后 q_M3-only 仍显著低于 standardized（−0.0322），失败不只是 conservative min。
- 先验敏感性稳定（Spearman 0.983–0.986）。
- cDLED/CGOMEA 是 static adaptation；SLL-MI、FBL incremental、DLED、LMM、ALI/AIM、GAwLL2 未运行。

### 不允许的下一步
- 不得复用 held-out 3000–3039 调参或重新宣称通过。
- 不得在 Estimator Gate 失败后运行 GOM 并声称 TCAIL 改善 EC。
- 不得把 q_M3-only 或 q_max 的事后结果写成预注册 Gate 通过。
- 不得调用真实 LLM API、训练 A800、启动 CI-GOM/IMCE-RSI 或完整 active acquisition。

### 下一会话可选方向（需用户决策）
1. **修复实现后重新预注册：** 相对梯度准则/更强优化器、random slopes/overdispersion、新的独立 held-out seeds（如 4000–4039），并预先声明 merge 规则。
2. **收窄主张：** 仅把 TCAIL 作为低支持/漂移下的 abstention 组件研究，不再声称普遍优于 direct contrast。
3. **转向 EC 价值：** 若 Oracle FOS 在该任务族仍显示上界价值，可单独研究“何时 linkage 值得学”，但必须先通过 Estimator Gate。
4. **补强基线：** SLL-MI、FBL incremental、DLED、LMM、ALI/AIM、GAwLL2。

### 可直接复制的接班提示词

你是 yujian777555/kaitibaogao 的实验 Executor。先核验远端 main HEAD，读取 README、05_DECISION_LOG、SESSION_HANDOFF（第 43 节）、`experiments/tcail_confirmatory_r1/R1_ESTIMATOR_GATE_RESULTS.md`、`results/summary.json`、`results/posthoc_diagnostics.json`、`experiment_config.json` 和 42 号协议。

当前结论是 ESTIMATOR_GATE_FAIL，GOM NOT RUN。不要重跑已解盲的 held-out 3000–3039 来调参。若用户要求继续，只允许以下之一：
A. 以新的独立 held-out seeds 预注册并复测修复后的估计器（相对梯度准则、random slopes/overdispersion、merge 规则先冻结）；
B. 收窄为低支持/漂移 abstention 研究；
C. 补强缺失基线。
任何新轮次必须保存原始数据、每 seed 结果、配置、环境、日志和独立重算；不得调用真实 LLM API、训练 A800、启动 CI-GOM/IMCE-RSI 或完整 active acquisition。失败结果不得删除。


## 44. 2026-11-05：TCAIL NO-GO 后的论文方向调整

完整重评见 44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md；决策见 D-047。TCAIL Estimator Gate 已失败，旧 CI-GOM 冻结，不得复用 held-out 3000–3039 调参。

新工作题目候选：《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》。两个核心候选：
1. 状态感知、契约约束的 Agent 恢复策略演化：将恢复控制器编码为 guarded finite-state policy，演化 verify/reconcile/retry/replan/compensate/rollback/escalate/abstain 决策；安全不变量为硬约束。
2. 故障场景—恢复策略双种群协同演化：在有效故障语法、挑战档案和 held-out fault families 下验证鲁棒泛化。

第三项跨任务恢复策略迁移暂作储备。通用 prompt evolution、blame-aware mutation、Pareto selection、failure-memory retrieval、transaction runtime 均已有直接工作，不能单独包装成创新。

下一步唯一任务：机制级文献差异矩阵 + Pilot A。先定义最小 stateful tool simulator、effect states、failure signatures、合法动作和硬不变量；实现 5–8 个手工恢复策略及 oracle 上界；配对运行并判断是否存在足够策略改进空间。若 oracle 不优于简单 retry/verify，停止。Pilot A 通过后才比较 random search、standard GA/GP、NSGA-II/III 和 contract-aware variation；再通过后才考虑双种群协同演化。

相关工作必须比较 GEPA、EvoTool、Q-Evolve、AgentEvo、GRSE、Sentry、AgentDebug/PROBE、ToolMaze、ReliabilityBench、Cordon、DelAct。LLM backbone 可固定并通过 API 使用；演化对象是结构化恢复策略。不得训练基模或启动无关模块。保存原始轨迹、配置、种子和 per-seed 结果，并维护 README、决策日志与 handoff。


## 45. A800 训练候选与 Pilot A 首轮接管（2026-11-05）

### 当前基线
- 工作分支：pilot-a-stateful-recovery（从 683b3fe7fc52c86e917d523fdc6bbb13abbfd653 建立）
- 最新主线：TCAIL NO-GO；新方向见 44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md
- 本轮决策：D-048
- 文献机制审计：46_RELATED_WORK_MECHANISM_AUDIT_ARWM.md
- Pilot A 代码与结果：experiments/pilot_a_recovery/

### A800 训练候选
ARWM（Agent Recovery World Model）：主 LLM 继续走 DeepSeek API；A800 训练辅助模型预测工具动作后的 effect-state、side-effect/invariant risk、postcondition 和 recovery outcome。训练数据应来自 simulator-grounded 同状态多动作反事实执行。ARWM 仅辅助候选策略筛选；真实 simulator rollout 才是最终 fitness 与安全门禁。该候选尚未实现/验证。

### 相关工作关键限制
- CoMAP (EMNLP 2026) 已闭环共演化 textual world model 与 Agent policy；其公开代码的 world model 以当前文本状态、目标、历史和动作预测下一文本状态，并用真实 next-state CE + teacher-logit distillation 训练。
- HarnessMDP 已从离线 rollout 学习冻结 LLM 的外部结构化控制器。
- TRACE/SENTINEL 已覆盖失败轨迹驱动的能力训练/目标任务生成。
- EvoTool 已覆盖 blame-aware tool policy mutation 与 diversity selection。
因此不得声称通用 world model、失败驱动训练、冻结 LLM controller 或工具策略进化本身新颖。ARWM 差异只能是配对反事实动作效果数据 + 结构化副作用风险/后置条件联合预测 + 校准不确定性门控 + 对约束 EA 固定真实 rollout 预算收益；须通过直接强基线验证。

### Pilot A 首轮结论
7 fault families × 10 deterministic parameter seeds；6 policies × 70 episodes。timeout-before-dispatch、timeout-after-commit、delayed-visibility 对策略暴露同一 TIMEOUT 观测，隐藏子类型仅 oracle 可见。
- state-aware handcrafted：success 0.8571、safe resolution 1.0、invariant violation 0、mean actions 3.0714；
- oracle upper bound：success 0.8571、safe resolution 1.0、violation 0、mean actions 1.5；
- blind retry：success 0.1429、violation 0.4286。

判断：CONDITIONAL HOLD。当前简单场景中手工规则已达到 oracle 成功/安全表现，只有动作效率差距；这不是足以启动大规模 EA 或训练 ARWM 的证据。已完成五项关键状态转移独立回归断言；仓库 pytest 文件尚未通过 GitHub Actions 实际运行。实验是探索性确定性模拟器，不是确认性统计证据。

### 下一步唯一任务：bounded Pilot A-2
增强任务复杂性，不得泄漏隐藏状态：
1. 多工具不同幂等性/补偿契约；
2. 同公开 TIMEOUT 下多个潜在执行结果与复合故障；
3. 随机化读可见延迟、部分提交范围和补偿可用性；
4. 任务族与故障组合族分离的 train/validation/held-out；
5. 对比 5–8 个可执行手工策略和 oracle，报告成功、安全、重复副作用、成本和 worst-group。

若强手工策略仍达到 oracle 成功/安全并接近成本，停止恢复策略路线。若仍有清晰可行策略空间，先做标准 GA/GP 与 contract-aware EA 对照。只有 ARWM 在 action-effect/risk 预测上超越 LightGBM/MLP，并且在固定真实 rollout 预算下提升 EA，才使用 A800 训练 ARWM。

不得启动 A800 训练、真实 LLM API、完整 EC 或 Co-evolution，直到 Pilot A-2 通过预注册 Gate。保留 kaitibaogao 为唯一毕业论文仓库。

### 可复制接班提示词

你是 yujian777555/kaitibaogao 的研究 Executor。先核验分支 pilot-a-stateful-recovery 和 main 的 HEAD；读取 README、D-047/D-048、SESSION_HANDOFF 第 44/45 节、44 号重评报告、46 号文献机制审计、Pilot A 代码/测试/结果。

当前 TCAIL = NO-GO。新方向是 stateful tool Agent recovery policy evolution + RSI；A800 ARWM 是条件候选。CoMAP、HarnessMDP、TRACE、SENTINEL、EvoTool 已覆盖相邻关键机制，不能声称泛化世界模型/失败训练/策略进化新颖。

Pilot A 首轮已显示：state-aware 手工策略 success 0.8571、safe resolution 1.0、violation 0，与 oracle 的成功安全表现持平；oracle 只在动作成本上更低。因此当前是 CONDITIONAL HOLD，禁止直接开始 A800 训练或完整 EC。

本轮只执行 bounded Pilot A-2：增加多工具幂等契约、潜在/复合故障、读可见延迟和补偿差异，冻结可观察接口与 held-out 划分；先比较手工策略与 oracle。若强手工策略仍匹配 oracle，则停止该方向。只有证明剩余策略空间后才比较 GA/GP 与 contract-aware EA；只有模型超越 LightGBM/MLP 且改善固定真实 rollout 预算下的 EA，才训练 ARWM。维护原始数据、每 seed 结果、配置、README、决策日志和 handoff。不要训练基模，不要调用真实 API，不要把研究计划当作实验成果。

ARWM 候选规格另见 `45_A800_TRAINED_RECOVERY_MODEL_CANDIDATE.md`。不要将其当作训练授权；当前 A800 训练仍 HOLD，须先完成 bounded Pilot A-2 并通过 M1/M2 前置证据。


### Pilot A 数据审计补充（2026-11-05）
注意：首轮报告的 unresolved 列已在 D-049 中更正。正确值依次为 blind retry 0.8571、verify-then-retry 0.5714、wait-verify-retry 0.4429、conservative escalation 0.0857、state-aware 0、oracle 0。原因是 state-aware/oracle 对权限失败执行 ESCALATE。其他指标不变。独立复现的 7 项状态转移/覆盖断言通过，但 GitHub Actions 没有运行记录，CI 尚未验证。不要引用旧 unresolved 数值。


## Pilot A-2 最新状态（2026-11-05）

- 分支：pilot-a-stateful-recovery
- Pilot A-2 代码：experiments/pilot_a_recovery/pilot_a2.py
- 测试：experiments/pilot_a_recovery/test_pilot_a2.py
- 结果：experiments/pilot_a_recovery/PILOT_A2_EXPLORATORY_RESULTS.md
- 机器可读摘要：experiments/pilot_a_recovery/pilot_a2_summary.json
- CI：run 42030194929 与后续 run 42030392313 均成功；最新 run 42030392313 的 job logs 显示 regression tests、Pilot A、A-2 和 pilot-a2-summary artifact upload 均完成（artifact ID 13415632289）。
- 结果：contract-aware success 0.7222 / safe 1.0 / violation 0；oracle diagnostic success 0.7778 / safe 1.0；差距 5.56pp。该差距只是模拟器探索信号，不是显著性或演化算法提升证据。
- 限制：双工具共享同一故障族；seed 只变延迟/限流；无 held-out task/fault composition。
- 当前门禁：CONDITIONAL GO to Pilot A-3；A800/ARWM 仍 HOLD。

### 下一步唯一任务：Pilot A-3
将每个工具的故障独立分配，构造真正跨步骤的 saga 部分提交、延迟可见、补偿失败、不同工具重试/幂等契约交互；冻结 train/validation/held-out task-family 与 fault-composition split。先跑强手工策略和 oracle，再引入 random search、GA/GP、contract-aware EA，全部固定真实 simulator rollout 预算。只有 EC 在 held-out 上超过强手工策略，才启动 ARWM 数据采集和 A800 训练。

不要把 A-2 的 5.56pp oracle gap 宣称为已证明的创新；不要直接开始大模型训练。


## 46. Pilot A-3 首版实现与待验证状态（2026-11-05）

### 项目边界与当前方向
- 唯一仓库：`yujian777555/kaitibaogao`。不得读取或混入其他 GitHub 仓库。
- 工作分支：`pilot-a-stateful-recovery`；main 保持独立，不要将实验分支直接合并。
- 最新已核验 main HEAD：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。
- TCAIL Estimator Gate 已 FAIL / NO-GO；旧 CI-GOM linkage 路线冻结，保留负结果。
- 当前主线候选：状态感知、契约约束的 Agent 恢复策略演化；第二项故障场景—恢复策略双种群协同演化暂候选；跨任务迁移储备。
- A800/ARWM 仍 HOLD；真实 LLM API、模型训练和双种群协同演化均未获授权。

### Pilot A 与 A-2 的证据边界
Pilot A 的 unresolved 指标已在 D-049 修正，不能引用旧数值。Pilot A 的手工 state-aware policy 与 oracle 在 success/safety 上持平，仅有动作数差异，不足以启动 EA。

Pilot A-2：
- 4 个双工具任务 × 9 个故障族 × 30 seeds；6 种策略，每种 1,080 episodes；
- contract-aware success 0.7222、safe 1.0、invariant violation 0；oracle diagnostic success 0.7778、safe 1.0；
- 5.56pp gap 是探索性模拟器信号，不是显著性或 EC 增益；
- CI run 42030194929 与后续 run 42030392313 均成功；最新 run 42030392313 完成 regression tests、Pilot A/A-2 和 artifact upload（pilot-a2-summary，ID 13415632289）；
- 主要缺陷：任务内工具共享故障族，且没有 held-out task/fault composition。
因此只 CONDITIONAL GO 到 Pilot A-3，不启动 A800。

### Pilot A-3 本轮交付
- `47_PILOT_A3_PROTOCOL.md`：冻结协议与 Pilot B 门禁；
- `experiments/pilot_a_recovery/pilot_a3.py`：三步 saga、每工具独立 fault vector、不同工具幂等/补偿契约、partial commit、delayed visibility、compensation failure、逆序补偿、七种策略、held-out cluster bootstrap；
- `experiments/pilot_a_recovery/test_pilot_a3.py`：15 项回归测试；
- `experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md`：实现范围和未验证边界；
- `.github/workflows/pilot-a-recovery.yml`：增加 A-3 simulator step，并上传 JSON 与 episode-level CSV artifact；
- README、D-051 和本 handoff 已更新。

### 冻结实验设计
六个三步 task families：
- Train：inventory_order_payment、calendar_order_ledger、customer_order_shipment；
- Validation：inventory_calendar_order；
- Held-out：return_refund_restock、subscription_ledger_notification。

故障组合：
- Train：single_timeout、timeout_then_rate_limit、partial_then_delay、schema_then_timeout；
- Validation：independent_mixed_val、partial_then_timeout_val；
- Held-out：partial_comp_failure、delay_rate_permission、triple_mixed。

预算：每策略 954 episodes（144 train、120 validation、690 held-out），七种策略共 6,678 policy episodes。Held-out 分为 task-only、fault-only、joint shift。所有策略共享 scenario IDs、seeds 和 fault realizations。策略只访问公开错误、工具契约与 VERIFY/WAIT 结果；隐藏 fault、真实 visibility time 和 compensation availability 只供诊断 oracle/离线审计。

策略：blind_retry、verify_then_retry、fixed_wait_verify、conservative_escalation、contract_aware、saga_aware、oracle_diagnostic。Oracle 只看当前步骤的潜在执行状态，是诊断参考，不是可部署策略，也不保证全局最优。

A-3 Pilot B gate：saga_aware 必须在 task-only、fault-only、joint-shift 三个 held-out slice **各自**达到零 invariant violation；随后还需 oracle-success gap ≥ 0.05 且按 task-family × fault-composition 的 paired cluster bootstrap 95% CI 下界 > 0。任一 slice 有安全违规即 HOLD；只有动作成本差异不能触发 GO。若全部 slice 零违规、success gap ≤ 0.02 且动作成本差 ≤ 10%，则该模拟器任务族 NO-GO。

### 当前真实状态（务必准确）
**SPECIFIED：** A-3 协议已冻结。  
**IMPLEMENTED：** A-3 simulator、15 tests、CI workflow step 和 artifact upload 已写入分支。  
**TESTED：** 尚未核验本轮 Actions run；不得声称 15 项测试已通过。  
**EXPERIMENTAL RESULTS：** 尚未检查 A-3 JSON/CSV；无 A-3 结果。  
**GATE：** A-3 gate 尚未评估；Pilot B 未获准；A800/ARWM 继续 HOLD。

### 下一会话唯一任务
1. 核验 `pilot-a-stateful-recovery` 最新 HEAD 与 main HEAD；确认 main 未被修改。
2. 检查本轮 push-triggered GitHub Actions run（工作流 `.github/workflows/pilot-a-recovery.yml`）。必须确认 regression tests、Pilot A、Pilot A-2、Pilot A-3 和 artifact upload 均成功。
3. 如果 CI 失败，先定位并修复，不得绕过测试；修复后重新运行。
4. 如果 CI 成功，下载 `pilot-a3-results` artifact，独立复算 JSON 与 CSV：
   - 6,678 policy rows；每策略 954；
   - train 144、validation 120、held-out 690；
   - scenario IDs 与 seeds 跨策略完全配对；
   - per-tool fault vectors 独立，held-out task/composition 无训练泄漏；
   - summary、worst-group、paired cluster bootstrap 与原始 CSV 一致。
5. 按 47 号预注册门禁判断是否 CONDITIONAL GO to Pilot B。Pilot B 才比较 random search、standard GA/GP、contract-aware EA，必须同真实 simulator rollout budget；held-out 只能最终评价。
6. 不要在 A-3 gate 前启动 Pilot B、A800/ARWM、真实 LLM API 或双种群 co-evolution。失败数据必须保留。

### 可直接复制的接班提示词
你是我的河北工业大学计算机技术硕士开题研究 Executor。唯一允许读取和维护的仓库是 `yujian777555/kaitibaogao`，严禁读取其他 GitHub 仓库或混用其他项目。工作分支是 `pilot-a-stateful-recovery`，main 必须保持独立。

先核验远端 main 与工作分支 HEAD，读取 README、05_DECISION_LOG 的 D-047–D-051、SESSION_HANDOFF 第 44–46 节、44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md、46_RELATED_WORK_MECHANISM_AUDIT_ARWM.md、47_PILOT_A3_PROTOCOL.md、experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md、pilot_a3.py、test_pilot_a3.py 和 workflow。

TCAIL Estimator Gate 已 FAIL / NO-GO，旧 CI-GOM 冻结。新主线是状态化工具型 LLM Agent 的故障恢复策略演化与 RSI。Pilot A-2 只 CONDITIONAL GO to Pilot A-3；A-2 的 5.56pp oracle gap 不是算法证据。A800/ARWM 仍 HOLD。

当前 A-3 已实现，但**CI 和实验结果尚未核验**。你的唯一任务是检查 push-triggered Actions run；确认 15 项测试、A1/A2/A3 执行和 artifacts 上传。成功后下载 JSON/CSV 并独立重算，验证 6,678 行、每策略 954 episodes、split、配对和 fault-vector 语义；失败则修复并重跑。最后严格按 47 号预注册 gate 判断是否进入 Pilot B。

不得将实现写成测试通过，不得将 A-3 模拟器结果写成真实 Agent 证据，不得提前启动 Pilot B、A800/ARWM、真实 LLM API 或双种群协同演化。每轮继续更新 README、05_DECISION_LOG、SESSION_HANDOFF 并核验远端。


## 47. 强制接管提示词维护制度（2026-11-05）

**唯一权威接管提示词：`NEXT_SESSION_PROMPT.md`**

今后每次实质性研究、实验、代码、协议、审计、分支或决策变化后，必须在同一轮更新：
1. `NEXT_SESSION_PROMPT.md`（自包含、可直接复制、唯一下一任务）；
2. `SESSION_HANDOFF.md`（详细历史与上下文）；
3. `05_DECISION_LOG.md`（证据、决策、限制、下一步）；
4. `README.md`（当前阶段和状态）。

会话结束前必须重新读取四份文件，检查内容一致，并核验接管提示词对应的最新远端 HEAD。若 CI/实验未运行或未核验，必须明确写未运行/未核验；不得推断成功。每次向用户汇报时必须说明接管提示词是否已更新，并附仓库链接。不得只在聊天中维护提示词。

当前 canonical prompt 已建立：`NEXT_SESSION_PROMPT.md`。当前唯一下一任务仍为：核验加入 A3 步骤后最新 GitHub Actions run，下载并独立复算 A3 JSON/CSV，再按 47 号协议决定 Pilot B。A3 CI 和结果尚未核验；Pilot B、A800/ARWM、真实 LLM API、双种群协同演化继续 HOLD。


## 48. 大论文当前定位澄清（2026-11-06）

### 当前工作题目（尚未冻结）
**《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》**

该题目来自 44 号方向重评，是当前聚焦后的工作题目。旧题目《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》属于 TCAIL/CI-GOM 交互结构旧路线；TCAIL Estimator Gate 已 FAIL / NO-GO，旧路线冻结。不得继续把旧题目作为当前论文题目。

### 研究问题
演化计算能否搜索可执行、契约约束的 Agent 恢复控制器，在状态化工具执行的超时歧义、部分提交、延迟可见、重复副作用和补偿失败下，提高未见任务/故障组合的恢复能力，同时满足硬安全不变量；并进一步形成跨轮反馈、策略更新、再验证的 RSI 闭环？

### 创新点候选结构
1. **核心候选一：契约约束的恢复策略演化。** 进化个体是带守卫条件的有限状态恢复控制器；候选机制为类型化表示、契约感知变异/重组与修复、feasibility-first survivor selection。尚未证明优于强手工策略或标准 EA。
2. **核心候选二：故障场景—恢复策略双种群协同演化。** 研究未见故障泛化；必须等候选一通过后再启动。
3. **储备候选三：跨任务恢复策略迁移与能力保持。** 暂时冻结，不为凑足数量纳入正式创新点。
4. **ARWM/A800：** 仅是有条件的辅助模型路线，需证明模型预测价值及固定真实 rollout 预算下的 EA 收益；目前 HOLD，不等同于第二创新点。

### 当前证据成熟度
- TCAIL Estimator Gate FAIL / NO-GO，旧 CI-GOM 冻结。
- Pilot A 的 unresolved 指标已纠正；初始 state-aware 手工策略与 oracle 在成功/安全上持平。
- Pilot A-2 仅为探索性结果：contract-aware success 72.22%，oracle diagnostic 77.78%，两者 safe 100%；未证明 EC 增益。
- Pilot A-3 协议、模拟器、15 项测试用例和 CI workflow step 已提交；本轮 A3 CI 尚未核验，JSON/CSV 尚未独立复算。
- Pilot B 未启动；尚无 Random/GA/GP/NSGA-II/III/contract-aware EA 的同预算比较。
- RSI 多轮恢复策略更新和未见任务持续改进尚无实验证据。
- 旧开题稿 V0.1–V0.3 基于 TCAIL/CI-GOM，不能直接作为当前方向正式开题稿；可审计复用其背景和参考文献，但研究内容、创新点、技术路线和可行性须重写。

**结论：** 大论文方向已比原来聚焦，但尚未进入最终开题定稿或大论文正文阶段；当前是新方向的预实验和算法可行性验证阶段。当前唯一下一任务仍为 A-3 CI 核验及原始结果独立复算。


## 49. 第一项创新相关工作审计（2026-11-06）

详见 `49_FIRST_INNOVATION_RELATED_WORK_AUDIT.md`。初步检索确认近邻工作较多，尤其：
- UndoBench arXiv:2610.05622：恢复 benchmark、lost-ACK paired trials，并纳入受零权限限制的 EvoUndo-RB1；
- EvoUndo arXiv:2608.28363：recoverability-constrained harness self-modification；self-evolution 不等于 EC，但与 effect contract / counterfactual recovery 高度相关；
- EvoTool ACL 2026：已做模块化 tool-use policy 的 gradient-free evolutionary optimization，blame-aware targeted mutation 和 diversity selection；
- LIMBO / Where Does Exactly-Once Live? arXiv:2609.29095：late commit、idempotency、missing read path、duplicate side effects；
- Cordon、Atomix、SagaLLM：transaction/commit/rollback/compensation；
- Verified Tool Calls、Repair Economics：verify-before-retry、idempotency 和 fault-injection policy benchmark；
- CDGP、GP controller synthesis、FSM-MOEA、SMC-ES：安全程序/控制器的进化合成和反例验证基础。

因此第一项创新不能只叫“用 GA/NSGA-III 优化 Agent 恢复策略”。目前仅保留待验证假设：**契约语义保持、反例驱动的可执行恢复 FSM 演化**，并在硬安全约束下验证跨任务/故障组合泛化。所有组件都需消融，且必须与 EvoTool、EvoUndo、标准 GP/EA、事务型 runtime 和安全控制器合成基线比较。

Pilot A-2 的 fault-injection testbed 本身不具新颖性；A-3 作为内部实验环境可继续，但需与 UndoBench、LIMBO、Repair Economics、FAILING TOOLS 做 feature-level comparison。当前 A3 CI/JSON/CSV 未核验，Pilot B 未授权。

### 下一任务（Pilot B 前置门）
完成 UndoBench、EvoUndo、EvoTool、LIMBO 和 Cordon/Atomix/SagaLLM 的全文机制级对照，并核验 A3 CI/原始数据；只有 A3 预注册 Gate 与 novelty/baseline review 均通过，才授权 Pilot B。


## 51. 数据集官方信息复核与下一步执行计划（2026-11-06）

执行计划见 51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md；数据选择见 50_DATASET_SELECTION_AND_VALIDATION_PLAN.md。

### 官方信息已核验
- ToolMisuseBench REALM 2026：seed-42 v0.2 large 为 6,000 train / 900 dev / 1,200 public-test records；HF 数据卡明确其中 600 条为 output-grounded tasks，最终评分分母需审计官方 evaluator。论文报告 Parser+Repair task success 0.767、conditional recovery success 0.736、recovery-disabled task success 0.158；这些是论文数值，不是本项目复现结果。
- UndoBench 当前数据卡版本 v1.0.1：36 workflows，DEV 14 / validation 10 / TEST 12；数据/spec CC BY 4.0，软件 Apache 2.0；frozen TEST 需要显式 opt-in。
- ThinkingBox-Bench v1.0：507 tasks / 5 domains；evaluation-only，不得用于演化搜索或调参，只能方法冻结后做 clean regression。

### A-3 当前状态（严格按仓库证据）
47 号协议为 PRE-REGISTERED / NOT RUN；A3 implementation status 为 IMPLEMENTED / NOT YET VALIDATED BY CI / RESULTS NOT YET RUN OR ACCEPTED。15 项测试和 artifact upload workflow 已编写，但未核验实际 Actions run、日志和 artifact。因此 A-3 未通过，Pilot B 不得启动。

### 下一步唯一执行优先级
Phase A：找出 A-3 对应 Actions run，核验 head SHA、job/step、15 项测试和 simulator run；下载 JSON/CSV artifact，计算 hashes，独立重算全部指标并应用 47 号 Gate。并行开展 ToolMisuseBench / UndoBench revision、manifest、license、split leakage、evaluator denominator 与故障覆盖审计。A-3 Gate、数据兼容 Gate、adapter smoke 均通过后，才起草 Pilot B 预注册协议。

HOLD：Pilot B、UndoBench TEST、ThinkingBox 优化、A800/ARWM、真实 LLM API。每次接管会话继续维护 NEXT_SESSION_PROMPT.md。


## 52. Phase A 执行轮：A-3 CI 修复、独立复核完成、Gate = HOLD（2026-11-06）

本节为 Phase A 的实际执行记录，覆盖此前"A-3 待核验"状态。完整证据见 `PILOT_A3_INDEPENDENT_REAUDIT.md`（独立复核报告）、`experiments/pilot_a_recovery/a3_artifact_manifest.json`（哈希清单）、`experiments/pilot_a_recovery/a3_recompute_report.json`（独立重算表）。

### 52.1 CI 核验发现：A-3 结果此前根本不存在
- workflow `Pilot A recovery simulator` 在 `76f62c09`（"Run Pilot A-3 and archive episode-level results in CI"）之后的全部 7 个 run 均失败于 "Run Pilot A-3 simulator" 步骤，artifact 上传全部 skipped。
- 根因：`recover_tool` 中 `tool.retry_after - tool.tick` 经 `PublicToolView` 读取运行时时钟 `tick`，而该门面按设计只暴露 `contract`/`retry_after`/动作方法 → `AttributeError: 'PublicToolView' object has no attribute 'tick'`。rate-limit 恢复分支必崩；15 项测试未覆盖该路径，所以测试全绿而模拟器必败。
- 因此：旧文档中"A-3 已实现"一直成立，但"实验已运行"从未成立；旧 run 42030194929/42030392313 只覆盖 A1/A2。

### 52.2 修复（commit `f5e6b46`）
- 可部署策略改为按公开 `retry_after` 自行计数等待；`PublicToolView` 可见边界保持不变（与 `test_policy_view_hides_latent_simulator_labels` 一致）。
- `oracle_recover` 保留特权 `tick`/`visible_at`（直接持有 `ToolRuntime`，属协议允许的诊断参考）。
- 新增第 16 项测试 `test_recover_tool_never_touches_hidden_runtime_fields`：6 种可部署策略 × 7 种公开错误签名逐一驱动公开门面。测试总数 28（A-3 部分 16 = 15 预注册 + 1 崩溃回归）。

### 52.3 被审计运行与 artifact
- run **42241224898**，head SHA `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`，push 触发，结论 success。
- 步骤核验：28 项测试逐条在日志中出现并 OK；A1/A2/A3 模拟器步骤全部成功；`pilot-a3-results` 上传成功。
- 哈希：ZIP `1119d14b70eedef221fe6e63439e2a04bd58c0354d5a723344d2c80c459ab727`（= GitHub digest）；JSON `3a60ae8385c723c57d54ff47608fe428690d94519f6762ec78bbc15c1d15fe14`；CSV `2c7d7dad5faaae58f182f27d77b90dfa237f4c1627e15b0bc029d34582f3c369`。
- 原始文件保存在 `experiments/pilot_a_recovery/ci_artifact/`（`.gitattributes` 设 `-text` 保字节）；本地重跑 CSV 逐字节一致，模拟器确定性成立。

### 52.4 独立重算与审计结论
- 结构：6,678 行；每策略 954（144 train / 120 validation / 690 held-out）；954 scenario 七策略完全配对（同 seed、同 fault vector）；split 因子化与 47 号 §3 零偏差（45 个 task×composition 组合）。
- 语义：逆序补偿（rollback 仅 saga/oracle、顺序为逆前缀）、补偿失败不冒充成功、unresolved/safe/violation 逐行一致。
- JSON 汇总 vs CSV 独立聚合：0 处偏差。
- Bootstrap：23 个 task×composition cluster，oracle−saga 配对差全为 0，CI [0.0, 0.0]（seed 42 敏感性相同）。

### 52.5 预注册 Gate 判定（47 号 §6 原文）
| 条件 | 实测 | 判定 |
|---|---|---|
| 每个 held-out slice saga_aware 零违规 | 三 slice 均 0.0 | 满足 |
| oracle − saga 成功率差 ≥ 0.05 | **0.0** | 不满足 |
| bootstrap CI 下界 > 0 | **0.0** | 不满足 |

gap ≤ 0.02 但动作成本差 +34.63% > 10% → 不构成 NO-GO；按协议"其他情况"分支 **判定 HOLD（HOLD_REVIEW_FAILURE_BOUNDARIES）**。Pilot B 不启动。

### 52.6 失败边界定位
- `partial_comp_failure`、`delay_rate_permission` 两个 held-out 组合族对全部 7 策略（含 oracle）0% 成功（占 held-out 52.2%）——结构性不可行死区，特权信息只能省动作。
- 任务族漂移 slice：saga_aware 97.5% 成功、零违规——策略跨任务族泛化良好。
- 唯一可优化维度是动作成本（saga 10.17 vs oracle 7.56，+34.6%）。
- 不得在查看该批 held-out 后调参再宣称通过；若继续需新预注册 A-3b（可行性分层指标/补充可行组合族/动作成本目标），保留 A-3 结果不动。

### 52.7 授权状态与下一步
- GO：文档维护；ToolMisuseBench / UndoBench 只读数据集审计（Phase B）；A-3b 协议设计（先批准后运行）。
- HOLD：Pilot B 演化搜索；用 A-3 held-out 调参；A800/ARWM；真实 LLM API；UndoBench frozen TEST；ThinkingBox 优化。
- 下一会话唯一任务：Phase B 数据集审计 + A-3b 新预注册设计。维护要求不变：每轮更新 NEXT_SESSION_PROMPT.md、SESSION_HANDOFF.md、README.md、05_DECISION_LOG.md 与 51 号计划状态。


## 53. Phase B 执行轮：数据集审计完成 + A-3b 设计（2026-11-06）

覆盖 §52.7 的"下一会话任务"。完整证据见 52/53/54 号审计、SPLIT_LEAKAGE_AUDIT.md、LICENSE_AND_PROVENANCE.md、DATASET_LOCK_MANIFEST.json、55_PILOT_A3B_RESEARCH_DESIGN.md；复现与 smoke 证据在 `experiments/dataset_audit/`。

### 53.1 ToolMisuseBench（rev 98eb2871，MIT）
- 规模实测 6,000/900/1,200；三文件 SHA-256 与官方 manifest 吻合；task_id 跨 split 零重叠。
- **评分口径解密**（用官方发布的 per-task episodes 独立复算）：0.767=全 1,200 TaskSuccess（复算 0.7667）；0.736=993 条故障任务的条件恢复（731/993=0.7362）；0.158=no-recovery 全量（0.1575）；600 output-grounded 是 `tool_output_path_equals` 子集（0.8783），非头号分母。
- **语义缺口（env/fault 代码取证）**：故障全在 before_call 拦截（无 lost-ACK）；环境幂等（重复副作用不可能）；故障单次触发（重试必恢复）；无补偿/幂等合同/部分提交/late commit/saga；双故障同工具。无结构性不可恢复场景。
- **Parser+Repair 逆向**：指令正则解析+错误码修参（别名映射 id↔doc_id↔account_id），无验证/补偿/等待/升级。**DEV 复现**：900 条 TaskSuccess 0.7622、条件恢复 0.7363；no-recovery 0.1511。必须列为 Pilot B 基线（解析强≠恢复强）。

### 53.2 UndoBench（rev 4be11518，CC-BY-4.0 / Apache-2.0）
- 36 行全量画像：33/36 SCN-LOST-ACK、全部 UNKNOWN_OUTCOME、idempotency_support 全 false、IRREVERSIBLE 8、forbidden_effects 22、19/36 多工具；指标 CRSR/DER/MER/URR/EOR 与我们语义同构（CRSR 条件在 CONTROL 成功）。
- **harness 实测**：doctor PASS（36 任务/47 工具/沙箱）、smoke PASS（CONTROL/FAULT/oracle/effect-log 全链路）、DEV 14 对示例 agent 跑通指标计算；内置 TEST 锁 `allow_frozen_test_execution: false`；TEST 未执行。
- 定位：外部泛化验证（TEST 锁箱一次性）+ DEV 24 条接口适配；不做主搜索（样本小且 test 同质 lost-ACK）。

### 53.3 ThinkingBox — 不可达
HF 401（gated/移除）+ GitHub 404。507 任务/evaluation-only 声称无法复核；继续按 evaluation-only 保守处理，不规划依赖实验。

### 53.4 泄漏审计摘要
ToolMisuseBench 模板级泄漏（72–73 模板跨 split、工具全重叠）→ 只能主张实例泛化；UndoBench 领域全重叠、test 同质 → 只能主张工作流泛化；A-3 因子化 OOD 保持唯一双因子干净来源。

### 53.5 A-3 gap=0 根因（写入 55 号 §0）
(a) 可行单元 saga 已达 oracle 水平；(b) held-out 52.2% 结构性死区稀释差异；(c) Gate 只认成功率、效率差异 +34.6% 无预注册地位；oracle 仅当前步、非上界（次因）。修正=可恢复性分层+效率目标+重划 held-out；**不删困难场景**。

### 53.6 A-3b 设计草案（55 号，未批准未运行）
R1/R2/R3/R4 可恢复性分类（评估器侧判定，与策略/oracle 隔离）；分母纪律（CondRecSucc 只算 R1+R2，R3+R4 计 CorrectEscalation）；硬约束 P(violation)=0；目标 min(C_recovery, C_side-effect, C_intervention)；两个可消融机制（A 契约语义保持算子、B 反例驱动）；基线 Random Search/GA/GP/NSGA-II/NSGA-III/手工规则/oracle 诊断；cluster bootstrap+置换+Holm；停止条件与失败预案预登记；A-3 旧 held-out 退役为历史诊断。

### 53.7 授权状态与下一步
- GO：55 号独立审查→预注册冻结（需用户批准）→ 实现分类器/场景生成器/adapter（Phase C 仅 train/dev/validation smoke）。
- HOLD：A-3b 运行、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 执行、ThinkingBox 任何用途、锁箱调参。
- 下一会话唯一任务：55 号独立审查并冻结预注册；未冻结批准前不得运行任何 A-3b 实验。


## 54. Pilot A-3b 独立审查结果（D-059，2026-11-07）

审查报告：`56_PILOT_A3B_INDEPENDENT_REVIEW.md`。当前分支新增 56 号审查文件；55 号原草案保留不覆盖。

### Gate
- Phase B：GO / 完成（ToolMisuseBench 与 UndoBench 真实下载、版本/hash、DEV 复现/Smoke、覆盖语义与泄漏审计；ThinkingBox 不可达）。
- 55 号：REQUEST CHANGES，不可直接预注册。
- A-3b：HOLD，未运行。
- Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox：HOLD。

### 必须修复的核心问题
1. R4 不可达零残留安全终态，却被要求 CorrectEscalation(R3+R4) 零残留；R4 应独立评价 DamageContainment。
2. R2 包含优雅失败/安全放弃，却进入 CondRecSucc；应把“补偿后完成”与“安全回滚/放弃”分开。
3. Recoverability 必须按仅依赖公开观测历史的 contingent policy 可达性判定；隐藏状态只供 evaluator，未知类不得强行分类。
4. 有限测试集只能报告 zero observed violations + 置信上界，不能声称经验上证明总体 P=0。
5. R4 unavoidable residual 与可避免损害分开；R3/R4 正确升级不能被统一成本惩罚。
6. 明确 3:1 是 (R1+R2):(R3+R4) 还是 R3:R4，给出每 split 每 slice 四类计数；按独立 task-family×fault-composition clusters 做功效分析。
7. A/B/A+B 消融固定同一 NSGA-II 骨干；所有 EA 共享初始化分布；NSGA-III 单独作强基线。
8. 明确 50k rollout 是每方法总预算还是每 seed 预算，所有实际 rollout 计费。
9. 主检验必须对最强标准 EA，而不仅是手工策略/随机搜索。
10. 49 号是初步文献扫描，novelty 未批准，需补系统性机制级审计。

### 下一会话任务
创建 `55_PILOT_A3B_RESEARCH_DESIGN_R1.md`，逐条回应 56 号 B1–B6/M1–M5；完善 R1–R4 互斥定义、reachability checker 规格、指标和成本、分层配额、cluster-level power、rollout budget、公平算法骨干和新颖性审计。可进行定义/分类器单元测试和 train/dev smoke；不得运行正式 A-3b，直到 R1 独立审查并获用户批准。


## 54. 55-R1 落地 + 判定器验证 + 机制诊断首轮（2026-11-07，D-060）

覆盖 §53 之后、D-059 所列任务。证据：`55_PILOT_A3B_RESEARCH_DESIGN_R1.md`、`experiments/pilot_a3b/`（代码+测试+结果 JSON）。

### 54.1 55-R1 修订（B1–B6/M1–M5 全部处置）
R1–R4 互斥重定义 + UNKNOWN：R2 成功=最终任务完成（安全放弃→R3 SAFE_ABORT）；R3 正确升级计成功；R4 不要求零残留、区分 UnavoidableResidualBurden 与可避免损害；可达性=信念态 AND-OR 观测策略鲁棒可达（horizon 12、动作类型化、截断→UNKNOWN、标签独立于被测算法）；安全主张分层（禁 P=0）；必要升级不入成本目标；配额 3:1≡(R1+R2):(R3+R4) 逐 split 计数；同初始池/同 NSGA-II 骨干/同预算归因；primary contrast=A+B vs NSGA-II。

### 54.2 可恢复性判定器（Stage 1 已过）
`reachability.py`：belief-state AND-OR 求解器 + 五级分类器 + 策略证书。`mini_env.py` 12 类 ground-truth 环境覆盖用户要求的全部情形（直接/补偿后/仅升级/不可恢复/同观测异隐藏/延迟提交/lost-ACK/补偿失败/重复副作用/超深度/部分 θ/saga 残留）。**27 项测试全绿；混淆矩阵 12/12 纯对角（R1×5、R2×2、R3×1、R4×2、UNKNOWN×2 设计内）**；资源截断正确返回 UNKNOWN；R2 无补偿不可达、R4 零残留不可达等语义护栏测试通过。

### 54.3 机制实现（Stage 2）
`a3_bridge.py` 复用 A-3 `ToolRuntime/PublicToolView`（未重建模拟器）+ FSM 基因组（守卫×宏动作）+ **A=契约语义保持修复算子**（非幂等×歧义禁裸重试等）+ 解析标签器（发现并修复 timeout_after 不可补偿残留漏判 R4 的 bug，含回归测试）。`ea.py`：NSGA-II 骨干、NSGA-III、GA、Random、**B=反例聚类+定向变异+≤2× 加权**。强手工基线对齐 saga_aware（初版过弱已修正）。

### 54.4 诊断实验（DIAGNOSTIC，非确认性）
216 个新生成场景（新 seed，非 A-3 旧 held-out）；标签 R1 96/R2 50/R3 36/R4 34；吞吐 ~97k eps/s；每方法每 seed 108,864 真实 episodes；3 seeds；同纯随机初始池（M1：手工种子混杂已发现并排除）。

**结果（cond_rec 三种子均值）**：hand 1.000 > A 0.968 > AB 0.938 > ga 0.911 > nsga3 0.902 > B 0.872 > nsga2 0.838 > random 0.575。

**机制 A 决定性效应：非法候选率 1.000→0.000**（A/AB 全合法；其余全部方法含 NSGA-II/GA 为 1.000）；A/AB 全 seed 零违规 vs 对照最高 8%。

**统计（54 cluster 配对 bootstrap + 置换 + Holm）**：primary AB vs NSGA-II Δ=+0.049、CI95 [−0.017,+0.122]、p=0.27——**方向正、不显著（功效不足，如实报告）**；AB vs A −0.006（B 本预算下稀释 A）；AB vs hand −0.026（未超过强手工）。

### 54.5 判定
- 契约语义保持算子（A）**有真实机制证据**（非法率消除+零违规+成功率方向性提升）；
- H1（A+B 超标准 EA 与手工规则）**未成立**，需功效足够的正式 A-3b；
- 第一项创新：**方向可行、未证实**；B 机制首轮信号弱待迭代。

### 54.6 授权与下一步
- GO：诊断级实验/代码、功效核算、49 系统检索、预注册材料准备。
- HOLD：正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、锁箱调参。
- 下一会话唯一任务：用本轮 54-cluster 方差做功效核算定正式实验规模 → B/A 机制迭代 → 49 系统检索 → preregistration candidate 交用户批准。未批准前禁止正式 A-3b。


## 55. D-060 首轮诊断的独立复核（D-061，2026-11-07）

完整报告：`57_PILOT_A3B_DIAGNOSTIC_INDEPENDENT_REAUDIT.md`。

### 仓库与 artifact 复核
- 远端 HEAD `edfc7ad0156617dccc4e4bf998df33f991ae921f`；main `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；ahead 94 / behind 0。
- 原始 diagnostic JSON 可解析：216 scenarios、24 method-seed runs、每 run 216 rows、scenario ID 完全配对。
- 正确类别计数 R1=96/R2=50/R3=35/R4=35；旧文档 36/34 为记录错误。
- 实际 episodes：hand 每 seed 216；搜索方法大多 108,864；A seed23=108,648（cache hit）。不能写所有方法/seed 实际执行数完全相同。
- 当前 commit 无 GitHub status checks；55/55 为本地测试报告。

### 核心阻断问题
1. 当前所谓 FSM 实为静态三元组查表，不具备状态记忆；任意未使用规则含 COMP 会触发全局 Saga rollback。
2. 任何恢复失败都会自动设置 escalated=True，R3 CorrectEscalation 不能证明策略明确升级。
3. R4 scorer 只看 escalation 和 duplicate，不检查可避免残留/最小可达损害；R4 residual 被整体排除。
4. action cost 在全体 rows 上平均，仍惩罚 R3/R4 必要升级。
5. A-3 216 场景由启发式 label_scenario 标记，未逐场景经过 AND-OR checker；6 组 sanity test 不足以证明全场景标签。
6. B pool 每次 update 清空；scenario_weights 从未使用；定向变异未定位错误签名；B/AB targeted branch 额外 mutation。
7. A 的 legality metric 与 repair 共用 ILLEGAL 表，validator 不完整；这不是独立安全证明，且 NSGA-II/GA 也零观察违规。
8. Reachability horizon cutoff 返回 False/ proved=True，可能错误降级为 R3/R4；必须 tri-state。
9. stats.py 平均 per-seed CI/p 不构成有效 pooled inference。独立 pooled cluster 探索重算 AB−NSGA-II Δ≈+0.0494、CI≈[-0.0031,+0.1034]、p≈0.0874，仍未显著，须实现正式 hierarchical/pooled 统计脚本。
10. NSGA-II/III/GA 当前实现并非完全 canonical；无 GP，Random 使用 Pareto survivor selection，须修正或准确命名。
11. 55-R1 的 3:1 文字与表中 3:2/58:38 配额冲突，必须冻结前修正。
12. 原始 artifact 的 R3/R4=35/35；D-060 旧记录 36/34 必须以 D-061 更正。

### 研究结论
D-060 只可作为诊断线索；不能声称 A 已证明安全提升、B 已验证、A+B 已超过标准 EA。A 的内部规则修复行为可保留，但不是独立语义安全证据。第一项创新继续验证，不放弃；正式 A-3b 仍 HOLD。

### 下一会话优先级
先修 controller/evaluator/labels/B/statistics/baselines 和配额矛盾，再用新诊断场景重跑。**暂不做功效分析，不扩大 rollout**，因为当前效应指标尚不可信。保留 D-060 原始 artifact，不覆盖。正式 A-3b 需独立复审和用户批准。


## 55. D-061 执行轮：57 号修复落地 + 第二轮诊断（2026-11-07）

完整记录：`58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md`。数据：`diagnostic2_results.json`（manifest d4fb2be680e74f2e…）+ `diagnostic2_stats.json`；D-060 `diagnostic_results.json` 保留。

### 55.1 修复（F1–F8/S1–S3 全部处置，47/47 测试绿）
真状态化 FSM + 显式补偿日志（隐式回滚已删）；升级事件三分（显式/强制/原因）；R4 四量损害记账；R1/R2-only 成本目标；A-3 标签解析证明器+检查器 309 模式穷举交叉（0 硬矛盾）；B 全种群聚合+涉事基因定位+权重进评价+预算对齐；独立 contract_validator；三值可达性+环检测；pooled hierarchical 统计；标准 NSGA-II/III/GA/Random（GP 排除）；train/val 分离。

### 55.2 第二轮诊断结果（8 方法×3 seeds，316,224 eps/method/seed）
- **A vs NSGA-II Δ=+0.239 [0.193,0.284] Holm p=0.0014（d=1.56）**；独立 validator 非法率 A/AB=0 vs 其余=1.0。
- primary AB vs NSGA-II +0.126（p=0.0002, d=0.82）显著。
- **AB vs A −0.113（p=0.0014）：B 叠加有害**；B 单独 +0.082（弱）。
- AB vs hand −0.514：**未超强手工**（hand 0.827）。
- Q6 验证集 AB vs NSGA-II +0.148（p=0.002, d=0.97）——泛化成立。
- 开放：环境违规率 A 0.36 vs hand 0.006（观测歧义 WAIT-SLA 时序属行为层）。

### 55.3 判定与下一步
机制 A 有真实显著证据；B 组合主张不成立；第一项创新**部分成立**。下一步：重设计 B 反例→基因映射 + 状态化 WAIT-SLA 契约修复，复测违规率后 A+新B 同配置重跑。正式 A-3b/功效分析继续 HOLD。


## 56. D-062：WAIT-SLA 行为安全与反例驱动演化（2026-11-08）

完整任务计划：`59_D062_WAIT_SLA_AND_COUNTEREXAMPLE_REDESIGN_PLAN.md`；完整接管提示：`NEXT_SESSION_PROMPT.md` 的 D-062 节。

### 当前基线
- 建立计划时 branch HEAD：`ac042b4e96b80edb8ca727009f0e34ef32179a1f`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；ahead 102 / behind 0。
- 58 号报告记录 D-061：A vs NSGA-II Δ=+0.239（Holm p=0.0014）；AB vs A Δ=-0.113（p=0.0014）；AB vs Hand Δ=-0.514；报告的环境行为违规率 A=0.36、Hand=0.006。
- 这些是报告结果，D-062 必须从 `diagnostic2_results.json` 和 episode 轨迹独立复算，特别核对 0.36/0.006 的分子、分母和口径。
- D-060/D-061 原始 artifact 均保留，禁止覆盖。
- 建立计划时当前 commit 无可读取的 status checks；workflow 仅触发 `experiments/pilot_a_recovery/**`，不会自动覆盖 `pilot_a3b/**`。

### 研究判断
A 有正向诊断证据；B 叠加到 A 后显著有害；A+B 未超过强手工策略；第一项创新部分成立，尚未达到投稿标准。不能把 D-061 汇总值直接升级为已独立验证事实。

### D-062 唯一首要任务
**先独立复核 D-061 环境行为违规率 A=0.36 vs Hand=0.006，并定位每条重复副作用的完整轨迹。** 复核必须区分 episode/action 分母、同 episode 重复事件、task/fault/seed/genome 分布，并还原公开观测与策略动作。判断提交未发生、lost ACK、已提交但未可见、仍处理中、结果未知和无可见性保证等不同情形。先完成独立脚本和审计报告，未通过前不扩大 rollout。

### 后续实现路线
1. 定义 WAIT-SLA 工具合同：visibility SLA/保证类型、query consistency、idempotency/key、safe retry、compensation、retry window、max wait/decision budget、escalation；区分 visibility SLA 与 retry SLA。
2. 实现状态化 WAIT-SLA，策略只能使用公开观测和自身状态。没有可证明 visibility guarantee 时，固定等待不能把 UNKNOWN 推断为 NOT_COMMITTED。
3. B-new 使用完整失败轨迹定位涉事 FSM 基因邻域；语义修复型变异替换普通变异，不能增加 mutation/rollout 预算，记录变异前后差异。
4. 比较独立 Contract Validator、关键行为 Safety Gate 和硬安全优先的分层生存者选择，防止 B 破坏 A。
5. 新非锁箱诊断场景做消融：Hand、NSGA-II、A、A+Fixed-WAIT、A+WAIT-SLA、A+WAIT-SLA+VERIFY、安全重试、B-new、A+B-new、A+B-new+Gate。
6. 指标包括 CondRecSucc、episode/action 行为违规、重复副作用、SLA 违规、CorrectEscalation、AvoidableHarm、不必要成本、worst-group、搜索效率和未见任务族泛化。
7. 旧 D-061 validation 若用于调参，不再称独立验证；正式 held-out 仍锁定。
8. 统计沿用 pooled hierarchical，但要审计 cluster=task×fault composition、seed 嵌套、paired bootstrap/permutation、Holm、效应量和 CI。

### Gate
GO：失败轨迹复核、WAIT-SLA/FSM/B-new/Safety Gate 实现、单测、独立 validator、新非锁箱诊断和统计复算。
HOLD：正式 A-3b、旧 held-out 调参、UndoBench TEST、Pilot B、A800/ARWM、大规模真实 API、ThinkingBox 和未经批准的锁箱测试。
指标稳定之前不做正式功效分析，不启动 A800。

### 研究问题
Q1 WAIT-SLA 是否降低重复副作用；Q2 是否优于固定 WAIT；Q3 VERIFY 是否有独立贡献；Q4 B-new 是否正确定位基因；Q5 B-new 是否优于 NSGA-II；Q6 A+B-new 是否优于 A；Q7 Safety Gate 是否保护 A；Q8 是否接近/超过 Hand；Q9 未见任务泛化；Q10 增益来自演化搜索还是手工规则。

本节记录的是 D-062 计划，**不是已实现或已验证的实验结果**。

## 56. D-062 执行轮：失败轨迹复核 + WAIT-SLA + B-new + 第三轮诊断（2026-11-07）

报告：59（复核）/60（设计）/61（结果）。数据：diagnostic3_results.json（manifest 017b3454…）。

### 56.1 Stage 0 复核推翻 D-061 叙事
0.36 违规率非重复副作用（A dup=0）：99.4% 是评价器 artifact（正确 ROLLBACK 被 saga 门禁误伤，hand 0.006 同源）；真实重复仅 7 例，轨迹确证 `TIMEOUT→VERIFY(SLA 内谎言)→RETRY→DUPLICATE`。

### 56.2 实现（51/51 测试绿）
评价器门禁只对执行类动作计罚；WAIT-SLA 契约（补偿清除 或 SLA 后查询确认才解锁重试，动作掩码）；B-new（动作序列签名+涉事基因+死因修复映射+validator）；Safety Gate（ABG 臂）。

### 56.3 第三轮结果
**AB vs A +0.119 p=0.0002（B-new 成立，逆转 D-061）**；**AwaitSLA vs A +0.089 p=0.005、vs Fixed +0.054 p=0.003（WAIT-SLA 成立）**；AB vs AwaitSLA all +0.031 p=0.0072；但 validation +0.031, p=0.244（n.s.），Q10 搜索增量尚未证明泛化；validation AB vs A +0.142 p=0.008。负结果：Gate 有害、B 单独劣于 NSGA-II、未超 hand（−0.282）。

### 56.4 判定与下一步
A + WAIT-SLA + B-new 三机制有诊断性消融证据；但 AB vs NSGA-II all p=0.062、validation p=0.2277，尚未证明优于标准 EA；Q10 validation p=0.244，搜索增量尚未证明泛化。安全保证限于明确工具合同假设。下一步：功效核算 → preregistration 交用户批准 → 正式 A-3b。


## 57. D-063：正式 A-3b 功效核算与预注册（2026-11-08）

执行计划：`62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md`；下一会话入口：`NEXT_SESSION_PROMPT.md` D-063 节。

### D-062 完成结论
- 59/60/61 已提交；D-062 Stage 0–4 完成。执行报告称 79/79；新 workflow Actions run `42398278551` 已 success，`pilot_a_recovery` 与 `pilot_a3b` 两个测试步骤均通过。
- D-061 0.36 vs 0.006 叙事被推翻：99.4% 为 evaluator artifact；真实重复 7 例，根因是 SLA 内 VERIFY 的 NOT_COMMITTED 谎言解锁非幂等 RETRY。
- WAIT-SLA、B-new 有诊断级机制证据；AB vs A +0.119、AwaitSLA vs A +0.089、AwaitSLA vs Fixed +0.054、AB vs AwaitSLA all +0.031。
- 负结果：B 单独劣于 NSGA-II；Safety Gate 有害；AB 未超过 Hand。

### 不能夸大的统计结论
- AB vs NSGA-II all：+0.1049，CI [0.000,0.2058]，p=0.062（54 clusters），未显著。
- AB vs NSGA-II validation：+0.1173，CI [-0.0679,0.2778]，p=0.2277（18 clusters），未显著。
- AB vs AwaitSLA validation：+0.031，CI [0.000,0.068]，p=0.244；Q10 搜索增益尚未建立独立泛化。
- AB vs A validation +0.142，p=0.0082 支持 B-new 增量，但不能替代 AB vs NSGA-II 主比较。
- AB vs Hand −0.282，显著落后；论文不得声称超越专家。

### 统计可复现性阻断
当前 `experiments/pilot_a3b/stats.py` 的 main 仍硬编码 `diagnostic2_results.json`，`run_diagnostic3.py` 只写原始结果，61 报告中的 AwaitSLA 三组比较没有在已提交统计入口中完整再生。先做 `analyse_diagnostic3.py`，对 raw diagnostic3 重新计算所有对比和 train/validation split；校正报告中任何差异。不能直接以现有 summary 数字冻结样本量。

### 初步功效数值
paired cluster t 近似，双侧 alpha=.05，基于 validation-only SD=.3914：
- 当前 validation：18 clusters；点估计 Δ=.1173。
- MDE=.1173：80%/90% power 约需 90/119 可分析 clusters。
- MDE=.10：约需 123/163 clusters；加 15% 失效预留约 145/192。
- MDE=.08：约需 190/254 clusters。
- 当前估计只有 18 个 cluster，SD 不稳定；最终要基于 empirical cluster differences 做 Monte Carlo sign-flip/bootstrap power simulation。
cluster 定义是 task×fault composition；增加 seeds 或 episode 数不能代替独立 cluster。若 9 compositions，145 clusters 约需 17 个 task families ×9。

### D-063 执行顺序
1. 统计流水线可复现性和 synthetic tests；
2. 从 validation-only paired cluster data 做 empirical power simulation；
3. 冻结 MDE、alpha、power、held-out cluster 数和任务族扩展方案；
4. 起草预注册（主比较 AB vs NSGA-II；次要比较 Holm；Hand 仅参考；安全硬门）；
5. 用户审阅批准后才冻结；
6. 正式 A-3b 另行授权，未批准前 HOLD。

### Gate
GO：统计复现、功效仿真、任务族可行性、预注册草案、CI。
HOLD：正式 A-3b、held-out 调参/查看、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。


## 58. D-063 执行接管更新（2026-11-09）

**唯一接管入口：** NEXT_SESSION_PROMPT.md（文件末尾“D-063 执行接管指令”覆盖本文件中较早的历史计划）。  
**详细计划：** 62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md。  
**数据门禁：** 51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md。

### 当前真实状态

- 工作仓库：yujian777555/kaitibaogao。
- 工作分支：pilot-a-stateful-recovery。
- 本轮维护起始 HEAD：e6fee3bde05e8dea3fcc54f2ea1d97bc54837867；接管时必须重新查询远端 HEAD。
- main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；不得修改或合并。
- 本轮只做 D-063 计划、接管提示词与状态文档维护；没有运行 diagnostic3 分析器、没有执行功效仿真、没有生成任务族审计或预注册。
- 最近一次实验代码 CI：run 42398278551，commit c0078d5c3db17380e81faca5752ac6a64f555a6d，结论 success；两个 job step（pilot_a_recovery、pilot_a3b）均成功。之后是文档提交，不能声称 CI 对当前文档 HEAD 重新运行。

### D-062 结果边界

- AB vs A +0.119 / p=.0002；validation +.142 / p=.0082。
- AwaitSLA vs A +.089 / p=.0047；AwaitSLA vs AwaitFixed +.054 / p=.0032。
- AB vs AwaitSLA all +.031 / p=.0072，但 validation +.031 / p=.244，Q10 搜索增量尚未证明泛化。
- AB vs NSGA-II all +.1049 / p=.062；validation +.1173 / p=.2277，均未显著。
- AB vs Hand −.282，仍落后强手工策略。
- B 单独和 Safety Gate 的负结果必须保留。安全保证只限明确工具合同假设。
- D-061 的 0.36 vs 0.006 行为违规叙事已被 59 号独立审计推翻：99.4% 为 evaluator artifact，真实重复副作用为 7 例。

### D-063 唯一执行顺序

1. **Stage 0 — diagnostic3 独立复算：** 新增 analyse_diagnostic3.py 或显式 CLI；从 diagnostic3_results.json 读取；输出 all/train/validation；复算七组比较；按 task × fault-composition cluster 推断，seed 嵌套；输出 cluster SD、CI、paired sign-flip p、效应量、seed 稳定性和适用 Holm；校验 episode 唯一、配对完整、cluster 一致、seed 完整、split 隔离、分母语义和哈希。
2. **Stage 1 — empirical power：** 基于 Stage 0 复算的 cluster-level paired differences，仿真 MDE=.08/.10/.1173、双侧 alpha=.05、80%/90% power、15% 失效预留和 SD 敏感性；报告 Monte Carlo 误差。18 个 validation clusters 太少，SD 不稳定，必须披露。
3. **Stage 2 — task-family audit：** 从 task/split/scenario manifests 对账总任务族数量与 validation 2 families ×9=18 clusters 的关系；检查近重复和泄漏；报告真实可用独立 cluster 数。不能用 seed/episode 凑独立样本。
4. **Stage 3 — preregistration：** 唯一主要比较 AB vs canonical NSGA-II；澄清 R1/R2 恢复与 R3/R4 正确升级的主要终点公式、分母、权重及聚合顺序；次要比较 Holm；Hand 仅参考；安全为硬门。草案标记 DRAFT — NOT FROZEN。
5. **用户批准：** 将预注册草案交用户审阅。批准预注册不自动授权正式 A-3b，正式实验必须另行获得明确批准。

### 当前 GO / HOLD

**GO：** 统计分析器、synthetic tests、历史 diagnostic3 复算、经验功效仿真、任务族/泄漏审计、预注册草案、CI 和文档维护。

**HOLD：** 正式 A-3b；查看或调参新的 held-out test；Pilot B；A800/ARWM；真实 LLM API；UndoBench TEST；ThinkingBox。

### 维护规则

每次实质性研究、实验、代码、协议、审计或决策变化后，同轮更新 NEXT_SESSION_PROMPT.md、SESSION_HANDOFF.md、README.md、05_DECISION_LOG.md 和相关计划文件。所有 SHA、测试、CI 和科学结论必须来自真实仓库或运行结果；不得把计划写成完成。


## 57. D-063 执行轮：统计复算、功效、扩展审计、预注册（2026-11-08）

### 57.1 Stage 0 独立复算（analyse_diagnostic3.py，17/17 测试）
结构检查零问题；7 对比 Δ 与 61 号逐位一致；p 值 3 位微差=置换 MC 种子差异（结论不变）。输出 diagnostic3_recomputed.{json,csv,md}。

### 57.2 Stage 1 功效（Monte Carlo 2000/点）
主对比需 test clusters（80%）：MDE 0.10→**145**（含 15% 失效 171）、0.1173→110、0.08→254；ICC≈−0.09 支持 cluster 独立；18-cluster 方差不稳已敏感性声明。

### 57.3 Stage 2 扩展审计（63 号）
576 候选序列/18 profile；多样性选择重叠 0.83/3（朴素 2.0/3）；train/val/test = 8/4/17 族 = 72/36/**153 clusters**；功效缺口替代序已定；泄漏面已登记。

### 57.4 Stage 3 预注册草案（64 号，CANDIDATE）
主要唯一对比 AB vs NSGA-II；次要 4 项 Holm；硬安全门；协议全冻结（pop48×60、seeds 411/522/633、test 459 场景锁箱）。

### 57.5 状态与下一步
GO：用户审阅 64。HOLD：正式 A-3b（批准+清单后解锁）及其他全项。下一步：批准 → 预检 → 正式 A-3b。


## 59. D-064：64 号预注册草案独立审查（2026-11-09）

**结论：REQUEST CHANGES。** D-063 的工程交付和 CI 验收通过；64 号预注册尚不具备批准条件。完整审查见 `65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md`。当前最高优先级接管指令见 `NEXT_SESSION_PROMPT.md` 的 D-064 节。

### 59.1 仓库与 CI 核验

- D-063 final HEAD：`4f23abed3150e09703839b980ad3afc9bb14dfb3`。
- main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，未修改。
- Actions run `42615985837` 在 D-063 final SHA 上 success。
- `pilot_a_recovery` 28/28；`pilot_a3b` 68/68；总计 **96/96**。
- D-064 审计文档已新增；README 与接管文档随后更新。接管时重新查询当前 HEAD 和 CI。

### 59.2 P0：主要 estimand / power mismatch

64 §3 的主要终点 CondRecSucc 只算 R1+R2；但 D-063 `power_simulation.py` 未按标签过滤，使用全 R1–R4 的 `class_success`，得到 54 clusters、SD=.404、Δ=.1049。该数值不是 CondRecSucc 的功效输入。

审查用快速配对重聚合（非正式统计产物）显示：原始 diagnostic3 的 54 clusters 中，只有 42 个含 R1/R2；R1/R2-only AB−NSGA-II Δ≈+.3175、SD≈.3189、42 个 eligible clusters。必须将该计算正式加入 `analyse_diagnostic3.py` 并独立复算，不能把快速审查值直接写入预注册。

### 59.3 P0：功效模拟方法不符合“经验重采样”描述

`power_simulation.py` 实际使用 `N(MDE, empirical SD)` 正态参数化生成；经验重采样分支未调用；signflip 选项也不是实际符号翻转检验，而是正态 z 近似。无 MCSE；小样本 null FPR 有偏高点。修复后需使用 CondRecSucc cluster 差值，做经验/层级模拟、检验校准、MCSE 和 ICC 敏感性。

### 59.4 P0：ICC 与任务族独立性

ICC 基于 6 个 task families，validation 仅 2 个；负点估计不能证明 task×composition clusters 独立。未来 17×9 结构需要层级相关敏感性或 family-level resampling。

### 59.5 P0：任务族语义和正式场景生成器

63 号只从 10 工具三步排列中按合同属性筛出 576 候选；未验证任务目标、前置/后置条件和工具顺序语义。贪心目标仅为工具重叠，不含 profile diversity；新 23 族实际覆盖 11/18 profiles，test 17 族覆盖 10/18。

当前 `pilot_a3.py` 仍固定 6 个 TASKS，`make_fault_vector()` 依赖固定映射；`run_diagnostic3.py` 仍硬编码 4 train +2 val。63 的 8/4/17 还不是已集成的正式场景生成器。需实现任务语义 validator、通用生成器、标签和 manifest 测试。9 种 fault-composition 类别跨 split 共享，因此泛化主张不能写成未见故障类型 OOD。

### 59.6 P1：样本量与协议尚未唯一冻结

原参数化 power 表：MDE=.10 / 80% 需 145 个可分析 clusters，含 15% 失效需招募 171；当前 test 153 clusters 失效后约 130，低于目标。MDE=.1173 来自观察到的 validation effect，不能未经科学意义论证自动成为 MDE。修复 estimand 后必须重算并只冻结一个 MDE/power/attrition 方案。

UNKNOWN 上限、类别分布、primary eligible clusters、硬安全门对 AB/NSGA-II 的规则、零事件置信上界、初始池 60 生成但只用前 48 个、精确 code SHA 也必须冻结。64 §5 的“27+ tests”需改为引用真实 CI 96/96 和具体 SHA。

### 59.7 下一阶段唯一任务

**D-064-A：** 在 `analyse_diagnostic3.py` 增加 R1/R2-only CondRecSucc 配对 cluster 对比，输出有效 cluster 数、每 cluster 分母、Δ、cluster SD、CI、sign-flip p；R3/R4 独立统计。之后才重做功效、ICC、任务族生成和 64 修订。

**GO：** D-064-A/B/C/D 修复、统计与场景生成测试、预注册修订、CI。  
**HOLD：** 正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。即使 64 获用户批准，正式 A-3b 仍需另行明确授权。


## 58. D-064-A 执行轮：CondRecSucc 主要终点独立复算（2026-11-09）

### 58.1 修复 P0-1（estimand 不一致）
`condrec_analysis.py` + 13/13 测试 + `condrec_diagnostic3.{json,csv,report.md}` + 66 号报告。CondRecSucc 仅 R1+R2；R3/R4 独立；四层配对；零分母 12 cluster 预规定排除并登记；真实 sign-flip MC；无硬编码。

### 58.2 真实结果（结论翻转）
**42 eligible clusters；Δ=+0.3175；SD=0.3189；CI [0.218, 0.411] 不含 0；p=0.000125**；scenario 加权 0.3145 一致；配对 1.000。原全类别 +0.1049/0.065 系 12 个 R3/R4-only cluster 稀释。65 快速核对值与正式复算逐位一致。

### 58.3 R3/R4 权衡（如实）
AB R3 0.226 / R4 0.80 vs NSGA-II 0.679 / 0.933——主要终点领先不掩盖安全行为率落后。

### 58.4 状态
GO：D-064-B（CondRecSucc 功效重做 + ICC 敏感性）。HOLD 不变；65 其余阻断项待后续。


## 59. D-064-A 完成与 D-064-B 接管（2026-11-09）

### 59.1 D-064-A 验收事实

- Final HEAD：`16e255de627b37713f0ea936df0ddb0dd03ac084`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。
- CI run `42631223393` 在 final HEAD 上 success；109/109 tests。
- 原始 diagnostic3 SHA-256：`b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`。
- CondRecSucc 仅 R1/R2；42 eligible task×composition clusters，12 zero-denominator clusters。
- AB 0.5582 vs NSGA-II 0.2407；Δ=+0.3175；cluster SD=.318856；D-064-A cluster bootstrap CI [.218254,.411376]；cluster-level sign-flip MC p=.000125（8000 次）。
- 42 clusters 嵌套在 6 个 task families 中，每个 family 当前 7 个 eligible compositions；不能假设 42 个独立 family。
- R3 AB .226 vs NSGA-II .679；R4 AB .800 vs NSGA-II .933。主要终点优势不能掩盖安全行为率落后。

### 59.2 D-064-B 的科学问题

D-064-A 的点估计和原始数据复算保留；但 42-cluster CI/sign-flip 对 family 内相关性敏感。D-064-B 必须以 task family 为高层级抽样单位，重新评估 ICC、family-level 推断和功效。历史 ICC 负点估计不构成独立性证明。

64 的候选 test 是 17×9=153 design clusters；若沿用当前 7/9 primary eligibility，只有约 119 primary-eligible clusters（条件性投影，待 D-064-C 正式生成器验证）。

### 59.3 D-064-B 执行规格

完整提示词与执行清单：`67_D064B_POWER_AND_HIERARCHICAL_SENSITIVITY_EXECUTION.md`。

- 重建 6 families×7 eligible clusters 层级结构；
- ANOVA method-of-moments + random-intercept REML ICC，并给不确定性；
- family-block empirical bootstrap + ICC-controlled hierarchical simulation；
- ICC=0/.05/.10/.20；
- MDE=.05/.08/.10/.1173/.15（.1173 仅历史敏感性，不是已选 MDE）；
- 双侧 alpha=.05，80%/90% power，报告 null Type-I error、MCSE 和区间；
- family-level t、family-level exact/MC sign-flip、family-block bootstrap 对照；
- families 6/8/10/12/15/17/19/22/25/30/40；eligible compositions 6/7/8/9；cluster/family attrition 分开；
- 区分 design clusters 与 primary-eligible clusters；不得将 153 直接当成 153 个 CondRecSucc 样本；
- D-064-B 只给条件性样本量建议，最终 MDE/test family 数等待 D-064-C 和用户审阅。

### 59.4 当前 GO / HOLD

**GO：** D-064-B 统计、功效、ICC 敏感性、代码、测试和仓库维护。

**HOLD：** 正式 A-3b、test peeking/tuning、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。64 号预注册仍未批准。


## 59. D-064-B 执行轮：层级功效与 ICC 敏感性（2026-11-09）

### 59.1 交付
power_hierarchical.py（22/22 测试）+ power_hierarchical.{json,report.md} + family_cluster_diagnostics.csv + 68 号报告。

### 59.2 核心结果
- 6/6 family 均值全正；ANOVA ICC=−0.1257（REML 边界 0，CI [−0.159,−0.111]）——**不解释为独立性证明**，改用 ICC 网格敏感性。
- **层级推断显著性保持**：t p=4.6e-5、精确符号翻转 p=0.031、block bootstrap CI [0.272,0.357]。
- 校准：**t 检验控制 α 良好（0.050–0.056）**；bootstrap CI 检验反保守（0.08–0.14）；修复 2 个校准 bug。
- 所需 families（MDE 0.10 @80%）：ICC 0/0.05/0.10/0.20 → 15/17/22/30；双 15% 损耗 22/30/40/40。**17-family 条件性充分**。

### 59.3 状态
GO：D-064-C（语义 validator + 正式生成器 + MDE/样本量唯一冻结）。HOLD 不变；64 号 REQUEST CHANGES。


## 60. D-064-C 执行轮：独立审计与设计冻结（2026-11-09）

### 60.1 审计（69 号报告；test_d064c_audit.py 25/25）
任务语义 validator 对抗性完备（12 类恶意变形全拒）；9 故障组合声明-注入-标签一致（修复 1 处陈旧注释：permission_after_compensatable_prefix）；标签器独立（AND-OR 判定器+证据哈希）；8/4/40 划分零泄漏；manifest/family/scenario 三哈希独立重建一致。

### 60.2 功效最终核验（不采信硬编码 0.85）
34 有效 families×5 comps（双 15% 损耗），ICC=0.20 最坏 **power=0.839 [0.832,0.846] ≥0.80**；null 0.054。生成器 POWER_DESIGN 更新为 0.839+provenance；MDE=0.10 标注 PROPOSED_MDE_PENDING_ADVISOR_APPROVAL。

### 60.3 64 号修订 R2
40-family test（1,080 场景/280 eligible，哈希冻结）；主检验 family 级 Student-t；bootstrap 降级描述性；UNKNOWN≤5% 门禁；损耗双 15%。状态 CANDIDATE R2。

### 60.4 状态
GO：64-R2 独立审计→用户批准→正式 A-3b。HOLD 不变。


## 61. 64-R2 独立审计 R1（2026-11-10）

结论：REQUEST CHANGES；正式 A-3b 继续 HOLD。

### 已核验的 D-064-C 最终交付
- 工作分支 HEAD：fa3bc2c5699c0fad8df384bebd44e5510d1d8927；main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead 170 / behind 0。
- CI run 42661732606：success；pilot_a_recovery 28/28 + pilot_a3b 146/146 = 174/174。
- 最终 manifest SHA：fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a；test-family 01b41df8…；test-scenario dded3bb7…。
- 实际提交链：1908026b → fa53d19876dec51681dc4ba5a9e1e760965ef328 → fa3bc2c5699c0fad8df384bebd44e5510d1d8927。

### 64-R2 必须修复
1. §2 与 §4 主检验冲突：统一为 family-level two-sided Student-t；sign-flip 仅敏感性；bootstrap CI 仅描述性；明确次要检验与 Holm。
2. df=39 改为 df=F_observed−1；完整 40 families 时 39，预期损耗后 34 families 时 33。
3. 更新 candidate manifest hash 至最终 CI 值；旧 af83f065… 仅保留为 superseded history。
4. 明确功效模拟采用固定向下取整的保守保留规模（40→34 families；7→5 eligible comps），并预注册实际缺失数据处理。
5. MDE=0.10 仍待导师认可；必须列为正式执行前置审批门。
6. 次要比较的检验方法和 Holm family 必须无歧义。

### 维护勘误
69 号报告、README、05_DECISION_LOG、NEXT_SESSION_PROMPT 已同步最终 manifest hash、CI 174/174 和最新状态；NEXT_SESSION_PROMPT 顶部优先级已更新。status.json 在当前分支不存在，不创建虚假状态文件。

### 唯一下一任务
修订 64-R2 并更新仓库；运行必要测试与 CI；请求独立 R2 复审。审计通过后，先取得导师 MDE 认可，再取得用户明确批准，按 64 §5 pre-flight 执行。不得提前启动正式 A-3b 或接触 Test 结果。


## 61. D-064-R2 执行轮：六项修正与 R3（2026-11-10）

### 61.1 修复（71 号；test_64r3_protocol.py 15/15）
R2-001 主检验统一 family 级 t；R2-002 动态 df（family_t_df，40→39/34→33）；R2-003 manifest 独立重建 **fb832bcc…**（af83f065 标注 superseded）；R2-004 attrition 定性+missing_data_rules 冻结；R2-005 GO 顺序含导师 MDE 认可；R2-006 H2–H5 全定义+Holm{H2..H5}，H4/H5 探索性。附带修复：F>15 符号翻转 MC 化（原 2^F 枚举挂死）。

### 61.2 验证
df 39/33/动态✓、family 等权✓、缺失规则✓、Holm 边界✓、功效复算 ICC=0.20 t=0.840 [0.833,0.847] 与历史一致✓、真实数据 df=5✓。全套件 189 绿。

### 61.3 状态
GO：**64-R3 独立复审**（71 号为 Executor 验证非审计）。HOLD 不变。下一步：独立复审 → 导师 MDE → 用户批准 → pre-flight → 正式 A-3b。


## 62. 64-R3 独立审计：REQUEST CHANGES（2026-11-10）

### 当前权威结论
`72_64R3_INDEPENDENT_REVIEW.md` 为当前权威独立审计。它取代此前“64-R3 六项已全部修复+已验证”的 Executor 状态表述。正式 A-3b 继续 HOLD；未运行正式实验，未读取 Test 逐场景标签或结果，未修改实验代码或 R3。

### 基线与验证
- 工作分支审计基线：`ca7bb12f89dd72deaac205ffab89cf3054e6be06`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。
- CI run 42670236796：success；测试 28+161=189/189；本地复跑一致。
- manifest/test-family/test-scenario 哈希独立重建均与 CI 一致。
- 独立证据：`experiments/pilot_a3b/audit_64r3_independent_checks.json`。

### 必须保留的发现
1. R2-003 已关闭；动态 df 成立；MDE 审批门文本存在，但批准未完成。
2. R2-001/004/006 的实现未关闭。R3 文本不能替代正式 40-family 分析系统。
3. pre-flight 错指 §6；labelled null 不 fail-closed；technical_missing_runs/family_loss/design_deviation 未实际计算。
4. `family_min_valid_compositions=1` 与固定 34×5 功效不一致。独立模拟 ICC=0.20：平衡 power=0.8400；17 族 m=5 + 17 族 m=1 时 power=0.5777。
5. 全零 family 差值在正式 helper 中 `t=inf,p=0`，在模拟 helper 中 p=1；必须统一边界。
6. H2–H5 的 family-t/四项 Holm 未实现；H2/H3 校准不足；H4/H5 探索性无正式报告路径。
7. 历史 diagnostic 未发现 Test 使用，但 Test payload 会由生成器返回，演化接口无 split guard，一次性解锁路径不存在。
8. `signflip_exact` 在 MC 下命名误导，实际 seed 未随结果记录。

### 唯一下一任务
Executor 完成 R4 corrective revision 并请求新的独立复审。修复范围见 72 号 §11：正式 40-family 入口、真实缺失处理、至少 5 comps 或不平衡功效重证、统一 Student-t 边界、H2–H5 family-t/四项 Holm、pre-flight、结构性 Test 锁箱、sign-flip 输出和真实路径测试。

### 可直接复制的接班提示词
你是本项目的 Executor。先重新核验远端工作分支和 main HEAD，读取 `72_64R3_INDEPENDENT_REVIEW.md`、`64_A3B_PREREGISTRATION_CANDIDATE_R3.md`、`experiments/pilot_a3b/audit_64r3_independent_checks.json` 及其实际代码。当前审计结论为 REQUEST CHANGES，不得把 189 个测试通过或 71 号 Executor 报告当作 ACCEPTED。

只执行 R4 corrective revision：保留 R2/R3 历史文件，修复 72 号 §11 的全部阻断项；不得运行正式 A-3b，不得读取或调参 Test，不得修改 main，不得启动 Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 或 ThinkingBox。所有缺失数据测试必须调用真实处理函数；不平衡功效必须保存配置、seed、MCSE/CI 和原始输出；Test 隔离用合成 sentinel 验证。完成后更新 README、05_DECISION_LOG、SESSION_HANDOFF、NEXT_SESSION_PROMPT，提交并核验远端，再交独立 Reviewer 复审。即使 ACCEPTED，仍需导师 MDE 认可、用户明确批准和真实 pre-flight。


## 63. D-076 执行完成记录（2026-11-10）

### 交付
- `64_A3B_PREREGISTRATION_CANDIDATE_R4.md`
- `77_D076_R4_AND_SBCG_EXECUTION_REPORT.md`
- `formal_runner.py`、`run_r4_preflight.py`、`sbcg.py`、`sbcg_runner.py`、`sbcg_experiment.py`、`sbcg_config.json`
- `results/r4_preflight/`、`results/r4_runner_synthetic/`、`results/r4_power_20261114/`、`results/r4_clean_clone.log`

### 状态
R4 = READY_FOR_INDEPENDENT_REVIEW。SBCG = IMPLEMENTED + SYNTHETIC TESTED，性能 NOT RUN。290/290 本地及 clean-clone 测试通过；CI regression/power success。pre-flight 当前 HOLD，未伪造任何批准。

### 唯一下一任务
提交 R4 独立复审。复审 ACCEPTED、导师 MDE=0.10 认可、用户批准和真实 pre-flight 前，禁止真实 Train/Validation 算法诊断、Test 访问、正式 A-3b、Pilot B、A800/ARWM、真实 LLM API 和 main 合并。



## 2026-11-10 D-078：已完成首轮合成 Train/Validation 探索实验

**最新实验提交：** `7cbbac54e2f3d8680a4851f7a7c79cd02b3cd8d3`（CI 自动保存结果）  
**实验 workflow：** [42820836080](https://github.com/yujian777555/kaitibaogao/actions/runs/42820836080) — success  
**回归 workflow：** [42820836104](https://github.com/yujian777555/kaitibaogao/actions/runs/42820836104) — success  
**实验报告：** [matrix_report.md](experiments/pilot_a3b/results/d078_train_validation_pilot/matrix_report.md)

- 14 臂 × 3 seeds = **42 runs**。
- 生成的合成 A-3b Train 216 scenarios、Validation 108 scenarios；Test payload/outcomes 未传入 runner、未读取。
- population=8、generations=5；每个进化臂计划 Train episode budget=10,368；LLM API calls=0。
- SBCG/NSGA-II/NSGA-III/Random/Rule/Hand 等多数臂的 Validation selected CondRecSucc=1.0000、AvoidableHarm=2.4444、ActionCost=4.3929，结果高度重合；SBCG 未显示可见的主指标提升。
- Reflection proxy 三个 seed 均 HOLD（无可行 Validation 候选）；no-M3 消融三个 seed 的 CondRecSucc 分别为 0、0、0.3929，表现明显不稳定/较差。
- 不同算法的 Pareto candidate counts 有差异，但不能据此认定性能提升。
- 这些是合成开发模拟器上的探索性、选择后 Validation 指标，存在 Validation selection optimism；不是无偏泛化估计，不是正式 A-3b，不是 Test 结果，不足以支持论文主张。

**对 D-076 独立复审的状态更新：** D-076 的 `78_D076_INDEPENDENT_REVIEW.md` 是针对旧基线 `3d2dacf` 的审查记录。其指出的若干 SBCG 阻断（canonical NSGA-III、f3 公式、Train→Validation 选择、cache accounting）已在后续 D-078 代码提交中作了修订并通过对应 CI；不能继续把旧审查结论当作当前代码状态。R4 pre-run/post-run gate、technical-missing power 校准等必须单独核验，不因 D-078 合成 pilot 通过而视为关闭。

**下一步：** 不扩大到 Test、不启动 A800/真实 LLM。先做 D-079 结果诊断：按 scenario/family 拆解指标与 Pareto 差异，检查 1.0 CondRecSucc 是否天花板效应、为什么多个优化器收敛到相同 FSM/结果；再设计难度分层的合成挑战集与预注册的 Train-only 机制诊断。只有能稳定区分算法的任务机制才进入后续更大规模验证。


## 0C. 最新权威状态（2026-11-10，D-079 corrective diagnostics）

- 接管前远端 work HEAD：2b7903749efd46426672467a1a7d82dce221928d；main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead 250 / behind 0。此为提交前基线，提交后需重新核验。
- D-078 已完成 14 arms × 3 seeds = 42 runs；Train 216、Validation 108；CI 42820836080 与回归 CI 42820836104 success；Test outcomes 未读取。
- D-079 原始数据初查：42 次选择中 32 次与 Hand FSM fingerprint 完全相同；Hand R1/R2=84/84、R3 correct escalation=0/12、R4 containment=12/12。待仓库内独立脚本和 CI 复核。
- 已识别并准备修复：成功完成任务的 active effects 不应作为 residual harm；permission/partial-commit 的 unavoidable prefix 需计入；robust AND-OR class 应覆盖旧 analytic class 的评估标签。
- D-079 新增审计脚本、Train-only 难度分层挑战生成器、回归测试及预注册候选；本次更新的 CI 尚待执行。
- 挑战集设计：8 Train-only families × 6 strata × 3 repeats × 2 roles=288 scenarios；search/diagnostic 各144；所有场景 split=train；不构建 Validation/Test。manifest hash 需经 CI 生成后锁定。
- 当前状态：IMPLEMENTED / CI PENDING；没有新的算法性能实验数据。正式 A-3b、Test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 均 HOLD。
- 唯一下一任务：核验 D-079 CI、审计报告与挑战集 manifest；如果所有门禁通过，提交 manifest hash lock；之后才可执行独立 Train-only exploratory diagnostic。不得跳过 manifest freeze。



## 0D. D-079 首轮 CI 失败与纠正（2026-11-10）

- 代码提交 4f83ea87d333441562ca7251aa3961f994bbd9dd 已推送；main 保持 683b3fe7fc52c86e917d523fdc6bbb13abbfd653。
- regression CI 42827879313 failure。既有 A3b 测试通过；新增 D079ChallengeTests.setUpClass 阻断，原因是 challenge generator 错误要求每个 Train family 同时有 compensatable 与 uncompensatable 工具。
- D-078 workflow run 42827879133 因同一全量测试 preflight 失败，Run 14-arm pilot 步骤 skipped；没有重新运行 D-078 算法，也没有新增 episode 数据。
- 已修正 D6：若 family 没有 contract-level uncompensatable 工具，则选用 compensatable 工具并将 runtime compensation_available 置 false，仍形成 R4 damage-containment 情景；增加测试确保 D6 是 R4。
- 已将 D-078 workflow 的 push trigger 移除，仅保留 workflow_dispatch，避免普通代码提交触发已完成的 D-078 实验。
- 修正提交后的 CI 尚未运行；challenge manifest SHA 尚未生成/冻结。
- 唯一下一任务：提交 corrective patch，等待 regression CI；若通过，审查 D-078 independent audit 与 288-scenario Train-only manifest，随后锁定 manifest hash。不得提前运行 D079 optimizer。

