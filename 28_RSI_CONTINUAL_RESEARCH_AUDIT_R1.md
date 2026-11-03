# 跨轮次 RSI 新近文献与第三创新点审计 R1

**日期：** 2026-11-03  
**项目：** yujian777555/kaitibaogao  
**对应开题稿：** 27_OPENING_REPORT_DRAFT_V0_3_RSI.md  
**状态：** THIRD_INNOVATION_HOLD / RSI_SCOPE_ACCEPTED

## 1. 本轮新增直接相关文献

### 1.1 CPE：能力保持已经不是空白

Yu et al., *Do Self-Evolving Agents Forget? Capability Degradation and Preservation in Lifelong LLM Agent Adaptation*, arXiv:2605.09315, 2026.

论文指出 self-evolving Agent 在 workflow、skill、model、memory 等演化通道中都可能发生 capability erosion，并提出 Capability-Preserving Evolution (CPE)。其实现分别针对 workflow anchor behavioral signatures、skill consolidation、模型参数的 EWC-style regularization 和 evidence-gated memory preservation。

**边界：** 不能把“加入历史任务回放”“对旧任务加一个惩罚项”或“能力保持门”作为第三创新点。必须研究 EC 特有的种群、局部 linkage、候选重组和跨轮次结构复用如何带来额外收益。

### 1.2 HarnessEvolve：性能门已经有直接先例

Jiang et al., *HarnessEvolve: Learning from Reference Trajectories for Reliable Agent Self-Evolution*, arXiv:2609.00829, 2026.

论文把执行、评价、优化和 gating 分离；通过 reference trajectory 对齐失败轨迹，聚类错误根因，质量门过滤数据泄漏与 prompt bloat；性能门要求候选在当前 batch 提升，同时不超过近期 batch 的回归容忍度，epoch-end 再从快照池中选择。

**边界：** 不能把“当前任务提升 + 最近任务不退化”作为第三创新点。必须比较长期 task-family retention、交互结构漂移和 linkage block 条件化迁移。

### 1.3 EvolveNet：分布式经验合并已经有直接先例

Nie et al., *EvolveNet: Collaborative Harness Evolution for Agent Self-Improvement*, arXiv:2608.04968, 2026.

多个 client 在本地 workload 上并行演化共同 harness，服务器根据证据和 scope 类型合并程序修改，并将更新后的 shared harness 重新分发。

**边界：** 不能把“不同任务的 Agent 经验汇总到一个共享系统”作为第三创新点。EvolveNet 必须作为强邻近基线。当前候选研究重点是单一 RSI 演化谱系中的 interaction-conditioned linkage memory 和 drift-aware block transfer，而不是多客户端程序聚合。

### 1.4 Can Coding Agents Sustain Continual Evolution without Forgetting?

Zhao et al., arXiv:2611.03219, 2026-11-02.

论文使用 SWE-bench Verified（代码修复）、SWT-Bench（测试生成）和 FeatureBench（功能实现）构造持续 harness 演化场景，评估 AHE 与 Meta-Harness。论文报告跨任务演化出现明显遗忘，并基于 520 余条轨迹将冲突归纳为 verification、workflow、budget strategy 三类；在 pass-to-fail 案例中，verification conflict 占 87.1%，workflow conflict 占 8.2%，budget conflict 占 0.6%。

**对本课题的作用：** 提供与用户关注的 SWE-bench Verified 直接相关的连续任务流设置和强对照。可将 SWE-bench Verified、SWT-Bench、FeatureBench 作为编码 Agent 主实验的三个候选任务家族。其结果不能直接当作本课题实验结果，样本规模应由本课题 pilot 决定。

### 1.5 Are Self-Evolving Agents Continual Learners?

Chen et al., arXiv:2610.25858, 2026-10-19.

论文在 BIRD、BFCL 和 ScienceWorld 上构造四类漂移流：topic drift、workflow drift、domain drift 和 compound drift；比较 ReasoningBank、GEPA 和 Meta-Harness。结果显示全局 Prompt/workspace 修改会引起跨任务干扰与知识覆盖；相似度记忆检索虽能局部化更新，但仍会向未见任务注入外来记忆，并在相似查询需要不同工作流时发生 retrieval collision。

**对本课题的作用：**
- 任务流必须允许 task-free 设置，算法不能直接读取 task-family 标签和 block 边界；
- 不可只按 query embedding 相似度检索历史经验；
- 可将“可观察任务上下文 + 局部交互签名 + 迁移证据”作为条件化检索的候选机制；
- 需要报告 pre-block interference、post-block forgetting 和 retrieval collision rate。

## 2. 第三个创新点重新收敛

原先宽泛的“跨轮次经验积累与自适应”过于容易与 DGM、CPE、HarnessEvolve、EvolveNet、ReasoningBank、GEPA、Meta-Harness 重合。

当前候选名称：

