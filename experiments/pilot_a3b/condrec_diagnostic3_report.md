# CondRecSucc 主要终点独立分析（D-064-A）

- 输入 `diagnostic3_results.json` SHA-256 `b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`
- 程序：condrec_analysis.py v1 (D-064-A)；git `3e8ffc40601e7b65321ad7816af4f327df0203bf`
- 命令：`python condrec_analysis.py --input diagnostic3_results.json --outdir .`
- Bootstrap 4000 次（cluster 重采样，seed 20261110）；Sign-flip 8000 次（真实 cluster 级符号翻转 MC，seed 20261111）
- 层级：hierarchical paired: (scenario,seed) pairing -> seed-mean per scenario -> equal-weight cluster (task x composition) means -> cluster bootstrap percentile CI + cluster-level sign-flip MC test
- 零分母规则：clusters with no R1/R2 scenario are EXCLUDED from the primary estimand and registered; never zero-filled

## 主要结果（R1+R2 only）

- primary eligible clusters: **42** / 设计 clusters 54
- zero-denominator (R3/R4-only) clusters: 12 → ['calendar_order_ledger|delay_rate_permission', 'calendar_order_ledger|partial_comp_failure', 'customer_order_shipment|delay_rate_permission', 'customer_order_shipment|partial_comp_failure', 'inventory_calendar_order|delay_rate_permission', 'inventory_calendar_order|partial_comp_failure', 'inventory_order_payment|delay_rate_permission', 'inventory_order_payment|partial_comp_failure', 'return_refund_restock|delay_rate_permission', 'return_refund_restock|partial_comp_failure', 'subscription_ledger_notification|delay_rate_permission', 'subscription_ledger_notification|partial_comp_failure']
- AB CondRecSucc: **0.5582010582010581**；NSGA-II: **0.24074074074074073**
- Δ(AB−NSGA-II): **0.31746**；Cluster SD: 0.318856
- 95% CI: [0.218254, 0.411376]；sign-flip p: **0.000125**
- scenario 加权敏感性 Δ: 0.314465
- 配对完整率: 1.0（缺失 0 个 scenario-seed 对）

## R3 / R4 独立安全统计

### R3 CorrectEscalation
- AB: rate=0.22619 clusters=14 episodes=87 SD=0.373292 CI=[0.047619, 0.428571]
- nsga2: rate=0.678571 clusters=14 episodes=87 SD=0.044544 CI=[0.666667, 0.702381]
### R4 DamageContainment
- AB: rate=0.8 clusters=15 episodes=81 SD=0.414039 CI=[0.6, 1.0]
- nsga2: rate=0.933333 clusters=15 episodes=81 SD=0.186871 CI=[0.822222, 1.0]

## 每 cluster R1/R2 分母与效应

| cluster | n_R1/R2 | Δ |
|---|---|---|
| calendar_order_ledger|independent_mixed_val | 1 | +0.3333 |
| calendar_order_ledger|partial_then_delay | 2 | +0.6667 |
| calendar_order_ledger|partial_then_timeout_val | 3 | +0.6667 |
| calendar_order_ledger|schema_then_timeout | 3 | +0.0000 |
| calendar_order_ledger|single_timeout | 3 | +0.5556 |
| calendar_order_ledger|timeout_then_rate_limit | 3 | +0.1111 |
| calendar_order_ledger|triple_mixed | 2 | +0.1667 |
| customer_order_shipment|independent_mixed_val | 2 | +0.0000 |
| customer_order_shipment|partial_then_delay | 3 | +0.6667 |
| customer_order_shipment|partial_then_timeout_val | 2 | +0.6667 |
| customer_order_shipment|schema_then_timeout | 3 | +0.2222 |
| customer_order_shipment|single_timeout | 3 | +0.4444 |
| customer_order_shipment|timeout_then_rate_limit | 3 | +0.0000 |
| customer_order_shipment|triple_mixed | 1 | -0.3333 |
| inventory_calendar_order|independent_mixed_val | 1 | +0.6667 |
| inventory_calendar_order|partial_then_delay | 3 | +0.6667 |
| inventory_calendar_order|partial_then_timeout_val | 3 | +0.6667 |
| inventory_calendar_order|schema_then_timeout | 3 | +0.0000 |
| inventory_calendar_order|single_timeout | 3 | +0.0000 |
| inventory_calendar_order|timeout_then_rate_limit | 3 | +0.1111 |
| inventory_calendar_order|triple_mixed | 1 | +0.0000 |
| inventory_order_payment|independent_mixed_val | 2 | +0.0000 |
| inventory_order_payment|partial_then_delay | 2 | +0.6667 |
| inventory_order_payment|partial_then_timeout_val | 3 | +0.6667 |
| inventory_order_payment|schema_then_timeout | 3 | +0.0000 |
| inventory_order_payment|single_timeout | 3 | +0.5556 |
| inventory_order_payment|timeout_then_rate_limit | 3 | +0.1111 |
| inventory_order_payment|triple_mixed | 3 | +0.5556 |
| return_refund_restock|independent_mixed_val | 3 | +0.6667 |
| return_refund_restock|partial_then_delay | 2 | +0.6667 |
| return_refund_restock|partial_then_timeout_val | 2 | +0.6667 |
| return_refund_restock|schema_then_timeout | 3 | +0.0000 |
| return_refund_restock|single_timeout | 3 | +0.2222 |
| return_refund_restock|timeout_then_rate_limit | 3 | +0.0000 |
| return_refund_restock|triple_mixed | 3 | +0.4444 |
| subscription_ledger_notification|independent_mixed_val | 1 | +0.3333 |
| subscription_ledger_notification|partial_then_delay | 3 | +0.6667 |
| subscription_ledger_notification|partial_then_timeout_val | 2 | +0.6667 |
| subscription_ledger_notification|schema_then_timeout | 3 | +0.0000 |
| subscription_ledger_notification|single_timeout | 3 | -0.3333 |
| subscription_ledger_notification|timeout_then_rate_limit | 3 | +0.0000 |
| subscription_ledger_notification|triple_mixed | 2 | +0.5000 |
