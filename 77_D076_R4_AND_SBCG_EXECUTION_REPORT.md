# 77 — D-076：R4 收尾与 SBCG-NSGA-III 实现验证报告

**日期：** 2026-11-10  
**角色：** Executor  
**任务书：** `76_EXECUTOR_R4_AND_ALGORITHM_UPLIFT.md`  
**R4 状态：** **READY_FOR_INDEPENDENT_REVIEW**（不是 ACCEPTED，不是 formal GO）  
**SBCG 状态：** **IMPLEMENTED + SYNTHETIC TESTED / PERFORMANCE NOT RUN**  
**正式 A-3b：** HOLD

## 1. Git 基线与提交链

| 阶段 | SHA |
|---|---|
| 本轮起始 work HEAD | `0dc0be4419b2316a95e3878aaceee6ecae8ba88a` |
| R4/SBCG 实现提交 | `32b6914b08075775c0d9000fb7b80392c33ec26e` |
| pre-flight 与 synthetic runner 证据提交 | `e92e9af964edd6963baed41b48a24073e34f99f8` |
| CI 功效写回与 clean-clone 目标 | `4c4c62fb7213868c3c8fa98f1bdd5b83edc77212` |
| main（未修改） | `683b3fe7fc52c86e917d523fdc6bbb13abbfd653` |

最终维护提交及远端核验见本轮最终汇报；报告不把自身提交 SHA 误写为实现代码 SHA。

## 2. R4 完成情况

| 阻断项 | 本轮实际状态 | 证据 |
|---|---|---|
| 正式 runner 接线 | **完成**：frozen manifest + run ledger 直接调用 primary/secondary family-level 分析 | `formal_runner.py`；`test_64r4_formal_runner.py` 7 项；`results/r4_runner_synthetic/` |
| 冻结 outcome-blind 五 compositions | **既有实现已核验，未重复实现**：5 个主分析 + 2 个 sensitivity-only，不按结果选择 | `formal_scenario_generator.py:66-90`；`test_d064c_audit.py:142-162` |
| 功效/Type-I 10,000 MC | **完成**：F=33/34/40 × ICC 0/.05/.10/.20 × null/MDE，共 24 格 | `power_r4_design.py`；`results/r4_power_20261114/power_r4_design.json` |
| Student-t 退化一致性 | **既有实现已核验**；本轮补齐 sign-flip 中性输出与实际 seed | `test_64r4_student_t.py` 13 项；`power_hierarchical.py` |
| H2–H5 | **既有真实路径已核验**：四项 family-t、完整四项 Holm、全部 exploratory | `test_64r4_secondary_analysis.py` |
| Test 隔离与一次性 gate | **既有实现已核验**，未读取真实 Test | `split_access.py`；`test_64r4_split_guard.py` |
| R4 候选预注册 | **新增并与实现对齐** | `64_A3B_PREREGISTRATION_CANDIDATE_R4.md` |
| 真实 pre-flight | **已执行，当前 HOLD**；审批和正式 outcome ledger 均未满足 | `run_r4_preflight.py`；`results/r4_preflight/` |
| CI / clean-clone | **完成**；详见 §6 | CI runs 42813004959 / 42813004752；`results/r4_clean_clone.log` |

R4 只能提交独立 Reviewer。Executor 不自评 ACCEPTED。

## 3. 功效复核

当前 CI 原始 JSON 记录：每格 10,000 MC、base seed 20261114、24 格、逐格 seed/MCSE/95% Wilson CI。ICC=0.20 时：

| F | 类型 | Rate | MCSE | 95% CI | 逐格 seed |
|---:|---|---:|---:|---|---:|
| 34 | MDE=0.10 power | 0.8427 | 0.00364 | [0.8354, 0.8497] | 23682114 |
| 34 | null Type-I | 0.0503 | 0.00219 | [0.0462, 0.0548] | 23681114 |
| 40 | MDE=0.10 power | 0.9028 | 0.00296 | [0.8968, 0.9085] | 24282114 |
| 40 | null Type-I | 0.0547 | 0.00227 | [0.0504, 0.0593] | 24281114 |

本机独立重跑的 24 个统计格与保存 JSON 逐格一致。输入原始字节哈希在不同换行环境下可不同，因此本轮新增 `input_canonical_sha256`；当前规范化内容哈希为 `9b1d90279852843bf93d92e66dab3e726ff1e19bc14b94e07ba260fc34eb68a7`。LF/CRLF 测试证明原始哈希可变而内容哈希不变。功效仍只支持“每族恰好 5 个 compositions”的设计，不支持最低 1 的旧规则。

## 4. SBCG 源代码缺口复核

已直接检查当前代码，而非重复 75 号推测：

1. `a3_bridge.py:609-613` 的历史目标只有三维；`corr_esc`、`containment` 虽计算但不进入目标向量。
2. `ea.py:167-175` 的 `safety_battery_pass()` 只检查 duplicate/SLA，未覆盖完整硬约束集合。
3. `ea.py:139-158` 的旧 `CounterexamplePool.targeted_mutate()` 使用全局 `most_common(1)`，存在多数错误垄断风险。
4. 旧 `run_evolution()` 的最终选择仍用 `min(sum(objectives))`；该路径保留为历史对照，SBCG 不使用该规则。
5. `run_diagnostic3.py:152-155` 的历史 EA 初始化只使用 sensible-random FSM，Hand 单独评价，不进入共享精英池。

