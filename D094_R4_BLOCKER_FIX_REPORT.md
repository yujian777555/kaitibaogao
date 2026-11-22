# D-094 R4 三项执行阻断修复报告

日期：2026-11-23。工作分支：`d094-llm-agent-integration`。接管基线：`d1351297e700130ac7fc117868d86ba3a7b852ef`。原独立审查：`D094_R4_INDEPENDENT_REVIEW.md`，结论 `REQUEST_CHANGES`，报告 SHA-256=`f91acb68d3c8596bc11484f5efc9a5d0da23604eb00ec49a1f6bcb39b4e33056`。

## 1. 当前科学状态

- 本轮只实现 R4-001～R4-003 的执行可靠性修复，没有更改任务、seeds、四臂、搜索算法、主要终点、最小效应或统计公式。
- 真实 R4=`NOT RUN`；真实 LLM API 调用=0；真实性能结果=无。
- 独立复审=`PENDING`。本报告是实现者自检，不是独立 ACCEPT。
- 完成提交与 CI 核验后的最高状态仅为 `READY_FOR_INDEPENDENT_REVIEW`，不是 `APPROVED_FOR_EXPERIMENT`。独立审查通过后仍需用户明确授权。

## 2. R4-001：冻结配置 fail-closed

实现位于 `experiments/d094_llm_agent/run_d094_r4.py`：

1. 新增集中 `_validate_frozen_config`，在 `run_r4` 第一行及 `compute_budget_plan` 入口执行。
2. 对 `R4Config` 每个字段同时比较类型和值，拒绝 `True == 1` 一类类型绕过。全局配置直接冻结为 320 requests / 0.442368 USD。
3. 校验 Fresh Train task IDs、canonical manifest SHA、B1 Fixed、B2 standard、B3 paired_credit、B4 failure_feedback、公共五步及全部调用方行为参数。
4. 预算计划再次核对 64 episodes、320 requests、0.442368 USD、四个 B1/final 预留池和三个独立搜索池。
5. 非法配置在输出目录、client、episode 和 HTTP 之前抛出带具体字段原因的 `ValueError`，不写失败实验产物。

反例覆盖 seeds=(401,402)、search_seed=999、generations=2（会得到 88 episodes）、440 requests、0.608256 USD、模型、每 episode 请求上限、布尔类型绕过、Train task ID、臂配置及 Fixed genome 五步。合法冻结配置仍为 `PREFLIGHT_PASS`，client 构造数=0。

## 3. R4-002：统计与最终分析入口进入 V2 执行锁

- 新执行锁版本：`D094_R4_EXECUTION_LOCK_V2`。
- `SOURCE_NAMES` 从 15 个扩展到 17 个，新增 `d094_r4_statistics.py` 与最终分析入口 `d094_r4_analysis.py`。
- `d094_r4_statistics.py` 未修改，SHA-256 保持 `59e16ee7457db7157d2ce2c5283c8ec0d17b009cc4a50c5be5a636187044643e`。
- 新分析入口按排序后的四个 `(task_id,seed)` final 单元构造 B3−B2、B4−B2、B3−B4、B2−B1，再调用既有 `preregistered_analysis`。`_mock_statistics` 保留为兼容包装。
- 锁内冻结 4 个独立单元、16 个符号模式、20,000 次 bootstrap、基础 seed=20261120、offsets=0/1/2/3、四比较 Holm 和最小效应 0.25。
- `verify_execution_lock` 重建期望锁并报告首个不一致字段；执行锁自身不嵌套哈希，避免循环。
- `statistical_analysis.json` 绑定 execution lock 原始字节 SHA、Train manifest canonical SHA、统计源码 SHA 和分析入口 SHA。

独立篡改测试在临时目录复制源码及协议文档，分别修改符号翻转、bootstrap、Holm 和最终分析入口；四次均无法通过锁验证，生产源码前后 SHA 不变。

统计解释不变：每次主要比较只有 2 个任务×2 个 seeds=4 个 final 配对单元；16 只是符号翻转模式数量，不是 16 个独立样本。所有统计仅作探索性描述，不支持跨任务普遍显著性。

## 4. R4-003：三个搜索池独立硬隔离

| 池 | 冻结请求上限 | 冻结成本上限 | 新 Mock 实际请求 | 新 Mock 成本上界 USD | 剩余请求 |
|---|---:|---:|---:|---:|---:|
| search:B2 | 80 | 0.110592 | 48 | 0.0003744 | 32 |
| search:B3 | 80 | 0.110592 | 48 | 0.0003744 | 32 |
| search:B4 | 80 | 0.110592 | 58 | 0.0004524 | 22 |

