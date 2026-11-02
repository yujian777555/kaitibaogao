# 22 — TCAIL Linkage Interface Revision Proposal R1（B1 处理稿）

**日期：** 2026-11-02  
**依据：** 20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md、21_GOMEA_LINKAGE_AND_NOISY_INTERACTION_RELATED_WORK_AUDIT_R1.md  
**状态：** PROPOSAL / NOT YET INTEGRATED INTO AUTHORITATIVE SPECIFICATION / PENDING INDEPENDENT REVIEW  
**范围：** 仅处理 B1（edge estimand 与 EC linkage 接口）；不代表 B2–B8 已关闭  
**唯一研究仓库：** yujian777555/kaitibaogao

---

## 1. 修订决策

建议放弃把 reference-background 平均有符号交互 \(\bar\Delta_{ij}\) 直接作为通用 linkage edge 的定义。

新的接口分为三层：

1. **Conditional fitness interaction：** 给定其他槽位背景 \(u\) 与任务上下文 \(z\)，定义目标函数的四格有限差分。
2. **Task-conditioned global interaction energy：** 用 RMS 汇总不同背景下的依赖强度，供描述、筛查和预算优先级使用；它不是某个 parent 的最终 FOS edge。
3. **Parent/task-conditioned local linkage posterior：** 对当前 parent \(x\) 和 task context \(z\)，估计局部依赖后验，形成 local weighted VIG；再由预注册的 FOS builder 构造 FOS。

这一区分既避免正负背景效应抵消，也避免把全局平均图直接强加给每一个搜索个体。

---

## 2. 目标尺度与 estimand

令 \(J(x,z)\) 为预先冻结、实际供演化算法优化的 Agent utility。对于成功率目标，\(J\) 是成功概率；若使用多指标 scalarization，scalarization 和归一化必须在训练前冻结。

统计模型可以在 link scale 上拟合，但每个 posterior draw 都必须通过 inverse-link 还原到 \(J\) 的 objective scale，再计算 linkage contrast。

对二元槽位 \(i,j\)，其余槽位背景 \(u=x_{-ij}\)，定义：

\[
\Delta_{ij}(u,z)=
J(+1,+1,u,z)-J(+1,-1,u,z)
-J(-1,+1,u,z)+J(-1,-1,u,z).
\]

该量是目标效用对 \(i,j\) 的条件二阶有限差分。若该值为零，则在指定背景下，改变 \(i\) 的效应不依赖 \(j\)；非零则表示存在局部 fitness interaction。

四格必须都满足：
- contract checker 合法；
- 任务/执行协议一致；
- 有可审计的支持或满足预注册的模型估计条件。

如果某格非法或没有共同支持，不能把模型外推当作直接识别。

---

## 3. 全局 RMS summary 与局部 linkage 必须分开

### 3.1 Global task-conditioned interaction energy

在预注册共同合法背景分布 \(\pi_{\rm ref}(u\mid z,i,j)\) 上定义：

\[
S_{ij}(z)=
\sqrt{
\mathbb E_{u\sim\pi_{\rm ref}}
[\Delta_{ij}(u,z)^2]
}.
\]

另可报告 signed mean：

\[
M_{ij}(z)=\mathbb E_u[\Delta_{ij}(u,z)]
\]

以及背景异质性：

\[
V_{ij}(z)=\operatorname{Var}_u[\Delta_{ij}(u,z)].
\]

其中 \(S_{ij}\) 是全局依赖能量摘要；\(M_{ij}\) 只描述平均方向；\(V_{ij}\) 描述背景变化。不得仅因 \(M_{ij}\approx0\) 就判定无 linkage。

在完整二元均匀全因子空间的 Walsh 展开下：

\[
S_{ij}(z)^2=
16\sum_{S\supseteq\{i,j\}}\beta_S(z)^2.
\]

在受约束或非均匀参考分布下，保留 RMS 定义，但不再声称它等于 Walsh 系数平方和。

### 3.2 Local parent-conditioned linkage posterior

对当前 parent \(x\)，令 \(u=x_{-ij}\)。定义：

\[
q_{ij}(x,z)=
P\left(
|\Delta_{ij}(x_{-ij},z)|>\delta_{\rm local}
\mid D
\right).
\]

\(\delta_{\rm local}\) 是在训练/验证阶段冻结的最小实际意义 interaction threshold。

当前 parent 的 local weighted VIG：

\[
G(x,z)=(V,E,W)
\]

