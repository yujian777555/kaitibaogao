# RSI 三创新点机制级研究设计 R1

**日期：** 2026-11-03  
**对应开题版本：** 25_OPENING_REPORT_DRAFT_V0_3.md  
**研究主线：** 面向大语言模型智能体递归自我改进（RSI）的交互感知演化优化  
**状态：** RESEARCH_DESIGN_CANDIDATE / NO ALGORITHM GATE PASSED

---

## 0. 本轮决策

导师要求将 RSI 明确纳入毕业论文。研究结构调整为三个相互衔接、但具有独立研究问题的候选创新点：

1. **RSI 轨迹驱动的任务条件化 Agent 组件交互结构学习**：认识 Agent 的协同与冲突结构；
2. **交互感知的约束最优混合演化算法**：利用交互结构产生更好的 Agent 版本；
3. **面向跨轮次 RSI 的交互记忆与保留能力约束演化**：让后续改进利用历史结构和经验，同时控制能力遗忘。

三个方向分别对应 Paper 1、Paper 2、Paper 3 的目标，但均为待验证研究假设，不代表已成立创新或已完成实验。第三项不再被简单删除，但其独立新颖性风险最高，必须单独通过强基线审查。

## 1. RSI 的工作定义与边界

### 1.1 本课题研究的是 Agent 系统级 RSI

定义 Agent 为：

\[
A_t=\langle M,H_t\rangle,
\]

其中：
- \(M\)：冻结的基础 LLM；
- \(H_t\)：第 \(t\) 轮 Agent harness / 系统配置，包括 Prompt、规划、工具路由、记忆、验证/恢复策略、工作流及可执行模块。

RSI 轮次由以下闭环组成：

1. 当前 Agent 执行下游任务并产生轨迹；
2. 从轨迹中提取失败、成功、模块使用和任务表现证据；
3. LLM 根据证据提出候选模块修改或配置候选；
4. 演化计算对候选进行种群维护、交互感知重组、选择和约束检查；
5. 经过独立评价的候选成为下一轮 Agent 版本和后续搜索的父代；
6. 新版本继续执行任务并参与下一轮自我改进。

递归性体现在：被改进的 Agent 版本不仅解决下游任务，也影响下一轮的轨迹、诊断和候选修改；演化算法负责将每一轮的改进纳入可重复的搜索过程。

### 1.2 明确不做什么

- 不把“让 LLM 反思一次”称为 RSI；
- 不把单轮 Prompt 优化冒充递归自我改进；
- 第一阶段不递归训练基础模型权重；
- 不允许 LLM 自行决定最终候选是否接受；
- 不允许演化过程访问 held-out/test 标签；
- 不允许把安全、权限、工具接口等硬约束变成可被性能收益抵消的软目标。

基础模型先冻结，优先研究 harness / Agent 配置级 RSI。若后续证据支持，可使用 A800 训练小型交互迁移预测器或改进收益预测器；这不等于微调基础 LLM，也不单独作为第四个创新点。

## 2. 三个创新点的依赖关系

| 创新点 | 核心问题 | 输出 | 下游作用 |
|---|---|---|---|
| I：交互结构学习 | 当前 Agent 在特定任务、父代和配置背景下，哪些组件存在非加性依赖？ | 局部交互后验、置信度、可识别性状态、加权 VIG | 为 II 构造 FOS / linkage |
| II：约束最优混合演化 | 如何利用交互结构重组 Agent，同时保持合法性和随机评价下的选择可靠性？ | 经过验证的新 Agent 候选及谱系 | 产生 RSI 下一轮的父代版本 |
| III：跨轮次交互记忆与能力保持 | 任务变化后，哪些历史交互和改进块可以迁移？如何避免遗忘？ | 可迁移交互记忆、漂移状态、保留能力约束下的演化档案 | 支持长期 RSI 的持续改进 |

三项之间不是重复做三次 Agent 搜索：I 的贡献是估计器，II 的贡献是单轮演化算子，III 的贡献是跨轮次状态与迁移/保留机制。

## 3. 创新点一：RSI 轨迹驱动的任务条件化组件交互结构学习

### 3.1 研究问题