- 运行时预留全部七池；搜索 `_episode` 使用 `search:{arm}`，不再使用共享 `search`。
- B1 和 final:B2/B3/B4 继续各预留 20 requests / 0.027648 USD；新 Mock 各实际 10 requests。
- `ReservedBudget.pool_snapshot` 记录每池请求数、成本上界、剩余量及 pending；run summary 新增 `search_pool_ledgers`。
- 三个臂各自的第 81 次直接 transport 请求均在底层调用前拒绝，底层计数保持 80，其他池不变。
- B2→B3、B3→B4 剩余预算不可借用；B4 在其他两池未用时仍不能发起第 81 次。
- 重试和异常逐次计入对应池；unknown usage 保留该请求最坏成本上界；pending 清零。缩小规模的全局上限单元测试证明传输不可越过全局 cap，未改变正式 R4 配置。

## 5. 实际测试证据

- 新增 `test_d094_r4_review_fixes.py`：15/15 通过。
- 新测试+原 R4 协议测试：22/22 通过。
- D-094 全量 discover：150/150 通过；旧结果为 135，新增 15。
- 七目录本地实际执行：28/28、396/398、8/8、8/8、14/14、86/86、150/150，总计 690/692。
- 两项失败均位于未修改的 pilot_a3b 历史测试，本地 Python=3.12.16：
  - `test_d087_replication...test_independent_audit_and_immutable_outputs`：residual/action_cost 仅有末位浮点表示差，例如 1.3250000000000002 与 1.325。
  - `test_dependency_gate...test_saved_gate_matches_raw_recomputation`：同类严格摘要相等断言失败。
- 未修改上述历史数据、测试或判据；CI 使用 Python 3.11.9，最终结果必须以实际 CI 日志为准，不能把本地两项写成通过。
- `compileall`：PASS。`git diff --check`：PASS。
- Black：`NOT RUN (No module named black)`；未擅自安装依赖。

## 6. 新产物与原始字节 SHA-256

旧 `r4_preflight/`、`r4_synthetic/` 以及 R1/R2/R3.1 历史结果未覆盖。新目录：

- `experiments/d094_llm_agent/results/r4_preflight_review_fix/`
- `experiments/d094_llm_agent/results/r4_synthetic_review_fix/`

| 项目 | SHA-256 |
|---|---|
| Train manifest canonical（不是 raw） | `e8412c74c33faf7a56195d685d49080b5669dbe46efd3ae1ab6dee88917b5bff` |
| Train manifest raw | `d3114d002b74ee877dc37a794938f63bd6446c7b8ebbc93c461035b1c824d520` |
| budget_plan.json raw | `903b2cf11c90cd26286a6e2faa5e3c92b4f984ceda8a9c3de2651d232611ee97` |
| preflight execution_lock.json raw | `d31efba77b98bd96cdd3faf70481b26dd6106695fdff0ba431fcea7abe5b9a8a` |
| Mock execution_lock.json raw | `b9a41961140e4b6058c61bc698ba4373d15a91b7228b1227c7f8db9310c148e2` |
| d094_r4_statistics.py raw | `59e16ee7457db7157d2ce2c5283c8ec0d17b009cc4a50c5be5a636187044643e` |
| d094_r4_analysis.py raw | `ae9f93ef052be1a12daa68eb0cf00f6011d182a63483844208552de67a6c2be9` |
| episodes.jsonl raw | `caad5bf5af3325e28dd7951cd7468e522d568b392a69c861a890b683b5b99cdc` |
| statistical_analysis.json raw | `33b20aea0e132c09bed5591703a700ba1f7696c22c6b90f356ba72022aa03d96` |
| verification_report.json raw | `4ad4f6648c2e00c8eb7c01d984201d80e9994e6396f4ecbc67633ba80eb27b0b` |
| preflight artifact_sha256.json raw | `7af415f0f93a7e86bf20c40c2f4c143bf671de59b4952d59d255f52451062d09` |
| synthetic artifact_sha256.json raw | `ef030255a21a6152a690e74dfc1638f19d491f53eb13b7a6e45f9afa3bdc5c37` |

独立复算实际读取 raw bytes，覆盖 17 个锁源码、4 份协议文档、64 条 episodes、194 个唯一预算请求 ID、64 条 trace 及 artifact 清单，结果 PASS。新 Mock 为 64 episodes、194 requests，成本上界 0.001513200000000003 USD；这些数字仅证明软件路径可执行，不是账单或真实 Agent 性能。

## 7. 发布、CI 与保护项

代码提交与 CI run/job 日志见 `D094_R4_STATUS.json`；最终文档 HEAD 必须动态查询 Git，不能由该文件自嵌套。文档提交若未触发 workflow，应写 `NOT RUN (docs-only path filter)`，不能沿用代码提交 CI 冒充新 run。

保护项继续保持未提交：`experiments/pilot_a3b/confusion_report.json`、`I_need_interpret_use.txt`、`incoming/`。main 必须保持 `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。

唯一下一步：由新的独立会话按 `D094_R4_INDEPENDENT_REVIEW_PROMPT.md` 只读复核并给出 `ACCEPT` 或 `REQUEST_CHANGES`。真实 R4 继续禁止，直到独立 ACCEPT 且用户明确授权。
