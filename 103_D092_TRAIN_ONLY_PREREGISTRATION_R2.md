# 103 — D-092 Train-only 动态失败反馈演化预注册 R2

**协议版本：** `D092-R2-PREREGISTRATION`
**状态：** `READY_FOR_INDEPENDENT_REVIEW / NOT FROZEN / NOT RUN`
**历史版本：** `103_D092_TRAIN_ONLY_PREREGISTRATION_R0.md`、`103_D092_TRAIN_ONLY_PREREGISTRATION_R1.md`
**最高审查依据：** `105_D092_R1_INDEPENDENT_REVIEW.md`
**唯一科学问题：** 在相同真实评价预算下，动态失败反馈能否比标准 NSGA-II 找到更好的安全恢复策略？

R2 只定义可执行协议、公式、预算、日志和静态测试。没有实现搜索器或 typed adapter，没有执行 probe、genome search 或候选选择。主要终点和四个比较职责保持不变。

---

## 1. 研究假设与实验臂

主假设为 A3 相对 A1 提高 R3 CorrectEscalation，同时不降低 R4、Conditional Recovery 或安全表现。A3−A4 是反馈的直接消融；A1−A0 和 A2−A1 是独立次要比较。A3 只优于 A0 不能支持反馈提升演化算法。

| ID | 唯一身份 | 研究职责 |
|---|---|---|
| A0 | 无放回均匀 Random Search | 同真实评价预算的随机基线 |
| A1 | feasibility-first NSGA-II，均匀块概率 | 标准演化骨干 |
| A2 | feasibility-first canonical NSGA-III，均匀块概率 | 多目标环境选择对照 |
| A3 | feasibility-first NSGA-II，动态失败反馈块概率 | 主研究臂 |
| A4 | 与 A3 相同但反馈永久为零 | 直接反馈消融 |

A1 与 A4 理论上产生同一搜索轨迹；它们不是两份独立证据。第 11 节规定逐 seed 等价检查。

## 2. 不可变数据、源码和版本锁

### 2.1 数据

只使用 `experiments/d090_recovery/results/d090_train_manifest.json` 中现有 96 个 Train 场景，不重新生成或替换，不读取 Validation/Test 或其他仓库数据。

| 对象 | Git blob SHA | 内部 SHA-256 | canonical file SHA-256 |
|---|---|---|---|
| D-090 Train manifest | `b917b4c624601022e8d8896182dfaed71ba0d21c` | `7d677fe075a5bac6b4241be6c4f38e0c55022b6059729e9a05c7cdf7d633350d` | `be64100e49191d42174db0cacb0d26c58302fe009933849c3e2406e7220ee4c3` |

canonical file hash 为 `b"\n".join(file_bytes.splitlines())` 的 SHA-256。

### 2.2 真实源码依赖闭包

以下 canonical SHA 与 Git blob 均为仓库中已复核的真实身份。`dependency_recovery.py` 同时提供环境和结果评估器。

| 路径 | canonical SHA-256 | Git blob SHA |
|---|---|---|
| `experiments/d090_recovery/d090_scenarios.py` | `98c21e5c36e1a5eb59605e9a0ea1ae0dddca768ab0a0017d6b4cb68bad6fe194` | `962ade0f8f7bb2eb849b852f0a67edcf08d75712` |
| `experiments/pilot_a3b/dependency_recovery.py` | `e10b966374afb98ce25ded6d3bd046537a061e0f420c100cf5f04ea211a64f89` | `5dfff3705ecc3ad64485775eace777a428970b63` |
| `experiments/d090_recovery/d090_experiment.py` | `511a5e7af6fbfa53ad1cede4e19eff9d2cb4c462e7c407ce887bcddd3652b767` | `16457f67969a8e0016fe4a531fe07acf771adacc` |
| `experiments/d090_recovery/d090_genome.py` | `335c89c71ec82ef6517a4978e5a6ec8ced6209d53b015e9518ca45032923e950` | `52a7e808e3c1fff89d55215ce256eb57c8ae5fd3` |
| `experiments/d090_recovery/d090_policies.py` | `0dc7ac2db65ebb882721c09dbc4a55b5c294711bceecd1f156c22f4baa5e5e13` | `c96beaf6577cf9898e6baaa4d22065662b269844` |
| `experiments/d089_recovery/d089_search_experiment.py` | `52cb6174a95f8a61ff4d827965ea7aa4c5e847eb784b8c518fcaff29d40d7904` | `fae92d703d918ffebef8093875b8e34dd90a8aa3` |
| `experiments/d089_recovery/d089_genome.py` | `b0de59480e07e88e40771d591bd54e8a969c5bc8f84c935b6d4a79e7a4b171ae` | `ad02e712732297e366d2cf8702eac29162b5a8d8` |
| `experiments/d089_recovery/d089_policies.py` | `c6cff025bbd7d221abc2e122eb9b5e12f251130f8ccbf45f9c544281d0de5a2b` | `10850ee98da1bd20a2bc3eb2388b9449cd9b926b` |
| `experiments/d089_recovery/d089_budget.py` | `52e3efde7ca3b7a24dc45a3e32abc38d1dcd46c6b23a18797637aa14da6c9473` | `c721d4a1d2ab6e671e2b3a99aca2fe4bf03b798b` |
| `experiments/d088_recovery/d088_genome.py` | `906b913fe32aeaee9a491dc39f6f2e07c258d24ef277d5c3cba154bd54743b3b` | `4ef7aae98615dc63a2016208d9b55c6f65758185` |
| `experiments/d088_recovery/d088_policies.py` | `b8be10b5df4f0a66ef4d4583e7cdc808dd91448609dfbbc9189488248c9fdd61` | `afe2ed253704d2bf9f4e3f57f6e0a14f04f14be5` |
| `experiments/pilot_a3b/dependency_genome.py` | `11f4d00673ff1088c6d244ff218c3fd69fe8376e4ba621c813b8fbb446f3c373` | `c3e544cdef87dbde1389aed8fde869bc94fe805b` |
| `experiments/pilot_a3b/dependency_policies.py` | `abcc0e83b070128973012ca8403e8ec56f70543d4b918dc5fbbb101e54af8d1a` | `dfcb2a0f4b5174482dd6d6e74d097f62852ceae6` |

