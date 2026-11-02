# 17 — TCAIL 形式化规格 V2（修订稿）

**日期：** 2026-11-02  
**状态：** REVISED SPECIFICATION / NOT IMPLEMENTED / PENDING INDEPENDENT REVIEW  
**替代关系：** 本文件仅替代 14_FORMAL_ALGORITHM_DESIGN_V1.md 的 TCAIL（Paper 1）部分；CI-GOM 部分不在本轮修改范围内，继续冻结。  
**审计依据：** 16_TCAIL_SPECIFICATION_AUDIT_R1.md、18_TCAIL_RELATED_WORK_AUDIT_R1.md  
**唯一研究仓库：** yujian777555/kaitibaogao

> 本文件是对 TCAIL V1 的规格修订，不代表算法已经实现、通过模拟实验或具有已证实的新颖性。V2 完成后仍需独立数学复审。

---

## 0. 修订目标与结论边界

V2 必须明确回答五件事：

1. TCAIL 究竟估计什么交互效应；
2. 受约束配置空间中，什么时候可识别、什么时候只是样本不足；
3. Gaussian、Bernoulli、Beta 三种结果类型如何使用一致的似然和信息计算；
4. 如何在多条边、多任务上下文下控制虚假交互发现；
5. 如何证明候选采样机制比成熟的最优实验设计和交互筛选基线更有效。

**关键边界：**
- TCAIL 是交互结构识别与实验设计模块，不直接负责寻找最优 Agent；
- posterior information gain / Bayesian D-optimal 本身是成熟思想，不作为独立创新；
- V2 增加一个面向交互边决策损失的候选 acquisition，但它同样属于 Bayesian decision-theoretic design 的范畴，不能仅凭改写目标函数宣称新颖；
- 只有在强基线、消融和真实 Agent 实验中证明独立收益，才考虑形成论文贡献。

### EC 主线约束

TCAIL 本身属于统计建模与主动实验设计，不是一个完整的演化计算算法。它可以为后续 CI-GOM 提供交互结构，但不能仅凭“未来会接入 GOMEA”就把 TCAIL 单独认定为演化计算创新。

因此：
- TCAIL 的独立验证回答“交互能否被可靠、低成本地识别”；
- CI-GOM 后续验证回答“识别出的交互能否真正改善演化重组和搜索”；
- 若 TCAIL 的结果无法改善演化搜索，它可以是一个统计工具，但不能自动成为硕士论文的核心创新点；
- 最终毕业论文的核心贡献仍须落到演化计算机制及其在 Agent 配置优化中的实证收益上。

---

# 1. 问题定义

## 1.1 配置空间

第一版 V2 限定为 m 个二元模块槽位：

\[
x=(x_1,\ldots,x_m),\quad x_i\in\{-1,+1\}.
\]

合法配置由声明式 contract checker 决定：

\[
\mathcal X_{\mathrm{valid}}
=\{x\in\{-1,+1\}^{m}:H(x)=1\}.
\]

V2 暂不处理多类别模块、任意 DAG 或自由代码生成。多类别扩展必须另做规格与实验，不允许在本轮结果出来后临时改变编码。

## 1.2 任务上下文与观测单位

任务上下文 z 包含：
- 预先定义的 task-family；
- 部署前可观察的任务特征；
- 训练阶段标准化的连续上下文特征。

不得使用测试任务答案、金标、事后轨迹或不可部署时获得的信息。

结果变量为 Y。根据任务结果类型选择似然：
- 二元成功/失败：Bernoulli；
- 严格位于 (0,1) 的连续分数：Beta；
- 近似连续、无明显边界偏态的工作模型：Gaussian working likelihood。

主要评价单位定义为一个独立 task-block。一个 task-block 对应一个任务实例及其预注册的执行协议。相同任务上的多个重复 rollout 不得自动当作多个独立任务样本；应先按预注册规则聚合，或在模型中显式处理任务内相关性。

目标条件均值：

\[
\mu(x,z)=\mathbb E[Y\mid x,z].
\]

