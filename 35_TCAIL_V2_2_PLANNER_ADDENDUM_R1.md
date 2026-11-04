# 35 — TCAIL V2.2 Planner Addendum R1：先行机制精读与新增数学闭合项

**日期：** 2026-11-04  
**状态：** PLANNER RESEARCH ADDENDUM / SPECIFICATION REVISION ONLY  
**唯一仓库：** `yujian777555/kaitibaogao`  
**依据：** 31_TCAIL_LINKAGE_INTERFACE_INDEPENDENT_REVIEW_R2.md、32_TCAIL_V2_2_SPEC_REVISION_TASK_R1.md，以及本轮对 FBL、cDLED、CGOMEA、GA-side-effect interaction learning 原文/正式出版信息的核验。

> 本文件补充 32 号任务，不替代 32 号任务，不是 V2.2 规格，不是独立复审通过，也不授权实现或实验。TCAIL 仍为 HOLD / IMPLEMENTATION BLOCKED。

## 1. 本轮原文精读带来的重要修正

### 1.1 FBL 已覆盖的不只是“四点评价”，还包括相对强度与增量预算

Olieman、Bouter 与 Bosman 的 FBL 工作在 RV-GOMEA 中使用 fitness perturbation / differential-grouping 思路估计变量依赖，并把依赖强度转为可比较的 pairwise linkage measure，再构造 Linkage Tree 或 marginal-product FOS。原文明确指出：

- 其依赖判断比较对变量 (i) 的相同扰动在变量 (j) 不同取值下造成的 fitness change；
- 依赖强度被缩放到可用于比较不同变量对的相对尺度，而不是只输出“是否有边”；
- 每轮可只抽取部分变量对进行检测，维护增量 dependency matrix；检测周期会随已发现依赖数调整，并在后续周期重新探测以适应结构变化；
- 论文讨论了部分评价、共享基准点与增量检测带来的评价成本降低。

因此，以下均不能作为 TCAIL 的新贡献：fitness-based linkage、四点有限差分、连续 pairwise dependency weight、Linkage Tree 构造、增量抽取部分变量对、随发现依赖数调整探测周期。V2.2 必须将 FBL 的 scaled dependency measure 和 incremental dependency updating 纳入强基线，而不只是把 FBL 写成一个二元阈值基线。

原文：Olieman, C., Bouter, A., & Bosman, P. A. N. (2021). Fitness-based Linkage Learning in the Real-Valued Gene-pool Optimal Mixing Evolutionary Algorithm. *IEEE Transactions on Evolutionary Computation*, 25(2), 358–370. DOI: https://doi.org/10.1109/TEVC.2020.3039698

### 1.2 cDLED 已覆盖 individual-local linkage、conditional eVIG 和 donor filtering

Przewozniczek 等人的 cDLED 不是单纯全局 linkage 方法。原文明确说明：

1. DLED 在给定当前个体附近，通过翻转两个基因及其组合，比较四个 fitness 值，识别该个体处的直接依赖；
2. cDLED 进一步处理 multi-structured problem，先用 probe link 判断当前个体所对应的子结构；
3. 对被选中的个体执行更完整的 DLED 分解，构造 conditional eVIG；
4. 将 conditional eVIG 与 SLL-DSM 结合构造 mixing clusters；
5. 根据当前个体的条件依赖过滤 donor，只允许依赖结构兼容的个体参与 mixing。

这意味着“当前 parent 一张局部图”“局部四点反事实”“用局部图过滤 donor”均已有直接先例。TCAIL 不能把 parent-conditioned posterior 或 local VIG 本身宣称为首次提出。

cDLED 原文还报告 DLED 分解成本在不同问题上约占运行时间的 5%–78%，并明确把降低 ELL 成本列为未来工作。这为 TCAIL 的预算问题提供了真实动机，但也意味着必须公平比较其局部探测成本，而不是仅比较边识别准确率。

原文：Przewozniczek, M. W., Bosman, P. A. N., Bouter, A., Guijt, A., Komarnicki, M. M., & Thierens, D. (2025). Conditional Direct Empirical Linkage Discovery for Solving Multi-Structured Problems. *FOGA 2025*, 238–249. DOI: https://doi.org/10.1145/3729878.3746624

### 1.3 CGOMEA 已覆盖 conditional linkage 与 solution mating filter

Dushatskiy 等人的 CGOMEA 通过 conditional dependencies 改进 linkage-based variation，并按条件依赖过滤 solution mating。它必须作为直接算法基线，而不能只比较标准 LT-GOMEA 或普通随机交叉。

原文：Dushatskiy, A., Virgolin, M., Bouter, A., Thierens, D., & Bosman, P. A. N. (2024). Parameterless Gene-Pool Optimal Mixing Evolutionary Algorithms. *Evolutionary Computation*, 32(4), 371–397. DOI: https://doi.org/10.1162/evco_a_00338

### 1.4 Tinós et al. 2026 已覆盖零额外 fitness evaluation 的交互学习

