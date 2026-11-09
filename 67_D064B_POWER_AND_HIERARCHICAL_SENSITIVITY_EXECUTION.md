# 67 — D-064-B 执行接管提示词：CondRecSucc 功效重算与 task-family 层级相关敏感性

**日期：** 2026-11-09  
**状态：** READY_TO_EXECUTE（仅授权 D-064-B；不授权正式 A-3b）  
**唯一仓库：** yujian777555/kaitibaogao  
**工作分支：** pilot-a-stateful-recovery  
**D-064-A 已验收基线：** 16e255de627b37713f0ea936df0ddb0dd03ac084  
**main：** 683b3fe7fc52c86e917d523fdc6bbb13abbfd653（不得修改）  
**前置报告：** 66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md  
**独立审查：** 65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md  
**本文件用途：** 下一会话可直接复制执行的完整 Planner/Executor 提示词。

---

# 给下一会话的完整执行指令

你现在接管的是我的硕士毕业论文第一项创新研究。你同时承担研究 Planner、统计方法审查者、实验实现者和 GitHub 仓库维护者的职责。

**不要重新讨论选题，不要重做已经通过的 D-064-A，不要只写研究计划。直接从仓库真实状态出发执行 D-064-B：以正确的 CondRecSucc 主要终点重做功效分析，并验证 task-family 内部相关性对推断和样本量的影响。**

## 一、项目边界与接管规则

唯一仓库：

https://github.com/yujian777555/kaitibaogao

唯一工作分支：

pilot-a-stateful-recovery

接管时首先重新核验：
1. 当前分支 HEAD、main HEAD、ahead/behind；
2. 工作区和暂存区是否 clean；
3. D-064-A 代码、JSON/CSV/报告是否存在且与 Git 一致；
4. 最新 GitHub Actions run 的真实 head SHA、status 和 conclusion；
5. 原始数据及分析产物的 SHA-256。

已知历史基线（必须实时复核，不得盲信）：
- D-064-A final HEAD：16e255de627b37713f0ea936df0ddb0dd03ac084；
- D-064-A 代码/产物提交：ad073eb（短 SHA）；
- main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；
- D-064-A CI：run 42631223393，head SHA 应为 16e255de...，结论 success；
- D-064-A 全套测试：109/109（pilot_a_recovery 28 + pilot_a3b 81）。

绝对禁止：
- 修改 main 或将实验分支合并到 main；
- 访问、查看、解锁或调节正式 held-out test；
- 启动正式 A-3b；
- 启动 Pilot B；
- 启动 A800/ARWM 训练；
- 调用真实 LLM API；
- 执行 UndoBench TEST 或 ThinkingBox；
- 用增加 episode、seed 或同一 task family 内重复轨迹冒充独立 task family；
- 为得到更小样本量或显著结果而更改 estimand、ICC 假设、MDE、统计检验或排除规则。

每次实质性工作完成后，必须更新本文件、NEXT_SESSION_PROMPT.md、README.md、05_DECISION_LOG.md、SESSION_HANDOFF.md 和相关状态文件，并推送当前工作分支。

## 二、D-064-A 已完成的事实基线

正式主要终点定义（64 §3）：

CondRecSucc = 仅在 R1 + R2 场景上计算 class_success 均值。

R3 CorrectEscalation、R4 DamageContainment 必须单独报告，不得混入 CondRecSucc。

D-064-A 正式产物：
- experiments/pilot_a3b/condrec_analysis.py
- experiments/pilot_a3b/test_condrec_analysis.py
- experiments/pilot_a3b/condrec_diagnostic3.json
- experiments/pilot_a3b/condrec_diagnostic3.csv
- experiments/pilot_a3b/condrec_diagnostic3_report.md
- 66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md

原始 diagnostic3 数据 SHA-256：

b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c

D-064-A 主要结果：
- 设计 cluster：54；
- R1/R2 primary-eligible cluster：42；
- zero-denominator cluster：12；
- primary AB CondRecSucc：0.5582；
- NSGA-II CondRecSucc：0.2407；
- cluster-equal Δ：+0.3175；
- 42 个 task×composition cluster 的 SD：0.318856；
- D-064-A cluster bootstrap 95% CI：[0.218254, 0.411376]；
- D-064-A cluster-level sign-flip MC p=0.000125（8000 次，seed 20261111）；
- scenario-weighted Δ=0.314465；
- 配对完整率 1.000；
- 12 个 zero-denominator cluster 均为 delay_rate_permission 与 partial_comp_failure 两种 composition × 6 个 task families。

