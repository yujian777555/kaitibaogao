# 36 — TCAIL V2.2 独立规格复审 R1

**日期：** 2026-11-04  
**审查对象：** 33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md、34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md  
**基线提交：** 11cccf45c7533782f2673612b4bd52930541c9bc  
**审查性质：** 独立数学、统计决策、预算账本、FOS/EC 接口与伪代码审查；未运行实现或性能实验  
**结论：** **REQUEST CHANGES / TCAIL HOLD / IMPLEMENTATION BLOCKED**

> 本报告只审查规格。发现规格缺陷不等于算法已被实验否证；规格修订也不等于创新成立。本文不授权代码实现、Phase 0、真实 LLM API、模型训练、CI-GOM 或 IMCE-RSI。

## 1. 远端核验与审查范围

审查前核验：
- 远端分支：main
- 远端 HEAD：11cccf45c7533782f2673612b4bd52930541c9bc
- 提交标题：Add TCAIL V2.2 specification draft
- 33 号规格：2,062 行；34 号矩阵：213 行
- 31、32、35 号历史复审/任务/补充文件均作为约束依据读取
- STATUS.md 不存在；本轮按仓库维护策略更新 README、Decision Log 和 Handoff

审查覆盖了统一 estimand、task-block GLMM、非线性可识别性、Fisher practical-information、M2/M3 与高阶门禁、BFDR 与 constrained-risk acquisition、missingness-aware FOS、缓存/attempt/retry 成本、完整伪代码、校准和强基线矩阵。

## 2. 独立结论摘要

33/34 号比 V2.1 有实质进步：许多此前没有定义的状态、统计单位和控制流已经写入。但“规格条款存在”仍不等于“条款正确”。本轮发现以下必须修订的问题：

| ID | 严重性 | 对应议题 | 独立结论 |
|---|---|---|---|
| R1 | BLOCKER | B2/B3：M2/M3 保守合并与决策风险 | max local-null 与其补概率不能同时被称为真实 posterior expected loss；需要重定义 |
| R2 | BLOCKER | B3：Acquisition MC 停止 | 以 A_hat <= 0 直接停止，没有考虑 MCSE_A，可能因 MC 噪声过早终止 |
| R3 | BLOCKER | B8/B10：retry 账本 | 同一 base key 跨轮次可重置 retry 计数；C0/Ccap 未扣除历史 attempt |
| R4 | MAJOR | B6/B9：practical information | lambda_min+ 忽略 target-space 零特征值；Fisher 定义与 GLMM 边际 likelihood 的关系未充分冻结 |
| R5 | MAJOR | B11：missingness-aware FOS | rho_AB 实际是 selected-positive-edge density，不是支持覆盖率；known-zero 与 unknown 在该门槛中无法区分 |
| R6 | MAJOR | B3/B10：双模型 fantasy 风险包络 | E[max(R2,R3)] 是独立 fantasy 的乘积分布风险，不等于 max(E[R2],E[R3])；需明确决策含义并比较 |
| R7 | MINOR/OPEN | B7/B3：活动图风险权重 | 活动图集合/权重只要求“采样前冻结”，但新 parent/generation 图进入风险集合的更新协议未明确 |

因此，B1–B12 仍不能整体验收。建议维持：**B1、B4、B5、B7、B9、B12 为 PARTIAL；B2、B3、B6、B8、B10、B11 为 REQUEST CHANGES / PARTIAL，待修订复审。** 这里的 PARTIAL 不是数学 PASS。

## 3. 已通过的定义层面检查

### 3.1 三层 estimand 拆分基本正确

33 号 §2.1–2.3 将：
- 当前 parent/background/anchor 的 objective-scale 条件四格差分 Delta_g,e；
- 全局 RMS 摘要 S_ij(a)；
- 局部后验证据 q 与连续权重候选 w

分开定义。这避免了把全局有符号均值直接当作每个 parent 的 linkage，也避免将 q 直接作为连续聚类相似度。

完整均匀独立二元背景下的 Walsh 恒等式
\[
S_{ij}^2=16\sum_{S\supseteq\{i,j\}}\beta_S^2
\]
在文中限定的条件下成立；文中也正确禁止将该恒等式直接推广到受约束/非均匀背景。

### 3.2 B9 的核心数学区分正确

33 号 §5.1–5.3 明确说明：线性 predictor contrast 的 row-space 判据不能自动证明 inverse-link 后的 objective-scale 非线性 contrast 可识别；四个 cell predictor 行分别可识别是充分条件，observational-equivalence / estimand-invariance 是更一般的定义。

对于固定 nuisance 的 canonical logistic 子模型，该不变性定义是合理的识别判据；完整 GLMM 以相同边际观测分布下 estimand 必须相同来定义识别，也方向正确。实际精确认证工具仍 OPEN。

