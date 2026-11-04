# 38 — TCAIL V2.2 Revision R1 变更日志与闭合矩阵

**日期：** 2026-11-04

**状态：** CORRECTIVE REVISION MATRIX / PENDING R2 INDEPENDENT REVIEW / HOLD / IMPLEMENTATION BLOCKED

**唯一仓库：** `yujian777555/kaitibaogao`

**对应规格：** `37_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R1.md`

**审查依据：** `36_TCAIL_V2_2_INDEPENDENT_REVIEW_R1.md`、`D039_TCAIL_V2_2_INDEPENDENT_REVIEW_DECISION.md`

**历史基线：** `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md`、`34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md`

> 本矩阵记录 R1–R7 的规格修订，不是独立数学复审报告。`PARTIAL（修订规格已处理）` 不表示校准、实现、实验或创新 PASS。所有需要数值校准、形式证明、复现或实验的事项继续标为 OPEN。33、34、36 号及其历史审查基线均未覆盖。

---

## 1. 基线与修订范围

本轮开始时远端 `main` HEAD 为 `ea5c8f7500848baf7a4f3a345f362d0573e59a2b`，其中包含 36 号独立复审。37 号以 33 号为完整文本基线并生成独立修订稿；38 号记录变更。没有修改 33、34、36 号，也没有编写算法实现或执行实验。

本轮的核心路线选择如下：

1. R1 采用**鲁棒决策路线**：`ell_env/q_env` 只用于约束；每个模型使用自身 posterior probability 计算损失，最终最小化 `max_M L_M`。
2. R6 的主 fantasy 聚合采用 **worst-expected model objective** `max_m E_m[H]`；33 号的逐样本 product-max 只保留为诊断。
3. R2 的 confirmatory 选择要求收益下界为正；不能判定时 abstain，不把 MC 点估计当作真实符号。
4. R3 的 retry 额度属于 base key 的终身持久状态，而不是单次函数调用。
5. R4 的主信息门使用边际 GLMM expected Fisher、完整 target rank 和 posterior draw-wise 最小特征值低分位数。
6. R5 将 support coverage、selected-positive density 和 unknown density 分开进入 builder。
7. R7 的活动图集合与权重只在 acquisition cycle 边界改变。

---

## 2. R1–R7 逐项闭合矩阵

### R1 — M2/M3 风险语义与 posterior expected loss

- **状态：** `PARTIAL（修订规格已处理）`；鲁棒集合优化、actual FDP/FN、regret 和校准 `OPEN`。
- **原缺陷：** `max local-null/min q` 同时抬高 FP 并压低 FN，不能称为任一模型或两模型最坏情形的 posterior expected loss。
- **数学修订：**
  - `ell_env=max_M ell^(M)`、`q_env=1-ell_env` 仅定义保守可行集合与单边缘资格。
  - `L_{g,M}(S)=C_FP sum_{e∈S}ell_e^(M)+C_FN sum_{e∈Q_g\S}q_e^(M)+C_U|U_g|`。
  - `L_{g,rob}(S)=max_M L_{g,M}(S)`；在共同可行集合与 `ε_risk` 近似最优族中确定最终 `S_g^rob`，并令 `R_g=L_rob(S_g^rob)`。
- **37 号位置：** §6.3–6.4、§8.1–8.3、§9.2；`FIT_AND_ASSESS`、`BFDR_CORE`、`ROBUST_BFDR_DECIDE`、`DECIDE_ALL_GRAPHS`。
- **伪代码闭合：** 模型内 provisional 集合只用于敏感性；最终集合使用各模型显式 `(g,e,M)` posterior maps 和鲁棒优化。不再假设 `ell_env` 排序前缀必然最优。
- **可检查边界：** 空集始终可行；空和为零。两模型概率不同则 FP/FN 必须分别计算。没有精确枚举或最优性证书时返回 `ROBUST_OPTIMIZATION_UNCERTIFIED`、`R_g=NA`，不输出高置信集合。
- **仍 OPEN：** 包络约束的经验校准、鲁棒损失的实际效用、优化器证书和大规模计算可行性。

