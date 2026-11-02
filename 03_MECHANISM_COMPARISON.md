# 03 — 核心论文机制级比较与候选缺口

**版本：** v0.1 / 2026-11-02  
**定位：** 初步机制审查，不是最终创新性结论。

## 1. 研究版图：不是单一的“Agent 遗传算法”

当前至少存在五类不同路线：

1. **模块/配置演化：** EvoAgent、AgentSquare、EvoMAS（Hu et al.）、HFlow；
2. **工作流/代码搜索：** ADAS、AFlow、GPTSwarm、AgentSwift、MASS；
3. **Prompt/组件演化：** EvoPrompt、Promptbreeder、GEPA；
4. **开放式自改进/自进化：** DGM、MOSS、Agent-Pro、EvoAgent（continual world model）；
5. **非 EA 的优化和学习：** MaAS、MASPOB、ScoreFlow、Optimas、Q-Evolve、SWIFT、Workflow-R1、TPGO。

开题报告必须把直接演化方法与非演化的 Agent 搜索/优化方法都纳入对照，避免只比较少量 GA 论文。

## 2. 重点论文机制矩阵

| 方法 | 优化对象/表示 | 搜索/遗传机制 | 评价/选择 | 关键审查点 |
|---|---|---|---|---|
| EvoAgent (NAACL 2025) | 专家 Agent 设置与多 Agent 扩展 | 变异、交叉、选择 | 任务表现 | 初始个体、角色差异、协作结构和跨任务泛化 |
| AgentSquare (ICLR 2025) | P/R/T/M 四模块组合 | 模块演化、模块重组 | 任务表现 + in-context predictor | 固定模块槽位是否限制拓扑和跨模块依赖 |
| ADAS (ICLR 2025) | 代码级 Agent 程序 | Meta Agent 搜索、档案驱动程序生成 | 执行任务表现 | 代码空间开放但可执行性、搜索归因和评估可靠性 |
| AFlow (ICLR 2025) | 代码化工作流 DAG | MCTS、代码修改、树状经验 | 执行反馈 | 与 EA 的机制差异；树搜索是否可替代 |
| MaAS (ICML 2025) | Agentic Supernet / 查询条件架构 | 从架构分布中采样 | 任务表现、资源分配 | 动态架构采样与静态演化种群的差异 |
| GPTSwarm (ICML 2024) | Agent 计算图 | 节点 Prompt 和边连接优化 | 任务表现 | 图拓扑优化与进化编码的关系 |
| EvoMAS (Hu et al., ICML 2026) | 结构化 MAS 配置 | 执行轨迹反馈条件变异、交叉 | 任务成功、可执行性和运行鲁棒性 | 候选池、经验记忆和配置表示已覆盖哪些缺口 |
| EvoMAS (Wei et al., ICML 2026) | Agentic workflow、角色与策略 | 七种策略、探索/开发算子、自适应策略选择、课程调度 | 工作流表现 | 算子自适应与任务复杂度梯度已被直接研究 |
| EvoCF (ICML 2026) | 多 Agent 协作计划 | 失败约束归纳、规则条件反事实变异 | 计划/协作质量 | 规则库质量、反事实真实性、跨环境可迁移性 |
| HFlow (Findings ACL 2026) | 工作流结构、Prompt、模型骨干 | 交叉、结构/Prompt/模型变异 | 性能、人类偏好、成本三目标 Pareto | 人类/代理偏好信号可靠性；任务分布外泛化 |
| GEPA (ICLR 2026) | Prompt/compound AI system 子模块 | 轨迹反思、遗传式提示演化 | 每个任务实例上的 Pareto 候选集合 | 任务实例级优势是否可转化为稳定的跨任务能力 |
| AgentNet (NeurIPS 2025) | 去中心化 Agent DAG 网络 | 动态拓扑与专业化 | 系统表现 | 是否有明确的经典 EA 个体、算子与选择 |
| DGM (2025 preprint) | Agent 自身代码 | 档案采样、代码修改、开放式多路径探索 | 编码 benchmark | 档案质量、多样性、独立验证与安全边界 |
| AgentSwift (AAAI 2026) | 工作流 + 组合功能组件 | 层次化 MCTS、价值模型 | 多 benchmark 表现 | 搜索预测器误差和搜索策略与 EA 的比较 |
| MASS (ICLR 2026) | 多 Agent Prompt 与拓扑 | 分阶段局部到全局搜索 | 多任务表现 | 设计空间剪枝是否丢失关键结构 |
| MASPOB (ICML 2026) | 多 Agent Prompt | UCB、GNN、坐标上升 | 预算内性能提升 | Bandit 强基线；拓扑耦合 |
| Optimas (2025 preprint) | 复合系统组件 | 组件级优化方法可异构 | 与全局表现对齐的局部奖励 | 局部奖励的因果有效性和非平稳性 |
| Q-Evolve (ICML 2026) | Agent policy | IQL critic、过程奖励、策略更新 | 长时程任务回报 | 稠密过程奖励与演化选择信号的区别 |
| TPGO (Findings ACL 2026) | Agent/工具/工作流文本参数图 | 文本梯度 + GRAO 元学习 | GAIA、MCP-Universe 等 | 自适应改进器与 EA 的差异 |
| SWIFT (EMNLP 2026) | 目标任务工作流 | 从源任务轨迹提取结构先验并迁移 | 多 benchmark 和 held-out transfer | 跨任务结构迁移是强基线 |