目标 schema/evaluator/ledger 分别为 `D092R2_TYPED_GENOME_V2`、`D092R2_EVALUATOR_V2`、`D092R2_LEDGER_V2`。新实现尚不存在；实现审查必须追加 typed adapter、搜索器、反馈、账本、运行时锁文件的真实哈希。任何不匹配均为 `INVALID_HASH_BINDING`。

## 3. Typed genome、枚举与搜索空间

### 3.1 五字段 schema

| 字段 | 允许值 | 语义 |
|---|---|---|
| `cycle_mode` | `OFF`, `FILTER_ONLY`, `ALT_AND_FILTER` | 互依环关闭、只过滤、过滤并允许 deadlock alternate |
| `fallback_enabled` | bool | 正常可用集为空后的公开可达 fallback |
| `completion_guarded` | bool | 公开最小残余和可继续派发条件下的 completion gate |
| `harm_reorder_budget` | `None`, `4`, `8`, `12` | harm 重排关闭或预算阈值 |
| `probe_wait` | `0.0`, `1.0`, `2.0` | 初始回执确认等待参数 |

四个 operator blocks 为 `pair={cycle_mode}`、`fallback={fallback_enabled}`、`completion={completion_guarded,probe_wait}`、`harm={harm_reorder_budget}`。BASE 参数固定且不可变异。mutation 必须选择不同合法值；crossover 按完整 block 继承；单 nullable harm 字段消除了旧条件 repair 歧义。

搜索空间严格为：

\[
3\times2\times2\times4\times3=144\ \text{genomes}.
\]

96 次评价覆盖 \(96/144=66.6667\%\)。全部 144 个 canonical genome 按 canonical JSON 字符串升序形成唯一枚举表 `G[0..143]`。

### 3.2 Canonical genome JSON

对标量先执行第 9.1 节规范化，再使用 UTF-8 JSON：`ensure_ascii=False`、`sort_keys=True`、`separators=(",",":")`、`allow_nan=False`。列表保持语义顺序，对象键排序。canonical genome hash 是该字节的 SHA-256，不使用 Python `hash()`。

## 4. F1/F2：固定种群、轮次和唯一预算伪代码

### 4.1 固定控制参数

- 种群 \(\mu=12\)；每轮接受的新唯一 offspring 数 \(\lambda=12\)。
- 12 个共享初始 unique genomes 加 7 轮 offspring，总计 \(12+7\times12=96\) unique evaluations。
- 每个 arm×seed 的 proposal attempts 独立从 0 开始，包含初始化和所有重复 proposal；上限为 **384**，包括初始化的 12 次最小 attempts。
- 每个 genome 原子评价全部 96 场景；完整 episodes 为 `96×unique_evaluations`。有效 run 必须为 9,216，部分 episodes 必须为 0。
- 五臂五 seeds 的 230,400 仅是全部有效时的设计上限。

### 4.2 初始化

从唯一枚举表 G 中用 init stream 均匀无放回抽取 12 个 genomes；因此初始 12 个 canonical-unique，初始 attempts 恰好为 12，初始 duplicates/cache hits 均为 0。相同 seed 的初始集合及顺序在五个臂完全相同。A0 后续采样与初始化都只依据枚举表，不依据性能。

