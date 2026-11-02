# 13 — 演化计算参数调节与自适应控制方案

**日期：** 2026-11-02  
**状态：** PARAMETER POLICY DECISION / INITIAL HYPOTHESES  
**适用对象：** Paper 1 交互结构估计器 + Paper 2 Agent 约束最优混合演化  
**原则：** 参数控制是算法设计的一部分，但不自动构成独立创新点。

---

## 1. 最终决策：三层调参，而不是人工逐项试数值

本课题采用：

1. **离线算法配置（offline tuning）：** 在训练任务上用 irace / iterated racing 搜索少量关键超参数；
2. **在线反馈控制（adaptive parameter control）：** 在每轮演化中，根据历史有效收益调整变异强度和算子选择概率；
3. **统计门禁参数固定（pre-specified statistical gates）：** 显著性水平、最小实际改进幅度和硬约束不由搜索结果随意改变。

不把 LLM 作为参数决策者，不允许它凭自然语言反思任意改写参数。

### 1.1 为什么这样分层

Eiben et al. 的参数控制分类区分参数调优与运行时控制；运行时控制又包括 deterministic、adaptive 和 self-adaptive。Aleti & Moser 的系统综述也指出，反馈信号、信用分配和更新机制是自适应参数控制的重要组成部分。

SHADE 通过历史成功的 DE 参数设置更新未来的 \(F\)、\(CR\)；Adaptive Operator Selection (AOS) 通过算子信用分配和选择规则调整算子使用概率。两者是可借鉴的成熟思想，不是本课题的新颖性来源。

## 2. 先区分三类“参数”

### 2.1 Agent 解的基因（被优化对象）

\[
x=(x_1,\ldots,x_m)
\]

每个 \(x_i\) 是 Agent 功能槽位的模块 ID，例如 planning、tool routing、memory、verification/recovery 的候选实现。它们是演化对象，不是优化器参数。

### 2.2 演化算法控制参数（决定如何搜索）

包括种群规模、变异强度、FOS/linkage block 顺序、donor 选择、算子选择概率、交互图更新频率等。这些参数才是本文件的调参对象。

### 2.3 统计评价门禁（控制结论可信度）

包括 \(\alpha\)、最小实际改进幅度 \(\delta_{\min}\)、最大重复评价次数、置信区间/序贯检验规则。这些参数不能通过“哪组让算法分数最高”来调节，否则会破坏统计错误率控制。应通过统计设计和 pilot 方差估计预先确定。

---

## 3. Paper 1：交互结构估计器参数

Paper 1 的核心是预算受限的任务条件化稀疏交互识别。

| 参数 | 含义 | 如何确定 |
|---|---|---|
| \(\lambda_{\mathrm{sparse}}\) | 主效应/交互项的稀疏正则强度 | 训练任务内层交叉验证；在合成真值上检验偏差与召回的权衡 |
| \(\tau_{\mathrm{edge}}\) | 交互边保留门槛 | 通过合成真值校准；按预注册置信水平与多重比较校正 |
| \(B_{\mathrm{batch}}\) | 每批新增评价数 | 先比较固定批量设计，再评估批量更新对预算和估计误差的影响 |
| \(n_{\mathrm{rep}}\) | 配置重复执行数 | pilot 方差 + 功效分析；不随最终得分任意改变 |
| \(z\)-conditioning complexity | 任务条件化模型复杂度 | 训练任务分组验证，优先共享参数 + 小幅任务偏移，避免小样本过拟合 |

### 3.1 交互边保留规则

不将 \(\lambda_{\mathrm{sparse}}\) 和 \(\tau_{\mathrm{edge}}\) 混为一谈。

建议只有当某个交互效应的置信区间在多重比较校正后排除实际等价区间 \([-\delta_{\min},+\delta_{\min}]\)，才建立有符号交互边：
- 明确大于 \(+\delta_{\min}\)：正交互候选；
- 明确小于 \(-\delta_{\min}\)：负交互候选；
- 落在等价区间或不确定：不建强制边。

4 个槽位只有 6 个 pairwise tests，第一版采用 Holm 校正即可；规模扩大后再评估 FDR 控制。统计门槛在看 test 结果之前锁定。

### 3.2 主动采样参数

第一版将主动采样目标限定为“降低交互结构估计不确定性 / 单位评价成本”，不再额外引入一个未校准的 fitness-versus-information 权重 \(\eta\)。搜索最优配置是 Paper 2 的任务。