## 3. 已确认的重复风险

### 3.1 多目标 Pareto 选择不能单独作为创新

HFlow 已明确将工作流表示为性能、人类偏好和成本三个目标，并使用 Pareto 支配关系进行种群生存者选择。GEPA 维护任务实例级 Pareto 候选；NSGA-II 等传统 MOEA 更是成熟基础。因此，不能只把 NSGA-II/III 接入 Agent 后宣称创新。

### 3.2 反馈引导变异不能单独作为创新

EvoMAS（Hu et al.）使用执行轨迹反馈条件变异/交叉；EvoCF 使用失败约束条件变异；HFlow 使用经验记忆和偏好引导变异；GEPA 使用自然语言轨迹反思。必须找到更细的机制差异，例如反馈如何转化为可验证的选择信号、是否进行因果归因、是否能在未见任务中改善。

### 3.3 自适应算子选择不能单独作为创新

EvoMAS（Wei et al.）已提出多种探索/开发策略和自适应策略选择。若研究算子选择，必须说明现有策略奖励、状态表示、信用分配或跨任务适应具体哪里不足，不能只换一个 UCB 或 bandit。

### 3.4 模块化 Agent 表示不能单独作为创新

AgentSquare 已使用 Planning、Reasoning、Tool Use、Memory 四类模块；AgentSwift 联合搜索工作流与功能组件；GPTSwarm 将 Agent 表示为图。需要提出更有依据的表示差异或结构化编码改进。

## 4. 当前候选研究缺口（待验证，不是最终创新）

### 候选 A：面向任务分布泛化的质量多样性演化

**问题：** 现有方法虽然保留候选池、Pareto 前沿或经验记忆，但是否充分维护“不同任务行为模式”的高质量多样性，并在未见任务分布上保持稳定优势？

可能机制：
- 从执行轨迹中构造行为描述符，而不是仅按 Prompt 文本距离定义多样性；
- 以任务能力分布、工具使用模式、规划/验证/恢复行为等描述个体；
- 采用 MAP-Elites / QD 档案保留不同能力区域的精英；
- 在档案内引入多目标或约束选择，评价训练任务表现、未见任务鲁棒性和执行可靠性；
- 研究任务特征到档案区域的检索或迁移。

必须先否证：
- GEPA 的实例级 Pareto 是否已经足以保持任务多样性？
- HFlow 的工作流 profile 标签检索和 Pareto 种群是否覆盖同一目标？
- DGM 的开放式档案是否已经达到所需的多样性？
- Rainbow Teaming 的 QD 行为描述符能否迁移到 Agent 轨迹？
- 仅用随机描述符、Prompt embedding 或任务标签是否也能取得同样收益？

可证伪假设 H-A：行为描述符驱动的 QD 档案，相较于仅按平均分保留的种群或单纯 Pareto 候选池，在训练任务分布变化或 held-out task family 上，能提高成功率下界/稳定性，同时不牺牲总体表现。若无显著改善或只增加档案复杂度，则否证。

### 候选 B：执行过程归因驱动的 Agent 演化

**问题：** Agent 失败时，如何识别规划、工具选择、工具参数、记忆、验证或协作拓扑中的关键责任组件，并将可验证的组件贡献转化为演化选择/变异信号？

可能机制：
- 以轨迹事件和组件调用构建可追踪执行图；
- 对候选组件进行配对反事实替换/消融，估计其边际贡献；
- 区分组件自身能力、组件间交互效应和任务难度影响；
- 将归因结果用于组件级选择、定向变异或重组；
- 用独立任务验证归因信号是否真正提高搜索效率与最终 Agent 能力。

