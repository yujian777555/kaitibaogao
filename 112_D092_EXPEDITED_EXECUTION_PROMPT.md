# D-092 快速实验执行提示词（2026-11-18）

## 0. 用户授权与边界

用户于 2026-11-18 明确要求：“抓紧实验吧，马上要开题了。”

将该指令记录为 D-092 实验授权：**先执行 960 Probe；只有实现关键门禁通过且全部预注册 Probe 判据 PASS，才继续正式 Train-only 五臂搜索。** 不需要再次向用户询问是否可以开始这两项 D-092 Train-only 工作。

授权不包括 Validation/Test、外部 benchmark 测试、真实 LLM/API、A800 模型训练、其他仓库实验或修改 main。13,824 exhaustive reference 仅能在正式搜索全部结果和日志锁定后，按 R2.3 §11.2 单独执行一次；不得用于调参、反馈或候选选择。

## 1. 唯一仓库与基线

- Repository: yujian777555/kaitibaogao
- Branch: pilot-a-stateful-recovery
- Start HEAD: cfe431ab026a2626bf28c00ec45352db9a7f1dd4
- main: 683b3fe7fc52c86e917d523fdc6bbb13abbfd653
- R2.3 canonical preregistration: 103_D092_TRAIN_ONLY_PREREGISTRATION.md
- Implementation: experiments/d092_recovery/
- Existing implementation self-check: 111_D092_TYPED_ADAPTER_IMPLEMENTATION_REVIEW.md
- Existing independent specification acceptance: 110_D092_R2_3_INDEPENDENT_REVIEW.md

开始前重新 fetch 并确认 branch/main/worktree。禁止切换仓库、修改 main、覆盖 R2.3/R2.2/R2.1/R1/R0、D-090 源码、Train manifest 或历史负面证据。

## 2. 已经从真实源码确认的三个阻断点

这不是猜测，请对照源码复现并修复。

### B1. Attempt Ledger 丢失失败 proposal

在 d092_runner.py 的 BudgetLedger.offer() 中，attempts 先递增，但 proposal_log 仅在成功 NEW_UNIQUE 或 DUPLICATE_CACHED 后 append。以下失败会消耗 attempt，却没有对应 proposal 记录：

- EvaluationInterrupted
- 普通 evaluator exception
- assert_optimizer_view malformed view
- genome identity mismatch
- feedback row_count mismatch

修复要求：proposal 在调用 evaluator 前先登记为 PENDING；完成后更新为 NEW_UNIQUE、DUPLICATE_CACHED、FAILED 或 INTERRUPTED。每个已消耗 attempt 恰有一条最终记录，attempts 必须等于已记录 attempt 数。失败不得进入 archive/cache，不得增加 unique_evaluations/full_episodes，不得自动重试或补预算。

### B2. Runner 没有把普通异常转为可审计 INVALID

run_arm() 目前只捕获 BudgetError 和 EvaluationInterrupted。RuntimeError、ValueError（包括 malformed optimizer view）可能直接逃逸，未返回带部分账本的 INVALID 结果。

修复要求：将可预期的 evaluator/view/identity/episode-count 错误分类并写入 ledger；run_arm 对普通 Exception 生成 INVALID 并保留已完成的 proposal、RNG、archive、audit 和部分 rollout 信息。不得捕获 KeyboardInterrupt/SystemExit。若无法精确知道已消耗的 partial episodes，明确标记 unknown，不得伪报为 0。

### B3. A1/A4 等价性检查没有比较 RNG 事件

m1_equivalence() 当前比较 proposal/round/survivor/archive 等字段，但没有把完整 rng event streams 纳入比较；因此测试通过不能证明 R2.3 §11.1 要求的逐轨迹 RNG 消耗等价。

修复要求：对 A1/A4 的每个 seed，比较完整命名 RNG stream 的事件序列（去掉仅 arm 标签差异），并比较每轮 RNG counts、proposal、parents、operator/block/locus、cache、survivor、archive、final candidate。仅忽略 R2.3 允许忽略的 arm 标签和纯反馈描述字段。新增一个会因人为篡改 RNG event 而失败的测试。

## 3. 先做最小修复，不再扩大审查范围

只处理会影响实验可信度的关键问题，不做无关重构，不改算法参数。

新增回归测试至少覆盖：

1. evaluator RuntimeError；
2. malformed optimizer view；
3. identity mismatch；
4. row_count mismatch；
5. EvaluationInterrupted 与 partial episode 数；
6. proposal attempt 一对一记录；
7. 初始 12 个 genome 中途失败；
8. A1/A4 RNG event equality；
9. 篡改 A1/A4 RNG event 后 equivalence 必须失败；
10. 失败 proposal 不进入 archive/cache。

保留历史合成结果，不得通过改变预算“修好”：

| Arm | Unique | Attempts | Status |
|---|---:|---:|---|
| A0 | 96 | 96 | VALID |
| A1 | 79 | 384 | INVALID |
| A2 | 77 | 384 | INVALID |
| A3 | 60 | 384 | INVALID |
| A4 | 79 | 384 | INVALID |

这些只是 synthetic control-flow 观察，不是算法性能比较。

## 4. 实现 Probe 执行入口

当前 experiments/d092_recovery/ 只有六个实现模块和测试文件，**尚无实际 960 Probe runner 或正式 Train-only experiment driver**。必须补齐可执行入口，而不是只写 READY 文档。

