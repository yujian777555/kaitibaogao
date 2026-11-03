# TCAIL Linkage Interface 独立复审 R2

**日期：** 2026-11-03  
**审查对象：** 22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md，以及 17_TCAIL_FORMAL_SPECIFICATION_V2.md 与 20 号独立复审的接口一致性  
**审查性质：** 数学、统计、EC 接口和相关工作机制级复审；未运行代码或实验  
**结论：** B1_PARTIALLY_ACCEPTED / TCAIL_OVERALL_HOLD / IMPLEMENTATION_BLOCKED  
**唯一仓库：** yujian777555/kaitibaogao

## 1. 独立结论

22 号 proposal 的核心方向**概念上正确，但 B1 还不能正式关闭**。

正确的改动是将三个不同对象分开：
1. 条件 fitness interaction：`Δᵢⱼ(u,z)`；
2. 全局 task-conditioned interaction energy：`Sᵢⱼ(z)`；
3. 当前 parent/task 条件下的局部 linkage posterior：`qᵢⱼ(x,z)`。

这修正了“平均有符号交互等于通用 linkage”的错误推断，也避免把 VIG 直接称为 GOMEA FOS。

但 22 号仍没有完全定义：
- 局部 edge evidence 如何转成 FOS 聚类所需的连续权重；
- 具体使用哪一种确定性 FOS builder；
- parent × task × generation 下的 BFDR 检验族；
- 当前局部图的主动采样风险如何与最终 BFDR 选择一致；
- M2/M3 不一致时如何形成最终 posterior 和 abstention；
- 局部四格配对评价的 task-block 统计模型。

所以 22 号可作为 B1 的修订基础，但仍是 proposal，不是可实现规格。TCAIL 整体继续 HOLD。

## 2. 相关工作事实与新颖性边界

本轮对关键先行工作进行了外部核验：

| 工作 | 已覆盖机制 | 对本课题的直接约束 |
|---|---|---|
| Olieman, Bouter & Bosman, 2021, *Fitness-based Linkage Learning in the Real-Valued Gene-pool Optimal Mixing Evolutionary Algorithm* | 通过 fitness perturbation / differential-grouping 思路学习 RV-GOMEA linkage | 不能宣称首次由 fitness difference 学习 linkage |
| Dushatskiy et al., 2024, *Parameterless Gene-Pool Optimal Mixing Evolutionary Algorithms* | GOMEA 与 CGOMEA；通过 conditional dependencies 过滤 solution mating | conditional linkage/mating 已有强先例 |
| Przewozniczek et al., 2025, *Conditional Direct Empirical Linkage Discovery for Solving Multi-Structured Problems* | 对当前个体发现条件化局部依赖，并用于多结构问题的 mating restriction | 不能仅把全局图改为 parent-specific 图就宣称新颖 |
| Tinós et al., 2026, *Learning Variable Importance and Interaction in Genetic Algorithms for Pseudo-Boolean Optimization* | 从 GA 搜索过程副产物提取变量重要性和交互，无需额外 fitness evaluations，并用于 reproduction operators | 必须加入 zero-extra-evaluation / side-effect interaction learning 强基线 |

文献元数据与摘要核验：
- Olieman et al.：IEEE Transactions on Evolutionary Computation, 2021, 25(2): 358–370. DOI: 10.1109/TEVC.2020.3039698.
- Dushatskiy et al.：Evolutionary Computation, 2024, 32(4): 371–397. DOI: 10.1162/evco_a_00338.
- Przewozniczek et al.：FOGA 2025, pp. 238–249. DOI: 10.1145/3729878.3746624.
- Tinós et al.：Evolutionary Computation, online 2026-09-15, pp. 1–36. DOI: 10.1162/EVCO.a.406.

**新颖性判断：** fitness-based linkage、conditional/local linkage、noise-aware decomposition、从 GA 轨迹副产物学习交互都已有直接先例。TCAIL 只能争取以下组合场景中的可证伪增量：任务上下文 + 当前 parent 双条件化、随机 task-block 配对数据、合法配置共同支持、后验不确定性/abstention、主动评价预算，以及这些输出对最终 GOM 搜索的增益。当前尚不能宣称该组合已经构成独立创新。

## 3. 对 22 号 proposal 的数学审查

### 3.1 通过的部分

条件有限差分：

[
Delta_{ij}(u,z)=J(++u,z)-J(+-u,z)-J(-+u,z)+J(--u,z)
]

在四格具有共同合法支持、目标效用 J 已冻结时，定义清楚。

全局 RMS：

[
S_{ij}(z)=sqrt{mathbb E_{usimpi_{ref}}[Delta_{ij}(u,z)^2]}
]

能够避免不同背景的正负 interaction 在平均有符号差分中抵消。对完整、均匀、独立的二元背景，Walsh 展开平方和恒等式成立；对受约束或非均匀参考分布，只能保留 RMS 的定义，不能继续使用完整正交空间的平方和解释。

局部 posterior：

