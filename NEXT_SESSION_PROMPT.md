# NEXT_SESSION_PROMPT.md — Canonical Handoff Prompt

> **强制规则：本文件是下一会话唯一权威接管提示词。每次实质性研究、实验、代码、协议、审计或决策发生变化后，必须在同一轮更新本文件，并同步 README、05_DECISION_LOG.md、SESSION_HANDOFF.md。不得只在聊天中交代进展，不得让接管提示词落后于仓库事实。**

**最后维护日期：** 2026-11-10（R4 统计/主次终点/隔离/pre-flight 初版实现；CI 240 tests success）
**唯一仓库：** `yujian777555/kaitibaogao`  
**工作分支：** `pilot-a-stateful-recovery`  
**主分支：** `main`（实验期间不得擅自合并）
**最近一次代码/测试核验：** work f4d8d0d1e314b29f7e6a7627f99293b306f76d92；main 683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead 207 / behind 0；CI 42791224479 success（28+212=240 tests）。接手时重新查询。
**R4 任务规范：** 73_D064_R4_EXECUTOR_SPECIFICATION.md。

> **当前任务优先级说明（2026-11-10）：** R3 独立审计仍为 REQUEST CHANGES。R4 已有实际实现：共享 Student-t/CI；正式 family-level analyzer + provenance；H2–H5 四项 family-level 配对分析与 Holm（全部 exploratory）；Train-only evolution guard、普通 evaluator Test guard、公共 manifest 不返回 Test payload、原子 one-time gate；metadata-only fail-closed pre-flight。CI 42791224479 @ f4d8d0d success（28+212=240 tests）。R4 尚未完成：正式 runner 接线、ICC/MDE/Type-I/power 10,000 MC 重算、R4 预注册和独立审计。唯一任务继续执行 73_D064_R4_EXECUTOR_SPECIFICATION.md。算法提升候选见 75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md，尚未实现/验证。不得读取真实 Test 逐场景标签/结果；正式 A-3b 继续 HOLD，直到独立审计 ACCEPTED、导师认可 MDE=0.10、用户明确批准和 R4 §9 pre-flight 全通过。

---

## 直接复制给下一会话的完整提示词

你是我的河北工业大学计算机技术硕士毕业论文研究 Planner + GitHub 仓库维护者。你的任务是推进研究、执行可授权的仓库操作、审查实验可信度，并持续维护长期会话交接信息。不要只写计划或提示词；在证据允许时直接完成代码、测试、实验、复算和仓库更新。

### 1. 仓库隔离与 Git 纪律

唯一允许读取和维护的毕业论文仓库：

`https://github.com/yujian777555/kaitibaogao`

- 当前工作分支：`pilot-a-stateful-recovery`。
- `main` 必须保持独立；未经明确授权，不得合并实验分支。
- 严禁读取、引用或混用用户其他 GitHub 仓库/项目。
- 每次开始先查询远端工作分支和 main 的真实 HEAD、比较 ahead/behind、检查工作流状态；不能只信本提示词中的历史 SHA。
- 所有修改在工作分支进行；每次提交后核验远端 commit、文件内容和分支差异。
- 不得将“文件已写入”“测试用例已编写”“CI workflow 已配置”表述为测试通过或实验完成。