AHE 已报告 Agent harness 组件具有非加性交互；ShapleyFlow 已研究固定工作流中组件模型升级的全组合归因。因此，本课题不能声称首次发现 Agent 组件交互。

候选问题收敛为：

> 在 Agent RSI 的随机 rollout、任务异质、类别型模块和合法配置约束下，能否以有限评价预算估计当前父代与任务上下文下的局部 fitness interaction，并将其转化为比已有归因/fitness-linkage 方法更可靠的演化 linkage 证据？

### 3.2 候选估计量

对当前父代 \(x\)、任务上下文 \(z\)、模块槽位 \(i,j\) 和共同合法支持背景 \(u\)，使用 objective-scale 的条件四格差分：

\[
\Delta_{ij}(x,z;u)=
J(x_{ij}^{++},z;u)-J(x_{ij}^{+-},z;u)
-J(x_{ij}^{-+},z;u)+J(x_{ij}^{--},z;u).
\]

多类别模块通过预注册的类别对比扩展。对随机执行结果不把单次得分当作确定适应度，而是使用 task-block 配对数据估计 \(\Delta_{ij}\) 的后验分布和不确定性。

输出至少包含：
- 当前 parent/task 条件化的局部交互后验；
- 正负方向与非加性强度；
- 后验不确定性和校准结果；
- legal common-support / identifiability 状态；
- 由固定 FOS builder 生成的 FOS（图本身不等于 FOS）。

全局 RMS interaction energy 只作为任务条件化的总体摘要，不直接替代 parent-specific linkage。22 号 proposal 仍只是接口提案，尚未通过独立复审，不得直接实现。

### 3.3 候选主动采样

在相同 rollout-equivalent 预算下，比较：
- 随机合法配置采样；
- 固定分数因子 / sparse fixed design；
- D-optimal / Bayesian D-optimal；
- MESH-Harness 的 additive surrogate / bandit 方案；
- ShapleyFlow 可执行的全组合归因适配；
- FBL、DLED/cDLED、Linkage Kernels、LMM、ALI/AIM；
- 候选 task-conditioned local posterior acquisition。

主动采样只有在同预算下改善边恢复、校准或下游搜索时才保留。

### 3.4 假设与停止条件

- H1a：在已知真值的合法类别配置 landscape 上，候选估计器优于普通 pairwise OLS 和 additive surrogate；
- H1b：在 task-family / parent 条件变化时，候选估计器能识别符号变化和背景变化，且不把无共同支持的边强行输出；
- H1c：更关键，learned local linkage 必须提高下游 GOM 搜索，而不仅仅提高 AUPRC。

如果 H1a/H1b 成立但 H1c 不成立，则统计估计器不能作为 EC 主线创新，必须停止或重构。

## 4. 创新点二：交互感知的 Agent 约束最优混合演化

### 4.1 研究问题

已有 GOMEA、FBL、DLED/cDLED、conditional GOMEA、LK-GOMEA 等成熟方法；Agent 自动设计中也已有 DGM、MESH-Harness、EvoMAS、AgentEvo、AHE 等工作。不能把“将 GOM 用于 Agent”本身作为创新。

候选问题：

> 在类别型 Agent 配置、接口/权限/调用依赖硬约束和随机任务评价下，如何将局部交互后验转化为有效的 FOS/mixing，并降低破坏性重组和误接受？

### 4.2 候选算法流程

1. **初始化种群**：在合法配置空间内生成可执行 Agent 版本，固定模型、工具和任务环境。
2. **FOS 构造**：从创新点一的局部加权 VIG 出发，使用固定 Linkage Tree / Conditional FOS builder；所有 linkage estimator 使用同一 builder，以隔离估计器贡献。
3. **可行 donor 选择**：供体候选必须满足槽位类型和硬约束；后验兼容性只作为软排序信息。
4. **GOM mixing**：按 FOS 子集尝试引入供体模块；正负交互都可能表示非加性依赖，不能只保留正边。
5. **确定性最小修复**：仅允许唯一、预注册、可审计的局部修复；无法唯一修复或修复范围超限则拒绝。
6. **配对序贯接受**：父代/子代在相同 task blocks 下评价，采用预注册的置信界和跨 proposal alpha-spending 控制；不能把同一任务的重复 rollout 当成独立任务块。
7. **谱系记录**：记录父代、供体、FOS 子集、修复、任务块、评价成本和性能差值。