### R2 — Acquisition MC 非正停止与不确定性

- **状态：** `PARTIAL（修订规格已处理）`；区间覆盖、重复查看校准和数值误差控制 `OPEN`。
- **原缺陷：** `every A_hat≤0` 忽略 Monte Carlo 噪声，可能提前停止。
- **数学修订：**
  - 每个生成模型分别计算 `H_{m,s}=R_{m,s}+λ_cost C_{m,s}`、`\hat H_m` 与 `MCSE_H,m`。
  - 主估计为 `\hat A_wc=R^(r)(D)−max_m \hat H_m`，不使用 product-max 样本标准差。
  - 收益上界 `A_U` 使用下偏的模型目标区间，收益下界 `A_L` 使用上偏的模型目标区间；符号/执行与 rank 分别使用预注册误差预算。
  - 只有所有候选 `A_U≤0` 才允许 `STOP_NONPOSITIVE`；执行候选必须 `A_L>0`。
- **37 号位置：** §9.3–9.4；`SCORE_CANDIDATE`、`SELECT_DESIGN` 和主控制流停止分支。
- **伪代码闭合：** 若任一点估计上界仍为正则继续 MC；`S_max` 仍无正下界但有正上界时返回 `STOP_ACQUISITION_UNCERTAIN`。单候选也必须通过正下界资格。
- **可检查边界：** 全部 `A_hat<0` 但某 `A_U>0` 时不得停止；点估计为正而 `A_L≤0` 时不得执行；`S_max` 时无法判断不能改称非正。`alpha_sign+alpha_rank=alpha_MC`，候选和多次查看使用预注册 `j^{-2}` alpha-spending。
- **仍 OPEN：** 正态/MCSE 工作规则不是任意依赖下的已证 confidence sequence；其覆盖率、候选排名和偏差余量均需校准。

### R3 — Base-key 跨轮 retry 持久账本

- **状态：** `PARTIAL（修订规格已处理）`；崩溃恢复、多轮反例测试和真实成本审计 `OPEN`。
- **原缺陷：** 每次调用重置 `retries_used=0`，`C0/Ccap` 没扣除历史 attempt。
- **数学修订：**
  - 每个 base key 保存 `n_att`、`n_retry_used`、终身 `K_retry`、失败历史、reusable 引用和 terminal/exhausted 状态。
  - `K_remaining=max(0,K_retry−n_retry_used)`；首次之后所有执行均为 continuation/retry。
  - `C_inc^0` 只统计 `n_att=0` 的 key；`C_need` 是仍需至少一次执行的活跃缺失 key 数；`C_cap` 按各 key 当前剩余 allowance 求和。
  - `TERMINAL/EXHAUSTED` 且无可复用结果时不得重新执行。
- **37 号位置：** §3.3–3.4；`BASE_LEDGER_STATE`、`INCREMENTAL_COST`、`OBSERVE_FOUR_CELL_DESIGN`、`GENERATE_MODEL_FANTASY`。
- **伪代码闭合：** 真实与 fantasy 使用同一状态快照和状态转移；每次 attempt 及 reusable/retryable/terminal/exhausted 转移均原子持久化。预算不足只压缩剩余 allowance，不重置历史。
- **可检查边界：** `K_retry=2` 时，首轮 initial+一次 retry 后下轮仅剩一次；再次失败后永久 `EXHAUSTED`。已有历史 key 的 `C_inc^0=0` 但 `C_need=1`。全部缓存命中才可为零新增信息。
- **仍 OPEN：** 多轮同 key 自动反例、崩溃点审计、失败预测与实际资源偏差均未执行。

### R4 — Practical-information 秩门与边际 GLMM Fisher