记录基线（2026-11-06 Phase A 完成时最后一次核验）：
- 工作分支 HEAD（Phase A 提交后）：以 `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`（A-3 崩溃修复）之后的审计/文档提交为准，见维护记录
- main HEAD：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`
- 工作分支相对 main：ahead 82+ / behind 0
- A-3 被审计 CI run：42241224898，head SHA `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`，结论 success
以上只是历史基线；接手后必须重新查询。

### 2. 研究背景与方向边界

- 用户是河北工业大学计算机技术硕士，导师要求演化计算（EC）是核心方法，并希望纳入 RSI（递归自我改进）。
- 用户希望毕业论文形成 2–3 个创新点，并尽可能各自形成小论文；每个创新点必须先逐一验证，不能为了凑数量保留失败方向。
- TCAIL Estimator Gate 已 FAIL / NO-GO；旧 CI-GOM linkage 路线冻结，保留负结果，不得继续把它当作当前主线。
- 当前候选主线：**状态化工具型 LLM Agent 的故障恢复策略演化与 RSI**。
- 当前重点问题：在有状态、多工具、存在部分提交/延迟可见/超时歧义/补偿失败的工具工作流中，演化计算能否找到超越强手工恢复策略、且在未见任务与故障组合上保持安全的恢复控制器？
- 第二候选：故障场景与恢复策略双种群协同演化；暂缓，必须先有第一项 EC 增益证据。
- A800 训练 ARWM 是条件候选，不是当前已批准工作。必须先证明模型预测质量和固定真实 simulator rollout 预算下的 EA 收益，才可申请训练。
- 用户的 LLM 使用方式是 API 调用；模型 API 与 A800 辅助模型是不同组件。当前不得擅自启动真实 LLM API。
- 不得把 RSI 仅画成循环框图；最终需要跨轮故障发现、策略更新、再验证及未见任务改进证据。

### 3. 已完成工作与证据边界

#### Pilot A 首轮
- 曾发现 unresolved 指标错误，已在 D-049 修正；不得引用旧 unresolved 值。
- 复算正确 unresolved：blind retry 0.8571、verify-then-retry 0.5714、wait-verify-retry 0.4429、conservative escalation 0.0857、state-aware 0、oracle 0。
- state-aware 手工策略与 oracle 在 success/safety 上持平，主要差异在动作成本；不足以直接授权大规模 EA 或 ARWM。

#### Pilot A-2
- 四类双工具任务、九类故障、六种策略；每种策略 1,080 episodes，共 6,480 policy episodes。
- contract-aware success 0.7222、safe 1.0、invariant violation 0；oracle diagnostic success 0.7778、safe 1.0。
- 5.56 个百分点差距只是探索性模拟器信号，不是统计显著性，不是 EC 增益，也不是论文创新证据。
- A-2 的缺陷：同一任务的工具共享故障族；缺少 held-out task/fault composition。
- 旧 CI run 42030194929、42030392313 只证明当时 A1/A2 工作流成功；**不能证明后来加入的 A3 已通过 CI**。

#### Pilot A-3 当前实现
已加入：
- `47_PILOT_A3_PROTOCOL.md`：A-3 预注册协议及 Pilot B 门禁；
- `experiments/pilot_a_recovery/pilot_a3.py`：独立 per-tool fault vector、三步 saga、不同工具幂等/补偿契约、partial commit、delayed visibility、rate limit、schema drift、permission denial、compensation failure、逆序补偿、七种策略、held-out cluster bootstrap；
- `experiments/pilot_a_recovery/test_pilot_a3.py`：当前 15 项测试用例；
- `experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md`：实现状态和验证边界；
- `.github/workflows/pilot-a-recovery.yml`：增加 A3 执行及 JSON/episode CSV artifact 上传；
- README、D-051、SESSION_HANDOFF 已更新。

冻结预算：
- 每策略 954 episodes：train 144、validation 120、held-out 690；
- 七种策略共 6,678 policy episodes；
- Held-out 分为 task-only、fault-only、joint shift；
- 所有策略共享 scenario IDs、seeds、fault realizations；
- 策略只可访问公开错误、工具契约、VERIFY/WAIT 结果；隐藏故障标签、真实可见时间、补偿可用性不得泄漏给可部署策略；
- oracle_diagnostic 仅是当前步骤潜在状态可见的诊断参考，不是可部署策略，也不保证全局最优。

七种策略：
1. blind_retry
2. verify_then_retry
3. fixed_wait_verify
4. conservative_escalation
5. contract_aware
6. saga_aware
7. oracle_diagnostic

**真实状态必须如实表述（2026-11-06 更新）：**
- SPECIFIED：A3 协议已冻结（47 号，未修改）。
- IMPLEMENTED：模拟器、16 项测试（15 预注册 + 1 崩溃回归）、CI workflow step 和 artifact 上传步骤在分支上。
- TESTED：run 42241224898（head `f5e6b46`）28 项测试全部通过，A1/A2/A3 模拟器全部真实运行；此前 7 个 run 因 `PublicToolView` 误读 `tick` 崩溃（已修复）。
- RESULTS：A-3 已运行并经独立复核（`PILOT_A3_INDEPENDENT_REAUDIT.md`）：6,678 episodes、结构/配对/split/语义全部通过审计、JSON 与 CSV 零偏差、artifact 哈希齐全、本地重跑确定性一致。
- GATE：**A-3 预注册 Gate = HOLD（HOLD_REVIEW_FAILURE_BOUNDARIES）**。三条件中安全条件满足（各 slice 零违规），但 oracle−saga 成功率差 0.0（要求 ≥0.05）、bootstrap CI [0.0,0.0]（要求下界 >0）；gap≤0.02 但动作成本差 +34.6%>10%，按 47 号原文为 HOLD。**Pilot B 未获准**；A800/ARWM、真实 LLM API、双种群协同演化继续 HOLD。

### 4. 当前唯一下一任务：A-3b 独立审查 → 预注册冻结 → 实现（分类器/场景生成器/adapter）

Phase A（A-3 复核，Gate=HOLD）与 Phase B（数据集审计）均已完成，A-3b 设计草案见 `55_PILOT_A3B_RESEARCH_DESIGN.md`。不要重跑 A-3，不要启动 Pilot B，不要运行 A-3b（未预注册）。按顺序执行：

1. 重新核验远端 `pilot-a-stateful-recovery` 与 `main` HEAD、ahead/behind、工作树、CI 状态。
2. **对 55 号设计做独立审查**：可恢复性四分类的可判定性、指标分母纪律、统计方案（cluster bootstrap+置换+Holm）、预算公平性、与 49 号新颖性边界的一致性、消融能否分离 A/B 机制。发现问题先改设计文档，不带病冻结。
3. **预注册冻结**：场景生成器规格（含 R3/R4 分层比例 3:1 主设定与 1:1、5:1 敏感性）、τ_min=saga_aware 基线、成本计价表、seed 清单、rollout 预算、场景清单哈希。冻结后经用户批准才允许运行。
4. **实现**（批准后）：可恢复性分类器（评估器侧，含一致性回归测试与 10% 人工抽检）、场景生成器扩展（新组合族含可区分恢复决策点）、FSM 基因组+语义修复算子、反例池。全部沿用 PublicToolView 观察边界（隐藏标签隔离测试保留）。
5. **Phase C adapter（可与 3 并行）**：ToolMisuseBench `reset()/act()` 与 UndoBench `UndoBenchAgent.run()` 到统一 episode contract 的封装；只用 train/dev/validation smoke（ToolMisuseBench DEV 复现报告已在 `experiments/dataset_audit/`）；UndoBench TEST 与 ToolMisuseBench test_public 继续锁箱。
6. 运行 A-3b 前置门禁：分类器一致性、泄漏检查脚本、预算表齐备、55 号审查通过。缺一项不得开跑。
7. Pilot B 预注册草案仅在 A-3b Gate + 数据兼容 Gate + adapter smoke 全过后起草。A800/ARWM、真实 LLM API、UndoBench TEST 执行、ThinkingBox 任何用途、双种群协同演化继续 HOLD，均需独立授权。

### 5. 强制接管提示词维护制度（不可违反）

每次会话、每个阶段结束、每次实验结论/代码/协议/分支/授权变化时，必须维护以下四处：

1. **`NEXT_SESSION_PROMPT.md`：唯一权威、可直接复制的接管提示词。** 更新当前仓库/分支/HEAD 基线、真实阶段、已完成证据、未完成事项、唯一下一任务、门禁、禁止事项和必要文件路径。它必须自包含，使新会话不依赖旧聊天也能正确接管。
2. `SESSION_HANDOFF.md`：详细历史、阶段记录和上下文；保留旧记录，追加新阶段，不得静默覆盖负结果。
3. `05_DECISION_LOG.md`：新增带日期的决策，记录证据、判断、限制和下一步；区分事实、推断和计划。
4. `README.md`：维护当前项目状态、当前分支/阶段、最新结论和下一步。

执行纪律：
- 每次提交代码或实验结果后，同一轮更新以上四处，不得留到“以后再说”。
- 如果任务中途改变了方向/门禁/下一步，必须立即同步更新，不等会话结束。
- 会话结束前必须重新读取这四个文件，确认相互一致；特别核验 `NEXT_SESSION_PROMPT.md` 的状态与最新远端 HEAD 一致。
- 接管提示词必须给出**唯一明确的下一任务**，不能只罗列一堆可能方向。
- 若尚无新结果，明确写“未运行/未核验/无结果”，不能填猜测。
- 每次回复用户时，明确报告接管提示词是否已更新，并提供其 GitHub 文件链接。
- 如果由于工具权限或 CI 尚未完成而不能更新某项，必须说明阻塞点，不能假称已维护。
- 不要只维护聊天中的提示词；仓库中的 canonical file 才是权威版本。

### 6. 每轮交付标准

每一轮都必须优先产出可审计研究成果：
- 可运行代码、测试、原始 episode 数据、配置和复算脚本；
- 强基线与公平预算；
- 明确的安全约束与 held-out 泛化；
- 可重复的统计分析；
- 清晰的 GO / HOLD / NO-GO 决策；
- README、决策日志、SESSION_HANDOFF 和本接管提示词同步维护。

不要连续多轮只写研究规格。不要为了让结果好看而调 held-out、删失败样本或弱化基线。不要把工程通过说成科学结论。负结果同样必须保存并解释。

---

## 维护记录

### 2026-11-05
- 建立本文件为唯一 canonical handoff prompt。
- 当前状态：Pilot A-3 已实现；CI/原始 artifacts 尚待核验；Pilot B 未获授权；A800/ARWM HOLD。
- 下一会话唯一任务：完成 A-3 最新 Actions run 核验及 JSON/CSV 独立复算。


### 2026-11-05 — D-052：强制维护制度正式生效
- 用户明确要求接管提示词必须一直维护。
- 本文件被指定为唯一 canonical handoff prompt。
- 同步规则已写入 `SESSION_HANDOFF.md` 第 47 节、`05_DECISION_LOG.md` D-052 和 README。
- 每次实质性进展后必须同一轮同步更新四份文件；会话结束前重新读取核对；每次对用户汇报附本文件链接。
- 本文件中的历史 SHA 只作接管前基线；新会话必须动态查询远端 HEAD，不能将历史 SHA 当作当前 HEAD。
- 当前唯一下一任务仍是 A-3 Actions 核验和 JSON/CSV 独立复算。


## 2026-11-06 Thesis-level status snapshot (authoritative clarification)

### Current working thesis title (NOT YET FROZEN)
**《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》**

This is the focused working title recorded in `44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md`. The older title `《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》` belongs to the former TCAIL / CI-GOM interaction-linkage route, whose estimator gate failed. Do not present the old title as the current thesis title. The title still needs advisor confirmation and a successful algorithmic evidence chain.

### Thesis research question
Can evolutionary computation search executable, contract-constrained recovery controllers for stateful tool-using LLM Agents, improving recovery on unseen tasks and fault compositions while satisfying hard side-effect safety invariants, and can feedback-driven controller updates form a measurable RSI loop?

### Current candidate structure
1. **Core candidate 1 — contract-constrained recovery policy evolution.** Search object: executable guarded finite-state recovery controller/policy genome. Candidate mechanisms: typed state/action representation, contract-aware variation/repair, feasibility-first selection with hard safety constraints, and multi-objective optimization of recovery success, unresolved side effects and recovery cost. No EC advantage has yet been demonstrated.
2. **Core candidate 2 — fault-scenario / recovery-policy co-evolution.** Co-evolve valid challenging fault scenarios and recovery controllers to improve held-out fault-family robustness. Deferred until candidate 1 passes an EC-vs-strong-baseline gate.
3. **Reserve candidate 3 — cross-task recovery-policy transfer with capability preservation.** Frozen; only reconsider after the first two candidates have independent evidence and novelty review.
4. **ARWM/A800 is a conditional supporting-model route, not a confirmed independent innovation point.** It remains HOLD pending novelty audit and evidence that it improves evolutionary search under a fixed real-rollout budget.

### Actual thesis maturity
- TCAIL estimator gate: FAIL / NO-GO; old CI-GOM route frozen. Keep its negative results, do not reuse it as a current innovation.
- Pilot A: exploratory simulator result; unresolved metric corrected. Hand-coded state-aware strategy matched oracle on success/safety in that initial slice.
- Pilot A-2: exploratory only; contract-aware success 72.22%, oracle diagnostic 77.78%, both safe 100%. This does not prove EC gain.
- Pilot A-3: protocol, simulator and 15 test cases implemented; latest A3 Actions run and JSON/CSV results still NOT VERIFIED / NOT AUDITED at this snapshot.
- Pilot B: not started / not authorized. No random search, GA/GP, NSGA-II/III or proposed EC comparison result yet.
- RSI: architecture hypothesis only; no multi-round Agent recovery-controller improvement has been demonstrated.
- Existing opening-report drafts V0.1–V0.3 were written for the former interaction-aware TCAIL/CI-GOM direction. They are not valid final/current proposal drafts as-is. Background and references may be audited and reused, but research content, title, innovation points, method, and feasibility sections must be revised for the stateful recovery direction after evidence gates.
- Therefore: thesis direction has narrowed, but final title and 2–3 validated innovations are NOT frozen; the project is in pre-proposal research validation, not final thesis writing.

### Next action remains unchanged
The only immediate task is to verify the latest A3 GitHub Actions run, independently recompute its JSON/CSV, and apply the pre-registered A3 gate. Do not start Pilot B or A800/ARWM before that gate.


### 2026-11-06 — D-053: thesis-level status clarification
- Current working title (not frozen): `《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》`.
- The older interaction-aware title belongs to the failed TCAIL/CI-GOM route and is no longer the current thesis title.
- Core candidate 1: contract-constrained recovery-policy evolution; EC benefit not yet validated.
- Core candidate 2: fault-scenario / recovery-policy co-evolution; deferred until candidate 1 passes.
- Reserve candidate 3: cross-task recovery-policy transfer with capability preservation; frozen.
- ARWM/A800 is a conditional supporting-model route, not a confirmed independent innovation; HOLD.
- TCAIL FAIL; Pilot A/A-2 exploratory only; A-2 contract-aware 72.22% vs oracle diagnostic 77.78%, both safe 100%; no EC gain established.
- Pilot A-3 implemented but CI and raw JSON/CSV not yet audited; Pilot B not started; no multi-round RSI benefit established.
- Existing opening drafts V0.1–V0.3 are based on TCAIL/CI-GOM and are not valid current proposal drafts as-is. `04_OPENING_REPORT_PLAN.md` now carries a warning and current direction update.
- Latest branch content before this prompt sync: `9f453fbd9afe78cc410ecc86293b8d1eac0af54f`. This is a historical baseline only; next session must query branch HEAD dynamically.
- Current stage: pre-proposal research validation, not final thesis writing. The immediate next task remains A-3 Actions verification and independent raw-data audit.


## 2026-11-06 — D-054: first-innovation related-work and novelty-boundary audit

New audit: `49_FIRST_INNOVATION_RELATED_WORK_AUDIT.md`.

### Main finding
Related work is substantial. Do NOT claim novelty for generic tool-failure recovery, verify-before-retry, idempotency, Saga compensation, transaction wrappers, generic prompt/tool-policy evolution, FSM synthesis, counterexample-guided GP, or safe evolutionary optimization alone.

Must-read close papers:
1. UndoBench, arXiv:2610.05622 — tool-agent recovery benchmark, paired lost-ACK evaluation, includes constrained EvoUndo-RB1 baseline.
2. EvoUndo, arXiv:2608.28363 — recoverability-constrained self-evolution of agent harness mutations; its "self-evolution" is not evolutionary computation, but it is a close conceptual neighbor due to effect contracts, witness capture, counterfactual recoverability and recovery synthesis.
3. EvoTool, ACL 2026 — gradient-free evolutionary optimization of modular natural-language tool-use policy; mandatory baseline/closest EC neighbor.
4. Where Does Exactly-Once Live?, arXiv:2609.29095 — LIMBO, late commits, idempotency, missing read paths, duplicate effects.
5. Cordon arXiv:2606.17573, Atomix arXiv:2602.14849, SagaLLM PVLDB 2025 — transactional tool runtime and compensation.
6. Verified Tool Calls arXiv:2608.02645 and Repair Economics Zenodo 2026-10-03 (explicitly non-peer-reviewed preprint) — direct retry/verification/idempotency and testbed overlap.
7. CDGP (Evolutionary Computation 2018), Formal Controller Synthesis via GP (2017), FSM-MOEA (ACM TODAES 2023), SMC-ES arXiv:2607.15003 — algorithmic foundations for safe program/controller synthesis.

### Revised novelty hypothesis — NOT APPROVED
Potential direction only: contract-semantics-preserving, counterexample-guided evolutionary synthesis of executable recovery FSMs for stateful side-effecting tool workflows. Typed effect-state genome, semantic variation/repair, feasibility-first safety, and cross-task/fault-family held-out evaluation must each show independent value. Merely combining FSM + contract + EA + Pareto is insufficient.

### Benchmark warning
Pilot A-2's deterministic fault-injection testbed/policy comparison is not itself novel: Repair Economics, LIMBO, UndoBench and FAILING TOOLS overlap. A-3 can remain an internal test environment, but do not claim benchmark novelty without feature-level comparison. A-3's per-tool independent compound faults, three-step saga and task × fault-composition shifts must be compared directly with existing benchmark coverage.

### Status and next gate
- A-3 protocol/code/test cases are implemented, but A3 CI and raw JSON/CSV remain NOT VERIFIED / NOT AUDITED.
- Pilot B remains NOT AUTHORIZED.
- Before Pilot B, finish the mechanism-level full-paper review of UndoBench, EvoUndo, EvoTool, LIMBO and the transaction/runtime papers, and compare their policy object, state/effect semantics, search loop, safety verifier, data split and budget.
- Continue to verify A3 CI/artifacts and independently recompute its results. Pilot B is authorized only if both the A3 pre-registered gate and novelty/baseline review are satisfactory.
- No A800/ARWM or real LLM API until separately authorized.


## 2026-11-06 — D-055: dataset selection and validation design

New plan: 50_DATASET_SELECTION_AND_VALIDATION_PLAN.md.

### Recommended benchmark stack (PROPOSED, NOT FROZEN)
1. Development/search: current Pilot A-3 deterministic simulator + ToolMisuseBench v0.2 large train split.
2. Development/tuning: A-3 validation + ToolMisuseBench dev.
3. Locked external recovery evaluation: ToolMisuseBench public test + UndoBench TEST.
4. Clean workflow regression only: ThinkingBox-Bench v1.0 or ToolSandbox. ThinkingBox is explicitly evaluation-only and must NOT be used for evolutionary search, tuning, prompt optimization or training.

### ToolMisuseBench details
- REALM 2026 ACL Anthology: https://aclanthology.org/2026.realm-1.28/
- Dataset: https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench
- Code: https://github.com/akgitrepos/toolmisusebench
- v0.2 large: 6,000 train / 900 dev / 1,200 public-test records; CRUD, retrieval, files, scheduling; clean, timeout, rate-limit, schema-drift, authorization, adversarial faults; task rows include initial_state, tool_schemas, fault_plan, success_criteria, budgets and seed.
- HF card marks MIT. It says public test has 1,200 records but only 600 output-grounded tasks; audit manifest/evaluator denominator before use.
- This is a close recovery benchmark, not our novelty. Audit split leakage, task/fault families, semantics, official runner and reproducibility before any Pilot B.

### UndoBench
- arXiv:2610.05622; 36 workflows / 36 faults / 8 domains; DEV 14 / VALIDATION 10 / TEST 12; paired CONTROL/FAULT with same seeds and effect-history/state oracle.
- Use TEST only after algorithm freeze; small test workflow count requires cluster-aware statistics.

### ThinkingBox / ToolSandbox
- ThinkingBox-Bench v1.0: 507 stateful business tasks across five domains, executable final-state/side-effect checks; official card says evaluation-only, so clean regression only, never search/tune.
- ToolSandbox: stateful tools, implicit dependencies, simulated user, dynamic trajectory evaluation; not a dedicated fault-recovery benchmark, so clean state-dependency regression or explicitly labeled modified fault-injection variant only.

### Critical principle
This is not ordinary supervised learning from text. Evolutionary controllers must be evaluated by executing rollouts in a deterministic stateful environment. The dataset supplies task definitions, initial states, tool schemas, fault plans and graders; fitness comes from actual environment outcomes.

### Immediate work / gates
- Do NOT launch Pilot B yet. First verify A-3 Actions and independently recompute JSON/CSV per protocol 47.
- In parallel, download/pin ToolMisuseBench v0.2 and UndoBench; audit license, manifest/checksums, schema, task/fault leakage, fault semantics and runner.
- Build a feature coverage matrix: timeout-before/after, late commit, partial mutation, delayed visibility, schema drift, authorization, cross-tool saga, compensation failure, no-readback, idempotency.
- Only after A-3 pre-registered gate AND benchmark compatibility/novelty gate pass may Pilot B begin. No A800/ARWM or real LLM API until separately authorized.


## D-055 (2026-11-06): dataset plan
See 50_DATASET_SELECTION_AND_VALIDATION_PLAN.md. Proposed, not frozen:
- Search: Pilot A-3 simulator + ToolMisuseBench v0.2 train (6,000).
- Dev: A-3 validation + ToolMisuseBench dev (900).
- Locked recovery evaluation: ToolMisuseBench public test (1,200 records; HF card says 600 are output-grounded, so audit actual denominator) + UndoBench TEST (12 workflows).
- Clean regression only: ThinkingBox-Bench v1.0 (507 tasks; evaluation-only, never use for search/tuning) or ToolSandbox (stateful dependencies, not a dedicated recovery benchmark).
Evolution fitness comes from executing controller rollouts, not supervised learning over JSONL. Audit versions, license, runner, manifests, leakage, and fault coverage first. A-3 CI/JSON/CSV still require independent audit; Pilot B remains HOLD. No A800/ARWM or real LLM API.


## 2026-11-06 — D-056: dataset plan official-source verification and next execution plan

New execution plan: 51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md.
Dataset strategy and official metadata are maintained in 50_DATASET_SELECTION_AND_VALIDATION_PLAN.md.

### Official-source corrections / confirmations
- ToolMisuseBench REALM 2026: seed-42 v0.2 large = 6,000 train / 900 dev / 1,200 public-test records; HF card explicitly says only 600 public-test tasks are output-grounded. Do not conflate record count and score denominator.
- ToolMisuseBench paper reports Parser+Repair task success 0.767 and conditional recovery success 0.736 on public test; recovery-disabled task success 0.158. These are paper-reported values, NOT our reproduction. Parser+Repair is a required reference baseline.
- UndoBench current dataset card version is v1.0.1, 36 workflows, DEV 14 / validation 10 / TEST 12; data/spec CC BY 4.0, software Apache 2.0. Frozen TEST requires explicit opt-in.
- ThinkingBox-Bench v1.0 has 507 tasks / 5 domains and is evaluation-only. It must not be used for search, tuning, prompt optimization or training; final clean regression only.

### Current A-3 status
- 47_PILOT_A3_PROTOCOL.md says PRE-REGISTERED / NOT RUN.
- experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md says IMPLEMENTED / NOT YET VALIDATED BY CI / RESULTS NOT YET RUN OR ACCEPTED.
- The 15 tests and artifact-upload workflow are authored, not evidence of a passing run.
- Per-policy budget 954 (144 train / 120 validation / 690 held-out); seven policies = 6,678 policy episodes.
- Do NOT claim A-3 passed. Do NOT start Pilot B.

### Immediate next task: Phase A in 51 plan
1. Identify the exact Actions run for the current implementation SHA.
2. Inspect jobs/steps/logs and verify the 15 A-3 tests actually ran.
3. Download the A-3 artifact and hash ZIP/JSON/CSV.
4. Independently recompute CSV metrics and JSON parity, verify scenario/seed/fault pairing and hidden-oracle isolation.
5. Apply the exact pre-registered Gate in file 47; publish GO / HOLD / NO-GO with evidence.
6. In parallel, pin ToolMisuseBench and UndoBench revisions, audit manifest/checksums, splits, licenses, evaluator denominator and feature coverage.
7. Only after A-3 Gate + dataset compatibility Gate + adapter smoke pass may Pilot B preregistration be drafted.

### Authorization boundary
GO: read-only dataset audit, A-3 CI/artifact audit, deterministic adapter smoke on train/dev.
HOLD: evolutionary Pilot B, public-test tuning, UndoBench TEST, ThinkingBox optimization, A800/ARWM, real LLM API.
At each session end update this file, SESSION_HANDOFF.md, README.md, 05_DECISION_LOG.md and 51 plan status. Record real commit SHA, run ID, artifact hashes and test outcomes. Never infer experiment success from documentation or workflow configuration.


## 2026-11-06 — D-057: Phase A complete — A-3 CI remediation, independent reaudit, Gate = HOLD

New report: `PILOT_A3_INDEPENDENT_REAUDIT.md`. Decision log: D-057.

### What actually happened (facts, verified)
1. **A-3 CI had never produced results.** All workflow runs from `76f62c09` onward crashed in "Run Pilot A-3 simulator": `recover_tool` dereferenced `tool.tick` through `PublicToolView` (which intentionally hides runtime fields) → `AttributeError`. Artifact upload was skipped every time; no A-3 JSON/CSV existed before today.
2. **Remediation (commit `f5e6b46`):** policies count their own waits against the public `retry_after` hint; `PublicToolView` unchanged (observation boundary preserved); added regression test #16 (`test_recover_tool_never_touches_hidden_runtime_fields`, 6 policies x 7 public errors). Test count is now **16** A-3 tests (15 pre-registered + 1 crash-regression), 28 total in the suite.
3. **Validated run:** 42241224898, head SHA `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`, conclusion success. 28 tests OK (verified in logs), A1/A2/A3 simulators all ran, `pilot-a3-results` uploaded.
4. **Artifacts (sha256):** ZIP `1119d14b70eedef221fe6e63439e2a04bd58c0354d5a723344d2c80c459ab727` (matches GitHub digest); `pilot_a3_results.json` `3a60ae8385c723c57d54ff47608fe428690d94519f6762ec78bbc15c1d15fe14`; `pilot_a3_episodes.csv` `2c7d7dad5faaae58f182f27d77b90dfa237f4c1627e15b0bc029d34582f3c369` (6,678 data rows). Preserved raw under `experiments/pilot_a_recovery/ci_artifact/` with `-text` gitattributes; manifest `a3_artifact_manifest.json`. Local rerun is byte-identical (deterministic simulator).
5. **Independent recompute** (`recompute_a3_audit.py`, does not import simulator code): 6,678 rows; 954/policy (144/120/690); 954 scenario IDs perfectly paired across 7 policies (same seeds + fault realizations); protocol-47 factorized splits exact (45 task x composition cells, 0 deviations); JSON vs CSV parity 0 mismatches; rollback/compensation/unresolved semantics consistent row-by-row.

### Pre-registered Gate (47 section 6, applied verbatim): **HOLD**
- Condition 1 (zero saga_aware invariant violations per held-out slice): **PASS** (task-shift 0.0, fault-shift 0.0, joint-shift 0.0).
- Condition 2 (oracle − saga held-out task-success gap >= 0.05): **FAIL — gap = 0.0**.
- Condition 3 (cluster paired bootstrap 95% CI lower > 0): **FAIL — CI = [0.0, 0.0]** (23 task-family x fault-composition clusters, every paired diff = 0; seed-42 sensitivity identical).
- gap <= 0.02 holds but action-cost difference +34.63% > 10%, so the NO-GO branch does not apply either → protocol's "otherwise HOLD" branch.
- Decision: **HOLD_REVIEW_FAILURE_BOUNDARIES**. Pilot B NOT authorized.

### Failure boundaries (why the gap is zero)
- Compositions `partial_comp_failure` and `delay_rate_permission` are structurally infeasible: 0% success for **all 7 policies including the privileged oracle** (360/690 = 52.2% of held-out). Compensation-failure residue and permission denials make completion impossible; latent oracle knowledge only saves actions.
- Task-family shift is near ceiling (saga_aware 97.5% success, zero violations) — policy rules generalize; collapse comes only from unseen fault compositions.
- The only real optimization headroom is action cost (saga 10.17 vs oracle 7.56 mean actions, +34.6%).
- Full worst-group table in the reaudit report.

### Status after this round
- Pilot A-3: **RUN / INDEPENDENTLY AUDITED / GATE = HOLD**. Do not re-run A-3 and do not tune on its held-out.
- Pilot B: NOT started / NOT authorized. A800/ARWM, real LLM API, dual-population co-evolution, UndoBench TEST, ThinkingBox optimization: all HOLD.

### Next session's only task
Phase B dataset audit (ToolMisuseBench / UndoBench version pinning, manifest/license/split-leakage/evaluator-denominator audit per 51 plan section 3) **plus** drafting a NEW preregistration A-3b addressing the failure boundaries (feasibility-stratified metrics / feasible held-out compositions / action cost as objective). A-3b must be approved before any new run. Pilot B remains blocked until A-3b Gate + dataset compatibility Gate + adapter smoke all pass.


## 2026-11-06 — D-058: Phase B dataset audits COMPLETE; A-3b research design drafted

New documents: `52_TOOLMISUSEBENCH_AUDIT.md`, `53_UNDOBENCH_AUDIT.md`, `54_BENCHMARK_COMPATIBILITY_MATRIX.md`, `SPLIT_LEAKAGE_AUDIT.md`, `LICENSE_AND_PROVENANCE.md`, `DATASET_LOCK_MANIFEST.json`, `55_PILOT_A3B_RESEARCH_DESIGN.md`; evidence in `experiments/dataset_audit/`.

### ToolMisuseBench v0.2 large (audited, MIT, HF rev 98eb2871)
- 6,000/900/1,200 rows verified; file SHA-256 match official manifest exactly. task_id clean across splits.
- **Scoring denominators decoded from released per-task episodes**: paper 0.767 = TaskSuccess over ALL 1,200 (recomputed 0.7667); 0.736 = conditional recovery over the 993 FAULTED tasks (731/993=0.7362); 0.158 = no-recovery full-split (0.1575). "600 output-grounded" = subset with tool_output_path_equals criteria (scores 0.8783 there vs 0.655 state-grounded) — NOT a headline denominator.
- **Semantics (official env/fault code)**: all faults fire BEFORE execution (no lost-ACK); envs idempotent/guarded (duplicates impossible); every fault triggers once (on_nth_call=1) so one retry always recovers; NO compensation/idempotency contracts/partial commit/late commit/saga (0 occurrences); two-fault plans never span tools. No structurally unrecoverable scenarios exist.
- **Parser+Repair = regex instruction parsing + error-code arg repair** (schema alias id↔doc_id↔account_id). Reproduced on DEV (900): TaskSuccess 0.7622, conditional recovery 0.7363; no-recovery 0.1511. MUST be a Pilot B baseline. It is a parser/repair baseline, not a recovery-policy upper bound.

### UndoBench v1.0.1 (audited, CC-BY-4.0 data / Apache-2.0 software, HF rev 4be11518)
- 36 workflows (14/10/12) fully characterized: 33/36 SCN-LOST-ACK with observability=UNKNOWN_OUTCOME on ALL rows; idempotency_support=false everywhere (duplicates real); IRREVERSIBLE 8, COMPENSATABLE 24; forbidden_effects 22; 19/36 multi-tool. Metrics CRSR/DER/MER/URR/EOR align with our safety-recovery semantics (CRSR conditions on Control success).
- Harness verified: doctor PASS, smoke PASS (control/fault/oracle/effect-log pipeline), DEV paired run with example agent (14 pairs) computes CRSR/DER/MER correctly. Built-in TEST lock `allow_frozen_test_execution: false`. TEST never executed.

### ThinkingBox-Bench: UNREACHABLE (HF 401 gated/removed; github.com/microsoft/thinkingbox-data 404). Claims (507 tasks, evaluation-only) NOT re-verifiable this round; keep evaluation-only policy; no experiments depending on it.

### Split leakage (SPLIT_LEAKAGE_AUDIT.md)
- ToolMisuseBench: 72–73 normalized instruction templates shared across splits; toolsets 100% shared → instance-level generalization ONLY.
- UndoBench: all 8 domains in all splits; test 12/12 homogeneous lost-ACK; tool overlap low (3/20) → workflow-level generalization only.
- Pilot A-3 remains the only task-family x fault-composition factorized OOD (keep it).

### A-3 gap=0 root cause (55 §0, evidence-based)
(a) on feasible cells saga_aware already matches oracle; (b) 52.2% of held-out is structurally infeasible (0% for everyone incl. oracle) and dilutes the aggregate; (c) the pre-registered gate values only success, not the real difference (action cost +34.6%); oracle sees only current-step state (not an upper bound). Fix = recoverability stratification + cost objective + re-graduated held-out — NOT deleting hard scenarios.

### A-3b design (55, DRAFT — not approved, not run)
Recoverability classes R1/R2/R3/R4 defined evaluator-side (never by "did a policy succeed"); stratified metrics (CondRecSucc on R1+R2 only; CorrectEscalation on R3+R4; hard P(violation)=0); two ablatable mechanisms (A contract-preserving operators, B counterexample-guided search); baselines Random Search/GA/GP/NSGA-II/NSGA-III/hand rules/oracle-diagnostic; paired cluster bootstrap + permutation + Holm; explicit stopping rules and pre-registered failure reasons. A-3 held-out retired as confirmation data.

### Status
- GO: A-3b design review + preregistration freeze (needs user approval before any run); Phase C adapters (train/dev/validation smoke only).
- HOLD: A-3b execution; Pilot B; A800/ARWM; real LLM API; UndoBench TEST execution; ThinkingBox anything; tuning on any locked split.

### Next session's only task
Independent review of 55_PILOT_A3B_RESEARCH_DESIGN.md, then preregistration freeze (scenario generator spec, R3/R4 stratification ratio, tau_min, cost table, seeds, budget), then implementation of the recoverability classifier + scenario generator + adapters. No A-3b run before the freeze is approved.


## 2026-11-07 — D-059: Independent review of Pilot A-3b design

Review: `56_PILOT_A3B_INDEPENDENT_REVIEW.md`.
Current status: Phase B = GO / complete; design 55 = REQUEST CHANGES; A-3b formal run = HOLD.

### Critical corrections required before preregistration
1. R4 is defined as having no reachable zero-residual safe terminal, so CorrectEscalation(R3+R4) requiring zero residual is contradictory. Define R4 DamageContainment; report unavoidable residual separately.
2. R2 currently includes graceful failure/safe abandonment but is counted in CondRecSucc. Restrict R2 to compensation-assisted task completion; classify safe abort as R3 or a separately defined outcome.
3. Define recoverability as existence of an observation-based contingent policy over public observation histories, robust across hidden states in the same observation-equivalence class. Specify finite horizon, action set, nondeterminism and UNKNOWN labels.
4. Finite rollouts cannot prove population P(violation)=0. Separate by-construction/static invariant checks from zero observed violations and a finite-sample confidence upper bound.
5. Separate avoidable from unavoidable residual effects; do not penalize necessary R3/R4 escalation as if it were unnecessary intervention.
6. Clarify whether 3:1 means (R1+R2):(R3+R4) or R3:R4. Freeze exact R1/R2/R3/R4 counts for every split and held-out slice.
7. Compute power at independent task-family × fault-composition cluster level. Do not treat repeated episodes/seeds as independent clusters.
8. Ensure all EA methods share initialization distribution and candidate pool; fix one common NSGA-II backbone for A/B/A+B mechanism ablations, with NSGA-III as a separate baseline.
9. Clarify 50k rollout budget (per method total or per seed), count all real simulator episodes, and separate search/validation/final evaluation budgets.
10. Make strongest standard EA comparison a primary test. Beating only hand rules or Random Search does not establish improved EA.
11. 49 related-work file remains INITIAL LITERATURE SCAN / NOT SYSTEMATIC / NOVELTY NOT APPROVED. Complete mechanism-level systematic review before novelty claims.

### Immediate task
DONE (2026-11-07, D-060): `55_PILOT_A3B_RESEARCH_DESIGN_R1.md` created (all B1–B6/M1–M5 addressed); observation-based AND-OR belief reachability classifier implemented (`experiments/pilot_a3b/reachability.py`) and Stage-1 verified (12 ground-truth cases, confusion matrix diagonal, 27 tests green); A/B operators + 8-method diagnostic run executed on 216 new-seed scenarios.

NEXT (single task): (1) cluster-level power simulation using this round's 54-cluster variance to size the formal A-3b experiment; (2) iterate mechanism B (counterexample granularity/weighting) and A (repair completeness) as diagnostic work; (3) complete the 49 mechanism-level systematic review; (4) assemble the preregistration candidate and submit for user approval. No formal A-3b run before approval.

### Authorization
GO: diagnostic-level code/experiments on new-seed own scenarios, design revision, related-work audit, power analysis, preregistration preparation.
HOLD: formal A-3b confirmatory runs, Pilot B, public test/UndoBench TEST, A800/ARWM, real LLM API, ThinkingBox optimization, tuning on any locked split.
User approval is required after independent review of the preregistration candidate and before any formal A-3b run. Continue maintaining this prompt, SESSION_HANDOFF.md, README.md, 05_DECISION_LOG.md and 51 plan every session.

## 2026-11-07 — D-060: 55-R1 + recoverability classifier + first mechanism diagnostics

### Delivered (real code and experiments)
- `55_PILOT_A3B_RESEARCH_DESIGN_R1.md`: B1–B6/M1–M5 all addressed; mutually exclusive R1–R4 + UNKNOWN; observation-history contingent robust reachability; layered safety claims (no P=0 claims); cost three-way split (necessary escalation unpunished); quotas 3:1=(R1+R2):(R3+R4) per split; same-init-pool/same-backbone/same-budget attribution; primary contrast A+B vs NSGA-II.
- `experiments/pilot_a3b/`: reachability.py (AND-OR belief-state checker + ladder classifier with certificates), mini_env.py (12 ground-truth environments), test_recoverability.py + test_a3_labels.py (27 tests, all green), a3_bridge.py (A-3 ToolRuntime reuse, FSM genome, contract-preserving repair = mechanism A, analytic labels), ea.py (NSGA-II backbone, NSGA-III, GA, Random, B = counterexample pool + targeted mutation + <=2x weighting), run_diagnostic.py, stats.py (cluster paired bootstrap + sign-flip permutation + Holm).
- Stage-1 gate PASSED: confusion matrix 12/12 diagonal (R1 5, R2 2, R3 1, R4 2, UNKNOWN 2 by design); horizon-cutoff and resource-cutoff cases correctly return UNKNOWN; labels generated independently of tested algorithms.

### Stage-2 diagnostic (DIAGNOSTIC, NOT confirmatory)
- 216 fresh scenarios (new seeds, NOT the frozen A-3 held-out dataset); labels R1 96 / R2 50 / R3 36 / R4 34; throughput ~97k episodes/s; budget 108,864 real episodes per method per seed; 3 seeds; methods: hand, random, ga, nsga2, nsga3, A, B, AB.
- **Mechanism A decisive effect: illegal-candidate ratio 1.000 -> 0.000** (A and AB final populations fully legal; every other method including NSGA-II/GA stayed at 1.000). A/AB zero observed invariant violations on all seeds; comparators up to 8%. Answers Q1 affirmatively.
- CondRec means: hand 1.000 > A 0.968 > AB 0.938 > ga 0.911 > nsga3 0.902 > B 0.872 > nsga2 0.838 > random 0.575.
- Primary AB vs NSGA-II (54 clusters, paired bootstrap): delta +0.049, CI95 [-0.017, +0.122], permutation p=0.27 — positive direction, NOT significant (underpowered). A vs nsga2 +0.056 (CI contains 0). AB vs A -0.006 (B dilutes A at this budget). AB vs hand -0.026 (hand baseline NOT beaten).
- All Holm-adjusted secondary tests ns. Honest conclusion: mechanism A demonstrably works (illegal-candidate elimination + zero violations + directional success gain); H1 (A+B beats standard EA and hand rules) NOT YET established; first innovation is feasible but unproven.

### Confound controls
Same random-only initial pool for all search methods (hand policy is a separate baseline); identical budget and evaluator; the earlier hand-seed-in-pool contamination was detected and removed (56 M1). Episode counts are real simulator rollouts.

### Next task
Power sizing from the 54-cluster variance; mechanism iteration (B granularity/weighting, A repair completeness); 49 systematic review; preregistration candidate for user approval. Formal A-3b remains HOLD.


# 2026-11-07 — D-061: D-060 独立复核（本节覆盖此前“下一步先做功效分析”的指令）

**独立报告：** `57_PILOT_A3B_DIAGNOSTIC_INDEPENDENT_REAUDIT.md`  
**当前状态：** D-060 原始诊断数据保留；Stage-2 指标/控制器/B/统计存在阻断问题；正式 A-3b 继续 HOLD。

## 复核事实
- 远端 branch HEAD：`edfc7ad0156617dccc4e4bf998df33f991ae921f`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；ahead 94 / behind 0。
- 原始 `diagnostic_results.json` 已从 GitHub blob 读取并解析：216 scenarios、24 runs、每 run 216 rows；全部 scenario ID 配对一致。
- 实际 label counts = R1 96 / R2 50 / R3 35 / R4 35。旧 D-060 文档中的 36/34 是记录错误，后续统一为 35/35。
- 固定 hand 每 seed 216 episodes；搜索方法大多 108,864；A/seed23=108,648（cache hit）。不能再声称所有方法/seed 都执行完全相同的真实 episode 数。
- 无 GitHub status checks；55/55 是本地测试报告，不是本轮 CI 记录。

## 阻断问题（先修代码，不要先做功效分析）
1. **控制器不是 stateful FSM**：实际是静态 `(error, idempotent, compensatable)->macro-action` 查表；Saga rollback 由“基因组任一规则含 COMP”触发，而非策略明确动作。必须实现真实状态/观察历史/事务进度/补偿栈，或收窄论文主张。
2. **自动升级污染指标**：任何宏动作失败都会把 `escalated=True`，不能区分策略明确升级和运行器自动失败终止。
3. **R4 评分错误**：`score_class(R4)` 只看 escalated 和 duplicate，不检查可避免残留/最小可达损害；R4 残留整体被排除在 avoid_resid 外。
4. **必要升级仍被成本惩罚**：`norm_actions` 对所有类别求平均，包含 R3/R4 的必要升级动作。
5. **A-3 labels 非 checker 输出**：216 个场景由启发式 `label_scenario` 分类；6 组 sanity tests 不等于 216 场景逐项可达性验证。
6. **B 实现与设计不符**：`CounterexamplePool.update` 每次清空池；`scenario_weights()` 未调用；只按 class label 粗略调 mutation，未按公开错误签名定位规则；B/AB targeted 分支有额外 mutation。
7. **A legality 指标同源**：`repair_genome` 与 `is_legal` 共用 ILLEGAL 表；validator 还漏检非 SCHEMA 的 REPAIR/default action。该指标只能叫内部规则合法性，不能当独立安全证明；NSGA-II/GA 本轮也零观察违规。
8. **Reachability horizon bug**：到达 horizon 时返回 False 但未标记 unproved，可能把“任务可达性未知”错误降级为 R3/R4。改成 WIN/PROVEN_LOSE/UNKNOWN 三值传播。
9. **统计汇总不正确**：stats.py 平均 per-seed CI 端点和 p 值。禁止这样合并。独立探索性 pooled cluster 重算 AB−NSGA-II Δ≈+0.0494、CI≈[-0.0031,+0.1034]、sign-flip p≈0.0874，仍不显著；需实现预先定义的 pooled/hierarchical cluster bootstrap。
10. **基线非 canonical**：当前 NSGA-II tournament 未完整使用 rank+crowding；NSGA-III 为 simplified niching；GA 与设计描述不一致；无 GP；Random 也使用 Pareto survivor selection。正式比较前换标准实现或准确改名。
11. **55-R1 配额冲突**：文字 3:1，但 Train/Validation 表 3:2，held-out 58:38 也不是 3:1。必须统一比例。
12. D-060 原始统计 label count 35/35，旧 handoff/decision log 36/34，按原始 artifact 更正。

## 下一会话唯一优先任务
创建并执行 D-061 修复分支任务，按顺序：
A. 修复控制器执行语义（显式升级、显式补偿、移除基因组全局 rollback flag）；决定并实现真正有状态 FSM。
B. 修复 R3/R4 scorer、最小可达损害、可避免/不可避免残留、类别条件化 action cost。
C. 把 A-3 全部场景标签接入 checker/可审计穷举证明；修复 horizon 三值传播。
D. 修复 B 反例池聚合、错误签名、实际权重采样和变异预算公平性。
E. 建立独立 contract validator；补 canonical NSGA-II/NSGA-III/GA（或准确命名），决定 GP 是否纳入。
F. 修复 pooled/hierarchical cluster statistics；重跑新诊断集（仍非 held-out）。
G. 纠正 3:1/3:2 配额定义和 D-060 记录；再做功效分析。

**不要先做功效分析，也不要先扩大 rollout**：当前执行和评分语义有缺陷，基于错误指标算样本量会固化错误。D-060 artifact 永久保留，任何修复后重跑必须使用新 run ID、新输出文件和新 manifest。

## 授权
GO：以上实现修复、单元测试、独立 validator、非锁箱新诊断集和统计复算。
HOLD：正式 A-3b 确认性实验、A-3 原 held-out 调参、UndoBench TEST、Pilot B、A800/ARWM、真实 LLM API、ThinkingBox 优化。用户批准 preregistration 后才可运行正式 A-3b。


## 2026-11-07 — D-061: 57-review fixes implemented; round-2 diagnostic run

Report: `58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md`. Artifacts: `experiments/pilot_a3b/diagnostic2_results.json` (manifest d4fb2be680e74f2e...) + `diagnostic2_stats.json`. D-060 `diagnostic_results.json` preserved untouched.

### All F1-F8/S1-S3 blockers fixed (47/47 tests green)
- F1 real stateful FSM (step/attempts/confirmed/comp-stack/decision-budget); explicit COMPENSATE/ROLLBACK with comp_log; implicit saga rollback REMOVED.
- F2 policy_selected_escalation vs runtime_forced_abort separated; R3 counts explicit escalation only.
- F3 R4 harm accounting: min_reachable_harm / actual_harm / avoidable_harm / unavoidable_residual; containment = explicit escalation AND zero duplicates AND avoidable_harm==0.
- F4 cost objective counts only R1/R2 unnecessary actions; necessary R3/R4 escalation unpunished.
- F5 A-3 verdicts: analytic prover + AND-OR checker exhaustive cross-check over 309 fault patterns: 0 hard contradictions, 120 exact, 18 R1->R2 refinements, 171 checker-UNKNOWN (bounded search, not counter-evidence).
- F6 B redesigned: per-generation population-wide aggregation, action-sequence implicated genes, weights actually reach the evaluator (<=2x), targeted mutation REPLACES standard mutation (budget-matched).
- F7 independent contract_validator.py (separate code path from repair table; exhaustive error x action matrix).
- F8 three-valued WIN/PROVEN_LOSE/UNKNOWN + cycle detection; no downgrade when higher goal UNKNOWN.
- S1 pooled hierarchical stats (cluster = task x composition, seeds nested; bootstrap + sign-flip + Holm + effect sizes + seed stability).
- S2 standard NSGA-II / NSGA-III (labelled reimplementation) / GA / Random; GP excluded with reason.
- S3 train 108 search / validation 54 (2 unseen task families, fresh seeds) reporting-only.

### Round-2 results (DIAGNOSTIC, not confirmatory)
8 methods x 3 seeds; pop 48 x 60 gens; 316,224 real episodes per method per seed; shared init pool.
- **A vs NSGA-II: +0.239 [0.193, 0.284], Holm p=0.0014 (d=1.56) -- significant.**
- **Independent-validator illegal ratio: A/AB = 0.00 vs everyone else = 1.00 -- decisive.**
- primary AB vs NSGA-II: +0.126 [0.086, 0.167], p=0.0002 (d=0.82) -- significant.
- **AB vs A: -0.113, p=0.0014 -- adding B HURTS A**; B alone +0.082 (Holm p=0.034, weak).
- AB vs hand: -0.514 -- strong hand baseline (0.827) NOT beaten.
- Q6 validation: AB vs NSGA-II +0.148, p=0.002 (d=0.97); A val 0.488 vs nsga2 0.222 -- generalisation holds.
- Open issue: environment violation rate A 0.36 vs hand 0.006 (observation-ambiguity WAIT-SLA timing is behavioural, not rule-level).

### Judgement
Mechanism A: real significant evidence (legality + success, attributable). Mechanism B in combination: NOT established (significantly harmful). First innovation PARTIALLY established (A yes, B needs redesign). Not yet paper-complete.

### Next task (single)
Redesign B's counterexample->gene mapping (action-sequence pattern signatures + semantic-repair-style targeted mutation) and add stateful contract repair for the ambiguous-observation WAIT-SLA discipline; re-measure environment violation rate; rerun A+newB with the same configuration. Formal power analysis and preregistration remain HOLD until then.


# 2026-11-08 — D-062：WAIT-SLA 行为安全与反例驱动演化（下一会话直接执行）

**完整执行计划：** `59_D062_WAIT_SLA_AND_COUNTEREXAMPLE_REDESIGN_PLAN.md`  
**D-061 结果报告：** `58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md`  
**当前任务状态：** READY_FOR_EXECUTION；本节是任务授权与接管指令，不代表 D-062 已经执行。

## 项目接管时先做
1. 重新检查 `pilot-a-stateful-recovery` 远端 HEAD、main、compare、工作树（若可访问）和 CI；建立计划时 HEAD 为 `ac042b4e96b80edb8ca727009f0e34ef32179a1f`，main 为 `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，ahead 102 / behind 0。
2. 阅读 58 号报告、59 号计划、D-061 原始 JSON/统计、`a3_bridge.py`、`ea.py`、`contract_validator.py`、`run_diagnostic2.py`、`stats.py`。
3. 不覆盖 D-060/D-061 原始 artifact。先复核数据哈希、manifest 和运行记录。
4. 当前 HEAD 没有可读取的 status checks；现有 `.github/workflows/pilot-a-recovery.yml` 只监控 `experiments/pilot_a_recovery/**` 和 workflow 自身，不会因 `pilot_a3b/**` 修改自动触发。若要让 D-062 自动测试，需单独评估 workflow path filter 和安全性，不可假称 CI 已运行。