Tinós 等人 2026 年 9 月 15 日 online-ahead-of-print 的论文，从 GA 搜索过程副产物估计 variable importance 和 interaction，不要求额外 fitness evaluations，并将信息用于 mutation/recombination operator；实验包括 NK landscapes 和 feature-selection pseudo-Boolean tasks。

这构成 TCAIL 的关键成本基线：如果 TCAIL 需要额外 Agent rollout，必须证明主动确认交互的收益足以抵消额外调用成本；不能只证明其交互图更准确。

原文：Tinós, R., Chicano, F., Przewozniczek, M. W., & Whitley, D. (2026). Learning Variable Importance and Interaction in Genetic Algorithms for Pseudo-Boolean Optimization. *Evolutionary Computation*, online ahead of print, 2026-09-15. DOI: https://doi.org/10.1162/EVCO.a.406

## 2. 新增规格阻塞：B9–B12

以下项目在 31 号复审的 B1–B8 基础上新增。Executor 必须在 33 号草稿和 34 号矩阵中逐项处理；不能因 32 号未列出而忽略。

### B9 — objective-scale 非线性 estimand 的可识别性

当前目标交互定义在实际成功概率/效用尺度上。若主 likelihood 是 Bernoulli-logistic，则对配置 (c)：

[
p(c;eta)=operatorname{logit}^{-1}(g_c^	opeta)
]

目标四格交互为：

[
Delta^p_{ij}(u,z;eta)
=p(++u,z;eta)-p(+-u,z;eta)
-p(-+u,z;eta)+p(--u,z;eta)
]

需要注意：线性 predictor 上的 contrast (l^	opeta) 满足 (linoperatorname{Row}(X_{obs}))，并不自动证明上述 probability-scale 非线性函数 (Delta^p) 可识别。31 号报告中提到的 row-space contrast 检验必须明确其适用对象，不能直接从线性 contrast 推广到 inverse-link 后的非线性 estimand。

V2.2 必须选择并明确以下一种检验路径：

- **保守充分条件：** 对四个目标配置分别检查其设计行向量 (g_{++},g_{+-},g_{-+},g_{--}) 是否处于 (operatorname{Row}(X_{obs}))。四个线性 predictor 均可识别，才能推出四个概率及其差分可识别。
- **直接 estimand-invariance 条件：** 对所有满足 (X_{obs}v=0) 的不可识别方向 (v)，检查目标函数是否满足 (Delta^p(eta+v)=Delta^p(eta))。若不满足，则该 estimand 在当前观测设计下不可识别。

结构可识别性使用 (X_{legal})；当前数据可识别性使用 (X_{obs})。GLM practical information 另用 Fisher-weighted information 和 posterior interval width 检查。阈值须在 synthetic training landscapes 上预校准，不得根据 held-out 结果调节。

### B10 — acquisition 的设计单位必须是四格 task-block 向量，而非抽象单次 observation

对 pair (e=(i,j))、parent (x)、context anchor (a)，一个可执行探测设计应至少明确：

[
d=(r, parent_id, a, e, u=x_{-ij}, task_block, n_{rep})
]

其新观测一般是四格结果向量：

[
Y_d=(Y_{++},Y_{+-},Y_{-+},Y_{--})
]

而不是不加区分的单个标量 (Y_{new})。若每格重复 (n_{rep}) 次，也必须明确重复的层级和统计单位。

- task-block 至少包含 task instance、固定执行协议版本和 evaluation replicate/run seed；
- 四格执行顺序随机化；
- 只有在环境随机数可控且不同配置确实共享同一外生随机源时，才称为 common random numbers；LLM API 的采样 seed 不可控或不同轨迹消耗随机流不同，不能假称严格 CRN；
- 无法严格 CRN 时，仍按 task instance 分块，并在层级模型中处理任务难度和 block 相关；
- 重复 rollout 嵌套于 task instance，不得伪装成独立任务样本；
- acquisition 的 future-block distribution 只能由训练/验证数据确定，不能使用 held-out test；
- 如果一个已评估配置会被多个 pair/anchor 复用，预算应按**新增的唯一 episode-equivalent**计数，不能每个 pair 都把缓存结果重复计费，也不能把缓存命中说成新 rollout。

### B11 — FOS builder 必须区分“无边”与“无证据”

weighted average-linkage 可以作为候选主 builder，但必须处理缺失/不支持的 pair。若把 PENDING_SUPPORT、STRUCTURALLY_NOT_IDENTIFIABLE 或 MODEL_ORDER_SENSITIVE 直接填成权重 0，就会把“没有证据”错误解释为“已确认独立”。

V2.2 必须冻结：
1. 支持状态和真实零边的不同编码；
2. average-linkage 的 cluster-to-cluster 更新公式；
3. tie-breaking 的稳定顺序；
4. singleton、unsupported edge、disconnected component 的处理；
5. 若两簇之间没有任何可用支持边，是保留 forest/partial FOS，还是进入明确的 safe fallback；
6. safe fallback 是否仅使用 singleton，而不能偷偷把 unsupported edge 当作 SLL/MI 正常边；
7. 所有 estimator 对比时使用相同 builder，另做 builder sensitivity。