必须先否证：
- HFlow 的结构/Prompt/模型偏好记忆是否已经实现足够的局部贡献归因？
- Optimas 的 globally aligned local rewards 是否已解决组件局部奖励与全局表现对齐？
- Q-Evolve 的过程奖励是否覆盖了 Agent 过程级监督？
- EvoCF 的反事实计划是否已包含关键反事实比较？
- 组件贡献估计是否会因交互作用、随机性或非平稳性而不可靠？

可证伪假设 H-B：显式过程归因信号能使演化算子更准确地修改导致失败的组件，并在相同任务、预算和模型下优于仅使用最终成功/失败或 LLM 自然语言反思的演化基线。若归因信号不稳定、不能提升独立测试结果，则否证。

### 候选 C：Agent 与演化算子的协同适应

**问题：** 是否能让搜索控制器根据种群状态、任务特征、历史算子收益和失败模式自适应选择或组合演化算子？

必须先否证：
- EvoMAS（Wei et al.）已经包含七种策略和自适应选择；
- Promptbreeder 已演化 mutation-prompt；
- EvoMAS（Hu et al.）和 HFlow 已使用反馈引导变异；
- 传统 Adaptive Operator Selection 文献已很多。

只有在发现明确的状态表示、信用分配、策略迁移或多任务非平稳适应缺口后，才保留此方向。

## 5. 候选方向当前排序

| 候选 | 当前判断 | 主要风险 | 下一步 |
|---|---|---|---|
| A 任务分布泛化 + QD | 优先审查 | 与 GEPA / HFlow / DGM 重叠 | 精读档案和行为描述符机制 |
| B 过程归因 + 演化 | 优先审查 | 与 Optimas / Q-Evolve / EvoCF 重叠 | 做局部贡献定义和反事实审计 |
| C 算子协同适应 | 暂缓 | EvoMAS（Wei et al.）直接覆盖 | 找到机制级差异再恢复 |

## 6. 下一轮必须完成的研究动作

1. 精读 EvoAgent、两篇 EvoMAS、EvoCF、HFlow、GEPA 的算法正文和附录。
2. 对 AgentSquare、ADAS、AFlow、MaAS、AgentSwift、MASS、GPTSwarm、AgentNet 做同样的机制抽取。
3. 精读 Optimas、Q-Evolve、TPGO、SWIFT，明确局部信用、过程反馈和跨任务迁移已有程度。
4. 将所有论文的 genotype、phenotype、fitness、selection、variation、survival、archive、transfer、test split 字段补齐。
5. 对 A/B/C 各写出至少一个强反例和停止条件；不通过则不进入实验。


## 7. 第二轮重大更新：EvoTest 直接给出算法改进线索

### 7.1 原文事实

EvoTest（ICLR 2026）将 Agent 配置表示为 χ=(p,M,h,u)，分别对应策略 Prompt、部署时记忆、超参数和工具使用例程。每轮由 Actor 执行一个 episode，Evolver 分析完整轨迹并生成候选配置，再通过 UCB 从父代和子配置中选出下一轮配置。

其 Appendix A 明确指出：
- 当前是简单的 (1+m) evolutionary strategy + UCB；
- 复杂配置空间可能局部收敛；
- 单任务重复学习会产生 task-specific overfitting；
- 作者建议未来探索更复杂的 population-based EA、Quality-Diversity 和 automated program synthesis。

### 7.2 为什么这比泛泛的研究空白更具体

它提供了已发表的直接基线、明确的 Agent 个体表示、明确的选择公式、明确的任务协议与 AUC，以及明确的算法局限和作者未来方向。

### 7.3 但不能忽略的竞争工作

- COvolve（GECCO 2026）已对 LLM 生成策略与环境进行两人零和协同演化，并用混合策略纳什均衡缓解遗忘；
- M*（NeurIPS 2026）已通过可执行程序种群搜索演化任务专用 memory harness；
- MemEvolve 已做记忆架构元演化和跨任务/跨 LLM 泛化；
- E-SPL 已把 system prompt 遗传演化与 RL 权重更新结合；
- INSPO 已把 instruction population 放入 RLVR 循环；
- SkillRL 已使技能库和 policy 递归协同演化；
- Live-Evo 已研究连续反馈和在线分布变化下的记忆更新；
- EvoTeam 已联合演化多 Agent 团队组织、交互规则和技能；
- EvoSkills 已通过 Skill Generator 与 Surrogate Verifier 协同演化技能和验证反馈。

因此，候选 D 必须聚焦于**跨任务序列中的测试时演化**，而不是泛化的记忆、技能或团队演化。

## 8. 当前候选排序调整（覆盖旧排序）

