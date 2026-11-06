# PILOT_A3_INDEPENDENT_REAUDIT — Pilot A-3 独立复核与预注册 Gate 判定

**日期：** 2026-11-06  
**工作分支：** `pilot-a-stateful-recovery`  
**复核对象：** Pilot A-3（`47_PILOT_A3_PROTOCOL.md`）的 CI 运行、原始 artifact 与全部指标  
**复核方式：** 不信任模拟器 JSON 汇总，从 episode CSV 独立重算全部指标并按 47 号预注册 Gate 原文判定  
**最终判定：** **HOLD（HOLD_REVIEW_FAILURE_BOUNDARIES）— 不进入 Pilot B**

---

## 0. 结论摘要（先看这里）

1. **A-3 确实运行了。** 修复前的全部 A-3 workflow run（`76f62c09` 起）在 "Run Pilot A-3 simulator" 步骤崩溃，artifact 从未产生；修复后 run **42241224898**（head SHA `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`）全部步骤成功，产生了真实的 6,678 条 episode 数据。
2. **测试真实通过。** 该 run 的回归测试步骤实际执行 **28 项测试全部 OK**，其中 Pilot A-3 测试 16 项（15 项预注册 + 1 项崩溃回归，见 §2）。
3. **实验结果可信。** 结构、配对、split 因子化、语义一致性全部通过审计；JSON 与 CSV 逐项一致（0 处偏差）；本地重跑与 CI 产物确定性一致（CSV 逐字节相同）。
4. **预注册 Gate 未通过。** 三条 GO 条件中只有安全条件满足；oracle−saga 成功率差 = **0.0**（要求 ≥ 0.05）；cluster paired bootstrap 95% CI = **[0.0, 0.0]**（要求下界 > 0）。零违规 + gap ≤ 0.02 但动作成本差 34.6% > 10%，按 47 号协议原文落入"其他情况"分支 → **HOLD**，先定位失败边界（§7 已定位）。
5. **Pilot B 继续 HOLD**；A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 优化全部维持 HOLD。

---

## 1. 运行身份（Phase A-1 / A2）

### 1.1 仓库状态（2026-11-06 核验）

| 项目 | 值 |
|---|---|
| 工作分支 | `pilot-a-stateful-recovery` |
| 被审计 CI 的 head SHA | `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`（"Fix A-3 simulator crash: policies must not read hidden runtime tick"） |
| main HEAD | `683b3fe7fc52c86e917d523fdc6bbb13abbfd653` |
| 分支相对 main | ahead 82 / behind 0 |
| 工作区 | 干净（本次审计产物随后提交） |

### 1.2 A-3 CI 历史（全部为 push 触发，workflow `Pilot A recovery simulator`）

| Run ID | Head SHA | 结论 | 说明 |
|---|---|---|---|
| 42037327488 | `2abd83ad` 起 4 个 run | success | A-3 首版实现/测试加入期，**未运行 A-3 simulator**（当时 workflow 尚无该步骤） |
| 42037561884 | `76f62c09` | **failure** | 首个含 "Run Pilot A-3 simulator" 步骤的 run；simulator 崩溃 |
| 42037934832 … 42038656132 | `7be807aa` … `e3b4d113` | **failure**（6 个） | 全部在同一位置崩溃；artifact 上传步骤均 skipped |
| **42241224898** | **`f5e6b46`** | **success** | 修复后的首个完整运行；本报告的审计对象 |

此前文档中引用的旧 run 42030194929 / 42030392313 只覆盖 A1/A2，**不构成 A-3 证据**。

### 1.3 被审计 run 的步骤级核验（run 42241224898, job 127971717249）

