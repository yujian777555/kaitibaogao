# 20 — TCAIL V2.1 第三轮独立规格复审 R1

**日期：** 2026-11-02  
**审查对象：** 17_TCAIL_FORMAL_SPECIFICATION_V2.md 第 12 节及其与全文的接口  
**依据：** 16_TCAIL_SPECIFICATION_AUDIT_R1.md、18_TCAIL_RELATED_WORK_AUDIT_R1.md、19_TCAIL_V2_SECOND_PASS_REVIEW_R1.md、15_SEQUENTIAL_INNOVATION_VALIDATION_PROTOCOL.md  
**审查性质：** 独立数学、统计、算法闭合性复核；未运行代码或实验  
**结论：** REQUEST CHANGES / IMPLEMENTATION BLOCKED  
**唯一研究仓库：** yujian777555/kaitibaogao

---

## 1. 总结

V2.1 确实补上了第二轮复核提出的五项文字级缺口：

- 明确构造 reference-standardized contrast vector \(l_e\)；
- 将 M2/M3 模型阶数敏感性纳入边结论；
- 将连续 context 的 BFDR 检验族限制到预注册有限 anchor set；
- 给出 edge-risk acquisition 的 posterior predictive Monte Carlo、posterior refit、MCSE 和 common-random-number 流程；
- 明确 full-factorial reference budget 的计数分母。

其中，\(l_e\) 的线性对比构造、固定 concentration \(\kappa\) 时的 Beta Fisher information、线性 predictor 下的 row-space estimability，以及在后验校准前提下的 BFDR 公式，纸面上基本正确。

但是，**V2.1 尚未达到可实现规格**。剩余问题不只是文字润色，而是会改变“什么叫一条交互边”、模型失配门禁、最终边选择和主动采样目标的实质问题。当前建议维持 TCAIL = HOLD，不进入代码和正式 Phase 0。

本轮没有新增外部文献检索；新颖性结论仍限于既有相关工作审计范围，不能据此宣称文献空白。

---

## 2. 已通过的检查

### P1 — Reference-standardized contrast vector

给定一个固定的线性 predictor basis \(\phi(x,z)\)，定义

\[
l_e=
\sum_{u\in\Omega_{ij}}\pi_{\rm ref}(u\mid z,i,j)
[\phi(++u,z)-\phi(+-u,z)-\phi(-+u,z)+\phi(--u,z)]
\]

则 \(\bar\Delta^\eta_e=l_e^\top\theta\)。只要 estimand、设计矩阵、reference distribution 和 contrast vector 使用完全相同的编码与 anchor，这个恒等式成立。V2.1 对 link-scale 与 reward-scale contrast 的区分也是正确的。

### P2 — Beta Fisher information

对固定 \(\kappa\) 的 Beta\((\kappa\mu,\kappa(1-\mu))\) 模型，令 \(\eta=\operatorname{logit}(\mu)\)，文档给出的

\[
I_\eta=\kappa^2\mu^2(1-\mu)^2
[\psi_1(\kappa\mu)+\psi_1(\kappa(1-\mu))]
\]

是正确的。它是关于 \(\mu\) 的 Fisher information 经 \(d\mu/d\eta=\mu(1-\mu)\) 链式变换后的结果。**该结论只对固定 \(\kappa\) 成立**；未知 \(\kappa\) 的处理仍有缺口，见 B5。

### P3 — Row-space estimability

在线性 predictor 模型中，参数对比 \(l_e^\top\theta\) 在设计矩阵 \(X\) 下可估计，当且仅当 \(l_e\in\operatorname{Row}(X)\)。投影残差作为数值检验是合理的。它是给定模型 basis 的代数可估计性判据，不等于非参数共同支持，也不自动保证有限样本下的信息量充足。

### P4 — Bayesian FDR 形式

若每个 \(l_e=P(H_{0,e}\mid D)\) 是校准的 posterior local null probability，且检验族预先固定，则对排序后前 \(k\) 条边计算平均 local null probability，是标准 posterior expected FDP / Bayesian FDR 决策形式。它不能替代 posterior calibration 和 null simulation。

### P5 — Edge-risk Monte Carlo 流程

V2.1 已明确 posterior draws、posterior predictive outcomes、重新拟合、MCSE 和候选间 common random numbers，较 V2 有实质进展。但当前风险函数与最终 BFDR 选择规则尚未一致，不能仅凭计算流程更具体就认定 acquisition 已闭合。

### P6 — Budget denominator

\(B_{\rm full}=|\mathcal X_{\rm valid}|\times|Z_{\rm anchor}|\times R\) 作为“等成本 task-block 计数”是清楚的。若不同配置或 task-block 的实际 rollout 成本不等，它就不是实际 rollout-equivalent cost；需要在 protocol 中补充等成本假设或加权口径，见 B8。

---

