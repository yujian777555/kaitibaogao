# 42 — TCAIL 最短证据路径：Estimator-to-GOM Confirmatory Gate R1

**日期：** 2026-11-04  
**状态：** PROTOCOL / NOT YET RUN  
**唯一目标：** 尽快检验 TCAIL 局部交互后验是否比强 linkage 基线更可靠，并且这种改进是否转化为同预算下的 GOM 搜索收益。

## 0. 本文件覆盖的旧下一步

本文件优先于 39 号“先继续修订完整 acquisition/retry 规格”的建议。当前不做完整 acquisition、retry、真实 API、A800 训练或 CI-GOM。只做固定 full-factorial、可重复、可证伪的合成研究原型。该范围不等于批准生产实现或 Phase 0。

研究问题只有一个：

> 在相同 task-block 四格观测和相同 episode-equivalent 总预算下，TCAIL 的 parent-conditioned posterior interaction / FOS 是否优于强 linkage 基线，并提高下游 GOM 的期望任务成功率？

必须分别报告：
- **Estimator Gate：** 交互边与局部 FOS 恢复是否改善；
- **Downstream Gate：** 学到的 FOS 是否改善 GOM 搜索；
- **Oracle ceiling：** 真值 FOS 是否有价值，仅作为必要上界，不作为 TCAIL 成功证据。

## 1. 先审计现有 pilot，不要把 pilot 数字当确认性结论

