# 12 — 两个核心创新候选的算法定义与最小预实验

**日期：** 2026-11-02  
**状态：** METHOD SPECIFICATION DRAFT / PRE-EXPERIMENT REQUIRED  
**依赖：** 11_INNOVATION_FEASIBILITY_AUDIT.md

---

## 1. 研究总问题与题目

工作题目：**《面向大语言模型智能体的交互感知演化优化方法研究》**

总问题：在可执行 Agent 由多个有类型、存在接口/调用依赖的模块组成，且任务执行存在随机性、完整评价昂贵的条件下，如何学习可用于演化计算的组件交互结构，并利用它改进 Agent 配置搜索？

本轮决定以两个核心方法候选推进：
1. 预算受限的任务条件化 Agent 组件交互链路学习；
2. 交互链路驱动的约束最优混合演化。

跨任务迁移仍为储备方向。

## 2. 统一问题定义

设 Agent 有 \(m\) 个功能槽位。第 \(i\) 个槽位的候选实现集合为 \(\mathcal C_i\)，配置为：

\[
x=(x_1,\ldots,x_m),\qquad x_i\in\mathcal C_i.
\]

不是所有组合都可执行，因此合法配置集合为：

\[
\mathcal X_{\mathrm{valid}}\subseteq\prod_{i=1}^{m}\mathcal C_i.
\]

合法性由类型、输入输出接口、控制流/数据流依赖和工具权限共同确定。

任务上下文 \(z\sim\mathcal D\)，执行随机性为 \(\omega\)，任务回报为：

\[
Y(x,z,\omega)\in[0,1].
\]

目标均值为：

\[
\mu(x,z)=\mathbb E_{\omega}[Y(x,z,\omega)].
\]

整体优化可写为最大化任务成功率，同时满足结构有效性、工具策略和资源上限等硬约束。第一阶段不把多目标 Pareto 本身作为创新点。

## 3. 创新候选一：预算受限的任务条件化交互链路学习

### 3.1 交互目标

对于两个槽位 \(i,j\)，在给定其他槽位配置 \(x_{-ij}\) 和任务上下文 \(z\) 时，定义离散交互对比：

