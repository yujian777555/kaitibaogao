# 14 — 两个核心算法的形式化设计 V1

**日期：** 2026-11-02  
**状态：** FORMAL ALGORITHM SPECIFICATION / NOT YET EMPIRICALLY VALIDATED  
**唯一研究仓库：** yujian777555/kaitibaogao  
**依赖：** 11_INNOVATION_FEASIBILITY_AUDIT.md、12_ALGORITHM_DESIGN_AND_MINIMUM_PILOT.md、13_EC_PARAMETER_CONTROL_PLAN.md

> 本文把两个候选算法从概念草案推进到可实现的数学规格。所有阈值和默认值仍是实验假设；未运行实验前，不得写成已验证创新。

---

## 0. 本轮重要修正

旧草案把“正交互”用于建立 linkage block，把“负交互”主要作为 donor 软过滤信号。这一规则不够严谨。

**Linkage 表示变量之间存在非加性依赖，不等于它们的交互必须为正。** 强负交互同样可能意味着两个模块必须联合考虑：如果独立替换其中一个模块会破坏原有组合，保留它们的依赖结构仍然重要。

因此 V1 修正为：
- **建边依据：** 交互效应绝对值是否可信地超过实际意义阈值，即 \(P(|\Delta_{ij}|>\delta_{\mathrm{link}}\mid D)\)，正、负交互均可形成 linkage；
- **符号用途：** 正/负符号用于解释和 donor compatibility scoring，不直接决定是否建边；
- **硬约束：** 类型、接口、权限、控制流/数据流依赖才是硬约束；
- **性能拮抗：** 负交互不是非法组合，不能仅因负号就禁止组合。

这是对之前“只用正交互形成 FOS”的正式纠正。

## 1. 统一问题定义

### 1.1 Agent 配置与合法空间

Agent 有 \(m\) 个固定功能槽位。第 \(i\) 个槽位的候选模块集合为 \(\mathcal C_i\)。配置为：

\[
x=(x_1,\ldots,x_m),\quad x_i\in\mathcal C_i.
\]

每个模块带有声明式 contract：
- 输入/输出类型；
- 前置条件和后置条件；
- 能力与权限；
- 资源需求；
- 对其他槽位的调用或数据依赖。

由 contract checker 定义合法空间：

\[
\mathcal X_{\mathrm{valid}}
=\{x\in\prod_i\mathcal C_i:H(x)=1\}.
\]

第一版只做固定槽位 categorical genotype，不做任意 DAG 搜索、自由代码生成或任意拓扑演化。

### 1.2 任务与随机执行

任务 \(t\) 有可观察上下文 \(z_t\)，Agent 在初态/执行随机性下产生归一化回报：

\[
Y(x,t,r)\in[0,1],\qquad
\mu(x,z)=\mathbb E[Y\mid x,z].
\]

\(r\) 表示执行重复或随机种子。只有在模型和环境支持可复现随机种子时才使用 common random numbers；否则以同任务、同初态、task-blocked repeated runs 配对，不能声称实现了严格 seed pairing。

Paper 1 的目标是估计可用于搜索的任务条件化交互结构；Paper 2 的目标是在合法配置空间内最大化目标任务分布上的期望回报，同时满足所有硬约束和固定评价预算。

---

# PART A — Paper 1：任务条件化主动交互结构学习

## 2. 算法目标与工作名称

工作代号：**TCAIL（Task-Conditioned Active Interaction Learning）**。

独立科学问题：

> 在模块组合评价昂贵、Agent rollout 有随机噪声、合法配置并非完整笛卡尔积时，如何主动选择下一批合法配置，识别具有统计可信度的任务条件化非加性交互结构，并对不可识别的交互明确 abstain？

TCAIL 不负责寻找最终最优 Agent。它的独立输出是：
1. 主效应与 pairwise interaction surrogate；
2. 每个任务上下文下的 interaction graph；
3. 每条边的强度、方向、后验不确定性和可识别状态；
4. 对当前证据不足的边明确 abstain；
5. 给出在固定评价预算下的交互恢复与预测性能。

## 3. 类别模块的效应编码

对槽位 \(i\)，令 \(k_i=|\mathcal C_i|\)。构造正交对比编码：

\[
h_i(x_i)\in\mathbb R^{k_i-1}.
\]

二元槽位可取 \(x_i\in\{-1,+1\}\)，多类别槽位使用正交 contrast coding。任务上下文编码为低维特征：