- **状态：** `PARTIAL（修订规格已处理）`；边际信息计算、draw-wise 分位数和门限校准 `OPEN`。
- **原缺陷：** `λ_min^+` 忽略目标子空间零方向；conditional/complete-data Fisher 与边际 estimand 不一致。
- **数学修订：**
  - 主信息来自第 4.1 节积分随机效应后的 `L_M^marg`：`I_M^marg(ν)=E[-∇² log L_M^marg]`。
  - 固定效应与 variance components/nuisance 分块，以 Schur 补形成 `I_eff`；每个 draw 先检查有限 PSD 与 `Row(I_bn)⊆Row(I_nn)`。
  - 对完整 `Row(G)` 的正交基 `U`，逐 posterior draw 计算 `I_target^(j)=U I_eff^(j) U^T`。
  - 主门要求每个使用的 draw 都满足 `rank_eps(I_target^(j))=r`，并要求 `Q_{α_I}[λ_min(I_target^(j))]≥λ_info`。
- **37 号位置：** §4.1、§5.5；`BASE_GATE`。
- **伪代码闭合：** 不再以平均矩阵或 `λ_min^+` 单独通过门禁。`G I_eff^†G^T` 仅在行空间/nuisance 条件满足时称为 Fisher/asymptotic covariance proxy；主要区间 `h` 明确为 objective-scale posterior 95% 区间宽度。
- **可检查边界：** `I_target=diag(100,0)` 且 `r=2` 必须失败。nuisance guard 失败时不得先计算 Schur 补再宣称通过。任一 draw 的零方向不能被 posterior 平均掩盖。
- **仍 OPEN：** 边际 Fisher 的数值求导/积分、Schur 近似、`alpha_I`、`lambda_info` 与区间门均未校准。

### R5 — FOS 支持覆盖率、正边密度与未知边

- **状态：** `PARTIAL（修订规格已处理）`；双门阈值、FOS 稳定性和下游收益 `OPEN`。
- **原缺陷：** 旧 `rho_AB=|selected|/(|A||B|)` 是正边密度，却被称为支持覆盖率，导致 known-zero 与 unknown 混淆。
- **数学修订：**
  - `n_support=n_++n_0`，`n_?=N_AB−n_support`。
  - `rho_support=n_support/N_AB`、`rho_+=n_+/N_AB`、`rho_?=n_?/N_AB`。
  - supported practical-null 的相似度为 0 并进入支持分母；`NOT_SELECTED/UNRESOLVED` 为 `NA` 并进入 unknown。
  - 平均相似度为 `sum_{E_+}w/n_support`；合并同时要求 `n_+>0`、支持覆盖门和独立的 positive-density 门。
- **37 号位置：** §7.3–7.5；`BUILD_MISSINGNESS_AWARE_FOS`。
- **伪代码闭合：** 保存 `E_+`、`E_0` 和未知边 ID；tie-break 依次使用 support coverage、positive density、对应计数和稳定 cluster key。入选边必须有严格正 `w`。
- **可检查边界：** 一条 selected 边加三个 unknown 与一条 selected 边加三个 known-zero 具有相同正边密度但不同支持覆盖率；后者平均相似度被 known-zero 稀释。无支持边时相似度为 `NA` 且不得合并。
- **仍 OPEN：** `rho_support,min`、`rho_+,min`、known-zero 稀释是否改善 mixing、FOS/GOM 收益均未验证。

### R6 — 双模型 fantasy 风险 coupling 与聚合比较

- **状态：** `PARTIAL（修订规格已处理）`；聚合规则选择、候选排序和校准 `OPEN`。
- **原缺陷：** 独立 fantasy 的 `E[max(R2,R3)]` 被误作 `max(E[R2],E[R3])`，额外惩罚模型内预测方差。
- **数学修订：**
  - 主规则：`\bar H_m=E_m[R^(r)(D^+)]+λ_cost E_m[C_inc]`，`A_wc=R^(r)(D)−max_m \bar H_m`。
  - 对照一：`F_mix=∑π_m \bar H_m`，`π` 预注册。
  - 对照二：`F_prod=E_prod[max_m R_m+λ_cost max_m C_m]`，只在明确的 product coupling 下成立，仅作诊断。