如果同一 task-family 内存在显著任务实例异质性，应通过 task-level random effect 或 cluster bootstrap 处理，不能把所有 rollout 当作独立同分布观测。

---

# 2. Pairwise interaction estimand：明确参考背景分布

这是 V2 最重要的数学修订。

## 2.1 条件交互

对槽位 i、j，令其他槽位配置为 \(u=x_{-ij}\)。在选定效应尺度 g 上定义：

\[
\begin{aligned}
\Delta^{g}_{ij}(u,z)
=&\ g(\mu(+1,+1,u,z))
-g(\mu(+1,-1,u,z))\\
&-g(\mu(-1,+1,u,z))
+g(\mu(-1,-1,u,z)).
\end{aligned}
\]

四项必须对应相同的其他槽位背景 u。该量一般依赖 u，不能不加说明地写成只依赖 z 的单一边效应。

效应尺度：
- Gaussian：\(g(\mu)=\mu\)；
- Bernoulli logistic：\(g(\mu)=\operatorname{logit}(\mu)\)；
- Beta reward：\(g(\mu)=\operatorname{logit}(\mu)\)。

**主要交互图在 link scale 上定义。** 同时报告 reward scale 的平均性能差异作为实际意义解释。两种尺度不可混用，也不能在看到结果后选择更有利的尺度。

## 2.2 合法共同支持

定义 pair 的共同四格合法背景集合：

\[
\Omega_{ij}
=
\{u:\ H(+1,+1,u)=H(+1,-1,u)
=H(-1,+1,u)=H(-1,-1,u)=1\}.
\]

如果四种模块组合中有任何一种非法，该背景下的四格交互就不能作为无模型假设的直接对比。

预先指定目标背景分布 \(\pi_{\mathrm{target}}(u\mid z)\)，定义共同支持质量：

\[
c_{ij}(z)
=
P_{u\sim\pi_{\mathrm{target}}}
(u\in\Omega_{ij}).
\]

在共同支持内定义参考分布：

\[
\pi_{\mathrm{ref}}(u\mid z,i,j)
=
\pi_{\mathrm{target}}(u\mid z,u\in\Omega_{ij}).
\]

如果没有可信的部署背景分布，合成实验使用共同支持上的均匀分布；真实 Agent 实验必须预先声明使用均匀背景还是目标部署分布。不能根据观测结果调整参考分布。

## 2.3 图中边的主要 estimand

\[
\bar\Delta^{g}_{ij}(z)
=
\mathbb E_{u\sim\pi_{\mathrm{ref}}}
[\Delta^{g}_{ij}(u,z)].
\]

同时报告背景异质性：

\[
V^{g}_{ij}(z)
=
\operatorname{Var}_{u\sim\pi_{\mathrm{ref}}}
[\Delta^{g}_{ij}(u,z)].
\]

因此一条边至少包含：
- 平均交互效应 \(\bar\Delta^g_{ij}(z)\)；
- 后验区间；
- 正/负方向概率；
- 背景异质性 \(V^g_{ij}(z)\)；
- 共同支持质量 \(c_{ij}(z)\)；
- 可识别性状态。

边表示的是指定参考背景分布下的平均非加性关系，不表示在所有其他模块配置下都具有相同符号和强度。

若平均交互接近零但背景异质性很高，应标记为 context-dependent interaction evidence，而不是简单宣称“没有交互”。

## 2.4 二元全因子下的解释

对二元配置的效应展开：

\[
\eta(x,z)=
\sum_{S\subseteq\{1,\ldots,m\}}
\beta_S(z)\prod_{k\in S}x_k.
\]

则条件交互为：

\[
\Delta^\eta_{ij}(u,z)
=
4\sum_{S\supseteq\{i,j\}}
\beta_S(z)\prod_{k\in S\setminus\{i,j\}}u_k.
\]

当参考背景是完整二元空间上的均匀分布时：

\[
\bar\Delta^\eta_{ij}(z)=4\beta_{\{i,j\}}(z).
\]

