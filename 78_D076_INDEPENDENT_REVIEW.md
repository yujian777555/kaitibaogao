# 78 — D-076 独立代码与协议复审

**复审日期：** 2026-11-10  
**复审对象：** D-076 执行交付（R4 + SBCG-NSGA-III）  
**复审基线：** `3d2dacf0871ab0f030084f6ed2d62e17ba524ddd`  
**main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`（复审时未变）  
**CI：** run [42814630988](https://github.com/yujian777555/kaitibaogao/actions/runs/42814630988) = success；R4 power run [42813004752](https://github.com/yujian777555/kaitibaogao/actions/runs/42813004752) = success。执行报告记录 290/290 tests；本复审核验了 GitHub run 状态与提交 SHA，未在本地重新运行 290 项测试。  
**数据边界：** 本复审只读代码、预注册、合成 fixtures、历史 diagnostic 汇总与 CI 元数据；未运行真实 Train/Validation 算法诊断，未读取真实 Test payload。  
**最终结论：** **REQUEST CHANGES**。R4 不可 ACCEPT；SBCG 尚不具备进入 Train/Validation 性能诊断的条件。

---

## 1. 总体判断

D-076 有真实工程进展：formal runner 已接线；五 composition roster、R4 统计 helper、Train/Test split guard、SBCG 三机制和 14 臂注册表均有代码；执行报告明确承认没有算法性能实验。这些是有价值的交付。

但本复审发现两个层面的阻断：

1. **R4 的 pre-flight 生命周期存在逻辑循环，当前真实 pre-flight 没有可达的 GO 路径。** 功效模拟也缺少任务书要求的 technical-missing 情景，并有一个 Type-I cell 超出名义水平。
2. **SBCG 的 NSGA-III 参考方向关联不是正确的标准 NSGA-III niching；M1 目标公式与冻结方案不一致；Train 到 Validation 的选择流程没有真正接通。**

因此，CI 通过和合成测试通过不能支持 R4 ACCEPT，也不能授权算法性能实验。

## 2. R4 复审发现

### R4-001 — BLOCKER：Pre-flight 把 pre-run 授权与 post-run 数据完整性混成一个门，导致循环依赖

证据：

- `run_current_preflight()` 将 `paired_rows_valid=False`、三个数据质量计数设为 `None`、`n_observed_families=0`、`family_composition_counts={}`、`design_deviation=True` 固定写入 context，见 [run_r4_preflight.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/run_r4_preflight.py#L59-L88)。
- `run_formal_preflight()` 要求 paired rows 完整、duplicate/null/metadata mismatch 为零、至少 34 个 observed families、每族恰好 5 compositions、design_deviation=false，见 [formal_preflight.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/formal_preflight.py#L116-L148)。
- 同一个 GO 又要求 `test_access_log_count=0` 和 `one_time_ledger_state=UNUSED`，见 [formal_preflight.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/formal_preflight.py#L145-L149)。
- R4 预注册 §5/§9 将该 pre-flight 作为正式 Test 执行前的必要条件；当前 pre-flight 文档也明确称 metadata-only pre-run gate。

这形成不可满足的状态：若 paired rows、observed families 和 composition counts 指的是 Test 结果，则它们必须在 Test payload 被读取和评价后才存在；但 GO 同时要求 Test 从未访问、one-time ledger 仍 UNUSED。当前 CLI 又没有提供 outcome-ledger 输入，`ledger_path` 也不能解决问题：若账本已存在，状态会变为 CONSUMED，仍违反 UNUSED。当前实际输出 HOLD 是诚实的，但不是一个可以在审批完成后自然转为 GO 的 pre-run gate。

**必须修复：** 拆成两个生命周期明确的门：

1. **Pre-run authorization/integrity gate：** 只检查审计批准、导师 MDE、用户批准、CI、冻结 manifest/code hashes、split roster、预算、seed、停止规则、Test access log=0、one-time ledger=UNUSED；不检查任何 Test outcome rows、paired completeness、family loss 或 labelled null。
2. **Post-run analysis-integrity gate：** 在获批的一次性 Test 执行完成后，检查 paired rows、duplicates、labelled null、family completeness、technical missing、design deviation，再决定是否具备确认性分析资格。此门不得再授权第二次 Test 访问。

需要新增端到端状态机测试，覆盖未批准、批准但 pre-flight 未过、一次性消费、执行成功、执行失败仍保持 consumed、post-run 完整性失败等状态。不能用人工构造的 `good_context()` 证明生产 pre-flight 可达 GO。

### R4-002 — BLOCKER：功效模拟未覆盖任务书要求的 technical missing，且 F=40 / ICC=0.20 的 Type-I 偏高

[power_r4_design.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/power_r4_design.py#L20-L70) 的 24 格只遍历：

- F = 33 / 34 / 40；
- ICC = 0 / 0.05 / 0.10 / 0.20；
- null μ=0 与 MDE μ=0.10；
- 每族固定 5 compositions。

生成器对每个 family 固定抽取 5 个 composition residual，没有 composition-level technical missing、run-level technical missing 或不利缺失机制，见 [power_hierarchical.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/power_hierarchical.py#L476-L489)。F=33 只模拟一个完整 family 少于最低门槛，并不能替代技术性缺失导致的 composition 不完整、配对损失和 family loss 情景。D-076 任务书明确要求对允许的 technical missing 进行不利情景模拟；当前交付未完成该项。

另一个需要解释的数值：执行报告 §3 中 F=40、ICC=0.20 的 null Type-I = **0.0547**，95% Wilson CI = **[0.0504, 0.0593]**。该区间下界高于名义 α=0.05。F=34、ICC=0.20 的 Type-I=0.0503、CI=[0.0462,0.0548]，则包含 0.05。

这不意味着单个 Monte Carlo cell 自动证明统计检验无效，但不能把全部 24 格描述为 Type-I 已充分校准。需要复核生成模型、学生 t 尾概率实现、种子敏感性，并在预先定义的误差容忍标准下决定是否接受。还应覆盖技术缺失后有效 family 数和每族 composition 数的分布。

**必须修复：** 增加 composition/run 层技术缺失情景、family-loss 边界和最不利缺失模式；对 F=40/ICC=.20 的 Type-I 做独立复算/多 seed 校准；报告每个关键情景的 MCSE 和区间。若不能校准，R4 保持 HOLD，不能只引用 F=34 的 0.8427 power。

### R4-003 — BLOCKER：一次性 Test gate 与正式分析 runner 没有形成受控的生产调用链

`consume_final_evaluation_once()` 目前检查审计、导师、用户批准及 manifest/code hashes，然后消费账本并调用 loader；它没有要求 pre-run pre-flight 状态为 GO，也没有验证 CI/tests 状态，见 [split_access.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/split_access.py#L84-L138)。

`run_formal_analysis()` 接收 caller-supplied ledger，默认 `analysis_split="test"`，返回 `caller_supplied_synthetic_or_unlocked_ledger`，但本身不要求 one-time gate 或 pre-flight GO，见 [formal_runner.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/formal_runner.py#L120-L182)。

这些函数可以作为底层 helper，但目前没有被证明存在一条唯一、不可绕过的生产 final-evaluation wrapper，把 pre-run GO → atomic consume → Test loader → final evaluator → post-run integrity analysis 串起来。

**必须修复：** 实现一个生产入口；该入口必须先验证 pre-run GO 与批准记录，再原子消费 ledger，随后才允许 loader 返回 Test payload，并在执行结束后运行 post-run integrity check。普通分析函数应拒绝伪装成正式 Test 执行；synthetic fixture 可显式走独立测试入口。新增端到端测试证明无论直接调用普通 runner、篡改批准字段、hash 不匹配、并发重复调用或执行失败，都不能绕过 one-time gate。

---

## 3. SBCG 算法复审发现

### SBCG-001 — BLOCKER：参考方向关联的投影距离公式错误，且 NSGA-III 基线也不是 canonical NSGA-III

在 [sbcg_runner.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/sbcg_runner.py#L39-L62)，当前代码使用：

`projection = dot(z, direction)`

然后用 `z - projection * direction` 计算垂直距离。但 Das–Dennis 方向向量被归一化为分量和为 1，并非单位二范数向量。对方向射线的正交投影系数应为：

`dot(z, d) / dot(d, d)`

否则关联距离会系统性偏离，导致个体被分配到错误参考方向。当前代码还仅按 splitting front 的 min/max 做归一化，且 niche load 从零开始，只统计当前 front，没有把前面已接受 fronts 的方向占用纳入 niche count。这不是标准 NSGA-III 的完整归一化和 niching 过程。

更重要的是，历史基线 [ea.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/ea.py#L245-L277) 也使用相同的未除以 `dot(d,d)` 的投影公式，并在每个方向中以 `min(sum(objs))` 选个体。因此注册为“canonical NSGA-III”的历史对照也不是 canonical NSGA-III。

这会直接影响算法身份和比较可信度：目前不能声称 SBCG 是在标准 NSGA-III 上增加了三个机制，也不能声称对照中的 NSGA-III 是标准基线。

**必须修复：**
- 使用经核验的 canonical NSGA-III reference-point normalization、association、niche-count 和 niching selection；
- 将标准 NSGA-III baseline 替换为可复核的 canonical 实现，保留旧实现并明确命名为 legacy/custom；
- 新增几何单元测试：已知方向的投影距离、非单位方向、尺度变换、跨 front niche occupancy、参考方向分配；
- 若不实现 canonical 算法，必须把名称改成“自定义参考方向 niching EA”，不能继续标记 NSGA-III。

### SBCG-002 — BLOCKER：M1 第三目标与冻结候选公式不一致

75 号候选明确规定 `f3 = UnnecessaryActionCost`（[75 号候选](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md#L56)）。

当前实际代码却是：

`unnec_esc + unnec_actions_r12 / 10`

见 [sbcg.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/sbcg.py#L18-L35)。配置文件也将其描述为“UnnecessaryEscalation + UnnecessaryActionCost/10”，而执行报告将其简写为 UnnecessaryActionCost。

这不是纯粹命名差异：它把不必要升级与动作成本按未经说明的 1/10 系数合成一个目标，改变 Pareto dominance 和选择结果。当前没有单位、尺度或系数依据，也没有在 75 号候选中预注册。

**必须修复：** 要么严格使用冻结的 UnnecessaryActionCost；要么在任何 benchmark 结果产生前，将该复合目标作为方法修订，给出量纲/归一化依据、系数敏感性、独立目标替代方案和新版本预注册。代码、config、报告、测试必须使用同一个明确公式。

### SBCG-003 — BLOCKER：当前所谓 Validation selection 实际在 Train archive 上完成

`run_sbcg_evolution()` 最后将 Train 进化得到的 `final_records` 传给 `select_validation_candidate()`，并明确写出 `input=train_elite_archive`、`validation_used=False`，见 [sbcg_runner.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/sbcg_runner.py#L290-L302)。

`validation_selection_report(records)` 只接受 CandidateRecord 列表，没有 split provenance 或验证来源检查；`sbcg_experiment.py` 目前只有 14 臂注册表和单臂 `run_algorithm_arm()`，没有把 Train Pareto archive 重新评估到 Validation、再按冻结规则选出最终候选的端到端流程，见 [sbcg_experiment.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/sbcg_experiment.py#L33-L166)。

当前 Train archive 的选择可以作为 Train 内部候选排序，但不能称为 Validation selection。也不能据此声称 Validation 已被限制为 selection-only。

**必须修复：** 将 Train optimizer 改为只返回冻结候选档案；增加独立的 Validation evaluation/selection 阶段，显式验证 split=validation，记录候选版本、调用次数和一次性选择结果；验证数据不得进入适应度、反例池或下一代进化。Validation selector 必须拒绝 Train/Test 来源不明的 CandidateRecord。

### SBCG-004 — MAJOR：对照矩阵尚未形成统一预算的可执行实验 orchestrator

`algorithm_specs()` 注册了 14 臂，但 `sbcg_experiment.py` 目前只提供单臂执行函数，没有统一驱动全部臂、seed、初始池、预算并写出总 ledger 的 matrix runner。预算通过调用者传入 `eval_budget`，未冻结在 `sbcg_config.json`；固定策略分支也没有验证 `len(scenarios)` 是否超过预算。

在真实诊断前，需要一个统一 orchestrator，冻结每臂唯一 simulator episode budget、初始候选池 hash、任务/seed 配对、cache 口径、固定策略评价口径和失败停止规则。固定策略的单次评价成本与 EA 搜索成本应分别报告，不得将两者混为同一个“公平预算”。

### SBCG-005 — MAJOR：SBCG runner 重复查询 offspring cache，污染 cache-hit 统计

`run_sbcg_evolution()` 在 offspring 生成时已执行 `record = evaluate(child)`，之后构造 combined population 时又执行 `evaluate(child)`，见 [sbcg_runner.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/sbcg_runner.py#L250-L263)。

第二次调用必然命中刚写入的 cache，导致每个 offspring 至少多记一次 cache hit/evaluation call。这不一定增加 unique simulator episodes，但会污染调用审计和 cache-hit 率。现有测试只检查 `unique_evaluations + cache_hits == evaluation_calls`，不能发现这种冗余二次查询。

**必须修复：** 直接复用 pending 中已得到的 CandidateRecord 构造 combined；增加精确计数测试，断言新 offspring 的 evaluator 调用次数、cache hit 和 unique evaluation 均符合预期。

### SBCG-006 — MINOR：M2 是 trace-conditioned mutation，不等于已定位因果基因

`aggregate()` 把失败决策 trace 中出现的所有 gene key 加入该 stratum；`mutate_with_record()` 再从这些 gene 中随机选一个，见 [sbcg.py](https://github.com/yujian777555/kaitibaogao/blob/pilot-a-stateful-recovery/experiments/pilot_a3b/sbcg.py#L213-L270)。

这证明变异被失败 trace 条件化，但不证明选中的 gene 是导致失败的因果基因。论文表述应使用“trace-conditioned gene mutation”，除非另有反事实/消融证据证明因果定位。建议增加随机 trace-gene mutation 对照，量化分层选择与基因定位各自贡献。

---

## 4. 复审结论与权限

| 项目 | 复审状态 | 说明 |
|---|---|---|
| R4 formal runner | REQUEST CHANGES | 有合成端到端入口，但 pre-flight / one-time gate 生命周期未闭合 |
| R4 power | REQUEST CHANGES | 缺 technical-missing 情景；F40/ICC.20 Type-I 需调查 |
| R4 preregistration | REQUEST CHANGES | 与不可达的 pre-flight 状态机需要同步修订 |
| SBCG M1 | REQUEST CHANGES | f3 与候选公式不一致 |
| SBCG NSGA-III | REQUEST CHANGES | 投影/归一化/niche counting 不符合 canonical NSGA-III |
| SBCG Validation | REQUEST CHANGES | 当前只在 Train archive 上选择 |
| SBCG budget/audit | REQUEST CHANGES | 需要统一 orchestrator 和准确 cache 计数 |
| 算法性能 | NOT RUN | 没有新的真实 Train/Validation 性能数据 |

**本复审不授予任何 Test 访问权限。**

继续禁止：
- 正式 A-3b；
- 真实 Test payload 读取或 final evaluation；
- Pilot B；
- A800/ARWM；
- 真实 LLM API；
- UndoBench TEST；
- ThinkingBox；
- 合并 main。

在以上阻断修复、重新提交审计之前，不得把 R4 标为 ACCEPTED，也不得运行 SBCG 真实 Train/Validation 性能诊断。合成测试可以继续，但必须清楚标记为 synthetic-only。

## 5. 唯一下一任务

**D-078 corrective revision：修复 R4 pre-run/post-run gate 生命周期、technical-missing power 与 Type-I 校准；修正 SBCG canonical NSGA-III niching、M1 目标公式、Train→Validation 选择链和预算/cache 计数，然后重新提交独立复审。**

本轮没有修改算法源码、没有运行真实 benchmark、没有读取 Test；只形成独立审查结论与仓库交接记录。
