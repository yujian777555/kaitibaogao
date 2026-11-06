# NEXT_SESSION_PROMPT.md — Canonical Handoff Prompt

> **强制规则：本文件是下一会话唯一权威接管提示词。每次实质性研究、实验、代码、协议、审计或决策发生变化后，必须在同一轮更新本文件，并同步 README、05_DECISION_LOG.md、SESSION_HANDOFF.md。不得只在聊天中交代进展，不得让接管提示词落后于仓库事实。**

**最后维护日期：2026-11-06（Phase A 独立复核完成轮）**  
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

### 4. 当前唯一下一任务：Phase B 数据集审计 + A-3b 新预注册设计

Phase A（A-3 独立复核）已完成，结论 HOLD，详见 `PILOT_A3_INDEPENDENT_REAUDIT.md` 与 D-057。不要重跑 A-3，不要启动 Pilot B。按顺序执行：

1. 重新核验远端 `pilot-a-stateful-recovery` 和 `main` HEAD、ahead/behind、工作树状态。
2. **Phase B（51 号计划 §3）：公开数据集只读审计**——
   - ToolMisuseBench v0.2 large：固定 HF dataset commit/revision，下载 train/dev/test_public 与 manifest/freeze/quality 文件，全部算 SHA-256；核验 6,000/900/1,200 行数、task_id 唯一性、600 output-grounded 子集、domain×fault_family 分布、官方 evaluator 分母语义（0.767/0.736/0.158 是论文报告值，不是我们的复现值）；做 train/dev/test 的 task/fault family 泄漏审计。
   - UndoBench v1.0.1：固定数据与官方代码 commit；核验 14/10/12 split、CC BY 4.0 / Apache 2.0、paired CONTROL/FAULT 语义、指标实现；TEST 锁箱，只用 DEV/validation 做接口 smoke。
   - ThinkingBox-Bench v1.0：仅记录 507 tasks/5 domains 与 evaluation-only 约束。
3. **A-3b 新预注册协议设计（先设计、后批准，不得直接开跑）**——针对 A-3 定位的失败边界：(a) 可行性分层的评价定义（区分结构性不可行场景）；(b) 补充可行的 held-out 故障组合族或明确可行/不可行标注；(c) 动作成本作为独立优化维度的评价方案。新协议必须保留 A-3 结果不动、held-out 继续锁箱，预注册后才允许运行。
4. 产出 Phase B 交付：DATASET_LOCK_MANIFEST.json、BENCHMARK_COMPATIBILITY_MATRIX.md、SPLIT_LEAKAGE_AUDIT.md、LICENSE_AND_PROVENANCE.md（51 号计划 §3 规定）。
5. 只有 A-3b Gate 通过 + 数据兼容 Gate + adapter smoke 通过，才可起草 Pilot B 预注册。Pilot B 必须证明 EC 超越强手工恢复策略与 Parser+Repair 等强基线，而不是只超过 blind retry。
6. A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 优化、双种群协同演化均需独立前置证据和明确授权，不得自动启动。

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
