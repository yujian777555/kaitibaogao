# 39 — TCAIL V2.2 Revision R1 独立规格复审 R2

**日期：** 2026-11-04  
**审查对象：** 37_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R1.md、38_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R1.md  
**审查基线：** 4f15ac303936817cc2bf122e649fff2331c9b1dc  
**审查范围：** R1–R7 数学/统计定义、成本账本、FOS 语义、主伪代码和跨章节一致性  
**结论：** **REQUEST CHANGES / HOLD / IMPLEMENTATION BLOCKED**

> 本轮是对 37/38 号的独立复审，不是实现或实验报告。R1 的若干修订确实解决了 36 号报告中的原始概念问题，但仍有影响停止决策、预算可信度和 FOS 语义的实质缺口。所有未校准事项继续 OPEN。

## 1. 远端基线与审查范围

审查前核验：
- 仓库：yujian777555/kaitibaogao
- 分支：main
- 远端 HEAD：4f15ac303936817cc2bf122e649fff2331c9b1dc
- 37 号规格：2,320 行
- 38 号矩阵：193 行
- 对照读取：33、34、36 号历史规格/复审，README、05_DECISION_LOG、SESSION_HANDOFF 和 REPOSITORY_MAINTENANCE_POLICY。

本轮检查覆盖了 objective-scale estimand、task-block GLMM、base-key retry、marginal Fisher、M2/M3 provisional 与 robust decision、BFDR 可行集合、worst-expected acquisition、MCSE/alpha spending、FOS builder 和 cycle 控制流。

## 2. 总体判断

**R1 有实质性进步，但 R2 不予通过。**

已经正确修正的部分：
1. **鲁棒风险语义：** 37 号明确把 ell_env/q_env 限定为保守可行性约束；各模型的 FP/FN loss 使用该模型自己的 ell/q，再最小化 max_M L_M。这个定义在数学上自洽，不再把 max-null/min-q 组合误称为某个模型的 posterior expected loss。
2. **鲁棒集合优化：** 37 §8.2–8.3 不再假定 ell_env 排序前缀是 max_M L_M 的最优解，并要求精确枚举或可审计最优性证书。方向正确，求解规模和证书仍 OPEN。
3. **Fantasy 风险聚合：** 37 §9.2 将主目标改为 max_m E_m[H]，将 product-coupled E[max] 与 model-average 单独列为诊断。该区分正确。
4. **Fisher 主口径：** 37 §5.5 改为边际 GLMM expected Fisher、完整 target rank 和 draw-wise lambda_min 分位数，避免了旧版 lambda_min+ 忽略零方向的问题。
5. **活动图周期：** 37 §8.4/§10.6 明确周期内冻结、周期边界切换、旧 decision 失效，解决了旧版活动图时间尺度缺失的大部分问题。

但下列问题仍要求修订：

| ID | 严重性 | 对应项 | 独立结论 |
|---|---|---|---|
| R2-A | BLOCKER | B3/B10：当前基准风险 MC 误差 | acquisition 的 A_L/A_U 把 R(D) 当作精确常数，但它由 posterior MC 和鲁棒集合优化得到，误差没有进入区间 |
| R2-B | BLOCKER | B3：多模型/多候选 alpha allocation | sign allocation 未分配两个生成模型；rank allocation 没有给出对全部 rival comparisons 的明确分配公式 |
| R2-C | MAJOR | B3/B10：MCSE 的独立性与嵌套误差 | sd/sqrt(S) 仅在相应样本近似 IID 时成立；posterior draws 的自相关、内层 posterior-fit MCSE 和 quadrature error 没有接入主区间 |
| R3-A | BLOCKER | B8：REUSABLE 状态与 cache miss | ledger 状态为 REUSABLE 但 cache 未命中时，规划器仍安排 continuation；执行器随后直接 BREAK，却可能返回 OK，存在漏观测/错误成功路径 |
| R3-B | MAJOR | B8：attempt 的 crash-consistency | 没有明确持久化 RESERVED/IN_FLIGHT/UNKNOWN_OUTCOME 状态；外部执行后、n_att 更新前崩溃可能造成 attempt 号复用或成本账不一致 |
| R4-A | MAJOR | B6：Fisher 参数向量 | nu 的 nuisance 描述含“离散参数”，但 expected Fisher 使用对 nu 的 Hessian；离散参数不能直接按普通连续参数求导 |
| R5-A | BLOCKER | B11：NOT_SELECTED 被算作 unknown | Q_g 中的 NOT_SELECTED 已通过基础支持/信息/模型门，却被排除在 rho_support 并计入 rho_unknown；当前 rho_support 不是一般意义的数据支持覆盖率 |
| R6-A | MAJOR/OPEN | B3/B10：paired MCSE 的 CRN 对应 | paired difference 需要明确跨候选共用的随机变量映射；当前表键/伪代码仍不足以完全复现该配对 |
| R7-A | MINOR | B7：generation 与 acquisition cycle 记号 | r 同时表示 graph generation/RSI round 和 acquisition cycle，需分开记号，避免图身份与风险快照混淆 |

