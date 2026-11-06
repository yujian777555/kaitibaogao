# 50 — 第一项创新的数据集选择与验证协议建议

**日期：** 2026-11-06  
**范围：** 第一项创新候选：状态化工具型 Agent 恢复控制器演化  
**状态：** DATASET PLAN / PROPOSED, NOT FROZEN  
**工作分支：** pilot-a-stateful-recovery

## 0. 结论先行

不建议只用一个数据集，也不建议把静态 JSONL 直接当作演化算法的训练数据。第一项研究需要可执行工具环境，演化个体必须实际执行任务/故障 rollout，按真实环境状态、副作用和恢复结果计算 fitness。

推荐组合：

1. **主开发/搜索环境：当前仓库 Pilot A-3 自有确定性模拟器 + ToolMisuseBench v0.2 large 的 train split。**
2. **验证/调参：Pilot A-3 的 validation splits + ToolMisuseBench dev split。**
3. **冻结确认性外部验证：ToolMisuseBench public test + UndoBench TEST split。**
4. **无故障正常任务回归：ThinkingBox-Bench v1.0 或 ToolSandbox；只能作为外部回归验证，不应替代故障恢复主基准。**

这是一份建议，不代表数据已下载、适配、复现或最终冻结。开始算法实验前必须先完成数据版本、许可、执行器、划分泄漏和指标语义审计。

## 1. 为什么需要“可执行基准”而不是普通文本数据集

研究对象是恢复控制器，不是文本分类器。每条样本至少需要：
- task goal / task family；
- initial environment state；
- 可调用工具及 schema；
- tool contract（idempotent、compensatable、可观测性/visibility bound 等）；
- fault plan 与触发阶段；
- 可执行环境转移；
- success criteria / postconditions；
- effect history / invariant oracle（只供评估，不暴露给策略）。

GA/GP/NSGA 的 fitness 必须来自策略在环境中的 rollout。数据集任务定义可复用，但需要真实执行环境和确定性 grader。

## 2. 主开发候选：ToolMisuseBench v0.2 large

### 2.1 官方信息
- 论文：Rista Baral, Akshey Sigdel, “ToolMisuseBench: An Offline Deterministic Benchmark for Tool Misuse and Recovery in Agentic Systems”, REALM 2026, ACL Anthology ID 2026.realm-1.28。
- 论文：https://aclanthology.org/2026.realm-1.28/
- 数据：https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench
- 执行器/代码：https://github.com/akgitrepos/toolmisusebench
- 数据卡标注 MIT license。
- v0.2 large：train 6,000 / dev 900 / public test 1,200；CRUD、retrieval、files、scheduling；clean、timeout、rate limit、schema drift、authorization、adversarial error；难度 easy/medium/hard；budget tight/standard/relaxed。
- 样本字段包含 initial_state、tool_schemas、fault_plan、success_criteria、budget、domain、difficulty、seed 等。
- 论文定位为 deterministic fault-conditioned recovery benchmark，含 typed recoverability metadata 和 output-grounded success criteria。

### 2.2 建议用途
- train：可用于恢复控制器的演化搜索与开发；必须实际执行任务，不是对文本标签做监督学习。
- dev：用于参数选择、策略选择、消融开发。
- public test：冻结，只在算法、超参数、表示、算子和预算全部锁定后做最终确认；不得反复查看后继续调参。
- 用官方 deterministic executor/reference agents 作起点，核实可复现基线和 fitness 定义。