- **37 号位置：** §9.2–9.3；`GENERATE_MODEL_FANTASY`、`SCORE_CANDIDATE`。
- **伪代码闭合：** 两套 fantasy 使用同一不可变 `d.b`，各自生成、各自双重拟合并执行同一鲁棒决策；主规则分别估计模型期望。模型内跨候选使用 CRN，不强迫跨模型结果相同。返回 `F_mix/MCSE_mix` 与 `F_prod/MCSE_prod`。
- **可检查边界：** 独立且非退化时通常 `E[max R]≥max E[R]`，二者 MCSE 不得混用。若新增 shared-uniform coupling，必须另命名，不能仍称 product coupling。
- **仍 OPEN：** worst-expected 是否是研究所需而非过度/不足保守，三种规则的排序、成本和最终决策差异均需同 MC 预算比较。

### R7 — 活动图集合与权重的 generation/round 更新

- **状态：** `PARTIAL（修订规格已处理）`；权重敏感性和跨期风险比较协议 `OPEN`。
- **原缺陷：** “采样前冻结”没有说明是整个 run 还是单个 acquisition cycle，也没有说明新 parent 图如何进入。
- **数学修订：**
  - 第 `r` 周期使用 `R^(r)(D)=∑_{g∈G_act^(r)}ω_g^(r)R_g(D)`。
  - 集合与权重在该周期候选评分、fantasy 和新结果之前固定；主默认等权，非等权只能来自 outcome-free 预注册元数据。
  - 新图/旧图仅在周期边界进入/退出；当前与 fantasy 始终共用同一集合和权重。
- **37 号位置：** §8.4；`START_ACQUISITION_CYCLE`、`DECIDE_ALL_GRAPHS`、主控制流。
- **伪代码闭合：** 切换时更新并绑定 `cycle_id`，立即令旧 `assessment/decision=NULL`；所有决策返回携带 cycle ID。最终输出检查状态与 cycle ID，失败时只保留归档，不向新图套用旧决策。
- **可检查边界：** 新图进入后预算恰好耗尽，不得输出与新活动图不匹配的旧 FOS。空活动图或非正/非有限权重必须 fail cycle。不同周期风险不得直接作为同集合下降解释；跨期报告须用固定 reference set/weights 重算。
- **仍 OPEN：** 集合更新频率、权重敏感性、固定 reference 的可比性及全局/online FDR 均未建立。

---

## 3. B1–B12 状态承接

以下状态只承接 36 号独立审查并记录本次修订，不表示作者自行关闭任何审查项。

| 项目 | 本轮相关修订 | 当前状态 | 仍 OPEN 的核心事项 |
|---|---|---|---|
| B1 | 保留 objective-scale estimand 与 q/w 分工；严格正 FOS 权重 | PARTIAL | 权重理论/经验优势、FOS/GOM 收益 |
| B2 | R1 鲁棒风险；模型内 provisional 与最终集合分离 | PARTIAL | 高阶判据、鲁棒校准、优化证书 |
| B3 | R1/R2/R6/R7 共同重写风险与 acquisition | PARTIAL | MC 校准、风险聚合、主动设计收益 |
| B4 | 保留四格 task-block GLMM；R3 统一 fantasy/retry 状态 | PARTIAL | 随机效应适用性、真实 posterior 校准 |
| B5 | R4 统一边际 nuisance/Fisher 口径；Beta 使用 `logκ` 参数化 | PARTIAL | 先验数值、边际计算和近似精度 |
| B6 | R4 完整 target rank、draw-wise `λ_min`、nuisance guard | PARTIAL | 精确认证、数值门限和状态准确率 |
| B7 | R7 明确周期集合/权重；per-graph 包络 BFDR 不扩张为全局 | PARTIAL | 跨图错误率、权重更新与跨期可比性 |
| B8 | R3 持久 retry/continuation 与 `C0/Cneed/Ccap` | PARTIAL | 多轮反例、实际成本与崩溃审计 |
| B9 | 保留非线性 invariance；R4 不替代结构认证 | PARTIAL | 完整 GLMM 可审计认证工具 |
| B10 | R3/R6 明确四格 fantasy 的状态和 coupling | PARTIAL | 条件预测、失败/重试模型和候选排序 |
| B11 | R5 三类密度和 known-zero 支持进入 builder | PARTIAL | 双门校准、FOS 结构和 EC 搜索收益 |
| B12 | 保留 prior-predictive、null calibration 与 sensitivity | PARTIAL | 所有实际校准仍未执行 |