## 3. 具体复审发现

### R2-A — A_L/A_U 漏掉当前基准风险 R(D) 的 Monte Carlo 不确定性

**位置：** 37 §6.2、§8.3–8.4、§9.3、§10.3–10.4。

当前 acquisition 定义：
\[
A_{\mathrm{wc}}(d)=R^{(r)}(D)-\max_m E_m[H_m(d)].
\]

37 §9.3 对未来模型目标 H_m 构造 MCSE，并定义 A_U/A_L；但公式和 §10.4 伪代码都把当前的 current_decision.total_risk / R^(r)(D) 当作精确常数。

问题在于 R^(r)(D) 并非已知常数：
- q_model、ell_model、方向概率和其他 posterior functional 来自有限 posterior draws；
- §6.2 要求 posterior functional 同时报告 MCSE；
- §8.3 的 robust loss 由这些估计量构成，并经过可行集合筛选、max_M 和集合优化；
- §10.3 的 DECIDE_ALL_GRAPHS 只返回 total_risk，没有返回其 MCSE、数值区间或 solver-gap 传播结果。

因此，即使未来 H_m 的区间正确，A_L/A_U 仍不是完整 acquisition gain 的区间。若 R(D) 被高估，可能错误满足 A_L>0；若被低估，也可能错误 STOP_NONPOSITIVE。

**要求：**
1. 明确给出当前风险区间 R_L(D), R_U(D)，或提供可审计的精确积分/误差证书，证明当前风险可视为确定值。
2. 在模型目标区间 H_{m,L}, H_{m,U} 有同时覆盖保证时，至少采用方向正确的组合：
\[
A_L(d)=R_L(D)-\max_m H_{m,U}(d),
\qquad
A_U(d)=R_U(D)-\max_m H_{m,L}(d).
\]
3. 若当前风险与未来 fantasy 共用 posterior draws 或其他随机流，明确协方差/配对处理；否则使用同时有效的保守区间。
4. 将 posterior integration error、quadrature error、robust optimizer optimality gap 和近似求解误差纳入数值余量，不能只在 H_m 一侧加 epsilon。
5. 当前风险的集合选择本身可能随 q/ell MC 误差变化；必须说明如何处理可行集合变化和 argmin 不稳定，而不是只对固定 S 的风险值计算标准误。

此项直接影响停止和执行资格，B3/B10 暂不能通过。

### R2-B — alpha spending 没有完整覆盖两个模型和所有候选比较

**位置：** 37 §9.3–9.4、§10.4。

符号查看公式为
\[
\alpha_{\mathrm{sign},j,d}
=\frac{\alpha_{\mathrm{sign}}}{N\zeta(2)j^2}.
\]
该式对 N 个候选和 j 次查看完成了分配，但每个 A_U/A_L 都依赖两个 model-specific 目标 H_2、H_3 的上下界。若每个模型都直接使用同一个 alpha_sign,j,d，则没有明确控制两模型联合覆盖误差。

此外，rank 部分只写“对全部预注册 pair/rival 使用同一 j^-2 alpha-spending 和 alpha_rank”，没有给出：
- 候选数 N；
- 有序或无序 rival pair 数；
- 两个模型均值区间的分配；
- 每个 look 的具体 alpha 和 z_rank；
- PRE_REGISTERED_MC_Z 的完整定义。

因此无法从规格核验整体 family-wise MC error 是否受 alpha_MC 控制。

**要求：**
- 明确将 sign alpha 分配到候选、生成模型和 look；例如可采用按 2 个模型、N 个候选和 zeta(2)j² 归一化的 Bonferroni 方案，或给出有证明的 max-statistic simultaneous bound。
- rank alpha 必须明确分配到全部候选/rival 比较和 look；如果使用候选级 simultaneous intervals，也必须说明两个模型及两侧边界的覆盖分配。
- 明确 PRE_REGISTERED_MC_Z 的输入、alpha table、单侧/双侧定义和失败处理。
- 证明所有符号、排名和重复查看使用的误差预算总和不超过预注册 alpha_MC。

不要求一定采用 Bonferroni，但必须给出可以复核的完整分配和覆盖论证。

