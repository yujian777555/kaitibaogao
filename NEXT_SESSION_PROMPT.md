# NEXT_SESSION_PROMPT.md — Canonical Handoff Prompt

> **强制规则：本文件是下一会话唯一权威接管提示词。每次实质性研究、实验、代码、协议、审计或决策发生变化后，必须在同一轮更新本文件，并同步 README、05_DECISION_LOG.md、SESSION_HANDOFF.md。不得只在聊天中交代进展，不得让接管提示词落后于仓库事实。**

**最后维护日期：2026-11-06（Phase B 完成 + A-3b 设计完成轮）**  
**唯一仓库：** `yujian777555/kaitibaogao`  
**工作分支：** `pilot-a-stateful-recovery`  
**主分支：** `main`（实验期间不得擅自合并）

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
- AB vs AwaitSLA +0.031 p=0.007 -- search adds independent gain on top of WAIT-SLA (Q10: gain = contract semantics + evolution, NOT hand rules alone).
- AB behavioural violations 0 (A 0.060); AB stability [0.543, 0.531, 0.543]; validation AB vs A +0.142 p=0.008.
- Negative results kept: Safety Gate harmful (ABG < AB, -0.193); B alone worse than NSGA-II (-0.074); hand still ahead (AB -0.282).

### Judgement
Three mechanisms now have independent ablation evidence (contract-preserving A, WAIT-SLA, B-new). Paper claim must be "significantly better than standard EA under equal budget with behavioural safety guarantees" -- NOT "beats experts". First innovation NEARLY established.

### Next task (single)
Power analysis from the round-3 cluster variance (cluster_sd ~ 0.40) -> freeze preregistration (with the Q10-scoped claim) -> submit for user approval -> formal A-3b. Everything else stays HOLD.


# 2026-11-08 — D-063：正式 A-3b 功效核算与预注册（下一会话接管）

**执行计划：** `62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md`  
**D-062 交付：** 59（失败轨迹独立复核）/ 60（WAIT-SLA、B-new、Safety Gate 设计）/ 61（diagnostic3 结果）。  
**当前阶段：** D-062 已完成；D-063 为 PLANNED；正式 A-3b 仍 HOLD。

## 接管时先核验
- 远端分支 `pilot-a-stateful-recovery`、main、HEAD、CI。
- D-062 基线 HEAD 曾为 `730431e1c52e97adf550a54f77cb53256e302525`；后续 D-063 文档/CI 更新会产生新 HEAD。
- 79/79 是执行报告中的本地测试结果。旧 workflow 只触发 `pilot_a_recovery/**`；新 workflow `.github/workflows/research-simulator-regression.yml` 应覆盖 `pilot_a_recovery/**` 和 `pilot_a3b/**`。必须查看真实 Actions run，不能把本地结果写成 CI 通过。

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
