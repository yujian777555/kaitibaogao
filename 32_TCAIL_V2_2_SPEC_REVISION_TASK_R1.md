# TCAIL V2.2 规格修订任务 R1

**日期：** 2026-11-03  
**状态：** SPECIFICATION_REVISION_ONLY / NO IMPLEMENTATION  
**唯一仓库：** yujian777555/kaitibaogao  
**依据：** 17_TCAIL_FORMAL_SPECIFICATION_V2.md、20_TCAIL_V2_1_INDEPENDENT_REVIEW_R1.md、21_GOMEA_LINKAGE_AND_NOISY_INTERACTION_RELATED_WORK_AUDIT_R1.md、22_TCAIL_LINKAGE_INTERFACE_REVISION_PROPOSAL_R1.md、31_TCAIL_LINKAGE_INTERFACE_INDEPENDENT_REVIEW_R2.md

## 1. 目标

形成一份完整、内部一致、可交给独立审查者复核的 **TCAIL V2.2 规格草稿**。只修改数学/统计/算法规格，不写代码，不运行实验，不调用 API，不启动 Phase 0。

新文件建议命名：
`33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md`

不得覆盖 17 号 V2 权威历史文件；V2.2 通过独立审查后再决定是否晋升为权威规格。

## 2. 必须关闭的问题

### B1：从条件 interaction 到 local fitness linkage
- 使用 objective-scale conditional finite difference `Δᵢⱼ(u,z)`。
- 将 global RMS `Sᵢⱼ(z)` 限定为描述性/筛查摘要，不直接输出为某个 parent 的 FOS edge。
- 使用 parent/task local posterior `qᵢⱼ(x,z)=P(|Δ|>δ_local|D)`。
- 明确 `δ_local`（实际意义阈值）、`τ_edge`（后验门限）和连续 FOS weight 的不同作用。
- 评估候选 `wᵢⱼ=E[(|Δ|-δ_local)_+|D]`；若选择其他权重，必须解释并列出替代方案。
- 正负方向概率单独报告；不能把负交互当作非法，也不能仅用 q 当作连续聚类强度。
- 明确 local VIG 到 FOS 的固定 builder、更新规则、tie-break、singleton/safe fallback 和 unsupported edge 处理。

### B2：M2/M3 与高阶
- 把 M2/M3 gate 写入正式算法伪代码，不得只在文字中提及。
- 低阶项可保留在模型中，但不得强制低阶系数非零，除非能解释 pure three-way-only 真值如何表示。
- 定义 MODEL_ORDER_SENSITIVE 的触发条件、最终 posterior/BFDR 规则和 acquisition 处理。
- 增加四阶/高阶 misspecification 压力测试，或明确限制方法适用范围及失败边界。

### B3：acquisition 与 BFDR
- 以最终 local BFDR-constrained edge-set decision 定义风险。
- 写出未来 observation 下的 posterior update、MC estimator、MCSE 和 common random numbers。
- 若使用 per-edge surrogate，必须明确降级并与 constrained-risk acquisition 比较。

### B4：task-block 统计模型
- 明确定义 task-block ID、task instance、run seed、配置四格配对和执行顺序随机化。
- 给出主要 likelihood / random effect / cluster posterior 规则，不允许仅写“必要时 bootstrap”。
- 明确 acquisition 的 future block sampling distribution。
- 重复 rollout 不能当作独立 task samples。

### B5：nuisance uncertainty
- 主目标优先考虑程序化成功概率 + Bernoulli likelihood。
- 若 Beta reward 为主，定义 κ prior、联合 posterior 和 acquisition 积分。
- 若 Gaussian 为主，定义 σ² 冻结或联合估计规则。
- 不允许在正文宣称纳入 nuisance uncertainty、在公式里却只代入点估计。

### B6：identifiability
- 对每个 model basis × context anchor 分别构造 legal/observed design matrix。
- 分开 structural row-space estimability、nonparametric common support 和 GLM practical information。
- 定义共同支持、Fisher-weighted conditioning 和 abstention 门限的训练期校准方式。