### R2-C — MCSE 公式需要处理自相关和嵌套估计误差

**位置：** 37 §9.3、§11.4、§10.4。

当前使用
\[
\operatorname{MCSE}_{H,m,S}
=\operatorname{sd}(H_{m,1:S})/\sqrt S.
\]

该公式以 fantasy 索引上的样本近似 IID 为前提。规格使用 joint posterior draws，但没有冻结这些 draws 是独立抽样还是 MCMC 链输出。若存在自相关，简单 sd/sqrt(S) 可能低估标准误。

另外，每个 fantasy 的 future_decision 还包含内层 posterior fitting、posterior functional 估计和数值积分。当前没有明确区分：
- outer fantasy sampling variance；
- inner posterior Monte Carlo error；
- quadrature/likelihood approximation error；
- robust optimization solver gap。

**要求：**
1. 明确 posterior/fantasy draws 的独立性条件；若使用 MCMC，使用 batch means、谱方差、ESS-adjusted MCSE 或其他可审计的 long-run variance 估计。
2. 给出 nested MCSE 的误差分解，或明确将内层误差压到预注册 tolerance 并纳入 epsilon_sign/epsilon_select/epsilon_rank。
3. 对自适应增加 S 和复用旧 fantasy 的过程，说明每次查看的 MCSE 估计如何保持有效。
4. 将这些作为 OPEN 校准，不得仅凭文档公式宣称区间已具备覆盖保证。

### R3-A — REUSABLE ledger 状态在 cache miss 时存在不一致执行路径

**位置：** 37 §3.4、§10.1 的 BASE_LEDGER_STATE、INCREMENTAL_COST、OBSERVE_FOUR_CELL_DESIGN。

当前 INCREMENTAL_COST 的顺序是：
1. FIND_REUSABLE 未命中；
2. 读取 base ledger state；
3. 只把 TERMINAL/EXHAUSTED 当作 terminal missing；
4. 若 n_att>0，就按 RETRY_CONTINUATION 规划 K_remaining 次执行。

但 status=REUSABLE 没有被单独处理。随后 OBSERVE_FOUR_CELL_DESIGN 的循环又规定：
\[
\text{if status in \{REUSABLE,TERMINAL,EXHAUSTED\}: BREAK}.
\]

因此存在以下可复现的状态组合：
- ledger 对 K0 记录 status=REUSABLE；
- cache 中的结果丢失、损坏或未能通过完整性校验；
- FIND_REUSABLE 返回 NONE；
- INCREMENTAL_COST 却把它当作 retry continuation 并计入 C_need/C_cap；
- OBSERVE 遇到 REUSABLE 后立即 BREAK，不执行 attempt；
- 外层仍可能返回 OBSERVATION(status=OK)，造成该 cell 没有结果却被当成正常完成。

**要求：**
- REUSABLE 必须要求存在与 reusable_attempt 一致且完整性验证通过的结果；
- 若 ledger 指向 REUSABLE 但 cache miss，必须从不可变 attempt record 安全重建，或返回专门的 LEDGER_CACHE_INCONSISTENT 并 fail-closed；
- 不得把 REUSABLE 状态降级成 retryable；
- 只有四格所有 cell 均有有效 observation 或明确合法的 unresolved status 时，OBSERVE 才能返回 OK；
- 增加 REUSABLE + cache miss/corruption 的边界测试。

### R3-B — attempt reservation 和 crash recovery 尚未形成完整状态机

**位置：** 37 §3.4、§10.1。

伪代码在执行前写“reserve and charge one unique new episode-equivalent”，但 n_att、n_retry_used、attempt record 和 status 的正式更新发生在外部执行结果返回之后。没有明确定义 durable reservation 必须先于外部 side effect 写入，也没有 IN_FLIGHT/UNKNOWN_OUTCOME 状态。

如果进程在外部执行已发生、但结果/ledger finalization 尚未写入时崩溃，下一次恢复可能：
- 仍看到旧 n_att；
- 重新分配同一个 attempt number/seed；
- 重复执行一个实际已消耗资源的 episode；
- 使 retry allowance 和实际成本账不一致。

**要求：**
- 在外部调用前原子持久化 attempt reservation、attempt ID、成本预留和 IN_FLIGHT 状态；
- 恢复时先 reconciliation：能查询外部状态则核对；不能核对则转 UNKNOWN_OUTCOME 并按保守成本/额度处理；
- attempt ID 必须不可重用；
- 明确哪些失败能 retry、哪些未知结果必须停止；
- 38 号已把 crash recovery 标为 OPEN，应继续 OPEN，不能在 37 号把该链路描述为已 crash-safe。