\[
\psi(z)=[1,\text{task-family indicators},\text{standardized observable context}].
\]

不能把测试任务 ID、答案、金标或事后轨迹信息作为部署前不可观察的上下文特征。

构造特征：

\[
\phi(x,z)=
\left[
\psi(z),
\{h_i(x_i)\otimes\psi(z)\}_{i=1}^m,
\{(h_i(x_i)\otimes h_j(x_j))\otimes\psi(z)\}_{i<j}
\right].
\]

模型：

\[
\mu(x,z)=
\beta_0^\top\psi(z)
+\sum_i h_i(x_i)^\top B_i\psi(z)
+\sum_{i<j}(h_i(x_i)\otimes h_j(x_j))^\top B_{ij}\psi(z).
\]

这里 \(B_i\) 是槽位主效应，\(B_{ij}\) 是任务条件化 pairwise interaction。该模型是 V1 的候选二阶模型；不宣称真实 Agent landscape 必然只有二阶交互。后续通过残差/留出预测检查模型失配，必要时 abstain 或另做高阶扩展。

## 4. 稀疏估计与不确定性

### 4.1 Group-ARD 层级收缩

对每个 pairwise interaction block 使用组级自动相关性确定（Group-ARD）先验：

\[
\operatorname{vec}(B_{ij})\sim
\mathcal N(0,\alpha_{ij}^{-1}I).
\]

主效应使用较宽的弱信息先验。通过边际似然/经验贝叶斯更新 \(\alpha_{ij}\)：缺乏数据支持的交互组被强收缩，数据支持的组保留较大后验方差和非零系数。

实现可使用迭代重加权贝叶斯线性回归；对有界连续分数先使用 Gaussian working likelihood。若真实任务采用 0/1 成功率，则使用 Bayesian logistic regression 的 Laplace posterior 或 beta-binomial 分层模型，并通过 task-level bootstrap 检验不确定性校准。不能把 Gaussian 工作模型的置信度未经校准地直接用于 Bernoulli 结果。

### 4.2 交互边的强度和方向

对给定任务上下文 \(z\)，从 \(B_{ij}\psi(z)\) 计算相应类别替换的 pairwise contrast。记候选对比为：

\[
\Delta_{ij}^{(a,b;c,d)}(z)
=
\mu(x_i=a,x_j=c,z)
-\mu(x_i=a,x_j=d,z)
-\mu(x_i=b,x_j=c,z)
+\mu(x_i=b,x_j=d,z),
\]

其他槽位固定在合法且相同的配置上下文中。二元 effect coding 下该 contrast 与相应交互系数仅差固定比例因子。

对多类别槽位，定义 pair strength 为所有可识别合法替换对比绝对值的最大值或预注册加权 RMS；第一版合成实验先用二元槽位，避免多类别聚合定义引入额外自由度。

后验边置信度：

\[
q_{ij}(z)=P(|\Delta_{ij}(z)|>\delta_{\mathrm{link}}\mid D).
\]

方向概率：

\[
q^+_{ij}(z)=P(\Delta_{ij}(z)>\delta_{\mathrm{link}}\mid D),
\quad
q^-_{ij}(z)=P(\Delta_{ij}(z)<-\delta_{\mathrm{link}}\mid D).
\]

- 若 \(q_{ij}(z)\ge\tau_{\mathrm{edge}}\)，且通过可识别性门禁，则保留 linkage edge；
- 若 \(q^+\) 高，标记为可信正交互；
- 若 \(q^-\) 高，标记为可信负交互；
- 若两者都不高，标记为不确定，不建强制边；
- 若不可识别，标记 **NOT_IDENTIFIABLE**，不能用模型先验填补成“已发现交互”。

\(\delta_{\mathrm{link}}\) 是实际意义阈值，不是零效应检验阈值；\(\tau_{\mathrm{edge}}\) 必须通过合成 null/alternative 校准和多重比较控制预先确定。

## 5. 合法空间下的可识别性门禁

这是 TCAIL 的关键安全阀。

对每个 pair \(i,j\)，令 \(Z_{ij}\) 为该 pair 的交互特征设计矩阵，\(X_{-ij}\) 为截距、任务上下文、主效应及其他 nuisance features。加权残差投影：

