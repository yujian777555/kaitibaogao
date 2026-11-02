# 09 — 候选 G：组件交互感知的演化重组

**工作题目：** 面向大语言模型智能体的交互感知演化重组方法研究  
**状态：** PRIORITY FOR AUDIT / NOT APPROVED

## 1. 研究动机

Agent 配置不是相互独立的 Prompt 字段集合。规划、记忆、工具路由、验证、恢复和工作流控制等组件之间存在依赖、协同与冲突。

现有方法已大量采用 Prompt/模块变异、workflow crossover、Agent 配置重组、跨 lineage merge、role/topology evolution。但“把两个高分父代的组件拼起来”并不保证得到高分子代。一个组件的效果可能依赖另一个组件的上下文、接口和执行顺序。组件单独有效，不代表组合后有效。

## 2. 直接相关工作的缺口线索

### DarwinX
DarwinX 使用 additive patch merge 合并不同 lineage 的 harness 修改。论文明确指出，recombination 相对单 lineage mutation 的贡献仍需受控消融，且 archive、parent selector、recombination 和 inference effort 没有被独立随机化。

### EvoMAS / HFlow
两篇 EvoMAS 和 HFlow 已使用交叉、变异和反馈驱动的 Agent/workflow 演化。因此普通 crossover、LLM 反馈变异不能作为创新。需要核查它们是否显式估计组件间 epistasis/linkage。

### AgentSquare
AgentSquare 使用模块化设计空间和模块演化/重组。需要核查其固定模块槽位、模块兼容性、交叉粒度和结构依赖处理。

### HiveMind
HiveMind 使用 DAG-Shapley 估计 Multi-Agent workflow 中不同 Agent 的贡献。这是重要归因基线，但 Agent 级 Shapley contribution 不等同于单个 Agent 配置内部组件之间的 pairwise interaction effect。

### EvoCF / Optimas / SERO
EvoCF 的反事实主要用于协作计划；Optimas 研究组件局部奖励与全局表现对齐；SERO 通过结构契约保持角色池有效性。这些工作需要精读，判断是否覆盖配置组件交互和遗传重组。

## 3. 拟研究的核心机制

### 3.1 组件表示

将 Agent 配置表示为带类型、参数和依赖关系的图：

G = (V, E, τ, θ)

- V：组件节点；
- E：控制流、数据流或调用依赖边；
- τ：组件类型；
- θ：组件参数/Prompt/策略配置。

初期只选择有限、可执行的组件集合，不追求任意程序级开放搜索。

### 3.2 交互效应估计

对于两个组件 i、j，通过配对反事实替换估计交互：

ε_ij = f(χ_ij) - f(χ_i0,j) - f(χ_i,j0) + f(χ_i0,j0)

所有变体在同一任务实例、同一环境状态和配对随机种子下执行。需要定义合法参考状态和修复规则。

如果 ε_ij 显著为正，说明组件组合可能存在正协同；如果显著为负，说明可能存在冲突或拮抗。若置信区间覆盖零，则不强制建立 linkage。

### 3.3 Linkage graph

根据交互效应及其不确定性构造组件交互图：
- 强正协同：作为 co-adapted block 一起继承；
- 强负交互：禁止直接交叉或触发兼容性修复；
- 交互不明显：允许独立重组；
- 证据不足：保留原组件组合。

### 3.4 Interaction-aware crossover

1. 选择两个互补父代；
2. 根据交互图识别可继承的协同模块块；
3. 执行块级交换；
4. 根据类型和依赖关系进行 repair；
5. 在统一验证任务上评价子代；
6. 将实际子代结果反馈给交互图更新。

## 4. 预期创新点候选

1. 面向 Agent 配置的组件交互效应估计方法：通过配对反事实干预估计模块间协同/拮抗关系，区分组件主效应与交互效应。
2. 基于交互图的 linkage-aware evolutionary crossover：将组件协同关系转化为重组粒度和兼容性约束，降低无效组合和破坏性重组。
3. 可选：面向任务分布变化的交互图更新机制。若证据不足，不强行列为创新点。

## 5. 实验方案草案

### 任务环境
优先选择具有可复现工具执行轨迹、可控组件配置和确定性结果检查的 Agent 任务。可先用受控 tool-use benchmark，再用真实工具 Agent benchmark 外部验证。

### 对照组
Mutation-only；random component crossover；LLM-proposed crossover；AgentSquare-style module recombination；EvoMAS-style configuration crossover；HFlow-style workflow crossover；DarwinX-style additive merge；interaction-aware crossover。

### 指标
offspring validity / execution success、offspring task success、improvement probability over parents、harmful recombination rate、held-out task performance、interaction prediction accuracy、component graph stability。