### 2.3 必须审计的限制
1. 该数据集直接覆盖 fault-conditioned recovery 和 typed recoverability，属于本研究的近邻基准；不能将它本身作为论文创新。
2. 其四类任务域不等于完整多工具 Saga；要逐项检查跨工具依赖、partial commit、compensation failure、late commit 和不可读回状态是否存在。
3. ACL 论文摘要报告 1,200 public-test tasks；HF README 同时写明 public test 有 1,200 条记录、其中 600 条为 output-grounded tasks。最终统计分母必须从冻结 manifest/JSONL 和 evaluator 实际运行核实，不可只引用摘要数字。
4. 检查 train/dev/test 的 task family、fault family、tool schema、initial-state template、seed 是否泄漏；不能假定 split 天然实现 task-family × fault-family 双重 OOD。
5. 数据卡和代码版本必须固定到 commit/revision，并保存 manifest、SHA-256、license 和环境依赖。
6. 数据集的公开 test 是 public，不是秘密测试集；要在研究仓库内部实行“锁箱”，只运行预注册的最终一次评价。

## 3. 自有 Pilot A-3 模拟器：补足多工具 Saga 与复合副作用

- 继续使用 47_PILOT_A3_PROTOCOL.md 中的六个三步任务族、独立 per-tool fault vector、Saga dependency、partial commit、delayed visibility、compensation failure。
- 但 A-3 目前仍须先核验 GitHub Actions 和 JSON/CSV；未通过 47 号预注册 gate 前，不进入 Pilot B。
- A-3 适合作为研究者可控的算法搜索/机制消融环境，不得单独作为外部有效性证据。
- 如果扩展 scenario generator，新增任务族和故障组合只能进入 train/validation；held-out task/fault/joint-shift 继续锁箱，不得在看到结果后修改。
- 建议补足 ToolMisuseBench 不覆盖的异构 effect contracts、多工具依赖、逆序补偿和补偿失败；先做 feature-level coverage matrix，确认真实缺口再开发，避免重复造 benchmark。

## 4. 外部恢复验证：UndoBench

- 论文/数据：UndoBench, “Separating Task Competence from Recovery Capability in Tool-Using AI Agents” (2026 preprint)。
- 数据入口：https://huggingface.co/datasets/TanmaySah/undobench
- 论文入口：https://arxiv.org/abs/2610.05622
- 36 workflows / 36 fault scenarios / 8 enterprise domains；DEV 14、VALIDATION 10、TEST 12。
- 采用相同 seed 的 CONTROL / FAULT paired executions，并以 effect-history/environment-state oracle 评价恢复和 duplicate effects。

建议：
- 不用 TEST 训练/调参；算法锁定后进行跨基准外部验证。
- 由于 TEST 仅 12 个 workflow，统计单位不能简单按多次重复 episode 当作独立 task；应按 workflow/fault scenario cluster 做 paired analysis，并明确样本量有限。
- 不应声称 UndoBench 是我们自己提出的 benchmark；重点报告外部迁移表现。

## 5. 正常任务能力回归：ThinkingBox-Bench 或 ToolSandbox

### 5.1 ThinkingBox-Bench v1.0
- 507 executable stateful business tasks / five domains。
- 任务提供初始后端状态、工具和 policy、用户目标，并通过 final backend state / side effects 的 executable checks 评分。
- 数据入口：https://huggingface.co/datasets/microsoft/ThinkingBox-Bench
- 执行代码/数据：https://github.com/microsoft/thinkingbox-data
- 重要限制：官方数据卡明确标注 intended exclusively for evaluation；不得将 task content、expected outcomes、gold states 或 tool trajectories 用于 prompt optimization、fine-tuning、RL 或其他模型优化。
- 因此只能在恢复控制器冻结后作为 no-fault/normal-workflow regression check；不得用于演化搜索、调参或学习。

### 5.2 ToolSandbox
- 论文：https://aclanthology.org/2025.findings-naacl.65/
- 代码：https://github.com/apple/ToolSandbox
- 具有 stateful tool execution、工具间隐式状态依赖、用户模拟器和 arbitrary trajectory 的动态中间/最终评价。
- 它主要是 stateful tool-use benchmark，不是专门的 fault-recovery benchmark。
- 可用于正常工具执行/状态依赖能力回归；若自行加入 fault injector，结果应标记为 ToolSandbox-derived modified setting，而非原始官方分数。