这意味着：
- 三阶项会改变条件交互；
- 在完整、均衡、正交的参考分布下，三阶项可以在平均 pairwise contrast 中抵消；
- 平均 pairwise effect 与条件交互异质性必须分别报告；
- 在受约束或不均衡参考分布下，平均交互不再必然等于简单的二阶回归系数。

---

# 3. 任务条件化响应模型

## 3.1 Pairwise 主模型

V2 先使用二阶模型：

\[
\eta(x,z)=
\gamma_0^\top\psi(z)
+\sum_i x_i\gamma_i^\top\psi(z)
+\sum_{i<j}x_ix_j\gamma_{ij}^\top\psi(z).
\]

其中：
- \(\psi(z)\) 为预先定义的 task-family/context 特征；
- \(\gamma_i\) 为槽位主效应；
- \(\gamma_{ij}\) 为任务条件化 pairwise interaction；
- 训练和测试按任务实例隔离，第一版不宣称能够泛化到训练中完全未出现的 task-family。

## 3.2 高阶诊断模型

Pairwise 模型不是 Agent landscape 必然正确的生成模型。

对合成环境和后续真实环境，单独拟合诊断模型：

\[
\eta_{\mathrm{diag}}(x,z)
=
\eta_{\mathrm{pair}}(x,z)
+
\sum_{i<j<k}x_ix_jx_k
\gamma_{ijk}^{\top}\psi(z).
\]

高阶项使用强层级收缩，且遵守 marginality / strong-heredity 规则：引入高阶项时保留其低阶父项。

诊断目标：
1. 检查 pairwise 平均交互是否估计正确；
2. 检查条件交互是否随背景变化；
3. 检查 pairwise surrogate 对完整 reward surface 的留出预测是否失配。

三阶项不意味着所有 pairwise edge 必须 abstain。只有当目标 estimand 无法识别、后验校准失败或预测失配严重到影响目标解释时，才对相应结论 abstain。

---

# 4. Group-ARD 与似然模型

## 4.1 Group-ARD prior

对每个 pairwise interaction group：

\[
\gamma_{ij}\sim
\mathcal N(0,\alpha_{ij}^{-1}I).
\]

主效应使用预先设定的弱信息先验。所有先验尺度、超参数上下界、停止条件和初始化必须在 confirmatory experiment 前冻结。

Gaussian likelihood 下可使用标准 Type-II ML / EM 更新：

\[
\alpha_g=
\frac{d_g}
{\|m_g\|_2^2+\operatorname{tr}(\Sigma_{gg})+\epsilon}.
\]

该闭式更新只在相应 Gaussian linear model 假设下使用。

## 4.2 Gaussian working likelihood

\[
Y_n\sim\mathcal N(\phi_n^\top\theta,\sigma_n^2).
\]

令 \(R=\operatorname{diag}(\sigma_n^2)\)，先验为
\(\theta\sim\mathcal N(m_0,\Sigma_0)\)，则：

\[
\Sigma=
(\Sigma_0^{-1}+\Phi^\top R^{-1}\Phi)^{-1},
\]

\[
m=
\Sigma(\Sigma_0^{-1}m_0+\Phi^\top R^{-1}y).
\]

Gaussian 情形下的 rank-one covariance update 是精确的共轭更新。

若观测本身严格在 (0,1)，Gaussian 仅作为工作近似，必须和 Beta 模型对照，不能默认其 posterior calibration 合格。

## 4.3 Bernoulli likelihood

\[
Y_n\sim\operatorname{Bernoulli}(p_n),
\qquad
p_n=\operatorname{logit}^{-1}(\phi_n^\top\theta).
\]

使用 Bayesian logistic regression。Laplace posterior 的局部 precision 为：

\[
\Lambda_{\mathrm{post}}
\approx
\Lambda_0+\Phi^\top W\Phi,
\qquad
W_{nn}=p_n(1-p_n).
\]

候选观测的期望 Fisher 权重应对当前参数后验取期望：

\[
w_{\mathrm{Bern}}(\phi)
=
\mathbb E_{\theta\mid D}
[p_\theta(1-p_\theta)].
\]