### 消融
不使用交互效应；只用单组件主效应；随机 linkage graph；去除依赖约束；去除 repair；只保留正交互；只保留负交互约束；用 Shapley agent-level contribution 替代 pairwise gene interaction。

## 6. 关键风险

1. 已有 crossover 已覆盖。如果 EvoMAS/HFlow/AgentSquare 已显式建模组件交互并据此重组，候选 G 不成立。
2. 反事实干预不合法。某些组件不能独立替换，需要类型约束、默认实现和修复器。
3. 交互效应噪声大。需要配对随机种子、重复运行和置信区间。
4. 组合数量爆炸。先研究少量关键组件和 pairwise interaction，不做全量高阶交互。
5. 传统 linkage learning 已成熟。必须明确 Agent 配置的语义依赖、执行约束和轨迹反馈带来的新问题，而不是简单复刻 GOMEA/LTGA。

## 7. 下一步研究任务

1. 精读两篇 EvoMAS 的 crossover 伪代码；
2. 精读 HFlow 的 workflow/prompt/model crossover；
3. 精读 AgentSquare 的 module evolution；
4. 精读 DarwinX 的 additive merge 与 limitation；
5. 精读 HiveMind 的 DAG-Shapley；
6. 精读 EvoCF、Optimas、SERO；
7. 检索并比较 GOMEA、LTGA、DSMGA-II、Bayesian Optimization Algorithm 等 linkage-learning EC 方法；
8. 再决定候选 G 是 GO、HOLD 还是 NO-GO。

## 8. 新增直接工作与候选 G 的收紧条件（2026-11-02）

### MESH-Harness
MESH-Harness (arXiv:2610.05300) 已将 harness 划分为固定接口槽位，维护各槽位实现池，并用 full-covariance LinUCB 和 mixed-start coordinate ascent 选择模块组合，再用执行轨迹引导模块编辑。其预测均值仍是 additive slot-wise sum；full covariance 主要保留跨槽位共同出现统计并估计组合不确定性。因此：
- 不能声称“此前没有模块组合搜索”；
- 不能把 full covariance 简单说成已显式估计 epistasis；
- 候选 G 必须证明显式非加性交互估计对重组决策的增量价值。

### ARTEMIS
ARTEMIS (arXiv:2512.09108) 已做 semantic-aware genetic operators 和 Agent 配置联合演化。必须精读其组件自动发现、语义交叉、组件依赖处理和消融。若其已显式建模组件间非加性交互并指导重组，候选 G 的核心机制可能被覆盖。

### EvoMAS / AgentEvo
EvoMAS 已做配置空间中的 feedback-conditioned crossover/mutation；AgentEvo 已做 workflow subgraph graft、prompt fusion 和多阶段演化。候选 G 必须在机制上超过通用 crossover 与结构化 workflow recombination。

### 对三篇论文的影响
- 小论文一（交互效应估计）必须证明估计器本身可独立验证，不只是给 crossover 提供的中间模块。
- 小论文二（交互感知重组）必须证明交互图比 MESH 的组合选择、ARTEMIS 的语义遗传算子和 EvoMAS/AgentEvo 的交叉有独立增益。
- 小论文三（任务条件化交互图迁移）必须区别于 Evo-Harness、TTHE 等已有在线 harness/test-time evolution。

当前仍是候选方向，不得将本文件中的草案直接写成已确认创新点。


## 9. 第四轮严格修订：从普通交互感知交叉转为 constrained optimal mixing

新增先行工作 Liu (2026) CCI 和 Lauziere et al. (2026) Prompt component regression，说明普通交互分析已被覆盖。经典 GOMEA、CGOMEA、DSMGA-II、LK-GOMEA 又说明 linkage learning 和 optimal mixing 已是成熟 EC 方法。

因此候选 G 的可行形式不能是“计算 ε_ij → 画交互图 → 普通交叉”。修订为：

**面向类型约束 Agent 配置的交互结构驱动约束最优混合（interaction-guided constrained optimal mixing）。**

必须同时处理：
1. Agent 模块的混合类型基因；
2. 组件接口、调用关系和控制流依赖；
3. 从 noisy/expensive rollout 学到的 linkage；
4. donor block 替换后的最小化 contract repair；
5. 配对/序贯接受规则，避免随机 fitness 下误接受有害 offspring。

强基线必须包含 standard GOMEA/GOM、CGOMEA、DSMGA-II、LK-GOMEA、AgentSquare、ARTEMIS、Hu-EvoMAS、AgentEvo、MESH-Harness。

**状态：HOLD / 优先预实验。** 如果只是在固定模块槽位上套 GOMEA，或只增加接口检查而没有新的 linkage/acceptance 机制，则 NO-GO。