[
q_{ij}(x,z)=P(|Delta_{ij}(x_{-ij},z)|>delta_{local}mid D)
]

是一个合理的 parent/task 条件化证据量。用它决定当前 parent 的局部 edge 是否有足够证据，比把全局 RMS 图直接应用于所有个体更合理。

### 3.2 B1 仍未闭合：证据概率不是聚类权重

`qᵢⱼ(x,z)` 是“局部交互超过最小实际意义阈值的后验概率”，主要表达证据强弱；它不是连续 interaction magnitude。若只把 q 直接作为 Linkage Tree 相似度，所有高置信边会趋于相似，无法表达边之间的实际依赖强度差异。

V2.2 必须把以下三个量分开：

- **实际意义阈值：** `δ_local`，在 objective utility J 的尺度上定义；
- **edge confidence threshold：** `τ_edge`，控制后验概率门限；
- **FOS similarity weight：** 供聚类使用的连续强度。

建议的待验证定义：

[
q_{ij}(x,z)=P(|Delta_{ij}(x_{-ij},z)|>delta_{local}mid D)
]

[
w_{ij}(x,z)=
mathbb E[(|Delta_{ij}(x_{-ij},z)|-delta_{local})_+mid D]
]

其中 q 用于 edge inclusion / abstention，w 用于 FOS builder 的加权相似度；正向与负向概率另行报告。该权重不是已证明最优的选择，必须与 posterior mean absolute contrast、posterior lower bound 等替代权重进行合成真值和下游搜索比较。

建议 edge 进入 local VIG 的条件为：
1. 四格共同合法支持门通过；
2. model-basis × anchor 可识别性和 practical-information 门通过；
3. M2/M3 model-order gate 不触发 abstention；
4. `qᵢⱼ ≥ τ_edge`；
5. 不确定状态不能静默当作无边。

### 3.3 FOS builder 还不够具体

22 号 proposal 说使用固定 LT / conditional FOS，但仍未给出唯一、可复现的主 builder。

V2.2 必须明确：
- 主分析使用哪种 builder；
- 输入权重究竟是 q 还是 w；
- 使用何种 linkage 更新规则（例如预注册的 average-linkage/UPGMA）；
- tie-breaking 规则；
- singleton、unsupported pair、disconnected components 如何处理；
- 每个 parent 的 local VIG 如何映射到实际 mixing subsets；
- 高阶/重叠依赖由 LT 还是 conditional/clique FOS 处理。

建议将“固定 weighted Linkage Tree builder”作为主实现候选，采用 w 作为相似度、固定 average-linkage 更新和确定性 tie-break；标准 MI-LT、fitness-based LT、CGOMEA/conditional-clique FOS 作为强对照。若 builder 尚未冻结，TCAIL 输出只能叫 local VIG，不能写成已得到 FOS。

## 4. B2–B8 的具体闭合要求

### B2 — M2/M3 与高阶敏感性

1. M2：主效应 + pairwise。
2. M3：M2 + sparse three-way diagnostics。
3. 所有低阶项保留在模型中，但不得强制低阶系数非零；否则 pure three-way-only 真值无法表示。应明确这是“低阶项保留”而非 strong heredity 的非零系数约束。
4. 对同一 objective-scale estimand，在 M2/M3 下分别计算 q、w、方向概率和 posterior null probability。
5. 若 edge inclusion、方向或实际权重差异超过预注册敏感性阈值，状态为 MODEL_ORDER_SENSITIVE，并 abstain，不进入 FOS。
6. 对四阶及更高阶 misspecification 进行压力测试；本课题若不建模四阶以上项，必须把适用范围和失败边界写清楚。
7. 建议最终 BFDR 使用保守的模型间 null probability 上界作为候选规则；该规则仍需在合成校准实验中比较，不能直接宣布正确。

### B3 — acquisition 与最终 BFDR 对齐

最终边选择是带 BFDR 约束的集合决策，不能继续把独立逐边 Bayes risk 直接称为最终决策风险。

建议先定义：

[
S^*(D)=argmin_{S:operatorname{BFDR}(Smid D)le q}
left[
C_{FP}sum_{ein S}p_{0,e}
+
C_{FN}sum_{e
otin S}p_{1,e}
ight]
]

[
R(D)=min_{S:operatorname{BFDR}(Smid D)le q}L(S,D)
]

候选设计 d 的 acquisition：

[
A(d)=R(D)-
mathbb E_{Y_{new}mid D,d}[R(Dcup{(d,Y_{new})})]
-lambda C(d)
]

如果精确计算成本过高，可以保留 per-edge risk 作为 surrogate，但必须与 BFDR-constrained risk 比较，并明确标注 surrogate，不能称为最终边决策风险。

### B4 — task-block 配对与相关性

建议将 task-block 定义为 task instance × 固定执行协议 × run seed。每个候选 pair 的四格配置尽可能在同一 task instance / 同一 run block 上配对执行，并随机化四格执行顺序。