### 4.3 强基线

- Random legal search / mutation-only / standard GA；
- standard GOM / GOMEA / Conditional GOM / LK-GOMEA；
- oracle linkage / random linkage / learned linkage；
- FBL / DLED / cDLED / LMM / ALI；
- MESH-Harness / AHE / DGM / EvoMAS / AgentSquare 等 Agent 自动设计方法。

不能声称完全复现未运行的开源方法。无法复现时必须说明“论文设置可比适配”，并给出差异。

### 4.4 假设与停止条件

- H2a：oracle linkage 在固定预算下优于 standard/random linkage，证明当前任务存在可利用的 linkage；
- H2b：learned linkage 接近 oracle，并优于 FBL/cDLED 等强基线；
- H2c：constraint-aware GOM 的收益不能被额外 rollout、修复成本或模型差异解释；
- H2d：序贯接受降低误接受率，且不以严重牺牲搜索效率为代价。

若 oracle linkage 无收益，停止当前 GOM 假设；若 oracle 有收益但 learned linkage 无收益，回到创新点一修订；若所有收益都来自 repair 或额外评价，不保留算法创新主张。

## 5. 创新点三：面向跨轮次 RSI 的交互记忆与保留能力约束演化

### 5.1 研究问题与已知先行工作

新近工作已覆盖部分相关机制：

- DGM：维护 Agent 档案，按性能和探索程度选择父代；档案维护与父代选择本身不是空白。
- CPE：对 workflow、skill、model、memory 演化引入能力保持机制；不能把“加一个 retention regularizer”作为创新。
- HarnessEvolve：使用当前 batch 改进 + 最近 batch 不退化的性能门，以及 epoch-end validation；不能把“加回归门禁”作为创新。
- EvolveNet：本地 workload 并行演化、scope-typed program aggregation 和共享更新；不能把“多任务经验合并”作为创新。
- 2026-11-02 的 continual harness study：已证明跨任务持续演化存在严重遗忘，并归纳 verification / workflow / budget-strategy conflicts；它是重要问题定义和实验基线，不是一个完整 EC 算法。

因此，本课题候选创新不能停留在普通经验库、全局档案、简单回放、通用性能门或跨任务合并。

### 5.2 候选机制：interaction-conditioned evolutionary memory

维护跨轮次档案：

\[
\mathcal M_t=\{(x_a,\mathbf U_a,\mathcal G_a,\mathcal L_a,\mathcal E_a)\},
\]

其中：
- \(x_a\)：Agent 配置/版本；
- \(\mathbf U_a\)：不同 task family 的性能向量及不确定性；
- \(\mathcal G_a\)：按 task family / parent context 估计的局部交互结构；
- \(\mathcal L_a\)：演化 lineage、父代、donor 和 mixing 记录；
- \(\mathcal E_a\)：编辑证据、执行轨迹摘要和验证结果。

候选机制分四步：

**A. 交互结构漂移检测。**  
对相同 task family 的历史交互后验与当前交互后验比较，识别稳定边、符号翻转边、结构新增/消失边和不确定边。漂移较小时允许复用历史 linkage；漂移较大或共同支持不足时重新估计，不直接迁移。

**B. 条件化 linkage block 复用。**  
复用对象不是整份 Agent 或整张全局图，而是具有来源 task family、适用上下文、证据强度和历史收益记录的 linkage block / module building block。只有在目标任务上下文相似、交互结构兼容且历史转移收益可信时才允许作为 donor/mixing 候选。

**C. 保留能力约束下的演化生存者选择。**  
设 \(\mathcal K_t\) 为历史保护 task families，候选 Agent \(x'\) 的新任务效用为 \(U_{new}(x')\)。初步采用带容忍度的 retention constraint：

