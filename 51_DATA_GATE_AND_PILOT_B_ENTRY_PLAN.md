# 51 — 数据门禁、Pilot A-3 复核与 Pilot B 进入计划

日期：2026-11-06
所属项目：kaitibaogao / 第一项创新候选
状态：D-064-A COMPLETE / D-064-B READY_TO_EXECUTE / PREREGISTRATION=REQUEST CHANGES / FORMAL A-3B=HOLD
工作分支：pilot-a-stateful-recovery
前置文件：47_PILOT_A3_PROTOCOL.md、49_FIRST_INNOVATION_RELATED_WORK_AUDIT.md、50_DATASET_SELECTION_AND_VALIDATION_PLAN.md
Phase A 交付：PILOT_A3_INDEPENDENT_REAUDIT.md、recompute_a3_audit.py、a3_recompute_report.json、a3_artifact_manifest.json、ci_artifact/（原始 JSON/CSV）

## 0. 本阶段唯一目标

在不启动 A800、不调用真实 LLM API、不进入大规模演化搜索的前提下，完成两项前置验收：

1. 独立确认 Pilot A-3 的代码、CI、artifact、原始 episode 和预注册 Gate；
2. 确认 ToolMisuseBench / UndoBench 是否能被当前恢复控制器接口忠实执行和评分。

只有两个 Gate 都通过，才提交 Pilot B 的正式实验协议。当前不授权 Pilot B。

## 1. 当前已知状态（不得夸大）

### Pilot A-3
- 协议：47_PILOT_A3_PROTOCOL.md，状态 PRE-REGISTERED / NOT RUN。
- 实现状态文件：experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md，明确标记 IMPLEMENTED / NOT YET VALIDATED BY CI / RESULTS NOT YET RUN OR ACCEPTED。
- 模拟器、15 项回归测试和 workflow artifact 上传步骤已编写；这不等于测试已通过或实验已运行。
- 预算：每策略 954 episodes（144 train / 120 validation / 690 held-out）；7 策略共 6,678 policy episodes。
- 因此目前不能报告 A-3 结果、不能宣称 A-3 Gate 通过、不能启动 Pilot B。

### ToolMisuseBench
- 论文：Baral & Sigdel, REALM 2026, ACL Anthology 2026.realm-1.28。
- 官方论文：https://aclanthology.org/2026.realm-1.28/
- 数据卡：https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench
- 官方代码：https://github.com/akgitrepos/toolmisusebench
- seed-42 v0.2 large：train 6,000 / dev 900 / public test 1,200；四个领域 CRUD、retrieval、files、scheduling；clean、timeout、rate limit、schema drift、authorization、adversarial error。
- HF 数据卡明确写明 public test 有 1,200 tasks，其中 600 条是 output-grounded tasks；不得将 1,200 与 600 混成同一个有效评分分母。最终分母要按 manifest、任务字段和官方 evaluator 复核。
- 论文报告 Parser+Repair public-test task success 0.767、conditional recovery success 0.736；recovery-disabled task success 0.158。它是必须复现/公平适配的强参考方法，不是可以忽略的基线。
- 数据卡列出 MIT license、manifest、freeze metadata、quality report 和确定性执行器；实际使用前仍需固定准确 revision 并校验 SHA-256。

### UndoBench
- 论文：https://arxiv.org/abs/2610.05622
- 数据卡：https://huggingface.co/datasets/TanmaySah/undobench
- 官方代码：https://github.com/tradertanmay/undobench
- 数据卡当前版本 v1.0.1，36 workflows / 8 domains；DEV 14 / validation 10 / TEST 12。
- 数据集与 benchmark specification 为 CC BY 4.0；执行软件为 Apache 2.0。
- 支持 paired CONTROL / FAULT 执行；字段包括 initial_state、fault_scenario、expected_outcome、required_effects、oracle_spec。
- frozen TEST split 需要显式 opt-in；只在方法和预算冻结后做最终跨基准验证。
- 12 个 test workflows 的样本规模有限，统计需按 workflow/fault cluster 处理，不得把重复 seeds 伪装成独立任务数。

### ThinkingBox-Bench
- 数据卡：https://huggingface.co/datasets/microsoft/ThinkingBox-Bench
- 可执行源与固定 release：https://github.com/microsoft/thinkingbox-data/tree/thinkingbox-bench-v1.0
- v1.0 共 507 个 stateful business tasks，5 个领域。
- 官方用途明确为 evaluation-only；不得用于演化搜索、参数调节、prompt optimization、训练或其他模型优化。
- 只能在恢复策略冻结后做 clean-workflow regression。不是故障恢复主数据集。

