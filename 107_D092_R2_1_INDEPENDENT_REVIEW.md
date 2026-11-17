# 107 — D-092 R2.1 F8–F15 独立定向复审

**审查日期：** 2026-11-17  
**仓库/分支：** yujian777555/kaitibaogao / pilot-a-stateful-recovery  
**审查对象：** commit ab915751d8bb95d5f3e76b1d1e4c259f9819cfcc 的 canonical R2.1、R2/R1 快照、13 项源码依赖、D-090 Train manifest、F8–F15 数学/接口/Probe 定义  
**最终决定：** REQUEST_CHANGES / HOLD  
**R2.1 状态：** REVIEWED_NOT_ACCEPTED / NOT FROZEN / NOT RUN  
**授权边界：** 只读独立复审；没有修改代码，没有实现 adapter/searcher，没有运行 probe、genome search、exhaustive reference 或 Validation/Test。

---

## 1. Git、文件与数据身份

| 项目 | 独立核验 |
|---|---|
| branch HEAD | ab915751d8bb95d5f3e76b1d1e4c259f9819cfcc，匹配 |
| main HEAD | 683b3fe7fc52c86e917d523fdc6bbb13abbfd653，未修改 |
| ahead / behind | 315 / 0 |
| R2.1 canonical Git blob | 773f39e5984c20d011a8d89245ecf52790886088 |
| R2 snapshot Git blob | 9196c717f2cb79ecd21a25e055a77afe0db03f59 |
| R1 snapshot Git blob | f5dc28e67d648344cfd8465956f51e1f0582baf4 |
| R2 snapshot preservation | 与父提交 canonical R2 逐字节一致 |
| R1 preservation | 与父提交 R1 逐字节一致 |
| R2.1 commit 文件 | 恰好 7 份文档，无算法源码/实验数据修改 |
| 新 workflow runs | 0 |
| check runs / commit statuses | 0 / 0 |
| 新 artifact | 无 |

远端 branch HEAD 与报告一致。GitHub 远端 API 不提供本地工作树状态，本审查不声称独立检查了执行者本地 clean。

### 1.1 Train 数据与 Probe 锚点

- Train manifest：96 个 scenario IDs，R1/R2/R3/R4 各 24 个。
- R2.1 列出的 6 个固定 probe 锚点均存在于冻结 manifest。
- R2 snapshot 与 R1 snapshot 未被覆盖。

### 1.2 源码依赖闭包发现一项哈希错误

R2.1 §2.2 的 `experiments/d088_recovery/d088_policies.py` 声明 Git blob：

`afe2ed253704d2bf9e3f4e57f6e0a14f04f14be5`

独立读取同一 commit 的实际 Git blob：

`afe2ed253704d2bf9f3e3f57f6e0a14f04f14be5`

两者不一致（中间字符不同）。本次核对的其他 12 项源码 blob 均匹配。因此不能接受 R2.1 中“13/13 源码 blob 匹配”的声明。canonical SHA 是否匹配不消除 Git blob 身份字段错误；必须修正表格并重算闭包检查。

---

## 2. 总体决定

R2.1 对 F8–F15 的规格补充有明显进展。五字段映射、translated-coordinate normalization、attempt-level 计数框架、action/state table、Pareto reference gap 和随机数 API 均比 R2 更具体。

但仍有四个直接影响实验有效性的阻断问题：

1. F9：attempt ID 在不同 genome 的同一 scenario episode 间会重复；分母集合没有明确使用 composite primary key；立即 COMPENSATED 成功回执没有明确关闭 ledger attempt。
2. F11：矩阵下标公式与“第 j 列”文字描述相互矛盾；现有对角线合成测试无法识别转置错误。
3. F12：optimizer allowlist 中的 per-scenario 字段会直接暴露 label class；scenario_id 还可与带标签 manifest 连接。
4. F13：P03 的 fallback 触发条件在固定 Q1 上不可能成立；P07 的预算区间对照在固定 Q3 的共同轨迹上不可达。

此外，F10 还有 malformed ID 的环境异常路径未闭合；F15 的 RNG 初始化写法与“禁止系统熵”声明不完全一致。故 R2.1 不批准进入 probe 或正式搜索。

---

## 3. F8–F15 逐项审查

### F8 — PASS（规格层）

五字段到 D090Genome 底层字段的映射与绑定源码一致：

- cycle OFF / FILTER_ONLY / ALT_AND_FILTER 分别控制 pair_rule 与 pair_race_alternate；
- fallback false 同时关闭 exhaustive_fallback 与 fallback_mode==2；
- completion false 同时关闭 completion_gate 与 completion_mode>=1/==2；
- harm=None 关闭 harm_first_ordering/harm_order_mode，使用中性数值 8，避免 None 进入比较；
- probe_wait 对应 delay_probe_wait，0/1/2 的继承策略语义明确。