### 3.3 Task-block 结构与 CRN 限制写得更严谨

33 号 §3.1–3.3 将四格结果作为一个 task-block 向量，明确任务、block、replicate 嵌套关系和执行顺序；也正确指出相同 API seed/任务实例不自动构成严格 CRN。Bernoulli GLMM 的 task/block 随机截距可作为预注册起点，但其分布假设、随机斜率必要性及真实任务校准仍须验证。

### 3.4 BFDR 前缀规则在概率输入有效时成立

33 号 §8.2–8.3 中，按 local-null probability 升序排列，并对前缀计算平均 local-null probability，确实可得到每个固定集合大小下最小的平均 local-null 前缀。给定 q_e=1-ell_e 且 C_FP,C_FN >= 0，文中固定大小集合的损失差推导成立。

但这项检查只验证“输入概率与损失定义一致时”的前缀优化，不代表 §6.4 的 M2/M3 envelope 可以直接解释为真实 posterior probabilities。R1 仍然阻塞最终风险解释。

### 3.5 未决边没有被直接填零

33 号 §7.3–7.5 区分了 unresolved、supported practical null、selected supported 与 not selected；主 builder 没有将所有 unsupported edge 静默赋值为零。这是正确方向。R5 指出的是其 rho_AB 覆盖率语义仍有缺口，而不是说文档完全没有缺失状态。

## 4. 必须修订的问题

### R1 — M2/M3 conservative envelope 不是当前所称的 posterior expected loss

**位置：** [33 §6.4](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L754-L770)、[33 §8.3](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L900-L938)。

当前定义：
\[
\ell_e^*=\max(\ell_e^{(2)},\ell_e^{(3)}),\qquad
q_e^*=1-\ell_e^*=\min(q_e^{(2)},q_e^{(3)}).
\]

这可以作为保守 local-null envelope 用于边资格/BFDR；但将其直接代入
\[
L(S)=C_{FP}\sum_{e\in S}\ell_e^*
+C_{FN}\sum_{e\notin S}q_e^*
\]
并称为“posterior expected decision loss”并不成立。

原因是对任一模型 M，ell_e* >= ell_e^(M)，但 q_e* <= q_e^(M)。因此：
- 入选边的 FP 项被抬高；
- 未入选边的 FN 项被压低。

该损失不是 M2 或 M3 下的 posterior expected loss，也不自动是两模型最坏情形总损失。它可以被定义为偏向避免假阳性的 envelope score，但必须如实命名，并证明该 score 对目标决策有用。

**要求任选并冻结一条路线：**

A. **模型平均路线：** 预注册 pi(M)，使用
\[
\ell_e^{mix}=\sum_M\pi(M)\ell_e^{(M)},\qquad
q_e^{mix}=1-\ell_e^{mix},
\]
再基于同一个模型平均 posterior 计算 BFDR、决策损失和 acquisition。

B. **鲁棒决策路线：** BFDR 可继续用 ell_e*=max_M ell_e^(M) 作保守约束；但决策损失应明确为
\[
L_{robust}(S)=\max_{M\in\{2,3\}}L_M(S),
\]
其中每个 L_M 使用同一模型自己的 ell^(M),q^(M)。需重新定义集合优化和伪代码；原有“固定 k 最优前缀”证明不能未经证明直接沿用。

C. **评分函数路线：** 保留 (ell*,q*)，但将其明确降级为 conservative envelope decision score，而不是 posterior expected loss / worst-case posterior risk；必须对实际 FDP、FN、decision regret 和搜索收益进行校准。

此外，§9.2 的逐索引 E[max(R^(2),R^(3))] 若两套 model-specific fantasy 独立生成，得到的是产品耦合下的期望最大值；它通常不等于 max(E[R^(2)],E[R^(3)])，且会对模型间预测方差额外惩罚。必须说明采用产品耦合的理由，并与“最大模型期望风险”及模型平均风险作比较；成本包络同理。

### R2 — Acquisition 非正停止没有 MC 不确定性门

**位置：** [33 §9.4](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L1072-L1091)、[33 伪代码 §10.4](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L1580-L1588)。

