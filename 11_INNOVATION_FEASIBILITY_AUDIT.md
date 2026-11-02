# 11 — 创新点可行性审查与研究路线修订

**审查日期：** 2026-11-02  
**审查范围：** 只使用本仓库已有文献与本轮公开论文原文/出版页面；未读取用户其他 GitHub 仓库。  
**总体状态：** 两个核心创新候选值得进入小规模预实验；第三个创新点暂不批准。  
**重要：** 本文是文献和方法可行性审查，不代表实验已经完成，也不构成“首次提出”的证明。

---

## 1. 结论摘要

| 研究项 | 当前判断 | 学术新颖性 | 工程可行性 | 能否现在写成正式创新点 |
|---|---|---:|---:|---|
| 原创新点一：普通组件交互效应估计 | **NO-GO（原表述）** | 低 | 高 | 否 |
| 修订创新点一：预算受限、任务条件化的稀疏交互结构识别 | **HOLD / 可做预实验** | 中 | 中高 | 暂不 |
| 修订创新点二：交互结构驱动的约束最优混合演化 | **HOLD / 优先预实验** | 中 | 中高 | 暂不 |
| 创新点三：跨任务交互结构迁移 | **HOLD / 暂不纳入核心开题** | 偏低至中 | 中 | 否 |

**当前建议：以两篇独立方法论文为主线推进。第三篇只作为储备，不为了满足数量强行凑创新。** 用户要求 2–3 个创新点，因此两个经验证的创新点已经符合范围。

## 2. 直接相关工作造成的关键变化

### 2.1 More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding

Ming Liu, arXiv:2605.05716, 2026-05-07，预印本。

论文对 Planning、Tool Use、Memory、Structured Reasoning、Reflection 五个组件做 \(2^5=32\) 种全因子组合实验，使用 HotpotQA/GSM8K 和多个模型规模，计算 Shapley 值并分析组件干扰。论文报告了一个三阶 Harsanyi dividend。

特别重要的是：作者的主效应回归在其 HotpotQA/Llama-8B 设置下 LOOCV \(R^2=0.872\)，加入 10 个 pairwise terms 后 LOOCV \(R^2=0.748\)，并认为 pairwise model 过拟合。其三阶效应是探索性分析，不应被表述为已经建立了普遍可靠的高阶交互估计方法。

**对本课题的影响：**
- “组件之间存在协同/拮抗”已经不是新问题；
- “做全因子实验、计算两两交互、Shapley 归因”不能作为创新点；
- 直接把二阶差分公式搬到 Agent 上不够；
- 可研究的差异只能进一步收窄到：多实现/混合类型的可执行 Agent 模块、随机轨迹噪声、任务条件化、昂贵评价预算，以及交互结构如何服务于演化算子；
- 该论文主要研究静态 prompt-based scaffolding，采用有限步数；它没有直接解决可执行模块池中的预算受限演化搜索，但它是必须比较的直接先行工作。

### 2.2 A Regression Framework for Understanding Prompt Component Impact on LLM Performance

Andrew Lauziere, Jonathan Daugherty, Taisa Kushner, EXPLAINABILITY 2026（IARIA），2026。研究 Prompt 组件特征与 LLM 性能之间的回归关系，并涉及 pairwise interaction model。

**影响：** 不能把“为 Prompt 组件建立回归模型”作为创新。研究对象必须从静态 prompt feature 扩展到可执行 Agent 模块的任务条件化、预算受限交互发现，并且需要证明其与现有回归框架不同。

### 2.3 MESH-Harness

MESH-Harness, arXiv:2610.05300，2026。模块槽位与候选池、shared embedding、full-covariance LinUCB、mixed-start coordinate ascent、执行轨迹驱动的模块编辑。

其论文公式明确说明：
- 预测均值是 slot-wise additive；
- full covariance 的 off-diagonal blocks 记录不同槽位表示的共同出现，影响参数估计和不确定性；
- 它没有显式加入 pairwise reward interaction features。

**影响：** 它是强组合搜索与评价预算分配基线。修订方法必须证明显式交互项的预测增益和搜索增益，不能把“使用全协方差”误称为“已经拟合非加性 epistasis”，也不能忽略其组合搜索能力。