| # | 步骤 | 结论 | 核验内容 |
|---|---|---|---|
| 4 | Run regression tests | success | 日志显示 `Ran 28 tests in 0.022s / OK`；逐条列出 27 项旧测试 + `test_recover_tool_never_touches_hidden_runtime_fields` |
| 5 | Run Pilot A baseline | success | A1 模拟器输出正常 |
| 6 | Run Pilot A-2 simulator | success | A2 模拟器输出正常 |
| 7 | Run Pilot A-3 simulator | success | A3 模拟器完整运行，生成 JSON/CSV |
| 8 | Upload Pilot A-3 episode-level results | success | artifact `pilot-a3-results` 已上传 |
| 9 | Upload Pilot A-2 summary | success | artifact `pilot-a2-summary` 已上传 |

15 项预注册 A-3 测试 + 1 项崩溃回归测试全部在 CI 中实际执行并通过；A-3 simulator 步骤真实运行。

## 2. CI 失败根因与修复（Phase A 的必要组成）

**症状：** 自 `76f62c09` 起 7 个连续 run 在 "Run Pilot A-3 simulator" 失败，没有任何 A-3 结果文件曾经存在。

**根因（日志原文）：**
```
File ".../pilot_a3.py", line 350, in recover_tool
    for _ in range(max(0, tool.retry_after - tool.tick)):
AttributeError: 'PublicToolView' object has no attribute 'tick'
```
`recover_tool`（可部署策略代码）通过受限门面 `PublicToolView` 读取了 `ToolRuntime` 才有的时钟字段 `tick`。`PublicToolView` 按设计只暴露 `contract`、`retry_after` 和动作方法；故障标签、真实可见时刻、补偿可用性不得泄漏给可部署策略。崩溃发生在 rate-limit 恢复分支，而 15 项测试没有覆盖"策略 × RATE_LIMIT × 公开门面"这条路径，所以测试全绿、模拟器却必崩。

**修复（commit `f5e6b46`）：**
- 可部署策略改为用公开 `retry_after` 提示自行计数等待（策略本来就应该只依赖自己的动作历史）；`PublicToolView` **未扩大**任何可见字段，观察边界与既有测试完全一致。
- `oracle_recover` 保持特权访问 `tick`/`visible_at`（它直接接收原始 `ToolRuntime`，属于协议允许的诊断参考）。
- 新增第 16 项测试 `test_recover_tool_never_touches_hidden_runtime_fields`：对 6 种可部署策略 × 7 种公开错误签名逐一驱动 `recover_tool(PublicToolView(...))`，任何对隐藏字段的再次触碰都会立刻失败。

修复后 28 项测试通过、模拟器完整运行，push 后 CI 全绿（即 §1.3 的 run）。

## 3. Artifact 与哈希（Phase A-3）

| 对象 | SHA-256 | 大小 |
|---|---|---|
| artifact ZIP `pilot-a3-results`（id 13517080091） | `1119d14b70eedef221fe6e63439e2a04bd58c0354d5a723344d2c80c459ab727` | 54,341 B |
| `pilot_a3_results.json`（CI 原始） | `3a60ae8385c723c57d54ff47608fe428690d94519f6762ec78bbc15c1d15fe14` | 94,400 B |
| `pilot_a3_episodes.csv`（CI 原始） | `2c7d7dad5faaae58f182f27d77b90dfa237f4c1627e15b0bc029d34582f3c369` | 1,701,434 B（6,678 数据行 + 表头） |

- ZIP 哈希与 GitHub API `digest` 字段一致。
- 完整清单：`experiments/pilot_a_recovery/a3_artifact_manifest.json`。
- 原始文件按下载原样保存于 `experiments/pilot_a_recovery/ci_artifact/`，不得被修正版覆盖。
- **确定性验证：** 本地用同一提交重跑 `pilot_a3.py`，CSV 与 CI 产物逐字节一致；JSON 内容一致（仅 Windows CRLF / Linux LF 换行差异）。模拟器完全确定，可跨平台复现。

CSV 列（23 列）：scenario_id, split, task_family, fault_composition, seed, policy, task_success, safe_resolution, safe, invariant_violation, duplicate_side_effect, unresolved, escalated, compensation_failure, compensation_failures, active_effects, steps_committed, steps_attempted, action_count, rollback_order, tool_action_counts, tool_vector, fault_vector。