R3/R4 不能隐去：
- R3 CorrectEscalation：AB 0.226，NSGA-II 0.679；
- R4 DamageContainment：AB 0.800，NSGA-II 0.933。

这说明 AB 在主要恢复成功率上有诊断级优势，但正确升级/损害遏制行为率落后。主要终点和安全行为指标必须分层报告。

### 最重要的新问题：42 个 cluster 并非 42 个已证实独立的抽样单位

42 个有效 cluster 实际嵌套在 **6 个 task families** 中，每个 family 当前有 7 个 R1/R2 eligible composition clusters。原 54 个设计 cluster 是 6 families × 9 compositions。

因此：
- task×composition 是观测/分析 cluster；
- task family 是更高层级的潜在独立抽样单位；
- 同一个 task family 内的多个 fault-composition cluster 可能相关；
- D-064-A 的 42-cluster bootstrap 和 cluster-level sign-flip 不能在未评估 family 内相关前直接当作最终确认性推断；
- D-064-A 的 Δ=+0.3175 是已复算的点估计，但其 CI/p 对独立性假设敏感，D-064-B 必须重新评估。

只有 6 个 task families，ICC 点估计会非常不稳定。历史负 ICC 点估计（曾报告约 −0.09）不能证明独立。

## 三、D-064-B 的唯一目标

回答：

1. 在 task-family 内部相关性存在时，CondRecSucc 的有效不确定性有多大？
2. 原 42-cluster 推断是否过度乐观？
3. ICC=0、0.05、0.10、0.20 时，80%/90% 功效分别需要多少独立 task families？
4. 如果每个 family 有 9 个 composition，但只有约 7 个进入 R1/R2 primary denominator，原 17-family × 9-composition 方案实际有多少 primary-eligible clusters？
5. 加入 15% cluster/family attrition 后，实际需要多少 task families？
6. 哪一种统计检验在层级结构下能控制双侧 alpha=.05 的 Type-I error？
7. MDE=0.08、0.10 等候选效应下，现有 17 个 test families 是否足够？
8. 当前 6 个 family 的诊断数据是否足以估计 ICC？若不足，必须明确报告不确定性，而不是给出“独立”结论。

D-064-B 的结果是**诊断数据驱动的样本量规划和敏感性分析**，不是正式实验，也不允许解锁 test。

## 四、任务 A：数据与统计层级独立核验

优先检查：
- experiments/pilot_a3b/condrec_analysis.py
- experiments/pilot_a3b/condrec_diagnostic3.json
- experiments/pilot_a3b/condrec_diagnostic3.csv
- experiments/pilot_a3b/diagnostic3_results.json
- experiments/pilot_a3b/power_simulation.py
- 64_A3B_PREREGISTRATION_CANDIDATE.md
- 65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md
- 66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md

必须从原始 diagnostic3 rows 或 D-064-A 可追溯的 cluster table 重新建立：
- family_id；
- composition_id；
- cluster_id = family_id × composition_id；
- R1/R2 分母；
- 每 cluster 的 AB−NSGA-II paired difference；
- 每 family 的 eligible cluster 数；
- 每 family 的平均配对差；
- family 内 cluster 方差；
- family 间均值方差。

必须验证：
- 当前确实是 6 个 task families；
- 42 个 primary-eligible clusters；
- 每个 family 当前是否均为 7 个 eligible clusters；
- 12 个 zero-denominator clusters 的分布；
- 同一 scenario 的 seed 嵌套规则不变；
- 没有重复 cluster 或重复 episode；
- 原始数据 SHA 与 D-064-A 一致；
- 不把 42 个 composition clusters 直接声明为 42 个独立 family。

将 6 个 family 的汇总表写入 CSV/JSON，并解释当前 family 数太少对 ICC 估计的影响。

## 五、任务 B：ICC 与层级方差结构分析

以 cluster-level paired difference 为分析变量：

d_fj = AB_fj − NSGAII_fj

其中 f 为 task family，j 为该 family 下的 R1/R2 eligible fault composition。