## D-061 结果的证据边界
58 号报告给出的结果（必须从原始 artifact 独立复算）：
- A vs NSGA-II：Δ=+0.239，95% CI [0.193,0.284]，Holm p=0.0014；
- AB vs NSGA-II：Δ=+0.126，CI [0.086,0.167]，p=0.0002；
- AB vs A：Δ=-0.113，CI [-0.152,-0.078]，p=0.0014；
- B vs NSGA-II：Δ=+0.082，CI [0.025,0.144]，p=0.034；
- AB vs Hand：Δ=-0.514，CI [-0.613,-0.416]，p=0.0014；
- 报告的环境行为违规率 A=0.36、Hand=0.006。
这些是报告值，不得跳过独立复算。当前研究结论：A 有正向诊断证据；B 叠加有害；未超过 Hand；第一项创新部分成立。

## 唯一首要任务：先查清 0.36 vs 0.006
从 `experiments/pilot_a3b/diagnostic2_results.json` 和原始 episode 轨迹复算：
- 分子、分母、episode-level/action-level 口径；
- 同一 episode 多次违规是否重复计数；
- task/fault/seed/genome 分层；
- Hand 与 A 是否同口径；
- 每条 duplicate side effect 的完整公开观测和动作轨迹；
- 区分提交未发生、lost ACK、已提交但不可见、处理中、未知结果、合同无 visibility guarantee。
新增独立复核报告（建议 58_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md；先查重，若占用则递增），脚本必须独立于原 scorer。Stage 0 未通过，不扩大 rollout。