### B7：BFDR family
- 明确 graph ID：generation/RSI round × parent ID × context anchor。
- 明确每个 local graph 的 edge family、MODEL_ORDER_SENSITIVE / PENDING_SUPPORT 状态的处理。
- 若只控制 per-graph BFDR，禁止声称跨 parent/跨 generation 的 global FDR 控制；若需要 global claim，另定义累计错误预算。

### B8：预算
- 明确定义一个 task-block evaluation / episode-equivalent。
- 固定单 episode 的 step/tool-call/token cap 和超限规则。
- 同时报告 episodes、tool calls、tokens、wall-clock、currency；不把 task-block 数直接等同于真实货币成本。

## 3. 强基线与 novelty boundary

V2.2 必须纳入：
- SLL-MI / standard LT-GOMEA；
- FBL / fitness-based LT；
- DLED / cDLED；
- CGOMEA / conditional-clique FOS；
- LMM、ALI/AIM；
- Tinós et al. 2026 GA-side-effect interaction learning；
- random linkage、oracle local linkage。

明确区分原论文复现和 paper-setting adaptation。所有 estimator 应尽可能使用相同 FOS builder，以隔离 estimator 的增量贡献。

## 4. 交付物

1. `33_TCAIL_FORMAL_SPECIFICATION_V2_2_DRAFT.md`：完整规格，不是补丁摘要。
2. `34_TCAIL_V2_2_CHANGELOG_AND_CLOSURE_MATRIX.md`：逐项映射 B1–B8，列出修改位置、公式、伪代码位置和仍未关闭项。
3. 更新 `STATUS/README/SESSION_HANDOFF/DECISION_LOG`，保持 HOLD 状态。
4. 提交 SHA、工作区状态和文件清单。

## 5. 验收规则

- 全文只有一个主要 edge estimand；global RMS、local q、FOS weight 各自角色无混淆。
- 数学符号在 estimand、likelihood、posterior、BFDR、acquisition 和伪代码中一致。
- M2/M3 gate 在状态机、伪代码、BFDR 和 acquisition 中闭合。
- task-block 配对和随机效应能落到可执行观测单位。
- 每个不可识别/弱识别/模型敏感状态都有明确后续动作。
- 参数表区分 `δ_local`、`τ_edge`、FOS weight、BFDR q 和 acquisition λ。
- 新颖性表述不使用“首次提出”，且强基线完整。
- 不把规格修订写成实现、实验或创新已成立。

## 6. 禁止事项

- 不修改其他独立项目仓库。
- 不调用 DeepSeek API，不使用 DeepSeek-V4-Pro。
- 不编码 TCAIL/CI-GOM，不运行 Phase 0，不训练 A800 模型。
- 不删除或覆盖 17 号权威 V2 文件、20 号 REQUEST CHANGES 复审和 22 号 proposal。
- 如果某项数学闭合需要新的假设，必须显式列为假设并给出可证伪实验，不能自行默认为成立。

## 7. 可直接复制给 Executor 的提示词

你是 `yujian777555/kaitibaogao` 仓库的规格修订 Executor。唯一任务是按本文件将 TCAIL 17 号 V2 规格修订成一份新的 V2.2 完整草稿。先读取 17、20、21、22、29、31 号文件，逐项处理 B1–B8。不要编码、不要调用 API、不要运行 Phase 0、不要训练模型。新建 33 号完整规格草稿和 34 号 change log/closure matrix，不覆盖 17 号权威文件。完成后检查所有公式、符号、状态机、BFDR、acquisition、task-block 模型、预算和参数表的一致性；将所有未闭合项保留为 OPEN，不得自行宣布 PASS。更新 README、05_DECISION_LOG 和 SESSION_HANDOFF，提交并核验远端 main。最终汇报每项 B1–B8 的 PASS/PARTIAL/OPEN、具体文件行/章节、提交 SHA、工作区 clean 状态。