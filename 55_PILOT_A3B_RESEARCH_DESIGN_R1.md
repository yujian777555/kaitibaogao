# 55-R1 — Pilot A-3b 研究设计（修订稿 R1）

**日期：** 2026-11-07  
**状态：** RESEARCH DESIGN R1 / 回应 56 号独立审查（B1–B6、M1–M5）/ **诊断实验已获授权、正式确认性实验仍未授权**  
**关系：** 55 号原草案**保留不覆盖**（历史记录）；本文件为当前唯一有效设计文本。56 号审查逐条回应见 §10。

---

## 0. 修订摘要

| 审查项 | 修正 |
|---|---|
| B1 R4 自相矛盾 | R4 不再要求零残留；改评 ContainmentSuccess + 可避免损害最小化；SafeResolution 只在 R1–R3 报告 |
| B2 R2 分母混淆 | R2 成功=**最终任务完成**；安全放弃改归 R3（SAFE_ABORT 子类）；CondRecSucc 只算 R1+R2 且以完成为准 |
| B3 可达性定义 | 冻结"观测历史 contingent policy + 信念态 AND-OR 鲁棒可达"语义（§3），UNKNOWN 兜底；标签由独立判定器生成 |
| B4 P(violation)=0 | 分层安全主张：设计层=类型化动作屏蔽+静态检查；实验层=zero **observed** violations + 置信上界（§5.4） |
| B5 成本惩罚正确行为 | 重复/可避免/不可避免残留三分；必要升级不惩罚；R4 只罚 excess harm（§5.3） |
| B6 配额与功效 | 明确 3:1 = (R1+R2):(R3+R4)；每 split 逐类计数表（§6.2）；cluster 级功效模拟（§6.3） |
| M1 归因混杂 | 全部方法共用同一初始候选池与同一 NSGA-II 骨干；初始化另做因子消融 |
| M2 预算口径 | 四类预算分列；先测 throughput；所有真实 episode 计入 |
| M3 主检验覆盖标准 EA | primary contrast = A+B vs NSGA-II（同骨干）；vs NSGA-III/GA/GP/手工 为 secondary；Holm 校正 |
| M4 目标冗余 | 分层目标向量（§5.2），不同类别不互相抵消 |
| M5 新颖性 | 主张限定为机制级差异（§9）；系统检索仍未完成，新颖性继续 NOT APPROVED |

---

## 1. 互斥可恢复性类别定义（替代 55 §4）

### 1.1 语义层（与打分层严格对应）

设场景族 \(\mathcal{F}\) 由任务、公开故障规格与**隐藏参数集** \(\Theta\) 构成；\(\theta \in \Theta\) 决定隐藏事实（补偿是否可用、真实提交时刻、延迟等）。执行由**观测历史 contingent policy** \(\pi: (o_1 a_1 \dots o_t) \mapsto a\) 控制——策略不得读取隐藏状态。

**鲁棒目标** \(\mathrm{Robust}_\pi(G) \equiv \forall \theta \in \Theta:\) 执行 \((\theta, \pi)\) 达到目标 \(G\)。

| 类别 | 互斥定义（按序判定，先满足者归类） |
|---|---|
| **R1 直接可完成** | \(\exists \pi:\ \mathrm{Robust}_\pi(\text{TASK\_COMPLETE}) \land \pi \text{ 的任何执行均不含 COMPENSATE/ROLLBACK 动作}\) |
| **R2 补偿后可完成** | R1 不成立，但 \(\exists \pi:\ \mathrm{Robust}_\pi(\text{TASK\_COMPLETE})\)（任何此类 \(\pi\) 必然使用补偿/回滚后**最终完成任务**） |
| **R3 可达零残留安全终态** | TASK\_COMPLETE 鲁棒不可达，但 \(\exists \pi:\ \mathrm{Robust}_\pi(\text{ZERO\_RESIDUAL\_TERMINAL})\)（安全停止 SAFE\_STOP、正确升级 ESCALATE、或补偿清零后放弃 SAFE\_ABORT） |
| **R4 仅可损害遏制** | 零残留安全终态鲁棒不可达；\(\exists \pi:\ \mathrm{Robust}_\pi(\text{CONTAINMENT})\)：不再新增禁止/不可逆副作用、触发升级或记录、可避免损害达到该场景的**最小可达值** |
| **UNKNOWN** | 有限 horizon/资源内无法证明任一上述判定；或目标仅对 \(\Theta\) 的真子集可达（非鲁棒可达且无法归入任何鲁棒类） |

