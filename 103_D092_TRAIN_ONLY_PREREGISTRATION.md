# 103 — D-092 Train-only 动态失败反馈演化预注册 R2.1

**协议版本：** `D092-R2.1-PREREGISTRATION`
**状态：** `READY_FOR_INDEPENDENT_REVIEW / NOT FROZEN / NOT RUN`
**历史版本：** `103_D092_TRAIN_ONLY_PREREGISTRATION_R0.md`、`103_D092_TRAIN_ONLY_PREREGISTRATION_R1.md`、`103_D092_TRAIN_ONLY_PREREGISTRATION_R2.md`
**最高审查依据：** `106_D092_R2_INDEPENDENT_REVIEW.md`
**唯一科学问题：** 在相同真实评价预算下，动态失败反馈能否比标准 NSGA-II 找到更好的安全恢复策略？

R2.1 只定向关闭 F8–F15：真实底层 genome 映射、attempt 级回执、公开动作/状态约束、NSGA-III 坐标系、信息接口、probe/collapse 判据、多目标 search gap 和 PRNG。μ=12、λ=12、12+7×12=96 unique evaluations、384 attempts、五臂、主次比较、五 seeds、反馈矩阵和统计门槛全部继承 R2，不作修改。

本文件只是可执行协议与静态/合成测试规格。没有实现搜索器或 typed adapter，没有执行 probe、genome search、穷举参考或候选选择。

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

目标 schema/evaluator/ledger 分别为 `D092R2_1_TYPED_GENOME_V2_1`、`D092R2_1_EVALUATOR_V2_1`、`D092R2_1_LEDGER_V2_1`。新实现尚不存在；实现审查必须追加 typed adapter、搜索器、反馈、账本、运行时锁文件的真实哈希。任何不匹配均为 `INVALID_HASH_BINDING`。

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

### 3.2 F8：typed genome 到 D090Genome 的唯一映射

adapter 必须先复制 `d090_genome.py` 的完整 `BASE`，再同时覆盖下表所有目标字段，构造 `D090Genome`。不得只切换一个 boolean 或把 `None` 直接赋给数值字段。

