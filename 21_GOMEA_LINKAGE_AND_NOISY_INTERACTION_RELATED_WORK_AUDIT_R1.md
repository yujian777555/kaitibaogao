# 21 — GOMEA Linkage、Fitness Interaction 与噪声场景相关工作补充审计 R1

**日期：** 2026-11-02  
**审计范围：** TCAIL 与 GOMEA linkage / fitness-based linkage learning / empirical linkage learning / noisy linkage detection 的接口和新颖性  
**性质：** 公开论文机制级补充审查；未运行代码或实验  
**状态：** LITERATURE AUDIT / DESIGN IMPLICATIONS / NOT A NOVELTY APPROVAL  
**唯一研究仓库：** yujian777555/kaitibaogao

---

## 1. 本轮最重要的结论

上一轮将“统计交互”与“演化计算 linkage”区分是必要的，但表述需要进一步精确：

**GOMEA linkage 并非只有一种定义。** 标准 Linkage Tree GOMEA 常通过种群中基因值的统计依赖（如 mutual information）学习 linkage；另一方面，已有 RV-GOMEA 工作直接通过目标函数有限差分学习 fitness-based linkage，并把它用于 linkage tree 或 conditional linkage model。

因此：
- 不能笼统地说“fitness interaction 与 GOMEA linkage 无关”；
- 也不能笼统地说“统计交互图就是 GOMEA linkage”；
- 对本项目而言，正确接口应明确采用哪种 linkage 定义、在哪个上下文下估计、如何构造 FOS，以及局部依赖变化时如何选择 donor/mixing mask。

更重要的是，**fitness-based linkage、conditional linkage、noise-aware decomposition 均已有直接先例**。TCAIL 不能把这些概念本身作为创新。

当前唯一值得保留的候选方向应收窄为：

> 面向随机、昂贵且任务异质的 Agent 模块配置优化，研究一种任务上下文与当前搜索位置双条件化的概率化 fitness-linkage 估计方法；通过 task-block 配对数据、后验不确定性和主动评价预算，学习当前个体适用的局部依赖图，并验证它是否能在同等 rollout 预算下减少错误 linkage、提高 FOS 质量和 Agent 搜索效率。

这仍是待证伪候选，不是已证实的研究空白或创新点。

---

## 2. 必须区分的四类 linkage / interaction 概念

### 2.1 Statistical Linkage Learning（SLL）

SLL 根据进化种群中基因值的联合分布估计变量依赖，常用 mutual information。它回答的是：

> 在当前种群/选择分布中，变量值是否统计相关？

它不等于目标函数在任意背景下的非可加交互。选择压力、种群分布、初始化偏差和搜索阶段都可能影响 MI。Olieman et al.（2021）明确讨论了连续 RV-GOMEA 中，选择后的种群可能因适应度等高线而产生伪相关，导致 MI 将原本可分解的变量误判为依赖。<https://doi.org/10.1109/TEVC.2020.3039698>

### 2.2 Fitness-Based Linkage Learning（FBL）

FBL 直接观察目标函数在变量扰动下的变化，判断一个变量的边际影响是否随另一个变量取值而改变。它回答的是：

> 对目标函数而言，这两个变量是否存在直接的非可加依赖？

Olieman et al.（2021）使用四点 fitness perturbation 构造 pairwise dependency strength，并据此学习 RV-GOMEA linkage tree。Andreadis et al.（GECCO 2024）进一步将 fitness-based dependency tests 与 conditional linkage model、maximum-clique 处理相结合，用于重叠依赖问题。

所以，本项目 14 号文件 PART B 中“以交互图作为 linkage 输入”的总体想法并非错误；但它已经处在 FBL / VIG / conditional GOMEA 的既有研究脉络中，不能作为独立创新。

### 2.3 Empirical / Conditional Linkage Learning（ELL / cDLED）

Przewozniczek et al.（GECCO 2021）的 DLED 在给定个体附近进行四点翻转比较，检测直接变量依赖；论文说明其依赖判定与相关 Walsh 系数非零有关。