**关键裁定（对应审查意见）：**
- R2 的**安全放弃不算恢复成功**：它属于 R3 的 SAFE_ABORT 子类；`ConditionalTaskCompletion` 在 R2 上只计"补偿后最终任务完成"。
- R3 的**正确升级计为成功**：CorrectEscalation-R3 要求零残留（R3 定义保证可达）。
- R4 **不要求零残留**：UnavoidableResidualBurden（不可避免残留）单独报告，不算策略损害。
- R4 **区分不可避免残留 vs 可避免损害**：可避免损害 = 实际损害 − 该场景最小可达损害（评估器计算基准）。
- UNKNOWN 不强制归类；实验按比例报告 UNKNOWN 率，超预注册阈值（默认 5%）触发分类器返工。

### 1.2 判定与打分的分离

- **判定器**（§3）只做可达性判定，产出类别与证书（策略存在性证据/不可达证据）。
- **打分器**（§5）按类别用不同成功标准评价被测策略。
- **禁止**：用被测算法的成败反向生成类别标签（判定器在算法运行前对场景独立标注并冻结）。

## 2. 场景与隐藏不确定性

- 场景 = (任务族, 故障组合族, 隐藏参数 \(\theta\), seed)。**同一场景族的 \(\Theta\) 中所有 θ 产生相同公开观测流**（直到动作后果分化），构成观测等价类。
- 判定器在**信念态**（=观测历史一致的隐藏状态集合）上做 AND-OR 搜索（§3），自然实现"同一公开观测对应多个隐藏状态时策略必须鲁棒"的要求。
- 延迟提交、lost-ACK、补偿失败、重复副作用均由隐藏参数表达（A-3 模拟器已有语义）。

## 3. 可恢复性判定器（可观察策略可达性，替代 55 §4 判定流程）

### 3.1 计算模型

- Episode 建模为有限转移系统 \((H, A, T, O, Z, G)\)：隐藏状态 \(h \in H\)、动作 \(a \in A\)、确定性转移 \(T\)、公开观测函数 \(Z(h)\)、目标谓词集 \(G \in \{\text{TASK\_COMPLETE}, \text{ZERO\_RESIDUAL}, \text{CONTAINMENT}\}\)。
- **信念态** \(B = \{h : Z(h) \text{ 一致于观测历史}\}\)。初始信念 \(B_0 = \Theta\)（场景族全部隐藏初态）。
- **AND-OR 搜索**：
  - **OR 节点**（策略选择）：对当前观测历史选一个动作 \(a \in A(o)\)（含类型化合法动作集）；
  - **AND 节点**（隐藏分支）：动作后每个 \(h \in B\) 各自演化；目标要求**所有**分支都达成（鲁棒）；
  - 节点合并：观测历史相同的分支合并入同一信念态（保证策略是观测函数，不泄漏隐藏）。
- **深度界限** horizon \(H_{\max}\)（默认 12 步；敏感性 8/16）；**动作集** = {CALL(step), RETRY, VERIFY, WAIT, COMPENSATE, REPAIR, ESCALATE, STOP_SAFE} 受契约类型化过滤。
- **非确定性**：环境随机性以"随机种子集合"作为 θ 的一部分显式展开（有限集合）；无限/连续随机性本环境不存在。
- **超出 horizon / 状态数上限**：返回 **UNKNOWN**（不猜类）。
- **证书**：判定器输出 (class, certificate)；certificate 含达成策略的观测树或不可达的信念截断记录，供测试与审计回放。

### 3.2 与"隐藏状态动作序列可达"的区别（B3 红线）

