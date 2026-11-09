# D-064-B — CondRecSucc 层级功效与 ICC 敏感性报告

- 输入 SHA-256：`b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`；程序 power_hierarchical.py v1 (D-064-B)；git `8526ab71d2580588bf62a8bd36a08b953388a70e`
- MC：key cells 10000 次、sweep 2000 次；seed 20261112；α=0.05 双侧

## 1. 层级数据复核（Task A）
- 6 families × 7 eligible compositions = **42 clusters**；零分母 12；问题：无
- 总均值 Δ=0.31746，总 SD=0.318856；family 均值：{'inventory_order_payment': 0.365079, 'calendar_order_ledger': 0.357143, 'customer_order_shipment': 0.238095, 'inventory_calendar_order': 0.301587, 'return_refund_restock': 0.380952, 'subscription_ledger_notification': 0.261905}
- within var=0.112385；between var(MoM)=-0.012553

## 2. ICC（Task B）
- ANOVA/MoM：**ICC=-0.1257**（约束 0.0000）
- REML：ICC=-0.1257（平衡设计下应与 MoM 一致）
- family-block bootstrap CI：[np.float64(-0.1589), np.float64(-0.1108)]（6 families，不稳定——**不解释为独立性证明**）

## 3. 层级推断（Task E：D-064-A 重评估）
- family-level t：t=13.1401 df=5 p=**4.6e-05**
- family-level exact sign-flip（2^6 枚举）：p=**0.03125**
- family-block bootstrap CI：[np.float64(0.272487), np.float64(0.357143)]
- 对照 D-064-A 42-cluster 独立分析结果（CI/p 见 66 号报告与 condrec_diagnostic3.json）

## 4. Type-I 校准与关键功效（Task C）
| ICC | MDE | n_fam | t 功效 (MCSE) | sign-flip | bootstrap |
|---|---|---|---|---|---|
| 0.0 | 0.0 | 6 | 0.0531 (0.0022) | 0.0306 | 0.1481 |
| 0.0 | 0.0 | 17 | 0.0533 (0.0022) | 0.0515 | 0.0812 |
| 0.0 | 0.1 | 6 | 0.384 (0.0049) | 0.2592 | 0.6314 |
| 0.0 | 0.1 | 17 | 0.8976 (0.003) | 0.8941 | 0.9306 |
| 0.05 | 0.0 | 6 | 0.0522 (0.0022) | 0.0324 | 0.1419 |
| 0.05 | 0.0 | 17 | 0.0508 (0.0022) | 0.0501 | 0.0796 |
| 0.05 | 0.1 | 6 | 0.3056 (0.0046) | 0.2035 | 0.5476 |
| 0.05 | 0.1 | 17 | 0.8116 (0.0039) | 0.8043 | 0.8641 |
| 0.1 | 0.0 | 6 | 0.0527 (0.0022) | 0.0305 | 0.1458 |
| 0.1 | 0.0 | 17 | 0.0517 (0.0022) | 0.0489 | 0.0806 |
| 0.1 | 0.1 | 6 | 0.2609 (0.0044) | 0.1684 | 0.4914 |
| 0.1 | 0.1 | 17 | 0.7271 (0.0045) | 0.7209 | 0.7939 |
| 0.2 | 0.0 | 6 | 0.0502 (0.0022) | 0.0323 | 0.1396 |
| 0.2 | 0.0 | 17 | 0.056 (0.0023) | 0.0537 | 0.0845 |
| 0.2 | 0.1 | 6 | 0.1987 (0.004) | 0.1314 | 0.3958 |
| 0.2 | 0.1 | 17 | 0.5976 (0.0049) | 0.5903 | 0.6771 |

## 5. 所需 family 数（m=7，t 检验）

| ICC | MDE | 80% 无损耗 | 80% 双 15% 损耗 | 90% 无损耗 | 90% 双 15% 损耗 |
|---|---|---|---|---|---|
| 0.0 | 0.05 | None | None | None | None |
| 0.0 | 0.08 | 22 | 40 | 30 | None |
| 0.0 | 0.1 | 15 | 22 | 17 | 30 |
| 0.0 | 0.1173 | 12 | 17 | 15 | 22 |
| 0.0 | 0.15 | 8 | 12 | 10 | 15 |
| 0.05 | 0.05 | None | None | None | None |
| 0.05 | 0.08 | 30 | 40 | 40 | None |
| 0.05 | 0.1 | 17 | 30 | 22 | 40 |
| 0.05 | 0.1173 | 15 | 19 | 17 | 25 |
| 0.05 | 0.15 | 10 | 15 | 12 | 17 |
| 0.1 | 0.05 | None | None | None | None |
| 0.1 | 0.08 | 40 | None | None | None |
| 0.1 | 0.1 | 22 | 40 | 30 | 40 |
| 0.1 | 0.1173 | 17 | 25 | 19 | 30 |
| 0.1 | 0.15 | 10 | 15 | 15 | 19 |
| 0.2 | 0.05 | None | None | None | None |
| 0.2 | 0.08 | None | None | None | None |
| 0.2 | 0.1 | 30 | 40 | 40 | None |
| 0.2 | 0.1173 | 22 | 30 | 30 | 40 |
| 0.2 | 0.15 | 15 | 19 | 19 | 25 |

## 6. 17-family 评估与结论见 power_hierarchical.json 与 68 号报告。

备注：0.1173 = historical observed effect (sensitivity only); +<diagnostic observed effect> = NOT an MDE (see 66 report); MDE needs independent scientific justification
