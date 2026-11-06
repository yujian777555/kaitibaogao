# 52 — ToolMisuseBench 审计报告

**日期：** 2026-11-06（Phase B）  
**对象：** `sigdelakshey/ToolMisuseBench` v0.2 large  
**HF revision：** `98eb28718b0393e029088ce80604c48807216de4`（last modified 2026-07-11）  
**许可：** MIT（HF 数据卡）；论文 Baral & Sigdel, REALM 2026（ACL Anthology 2026.realm-1.28）  
**官方代码：** `akgitrepos/toolmisusebench` @ `b6ee3412f98d2058ee487e182a72b26c58046d51`（经用户明确授权审计）  
**数据缓存：** `datasets/toolmisusebench/`（gitignored，哈希见 `DATASET_LOCK_MANIFEST.json`）

---

## 1. 版本与规模（实测，非数据卡转述）

仓库内并存两代数据，必须区分：

| 版本 | 位置 | train / dev / test_public | 状态 |
|---|---|---|---|
| v0.1 | 根目录 `train/dev/test_public/tasks.jsonl` | 5,000 / 800 / 1,000 | 已被 v0.2 取代，仅存档 |
| **v0.2 large** | `data/v0_2_large/*.jsonl` | **6,000 / 900 / 1,200** | **本项目采用** |

- 三个 v0.2 文件的 SHA-256 与官方 `artifacts/v0_2_large/manifest.json` **逐一吻合**（70c1f33b… / a5a2b49b… / 12c5e1e9…）。
- task_id 全局唯一（6000/900/1200），跨 split 零 ID 重叠。
- 实测统计与官方 `dataset_quality_report.json` 一致（fault 分布、difficulty 3×、budget 3×、output_grounded_task_count=600）。

任务字段（13）：`task_id, split, domain, difficulty, budget, seed, instruction, initial_state, tool_schemas, toolset_id, success_criteria, fault_plan, gold_summary`。

## 2. 任务与故障语义

- **4 领域 / 4 工具集**：crud、retrieval、files、scheduling（toolset_id `*_v1`），共 **12 个工具**，三分割工具集 100% 相同。
- **6 故障族**：clean、timeout、rate_limit、schema_drift、authz、adversarial_error；每任务 0–2 个故障。
- fault_plan 条目结构：`{fault_type, severity(soft|hard), payload{recoverability, …}, trigger{on_nth_call, on_tool}}`。
- **typed recoverability**（与我们的可恢复性分类直接对话）：transient / repairable / transient_denial / transient_with_ambiguous_feedback。
- 故障载荷实测：
  - timeout `{timeout_ms, recoverability:transient}`；
  - rate_limit `{after_n_calls, retry_after_ms, recoverability:transient}`；
  - schema_drift `{rename_args, drift_visibility:hidden_backend, recoverability:repairable}`；
  - authz `{deny, required_role, recoverability:transient_denial}`；
  - adversarial_error `{code:ambiguous_error, message:"…Try a safer recovery.", recoverability:transient_with_ambiguous_feedback}`。

### 2.1 执行语义（读官方 env/fault 代码取证）

| 问题 | 实测结论 | 证据 |
|---|---|---|
| 故障在哪一步生效？ | **全部在 `before_call` 阶段**（timeout/rate_limit/authz），工具**从未执行** | `faults/base.py FaultEngine.before_call` |
| timeout 是否有 lost-ACK（已提交但报错）？ | **没有**。timeout=事前失败，盲目重试永远安全 | `faults/timeout.py maybe_fail` 返回错误即拦截 |
| 工具是否幂等？ | **实质幂等**：update/close 为状态覆盖；create 有 `already_exists` 守卫 | `envs/crud_env.py` |
| 重复副作用可能出现吗？ | **结构上不可能**（重试不产生双写） | 同上；全文 grep `duplicate/rollback/compensat/idempoten/saga/transaction/late commit` 在数据中出现 0 次（`duplicate` 的 346 次出现在错误文案里，非效应语义） |
| 故障触发几次？ | **全部 on_nth_call=1**，单次触发；重试（第 2 次调用）必然通过 | 全量 fault_plan 统计（8,076 条触发记录） |
| 双故障计划跨工具吗？ | **不跨**：1,341 条双故障计划 100% 同工具（adversarial_error+timeout 叠加歧义文案） | 全量统计 multi-tool=0 |
| 部分提交/延迟可见/补偿失败？ | **无**（0 次出现） | 关键词全量检索 + env 代码 |

**结论：** 每条故障任务在该基准中都是"重试一次即恢复"（schema_drift 需一次参数修复）。**不存在结构性不可恢复场景**，也不存在"结果不明"歧义——这是与我们 A-3/A-3b 问题设定的**根本语义差异**。

## 3. 评分口径（从 per-task 数据独立复算，已解密）

官方 `SCORING.md` + 发布的 `deterministic_instruction_parser/episodes.jsonl`（1,200 行逐任务记录）：

| 论文报告值 | 含义（实测分母） | 独立复算 |
|---|---|---|
| Task Success 0.767 | **全部 1,200** 条 public-test 的 TaskSuccess 均值 | 0.7667 ✓ |
| Conditional Recovery 0.736 | **仅 993 条带故障任务**的 RecoverySuccess（成功且遇到过故障） | 731/993 = 0.7362 ✓ |
| Recovery-disabled 0.158 | `instruction_parser_no_recovery` 全 1,200 均值 | 0.1575 ✓ |