| typed 字段/值 | `pair_rule` | `pair_race_alternate` | `exhaustive_fallback` | `fallback_mode` | `completion_gate` | `completion_mode` | `harm_first_ordering` | `harm_order_mode` | `harm_budget_threshold` | `delay_probe_wait` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cycle_mode=OFF` | 1 | false | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 |
| `cycle_mode=FILTER_ONLY` | 0 | false | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 |
| `cycle_mode=ALT_AND_FILTER` | 0 | true | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 |
| `fallback_enabled=false` | 保持 | 保持 | false | 0 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 |
| `fallback_enabled=true` | 保持 | 保持 | true | 2 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 |
| `completion_guarded=false` | 保持 | 保持 | 保持 | 保持 | false | 0 | 保持 | 保持 | 保持 | 保持 |
| `completion_guarded=true` | 保持 | 保持 | 保持 | 保持 | true | 1 | 保持 | 保持 | 保持 | 保持 |
| `harm_reorder_budget=None` | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | false | 0 | **8** | 保持 |
| `harm_reorder_budget=4/8/12` | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | true | 1 | **4/8/12** | 保持 |
| `probe_wait=0.0/1.0/2.0` | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | 保持 | **0.0/1.0/2.0** |

“保持”指同一 typed genome 的其他映射结果，而不是可自由选择的默认值。`harm=None` 的中性数值占位固定为 **8**；只有 `harm_first_ordering=true AND harm_order_mode!=0` 才允许该阈值进入 `_priority()` 的数值比较。关闭 fallback 时必须同时使 `exhaustive_fallback OR fallback_mode==2` 为 false；关闭 completion 时必须同时使 `completion_gate OR completion_mode>=1` 为 false，并排除 `completion_mode==2`。除上述十个底层字段外，其他继承字段逐值等于 `BASE`，不得搜索或修改。

静态/合成验收必须包含：(1) 144 个 typed genomes 映射后的完整底层 canonical JSON 仍有 144 个唯一值；(2) typed→D090Genome→typed 往返完全相等；(3) 每个高层取值逐项等于上表，而非只改变部分控制字段；(4) 三个 OFF/false/None 条件的 OR/数值边界断言；(5) 所有未映射字段与 `BASE` 完全相等；(6) 第 10 节 P00–P09 的展开逐项相等。

### 3.3 Canonical genome JSON

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

### 5.1 F12：信息边界与两个不可混用接口

真实 `report()` 同时含公开结果和 label-derived 字段。R2.1 不允许把该字典直接交给优化器；trusted evaluator 在**完整 Train episode 结束后**先投影，再交付下列两个接口：

- `optimizer_reward_view`：只允许 `scenario_id`、`class_success`、`task_success`、`conditional_recovery_success`、`correct_escalation`、`residual_side_effects`、`avoidable_harm`、`action_cost`、`recovery_cost`、`decision_count`、`pending_compensation`、`duplicate_compensation`、legacy `constraint_violation`、`policy_selected_escalation`、`safe_stop`、`runtime_forced_abort`、六类硬约束和两个 soft blocked-attempt 聚合、第 5.2 节公开 attempt ledger，以及逐项仅含 `action/observation/cost/tick` 的 trace。字段不在 allowlist 即不得出现。fitness 的 R3/R4/CondRec 分层在 trusted evaluator 内完成后只交付聚合数值；不向优化器暴露标签列。
- `audit_only_view`：完整 `report()`、原始 `label`、`min_reachable_harm`、`classify_scenario()` 输出、hidden-outcome-derived diagnostics、完整 outcome-signature bundle 和审计哈希。只能由 evaluator/独立审计器访问，不能传给 policy、variation、survivor、feedback selector、候选选择器或任何其他搜索组件；只能写受控审计日志，搜索日志仅保留 opaque hash。

策略仍只接收环境现有 `public_view()`，不得接收上述任一 report view。原始 `label`、`min_reachable_harm`、`classify_scenario()` 调用、hidden route outcomes、真实 delay/resolve_at、未来结果、Validation/Test 或锁箱字段均不得进入 optimizer-visible rows。`class_success`、`avoidable_harm` 和分层 fitness 是明确允许的 post-rollout reward，但不能反读其生成过程或在 rollout 前调用。

第 9.3 节含 `min_reachable_harm` 的 outcome signature 仅由 `audit_only_view` 计算；优化器最多接收 opaque `outcome_signature_sha256`，不能接收原始 bundle 或反查表。每次视图创建记录 `view_type`、字段排序 allowlist hash、源 episode ID 和接收者；若 optimizer view 出现额外键、audit view 被搜索组件访问，或哈希反查表暴露给搜索组件，立即 `INFORMATION_BOUNDARY_VIOLATION / INVALID`。

### 5.2 F9：attempt-level 回执账本、反馈集合和六项特征

\(U_t\) 始终是上一轮恰好 12 个新唯一 offspring，因此 \(N_t=12\times96=1{,}152\)。cache/duplicates 不重复加权，初始池不进入 offspring feedback。

每次通过语法和 public mask 的 `COMPENSATE(tool,route)` dispatch 分配一个 `compensation_attempt_id`：`dispatch_ordinal` 在每个 episode 从 0 开始、仅对通过 grammar/mask 的 COMPENSATE 递增；对该 ordinal 计算
`SHA256(canonical_json({"dispatch_ordinal":n,"scenario_id":ID}))`，使用完整 32 字节十六进制值；`(episode_reference,compensation_attempt_id)` 是账本主键。记录 tool、route、dispatch tick、dispatch observation、terminal receipt、terminal tick、来源 VERIFY ordinal 和 `terminal_recorded` boolean。语法 invalid 或 mask unauthorized 的请求不创建 attempt。

归因规则如下：

1. 原 dispatch 返回 `FAILED`、`DEPENDENCY_BLOCKED` 或 `CONTRACT_BLOCKED` 时，立即记录该 attempt 的唯一 terminal failure；`TIMEOUT` 不是 terminal receipt。
2. delayed attempt 由 `VERIFY(tool)` 完成时，通过该 tool 当前唯一 pending route 回连原 attempt；只有首次得到 `COMPENSATED` 或 `FAILED` 才写 terminal receipt。若同 tool 有多个 pending route 或找不到原 attempt，账本 INVALID。
3. 无 pending 的 VERIFY 即使重复返回 `last_receipt=FAILED`，也只是历史观测，不创建 attempt、不修改 terminal receipt、不增加任何反馈分子。尚早的 VERIFY 返回 `PENDING` 也不是 terminal failure。
4. 每个 attempt 最多一个 terminal receipt。`ALREADY_COMPENSATED`、dispatch 时 `PENDING`、`DUPLICATE_COMPENSATION` 和未解决的 `TIMEOUT` 均不进入 r/d 分子；未解决 attempt 留在分母并由 p 特征独立反映。
5. 软 blocked 的计数单位也是唯一 attempt ID，不是任意 trace observation。每个 attempt 在 `{FAILED,DEPENDENCY_BLOCKED,CONTRACT_BLOCKED}` 中至多贡献一次。

令 \(\mathcal C_t\) 为 \(U_t\) 的全部唯一 compensation attempt IDs，\(C_t=|\mathcal C_t|\)，\(\mathcal F_t\) 为其中 terminal receipt 属于上述三类的 IDs，\(\mathcal D_t\) 为其中 `DEPENDENCY_BLOCKED` IDs。定义

\[
r_t=\frac{|\mathcal F_t|}{\max(1,C_t)},\qquad
 d_t=\frac{|\mathcal D_t|}{\max(1,C_t)}.
\]

因为 \(\mathcal D_t\subseteq\mathcal F_t\subseteq\mathcal C_t\)，必有 \(0\le d_t\le r_t\le1\)。立即失败、延迟失败、重复 VERIFY、重复 COMPENSATE、blocked 和未决 pending 的合成账本测试必须逐项验证这一不变量。其余四个特征保持 R2 定义：

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
3. **Normalization（F11，统一使用 translated coordinates）：** 极端点矩阵唯一地定义为
   \[
   E_{j i}=\bar f_i(e^j)=f_i(e^j)-z_i^*,\qquad j,i\in\{1,\ldots,5\},
   \]
   即第 \(j\) 列是第 \(j\) 个极端点的**平移后**五维向量，绝不能使用 raw \(f(e^j)\)。解 \(E x=\mathbf1\)，并令 translated intercept \(a_j=1/x_j\)。仅当矩阵非奇异、解和所有 \(x_j,a_j\) 有限且所有 \(a_j>10^{-12}\) 时接受该超平面；任一条件失败即对**所有维度**使用 translated fallback \(a_i=\max_{s\in S}\bar f_i(s)\)。无论哪种路径，均有
   \[
   scale_i=a_i\quad(\text{不是 }a_i-z_i^*),\qquad f_i^n=\bar f_i/scale_i.
   \]
   若 `scale_i<=1e-12`，该零跨度目标的所有归一化值固定为 0、用于除法的 scale 记录为 1，同时另存 `raw_scale=a_i` 和 `zero_span=true`；否则使用上式。fallback 的最大值同样只在 translated objectives 上计算。仅将 [-1e-12,0] 的数值误差截为 0，其他负值 INVALID。

   非零 ideal-point 合成测试固定为 \(z^*=(10,20,30,40,50)\)，五个极端点的 translated 向量分别为 \(2e_1,4e_2,5e_3,8e_4,10e_5\)，另有点 \(\bar f=(1,1,1,1,1)\)。必须有 \(E=\operatorname{diag}(2,4,5,8,10)\)、\(a=scale=(2,4,5,8,10)\)、该点 \(f^n=(0.5,0.25,0.2,0.125,0.1)\)；任何再次减 \(z^*\) 的实现均失败。另测奇异 E 的 translated-max fallback 与零跨度路径。
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

### 6.4 F15：冻结 PRNG engine、API 与 common random numbers

唯一生成器为 CPython **3.11.9** 标准库 `random.Random`（MT19937）；不得使用 NumPy Generator/PCG64、全局 `random` 模块状态或系统熵。每个 stream 执行：
`rng=random.Random(); rng.seed(seed_integer,version=2)`。种子字符串固定为 `D092-R2|<seed>|<stream>`，其中 stream 为 `init`、`random_proposal`、`variation`、`selection_niching`，seed 用无多余前导零的十进制；字符串按 UTF-8 编码，SHA-256 取 `digest[0:8]`，再用 `int.from_bytes(...,"big")` 得到 `seed_integer`。保留 `D092-R2` 前缀是为了不改变 R2 已通过的随机序列设计，不表示协议身份未升级。

所有 API 只采用下列形式：

- 连续均匀数：`rng.random()`；fair coin 为 `rng.random()<0.5`。
- 从长度 n 的已排序序列均匀取一项：`index=rng.randrange(n)`；不使用 `choice()` 的隐含实现。
- 无放回抽样：从 canonical 升序的可变 pool 反复执行 `j=rng.randrange(len(pool)); item=pool.pop(j)`。初始 12 项和 A0 每轮 12 项均如此，不用 `sample()` 或 shuffle。
- crossover 两个不同父代：先 `i=rng.randrange(12)`，再 `j=rng.randrange(11)`，若 `j>=i` 则 `j+=1`；父代列表按 canonical genome hash 升序。block 继承用 fair coin，其余合法 allele 用上述 randrange。
- mutation block：调用一次 `u=rng.random()`，按 pair、fallback、completion、harm 的固定顺序累计当前 \(p_k\)，选择首个满足 `u<cumulative` 的 block；仅在末项因浮点误差未命中时选择 harm。completion block 内字段顺序固定为 completion_guarded、probe_wait，再用 randrange；其他单字段 block 不消耗字段随机数。剩余合法 allele 顺序为 cycle=`OFF,FILTER_ONLY,ALT_AND_FILTER`，两个 bool 均为 `false,true`，harm=`None,4,8,12`，probe=`0.0,1.0,2.0`；排除当前值后用 randrange 抽取。
- niching 方向并列和 niche>0 的候选选择：在预注册排序列表上使用 `randrange(len(list))`。niche=0 不消费随机数。

每次调用记录 stream、调用 ordinal、API、输入列表 hash/长度、返回值和调用前后已消费计数；不得因异常重试而静默重置流。A0 只消费 init/random_proposal，A1/A3/A4 消费 init/variation，A2 另消费 selection_niching；A4 的零反馈计算不消费随机数。

seed 派生不含 arm ID 是**有意的 common-random-numbers coupling**，不是跨臂独立随机序列。init 在五臂完全共享；同名流的初始序列相同，但不同控制流可有不同消费量。A1/A4 必须每次消费完全一致；A3 因反馈映射可与 A1 产生不同后续 genome，不能假定整条流仍逐步对齐。A2 的 niching 只能消费自己的 selection_niching，不得扰动 variation。

## 7. F4：环境回执、策略安全约束和硬约束

### 7.1 非硬约束的合法拒绝回执

`CONTRACT_BLOCKED` 和 `DEPENDENCY_BLOCKED` 是格式正确、tool/route 存在的 COMPENSATE 请求被环境拒绝的回执；没有发生非法状态转移。它们按第 5.2 节唯一 attempt 记为 soft `contract_blocked_attempts` 和 `dependency_blocked_attempts`，用于反馈和性能解释，但不直接成为非法状态转移或硬违规。public mask **明确允许**这些请求，否则相应反馈永远无法产生。

若未来要把这些 attempts 作为硬门，必须另立“额外策略安全约束”版本，不能借用环境非法转移名称。本 R2.1 不作此扩张。

### 7.2 F10：动作 grammar、public mask 与状态转移

#### 7.2.1 唯一动作 schema 和公开前置条件

动作必须是以下六种**精确 tuple**之一；JSON 账本中保存等长字符串数组：

| 动作 | 精确 schema | public mask 前置条件（只读 public view） |
|---|---|---|
| WAIT | `WAIT()` | active episode 内允许 |
| RETRY_WORKFLOW | `RETRY_WORKFLOW()` | `permission`：允许，环境可返回 soft `PERMISSION`；`timeout_before`：允许；`partial_recover`：仅 current tool=`COMPENSATED` 且该 tool 无 pending 时允许，其他 current 状态拒绝 |
| VERIFY | `VERIFY(tool)` | tool ID 必须存在；存在即允许，包括 pending、非 pending 和重复 VERIFY |
| COMPENSATE | `COMPENSATE(tool,route)` | tool/route 必须存在；存在即允许，**不因** contract unavailable、requires 未满足、tool state 或 pending 预先拦截 |
| ESCALATE | `ESCALATE()` | active episode 内允许，包括仍有 pending；最终 pending 由硬约束处理 |
| STOP_SAFE | `STOP_SAFE()` | 同 ESCALATE |

active episode 指 runner 尚未 task success、无 terminal action 且 decision_count<24；runner 在 task success、terminal action 或 cap 后不再请求动作。mask 只能使用公开 `terminal_fault/current_tool/tools/routes/pending`，不能使用 hidden outcome、delay 或 resolve_at。

**判定顺序固定为 grammar → public mask → environment。** 非 tuple/list、空动作、未知 kind、长度不对、非字符串参数、tool/route 不存在均直接进入环境 `INVALID_ACTION` 路径并计 `invalid_action_count`，不得先判 unauthorized。语法正确但 mask=false 才计 `unauthorized_action_count`，且不送入环境、不创建 compensation attempt、不改变 tick/state。语法和 mask 均通过后调用原环境。此顺序替代 R2 旧的 `unauthorized > invalid` 表述，消除同一请求双重归因。

#### 7.2.2 冻结环境参考转移表

下表是独立监视器的完整参考。`same` 表示整个 tool-state map 不变；除 WAIT 外 tick 不变。pending/last_receipt 另按原环境逐步核对。delayed success 的真实语义是**在 COMPENSATE dispatch 当下**将 tool 改为 COMPENSATED，之后 VERIFY 只揭示回执，不再次改变 tool state。

| 条件/动作 | observation | tool state、pending 与其他效果 |
|---|---|---|
| WAIT | `WAITED` | state same；tick `t→t+1` |
| RETRY，permission | `PERMISSION` | state same |
| RETRY，timeout_before，current=`NOT_COMMITTED` | `COMMITTED` | 仅 current `NOT_COMMITTED→COMMITTED` |
| RETRY，timeout_before，current 为其他已知状态 | `INVALID_ACTION` | state same；计 invalid |
| RETRY，partial_recover，current=`COMPENSATED` 且 current 无 pending | `COMMITTED` | 仅 current `COMPENSATED→COMMITTED` |
| RETRY，partial_recover，其他 current 状态 | public mask 拒绝；直接环境参考为 `PARTIAL` | state same；正式 adapter 中计 unauthorized，不 dispatch |
| VERIFY，tool 有 pending 且 tick<resolve_at | `PENDING` | state/pending same |
| VERIFY，tool 有 pending 且 tick≥resolve_at | `COMPENSATED` 或 `FAILED` | state same；仅清除该 route pending/resolve_at 并写 last_receipt |
| VERIFY，无 pending，tool=`COMPENSATED` | `COMPENSATED` | state/pending same |
| VERIFY，无 pending，tool 非 COMPENSATED，有 last_receipt | 最后非空 last_receipt | state/pending same；不得新增反馈 failure |
| VERIFY，无 pending、无 last_receipt | `NOT_COMMITTED` | state/pending same |
| COMPENSATE，tool=`COMPENSATED`、tool 有 pending、route 非幂等 | `DUPLICATE_COMPENSATION` | state same；duplicate 加 1 |
| COMPENSATE，tool=`COMPENSATED`，不属于上行 | `ALREADY_COMPENSATED` | state same |
| COMPENSATE，tool 非 COMPENSATED、tool 有 pending | `PENDING` | state/pending same |
| COMPENSATE，contract unavailable | `CONTRACT_BLOCKED` | state same；写公开 last_receipt |
| COMPENSATE，requires 未全 COMPENSATED | `DEPENDENCY_BLOCKED` | state same；写公开 last_receipt |
| 实际 route attempt，成功、immediate | `COMPENSATED` | 仅目标 tool 从 `{NOT_COMMITTED,COMMITTED,PARTIAL}` 的原状态转为 `COMPENSATED`；attempts 加 1，无 pending |
| 实际 route attempt，成功、delayed | `TIMEOUT` | dispatch 当下仅目标 tool 从 `{NOT_COMMITTED,COMMITTED,PARTIAL}` 的原状态转为 `COMPENSATED`；attempts 加 1，设置 pending/resolve_at |
| 实际 route attempt，失败、immediate | `FAILED` | state same；attempts 加 1，无 pending |
| 实际 route attempt，失败、delayed | `TIMEOUT` | state same；attempts 加 1，设置 pending/resolve_at |
| ESCALATE / STOP_SAFE | `ESCALATED` / `STOPPED_SAFE` | tool states same；terminal_action 分别为 ESCALATE/STOP_SAFE |
| 语法/ID/route 无效 | `INVALID_ACTION` | state/pending same；计 invalid |

因此允许的 tool-state edge 仅为上表非 same 的边：`NOT_COMMITTED→COMMITTED`（retry）、`COMPENSATED→COMMITTED`（retry）、以及 `{NOT_COMMITTED,COMMITTED,PARTIAL}→COMPENSATED`（成功 COMPENSATE dispatch），且必须满足对应 fault、action、pending 和 route outcome 条件。原环境允许对 NOT_COMMITTED tool 发出语法正确的 COMPENSATE，因此不得自行把该成功边改称环境非法转移。除已列 retry 边外的逆向边、工具间状态互换、未知状态或 delayed VERIFY 再次改状态都属于非法转移。

#### 7.2.3 逐步监视与六类硬约束

监视器每步保存 `(before_public_state, action, mask_result, observation, after_public_state)`、pending/attempt/tick/terminal 前后值和 reference-row ID。它独立从 before+action+允许的回执类别推导 after，再与实际 after 比较；不能仅检查状态属于允许集合。环境隐藏参数只供独立参考实现选择期望分支，不向 policy/optimizer 暴露。无匹配行、状态不一致、pending/tick/terminal 不一致或无法判定时记录非法转移并使 run INVALID，不得默认填 0。

| 字段 | 精确来源与计数 | hard/soft |
|---|---|---|
| `invalid_action_count` | grammar 通过但环境返回 `INVALID_ACTION`，以及直接送入环境的语法无效动作；每动作最多一次 | hard |
| `unauthorized_action_count` | grammar 通过但 public mask=false；每请求一次，不 dispatch | hard，额外策略安全约束 |
| `illegal_state_transition_count` | 独立监视器发现未知状态或与上表状态/pending/tick/terminal 参考行不一致；每动作最多一次 | hard |
| `pending_count` | episode 结束时 `pending_compensation` 原始数量 | hard，若大于 0 |
| `duplicate_count` | 环境 `DUPLICATE_COMPENSATION` 事件和 report duplicate 数量一致时的原始数量 | hard |
| `runtime_abort_count` | episode 的 `runtime_forced_abort`，取 0 或 1 | hard，若大于 0 |

dispatch 后按 `invalid_action > duplicate > illegal_state_transition` 作动作级唯一归因；非法转移若与 invalid/duplicate 同时出现，另存 monitor anomaly 供 INVALID 审计但不重复增加动作级硬计数。pending 和 runtime abort 是 episode 终止状态，单独计数。duplicate 事件数与 report duplicate 数量不一致时 run INVALID。`CONTRACT/DEPENDENCY_BLOCKED`、`PERMISSION`、`ALREADY_COMPENSATED` 和普通 `PENDING` 回执本身不进入非法转移字段。

`constraint_episode` 表示该 episode 六类硬约束任一大于 0；候选可行要求 96 场景六类原始计数之和全部为 0。历史环境 `constraint_violation` 仍保留为 legacy duplicate/pending 指标，但不冒充 R2.1 的完整硬约束。

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

此 bundle 明确属于 `audit_only_view`；其中 `min_reachable_harm` 不得进入 optimizer-visible row。搜索器只能接收 opaque hash 作多样性计数，不能访问 bundle、字段值或 hash→审计记录的查询接口。

联合 phenotype 为 `{"outcome_signature_sha256":...,"trace_phenotype_sha256":...}` 的 canonical JSON SHA-256。所有 hash 均对 UTF-8 字节计算 SHA-256；账本版本绑定上述 schema。

## 10. F8/F13：固定 probe 展开、PASS/HOLD 与独立预算

### 10.1 P00–P09 的最终底层 genome

基准 \(g^*\) 固定为 `cycle_mode=ALT_AND_FILTER`、`fallback_enabled=true`、`completion_guarded=true`、`harm_reorder_budget=8`、`probe_wait=1.0`。按第 3.2 节映射，十个 probe 的**完整可变底层字段**如下；未列字段全部等于 `BASE`，不存在其他差异。

| Probe | pair_rule | pair_race_alternate | exhaustive_fallback | fallback_mode | completion_gate | completion_mode | harm_first_ordering | harm_order_mode | harm_budget_threshold | delay_probe_wait |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P00 | 0 | true | true | 2 | true | 1 | true | 1 | 8 | 1.0 |
| P01 | 1 | false | true | 2 | true | 1 | true | 1 | 8 | 1.0 |
| P02 | 0 | false | true | 2 | true | 1 | true | 1 | 8 | 1.0 |
| P03 | 0 | true | false | 0 | true | 1 | true | 1 | 8 | 1.0 |
| P04 | 0 | true | true | 2 | false | 0 | true | 1 | 8 | 1.0 |
| P05 | 0 | true | true | 2 | true | 1 | false | 0 | 8 | 1.0 |
| P06 | 0 | true | true | 2 | true | 1 | true | 1 | 4 | 1.0 |
| P07 | 0 | true | true | 2 | true | 1 | true | 1 | 12 | 1.0 |
| P08 | 0 | true | true | 2 | true | 1 | true | 1 | 8 | 0.0 |
| P09 | 0 | true | true | 2 | true | 1 | true | 1 | 8 | 2.0 |

对应 typed contrast：P01=OFF、P02=FILTER_ONLY、P03=fallback false、P04=completion false、P05=harm None、P06=harm 4、P07=harm 12、P08=probe 0、P09=probe 2。实现测试必须逐项构造上表，不允许由 policy 的默认值补全。

### 10.2 固定锚点和语义比较

以下 ID 简写均为既有 96 Train IDs；`Q0` 是 R2 已指定的 pair 锚点，`Q0b` 是依据公开依赖与 `_pair_filtered_available()` 源码预先加入的 OFF-vs-FILTER 对照，不是按 probe 结果挑选：

| 简写 | scenario_id |
|---|---|
| Q0 | `d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r0` |
| Q0b | `d090r|train|d090_PAIR_RACE|D4_BLOCKED_COMPENSATION|r0` |
| Q1 | `d090r|train|d090_MULTI_ROUTE|D3_DEPENDENT_ABORT|r0` |
| Q2 | `d090r|train|d090_FANOUT_DELAY|D3_DEPENDENT_ABORT|r1` |
| Q3 | `d090r|train|d090_DEEP_CHAIN|D3_DEPENDENT_ABORT|r1` |
| Q4 | `d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r1` |

对 probe a、b 和场景 s，语义 trace \(T(a,s)=[(action_1,observation_1),\ldots]\) 按执行顺序仅保留动作和观测。定义 \(\Delta_{a,b}(s)=\mathbf1[T(a,s)\ne T(b,s)]\)。它不看 cost、tick 或 outcome；只有 action/observation 序列改变才使 \(\Delta=1\)。完整 trace/outcome 仍保存作审计，**仅 cost/tick 改变一律不算 PASS**；outcome 改变可辅助解释但不能替代下表要求的动作分支证据。

probe instrumentation 可从 public view 记录 `normal_available_count`、`fallback_candidate_count`、`fallback_selected`、`active_count/public_min_harm`、completion override、普通/tight priority 选项、budget_remaining、pending route 的 WAIT elapsed 和即将执行的动作；这些标记只能由公开字段推导，不能读取 hidden schedule。对照必须锁定第一处分叉前的公共 before-state，不能只凭两份最终汇总猜测分支。

### 10.3 逐项 PASS/HOLD 判据

| Probe | 必须同时满足的预注册条件；任一不满足即 HOLD |
|---|---|
| P00 | 底层展开与第 10.1 节逐项相等；96 场景完整、无缺失 ledger、视图/mask/monitor 均有效；作为基准不要求与自身有 trace 差异，也不以性能好作为通过条件。 |
| P01 | 在 Q0，P00 首个 COMPENSATE 为 `(A或B,alternate)`，P01 为 `(C,primary)`，且 \(\Delta_{P01,P00}(Q0)=1\)。在 Q0b，cycle pending 时 P01 能继续 `COMPENSATE(C,primary)`，而 P02 在同一步为 `WAIT()`，且 \(\Delta_{P01,P02}(Q0b)=1\)。 |
| P02 | 在 Q0，P02 首个 COMPENSATE 为 `(C,primary)`，与 P00 的 `(A或B,alternate)` 不同，且 \(\Delta_{P02,P00}(Q0)=1\)。在 Q0b 满足上一条 P02=`WAIT()`、P01=`COMPENSATE(C,primary)` 的 filtering 证据。 |
| P03 | 在 Q1 的共同前缀出现 normal available 为空、public fallback candidate 非空且可继续派发的状态；P00 的下一动作选择其中一个 fallback route，P03 在相同 before-state 不得选择该 fallback route，且 \(\Delta_{P03,P00}(Q1)=1\)。 |
| P04 | 在 Q2 的共同前缀出现 `active>public_min_harm`、普通或 fallback route 可用、`_can_dispatch_more=true`，且 P00 completion gate 阻止停止；P00 下一动作非 terminal，P04 在相同 before-state 为 ESCALATE/STOP_SAFE，且 \(\Delta_{P04,P00}(Q2)=1\)。 |
| P05 | 在 Q3 的共同前缀出现 `budget_remaining<=8`、至少两个候选、普通 priority 与 tight priority 选择不同；P00 选 tight 项、P05 选普通项，且 \(\Delta_{P05,P00}(Q3)=1\)。另验证 P05 的两个 harm 开关均关闭，未发生 None 数值比较。 |
| P06 | 在 Q3 的共同前缀出现 `4<budget_remaining<=8` 且普通/tight 选项不同；P00 选 tight 项、P06 选普通项，且 \(\Delta_{P06,P00}(Q3)=1\)。 |
| P07 | 在 Q3 的共同前缀出现 `8<budget_remaining<=12` 且普通/tight 选项不同；P07 选 tight 项、P00 选普通项，且 \(\Delta_{P07,P00}(Q3)=1\)。 |
| P08 | 在 Q4 的首个尚未改变 learned delay 的 delayed-route 确认点，公共 before-state 为 pending、elapsed=0、无其他可派发工作；P08 下一动作为 `VERIFY(tool)`，P00 为 `WAIT()`，且 \(\Delta_{P08,P00}(Q4)=1\)。 |
| P09 | 在 Q4 的同一初始 delayed-route 序列经过一次共同 WAIT 后，elapsed=1、learned delay 尚未因 PENDING 修改；P00 下一动作为 `VERIFY(tool)`，P09 为 `WAIT()`，且 \(\Delta_{P09,P00}(Q4)=1\)。 |

若动作/观测不同但未出现指定分支，或出现指定分支但无 \(\Delta=1\)，都为 HOLD，不允许改看其他场景、其他 outcome 或仅 cost/tick 差异来“补救”。十个 probe 都在全部 96 个 Train 场景执行一次，设计量为 **960 probe episodes**，与正式 96×96 搜索预算完全分账，无 cache 复用。probe panel 的排序 96-ID hash 为 `cccb84511a84f3bcd1dd7141b83fb278459e0267cf00a332e96f6d7cb6da6934`。所有 96 场景的 trace/outcome 差异与预定分支证据一并保存。

### 10.4 正式 run 的 phenotype-collapse 定量门

对每个 arm×seed 的 **96 个 unique evaluated genomes**，分别计算第 9 节三类完整 96-scenario bundle hash 的唯一数量：
\[
H_{trace}=|\{h_{trace}(g):g\in\mathcal A_{96}\}|,\quad
H_{outcome}=|\{h_{outcome}(g):g\in\mathcal A_{96}\}|,\quad
H_{joint}=|\{h_{joint}(g):g\in\mathcal A_{96}\}|.
\]
每类预期计数为 96；定义 `phenotype_collapse = (H_trace<2 OR H_outcome<2 OR H_joint<2)`。任一成立即触发第 12.2 节 `INVALID / NO_CLAIM`，不得用 genome hash 数量替代 phenotype 数量，也不得删除重复 phenotype 后重算。probe 任一预定位点对照 HOLD 时，后续 probe 结果只作诊断，不启动正式搜索。

probe 只用于编码可辨识性，不用于调参、选择 scenario、修改阈值、训练反馈或选择候选。probe 表现不是 Validation 或算法提升证据。本轮未执行这 960 个 rollouts。

## 11. M1/M2：轨迹等价与穷举参考上界

### 11.1 A1/A4 trajectory equivalence

对每个 seed 比较 A1/A4 的初始化顺序、每 proposal 的 canonical genome、parent IDs、operator/block/locus、round、attempts/cache、完整 rows、survivor、RNG 消费和最终候选。忽略 arm 标签及纯反馈元数据；其余必须完全一致。A4 的零反馈概率计算不得消费额外 variation 随机数。

任何差异均为 `M1_EQUIVALENCE_FAIL`，必须定位实现/流消费原因，相关比较 NO_CLAIM。A3−A1 与 A3−A4 不得被包装成两份相互独立的科学证据。

### 11.2 F14：Train-only exhaustive reference 与多目标 search gap

在所有正式臂结果和日志锁定后，单独评价全部 144 genomes×96 scenarios，共 **13,824 episodes**，仅执行一次。它使用独立 `EXHAUSTIVE_REFERENCE` 账本，不重复按 seeds 执行，不与前述 probe/search 共用缓存。

令 \(\mathcal E\) 为 144 个评价中满足六类硬约束均为 0 的可行 archive，\(f(h)\in\mathbb R^5\) 为第 6.1 节最小化目标。Pareto front 为
\[
\mathcal P=\{h\in\mathcal E:\nexists h'\in\mathcal E,\ h'\prec h\},
\]
其中 \(h'\prec h\) 当且仅当所有 \(i\) 满足 \(f_i(h')\le f_i(h)+10^{-12}\)，且至少一个 \(i\) 满足 \(f_i(h')<f_i(h)-10^{-12}\)；这与第 8 节并列容差一致。对每个正式臂×seed 的可行选中候选 \(g\)，必须同时报告：

1. **Component-wise regret：**
   \[
   z_i^{\mathcal E}=\min_{h\in\mathcal E}f_i(h),\qquad
   \rho_i(g)=f_i(g)-z_i^{\mathcal E},\quad i=1,\ldots,5.
   \]
   五项分别报告原目标单位和 regret；\(z^{\mathcal E}\) 只是分量下界，**不得拼成一个声称实际存在的“最优 genome”**。另报告 `on_exhaustive_front`、dominates g 的 front 点数和 g 在 exhaustive archive 中的 Pareto rank。
2. **到 exhaustive Pareto front 的归一化距离：** 令 \(R_i=\max_{h\in\mathcal P}f_i(h)-\min_{h\in\mathcal P}f_i(h)\)，零跨度集合 \(\mathcal I_0=\{i:R_i\le10^{-12}\}\)，非零集合 \(\mathcal I_+=\{1,\ldots,5\}\setminus\mathcal I_0\)。当 \(\mathcal I_+\ne\varnothing\) 时
   \[
   D(g,\mathcal P)=\min_{h\in\mathcal P}
   \sqrt{\frac1{|\mathcal I_+|}\sum_{i\in\mathcal I_+}
   \left(\frac{f_i(g)-f_i(h)}{R_i}\right)^2}.
   \]
   保留分子中的有符号目标差，不取 absolute/positive part；min 和平方定义最终非负距离。排除并记录所有零跨度维度；若五维全部零跨度且 front 非空，则定义 \(D=0\)。若 g 属于 \(\mathcal P\)，必须有 D=0（数值容差 \(10^{-12}\)）。

若 exhaustive 无可行 archive/front，或选中结果不可行/为 `NO_FEASIBLE_CANDIDATE`，则所有 gap 字段为 `undefined` 并标 `REFERENCE_GAP_HOLD`，**不得填 0**。任一 NaN/Inf、空 front 或未解释的重复 genome 也使参考 INVALID。

该参考只提供描述性 search gap，不参与调参、反馈、候选选择、主比较或算法竞争，也不设新的通过阈值。96 评价只覆盖 66.7% 空间，D-092 的科学价值是检验结构化演化/反馈能否在不完整枚举下接近参考，不证明大规模可扩展性，也不允许声称胜过完整枚举。

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

每个 proposal 保存 ID、round、父代 IDs、operator/block/locus、canonical typed genome、完整展开 D090Genome、cache/duplicate 状态、unique ordinal、96 rows 引用、五维 fitness、六类硬约束、三类 phenotype hashes、survivor/反馈/RNG 明细和最终选择理由。每 episode 另保存第 5.2 节完整 compensation-attempt ledger、第 5.1 节两个视图的 allowlist/access 记录，以及第 7.2 节逐步 `(before,action,mask,observation,after)` reference-row 监视记录。缺失任一必要字段为 `INCOMPLETE_LEDGER / INVALID`。

## 14. 静态/合成测试规格与 R2.1 闭合矩阵

本节只是**未来实现审查的测试规格**，不是已执行测试。当前只允许文档、公式和映射静态检查；不运行 genome search、960 probe 或 exhaustive reference。

- F8 mapping：144 映射唯一性、往返一致、P00–P09 展开、BASE 不变、关闭 OR 条件和 harm=None 的中性 8/无数值比较；
- F9 receipt：立即失败、delayed VERIFY 失败、重复 VERIFY、重复 COMPENSATE、blocked、pending 各一例，验证 attempt 一对一和 \(0\le d_t\le r_t\le1\)；
- F10 action/state：六类 tuple、未知 kind/tool/route、mask 判定顺序、所有 RETRY 分支、blocked 可观测、duplicate、terminal pending、表中每条 state/pending/tick/terminal 边及 delayed success 的 dispatch 时点；
- F11 NSGA-III：ASF、极端点、35 方向、last front、niche=0/>0，以及第 6.3 节非零 ideal=(10,20,30,40,50) 的精确 E/intercept/scale/归一化答案、translated-max fallback 和零跨度；
- F12 view：optimizer allowlist 多一个字段即失败、label/min_reachable_harm/hidden outcome 不可达、audit view 不得进入搜索组件、outcome 只暴露 opaque hash；
- F13 probe：固定语义 projection 对 cost/tick-only 差异判 false，对 action/observation 差异判 true；逐 P00–P09 检查 PASS/HOLD 规格完整；H_trace/H_outcome/H_joint 的 96/2/1 边界；此处不执行 probe；
- F14 gap：合成的非对角五维 front 检验 regret、min-distance、零跨度排除、on-front D=0、无可行 front/不可行选中为 undefined，且不存在拼接的理想 genome；
- F15 PRNG：UTF-8/digest[0:8]/big-endian 已知答案、random.Random 固定 API、pop/randrange 无放回顺序、双父映射、A1/A4 消费等价和 A2 niching 流隔离；
- R2 已通过的预算、控制流、指纹、统计和 A1/A4 等价规格保持不变：12 initial+7×12=96、9,216 episodes、384 cap、1,152 feedback rows、96/144=66.7%。

| 项 | R2.1 关闭依据 | 规格状态 |
|---|---|---|
| F1 控制流 | 第 4 节 μ/λ/7 rounds、父代、A0、survivor 时点 | SPEC_CLOSED |
| F2 预算 | OFFER 唯一伪代码，初始化计 attempt，384 含初始 | SPEC_CLOSED |
| F3 NSGA-III | 第 6.3 节 canonical ASF/niching；F11 另补唯一 translated normalization | SPEC_CLOSED |
| F4 硬约束 | 第 7 节 soft blocked 与六类 hard 分离；F10 补完整接口 | SPEC_CLOSED |
| F5 反馈边界 | 第 5 节 post-rollout reward；F9/F12 补唯一事件和接口 | SPEC_CLOSED |
| F6 指纹/probe | 第 9–10 节 hashes、probe 展开、量化 PASS/HOLD | SPEC_CLOSED |
| F7 无效统计 | 第 12 节五对完整、NO_FEASIBLE、无替换 seed | SPEC_CLOSED |
| M1 A1/A4 | 第 11.1 节逐轨迹等价与 NO_CLAIM | SPEC_CLOSED |
| M2 144 空间 | 第 3、11.2 节 66.7%、独立穷举与 F14 多目标 gap | SPEC_CLOSED |
| M3 runtime/RNG | 第 6.4、13.1 节精确 PRNG 与目标 runtime | SPEC_CLOSED |
| M4 日志 | 第 13.2 节硬字段、attempt、view 和逐步监视账本 | SPEC_CLOSED |
| F8 genome mapping | 第 3.2、10.1 节唯一底层映射和十项展开 | SPEC_CLOSED / REVIEW_PENDING |
| F9 receipt attribution | 第 5.2 节唯一 attempt、delayed VERIFY、分母不变量 | SPEC_CLOSED / REVIEW_PENDING |
| F10 action/state | 第 7.2 节 grammar、mask、转移表和监视器 | SPEC_CLOSED / REVIEW_PENDING |
| F11 normalization | 第 6.3 节 translated E/intercept/scale/fallback 和非零 ideal 测试 | SPEC_CLOSED / REVIEW_PENDING |
| F12 view isolation | 第 5.1、9.3、13.2 节 allowlist、audit-only 和访问日志 | SPEC_CLOSED / REVIEW_PENDING |
| F13 probe/collapse | 第 10.2–10.4 节固定分支、语义差异和 H<2 门槛 | SPEC_CLOSED / REVIEW_PENDING |
| F14 search gap | 第 11.2 节五项 regret 与 front-normalized distance | SPEC_CLOSED / REVIEW_PENDING |
| F15 PRNG/CRN | 第 6.4 节 engine/API/seed bytes/common random numbers | SPEC_CLOSED / REVIEW_PENDING |

## 15. 下一门禁

**最终状态：`READY_FOR_INDEPENDENT_REVIEW`。本文件未被起草者标记为 APPROVED 或 FROZEN，所有 F8–F15 均需独立复核。**

下一会话只独立复核 106 号报告 F8–F15 的数学、源码相容性、主控制流和边界条件，不重开已通过的预算、五臂、seeds、反馈矩阵或统计门槛。定向复核通过后，下一阶段立即进入 **typed adapter + static/synthetic algorithm tests** 的实现与实现一致性审查，不再做大范围文档重构；实现审查通过和用户明确批准前仍不得执行 probe、genome search 或 exhaustive reference。

当前禁止实现搜索器/adapter、执行 probe、genome search、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑 D-090 或修改 main。规格完整不等于算法有效或创新成立。