\[
\operatorname{LCB}_{1-\alpha}
\left(U_k(x')-U_k(x_k^{\mathrm{anchor}})\right)
\ge -\epsilon_k,
\quad \forall k\in\mathcal K_t.
\]

若多个历史能力存在真实冲突，不强行压成单一加权平均，而维护在“新任务适应—历史能力保持—成本”上的 Pareto / quality-diversity 候选档案。保护任务评估使用独立 replay/validation blocks，不能让测试集进入档案更新。

**D. 漂移条件化的迁移预测器（可选训练组件）。**  
从历史轮次收集“源任务上下文、局部交互块、目标任务上下文、迁移后增益/回归”数据，训练轻量 transferability predictor，估计某个 linkage block 在目标任务上的预期收益和遗忘风险。先比较 nearest-neighbor、统计回归、GBDT 与小型神经网络；只有预测器在 held-out task families 上显著优于简单方法时才保留。A800 可用于该小模型训练，但不要求微调基础 LLM。

### 5.3 该创新与先行工作的差异边界

| 先行方法 | 已覆盖内容 | 本课题不能重复的内容 | 候选差异 |
|---|---|---|---|
| DGM | 全 Agent 档案、开放式探索、父代选择 | 普通档案与探索选择 | 档案中保存 task-conditioned local linkage 和迁移证据，并按交互兼容性复用块 |
| CPE | 多演化通道的能力保持约束 | 通用 retention regularizer | 以局部交互漂移和 linkage block 为迁移对象，并把保持约束嵌入种群演化 |
| HarnessEvolve | 当前 batch + 最近 batch gate、快照池、验证集选优 | 普通性能回归门 | 跨任务家族长期保护 + 交互条件化迁移 + 演化档案 |
| EvolveNet | 本地并行演化、scope-typed program aggregation | 普通跨 workload 聚合 | 单个 RSI 演化谱系内的交互块迁移与 drift-aware GOM；EvolveNet 仍需作为强邻近基线 |
| Continual harness study | 任务序列设置、遗忘现象和冲突分类 | 仅重复证明遗忘 | 通过 EC 结构学习和种群选择解决遗忘/迁移冲突 |

该差异只是研究假设，必须精读原文和复现关键基线后确认，不能据此宣称“首次”。

### 5.4 假设与停止条件

- H3a：任务条件化交互记忆比 latest-only、whole-agent archive 和无交互记忆更能预测可迁移模块块；
- H3b：drift-aware transfer 比 direct transfer 和 from-scratch relearning 在同预算下更有效；
- H3c：retention-constrained Pareto evolution 在提升新任务性能时，显著降低旧任务回归；
- H3d：迁移预测器若不能优于简单检索/统计模型，则不使用神经网络，不为使用 A800 强行增加模型。

若第三项仅复现 CPE/HarnessEvolve 的通用保持门，或不优于 DGM/EvolveNet 的档案/聚合基线，则不形成独立 Paper 3，只作为 Paper 2 的长期泛化实验。

## 6. 任务与实验平台候选

优先采用有程序化验证的编码 Agent 任务流，以便明确 RSI 的多轮能力变化：

| 任务家族 | 候选数据集 | 任务能力 |
|---|---|---|
| 代码修复 | SWE-bench Verified | 定位并修复真实代码仓库 issue |
| 测试生成 | SWT-Bench | 生成能暴露缺陷、并在修复后通过的测试 |
| 功能实现 | FeatureBench | 在真实仓库中实现新功能，并检查 F2P/P2P |

2026-11-02 的持续演化研究已使用这三类任务构造 task stream，并报告跨任务遗忘。SWE-bench Verified 含 500 个经人工验证的实例；其论文因资源限制分别抽样 50、50、30 个任务用于演化。我们只借鉴任务类型和序列实验设计，正式样本量必须根据本课题 pilot、算力和 API 预算重新确定，不直接照搬其数字。

正式实验至少包含多个任务顺序、多个独立随机种子和 held-out task family；任务顺序、模型版本、工具权限、任务划分和预算须预先冻结。

## 7. RSI 实验评价体系

除单轮任务成功率外，第三项必须报告长期指标：

- **Current-task adaptation**：新任务家族上的性能增益；
- **Backward retention / forgetting**：历史任务家族的绝对和相对性能下降；
- **Average cumulative performance**：跨轮次、跨任务家族的累计表现；
- **Worst-family performance**：最差任务家族表现；
- **Forward transfer**：历史交互记忆对新任务的增益；
- **Transfer precision / negative transfer rate**：被复用模块块的有效比例与负迁移比例；
- **Interaction drift detection**：漂移识别准确率、误报率和漏报率；
- **Cost**：每轮 rollout、token、API 成本、训练时间和总 wall-clock；
- **Stability**：多个独立随机种子下的方差、置信区间和回归率。

不能只报告 best-so-far；也不能只报告平均任务成功率掩盖单个任务家族的灾难性退化。

## 8. 强基线矩阵

| 创新点 | 必须比较 |
|---|---|
| I：交互结构学习 | full factorial/CCI、pairwise OLS、ShapleyFlow、MESH additive surrogate、FBL、DLED/cDLED、Linkage Kernels、LMM、ALI/AIM、random/fixed design |
| II：交互感知 GOM | GA、mutation-only、standard GOM/GOMEA、Conditional GOM、LK-GOMEA、oracle/random/learned linkage、MESH-Harness、AHE、DGM、EvoMAS |
| III：跨轮次 RSI | latest-only sequential evolution、DGM archive、CPE、HarnessEvolve、EvolveNet、AHE/Meta-Harness continual adaptation、no interaction memory、no retention constraint、no drift detection |

基线复现状态必须逐一标记：OFFICIAL REPRODUCTION、PAPER-SETTING ADAPTATION 或 CONCEPTUAL COMPARISON。不得把概念对比写成已复现。

## 9. 模型调用、训练和算力分工

- DeepSeek-Flash API：冻结的基础模型，用于 Agent 任务执行、轨迹分析和候选修改建议；固定具体 API model ID / 参数 / 日期。
- 演化计算：本地 Python 实现，负责 genotype、population、FOS、GOM、约束、选择和谱系管理。
- A800：优先用于第三项的轻量交互迁移预测器/收益预测器训练，或必要的统计代理模型训练。
- 不在第一阶段训练基础模型；如后续要加入 LoRA/SFT，必须单独定义训练数据、目标、遗忘风险和对照，不能与 harness RSI 的收益混淆。
- LLM 只生成候选或诊断；最终接受/拒绝必须由环境执行、确定性约束检查和预注册统计规则决定。

## 10. 三篇小论文的预期结构

| 论文 | 暂定主题 | 核心独立贡献 | 关键否证 |
|---|---|---|---|
| Paper 1 | Task- and Parent-Conditioned Interaction Learning for RSI Agents | 随机、合法、任务异质 Agent 配置中的局部交互学习与预算分配 | learned linkage 不能改善下游搜索则不成立 |
| Paper 2 | Interaction-Aware Constrained Gene-Pool Optimal Mixing for Agent RSI | 交互结构驱动的类别型约束 GOM 和可靠接受机制 | oracle linkage 无益或 learned 不优于强基线则停止 |
| Paper 3 | Interaction-Memory-Aware Continual Evolution for RSI Agents | 漂移感知交互记忆、条件化块迁移和保留能力约束的种群演化 | 不优于 CPE/HarnessEvolve/DGM/EvolveNet 则不独立成篇 |

三篇论文不是保证录用的承诺。开题目标是三个有独立假设的创新方向；实际成果可以是 2–3 篇，取决于各自 Gate。

## 11. 阶段顺序与 Gate

- **Gate-0（问题与规格）**：冻结 RSI 定义、Agent genotype、任务流、评价器和硬约束。
- **Gate-1（Paper 1）**：TCAIL 数学规格通过独立审查；合成真值和强基线对照；必须证明下游 linkage 有效。
- **Gate-2（Paper 2）**：oracle linkage、learned linkage、GOM 和强基线完成同预算比较。
- **Gate-3（Paper 3）**：多轮任务流上证明交互记忆/漂移迁移/能力保持的独立收益；对照 CPE、HarnessEvolve、DGM、EvolveNet 和 2026-11-02 continual study。
- **Gate-4（论文整合）**：三个研究内容的共同 RSI 闭环和各自独立贡献均可复现。

Gate 顺序不可跳过。第三项可先做问题定义和文献审查，但不能在前两项机制未通过时开展大规模实验。

## 12. 当前项目状态和禁止事项

- TCAIL V2.1：REQUEST CHANGES / IMPLEMENTATION BLOCKED；
- 22 号 local-linkage/FOS 接口文件：PROPOSAL / PENDING INDEPENDENT REVIEW；
- CI-GOM：冻结，未实现、未实验；
- RSI 第三项：本文件仅为研究设计候选，尚无正式算法规格；
- 没有正式 Phase 0 性能实验，没有本课题真实 LLM 实验结果；
- 本轮仅调整开题研究框架，不调用 DeepSeek API，不启动 GPU 训练。

**当前决策：** 将论文方向调整为 RSI 系统级自我改进；把三个创新点正式作为开题阶段的三个研究目标；仍以证据 Gate 决定每项是否成立，不预先写成既有成果。


## 13. 2026-11-03 持续 RSI 相关工作复审补充

新增直接相关工作包括 CPE（arXiv:2605.09315）、HarnessEvolve（arXiv:2609.00829）、EvolveNet（arXiv:2608.04968）、Can Coding Agents Sustain Continual Evolution without Forgetting?（arXiv:2611.03219）和 Are Self-Evolving Agents Continual Learners?（arXiv:2610.25858）。完整机制对照见 28_RSI_CONTINUAL_RESEARCH_AUDIT_R1.md。

尤其是 Chen et al. (2026) 对 ReasoningBank、GEPA、Meta-Harness 的 task-free drift-stream 比较显示：全局 prompt/workspace 修改会导致跨任务干扰和知识覆盖；相似度检索会出现 foreign-memory injection 与 retrieval collision。因此第三创新点进一步限定为“可观察任务上下文 + 局部交互签名”联合条件化的 linkage-block memory 与漂移感知迁移，不能只依赖 query embedding，也不能读取 task-family 标签或任务流 block boundaries。

第三项强基线补充：DGM、CPE、HarnessEvolve、EvolveNet、ReasoningBank、GEPA、Meta-Harness、AHE/Meta-Harness continual adaptation。若无法官方复现，必须标记 paper-setting adaptation。

**研究状态不变：** 本文件仍为研究设计候选；TCAIL V2.1 REQUEST CHANGES；22 号接口提案待独立复审；CI-GOM 未实现；IMCE-RSI 尚无正式算法规格。

## 14. IMCE-RSI 的双键记忆检索与 retrieval-collision 处理

为避免第三项停留在泛化的“交互记忆”，进一步将历史 linkage block 的检索设计为上下文键与交互键联合条件化。

当前任务的上下文键 (z_t) 只由可观察输入、工具 schema、环境元数据和执行轨迹摘要构成；交互键 (G_t) 来自创新点一估计的局部交互后验、方向、不确定性、共同支持状态和 FOS。候选记忆检索可按以下兼容性评分：

\[
S(m\mid z_t,G_t)=
\lambda_z\,\mathrm{sim}(z_t,z_m)
+\lambda_G\,\mathrm{compat}(G_t,G_m)
-\lambda_u\,\mathrm{uncertainty}(m).
\]

候选流程：
1. 根据可观察上下文召回多个历史记忆；
2. 使用交互签名检查 linkage block 兼容性和历史收益；
3. 如果语义相似的历史记忆具有冲突的交互方向、工作流依赖或迁移结果，触发 retrieval-collision 标记；
4. 对高不确定性或冲突候选执行有限的合法配对探测；预算不足时 abstain，不强制迁移；
5. 只有迁移收益置信下界为正且历史能力保持约束通过，才将该 block 加入 GOM donor/mixing 候选。

漂移检测只依赖滚动窗口中的可观察上下文和交互后验，不依赖任务家族标签或 block 边界。标签仅用于离线评价。必须比较 context-only、interaction-only、dual-key、dual-key without collision detection 和 dual-key without active probe。

新增指标：retrieval collision rate、memory precision、negative-transfer rate、abstention rate、probe cost、transfer calibration。若 dual-key 检索不能优于 ReasoningBank-style similarity retrieval 和 DGM whole-agent archive，则不保留该机制。


## 15. 参数调节与实验 Gate

三个创新点的参数、候选范围、调参顺序、A800 轻量迁移预测器条件、同预算基线和停止规则详见 `29_PARAMETER_TUNING_AND_EXPERIMENT_GATES_R1.md`。该文件只定义实验设计，不代表已执行。