## 2. Phase A — Pilot A-3 独立验收（最高优先级）— 已完成（2026-11-06，Gate = HOLD，见 PILOT_A3_INDEPENDENT_REAUDIT.md）

### A1. 固定运行身份
- 找到 pilot-a-stateful-recovery 当前 HEAD。
- 找到触发 A-3 的 GitHub Actions workflow run，确认 run 的 head SHA 与当前实现提交一致。
- 记录 run ID、head SHA、workflow 名称、触发事件、结论、job IDs 和 artifact IDs。
- 如果没有对应 run，明确记为 NOT RUN；不得用其他分支或旧提交的 CI 代替。

### A2. 检查 CI
- 查看全部 job 和 step 结论。
- 获取完整日志，确认 A1/A2/A3 regression tests 是否都运行。
- 确认 15 项 A-3 tests 实际执行且全通过；不能只看 workflow 总体绿色。
- 检查模拟器运行步骤是否成功，以及运行的是哪个 commit。
- 确认 artifact 上传步骤成功，artifact 名为 pilot-a3-results 或按 workflow 实际名称记录。

### A3. 下载并审计 artifact
- 下载 workflow artifact ZIP。
- 检查 ZIP 内是否确实包含 pilot_a3_results.json 和 pilot_a3_episodes.csv。
- 记录 ZIP SHA-256、两个文件 SHA-256、行数、列名、空值和唯一键。
- 检查 CSV 是否有每个 policy × scenario 的唯一记录；验证 scenario ID、seed、fault vector 对所有策略完全一致。
- 检查 split 计数：每策略 train 144、validation 120、held-out 690，总计 954；7 策略总计 6,678。
- 检查 JSON 汇总与 CSV 独立聚合结果逐项一致。
- 检查 oracle 的 privileged 信息没有泄漏到普通策略输入或普通策略输出字段。

### A4. 独立重算与预注册 Gate
- 从 CSV 重算 task success、safe resolution、invariant violations、duplicate effects、unresolved effects、compensation failures、actions。
- 分别重算 held-out task-shift、fault-shift、joint-shift。
- 按 47 号协议重新计算以 task-family × fault-composition 为 cluster 的 paired bootstrap 95% CI。
- Gate 条件必须全部按原协议判断：
  1. saga_aware 在每个 held-out slice 的 invariant violation rate 均为 0；
  2. held-out 合并集 oracle_diagnostic − saga_aware task-success gap 至少 0.05；
  3. cluster paired bootstrap 95% CI 下界大于 0。
- 若任一 slice 有安全违规：HOLD，先修复安全问题。
- 若所有 slice 零违规，但 gap ≤ 0.02 且动作成本差 ≤ 10%：该模拟器任务族 NO-GO。
- 其他情况：HOLD，解释失败边界；不得在看过 held-out 后调参再宣称通过。
- 输出独立复核报告、可重算脚本、修正后的 JSON/CSV（若有修正，原始文件必须保留且哈希不变）和 Gate decision。

Phase A 交付：PILOT_A3_INDEPENDENT_REAUDIT.md、重算脚本、原始 artifact manifest、独立重算表和明确的 GO / HOLD / NO-GO。

## 3. Phase B — 公开数据集版本与语义审计 — 已完成（2026-11-06，见 52/53/54 号审计、SPLIT_LEAKAGE_AUDIT、LICENSE_AND_PROVENANCE、DATASET_LOCK_MANIFEST.json）

### B1. ToolMisuseBench v0.2 large
- 固定 Hugging Face dataset commit/revision，不跟随 main 浮动。
- 下载 train/dev/test_public 和 manifest.json、v0_2_freeze.json、dataset_quality_report.json、release_summary.json、fault ablation 与 score artifacts。
- 对所有文件计算 SHA-256，保存 dataset manifest 和 license。
- 校验 6,000 / 900 / 1,200 行数、task_id 唯一性、split 标签和 600 output-grounded 子集。
- 按 domain × fault_family × difficulty × budget_profile 统计样本数。
- 审计 clean 与 faulted 的定义，尤其 timeout、rate_limit、schema_drift、authorization、adversarial_error 的可观察输出。
- 检查是否有多步骤工具链、跨工具事务、partial commit、late commit、compensation failure、no-readback、稳定 idempotency key；没有的场景明确记录为 coverage gap，不自行推断其存在。
- 检查 train/dev/test 是否共享 task template、toolset、schema、initial-state generator 或高度相似任务；形成 exact/near-duplicate 与 family leakage 报告。
- 审计官方 evaluator 的实际评分分母、output-grounded 判定和 CRSR 计算语义；0.767 / 0.736 / 0.158 先作为论文报告值，复现前不得称为我们已复现结果。