144 个 typed combinations 的字段映射在规格上是一一对应的。此项接受为 SPEC_ACCEPTED；实际 adapter 往返与 144 unique 测试仍未运行，不能标记实现 PASS。

### F9 — REQUEST_CHANGES：attempt identity 与 terminal receipt 仍不完整

**问题 A：跨 genome attempt ID 冲突。**

R2.1 规定：

`compensation_attempt_id = SHA256({"dispatch_ordinal": n, "scenario_id": ID})`

但同一 Train scenario 会在每个 offspring genome episode 中重复执行。对同一 scenario 的第一个 COMPENSATE dispatch，不同 genome episode 都会得到相同的 attempt ID。

R2.1 虽将 `(episode_reference, compensation_attempt_id)` 作为 ledger primary key，但随后把 `C_t` 定义为 `U_t` 中全部 unique compensation attempt IDs 的集合大小，没有明确说集合元素必须是 composite key。若按裸 ID 去重，12 个 offspring 对同一 scenario 的 attempt 会被合并，导致分母低估。

**R2.2 必须明确：**

- `episode_reference` 的唯一 schema，例如包含 arm、seed、proposal/genome ID、scenario ID；
- `C_t)、`F_t)、`D_t` 全部基于 `(episode_reference, compensation_attempt_id)` composite keys；
- 或将 episode_reference 纳入 attempt hash 输入；
- 合成测试覆盖同一 scenario 在 12 个不同 genome episodes 的相同 dispatch ordinal，必须得到 12 个独立 ledger attempts。

**问题 B：立即成功没有 terminal-record 规则。**

5.2 第 1 条只明确立即 FAILED/DEPENDENCY_BLOCKED/CONTRACT_BLOCKED 写 terminal failure；第 2 条明确 delayed VERIFY 首次得到 COMPENSATED/FAILED 时写 terminal receipt。真实环境的 immediate successful COMPENSATE 会直接返回 COMPENSATED，但没有明确规则将它写为 terminal success。

R2.2 必须补充 immediate COMPENSATED 的 terminal receipt、terminal tick、terminal_recorded=true 规则，并明确 ALREADY_COMPENSATED、PENDING、DUPLICATE_COMPENSATION 等非失败 dispatch receipt 是否关闭本次 dispatch ledger record。每个已完成 dispatch 必须有唯一、可审计的 receipt lifecycle。

### F10 — PARTIAL：主状态表基本匹配源码，但 malformed-action 路径仍有缺口

状态转移、retry 条件、delayed success 在 dispatch 时修改 tool state、blocked receipts 作为 soft outcome 等内容与绑定环境大体一致。

但 R2.1 规定非字符串参数、未知 tool/route 等语法错误直接进入环境 INVALID_ACTION 路径。实际 `DependencyRecoveryEnv.step()` 对若干 unhashable 参数会在字典成员检查时抛出 TypeError，例如：

- `VERIFY([tool])` 的 tool membership；
- `COMPENSATE([tool], route)` 的 tool membership；
- `COMPENSATE(tool, [route])` 的 route membership。

这些输入不会自然落入 `_record(..., "INVALID_ACTION", ...)`。R2.2 必须规定总函数式 grammar validator：所有 malformed 输入在环境字典查询前被识别，并通过安全 sentinel/明确的 runner-side invalid receipt 记录原始请求与唯一 invalid_action_count；不得抛异常或丢失原始请求。

另外，必须修正 §2.2 的 `d088_policies.py` Git blob SHA。其余 action/state 内容可保留，不需要重新设计六种动作或硬约束。

### F11 — REQUEST_CHANGES：E 矩阵方向的公式与文字矛盾

R2.1 写：

[
E_{ji}=ar f_i(e^j)
]

这一定义表示**第 j 行**是第 j 个 extreme point 的五维 translated vector；但紧接着文字写“第 j 列是第 j 个极端点的平移后五维向量”。

按公式解 `E x = 1` 与按文字构造列矩阵会得到转置的不同实现。当前非零 ideal 合成测试使用对角矩阵，转置后完全相同，无法发现这一问题。

**R2.2 必须：**

1. 明确 E 的行/列约定；若保留现有公式，应将文字改为“第 j 行”；
2. 增加一个非对称、非对角的 translated extreme-point matrix；
3. 明确给出解 `x`、intercepts `a_i=1/x_i`、scale 和归一化结果的手算期望值；
4. 测试必须在错误转置时失败。

其他 translated fallback、zero-span 规则可以保留。

### F12 — REQUEST_CHANGES：optimizer_reward_view 仍泄露标签类别

R2.1 allowlist 包含 `conditional_recovery_success` 和 `correct_escalation`。