### 4.3 原子 proposal 接口

```text
state per arm×seed:
  attempts = 0
  unique_evaluations = 0
  cache_hits = 0
  duplicate_proposals = 0
  full_episodes = 0
  partial_episodes = 0
  proposal_seen = empty set
  completed_cache = empty map
  archive = empty ordered map

OFFER(candidate, round_id):
  require attempts < 384 else INVALID_ATTEMPT_CAP
  attempts += 1
  key = canonical_genome(candidate)
  if key in proposal_seen:
    duplicate_proposals += 1
    if key in completed_cache:
      cache_hits += 1
      return DUPLICATE_CACHED
    return INVALID_INCOMPLETE_PRIOR_PROPOSAL
  proposal_seen.add(key)
  rows = evaluate_all_96_atomically(candidate)
  if interrupted or any row missing:
    partial_episodes += actual completed scenario rollouts
    return INVALID_EVALUATION_INTERRUPT
  completed_cache[key] = rows
  archive[key] = complete candidate record
  unique_evaluations += 1
  full_episodes += 96
  return NEW_UNIQUE
```

在有效 run 中，所有重复 proposal 都有完整缓存，因此 `duplicate_proposals=cache_hits`；无效 run 仍分别保留两字段。attempts 在重复/cache 前递增，不能跨臂或跨 seed 共用。

### 4.4 A0 Random Search

初始池之后，将 G 中尚未完成评价的 canonical genomes 按 canonical 字符串升序构成 remaining set。每轮从 remaining set 用 random_proposal stream 均匀无放回抽取 12 个；每次调用 OFFER。由于无放回，A0 每轮恰好 12 attempts、12 个新评价，duplicates/cache hits 始终为 0。7 轮后 remaining 为 48。A0 的 round 只是固定批次，不执行 survivor selection或 population 更新。

### 4.5 A1/A2/A3/A4 的每轮 offspring

每轮开始时冻结 12 个父代 population，直到本轮结束。重复执行 variation+OFFER，直到本轮接受恰好 12 个 NEW_UNIQUE；重复候选不占这 12 个名额，但计 attempt。该 round 的 12 个接受者组成 `U_t`。

每个 proposal 的 variation：

1. 用 variation stream 生成 \(u\sim U(0,1)\)。
2. 若 \(u<0.7\)，从当前 population 的 canonical-hash 排序列表中均匀抽取一个父代执行 mutation。
3. 否则从同一排序列表均匀无放回抽取两个不同父代；不允许 self-crossover。四个 blocks 分别用一次公平随机选择决定来自父代 1 或父代 2，然后执行一次 mutation。
4. mutation 按当前块概率选择 block，在块内均匀选字段，再从该字段剩余合法值中均匀选不同值。

一轮接受 12 个 unique offspring 后：

- A3 立即用且只用 `U_t` 的 `12×96=1,152` rows 更新下一轮反馈；第一个 offspring round 使用零反馈。
- A1/A2/A4 保持均匀块概率；A4 仍计算并记录零反馈检查，但不据此改变行为。
- A1/A3/A4 对 parent+12 offspring 执行 NSGA-II survivor，A2 执行 canonical NSGA-III survivor，均输出下一轮 12 个父代。
- survivor 只在整轮结束后执行，不在中途替换父代。

```text
initialize shared 12 by uniform sampling without replacement
for each initial candidate in order: OFFER(candidate, round_id=0)
population = initial 12 for evolutionary arms
for t = 1..7:
  U_t = empty ordered set
  while size(U_t) < 12:
    candidate = A0_uniform_unevaluated() for A0
                otherwise variation_from_frozen_population()
    result = OFFER(candidate, t)
    if result == NEW_UNIQUE: append candidate to U_t
    if result is invalid: stop run as INVALID
  if A3: update feedback exclusively from U_t
  if A1/A3/A4: population = NSGA2(population + U_t, 12)
  if A2: population = Canonical_NSGA3(population + U_t, 12)
  if A0: no survivor operation
require attempts <= 384, unique_evaluations == 96, full_episodes == 9216
```

任何轮次不足 12 个新 unique offspring、cap 耗尽或评价中断均使该 arm×seed INVALID；不得增加轮数或追加 attempts。

## 5. F5：动态反馈的允许信息与数学定义

### 5.1 信息边界

真实 `report()` 内部调用 `classify_scenario()` 并使用 route outcomes/minimum 计算 reward。R2 明确允许优化器在**完整 Train episode 结束后**使用聚合 evaluator reward/fitness，包括 `class_success`、`avoidable_harm`、pending、trace receipts 和 runtime abort。这不等于在 rollout 前读取标签。

