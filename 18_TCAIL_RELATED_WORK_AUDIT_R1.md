# 18 — TCAIL 相关工作与新颖性审查 R1

**日期：** 2026-11-02  
**范围：** TCAIL / Agent component interaction learning / active experimental design  
**状态：** INITIAL LITERATURE AUDIT / NOT EXHAUSTIVE  
**结论：** 研究问题有现实意义，但 TCAIL V1 的独立新颖性尚未成立。  
**唯一研究仓库：** yujian777555/kaitibaogao

---

## 1. 核心结论

本轮检索确认：以下内容均不能单独作为 TCAIL 的新颖性主张：

- Agent 组件之间存在正/负交互；
- 用全因子实验识别模块交互；
- 用回归模型拟合主效应和 pairwise interaction；
- 用 Group-ARD / 稀疏回归筛选交互；
- 用 Bayesian information gain / D-optimality 选择下一次实验；
- 对交互变量选择使用 Bayesian FDR；
- 对 Agent harness 做预算约束的自动搜索。

这些方向在实验设计、统计学习和近期 Agent 研究中均已有先例。

当前唯一值得继续验证的候选缺口是：

> 当 Agent 模块组合评价具有随机噪声、任务家族异质性、合法组合约束和有限 rollout 预算时，如何定义可解释的任务条件化交互 estimand，并在可识别性门禁、校准和全局 false-discovery 控制下，选择能降低交互边决策风险的合法实验？

这是一个待验证的研究缺口，不是已经证明的空白。

---

## 2. 相关工作

### R1 — Lewis & Dean (2001), interaction group screening

S. M. Lewis and A. M. Dean, “Detection of Interactions in Experiments on Large Numbers of Factors,” Journal of the Royal Statistical Society: Series B, 63(4), 633–672, 2001. DOI: 10.1111/1467-9868.00304.

主要内容：
- 研究大量因子下的交互检测；
- 提出两阶段 group screening；
- 其中一种方案在第一阶段同时估计主效应与关键两因子交互；
- 以总观测数、超预算概率和漏检比例为设计准则。

对 TCAIL 的影响：
- “有限预算下识别稀疏交互”不是新问题；
- 必须将 interaction group screening 作为相关方法基线或至少解释其不适用之处；
- TCAIL 的差异只能落在 Agent task context、合法组合约束、随机 rollout 和后验边决策上。

来源：
https://doi.org/10.1111/1467-9868.00304

### R2 — Singh & Stufken (2024), GDS-ARM

Rakhi Singh and John Stufken, “Factor selection in screening experiments by aggregation over random models,” Computational Statistics & Data Analysis, 194, 107940, June 2024. DOI: 10.1016/j.csda.2024.107940.

主要内容：
- 针对大量主效应和两因子交互导致模型维数过高的问题；
- 在多个随机选取的交互子模型上执行 Gauss-Dantzig Selector；
- 聚合多模型结果识别重要因子。

对 TCAIL 的影响：
- 必须纳入 sparse screening / random-model aggregation 类基线；
- 不能只与 OLS 和随机采样比较；
- 需要证明任务条件化后验、合法空间识别或自适应设计确有额外收益。

来源：
https://doi.org/10.1016/j.csda.2024.107940

### R3 — Huan, Jagalur & Marzouk (2024), Optimal Experimental Design

Xun Huan, Jayanth Jagalur, and Youssef Marzouk, “Optimal experimental design: Formulations and computations,” Acta Numerica, 33, 715–840, 2024. DOI: 10.1017/S0962492924000023.

主要内容：
- 系统综述经典与 Bayesian optimal experimental design；
- 讨论信息型、决策型实验效用；
- 涵盖非 Gaussian / 非线性模型的 expected utility 计算；
- 讨论离散组合观测选择和 sequential optimal design。

对 TCAIL 的影响：
- posterior IG、Bayesian D-optimal、expected utility、sequential acquisition 都有成熟理论；
- 不能将 interaction-only log-determinant 本身宣称为新算法；
- V2 必须设置严格匹配的 Bayesian interaction-subspace D-optimal 对照；
- 若提出 edge-decision risk reduction，也必须作为已有 goal-oriented / decision-theoretic design 的具体应用接受比较。