### B2. UndoBench v1.0.1
- 固定数据 commit 和官方代码 commit/tag。
- 记录 36 workflow、14/10/12 split、CC BY 4.0 数据许可和 Apache 2.0 软件许可。
- 先运行 doctor、smoke，只用 DEV / validation 做接口调试。
- 检查 policy 可见输入，确保 initial_state、expected_outcome、required_effects、oracle_spec 和 fault injection metadata 不作为 privileged inputs 泄漏给策略。
- 检查 paired CONTROL/FAULT 的 seed 配对、指标实现（Control Pass Rate、RSR、CRSR、EOR、DER、MER）。
- frozen TEST 必须锁箱，最终评价前显式批准和登记。

### B3. ThinkingBox-Bench v1.0（可选回归）
- 固定 thinkingbox-bench-v1.0 tag。
- 只记录其 507 tasks、5 domains、可执行 final-state / side-effect checks。
- 只允许方法冻结后运行一次 clean regression；不得用其任何任务、expected outcome、gold state 或 trajectory 调整策略。

Phase B 交付：DATASET_LOCK_MANIFEST.json、BENCHMARK_COMPATIBILITY_MATRIX.md、SPLIT_LEAKAGE_AUDIT.md、LICENSE_AND_PROVENANCE.md。

## 4. Phase C — 统一执行接口与小规模适配 Smoke Test

仅当 Phase A 的 A-3 结果已得到独立报告后启动。此阶段不是 Pilot B，不运行演化搜索。

### C1. 统一 episode contract
定义标准接口字段：
- task_id / task_family / split；
- initial_state（仅环境可见）；
- tool_schemas / allowed_contracts（按 benchmark 原生能力提供）；
- fault_plan（仅注入器可见）；
- public observation stream（策略可见）；
- effect_history / final_state / invariant_oracle（仅 evaluator 可见）；
- success criteria / budget / seed。

策略输入必须由 allowlist 构造；不能将 fault_plan、expected_outcome、oracle_spec、gold summary 或 hidden state 暴露给策略。

### C2. ToolMisuseBench adapter
- 忠实调用官方 deterministic executor/reference implementation，不重新发明数据集语义。
- 对 4 个 domain × 6 个 fault family 做 stratified smoke sample；建议每个有效 cell 先取 5 条 train tasks，目标约 120 条（以实际非空 cell 数为准）。
- 运行官方 Parser+Repair、recovery-disabled 和一个简单安全规则策略。
- 验证 reset/replay 确定性、policy input isolation、grader consistency 和原始输出保留。
- 如果官方 runner 与我们的 episode contract 无法无损映射，记录 unsupported semantics，不得静默简化。

### C3. UndoBench adapter
- 只用 DEV / validation 做接口 smoke。
- 跑官方 baseline 和无恢复 baseline，验证 paired control/fault、状态隔离、effect oracle 与报告脚本。
- 不访问 frozen TEST。

Phase C 交付：两个 adapter、统一 episode schema、smoke logs、baseline reproduction note 和 compatibility blockers。

## 5. Phase D — Pilot B 正式算法比较（仍需单独授权）

Phase A、B、C 全部通过后，才提交 Pilot B preregistration。正式比较至少包括：
- Strong hand-designed recovery policy；
- Official Parser+Repair（ToolMisuseBench）；
- Random Search；
- Standard GA；
- Standard GP；
- NSGA-II；
- NSGA-III；
- Contract-semantics-preserving / counterexample-guided proposed EA；
- EvoTool-inspired policy-evolution adaptation（只有能公平适配时才列为实测基线；否则只做机制对照，不伪称已比较）。

### 公平比较
- 同一 train/dev tasks、相同 initial states、fault realizations、seeds 和 rollout/evaluation budget。
- 以真实 simulator executions 计费；不能只让 proposed method 获得更多 fitness calls。
- test split 不用于算子设计、参数选择、种群选择或 early stopping。
- 报告完整 search cost、候选数、每候选 rollout 数、API 调用（若未来获批）、wall-clock 和计算成本。
- 采用 cluster-aware paired bootstrap / permutation，统计单位按 task/workflow 与 fault family 聚类。
- 安全不变量作为硬门禁；成功率不能抵消安全违规。

### Pilot B 核心指标
- Conditional Recovery Success / task success；
- Safe Resolution / correct final state；
- invariant violation、duplicate effect、incorrect compensation；
- unresolved residual effects；
- worst-group performance；
- recovery action count / execution cost；
- clean-task regression。

