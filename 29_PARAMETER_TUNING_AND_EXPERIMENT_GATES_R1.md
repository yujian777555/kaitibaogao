# 三个 RSI 创新点的参数调节与实验 Gate R1

**日期：** 2026-11-03  
**项目：** yujian777555/kaitibaogao  
**适用报告：** 27_OPENING_REPORT_DRAFT_V0_3_RSI.md  
**状态：** EXPERIMENT_DESIGN_ONLY / NO EXECUTION

## 1. 参数调节总原则

1. 所有算法参数只在 train tasks / train task streams 上调节；validation 用于选择稳定配置；held-out test 不参与调参。
2. 首先离线调参，在线控制作为单独消融，不能一开始让多个参数同时在线变化。
3. 硬约束（接口、权限、调用依赖、状态不变量）不作为可被性能收益抵消的惩罚项；非法配置直接拒绝或 fail-closed。
4. 各基线使用相同模型版本、任务实例、初始种群和 rollout-equivalent budget；API token、tool calls、wall-clock 和 monetary cost 分别报告。
5. 不把一次任务 rollout 当作独立统计样本；按 task instance / task block / independent seed 分层分析。
6. 任何自动调参器都不能读取 held-out test 或 hidden task-family labels。

## 2. 创新点一：TCAIL 交互结构学习参数

| 参数 | 含义 | 候选范围/选择方式 | 主要影响 |
|---|---|---|---|
| (B_{probe}) | 主动交互探测预算（rollouts） | 以 pilot 估计总预算后，比较 5/10/20/40% 分配 | 交互识别精度与成本 |
| (m_{rep}) | 每个合法对比的重复任务块数 | 从 2 起，按区间宽度/停止规则增加 | 随机评价噪声 |
| (lambda_{sparse}) | 交互稀疏正则强度 | log-scale 网格 + irace | 假阳性边与漏检 |
| (lambda_{shrink}) | 跨任务/父代的层级收缩强度 | 0、弱、中、强；验证集选择 | 稀疏数据下的方差 |
| (	au_{edge}) | 输出边阈值/后验门限 | 在 train/validation 上校准覆盖率和 FDR | 图稀疏度 |
| (eta_{acq}) | 主动采样的探索权重 | 0（固定设计）到高探索 | 采样效率 |
| (K_{FOS}) | FOS builder 的结构约束 | Linkage Tree / bounded cluster / fixed singleton+pair | 结构复杂度 |

**建议调参顺序：**
1. 先固定 estimator，使用完整全因子或大预算参考设计获得可识别性上界；
2. 在合成真值上调整 (lambda_{sparse})、(lambda_{shrink})、(	au_{edge})，优先控制 null false-edge rate 和区间覆盖；
3. 固定统计模型，再比较主动采样 (eta_{acq}) 和预算 (B_{probe})；
4. 最后将相同 FOS builder 接入不同 linkage estimator，验证下游搜索收益，避免 FOS 差异混淆估计器效果。

**关键门禁：** 交互 AUPRC/F1 提升不够；必须证明 learned linkage 在同预算 GOM 搜索中改善结果。若 oracle linkage 本身无收益，停止当前 linkage 研究假设。

## 3. 创新点二：CI-GOM 参数

| 参数 | 含义 | 调节方式 |
|---|---|---|
| (mu) | population size | 小规模 8/16/32 起步；由 rollout budget 约束 |
| (G) | generations | 固定总预算下比较不同代数与每代 mixing 数 |
| (p_{donor}) | donor 候选策略 | random / best-compatible / posterior-ranked |
| (o_{FOS}) | FOS 遍历顺序 | random / small-to-large / large-to-small |
| (r_{mix}) | 每个个体每代 mixing 次数 | 由剩余 rollout budget 控制 |
| (r_{repair}) | 最大 repair 次数/范围 | 预注册小上限；超过即拒绝 |
| (delta_{accept}) | 最小实际改进幅度 | 在 validation task blocks 上定标 |
| (alpha_{seq}) | 序贯接受统计门限 | 固定 family-wise error 控制策略 |
| (B_{eval}) | 每个候选评价预算 | 所有基线统一 rollout-equivalent budget |

**建议调参顺序：**
1. 先用 oracle linkage 证明 GOM 对当前 Agent 搜索地形有用；
2. 固定 population 和总评价预算，调 FOS 遍历、donor 策略和 mixing 次数；
3. 加入硬约束和确定性 repair，单独统计 invalid offspring、repair rate 和 harmful recombination；
4. 最后调 (delta_{accept}) 和 (alpha_{seq})，比较误接受率与搜索速度；
5. 再用 irace/SMAC 对少数参数做联合调节，测试集完全冻结。

