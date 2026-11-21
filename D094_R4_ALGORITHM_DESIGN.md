# D-094 R4 算法设计：质量优先的配对父子算子信用

状态：`R4_ALGORITHM_DESIGNED / R4_IMPLEMENTED / R4_SYNTHETIC_VALIDATED`；真实实验未运行，`APPROVED_FOR_EXPERIMENT=NO`。

## 1. 单一主假设

在相同任务、相同 seed 的父子配对单元上，以硬约束优先、任务/恢复成功与 Harm 的严格 Pareto 改善评价 variation 算子，再用最近 accepted offspring 的信用更新后续算子概率。与失败频率反馈相比，该机制直接学习“哪个算子实际改善了什么”，同时避免把纯资源变化或行为新颖性误记为主质量收益。

## 2. 实验臂与独立归因

| 臂 | 模式 | 职责 |
|---|---|---|
| B1 | Fixed LLM | 非演化基线 |
| B2 | `standard` | 标准 NSGA-II、六算子均匀分布 |
| B3 | `paired_credit` | 唯一主创新：在线配对父子信用 |
| B4 | `failure_feedback` | R3 的旧失败频率反馈消融 |

不保留 B5，不叠加行为多样性。所有臂采用同一 feasibility-first 标准 NSGA-II survivor 规则，因此 B3−B2 的差异只来自算子概率更新；B3−B4 区分结果信用与失败频率，B4−B2 衡量旧反馈本身。

## 3. 公共搜索空间与可达性

- 原始合法池 648 个 Genome；R4 搜索池固定 `max_plan_steps=5`， eligible pool=`3×4×3×3×2=216`。
- planning mutation 只改变 `planning_mode`，不改变步数；crossover 也继承固定五步。
- 五步不是主创新，也不是给 B3 的额外优势，而是所有臂共享的动作可达性前提。
- Fresh Train 的补偿任务公共路径为 inspect→compensate→complete（3 步）；单次 transient 为 inspect→retry→retry→complete（4 步）。两个 seeds 均通过真实本地确定性环境执行，API=0。
- 可达性证明不表示真实 LLM 必然找到路径，只排除已知不可能配置。

## 4. 配对单元与主信用

设父代 `p` 是 variation 的第一个 parent。父子必须具有唯一且完全相同的集合：

`K={(task_id,seed)} = {两个 R4 任务}×{301,302}`，`|K|=4`。

任一缺失/重复单元、集合不一致或 execution error 都使运行无效，不允许用剩余单元补算信用。

对每个单元 `j∈K`，先比较约束总数 `C`：

- `C_child>C_parent`：`r_j=-1`；
- `C_child<C_parent`：`r_j=+1`；
- 约束相同时，构造最小化质量向量 `q=(1-task_success, 1-recovery_success, harm)`：
  - `q_child` 严格 Pareto 支配 `q_parent`：`r_j=+1`；
  - 反向严格支配：`r_j=-1`；
  - 完全相同或存在 trade-off：`r_j=0`。

一次 accepted offspring 的奖励为：

`R_o = (1/|K|) Σ_j r_j`，故 `R_o∈[-1,1]`。

**Tool Cost、token/cost upper、latency 不进入 `r_j` 或 `R_o`。** 它们仍是七目标 NSGA-II 和 final Pareto 选择的一部分，但不能单独驱动主信用。

## 5. 滑窗、探索下限与概率更新

六个算子顺序冻结为：

`planning_mutation, recovery_mutation, memory_mutation, verification_mutation, tool_guard_mutation, crossover`。

每个算子 `k` 只保存最近 `W=4` 次 accepted offspring 奖励，记窗口为 `H_k`：

`c_k = 0`（冷启动或空窗口）；否则 `c_k = mean(H_k)`。

冻结 `τ=0.25`、`ε=0.2`：

`p_k = (1-ε) × exp(c_k/τ) / Σ_l exp(c_l/τ) + ε/6`。

实现用减去最大 logit 的稳定 softmax。每算子概率下界为 `ε/6=0.033333…`，总和为 1。

- 冷启动严格均匀 `1/6`。
- duplicate 不评价、不更新窗口、不改变概率。
- 只有 child 的全部四个配对单元评价完成后才更新。
- 本次 child 的结果只影响后续 proposal；当前 proposal 的概率在评价前写入账本。
- 一代只有两个 offspring 时，最后一个 credit update 可能没有后续 proposal，这是合法的时序边界，不得伪装成搜索行为收益。

## 6. 旧失败反馈对照

B4 保留 R3 的公开七类失败分类、反馈矩阵、`β=2`、`τ=0.25`、`ε=0.1`。它只读取已完成候选的公开聚合失败 profile，不读取配对信用。B2 不使用 feedback/credit；B3 不使用旧 feedback。三臂的 survivor、任务、seeds、初始种群、候选评价次数和 final 规则一致。

## 7. 评价预算与 final

每个候选必须在全部 `2×2=4` 个 task/seed 单元上评价。每演化臂：

- 初始候选 2；
- 1 代 offspring 2；
- search 共 4 个唯一候选、16 episodes；
- final 从**全部四个已评价搜索候选**的可行第一 Pareto front 选择，而非只看最后 survivors；
- final 选择键=`(objectives, genome_sha256)` 字典序最小；
- final 使用相同 Train 单元的新真实 episodes 独立评价 4 次，不得复用搜索成绩。

无可行 final、final 缺失、零真实调用、配对不完整、执行错误、未知成本、hash-chain 失败或超预算均为 INVALID。

## 8. 账本与信息隔离

新模块保存：

- evaluation：完整 Genome、七目标、配对单元质量、Phenotype、execution error；
- variation：两个 parent、主 parent、算子、提案时概率、locus before/after、duplicate 终态；
- credit update：逐 task/seed 父子质量、每单元奖励、均值、W/τ/ε、更新前后窗口/信用/概率、资源未使用和未来信息未使用标记；
- feedback update（仅 B4）；
- 每代 survivors 与 genotype/phenotype/performance diversity；
- 请求预留/结算、逐事件 hash-chain、全 archive、Pareto/final。

合成 evaluator 只由 Genome 决定公开 fixture，不读取 parent、credit、后续评价或隐藏标签。合成/Mock 结果不得写成真实 Agent 提升。

## 9. 实现入口

- `d094_r4_credit.py`：配对数据结构、信用公式、216 池、三种模式和完整搜索账本。
- `d094_r4_tasks.py`：Fresh Train、逐任务 SHA、历史 Train 隔离与可达性。
- `d094_r4_statistics.py`：四单元精确符号翻转、20,000 次配对 bootstrap、Holm。
- `run_d094_r4.py`：纯预检或 Mock-only 协议；**没有真实 API 执行参数**。
- `run_d094_r4_synthetic.py`：合成门禁与 64 episode Mock 全链。

真实执行入口需在独立审查后按审查意见补齐，并取得用户明确批准；当前实现不得自行转成 `APPROVED_FOR_EXPERIMENT`。

## 10. 可证伪性

若 B3 相对 B2 仅改变概率/Genome/Phenotype，而 final Task Success 无最小有意义效应，或改善只伴随资源变化、单一 seed 或搜索成绩，应报告 `NO_CLEAR_GAIN`。若 B3 与 B4 无差异，不能声称结果信用优于失败反馈。若任何臂评价机会不均或 final 复用搜索成绩，实验无效而不是有利结果。