绑定环境 `DependencyRecoveryEnv.report()` 定义：

- `conditional_recovery_success` 仅在 label 属于 R1/R2 时为非 None；
- `correct_escalation` 仅在 label 为 R3 时为非 None；
- 两者均为 None 时可识别 R4。

因此，仅观察这两个字段的 None/non-None pattern，optimizer 就能恢复 scenario label class。这与“不得向优化器暴露标签列”的声明冲突。

此外，`scenario_id` 可与同一 Train manifest 中带 label 的 scenario records 连接，进一步削弱隔离。

R2.2 必须将接口拆成明确的两层：

- evaluator-internal reward rows：允许 evaluator 使用 label 计算分层指标，但只在可信 evaluator 内部；
- optimizer-visible fitness summary：仅输出预注册的聚合数值、六类硬约束、反馈聚合所需公开 attempt receipts 和必要 opaque IDs。

从 optimizer-visible allowlist 移除 per-scenario `conditional_recovery_success`、`correct_escalation`、可连接 label 的 `scenario_id`；如需 episode correlation，使用不能映射回 manifest 的 opaque episode token。若保留 per-scenario `class_success`/avoidable_harm，必须说明它们是允许的 reward，而不是标签或可 join 的标签索引。

同时，明确 audit_only_view 的哈希生成与搜索器访问边界；opaque hash 只能用于预注册的相等性/多样性计数，不能暴露 hash→audit record 查询接口。

### F13 — REQUEST_CHANGES：至少两个固定 Probe 判据在冻结场景上不可达

#### P03 / Q1：fallback 分支不会触发

Q1 是 `d090_MULTI_ROUTE|D3_DEPENDENT_ABORT|r0`。场景中 A primary requires C，C primary requires A，形成 A↔C 活跃依赖环；A/C 都有 alternate route。

P00 的 genome 是 ALT_AND_FILTER，即 `pair_rule=0`、`pair_race_alternate=true`。绑定 D090Policy 的 `_primary_deadlocked()` 会识别 A/C 的 cycle primary 为 deadlocked；继承 D088Policy 的 alternate 许可规则因此使 A/C alternate 进入 normal available set。pair filter 保留 cycle member routes。

而 `_available_or_fallback()` 只在 normal `_available()` 为空时才调用 exhaustive fallback。因此 Q1 上 normal available 非空，P00 不会进入 fallback 分支。P03 只关闭 fallback，不能产生其要求的“normal available empty + fallback candidate nonempty”共同状态。

**P03 当前 HOLD。** 必须从冻结 96 Train 场景中选择一个真实满足“normal available empty 且 fallback candidate nonempty”的固定 anchor，或者重新设计一个不改变数据集的可达 probe contrast；先用源码级状态推演证明，再冻结，不得运行 probe 后再挑场景。

#### P07 / Q3：budget 8–12 的 priority contrast 不可达

Q3 是 `d090_DEEP_CHAIN|D3_DEPENDENT_ABORT|r1`。冻结链为 A requires B、B requires C、C 无依赖；D 为 NOT_COMMITTED。A/B/C primary 和 alternate 都是 delayed receipt，delay=2，primary/alternate outcome 序列为 false→true。

按绑定 D088/D090 policy 的公共控制流：

- 初始只有 C primary 可派发；
- C primary 失败后，C primary/alternate 的竞争状态出现在 remaining budget 19；
- C alternate 失败后，C primary/alternate 的下一竞争状态出现在 remaining budget 14；
- C primary 成功后继续 B primary；B primary 首次失败后，需先处理仍 pending 的 C receipt，之后下一次可比较的 B primary/alternate 状态在 remaining budget 7。

因此 P00 threshold=8 与 P07 threshold=12 在两个较早竞争点均走 ordinary priority，在后续可比较点均走 tight priority；不存在 P07 声称的 `8 < budget_remaining <= 12` 且普通/tight priority 选择不同的共同 before-state。P07 无法提供其预注册分支证据。

**P07 当前 HOLD。** 必须更换为冻结 Train 中经源码级状态推演证明可达的预算窗口 anchor，或修改一个可达且不改变原 genome 搜索空间的 probe contrast；不允许事后换窗口。

#### Phenotype-collapse threshold

`H_trace/H_outcome/H_joint < 2` 只检测“完全退化为单一 phenotype”，并不检测 96 个候选中仅有 2 个不同 phenotype 的近乎完全塌缩。若研究意图确实只是阻止全同，建议命名为 `complete_phenotype_collapse`；若要作为多样性门，则需预注册更有区分度的阈值。不得在看到正式搜索结果后修改。

P01/P02、P04、P05/P06、P08/P09 的判据本轮未发现同等级的明确矛盾；这不等于 rollout 已验证。

### F14 — PASS（规格层）