**面向跨轮次 RSI 的交互记忆与保留能力约束演化（Interaction-Memory-Aware Continual Evolution, IMCE-RSI）**

核心机制仅保留四个互相依赖的部分：

1. **交互记忆：** 保存的是经过验证的任务/父代条件化局部交互后验和 linkage block，而不只是完整 Agent 快照或自然语言经验。
2. **漂移检测：** 比较历史与当前可观察上下文下的交互后验，判断结构稳定、符号翻转、结构新增/消失或证据不足。
3. **条件化块迁移：** 只有当任务上下文和交互签名均兼容、历史转移证据可信时才复用 block；不能只靠 query embedding 相似度。
4. **保留能力约束下的种群选择：** 在新任务适应、历史任务保持和评价成本之间做受约束/多目标选择；对旧任务回归使用独立保护任务块。

### 2.1 任务标签泄漏风险

Chen et al. 的 task-free setting 不向算法提供 task-family 标签或 block 边界。我们也应采用：
- 任务家族标签仅用于离线数据划分、统计分析和结果报告；
- 在线算法只读取输入、工具 schema、可观察上下文和当前/历史轨迹特征；
- 不把 benchmark 名称、隐藏 task id、测试标签或事后失败原因直接输入迁移预测器；
- 若需要 task-aware oracle，单独报告为上界，不当作主算法。

### 2.2 训练模型是否加入

可以将 A800 用于训练轻量 transferability predictor，但不是默认必须项。输入为可观察任务描述、源局部交互签名、候选 linkage block 和历史干预证据；输出为预期迁移收益及负迁移风险。必须与 nearest-neighbor、统计回归、GBDT 比较。若预测器没有 held-out task family 上的独立收益，则删除神经模型，不能为使用 GPU 强行加入。

## 3. 三个创新点的独立边界

| 创新点 | 研究单位 | 主要输出 | 不可混淆的贡献 |
|---|---|---|---|
| I. RSI 轨迹驱动交互结构学习 | 单轮内的 parent × task context × module pair | 局部交互后验和 FOS 输入 | 估计交互，不负责产生最终 Agent |
| II. 交互感知约束 GOM | 单轮 Agent population | 新 Agent 候选及谱系 | 负责受约束重组和接受，不负责长期记忆迁移 |
| III. IMCE-RSI | 多轮 task stream | 交互记忆、漂移检测、条件化 block transfer 和 retention-aware archive | 负责跨轮次知识复用和长期稳定性 |

## 4. 第三创新点必须纳入的基线

- Latest-only sequential evolution；
- DGM whole-agent archive；
- CPE；
- HarnessEvolve；
- EvolveNet；
- ReasoningBank；
- GEPA；
- Meta-Harness；
- AHE / Meta-Harness 的连续任务流适配；
- no interaction memory；
- no drift detection；
- no interaction-conditioned retrieval；
- no retention constraint。

如无法官方复现，标记 PAPER-SETTING ADAPTATION，不得声称 official reproduction。

## 5. 建议的实验任务流

**主实验（编码 Agent）：**
- SWE-bench Verified：代码修复；
- SWT-Bench：测试生成；
- FeatureBench：功能实现。

这三个任务家族直接对应 2026-11-02 的持续 harness study。正式训练样本、validation 和 held-out test 数量需通过本课题 pilot 预注册，不能照搬对方 50/50/30 的资源受限抽样数字。

**可选 task-free drift 外部验证：**
- 参考 Are Self-Evolving Agents Continual Learners? 的 topic/workflow/domain/compound drift 设计；
- 若资源允许，在 BIRD/BFCL/ScienceWorld 上做外部验证；否则先把其作为方法学强基线，不扩大主实验范围。

## 6. 评价指标补充

- Plasticity：当前任务块学习能力；
- Stability：跨任务干扰与后续遗忘；
- Pre-block interference：新任务学习前对未见任务的影响；
- Post-block forgetting：完成任务块学习后到序列末端的能力下降；
- Retrieval collision：相似查询检索到冲突工作流记忆的比例；
- Forward transfer / backward retention；
- Interaction drift detection FPR/FNR；
- Linkage block transfer precision / negative transfer rate；
- Stream average advantage、terminal advantage、worst-family score；
- rollout/token/API cost 和独立随机种子间方差。

## 7. 决策

- RSI 作为毕业论文主线：接受。
- 三个创新点：均列为开题阶段的研究目标，但不预先宣称成立。
- 创新点三：继续 HOLD，不得只写“记忆库/性能门”；必须按本文件的 interaction-conditioned drift-aware block transfer 进行差异化审查。
- TCAIL V2.1：仍 REQUEST CHANGES / IMPLEMENTATION BLOCKED。
- 22 号 linkage/FOS 接口提案：仍待独立复审。
- CI-GOM：未实现、未实验。
- 本轮未启动 Phase 0、未调用 DeepSeek API、未训练模型。

