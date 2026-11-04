# D-039 — TCAIL V2.2 独立复审 R1

日期：2026-11-04  
基线：11cccf45c7533782f2673612b4bd52930541c9bc  
完整报告：36_TCAIL_V2_2_INDEPENDENT_REVIEW_R1.md

**决定：REQUEST CHANGES / HOLD / IMPLEMENTATION BLOCKED。**

关键问题：
1. M2/M3 conservative local-null envelope 与 posterior expected loss 语义不一致。
2. Acquisition 非正停止只检查点估计，没有使用 MCSE。
3. 同一 base key 的 retry 配额可能跨轮重置。
4. practical-information rank 门忽略 target-space 零特征值，且 Fisher 的 marginal GLMM 口径未冻结。
5. rho_AB 实际是 selected-positive-edge density，不是 support coverage。
6. 双模型 fantasy 的 sample-wise max-risk/max-cost 需要明确概率 coupling。
7. 活动图集合和权重随 parent/generation 更新的时间尺度未定义。

B1/B4/B5/B7/B9/B12 保持 PARTIAL；B2/B3/B6/B8/B10/B11 需要修订。33/34 保留为 R0，不覆盖。

不授权实现、Phase 0、真实 LLM API、模型训练、CI-GOM 或 IMCE-RSI。下一步只进行 V2.2 corrective specification revision R1，并在修订后交不同会话独立复审。