| 候选 | 状态 | 理由 |
|---|---|---|
| D：跨任务序列的演化测试时自适应 | PRIORITY FOR AUDIT | EvoTest 提供明确的 (1+m) + UCB 局限和作者未来方向 |
| A：任务分布泛化 + QD | 保留为 D 的子机制候选 | 单独提出 QD 风险较高，且 COvolve、GEPA、HFlow 等有相关覆盖 |
| B：执行过程归因 + 演化 | 暂缓 | Optimas、Q-Evolve、TPGO、EvoCF、EvoSkills 等已覆盖多种过程/组件反馈机制 |
| C：Agent 与演化算子协同适应 | 暂缓 | EvoMAS（Wei et al.）已有七种策略和自适应策略选择 |

## 9. 候选 D 的待验证算法框架

工作代号 TC-QD-ETTA：
- 个体：结构化 Agent 配置；
- 任务签名：只使用部署时可观察的任务特征；
- 行为描述符：从工具调用、规划、验证、恢复、记忆使用等轨迹特征提取；
- 档案：维护不同任务/行为区域中的高质量配置；
- 选择：新任务到来时检索相似任务区域中的父代，兼顾质量和多样性；
- 变异/重组：对配置模块进行受约束变异和兼容性重组；
- 评价：同一 backbone、固定任务协议下测 AUC、held-out 成功率、最差任务组表现、负迁移率和任务切换恢复速度。

这只是待验证框架。需要先证明任务签名、行为描述符和 QD 档案比 UCB、标准 EA 和已有记忆档案确实更有效。

详细定义见 07_CANDIDATE_D_TEST_TIME_ADAPTATION.md。


## 10. 第三轮检索后的方向重审

### 10.1 候选 D（跨任务测试时演化）不再作为优先方向
新增直接工作包括 TTHE（跨多个任务批次持续演化 harness）、Meta-TTL（跨任务学习测试时适应策略）、TacoMAS（测试时拓扑/能力协同演化）、Inherit-MAS（工作流和执行继承）、EvolveNet（多工作负载协同 harness 演化）、DarwinX（自然选择式 harness 演化）。因此，“跨任务序列中的测试时演化”这一宽泛问题已被密集覆盖。

**决策：** 候选 D 的宽泛表述标记 NO-GO / SUPERSEDED。EvoTest 仍作为关键基础文献保留，但不能再以“跨任务测试时演化”本身作为创新。

### 10.2 新增强相关方法对研究缺口的影响
MOAE 已做完整 Agent rollout 的 Pareto-preserving evolutionary search；SkillMOO 已使用 NSGA-II 优化 Agent skill bundle；MOCHA 已做 Agent skill 多目标优化；AgentBreeder 已对 Multi-Agent scaffold 做质量多样性/多目标演化；HGM 已用后代 clade metaproductivity 估计 Agent 的未来自改进潜力；PCE 已把整个种群的成功、失败和修改历史用于父代改进；FreeEvolve 已 meta-evolve evolver 自身的搜索策略；SERO 已做结构契约保持的角色演化；HiveMind 已用 DAG-Shapley 进行 Agent 级贡献归因；AHE、DarwinX、TTHE、EvolveNet 等已经覆盖 coding-agent harness 的自动演化。

因此，普通多目标选择、skill 进化、角色演化、测试时演化、种群知识汇总、evolvability 选择和 Agent 贡献归因都不能直接作为新颖点。

### 10.3 新的优先候选 G：组件交互感知的演化重组

**问题：** Agent 配置由相互依赖的 Prompt、工具策略、记忆、规划、验证、恢复等组件构成。现有方法已大量使用变异、交叉、模块重组或跨 lineage merge，但这些组件之间的协同/拮抗关系是否被显式估计？能否通过反事实干预学习组件间的 epistasis/linkage，并用其指导重组？

关键依据：
- DarwinX 明确指出，当前实验没有把 archive、parent selector、recombination operator 和 inference effort 独立随机化；recombination 相对 mutation 的贡献仍需要受控消融。
- EvoMAS、HFlow、AgentSquare 已有交叉/模块重组，因此“使用 crossover”本身不是创新。
- HiveMind 的 DAG-Shapley 是 Agent 级贡献分配，不等同于单 Agent 配置内部组件之间的 pairwise epistasis。
- EvoCF 的 counterfactual 是协作计划层面的反事实，不等同于配置基因的交互效应估计。
- SERO 的结构契约保持能防止角色结构破坏，但不是基于组件协同关系的遗传重组。