Przewozniczek et al.（FOGA 2025）的 cDLED 将 DLED 用于多结构问题：不同个体可能对应不同局部子结构，因此需要按个体识别适用依赖，并限制不匹配个体之间的 mating。它已经直接覆盖“linkage 随当前解/局部结构变化”的问题。

因此，TCAIL 不能只把“全局任务条件化图”换成“每个 Agent 个体一张图”就宣称新颖；必须证明随机 rollout、任务上下文、预算约束和概率校准带来的具体方法增益。

### 2.4 Task-Conditioned Agent Fitness Interaction

本项目的统计对象是：
- 基因：Agent 离散模块槽位；
- 目标：固定版本 Agent 在指定任务块上的实际效用；
- 外部上下文：task-family 与部署前可观察任务特征；
- 内部上下文：当前 Agent 配置中除被检测模块外的其他槽位；
- 观测：随机 rollout，且同一 task instance 下不同配置的结果可能相关。

这比单纯 SLL 多了目标函数差分；比经典确定性 FBL 多了任务异质、随机 rollout、合法配置约束和高评价成本；比 cDLED 多了跨 task-family 的概率化估计与主动预算分配。

但这些差异只是候选研究切入点。必须与 FBL、cDLED、LMM、ALI 等公平比较后，才可判断是否存在独立贡献。

---

## 3. 关键先行工作及对 TCAIL 的影响

| 工作 | 已覆盖机制 | 对 TCAIL 的约束 |
|---|---|---|
| Olieman, Bouter & Bosman, 2021, *Fitness-based Linkage Learning in RV-GOMEA* | 四点 fitness difference、pairwise dependency strength、linkage tree | 不得宣称首次从 fitness difference 学习 linkage |
| Andreadis, Alderliesten & Bosman, GECCO 2024, *Fitness-based Linkage Learning and Maximum-Clique Conditional Linkage Modelling for Gray-box Optimization with RV-GOMEA* | 增量 DSM、fitness-based dependency test、conditional FOS、重叠依赖最大团 | 不得宣称首次将 fitness linkage 用于 conditional GOMEA |
| Przewozniczek et al., GECCO 2021, *Direct Linkage Discovery with Empirical Linkage Learning* | 个体局部四点扰动、直接依赖识别、降低 ELL 计算成本 | 局部四点依赖检测已有先例 |
| Przewozniczek et al., FOGA 2025, *Conditional Direct Empirical Linkage Discovery for Solving Multi-Structured Problems* | 个体条件化依赖、局部子结构、mating restriction | 必须处理当前搜索位置/局部结构，不得只给全局图 |
| Zhong, Zhang & Munetomo, 2023, *Cooperative Coevolutionary Differential Evolution with Linkage Measurement Minimization for Large-Scale Optimization Problems in Noisy Environments* | LMM；把分解当作组合优化，在噪声环境中搜索 linkage decomposition | “噪声下识别 linkage”不是空白 |
| Zhong, Tu, Zhang & Munetomo, 2024, *Cooperative Coevolutionary Differential Evolution with Adjacent Intensity Matrix with Linkage Identification for Large-Scale Optimization Problems in Noisy Environments* | ALI/AIM；利用相对交互强度与强度规律，在噪声下判别变量依赖 | 不得把“相对强度 + 抗噪阈值”包装成新机制 |
| Tinós et al., 2026, *Learning Variable Importance and Interaction in Genetic Algorithms for Pseudo-Boolean Optimization* | 从 GA 搜索过程副产物提取变量重要性和交互，无需额外 fitness evaluations，并用于 reproduction operators | 必须加入在线/副产物式交互学习强基线；额外 rollout 的成本必须有充分回报 |
| Dushatskiy et al., 2024, *Parameterless Gene-Pool Optimal Mixing Evolutionary Algorithms* | GOMEA、Linkage Tree、GOM、CGOM 和 conditional mating | 必须比较标准 LT-GOMEA/CGOMEA，而不是只与随机 crossover 比较 |
| Guijt et al., 2022, *Solving Multi-Structured Problems by Introducing Linkage Kernels into GOMEA* | 在个体局部邻域学习不同 linkage kernel | 任务条件化不能忽略已有 local/solution-conditioned linkage |

