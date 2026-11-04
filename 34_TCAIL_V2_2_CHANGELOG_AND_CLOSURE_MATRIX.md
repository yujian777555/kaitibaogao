# 34 — TCAIL V2.2 变更日志与 B1–B12 闭合矩阵

**日期：** 2026-11-04

**状态：** DRAFT CHANGELOG / PENDING INDEPENDENT REVIEW / HOLD / IMPLEMENTATION BLOCKED

**唯一仓库：** `yujian777555/kaitibaogao`

**对应规格：** `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md`

**需求来源：** `20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md`、`31_TCAIL_LINKAGE_INTERFACE_INDEPENDENT_REVIEW_R2.md`、`32_TCAIL_V2_2_SPEC_REVISION_TASK_R1.md`、`35_TCAIL_V2_2_PLANNER_ADDENDUM_R1.md`

> 本矩阵记录规格草稿如何处理 B1–B12，不是独立数学复审报告。`PARTIAL` 仅表示已有明确规格条款；它不等于独立审查通过、校准完成、算法实现、实验成功或创新成立。所有尚需证明、校准、复现或实验的事项均保留为 `OPEN`。

---

## 1. 版本关系与变更范围

V2.2 是新建的完整草稿，不覆盖 `17_TCAIL_FORMAL_SPECIFICATION_V2.md`，也不改写 20、22、31、32、35 号历史结论。17 号 V2.1 仍是历史权威规格；33 号只有在后续独立审查通过后，才可讨论是否晋升。

本轮只变更数学、统计、观测、决策、FOS 接口和实验规格。没有编写 TCAIL/CI-GOM 算法实现，没有启动 Phase 0，没有调用 DeepSeek 或其他真实 LLM API，没有训练模型，没有启动 CI-GOM 或 IMCE-RSI。

### 1.1 状态词定义

| 标记 | 本文件中的严格含义 |
|---|---|
| `PARTIAL（规格已处理）` | 已有完整定义和跨章节接口，但作者不据此自行宣布数学或研究 `PASS` |
| `OPEN` | 尚需独立审查、数值校准、原论文复现、实现验证或实验；不得以文字完整替代证据 |
| `NOT ESTABLISHED` | 当前没有足够证据支持新颖性、EC 收益或论文贡献结论 |

---

## 2. 相对 V2.1 的主要变更日志

