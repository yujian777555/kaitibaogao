# 16 — TCAIL 数学与统计规格独立审计 R1

**日期：** 2026-11-02  
**审计对象：** 14_FORMAL_ALGORITHM_DESIGN_V1.md 的 Paper 1 / TCAIL 部分  
**审计性质：** 设计审查；尚未运行代码或实验  
**审计结论：** REQUEST REVISION / IMPLEMENTATION BLOCKED  
**唯一研究仓库：** yujian777555/kaitibaogao

## 1. 总结

TCAIL 已有可实现的总体框架：类别模块编码、任务条件化 pairwise surrogate、Group-ARD、合法空间可识别性门禁、interaction-only posterior information gain 和主动采样。

但当前规格还有若干会影响估计对象、统计有效性和创新性判断的缺口。**当前不应直接开始正式实现，更不能把算法写成已验证创新。** 应先完成下列修订，再冻结 Phase 0 protocol。

主要阻塞项：
1. pairwise contrast 未明确对其他槽位的条件化/边际化，导致交互 estimand 不唯一；
2. 把当前样本不足与结构性不可识别混在一起，可能过早 abstain；
3. Bernoulli/Beta 似然与 Gaussian rank-one posterior update / IG acquisition 的关系尚未严格定义；
4. edge threshold 缺少可执行的多重比较/FDR 规则；
5. interaction-only IG 本质上是 Gaussian 子空间 Bayesian D-optimal 信息增益，必须设置强 D-optimal 对照，不能将其本身宣称为新 acquisition；
6. 4 个二元槽位/16 个配置只能用于单元和机制调试，不足以证明预算优势或可扩展性；
7. 三阶 misspecification 与 pairwise edge 的目标定义需要区分。

---

## 2. 阻塞发现

### F1 — Pairwise interaction estimand 不唯一（BLOCKER）

当前 contrast 写为 \(\Delta_{ij}(z)\)，但其定义实际依赖其他槽位 \(x_{-ij}\)：

\[
\Delta_{ij}(x_{-ij},z)=
\mu(a,c,x_{-ij},z)-\mu(a,d,x_{-ij},z)
-\mu(b,c,x_{-ij},z)+\mu(b,d,x_{-ij},z).
\]

当存在三阶及更高阶项时，pairwise contrast 会随背景模块改变。不能一边写“其他槽位固定”，一边把结果记作只依赖 z 的单一边强度。

对当前 Phase 0 真值函数：
\[
\mu=0.5+\cdots+0.08x_1x_2-0.07x_2x_3
+0.06s(z)x_3x_4+0.025x_1x_2x_3,
\]
有：
\[
\Delta_{12}(x_3,z)=4(0.08+0.025x_3),
\]
因此 \(x_3=+1\) 时为 0.42，\(x_3=-1\) 时为 0.22；对 \(x_3\) 均匀边际化后才是 0.32。
同样：
\[
\Delta_{23}(x_1,z)=4(-0.07+0.025x_1),
\]
会随 \(x_1\) 改变强度。三阶项还会产生依赖背景槽位的条件性交互。

**必须修订：**
- 显式写出 \(\Delta_{ij}(x_{-ij},z)\)；
- 为图中的 pair edge 预先定义 reference distribution \(\pi_{\mathrm{ref}}(x_{-ij}\mid z)\)，例如全合法 Phase 0 的其他槽位均匀分布；
- 定义边 estimand 为该 reference distribution 下的平均 contrast：
\[
\bar\Delta_{ij}(z;\pi_{\mathrm{ref}})
=\mathbb E_{x_{-ij}\sim\pi_{\mathrm{ref}}}
[\Delta_{ij}(x_{-ij},z)];
\]
- 另行报告背景异质性，例如 conditional contrast 的方差/范围；
- 若背景依赖很强，标记 context-dependent / higher-order evidence，不能把平均边解释成所有背景下均成立；
- 对受约束空间，reference support 必须事先定义，并报告有共同四格支持的背景质量。没有共同支持时，不得伪造条件对比。

### F2 — 结构性不可识别与当前样本不足混淆（BLOCKER）

当前算法在 rank/eigenvalue gate 失败时直接标记 NOT_IDENTIFIABLE。但 rank 不足可能只是当前主动设计尚未采到必要配置，而不代表合法空间永远无法识别。