## 3. 阻塞问题

### B1 — 有符号平均交互不等于演化 linkage（BLOCKER）

当前主 estimand 是

\[
\bar\Delta_{ij}(z)=E_{u\sim\pi_{\rm ref}}[\Delta_{ij}(u,z)]
\]

边假设又是 \(H_0:|\bar\Delta_{ij}(z)|\le\delta_{\rm link}\)。这定义的是**参考背景分布下的平均有符号交互**，不是一般意义上的“两个模块是否存在非加性依赖”。

如果不同背景下的条件交互符号相反，平均值可能接近零，但条件交互绝对值仍然很大。V2 虽然报告背景异质性 \(V_{ij}(z)\)，并说均值接近零而异质性较高时应标记 context-dependent evidence，但：

1. \(V_{ij}(z)\) 没有进入 H0/H1；
2. 没有对应的边选择或 BFDR 规则；
3. 没有进入 \(R_{\rm edge}\) acquisition；
4. 没有定义这种边是否应该进入后续 CI-GOM linkage。

因此可能出现：文字上承认存在 context-dependent interaction evidence，最终 BFDR 却把它当作无边；下游 EC 也拿不到该结构。

**必须先作研究定义选择：**

- 若目标确实只是平均有符号效应，则把输出称为 mean-effect graph，明确它不等价于通用 linkage graph；不能用它声称已识别所有非加性依赖。
- 若目标是给演化重组提供 linkage，则需定义对背景异质性敏感的依赖量，例如 \(E_u|\Delta_{ij}(u,z)|\)、\(\sqrt{E_u[\Delta_{ij}(u,z)^2]}\)，或预先定义的背景分层边决策；同时为该量定义实际意义阈值、后验决策和多重比较规则。

这不是简单增加一个报告指标，而是决定 TCAIL 识别对象的核心问题。必须先解决，再谈它能否为 GOM 提供有效 linkage。

### B2 — M2/M3 gate 没有在算法流程中闭合，且高阶范围不足（BLOCKER）

V2.1 第 12.2 节要求对每条边比较 M2 与 M3，但第 8 节伪代码仍只写“拟合 posterior—计算每条边 contrast—赋予四种 identifiability 状态—执行 BFDR”。伪代码没有：

- 拟合 M3；
- 在 M2/M3 下分别构造 \(l_e\) 并计算 contrast；
- 执行 model-order sensitivity gate；
- 产生 MODEL_ORDER_SENSITIVE 状态；
- 规定该状态如何影响 BFDR、acquisition 和最终图。

第 5.3 节的状态机也没有列入 MODEL_ORDER_SENSITIVE。当前文字规则和算法流程不一致。

此外还有三个实质问题：

1. **M3 只加入三阶项。** M2/M3 一致并不能排除四阶及更高阶项在受约束或非均匀 reference distribution 下投影到 pairwise contrast。12 槽位空间中四阶项并非可以忽略。必须增加更高阶压力测试/模型敏感性方案，或明确限制研究主张适用的真实响应阶数，并把超出范围的情形列为已知失效边界。
2. **Strong heredity 与 three-way-only 场景可能冲突。** 若 strong heredity 意味着三阶项非零时其所有低阶父项也必须非零，那么 9.3 要求的 three-way-only landscape 无法由 M3 正确表示。必须明确采用的是“父项保留在模型中”还是“父项系数必须非零”；后者会排除纯三阶真值。需要选择可覆盖预注册真值场景的层级先验/约束。
3. **模型间最终概率没有定义。** M2 和 M3 的 local null probability、BFDR 选择结果可能不同。当前只说比较决策，但没有规定最终 \(P(H_0\mid D)\) 来自 M3、模型平均、保守上界，还是两模型交集。不能把两个模型分别算出结果后再凭口头规则选一个。

**修订要求：** 将 M2/M3（以及确定的高阶敏感性范围）写入正式算法流程；定义明确的 model-order state 和最终 edge posterior/BFDR 规则；说明不一致边是否进入 acquisition、是否允许通过继续采样解除敏感状态。

### B3 — Acquisition 风险函数与 BFDR 最终决策不一致（BLOCKER）

当前 acquisition 使用

\[
R_{\rm edge}(D)=\sum_e w_e
\min\{C_{\rm FP}P(H_{0,e}\mid D),C_{\rm FN}P(H_{1,e}\mid D)\}
\]

这是各边独立二分类的 Bayes risk。可是最终输出并不是逐边独立地按该损失决策，而是对全局 edge family 执行 BFDR 约束后选择边集。

因此 acquisition 最小化的风险与最终实际采用的决策规则不是同一个决策问题。两者可能给出不同的最优采样配置，尤其当边数、anchor 数增加或 BFDR 阈值较严格时。

有两条可接受路线：