**必须分开的成本：** 如果某方法因为更多候选 rollout 或更多 repair 而获益，不能归因于 GOM 本身。所有基线必须按真实 Agent rollout 和 evaluator calls 进行公平预算匹配。

## 4. 创新点三：IMCE-RSI 参数

| 参数 | 含义 | 调节方式 |
|---|---|---|
| (K_{mem}) | 历史 linkage block 档案容量 | 8/16/32/64 及容量敏感性 |
| (lambda_z) | 可观察上下文键权重 | 在训练任务流中校准 |
| (lambda_G) | 交互签名兼容性权重 | 与 context-only / graph-only 对照 |
| (lambda_u) | 记忆不确定性惩罚 | 按验证集校准置信覆盖 |
| (	au_{drift}) | 交互结构漂移门限 | 用预先标注的离线 drift annotations 校准；线上不读取标签 |
| (	au_{collision}) | retrieval collision 门限 | 通过冲突工作流对照任务校准 |
| (B_{probe}^{mem}) | 记忆冲突时额外探测预算 | 设置硬上限，预算不足时 abstain |
| (epsilon_{retain}) | 历史能力允许退化容忍度 | 由业务/评测要求预注册，不能只为提升当前任务调高 |
| (alpha_{retain}) | 保留能力置信门限 | 以 validation replay blocks 校准 |
| (K_{archive}) | Pareto / QD archive 容量 | 固定容量与动态容量对照 |

**建议调参顺序：**
1. 比较 latest-only、whole-agent archive、context-only retrieval、interaction-only retrieval；
2. 再加入 dual-key retrieval，调整 (lambda_z,lambda_G,lambda_u)；
3. 单独测试 collision detector 和 active probe，报告 collision precision/recall、abstention 和 probe cost；
4. 加入 retention constraint，评估新任务提升与旧任务回归之间的 Pareto 前沿；
5. 最后才训练 transferability predictor；不允许先训练一个复杂模型，再把所有增益归因于演化机制。

## 5. A800 上训练什么

优先候选是轻量 **Linkage-Block Transferability Predictor**，不是基础 LLM 微调。

输入：
- 可观察任务上下文 embedding；
- 历史局部交互图/边后验；
- 候选 linkage block；
- 历史干预的收益、方差和负迁移证据。

输出：
- 目标任务中的预期迁移收益；
- 负迁移概率；
- 预测不确定性。

比较顺序：
1. nearest-neighbor retrieval；
2. logistic/linear regression；
3. GBDT；
4. 小型 MLP / GNN。

数据划分必须按 task stream / task source 隔离，避免同一仓库或同一任务模板泄漏到 train 和 held-out。只有小型神经模型在 held-out task families 上显著优于简单基线，才值得使用 A800 训练；否则保留统计模型。基础 LLM 权重保持冻结，DeepSeek-Flash API 作为统一执行模型。

## 6. 总体 Gate 与停止条件

| Gate | 通过条件 | 停止条件 |
|---|---|---|
| G1-A 合成交互 | 估计器在已知真值、null、噪声和类别约束下校准 | 假阳性边率或覆盖率不达标 |
| G1-B 下游价值 | learned linkage 同预算改善 GOM | 只改善统计指标、不改善搜索 |
| G2 oracle | oracle linkage 对标准 GOM 有可重复增益 | oracle 本身无增益 |
| G2 learned | learned linkage 接近 oracle 且优于强基线 | 不优于 FBL/cDLED/standard GOM |
| G3 dual-key memory | 比 ReasoningBank-style context retrieval 降低 collision 和负迁移 | 只与普通 embedding retrieval 持平 |
| G3 retention | 新任务适应提升且历史能力退化受控 | 仅降低遗忘但完全丧失适应，或反之 |
| G3 overall | 同预算优于 CPE/HarnessEvolve/DGM/EvolveNet/ReasoningBank/GEPA/Meta-Harness | 无独立增量收益，不独立成篇 |

**执行限制：** 本文只是参数和实验设计，不授权真实 API 调用、Phase 0、GPU 训练或代码实现。TCAIL V2.1 仍 REQUEST CHANGES；22 号接口提案待独立复审；CI-GOM 未实现；IMCE-RSI 无正式算法规格。