**必须拆成三个状态：**
- PENDING_SUPPORT：当前观测设计不满秩，但合法候选池中存在可补足识别性的配置；主动采样应继续寻找这些配置；
- IDENTIFIABLE：在预定义 estimand 下，合法支持和当前观测设计满足预设秩/条件数要求；
- STRUCTURALLY_NOT_IDENTIFIABLE：即使遍历全部合法配置，目标 contrast 仍无法识别。

只有第三种情况才能永久标记 NOT_IDENTIFIABLE。当前数据不足不得提前终止。

另需明确：
- \(X_{-ij}\) 应包含模型中所有非目标 nuisance columns，至少包含其他主效应、其他 pairwise groups、任务上下文交互及预先纳入的高阶诊断项；
- 区分 full legal design 的结构秩与 observed design 的当前秩；
- 若只存在部分可识别子空间，报告可识别 contrast 子空间，不得把整组参数一概称为已识别。

### F3 — Bernoulli / Beta likelihood 与 IG 更新不一致（BLOCKER）

当前 Sherman–Morrison 更新：
\[
\Sigma^+=\Sigma-
\frac{\Sigma\phi\phi^\top\Sigma}{v+\phi^\top\Sigma\phi}
\]
是线性 Gaussian likelihood 下的精确共轭更新。不能未经解释就直接套用于 Bernoulli logistic 或 Beta likelihood。

**必须分别定义：**
- Gaussian working likelihood：\(v\) 为单次观测噪声方差；
- Bernoulli：使用 logistic posterior（例如 Laplace）；候选设计评分使用当前预测概率 \(p\) 的 expected Fisher information \(w=p(1-p)\)，等价局部权重 \(1/v=w\)，采样后用观测重新拟合 Laplace posterior；
- Beta reward：若使用 \(\mathrm{Beta}(\kappa\mu,\kappa(1-\mu))\)，说明 \(\kappa\) 是 concentration，并使用对应 likelihood/Fisher information；若只用 Gaussian working variance，必须标明是近似设计并做 coverage calibration；
- 若一个候选配置聚合 \(r\) 次独立 rollout，明确有效观测信息和成本如何随 r 变化；同一任务内相关 rollout 不得按 r 个独立 task 样本计算。

候选 acquisition 必须和真实评价单位一致：单次 rollout、同任务重复 rollout 的均值、或一个 task-block 不能混用。

### F4 — Edge threshold 缺少明确多重比较控制（BLOCKER）

目前只说 \(\tau_{\mathrm{edge}}\) 通过 null/alternative 与多重比较校准，但没有可执行规则。槽位数增长后，pair 数 \(m(m-1)/2\) 和任务上下文数会共同增加。

建议预先定义 Bayesian FDR 选择规则。对被选边集合 S：
\[
\widehat{\mathrm{BFDR}}(S)=
\frac{1}{|S|}
\sum_{e\in S}
P(|\Delta_e|\le\delta_{\mathrm{link}}\mid D).
\]
选择满足预设目标 BFDR 的边集，并在 null simulations 中检查实际 false-edge rate。若改用 frequentist procedure，需说明依赖结构下的校正方法。不能只对每条边独立使用同一个 posterior threshold 而不控制整体错误发现。

### F5 — Interaction-only IG 与 Bayesian D-optimal 设计的关系未说明（NOVELTY BLOCKER）

在 Gaussian linear model 下：
\[
\frac12\log\frac{\det\Sigma_I}{\det\Sigma_I^+}
\]
就是对 interaction parameter subspace 的 Bayesian D-optimal information gain / mutual information。它不是天然的新 acquisition。

**必须加入强基线：**
1. full-parameter Bayesian D-optimal；
2. interaction-subspace Bayesian D-optimal（与当前 IG 目标严格匹配）；
3. frequentist D-optimal / fractional factorial；
4. Group-ARD fixed design；
5. Group-ARD + random sequential design；
6. 完整 TCAIL。

Paper 1 的潜在贡献不能只写“提出 posterior IG 主动采样”。必须证明任务条件化、稀疏层级估计、合法空间识别和经过校准的交互发现机制之间的组合，在同预算下比上述强基线有独立收益。还要做针对 Bayesian optimal design / adaptive experimental design 的文献审计。

### F6 — 4 槽位合成空间仅能作 debug（SCOPE BLOCKER）

4 binary slots 只有 16 个配置，适合：
- 单元测试；
- 验证公式；
- 检查正/负交互和 sign flip；
- 检查 constrained identifiability；
- 做小型 oracle 对照。

但它不足以单独证明 active design 的预算优势和可扩展性。必须增加更大空间，例如 8/10/12 个二元槽位，或可控多类别槽位，并系统改变：
- 真实交互稀疏度；
- 任务家族数量；
- 交互异质性；
- 合法组合比例；
- rollout noise；
- 评价预算。