## 4. 结构与配对审计

复算脚本：`experiments/pilot_a_recovery/recompute_a3_audit.py`（独立实现，不 import `pilot_a3`）。输出：`experiments/pilot_a_recovery/a3_recompute_report.json`。

| 检查项 | 预算要求 | 实测 | 结论 |
|---|---|---|---|
| 总行数 | 6,678 | 6,678 | 通过 |
| 每策略行数 | 954 | 7 × 954 | 通过 |
| 每策略 train | 144 | 144 | 通过 |
| 每策略 validation | 120 | 120 | 通过 |
| 每策略 held-out | 690 | 690 | 通过 |
| 唯一 (scenario_id, policy) | 6,678 | 6,678（0 重复） | 通过 |
| 唯一 scenario ID | 954 | 954 | 通过 |
| 七策略共享 scenario ID | 全部 | 全部 | 通过 |
| 同 scenario 的 seed/fault vector/tool vector 跨策略一致 | 完全配对 | 完全配对（common random numbers 成立） | 通过 |
| split 因子化（47 号 §3 因子表） | 45 个 task×composition 组合 | 45 个，0 偏差；train/val 每组合 12 次重复，held-out 每组合 30 次 | 通过 |
| held-out 泄漏 | 无 | held-out 任务族/组合族不出现在 train/validation，反之亦然 | 通过 |

per-tool fault vector 存在于每行 `fault_vector` 列（`fault:comp=0/1` 逐步标注），与"故障独立按工具生成"的协议一致。

## 5. 信息边界审计

| 检查项 | 证据 | 结论 |
|---|---|---|
| 可部署策略不接触隐藏状态 | `test_policy_view_hides_latent_simulator_labels`：`fault`/`compensation_available`/`visible_at` 对策略不可见 | 通过 |
| 策略代码不绕过门面 | 新增 `test_recover_tool_never_touches_hidden_runtime_fields` 覆盖 6 策略 × 7 公开错误 | 通过（修复后） |
| oracle 特权隔离 | `oracle_recover` 单独接收 `ToolRuntime`；策略入口只有 `PublicToolView` | 通过 |
| CSV 隐藏列的性质 | `fault_vector` 等列为评估侧审计记录，对所有策略对称记录，不进入策略输入 | 通过（记录用途，非泄漏） |
| 逆序补偿语义 | rollback 仅出现在 saga_aware/oracle_diagnostic（各 364 行）；顺序均为 tool_vector 的逆前缀，如 `order>inventory` | 通过 |
| 补偿失败语义 | `compensation_failure` 与 `compensation_failures>0` 逐行一致；失败记为 `*:FAILED`，不冒充成功 | 通过 |
| unresolved / safe / violation 语义 | `unresolved == (非成功 且 active_effects>0)` 逐行成立；`safe + invariant_violation == 1`；duplicate ⇒ violation | 通过 |

## 6. 独立指标重算（Phase A-4）

以下全部由 `recompute_a3_audit.py` 从 CSV 独立聚合，与 `pilot_a3_results.json` 汇总**逐项一致（0 处偏差）**。

### 6.1 Held-out 合并集（690 episodes / 策略）

| 策略 | task success | safe resolution | invariant viol. | duplicate | unresolved | escalated | comp fail | mean actions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blind_retry | 0.0478 | 0.2072 | 0.4029 | 0.4029 | 0.7928 | 0.9522 | 0.0000 | 3.64 |
| verify_then_retry | 0.0551 | 0.2145 | 0.3275 | 0.3275 | 0.7855 | 0.9449 | 0.2275 | 5.34 |
| fixed_wait_verify | 0.1812 | 0.3217 | 0.1957 | 0.1957 | 0.6783 | 0.8188 | 0.2290 | 8.94 |
| conservative_escalation | 0.0159 | 0.0768 | 0.0000 | 0.0000 | 0.9232 | 0.9841 | 0.0000 | 2.64 |
| contract_aware | 0.4783 | 0.5014 | 0.0000 | 0.0000 | 0.4986 | 0.5217 | 0.2290 | 9.76 |
| **saga_aware** | **0.4783** | **0.6101** | **0.0000** | **0.0000** | **0.3899** | **0.5217** | **0.2855** | **10.17** |
| oracle_diagnostic | 0.4783 | 0.6101 | 0.0000 | 0.0000 | 0.3899 | 0.5217 | 0.2855 | 7.56 |