至少提供以下统计量：
- 总体 cluster-level mean / SD；
- family-level mean；
- family-level mean 的 SD；
- within-family variance；
- between-family variance；
- random-intercept variance；
- ICC；
- ICC 的不确定性区间或 profile/parametric-bootstrap 区间；
- 每个 family 的 cluster 数。

至少使用两种互相核验的 ICC 估计路径：
1. balanced one-way random-effects ANOVA / method-of-moments；
2. random-intercept mixed model（REML 或有依据的等价方法）。

要求：
- 若 method-of-moments ICC 为负，保留原始估计并同时报告边界约束估计；不得静默截断为 0；
- 对 REML 方差分量边界和小样本问题作解释；
- ICC 区间必须反映只有 6 个 family 的不确定性；
- 可以使用 parametric bootstrap 或 profile likelihood，但要说明方法；
- 不得将负 ICC 写成“cluster 独立性已经证明”；
- 与历史 ICC≈−0.09 比较时，解释估计方法、数据口径或分组差异，不能强行匹配历史数字。

**核心原则：** ICC 点估计只作为描述；正式功效必须对预设 ICC 情景做敏感性分析，不依赖一个不稳定的点估计。

## 六、任务 C：重建正确的层级功效模拟

### C1. 主要 estimand 和推断单位

主要 estimand 仍是 64 §3 的 R1/R2-only CondRecSucc。

不得混入 R3/R4 或 UNKNOWN。

保留 task×composition cluster 的观测结构，但推断必须承认多个 composition cluster 嵌套在同一个 task family 内。

balanced 情形（每 family 7 个 eligible compositions）下，family 均值的等权平均与 cluster 等权总体均值一致。若未来每个 family 的 eligible composition 数不同，必须分别报告：
- cluster-equal estimand；
- family-equal estimand；
- 两者差异及敏感性。

不得在不说明的情况下从 cluster-equal 偷换为 family-equal。

### C2. 至少两类数据生成机制

**机制 1：Empirical family-block resampling**

- 将一个 task family 的全部 eligible composition cluster differences 作为一个整体 block；
- 重采样单位为 family，不得拆散同 family 的 compositions；
- 以 family-block bootstrap 构造抽样分布；
- 对仅有 6 个 family 导致的经验分布局限做明确说明；
- 不得将 42 个 cluster 独立重采样并称为 family-block bootstrap。

**机制 2：ICC-controlled hierarchical random-intercept simulation**

使用清晰可审计的层级生成模型，例如：

d_fj = μ + u_f + ε_fj

其中：
- u_f 为 task-family 随机效应；
- ε_fj 为 family 内 composition cluster 残差；
- 总边际方差与诊断数据的 cluster-level 方差相匹配；
- 通过预设 ICC 控制 family 内相关；
- 残差分布尽可能利用 D-064-A 的经验分布形状；
- 若使用正态随机效应，检查生成差值超出理论范围 [-1,1] 的比例，并提供 bounded-outcome 敏感性方案；
- 不得用裁剪结果掩盖分布失真；
- 清楚区分“由诊断数据估计的参数”和“人为指定的敏感性参数”。

ICC 情景至少为：

0、0.05、0.10、0.20。

可以额外报告 0.30，但不能省略上述四档。

### C3. MDE 网格与解释纪律

至少评估：
- 0.05
- 0.08
- 0.10
- 0.1173
- 0.15

其中：
- 0.1173 是历史 validation 观察效应，只能作为历史对照敏感性值；
- D-064-A 观察效应 +0.3175 不是 MDE；
- 不得把观察到的大效应直接当作最小有意义效应；
- 不得为了使现有 17 个 families 看起来足够而选择 MDE；
- 必须区分统计可检出差异与研究/工程上有意义的最小差异。

D-064-B 应给出不同 MDE 的功效曲线和样本量表，但**不单方面冻结最终 MDE**。最终 MDE 需要有事前科学/实践意义依据，并在正式预注册批准前由用户确认。

### C4. 检验方法和校准

双侧 alpha=.05；同时报告 80% 和 90% power。

至少比较：
1. family-level Student-t test（family 为独立推断单位）；
2. family-level exact sign-flip（family 数较小时）或可复现 Monte Carlo sign-flip；
3. family-block bootstrap / 合适的层级方法作为敏感性分析。