\[
M_{-ij}=I-X_{-ij}(X_{-ij}^{\top}WX_{-ij})^{\dagger}X_{-ij}^{\top}W.
\]

定义：

\[
G_{ij}=Z_{ij}^{\top}W M_{-ij}Z_{ij}.
\]

只有当 \(G_{ij}\) 的有效秩足够、最小非零特征值高于预设数值门槛、且有足够独立任务块支持时，才允许对该交互作强结论。若约束导致某些组合永远不合法，导致四格对比无法识别，则输出 **NOT_IDENTIFIABLE**，不伪造反事实。

对二元模块，若要作直接四格差分解释，四种模块组合必须在同一任务上下文和相同其他槽位条件下均合法并有观测支持。若不满足，只能在额外模型假设下做预测，不能宣称设计上识别了纯交互效应。

## 6. 主动合法配置采样

### 6.1 候选集

- 小空间：枚举 \(\mathcal X_{\mathrm{valid}}\)；
- 大空间：通过 contract-aware backtracking / constraint solver 生成合法候选池；
- 禁止先随机生成非法配置再把它们计为有效样本；
- 对候选任务上下文保持 task-family 平衡，避免 acquisition 只集中在单一任务类型。

### 6.2 Posterior information gain

令完整参数后验为：

\[
\theta\mid D_t\approx\mathcal N(m_t,\Sigma_t).
\]

\(P_I\) 是抽取所有 interaction 参数的选择矩阵，交互参数边际协方差为：

\[
\Sigma_{I,t}=P_I\Sigma_tP_I^\top.
\]

对候选合法配置及任务上下文 \((x,z)\)，特征向量为 \(\phi=\phi(x,z)\)，预测观测噪声方差为 \(v(x,z)\)。单次观测后的协方差更新：

\[
\Sigma_t^+
=
\Sigma_t-
\frac{\Sigma_t\phi\phi^\top\Sigma_t}
{v(x,z)+\phi^\top\Sigma_t\phi}.
\]

\[
\Sigma_{I,t}^+=P_I\Sigma_t^+P_I^\top.
\]

定义 interaction-only 信息增益：

\[
IG_I(x,z)=\frac12
\log\frac{\det(\Sigma_{I,t}+\epsilon I)}
{\det(\Sigma_{I,t}^++\epsilon I)}.
\]

采样 acquisition：

\[
A_t(x,z)=\frac{IG_I(x,z)}{\widehat c(x,z)}.
\]

\(\widehat c\) 是预估 rollout 成本。第一版不混入 fitness UCB，避免把“发现交互”与“直接找高分配置”两个目标混在一起。若后续需要联合目标，必须作为独立消融。

批量采样时采用 greedy batch selection，并加入任务家族覆盖/候选去重；每次真实评价后重新拟合 posterior，而不是一次性按初始分数选完所有样本。

### 6.3 噪声处理

- 有可控共同随机数时，同一 task/seed 对配置进行配对；
- 无法控制 LLM seed 时，对同一任务初态做 task-blocked repeated runs；
- 以任务实例/任务簇为独立统计单位，不把同一任务上的多个高度相关 rollout 当作完全独立样本；
- 每轮记录均值、方差、失败率、任务 family、初态、模型版本和评价成本；
- 对模型置信度用 held-out task-block bootstrap 或模拟覆盖率校准。

## 7. TCAIL 伪代码

~~~text
Algorithm 1: TCAIL
Input:
    slot domains C_1...C_m
    contract constraints H
    training task contexts Z_train
    rollout budget B
    initial design budget B0
    edge threshold delta_link, tau_edge
Output:
    task-conditioned interaction graphs G(z)
    posterior surrogate p(theta | D)
    identifiability report

1. X_valid <- EnumerateOrGenerateLegalConfigurations(C, H)
2. D <- SelectStratifiedInitialDesign(X_valid, Z_train, B0)
3. Y <- EvaluateTaskBlocked(D)
4. while Cost(Y) < B:
5.     FitGroupARDPosterior(D, Y)
6.     EstimateNoiseAndCalibratePosterior(D, Y)
7.     for each pair (i,j):
8.         test rank / eigenvalue / support of residualized interaction design
9.         if gate fails: mark (i,j) NOT_IDENTIFIABLE
10.        else estimate q_ij(z), qplus_ij(z), qminus_ij(z)
11.    if candidate model fails held-out residual / calibration checks:
12.        mark affected interactions ABSTAIN; do not force an edge
13.    for each legal candidate x and balanced task context z:
14.        compute posterior covariance update Sigma_plus
15.        compute IG_I(x,z) / expected_cost(x,z)
16.    select a diverse legal batch with highest acquisition
17.    evaluate selected configurations using paired/task-blocked protocol
18.    append observations to D, Y
19. return posterior, G(z), edge directions, confidence and abstentions
~~~