### R4-A — Fisher Hessian 的参数向量含离散 nuisance 歧义

**位置：** 37 §5.5。

该节写明 nuisance 向量包含“其他离散/收缩/likelihood 参数”，同时定义
\[
I_M^{marg}(\nu_M)
=E[-\nabla_{\nu_M}^2\log L_M^{marg}(Y\mid\nu_M)].
\]

普通 Hessian/Fisher 对连续可微参数定义。若“离散参数”指离散模型指示、离散潜变量或离散超参数，不能直接纳入同一个普通梯度向量。

**要求：**
- 明确 Fisher differentiation vector 只包含连续、可微参数；
- M2/M3 模型指标保持分模型处理；
- 离散潜变量/离散 nuisance 必须先求和/积分边际化，或对每个离散状态分别计算 Fisher 后再按预注册规则处理；
- 说明 variance-component 边界和非正则点如何处理。

其余边际 GLMM Fisher、完整 target rank、draw-wise lambda_min 低分位和 Fisher/asymptotic covariance proxy 的方向正确；具体数值与 coverage 继续 OPEN。

### R5-A — NOT_SELECTED 并非 unknown，当前 support coverage 定义不成立

**位置：** 37 §7.3–7.4、§8.1–8.3、§10.5。

这是本轮 FOS 最重要的语义问题。

§8.1 定义
\[
Q_g=\{e:\ e\text{ 为 DECISION\_ELIGIBLE，且两模型基础门通过}\}.
\]
所以 Q_g 中每条边都已经通过支持、结构、信息、模型阶数和高阶资格门。

但 §7.3 把最终集合之外、且不属于 practical-null 的边标为 NOT_SELECTED；它们属于 Q_g\\S_g。此类边只是没有进入最终鲁棒 BFDR 集合，可能是单边资格不足，也可能是集合级 BFDR/风险优化没有选它们。它们不是“没有数据支持”或“未知是否支持”。

当前 §7.4 又定义
\[
n_{\mathrm{support}}=n_++n_0,\qquad
n_?=N_{AB}-n_{\mathrm{support}},
\]
并明确把 NOT_SELECTED 和 UNRESOLVED 都放进 n_?。这导致 rho_support 低估已经通过基础门的 pair，rho_unknown 则高估真正缺乏支持的 pair。

**可检查反例：** 一个 cluster pair 有 4 个 cross-pairs，四条边全部属于 Q_g，即四条都通过基础支持/信息门；其中没有任何边进入 S_g，且 q_env 均大于 tau_zero。按当前分类，四条边全部为 NOT_SELECTED，故 n_support=0、rho_support=0、rho_unknown=1。数据支持事实上为 100%，当前指标却报告为 0%。

**要求：**
1. 至少区分四类：SELECTED_SUPPORTED、SUPPORTED_PRACTICAL_NULL、SUPPORTED_NOT_SELECTED（或等价状态）、UNRESOLVED。
2. 分别定义真正的数据/结构支持覆盖率与“相似度已解析覆盖率”；不要把二者都叫 rho_support。
3. NOT_SELECTED 可继续在相似度矩阵中记 NA，不能自动赋零；但它必须与 UNRESOLVED 分开计数，不能被称为无数据支持。
4. 给出 builder 对这四类的精确 merge gate：哪些计入 data support，哪些计入 similarity-resolved denominator，哪些保持 NA。
5. 增加上面的四边反例，以及“全部 eligible 但 BFDR set 未选中”测试。

否则 R5 的核心目标仍未完成，B11 不通过。

### R6-A — Worst-expected 聚合已修正，但 paired MCSE 需要固定 CRN 映射

**位置：** 37 §9.2–9.3、§10.4。

主目标
\[
A_{\mathrm{wc}}=R(D)-\max_m E_m[H_m]
\]
与 product-coupled envelope 的数学区别现在写清楚，主规则不再混用两者；这一修订接受为正确方向。