### Pilot B 停止条件
- proposed method 无法保持硬安全约束：停止或重构，不进入论文主结果。
- 与标准 GA/GP/NSGA 在相同 rollout budget 下没有稳定增益：不保留“改进 EA”主张。
- 只在训练任务提升、held-out/OOD 不提升：判为记忆/过拟合，不通过。
- 仅平均值提高但 worst-group 或副作用安全明显恶化：不通过。
- 若基准语义不支持关键契约机制：缩小研究主张，不靠新增自建场景包装公开基准结果。

## 6. 执行顺序与停止门

| 顺序 | 阶段 | 交付 | 允许做什么 | 不允许做什么 |
|---|---|---|---|---|
| 1 | A-3 独立复核 | CI / artifacts / 重算 / Gate | 检查与复算 | Pilot B、A800、真实 API |
| 2 | 数据集审计 | 固定版本、hash、split、coverage | 下载、只读审计 | 用 test 调参 |
| 3 | Adapter smoke | 两个 adapter、baseline smoke | 小样本接口验证 | 演化搜索 |
| 4 | Pilot B preregistration | 冻结算法、预算、统计协议 | 提交审批 | 未获批就启动大实验 |
| 5 | Pilot B | 同预算强基线实验 | 执行授权实验 | 访问锁箱 test 调参 |
| 6 | 外部最终评估 | ToolMisuseBench public test / UndoBench TEST / clean regression | 冻结后确认 | 再根据 test 改方法并继续报同一 test |

## 7. 当前明确决定（2026-11-06 Phase A 完成后更新）

- **Phase A 结论：A-3 预注册 Gate = HOLD（HOLD_REVIEW_FAILURE_BOUNDARIES）。** 完整证据见 PILOT_A3_INDEPENDENT_REAUDIT.md。要点：run 42241224898（head `f5e6b46`）真实运行并成功上传 artifact（此前全部 run 因 `PublicToolView.tick` 崩溃）；28 项测试通过；6,678 episodes 结构/配对/语义审计全部通过；oracle−saga 成功率差 0.0、bootstrap CI [0.0,0.0]、动作成本差 +34.6% → 按 47 号原文 HOLD。
- Phase A artifact 哈希（SHA-256）：ZIP `1119d14b70eedef221fe6e63439e2a04bd58c0354d5a723344d2c80c459ab727`；JSON `3a60ae8385c723c57d54ff47608fe428690d94519f6762ec78bbc15c1d15fe14`；CSV `2c7d7dad5faaae58f182f27d77b90dfa237f4c1627e15b0bc029d34582f3c369`（6,678 数据行）。原始文件：`experiments/pilot_a_recovery/ci_artifact/`；清单：`a3_artifact_manifest.json`。
- GO：文档维护、公开数据集只读审计（Phase B，已完成）、adapter smoke 的准备（Phase C，仅 train/dev/validation）、A-3b 新预注册协议设计（已完成草案，待独立审查与批准）。
- HOLD：A-3b 正式运行（预注册冻结+批准前禁止）；Pilot B 演化搜索；用 A-3 held-out 或任何锁箱调参；A800 / ARWM；真实 LLM API；UndoBench frozen TEST 执行。
- ThinkingBox：UNREACHABLE（HF 401 / GitHub 404，53 号记录）；恢复访问前不规划任何依赖实验；即便恢复也仅冻结后 clean regression。
- Phase B 结论（2026-11-06）：ToolMisuseBench 评分口径已解密（0.767/1200、0.736/993、600 OG 为子集）；语义缺口确认（无 lost-ACK/补偿/saga/重复副作用）；Parser+Repair DEV 复现 0.7622/0.7363，列为 Pilot B 必选基线。UndoBench 语义与指标同构、harness 验证、TEST 锁内置；定位外部泛化验证。融合判断见 54 号：主搜索=A-3b 自有模拟器+ToolMisuseBench train 第二域，外部=UndoBench TEST；公开基准不能单独支撑第一项创新。数据 revision：ToolMisuseBench `98eb28718b0393e029088ce80604c48807216de4`、UndoBench `4be1151851a109e7c9cfc1ba5d6e6c64461f6f93`（哈希明细在 DATASET_LOCK_MANIFEST.json）。
- 下一项实际执行任务：55_PILOT_A3B_RESEARCH_DESIGN.md 独立审查 → 预注册冻结（R3/R4 分层比例、τ_min、成本计价、seed、预算、场景哈希）→ 用户批准 → 实现可恢复性分类器/场景生成器扩展/统一 adapter。任何 A-3b 运行在冻结批准前一律禁止。
- 接管要求：每次会话结束前更新 NEXT_SESSION_PROMPT.md、SESSION_HANDOFF.md、README.md、05_DECISION_LOG.md 和本计划的状态；必须记录实际 HEAD、CI run、artifact hashes、工作区/分支状态。不得把文档提交或 CI 配置写成实验已通过。