- 定义与最终 BFDR 规则一致的 constrained decision risk：先按预注册 BFDR 规则得到 \(S_{\rm BFDR}(D)\)，再定义该集合的 FP/FN loss，并对未来观测计算其期望下降；
- 或明确将当前 \(R_{\rm edge}\) 降级为 unconstrained per-edge surrogate acquisition，不能称为最终边决策风险；必须实验验证它与 BFDR 决策质量之间的关系，并与直接优化 BFDR-constrained risk 的方法比较。

同时必须明确 B2 的模型阶数敏感边如何计入风险。否则 acquisition 仍然不是完整可复现的算法定义。

### B4 — Task-block、配对执行与随机效应没有形成可执行统计模型（BLOCKER）

文档强调任务异质、随机 rollout 和 task-cluster bootstrap，但目前观测模型仍主要写成 \(Y\mid x,z\)，没有明确同一任务实例在多个配置下的重复观测关系。

需要明确：

- task-block ID 是否在不同配置之间复用；
- 是否对相同 task instance、相同随机种子做配对执行 / common random numbers；
- 若复用任务实例，任务难度造成的组内相关性如何进入 likelihood；
- 若不复用，如何通过随机分配和分层保证不同配置的 task mix 可比；
- task-level random intercept / random slope、paired contrast 或 cluster-robust/bagged posterior 具体采用哪一种；
- acquisition 中候选 \(d\) 究竟是 \((x,z)\) 还是 \((x,z,b)\)，未来 task-block 的抽样分布如何定义。

仅写“必要时 task-level random effect 或 cluster bootstrap”不足以闭合 BFDR 和 posterior risk 的统计基础。Bootstrap 可以评估抽样稳定性，但不能在未说明重采样和后验合并规则时自动修复一个忽略任务内相关性的 likelihood。

### B5 — 未知 Beta concentration 的 nuisance uncertainty 未进入信息计算（MAJOR）

Beta Fisher information 公式在固定 \(\kappa\) 下正确；但规格又规定 \(\kappa\) 未知时必须估计并纳入 posterior/uncertainty。当前没有定义：

- \(\kappa\) 的先验或估计方法；
- \(\theta\) 与 \(\kappa\) 的联合 posterior / Laplace 参数化；
- acquisition 中是否对 \(\kappa\) posterior 积分；
- 若使用 Fisher approximation，是否使用包含 nuisance parameter 的联合信息矩阵或相应有效信息。

不能一边声明 \(\kappa\) 未知并纳入不确定性，一边在设计权重中直接代入单个 \(\kappa\) 点估计。需要选择：预先用独立 pilot 冻结 \(\kappa\)，或定义联合 nuisance posterior/Fisher 处理。Gaussian 的 \(\sigma_n^2\) 若未知，也应采用同样的冻结或联合估计规则。

### B6 — Structural identifiability 的设计矩阵范围和实际信息门禁不完整（MAJOR）

V2.1 的 \(l_e\) 依赖 anchor 和模型阶数，但当前没有明确规定：

- \(X_{\rm legal}\) 是对每个 anchor，将所有合法配置与 anchor 交叉生成，还是只使用当前训练任务中实际出现的 context；
- M2 与 M3 是否分别构造 \(X_{\rm legal}^{M2}\)、\(X_{\rm obs}^{M2}\)、\(X_{\rm legal}^{M3}\)、\(X_{\rm obs}^{M3}\) 并执行 row-space test；
- M2 可识别而 M3 不可识别时，状态如何判定；
- GLM 中设计矩阵满秩但预测概率接近 0/1、Fisher information 极弱时，如何区分代数可识别与实际弱识别；
- 共同支持质量 \(c_{ij}(z)\) 很低时，是否仍允许输出高置信度边。

**修订要求：** 结构可识别性按模型 basis × anchor 单独计算；GLM 增加 Fisher-weighted practical information/conditioning 检查；为低共同支持质量预注册 abstention 或范围限定规则。不能把 row-space 满足直接等同于“足以可靠识别”。

### B7 — BFDR 检验族与最终图的索引不一致（MAJOR）

第 6 节原文定义为 task-family × pair；第 12.3 节改为 pair × anchor。两者只有在 anchor 与 task-family 一一对应时才等价，而文档允许一个 family 有多个连续特征 anchor。

必须统一成一个明确索引，例如 \(e=(i,j,a)\)，并明确：

- 最终输出是每个 anchor 一张 context-indexed graph，还是再聚合成一张全局图；
- 全局 BFDR 是对全部 pair × anchor 一起控制，还是先在 family 内控制再做跨 family 校正；
- MODEL_ORDER_SENSITIVE、PENDING_SUPPORT 和结构状态未认证的边是否进入检验族；
- M2/M3 不同 posterior local null probability 时，最终 BFDR 使用哪个概率。

在这些规则统一前，BFDR 虽有公式，但完整检验族仍未定义。