候选 acquisition：
\[
A_t(x)=\frac{\mathbb E[\Delta U_{\mathrm{interaction}}\mid x,\mathcal D_t]}{c(x)}
\]
其中 \(x\) 必须属于合法配置集合。若某配置对关键交互不可识别或结构非法，则不能因其预测不确定性高而被采样。

---

## 4. Paper 2：Agent 约束最优混合演化的参数

### 4.1 参数清单与初始策略

| 参数 | 第一版策略 | 后续调节方式 |
|---|---|---|
| Population size \(N\) | 合成 4 槽位实验先固定 \(N=8\) | 做 \(N\in\{4,8,12\}\) 敏感性；规模扩大后比较 IMS/P3 |
| Mutation intensity \(K\) | 每次变异改动的槽位数，候选 \(K\in\{1,2,3\}\) | 由在线成功历史控制器选择 |
| Per-locus mutation \(p_m\) | 作为基线，\(p_m=1/m\)；4 槽位时为 0.25 | 主算法中由 \(K\) 选择隐式决定，不另设重复的自由参数 |
| FOS composition | 单槽位集合 + 统计可信的正向 pairwise linkage blocks | 第一版最大块大小为 2；高阶交互有证据后再扩展 |
| FOS order | random / ascending block size | 离线调参比较 |
| Donor strategy | 只从接口合法的 donor pool 中选择 | random-compatible vs exhaustive-compatible 离线比较 |
| Negative interaction | 不当作硬约束 | 作为软兼容性/条件供体筛选信号；低置信负边不阻止重组 |
| Contract repair | 确定性最小依赖闭包修复；不能唯一修复则拒绝 | 不用 LLM 自由修复；修复范围由接口/依赖规范决定 |
| Graph update interval | 每完成一批配对评价后更新 | 比较每 1、2、4 个 generation 更新一次 |
| Operator controller | discounted UCB / AOS | 调整探索系数 \(c\) 和历史折扣 \(\rho\) |
| Acceptance | 配对任务上的序贯置信规则 | \(\alpha\) 与 \(\delta_{\min}\) 预先确定，不按 test 调参 |
| Population scheme | Phase 0 固定种群 | 扩大后比较 fixed-N、IMS、P3，所有方案同 FE/rollout budget |

**重要：** 本算法是 categorical genotype + GOM 思路，不是 Differential Evolution。因此不引入 DE 专属的 \(F\)、\(CR\) 参数。若 DE 作为对照，则按 JADE/SHADE/L-SHADE 的适配方式使用其参数，不能把它们硬塞进 GOM。

### 4.2 为什么第一版只用 pairwise blocks

4 槽位的 Phase 0 只有 6 条可能的 pairwise edge。第一版 FOS 使用 singleton + 可信正交互 pair，不直接把图的连通分量合并成一个大块，避免一条链式边把所有基因绑定。

负交互不是“非法组合”的同义词：
- 类型/接口/调用依赖失败是硬约束，必须拒绝或确定性修复；
- 负交互是性能层面的拮抗证据，只能用于条件 donor 筛选或避免高风险混合；
- 低置信负交互不能成为硬拒绝规则。

### 4.3 在线自适应算子控制

动作集合：
\[
\mathcal A=\{
\text{mutation-1},
\text{mutation-2},
\text{mutation-3},
\text{positive-linkage-mix},
\text{conditional-donor-mix}
\}.
\]

每个动作维护历史收益。一次子代评价采用同任务、同初态、配对 seed（若可控）估计改进；不能配对 seed 时使用 task-blocked repeated runs。

定义成本归一化的保守奖励：
\[
R_{a,t}=
\frac{\max(0,\operatorname{LCB}_{1-\alpha}(\widehat{\Delta f}_{a,t}))}
{C_{a,t}},
\]
无效 offspring 的奖励为 0，并单独记录原因。\(C_{a,t}\) 至少统计 rollout 数；API tokens / wall-clock / monetary cost 另行报告，不能在不同单位之间随意相加。

更新历史均值：
\[
\bar R_{a,t}=(1-\rho)\bar R_{a,t-1}+\rho R_{a,t}.
\]

选择分数：
\[
UCB_{a,t}=
\bar R_{a,t}
+c\sqrt{\frac{\ln(1+\sum_b n_{b,t})}{1+n_{a,t}}}.
\]

每轮选择 \(UCB\) 最大的动作，或按归一化分数采样。\(c\) 控制探索，\(\rho\) 控制旧历史遗忘速度。