其中：

\[
(i,j)\in E
\]

当且仅当：
- 当前局部四格支持与 identifiability 门禁通过；
- \(q_{ij}(x,z)\) 通过预注册 local edge-selection / BFDR 规则；
- 没有触发 model-order sensitivity abstention。

\(W_{ij}\) 可以使用 \(q_{ij}\) 或 posterior expected local interaction magnitude，但具体权重形式必须通过验证确定，不能临时挑选。

### 3.3 不支持时的状态

- 四格都合法但当前观测尚未支持：PENDING_LOCAL_SUPPORT；
- 合法空间结构性不可能形成共同四格：STRUCTURALLY_NOT_IDENTIFIABLE；
- 设计矩阵/模型阶数/实际信息不足以认证：STRUCTURAL_STATUS_UNCERTIFIED 或 MODEL_ORDER_SENSITIVE；
- 不得将这些状态静默转换为“无边”。

---

## 4. 为什么平均有符号 contrast 不够

考虑：

\[
J(x)=a x_i x_j x_k.
\]

对背景 \(u=x_k\)：

\[
\Delta_{ij}(x_k)=4a x_k.
\]

若 \(x_k\) 在参考分布中均匀：

\[
M_{ij}=0,\qquad S_{ij}=4|a|.
\]

平均有符号 contrast 会因背景正负抵消而漏掉该依赖；RMS summary 能保留其能量。对当前 parent，local posterior \(q_{ij}(x,z)\) 还能报告具体背景下的方向和强度。

但这不意味着 RMS 是新颖算法：它是对条件差分的二阶矩汇总，必须与 DLED、fitness-based linkage 和 noisy decomposition 方法比较。

---

## 5. 从 local VIG 到 GOMEA FOS

local weighted VIG 不等于 FOS。

建议采用如下接口：

1. TCAIL 为当前 parent/task 输出 local weighted VIG 和 posterior uncertainty；
2. 使用固定、公开、预注册的 FOS builder，把各 linkage estimator 输出统一转换为 FOS；
3. 至少比较 standard linkage tree、fitness-based linkage tree 和 conditional/clique-based FOS；
4. 对所有估计器使用相同的 FOS builder，以隔离“linkage estimator”本身的影响；
5. Pairwise graph 不可自动解释为 pair-only mixing masks。高阶/重叠依赖需要检验 LT/conditional FOS 是否构造了正确的联合 subset；
6. 对局部支持不足的边，不允许直接用于 mixing；保留 singleton / safe fallback。

本 proposal 不修改 CI-GOM 的实现，也不解除 CI-GOM 冻结。

---

## 6. TCAIL 可保留的候选方法贡献

现有工作已经覆盖：
- SLL-MI 与 Linkage Tree；
- fitness-based finite-difference linkage；
- DLED/cDLED 的 local/conditional linkage；
- conditional GOMEA 和最大团 FOS；
- LMM、ALI/AIM 等噪声环境下的 linkage decomposition；
- GA 搜索过程中副产物式 interaction learning。

所以 TCAIL 不得把上述任一项单独作为创新。

候选差异只能是：在随机、昂贵、任务异质且有合法配置约束的 Agent 模块空间中，联合完成：
- task-conditioned response model；
- current-parent-conditioned local fitness interaction；
- task-block matched stochastic evaluations；
- posterior uncertainty and abstention；
- active rollout allocation；
- 将局部 posterior linkage 传给标准 FOS builder。

只有在同预算下优于 FBL / cDLED / LMM / ALI 及在线副产物式基线，并提高最终 Agent 搜索表现，才能继续主张方法贡献。

---

## 7. 本 proposal 的边界

本 proposal 只为 B1 提供修订方向。以下问题仍未解决：
- B2：M2/M3、高阶失配、heredity、最终 posterior 合并和伪代码闭合；
- B3：acquisition 风险与最终 local BFDR 决策一致；
- B4：task-block 配对、任务内相关和 cluster posterior；
- B5：Beta concentration / Gaussian variance nuisance uncertainty；
- B6：模型 basis × anchor 的 practical identifiability；
- B7：动态 local graph 的 BFDR 检验族；
- B8：等成本或加权 rollout-equivalent budget。

**状态仍为 PROPOSAL / PENDING INDEPENDENT REVIEW。** 在完整 V2.2 规格通过独立复审前，不实现、不运行正式 Phase 0、不调用真实 LLM。