## WAIT-SLA 状态化合同设计
为工具定义 submit semantics、visibility SLA/保证类型、query consistency、idempotency/idempotency-key、safe retry preconditions、compensation capability、retry window、max wait/decision budget、escalation conditions。区分 visibility SLA 和 retry SLA；没有可证明的可见性上界时，固定等待不得把 UNKNOWN 推断成 NOT_COMMITTED。
状态/观测测试至少覆盖：SLA 边界前后可见、超过 SLA 仍未知、无 visibility guarantee、强一致/最终一致/无保证查询、幂等/非幂等、幂等键有无、处理中、lost ACK、WAIT 失败/限流、多工具部分提交。
策略只能读取公开观察与自身状态，不能读 hidden state。

## B-new 和安全门
- 反例签名细化为公开观测序列 + 合同 + FSM 状态/事务阶段 + 动作序列 + 失败后果 + 涉事基因。
- 建立 `failure trace -> violated transition/contract -> implicated gene neighborhood -> semantic repair mutation` 映射。
- 定向变异替换普通变异，不增加 mutation 或 rollout 预算；每代聚合全种群反例；记录变异前后基因和独立 validator 结果。
- 变异后独立 Contract Validator；关键行为场景 Safety Gate；生存者选择先满足硬安全，再优化性能。
- B 不能硬编码 TIMEOUT->WAIT；必须在不同工具合同和故障模式上搜索。