## 8. 2026-11-07 状态更新：Phase B 完成，55 号独立审查 REQUEST CHANGES

- Phase B 数据审计交付物见 52–54、DATASET_LOCK_MANIFEST.json、SPLIT_LEAKAGE_AUDIT.md、LICENSE_AND_PROVENANCE.md 与 experiments/dataset_audit/。
- A-3b 设计草案见 55 号；独立审查见 56 号。
- Phase B = GO / complete；55 = REQUEST CHANGES；A-3b execution = HOLD。
- 55 号不能直接冻结：必须修复 R4 零残留矛盾、R2 完成/安全放弃混淆、observation-based recoverability 定义、有限样本 P(violation)=0 表述、R4 成本与必要升级惩罚、类别比例/精确配额/cluster-level power、算法初始化与共同骨干、rollout 预算边界和新颖性审计。
- 下一阶段：55-R1 修订 + reachability checker 规格/单测 + 场景配额与功效分析 + 算法公平性设计。只允许单元测试和 train/dev/validation smoke；正式 A-3b、Pilot B、A800、真实 API、UndoBench TEST 均 HOLD。


## 9. D-061 更新：D-060 诊断复核 REQUEST CHANGES（2026-11-07）

- 独立复核报告：`57_PILOT_A3B_DIAGNOSTIC_INDEPENDENT_REAUDIT.md`。
- D-060 原始 JSON 保留，216 scenarios / 24 runs / 每 run 216 rows；正确类别数 R1=96/R2=50/R3=35/R4=35。
- 当前算法结论不得升级为确认性证据：静态 rule table 冒充 stateful FSM、运行器隐式 Saga rollback/auto-escalation、R4 scorer 忽略可避免残留、必要升级仍计入 action cost、A-3 labels 非 checker 全量验证、B pool 清空/权重未使用、per-seed CI/p 平均、基线非 canonical。
- 55-R1 的 3:1 文字与表中 3:2/58:38 冲突；冻结前必须重算。
- 下一阶段先修控制器执行语义、R3/R4 evaluator、标签器、B、独立合同验证器、标准 EA 和 pooled/hierarchical 统计，再以新诊断集重跑。
- **暂停功效分析和扩大 rollout**，避免用有缺陷的指标估算正式样本量。正式 A-3b 继续 HOLD，直到独立复核和用户批准。

### D-061 执行更新（2026-11-07）
上述修复**已全部落地**（58 号报告；47/47 测试绿）。第二轮诊断（diagnostic2，manifest d4fb2be6…）：A vs NSGA-II Δ=+0.239（Holm p=0.0014）显著、独立 validator 非法率 1.00→0.00；primary AB vs NSGA-II +0.126（p=0.0002）显著；**AB vs A −0.113（B 叠加有害）**；未超过强手工（−0.514）；验证集泛化显著（+0.148, p=0.002）。判定：机制 A 成立、B 需重设计、创新部分成立。下一步：B 反例→基因映射重设计 + WAIT-SLA 行为层契约修复后重跑。正式 A-3b/功效分析继续 HOLD。


## 10. D-062 更新：WAIT-SLA 行为安全与反例驱动演化（2026-11-08）

任务计划：`59_D062_WAIT_SLA_AND_COUNTEREXAMPLE_REDESIGN_PLAN.md`；接管入口：`NEXT_SESSION_PROMPT.md` D-062 节。

- D-061 结果报告给出 A vs NSGA-II Δ=+0.239、AB vs A Δ=-0.113、AB vs Hand Δ=-0.514；报告行为违规率 A=0.36、Hand=0.006。以上必须先从原始 episode 数据独立复算，尤其核对分子、分母、episode/action 口径和重复事件。
- 第一阶段：独立复核失败轨迹，区分未提交、lost ACK、已提交但不可见、处理中、未知结果及缺少 visibility guarantee。
- 第二阶段：定义工具级 WAIT-SLA 合同，明确 visibility SLA 与 retry SLA，保证策略只读取公开观测；无可证明 visibility guarantee 时不得通过固定等待推断 NOT_COMMITTED。
- 第三阶段：B-new 依据完整失败动作序列定位涉事 FSM 基因邻域，语义修复型变异替换普通变异，保持变异/rollout 预算公平。
- 第四阶段：评估独立 Contract Validator、行为层 Safety Gate 和硬安全优先的生存者选择。
- 新诊断至少比较 Hand、NSGA-II、A、Fixed-WAIT、WAIT-SLA、WAIT-SLA+VERIFY、安全重试、B-new、A+B-new、A+B-new+Gate；指标覆盖恢复成功、episode/action 行为违规、重复副作用、SLA 违规、正确升级、损害、不必要成本和未见任务泛化。
- 旧 D-061 validation 若用于调参不得继续作为独立验证；正式 held-out 继续锁定。
- **当前状态 READY_FOR_EXECUTION，不代表代码或实验已完成。** GO：复核、实现、测试、新非锁箱诊断；HOLD：正式 A-3b、锁箱调参、UndoBench TEST、Pilot B、A800/ARWM、大规模真实 API。