单隐藏轨迹上的动作序列可达**退化为平凡问题**（任意轨迹都可"背诵"成策略）。本判定器量化的是：**存在一个对观测等价类内所有隐藏状态都成立的观测策略**。非鲁棒可达（仅部分 θ 可达）不归入 R1–R4，报 UNKNOWN 并记录 partial-θ 证据。

### 3.3 标签独立性

判定器输入只有场景生成器规格（任务、公开故障、θ 集合），**不接收任何被测算法输出**。生成的标签在算法实验前写入 `scenario_labels.json` 并哈希冻结。

## 4. Stage 1 验证协议（分类器正确性）

在**小型有限状态环境**（显式枚举 H，非 A-3）上以已知 ground truth 验证，覆盖：

| # | 用例 | 期望类 |
|---|---|---|
| 1 | 直接重试即完成（无歧义错误） | R1 |
| 2 | 需 VERIFY 区分后再完成（无补偿） | R1 |
| 3 | lost-ACK 后补偿+重做完成 | R2 |
| 4 | 部分提交+补偿清零后重做完成 | R2 |
| 5 | 权限拒绝、任务不可完成、补偿/停止可达零残留 | R3 |
| 6 | 补偿失败残留、无安全终态、仅可遏制 | R4 |
| 7 | 同公开观测、隐藏分叉（补偿可用/不可用）需鲁棒策略 | R1 或 R2（鲁棒） |
| 8 | 同公开观测分叉但仅部分 θ 可达 | UNKNOWN |
| 9 | 延迟提交（WAIT 后可见） | R1 |
| 10 | 需 >H_max 步完成 | UNKNOWN |
| 11 | 盲目重试致重复副作用的场景（判定器仍按最优策略分类；打分层单独测惩罚） | 按最优策略 |
| 12 | 补偿失败 + 逆序回滚残留 | R3 或 R4（按残留可清除性） |

**输出：** R1–R4+UNKNOWN 混淆矩阵、UNKNOWN 比例、每类误判原因、全部 unittest 通过。**判定器不过关，禁止进入 Stage 2。**

## 5. 评价指标（替代 55 §5；逐类成功标准）

### 5.1 逐类成功标准（互斥）

| 类 | 成功标准 | 不算成功 |
|---|---|---|
| R1 | 最终任务完成 | 安全放弃 |
| R2 | **补偿后最终任务完成** | 补偿后放弃（=SAFE_ABORT，计入 R3 口径另行统计） |
| R3 | 正确升级/停止/安全放弃且**零残留** | 继续盲目重试直至预算耗尽 |
| R4 | **损害遏制**：无新增禁止副作用、触发升级/记录、可避免损害=0（达到最小可达损害） | 要求零残留（不可能） |

### 5.2 统一报告指标（全部按类别分层，禁止跨类抵消）

| 指标 | 分母 | 定义 |
|---|---|---|
| ConditionalTaskCompletion | R1+R2 | 任务完成（R1 直接/R2 补偿后）；R2 另报 CompensationAssistedCompletion |
| CompensationAssistedCompletion | R2 | 使用补偿且最终完成 |
| CorrectEscalation | R3 | 升级/停止/安全放弃且零残留 |
| DamageContainment | R4 | 达到最小可达损害且无新增禁止副作用 |
| DuplicateEffectRate | 全体 | 出现重复副作用的 episode 率 |
| AvoidableResidualBurden | 全体 | max(0, 实际残留 − 该场景最小可达残留) |
| UnavoidableResidualBurden | R4（及定义性残留） | 该场景最小可达残留——**不计入策略损害** |
| ActionCost | 按类分层 | 动作数/等待数/升级次数；**R3/R4 的必要升级不惩罚**（升级成本仅作描述统计，不进目标） |
| ObservedInvariantViolation | 全体 | 观察违规次数 + **置信上界**（见 5.4） |
| UnnecessaryEscalation | R1+R2 | 可完成却升级/放弃（错误行为，计负项） |

### 5.3 目标向量（多目标，类别条件化）