五个 objective-wise regret、exhaustive Pareto front、front-normalized minimum distance、zero-span dimensions、empty-front/不可行选中 undefined 规则已足够明确；没有把五个目标各自最优值拼成虚假 genome。

穷举仍为未来独立 13,824 episodes；当前未运行，不产生算法性能结论。

### F15 — PARTIAL：随机序列定义已基本闭合，但初始化仍调用默认系统熵

CPython 3.11.9 `random.Random`、MT19937、SHA-256 字节截取、randrange/pop、stream 隔离和 common-random-numbers 语义均已具体化。

但当前伪代码是：

`rng = random.Random(); rng.seed(seed_integer, version=2)`

无参数构造 `Random()` 会先执行默认 seed 初始化，然后才显式 reseed。虽然显式 reseed 后最终输出流仍可确定，但这与“不得使用系统熵”的文字不完全一致。

建议直接冻结为 `rng = random.Random(seed_integer)`，并说明 integer seed 不依赖 version 参数；或明确允许一次不影响后续状态的初始化后立即 reseed。为严格可审计，优先使用前者。

---

## 4. 独立审查矩阵

| 项目 | 结论 | 说明 |
|---|---|---|
| Git/R2/R1 snapshot | PASS | HEAD、R2 逐字节快照、R1 保留通过 |
| Train IDs / 6 anchors | PASS | 96 IDs 和 6 个锚点存在 |
| 源码依赖闭包 | REQUEST CHANGES | 12/13 blob 匹配；d088_policies.py SHA 错 |
| F8 genome mapping | PASS（规格层） | 与 D090Genome/D090Policy 语义一致 |
| F9 receipt accounting | REQUEST CHANGES | composite identity 与 immediate success terminal receipt 缺失 |
| F10 action/state | PARTIAL | 主表基本匹配；malformed unhashable args 路径不闭合，另修源码 blob |
| F11 NSGA-III normalization | REQUEST CHANGES | E 行列文字冲突；对角测试不能识别转置 |
| F12 information boundary | REQUEST CHANGES | per-scenario None pattern 泄露 R1/R2/R3/R4 类别，scenario_id 可 join |
| F13 probe/collapse | REQUEST CHANGES | P03 fallback 不触发；P07 budget window 不可达 |
| F14 exhaustive gap | PASS（规格层） | 五维 regret 与 front distance 定义清楚 |
| F15 PRNG/CRN | PARTIAL | 基本冻结；默认 Random() 构造与禁系统熵不一致 |

---

## 5. 唯一下一任务：R2.2 定向修订

保留 canonical R2.1 immutable snapshot：

`103_D092_TRAIN_ONLY_PREREGISTRATION_R2_1.md`

修订 canonical 103 为 R2.2，只关闭：

1. F9：composite attempt key、episode_reference schema、立即成功/非失败 receipt lifecycle；
2. F10：修正 d088_policies.py blob；补 malformed/unhashable action 的总函数式 invalid path；
3. F11：E 行列统一 + 非对称非对角 synthetic expected answer；
4. F12：删除 per-scenario label-indicating fields 和可 join label 的 scenario_id，拆分 evaluator-internal 与 optimizer-visible interface；
5. F13：更换 P03、P07 为源码推演可达的预注册对照，重写逐分支 PASS/HOLD；明确 complete collapse 与 near-collapse 的术语/门槛；
6. F15：Random(seed_integer) 或等价无系统熵初始化写法。

不得重开：

- F8 映射；
- F14 search-gap 公式；
- μ=12、λ=12、12 initial + 7×12=96 unique；
- 384 proposal attempts；
- 五臂与 A3−A1/A3−A4 主比较；
- 五个 seeds、反馈矩阵、统计门槛；
- 96 Train scenarios、manifest 和 R2/R1 snapshots。

R2.2 完成后只对上述定向问题复核。**定向复核通过后立即进入 typed adapter + static/synthetic algorithm tests 的实现审查**，不再进行大范围文档重构。

---

## 6. 当前授权边界

当前为 **REQUEST_CHANGES / HOLD**。

在 R2.2 定向复核通过前，不运行：

- adapter/searcher 的正式实现；
- 960 probe episodes；
- 96×96 genome search；
- 13,824 exhaustive reference；
- 调参或候选冻结；
- Validation/Test、Pilot B、正式 A-3b；
- 真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox；
- main merge 或跨仓库复用。

R2.2 定向复核通过后，进入 typed adapter + static/synthetic tests。实现审查通过并取得用户明确批准后，再执行 probe 和 D-092 Train-only search。

**最终结论：R2.1 的 F8 与 F14 规格可以接受；F9、F11、F12、F13 仍有实质性问题，F10/F15 有小型闭合缺口。REQUEST_CHANGES / HOLD。**
