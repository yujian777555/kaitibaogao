# 47 — Pilot A-3：独立故障组合与跨任务泛化协议

**状态：PRE-REGISTERED PILOT PROTOCOL / NOT RUN**  
**日期：2026-11-05**  
**工作分支：pilot-a-stateful-recovery**

## 1. 目的与边界

Pilot A-2 的 contract-aware 策略成功率为 0.7222，诊断 oracle 为 0.7778；5.56 个百分点的差距只是探索性模拟器信号。A-2 的两个关键限制是：同一任务的两个工具共享同一故障族；没有 held-out task/fault composition。

A-3 只回答一个问题：在每个工具独立故障、跨步骤 saga 依赖、部分提交、延迟可见和补偿失败同时存在时，强手工恢复策略是否仍然接近诊断 oracle？

A-3 **不运行 EA，不调用真实 LLM API，不训练 ARWM，不使用 A800**。A-3 通过后才进入 Pilot B（随机搜索、GA/GP、契约约束 EA 的同预算比较）。

## 2. 模拟器语义

### 2.1 任务与 saga

六个三步任务族：

| Split | Task family | Ordered tools |
|---|---|---|
| Train | inventory_order_payment | inventory → order → payment |
| Train | calendar_order_ledger | calendar → order → ledger |
| Train | customer_order_shipment | customer → order → shipment |
| Validation | inventory_calendar_order | inventory → calendar → order |
| Held-out | return_refund_restock | order → refund → inventory |
| Held-out | subscription_ledger_notification | subscription → ledger → notification |

后一步只有在前一步确认提交后才能执行。任一步不可恢复时，saga 终止；saga-aware 策略按逆序补偿此前已提交的步骤。

### 2.2 工具契约

工具公开给策略的契约字段只有 idempotent、compensatable 和 visibility_bound。补偿在运行时仍可能失败；策略不能预先读取 compensation_available。

| Tool | Idempotent | Compensatable |
|---|---:|---:|
| inventory | no | yes |
| calendar | yes | yes |
| order | no | yes |
| payment | no | yes |
| ledger | no | no |
| customer | yes | yes |
| shipment | no | no |
| refund | no | no |
| subscription | yes | yes |
| notification | no | no |

### 2.3 故障与可观察性

基本故障：none、timeout_before、timeout_after、delayed_visibility、partial_commit、rate_limit、schema_drift、permission_denied。

timeout_before、timeout_after 和 delayed_visibility 对策略暴露同一 TIMEOUT 结果。策略只能通过公开 VERIFY、WAIT 和工具契约恢复；隐藏故障标签、真实提交时刻、补偿可用性只供 oracle diagnostic 与离线审计使用。

每个步骤独立生成故障向量，不再像 A-2 一样把同一故障复制给任务内全部工具。延迟、限流窗口和补偿可用性由 episode seed 确定。

### 2.4 故障组合族

- Train：single_timeout、timeout_then_rate_limit、partial_then_delay、schema_then_timeout。
- Validation：independent_mixed_val、partial_then_timeout_val。
- Held-out：partial_comp_failure、delay_rate_permission、triple_mixed。

Held-out 组合族不参与手工规则调整、阈值选择或参数调节。

## 3. 数据划分与评价预算

采用任务族 × 故障组合族的因子化划分，以分离任务漂移、故障组合漂移和联合漂移：

| Split | 组合 | Repeats |
|---|---|---:|
| Train | 3 train tasks × 4 train compositions | 12 |
| Validation-task-shift | 1 validation task × 4 train compositions | 12 |
| Validation-fault-shift | 3 train tasks × 2 validation compositions | 12 |
| Held-out-task-shift | 2 held-out tasks × 4 train compositions | 30 |
| Held-out-fault-shift | 3 train tasks × 3 held-out compositions | 30 |
| Held-out-joint-shift | 2 held-out tasks × 3 held-out compositions | 30 |

总计每种策略 954 episodes：train 144、validation 120、held-out 690。七种策略共 6,678 policy episodes。所有策略使用完全相同的 scenario ID、seed 和 fault realization（common random numbers）；episode 数预算相同，动作成本另行报告。

## 4. 对照策略

1. blind_retry
2. verify_then_retry
3. fixed_wait_verify
4. conservative_escalation
5. contract_aware（单工具契约感知恢复，不执行跨步骤补偿）
6. saga_aware（契约感知恢复 + 逆序补偿）
7. oracle_diagnostic（可见当前步骤潜在执行状态，仅作诊断参考，不是可部署基线，也不保证全局最优）

A-3 只比较预先定义的手工策略与 oracle；不在 held-out 上选择策略，也不把 oracle 作为可实现算法。

## 5. 硬不变量与指标

硬不变量：
- 不允许在前置步骤未确认提交时执行后续步骤；
- 非幂等工具不得在提交状态不明时盲目重试；
- 不得将补偿失败报告为补偿成功；
- 不得在未完成全部步骤时报告任务成功。

报告指标：
- task success；
- safe resolution（成功完成，或所有副作用均已撤销/无副作用）；
- invariant violation / duplicate side effect；
- unresolved residual effects；
- compensation failure / escalation；
- actions per episode；
- held-out task-only、fault-only、joint-shift 的分层结果及 worst-group success。

所有原始 episode、fault vector、per-policy/per-split 汇总和配置均保留。

## 6. 预注册门禁

A-3 只决定是否进入 Pilot B，不证明演化算法有效。

**CONDITIONAL GO to Pilot B** 必须同时满足：
1. saga_aware 在每一个 held-out slice（task-only、fault-only、joint-shift）上的 invariant violation rate 均为 0；
2. held-out 合并集上 oracle_diagnostic − saga_aware 的 task-success 差至少 0.05；
3. 以 task-family × fault-composition 为 cluster 的 paired bootstrap 95% CI 下界大于 0。

若任一 held-out slice 出现 saga_aware invariant violation，则 HOLD，先修复安全问题，不得进入 Pilot B。若全部 slice 零违规，但 saga_aware 与 oracle 的 success gap ≤ 0.02 且动作成本差不超过 10%，则对该模拟器任务族 NO-GO（没有足够优化空间）。其他情况为 HOLD，先定位失败边界，不得通过查看 held-out 后调参再宣称通过。

即使 Pilot A-3 通过，也只允许进入 Pilot B 的算法比较：random search、standard GA/GP、contract-aware EA；必须在相同真实 simulator rollout budget 下比较，held-out 只作最终一次评价。

## 7. 运行与复现

运行：
```bash
python -m unittest discover -s experiments/pilot_a_recovery -p "test_*.py" -v
python experiments/pilot_a_recovery/pilot_a3.py
```

输出：
- `pilot_a3_results.json`
- `pilot_a3_episodes.csv`

CI 必须运行 A1、A2、A3 回归测试和三个 simulator，并上传 A2/A3 结果 artifact。所有结果必须标为 exploratory，除非后续独立确认性协议另行预注册。

## 8. 停止条件

- 如果 saga_aware 在 held-out 上已接近 oracle，且动作成本接近，停止本方向的 EA 研究；
- 如果零安全违规无法维持，先修复策略/模拟器语义，不运行 EA；
- 如果 oracle 也无法显著优于简单安全策略，停止该任务族；
- 不因 A-2 的 5.56pp gap 或 A-3 的单次模拟器结果宣称创新成立；
- A800/ARWM 保持 HOLD，直到 Pilot B 证明 EC 增益，并另行通过 ARWM 的预测质量与固定真实 rollout 预算收益门禁。
