# 19 — TCAIL V2 第二轮数学复核 R1

**日期：** 2026-11-02  
**审查对象：** 17_TCAIL_FORMAL_SPECIFICATION_V2.md  
**性质：** 第二轮纸面数学与统计复核；尚未实现、未运行模拟  
**结论：** REQUEST CHANGES / NOT READY FOR IMPLEMENTATION

---

## 1. 已通过的数学检查

### 1.1 Reference-background pairwise estimand
条件四格 contrast 对其他模块背景的依赖已被明确；在预先定义的共同合法支持上进行 reference averaging，避免把不同背景下的交互混成一个没有定义的量。

### 1.2 Link-scale separation
Gaussian identity、Bernoulli logistic、Beta logit-mean 三种尺度已明确分开。link-scale graph 与 reward-scale practical contrast 不再混为一谈。

### 1.3 Beta Fisher information
对固定 concentration κ 的 Beta(κμ, κ(1−μ)) 模型，令 η=logit(μ)，有：

\[
I_{\eta}
=
\kappa^2\mu^2(1-\mu)^2
\left[
\psi_1(\kappa\mu)+\psi_1(\kappa(1-\mu))
\right].
\]

该式由 Beta likelihood 对 μ 的 Fisher information 经链式法则乘以 (dμ/dη)^2 得到，公式正确。

### 1.4 Row-space estimability
在线性 predictor scale 上，目标 contrast \(l_e^\top\theta\) 在设计矩阵 X 下可估计，当且仅当 \(l_e\in Row(X)\)。数值投影残差 \(||l_e-X^\dagger Xl_e||/||l_e||\) 是合理的可实现检查。

### 1.5 Bayesian FDR
对 H0,e 与 H1,e 的 posterior local null probability 排序，并限制所选边平均 local null probability，是标准 posterior expected FDP / Bayesian FDR 决策形式。仍需 null simulation 检查 posterior calibration。

### 1.6 Gaussian information update
Gaussian 共轭后验更新和 interaction-subspace log-determinant 信息增益公式正确。将其明确归为 Bayesian D-optimal / mutual information baseline 是必要修正。

---

## 2. 阻塞问题

### F1 — 高阶模型失配尚未进入主要边估计（BLOCKER）

V2 的主要模型 M2 只包含主效应与 pairwise terms；三阶项被放在单独的诊断模型 M3 中。

问题在于：主动采样会产生非均匀配置设计。若真实响应包含三阶项，而主要估计仍只拟合 M2，则在非均匀/受约束/自适应设计下，高阶项可能与 pairwise columns 相关，从而偏置 pairwise coefficient。事后对 posterior prediction 做 reference averaging，不能自动消除这种模型投影偏差。

必须修订：
1. M3 不得只做报告性诊断；
2. 对每条边分别在 M2 与 M3 下计算 posterior reference-standardized contrast；
3. M2 与 M3 对边方向、是否超过实际意义阈值或 BFDR 决策不一致时，标记 MODEL_ORDER_SENSITIVE；
4. MODEL_ORDER_SENSITIVE 边不得进入高置信度交互图或后续 EC linkage；
5. 在完整均匀全因子下三阶项可能抵消，但在受约束或非均匀 reference distribution 下不得假设其抵消。

### F2 — 目标 contrast 向量 \(l_e\) 未显式构造（MAJOR）

V2 使用 \(l_e^\top\theta\)，但尚未把 \(l_e\) 与 reference distribution 的关系写成可直接编码的公式。

必须定义：

\[
l_e=
\sum_{u\in\Omega_{ij}}
\pi_{\mathrm{ref}}(u\mid z,i,j)
[
\phi(+,+,u,z)-\phi(+,-,u,z)
-\phi(-,+,u,z)+\phi(-,-,u,z)
].
\]

这样才能确保模型设计矩阵、estimability test、posterior contrast 和 reference distribution 使用同一个目标 estimand。

### F3 — 连续 task context 的 FDR 检验族未有限化（MAJOR）

模型允许连续 context features，但 BFDR 只写 task-family × pair。若要输出不同连续上下文下的图，必须预先指定有限的 context anchor set；否则“所有上下文边”的检验族没有可执行定义。

### F4 — Edge-risk acquisition 缺少 Monte Carlo 实现协议（MAJOR）

风险下降的数学目标已定义，但对 Beta 连续观测、Laplace posterior 和重新估计 ARD hyperparameters 的计算方式还不够具体。

必须明确 posterior draws、predictive outcomes、posterior refit、Monte Carlo standard error、候选间 common random numbers 和平局处理规则。否则不同实现可能得到不同 acquisition 排序。

### F5 — 预算分母定义不够精确（MINOR）

预算比例需要明确 reference full-factorial cost 的计算方式，包括 legal configurations、context anchors、每个配置的独立 task-block 数。否则 5%/10%/20%/40% 在不同任务拆分中不具可比性。

---

## 3. EC 主线检查

TCAIL 仍然不是完整 EC 算法。V2 已诚实记录这一点，这是正确的。

但这意味着：
- TCAIL 独立论文可能是统计/实验设计方向；
- 它不能仅凭给 CI-GOM 提供一张图，就自动成为 EC 创新；
- 后续必须证明图结构改变 linkage/mixing 决策，并在相同评价预算下改善演化搜索；
- 如果 TCAIL 不优于强设计基线，或不能为 EC 搜索带来下游收益，应缩小主张或 NO-GO。

---

## 4. 结论与下一步

**结论：REQUEST CHANGES。**

V2 的基础数学大部分正确，但高阶模型失配处理和 estimand-to-design-matrix 映射尚未闭合。先按本报告修订为 V2.1，再交由独立复审；当前仍不得进入正式实现或性能实验。

本轮没有代码、没有实验、没有性能结果、没有 Gate-1 PASS。