## 新诊断对照和指标
对照至少 Hand、NSGA-II、A、A+Fixed-WAIT、A+WAIT-SLA、A+WAIT-SLA+VERIFY、安全重试、B-new、A+B-new、A+B-new+Safety Gate。可分机制消融和完整对照两轮，但预算公平。
指标：CondRecSucc、episode/action behavior violation、duplicate side-effect、SLA violation、CorrectEscalation、AvoidableHarm、不必要成本、worst-group、搜索效率、未见任务族泛化。
旧 D-061 validation 若用于调参，不得继续称独立验证；生成新的非锁箱诊断数据。正式 held-out/确认性实验仍 HOLD。

## 必须回答
Q1 WAIT-SLA 是否减少重复副作用？Q2 是否优于固定 WAIT？Q3 VERIFY 独立贡献？Q4 B-new 是否定位正确基因？Q5 B-new 是否优于 NSGA-II？Q6 A+B-new 是否优于 A？Q7 Safety Gate 能否保护 A？Q8 能否接近/超过 Hand？Q9 未见任务泛化？Q10 增益来自演化搜索还是手工编码 WAIT-SLA？

## Gate
GO：原始数据复核、WAIT-SLA、FSM/B-new/Safety Gate 代码、单测、独立 validator、新非锁箱诊断和统计复算。
HOLD：正式 A-3b、旧 held-out 调参、UndoBench TEST、Pilot B、A800/ARWM、大规模真实 API、ThinkingBox、未经批准的锁箱测试。
当前不启动 A800。指标和执行语义稳定后再做正式功效分析。

## 仓库接班纪律
每个阶段及时更新本文件、`SESSION_HANDOFF.md`、`README.md`、`05_DECISION_LOG.md`、`51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md`。每轮区分 PLANNED / IMPLEMENTED / TESTED / EXPERIMENTALLY VERIFIED。不得把计划写成完成。每次阶段提交后核验远端 HEAD、main、CI 和工作树。

## 2026-11-07 — D-062: D-061 failure-trace audit, WAIT-SLA contract, B-new, round-3 diagnostics

Reports: `59_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md`, `60_WAIT_SLA_CONTRACT_BNEW_AND_SAFETY_GATE_DESIGN.md`, `61_D062_DIAGNOSTIC_RESULTS.md`. Data: `experiments/pilot_a3b/diagnostic3_results.json` (manifest 017b3454c0b9cf90...) + `diagnostic3_stats.json`. D-060/D-061 artifacts preserved untouched.

### Stage 0 audit (OVERTURNS the D-061 narrative)
- diagnostic2_results.json SHA-256 dc455355... ; independent aggregation + genome replay.
- The 0.36 violation rate is NOT duplicates (A dup_rate = 0.0000): 1,132/1,139 (99.4%) violations are an EVALUATOR ARTIFACT -- correct ROLLBACK safe-aborts were charged by the saga gate; hand's 0.006 is the same artifact.
- Only 7 genuine duplicate episodes; their traces confirm `TIMEOUT -> VERIFY (SLA-internal NOT_COMMITTED lie) -> RETRY -> DUPLICATE` on non-idempotent tools. timeout_before is retry-safe; timeout_after/delayed_visibility are not.

### Fixes and new mechanisms (51/51 tests green)
- Evaluator: saga gate applies to EXECUTE-type actions only; safe rollback is free. Metrics separated: sla_violation / duplicate / downstream_violation.
- WAIT-SLA contract (implemented): under UNKNOWN_OUTCOME on non-idempotent tools, RETRY unlocks only after compensation clears the ambiguity OR (visibility SLA elapsed AND a post-SLA query confirms non-commitment); SLA-internal queries never unlock retry. Action masking; genome unchanged (Q10 isolation).
- B-new: action-sequence failure signatures, population-wide per-generation aggregation, implicated-gene targeting, cause->repair-action map, contract repair + independent validator, budget-matched.
- Safety Gate: 6-scenario behavioural battery + layered survivor (ABG arm).

### Round-3 results (DIAGNOSTIC; fresh seeds 2026110900)
- **AB vs A: +0.119 [0.066, 0.183] p=0.0002 -- B-new combination gain ESTABLISHED (D-061 negative reversed).**
- **AwaitSLA vs A: +0.089 p=0.005; AwaitSLA vs AwaitFixed: +0.054 p=0.003 -- WAIT-SLA works and beats fixed waiting.**
- AB vs AwaitSLA +0.031 p=0.0072 on all data, but validation +0.031, p=0.244 (n.s.); Q10 search increment is suggestive in-sample but not yet shown to generalize.
- AB behavioural violations 0 (A 0.060); AB stability [0.543, 0.531, 0.543]; validation AB vs A +0.142 p=0.008.
- Negative results kept: Safety Gate harmful (ABG < AB, -0.193); B alone worse than NSGA-II (-0.074); hand still ahead (AB -0.282).

### Judgement
Three mechanisms now have independent ablation evidence (contract-preserving A, WAIT-SLA, B-new). Mechanism-level ablations are promising, but AB vs NSGA-II is not significant (all p=0.062; validation p=0.2277), and Q10 is not significant on validation (p=0.244). Do NOT yet claim superiority to standard EA or generalized search gain. Hand remains ahead.

### Next task (single)
Power analysis from the round-3 cluster variance (cluster_sd ~ 0.40) -> freeze preregistration (with the Q10-scoped claim) -> submit for user approval -> formal A-3b. Everything else stays HOLD.


# 2026-11-08 — D-063：正式 A-3b 功效核算与预注册（下一会话接管）

**执行计划：** `62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md`  
**D-062 交付：** 59（失败轨迹独立复核）/ 60（WAIT-SLA、B-new、Safety Gate 设计）/ 61（diagnostic3 结果）。  
**当前阶段：** D-062 已完成；D-063 为 PLANNED；正式 A-3b 仍 HOLD。

## 接管时先核验
- 远端分支 `pilot-a-stateful-recovery`、main、HEAD、CI。
- D-062 基线 HEAD 曾为 `730431e1c52e97adf550a54f77cb53256e302525`；后续 D-063 文档/CI 更新会产生新 HEAD。
- 执行报告称 79/79 测试通过。新 workflow `.github/workflows/research-simulator-regression.yml` 已覆盖 `pilot_a_recovery/**` 和 `pilot_a3b/**`；Actions run `42398278551` 在 D-062 代码提交 `c0078d5` 上成功，两个测试步骤均 success。后续提交只改文档，未改实验代码。

## D-062 关键结果和限制
- 59 号独立审计推翻 D-061 的 0.36 vs 0.006 行为违规叙事：99.4% 为 evaluator artifact（正确 rollback 被 saga gate 误伤）；真实重复副作用 7 例，错误链为 `UNKNOWN_OUTCOME -> SLA 内 VERIFY 谎言 -> 非幂等 RETRY -> DUPLICATE`。
- WAIT-SLA 契约实现：非幂等工具 UNKNOWN_OUTCOME 下，只有补偿清除歧义，或等满 visibility SLA 且 SLA 后查询确认未提交，才解锁 RETRY；SLA 内查询不能解锁。无可靠合同保证时应升级/安全停止。
- B-new：动作序列签名、全种群聚合、涉事基因定位、死因到修复动作映射、替换式预算对齐变异。
- diagnostic3 报告：AB vs A +0.119 p=.0002；AwaitSLA vs A +.089 p=.0047；AwaitSLA vs Fixed +.054 p=.0032；AB vs AwaitSLA +.031 p=.0072（all）；AB vs A validation +.142 p=.0082。
- 负结果：B 单独劣于 NSGA-II（−.074）；ABG gate 有害（AB−ABG +.193）；AB 未超 Hand（−.282）。
- **关键限制：AB vs NSGA-II all +.1049, p=.062；validation +.1173, p=.2277。两者均未显著。Q10 的 AB vs AwaitSLA validation +.031, p=.244，也未显著。** 当前不能宣称 AB 已在独立测试集显著优于 NSGA-II，也不能说搜索增益已泛化。

## D-063 第一阻断项：重现 diagnostic3 统计
当前 `experiments/pilot_a3b/stats.py` 仍硬编码读取 `diagnostic2_results.json`，而 `run_diagnostic3.py` 只写原始数据；已提交 `diagnostic3_stats.json` 没有完整包含 AwaitSLA 相关对比的 cluster SD / 推断结果。先新增可执行 `analyse_diagnostic3.py` 或通用 CLI 分析器，完整再生 61 号统计并校对，不得硬编码结果。

必须输出 all/train/validation 三种 split；AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II；cluster SD、CI、paired sign-flip p、Holm（次要家族）、效应量、seed nesting、输入 hash 和分析命令。新增 synthetic tests。

## 功效规划初值（paired cluster t 近似，最终需 empirical simulation）
- 正确主要依据是 validation-only AB vs NSGA-II：Δ=.1173、cluster SD=.3914、18 clusters、p=.2277。
- 当前 all-split AB vs NSGA-II：Δ=.1049、SD=.404、54 clusters、p=.062；不得把 train+validation 混合作正式确认性证据。
- 双侧 α=.05，80%/90% power：
  - MDE=.1173，SD=.3914：90/119 可分析 clusters；
  - **MDE=.10：123/163 clusters**；
  - MDE=.08：190/254 clusters。
- MDE=.10、80% power 加 15% 失效预留约 145 clusters。cluster=task×fault composition；不能靠增加 seeds/episodes 伪造独立样本。若 9 个 fault compositions，145 clusters 约需 17 个 task families ×9（153）。
- 以上是近似规划值；18 个 validation clusters 对 SD 的估计不稳定，先用完整 paired cluster 数据做 Monte Carlo sign-flip/bootstrap power simulation，再冻结。

## D-063 预注册要求
主要假设：AB 在全新 held-out test clusters 的 balanced class-success 上优于 NSGA-II；双侧 α=.05；唯一主要对比。次要对比 Holm：AB vs A、AwaitSLA vs A、AwaitSLA vs Fixed、AB vs AwaitSLA。Hand 作为参考，不声称超越专家。安全为硬接受条件；保证仅在工具合同假设成立的范围内，不将零观察违规夸大为对所有工具的绝对证明。
锁定新任务族、新故障组合、算法版本、预算、种子、类别权重、排除规则、统计脚本和 manifest。当前 diagnostic3 validation 不得再作为正式 test。

## GO / HOLD
GO：统计脚本修复与独立复算、empirical power simulation、任务族扩展可行性审计、预注册草案、CI 测试。
HOLD：正式 A-3b、查看/调参 held-out test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。
**完成 D-063 草案后交用户审阅批准；未经明确批准，不启动正式 A-3b。**


---

# D-063 执行接管指令（2026-11-09；本节优先于所有较早历史段落）

你现在继续接管唯一研究仓库 yujian777555/kaitibaogao。当前任务不是重新选题，也不是重复写研究计划，而是把 D-062 diagnostic3 的统计证据独立复算正确，并据此完成正式 A-3b 的功效设计和预注册草案。

**本节是当前最高优先级指令。若本文较早的历史段落与本节冲突，以本节为准。**

## A. 接管时先做真实仓库核验

- 仓库：yujian777555/kaitibaogao。
- 分支：pilot-a-stateful-recovery。
- 本轮维护开始前 HEAD：e6fee3bde05e8dea3fcc54f2ea1d97bc54837867（仅为历史核验基线）。
- main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653（历史核验值）。
- 本轮维护开始前工作分支 ahead 123 / behind 0。
- 接管时重新读取远端 branch HEAD、main HEAD、ahead/behind、工作区状态和最新 Actions；不得照抄历史 SHA。
- main 不得修改或合并；所有写入仅发生在 pilot-a-stateful-recovery。