### D-062 执行更新（2026-11-07）
59/60/61 号报告落地。复核确认 D-061 的 0.36 违规率系评价器 artifact（正确 ROLLBACK 被误伤），真实损害仅 7 例重复（`TIMEOUT→VERIFY 谎言→RETRY→DUPLICATE`）。修复评价器并实现 WAIT-SLA 契约 + B-new。第三轮（diagnostic3，manifest 017b3454…）：**AB vs A +0.119 p=0.0002（B-new 成立）**；**WAIT-SLA vs A +0.089 p=0.005、vs 固定等待 +0.054 p=0.003**；AB vs AwaitSLA +0.031 p=0.007（搜索独立增益）；validation AB vs A +0.142 p=0.008。负结果：Safety Gate 有害、B 单独无效、未超 hand（−0.282）。判定：三机制独立证据齐备，第一项创新接近成立。下一步：功效核算 → preregistration 交用户批准 → 正式 A-3b。


## 11. D-063：统计复现、经验功效与预注册 Gate（2026-11-09 更新）

**当前状态：ACTIVE PLAN；Stage 0 尚未完成；正式 A-3b = HOLD。**  
完整计划与执行验收标准见 [62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md](62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md)。唯一接管入口为 [NEXT_SESSION_PROMPT.md](NEXT_SESSION_PROMPT.md)。

### 11.1 必须保留的 D-062 证据边界

- AB vs NSGA-II all +0.1049 / p=.062（54 clusters）；validation +0.1173 / p=.2277（18 clusters），均未显著。
- AB vs A validation +.142 / p=.0082，支持 B-new 在 A 上的增量，但不能替代 AB vs NSGA-II 主比较。
- AB vs AwaitSLA validation +.031 / p=.244，Q10 搜索增量尚未证明泛化。
- AB vs Hand −.282，仍落后强手工策略。
- AwaitSLA vs A +.089 / p=.0047；AwaitSLA vs AwaitFixed +.054 / p=.0032。
- B 单独和 Safety Gate 的负结果必须保留；安全保证严格限定于明确工具合同假设。

### 11.2 Stage 0：统计分析器与独立复算（唯一首要任务）

当前 stats.py 仍有 diagnostic2 硬编码读取路径，diagnostic3 需要单独可复现的分析入口。新增 analyse_diagnostic3.py 或显式输入参数的通用 CLI，必须：

- 从 diagnostic3 原始 JSON 读取数据，输出 all/train/validation；
- 重新计算七组主要/次要比较：AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II；
- 以 task × fault-composition cluster 为推断单位，seed 为嵌套因素；
- 检查 episode ID 唯一、实验臂配对完整、cluster 成员一致、split 隔离、分母和 R1/R2/R3/R4 标签语义；
- 输出 cluster SD、95% CI、paired sign-flip p、适用的 Holm-adjusted p、效应量和 seed 稳定性；
- 保存输入 JSON / manifest / 分析配置哈希、分析命令和版本；
- 对缺失配对、重复 episode、cluster mismatch、seed 缺失、split 泄漏、分母错误设置 fail-closed 测试；
- 独立再生统计摘要，并逐项对账 61 号报告；差异要解释，不得硬编码结果以匹配历史数字。

### 11.3 Stage 1：经验功效仿真

- 使用 Stage 0 再生的 cluster-level paired differences。
- 主要设计只针对新 held-out test 上 AB vs canonical NSGA-II。
- 报告 MDE=.08/.10/.1173、双侧 alpha=.05、80%/90% power。
- 用 cluster-level Monte Carlo resampling / sign-flip 估计功效，并报告模拟次数、Monte Carlo 误差与稳定性。
- 做 15% cluster 失效预留与 SD 敏感性分析。
- validation 仅 18 clusters，SD 估计不稳定，必须披露。
- 不能通过增加同一 cluster 的 episodes 或 seeds 伪造独立样本。

### 11.4 Stage 2：任务族与 cluster 扩展审计