但 §9.3 的
\[
\operatorname{MCSE}_{\Delta H,m,d,d'}
=\operatorname{sd}_s(H_{m,s}(d)-H_{m,s}(d'))/\sqrt S
\]
要求同一模型下候选 d 与 d' 的第 s 个样本由明确共同随机数映射配对。当前文字声称同模型跨候选复用 CRN，但伪代码的 posterior_predictive 索引又包含 d，未把底层 uniform stream、task/block effects、protocol-failure stream 与 candidate transform 的对应关系完整写出。

**要求：**
- 定义底层共享随机表的键和映射；区分 posterior parameter draws、task/block random effects、Bernoulli uniforms、protocol failures/retries；
- 若某类变量不能跨候选共享，则对该部分使用独立方差估计，不得套用 paired MCSE；
- paired MCSE 未定义前保持 OPEN。worst-expected 主目标的数学定义本身可保留。

### R7-A — generation index 与 acquisition-cycle index 重名

**位置：** 37 §1.2、§8.4、§10.6。

§1.2 用 r 表示 graph 的 generation/RSI round，graph key 为 g=(r,parent_id,a)；§8.4 又用 R^(r)、G_act^(r)、omega^(r) 表示 acquisition cycle。§10.6 实际使用 cycle_id，说明两者并非必然同一索引。

**要求：**
- graph generation/RSI round 使用独立符号，例如 g=(generation,parent_id,anchor)；
- acquisition cycle 使用 c，统一写 G_act^(c)、omega^(c)、R^(c)、cycle_id=c；
- 明确一个 generation 是否可有多个 acquisition cycles，以及 parent/anchor graph 的进入/退出事件如何触发新 cycle。
- 这主要是符号/接口闭合问题，不推翻 §8.4 的周期冻结原则。

## 4. R1–R7 独立状态

| 项目 | R2 独立复审状态 | 判断 |
|---|---|---|
| R1 | PARTIAL | 鲁棒 posterior loss 与 envelope 分工正确；精确优化证书和实际 regret 校准 OPEN |
| R2 | REQUEST CHANGES | 基准风险 MCSE、模型/候选 alpha allocation 和 nested MCSE 未闭合 |
| R3 | REQUEST CHANGES | REUSABLE/cache miss 路径和 crash-consistent reservation 未闭合 |
| R4 | PARTIAL | 完整 target rank 与边际 Fisher 方向正确；连续参数向量需澄清 |
| R5 | REQUEST CHANGES | NOT_SELECTED 与真正 unknown 混淆，rho_support 仍不成立 |
| R6 | PARTIAL | worst-expected 主目标定义正确；paired CRN 映射未完全冻结 |
| R7 | PARTIAL | 周期冻结逻辑正确；generation/cycle index 冲突待修 |

## 5. B1–B12 状态

| 项目 | R2 状态 | 仍 OPEN / 阻塞内容 |
|---|---|---|
| B1 | PARTIAL | w 作为 FOS similarity 的优势、同预算 GOM 收益 |
| B2 | PARTIAL | M2/M3 鲁棒校准、高阶范围和 solver certificate |
| B3 | REQUEST CHANGES | 当前风险误差、MC 区间和 alpha family control |
| B4 | PARTIAL | GLMM 随机效应适用性与真实 posterior calibration |
| B5 | PARTIAL | 先验数值、边际 nuisance 计算和近似精度 |
| B6 | PARTIAL | Fisher 连续参数定义、精确认证和阈值校准 |
| B7 | PARTIAL | 跨图 global/online FDR 不主张；周期权重敏感性 OPEN |
| B8 | REQUEST CHANGES | REUSABLE/cache 状态一致性和 crash-safe attempt ledger |
| B9 | PARTIAL | 完整 GLMM estimand-invariance 认证工具 |
| B10 | REQUEST CHANGES | acquisition sign interval 与嵌套 MCSE |
| B11 | REQUEST CHANGES | NOT_SELECTED/support/unknown 分离仍未完成 |
| B12 | PARTIAL | prior sensitivity、null calibration 尚未运行 |

## 6. 本轮没有通过的事项

- 未批准 37/38 号整体规格。
- 未批准 TCAIL 独立创新性或 EC 核心贡献。
- 未批准算法实现、Phase 0 或任何真实 Agent 评价。
- 未调用真实 LLM API，未训练模型。
- 未启动 CI-GOM 或 IMCE-RSI。
- 未运行算法性能实验、posterior calibration 或 FOS/GOM 下游实验。

TCAIL 继续 **HOLD / IMPLEMENTATION BLOCKED**。R1–R7 的修订规格仍不等于数学/统计 PASS，所有校准和实验仍 OPEN。

## 7. 下一步唯一任务

只进行 **TCAIL V2.2 corrective specification revision R2**，不编码、不实验。保留 37/38/39 号历史文件，不覆盖。

建议新增：
1. 40_TCAIL_FORMAL_SPECIFICATION_V2_2_REVISION_R2.md
2. 41_TCAIL_V2_2_REVISION_CHANGELOG_AND_CLOSURE_MATRIX_R2.md

必须先修复 R2-A/B/C、R3-A/B、R4-A、R5-A；R6-A/R7-A 明确处理。修订后交不同会话进行下一轮独立复审。具体接班提示词见 SESSION_HANDOFF.md 新增章节。