候选 G 仅在精读 EvoMAS、HFlow、AgentSquare、AgentBreeder、DarwinX、SERO、HiveMind 后，确认没有等价机制时才可保留。

### 10.4 候选 E/F 暂时保留为对照，不优先
- E：弱反馈/代理评价下的适应度可靠性与稳健生存者选择。TTHE、DarwinX、RQGM、Certified Selective Automation、Calibrating the Evaluator 已覆盖大量相关机制，必须先比较。
- F：可进化性/后代潜力驱动的 Agent 选择。HGM 的 CMP、Evolvability Search、Evolvability ES、CATArena、PCE、FreeEvolve 已覆盖关键概念，不应简单重复。

## 11. 候选 G 的可证伪算法草案

将 Agent 配置表示为模块化基因集合或依赖图。对组件 i、j 的组合进行同任务、同种子配对反事实干预，估计交互效应：

ε_ij = f(χ_ij) - f(χ_i0,j) - f(χ_i,j0) + f(χ_i0,j0)

其中 χ_ij 表示两个组件同时处于待测状态，其他三项表示单独替换/基准状态。该公式是工作定义，必须针对组件不可独立替换和执行依赖做修正。

据此构造 linkage/interaction graph：
- 正向强交互：作为 co-adapted block 一起继承；
- 负向强交互：禁止直接组合或触发兼容性修复；
- 低交互：允许独立重组；
- 估计不确定：保持父代模块或进入验证阶段。

候选算法名称：Interaction-Aware Evolutionary Recombination for Agent Configurations（IAER-AC），仅为工作代号。

证伪条件：若 ε_ij 无预测力，或 linkage-aware crossover 不优于随机模块交叉、LLM crossover、mutation-only，则停止；若已有工作显式使用组件交互图指导 Agent crossover，则候选 G 需改题或 NO-GO。


## 12. 面向 2–3 篇小论文的创新结构与直接工作补充（2026-11-02）

### 12.1 新增强基线及必须区分的机制

- **MESH-Harness (arXiv:2610.05300)**：模块槽位 + 实现池 + full-covariance LinUCB + mixed-start coordinate ascent + trace-driven module evolution。其 full covariance 保留跨槽位共同出现信息并估计组合不确定性，但预测均值仍是各槽位表示的加性和。因此它是强组合搜索基线，不能误称其已经显式拟合非加性 epistasis；同时也不能忽略它对模块组合搜索的覆盖。
- **ARTEMIS (arXiv:2512.09108)**：自动发现 Agent 可配置组件，使用 semantic-aware genetic operators 联合优化 Agent 配置。需要精读其依赖识别与算子定义，不能将“语义感知遗传算子”重新包装成创新。
- **EvoMAS (ICML 2026)**：结构化 MAS 配置空间中的反馈引导 mutation/crossover。
- **AgentEvo (2026)**：多阶段 workflow evolution，已有 subgraph graft、prompt fusion 和 Pareto performance-cost selection。
- **Evo-Harness (EMNLP 2026)**：单次执行上下文编译为可复用 harness skill，和第三创新点的任务迁移/经验更新高度相关。

### 12.2 三个创新点的独立分工

| 创新点 | 方法对象 | 预期独立贡献 | 独立实验 |
|---|---|---|---|
| I：任务条件化组件交互效应估计 | 估计器 | 从主效应中分离协同/拮抗，得到稀疏且带不确定性的交互图 | 合成真值环境 + 真实 Agent；估计偏差、符号准确率、图恢复率 |
| II：交互感知演化重组 | EC 交叉算子 | 将交互图转为 linkage blocks，设计协同块继承和依赖约束修复 | 固定评价次数和种群，对比 mutation-only、随机/LLM crossover、EvoMAS、ARTEMIS、MESH |
| III：任务分布变化下交互结构迁移 | 结构更新机制 | 分离共享/任务条件化交互，识别结构漂移并更新 linkage | 任务家族迁移、负迁移、结构恢复速度、旧任务回退 |

### 12.3 不能将三个实现步骤伪装成三个创新点

“交互估计→构图→图引导交叉”如果仅是一个方法的连续实现步骤，不能自动拆成三个创新点。创新点 I 必须有独立的估计算法与真值/预测实验；创新点 II 必须有独立的演化算子与受控搜索实验；创新点 III 必须有独立的任务分布变化问题和迁移实验。

### 12.4 题目调整

总题目工作稿调整为：

**《面向大语言模型智能体的交互感知演化优化方法研究》**

该题目比“交互感知演化重组”更能覆盖估计、重组和交互结构更新。最终仍须以相关工作审查和实验结果为准。