伪代码在计算 A_hat 后直接：
\`\`\`text
IF every A_hat <= 0:
    RETURN STOP_NONPOSITIVE
\`\`\`

但 MCSE_A 已计算，却没有用于判断 acquisition 是否确实非正。小样本下 A_hat <= 0 可能只是 MC 误差。

**要求：**
1. 预注册 acquisition sign 的单侧不确定性规则，例如只有所有候选的 A_hat(d)+z_MC MCSE_A(d)<=0 时才允许以非正收益停止。
2. 若上界仍大于 0，继续增加 MC 至 S_max；达到上限仍不能判断时，必须按预注册规则标记 uncertain/abstain，而不是把点估计当真值。
3. 若选择一个点估计为正但下置信界不为正的候选，也必须明确是“探索性选择”还是拒绝执行。
4. 对自适应 top-two 比较和多候选重复查看，说明 MC stopping rule 的误差控制/校准方式。

否则当前停止逻辑会让 acquisition 因 MC 噪声提前终止，B3 不通过。

### R3 — 同一 base key 的 retry 次数会跨轮重置

**位置：** [33 §3.4](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L278-L320)、[33 伪代码 §10.1](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L1183-L1213)。

INCREMENTAL_COST 对 cache miss 计算 C0，并从 ledger 取 next_unused_attempt；但 OBSERVE_FOUR_CELL_DESIGN 每次被调用都把
\`\`\`text
retries_used := 0
current_attempt := next_unused_attempt(base_key, ledger)
\`\`\`
重新初始化。

如果某个 base key 先前已经发生一次或多次 retryable failure，之后再次以同一 base key 进入候选池，新的调用仍可能获得完整的 K_retry 配额。当前 C0 也把“已有失败历史但没有可复用成功结果”的 key 当成新的 initial-new key。

**要求：**
- 在 base-key ledger 中持久化首次 attempt、已消耗 retry 数、失败类别、是否 terminal/exhausted、可复用结果和剩余 retry allowance；
- C_inc^0 只统计真正从未执行过的 base key；已有 attempt 历史的下一次执行应记为 continuation/retry；
- K_retry_remaining=max(0,K_retry-K_retry,used)，且跨 proposal/generation 不得重置；
- terminal/exhausted key 不得仅因 cache 中没有成功结果而重新获得完整 retry 配额；
- fantasy 与真实执行必须读取相同的 retry-history state；
- C_cap 应按当前剩余 attempt/retry allowance 计算，并通过多轮同 key 反例测试。

否则 retry policy 不具备跨轮可审计性，B8/B10 不通过。

### R4 — Fisher practical-information 门存在 rank 与 GLMM 信息定义缺口

**位置：** [33 §5.5](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L574-L637)。

当前
\[
I_{target}=U\bar I_{eff}U^\top
\]
维度为 r×r，但门禁使用 lambda_min+(I_target)，只检查正特征值。若
\[
I_{target}=\begin{bmatrix}100&0\\0&0\end{bmatrix},
\]
则 lambda_min+=100，可能通过阈值，尽管 target subspace 中仍有一个完全无信息方向。

**要求：**
- 若目标定义为完整 Row(G)，必须要求 rank(I_target)=r，再检查最小特征值；若只需 estimand-sensitive 子空间，则显式构造该子空间并证明未被遗漏的方向不影响 Delta。
- 不得让 Moore–Penrose inverse 将未识别方向变成“零方差”。V=G I_eff_bar^dagger G^T 不能不加限定地称为 posterior covariance；若保留，应称 Fisher/asymptotic covariance proxy 并给出成立条件，或直接用 posterior predictor/estimand covariance。
- 明确 I_M 是对第 4.1 节边际 GLMM likelihood（已积分 task/block random effects）计算的 expected Fisher，还是 conditional/complete-data Fisher。主 estimand 已积分随机效应，信息门也必须与该边际目标一致；variance components 作为 nuisance 的处理需明确。
- 仅用 posterior mean information 再取最小特征值可能掩盖 posterior draw 中的弱信息方向；至少报告 posterior draw-wise lambda_min 分布/低分位数，并预注册主门禁用哪个分位数。

### R5 — rho_AB 当前不是支持覆盖率

**位置：** [33 §7.3–7.5](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L812-L849)。

当前定义
\[
\mathcal S_g(A,B)=\{(i,j)\in S_g:i\in A,j\in B\},
\quad
\rho_{AB}=\frac{|S_g(A,B)|}{|A||B|}.
\]
由于 S_g 是 selected edge set，rho_AB 测量的是 selected-positive-edge density，而不是 supported cross-edge coverage。SUPPORTED_PRACTICAL_NULL 已有支持且应与 unknown 区分，但它不进入 n_AB；UNRESOLVED 也不进入 n_AB。因此当前 rho 将已确认 practical zero 与 unknown 一样从覆盖率分子排除。

**要求二选一：**
- 若 rho 的含义是 support coverage，定义 n_support=n_selected+n_supported_null，rho_support=n_support/(|A||B|)，并单独定义 positive selected density；已确认 practical-null 的 similarity 可作为支持的零值，但 NOT_SELECTED/UNRESOLVED 仍为 NA。
- 若 rho 的含义是 selected-positive density，则重命名，不再称 coverage，并将其作为额外稀疏度门限进行敏感性分析；同时定义真正的 support coverage 指标。

否则 B11 的“无边与无证据分离”只在分类表中成立，没有完全传递到 cluster merge gate。

### R6 — 双模型 fantasy 的 max-risk/max-cost 需要概率解释

**位置：** [33 §9.2–9.3](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L982-L1027)。

两套 fantasy 分别从 M2/M3 posterior predictive 生成，并在相同索引 s 上计算 max(R2_s,R3_s)。若两套 fantasy 独立，则 (1/S) sum_s max(R2_s,R3_s) 估计的是独立产品耦合下的 E[max(R2,R3)]，而非标准 worst-case model risk max_M E_M[R]。它会额外惩罚模型预测分布的离散程度，且成本包络同理。

**要求：**
- 明确当前规则是 product-coupled envelope risk，而不是一般意义的 worst-case expected risk；
- 同时报告/比较 max_M E_M[R]、预注册模型平均风险及当前 E[max R_M]；
- 若要保留当前方法，证明其保守性是研究所需而非纯粹过度惩罚，并在相同 MC 预算下比较候选排序、采样成本和最终决策；
- 说明两个模型的 fantasy draws 如何配对、是否复用计算层 CRN，以及为何该 coupling 不会人为改变候选排序。

本项可保留为 OPEN 候选，但不能把它当作已证明的保守定理。

### R7 — 活动图集合和权重更新需要明确时间尺度

**位置：** [33 §8.4](33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md#L940-L948)。

文档要求 G_act 和 omega_g 在采样前冻结，但 graph key 包含 round 和 parent ID。需要明确这是“每个 acquisition cycle/round 内冻结，下一轮重新预注册”，还是整个 RSI run 固定。新 parent/new generation 图加入时，旧图何时退出、权重如何重归一、跨轮风险曲线如何比较，都应写清楚。否则 R(D) 会随活动图集合变化，acquisition 改善可能混入图集合/权重变化。

## 5. B1–B12 独立状态

| 项目 | 独立复审状态 | 说明 |
|---|---|---|
| B1 | PARTIAL | estimand 与 q/w 已拆分；权重作为 linkage similarity 的理论/经验优势未成立 |
| B2 | REQUEST CHANGES | M2/M3 状态机存在；保守 envelope 与损失解释不一致，高阶诊断的具体统计判据仍 OPEN |
| B3 | REQUEST CHANGES | risk/acquisition 结构已对齐，但概率含义与 MC sign stopping 未闭合 |
| B4 | PARTIAL | 四格 task-block 与随机截距已定义；随机效应假设和真实校准 OPEN |
| B5 | PARTIAL | nuisance 联合后验框架已定义；先验数值、近似和 Fisher nuisance 处理 OPEN |
| B6 | REQUEST CHANGES | rank 门和边际 GLMM Fisher 定义仍有缺口 |
| B7 | PARTIAL | per-graph family 清楚；跨图 global/online FDR 明确不主张，活动图权重时间尺度待补 |
| B8 | REQUEST CHANGES | base/attempt key 框架已定义；跨轮 retry 额度没有持久化 |
| B9 | PARTIAL | 非线性识别定义方向正确；精确认证工具和 GLMM 认证仍 OPEN |
| B10 | REQUEST CHANGES | 四格固定设计已定义；retry state 和 fantasy coupling 仍有缺口 |
| B11 | REQUEST CHANGES | 未决不填零已定义；cluster rho 没有真正区分 known-zero support 与 unknown |
| B12 | PARTIAL | prior sensitivity/null calibration protocol 已写；没有实际校准结果，保持 OPEN |

## 6. 本轮没有通过的事项

- 未批准 V2.2 整体规格。
- 未批准 TCAIL 独立创新性。
- 未批准 TCAIL 为演化计算核心创新。
- 未批准算法实现或正式 Phase 0。
- 未运行任何性能实验、真实 Agent 实验或 A800 训练。
- 未调用 DeepSeek/真实 LLM API。
- CI-GOM、IMCE-RSI 继续冻结。

## 7. 下一步唯一任务

只做 **V2.2 corrective specification revision R1**，不编码、不实验。Executor 应创建新的修订草稿和矩阵，保留 33/34 号作为原始 R0 审查对象，不静默覆盖历史审查基线。修订完成后交给不同会话进行 R2 独立复审。

下一轮必须先解决 R1–R5；R6/R7 需给出明确数学定义或保留 OPEN 并说明不会影响主 claim 的条件。完整执行提示词见 SESSION_HANDOFF.md 最新章节。