这些是代码结构缺口，不是已经证明的性能因果解释。

## 5. SBCG 实现

### M1：五维安全目标与硬约束

`sbcg.py` / `sbcg_runner.py` 实现：

- `1−CondRecSucc`、AvoidableHarm、UnnecessaryActionCost、`1−CorrectEscalation`、`1−DamageContainment`；
- Duplicate、SLA violation、invariant violation 采用 **0 容差硬约束**，不进入可补偿目标；
- 五维 Das–Dennis 参考方向：m=5、p=3、35 directions；
- 可行性优先于 Pareto 选择；不可行个体不能用 CondRecSucc 补偿。

### M2：分层反例引导

- 分层键 = task family × failure signature × safety class；
- 观察到的 S 个 stratum 均匀采样，概率 1/S，不再使用全局 most-common；
- 优先命中失败 trace 中的真实基因；空池时退回标准变异；
- 每层记录 examples、sampling_probability、sampled、gene_hits、repair_attempts、repair_success_rate 和 new_valid_individuals；
- 变异后继续执行 contract repair 与独立 genome validity 检查。

### M3：Hand-anchor 与 Pareto 选择

- 共享初始池由同一 sensible-random 池构成；Hand 只占 slot 0；no-M3 消融移除该 slot 且保留其他 59 个个体不变；
- 可行精英档案执行 fingerprint 去重、Pareto 非支配和 per-family best 覆盖保护；
- Validation 选择规则固定为：可行性 → Pareto → family coverage → worst-family CondRecSucc → 冻结字典序/fingerprint tie-break；
- 无 `sum(objectives)` 或等权标量化；没有可行候选返回 HOLD；
- `validation_selection_report()` 提供 JSON-safe 选择报告；本轮未运行真实 Validation。

### 对照与消融

`sbcg_experiment.py` 注册 14 个臂：Hand、Random、Rule-based、Reflection（明确为非 LLM 确定性代理）、NSGA-II、NSGA-III、matched-objective NSGA-II、matched-objective NSGA-III、A、AB、SBCG，以及 no-M1/no-M2/no-M3。所有 EA 臂共享初始池、预算、seed 和 Train 信息权限；仅 no-M3 按预注册移除 Hand-anchor。

`ea.py` 本轮只新增 unique_evaluations/cache_hits/evaluation_calls 计数，不改变旧 EA 的选择逻辑。`sbcg_config.json` 冻结机制配置和当前权限边界。

## 6. 测试、CI 与 clean-clone

| 验证 | 实际结果 |
|---|---|
| 本地 pilot_a3b | **262/262 OK** |
| 本地 pilot_a_recovery | **28/28 OK** |
| 合计 | **290/290** |
| CI regression run 42813004959 | success @ `e92e9af…` |
| CI R4 power run 42813004752 | success @ `e92e9af…`；写回 10,000 MC 结果 |
| 干净远端 clone @ `4c4c62f…` | 262+28=290/290 OK |
| clean-clone 日志 | `experiments/pilot_a3b/results/r4_clean_clone.log`（首次网络失败保留于 `r4_clean_clone_attempt1.log`） |

新增测试包括 formal runner 7、pre-flight 执行 2、SBCG 机制 15、SBCG runner 8、对照/计数 7、功效输入哈希 1，以及 sign-flip 字段/seed 2。旧 R3 测试已随中性字段名同步更新。

## 7. 数据访问与预算

- 仅运行合成 fixtures、合成 sentinels 和历史 diagnostic3 开发数据上的功效重算。
- **未运行真实 benchmark Train/Validation 算法诊断；未读取真实 Test；未启动 final evaluation。**
- 未运行 Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 或 ThinkingBox；未合并 main。
- SBCG 性能配置仅为 pop=48、generations=60、seeds {411,522,633}；本轮没有任何臂的正式性能评价预算消耗、唯一调用数或 cache hit 可报告为实验结果。所有臂的 CondRecSucc、安全、harm、cost、Pareto/hypervolume 与消融性能均为 **NOT RUN**。

## 8. 科学结论

**尚不能判断 SBCG 是否优于 NSGA-II、NSGA-III、matched-objective NSGA-II 或 Hand。** 本轮只证明实现存在、合成行为符合接口、预算/缓存可审计、测试和 clean-clone 可复现；这些不构成算法创新或性能提升证据。

安全非劣界值和 hypervolume reference point 尚无充分领域依据，保持 OPEN，不得查看结果后补选。若后续不能安全地超过 matched-objective 强基线，应明确 NO-GO。

## 9. 唯一下一步任务

**将 64-R4 及本报告提交独立 Reviewer。** 只有独立审计 ACCEPTED、导师 MDE=0.10 认可、用户明确批准且 R4 pre-flight 通过后，才可先冻结安全非劣与 hypervolume 规则，再运行 Train-only SBCG 强对照/消融；Validation 只做冻结选择，Test 只走获批的一次性 gate。