### 2.4 ARTEMIS、AgentSquare、EvoMAS、AgentEvo、HFlow、AgentBreeder

- ARTEMIS：已经使用语义感知 mutation/crossover 联合优化混合类型 Agent 配置；
- AgentSquare：已经使用 Planning/Reasoning/Tool Use/Memory 模块化搜索、module evolution 和 module recombination；
- Hu et al. 的 EvoMAS：已经使用结构化 MAS 配置、执行反馈引导的 mutation/crossover 和经验记忆；
- Wei et al. 的 EvoMAS：已经使用七种演化策略、自适应策略选择、角色演化和课程式工作流演化；
- AgentEvo：已经使用探索、精炼、交叉的多阶段演化和性能—成本 Pareto archive；
- HFlow：已经使用结构、Prompt、模型的变异/交叉、人类偏好和层级经验记忆；
- AgentBreeder：已经使用多目标 scaffold 演化。

**影响：** 普通模块重组、语义交叉、反馈变异、多阶段演化、Pareto 选择都不能单独作为创新。

### 2.5 经典演化计算已覆盖 linkage learning

必须对照：
- GOMEA / LTGA：基于 linkage model / Linkage Tree 学习变量依赖，并通过 Gene-pool Optimal Mixing 对 linkage subset 做 donor mixing；
- CGOMEA：进一步利用条件依赖过滤 donor mating；
- DSMGA-II：图结构 linkage model；
- LK-GOMEA：为不同解的局部邻域学习不同 linkage structure，处理 multi-structured landscapes；
- DG2 / RDG：基于适应度差分或非线性检测识别变量交互/分组。

**影响：** “用交互图指导 crossover”本身不是 EC 创新。必须说明 Agent 组件的语义类型、接口约束、合法组合空间、任务条件和随机执行噪声给 linkage learning 与 optimal mixing 带来了什么新问题，以及提出了什么实质新算法。

---

## 3. 修订创新点一：预算受限的任务条件化 Agent 组件交互结构识别

### 3.1 建议工作题目
《面向随机执行智能体配置的预算受限交互结构识别方法》

### 3.2 科学问题
Agent 的每个功能槽位可能存在多个可执行实现。完整配置组合空间随槽位数和实现数呈指数增长；执行结果受到任务差异、模型采样和环境状态影响。全因子实验昂贵，单纯加性 surrogate 可能忽略组合效应，而不加约束的 pairwise regression 又可能过拟合。

### 3.3 候选方法（必须通过预实验验证）
将 Agent 配置表示为带类型和依赖约束的离散模块选择向量 \(x=(x_1,\ldots,x_m)\)，任务上下文为 \(z\)，观测回报为 \(y\)。

候选模型：
\[
F(x,z)=\beta_0(z)+\sum_i f_i(x_i,z)+\sum_{i<j}g_{ij}(x_i,x_j,z)+\epsilon.
\]

其中：
- \(f_i\)：模块主效应；
- \(g_{ij}\)：条件化组件交互项；
- 对 \(g_{ij}\) 使用稀疏/层级收缩，只有数据支持时才保留交互；
- 允许高阶项作为扩展，但不得一开始就无约束拟合所有三阶/四阶项；
- 对同任务、同初态、可控随机种子进行配对执行；API 不支持固定 seed 时采用 task-blocked repeated runs；
- 对不合法的四格组合不计算伪因果差分，而是在可行组合空间中进行条件估计。