## B. 研究目标与当前证据边界

第一项创新候选：

**契约约束与反例引导的 Agent 事务安全恢复策略演化。**

已实现机制：
- A：契约语义保持算子；
- WAIT-SLA：未知工具执行结果下的状态化等待/验证/重试解锁合同；
- B-new：基于动作序列失败签名、涉事基因定位和语义修复的反例引导演化。

D-062 diagnostic3 结果必须如实继承：

| 对比 | 报告结果 | 证据边界 |
|---|---:|---|
| AB vs A | +0.119，p=.0002 | 诊断性正向证据 |
| AB vs A（validation） | +0.142，p=.0082 | B-new 增量的 validation 证据 |
| AwaitSLA vs A | +0.089，p=.0047 | WAIT-SLA 诊断性正向证据 |
| AwaitSLA vs AwaitFixed | +0.054，p=.0032 | SLA-aware 优于固定等待 |
| AB vs AwaitSLA（all） | +0.031，p=.0072 | 全数据正向；不能替代 validation |
| AB vs AwaitSLA（validation） | +0.031，p=.244 | 不显著，Q10 搜索增量尚未证明泛化 |
| AB vs NSGA-II（all） | +0.1049，p=.062 | 不显著 |
| AB vs NSGA-II（validation） | +0.1173，p=.2277 | 不显著 |
| AB vs Hand | −0.282，p=.0002 | 仍落后强手工策略 |

其他限制：
- B 单独劣于 NSGA-II；Safety Gate 在当前设定下有害，必须保留负结果。
- A 的非法候选率下降、WAIT-SLA 行为违规为零是诊断实验结果，不应夸大为对所有外部工具的绝对安全保证。
- 安全保证只能限定于明确的工具合同、可见性 SLA、查询一致性、幂等和补偿假设。
- 59 号独立审计已推翻 D-061 的 0.36 vs 0.006 叙事：99.4% 是 evaluator artifact；真实重复副作用 7 例。必须保留更正。
- D-062 是 diagnostic，不是 confirmatory。不得声称 AB 已显著优于 NSGA-II，也不得声称超过专家。

## C. 本轮唯一主线：D-063

### Stage 0 — diagnostic3 统计分析独立复现（唯一首要任务）

先审查：
- experiments/pilot_a3b/diagnostic3_results.json
- experiments/pilot_a3b/diagnostic3_stats.json
- experiments/pilot_a3b/stats.py
- experiments/pilot_a3b/run_diagnostic3.py
- 相关 manifest、报告和测试。

当前已知问题：
- stats.py 的 main() 仍硬编码读取 diagnostic2_results.json；
- run_diagnostic3.py 负责产生原始结果，但没有完整的 diagnostic3 独立统计复算入口；
- 已提交 diagnostic3_stats.json 未完整包含 61 号报告中的所有 AwaitSLA 相关对比。
- 因此 61 号报告的关键结果必须从原始 diagnostic3 数据重新生成、逐项对账。

新增 experiments/pilot_a3b/analyse_diagnostic3.py，或将 stats.py 改为显式输入输出参数的通用 CLI。必须满足：

1. 输入显式指定 diagnostic3_results.json，不能静默回退 diagnostic2。
2. 输出 all/train/validation 三种 split。
3. 复算七组比较：AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II。
4. 推断单位为 task × fault-composition cluster；seed 是嵌套重复，不是独立 cluster。
5. 每个比较输出样本数、cluster SD、效应量、95% cluster bootstrap CI、paired cluster sign-flip p、适用的 Holm-adjusted p、seed 稳定性。
6. 校验 episode ID 唯一性；重复 episode 必须 fail-closed。
7. 校验配对完整性、cluster 成员一致性、seed 完整性、split 隔离。
8. 校验评价分母和 R1/R2 条件恢复、R3/R4 正确升级、UNKNOWN 标签语义。
9. 明确缺失 episode、异常退出、预算截断和无效样本的处理规则。
10. 对输入 JSON、manifest、分析配置和代码版本计算/记录哈希。
11. 固定随机种子、bootstrap/permutation 次数、CI 算法、缺失配对处理和多重比较 family。
12. 同一输入与配置重复运行必须得到可复现统计结果。
13. 新增 synthetic tests，覆盖正常配对、缺失臂、重复 episode、cluster mismatch、seed 缺失、split 泄漏、分母错误、Holm 正确性和确定性。
14. 独立再生 diagnostic3_recomputed.json、diagnostic3_recomputed.csv、diagnostic3_recomputed_report.md。
15. 与 61 号报告逐项比较；任何差异必须解释和记录，不能为了匹配历史结果而硬编码统计值。

**Stage 0 未通过，不进入正式功效冻结。**

### Stage 1 — empirical Monte Carlo power simulation

必须使用 Stage 0 独立复算后的 cluster-level paired differences。

- 主要比较：未来新 held-out test 上 AB vs canonical NSGA-II。
- 当前 diagnostic3 validation 只能作为历史开发/功效规划数据，不能重新命名为正式 test。
- 报告 MDE=.08、.10、.1173。
- 双侧 alpha=.05，分别报告 80% 和 90% power。
- 采用与配对 cluster 设计匹配的 empirical resampling / sign-flip Monte Carlo。
- 记录模拟重复数、Monte Carlo 标准误、随机种子和稳定性检查。
- 评估 15% cluster 失效预留。
- 做 cluster SD 敏感性分析，明确 18 个 validation clusters 导致方差估计不稳定。
- 不能通过增加同一 cluster 的 episode 或 seed 凑独立样本。

初步 t 近似（不是最终冻结值）：
- MDE=.1173：80%/90% 约 90/119 个可分析 clusters；
- MDE=.10：约 123/163 个可分析 clusters；加 15% 失效预留约 145/192；
- MDE=.08：约 190/254 个可分析 clusters。

这些只是初步规划，最终样本量以 empirical simulation 为准。

### Stage 2 — task-family / fault-composition 扩展审计

仓库中存在两种计数表述：
- 某些历史设计记录提到总计 6 个任务族；
- validation 当前描述为 2 个任务族 ×9 compositions =18 clusters。

两者可能分别代表全量任务族与 validation 子集。必须从真实 task manifest、split manifest、scenario IDs 对账，不得猜测。

审计至少包含：
- task family ID、生成规则、语义目标、工具依赖；
- fault composition 定义及其适用性；
- cluster ID 的确定性生成规则；
- 同模板、状态图、工具序列和故障轨迹的近重复检查；
- train/validation/test 泄漏矩阵；
- 真实可用独立 cluster 数；
- 新任务族生成成本和人工审核要求。

目标 cluster 数必须以 Stage 1 经验功效结果为准。145 只是 MDE=.10、80% power、15% 预留下的初步近似值。不能拆分相似任务伪造独立 cluster。

输出 63_D063_TASK_FAMILY_EXPANSION_AUDIT.md。

### Stage 3 — preregistration candidate

输出 64_A3B_PREREGISTRATION_CANDIDATE.md。

必须明确：
- 唯一主要比较：AB vs canonical NSGA-II；
- 主要 estimand、主要终点、逐类公式、分母、类别权重和 cluster 聚合顺序；
- R1/R2 条件恢复与 R3/R4 正确升级是不同语义，不能混成含糊的“成功率”；
- UNKNOWN 必须有预先定义的处理方式，不得事后重分类；
- 双侧 alpha=.05、目标 power、MDE 和最终 cluster 数；
- 次要比较及 Holm family；
- Hand 仅作强手工参考，不声称超越专家；
- 安全硬门和明确工具合同假设；
- 算法/代码/依赖版本、初始化、演化参数、相同预算；
- 随机化、配对、seed、cluster、排除和缺失值规则；
- 锁箱 manifest、哈希、执行命令和偏离预注册的披露方式。

预注册必须标记 DRAFT — NOT FROZEN，交用户审阅。用户批准预注册不自动授权正式 A-3b；正式实验另需明确授权。

## D. 当前 GO / HOLD

**GO：**
- 统计分析器与 synthetic tests；
- 历史 diagnostic3 原始数据独立复算；
- empirical power simulation；
- task-family / leakage audit；
- preregistration draft；
- CI、仓库文档和接管提示词维护。

**HOLD：**
- 正式 A-3b 确认性实验；
- 新 held-out test 查看或调参；
- Pilot B；
- A800/ARWM；
- 真实 LLM API；
- UndoBench TEST；
- ThinkingBox。

本轮不需要 GPU，不需要真实 LLM API。

## E. 仓库维护和 CI 纪律

每轮实质性研究后，同轮更新：
- NEXT_SESSION_PROMPT.md（本文件，唯一权威接管提示）；
- SESSION_HANDOFF.md；
- README.md；
- 05_DECISION_LOG.md；
- 62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md；
- 新增的 63/64 号交付文件（若已实际完成）。

记录起始 SHA、最终 SHA、修改文件、数据哈希、测试结果、真实 CI run URL、科学结论和下一步唯一任务。GitHub Actions 未触发或失败必须如实记录，不得写成通过。main 不得修改。

## F. 本轮最终汇报格式

1. 仓库分支、HEAD、main、ahead/behind、工作区；
2. 统计分析器实现和运行命令；
3. diagnostic3 独立复算及与 61 号报告的差异；
4. synthetic tests 与仓库回归测试；
5. Monte Carlo 功效结果及不确定性；
6. task-family 扩展和泄漏审计；
7. 预注册草案与终点定义；
8. CI 实际运行记录；
9. 科学结论和负结果；
10. GO/HOLD；
11. 仓库链接与更新后的接管提示；
12. 下一阶段唯一任务。

**接管后立即开始 Stage 0，不要再询问用户是否开始。不得把计划写成已完成，不得擅自启动正式 A-3b。**

## 2026-11-08 — D-063 COMPLETE: independent recomputation, power simulation, expansion audit, preregistration candidate

### Stage 0 (analyse_diagnostic3.py, 17/17 tests)
- Independent recomputation from diagnostic3 raw rows; structural checks (pairing/seed nesting/clusters/duplicates/leakage/denominators) all clean; manifest verified.
- **All 7 contrast effect sizes match report 61 EXACTLY** (AB vs nsga2 +0.1049; AB vs A +0.1193; AwaitSLA vs A +0.0885; AwaitSLA vs Fixed +0.0535; AB vs AwaitSLA +0.0309; AB vs hand -0.2819; B vs nsga2 -0.0741). p-values drift at 3rd decimal (permutation MC seed difference); conclusions unchanged.
- Outputs: diagnostic3_recomputed.{json,csv,report.md}.

### Stage 1 (power_simulation.json, 2000 MC/point, seed 20261110)
- Primary contrast (AB vs NSGA-II, cluster sd 0.404) test clusters needed @80%: MDE 0.08 -> 254, 0.10 -> **145**, 0.1173 -> 110 (with 15% attrition: 299/171/130). ICC ~ -0.09 (cluster independence supported). 18-cluster variance instability honestly reported via 3-source sensitivity.