| 变更 | V2.1 的风险 | V2.2 草稿处理 | 33 号位置 |
|---|---|---|---|
| 局部 linkage estimand | 平均有符号 link-scale contrast 可能抵消，不等于局部 linkage | 主对象改为 graph-specific、objective-scale 四格差分；global RMS 只作摘要 | §2.1–2.3 |
| Evidence 与聚类强度 | `q` 同时承担边证据和连续权重的风险 | `q` 用于证据、资格和边决策，但不直接作连续 FOS 权重；主权重为 posterior expected excess magnitude | §2.3、§6.4、§7.1–7.2 |
| Task-block 观测 | 标量 observation 与配对/replicate 层级不完整 | 固定四格向量、block/task 嵌套、三类预测路径和显式执行状态 | §3.1–3.3、§4.1–4.2、§9.1 |
| 主统计模型 | 任务内相关没有进入明确 likelihood | 主分析使用带 task/block 随机截距的 Bernoulli GLMM，目标估计积分任务与随机效应 | §4.1 |
| Nuisance | 未知 Beta/Gaussian 参数可能被点估计替代 | 次级模型使用 nuisance prior、联合后验、有效 Fisher 和 acquisition 积分 | §4.4–4.5、§5.5 |
| 非线性可识别性 | 线性 row-space 被误用于 probability-scale estimand 的风险 | 四 cell 行分别可识别作为充分条件；另定义 observationally-equivalent 参数下的 estimand-invariance | §5.1–5.3 |
| 实际识别与支持 | 代数满秩、共同支持和弱信息可能混淆 | 分离结构、局部合法/零支持、matched-task 数、effective information、conditioning 和区间门 | §5.4–5.6 |
| 双模型状态 | 单模型状态和 M2/M3 联合敏感状态可能冲突 | 明确 `BASE_GATE`、`SUMMARIZE_EDGE_STATE`、结构冲突、可采样缺口和双通过后的模型阶数审查 | §5.6、§6.3、§10.2 |
| 高阶失配 | M3 一致无法排除四阶以上项 | 增加纯四阶、混合阶、五阶以上、非均匀/受约束投影压力场景及 abstention | §0.3、§6.6、§12.3 |
| 最终边集 | 独立逐边风险与 BFDR 集合决策不一致 | 最终规则为带单边缘证据资格的 per-graph BFDR-constrained set loss；acquisition 重用同一规则 | §8、§9 |
| Fantasy 预测 | M2/M3 生成哪个未来观测未定义 | 两个 model-specific fantasy 分别生成并双重拟合；逐索引 max-risk/max-cost 包络 | §9.2–9.3、§10.4 |
| FOS 缺失处理 | unsupported edge 若填零会被误作独立 | missingness-aware weighted average-linkage；仅支持边进入更新，保留 forest/singleton fallback | §7.3–7.5、§10.5 |
| 预算 | pair 或缓存复用可能重复计费 | 以 base key/attempt key 区分复用和新执行；只计唯一新增 episode，显式纳入重试和剩余预算 | §3.4–3.5、§9.4、§10.1 |
| 先验与 null | 单一 prior 下高 `q` 可能被误作确认 | 增加 prior-predictive、SBC/coverage、null/additive 校准和 prior-scale sensitivity | §11 |
| 强基线 | 弱基线无法排除 FBL/cDLED 等直接先例 | 纳入全部指定强基线，并区分 original reproduction、adaptation、common/native builder | §13 |

---

## 3. B1–B12 逐项闭合矩阵

### B1 — 条件 interaction 到 local fitness linkage

- **草稿状态：** `PARTIAL（规格已处理）`；权重选择、校准和下游 EC 价值 `OPEN`。
- **规格位置：** 33 号 §1.2、§2.1–2.3、§6.4、§7.1–7.3；伪代码 `FIT_AND_ASSESS`、`BUILD_MISSINGNESS_AWARE_FOS`。
- **核心公式：** 局部 objective-scale `\Delta_{g,e}`；`q=P(|\Delta|>\delta_{\mathrm{local}}\mid D)`；`w=E[(|\Delta|-\delta_{\mathrm{local}})_+\mid D]`；global `S` 仅作描述/筛查/预算优先级，`M/V` 为描述摘要。
- **闭合动作：** `q` 不直接作为 FOS 连续权重；`\delta_{\mathrm{local}}`、`\tau_{\mathrm{edge}}`、`q_{\mathrm{BFDR}}` 和 `\lambda_{\mathrm{cost}}` 分离；负交互可入选，方向概率另报。
- **仍未解决：** `w` 相对其他权重的优势、实际阈值、FOS/GOM 增益均为 `OPEN`。

### B2 — M2/M3、高阶和 heredity

- **草稿状态：** `PARTIAL（规格已处理）`；保守合并校准和四阶以上验证 `OPEN`。
- **规格位置：** 33 号 §0.3、§4.3、§5.6、§6.1–6.6；伪代码 `SUMMARIZE_EDGE_STATE`、`FIT_AND_ASSESS`、主控制流。
- **核心规则：** 低阶父项保留在 basis 中，但不要求父系数非零；仅双 `BASE_PASS` 后比较方向、效应、`q/w` 和 provisional BFDR 集合；不一致则 `MODEL_ORDER_SENSITIVE` 并 abstain；若同时触发高阶诊断失败，则以 `HIGH_ORDER_UNCERTIFIED` 优先。
- **最终 posterior 接口：** 主候选为 max-local-null/min-`q`/min-`w`；没有按有利结果选择 M2 或 M3。
- **仍未解决：** max-null/min-weight 不自动保证校准；M2/M3 一致不排除四阶以上；压力测试和真实失效边界均为 `OPEN`。