### B8 — Full-factorial 计数预算与实际 rollout-equivalent budget 的等价条件未写明（MINOR）

\(B_{\rm full}=|\mathcal X_{\rm valid}|\times|Z_{\rm anchor}|\times R\) 仅在每个配置/anchor/task-block 的执行协议具有相同评价次数和可比成本时，才与 rollout-equivalent budget 成比例。

若某些模块配置触发更多工具调用、重试或重复 rollout，则 task-block 计数与真实成本不同。需明确固定每个 block 的 rollout 数，或定义加权 reference cost；同时说明缓存命中、失败、重试和不等成本配置如何计入 acquisition 与预算曲线。

---

## 4. 新颖性与 EC 主线判断

### 4.1 TCAIL 独立新颖性：仍未成立

现有规格中的主要构件分别属于已有成熟方向：

- Group-ARD / 稀疏交互估计；
- task-conditioned regression；
- Bayesian OED / D-optimal；
- Bayesian FDR；
- model-order sensitivity；
- decision-theoretic / goal-oriented acquisition。

将这些机制放入 Agent 模块组合、合法配置和随机 rollout 场景，构成有价值的应用问题，但仅靠组合这些已知机制还不能证明存在独立算法贡献。edge-risk acquisition 目前仍是决策型实验设计的具体实例，不应先验称为新颖算子。

### 4.2 EC 核心贡献：尚未建立

TCAIL 仍是统计建模与主动实验设计模块，不是演化计算算法。即使它通过统计 Gate，也只能证明交互结构能被识别；不能证明它改善了 EC 搜索。

若最终目标是给 GOM/GOMEA 提供 linkage，则 B1 的“平均交互是否等于 linkage”必须先解决。后续仍需通过 oracle-linkage 与 learned-linkage 对照证明：估计结构能够改变 FOS/mixing，并在同 rollout budget 下改善 Agent 配置搜索。

因此当前不能把 TCAIL 直接列为已成立的硕士创新点或独立投稿论文。

---

## 5. 复审结论与状态

| 项目 | 复审结果 |
|---|---|
| \(l_e\) reference-standardized contrast | PASS（给定同一线性 predictor basis） |
| 固定 \(\kappa\) 的 Beta Fisher information | PASS |
| 线性 contrast row-space 判据 | PASS（代数可估计性层面） |
| BFDR 基本公式 | PASS（依赖校准 posterior 与固定检验族） |
| V2.1 MC acquisition 执行骨架 | PARTIAL |
| M2/M3 算法闭合 | FAIL |
| 高阶模型敏感性覆盖 | FAIL |
| linkage estimand 与边选择一致性 | FAIL |
| acquisition 与 BFDR 决策一致性 | FAIL |
| task-block 相关结构 | FAIL |
| 未知 nuisance 参数处理 | PARTIAL |
| anchor/BFDR 检验族 | PARTIAL |
| 预算口径 | PARTIAL |
| 独立新颖性 | NOT ESTABLISHED |
| EC 核心贡献 | NOT ESTABLISHED |

**最终结论：REQUEST CHANGES / IMPLEMENTATION BLOCKED。**

这不是说 TCAIL 已经被实验否证；它仍未实现、未实验。当前只是规格尚未闭合。不要把本次 REQUEST CHANGES 写成算法性能失败，也不要把纸面修订写成创新成立。

---

## 6. 下一轮唯一任务：修订规格，不编码

按以下顺序修改 17_TCAIL_FORMAL_SPECIFICATION_V2.md：

1. 先决定并固定 edge estimand：平均有符号效应，还是适用于 linkage 的背景条件化非加性强度；定义对应 H0/H1、BFDR 和输出图。
2. 闭合 M2/M3 gate：明确 strong/weak heredity；加入高阶 misspecification 压力测试；将 model-order status、posterior 合并/保守规则、BFDR 与 acquisition 接入伪代码。
3. 让 acquisition 目标与最终 BFDR edge decision 一致，或明确降级为 surrogate acquisition。
4. 定义 task-block 观测索引、配对任务/随机种子策略、任务内相关处理和 cluster posterior/calibration 方法。
5. 明确 Beta \(\kappa\) 与 Gaussian \(\sigma^2\) 的冻结或联合 nuisance uncertainty 方案。
6. 对每个模型 basis × anchor 构造 legal/observed design matrix；区分 structural identifiability 与 practical weak identification；定义低共同支持 abstention。
7. 统一 BFDR test family 与 context-indexed graph 输出。
8. 明确等成本 task-block 假设或加权 rollout-equivalent budget。

完成后再进行独立复审。**在上述阻塞关闭前，不实现 TCAIL，不运行正式 Phase 0，不调用真实 LLM，不启动 CI-GOM 或第三项迁移，不写硕士大论文正文。**