小空间 full factorial 是 oracle 上界；大空间下比较固定预算的 active/random/D-optimal 曲线。

### F7 — 三阶 misspecification 与 pairwise edge 解释混淆（MAJOR）

当前文档称三阶项是 pairwise model misspecification，并要求发现后扩大区间或 abstain。但在正交、均衡的全因子设计中，三阶项可能与二阶项正交；此时 pairwise marginal estimand 仍可正确估计，模型的高阶预测残差却不为零。

**必须区分：**
- pairwise marginal interaction 是否估计正确；
- conditional interaction 是否随背景改变；
- pairwise surrogate 对完整 reward surface 是否失配。

三阶项不意味着所有 pairwise edge 都必须 abstain。正确做法是报告 reference-marginal pair effects、conditional heterogeneity 和 held-out residual diagnostics；只有当目标 estimand 不可识别或区间失去校准时才 abstain。若 CI-GOM 需要上下文依赖的高阶 linkage，则需另行研究，不能由 pairwise graph 自动推断。

---

## 3. 非阻塞但必须补齐的规格

### N1 — Task context 的适用范围
\(\psi(z)\) 含 task-family indicators，V1 只能在训练中已知的 task families 内做任务条件化；不能声称可直接泛化到完全未见的任务家族。第一阶段建议按 task instances 留出、但保证 family 在训练中出现。未见 family transfer 留给第三创新点。

### N2 — Empirical Bayes posterior calibration
Group-ARD 使用 plug-in \(\alpha_g\) 时，条件后验可能低估超参数不确定性。建议采用 task-level bootstrap 并在每次 bootstrap 中重新估计 \(\alpha_g\)，或引入 hyperprior 积分；报告 plug-in 与 bootstrap interval 的 coverage 差异。

### N3 — 初始设计与 rank-aware acquisition
B0 不能只是任意固定数字。先保证 task-family coverage 和最低可识别设计秩；当前数据为 PENDING_SUPPORT 时，acquisition 应能选择补足 rank 的合法配置。对数值矩阵使用相对尺度的 eigenvalue/condition-number threshold。

### N4 — 数值实现
log-determinant 使用 Cholesky / stable logdet；jitter 根据矩阵尺度确定；Group-ARD 的 \(\alpha_g\) 设置边界和收敛条件，避免数值塌缩。所有矩阵运算有小型解析测试。

### N5 — 多类别扩展
V1 先限制为二元槽位。后续多类别 edge strength 必须在看测试结果前固定一个聚合 norm/weighted contrast，不能事后在 max 与 RMS 之间择优。

---

## 4. 当前 TCAIL 状态

| 项目 | 状态 | 说明 |
|---|---|---|
| 总体算法框架 | SPECIFIED | 主体框架完整 |
| Pair estimand | REVISION REQUIRED | 缺少背景 reference distribution |
| Identifiability gate | REVISION REQUIRED | 需区分 sample insufficiency / structural impossibility |
| Likelihood 与 acquisition | REVISION REQUIRED | Gaussian/Bernoulli/Beta 更新需一致 |
| Edge multiplicity | REVISION REQUIRED | 需明确 BFDR/FDR 控制 |
| Acquisition novelty | HOLD | Bayesian D-optimal 强基线未加入 |
| Synthetic scope | REVISION REQUIRED | 16 配置只做 debug，需扩展规模 |
| Higher-order diagnostics | REVISION REQUIRED | 需拆分边估计与预测失配 |

**结论：REQUEST REVISION。当前不启动正式 Phase 0 性能实验。**

---

## 5. 下一步必须完成的修订顺序

1. 先重写 pairwise estimand，固定 reference background distribution；
2. 把识别状态拆为 PENDING_SUPPORT / IDENTIFIABLE / STRUCTURALLY_NOT_IDENTIFIABLE；
3. 对 Gaussian、Bernoulli、Beta 分别写出与 likelihood 一致的 posterior / expected-information update；
4. 明确 Bayesian FDR edge selection；
5. 将 interaction-subspace Bayesian D-optimal 纳入强基线，并重新评估 TCAIL 的独立新颖性；
6. 将 4-slot landscape 降级为 unit-test fixture，新增 8/10/12-slot scaling protocol；
7. 修正三阶 misspecification 的解释与测试；
8. 规格复审通过后再实现代码。

**本轮没有运行实验，没有产生任何性能结果，也没有通过 Gate-1。**