### B3 — Acquisition 与最终 BFDR 决策一致

- **草稿状态：** `PARTIAL（规格已处理）`；数值近似、校准和相对 OED 的收益 `OPEN`。
- **规格位置：** 33 号 §8.1–8.4、§9.2–9.5；伪代码 `BFDR_CORE`、`DECIDE_ALL_GRAPHS`、`SCORE_CANDIDATE`。
- **核心公式：** 同一个 `BFDR_CORE` 决定当前和未来的 `S_g`；风险为实际所选近似最优可行前缀的损失加 unresolved 代价；`A(d)=R(D)-E[H_{d,s}\mid D,d]`。
- **闭合动作：** fantasy 后重拟合两模型、重跑所有门禁和同一集合决策；使用 MCSE、自适应样本数、计算层 CRN 和确定性平局。
- **仍未解决：** model-specific max-risk/max-cost 是候选保守规则，不是校准定理；per-edge 仅作 surrogate 对照；计算可行性与功效为 `OPEN`。

### B4 — Task-block 四格观测和相关模型

- **草稿状态：** `PARTIAL（规格已处理）`；真实任务分布、随机效应适配和 posterior 校准 `OPEN`。
- **规格位置：** 33 号 §3.1–3.2、§4.1–4.2、§9.1；伪代码 `CONSTRUCT_CANDIDATE`、`GENERATE_MODEL_FANTASY`、`OBSERVE_FOUR_CELL_DESIGN`。
- **核心定义：** `b=(block_id,t_b,protocol_id,v_protocol,s_b)`；`d=(g,e,b,n_rep)`；`Y_d=(Y_{++},Y_{+-},Y_{-+},Y_{--})`，每格保留嵌套 replicate。
- **闭合动作：** 四格同 block、随机执行顺序；task/block 随机截距进入 Bernoulli GLMM；task instance 是 cluster 单位；future block 只能来自冻结的 train/validation 分布。
- **仍未解决：** 真实 LLM 采样不能默认严格 CRN；随机效应充分性、block 分布和校准结果均为 `OPEN`。

### B5 — Beta/Gaussian nuisance uncertainty

- **草稿状态：** `PARTIAL（规格已处理）`；次级模型先验数值和近似精度 `OPEN`。
- **规格位置：** 33 号 §4.4–4.5、§5.5、§9.2。
- **核心规则：** 主分析固定为 Bernoulli；Beta 使用 `\log\kappa` prior，Gaussian 未知方差使用 `\log\sigma` prior；联合 posterior、posterior predictive 和 fantasy 均积分 nuisance。
- **信息计算：** 使用 joint-Fisher 分块和 nuisance-adjusted effective information，不能用点估计替代不确定性。
- **仍未解决：** 先验尺度、后验近似、联合信息数值稳定性和次级模型适用性均为 `OPEN`；精确 0/1 不静默 clipping。

### B6 — 结构、支持和 practical identifiability

- **草稿状态：** `PARTIAL（规格已处理）`；认证工具、门限和状态准确率 `OPEN`。
- **规格位置：** 33 号 §5.1–5.6；伪代码 `BASE_GATE`、`RESOLVABLE`、`SUMMARIZE_EDGE_STATE`。
- **核心规则：** 每个 `M×a` 分别构造 `X_legal/X_obs`；结构、非参数共同支持、当前观测支持、Fisher 信息和 posterior 区间分别判定。
- **状态动作：** 永久不可识别、结构未认证、局部零支持、可补支持、弱信息、模型冲突和可决策均有不同后续动作；`resolvable` 需要合法候选和剩余预算。
- **仍未解决：** `\lambda_info`、`\kappa_max`、`h_max`、`c_min`、`N_min` 等只能训练期校准；精确认证和实际信息有效性为 `OPEN`。

### B7 — BFDR family 和 graph 输出