来源：
https://doi.org/10.1017/S0962492924000023

### R4 — Hainy et al. (2022), Bayesian design for model discrimination

Markus Hainy, David J. Price, Olivier Restif, Christopher Drovandi et al., “Optimal Bayesian design for model discrimination via classification,” Statistics and Computing, 32, Article 25, 2022. DOI: 10.1007/s11222-022-10078-2.

主要内容：
- Bayesian model discrimination；
- 用分类器近似 expected model discrimination design；
- 以 misclassification error 评价设计；
- 明确采用设计损失/expected utility，而不是只最大化参数信息量。

对 TCAIL 的影响：
- edge-decision risk reduction 并非天然新颖；
- 应与 decision-theoretic / classification-based design 进行方法层面对照；
- 不能因为把 model discrimination 换成 edge classification 就宣称首次提出。

来源：
https://doi.org/10.1007/s11222-022-10078-2

### R5 — Chen et al. (2008), Bayesian FDR for interaction selection

Wei Chen, Debashis Ghosh, Trivellore E. Raghunathan, and Daniel J. Sargent, “A false-discovery-rate-based loss framework for selection of interactions,” Statistics in Medicine, 27(11), 2004–2021, 2008. DOI: 10.1002/sim.3118.

主要内容：
- 研究交互变量选择的多重比较；
- 提出 Bayesian context 下的 FDR loss 和决策规则；
- 通过模拟比较 FDR 与 power。

对 TCAIL 的影响：
- Bayesian FDR 不能算作 TCAIL 新颖点；
- V2 的 BFDR 是统计治理和正确性要求；
- 应引用并说明我们针对任务条件化边集的具体实施方式。

来源：
https://doi.org/10.1002/sim.3118

### R6 — Lauziere, Daugherty & Kushner (2026), IAMs

Andrew Lauziere, Jonathan Daugherty, and Taisa Kushner, “A Regression Framework for Understanding Prompt Component Impact on LLM Performance,” arXiv:2603.26830, March 2026.

主要内容：
- 把 prompt 拆分为多个组件；
- 通过二元设计矩阵编码组件是否出现；
- 回归模型同时包含主效应和二阶、三阶交互项；
- 通过全组合 prompt 子集对模型表现进行分析。

对 TCAIL 的影响：
- “把 Agent/Prompt 组件编码为因子并回归估计交互”已经有直接先例；
- 不能将二元组件编码、pairwise regression 或可视化作为独立创新；
- 必须说明 TCAIL 解决了其固定/全组合分析之外的预算、随机性、任务条件和约束问题。

来源：
https://arxiv.org/abs/2603.26830

### R7 — Liu (2026), More Is Not Always Better

Ming Liu, “More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding,” arXiv:2605.05716, May 2026.

主要内容：
- 对 planning、tool use、memory、structured reasoning、reflection 五个组件做 2^5 全因子实验；
- 研究 HotpotQA 与 GSM8K 的组件组合；
- 报告任务和模型规模相关的组件效果；
- 其特定 HotpotQA 设置下，主效应模型的 LOOCV R² 为 0.872，而加入 pairwise terms 后为 0.748，显示 pairwise model 在该数据设置中可能过拟合；
- 报告一个探索性三阶交互。

对 TCAIL 的影响：
- Agent 组件交互已经被直接研究，不能宣称发现交互本身是新颖；
- 更重要的是，真实 Agent 场景不保证 pairwise 模型有用；
- TCAIL 必须包含 additive/null、three-way-only 和高阶混合情形；
- 必须证明 pairwise graph 在独立任务上的识别/预算价值，而不是默认 pairwise interaction 一定存在；
- 该工作是 arXiv preprint，结果作为强相关先例与实验警示，不视为所有 Agent 的普遍规律。

来源：
https://arxiv.org/abs/2605.05716

### R8 — Radwan, Vasilakos & Raza (2026), Harness-Aware Evaluation

