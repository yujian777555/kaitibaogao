# D-094 R4 下一轮算法机制实验计划

状态：**R4已完成设计、实现、预注册与合成/Mock验证；真实R4 NOT RUN，独立审查PENDING，APPROVED_FOR_EXPERIMENT=NO。** R3.1结论保持`NO_CLEAR_GAIN`，不得重跑调参。

## 1. R3.1 提供的直接依据

真实五臂共42 episodes、169 HTTP、0.0478524 USD，预算和复算均通过，但四个演化臂final全部0/2，四个预注册比较没有成功率差。深度分析进一步确认16/16搜索候选成功率均为0；B3/B5增加的Phenotype包含更多约束拒绝循环，且一次七目标Pareto改善只来自资源变化。详见`D094_R3_1_DEEP_ANALYSIS.md`。

最终8个演化episodes均inspect→verify→retry后因三步上限终止，未补偿/完成。R4因此把公共动作可达性作为有效性前提，但不把提高步数本身包装为算法创新。

## 2. 已选定的单一R4方案

| 臂 | 方法 | 研究职责 |
|---|---|---|
| B1 | Fixed LLM | 非演化基线 |
| B2 | 标准NSGA-II、六算子均匀 | 主对照 |
| B3 | 质量优先的配对父子算子信用 | 唯一主创新 |
| B4 | 旧失败频率反馈 | 消融对照 |

不保留B5，不组合多样性。所有演化臂采用相同feasibility-first标准NSGA-II survivor、216个公共五步Genome、相同初始种群和候选评价机会。

主信用在variation第一parent与child的完全相同四个task/seed单元上计算：先比较约束增减；约束相同再比较`(1-task_success,1-recovery_success,harm)`的严格Pareto支配；四单元均值为offspring reward。资源-only变化=0。最近W=4个accepted reward进入τ=0.25、ε=0.2的softmax；冷启动均匀，duplicate不更新，child完整评价后仅影响后续proposal。

## 3. 已冻结的Fresh Train、预算、final与统计

- 两项Fresh Train与历史18个Train任务双向ID/完整规格交集为空；未读取Validation/Test，held-out语义重叠明确标为未检查。两任务×seeds 301/302的本地确定性路径为3/4步，均≤公共五步，API=0。
- B1=4 episodes；B2/B3/B4各4个搜索候选×4单元+独立final 4 episodes，总计64 episodes。B3没有额外配对评价。
- final从全部已评价搜索候选的可行第一Pareto front，以`(objectives,genome_sha256)`字典序最小选择，并用四个新episodes重新评价。
- 全局R4硬上界=320请求/0.442368 USD；B1及三个final各预留20请求/0.027648 USD，搜索不得占用。
- 主比较=B3−B2 final Task Success，最小有意义效应=0.25；四单元16次精确符号翻转、20,000次paired bootstrap 95% CI、四比较Holm。小样本只作探索性机制证据。

权威文件=`D094_R4_ALGORITHM_DESIGN.md`、`D094_R4_PREREGISTRATION.md`、`D094_R4_BUDGET_ANALYSIS.md`、`D094_R4_IMPLEMENTATION_REVIEW.md`。

## 4. 当前唯一任务与禁止事项

最新预检为`PREFLIGHT_PASS`，合成为`SYNTHETIC_VALIDATED`（13项门禁全true）；D-094=135/135，七目录全量=677/677。以上均为软件证据，不是实际Agent性能。

**下一步只在新独立会话按`D094.NEXT_SESSION_PROMPT.md`进行只读独立审查。** 当前没有真实执行入口，不得自动运行真实API。审查发现的问题须先报告，不得由审查者暗中改协议追求通过；审查通过后仍须用户明确授权。不得删除不利seed、追加预算、改写R1/R2/R3.1或访问Validation/Test、A800、外部模型训练和main。

---

# 历史：D-094 R3 算法机制实验计划（R3.1结果见上方）

状态：**历史设计；R3.1已COMPLETED / NO_CLEAR_GAIN。**

## 1. R2 给出的针对性依据

R2 证明真实 LLM/NSGA-II 链路可运行，但 B1 不如 B0，B2 最终评价因预算耗尽无效。32个 Genome 有24个 phenotype，17/496对出现相同行为。下一轮不只追求成功率，还要减少无效搜索、保留最终评价预算并补齐账本。

优先验证 **失败反馈驱动算子选择** 与 **行为多样性感知选择**，而不是扩大搜索规模或提高预算。

## 2. 实验臂与归因

| 臂 | 方法 | 研究职责 |
|---|---|---|
| B1 | 固定 DeepSeek Agent | 非演化 LLM 基线 |
| B2 | 标准 NSGA-II | 标准 EC 对照 |
| B3 | 失败反馈驱动 NSGA-II | 检验动态算子的独立贡献 |
| B4 | Phenotype-aware NSGA-II | 检验行为选择机制的独立贡献 |
| B5 | Feedback + Phenotype | 检验互补或干扰 |

