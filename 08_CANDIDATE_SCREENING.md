# 08 — 候选方向筛选与当前决策

**更新日期：** 2026-11-02  
**当前状态：** 尚未确定最终选题；候选 G 优先审查。

## 1. 为什么必须重新筛选

截至 2026-11-02，直接 Agent 演化研究已覆盖多目标 Agent rollout 搜索、Agent skills、test-time adaptation、harness evolution、multi-agent topology、population-centered evolution、evolvability、evaluator co-evolution 和 capability preservation。不能再把“用遗传算法优化 Agent”当作充分创新。

## 2. 候选筛选表

| 候选 | 当前状态 | 已有直接覆盖 | 判断 |
|---|---|---|---|
| D：跨任务序列测试时演化 | NO-GO / SUPERSEDED | TTHE、Meta-TTL、TacoMAS、Inherit-MAS、EvolveNet、DarwinX | 宽泛问题已被直接覆盖 |
| E：弱反馈下的可信适应度与稳健选择 | HOLD | TTHE 的 judge selection、DarwinX 的 verifier-based avg@k、RQGM、Certified Selective Automation、evaluator calibration | 需要进一步明确“弱反馈、无原生 verifier”场景的机制缺口 |
| F：可进化性驱动的 Agent 父代选择 | HOLD / broad form covered | HGM 的 clade metaproductivity、Evolvability Search、Evolvability ES、CATArena、PCE、FreeEvolve | 不能只提出 offspring diversity / metaproductivity |
| G：组件交互感知的演化重组 | PRIORITY FOR AUDIT | EvoMAS、HFlow、AgentSquare、AgentBreeder 有 crossover；DarwinX 有 additive merge；HiveMind 有 DAG-Shapley；SERO 有结构契约 | 需要审查是否有人显式估计组件 epistasis 并指导 crossover |

## 3. 候选 G 的精确定义

目标不是“图结构 Agent 搜索”，也不是“用 Shapley 找贡献最大的 Agent”。目标是：

**在模块化 Agent 配置中，估计组件之间的协同/拮抗效应，并将其转化为可验证的 linkage-aware evolutionary recombination。**

示例组件：planning/reasoning policy、tool routing、memory read-write、verification/critic、retry/recovery、workflow control。

工作假设：不同组件的效果存在 epistasis。单独表现良好的两个模块不一定组合后仍然良好；任意交叉可能破坏 co-adapted component blocks。

## 4. 初步数学定义

设 Agent 配置为 χ，组件 i、j 分别有当前状态和参考状态。可定义配对反事实交互效应：

ε_ij = f(χ_ij) - f(χ_i0,j) - f(χ_i,j0) + f(χ_i0,j0)

其中 χ_ij：i、j 同时采用待测状态；χ_i0,j：仅将 i 替换为参考状态；χ_i,j0：仅将 j 替换为参考状态；χ_i0,j0：两者均为参考状态；f：在相同任务实例、相同环境状态和配对随机种子下测得的表现。

这是离散交互效应的工作定义。必须考虑组件不可独立替换、模块依赖、状态重置和执行随机性。

## 5. 候选算法轮廓

1. 将 Agent harness 表示为带类型和依赖关系的组件集合/图；
2. 对候选组件及组件对进行受控替换/消融，得到配对执行结果；
3. 估计组件主效应和交互效应，构造 linkage graph；
4. 将强正交互组件作为协同块继承；
5. 对强负交互或违反接口依赖的组合进行禁止、修复或重新生成；
6. 用统一任务集评价 offspring，比较 interaction-aware crossover 与普通 crossover。

## 6. 强基线

EvoMAS (Hu et al.)、EvoMAS (Wei et al.)、HFlow、AgentSquare、AgentBreeder、DarwinX、SERO、HiveMind、EvoCF、mutation-only、random module crossover、LLM-proposed crossover。

## 7. 必须通过的证伪实验

- H-G1：配对反事实估计的 ε_ij 能否预测组件组合后的表现？若预测不优于随机或简单相关性，停止。
- H-G2：interaction-aware crossover 是否提高有效 offspring 比例和任务成功率？若不优于随机模块交叉、LLM 交叉或 mutation-only，停止。
- H-G3：收益是否来自交互建模本身，而非额外执行次数、更多 repair 或更强模型？必须固定模型、任务、随机种子和评价次数。
- H-G4：交互图能否跨任务家族迁移？如果只能在单一任务上有效，不能宣称泛化。

## 8. 当前不确定性

- EvoMAS、HFlow、AgentSquare 的完整 crossover 细节尚未逐篇精读；
- DarwinX 的 recombination ablation 尚未完整复核；
- HiveMind 的 DAG-Shapley 可能为组件交互建模提供强对照；
- 经典 EC 中 linkage learning、GOMEA、LTGA、DSMGA-II 已有成熟机制，Agent 场景的新增价值必须清楚；
- 反事实组件替换可能导致不合法配置，需要设计类型约束与 repair。

**当前结论：G 仅为优先审查候选，不是已确认创新点或最终论文题目。**

## 9. 2–3 篇投稿论文的结构约束与新增威胁

用户明确要求硕士论文有 2–3 个创新点，并且每个创新点分别形成一篇小论文投稿。现将此要求设为硬约束。

新增直接工作：
- MESH-Harness：模块池、模块组合、full-covariance LinUCB、coordinate ascent、轨迹引导模块演化；
- ARTEMIS：Agent 组件自动发现、语义感知遗传算子、配置联合演化；
- EvoMAS：结构化 MAS 配置空间中的反馈引导 mutation/crossover；
- AgentEvo：多阶段 workflow evolution、subgraph graft、prompt fusion、Pareto cost-performance；
- Evo-Harness：经验上下文编译成可复用技能 harness。

这些工作使普通模块交叉、语义交叉、模块组合搜索、跨任务 harness 更新都不能直接作为创新。

三篇规划见 10_THESIS_INNOVATION_AND_PAPER_ROADMAP.md：
1. 任务条件化组件交互效应估计；
2. 交互感知演化重组算子；
3. 任务分布变化下交互结构迁移（条件性）。

候选 G 仍为 HOLD / PRIORITY FOR AUDIT。尤其要精读 ARTEMIS 和 MESH-Harness 的组件表示、交互建模、选择、交叉和消融。只有确认没有等价机制后，创新点一、二才能 GO。
