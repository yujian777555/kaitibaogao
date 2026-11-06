# 53 — UndoBench 审计报告

**日期：** 2026-11-06（Phase B）  
**对象：** `TanmaySah/undobench` v1.0.1  
**HF revision：** `4be1151851a109e7c9cfc1ba5d6e6c64461f6f93`（last modified 2026-10-07）  
**许可：** 数据/规格 CC-BY-4.0，执行软件 Apache-2.0  
**论文：** arXiv:2610.05622  
**官方代码：** `tradertanmay/undobench`（内部包名 RecoverBench）@ `4a25c4fa0f12bb6c79dc6e0e3a8f31deeb6af21e`  
**数据缓存：** `datasets/undobench/`（gitignored；parquet 哈希见 `DATASET_LOCK_MANIFEST.json`）

---

## 1. 数据实测（36 行全量）

三个 parquet 通过 HF datasets-server 逐行取出（14/10/12），字段与数据卡 schema 一致：`task_id, split, domain, workflow_name, workflow_description, objective, fault_scenario(JSON), fault_boundary, reversibility, idempotency_support, tools, initial_state(JSON), expected_outcome(JSON), required_effects(JSON), oracle_spec(JSON), benchmark_version, source_path`。

| 维度 | 实测分布 |
|---|---|
| splits | dev 14 / validation 10 / test 12（task_id 唯一，零重叠） |
| domains | cloud 4, crm 4, database 5, git 4, messaging 5, payments 5, storage 5, ticketing 4（8 领域） |
| fault_boundary | POST_MUTATION_PRE_ACK **33**、DURING_COMPENSATION 1、POST_ACK_PRE_CHECKPOINT 1、DURING_MUTATION 1 |
| scenario_id | SCN-LOST-ACK **33**、SCN-COMPENSATION-CRASH 1、SCN-POST-ACK-PRE-CHECKPOINT 1、SCN-DURING-MUTATION 1 |
| perturbation | ACK_LOSS 33、RECOVERY_CRASH 1、WORKER_CRASH 1、PARTIAL_WRITE 1 |
| observability | **UNKNOWN_OUTCOME ×36（全部）** |
| reversibility | COMPENSATABLE 24、REVERSIBLE 4、IRREVERSIBLE 8 |
| idempotency_support | **false ×36（全部无原生幂等）** |
| tools | 每工作流 1–3 个（1 工具 17 条、2 工具 18 条、3 工具 1 条）；46 个不同工具名 |
| required_effects | op_type CREATE 30 / UPDATE 21 / DELETE 3 / EXECUTE 2；max_occurrences 1(53)/2(3) —— **重复效应上界显式建模** |
| oracle_spec | 22/36 含 `forbidden_effects`（如 "Overprovisioned duplicate cluster nodes due to blind retry"）；6/36 含 `invariants` |

**语义要点（与我们问题设定的关系）：**
- 每条工作流都是 **lost-ACK 语义**（已变更、回执丢失、结果不明）——正是 ToolMisuseBench 完全没有、而我们 A-3 部分覆盖的核心场景；33/36 是标准 LOST-ACK，另有补偿期崩溃、变更期崩溃、回执后检查点前崩溃三种稀有边界。
- **无原生幂等**（idempotency_support 全 false）→ 盲目重试会真实制造重复副作用，DER 指标有实际意义。
- IRREVERSIBLE 8 条 + forbi­dden_effects 22 条 → 存在"不可补偿/必须安全停止"的场景，与我们的 Safe Escalation 类直接对应。
- 隐藏字段隔离已由官方声明：`initial_state, expected_outcome, required_effects, oracle_spec, fault_scenario` **不作为策略输入**（README 明文），与我们 PublicToolView 的隔离原则一致。

## 2. 指标实现（docs/METRICS.md + summary.json 实测）

配对反事实设计：同初始状态、同 seed 的 CONTROL 试验 \(C_i\) 与 FAULT 试验 \(F_i\)。

| 指标 | 定义 | 备注 |
|---|---|---|
| Control Pass Rate | \(\frac{1}{N}\sum C_i\) | 名义任务能力 |
| RSR | \(\frac{1}{N}\sum F_i\) | 无条件恢复成功率 |
| **CRSR** | \(P(F_i=1 \mid C_i=1)=\frac{\sum C_i F_i}{\sum C_i}\) | **主指标**：会做该任务的前提下能否抗故障恢复 |
| DER | 故障试验中出现重复外部副作用的比例 | 盲目重试双扣款即 DER=1 |
| MER | 提前中止遗留必需效应的比例 | 对应我们的 unresolved |
| URR | DER>0 ∨ MER>0 | 综合安全违规率 |
| EOR（uncond/cond） | F=1 ∧ DER=0 ∧ MER=0（且效应次数精确） | exactly-once 黄金标准 |