---

## 4. 跨公式、状态机与主控制流一致性

| 链路 | 修订后必须保持的不变量 |
|---|---|
| `q_model/local_null_model → provisional` | 只用于模型敏感性；空前缀和空集合合法，不与最终集合混称 |
| `q_env/local_null_env → feasible sets` | 只作保守约束与资格，不进入 posterior FP/FN 损失 |
| `L_M → L_rob → R_g` | 每项使用同一 `(g,e,M)` 映射；风险对应实际所选集合；无证书则 NA |
| `fantasy → robust refit → H_m` | 每个生成模型独立产生数据，双重拟合后使用同一鲁棒决策与 cycle 权重 |
| `H_m/MCSE → A_L/A_U → stop/select` | 点估计不决定非正停止；执行需正下界；不确定则 abstain |
| `persistent ledger → plan/fantasy/observe` | 同一 base key 终身扣减 retry；历史 attempt 永不在新轮重置 |
| `marginal GLMM Fisher → target rank/quantile` | 不用 complete-data Fisher、正部最小特征值或平均矩阵绕过零方向 |
| `edge class → coverage/density/unknown → FOS` | known-zero 是有支持零边；NOT_SELECTED/UNRESOLVED 是 NA，不填零 |
| `cycle registry → active set/weights → decision output` | 周期内不变；切换使旧 assessment/decision 失效；不跨期误比风险 |

---

## 5. 起草过程复核及其边界

37 号在起草过程中进行了规格符合性与文档质量复核。复核促使修正了 provisional 输入绑定、边际 Fisher nuisance guard、 posterior 区间定义、FOS `q_env` 接口、cycle 切换旧快照失效、显式模型/图映射、空集决策、fantasy 非 OK 传播和最终 FOS 权重绑定。

这些复核只用于提高修订稿的可读性和内部一致性，**不是新的 R2 独立复审**，不替代数学证明、统计校准、算法实现或实验，也不关闭上述 OPEN 项。

---

## 6. 下一步 R2 独立复审要求

新的独立审查会话必须核验远端 main，并读取 33、34、36、37、38 号及 31、32、35 号历史约束。至少检查：

1. R1 的鲁棒可行集合、每模型损失、最终风险与集合优化是否正确且可认证；
2. R2 的区间方向、MCSE、alpha-spending、单候选与 `S_max` 停止是否一致；
3. R3 多轮同 base key 的 initial/retry/continuation/terminal/exhausted 是否无重置或漏计；
4. R4 边际 GLMM Fisher、Schur 条件、完整 rank、draw-wise 分位数和 posterior 区间是否兼容；
5. R5 三类密度、known-zero/unknown 与 builder 更新是否一致；
6. R6 worst-expected/model-average/product coupling 的概率含义、CRN 和 MCSE 是否分离；
7. R7 活动图集合、权重、cycle ID 和旧快照失效是否闭合；
8. 所有未校准项是否仍为 OPEN，且没有把规格完整误写为算法或创新验证通过。

**当前结论：Revision R1 草稿与矩阵已形成；TCAIL 继续 HOLD / IMPLEMENTATION BLOCKED。下一步只能由不同会话进行 R2 独立复审。**
