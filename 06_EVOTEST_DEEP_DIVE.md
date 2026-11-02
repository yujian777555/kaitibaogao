# 06 — EvoTest 深度审查：测试时演化学习

**论文：** He et al. (2026), *EvoTest: Evolutionary Test-Time Learning for Self-Improving Agentic Systems*, ICLR 2026  
**原文：** https://openreview.net/pdf?id=JFnnajbkvP  
**arXiv：** https://arxiv.org/abs/2510.13220  
**状态：** 已精读核心方法与局限性章节；附录和全部实验细节仍需继续核对。

## 1. 为什么它对本课题重要

EvoTest 是当前检索到的、与“演化计算直接优化 Agent 整体配置”高度相关的正式会议论文。它不是只优化 Prompt，而是把 Prompt、部署时记忆、超参数、工具使用逻辑都作为可调整的 Agent 配置。

论文作者在局限性中明确写出：
- 当前使用简单的 (1+m) evolutionary strategy 与 UCB 选择；
- 该启发式可能在复杂任务中陷入局部最优；
- 当前学习目标主要是同一任务的重复尝试，学到的策略容易针对具体任务过拟合；
- 作者建议后续探索更复杂的 population-based EA、quality-diversity 和 automated program synthesis。

这为本课题提供了来自正式论文的具体方法改进线索，但不等于创新性结论。还必须与 2025–2026 年其他种群演化、记忆演化、工作流演化和跨任务自进化方法比较。

## 2. 问题与基准

EvoTest 提出 Jericho Test-Time Learning（J-TTL）：
- 一个 Agent 在同一款文本冒险游戏中连续执行多个 episode；
- 每个 episode 后重置环境到相同初始状态；
- Agent 只能依赖本次 session 中积累的经验改善下一次表现；
- 六款游戏：Detective、Library、Zork1、Zork3、Balances、Temple；
- 每个 episode 通常最多 110 步，session 包含 50 个连续 episode。

Agent 既要最大化单次 episode 的回报，也要提升连续 episode 的学习曲线。论文用归一化 AUC 汇总 session 内的累计表现：

AUC = Σ_e R(e) / (K · R_max)

其中 K 为 episode 数，R(e) 为第 e 个 episode 的总回报，R_max 为单次 episode 的最大可能回报。

## 3. Agent 配置表示

论文将 Agent 配置定义为：

χ = (p, M, h, u)

- p：Policy Prompt，编码策略、启发式和行为约束；
- M：Deployment-time Memory，包含成功状态-动作记录和失败模式；
- h：Hyperparameters，例如 temperature、探索强度和停止条件；
- u：Tool-use routines，包括记忆交互逻辑和状态抽象逻辑；其中 state extractor 可以是可演化 Python 函数。

这是一个重要启发：Agent 个体不应被简化为一个 Prompt 字符串。其配置是多个相互依赖的结构化组件。

## 4. 演化循环

### 4.1 Actor 阶段
Actor 使用当前配置 χ(e) 与环境交互，产生轨迹 τ(e) 和回报 R(e)。

### 4.2 Evolver 阶段
Evolver 读取父配置和完整轨迹，生成子配置集合。论文包含：
- Prompt Mutation：根据成功和失败轨迹修改策略；
- Memory Update：提取有效状态-动作对和无效循环；
- Hyperparameter Tuning：修改探索强度、temperature 等；
- Tool-use Refinement：修改何时读取记忆、如何抽象状态等逻辑。

### 4.3 UCB 选择
下一轮候选池包含父配置和新子配置。论文用 UCB 评分：

UCB(χ) = μ_hat(χ) + β √(log N / (1+n(χ)))

其中 μ_hat 为候选配置的历史平均回报，n 为该配置被执行的次数，N 为总 episode 数，β 控制探索程度。

父配置始终留在候选池中，避免一次偶然高分的新配置永久替换成熟配置。

## 5. 已有贡献与不可重复之处