- **草稿状态：** `PARTIAL（规格已处理）`；跨图 global/online FDR 明确 `OPEN` 且本版不作该主张。
- **规格位置：** 33 号 §1.2、§8.1–8.5；伪代码 `BFDR_CORE`、`DECIDE_ALL_GRAPHS`。
- **核心定义：** `g=(r,parent_id,a)`；每张图的 family 是该 graph 的预注册 pair 集合；只有 `DECISION_ELIGIBLE` 边进入运算，其余为 unresolved/abstain。
- **输出：** graph-indexed local VIG/FOS，不自动聚合成跨 parent/generation 单图。
- **仍未解决：** per-graph BFDR 依赖后验校准；不得推断跨图 global FDR。若未来需要全局声明，必须另立 error-budget、证明与校准，当前 `OPEN`。

### B8 — 唯一新增 episode-equivalent 预算

- **草稿状态：** `PARTIAL（规格已处理）`；真实失败/重试成本模型和资源审计 `OPEN`。
- **规格位置：** 33 号 §3.3–3.5、§9.2–9.4；伪代码 `BASE_REUSABLE_KEY`、`ATTEMPT_KEY`、`INCREMENTAL_COST`、`OBSERVE_FOUR_CELL_DESIGN`、主控制流。
- **核心规则：** base key 含 configuration、task、全局唯一 block、anchor、protocol、seed/replicate、模型/evaluator/objective/environment/cap 版本；attempt 另记。
- **成本：** 缓存命中零当期新增但保留历史成本；新 initial、失败、超限和 retry 均入账；acquisition 用期望总新增成本，执行用最大成本 cap 防超预算。
- **仍未解决：** `B_full` 按唯一 configuration×anchor×reference repeats，不按 pair 重复；tokens/tools/wall/currency 另报。实际协议等价性和重试预测偏差为 `OPEN`。

### B9 — Probability-scale nonlinear estimand 可识别性

- **草稿状态：** `PARTIAL（规格已处理）`；完整 GLMM 的可审计认证方法 `OPEN`。
- **规格位置：** 33 号 §5.1–5.3、§5.5；伪代码 `BASE_GATE` 中 `CERTIFY_NONLINEAR_ESTIMAND`。
- **充分条件：** 四个 cell 的固定效应设计行分别属于相应 row space，且所需 nuisance 可识别，则四个 predictor、四个概率和其差分可识别。
- **充要条件：** 对所有可容许 observationally-equivalent 参数，目标 `\Delta` 必须不变；完整 GLMM 使用所有可能观测下的 marginal predictive law 定义等价。
- **仍未解决：** 数值搜索未找到反例不能作为证明；精确求解、代数证书和未知 nuisance 的实现工具均为 `OPEN`。

### B10 — Acquisition 设计是四格 task-block 向量

- **草稿状态：** `PARTIAL（规格已处理）`；候选分布、条件预测与重试模型校准 `OPEN`。
- **规格位置：** 33 号 §3.1–3.4、§9.1–9.4；伪代码 §10.4 全部函数。
- **核心定义：** 候选是固定 `d=(g,e,b,n_rep)` 及其四格向量，不是抽象单标量；候选构造时一次性固定 `d.b`，两套 fantasy 和实际执行不得另抽设计。
- **条件预测：** 区分全新 task、已有 task 新 block、已有 block 缺失 cell；既有随机效应条件于同一 `D` 和本次 `\nu^{gen}`，缓存 cell 固定。
- **仍未解决：** 严格 CRN 只在共享外生随机流时成立；失败/重试 fantasy、候选构造分布和成本排名为 `OPEN`。

### B11 — FOS builder 区分无边与无证据