### 5.3 可选：τ²-Bench-Verified
- 代码：https://github.com/amazon-agi/tau2-bench-verified
- 是修正和验证后的 τ²-bench 版本，涵盖 mock、airline、retail、telecom 等工具环境。
- 可用于额外的 clean-workflow 泛化；原生任务并非专门为复合故障恢复设计，因此不是第一项创新的主数据集。

## 6. 推荐的实验分工（初始方案）

| 层次 | 环境/数据 | 用途 | 允许调参？ |
|---|---|---|---|
| EA search / train | Pilot A-3 train + ToolMisuseBench train | 搜索策略基因、算子开发、机制消融 | 是 |
| Development | Pilot A-3 validation + ToolMisuseBench dev | 选择参数、冻结候选策略 | 是，但须记录 |
| External recovery test | ToolMisuseBench public test | 冻结算法确认 | 否，最终一次 |
| Cross-benchmark recovery test | UndoBench TEST | 外部迁移/配对复现 | 否，最终一次 |
| Clean regression | ThinkingBox-Bench v1.0 或 ToolSandbox | 确认恢复改进没有损害正常工具任务 | 否；ThinkingBox 明确禁止用于优化 |

重要：Pilot A-3 现有样本数与任务族数有限；ToolMisuseBench 也不能替代多步骤 Saga。应先审计后确定训练比例和真正独立的 OOD split，不要现在就把上表当成冻结实验协议。

## 7. 统一指标

主指标：
- Conditional Recovery Success；
- Safe Resolution / Correct Final State；
- Worst-group recovery success（task-family × fault-family）。

硬门禁：
- Critical invariant violation；
- Duplicate side-effect rate；
- Incorrect compensation / compensation falsely reported successful；
- Unsafe retry under unknown outcome。

辅助指标：
- unresolved residual effects；
- recovery tool calls / steps；
- wall-clock / token / rollout cost；
- normal clean-task regression；
- calibration / abstention when outcome is unobservable。

任务成功不能抵消硬安全违规。必须同时报告 clean-control 和 faulted condition，使用相同 initial state / seed 的 paired trials。

## 8. 进入 Pilot B 前的数据 Gate

1. 下载并固定 ToolMisuseBench v0.2 large、UndoBench、ThinkingBox 或 ToolSandbox 的准确版本与 license。
2. 对 ToolMisuseBench 做 manifest/checksum、样本 schema、fault_plan、recoverability metadata、success criteria、task/fault leakage 审计。
3. 对 UndoBench 做 14/10/12 split 和 paired-control semantics 审计。
4. 对 A-3 做 CI、JSON/CSV 独立重算；按 47 号预注册 gate 作判断。
5. 形成 benchmark coverage matrix：timeout-before/after、late commit、partial mutation、delayed visibility、schema drift、authorization、cross-tool saga、compensation failure、no-readback、idempotency。
6. 明确每个 baseline 能否在各 benchmark 上执行，无法执行时给出 faithful adaptation 及限制，不得把未运行的论文方法写成实测对照。
7. 在数据 Gate 和 A-3 Gate 均通过前，Pilot B 仍 HOLD；不启动真实 LLM API，不训练 ARWM，不使用 A800。

## 9. 本轮最终建议

**优先组合：ToolMisuseBench（开发/搜索） + 自有 A-3（多工具 Saga 补充） + UndoBench（外部恢复验证） + ThinkingBox/ToolSandbox（正常任务回归）。**

如果时间和工程资源必须收缩，最低可接受组合是：
- A-3 + ToolMisuseBench train/dev 做算法开发；
- ToolMisuseBench public test + UndoBench TEST 做锁箱外部验证；
- 不把 ThinkingBox 作为必需项。

这套方案比只在自建模拟器上跑 GA/NSGA 更有说服力，也能避免把已有 benchmark 的任务内容当成自己的创新。