EvoTest 已经覆盖：
- 整个 Agent 配置而非单一 Prompt 的演化；
- Prompt、记忆、超参数和工具逻辑的联合更新；
- 执行轨迹作为自然语言反馈；
- 父代保留与 UCB 探索/开发；
- 同一任务连续 episode 的测试时学习。

不能把“全配置演化”“保留父代”“UCB”“执行反馈引导 Prompt 更新”当作独立创新。

## 6. 论文明确指出的局限

原文 Appendix A：
1. Frozen backbone：不更新模型权重，无法创造预训练模型不具备的低层能力。
2. Task-specific overfitting：策略和 verbal guardrails 针对当前游戏，可能无法迁移到轻微变化的环境。
3. Evolver dependency：演化效果与 Evolver LLM 的推理能力相关。
4. Search-space complexity：χ=(p,M,h,u) 是复杂组合搜索空间，当前 (1+m) + UCB 较简单，可能局部收敛。
5. Future directions：更复杂的 population-based EA、Quality-Diversity、automated program synthesis。

## 7. 与近年工作的关系

| 工作 | 主要对象 | 与 EvoTest 的区别 |
|---|---|---|
| EvoMAS (Hu et al., ICML 2026) | 多 Agent 配置和结构 | 配置空间搜索、轨迹反馈变异/交叉，不是同一 Agent 的在线 episode-to-episode TTL |
| EvoMAS (Wei et al., ICML 2026) | Agentic workflow | 多种演化策略和自适应选择，主要为工作流搜索 |
| HFlow (Findings ACL 2026) | Workflow、Prompt、模型骨干 | 人类偏好与三目标 Pareto 生存者选择，不是 EvoTest 的同任务连续测试时更新 |
| M* (NeurIPS 2026) | Agent memory harness | 将 memory 系统表示为可执行程序并按任务演化，不等于整套 Agent 的在线测试时演化 |
| MemEvolve (2025 preprint) | Agent 经验与记忆架构 | 重点为记忆架构元演化及跨任务/跨模型泛化 |
| E-SPL (ICML 2026 FoGen workshop) | System prompt + 模型权重 | Prompt 遗传演化与 RL 权重更新耦合 |
| INSPO (2025/2026 preprint) | Instruction + RL policy | 在 RLVR 循环中动态演化 instruction population |
| SkillRL (NeurIPS 2026) | SkillBank + policy | 技能库与 policy 的递归 RL 协同演化 |
| COvolve (GECCO 2026) | Policy population + environment population | 对抗式策略-环境协同演化和混合策略纳什均衡 |
| EvoTeam (2026 preprint) | Team organization、interaction、skills | 团队层协作演化，重点是异构任务下团队组织 |
| Evolving Agent Teams (2026 preprint) | Agent team roles/coordination | supervisor 诊断局部最优后重构团队，不是经典种群 EA |

## 8. 对本课题的初步启示

EvoTest 的局限与“演化计算方法改进”直接相关，但不能只把它替换成 NSGA-III 或 MAP-Elites。需要验证：
- 单任务反复试错，能否改造成跨任务序列的在线适应？
- 如何区分任务特定策略和可迁移策略？
- 是否需要行为描述符而非仅使用最终 episode 分数？
- 如何保持多种互补配置，同时避免把无效多样性当成搜索进步？
- 任务切换时，如何从历史配置档案中检索/重组父代？
- 如何证明收益来自演化机制，而不是 Evolver 模型更强或评价次数更多？

## 9. 下一轮需补充的原文核验

- 完整检查 EvoTest Appendix C–N 的实现、计算复杂度、多种子、基线和消融；
- 核对 EvoTest 对 Promptbreeder、EvoPrompt、TextGrad 等基线的适配方式；
- 精读 M*、MemEvolve、EvoMAS、HFlow、EvoTeam 的搜索空间、档案和跨任务实验；
- 检查是否有比 EvoTest 更新的测试时进化论文；
- 明确 J-TTL 是否适合作为复现基准，以及是否需要 AppWorld / ALFWorld / WebArena 等不同任务家族的外部验证。