- **草稿状态：** `PARTIAL（规格已处理）`；`\rho_min`、FOS 稳定性和下游收益 `OPEN`。
- **规格位置：** 33 号 §7.3–7.6；伪代码 `BUILD_MISSINGNESS_AWARE_FOS`。
- **核心规则：** `SELECTED_SUPPORTED`、`SUPPORTED_PRACTICAL_NULL`、`NOT_SELECTED`、`UNRESOLVED` 互斥；强制 `\tau_zero<\tau_edge`。
- **Builder：** 主输入为保守 `w`；cluster 更新只对 supported cross edges 求均值并报告覆盖 `\rho_AB`；无合格连接时保留 partial forest 或 singleton safe fallback。
- **仍未解决：** unsupported/`NOT_SELECTED` 不填零，不用 SLL/MI 偷补；高阶结构是否被合适 mixing subset 捕获以及 GOM 价值为 `OPEN`。

### B12 — Prior sensitivity 与 null calibration

- **草稿状态：** `PARTIAL（规格已处理）`；所有实际校准结果 `OPEN`。
- **规格位置：** 33 号 §4.3–4.5、§11.1–11.4、§12.3、§15.2。
- **核心规则：** effect/shrinkage/random-effect/nuisance prior 来源必须登记；null/additive 上执行 prior-predictive、posterior/SBC、coverage 和 false-link 校准。
- **敏感性：** 冻结的尺度网格下重新拟合并报告 `q/w`、方向、BFDR 集合、empirical FDP、模型敏感、abstention 和 FOS/搜索变化。
- **仍未解决：** 本轮没有运行任何校准；小样本安全性、先验尺度、翻转容差和 Gate 数值均为 `OPEN`。单一 prior 下 `q\ge\tau_edge` 不能确认边。

---

## 4. 跨机制一致性矩阵

| 环节 | 唯一输入/规则 | 下游消费者 | 一致性约束 |
|---|---|---|---|
| Estimand | graph-specific objective-scale `\Delta_{g,e}` | posterior、identifiability、q/w | M2/M3 使用同背景、anchor、任务参考分布和 objective 版本 |
| Likelihood | 主 Bernoulli GLMM；次级 Beta/Gaussian | posterior 与 predictive | task/block 相关和 nuisance 不被点估计或独立 rollout 假设抹去 |
| Identifiability | 每模型×anchor 的非线性证书 + 支持/信息门 | `Q_g` 与 acquisition | 线性 row-space 不单独充当 probability-scale 证明 |
| Model order | 双 base 通过后比较；保守 local-null/q/w | BFDR、risk、FOS | 敏感、高阶或结构冲突边不得进入高置信输出 |
| Final decision | 同一 `BFDR_CORE` 与 constrained loss | 当前输出和 fantasy | `τ_edge`、资格、损失、近似平局规则一致 |
| Acquisition | 固定四格 task-block 向量、双生成/双重拟合 | 下一唯一新增设计 | 重算所有图、所有门禁和同一风险；成本含重试 |
| Local VIG | `q` 作证据、`w` 作强度、状态作缺失掩码 | FOS builder | `q` 不直接成为聚类相似度；未决不填零 |
| FOS | missingness-aware weighted average-linkage | 后续 EC 接口 | 无支持连接则 forest/singleton；不启动 CI-GOM |
| Budget | base/attempt key 与唯一新增 episode 账 | acquisition、执行和比较 | 缓存不按 pair 重复收费；实际资源另报；不超剩余预算 |
| Calibration | prior-predictive、null、SBC/coverage、sensitivity | Gate 与结论 | 未执行就保持 `OPEN`，不能由规格文字替代 |

---

## 5. 强基线覆盖与公平性闭合

每条记录均区分 `original-paper reproduction`（表中原生复现要求）与 `paper-setting adaptation`；适配版不得冒充原论文算法。