交互效应的局部差分定义可写为：
\[
\Delta_{ij}(x_{-ij},z)=F(x_i',x_j',x_{-ij},z)-F(x_i',x_j,x_{-ij},z)
-F(x_i,x_j',x_{-ij},z)+F(x_i,x_j,x_{-ij},z).
\]

该式是估计目标的工作定义，不是创新本身。

### 3.4 必须形成的真正算法贡献
不能只拟合一个回归式。候选算法至少需要包含：
1. 任务分层/条件化的交互模型；
2. 稀疏、层级且带不确定性的交互结构估计；
3. **主动实验设计**：根据交互参数的不确定性、候选结构的重要性和单次执行成本，选择下一组最有信息价值的合法配置；
4. 对随机执行结果进行配对估计和置信度校准；
5. 明确识别何时应退回加性模型，避免无证据地引入交互项。

可考虑以每次评价带来的预期交互不确定性下降/执行成本作为采样准则；具体形式须经推导和消融，不能先定名再找理由。

### 3.5 对照方法
- 全因子实验（小规模可行空间的 oracle reference）；
- 主效应回归；
- 普通 pairwise OLS；
- 稀疏回归/层级交互模型；
- Shapley / Harsanyi interaction（小规模组合）；
- MESH-Harness 的 additive full-covariance LinUCB；
- 随机配置采样；
- 固定 pairwise / fractional-factorial design；
- 适用时对照 DG2/RDG 的交互分组思想。

### 3.6 实验与指标
- 先在已知真值的合成 Agent landscape 上测试交互恢复；
- 再在可执行模块化 Agent 上验证；
- 指标：交互效应 RMSE、符号识别 F1、图结构 Precision/Recall、置信区间覆盖率、未执行配置预测误差、固定评价预算下的 best-so-far regret；
- 消融：无任务条件、无稀疏收缩、无主动采样、无配对执行、无高阶筛查；
- 关键比较：相同执行预算下，能否比 MESH 的加性 surrogate 和普通 pairwise model 更准确地恢复有效交互，并提升后续搜索。

### 3.7 可行性判断
- **工程可行性：中高。** 可从 4 个固定槽位、每槽位 2 个实现开始，先做 16 组合全因子小实验，建立可控真值和基线；再扩展到更多实现并检验主动采样。
- **学术新颖性：中等、尚未确认。** CCI 与 prompt regression 已经覆盖交互分析；只有预算受限、任务条件化、可执行多实现模块和主动交互发现的算法增量得到证明，才值得投稿。
- **当前状态：HOLD。** 预实验若不能在相同预算下优于加性 MESH surrogate/普通 pairwise regression，则 NO-GO。

---

## 4. 修订创新点二：交互结构驱动的约束最优混合演化

### 4.1 建议工作题目
《面向类型约束智能体配置的交互保持最优混合演化算法》

### 4.2 科学问题
普通 Agent crossover 已被多篇工作覆盖；经典 GOMEA 已经通过 linkage subsets 和 optimal mixing 保留变量依赖。新的问题不是再提出一个 crossover，而是：

**当基因是有类型、接口、控制流和执行依赖的 Agent 模块，且 fitness 是有噪声的昂贵 rollout 结果时，如何学习可用的 linkage，并执行合法、低破坏性的块级最优混合？**

### 4.3 候选算法
1. genotype：固定功能槽位的模块 ID/参数，另附模块类型、接口、控制流/数据依赖约束；
2. linkage：使用创新点一得到的任务条件化交互结构，形成 FOS/linkage blocks；
3. donor mixing：从兼容父代中选择 donor，按 linkage block 替换组件；
4. contract-aware repair：只修复受影响的接口/依赖，不允许 repair 静默改变无关基因；
5. noisy acceptance：使用相同任务块的配对评价与序贯置信检验，只有满足预设改进/非劣门槛才接受；安全和结构硬约束先作为 gate；
6. population update：记录有效/有害重组、模块 lineage 和交互图版本。

### 4.4 必须证明的贡献
- 不是把 GOMEA 直接套到 Agent；
- 不是把交互图作为普通 crossover 的装饰；
- 必须提出适用于混合类型、依赖约束和随机 fitness 的新型 constrained optimal mixing 机制；
- 必须用 oracle linkage、估计 linkage、随机 linkage 做对照，隔离交互估计误差和算子贡献；
- 必须固定任务、模型、种群、评价次数和 repair 预算。

### 4.5 强基线
- standard GA / mutation-only；
- random component crossover；
- LLM semantic crossover（ARTEMIS 类）；
- AgentSquare module recombination；
- Hu-EvoMAS feedback-conditioned crossover；
- AgentEvo workflow crossover；
- MESH-Harness compositional search；
- GOMEA / LTGA / CGOMEA / DSMGA-II（在相同离散 genotype 上）；
- standard GOM + repair（区分新增机制）。

### 4.6 指标与消融
指标：valid offspring rate、harmful recombination rate、paired offspring improvement probability、held-out task success、每次有效提升的执行次数、repair cost、旧任务回退。

消融：
- 不用 linkage；
- 随机 linkage；
- oracle linkage；
- learned linkage；
- 无 contract repair；
- 无 noisy sequential acceptance；
- 标准 GOM；
- 仅 pairwise 与 task-conditioned linkage；
- 仅正交互块与正/负交互联合处理。

### 4.7 可行性判断
- **工程可行性：中高。** 先用固定槽位的 categorical genotype，不要第一版就搜索任意 DAG/任意代码；可在小规模工具任务中快速验证。
- **学术新颖性：中等、尚未确认。** Agent crossover 已密集；GOMEA/CGOMEA/LK-GOMEA 已有成熟 linkage 与 mixing。只有“Agent 组件约束 + 交互估计 + 噪声感知的块级接受”带来可重复增益，才构成方法创新。
- **当前状态：HOLD / 优先预实验。** 若它只是 GOMEA 的直接应用，或与 ARTEMIS/EvoMAS 的实际算子等价，则 NO-GO。

---

## 5. 创新点三：跨任务交互结构迁移（暂缓）

### 工作题目候选
《面向任务分布变化的智能体交互结构迁移演化方法》

### 当前问题
该方向与任务条件化交互估计、LK-GOMEA 的局部 linkage、HFlow 的层级经验记忆、EvoMAS 的 curriculum、Evo-Harness/TTHE 的跨任务更新有明显交叉。

### 暂缓原因
- 目前尚未证明不同任务之间存在稳定、可迁移的共享交互结构；
- 迁移收益可能只是任务相似度/经验复用，而不是新的 EC linkage 方法；
- 与创新点一的 task-conditioned estimator 容易合并，独立小论文贡献尚不清楚。

### 重启条件
先在不同任务家族上估计 linkage graph，验证：
1. 共享交互和任务特定交互可被统计地区分；
2. 迁移比从头估计节省评价预算；
3. 迁移不会明显增加负迁移和旧任务性能回退；
4. 其机制优于固定 linkage、直接迁移、LK-GOMEA 类局部 linkage 和普通 online harness evolution。

未满足前，不写成正式创新点三。

---

## 6. 建议的最小可证伪实验路线

### Phase A：可控交互地形（不调用真实 LLM）
- 4 个功能槽位，每槽位 2 个实现，16 个配置；
- 构造已知主效应、正/负 pairwise interaction、少量高阶交互、任务条件化交互和随机噪声；
- 比较 full factorial、main-effects、pairwise OLS、sparse interaction、active design；
- 先验证估计器在已知真值下是否有效。

### Phase B：真实 Agent 小规模试验
- 固定 Agent 执行模型、工具集合和评分器；
- 选择 4 个槽位：planning、tool routing、memory、verification/recovery 中的 4 个；
- 每槽位 2 个可替换实现；保持接口一致；
- 任务优先使用可程序化检查状态的工具任务，如 ToolSandbox、AppWorld 或 τ-bench；
- 对每个任务、配置、seed 保存完整轨迹和最终状态；训练/验证/测试任务严格分开。

### Phase C：演化算法对照
- 用同一 genotype、同一 population initialization、同一 evaluation budget；
- 对比 standard GA、Agent crossover、GOMEA/GOM、random linkage、oracle linkage、learned linkage；
- 分别报告 oracle linkage 和 estimated linkage 结果；
- 若 oracle linkage 有效而 estimated linkage 无效，说明估计器是瓶颈；若 oracle linkage 也无效，说明 linkage-aware mixing 假设不成立。

### Phase D：跨任务迁移（仅在 A/B 通过后）
- 任务家族之间切换；
- 比较固定 linkage、独立学习、直接迁移、带漂移检测的更新；
- 只有出现可重复迁移收益才考虑第三篇。

---

## 7. 预期投稿路线与风险

| 小论文 | 当前主题 | 当前状态 | 投稿前必须达到 |
|---|---|---|---|
| Paper 1 | 预算受限任务条件交互结构识别 | HOLD | 已知真值恢复 + 真实 Agent 预测/搜索收益 + 同预算胜过 MESH/additive 和普通 pairwise |
| Paper 2 | 交互结构驱动的约束最优混合演化 | HOLD，优先 | 同预算优于 GOMEA/standard GOM/Agent crossover；收益能归因于新算子 |
| Paper 3 | 跨任务交互结构迁移 | 暂缓 | 明确独立机制、迁移收益和负迁移控制 |

**当前不建议对导师承诺三篇一定都能投稿。** 建议开题时将 Paper 1 和 Paper 2 作为两个核心研究内容，Paper 3 作为扩展研究方向，待前两项实验产生证据后再决定是否独立成篇。

---

## 8. 最终可行性结论

1. 原创新点一（简单组件交互估计）不成立，不能继续按原方案写。
2. 修订后的预算受限交互结构识别有研究空间，但必须从“分析组件”升级为“有限预算下主动学习可用于演化的交互结构”。
3. 交互结构驱动的约束最优混合演化是目前最值得优先验证的 EC 算法贡献，但不能只是 GOMEA 的直接应用。
4. 第三个跨任务迁移创新点暂缓，当前不具备足够独立性。
5. 因而本项目目前的合理目标是 **2 个核心创新点 + 1 个有条件的扩展方向**。这符合用户要求的 2–3 个创新点，但不虚构研究成果。


## 9. 第五轮：演化参数控制可行性（2026-11-02）

演化参数方案已独立形成，详见 13_EC_PARAMETER_CONTROL_PLAN.md。当前确定采用：
- 离线 irace/iterated racing 调参；
- 在线 discounted-UCB/AOS 控制变异强度与算子动作；
- 统计门禁预先锁定；
- 主算法 categorical GOM 不使用 DE 的 \(F,CR\)；
- Phase 0 固定种群并做敏感性，后续才比较 IMS/P3。

参数控制本身是成熟研究领域，且 Wei et al. EvoMAS 已使用 adaptive strategy selection。故本课题不能把 UCB/AOS 或 parameterless population management 单独作为创新点。只有当交互置信度与 Agent 约束重组的结合，在同预算实验中产生独立、可重复收益时，才保留相应方法。

当前创新点一和二仍为 HOLD；参数策略解决的是“如何公平、可复现地设定和控制算法参数”，并不自动证明创新性。


## 10. 第六轮：算法规格成熟度与风险更新（2026-11-02）

新增 14_FORMAL_ALGORITHM_DESIGN_V1.md。两个候选已有可实现的数学规格，但新颖性仍未确认。

### 新的关键风险
1. Group-ARD + posterior IG 是成熟统计工具的组合，必须证明其在 Agent 合法组合空间、任务条件化和随机评价下比 sparse fixed design / MESH additive surrogate 更有增益。
2. GOM + FOS 本身是经典方法；CI-GOM 必须证明 Agent contract repair、posterior donor compatibility 和 noisy sequential acceptance 不是工程包装，而是解决传统 GOM 在该问题设定中的具体失效模式。
3. 负交互同样是 linkage。V1 已将 FOS 建边从“只选正交互”修正为“可信非加性绝对强度”；符号只参与 donor score。
4. 可识别性门禁可能使部分边 abstain；这不是算法失败，而是防止在约束空间里制造伪交互。但若真实任务中大部分关键边都不可识别，Paper 1 的适用价值会受限。
5. anytime-valid acceptance 依赖独立、有界 task-block differences。若任务块相关或重复 rollout 伪独立，必须按 task family/cluster 重新定义统计单位。

### 更新后的判断
- TCAIL：HOLD，进入合成真值验证；
- CI-GOM：HOLD，优先做 oracle-linkage 对照；
- AOS：可选，只有同预算优于离线调参固定策略才保留；
- 第三创新点：继续暂缓。