现有文件：
- \`experiments/tcail_oracle_gate_pilot/RESULTS.md\`
- \`experiments/tcail_estimator_gate_pilot/RESULTS.md\`
- \`experiments/tcail_estimator_gate_pilot/FBL_COMPARISON_RESULTS.md\`

现有结果只能标为 EXPLORATORY：
- Oracle FOS 在 40-bit concatenated deceptive trap 简化 GOM 上 13/20 成功；说明该特定问题中正确 linkage 有上界价值。
- EB q AUPRC 0.802、EB w 0.797；但使用 Normal-Normal empirical-Bayes proxy，不是 TCAIL M2/M3 Bernoulli GLMM。
- scaled-FBL 0.414 是 task-block binary adaptation，不是原论文复现。
- 8-block low-support AUPRC 0.353，是明确失败边界。
- 所有结果均需 clean rerun；不能写成 TCAIL 已被证明。

### 1.1 现有代码必须先修的审计项
1. \`run_fbl_comparison.py\` 中 FBL adaptation 的四格 cell 顺序、条件主效应和 scaled dependency 公式必须逐项与原论文定义对照；报告必须给出逐式映射，不得只称“paper-faithful”。
2. FBL epsilon gate 使用 \`abs(mean_d)\`，即与 local four-cell interaction contrast 同源；必须说明这是否等价于原 FBL 的 four-point tolerance，若不等价则明确称 adaptation，并加一个不使用该 gate 的 sensitivity。
3. 目前每个 seed 的 pair class 数固定，test seeds 主要改变随机实现而非任务分布。新增独立 generator seeds / distribution shifts，避免只在同一固定 class mixture 上验证。
4. 当前 shared block shift 是 probability-scale additive perturbation，不是 logistic random-intercept GLMM。确认性主生成器必须改为 logistic task/block random effects，并在不同 random-slope / overdispersion 条件下压力测试。
5. 当前 \`se=sd(d_b)/sqrt(n_blocks)\` 与 Normal likelihood 是 proxy；确认性主模型必须使用明确的 Bernoulli task-block likelihood，或将其标为近似并用模拟校准覆盖率。
6. 重新计算全部指标，保留原始 per-pair/per-context/per-block 四格 outcomes、seed 级结果、配置、版本和哈希；不能仅复用报告中的汇总数。
7. Oracle GOM 结果必须 clean rerun；检查 initial population evaluations 是否统一计入预算、相同 seed 初始种群是否一致、停止规则是否对各方法一致。

## 2. Confirmatory synthetic generator

### 2.1 变量和目标
- 40 个 binary decision variables，10 个预先定义的局部模块；每个 pair/context 是一个局部四格设计。
- Agent outcome 为 Bernoulli success。对 task \(t\)、block \(b\)、配置 \(x\)，生成：
\[
Y_{t,b,x}\sim\operatorname{Bernoulli}(p_{t,b,x}),
\quad
\operatorname{logit}(p_{t,b,x})
=\beta_{0,t}+u_{t,b}+\sum_i\beta_i x_i+
\sum_{(i,j)}\theta_{ij}^{(g)}x_ix_j+
\sum_{S:|S|\ge3}\theta_S x_S.
\]
其中 task intercept 与 block intercept 分层抽样；压力测试加入随机斜率、block overdispersion 和 task drift。
- 真值局部 estimand 必须按目标 task 分布在 probability scale 计算四格差分，而不是把 logit 系数 \(\theta_{ij}\) 直接当成真值标签。

### 2.2 必含五种情景
1. **Additive/null：** 无 pair interaction，检验 false-link 和错误 FOS 密度。
2. **Sparse pairwise：** 稀疏正/负 pair interactions，检验 edge recovery。
3. **Parent sign-flip：** 同一 pair 在不同 parent/context 下交互符号反转，检验 parent conditioning。
4. **Overlapping/higher-order：** 交互组重叠并含三阶项，检验模型失配和错误 pair-only FOS。
5. **Low-support / drift：** 8/16/32/128 task-block 支持、缺失 cell、task distribution shift，检验 abstention 与迁移边界。

每种情景都要有多档效应强度；弱效应与 practical-null 必须按 probability-scale \(\delta_{local}\) 定义。unsupported 不得作为 known-zero。

### 2.3 数据隔离
- 训练 seeds：至少 40；验证 seeds：至少 20；最终 held-out seeds：至少 40。最终 held-out 在模型、阈值、超参、基线实现和停止规则冻结前不可查看。
- 同一 seed 的所有方法共享同一生成参数、task blocks、四格 observations 和合法配置支持。
- 任何 prior scale、阈值、温度、FBL epsilon 或 cDLED 参数只允许在 train/validation 上确定。
- test 结果按 seed 聚合，不能把 pair/context 当成独立 seed 扩大显著性。

## 3. 必须比较的方法

所有估计方法共享相同的四格 task-block 数据和 episode-equivalent 预算：

1. **TCAIL candidate：** Bernoulli task/block hierarchical model，M2/M3 model-specific posterior；输出 \(q=P(|\Delta|>\delta_{local}\mid D)\)、\(w=E[(|\Delta|-\delta_{local})_+\mid D]\)，支持不足时 abstain。
2. **FBL / scaled-FBLT：** 尽可能按原论文机制实现；若将 deterministic fitness 改为 Bernoulli task-block success，必须标为 adaptation，并同时报告 paper-setting reproduction 与 adaptation（若可行）。
3. **cDLED-P3M：** 复现其 individual-local conditional linkage / conditional eVIG 关键机制；若需要适配 task-block Bernoulli 数据，明确 adaptation 边界。
4. **CGOMEA conditional linkage：** 作为 linkage/mating 机制基线；不得把原算法组件误称为新方法。
5. **Simple local contrast / standardized contrast：** 弱基线。
6. **Context-pooled/global score：** 检验 sign-flip 时全局汇总是否抵消局部依赖。
7. **Random linkage** 与 **Oracle linkage**：分别作为随机基线与不可达到的上界。

对无法在同一观测接口下公平复现的基线，必须明确标注原因，不得删除后宣称击败强基线。

## 4. 指标与预注册 Gate

### 4.1 Estimator Gate（主 Gate）
Primary metric：最终 held-out seeds 上、按五种情景 macro-average 的 edge AUPRC。

- 先在 validation seeds 选定 strongest non-oracle baseline；test 不得重新挑基线。
- 计算每 seed 的 TCAIL minus baseline macro-AUPRC，再对 seed 做 paired bootstrap 95% CI。
- **通过条件：** overall macro-AUPRC 差值 95% CI 下界大于 0；且 sparse pairwise 与 parent sign-flip 两个关键情景均不得显著劣于 strongest baseline。
- 若只有部分情景获益，必须收窄论文主张，不得写成普遍优越。

Secondary metrics：
- Posterior q：Brier、reliability curve、calibration intercept/slope、ECE；对不同模型阶数分别检查。
- Null false-link rate：在预注册阈值下报告每 seed 和 pooled rate。
- Positive/negative interaction sign recovery。
- FOS pair co-clustering precision/recall/F1、variation of information、错误 merge rate。
- Abstention risk-coverage curve：尤其 8/16 block，不允许用低支持强制生成边来提高 coverage。
- 按支持量、效应强度、task drift 分层。

### 4.2 Downstream GOM Gate（决定 EC 价值）
仅在 Estimator Gate 通过后启动。对每个 held-out synthetic task family：
- 用独立 discovery blocks 学 linkage；用完全独立 evaluation blocks 评价 GOM 候选配置。
- 比较 TCAIL-FOS、FBL-FOS、cDLED-FOS、CGOMEA-compatible linkage、random FOS、singleton FOS、oracle FOS。
- 同一初始 population、donor policy、subset order protocol、termination rule。
- 总预算必须包括 linkage discovery episodes + GOM search/evaluation episodes；不能只匹配搜索阶段预算。
- Primary metric：固定总 episode-equivalent budget 下，held-out expected success / objective。
- Secondary：达到预定目标的 success rate、evaluation-to-target、best-so-far 曲线、实际 episode/token/time cost。
- 采用 paired seeds 和 paired bootstrap；报告所有 seed，不只均值。

**通过条件：** TCAIL-FOS 相对 validation-selected strongest non-oracle linkage baseline 的 held-out objective/success paired 95% CI 下界大于 0；否则不能声称 TCAIL 带来 EC 搜索提升。Oracle 仅用于判断该任务是否存在可利用的 linkage 上界。

## 5. 立即执行顺序（不再扩展规格）

1. **Clean rerun + code audit：** 重跑现有两个 pilot，核对摘要与原始 CSV 一致；修复所有统计/预算/随机数/公式问题。
2. **Estimator confirmatory implementation：** 实现 Bernoulli task-block likelihood 与 M2/M3 posterior q/w；先在模拟数据上做 null calibration、coverage 和 posterior predictive checks。
3. **Strong baseline implementations：** FBL/scaled-FBLT、cDLED-P3M、CGOMEA linkage，逐项记录 original reproduction/adaptation。
4. **Estimator Gate：** 跑完 train/validation/test，冻结阈值，按预注册指标作 GO/NO-GO。
5. **Downstream GOM Gate：** 只有第 4 步 GO 才执行；将 discovery cost 纳入总预算。

不得先实现 active acquisition、retry ledger 或真实 Agent API；它们不是回答“局部交互估计是否有效、是否改善 EC 搜索”的必要条件。

## 6. 停止规则

- Oracle FOS 在该类任务上都不能改善 GOM：停止该任务族的 linkage-to-GOM 主张，先换可证实有 epistasis 的任务族。
- TCAIL 不优于 strongest baseline：停止 TCAIL estimator 新颖性主张，考虑把其作为成熟组件组合，不继续堆模型。
- TCAIL edge AUPRC 提升但 FOS/GOM 不提升：停止“改善演化搜索”的主张。
- 仅高支持场景获益：论文明确限定支持条件；低支持必须 abstain。
- 任何 test leakage、预算不等价、基线不忠实、指标重算不一致：该轮结果无效，修复后重新运行。

## 7. 资源与边界

- 这一阶段优先 CPU 合成实验；不需要 A800，不调用 DeepSeek/其他真实 LLM API。
- 不启动 CI-GOM/IMCE-RSI；下游只运行隔离的 GOM research prototype。
- 这是研究原型实验授权，不代表生产算法、Phase 0 或真实 Agent 实验已获批准。
- 所有脚本、原始数据、per-seed 结果、环境锁定、Git SHA、运行命令和日志必须入仓库。
- 未运行的实验保持 NOT RUN；不得把 protocol、代码测试或 pilot 当成确认性证据。