这属于已有 AOS / bandit parameter control 思路。它在本课题中是搜索控制模块，不单独宣称创新。真正待验证的算法贡献仍是 interaction linkage 如何形成合法 FOS、如何处理负交互/接口依赖，以及如何进行噪声感知的 constrained mixing。

### 4.4 多参数不要全部在线变化

第一版只让 \(K\)/算子动作选择在线变化。以下参数先固定或离线选择：
- 种群规模；
- FOS 构造规则和顺序；
- donor 搜索策略；
- 交互稀疏强度；
- 交互图更新批量；
- 统计置信门槛。

这样可避免同时改变太多参数而无法解释性能变化。

---

## 5. 离线调参工具与实验协议

### 5.1 选择 irace 的理由

irace 使用 iterated racing 对算法配置进行自动调优：先产生候选参数配置，再在多个问题实例上评价，并逐步淘汰明显较差的配置。其适合包含数值、类别和条件参数的算法配置问题；本课题的 donor strategy、FOS order、population scheme 属于类别参数，\(c,\rho,\lambda_{\mathrm{sparse}}\) 等属于数值参数。

**决策：** 第一版离线调参优先使用 irace；若运行环境不便安装 R，则可用 SMAC/Optuna 实现同样的严格预算和训练/验证隔离，但必须记录配置器及其版本。不能为了方便而在 test tasks 上反复试参。

### 5.2 推荐的离线调参参数空间

先控制规模，不把所有参数一次性扔进 tuner：

| 参数 | 候选集合 |
|---|---|
| \(\lambda_{\mathrm{sparse}}\) | 标准化后的对数尺度候选值 |
| \(c_{\mathrm{UCB}}\) | \(\{0.5,1,2\}\) |
| \(\rho\) | \(\{0.05,0.1,0.2,0.4\}\) |
| FOS order | random / ascending size |
| donor strategy | random-compatible / exhaustive-compatible |
| graph update interval | 1 / 2 / 4 generations |
| \(N\) | 先固定；扩展实验再测 4 / 8 / 12 |

\(K\in\{1,2,3\}\) 是在线动作集合，不是另一个静态 \(p_m\) 参数。统计门禁 \(\alpha,\delta_{\min}\) 不进入 irace 的性能优化空间。

### 5.3 调参数据隔离

1. **Train tasks / synthetic landscapes：** 用于搜索参数配置；
2. **Validation tasks：** 选择稳健配置、检查参数敏感性；
3. **Held-out test task families：** 只运行最终冻结算法，不再调参。

所有对照算法也必须获得相同级别的调参预算。不能用调优过的 proposed method 对比默认参数的 baseline。

初始建议把总开发 rollout 预算的 10–15% 作为离线配置上限，后续依据真实任务成本调整；这只是预算规划起点，不是文献规定。最终论文必须报告调参预算，且将其计入总成本。

### 5.4 调参目标

在硬约束零违规且 rollout 预算固定的前提下：
- 主目标：训练任务上的平均任务成功率；
- 选择时：在与最好配置统计上相近的候选中，优先选择跨任务波动较小、成本较低者；
- 另报告最差任务组表现、成功率下界和成本分布。

不能只挑单个 seed 或单个任务上最高分的参数。

---

## 6. 预实验的参数敏感性与消融

至少比较四种模式：

| 组别 | 离线调参 | 在线参数控制 | 目的 |
|---|---|---|---|
| A | 默认参数 | 固定算子概率 | 最基础基线 |
| B | irace | 固定算子概率 | 仅离线调参的效果 |
| C | 默认参数 | discounted-UCB/AOS | 仅在线控制的效果 |
| D | irace | discounted-UCB/AOS | 完整方案 |

另外比较：
- fixed \(N\) vs IMS vs P3；
- 固定 \(K=1\) vs \(K\in\{1,2,3\}\) 自适应；
- random FOS order vs ascending-size；
- random-compatible donor vs exhaustive-compatible donor；
- raw offspring score reward vs paired-LCB-per-cost reward；
- 不使用 interaction graph vs learned graph vs oracle graph。

所有组固定总 rollout/FE 预算，另报 tokens、wall-clock 和 API cost。

### 6.1 停止规则