若每个独立 task-block 内有 r 次真正独立 Bernoulli trials，信息量可按 Binomial likelihood 计算；若 rollout 在同一任务内相关，不得直接乘以 r，应建模任务内相关或先聚合。

## 4.4 Beta likelihood

只对严格位于 (0,1) 的连续结果使用：

\[
Y_n\sim\operatorname{Beta}
(\kappa\mu_n,\kappa(1-\mu_n)),
\quad
\mu_n=\operatorname{logit}^{-1}(\phi_n^\top\theta).
\]

\(\kappa\) 是 concentration parameter。若 \(\kappa\) 未知，必须估计并纳入后验/不确定性；不得将其当作已知常数而不说明。

固定 \(\kappa\) 时，link predictor \(\eta=\operatorname{logit}(\mu)\) 的 Fisher information weight 为：

\[
w_{\mathrm{Beta}}(\mu,\kappa)
=
\kappa^2\mu^2(1-\mu)^2
\left[
\psi_1(\kappa\mu)+
\psi_1(\kappa(1-\mu))
\right],
\]

其中 \(\psi_1\) 是 trigamma function。

Beta 数据若包含精确 0 或 1，不能静默 clipping 后直接套 Beta；应预先选择 zero-one-inflated Beta 或适合该数据生成过程的其他模型。

## 4.5 非 Gaussian 的 Group-ARD 更新

Bernoulli 与 Beta 情形下，不得直接复用 Gaussian 的闭式 \(\alpha_g\) 更新。

采用：
- Laplace approximation 或明确指定的近似后验；
- 对 Group-ARD 超参数通过 Laplace approximate marginal likelihood 外层优化；
- 设置 \(\alpha_g\) 上下界和收敛准则；
- 使用 task-cluster bootstrap 重采样独立任务块，每次重新拟合 \(\alpha_g\)，评估超参数不确定性对区间校准的影响。

---

# 5. 可识别性：结构性不可识别与样本不足分开

## 5.1 两个不同层次

必须区分：

**模型参数可估计性：** 在当前预先指定的 pairwise feature basis 下，某个目标 interaction contrast 是否能由合法设计矩阵识别。

**非参数共同支持：** 对目标参考背景中的四格配置，是否存在真实合法且有观测支持的对比。模型外推不等于非参数识别。

## 5.2 设计矩阵检验

令 \(X_{\mathrm{legal}}\) 为合法配置及训练 task contexts 的特征矩阵；\(X_{\mathrm{obs}}\) 为当前已观测设计矩阵。

对 link-scale 目标边 e，定义其线性 contrast 向量 \(l_e\)，满足：

\[
\bar\Delta^g_e=l_e^\top\theta
\]

（该表达适用于本 V2 的线性 predictor scale）。

目标 contrast 在设计矩阵 X 下可估计，当且仅当：

\[
l_e\in\operatorname{Row}(X).
\]

数值检查：

\[
r_e(X)=
\frac{\|l_e-X^\dagger Xl_e\|_2}
{\|l_e\|_2+\epsilon}.
\]

当 \(r_e(X)\le\varepsilon_{\mathrm{rank}}\) 时判定该 contrast 在当前设计下可估计。数值容差、相对特征值阈值和条件数门槛须通过训练模拟确定并冻结。

## 5.3 状态机

每条边使用以下状态：

- **IDENTIFIABLE：** 目标 contrast 在当前观测设计的 row space 内，数值条件满足，且独立 task-block 数达到预注册要求；
- **PENDING_SUPPORT：** 当前观测设计尚不能估计该 contrast，但完整合法设计矩阵可以；主动采样应优先寻找能补足支持/秩的配置；
- **STRUCTURALLY_NOT_IDENTIFIABLE：** 完整合法设计矩阵仍不能识别该 contrast，且通过精确枚举或可审计约束求解证明；
- **STRUCTURAL_STATUS_UNCERTIFIED：** 配置空间过大，无法证明完整合法空间的结构秩。此时不得把它伪装成 STRUCTURALLY_NOT_IDENTIFIABLE，也不得宣称已识别。

