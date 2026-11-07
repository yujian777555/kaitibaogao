# 59 — D-061 失败轨迹独立复核

**日期：** 2026-11-07（D-062 Stage 0）  
**对象：** `experiments/pilot_a3b/diagnostic2_results.json`（D-061 原始数据，只读）  
**原始数据哈希：** SHA-256 `dc45535532dd91c3ef573145f007e5114bf7872b5e4d438e2189d2b4d28884c7`（2,735,653 字节；payload manifest `d4fb2be680e74f2e8351ae2648b00a20c1a3fe2d8d4579dac68f180f321ba25d`）  
**复算方式：** 从 rows 逐行独立聚合 + 从保存的基因组规则重建 FSM 重放轨迹（`run_episode_fsm` 逐 episode 提取 decision_trace）。脚本为一次性审计代码，逻辑记录于本报告 §2。

---

## 1. 0.36 违规率的真实性（逐项核实）

| 问题 | 答案 |
|---|---|
| 分母 | episode 级；486 = 3 seeds × 162 场景（train 108 + validation 54）；每方法同分母 |
| 违规定义 | `invariant_violation = (downstream_violation + Σ tool.violation_count > 0)`，episode 级二值，同一 episode 只计一次 |
| 重复副作用是什么 | `tool.violation_count` 只在**非幂等重试已提交调用**时增加（DUPLICATE） |
| 是否重复计算 | 否；486 个独立 episode 计数 |
| Hand 0.006 同分母？ | 是（3/486 = 0.0062），同一评价器、同一行结构 |
| A 的失败是否集中在少数任务族？ | 否——见 §3，分布在所有含多步补偿的任务族 |

**独立复算结果（episode 级率）：**

| 方法 | viol_rate | **dup_rate** | class_succ |
|---|---:|---:|---:|
| hand | 0.0062 | **0.0000** | 0.8272 |
| A | 0.3601 | **0.0000** | 0.4259 |
| AB | 0.4136 | **0.0000** | 0.3128 |
| B | 0.2819 | 0.0062 | 0.2695 |
| nsga2 | 0.4383 | 0.0000 | 0.1872 |
| ga | 0.3971 | 0.0041 | 0.2737 |
| nsga3 | 0.3272 | 0.0000 | 0.1996 |
| random | 0.1193 | 0.0041 | 0.3333 |

## 2. 关键发现：0.36 不是重复副作用

**A 的 dup_rate = 0.0000。** 全部违规来自 `downstream_violation`。轨迹重放定位：

- 全部 24 个 run 重放共 **1,139 个违规 episode：1,132（99.4%）dup=0（纯 downstream），仅 7（0.6%）为真实重复**。
- A 的 175 个违规 episode **100% 是 `|DOWNSTREAM`**；hand 的 3 个（0.0062）同样是此类。

**根因：D-061 运行器的 saga 门禁误伤正确安全回滚。** 机制：控制器在第 i 步故障后执行 `COMPENSATE → ROLLBACK`（清空前序已提交步骤，即安全放弃序列），while 循环下一轮顶部的门禁检查"下游步骤无前序提交"→ 记违规 → 中止。控制器本应接着 ESCALATE 的正确行为被提前截断并计罚。典型轨迹：

```
t2train|inventory_order_payment|single_timeout|1 (R1)
TIMEOUT/COMPENSATE -> COMPENSATED/ROLLBACK     [comp_log: step1 COMPENSATED, step0 COMPENSATED, resid=0]
→ 循环顶部 saga 门禁 → downstream_violation（评价器 artifact）
```

**结论：D-061 报告的"行为违规率 0.36 vs hand 0.006"叙事不成立**——它度量的是"使用回滚的频率差异"，不是行为安全。真实行为安全（重复副作用）上 hand/A/AB 均为 0。

## 3. 真实重复副作用轨迹（7 例，全部重放提取）

| run | 场景 | 模式 |
|---|---|---|
| random/s101 | timeout_then_rate_limit（step2 timeout_after） | `TIMEOUT/COMPENSATE → COMP_FAILED/VERIFY → NOT_COMMITTED/RETRY → DUPLICATE → …`（重复 11 次） |
| random/s101 | delay_rate_permission（step2 delayed_visibility） | 同上（11 次） |
| ga/s101 | 同上两场景 | 同模式，停止于 STOP_SAFE（1 次） |
| B/s101 | single_timeout×3（timeout_after/delayed_visibility） | `TIMEOUT/COMPENSATE → COMP_FAILED/RETRY → DUPLICATE/VERIFY → NOT_COMMITTED/REPAIR → DUPLICATE → …`（12 次） |

**轨迹语义解析（区分隐藏情形）：**

1. `timeout_after`/`delayed_visibility` = **已提交但 ACK 丢失/结果延迟可见**（不是未提交）；
2. `timeout_before` = **根本未提交**（重试安全）；
3. 上述失败链的错误点：VERIFY 在可见性 SLA 内**会说谎**（返回 NOT_COMMITTED）→ 策略据"未提交"判定重试安全 → 非幂等工具重复提交 → DUPLICATE；
4. 部分案例先尝试 COMPENSATE 失败（补偿不可用/合同不允许）后仍重试——同样未满足"重试安全"前提；
5. **不存在可靠的幂等键**（A-3 工具合同 idempotent=false）；查询工具的一致性 = 可见性 SLA 内不一致。

**因此真正的状态转移错误是：`UNKNOWN_OUTCOME --(信任 SLA 内的 NOT_COMMITTED 查询)--> RETRY_NON_IDEMPOTENT`。** 并非所有 TIMEOUT 都必须 WAIT——`timeout_before` 情形重试是安全的；需要的是"SLA 内禁止以查询结果解锁重试"。

## 4. 对 D-062 算法设计的影响

1. **先修评价器**（已完成）：saga 门禁只对**执行类动作**（RETRY/REPAIR/首次 CALL）生效；COMPENSATE/ROLLBACK/VERIFY/WAIT/ESCALATE 永远合法——安全放弃不再计罚。
2. **WAIT-SLA 契约语义**（已实现）：非幂等工具在 UNKNOWN_OUTCOME 下，RETRY 仅在 (a) 补偿已清除歧义 或 (b) 已等满可见性 SLA **且** SLA 后查询确认未提交 时解锁；SLA 内的 NOT_COMMITTED 查询不得解锁重试。
3. **B 的反例签名**必须是动作序列模式（如 `UNKNOWN→VERIFY_lie→RETRY→DUPLICATE`），不是粗标签——否则定向变异打错基因（D-061 教训）。
4. **度量分离**：`sla_violation`（行为层）、`duplicate`（实际损害）、`downstream_violation`（执行门禁）三者分列，不再混入一个 invariant_violation 叙事。