### 文献核验链接与关键证据

1. Olieman et al. 2021：CWI 全文和方法段落说明 SLL-MI 与 fitness-based perturbation 两类 linkage learning，并定义缩放 dependency strength。  
   https://ir.cwi.nl/pub/30301/30301.pdf

2. Andreadis et al. 2024：摘要说明将 fitness-based linkage learning 与 conditional linkage modelling 结合；正文定义 VIG、DSM 和 conditional FOS。  
   https://doi.org/10.1145/3638529.3654103  
   https://ir.cwi.nl/pub/34532/34532.pdf

3. Przewozniczek et al. 2021：DLED 在单个 binary genotype 上翻转两个变量并比较四个 fitness 值。  
   https://doi.org/10.1145/3449639.3459333

4. Przewozniczek et al. 2025：cDLED 通过 DLED 发现 individual-specific linkage，并在多结构问题中执行 mating restriction。  
   https://doi.org/10.1145/3729878.3746624  
   https://ir.cwi.nl/pub/35838/35838.pdf

5. Zhong et al. 2023：LMM 在乘性噪声下通过优化 linkage measurement function 进行变量分解。  
   https://doi.org/10.1007/s40747-022-00957-6

6. Zhong et al. 2024：ALI/AIM 利用相对强度规律和显著强度识别噪声下的依赖。  
   https://doi.org/10.1007/s12065-024-00941-8

7. Tinós et al. 2026：在线发表日期 2026-09-15，摘要说明从 GA 优化过程副产物估计 variable importance / interaction，并用于 reproduction operators。  
   https://doi.org/10.1162/EVCO.a.406

8. Dushatskiy et al. 2024：GOMEA/CGOMEA 的 linkage、optimal mixing 和 conditional mating。  
   https://doi.org/10.1162/evco_a_00338

9. Guijt et al. 2022：Linkage Kernels 用于 multi-structured problems。  
   https://doi.org/10.1145/3512290.3528828

---

## 4. B1 的修订方向：从“平均边”转向“局部条件化 fitness linkage”

### 4.1 目标函数尺度必须与 EA 实际优化目标一致

令 \(J(x,z)\) 为预先冻结的 Agent 目标效用，例如按固定规则归一化的任务成功率/效用。若统计模型采用 logit 或其他 link function，link function 仅用于建模；用于 linkage 判断的有限差分必须从每个 posterior draw 的 inverse-link prediction 还原到实际目标效用尺度。

理由：GOM 接受/拒绝 offspring 时优化的是实际 fitness/utility，而不是统计模型内部的 logit predictor。若只在 link scale 上定义非加性，得到的图未必对应 EA 实际优化的目标函数。

### 4.2 条件四格差分

对模块槽位 \(i,j\)，其余模块背景为 \(u=x_{-ij}\)，任务上下文为 \(z\)，定义：

\[
\Delta_{ij}(u,z)=
J(+1,+1,u,z)-J(+1,-1,u,z)
-J(-1,+1,u,z)+J(-1,-1,u,z).
\]

该量直接回答：在背景 \(u\) 和任务 \(z\) 下，改变模块 \(i\) 的效应是否依赖模块 \(j\)。

四格必须同时合法。若任何一格不合法或无可信支持，不得通过模型外推把它伪装成直接实验依赖。

### 4.3 两个不同层次：全局交互能量与局部 linkage

全局任务条件化强度可作为描述性汇总：

\[
S_{ij}(z)=
\sqrt{
\mathbb E_{u\sim\pi_{\rm ref}(\cdot\mid z,i,j)}
[\Delta_{ij}(u,z)^2]
}.
\]

其意义是目标背景分布下的 RMS interaction strength。它不会因不同背景的正负交互抵消而变成零。

但 **\(S_{ij}(z)\) 不应直接等同于某个当前个体的 FOS edge**。它描述的是目标背景分布上的总体依赖强度，不代表每个搜索位置都应执行同样的联合 mixing。