建议新增：

- experiments/d092_recovery/d092_probe.py
- experiments/d092_recovery/run_d092_probe.py
- experiments/d092_recovery/d092_search_experiment.py
- 对应 probe/search tests

Probe 必须严格遵守 R2.3 §10：

- P00–P09 十个预注册 typed genomes；
- 96 个冻结 Train scenarios；
- 每个 genome 对每个 scenario 执行一次；
- 总计恰好 960 独立 episodes；
- 不使用 cache，不与正式 search 共享账本；
- 保留每 episode 的原始 trace、outcome、before/action/mask/observation/after、episode reference、三个 phenotype hashes 和完整错误信息；
- 只用 public view 计算预注册分支标记，不读取 hidden schedule/hidden outcome；
- P03/P01、P07/P06 等对照严格按 103 §10.2–10.3；
- trace 差异只比较 action/observation 序列，cost/tick 差异不能算 PASS；
- 逐项报告 P00–P09 的 96/96 完整性和每个预注册 PASS/HOLD 判据。

Probe seed 在 R2.3 §10 未单独列出。执行前建立补充 execution lock：采用现有 evaluate_train_genome() 的明确默认 seed=711，记录依据、manifest hash、probe panel hash、环境 hash 和代码 SHA；在第一条 rollout 前提交锁文件。不得看结果后改 seed。

任何 probe 对照 HOLD，正式 Train-only search 暂不启动；但不得因此终止整个课题。保留所有结果，定位具体机制问题，提出 D-093 新候选和新预注册方案，不得反复重跑同一冻结 Probe 来调参。

## 5. Probe 全部 PASS 后，立即运行正式 Train-only 搜索

无需再次等待用户确认；这是本轮授权的条件性下一阶段。

严格使用 R2.3 冻结配置：

- 5 arms: A0/A1/A2/A3/A4
- 5 seeds: 711/822/933/1044/1155
- 每个 arm×seed：96 unique genome evaluations
- 每个 genome：96 个 Train episodes
- 每个 arm×seed：9,216 episodes
- 384 proposal attempts cap，包含初始化、重复和 cache hit
- μ=12、λ=12、7 rounds
- 不改变五臂、反馈矩阵、NSGA-II/III、目标、硬约束、统计门槛和 RNG 语义

正式搜索总设计量为 5×5×96×96 = 230,400 episodes。按 seed/arm 分账、分文件保存。每个 run 必须有完整 proposal/attempt/RNG/feedback/survivor/archive/episode/audit ledger。

A3 反馈只能来自上一轮 12 个真实 unique offspring 的完成聚合结果。A4 永久零反馈。A1/A4 必须逐 seed 完整轨迹和 RNG 等价。

INVALID、attempt cap、partial rollout、NO_FEASIBLE_CANDIDATE、complete phenotype collapse 必须按 R2.3 §12 保留，不删除 seed、不补预算、不替换候选、不用剩余 seed 计算 4/5。若运行出现 INVALID，保留证据并诊断原因；不得擅自放宽预算或修改协议。

主比较和 GO 判据严格使用 R2.3 §12.1。只有所有相关配对完整且可行，才计算预注册均值与 4/5 条件。不得把 synthetic tests 或 Probe PASS 写成算法提升。

## 6. 环境与 CI

正式执行环境按 R2.3 §13.1：

- Ubuntu 22.04 LTS x86_64
- CPython 3.11.9
- NumPy 1.26.4
- PYTHONHASHSEED=0
- 依赖 hash lock
- 不引入未审查演化框架

现有 workflow 使用 ubuntu-latest/Python 3.11，不能直接冒充目标环境验证。增加 D-092 专用的 Ubuntu 22.04 / Python 3.11.9 检查，运行完整回归。CI 只证明实现与测试，不证明算法提升。

## 7. 结果、报告和仓库维护

建议产物目录：

- experiments/d092_recovery/results/probe/
- experiments/d092_recovery/results/train_only/
- experiments/d092_recovery/results/exhaustive_reference/

新增报告：

- 112_D092_TYPED_ADAPTER_INDEPENDENT_REVIEW.md
- 113_D092_PROBE_RESULT.md
- 114_D092_TRAIN_ONLY_RESULT.md

只有当对应工作实际完成后才创建对应结果报告；不提前伪造 PASS 或结果。

每次推进更新 README.md、SESSION_HANDOFF.md、NEXT_SESSION_PROMPT.md、05_DECISION_LOG.md、51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md。提交后核验本地/远端 HEAD、main、ahead/behind、clean worktree、diff --check、CI run、关键文件 blob SHA 和 artifact manifest。

## 8. 最终目标

本轮不以“文档齐全”作为交付。目标是：

1. 修复三个已确认的实现门禁问题；
2. 独立实现审查达到 ACCEPT_FOR_PROBE；
3. 真正执行并交付 960 Probe 原始数据；
4. Probe 全部 PASS 后，立即执行五臂×五 seed Train-only 搜索；
5. 产出可复算的逐 seed 结果、对照差值、硬约束和资源账本；
6. 如 A3 未提升，不停止整个研究：基于真实失败轨迹提出新的演化机制候选，建立新预注册与新 Train 证据，不篡改 D-092。

**当前任务优先级：修复 → Probe → Train-only 搜索 → 结果复算。不要再开展大范围文献调研或反复重写开题文档。**