### Stage 2 (63_D063_TASK_FAMILY_EXPANSION_AUDIT.md)
- 576 contract-meaningful 3-step sequences, 18 contract profiles. Naive per-profile selection concentrates on ledger (overlap 2.0/3); greedy diversity panel = 0.83/3, 144/406 zero-overlap pairs.
- Proposed split: train 8 / val 4 / **test-locked 17 families** = 72/36/**153 clusters** (power gap vs 171-with-attrition covered by pre-registered fallback: MDE 0.1173 or accept 75-80%; never inflate with repeats).
- Leakage registered: shared 10-tool pool (claim limited to new sequences/contract combos), shared fault vocabulary, shared generator.

### Stage 3 (64_A3B_PREREGISTRATION_CANDIDATE.md — awaiting user approval)
Primary sole contrast AB vs NSGA-II; 4 secondary w/ Holm; Hand reference only. Frozen: metrics formulas, hard safety gate (any violation -> fail, scoped claims), pop 48x60, seeds 411/522/633, scenario base 2026111100, train/val/test 216/108/459 scenarios (test 153 clusters locked), budget/exclusion/stopping/archival rules.

### Status
GO: user review of 64. HOLD: formal A-3b (until approved AND checklist 64 §5 done), test peeking, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox.

### Next task (single)
User reviews 64_A3B_PREREGISTRATION_CANDIDATE.md -> upon approval run pre-flight checklist (freeze scenario hashes, record code SHA, tests green) -> execute formal A-3b.


---

# D-064 执行接管指令（2026-11-09；优先级高于上方 D-063 历史指令）

**当前决策：D-063 工程交付已完成；64 号预注册草案经独立审查为 REQUEST CHANGES；正式 A-3b 继续 HOLD。**  
独立审查：`65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md`。不得照抄上方 D-063 旧段落中“用户直接审阅 64 → 预检 → 正式实验”的路径；必须先完成本节修复。

## 1. 接管基线

- 仓库：`yujian777555/kaitibaogao`。
- 分支：`pilot-a-stateful-recovery`。
- D-063 最终审查基线：`4f23abed3150e09703839b980ad3afc9bb14dfb3`。
- main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，不得修改或合并。
- D-064 审计文档初始提交：`77c7118ce7631830bc79f7cb09553cced9cb5cc8`；之后 README/接管文档会继续产生提交。
- 接管时必须重新查询真实 branch HEAD、main HEAD、ahead/behind、工作区和最新 CI；以上均为历史核验值。

## 2. D-063 工程交付已核验

- D-063 final HEAD：`4f23abe`。
- GitHub Actions run `42615985837` 在该 SHA 上真实 success。
- `pilot_a_recovery`: 28 tests；`pilot_a3b`: 68 tests；总计 96/96。
- 新增 `analyse_diagnostic3.py`、复算报告、power simulation、task-family expansion audit、64 号候选草案均已提交。
- 这代表工程交付和当前 CI 通过，不代表 64 号预注册科学设计已通过审查。

## 3. 64 号草案独立审查结论

`64_A3B_PREREGISTRATION_CANDIDATE.md` = **REQUEST CHANGES，不得批准，不得运行正式 A-3b**。

### P0-A：主要终点与功效输入不一致（第一优先级）

64 §3 的 primary endpoint 是 CondRecSucc，仅 R1+R2；但 `power_simulation.py` 的 `load_cluster_diffs()` 没有按 R1/R2 过滤，实际把 R1/R2/R3/R4 的 `class_success` 混在一起，使用 54 clusters、SD=.404、Δ=.1049 做样本量规划。

原始 diagnostic3 共有 54 task×composition clusters；只有 42 个含 R1/R2 场景，另 12 个仅含 R3/R4。审查用快速配对聚合（非正式输出）得到 R1/R2-only AB−NSGA-II Δ≈+.3175、SD≈.3189、42 个有效 clusters。该值不能直接用于预注册，但证明当前 145-cluster 规划与 64 的 primary estimand 不一致。

**立即执行：**
1. 修改 `analyse_diagnostic3.py`，新增 R1/R2-only CondRecSucc paired contrast。
2. 逐 scenario 配对、seed 嵌套；按 task×composition cluster 等权。
3. 输出 primary eligible clusters、每 cluster R1/R2 分母、零分母 cluster 数、Δ、cluster SD、95% cluster bootstrap CI、cluster sign-flip p。
4. R3 CorrectEscalation、R4 DamageContainment 单独统计，不混入 primary。
5. 为零分母 cluster 预先制定规则，不得事后排除。
6. 增加 synthetic tests 和真实原始数据复算测试。

### P0-B：功效模拟并非经验重采样

当前 `power_simulation.py` 实际使用 `N(MDE, empirical SD)` 正态生成；`assume_mean_shift=False` 经验重采样分支没有被调用；`test="signflip"` 分支仍是正态 z 近似；t 检验也使用正态 CDF 近似。没有 MCSE/功效区间，null FPR 在部分小样本点偏高。

修复后必须：
- 使用 CondRecSucc primary cluster differences；
- 运行 empirical centered cluster resampling 或经论证的层级模型；
- 使用与预注册一致的检验（Student-t / cluster sign-flip）；
- 报告 MCSE/区间、null FPR 校准、seed、模拟次数和收敛检查；
- 做 task-family 内相关性敏感性。

### P0-C：ICC 不足以证明独立

当前 ICC 仅 6 个 task families（validation 2 个），负点估计不是独立性证明。未来 17 families ×9 compositions 存在同 family 内相关可能。

需明确独立推断单位，报告 ICC 不确定性，并至少做 ICC=0/.05/.10/.20 的设计效应/功效敏感性，或采用 family-level bootstrap / hierarchical simulation。删除“ICC≈−.09 证明独立”的表述。

### P0-D：任务族有效性与正式生成器

`task_family_expansion_audit.py` 仅枚举 10 工具的三步排列，并检查合同属性组合；没有验证业务/抽象 saga 的前置、后置条件和目标。贪心选择只最小化工具重叠，没有优化 profile diversity；实际新序列覆盖 11/18 profiles，test 覆盖 10/18。

当前 `pilot_a3.py` 仍固定 6 个 TASKS，`make_fault_vector()` 依赖 `TASKS[task_name]`；`run_diagnostic3.py` 仍硬编码 4 train + 2 val tasks。63 的 8/4/17 只是候选划分，尚非可运行正式生成器。

需实现：
1. task semantic contract（目标、前置/后置条件、工具输入输出和合法顺序）；
2. 独立任务序列 validator；
3. 通用正式 scenario generator，支持 8/4/17 或经修订的 split；
4. 标签生成、R1–R4/UNKNOWN 计数、primary-eligible cluster 检查；
5. train/val/test manifest、seed、hash 和零 task-family overlap 测试；
6. 重新核对 profile coverage；若只声称工具重叠贪心，修正文档措辞。
7. 明确 9 种 fault-composition 类别在各 split 重复出现，因此不能声称 unseen fault-type OOD，只能声称新 task-family/sequence 上的泛化。

### P1：样本量、UNKNOWN、安全门与冻结协议

- 153 test clusters 在 15% 失效后约 130；原参数化方案 MDE=.10/80% 需要 145 个可分析、约 171 个招募 clusters。必须用修复后的 primary power simulation 重新决定。
- MDE=.1173 来自观察到的 validation effect，不得未经实质意义论证就当作 MDE。
- 64 当前同时保留 MDE=.10 和 .1173 方案，没有唯一冻结。
- UNKNOWN 不进入 primary denominator，但必须冻结最大比例/超限处理；55-R1 的 ≤5% 规则不能无说明消失。
- 冻结 R1/R2/R3/R4 分布、primary eligible clusters 和每 cluster 分母。
- 精确定义硬安全门：AB 是否必须全部为 0；NSGA-II 安全失败如何报告；零观察事件报告分母和置信上界。
- 初始池生成 60 个但 `run_evolution()` 只用前 48 个；预注册明确实际初始 population。
- 64 §5 “27+ tests”更新为精确 CI 证据：当前 D-063 是 96/96；正式冻结时记录确切 commit 和 run。
- 批准必须绑定具体代码 SHA 与场景 manifest hash；批准后代码变更须新版本/重新批准。

## 4. D-064 执行顺序

1. **D-064-A（唯一首要任务）：** CondRecSucc R1/R2-only paired cluster analysis。
2. **D-064-B：** 以正确 primary estimand 重做 empirical/hierarchical power simulation、ICC 敏感性和样本量决策。
3. **D-064-C：** 任务语义 validator + 正式 8/4/17 场景生成器 + label/manifest/hash 测试。
4. **D-064-D：** 修订 64：MDE/power、UNKNOWN、类别分布、安全门、初始池、预算、代码 SHA、解释边界。
5. 更新 65 审计状态；由独立复核确认 blockers 关闭后，才将 64 标记为 READY_FOR_USER_REVIEW。

## 5. GO / HOLD

**GO：** D-064-A/B/C/D 修复、synthetic tests、历史诊断数据重算、任务族生成器与标签审计、预注册修订、CI 和仓库维护。

**HOLD：** 正式 A-3b；生成后查看/调参 held-out test；Pilot B；A800/ARWM；真实 LLM API；UndoBench TEST；ThinkingBox。

用户批准预注册后，正式 A-3b 仍需另行明确授权。

## 6. 下一会话汇报

按以下格式报告：仓库 SHA/main/ahead-behind；primary CondRecSucc 正式复算；与旧全类别统计的差异；修正功效与 ICC 敏感性；任务序列语义 validator 与新生成器测试；64 修订点；CI 实际结果；剩余 HOLD；下一唯一任务。

**接管后直接执行 D-064-A，不要再询问是否开始；不得擅自启动正式 A-3b。**

## 2026-11-09 — D-064-A COMPLETE: CondRecSucc primary endpoint independently recomputed — CONCLUSION REVERSED

Report: `66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md`. Program: `experiments/pilot_a3b/condrec_analysis.py` (no hardcoded summaries) + `test_condrec_analysis.py` (13/13). Artifacts: `condrec_diagnostic3.{json,csv,report.md}` (input SHA-256, git SHA, command, MC reps, seeds recorded).

### Primary result (R1+R2 only, 4-level pairing, cluster-equal-weight, real diagnostic3 rows)
- primary eligible clusters **42** (of 54 design clusters); zero-denominator 12 (= delay_rate_permission + partial_comp_failure x 6 task families, structurally infeasible by design, excluded per pre-specified rule and registered).
- **AB CondRecSucc 0.5582 vs NSGA-II 0.2407; delta = +0.3175; cluster SD 0.3189; 95% CI [0.218, 0.411] (excludes 0); cluster-level sign-flip MC p = 0.000125** (8000 real sign flips, not z-approx).
- scenario-weighted sensitivity +0.3145 (consistent); pairing completeness 1.000.
- **CONCLUSION REVERSED vs all-class +0.1049 (p=0.065)**: the old statistic diluted the effect with 12 R3/R4-only clusters where both methods tie. 65's quick-check numbers (+0.3175 / 0.3189 / 42) match this formal recomputation digit-for-digit.

### R3/R4 independent safety stats (trade-off reported honestly)
R3 CorrectEscalation: AB 0.226 vs NSGA-II 0.679. R4 DamageContainment: AB 0.80 vs 0.933. AB leads the primary endpoint but trails on safe-escalation behaviour; neither masks the other.

### Status
GO: **D-064-B** (power re-analysis on the CondRecSucc estimand + ICC hierarchical sensitivity = 65 P0-2/P0-3). HOLD unchanged: formal A-3b, test peeking, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox. 65 P0-4/P1-5/6/7 remain open after D-064-B.

### Next task (single)
D-064-B: rebuild the power analysis on the real CondRecSucc cluster-diff distribution (delta 0.3175, sd 0.3189, 42 clusters) with empirical resampling + proper sign-flip/Student-t tests + ICC hierarchical sensitivity (0/0.05/0.10/0.20), then revise 64's sample-size/MDE freeze.


---

# D-064-B 执行接管指令（2026-11-09；当前唯一下一任务）

**本轮状态：D-064-A 已完成；D-064-B 已获准执行；正式 A-3b 仍 HOLD。**

下一会话必须先完整阅读并直接执行：

`67_D064B_POWER_AND_HIERARCHICAL_SENSITIVITY_EXECUTION.md`

该文件是 D-064-B 的完整可复制提示词，包含数据基线、层级结构、ICC 估计、两类功效生成机制、MDE 网格、检验校准、样本量换算、测试和仓库维护要求。

## D-064-A 事实基线

- 最终 D-064-A HEAD：`16e255de627b37713f0ea936df0ddb0dd03ac084`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。
- CI run `42631223393`：head SHA 匹配，success；109/109 tests。
- 原始 diagnostic3 SHA-256：`b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`。
- CondRecSucc 仅 R1+R2：42 eligible task×composition clusters、12 zero-denominator clusters。
- 42 个 clusters 嵌套于 6 个 task families，每个 family 当前 7 个 eligible compositions。
- AB 0.5582 vs NSGA-II 0.2407；Δ=+0.3175；cluster SD=0.318856；D-064-A cluster bootstrap CI [0.218254, 0.411376]；cluster-level sign-flip p=0.000125（8000 次）。
- R3 AB 0.226 vs NSGA-II 0.679；R4 AB 0.800 vs NSGA-II 0.933。安全行为权衡必须保留。

## D-064-B 必须解决的核心问题

**不能把 42 个 task×composition clusters 当成 42 个已证明独立的抽样单位。** 高层级单位是 task family，目前只有 6 个。D-064-A 的 cluster-level CI/p 对 family 内相关性敏感，必须通过 family-level 与 hierarchical sensitivity 重新评估。

另外，64 号草案的候选 test 为 17 families×9 compositions=153 design clusters；如果延续当前 7/9 R1/R2 eligibility，则约为 119 primary-eligible clusters（尚未扣除 attrition）。不得将 153 design clusters 写成 153 primary-eligible clusters。

## D-064-B 执行顺序

1. 从原始 rows / D-064-A 可追溯产物复建 family→composition→scenario→seed 层级，验证 6 families×7 eligible clusters。
2. 输出 family means、within/between variance、ICC（至少 ANOVA method-of-moments + random-intercept REML）和不确定性区间；负 ICC 不等于独立。
3. 使用 family-block empirical resampling 和 ICC-controlled random-intercept simulation 两类 DGP。
4. ICC 场景：0/.05/.10/.20；MDE 场景：.05/.08/.10/.1173/.15；双侧 alpha=.05；80%/90% power；至少 10,000 MC/config 或达到预先声明的 MCSE 精度。
5. 检验至少比较 family-level Student-t、family-level exact/MC sign-flip、family-block bootstrap；在 null 下校准 Type-I error。ICC>0 时禁止把 42 clusters 当独立样本做主检验。
6. 设计网格至少 6/8/10/12/15/17/19/22/25/30/40 families；每 family eligible compositions 6/7/8/9；区分 cluster-level 与 family-level 15% attrition。
7. 输出 families、design clusters、primary-eligible clusters、attrition 后数量和 power；不以增加 seed/episode 凑独立单位。
8. 0.1173 仅为历史观察效应敏感性值；+0.3175 不是 MDE。不得按观察效应挑选 MDE。
9. D-064-B 给出条件性样本量建议，但在 D-064-C 任务语义 validator / 正式场景生成器完成前，不冻结最终 test family 数、eligibility 数和 MDE。
10. 更新 67 号文件、65 审计、62 计划、README、05_DECISION_LOG、SESSION_HANDOFF 和本接管提示；测试、CI、push、SHA 核验。

## GO / HOLD

**GO：** D-064-B 功效与 ICC 层级敏感性分析、代码、测试、历史诊断数据重算和仓库维护。

**HOLD：** 正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。64 号预注册仍为 REQUEST CHANGES。

**接管后直接执行 D-064-B，不要再询问是否开始。** 具体参数、算法和验收标准以 67 号文件为准。

## 2026-11-09 — D-064-B COMPLETE: hierarchical power, ICC sensitivity, family-count plan

Report: `68_D064B_HIERARCHICAL_POWER_REPORT.md`. Program: `experiments/pilot_a3b/power_hierarchical.py` (no hardcoded historical values) + `test_power_hierarchical.py` (22/22). Artifacts: `power_hierarchical.json`, `power_hierarchical_report.md`, `family_cluster_diagnostics.csv`. Input SHA-256 b9498195... matches D-064-A.

### Hierarchy & ICC
6 families x 7 eligible comps = 42 clusters (12 zero-denom); ALL SIX family means positive (0.238-0.381); family-mean SD 0.059. ANOVA/MoM ICC = **-0.1257**; REML boundary 0; family-block bootstrap CI [-0.159, -0.111]. Negative ICC retained and NOT interpreted as proof of independence (6 families imprecise) -> planning uses ICC grid sensitivity instead.

### Hierarchical inference (D-064-A re-qualified)
family-level Student-t **p=4.6e-05**; exact sign-flip (2^6) **p=0.03125** (resolution floor); family-block bootstrap CI **[0.272, 0.357]** excludes 0. **Significance HOLDS under family correlation**; the cluster-level p=0.000125 is superseded for hierarchical claims.

### Power & calibration (10,000 MC key cells / 2,000 MC sweep)
- **Student-t well calibrated (Type-I 0.050-0.056) -> recommended primary test**; sign-flip 0.031(F=6)/0.05(F=17); **bootstrap-CI test anti-conservative (0.08-0.14) -> NOT an alpha test**. Two calibration bugs found and fixed (MC sign-flip counting; block-resample centering).
- Required families (m=7, MDE=0.10 @80%): ICC 0->15, 0.05->17, 0.10->22, 0.20->30; with 15%+15% attrition: 22/30/40/40. MDE=0.05 unreachable in <=40 grid (reported).
- **17 families conditionally sufficient** (low ICC + low attrition + MDE>=0.10); insufficient otherwise.

### Status
GO: **D-064-C** (task-family semantic validator + formal scenario generator + unique freeze of MDE/sample size). HOLD unchanged: formal A-3b, test peeking, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox. 64 stays REQUEST CHANGES.

### Next task (single)
D-064-C: semantic validator for candidate task families (65 P0-4), formal 8/4/17-or-larger scenario generator with manifest/hash tests, scientific MDE justification and unique sample-size freeze; then revise 64.

## 2026-11-09 — D-064-C COMPLETE: semantic audit, generator verification, design freeze (64-R2)

Report: `69_D064C_INDEPENDENT_AUDIT_AND_DESIGN_FREEZE.md`. New tests: `test_d064c_audit.py` (25/25). Power recheck: `power_final_design_check.json`. 64 revised to **R2**.

### Audits (all passed)
- Task semantics: validator rejects all 12 adversarial tampering classes.
- 9 fault compositions: declared-vs-injected-vs-label consistent; ONE stale note fixed (permission_after_compensatable_prefix described legacy triple-fault but injects step-1 permission only; implementation matches name and R3 mechanism; R3 premise holds 52/52 families; 7/9 primary eligibility unchanged).
- Labeler: independent AND-OR robust reachability (horizon 24) with analytic cross-check and per-cluster evidence hashes; no algorithm input; UNKNOWN 0% (not claimed perfect).
- Split 8/4/40: disjoint, 10 profiles x 4 families, determinism + lockbox clean; semantic diversity scoped to abstract saga.
- Hashes reproduced independently: manifest fb832bcc...（最终 CI run 42661732606）/ test-family 01b41df8... / test-scenario dded3bb7...

### Power at final design (hardcode 0.85 NOT trusted)
40 design families x 7 eligible comps, dual 15% attrition -> 34 eff families x 5 eff comps = 170 eff clusters; MDE=0.10; 10,000 MC (seed 20261113):
- **ICC=0.20 worst case: power 0.839 [0.832, 0.846] >= 0.80 TARGET MET**
- ICC 0/0.05/0.10: 0.979/0.953/0.922; null Type-I 0.054 calibrated.
- Generator POWER_DESIGN updated to 0.839 + CI + provenance; MDE marked **PROPOSED_MDE_PENDING_ADVISOR_APPROVAL**.

### 64-R2 frozen items
Primary = family-level Student-t (calibrated); sign-flip sensitivity-only; bootstrap descriptive-only; UNKNOWN>5% = label-gate failure; double-15% attrition rule; test 40 families / 1,080 scenarios / 280 eligible clusters (hashes frozen); lockbox + stopping rules unchanged. Status: CANDIDATE R2 awaiting independent review + user approval.

### Status
GO: correct 64-R2 findings and request independent R2 review. HOLD: formal A-3b, test peeking/tuning, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox, main merges. Formal A-3b additionally requires advisor approval of MDE=0.10, explicit user approval, and a passing §5 pre-flight.

### Next task (single)
Resolve 70_64R2_INDEPENDENT_REVIEW_R1.md REQUEST CHANGES: correct §2 primary/secondary inference, dynamic df, final manifest hash, conservative attrition wording, and advisor-approval gate; update README/05_DECISION_LOG/SESSION_HANDOFF/NEXT_SESSION_PROMPT; run tests and CI; request independent R2 review. Do not run formal A-3b until independent review ACCEPTED + advisor MDE approval + explicit user approval + §5 pre-flight.


## 2026-11-10 — 64-R2 independent review R1: REQUEST CHANGES

Reviewed: 64_A3B_PREREGISTRATION_CANDIDATE.md R2; report: 70_64R2_INDEPENDENT_REVIEW_R1.md.

Current verified state: work branch HEAD fa3bc2c5699c0fad8df384bebd44e5510d1d8927; main 683b3fe7fc52c86e917d523fdc6bbb13abbfd653; ahead 170 / behind 0; CI run 42661732606 success, 174/174. Final manifest SHA fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a; family/scenario hashes unchanged.

Blocking findings: §2 cluster-level bootstrap/sign-flip conflicts with §4 family-level Student-t; df=39 must be dynamic F_observed−1 (expected df=33 at 34 families after attrition); stale manifest hash; secondary test specification incomplete; deterministic floor attrition requires explicit conservative wording; MDE=0.10 still needs advisor approval. See report 70.

Only next task: correct 64-R2 and re-review. Formal A-3b remains HOLD until independent review passes, advisor accepts MDE, user explicitly approves, and §5 pre-flight passes.

## 2026-11-10 — D-064-R2 COMPLETE: six R1 findings fixed; 64-R3 created for independent re-review

Deliverables: `64_A3B_PREREGISTRATION_CANDIDATE_R3.md` (R2 original preserved in `64_A3B_PREREGISTRATION_CANDIDATE.md`), `71_64R2_CORRECTIVE_RESPONSE_AND_R3_VALIDATION.md`, `test_64r3_protocol.py` (15/15), code fixes in `power_hierarchical.py`.

### R1 findings — independently verified, all CONFIRMED, all fixed
- R2-001: primary test unified = two-sided family-level Student-t (alpha=0.05) on family-level paired CondRecSucc diffs; sign-flip = sensitivity; bootstrap CI = descriptive only; AB vs Hand descriptive.
- R2-002: **df = F_observed - 1 dynamic** via `family_t_df()` (40->39, 34->33); documented + tested through the real code path.
- R2-003: **manifest hash independently rebuilt = fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a** (matches CI run 42661732606); af83f065... marked SUPERSEDED (pre-POWER_DESIGN-edit); test-family 01b41df8... / test-scenario dded3bb7... unchanged.
- R2-004: attrition = deterministic floor conservative retention (34 x 5; 5/7 != exact 15%); `missing_data_rules()` freezes technical-missing / behavioural-failure (score 0, keep denominator) / fail-closed integrity; family floor >=1; design_deviation flag if F<34; selective deletion forbidden.
- R2-005: GO sequence now explicitly requires **advisor MDE acceptance**; MDE stays PROPOSED_MDE_PENDING_ADVISOR_APPROVAL.
- R2-006: H2-H5 fully specified with Holm family {H2..H5}; H4/H5 marked exploratory (no dedicated Type-I calibration); safety endpoints reported separately.

### Extra implementation fix (found during verification)
`family_level_tests` ran exact 2^F sign-flip enumeration (hangs at F=40) -> now exact for F<=15, 10,000-rep MC sign-flip otherwise (method recorded).

### Verification numbers
df tests 39/33/dynamic; family-equal weighting verified; missing-data rules tested; Holm edges tested; power recheck ICC=0.20 t=0.840 [0.833, 0.847] consistent with history 0.8391; real-data df=5 with 6 families. Full suite 28 + 161 = 189 green. CI: see maintenance docs for the run at the pushed HEAD.

### Status
GO: **64-R3 independent re-review** (71 is executor validation, NOT an audit). HOLD unchanged: formal A-3b (blocked until review ACCEPTED + advisor MDE + user approval + pre-flight), test access/tuning, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox, main merges.

### Next task (single)
Submit 64-R3 + 71 for independent R2 re-review; upon ACCEPTED obtain advisor MDE acceptance, then user approval, then run the R4 §9 pre-flight and execute the formal A-3b.


## 2026-11-10 — 64-R3 independent review: REQUEST CHANGES

Current authoritative audit: `72_64R3_INDEPENDENT_REVIEW.md`. Independent evidence: `experiments/pilot_a3b/audit_64r3_independent_checks.json`.

Verified baseline: work branch `ca7bb12f89dd72deaac205ffab89cf3054e6be06`; main `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`; CI run 42670236796 success with 28+161=189 tests. Manifest/test-family/test-scenario hashes independently reproduced.

The review does NOT accept the executor's “all six R1 findings fixed and verified” status. R2-003 is closed; dynamic df and the advisor-approval text gate are present. Implementation remains open for R2-001/004/006.

Blocking findings:
1. R3 §5 points pre-flight to §6, but no such checklist exists there.
2. `missing_data_rules()` is only a dictionary; labelled null does not fail closed, technical_missing_runs/family_loss/design_deviation are not computed, and families can silently disappear.
3. Power assumes fixed 34x5, while the rule permits m=1. Independent ICC=0.20 recheck: balanced power=0.8400 [0.8328,0.8472]; 17 families m=5 + 17 families m=1 gives power=0.5777 [0.5680,0.5874]. Do not claim family-equal weighting removes this precision loss.
4. `family_level_tests()` returns `t=inf,p=0` for 34 all-zero differences; the simulation helper returns p=1 for the same case.
5. `build_hierarchy()` hardcodes 6/42/7/12 and is a historical D-064-B diagnostic function; no formal 40-family analysis entry exists.
6. H2-H5 have no actual family-level Student-t + four-test Holm pipeline. The historical secondary family is six cluster-level sign-flip contrasts. H2/H3 also lack dedicated calibration; H4/H5 exploratory status has no formal report path.
7. Historical diagnostics do not use Test, but the generator returns the full Test payload to callers, `run_evolution()` has no split guard, and labels can enter fitness through `evaluate_controller()`. No one-time unlock path exists.
8. `signflip_exact` is misleading under Monte Carlo, and the actual MC seed is not serialized.

### Only next task
Executor completes an R4 corrective revision covering every item in `72_64R3_INDEPENDENT_REVIEW.md` §11, then requests a fresh independent review. Preserve R2/R3 history. Implement the real 40-family analysis and missing-data paths; either require at least five valid compositions or preregister and validate an unbalanced missingness model; unify Student-t degenerate handling; implement H2-H5 with exactly four Holm tests; fix the pre-flight checklist; enforce split guards and one-time Test unlocking; correct sign-flip output; add real-path tests and rerun CI.

Formal A-3b remains HOLD. Do not read or tune Test, merge main, start Pilot B/A800/ARWM/real LLM APIs/UndoBench TEST/ThinkingBox. Even an ACCEPTED review would still require advisor MDE acceptance, explicit user approval, and a real pre-flight.


## 2026-11-10 — D-064-R4 Executor handoff

当前独立审计为 72_64R3_INDEPENDENT_REVIEW.md = REQUEST CHANGES。唯一执行任务与逐项验收标准见 73_D064_R4_EXECUTOR_SPECIFICATION.md。不要把本轮 Planner 规范提交描述为代码修复或实验通过。正式 A-3b、真实 Test 访问/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main 合并继续 HOLD。


## 2026-11-10 R4 implementation checkpoint

- Current code checkpoint: 5e7568050be4d7c1ac7511137bb5627a08ec044d; later doc-only note commit: f2862840d5db6ce788244fc0c2d3487089db3b1d. Re-query remote before work.
- CI 42788079429 @ 5e756805: success; pilot_a_recovery 28 tests, pilot_a3b 183 tests, total 211. D-064-C manifest gate PASS.
- Implemented: shared Student-t boundary function in power_hierarchical.py; formal_analysis.py initial dynamic family-level primary analyzer; 22 synthetic tests across test_64r4_student_t.py and test_64r4_formal_analysis.py.
- Known R4 gaps: R4 preregistration file, real preflight, missing-data integration/provenance, H2-H5, Test split guard and one-time final evaluation, power/Type-I re-calibration, independent review.
- Algorithm candidate note: 75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md. Do not claim uplift; current AB trade-off and strong hand baseline are explicitly documented.
- Do not access real Test labels/results or run formal A-3b.

## 2026-11-10 R4 implementation checkpoint — H2-H5 / split isolation / pre-flight

- Last verified code/test commit: f4d8d0d1e314b29f7e6a7627f99293b306f76d92. CI 42791224479 success; pilot_a_recovery 28, pilot_a3b 212, total 240 tests.
- D-064-C gate PASS; manifest fb832bcc..., test-family 01b41df8..., test-scenario dded3bb7... unchanged.
- formal_analysis.py now includes deterministic normalized input SHA-256, requires manifest/code/git provenance for confirmatory inference, and returns Student-t CI95 for regular cases.
- H2-H5 implemented through paired family-level contrasts and one four-p-value Holm family. All four are exploratory pending null/partial-null Type-I calibration.
- split_access.py, ea.py, a3_bridge.py and formal_scenario_generator.py enforce Train-only evolution, Test-restricted ordinary evaluation, no Test payload in public audit return, and atomic one-time final-evaluation ledger.
- formal_preflight.py is metadata-only and fail-closed; it does not read Test payload.
- Remaining: connect real formal runner, decide/freeze the outcome-blind five-composition roster, run R4 power/Type-I 10,000 MC, write R4 preregistration, independent review. No real Test labels/results or formal A-3b.