如果当前合法候选池中存在补足 row space 的候选，状态必须是 PENDING_SUPPORT，而不是永久 NOT_IDENTIFIABLE。

## 5.4 非参数共同支持报告

另外报告：

\[
c_{ij}(z)=P_{\pi_{\mathrm{target}}}
(u\in\Omega_{ij}).
\]

对于共同支持不足的背景，必须说明目标 estimand 只覆盖共同支持子域。若使用 pairwise model 对未观测背景外推，应明确标注 MODEL-BASED，不得写成无模型假设的直接实验对比。

---

# 6. Edge selection 与 Bayesian FDR

对每个可识别边 e 定义：

\[
H_{0,e}:|\bar\Delta^g_e|\le\delta_{\mathrm{link}},
\qquad
H_{1,e}:|\bar\Delta^g_e|>\delta_{\mathrm{link}}.
\]

\(\delta_{\mathrm{link}}\) 是实际意义阈值，必须在训练/验证阶段冻结。

后验局部 null probability：

\[
l_e=P(H_{0,e}\mid D).
\]

将所有预注册 task-family × pair 的可识别边作为一个全局检验族，按 \(l_e\) 从小到大排序：

\[
l_{(1)}\le\cdots\le l_{(K)}.
\]

对候选前 k 条边计算：

\[
\widehat{\operatorname{BFDR}}(k)
=
\frac{1}{k}\sum_{r=1}^{k}l_{(r)}.
\]

给定预注册目标 \(q_{\mathrm{BFDR}}\)，选择最大的 k 使：

\[
\widehat{\operatorname{BFDR}}(k)
\le q_{\mathrm{BFDR}}.
\]

若不存在满足条件的 k，则输出空边集。

规则：
- PENDING_SUPPORT、STRUCTURALLY_NOT_IDENTIFIABLE 和 STRUCTURAL_STATUS_UNCERTIFIED 不混入已检验边集合；分别报告数量和比例；
- 不能对每个任务家族各自重复使用 q 而不说明整体错误率；
- 同时在独立 null simulations 中报告 empirical FDR / false-edge rate；
- Bayesian FDR 依赖后验校准，不能替代 posterior coverage 检查；
- \(q_{\mathrm{BFDR}}\)、\(\delta_{\mathrm{link}}\) 通过训练/验证和 null simulations 冻结，不能根据测试结果选择。

---

# 7. 候选 acquisition：区分成熟基线与待验证改进

## 7.1 标准 interaction-subspace Bayesian information gain

令 \(\theta_I\) 为所有目标 pairwise interaction 参数。一般形式：

\[
IG_I(d)=
H(\theta_I\mid D)
-
\mathbb E_{Y\mid D,d}
[H(\theta_I\mid D,d,Y)].
\]

其中 d 表示一个合法配置及 task context。

Gaussian linear model 下，若候选观测噪声方差为 v：

\[
\Sigma^+
=
\Sigma-
\frac{\Sigma\phi\phi^\top\Sigma}
{v+\phi^\top\Sigma\phi}.
\]

投影到 interaction subspace 后：

\[
IG_I(d)=
\frac12\log
\frac{\det(\Sigma_I)}
{\det(\Sigma_I^+)}.
\]

**该目标就是 interaction-subspace Bayesian D-optimal / mutual-information design 的特例，不是 TCAIL 的独立创新。** 必须把严格匹配的 interaction-subspace Bayesian D-optimal 作为等价基线，并设置数值一致性测试。

## 7.2 非 Gaussian expected information

Bernoulli / Beta 情形下，不得把 Gaussian rank-one 更新称为精确 posterior update。

主定义仍为 expected posterior entropy reduction。实现可选：
1. 对候选结果做 predictive Monte Carlo；
2. 对每个可能结果重新拟合 Laplace posterior；
3. 计算 interaction posterior entropy 的期望变化。

计算量过大时可用 expected Fisher approximation：

\[
\Sigma^+\approx
(\Sigma^{-1}+w(\phi)\phi\phi^\top)^{-1},
\]