Ahmed Y. Radwan, Athanasios V. Vasilakos, and Shaina Raza, “Harness-Aware Evaluation of LLM Agents: Systems, Benchmarks, and Protocols,” Preprints, September 2026, DOI: 10.20944/preprints202609.2140.v1.

主要内容：
- 将 Agent 结果视为 model、harness、environment、evaluator 与 protocol 的共同产物；
- 强调任务划分、预算、重复运行和配置报告；
- 将“如何在不穷举全部配置的情况下测量因素交互”列为开放方向之一。

对 TCAIL 的影响：
- 支持该研究问题具有现实意义；
- 也说明交互测量、跨环境泛化和公平预算仍是研究议题；
- 该 survey 的 open challenge 不能直接当作算法新颖性证明。

来源：
https://doi.org/10.20944/preprints202609.2140.v1

### R9 — Zhao et al. (2026), Beyond Prompts

Cen Mia Zhao, Haibo Ruan, Wenjie Chen, Pei-fen Tu, Usman Abbasi, and Joel Hesch, “Beyond Prompts: Measuring and Optimizing LLM Tool-Agent Harnesses,” arXiv:2609.05736, September 2026.

主要内容：
- 研究固定模型下 prompt 与 tool-boundary middleware 的预算约束优化；
- 使用 failure routing、进化搜索、Pareto retention 和 reliability-oriented selection；
- 与 BetterHarness-style hill climbing、MIPROv2、GEPA 等比较；
- 强调相同 rollout budget、held-out scorecard 和搜索可靠性。

对 TCAIL 的影响：
- Agent harness 的自动优化和进化搜索已有很近的研究；
- 不能把“自动搜索 Agent 组件”作为 CI-GOM 的唯一创新；
- 后续 CI-GOM 必须证明 linkage、contract repair、donor 和 noisy acceptance 的独立算法收益；
- 该工作不等同于交互结构主动识别，但应进入后续 Paper 2 相关工作审查。

来源：
https://arxiv.org/abs/2609.05736

---

## 3. 研究缺口的当前判断

### 已经被覆盖的部分
- 组件全因子实验与组合比较；
- 组件/Prompt 的主效应和 pairwise regression；
- 稀疏交互筛选；
- 大规模因子交互 group screening；
- Bayesian D-optimal / expected information gain；
- Bayesian FDR；
- 预算约束的 Agent harness 搜索与 Pareto 进化。

### 仍值得检验、但尚未证明空白的部分
- Agent rollout 噪声下的任务条件化交互估计；
- 合法配置约束导致的 contrast estimability；
- 把当前样本不足与结构性不可识别明确分开；
- 在统一 rollout budget 下，比较交互边决策风险下降与参数信息增益；
- 在真实 Agent task-family shift 中检验交互结构是否稳定、异质或符号翻转；
- 识别出的图是否真的改善后续演化计算搜索，而不是只提高统计指标。

### 新颖性判定

TCAIL V1：**不接受为已成立的新算法。**

TCAIL V2：**保留为条件性研究候选。**

未来可以成立的贡献必须是：
1. 明确定义 Agent 模块合法空间与任务条件化交互 estimand；
2. 对当前设计支持和结构性不可识别进行可靠区分；
3. 在强基线下证明其能以更少 rollout 获得校准、可复现的交互边决策；
4. 真实 Agent 验证表明识别的结构具有实际价值；
5. 进一步证明该结构能够改善 EC 的 linkage / mixing / search，才与毕业论文 EC 主线闭环。

---

## 4. 文献登记状态

本文件是首轮相关工作审计，不代表系统性综述完成。下一轮需：
- 检查上述论文的版本、实验设置和补充材料；
- 对比其设计矩阵、estimand、统计单位、预算和数据划分；
- 搜索 2025–2026 年 active factorial design、sparse interaction learning、goal-oriented Bayesian design 和 agent configuration optimization；
- 在相关工作矩阵中记录“已覆盖机制 / 尚未覆盖机制 / 可改进不足 / 直接基线”。

**不能因为没有检索到完全相同的 TCAIL 名称，就认定算法新颖。**