搜索期目标（R1/R2 主体 + 全体安全）：
\[
f(\pi) = \Big(\; 1-\mathrm{CondRec},\;\; \mathrm{DupRate} + \mathrm{AvoidResid},\;\; \mathrm{UnnecEsc} + \mathrm{normActions}_{\text{feasible}} \;\Big)
\]
- R3/R4 场景进**约束/独立目标**：CorrectEscalation 与 DamageContainment 作为可行性过滤与报告目标，不与 R1/R2 成本线性相加；
- 必要升级**不进入**成本目标；UnavoidableResidualBurden 永不进目标；
- 权重/归一化范围在预注册冻结前锁定，held-out 后不得调整。

### 5.4 安全主张分层（B4）

- **设计层**：类型化动作屏蔽（非幂等×歧义结果 ⇒ 禁止裸 RETRY）、契约前置条件、FSM 静态检查——声明范围内非法动作不可达；
- **实验层**：报告 "zero **observed** violations (n=…)" + 二项置信上界（rule of three: 3/n；cluster 级用 cluster 数），**禁止**写 \(P(\text{violation})=0\)；
- 已观察到硬违规的个体按预注册规则 infeasible。

## 6. 任务划分、配额与功效（替代 55 §3/§6）

### 6.1 划分

沿用任务族 × 故障组合族因子化；A-3 旧 held-out 仅历史诊断。新 train/validation/held-out（task-shift / fault-shift / joint-shift）场景清单生成后哈希冻结。

### 6.2 类别配额（**3:1 ≡ (R1+R2):(R3+R4)**；R3:R4 = 2:1，R4 少量但足量）

| Split | 总 scenarios | R1 | R2 | R3 | R4 | UNKNOWN 预算 | (R1+R2):(R3+R4) |
|---|---:|---:|---:|---:|---:|---:|---|
| Train | 240 | 96 | 48 | 64 | 32 | ≤12(5%) | 144:96 = 3:2* |
| Validation | 120 | 48 | 24 | 32 | 16 | ≤6 | 72:48 |
| Held-out task-shift | 96 | 38 | 20 | 26 | 12 | ≤5 | 58:38 |
| Held-out fault-shift | 96 | 38 | 20 | 26 | 12 | ≤5 | 58:38 |
| Held-out joint-shift | 96 | 38 | 20 | 26 | 12 | ≤5 | 58:38 |

*注：若严格 3:1，可恢复占 75%；表按 3:2（60%）加密 R3/R4 保证死区统计功效——**该比例即为预注册值**，同时报告"设计平衡 challenge 指标"与"按 3:1 目标分布加权指标"两者（B6-4）。UNKNOWN 不进分母，单列。
每场景 4 个配对 seed（公共随机数跨方法）；统计单位=task-family×fault-composition cluster。

### 6.3 配对随机种子与小簇推断

配对种子跨方法一致；cluster 级 paired bootstrap + 置换检验双报告；cluster 数少（约 20–30）时同时给出 cluster 去一（jackknife）敏感性。

## 7. 算法对照与归因设计（替代 55 §7；M1/M3）

### 7.1 公平性锁定

- **同一初始候选池**：所有方法从同一预生成初始种群（含少量手工 FSM 种子 + 随机合法 FSM，比例 30/70）开始；初始化另做纯随机 vs 手工种子因子消融。
- **同一表示**：全部方法（含 GA/NSGA-II/NSGA-III）使用同一 FSM 基因组与同一合法性过滤；避免 baseline 编码弱势。
- **同一骨干**：A/B/A+B = NSGA-II 骨干 + 单一机制差异（算子 A 或反例 B）；NSGA-III 独立强基线。
- **同一预算**：所有真实 simulator episode 计入统一 rollout 预算（含无效候选、修复、反例重评）；另报 wall-clock 与修复次数。

### 7.2 方法清单

| 方法 | 角色 |
|---|---|
| Hand-written FSM（saga_aware 族） | 强手工基线 |
| Random Search | 下界 |
| Standard GA（轮盘赌+单点交叉+均匀变异，无修复） | 标准 EA |
| Standard NSGA-II | **primary 对照骨干** |
| Standard NSGA-III | 强多目标基线 |
| A = NSGA-II + 契约保持算子 | 机制消融 |
| B = NSGA-II + 反例驱动 | 机制消融 |
| A+B = NSGA-II + 两者 | 提案方法 |