主要比较：B3−B2、B4−B2；次要比较：B5−B3、B5−B4。不得把 B5 的效果同时归给两种机制。

## 3. 小规模预注册配置

- 模型：`deepseek-flash`；temperature=0；显式非思考 JSON；相同 base URL、工具和 Schema。
- 新 D-094 R3 独立 Train manifest：6个任务，覆盖 verification/transient/compensation 三类，各2个；不使用R2结果生成任务，不读取 Validation/Test。
- 新配对 seeds：201、202。每个候选评价相同6×2=12 episodes。
- 每个演化臂：初始种群4、1代、最多8个唯一搜索候选；最终1个 feasible Pareto 候选重新评价12 episodes。
- B1 fixed=12 episodes；每个演化臂 search≤96、final=12。B0不纳入R3，保留R2历史基线。
- 全局上限：**1500次真实 HTTP、0.50 USD Token成本**，不超过R2预算；并发、超时和重试固定，不无限重试。
- 所有臂共享相同真实评价预算规则；不得减少B2评价量或删除失败 seed。

这是机制预检，不是确认性统计实验。若预检预算不能完整覆盖，状态为 BLOCKED_BUDGET，不发起首个请求。

## 4. 预算安全必须先修复

R3 实现前必须具备：

1. 实验开始前锁定并预留 B1 和每个最终候选的评价预算；搜索不得消耗预留。
2. 搜索预算耗尽时停止提出新候选；不得继续生成只有 LLM_ERROR 的“完整” final episodes。
3. 真实发送、预算拒绝、Token、已知成本与上界分账；任何缺失/超额使运行 INVALID。
4. 每个 candidate/seed/task/episode 的实际数量与预算在执行锁中可复算。
5. 不通过缓存命中冒充新真实评价；缓存仅用于相同已评价 key 的显式审计，不进入性能对照。

## 5. 算法机制

### B3：失败反馈

只从已完成 Train 候选的公开聚合失败计算工具失败、规划错误、恢复失败、依赖错误、未完成和冗余调用等特征，通过冻结的 softmax/探索下限调整下一轮 mutation block 概率。保存原始计数、归一化分子分母、每个概率和实际算子调用。零反馈必须退化为均匀概率。

### B4：Phenotype-aware NSGA-II

保持可行性优先、非支配排序和 crowding。只在候选已经完成真实评价后使用其实际 phenotype，对相同 phenotype 的 Genome 施加预注册的确定性选择规则。不得在评价前假定 phenotype，不得修改真实 fitness。记录每个 survivor 的 Genome/Phenotype。

### B5：组合

仅组合B3/B4已冻结的机制，不新增第三套参数。用于检验反馈与行为选择是否互补。

## 6. 评价与判据

报告 Task/Recovery Success、Harm、Constraint Violation、Tool Cost、Token Cost、Latency、行为多样性、唯一候选数和 Pareto front。硬约束不可补偿。

- 主要机制信号要求总体方向及两个配对 seeds 均一致，并报告全部原始差值；不做确认性显著性宣称。
- B3/B4/B5 若仅增加 Token 或 API 次数而没有行为/性能改善，记为 NO_CLEAR_GAIN。
- 若 phenotype 相同，不得把 Genome hash 差异写成行为创新。
- 若最终预算不足、执行错误或账本不完整，记为 INVALID，不进入性能结论。
- 正向小样本结果必须另建独立复现，不能直接写成普遍提升。

## 7. R3 必须补齐的审计字段

- 每次 variation 的中间 Genome、实际 mutated locus、before/after gene value；
- 所有被拒绝 duplicate proposal 及原因；
- 每代 survivors 及其 Genome/Phenotype；
- 每 episode 的逐事件 hash-chain；
- 反馈分子/分母/概率和 operator invocations；
- 预算预留、释放、真实发送和预算拒绝账本。

## 8. 后续 RSI 与训练

只有当 B3/B4/B5 的独立贡献可复现，才研究跨代经验驱动的 RSI。A800训练继续冻结；高质量轨迹需先通过数据质量、独立评价和训练目标审查，不能与 R2/R3 的 Prompt/Genome 演化混报。


## R3 算法实现与合成审查状态（2026-11-19）

B4、B3、B5及请求前预算预留已实现，见`D094_DIVERSITY_AWARE_NSGA2.md`、`D094_FAILURE_FEEDBACK_EVOLUTION.md`和`D094_R3_PREREGISTRATION.md`。实现自检见`D094_R3_IMPLEMENTATION_REVIEW.md`。

D-094测试82/82。专用选择器fixture中Standard唯一phenotype=1、Full B4=2；演化fixture中Standard/B4均0.75，B5=0.50，所有臂均8次评价。没有真实搜索效率或性能提升信号。

当前为READY_FOR_INDEPENDENT_REVIEW，不是APPROVED_FOR_EXPERIMENT。R3真实API实验NOT RUN；下一独立会话必须复核公式、控制流、账本和预算可执行性，并取得用户明确批准。