### 6.2 saga_aware 与 oracle_diagnostic 的 held-out 分层

| Slice | n | saga success | oracle success | saga inv. viol. | saga mean actions | oracle mean actions |
|---|---:|---:|---:|---:|---:|---:|
| heldout_task_shift | 240 | 0.9750 | 0.9750 | 0.0000 | 11.41 | 7.40 |
| heldout_fault_shift | 270 | 0.2148 | 0.2148 | 0.0000 | 9.51 | 7.77 |
| heldout_joint_shift | 180 | 0.2111 | 0.2111 | 0.0000 | 9.51 | 7.44 |
| heldout_all | 690 | 0.4783 | 0.4783 | 0.0000 | 10.17 | 7.56 |

train/validation 成功率（同为三策略持平）：train 0.9653，validation 0.8167。其他策略全 split 明细见 `a3_recompute_report.json`。

### 6.3 Cluster paired bootstrap（task-family × fault-composition）

- 单位：23 个 cluster（held-out 的 task×composition 组合），每 cluster 30 个配对 scenario；
- 指标：task_success，oracle_diagnostic − saga_aware，按 scenario 配对；
- 2,000 次 cluster 重采样（seed 20261105）：**mean difference = 0.0，95% CI = [0.0, 0.0]**；
- 23 个 cluster 的配对差**全部为 0**（两个策略在每个 scenario 上同成同败）；
- 敏感性（seed 42）：同样 [0.0, 0.0]。结论不依赖随机种子。

## 7. 预注册 Gate 判定（Phase A-5，47 号 §6 原文执行）

**CONDITIONAL GO to Pilot B 必须同时满足：**

| # | 条件 | 实测 | 判定 |
|---|---|---|---|
| 1 | saga_aware 在每个 held-out slice 的 invariant violation rate = 0 | task-shift 0.0、fault-shift 0.0、joint-shift 0.0 | **满足** |
| 2 | held-out 合并集 oracle − saga task-success 差 ≥ 0.05 | **0.0** | **不满足** |
| 3 | task×composition cluster paired bootstrap 95% CI 下界 > 0 | **0.0**（CI [0.0, 0.0]） | **不满足** |

**分支判定（按协议原文顺序）：**
- 任一 slice 有安全违规 → HOLD_SAFETY：**不适用**（三 slice 全部零违规）；
- 全部 slice 零违规，但 gap ≤ 0.02 **且** 动作成本差 ≤ 10% → NO-GO（无优化空间）：gap = 0.0 ≤ 0.02 成立，但动作成本差 = (10.171 − 7.555)/7.555 = **+34.63% > 10%**，**不满足**；
- 其他情况 → **HOLD，先定位失败边界**。

### **判定：HOLD（HOLD_REVIEW_FAILURE_BOUNDARIES）。不得进入 Pilot B。**

本判定严格使用预注册阈值，未做任何事后调整；held-out 结果不用于修改策略后再宣称通过。

## 8. 失败边界定位（HOLD 要求的分析）

### 8.1 为什么 oracle − saga 成功率差是 0

23 个 cluster 的配对差全部为 0，即 oracle 与 saga 在**每一个** scenario 上同成同败。逐组检查显示（saga_aware worst-group，oracle 逐组相同）：