其中 w 使用第 4 节相应似然的 expected Fisher weight。该方法必须标记为 local Fisher approximation，并通过模拟 coverage / ranking agreement 检查，不能称为精确 Bayesian IG。

## 7.3 候选：交互边决策风险下降

因为目标不是泛化的参数估计，而是作出“是否保留交互边”的决策，定义单边 Bayes classification risk：

\[
r_e(D)=
\min\{
C_{\mathrm{FP}}P(H_{0,e}\mid D),
C_{\mathrm{FN}}P(H_{1,e}\mid D)
\}.
\]

其中 \(C_{\mathrm{FP}}\)、\(C_{\mathrm{FN}}\) 是预先确定的误报/漏报代价；默认等权，若不等权必须说明应用依据。

总风险：

\[
R_{\mathrm{edge}}(D)=
\sum_{e\in\mathcal E_{\mathrm{estimable}}}
w_e r_e(D),
\]

默认 \(w_e\) 等权，不能根据测试结果加权。

候选配置 d 的 expected edge-decision risk reduction：

\[
A_{\mathrm{risk}}(d)=
\frac{
R_{\mathrm{edge}}(D)
-
\mathbb E_{Y\mid D,d}
[R_{\mathrm{edge}}(D\cup\{(d,Y)\})]
}{
\widehat c(d)
}.
\]

这是一种 goal-oriented Bayesian decision-theoretic design 候选。它的潜在价值是直接针对边发现决策，而不是最小化所有参数的体积；但 Bayesian decision-theoretic design / model-discrimination design 已有成熟先例，不能把该公式单独宣称为新颖。

**实验中必须同时比较：**
- interaction-subspace Bayesian D-optimal / IG；
- full-parameter Bayesian D-optimal；
- candidate edge-decision risk reduction；
- fixed D-optimal / fractional-factorial；
- random sequential design。

若 \(A_{\mathrm{risk}}\) 没有比严格匹配的 IG/D-optimal 提供稳定收益，则删除该候选机制。

## 7.4 PENDING_SUPPORT 时的 rank completion

当存在 PENDING_SUPPORT 边时，不应仅按当前 posterior variance 采样。

对候选 d，计算加入该配置后：
- 当前目标 contrast 中新增可估计的数量；
- 当前 interaction design matrix 的 rank gain；
- 估计子空间的最小非零特征值改善；
- 预计评价成本。

采用预先冻结的词典序策略：
1. 优先最大化能够被补足的目标 contrast 数；
2. 再最大化有效 rank gain；
3. 再最大化最小非零特征值改善；
4. 最后按 expected edge-decision risk reduction / cost 排序。

一旦不存在可补足的合法候选，才把无法识别的边转入结构性状态；若不能精确证明，则标记 STRUCTURAL_STATUS_UNCERTIFIED。

## 7.5 采样流程

V2 默认一次只选一个配置/task-block，完成评价后重新拟合 posterior，再选下一项。并行 batch 只能通过 greedy fantasy 或预先冻结的 batch rule 扩展；不能在初始 posterior 上一次性选完整批次却称为完全自适应。

---

# 8. V2 算法流程

~~~text
Algorithm: TCAIL-V2

Input:
    binary module slots and contract checker H
    pre-registered task families and observable context features
    target/reference background distributions
    rollout-equivalent budget B
    meaningful-effect threshold delta_link
    target Bayesian FDR q_BFDR

1. Enumerate or certify legal configuration support.
2. Build the full-legal and observed design matrices.
3. Select a task-family-stratified initial design.
4. Evaluate one task-block per selected configuration/context.
5. Fit task-conditioned Group-ARD posterior under the selected likelihood.
6. Refit/estimate ARD hyperparameters and assess task-cluster calibration.
7. For every pair:
       a. construct the pre-registered link-scale contrast;
       b. compute reference-background mean and heterogeneity;
       c. assess full-legal and observed-design estimability;
       d. assign IDENTIFIABLE / PENDING_SUPPORT /
          STRUCTURALLY_NOT_IDENTIFIABLE / STRUCTURAL_STATUS_UNCERTIFIED.