对当前 parent \(x\) 和任务上下文 \(z\)，真正用于局部 linkage 的候选量应是：

\[
q_{ij}(x,z)=
P\left(
|\Delta_{ij}(x_{-ij},z)|>\delta_{\rm local}
\mid D
\right).
\]

由 \(q_{ij}(x,z)\) 构造当前 parent 的 local weighted VIG。若局部四格支持不足，则标记 PENDING_LOCAL_SUPPORT / ABSTAIN，不得把它当作“无依赖”。

因此：
- \(S_{ij}(z)\)：全局 task-conditioned interaction energy，作为描述和预算优先级信息；
- \(q_{ij}(x,z)\)：当前 parent / task 下的局部 posterior linkage evidence；
- local weighted VIG：候选依赖图；
- FOS：由预先指定的 LT / conditional FOS 构造方法从图中得到，不能将 VIG 直接称为 FOS。

### 4.4 RMS 解决符号抵消的代数示例

若

\[
J(x)=a x_i x_j x_k,\qquad x_k\sim\{-1,+1\}
\]

则：

\[
\Delta_{ij}(x_k)=4a x_k.
\]

均匀背景下：

\[
\mathbb E[\Delta_{ij}(x_k)]=0,
\qquad
\sqrt{\mathbb E[\Delta_{ij}(x_k)^2]}=4|a|.
\]

因此平均有符号 contrast 会漏掉该条件依赖，而 RMS interaction energy 能识别其存在。

更一般地，在完整二元全因子空间上，对 Walsh 展开

\[
J(x,z)=\sum_{S\subseteq[m]}\beta_S(z)\prod_{k\in S}x_k
\]

有：

\[
\Delta_{ij}(u,z)
=4\sum_{S\supseteq\{i,j\}}
\beta_S(z)\prod_{k\in S\setminus\{i,j\}}u_k,
\]

且在其余槽位均匀独立时：

\[
S_{ij}(z)^2
=16\sum_{S\supseteq\{i,j\}}\beta_S(z)^2.
\]

这说明 RMS summary 捕获所有包含 \(i,j\) 的 Walsh interaction energy，而不只二阶系数。受约束或非均匀背景下，正交恒等式不再自动成立，但 RMS functional 本身仍有定义，必须按共同合法支持和冻结 reference distribution 解释。

### 4.5 该修改不代表新颖性成立

RMS conditional contrast 是一个合理的统计汇总，但不能只凭平方再求平均就宣称新颖。Fitness-based linkage、DLED 和 noisy linkage methods 已有直接先例。

候选创新只能落在以下可证伪的组合机制上：
- task-family-conditioned，而不是把所有任务池化成一张图；
- current-parent-conditioned，而不是只输出静态全局 linkage；
- task-block 配对和随机 rollout 后验，而不是确定性四点评估；
- 合法配置共同支持与 abstention；
- 主动预算用于确认最影响当前 FOS 的局部依赖；
- 在同等 rollout budget 下，优于 FBL / cDLED / LMM / ALI 和在线副产物式学习。

---

## 5. 对 TCAIL → GOMEA 的正确接口

本轮只确定接口原则，不启动 CI-GOM 实现。

1. TCAIL 不输出“已经完成的 GOMEA FOS”，而是输出当前 parent / task 的 local weighted VIG 及其 posterior uncertainty。
2. 用同一套预先冻结的 FOS builder 将各方法提供的 VIG/DSM 转换为 FOS，避免把“图估计器”与“聚类器”混为一个贡献。
3. FOS builder 至少包含：
   - standard linkage tree；
   - fitness-based linkage tree；
   - conditional / clique-based FOS。
4. Pairwise graph 不等于 pair-only FOS。若存在三阶或重叠依赖，必须检查 LT/conditional FOS 是否形成合适的联合 mixing subsets；不能仅加入 singleton 和 pair blocks 后声称完整捕获高阶结构。
5. 对每个 parent 使用局部图时，必须记录图版本、任务 anchor、支持状态、FOS、donor 规则和实际 mixing masks。
6. 如果局部图在不同 parent 间变化，不能用一张 pooled graph 替代所有局部图；这正是 cDLED / Linkage Kernels 已经强调的多结构问题。