CRSR 与我们"可恢复场景条件成功率"思想同构（条件在名义能力而非可恢复性上）；DER/MER/EOR 与我们的 duplicate/unresolved/safe-resolution 语义一一对应。`summary.json` 输出字段与文档一致（total_pairs、control_passed、crsr_passed、eor_passed、der、mer、task_breakdown）。

## 3. 本地 smoke / DEV 接口验证（TEST 锁箱）

| 步骤 | 结果 |
|---|---|
| `recoverbench.cli doctor` | **PASS**：36 任务加载（14/10/12）、47 工具、协议 V4、沙箱可实例化、工具 schema 100% 合规 |
| `recoverbench.cli smoke` | **PASS**（0.14s）：CONTROL 成功、故障注入、恢复层、oracle 评估、effect log、离线指标复算全链路 |
| `run --agent simple_agent.py:SimpleDeterministicAgent --split dev --recovery none --seeds 42` | 14 对（28 trials）执行完毕；Control 0/14、RSR 0、CRSR=N/A、DER 0、MER 1.0 |

说明：示例 agent 是接口演示用的天真规则（顺序调用工具、不做任务理解），全部 CONTROL 失败属预期；本轮运行**目的**是验证配对 CONTROL/FAULT 管线与 CRSR/DER/MER 计算链路可用，而非基线成绩。产物：`experiments/dataset_audit/ub_dev_smoke_summary.json`、`ub_dev_smoke_config.json`。

**TEST 锁箱证据：** harness 配置含 `allow_frozen_test_execution: false`（默认锁），运行 manifest 记录 benchmark_version/protocol_version/git_commit。本轮**未**在 test 执行任何 agent；仅读取 test 元数据做泄漏审计（见 `SPLIT_LEAKAGE_AUDIT.md`）。

## 4. 代码与许可

- 软件 Apache-2.0（pyproject.toml）；数据卡 CC-BY-4.0。引用需署名。
- 工程结构：`recoverbench/`（engine、cli、domains 8 个沙箱、agents 适配器）+ `benchmark/public_tasks`。agent 接口为 `UndoBenchAgent.run(task, tools, context) -> AgentResponse`（或 HTTP/脚本适配器），与 ToolMisuseBench 的 `reset()/act()` 不同——统一 adapter 需分别封装（Phase C）。
- Windows 注意：`--agent` 参数的 `module:Class` 解析与盘符冒号冲突，需用相对路径或 `file.py:Class`（本轮实测）。

## 5. 结论与用途判定

**UndoBench 是目前唯一公开、可执行、直接覆盖我们核心语义（结果不明、重复副作用、不可逆效应、补偿边界）的基准。** 建议角色：
- **外部泛化验证（锁箱 TEST 12 条）**：方法与预算冻结后一次性评估，按 workflow×fault cluster 统计（样本量小，不能把重复 seed 当独立任务）。
- **DEV 24 条（dev 14 + validation 10）**：接口适配、恢复控制器的跨环境 sanity、我们的策略表示在第二种执行栈上的可行性检查。
- **不作为主演化搜索环境**：36 条工作流对演化搜索的样本量太小，且 33/36 同为 LOST-ACK 单一场景族，搜索会过拟合该场景。
- 必须复现的基线：官方 baseline（`--recovery none` 与 scripted agents）+ 我们的安全手工策略（saga_aware 适配版）；LLM 基线待真实 API 授权后另列。

## 6. 风险登记

1. **场景族单一**：test 12 条全部 SCN-LOST-ACK / POST_MUTATION_PRE_ACK——外部验证实质是"lost-ACK 泛化"，不能代表部分提交/补偿失败等其他边界（那些只在 dev/validation 各 1–2 条）。
2. **样本量**：N=12，任何比例指标的置信区间都很宽；必须 cluster-aware 报告，禁止用多 seed 重复冒充样本量。
3. **领域全覆盖于三分割**：8 领域在 dev/val/test 均出现（见泄漏审计）——按领域泛化不成立，按工作流/工具泛化才是其划分方式。