## 8. TCAIL 的独立实验

基线：
1. full factorial（小空间 oracle）；
2. random legal design；
3. fixed fractional-factorial / D-optimal design；
4. main-effects regression；
5. pairwise OLS；
6. sparse pairwise regression with fixed design；
7. MESH-Harness additive full-covariance surrogate；
8. TCAIL active Group-ARD。

指标：
- interaction contrast RMSE；
- edge AUPRC / precision / recall / F1；
- 正负方向识别准确率；
- posterior interval coverage；
- held-out configuration-task prediction error；
- 固定预算下识别出的真实边数量；
- 达到给定 edge-recovery accuracy 所需 rollout 数。

Paper 1 的 GO 条件不是“拟合结果看起来合理”，而是在相同评价预算下，TCAIL 对真实非零交互的恢复、校准或预测有可重复优势。若只比随机采样好、却不比 D-optimal/fractional design、sparse regression 或 MESH 强，则不 GO。

---

# PART B — Paper 2：交互感知的 Agent 约束最优混合演化

## 9. 算法目标与工作名称

工作代号：**CI-GOM（Contract-aware Interaction-guided Gene-pool Optimal Mixing）**。

独立科学问题：

> 当 Agent 个体由有类型、存在调用依赖的离散模块构成，适应度由随机 rollout 估计时，如何把任务条件化交互结构转化为合法的 linkage mixing，并避免修复破坏、错误 donor 和噪声接受造成的搜索退化？

CI-GOM 不能只是“把 TCAIL 的图交给 GOMEA”。它必须单独验证：
- 交互 FOS 是否比随机/传统 linkage 更适合 Agent 模块；
- contract-aware repair 是否能减少无效后代且不静默改变无关基因；
- confidence-aware donor selection 是否改善有效重组；
- noisy sequential acceptance 是否降低误接受；
- 同预算端到端性能是否优于标准 GOM 和 Agent crossover。

## 10. 交互 FOS：以非加性依赖而非交互正负决定 linkage

对当前任务上下文 \(z\) 和当前搜索区域，使用 TCAIL 后验：

\[
q_{ij}(z)=P(|\Delta_{ij}(z)|>\delta_{\mathrm{link}}\mid D).
\]

构造第一版 pairwise FOS：

\[
\mathcal F(z)=
\{\{i\}:i=1,\ldots,m\}
\cup
\{\{i,j\}:q_{ij}(z)\ge\tau_{\mathrm{edge}},
\ (i,j)\text{ identifiable}\}.
\]

说明：
- singleton 保证每个槽位仍可独立变化；
- 正交互和负交互均可能形成 pair block；
- 不确定边不强制合并；
- 第一版最大块大小为 2，避免小样本下把连通分量全部合并；
- 后续只有在高阶交互真值实验支持时才扩展三元块；
- 若任务上下文不可用，使用预先定义目标任务分布上的加权图，并明确这是 pooled graph，不得伪称任务条件化。

## 11. Contract-aware mixing 与最小修复

### 11.1 依赖闭包

令 \(B\in\mathcal F(z)\) 为待混合 block，父代为 \(x\)，donor 为 \(d\)。先构造原始混合：

\[
\tilde x_i=
\begin{cases}
d_i,&i\in B\\
x_i,&i\notin B.
\end{cases}
\]

根据模块输入输出、前后置条件和依赖图，求受影响依赖闭包 \(C(B,x,d)\)。修复只能在该闭包内改变模块，不得静默修改闭包之外的无关基因。

### 11.2 确定性最小修复

定义 repair：

\[
x^\star=
\arg\min_{u}
\left(
d_H(u,\tilde x),
\operatorname{RepairCost}(u,\tilde x),
\operatorname{Lex}(u)
\right)
\]

subject to：
- \(H(u)=1\)；
- 对所有 \(k\notin C(B,x,d)\)，\(u_k=\tilde x_k\)；
- \(u\) 满足权限、类型、接口和调用依赖约束。