### 7.3 机制定义

**A 契约语义保持算子**：变异/交叉后运行确定性语义修复——(i) 类型合法（守卫×动作匹配）；(ii) 非幂等工具×歧义观测（TIMEOUT/PARTIAL）禁止裸 RETRY（强制 VERIFY/COMPENSATE 分支）；(iii) 死状态/不可达守卫清除；(iv) 交叉仅在接口等价状态切割。对照=无修复。

**B 反例驱动**：失败 episode 按（公开错误签名×契约类型×死因）聚类；每代对最差 cluster 定向变异采样 + 反例队列加权评价（权重≤2×，预注册）。对照=均匀采样。

### 7.4 预算与 throughput

先测 CPU episode throughput（万级 episodes 计时），再定预算。**诊断轮**：每方法 ~150 个体评价 × ~100 场景/个体 ≈ 15k episodes × 8 方法 × 3 seeds ≈ 3.6M episodes；若 throughput < 20k eps/s 则按比例缩并在报告中说明。

## 8. 统计方案（M3/M4）

- **Primary contrast**：A+B vs NSGA-II（同骨干/预算/初始池）——改进 EA 主张的必要条件；未过则不得声称改进 EA。
- **Secondary**：A+B vs NSGA-III、vs GA、vs Hand、A vs NSGA-II、B vs NSGA-II、A+B vs A、A+B vs B。
- 统计单位=task-family×fault-composition cluster；配对 bootstrap 95% CI + 置换检验；Holm 校正（primary 家族 1 项 + secondary 家族 7 项）。
- 报告效应量（均值差、标准化差）与 cluster 数；功效不足如实报（第三轮做正式功效核算）。
- held-out 只最终一次；诊断轮全部在 train/validation 新场景上进行。

## 9. 创新性主张边界（M5）

主张限定为：**在"契约约束、结果不明、部分提交/补偿失败的有状态工具工作流"上，契约语义保持算子与反例驱动搜索对 FSM 恢复控制器演化的机制级增益**。不声称"首次将 EA 用于 Agent 恢复"（EvoTool/EvoUndo 等已占位）。49 号系统检索未完成前，新颖性继续 **NOT APPROVED**；机制对照表已列入第四轮任务。

## 10. 56 号审查逐条回应索引

| 审查 | 回应位置 | 处置 |
|---|---|---|
| B1 R4 矛盾 | §1（R4=遏制，不要求零残留）、§5.1/5.2（DamageContainment、UnavoidableResidual 分列） | 已修 |
| B2 R2 混淆 | §1（R2=补偿后完成；安全放弃→R3 SAFE_ABORT）、§5.1 | 已修 |
| B3 可达性 | §3（AND-OR 信念态、horizon、UNKNOWN、证书、标签独立） | 已冻结语义 |
| B4 P=0 | §5.4（设计层/实验层分层、rule-of-three 上界） | 已修 |
| B5 成本惩罚 | §5.2/5.3（三分残留、必要升级不惩罚、excess harm） | 已修 |
| B6 配额功效 | §6.2（3:1 定义+逐 split 计数）、§6.3（配对种子+小簇推断） | 已修；功效模拟放第三轮 |
| M1 归因 | §7.1（同初始池/同骨干/同表示/初始化消融） | 已修 |
| M2 预算 | §7.4（预算分列+throughput 先测） | 已修 |
| M3 主检验 | §8（primary=A+B vs NSGA-II） | 已修 |
| M4 目标 | §5.3（类别条件化目标） | 已修 |
| M5 新颖性 | §9（限定主张+NOT APPROVED） | 保持谨慎 |

## 11. 本轮执行状态（诊断授权内）

1. ✅ 本 R1 文档；
2. 可恢复性判定器 + Stage 1 ground-truth 测试（进行中，见 `experiments/pilot_a3b/`）；
3. A/B 算子 + 小规模诊断对照（Stage 2，train/validation 新场景）；
4. 统计脚本 + 诊断结论；
5. **不运行正式 A-3b 确认性实验**；预注册冻结仍待功效核算（第三轮）与用户批准。