旧文档同时出现“总计 6 个任务族”和“validation 2 个任务族 ×9 compositions =18 clusters”。可能分别指全体任务族和 validation 子集，必须从真实 task/split/scenario manifests 对账。

63 号审计需列出 task family、生成规则、工具依赖、9 类 fault composition 适用性、确定性 cluster ID、近重复/模板泄漏、train/validation/test 泄漏矩阵、可用独立 cluster 数和扩展成本。目标 cluster 数以经验功效仿真为准；145 只是 MDE=.10、80% power、15% 预留下的初步 t 近似值，不是冻结样本量。

### 11.5 Stage 3：预注册草案

64 号草案必须先澄清主要终点：R1/R2 的条件恢复与 R3/R4 的正确升级不是同一语义；给出逐类公式、分母、类别权重、cluster 聚合顺序，UNKNOWN 按预先定义的规则处理。

- 唯一主要比较：AB vs canonical NSGA-II；
- 双侧 alpha=.05；主要终点、MDE、目标 power 和 cluster 数事前冻结；
- 次要比较 Holm 校正；
- Hand 仅作强手工参考，不声称超越专家；
- 安全作为硬门，合同假设与事件级指标明确；
- 代码、算法版本、初始化、预算、种子、排除规则、锁箱 manifest 和哈希全部冻结；
- 文件状态为 DRAFT — NOT FROZEN，提交用户审阅。

### 11.6 GO / HOLD

**GO：** 统计复现、synthetic tests、经验功效仿真、任务族审计、预注册草案、CI 和文档维护。

**HOLD：** 正式 A-3b、查看/调参新 held-out test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。用户批准预注册后，正式 A-3b 仍需单独授权。

**下一会话唯一首要任务：** Stage 0 — 从 diagnostic3 原始数据建立独立、可复现的分析入口。


---

## 12. D-064 预注册独立审查更新（2026-11-09）

64 号预注册草案暂不批准。完整阻断项见 `65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md`。

核心问题：
- 64 §3 主要终点 CondRecSucc 只含 R1+R2；D-063 功效模拟使用全 R1–R4 的 class_success，estimand 不一致；
- 当前功效脚本是参数化正态 Monte Carlo，不是实际经验重采样/sign-flip；
- ICC 仅由 6 个 task families（validation 2 个）估计，负点估计不能证明 cluster 独立；
- 任务族候选只经过合同属性筛选，没有任务语义验证；正式 8/4/17 场景生成器尚未接入当前运行代码；
- MDE=.10、失效预留和 MDE=.1173 备选未形成唯一冻结决定；
- UNKNOWN 上限、primary eligible clusters、硬安全门规则需要补齐。

**当前 GO：** D-064-A/B/C/D 修复、CondRecSucc 分析、功效重算、任务语义 validator、正式场景生成器、标签和 manifest 测试、预注册修订。

**当前 HOLD：** 正式 A-3b、任何 held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。

**下一步唯一首要任务：** D-064-A — 对 diagnostic3 原始 rows 建立 R1/R2-only CondRecSucc 配对 cluster 分析；在 primary estimand 和功效方案修正前，不批准 64 号草案。


---

## 13. D-064-A 完成后的数据门禁更新（2026-11-09）

D-064-A 已从 diagnostic3 原始数据完成 CondRecSucc R1/R2-only 独立分析（66 号报告）：
- 42 个 primary-eligible task×composition clusters，12 个 zero-denominator clusters；
- 42 个 clusters 嵌套在 6 个 task families 中，每 family 7 个 eligible compositions；
- AB=.5582、NSGA-II=.2407、Δ=+.3175、cluster SD=.318856；
- D-064-A cluster-level CI [.218254,.411376]，sign-flip p=.000125；
- R3/R4 行为率权衡独立保留。

**当前关键数据门禁：** 不得假设 42 个 composition clusters 独立。D-064-B 必须先评估 family 内相关性、ICC 不确定性、family-level 推断与层级功效。17×9=153 是 design clusters；在 7/9 eligibility 条件下约 119 才是 primary-eligible clusters，且需要 D-064-C 标签生成器核验。

GO：D-064-B（完整执行规格见 67 号提示词）。  
HOLD：正式 A-3b、任何 held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。

### D-064-B 更新（2026-11-09）
层级功效与 ICC 敏感性完成（68 号）：t 检验为校准主检验；所需 families（MDE 0.10 @80%）ICC 敏感 15–30，双 15% 损耗 22–40；17-family 条件性充分。数据门禁不变；下一步 D-064-C 语义 validator 与正式生成器。


## 14. D-079 更新（2026-11-10）：D-078 诊断与 Train-only 挑战集