8. If PENDING_SUPPORT edges remain:
       select a legal candidate by lexicographic rank-completion gain.
   Else:
       select a candidate by the pre-registered acquisition
       (risk-reduction candidate or IG baseline).
9. Evaluate the candidate using the task-block protocol.
10. Update posterior and task-cluster uncertainty.
11. Apply global Bayesian FDR edge selection to identifiable edges.
12. Repeat until the fixed budget is exhausted.
13. Report graph, edge direction, uncertainty, heterogeneity,
    support coverage, calibration, cost, and abstentions.
~~~

---

# 9. 实验设计 V2

## 9.1 4 槽位仅作单元测试

m=4、16 个配置只用于：
- 解析公式测试；
- 正/负交互测试；
- task-family sign flip；
- 三阶条件交互；
- 受约束空间的结构性不可识别；
- Gaussian / Bernoulli / Beta likelihood 单元测试；
- IG 与 Bayesian D-optimal 数值等价测试。

不得用 4 槽位结果宣称算法可扩展或证明真实 Agent 有效。

## 9.2 扩展 landscape

正式合成评估至少覆盖：

| 槽位数 | 全空间配置数 | 用途 |
|---|---:|---|
| 4 | 16 | 单元与解析 oracle |
| 8 | 256 | 初步规模测试 |
| 10 | 1,024 | 中等规模 |
| 12 | 4,096 | 扩展性测试 |

每个规模改变：
- 稀疏 pair edge 数 / 平均度；
- 主效应与 pairwise interaction 强度；
- task-family 数量（至少 2、4）；
- 共享交互、符号翻转、幅度变化、任务特异边；
- 无交互 null、仅主效应、pairwise、三阶-only、高阶混合；
- 合法配置比例（全合法与不同约束密度）；
- Bernoulli noise 与 Beta concentration；
- 评价预算比例。

至少 30 个独立 landscape seeds；最终 confirmatory 样本量还要由预先的 power simulation 检查。各算法在相同 landscape、task blocks 和 budget 下配对比较。

预算按完整合法配置 × 预注册 task-family task-block 总数的比例冻结，例如 5%、10%、20%、40%。同一预算下按实际 task-block evaluations 计费；重复 rollout、缓存命中、失败任务也必须进入成本账本。

## 9.3 必须包含的真值场景

1. Null：只有截距/主效应，没有 pairwise interaction；
2. Sparse pairwise：少量正交互与负交互；
3. Task sign flip：同一边在不同 task-family 方向相反；
4. Task magnitude shift：边强度随 task-family 改变；
5. Task-specific edges：只在部分任务家族存在；
6. Three-way only：存在高阶效应但没有真实 pairwise link-scale 平均效应；
7. Mixed order：pairwise 与三阶项共存；
8. Constrained support：部分组合非法，导致部分目标 contrast 只能部分识别或结构性不可识别。

Null 与 three-way-only 场景尤其重要：TCAIL 必须控制 false edge，不能把高阶项或噪声强行解释成两两边。

## 9.4 基线矩阵

必须比较：

1. Full factorial oracle（仅小空间）；
2. Random legal design；
3. Fixed fractional-factorial / resolution-aware design；
4. Frequentist D-optimal design；
5. Full-parameter Bayesian D-optimal；
6. Interaction-subspace Bayesian D-optimal / IG；
7. Sparse pairwise regression + fixed design；
8. Group-ARD + fixed D-optimal design；
9. Group-ARD + random sequential design；
10. Group-ARD + standard IG；
11. TCAIL-V2 candidate risk-reduction acquisition + rank-aware support gate；
12. 可复现的 interaction group screening / GDS-ARM 等强筛选方法（确认其设计假设与任务适用性后纳入）。

严格匹配：
- rollout-equivalent budget；
- task split；
- noise realization / paired task blocks；
- hyperparameter tuning budget；
- model family / evaluator / execution environment。

## 9.5 主要指标与统计