禁止向搜索器或策略直接提供：`label`、`min_reachable_harm`、`classify_scenario()` 调用、原始 hidden route outcomes、真实 delay/resolve_at、未来结果、Validation/Test 或任何锁箱字段。`class_success` 与 `avoidable_harm` 只能作为已完成 episode 的 reward 输出使用，不能反向读取其生成过程。

### 5.2 反馈集合和六项特征

\(U_t\) 始终是上一轮恰好 12 个新唯一 offspring，因此 \(N_t=12\times96=1{,}152\)。cache/duplicates 不重复加权，初始池不进入 offspring feedback。令 \(F_t=(r_t,d_t,p_t,a_t,u_t,h_t)\)，\(C_t\) 为全部 COMPENSATE 事件数且最小分母为 1。

\[
r_t=\frac{\#\{FAILED,DEPENDENCY\_BLOCKED,CONTRACT\_BLOCKED\}\text{ events}}{C_t},
\quad
d_t=\frac{\#\{DEPENDENCY\_BLOCKED\}\text{ events}}{C_t},
\]
\[
p_t=\frac{\#\{\mathrm{pending\_compensation}>0\}\text{ rows}}{N_t},
\quad
a_t=\frac{\#\{\mathrm{runtime\_forced\_abort}=1\}\text{ rows}}{N_t},
\]
\[
u_t=\frac{\#\{\mathrm{policy\_selected\_escalation}=1,\mathrm{class\_success}=0,\mathrm{runtime\_forced\_abort}=0\}\text{ rows}}{N_t},
\]
\[
h_t=\min\left(1,\frac{\sum\mathrm{avoidable\_harm}}{4N_t}\right).
\]

\(u_t\) 的名称是 **unsuccessful escalation rate（未成功升级率）**，不再称为过早终止率。所有特征在 [0,1]；零向量对应无失败反馈，不表示所有行为都被观测为零。

### 5.3 映射和概率

矩阵行顺序 pair/fallback/completion/harm，列顺序 \(r,d,p,a,u,h\)：

\[
M=\begin{bmatrix}
0&0.5&0&0.5&0&0\\
0.5&0.5&0&0&0&0\\
0&0&0.5&0.25&0.25&0\\
0&0&0&0&0&1
\end{bmatrix},
\qquad \phi_k(F_t)=\sum_fM_{kf}F_{t,f}.
\]

无截距且 \(\phi_k(0)=0\)。固定 \(K=4,\beta_k=2.0,\tau=0.25,\epsilon=0.1\)：

\[
z_k=\frac{\beta_k\phi_k(F_t)}{\tau},\qquad
\widetilde p_k=\frac{\exp(z_k-\max_jz_j)}{\sum_l\exp(z_l-\max_jz_j)},
\]
\[
p_k(t)=(1-\epsilon)\widetilde p_k+\epsilon/K.
\]

概率范围 [0.025,0.925]，总和为 1（绝对误差不超过 \(10^{-12}\)）。A4 永久 F=0，因此严格均匀。每轮保存 12 个 genome IDs、所有分子/分母、F、phi、z、概率、参数、输入评价 hash 和 RNG 计数。反馈只改变下一轮 mutation block 分布，不增加 mutation 或真实评价预算。

## 6. F3：NSGA-II 与 canonical NSGA-III

### 6.1 共同目标与可行性包装

可行候选的五维最小化目标为 \((1-R3,1-R4,1-CondRec,Harm,RecoveryCost)\)。性能 survivor 仅处理可行候选。可行候选不少于 12 时使用标准性能 survivor；不足 12 时保留全部可行者并用第 8 节不可行严重度键补足；没有可行者时只按严重度排序。硬约束不作为普通性能目标。

### 6.2 NSGA-II

标准非支配排序；逐 front、逐目标 crowding distance；边界距离无穷；零跨度目标不贡献距离；按 front rank、crowding 降序、canonical genome hash 升序选取。重复 canonical genome 只保留最早 proposal，phenotype 重复只记录不删除。

### 6.3 Canonical NSGA-III 的完整步骤

对 parent+offspring 可行池 S 执行非支配 fronts，完整接受 fronts 直至下一 front \(F_L\) 会超过 12；niching 只从 \(F_L\) 选取，绝不从其他 front 补选。

1. **Ideal point：** \(z_i^*=\min_{s\in S}f_i(s)\)，平移 \(\bar f_i(s)=f_i(s)-z_i^*\)。
2. **ASF/extreme points：** 对轴 \(j\)，\(w_i^j=1\) 若 \(i=j\)，否则 \(w_i^j=10^{-6}\)，
   \[
   ASF(s,w^j)=\max_{1\leq i\leq5}\frac{\bar f_i(s)}{w_i^j},\qquad
   e^j=\arg\min_{s\in S}ASF(s,w^j).
   \]
   ASF 并列取 canonical genome hash 最小者。
3. **Normalization：** 用五个极端点构造矩阵并解 \(E x=\mathbf1\)，候选截距为 \(a_j=1/x_j\)。若奇异、非有限或分母无效，使用 S 中该目标最大值作为截距。令 \(scale_i=a_i-z_i^*\)。若 `scale_i<=1e-12`，该零跨度目标的所有归一化值固定为 0、scale 记录为 1；否则 \(f_i^n=\bar f_i/scale_i\)。仅将 [-1e-12,0] 的数值误差截为 0，其他负值 INVALID。
4. **参考方向：** 生成所有非负整数五元组 \((a_1,\ldots,a_5)\)、和为 3 的 \((a_i/3)\)，共 35 个；按整数五元组字典升序排列并赋 index 0..34。方向和为 1，故范数非零。
5. **Association：** 对 S 中每个候选和方向 w 计算
   \[
   d(v,w)=\left\|v-\frac{v^\top w}{\|w\|^2}w\right\|^2,
   \]
   关联到最小距离方向，距离差不超过 \(10^{-12}\) 时取最低 index。已接受 fronts 的候选也关联并初始化 niche count。
6. **Niching：** 仅维护 \(F_L\) 中未选候选。选择其关联方向集合中 niche count 最小者；并列方向按 index 排序后用 selection_niching stream 均匀随机选一个。若该方向无剩余候选，将它从本轮可用方向集移除并重试。
7. **niche count=0：** 在该方向剩余候选中选关联距离最小者；距离并列取 canonical hash 最小者。
8. **niche count>0：** 在该方向按 canonical hash 排序后的剩余候选中，用 selection_niching stream 均匀随机选一个。
9. 每次选择后从 \(F_L\) 移除该候选、增加该方向 niche count，直到补足 12。

该算法使用预先固定的 seeded random niching，不冒充 R1 的确定性 niching 变体。所有方向枚举、ASF、归一化 fallback、关联、随机选择前后列表、niche count 和 RNG 消费均写入日志。

### 6.4 RNG streams

每个 seed 的 `init`、`random_proposal`、`variation`、`selection_niching` 流种子为：

\[
\mathrm{int.from\_bytes}(\mathrm{SHA256}("D092-R2|seed|stream")_{bytes[0:8]},"big"),
\]

其中 `seed` 和 `stream` 替换为实际十进制 seed 与流名。init 在臂间共享；其他流按 arm×seed 独立实例化，但派生不含 arm ID，使 A1/A4 可完全对齐。A2 的随机 niching 只消费 selection_niching，不影响 variation。

## 7. F4：环境回执、策略安全约束和硬约束

### 7.1 非硬约束的合法拒绝回执

`CONTRACT_BLOCKED` 和 `DEPENDENCY_BLOCKED` 是格式正确、tool/route 存在的 COMPENSATE 请求被环境拒绝的回执；没有发生非法状态转移。它们记为 soft `contract_blocked_attempts` 和 `dependency_blocked_attempts`，用于反馈和性能解释，但不直接成为非法状态转移或硬违规。

若未来要把这些 attempts 作为硬门，必须另立“额外策略安全约束”版本，不能借用环境非法转移名称。本 R2 不作此扩张。

### 7.2 六类硬约束的统一字段

| 字段 | 精确来源与计数 | hard/soft |
|---|---|---|
| `invalid_action_count` | 环境 observation=`INVALID_ACTION` 的事件数；格式、动作类型、tool/route 不合法 | hard |
| `unauthorized_action_count` | 在 dispatch 前，动作不属于下述公开允许集合的请求数；被拦截的请求不送入环境 | hard，额外策略安全约束 |
| `illegal_state_transition_count` | 独立转移监视器发现状态不在 `{NOT_COMMITTED,COMMITTED,PARTIAL,COMPENSATED}`，或实际转移与冻结环境参考转移不一致 | hard |
| `pending_count` | episode 结束时 `pending_compensation` 原始数量 | hard，若大于 0 |
| `duplicate_count` | 环境 `DUPLICATE_COMPENSATION` 事件和 report duplicate 数量一致时的原始数量 | hard |
| `runtime_abort_count` | episode 的 `runtime_forced_abort`，取 0 或 1 | hard，若大于 0 |

公开允许集合按状态计算：合法 `ESCALATE`、合法 `STOP_SAFE`；`WAIT`；`RETRY_WORKFLOW`；`VERIFY` 仅限 tool ID 存在；`COMPENSATE` 仅限 tool/route 存在且 typed policy 的公开动作掩码允许。动作格式或 ID 不存在属于 INVALID；格式合法但 mask 禁止属于 unauthorized。当前环境没有独立 unauthorized 字段，adapter 必须在 dispatch 前计算；监视器或 mask 无法判定时 run INVALID，不得默认填 0。duplicate 事件数与 report duplicate 数量不一致时同样 run INVALID。

每个动作采用唯一归因优先级 `unauthorized > invalid_action > duplicate > illegal_state_transition`，避免同一动作重复计数。pending 和 runtime abort 是 episode 终止状态，单独计数。`CONTRACT/DEPENDENCY_BLOCKED` 不进入上述非法转移字段。

`constraint_episode` 表示该 episode 六类硬约束任一大于 0；候选可行要求 96 场景六类原始计数之和全部为 0。历史环境 `constraint_violation` 仍保留为 legacy duplicate/pending 指标，但不冒充 R2 的完整硬约束。

### 7.3 不可行严重度与最终候选

不可行候选统一排序键为：

```text
(any_duplicate, any_unauthorized, illegal_state_transition_count,
 invalid_action_count, pending_count, runtime_abort_count,
 total_hard_events, canonical_genome_hash)
```

该键只用于搜索诊断和 survivor 补足，不用于最终成果选择。最终没有可行候选时输出 `NO_FEASIBLE_CANDIDATE`。

## 8. 最终候选选择

从全部 unique evaluated archive 过滤六类硬约束均为 0 的候选，求五维 Pareto 非支配集合，再依次按：

1. `min(R3,R4)` 最大化；
2. `R3+R4` 最大化；
3. Conditional Recovery 最大化；
4. Harm 最小化；
5. Recovery Cost 最小化；
6. canonical genome hash 升序。

有限原始数值参与选择，差值不超过 \(10^{-12}\) 为并列。必要指标 None/NaN/Inf 或缺失使 run INVALID。每个 arm×seed 独立选择，不挑最佳 seed。

## 9. F6：行为 fingerprint 的 canonical schema

### 9.1 标量规范化

- None→JSON null；bool 保持 true/false；整数保持 JSON integer。
- 有限 float 先对 ±0 统一为 0.0，否则使用 `float(format(x,".12g"))` 的 12 位有效数字规范化，再编码为 JSON float。
- NaN/Inf 为 INVALID；字符串保留 UTF-8；字典键排序；列表顺序不变。
- 所有对象使用 compact JSON：`ensure_ascii=False`、`sort_keys=True`、`separators=(",",":")`、`allow_nan=False`。

### 9.2 Trace phenotype

每场景事件按真实执行顺序排列，每事件仅含：

```text
{"action":[字符串...], "observation":字符串,
 "cost":规范化数值, "tick":整数}
```

96 个条目按 `scenario_id` 字典升序，每条为 `{"scenario_id":ID,"events":[...]}`。该 bundle 的 canonical JSON SHA-256 是 `trace_phenotype_sha256`。

### 9.3 Outcome signature

96 个条目按 scenario_id 升序，每条仅含：`scenario_id`、`class_success`、`task_success`、`conditional_recovery_success`、`correct_escalation`、`residual_side_effects`、`min_reachable_harm`、`avoidable_harm`、`action_cost`、`recovery_cost`、`decision_count`、`constraint_episode`、第 7.2 节六个硬约束原始字段、`policy_selected_escalation`、`runtime_forced_abort`、`final_tool_states`。`final_tool_states` 是键排序的 string→state 字典。该 bundle 的 canonical JSON SHA-256 是 `outcome_signature_sha256`。

联合 phenotype 为 `{"outcome_signature_sha256":...,"trace_phenotype_sha256":...}` 的 canonical JSON SHA-256。所有 hash 均对 UTF-8 字节计算 SHA-256；账本版本绑定上述 schema。

## 10. F6：固定 probe contrasts 与独立预算

基准 genome \(g^*\) 固定为：`cycle_mode=ALT_AND_FILTER`、`fallback_enabled=true`、`completion_guarded=true`、`harm_reorder_budget=8`、`probe_wait=1.0`。

| Probe | 相对 \(g^*\) 的唯一变化 | 分支锚点 scenario ID |
|---|---|---|
| P00 | 无，基准 | 全部锚点 |
| P01 | cycle_mode=OFF | `d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r0` |
| P02 | cycle_mode=FILTER_ONLY | 同 P01 |
| P03 | fallback_enabled=false | `d090r|train|d090_MULTI_ROUTE|D3_DEPENDENT_ABORT|r0` |
| P04 | completion_guarded=false | `d090r|train|d090_FANOUT_DELAY|D3_DEPENDENT_ABORT|r1` |
| P05 | harm_reorder_budget=None | `d090r|train|d090_DEEP_CHAIN|D3_DEPENDENT_ABORT|r1` |
| P06 | harm_reorder_budget=4 | 同 P05 |
| P07 | harm_reorder_budget=12 | 同 P05 |
| P08 | probe_wait=0.0 | `d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r1` |
| P09 | probe_wait=2.0 | 同 P08 |

10 个 genomes 都在全部 96 个 Train 场景执行一次，设计量为 **960 probe episodes**，与正式 96×96 搜索预算完全分账，无 cache 复用。probe panel 的排序 96-ID hash 为 `cccb84511a84f3bcd1dd7141b83fb278459e0267cf00a332e96f6d7cb6da6934`。

P01/P02 检查互依环/alternate 分支，P03 检查 fallback，P04 检查 completion gate，P05–P07 检查 harm 开关及阈值，P08/P09 检查 WAIT/VERIFY 顺序。每个位点除预定分支证据外还保存全部 96 场景的 trace/outcome 差异。

probe 只用于编码可辨识性 PASS/HOLD，不用于调参、选择 scenario、修改阈值、训练反馈或选择候选。probe 表现不是 Validation 或算法提升证据。本轮未执行这 960 个 rollouts。

## 11. M1/M2：轨迹等价与穷举参考上界

### 11.1 A1/A4 trajectory equivalence

对每个 seed 比较 A1/A4 的初始化顺序、每 proposal 的 canonical genome、parent IDs、operator/block/locus、round、attempts/cache、完整 rows、survivor、RNG 消费和最终候选。忽略 arm 标签及纯反馈元数据；其余必须完全一致。A4 的零反馈概率计算不得消费额外 variation 随机数。

任何差异均为 `M1_EQUIVALENCE_FAIL`，必须定位实现/流消费原因，相关比较 NO_CLAIM。A3−A1 与 A3−A4 不得被包装成两份相互独立的科学证据。

### 11.2 Train-only exhaustive reference

在所有正式臂结果和日志锁定后，单独评价全部 144 genomes×96 scenarios，共 **13,824 episodes**，仅执行一次。它使用独立 `EXHAUSTIVE_REFERENCE` 账本，不重复按 seeds 执行，不与前述 probe/search 共用缓存。

该参考用于报告每个选中结果相对已知 Train 最优的 search gap，不参与调参、反馈、候选选择或算法竞争。96 评价只覆盖 66.7% 空间，D-092 的科学价值是检验结构化演化/反馈能否在不完整枚举下接近参考上界，不证明大规模可扩展性，也不允许声称胜过完整枚举。

## 12. F7：统计、无效 seed 与 NO_FEASIBLE

### 12.1 终点与判据不变

R3 为 24 个 R3 场景正确升级均值；R4 为 24 个 R4 场景成功均值；Conditional Recovery 为 R1+R2 共 48 场景均值；Harm/Cost 为全部 96 场景均值。先 family 内等权再对 6 families 等权，同时保存简单全场景均值作核查。

主比较 A3−A1 与直接消融 A3−A4：五 seed R3 均值差至少 \(1/24\)，至少 4/5 seeds 的配对差严格大于 \(10^{-12}\)，R4/CondRec 均值差不小于 0，Harm 均值差不大于 0，且双方五个最终候选全部可行。A1−A0、A2−A1 为次要探索比较。五个 seeds 固定为 `{711,822,933,1044,1155}`；报告逐 seed、均值、中位数、样本标准差、配对差和完整资源账本，不作确认性 p-value 或泛化主张。

### 12.2 无效与无可行候选

- 任一配对 seed 出现 hash/log/dispatch 错误、不足 96 unique、attempt cap、episode 中断、 phenotype collapse 或其他 INVALID，涉及比较为 `INCOMPLETE / NO_CLAIM`；不得删除该 seed、替换 seed 或只用剩余四个计算“4/5”。
- 预算和日志完整但最终 `NO_FEASIBLE_CANDIDATE` 的 run 保留为已完成搜索结果，不伪造指标为 0。涉及它的比较为 `HOLD_NO_FEASIBLE / NO_CLAIM`；五个配对候选全部可行后才计算五 seed 均值和 4/5 条件。
- 4/5 的分母始终是预注册五 seeds。无效或无可行配对不进入均值且使该比较 NO_CLAIM，不能从剩余样本计算替代判据。
- phenotype collapse、反馈来源违规、A1/A4 非等价也使相关比较 NO_CLAIM。

### 12.3 基础设施重跑

只允许对首个 proposal 之前发生的、可由日志证明的纯基础设施 preflight 故障使用同一 seed、同一哈希重跑一次。已经产生 proposal 或 rollout 后不得因崩溃、负面结果或预算不足重跑。不得替换或新增 seed；首次和重跑日志都保留。运行器异常、超时或资源不足若发生在任何 rollout 后，均按 INVALID 处理。

## 13. M3/M4：运行环境与统一账本

### 13.1 目标执行环境

未来执行锁固定为：CPython **3.11.9**、NumPy **1.26.4**、Ubuntu **22.04 LTS**、**x86_64**，`PYTHONHASHSEED=0`。只使用标准库与 NumPy；不引入未审查的演化框架。

实现锁必须保存精确 interpreter build、OS/libc/kernel、CPU architecture、NumPy wheel SHA-256、BLAS/LAPACK 信息、完整依赖清单和 hash-locked requirements。安装使用 `pip install --require-hashes`；数值容差统一为 \(10^{-12}\)。当前没有声称该目标环境已经部署。

### 13.2 账本字段一致性

每个 arm×seed 独立记录：attempts、unique evaluations、cache hits、duplicate proposals、full episodes、partial episodes、中断原因、无效原因；另记录 probe 960 和 exhaustive 13,824 的独立资源账本。

每个 episode 的硬约束字段始终是且仅是：`invalid_action_count`、`unauthorized_action_count`、`illegal_state_transition_count`、`pending_count`、`duplicate_count`、`runtime_abort_count`。另设 `constraint_episode` 和两个 soft blocked-attempt 字段。所有指纹/选择/统计章节引用同一 schema，不再出现五类/六类混写。

每个 proposal 保存 ID、round、父代 IDs、operator/block/locus、canonical genome、cache/duplicate 状态、unique ordinal、96 rows 引用、五维 fitness、六类硬约束、三类 phenotype hashes、survivor/反馈/RNG 明细和最终选择理由。缺失任一必要字段为 `INCOMPLETE_LEDGER / INVALID`。

## 14. 静态测试规格与 R2 闭合矩阵

只允许以下静态/合成测试，不运行 genome search 或 probe：

- 预算：初始 12 attempts、7×12 unique、96 unique、9,216 episodes、384 cap、重复计数、原子中断；
- 控制流：父代固定、mutation 单父、crossover 两不同父、A0 无放回、每轮 12 unique、A3 的 1,152-row 反馈集合；
- NSGA-III：ASF 已知答案、极端点、奇异/零跨度 fallback、35 方向唯一顺序、最后 front、niche=0 与 >0 分支和独立 RNG；
- 约束：blocked receipts 不误计、六类硬字段唯一归因、unauthorized mask、无重复计数；
- 指纹：标量/None/浮点/顺序的稳定 canonical hash；
- 统计：无效 seed、NO_FEASIBLE、不可替换 seed、五对完整前 NO_CLAIM；
- A1/A4 数值控制流等价与 144/96/66.7% 算术。

| 项 | R2 关闭依据 | 状态 |
|---|---|---|
| F1 控制流 | 第 4 节 μ/λ/7 rounds、父代、A0、survivor 时点 | SPEC_CLOSED |
| F2 预算 | OFFER 唯一伪代码，初始化计 attempt，384 含初始 | SPEC_CLOSED |
| F3 NSGA-III | 第 6.3 节 canonical ASF/normalization/niching/RNG | SPEC_CLOSED |
| F4 硬约束 | 第 7 节 soft blocked 与六类 hard 分离 | SPEC_CLOSED |
| F5 反馈边界 | 第 5 节 post-rollout reward 和 unsuccessful escalation | SPEC_CLOSED |
| F6 指纹/probe | 第 9–10 节 canonical hashes、10 genomes、960 独立 episodes | SPEC_CLOSED |
| F7 无效统计 | 第 12 节五对完整、NO_FEASIBLE、无替换 seed | SPEC_CLOSED |
| M1 A1/A4 | 第 11.1 节逐轨迹等价与 NO_CLAIM | SPEC_CLOSED |
| M2 144 空间 | 第 3、11.2 节 66.7% 与独立穷举参考 | SPEC_CLOSED |
| M3 runtime | 第 13.1 节精确目标环境和 hash lock 责任 | SPEC_CLOSED |
| M4 日志 | 第 13.2 节六类硬字段与独立资源账本 | SPEC_CLOSED |

## 15. 下一门禁

**最终状态：`READY_FOR_INDEPENDENT_REVIEW`。**

下一会话只能独立审查 R2。不得由修订者自行批准实验。审查后仍需实现授权、实现一致性复审和用户明确批准；此前禁止实现搜索器/adapter、执行 probe、genome search、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑 D-090 或修改 main。