\[
\Delta_{ij}(x_{-ij},z)=
\mu(x_i',x_j',x_{-ij},z)
-\mu(x_i',x_j,x_{-ij},z)
-\mu(x_i,x_j',x_{-ij},z)
+\mu(x_i,x_j,x_{-ij},z).
\]

其中 \(x_i,x_i'\) 和 \(x_j,x_j'\) 是两个槽位的不同实现。若某个四元组包含非法配置，则不能直接套用该差分式；需要在合法干预子空间内定义对比，或将其标记为不可识别。

### 3.2 候选统计模型

\[
\mu(x,z)=\beta_0(z)+\sum_i f_i(x_i,z)+
\sum_{i<j}g_{ij}(x_i,x_j,z).
\]

拟采用：
- 任务上下文条件化的主效应和交互项；
- 对交互项进行组稀疏/层级收缩，防止无约束 pairwise regression 过拟合；
- 仅在交叉验证和置信区间支持时保留交互项；
- 对不同任务家族采用共享参数 + 任务偏移，检验哪些交互可共享；
- 使用 task-blocked paired runs 或可控随机种子降低执行噪声；
- 对模型调用随机性不可控的设置，明确采用重复执行与分层 bootstrap，而不假装随机数完全配对。

注意：该模型本身不是创新。真正候选贡献是下面的主动探测策略、稀疏交互筛选和预算效率。

### 3.3 主动合法配置探测

每轮选择一个合法配置 \(x\in\mathcal X_{\mathrm{valid}}\)。候选 acquisition：

\[
A_t(x)=
\eta_t\,\mathrm{UCB}_{\mathrm{fitness}}(x)
+(1-\eta_t)\frac{\mathrm{IG}_{\mathrm{interaction}}(x)}{c(x)}.
\]

其中：
- \(\mathrm{UCB}_{\mathrm{fitness}}\)：兼顾当前优化；
- \(\mathrm{IG}_{\mathrm{interaction}}\)：该配置预计能降低多少交互参数/交互图的不确定性；
- \(c(x)\)：该配置的预计执行成本；
- \(\eta_t\)：控制探索与利用的权重。

具体 IG 形式需要在实现前确定，例如用后验协方差的加权 log-determinant reduction；不能只凭名称声称新颖。

输出交互图：
- 正向交互：候选协同 linkage；
- 负向交互：候选冲突 linkage；
- 估计不确定：不强制建边；
- 任务条件化交互：保留任务条件或局部图，不直接平均掉符号变化。

### 3.4 论文一的独立性要求

Paper 1 必须独立回答：在有限昂贵评价下，算法能否更准确、更稳定地识别影响 Agent 配置组合表现的交互结构？

它不能只为 Paper 2 生成一张图。必须独立比较：
- full factorial reference（小规模可行空间）；
- main-effects regression；
- pairwise OLS；
- sparse/hierarchical interaction regression；
- MESH-Harness additive full-covariance LinUCB；
- random design；
- fixed pairwise/fractional-factorial design；
- proposed active interaction design。

指标：
- interaction RMSE；
- sign F1 / top-k edge precision-recall；
- confidence interval coverage；
- held-out configuration prediction error；
- fixed evaluation budget 下的 best-so-far regret；
- 每识别一个有效 interaction 所需评价次数。

## 4. 创新候选二：交互链路驱动的约束最优混合演化

### 4.1 基因型

第一版使用固定槽位的 categorical genotype：

\[
x=(x_1,\ldots,x_m),\quad x_i\in\mathcal C_i.
\]

另存类型、接口、控制流/数据流依赖，不在第一版开放任意 DAG 或任意代码生成。

### 4.2 Linkage / FOS

由候选一估计的交互图生成 family of subsets (FOS)：
- 高置信正交互优先形成协同块；
- 高置信负交互不允许无条件组合，可作为 donor compatibility 条件；
- 不确定边暂不强制分组；
- 与 GOMEA Linkage Tree、CGOMEA、DSMGA-II、LK-GOMEA 做严格对照。

### 4.3 Constrained Optimal Mixing

对于父代 \(x\) 和 donor \(d\)，选取 linkage block \(B\)，构造：

\[
x'_B=d_B,\qquad x'_{-B}=x_{-B}.
\]

随后：
1. 检查类型和接口；
2. 检查调用依赖和硬约束；
3. 若可用最小 repair 恢复，则执行并记录 repair delta；
4. 若 repair 改动超过预设阈值，直接拒绝；
5. 对 parent/offspring 在同一任务块上进行配对评价；
6. 用序贯置信区间判断是否接受，避免单次随机高分导致误接受；
7. 更新 population、lineage 和 linkage 证据。

一个可测试的接受规则是：在满足硬约束后，只有当配对差值置信下界高于预设非劣阈值 \(-\delta\)，才允许作为非劣替换；若要求严格改进，则进一步要求置信下界大于 0。最终规则需根据评价噪声和统计功效预注册。

### 4.4 论文二的独立性要求

Paper 2 必须证明算子本身有效。实验至少要分别运行：
- oracle interaction graph + proposed operator；
- learned interaction graph + proposed operator；
- random graph + proposed operator；
- no linkage + standard GOM；
- GOMEA / CGOMEA / LK-GOMEA / DSMGA-II；
- AgentSquare / ARTEMIS / Hu-EvoMAS / AgentEvo / MESH-Harness 相关搜索基线。

若 oracle graph 有效但 learned graph 无效，瓶颈在论文一；若 oracle graph 也无效，论文二核心假设失败；若只有多 repair/多评价才提升，则不算算法增益。

## 5. 最小预实验设计

### Phase 0：合成真值 Agent landscape

- 4 个槽位；
- 每个槽位 2 个可执行的抽象实现；
- 全空间 16 个配置；
- 构造已知主效应、正/负 pairwise interaction、少量任务条件化符号翻转，以及不同噪声水平；
- 记录真实交互图，测试估计器恢复能力；
- 比较全因子、主效应、pairwise OLS、稀疏交互和主动探测；
- 预算设为全因子预算的多个比例，比较精度—成本曲线。

### Phase 1：真实可执行 Agent

候选环境：
- ToolSandbox：有状态工具执行、隐式状态依赖和 on-policy user simulator；
- AppWorld：多应用、多 API、程序化终态检查；
- tau-bench：airline/retail API 交互与最终数据库状态检查。

建议先选一个环境和固定模型，使用 4 个功能槽位，例如 planning、tool routing、memory、verification/recovery；每槽位两个接口兼容实现，得到 16 个配置。先做 20–30 个任务、3 个执行种子的 pilot，再依据方差估算扩大规模。不能把 pilot 当最终显著性结论。

### Phase 2：演化对照

相同初始种群、相同任务划分、相同模型、相同执行次数和相同修复预算。报告 oracle graph 与 learned graph，避免把估计误差和算子效果混在一起。

## 6. GO / HOLD / NO-GO 门槛

### Paper 1
GO 条件：
- 合成真值中能稳定恢复稀疏交互；
- 在同等执行预算下，显著优于 additive surrogate、普通 pairwise regression 和固定设计；
- 对未执行配置的预测更准确；
- 置信区间/不确定性校准可靠。

若 pairwise interaction 在真实 Agent 任务中没有稳定预测增益，或主动探测不优于固定设计，则 NO-GO。

### Paper 2
GO 条件：
- oracle linkage 下 constrained mixing 优于 standard GOM/random crossover；
- learned linkage 下仍有端到端收益；
- repair 率、评价次数和模型调用成本可控；
- 增益在 held-out task family 上保持。

若只是套用 GOMEA，或只靠更多评价/repair 获益，则 NO-GO。

### Paper 3
目前不做。只有前两项通过且观测到可迁移的跨任务 linkage 规律后再重启。

## 7. 当前结论

- 工程实现：两个核心候选均可做最小原型；
- 学术新颖性：均为 HOLD，尚不能正式确认；
- 最终毕业论文结构：先按 2 个核心创新推进，第三个方向保留；
- 当前下一步：完成 Phase 0 的数学地形与算法伪代码，再决定是否启动真实 Agent 试验。