**"600 output-grounded" 的真实含义：** success_criteria 含 `tool_output_path_equals`（工具输出路径断言）的任务子集——test 600 / dev 432 / train 3,000。它是**难度子集**（Parser+Repair 在其上 TaskSuccess 0.8783，在 state-grounded 600 条上 0.655），**不是**论文头号指标的分母。此前文档担心的"1,200 与 600 分母混淆"已澄清：头号 TaskSuccess 用 1,200，条件恢复率用 993。

成功判据操作符：`equals`、`in`、`map_value_equals`（状态路径）、`tool_output_path_equals`（输出断言）、`successful_tool_call`。

## 4. Parser+Repair（`InstructionParserAgent`）机制分析

代码位置：`toolmisusebench/version2/baselines.py` + `baselines/schema_repair_agent.py`。

**机制 = 指令正则解析 + 错误码修参重试：**
1. **Parse**：按领域正则从自然语言指令抽取工具名与参数（crud：账户 ID + close/update/create；retrieval：doc ID/引号 query；files：路径+引号内容；scheduler：cron+job 名）。
2. **Repair**（继承 `SchemaRepairAgent`）：按错误码修复——`unknown_argument` 删参、`missing_required_arg` 别名映射（id↔doc_id↔account_id）或类型默认值、`invalid_argument_type` 类型转换；其余错误原样重试。
3. **Stop**：transcript 有成功记录且无错误即停。`InstructionParserNoRecoveryAgent` 是"只做一次、遇错即停"的消融（= recovery-disabled 0.158）。

**适用故障与局限：**
- 有效：schema_drift（本质是参数改名——正中其别名修复）、以及所有"重试即过"的瞬态故障。
- 无效/未处理：无等待/退避（rate_limit 靠触发一次性）、无状态验证、无补偿、无幂等推理、无升级。由于基准语义（§2.1）这些机制**用不上**，所以 0.767 基本是"指令解析正确率 × 预算"。
- **与我们恢复控制器的区别**：Parser+Repair 是任务解析器 + 参数修复器，不做恢复决策（何时重试、是否验证、是否补偿、是否升级）；我们的对象是在结果不明/部分提交/补偿失败下的**恢复策略**。二者不同层，但 Parser+Repair 是 ToolMisuseBench 上不可回避的强基线（其正则覆盖了该数据集的全部指令模板）。

**能否纳入 Pilot B 基线：** 能，且必须。适配方式：按官方 agent 接口（`reset()`/`act()`）接入统一 adapter，在 ToolMisuseBench train/dev/test_public 上对照。注意其强项来自模板化解析——**不可**把它当作恢复能力上限。

## 5. 本地复现（DEV，授权范围）

- 环境：Python 3.12 venv + pydantic 2.14.3（离线 wheel 安装；PyPI 直连被代理阻断，经 urllib+代理下载 wheel 解决）。
- 命令：`toolmisusebench eval --dataset <v0_2_layout> --split dev --agent-module toolmisusebench.version2.baselines:InstructionParserAgent`。

| Agent | TaskSuccess (dev 900) | 条件恢复（故障 747 条） | 对照 test |
|---|---:|---:|---|
| Parser+Repair | **0.7622** | **0.7363**（550/747） | 0.7667 / 0.7362 |
| No-recovery | **0.1511** | 0 | 0.1575 |

**复现成立**：确定性执行器与基线忠实可运行，dev 与 test 表现一致，无异常漂移。报告存档 `experiments/dataset_audit/dev_parser_report.json`（SHA-256 d2306a12…）与 `dev_norec_report.json`（33abcb83…）。

## 6. 覆盖缺口登记（对我们研究机制的适用性）

| 机制 | ToolMisuseBench | 证据 |
|---|---|---|
| Timeout（事前失败） | YES | faults/timeout.py |
| Timeout 丢失 ACK / 结果不明 | **NO** | 故障在 before_call 拦截 |
| Late commit | **NO** | 语义不存在 |
| Partial commit | **NO** | 语义不存在 |
| Duplicate side effect | **NO**（不可能发生） | 环境幂等/守卫 |
| Compensation / 补偿失败 | **NO** | 0 次出现 |
| Cross-tool saga 依赖 | **NO** | 双故障同工具；无步骤依赖 |
| Delayed visibility | **NO** | 0 次出现 |
| Idempotency 合同 | **NO**（工具无契约字段） | schema 仅 name/properties/required |
| Authorization failure | YES（一次性瞬态） | faults/authz.py |
| Safe escalation / 不可恢复类 | **NO**（全部可重试恢复） | on_nth_call=1 全量统计 |
| typed recoverability 元数据 | YES | payload.recoverability |

**定位：** ToolMisuseBench 适合评测"故障条件下的单工具调用修复与重试"，**不能**支撑我们的核心主张（状态副作用安全的恢复控制器演化）。它在 Pilot B 中的角色是**外部强基线主场 + 指令-参数修复能力对照**，不是主搜索环境。

## 7. 官方基线数值溯源（论文报告值 ≠ 我们的复现值）

- 0.767 / 0.736 / 0.158 均为**论文/发布物报告值**；本轮用官方发布的 per-task episodes **独立复算验证**了其口径（§3），并在 DEV 上**重新运行**得到一致水平（§5）。引用时须区分：test 1,200 上的 0.7667 是发布值+复算值；dev 0.7622 是我们自己的复现值。
- 发布物中另有 `deterministic_heuristic / schema_repair / policy_aware` 三个弱基线（TaskSuccess 0.0，预算耗尽型）与 Qwen3-4B 本地 LLM 面板（216 条抽样，TaskSuccess 0.796）；后者使用本地小模型，与我们的 DeepSeek API 路线无关。