| 必需基线 | 33 号位置 | 原生复现要求 | Paper-setting adaptation / common-builder 要求 | 状态 |
|---|---|---|---|---|
| SLL-MI / LT-GOMEA | §13.2 | 种群 MI 与标准 LT | 二元 Agent 和任务效用；不得用差分补边 | `OPEN：未复现` |
| FBL / scaled FBLT | §13.2 | fitness perturbation、scaled strength、LT/MP | 随机四格/task-block，保留连续强度 | `OPEN：未复现` |
| FBL incremental | §13.2 | 部分 pair、增量 DSM、周期更新 | 相同 graph rounds 与唯一成本账 | `OPEN：未复现` |
| DLED | §13.2 | 当前个体四点直接依赖 | matched stochastic block，不借 TCAIL posterior | `OPEN：未复现` |
| cDLED-P3M | §13.2 | probe link、individual DLED、conditional eVIG、SLL-DSM clusters、P3M、donor restriction | parent/anchor 适配并保留原生 donor 规则 | `OPEN：未复现` |
| CGOMEA | §13.2 | conditional dependencies、conditional variation 与 solution mating filter | 二元 Agent 接口；原生 conditional builder 独立对照 | `OPEN：未复现` |
| FBL conditional / maximum clique | §13.2 | fitness-based conditional linkage 与最大团 FOS | 相同局部图上的原生 clique builder；另接共同 builder | `OPEN：未复现` |
| LMM | §13.2 | 噪声下 linkage measurement minimization 与 decomposition search | 明确连续/DE 假设及所有改变，保留分解优化 | `OPEN：未复现` |
| ALI/AIM | §13.2 | 相对强度和噪声判别 | 同一 task-block 强度矩阵、独立调阈值 | `OPEN：未复现` |
| Tinós 2026 GAwLL2 | §13.2 | GA 副产物交互学习与 operator 使用 | 零额外探测；TCAIL 额外 episode 全计费 | `OPEN：未复现` |
| Random linkage | §13.2 | 程序性下界 | 冻结随机分布/稀疏度，同一 builder | `OPEN：未实现` |
| Oracle local linkage | §13.2 | 程序性上界 | parent/anchor 真值，同一 builder | `OPEN：未实现` |

所有能输出 pairwise DSM/VIG 的估计器尽可能增加同一个 missingness-aware builder 分支；原生 LT、MP、conditional/clique、P3M 和 donor 规则另作独立公平对照。无法无损映射时必须报告信息损失，不能声称已完全隔离 estimator。固定/随机/fractional/full-factorial、full-parameter 与 interaction-subspace Bayesian D-optimal/IG 也在 §13.4 保留。

---

## 6. 本轮内部审查记录及其边界

33 号草稿经过编写过程中的规格符合性复核和文档质量复核。复核曾指出并促使修正：model-specific fantasy 生成分布、缓存/既有 block 的条件随机效应、attempt/retry 成本、预算与停止状态、联合 Fisher 维度、双模型状态优先级、零支持不可采样状态、近似 BFDR 风险语义、自适应 MC 变量绑定和单候选控制流。

这些记录只说明草稿修订过程，不构成不同审查者对 V2.2 的正式独立数学复审，不关闭 33 号 §16 的任何 `OPEN` 项。下一步仍必须由新的独立审查会话检查完整 33/34 号，而不能引用本节的编写过程复核作为研究 `PASS`。

---

## 7. 未关闭事项与最终结论

1. `OPEN`：V2.2 整体数学、统计、EC 接口和伪代码的正式独立复审。
2. `OPEN`：全部数值阈值、先验尺度、null/posterior/prior sensitivity、M2/M3 合并和高阶压力校准。
3. `OPEN`：非线性 estimand 的精确认证工具、GLMM 近似、acquisition MC/成本/排名和 missingness-aware FOS 验证。
4. `OPEN`：全部强基线的 original reproduction、paper-setting adaptation、公平预算和 clean rerun。
5. `OPEN`：跨 parent/generation global 或 online FDR；本版明确不作此主张。
6. `NOT ESTABLISHED`：TCAIL 独立新颖性、真实 Agent 有效性、下游 FOS/GOM 搜索收益和 EC 核心论文贡献。

**最终状态：V2.2 完整规格草稿和本矩阵已形成；TCAIL 继续 `HOLD / IMPLEMENTATION BLOCKED`。规格完成不等于创新成立，不授权实现、Phase 0、真实 API、模型训练、CI-GOM 或 IMCE-RSI。**