| 故障组合族 | 出现范围 | saga/oracle success | 解释 |
|---|---|---:|---|
| partial_comp_failure | 全部 6 个任务族（30×6=180 held-out episodes） | **0.000** | 部分提交落在可补偿工具上但补偿运行时失败（comp_fail=1.000），残留副作用无法清除（unresolved=1.000）→ **结构性不可行**，特权诊断也无法完成任务 |
| delay_rate_permission | 全部 6 个任务族（30×6=180） | **0.000** | 逐步注入延迟+限流+权限拒绝；permission_denied 步骤不可提交，含补偿失败残留（unresolved 0.23–1.00）→ **结构性不可行占主导** |
| triple_mixed | 6 个任务族 | 0.533–0.733 | 部分可行，存在真实恢复难度 |
| partial_then_delay / schema_then_timeout / single_timeout / timeout_then_rate_limit | held-out 任务族 | 0.867–1.000 | 强手工策略与 oracle 都能处理 |

held-out 中 360/690（52.2%）落在全员 0% 的两个组合族。**oracle 的特权信息在这些单元里改变不了可行性**，只在可行单元上节省动作（每 episode 约 2.6 次动作）。这就是 gap = 0 且 CI = [0,0] 的直接原因：GO 条件 2/3 要求"存在 oracle 明显强于强手工策略的优化空间"，而本模拟器里**成功率维度的剩余空间被结构性不可行场景吃掉，剩余空间只在动作成本维度**（+34.6%）。

### 8.2 三个明确的失败边界

1. **可行性边界**：partial_comp_failure、delay_rate_permission 两个预注册组合族对任何策略（含诊断 oracle）都是 0% 成功。这不是策略缺陷，而是故障注入设计决定的死区。
2. **泛化边界**：任务族漂移（unseen tasks × seen compositions）上 saga 达 97.5%，说明策略规则本身跨任务族泛化良好；塌陷完全来自未见故障组合。
3. **效率边界**：saga 相对 oracle 多 34.6% 动作（盲目等待 visibility SLA 上限、逐步 verify），是本任务族里唯一明确的可优化维度。

### 8.3 HOLD 的含义

- A-3 gate **没有通过**，Pilot B（随机搜索 / GA / GP / 契约约束 EA）**不启动**。
- 不允许在查看这批 held-out 后修改组合族或策略，再用同一批数据宣称通过。
- 若继续本方向，需要**新的预注册**（例如 A-3b：可行性分层的成功率定义、或补充可行 held-out 组合族），并保留本报告作为 A-3 的完整负/中性结果记录。
- 结果定位：探索性确定性模拟器信号，不是真实 LLM Agent 结论，不是 EC 增益证据，不是统计显著的算法改进。

## 9. 交付物清单

| 交付物 | 位置 |
|---|---|
| 本独立复核报告 | `PILOT_A3_INDEPENDENT_REAUDIT.md` |
| 独立复算脚本 | `experiments/pilot_a_recovery/recompute_a3_audit.py` |
| 独立重算表 / 完整复算输出 | `experiments/pilot_a_recovery/a3_recompute_report.json` |
| 原始 artifact manifest（哈希、行数、列名、确定性证明） | `experiments/pilot_a_recovery/a3_artifact_manifest.json` |
| CI 原始 JSON / CSV（原样保存，不覆盖） | `experiments/pilot_a_recovery/ci_artifact/` |
| CI 失败根因与修复记录 | `experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md`、commit `f5e6b46` |

## 10. 授权边界（自本报告起生效）

- **GO：** 文档维护；ToolMisuseBench / UndoBench 只读数据集审计（版本固定、manifest、license、split 泄漏、evaluator 分母）；A-3b 新预注册协议的**设计**。
- **HOLD：** Pilot B 演化搜索；用本批 held-out 调参；A800/ARWM 训练；真实 LLM API；UndoBench frozen TEST；ThinkingBox 任何优化用途。
- 每轮结束更新 `NEXT_SESSION_PROMPT.md`、`SESSION_HANDOFF.md`、`README.md`、`05_DECISION_LOG.md` 与 51 号计划状态。