按上述字典序确定唯一修复结果，保证可复现。若不存在解、超出 \(r_{\max}\) 个额外修改、或修改超出依赖闭包，则拒绝该 proposal。记录：
- 原始 block \(B\)；
- dependency closure；
- 实际变化集合 \(B_{\mathrm{eff}}=\{i:x_i^\star\ne x_i\}\)；
- repair count、repair distance、失败原因。

修复不是 LLM 自由改写，不允许在没有声明式规则的情况下自动猜测接口。

## 12. Donor compatibility：用后验预测差而不是简单看边符号

对当前 parent \(x\)、block \(B\) 和可行 donor \(d\)，修复得到 \(x^\star_d\)。利用 TCAIL surrogate 计算预测差：

\[
\widehat{\Delta}_d
=\widehat\mu(x^\star_d,z)-\widehat\mu(x,z),
\qquad
s_d^2=\operatorname{Var}(\Delta_d\mid D).
\]

定义保守 donor score：

\[
S(d\mid x,B,z)=
\widehat{\Delta}_d-\kappa_d s_d-\lambda_r R_d,
\]

其中 \(R_d\) 是 repair distance/cost。只在硬约束可行 donor 集合中选择。采用带探索地板的 softmax：

\[
P(d\mid x,B,z)
=
\frac{\epsilon_{\mathrm{donor}}}{|\mathcal D_{\mathrm{valid}}|}
+(1-\epsilon_{\mathrm{donor}})
\frac{\exp(S_d/T)}
{\sum_{d'\in\mathcal D_{\mathrm{valid}}}\exp(S_{d'}/T)}.
\]

这样：
- 负交互不被机械地视为禁配；
- 如果某个 donor 与当前背景组合的后验预测确实较差，其分数自然下降；
- 保留 \(\epsilon_{\mathrm{donor}}\) 探索，防止 surrogate 错误导致永久排除；
- 若 surrogate 不确定，\(\kappa_d\) 会保守惩罚高不确定候选；必须通过消融验证其是否优于随机 donor。

## 13. Noisy sequential acceptance