---

## 6. 必须新增的强基线与消融

### 6.1 Linkage / decomposition 基线

1. Standard SLL-MI + Linkage Tree GOMEA；
2. Standard CGOMEA / conditional FOS；
3. Olieman et al. fitness-based linkage learning；
4. Andreadis et al. fitness-based conditional linkage / maximum-clique FOS；
5. DLED / cDLED（按随机任务评价协议做公平适配）；
6. LMM（Zhong et al. 2023）；
7. ALI/AIM（Zhong et al. 2024）；
8. Tinós et al. 2026 GA-side-effect interaction learning（可复现/适配后）；
9. Random linkage / random FOS；
10. Oracle local VIG / Oracle FOS。

所有适配都必须明确区分原论文算法与本项目实现变体，不能把自己改造后的 baseline 冒充原论文原始实现。

### 6.2 TCAIL 机制消融

- pooled task graph vs task-conditioned graph；
- global RMS summary only vs current-parent local \(q_{ij}(x,z)\)；
- local posterior graph vs point-estimate finite-difference threshold；
- posterior uncertainty / abstention on vs off；
- active design vs random / fixed fractional / D-optimal / ALI/LMM-style budget；
- local graph confirmation on vs off；
- objective-scale contrast vs link-scale contrast；
- local VIG to standard LT vs local VIG to conditional/clique FOS。

### 6.3 评价指标

统计层：
- local edge precision / recall / AUPRC；
- false-link rate / BFDR calibration；
- posterior coverage；
- task-family sign flip detection；
- context-dependent edge detection；
- abstention accuracy；
- rollout cost per confirmed local edge。

演化层：
- FOS structural similarity / VIG recovery；
- offspring acceptance and improvement rate；
- invalid / destructive mixing rate；
- 每个 FOS element 的有效改进率；
- 同等 rollout budget 下 best-so-far utility；
- across-task generalization and worst-family performance。

不能只报告 edge AUPRC；最终必须证明局部图让 GOM 更有效。

---

## 7. B1 修订的 GO / NO-GO 条件

B1 只有在以下证据出现后才可关闭：

1. 纯三阶符号翻转场景中，平均有符号边会失败，local conditional posterior / RMS summary 按设计恢复；
2. additive-only/null 场景不产生系统性 false linkage；
3. task-family sign flip 与同一任务内 background sign flip 能分别识别；
4. 受约束配置中，没有共同四格支持的局部边会正确 abstain；
5. local graph 在 FOS builder 之前具有可信的 posterior calibration；
6. 对同一 FOS builder，TCAIL local graph 相对 FBL/cDLED/ALI 等强基线，在同等 rollout budget 下有可重复收益；
7. 更关键：该收益能传递到 GOM search，而不仅是统计图指标。

如果只有全局 RMS 较准确，但 parent-specific FOS 仍不优于 cDLED / conditional FOS，则不能声称已经解决 linkage 学习问题。

---

## 8. 当前结论

- “交互统计量与 GOMEA linkage 完全不同”这一表述过于粗糙，需要按 SLL、FBL、ELL/cDLED 和任务条件化 Agent interaction 区分。
- 现有 TCAIL 的 reference-background 平均有符号 contrast 不适合作为通用 linkage edge 判据。
- 建议采用 objective-scale local finite difference 的 posterior linkage evidence；全局 RMS 仅作为任务条件化交互能量摘要，不直接替代 local FOS。
- Fitness-based linkage、conditional linkage、噪声下 linkage decomposition 均有强先例。
- TCAIL 仍有条件性候选空间：任务上下文 + 当前 parent + 随机 task-block + 合法支持 + posterior uncertainty + 主动预算的联合问题。
- 该候选尚未证明新颖，也尚未证明能提高演化搜索。

**本报告只补充 B1 的机制定义和相关工作，不代表 20 号报告的八项阻塞已全部解决。当前 TCAIL 仍 HOLD / IMPLEMENTATION BLOCKED。**