**禁止**在 ICC>0 时仍把 42 个 composition clusters 当作完全独立单位做主检验。

当前只有 6 个 family 时，exact two-sided sign-flip 的离散分辨率很粗；报告实际可达到的 p 值网格，不要通过增加 Monte Carlo 次数假装获得更高的独立样本分辨率。

每个统计方法必须做 null calibration：
- 在 μ=0 下估计 Type-I error；
- 报告 Monte Carlo standard error 和 95% Monte Carlo interval；
- 若实际 Type-I error 明显偏离 .05，必须标为未校准并解释；
- 不能只报告 power，不报告 null false-positive rate；
- 不允许把正态 z 近似称作 Student-t 或 sign-flip；
- 不允许对 per-seed p 值或 CI 做简单平均。

模拟次数建议至少 10,000 次/配置；若计算成本较高，可以先做小规模开发测试，但最终结果必须达到预先说明的 MCSE 精度（建议 power MCSE ≤0.005），并记录实际次数、种子和停止依据。

## 七、任务 D：样本量与任务族数量换算

64 号候选方案目前是：

17 test task families × 9 fault compositions = 153 个设计 cluster。

但 D-064-A 发现当前每个 family 的 9 个 compositions 中只有 7 个进入 R1/R2 primary denominator：

6 families × 7 eligible compositions = 42 primary-eligible clusters。

因此，**153 个设计 clusters 不等于 153 个 primary-eligible clusters**。

如果未来仍保持 7/9 eligible 的结构，17 个 test families 预计只有 119 个 primary-eligible clusters（未计失效）。这只是按当前诊断结构的条件性投影，不是新任务族生成器的最终事实；D-064-C 还要重新验证标签分布。

功效报告必须分开给出：
- 独立 task-family 数；
- 总设计 cluster 数；
- primary-eligible cluster 数；
- 每 family 的 eligible cluster 数；
- cluster-level attrition 后数量；
- family-level attrition 后数量；
- 对应 power。

至少做以下设计敏感性：
- 每 family 9 个设计 compositions；
- primary-eligible compositions/family = 6、7、8、9；
- cluster-level attrition = 0%、10%、15%、20%；
- family-level attrition = 0%、10%、15%、20%；
- ICC = 0、0.05、0.10、0.20；
- task families 数量网格至少包含 6、8、10、12、15、17、19、22、25、30、40。

不要只用 design effect 公式替代仿真。可以报告 DE=1+(m−1)ρ 作为核对，但最终样本量必须来自实际层级模拟和正确推断程序。

特别核对：
- 17 families ×9 compositions =153 design clusters；
- 在 7/9 eligibility 假设下 =119 primary-eligible clusters；
- 15% 失效后还会进一步下降；
- 若 family-level attrition，丢失一个 family 会同时丢失其全部 compositions；
- 不能把重复 seeds、episode 或同 family 新增轨迹当作新 family。

给出每种 ICC/MDE/power 组合下需要多少 test families，并明确 17-family 候选方案在哪些条件下足够、在哪些条件下不足。

## 八、任务 E：D-064-A 统计推断重新限定

D-064-A 的点估计 Δ=+0.3175 保留，不得修改原始结果。

但必须新增层级敏感性结果：
- 42-cluster independent analysis（作为旧口径参考）；
- 6-family aggregate analysis；
- family-level t interval/test；
- family-level sign-flip；
- family-block bootstrap；
- ICC-controlled model 的推断区间。

解释：
- 点估计是否保持；
- CI 是否变宽；
- p 值是否改变；
- 42-cluster 级 p=0.000125 在 family dependence 下是否仍适用；
- 目前只有 6 families 能支持怎样的外推范围；
- 诊断数据的显著性是否仍然成立，还是仅能说方向一致。

不要把“D-064-A 的 cluster-level p 显著”自动升级成“考虑 family 依赖后仍显著”。

## 九、任务 F：R3/R4 和安全边界

R3 CorrectEscalation、R4 DamageContainment 保持独立。

可以提供其 family-level 描述和置信区间/精度分析，但：
- 不得混入 CondRecSucc primary；
- 不得因 AB 的 primary 增益掩盖 AB 在 R3/R4 上的落后；
- 不得把行为成功率与硬安全违规率混为一谈；
- 不得宣称零观察风险等于零风险；
- 正式实验的安全硬门仍须在 64 修订版中明确。