主要指标：
- 非 null 场景的 edge AUPRC-budget 曲线面积（AUBAC），在预注册预算点上计算；
- null 场景 empirical false-edge rate / FDR 作为安全门禁。

次要指标：
- link-scale marginal interaction contrast RMSE；
- reward-scale marginal contrast error；
- edge precision / recall / F1；
- positive/negative direction accuracy；
- posterior interval coverage；
- held-out configuration-task prediction error；
- conditional heterogeneity estimation error；
- NOT_IDENTIFIABLE / PENDING_SUPPORT 状态准确率；
- 每条边达到目标后验决策风险所需 rollout 数；
- wall-clock、token、失败次数和货币成本。

统计：
- 以 independent landscape 为主要重采样单位；
- 同一 landscape 上的算法结果配对；
- 报告效应量、95% 区间和每个预注册场景的结果；
- 多场景、多基线比较采用预先指定的多重比较校正；
- 不能只挑最好任务、最好 seed 或最好预算点报告。

## 9.6 消融

1. 去掉 task conditioning；
2. Group-ARD 换为普通 pairwise OLS / sparse regression；
3. risk-reduction acquisition 换为 interaction-subspace IG；
4. 去掉 rank-aware support completion；
5. 去掉 Bayesian FDR；
6. 去掉 task-cluster bootstrap recalibration；
7. 去掉 higher-order heterogeneity diagnostic。

每项消融必须对应一个预注册机制假设。

---

# 10. 通过、停止与修订规则

## 10.1 TCAIL 合成 Gate

只有以下条件全部满足，才进入真实 Agent protocol 设计：

1. 公式、实现和数值单元测试通过独立审查；
2. null 场景虚假边控制达到预先锁定标准；
3. 正/负交互、task sign flip 与 task-specific edge 能稳定识别；
4. 受约束空间的 identifiability state 不混淆；
5. posterior interval coverage / calibration 达到预注册标准；
6. 在同预算下，候选方法相对最强公平基线具有可重复的实际收益；
7. risk-reduction acquisition 若不优于 IG/D-optimal，则删除，不包装为创新；
8. 大规模 landscape 上没有明显失效或成本不可接受的问题；
9. 结果可由独立代码复审和 clean rerun 重现。

阈值必须由 training/pilot 和 null simulation 事先确定；测试集不能参与阈值、先验、超参数和 acquisition 选择。

## 10.2 停止规则

- 若 pairwise edge 在真实 Agent 任务中普遍弱于主效应模型，TCAIL 的必要性不成立，暂停或 NO-GO；
- 若 active design 不优于固定 D-optimal / interaction screening，删除主动采样创新主张；
- 若只有合成真值有效、真实 Agent 无效，不能作为已验证论文贡献；
- 若交互后验不校准或 BFDR 失效，先修统计方法；
- 若 TCAIL 图不能改善后续 EC 搜索，它不能仅凭统计识别准确率就被认定为 EC 核心贡献。

---

# 11. 当前状态

| 项目 | V2 状态 |
|---|---|
| Pairwise estimand | REVISED / PENDING REVIEW |
| Reference background distribution | DEFINED |
| Link-scale vs reward-scale | SEPARATED |
| Identifiability state machine | REVISED / PENDING REVIEW |
| Gaussian likelihood | DEFINED |
| Bernoulli likelihood | DEFINED |
| Beta likelihood | DEFINED |
| Non-Gaussian ARD update | DEFINED AS LAPLACE APPROXIMATION |
| Bayesian FDR | DEFINED |
| Standard IG / Bayesian D-optimal | BASELINE, NOT NOVEL |
| Edge-decision risk acquisition | CANDIDATE, NOT NOVELTY-VERIFIED |
| 8/10/12-slot scaling | SPECIFIED |
| Higher-order diagnostics | SPECIFIED |
| EC-core contribution status | NOT ESTABLISHED |
| Implementation / experiments | NOT STARTED |

**本文件不宣称 TCAIL 已经通过 Gate。下一步是独立复审本规格；通过后才进入实现。**