FBL 论文已经研究 partial linkage tree 与 marginal-product FOS；cDLED 也将 conditional eVIG 与 SLL-DSM 组合构造 LT clusters。因此不能把“使用 weighted LT”本身列为创新。

### B12 — posterior edge probability 的先验敏感性与校准

[
q_e=P(|Delta_e|>delta_{local}mid D)
]

是 posterior probability，不是数据量本身。低样本或先验过宽时，(q_e) 可能受 prior mass、模型阶数和随机效应先验显著影响。V2.2 必须：

- 明确 effect prior、shrinkage prior、task random-effect prior 及超参数的来源；
- 对 null/additive landscapes 做 prior-predictive 与 posterior calibration；
- 进行 prior-scale sensitivity，报告 (q_e)、(w_e)、BFDR 和 abstention 随先验变化的结果；
- 说明小样本时为何不会把“宽 posterior”误判为高置信交互；
- 如采用 spike-and-slab、practical-null interval 或其他保守机制，写清其 estimand 和 posterior null probability 定义；
- 不能仅以一个 prior 设定下 (q_e) 超过阈值就认定 edge 已确认。

## 3. V2.2 必须新增的直接强基线矩阵

| 基线 | 必须复现/适配的机制 | 对照目的 |
|---|---|---|
| FBL / scaled FBLT | fitness-based contrast、相对依赖强度、LT/MP FOS | 排除普通 fitness-based linkage 的包装 |
| FBL incremental update | 每轮部分 pair probing、增量 DSM、依赖周期更新 | 检验主动采样是否真的优于简单增量预算 |
| DLED | 当前 parent 四点局部依赖检测 | 排除局部四点反事实本身的新颖性 |
| cDLED-P3M | conditional eVIG、局部结构识别、donor mating restriction | 排除 parent-specific graph + donor filter 的重复 |
| CGOMEA | conditional dependencies 与 solution mating filter | 对照 conditional linkage/GOM |
| Tinós et al. 2026 / GAwLL2 | 从 GA 搜索副产物提取交互，不增加 fitness evaluations | 检验额外 Agent rollout 是否值得 |
| LMM、ALI/AIM | noisy linkage/decomposition | 排除噪声下 linkage 的一般性新颖性 |
| SLL-MI / LT-GOMEA | 标准统计 linkage | 基础基线 |
| Random linkage / Oracle local linkage | 随机下界和已知真值上界 | 验证 estimator 与下游 FOS 的实际价值 |

必须区分原论文方法与 paper-setting adaptation。对每个基线报告适配了哪些接口、哪些假设不成立、额外引入了哪些参数；不能将改造版本冒充原论文原始算法。

## 4. TCAIL 当前真正可能成立的窄贡献

在上述先行工作之后，TCAIL 不能再声称提出了 fitness linkage、individual-local linkage、四格差分、conditional donor filtering、weighted LT 或 incremental pair probing。

唯一暂时保留的候选问题是：

> 在 LLM Agent 评价具有随机性、任务实例异质性、合法配置共同支持限制且单次 rollout 成本较高时，能否构造一个经过任务块校准的概率化局部 fitness-linkage 估计与决策机制，在同等 episode-equivalent 预算下，比 FBL incremental、DLED/cDLED、LMM/ALI 和 GA-side-effect learning 更可靠地输出当前 parent/context 可用的 linkage，并进一步提高下游 GOM 的 FOS 质量与搜索表现？

这只是可证伪候选。若最终实现只是“给 cDLED/FBL 加一个 Bayesian posterior，再套一般 Bayesian OED”，而没有独立的统计校准、预算决策和下游搜索增益，应判为 NO-GO 或继续收窄，不得因为组合了多个成熟模块就宣称创新。

## 5. 给 Executor 的具体追加要求

在执行 32 号任务时，额外读取本文件，并完成：

1. 在 33 号规格中新增 B9–B12 独立章节；在 34 号矩阵中逐项登记。
2. 明确 objective-scale nonlinear (Delta^p) 的 structural/practical identifiability。
3. 将 acquisition design 写成四格 task-block vector，并明确 CRN 何时成立。
4. 定义缓存复用后的 incremental episode-equivalent cost。
5. 冻结 unsupported edge 的 missingness-aware FOS 处理；不得将缺失边填零。
6. 进行 posterior prior sensitivity 与 null calibration 规格。
7. 扩充 FBL incremental、DLED/cDLED-P3M、CGOMEA、Tinós/GAwLL2 强基线。
8. 保持 TCAIL HOLD；未闭合项标记 OPEN，不得编码或启动实验。

## 6. 本轮状态

- 公开原文核验：FBL、cDLED、CGOMEA、Tinós et al. 2026；
- 规格新增阻塞：B9–B12；
- TCAIL：HOLD / IMPLEMENTATION BLOCKED；
- CI-GOM：冻结；
- IMCE-RSI：冻结；
- 真实 LLM API：未调用；
- Phase 0：未启动；
- A800 训练：未启动；
- 本轮未进行代码实现或性能实验。