对 parent \(x\) 与 offspring \(x'\) 在相同任务块上做配对评价。每个独立任务块得到：

\[
d_s=Y(x',t_s)-Y(x,t_s)\in[-1,1].
\]

如果无法控制相同随机 seed，则 \(d_s\) 是同一任务/初态下两组重复运行的 task-blocked difference，不宣称是完全共享随机数。

使用 anytime-valid Hoeffding confidence sequence 的简单实现。令：

\[
\alpha_n=\frac{6\alpha}{\pi^2n^2},\quad
\bar d_n=\frac1n\sum_{s=1}^n d_s,\quad
r_n=\sqrt{\frac{2\ln(2/\alpha_n)}{n}}.
\]

\[
LCB_n=\bar d_n-r_n,\qquad UCB_n=\bar d_n+r_n.
\]

在独立任务块、有界差值的假设下，\(\sum_n\alpha_n=\alpha\)，通过 union bound 控制反复查看造成的错误率。若同一任务的多个 rollout 相关，先聚合成 task-level block，再将独立任务/任务簇作为统计单位。

决策：
- 若 \(LCB_n>\delta_{\min}\)：接受 offspring；
- 若 \(UCB_n\le\delta_{\min}\)：拒绝 offspring；
- 否则继续评价，直至最大任务块数 \(n_{\max}\) 或总预算用尽；
- 到达上限仍不确定：保守拒绝，记录 **UNRESOLVED**。

\(\alpha\)、\(\delta_{\min}\)、\(n_{\max}\) 在训练/验证阶段确定并在测试前冻结。结构、安全和权限硬约束在评价前检查，不能通过 fitness trade-off 放宽。

## 14. 在线参数控制：只调节动作选择，不让所有参数同时漂移

### 14.1 动作集合

每个 proposal 只选择一个动作，以便将结果归因到对应算子：

| Arm | 动作 |
|---|---|
| \(a_1\) | 单槽位 donor mutation / singleton mixing |
| \(a_2\) | 随机 2 槽位 mixing |
| \(a_3\) | 随机 3 槽位 mixing |
| \(a_4\) | learned interaction block mixing + uniform feasible donor |
| \(a_5\) | learned interaction block mixing + posterior-aware donor |

若当前没有可信 pair edge，则 \(a_4,a_5\) 暂不可用。不得为了让该 arm 被选中而强制添加不确定边。

### 14.2 Discounted-UCB

每个 arm 维护折扣收益 \(\bar R_a\) 和有效计数 \(n_a\)。完成一次 proposal 后，用配对改进的保守下界和 rollout 成本计算 bounded reward：

\[
R_{a,t}=
\operatorname{clip}
\left(
\frac{LCB_n-\delta_{\min}}{C_{\mathrm{rollout}}},
-1,1
\right).
\]

非法 proposal、repair 超限或无可行 donor 给予预先定义的负反馈并单独记录原因。更新：

\[
\bar R_a\leftarrow(1-\rho)\bar R_a+\rho R_{a,t},
\qquad
n_a\leftarrow(1-\rho)n_a+1.
\]

选择分数：

\[
UCB_a=
\bar R_a+
c\sqrt{\frac{\ln(1+\sum_b n_b)}{1+n_a}}.
\]

未试过的可用 arm 至少获得一次初始试验。\(c,\rho\) 由训练任务离线配置，在线只更新 arm 使用倾向。成本归一化第一版只用 rollout-equivalent；token、wall-clock、货币成本分别报告，不把不同单位任意相加。

**AOS/UCB 是已有参数控制思想，不是独立创新。** 只有当它在同预算下优于离线调参固定算子概率，才保留为 CI-GOM 的有效组件。

## 15. CI-GOM 伪代码

~~~text
Algorithm 2: CI-GOM
Input:
    legal genotype space X_valid and contract checker H
    initial legal population P, size N
    TCAIL posterior and task-conditioned interaction graph G(z)
    rollout budget B
    alpha, delta_min, n_max
Output:
    best legal Agent configuration x_best
    final population P and operator statistics

1. Initialize discounted-UCB statistics for available operator arms
2. for each generation while budget remains:
3.     for each target parent x in P:
4.         z <- current training/evaluation task context
5.         FOS <- singleton blocks + identifiable credible interaction pairs from G(z)
6.         choose one available proposal arm a using discounted-UCB
7.         choose block B according to arm a (singleton, random k-set, or learned pair)
8.         select donor d from P using uniform-compatible or posterior-aware rule
9.         construct raw mixed genotype x_tilde
10.        compute dependency closure C(B,x,d)
11.        x_child <- deterministic minimum repair within C
12.        if no feasible repair or repair exceeds r_max:
13.            reject proposal; assign invalid-proposal feedback to arm a; continue
14.        evaluate parent/child on paired task blocks
15.        update LCB/UCB confidence sequence after each task block
16.        if LCB > delta_min: accept child and replace target parent
17.        else if UCB <= delta_min: reject child
18.        else continue until n_max or budget; unresolved -> reject
19.        compute bounded conservative reward and update arm a
20.     if graph update interval reached:
21.         update TCAIL posterior/graph using only training observations
22.     record population diversity, valid-offspring rate, repair, accept rate,
           edge version, operator usage, rollout/token/time cost
23. return best legal configuration and complete audit trail
~~~

## 16. 两篇论文的独立性与实验拆分

### Paper 1 独立实验
只测试 TCAIL 的估计与采样：
- 不运行演化搜索；
- 使用已知真值 landscape；
- 比较 active vs random/fixed designs；
- 证明预算效率、交互恢复、预测和置信校准。

### Paper 2 独立实验
固定估计图来源，先做 oracle graph，再做 learned graph：
- oracle graph + CI-GOM：检验算子上限；
- learned graph + CI-GOM：检验端到端效果；
- random graph + CI-GOM：检验图内容是否有用；
- standard GOM / GOMEA / CGOMEA：检验是否只是套用传统 linkage；
- Agent crossover / mutation-only：检验是否只是普通 Agent 演化；
- 分别消融 contract repair、posterior donor、sequential acceptance、AOS。

若 oracle graph 都无效，停止 Paper 2 核心假设；若 oracle 有效但 learned 无效，先修 Paper 1；若 learned graph 只在增加 rollout/repair 后有效，则不接受算法增益。

## 17. 复杂度与评价预算

设参数维度为 \(d\)，候选合法配置数为 \(M=|\mathcal X_{\mathrm{valid}}|\)，交互参数维度为 \(d_I\)。

### TCAIL
- Group-ARD posterior 拟合：稠密实现约 \(O(d^3)\)（可利用分块/稀疏结构优化）；
- 单个观测的 rank-one covariance 更新：约 \(O(d^2)\)；
- 对所有候选评分：朴素约 \(O(Md^2)\)，可缓存特征和使用低秩更新；
- 16 配置的 Phase 0 空间可直接枚举；大空间需要约束候选生成器。

### CI-GOM
- 每个 proposal 扫描最多 \(N-1\) 个 donors；
- contract checking / repair 取决于受影响依赖闭包大小，第一版固定槽位空间可枚举闭包内合法赋值；
- 若每代对每个个体产生 \(L\) 个 proposal，donor 筛选粗略为 \(O(N^2L)\) 次轻量评分，实际 rollout 成本通常占主导；
- 所有方法按相同 rollout-equivalent 预算比较；缓存只有在配置、任务、初态、模型版本和评价协议完全相同时才允许复用。

## 18. Phase 0 合成真值测试的最低规格

第一阶段先用 \(m=4\)、每槽位 2 个实现，\(x_i\in\{-1,+1\}\)，每个任务家族有 16 个配置。构造：

\[
\begin{aligned}
\mu(x,z)=0.5
&+0.04x_1-0.03x_2+0.02x_3+0.01x_4\\
&+0.08x_1x_2-0.07x_2x_3
+0.06s(z)x_3x_4\\
&+0.025x_1x_2x_3,
\end{aligned}
\]

其中 \(s(z)=+1\) 表示任务家族 A，\(s(z)=-1\) 表示任务家族 B。该函数的总偏移绝对值不超过 0.34，因此 \(\mu\in[0.16,0.84]\)，无需 clipping 即合法。

真实结构：
- \(1\leftrightarrow2\)：共享正交互；
- \(2\leftrightarrow3\)：共享负交互；
- \(3\leftrightarrow4\)：任务家族 A/B 符号翻转；
- \(1,2,3\)：小幅三阶失配项，用于检查 pairwise 模型能否通过残差诊断而不是过度自信。

噪声至少两档：
- Bernoulli success \(Y\sim\operatorname{Bernoulli}(\mu)\)；
- bounded continuous reward \(Y\sim\operatorname{Beta}(\kappa\mu,\kappa(1-\mu))\)，例如 \(\kappa\in\{20,100\}\)。

分两种空间：
1. **全合法空间：** 16 个配置全部可行，用于验证真值恢复；
2. **受约束空间：** 人为设置某些模块组合不兼容，使特定 pair contrast 缺少必要四格，检验 TCAIL 是否正确输出 NOT_IDENTIFIABLE，CI-GOM 是否拒绝非法组合。

注意：三阶项不属于 V1 pairwise 模型的可恢复目标。正确行为是检测模型失配、扩大预测区间或 abstain，而不是声称成功恢复三阶交互。

---

## 19. 初步 GO / HOLD / NO-GO

| 项目 | 当前判断 | 下一步 Gate |
|---|---|---|
| TCAIL Group-ARD + active IG | HOLD | 合成真值下优于 fixed design / sparse regression / MESH additive |
| 可识别性 abstention | 必须实现 | 受约束空间不产生伪交互结论 |
| CI-GOM interaction FOS | HOLD | oracle graph 优于 standard GOM / random linkage |
| contract-aware minimal repair | 必须实现 | 不越出依赖闭包，确定性、可审计 |
| noisy sequential acceptance | HOLD | 同预算下减少误接受且不严重损失搜索效率 |
| discounted-UCB operator control | 可选组件 | D 组优于 B 组才保留 |
| 第三篇跨任务迁移 | 暂缓 | 前两项通过且迁移有独立证据后再开 |

## 20. 本轮最终结论

当前算法设计已经明确到可编写最小模拟器的程度：
- Paper 1：Group-ARD 任务条件化 surrogate + 合法配置可识别性门禁 + interaction-only posterior IG 主动采样；
- Paper 2：绝对交互强度构建 FOS + contract-aware deterministic minimal repair + posterior-aware donor + paired anytime-valid sequential acceptance；
- 参数控制：irace 离线调少量参数，discounted-UCB 在线选择动作；AOS 不单独算创新。

**仍未证明：** 这两个方法是否优于强基线、是否有足够学术新颖性、是否能在真实 Agent 环境中提高成功率。下一步必须实现并运行 Phase 0 合成实验，不能仅凭公式确认创新成立。