- 若模型/环境 seed 可控，使用 matched seed；
- 若 API 采样无法严格控制，仍按 task instance 配对，并在统计模型中纳入 task-level random intercept / cluster structure；
- 重复 rollout 不得视为独立 task sample；
- posterior、bootstrap 和 acquisition 必须使用同一 block 抽样单位；
- 未来 task-block 的抽样分布必须来自 train/validation，而非 held-out test。

### B5 — nuisance parameter

主 estimand 建议固定为程序化任务成功概率，采用 Bernoulli likelihood，避免将未知 Beta concentration `κ` 引入主 edge decision。若要用连续 bounded reward 作为主目标，则必须对 `κ` 设先验并联合估计/积分；Gaussian 的 `σ²` 也要明确冻结或联合估计。不能在文中声明 nuisance uncertainty 被纳入，却在 acquisition 中只代入点估计。

### B6 — structural 与 practical identifiability

对每个 model basis × context anchor 分别构造：
- `X_legal(M,a)`：该 basis 和 anchor 下完整合法配置设计矩阵；
- `X_obs(M,a)`：当前已观测配置矩阵。

分别执行 row-space contrast test。GLM 还需增加 Fisher-weighted information / conditioning 门，避免出现代数可估计但实际信息接近零的假象。共同支持质量低于预注册阈值时 abstain 或将 estimand 限定到支持子域。

### B7 — BFDR 检验族

建议将一个 local graph 的索引明确为：

[
g=(r, parent_id, context_anchor)
]

每个 graph 的 edge family 为该 parent/anchor 下所有槽位 pair。每张图单独报告 graph-level BFDR；跨 parent、跨 generation 的全局 FDR 不得从 per-graph BFDR 自动推断。若论文要宣称全局控制，必须另加预注册的 cumulative/online error-budget 规则。MODEL_ORDER_SENSITIVE、PENDING_SUPPORT 和结构未认证状态必须作为 unresolved/abstain 单独报告，不能伪装成 negative edge。

### B8 — rollout-equivalent budget

建议把一个完整 task-block evaluation 定义为一个 episode-equivalent，固定最大 step/tool-call/token cap；超限按预注册失败规则计入。每种算法在相同 task-block 数和 cap 下比较。实际 token、tool calls、wall-clock 和货币成本仍须分别报告。只有当每个配置/anchor 的重复次数和执行协议一致时，`B_full` 的简单计数公式才成立；否则必须给出加权预算口径。

## 5. 新颖性与 EC 贡献的独立判断

当前可保留的候选方法表述：

> 面向随机、昂贵、任务异质且存在合法配置约束的 Agent 模块优化，研究一种 task-context 与 current-parent 双条件化的概率化 fitness-linkage 学习方法；通过 task-block 配对执行、模型阶数敏感性、后验不确定性和可证伪的主动预算分配，产生当前个体适用的局部依赖证据，并验证这些证据是否在同等 rollout budget 下提高 GOM 的 FOS 质量和 Agent 搜索表现。

这只是候选贡献，不是新颖性批准。必须至少比较：
- SLL-MI / standard LT-GOMEA；
- FBL / fitness-based LT；
- DLED / cDLED；
- CGOMEA / conditional-clique FOS；
- LMM、ALI/AIM；
- Tinós et al. 2026 GA-side-effect interaction learning；
- random linkage、oracle local linkage。

所有 estimator 使用同一 FOS builder，另做 builder 消融。最终指标必须从“统计图恢复”延伸到“FOS 质量、有效 mixing 和同预算搜索收益”。

## 6. 审查状态

| 项目 | R2 结论 |
|---|---|
| 22 号 B1 概念拆分 | PARTIAL PASS |
| global RMS 与 local q 分离 | PASS（定义层面） |
| q 到 FOS 权重 | NOT CLOSED |
| FOS builder | NOT CLOSED |
| M2/M3 / 高阶 / heredity | NOT CLOSED |
| acquisition–BFDR 一致性 | NOT CLOSED |
| task-block 配对统计 | NOT CLOSED |
| nuisance uncertainty | NOT CLOSED |
| model-basis × anchor practical identifiability | NOT CLOSED |
| parent/anchor/generation BFDR family | NOT CLOSED |
| rollout-equivalent budget | NOT CLOSED |
| TCAIL 新颖性 | NOT ESTABLISHED |
| EC 下游搜索贡献 | NOT ESTABLISHED |

**最终状态：B1_PARTIALLY_ACCEPTED；TCAIL = HOLD / IMPLEMENTATION BLOCKED。**

本轮未修改 17 号权威规格，未实现代码，未启动 Phase 0，未调用 DeepSeek API，未训练模型。下一步应形成独立的 V2.2 规格草稿，再交给不同会话/审查者复审。

## 7. 核验来源

- Olieman et al., 2021: https://doi.org/10.1109/TEVC.2020.3039698
- Dushatskiy et al., 2024: https://doi.org/10.1162/evco_a_00338
- Przewozniczek et al., 2025: https://doi.org/10.1145/3729878.3746624
- Tinós et al., 2026: https://doi.org/10.1162/EVCO.a.406