- 如果在线控制不优于“离线调参后的固定策略”，则删除在线控制，保留简单固定策略；不宣称参数自适应创新。
- 如果 IMS/P3 在同预算下没有收益，则保留固定种群，不强行追求 parameterless。
- 如果 interaction graph 不优于 GOMEA/CGOMEA 的 population-learned linkage，则重新审查交互估计是否真的提供了额外信息。
- 如果自适应控制只通过更多 rollout 获益，则判为预算不公平，不接受结论。
- 如果 UCB/AOS 贡献与已有 EvoMAS 的 adaptive strategy selection 无法区分，则只作为工程控制，不单独写创新点。

---

## 7. 伪代码：参数控制版 Interaction-Guided Constrained GOM

1. 在训练任务上离线配置 \(\lambda_{\mathrm{sparse}},c,\rho\)、FOS 顺序和 donor 策略；
2. 初始化种群 \(P\)，初始化算子收益表 \(\bar R_a,n_a\)；
3. 使用 Paper 1 的交互估计器建立初始 linkage graph；
4. 每批评价后更新交互估计及置信度，生成 singleton + credible positive-pair FOS；
5. 对每个父代：
   - 根据 discounted-UCB 选择动作 \(a\)；
   - 按动作执行 1/2/3 槽位变异或 linkage-block mixing；
   - 检查类型、接口和依赖；执行确定性最小修复，不能合法修复则拒绝；
   - 在相同任务块上对父代/子代做配对评价；
   - 若置信下界支持改进则接受；若不确定则继续评价至预算/序贯停止边界；
   - 计算 \(R_{a,t}\)，更新算子收益表；
6. 记录种群多样性、停滞、repair rate、operator usage、accepted offspring、rollout cost；
7. 达到总评价预算停止，返回最优配置及其置信区间。

---

## 8. 最终判断

**演化计算调参方案已经确定为：**

- 离线：irace 对少量算法结构参数进行训练集配置；
- 在线：discounted-UCB/AOS 调整变异强度和算子选择；
- 统计层：置信门槛和最小实际改进幅度预先锁定；
- 种群规模：先固定，随后比较 IMS/P3，不把 parameterless 当作创新；
- 第一版不使用 DE 的 \(F,CR\)，因为主算法是 categorical GOM。

这套方案可以解释“初始参数怎么定、搜索中参数怎么变、如何防止 test leakage、如何证明自适应真的有用”。它是本课题的研究设计决策，仍需通过同预算实验验证。

## 9. 下一步

1. 在 12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md 中落实该参数策略；
2. 生成合成 landscapes，检验 \(\lambda_{\mathrm{sparse}}\)、\(\tau_{\mathrm{edge}}\)、\(K\)、UCB 参数的敏感性；
3. 先跑 A/B/C/D 四组参数控制消融；
4. 若在线自适应无显著收益，删掉它，不为“自适应”这个词保留复杂度；
5. 只有 Phase 0 通过后才进入真实 Agent rollout。


## 10. 参数控制与 CI-GOM V1 的对接（2026-11-02）

正式动作集合见 14_FORMAL_ALGORITHM_DESIGN_V1.md：
- \(a_1\)：singleton mixing；
- \(a_2\)：2-locus random mixing；
- \(a_3\)：3-locus random mixing；
- \(a_4\)：learned interaction block + uniform feasible donor；
- \(a_5\)：learned interaction block + posterior-aware donor。

每个 proposal 只选择一个 action，避免一次 offspring 同时经过多个算子后无法做信用分配。若当前没有可识别的 pair edge，\(a_4,a_5\) 暂不可用。reward 使用配对改进 LCB 减去 \(\delta_{\min}\)，再按 rollout-equivalent 成本归一化；非法 repair、无 donor 等情况按预先定义的负反馈记录。

重要修正：FOS 建边依据是可信非加性强度的绝对值，不是只看正交互。正/负符号进入 donor score；负交互不能直接作为硬拒绝条件。


## 11. CI-GOM V1 的动作归因与多重序贯检验补充（2026-11-02）

CI-GOM 每个 target 可执行多个 proposal，每个 proposal 只归因给一个 operator arm；每次提案有独立 proposal index。为避免“每个 proposal 各自用 alpha=0.05”导致跨提案累计误接受，14_FORMAL_ALGORITHM_DESIGN_V1.md 已采用两层 alpha spending：
\[
\alpha_k=\frac{6\alpha_{\mathrm{total}}}{\pi^2 k^2},\quad
\alpha_{k,n}=\frac{6\alpha_k}{\pi^2 n^2}.
\]
第一层控制跨 offspring proposals，第二层控制单个 proposal 内反复查看。该结论要求 task-block differences 有界，且 task blocks 独立或满足对应 martingale 条件。统计门槛不能交给 irace 调优。