D-078 的 14 臂 × 3 seeds 探索结果未证明 SBCG 性能提升。D-079 初查发现 32/42 次 selected FSM 与 Hand FSM fingerprint 相同；Hand 在 R1/R2 的 84 个 Validation 场景全部成功，但 R3 正确升级为 0/12。另发现成功任务 active effects 被错误计入 harm，以及旧 analytic label 被用于评估。

D-079 已新增 evaluator 修复、独立 per-family/per-scenario audit 和 Train-only 难度分层挑战集候选。挑战集计划为 8 Train families × 6 strata × 3 repeats × search/diagnostic 两角色，共 288 个场景；不构建 Validation/Test。CI 与 manifest SHA lock 尚待完成。

**Pilot B 仍 HOLD。** D-079 Train-only synthetic diagnostic 不等于 ToolMisuseBench/UndoBench 适配完成，也不授权 public-test 或 UndoBench TEST。A800/ARWM、真实 LLM API、ThinkingBox 继续 HOLD。当前唯一下一任务是核验 D-079 CI 和 challenge manifest，锁定 hash 后才可运行 Train-only exploratory mechanism diagnostic。



## 15. D-079 corrective update（2026-11-10）

首轮 D-079 regression CI 因 challenge generator 对 Train family contract composition 的假设过强而失败：不是每个 Train family 都同时包含 contract-level compensatable 和 uncompensatable tools。D6 已改为允许 runtime compensation unavailable 表达 R4，并补充回归测试。D-078 workflow 已从 push 自动触发改为 workflow_dispatch only，防止普通维护提交重跑已完成的 14-arm pilot。该失败发生在测试 preflight，未产生新的算法实验数据。当前仍需等待 corrective CI；challenge manifest hash 未锁定前不运行新的 Train-only optimizer diagnostic。Pilot B、Test、A800/ARWM、真实 LLM API 继续 HOLD。



## 16. D-081 corrective commit / D-079 CI gate（2026-11-11）

D-081 已推送到 `pilot-a-stateful-recovery`：`192f958847fb31d7d704cfa0760201dcd8371e32`。修复 D6 对 Train family contract composition 的过强假设：若没有 contract-level uncompensatable tool，可在 compensatable tool 上设置 runtime compensation unavailable，形成 R4 damage-containment 场景；同时新增 D6 回归测试。D-078 workflow 改为 `workflow_dispatch` only，普通 push 不会重跑已完成的 14-arm pilot。

首轮失败记录保留：regression run 42827879313 在 282 tests 后失败；D-078 run 42827879133 在 full regression preflight 失败、算法步骤 skipped。D-081 commit combined status 当前无 checks，corrective CI 尚未验证成功。

**唯一下一任务：** 核验 D-081 regression CI。成功后检查 D-079 D-078 audit artifacts 与 288-scenario Train-only challenge manifest，审查 R1-R4 分布、UNKNOWN/label disagreement、scenario ID、search/diagnostic 配对及 manifest SHA，再提交 manifest lock。manifest lock 前禁止运行新优化器。

**HOLD：** 正式 A-3b、Test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge。


## 17. D-082 数据门禁与挑战集冻结结果（2026-11-11）

D-081 corrective CI 已成功：run 42828590264 @192f958，318/318 tests。D-078 原始 artifact 未覆盖；D-079 独立复算、288 场景挑战集与 manifest lock 均已完成。

挑战集只含 Train：8 families×6 difficulty strata×3 repeats×Search/Diagnostic=288 scenarios；无 Validation/Test；0 UNKNOWN；robust/analytic disagreement=0。manifest 内容 SHA=`cafdc52e037c08ca8cd95c0546014bab6dd27e9bd6d28122afb90f28b3cd1efa`，raw-file SHA=`0072550d432d306d4c02912bebaaa4a4756edb33a68c962cf59e9fb198d6c152`，scenario-ID SHA=`4d7b19605155bdbfde61216ecfda6019f09d78a76fa7162fd16c18496114ec99`。

在 lock 通过后已运行 Train-only 14-arm×3-seed exploratory diagnostic。SBCG 未超过 Hand/Rule-based，且 matched NSGA-II 差异不支持提升；当前算法整体 NO-GO。该诊断不等于 Pilot B、正式 A-3b、UndoBench/ToolMisuseBench 或真实 LLM 验证。

**Pilot B 与真实 Test 继续 HOLD。** 下一步先做 R4 独立复审；算法侧只允许预注册针对 R3 的 prefix rollback/compensation-before-escalation 单机制消融与新挑战划分，不得在同一 Diagnostic 上反复调参。