D-064-B 重点是主要终点功效和 family-level 依赖；不要擅自改写 R3/R4 的正式终点定义。

## 十、代码、测试与产物要求

建议实现：
- experiments/pilot_a3b/power_hierarchical.py
- experiments/pilot_a3b/test_power_hierarchical.py
- experiments/pilot_a3b/power_hierarchical.json
- experiments/pilot_a3b/power_hierarchical_report.md
- experiments/pilot_a3b/family_cluster_diagnostics.csv
- 可选：功效曲线图和 family-level diagnostics 图。

测试至少覆盖：
1. family ID 从 cluster ID 正确解析；
2. 42 clusters 正确分为 6 families；
3. 每 family 的 eligible cluster 数准确；
4. family-block bootstrap 不拆分 family；
5. ICC=0 时模拟器接近独立 cluster 情况；
6. ICC 增大时方差/设计效应方向合理；
7. empirical marginal variance 与目标值匹配；
8. family-level sign-flip 的离散 p 网格正确；
9. null Type-I error 估计和 MCSE 正确；
10. power MCSE/区间正确；
11. MDE 网格完整；
12. family/cluster attrition 计算正确；
13. design clusters 与 primary-eligible clusters 不混淆；
14. 不会将 seed/episode 当作 family；
15. 随机种子可复现；
16. 原始数据 SHA-256 校验；
17. 没有硬编码 +0.3175、SD=0.318856 或历史 power 摘要；
18. 对异常/不可能的 ICC、负方差、零 family、零 eligible cluster fail closed。

使用微型人工数据验证已知答案，并用真实 diagnostic3 数据做回归。全部随机生成过程都必须记录 seed。

## 十一、正式决策边界

D-064-B 完成后：
- 可以给出基于 ICC 情景的条件性样本量建议；
- 可以建议 17 个 test families 是否足够；
- 可以指出需要扩展到 19、22、25 或更多 families；
- 可以给出 MDE 的候选范围和理由；
- 可以说明当前 6 个 families 对 ICC 估计的局限。

但**不得在 D-064-C 的任务语义验证与正式场景生成器完成前，最终冻结 test family 数、primary-eligible cluster 数和标签分布**。

64_A3B_PREREGISTRATION_CANDIDATE.md 继续保持未批准状态。D-064-B 只新增分析结果和修订建议；若需要提出 64 的修订，另存候选修订稿或明确 diff，不得覆盖原始候选并伪装成已批准版本。

最终 MDE 必须有事前实践意义依据，不能从 +0.3175 观察效应倒推。用户批准前不得将 64 标记为 APPROVED。

## 十二、仓库维护要求

完成 D-064-B 后，必须：
1. 更新本文件的执行状态和结果摘要；
2. 更新 NEXT_SESSION_PROMPT.md（下一任务应转为 D-064-C 或经证据支持的明确下一步）；
3. 更新 README.md；
4. 更新 05_DECISION_LOG.md；
5. 更新 SESSION_HANDOFF.md；
6. 更新 65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md，明确 P0-2/P0-3 是否关闭；
7. 更新 62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md；
8. 必要时更新 51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md；
9. 不覆盖 diagnostic3 原始数据和 D-064-A 产物；
10. 运行全部相关测试；
11. 真实触发 GitHub Actions CI，并核验 run head SHA 与结论；
12. 确认工作区 clean、远端与本地 SHA 一致；
13. 保持 main 不变；
14. 记录全部输入哈希、代码 SHA、分析命令、随机种子、MC 次数和输出哈希。

## 十三、最终汇报格式

完成后严格按以下格式汇报：

### 1. 仓库状态
起始 SHA、最终 SHA、main SHA、ahead/behind、推送状态、工作区状态。

### 2. D-064-A 数据复核
原始输入 SHA、D-064-A 输出 SHA、42 clusters / 6 families 结构、每 family eligible 数。

### 3. ICC 与层级方差
family means、within/between variance、ICC 方法、ICC 点估计、区间和小样本限制。

### 4. 功效模拟设计
数据生成机制、ICC 网格、MDE 网格、检验方法、alpha、power 目标、MC 次数、随机种子。

### 5. Type-I error 校准
各 ICC/检验方法的 null FPR、MCSE、95% MC 区间；未校准方法必须明确标记。

### 6. 样本量结果
按 MDE × ICC × power 输出需要的独立 families、设计 clusters、primary-eligible clusters、失效预留后数量。

### 7. 17-family 方案评估
区分 153 design clusters 与在 7/9 eligibility 下的 119 primary-eligible clusters；报告何种 ICC/MDE 条件下足够或不足。

### 8. 对 D-064-A 推断的影响
Δ 是否保持、CI/p 是否变化、cluster-level p 是否仍适用、诊断证据边界。

### 9. R3/R4
保持独立，报告主要权衡，不得跨类抵消。

### 10. 测试与 CI
测试数量、通过/失败、真实 Actions run 链接、run head SHA。

### 11. 科学结论
明确是否支持继续第一项创新、统计不确定性、样本量方案限制。不得宣称正式创新已经成立。

### 12. GO/HOLD
D-064-B 是否通过；D-064-C 是否可进入；正式 A-3b 是否继续 HOLD。

### 13. 仓库维护与下一会话提示词
列出更新文件、提交 SHA 和最新 NEXT_SESSION_PROMPT.md 链接。

---

## 最终执行指令

**接管后直接执行 D-064-B，不要再询问是否开始。**

先核验真实仓库状态与 D-064-A 输入哈希，然后从 42 个 R1/R2 cluster differences 和 6 个 task families 的嵌套结构开始。

优先保证：
1. 推断单位正确；
2. ICC 不确定性如实报告；
3. Type-I error 校准；
4. 主要终点 estimand 不变；
5. 不将 153 个设计 cluster 错当成 153 个 primary-eligible cluster；
6. 不把诊断观察效应当作 MDE；
7. 不查看正式 test；
8. 每轮更新并推送仓库和接管提示词。

**D-064-B 的交付目标是得到可信的功效曲线和条件性样本量方案，不是为了证明现有 17 个 task families 一定够用。**

---

## D-064-B 执行完成记录（2026-11-09）

交付：`power_hierarchical.py` + `test_power_hierarchical.py`（22/22）+ `power_hierarchical.json` + `power_hierarchical_report.md` + `family_cluster_diagnostics.csv` + `68_D064B_HIERARCHICAL_POWER_REPORT.md`。

- **Task A ✓**：6 families × 7 comps = 42 clusters、零分母 12、seed 嵌套正确、无重复——零问题。
- **Task B ✓**：ANOVA/MoM ICC=−0.1257、REML 边界 0、family-block bootstrap CI [−0.159,−0.111]；负值保留且不解释为独立性证明；敏感性网格替代点估计。
- **Task C ✓**：双机制（family-block 重采样 + ICC 层级模拟，边际方差匹配，越界率 ~1e-5）；MDE 网格 0.05–0.15；ICC 0/0.05/0.10/0.20；key cells 10,000 次、sweep 2,000 次含 MCSE/CI；null 校准：**t 0.050–0.056 ✓、符号翻转 0.031(F=6)/0.05(F=17) ✓、bootstrap CI 检验 0.08–0.14 反保守 ✗**（发现并修复 2 个校准 bug：MC 计数、块中心化）。
- **Task D ✓**：所需 families 表（MDE 0.10 @80%：ICC 0→15、0.05→17、0.10→22、0.20→30；双 15% 损耗 22/30/40/40）；design 153 vs eligible 119 区分；DE 公式仅核对。
- **Task E ✓**：层级推断保持显著（t p=4.6e-5、精确符号翻转 p=0.031=2/64、block bootstrap CI [0.272,0.357]）；6/6 family 全正；外推范围限定于 6 抽样单位。
- **Task F ✓**：R3 AB 0.226 vs NSGA-II 0.679；R4 0.800 vs 0.933——权衡如实。

**17-family 评估**：条件性充分（低 ICC + 低损耗 + MDE≥0.10）；ICC=0.10 或 15% 损耗或 MDE=0.08 时不足（须 22–40 families）。

**状态**：GO=D-064-C（语义 validator + 正式生成器 + MDE/样本量唯一冻结）；HOLD 不变；64 号保持 REQUEST CHANGES。
