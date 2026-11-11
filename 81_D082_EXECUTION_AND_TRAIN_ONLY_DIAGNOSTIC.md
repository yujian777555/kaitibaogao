# 81 — D-082：D-079 修复验收、挑战集冻结与 Train-only 算法诊断

**日期：** 2026-11-11  
**角色：** Executor  
**起始 HEAD：** `0726f779e00c82ca4fd96e4a3adb3ac8b67bda88`  
**main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`（未修改）  
**范围：** D-081 CI 验收、D-078 独立复算、288 场景挑战集、manifest lock、Train-only 探索性算法诊断  
**版本修正：** 本报告首次写入时使用 v1 角色碎片化 cluster_id。后续 D-083/D-084 独立审计撤销了 v1 lock 资格；v1 诊断仅保留为 superseded。最终有效结果来自 v2 及 committed lock，见 §8。
**正式 A-3b / Test / Pilot B / A800 / 真实 LLM API：** 均未运行或未访问

## 1. D-081 CI 验收

### 修正版成功证据

- 修正提交：`192f958847fb31d7d704cfa0760201dcd8371e32`
- Regression run：[42828590264](https://github.com/yujian777555/kaitibaogao/actions/runs/42828590264)
- 结论：**success**
- 测试：pilot_a_recovery 28 + pilot_a3b 290 = **318/318**
- D-064-C gate PASS；正式候选 manifest/test-family/test-scenario 哈希保持不变。

### 首轮失败根因

- run 42827879313：282 tests 后 `test_d079_diagnostics.D079ChallengeTests.setUpClass` 失败；
- run 42827879133：同一 preflight 失败，算法执行步骤 skipped；
- 错误为 `D-079 family must contain compensatable and uncompensatable tools`；
- 首轮没有产生新算法实验数据。

D-081 通过允许 D6 使用 runtime compensation unavailable 修复了该错误，而不是删除或放宽测试。D-078 workflow 已改为 workflow_dispatch only，普通 push 不会自动重跑 D-078。

## 2. D-078 独立复算

实际执行：

```bash
python experiments/pilot_a3b/d079_diagnostics.py \
  --outdir experiments/pilot_a3b/results/d079_d078_audit
```

输出：

- `d079_d078_audit.json`
- `d078_scenario_diagnostics.csv`
- `d078_family_composition_diagnostics.csv`
- `d079_d078_audit_report.md`
- `independent_recheck.json`（直接从原始 ledger 独立重算）

### 核心结果

| 项目 | 独立复算结果 |
|---|---:|
| 注册 runs | 42/42 |
| Validation scenarios / families | 108 / 4 |
| 选择结果与 Hand FSM 完全相同 | **32/42** |
| Validation Pareto front 含 Hand | **33/42** |
| robust/analytic label disagreement | **0** |
| Hand R1/R2 CondRecSucc | **1.000**（252/252） |
| Hand R3 CorrectEscalation | **0.000**（0/36） |
| Hand R4 DamageContainment | **1.000**（36/36） |

成功完成的 R1/R2 行中有 252 行带预期 active effects；原始 harm 将 756 个预期效应误计为 harm，修正后为 0。不可补偿/不可回滚前缀通过 `unavoidable_residual`/`min_reachable_harm` 进入 R4 最小伤害边界；R3 的 36 行则显示 Hand  escalation 后仍留有 residual，不能判为 CorrectEscalation 成功。

**解释：** “32/42 选择 Hand”主要是 Hand-anchor、可行性过滤和 Pareto 选择的联合结果，不是 32 次独立演化发现了 Hand。Validation 仍用于 D-078 候选选择，存在 selection optimism。

D-078 原始 runner 使用 analytic verdict；D-079 的独立复算显式使用重建的 robust AND-OR 标签。新挑战集 runner 使用 `evaluator_verdict_from_scenario()`，robust 标签是正式评估输入，analytic 仅作 harm-bound 与交叉检查。

## 3. 288 场景挑战集审查

实际执行：

```bash
python experiments/pilot_a3b/d079_challenge_generator.py \
  --outdir experiments/pilot_a3b/results/d079_challenge_candidate
```

| 检查 | 结果 |
|---|---|
| 总场景 / Search / Diagnostic | **288 / 144 / 144** |
| Train families / difficulty strata | **8 / 6** |
| 每 family×stratum×role repeats | **3** |
| Search/Diagnostic fault pattern 配对 | **144/144 配对一致，参数 seed 独立** |
| split=train | **288/288** |
| Validation/Test 包含或读取 | **否 / 否** |
| scenario ID / seed 唯一 | **288 / 288** |
| UNKNOWN | **0** |
| robust/analytic disagreement | **0** |
| D6 compensation unavailable | **48/48 均为 unavailable** |

### 每角色标签与难度层

| Stratum | 每角色数 | Robust 标签 | 语义证据 |
|---|---:|---|---|
| D1_CLEAR_PRECOMMIT_TIMEOUT | 24 | R1 | 无补偿任务可达 |
| D2_AMBIGUOUS_NONIDEMPOTENT_COMMIT | 24 | R1 | 等待延迟可见后可完成，无需补偿；没有强行伪造为 R2 |
| D3_COMPENSATABLE_PARTIAL_COMMIT | 24 | R2 | 无补偿不可达，有补偿可达 |
| D4_CROSS_TOOL_THREE_FAULT_INTERACTION | 24 | R2 | 同上 |
| D5_PERMISSION_AFTER_COMMITTED_PREFIX | 24 | R3 | 零残余安全放弃可达 |
| D6_UNCOMPENSATABLE_PARTIAL_COMMIT | 24 | R4 | 零残余不可达，但损害遏制可达 |

每角色合计 R1=48、R2=48、R3=24、R4=24。D2 的 R1 是当前 robust 语义下的真实可达性结论，不是标签伪造。

## 4. Manifest lock

新增 `d079_manifest_lock.py` 与 `test_d079_manifest_lock.py` 6 项真实篡改测试：

- 内容哈希、原始文件哈希、scenario ID 集合、generator version、seed、family/scenario/cluster 计数全部核验；
- 改 label、改 scenario ID、改 generator/seed、改原始文件空白均使 lock 失败；
- UNKNOWN 或计数不合法在 lock 前被拒绝。

锁定值：

- manifest content SHA-256：`cafdc52e037c08ca8cd95c0546014bab6dd27e9bd6d28122afb90f28b3cd1efa`
- manifest raw-file SHA-256：`0072550d432d306d4c02912bebaaa4a4756edb33a68c962cf59e9fb198d6c152`
- scenario IDs SHA-256：`4d7b19605155bdbfde61216ecfda6019f09d78a76fa7162fd16c18496114ec99`
- lock：`experiments/pilot_a3b/results/d079_challenge_candidate/d079_manifest_lock.json`
- 自验与独立重算：**PASS**

## 5. Train-only 算法诊断

### 权限与方法

Task 1–4 全部通过后，执行：

```bash
python experiments/pilot_a3b/d079_train_only_diagnostic.py \
  --manifest experiments/pilot_a3b/results/d079_challenge_candidate/d079_challenge_manifest.json \
  --lock experiments/pilot_a3b/results/d079_challenge_candidate/d079_manifest_lock.json \
  --outdir experiments/pilot_a3b/results/d079_train_only_diagnostic_final
```

- 14 arms × 3 seeds = **42 runs**；使用 seeds 411/522/633。
- 每 EA 臂 Search 上限 = 8×(5+1)×144 = **6,912 episodes**。
- Diagnostic 在独立角色的 144 个 Train 场景上执行；不回灌搜索、反例池或选择器。
- 固定 Hand/Rule/Reflection 直接在 Diagnostic 评价；EA 先 Search，再按同一 Train-only 可行性/Pareto/family 规则选择。
- Hand-anchor 仅用于完整 SBCG 和 no-M1/no-M2；no-M3、matched 和普通 EA 对照使用同一底层随机池，预算不变。
- 配对 seed 差值与 10,000 次 bootstrap 区间仅为探索性描述，不发确认性 p 值。

### 各臂实际指标（3 seeds 均值）

| Arm | 可选/run | Search episodes | Diagnostic episodes | CondRec | R3 Correct | R4 Containment | AvoidableHarm | ActionCost | ConstraintViolation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hand FSM | 3/3 | 0 | 144 | **0.7812** | 0.0000 | 0.0000 | 0.4375 | **3.4688** | 0.1458 |
| Random | 0/3 | 6912 | 1152 | NA | NA | NA | NA | NA | NA |
| Rule-based | 3/3 | 0 | 144 | **0.7812** | 0.0000 | 0.0000 | 0.4375 | **3.4688** | 0.1458 |
| Reflection | 3/3 | 0 | 144 | 0.5312 | 0.0000 | 0.0000 | 1.0417 | 4.0312 | 0.8125 |
| NSGA-II | 0/3 | 6912 | 1152 | NA | NA | NA | NA | NA | NA |
| NSGA-III | 0/3 | 6912 | 1152 | NA | NA | NA | NA | NA | NA |
| Matched NSGA-II | 3/3 | 6912 | 1152 | 0.2396 | 0.0000 | 0.3333 | 0.7569 | 9.3160 | 0.0000 |
| Matched NSGA-III | 3/3 | 6912 | 1152 | 0.2396 | 0.0000 | 0.3333 | 0.7569 | 9.3160 | 0.0000 |
| A | 2/3 | 6912 | 1152 | 0.0781 | 0.0000 | 0.0000 | 0.6354 | 9.1250 | 0.0000 |
| AB | 1/3 | 6384 | 1152 | 0.0938 | 0.0000 | **1.0000** | 0.3125 | 5.5521 | 0.0000 |
| **SBCG** | 3/3 | 6576 | 912 | 0.2292 | 0.0000 | **0.6667** | 0.3472 | 3.7083 | **0.0000** |
| no-M1 | 3/3 | 6720 | 576 | **0.4896** | 0.0000 | 0.6667 | 0.4444 | 6.8299 | 0.0000 |
| no-M2 | 3/3 | 6912 | 1104 | 0.3854 | 0.0000 | 0.0000 | 0.7014 | 9.9583 | 0.0000 |
| no-M3 | 3/3 | 6576 | 1152 | 0.2500 | 0.0000 | 0.3333 | 0.6875 | 13.7222 | 0.0000 |

Random、canonical NSGA-II 和 canonical NSGA-III 的“0/3 可选”表示 Diagnostic 上没有满足零容差硬约束的候选，不是把它们当作零分或删除失败臂。

### 关键配对差（SBCG − 对照）

| 对照 | CondRec | R4 Containment | AvoidableHarm | ConstraintViolation |
|---|---:|---:|---:|---:|
| Hand | **−0.5521** [−0.7812,−0.3125] | **+0.6667** [0,1] | −0.0903 [−0.2500,0.0833] | **−0.1458**（3/3 一致） |
| Matched NSGA-II | −0.0104 [−0.1875,0.1562] | +0.3333 [0,1] | −0.4097 [−0.5833,−0.3125] | 0 |
| no-M1 | −0.2604 | 0 | −0.0972 | 0 |
| no-M2 | −0.1562 | +0.6667 | −0.3542 | 0 |
| no-M3 | −0.0208 | +0.3333 | −0.3403 | 0 |

SBCG 相对 Hand 的 CondRecSucc 在每个 seed 都更低（−0.3125、−0.5625、−0.7812）。因此不存在恢复性能提升。安全/硬约束和 R4 损害遏制存在正向信号，但不能抵消主恢复终点失败。

### 独立结果核验

`results/d079_train_only_diagnostic_final/independent_verification.json`：

- 42 runs、4320 条 Diagnostic 行；
- 预算违规 0、cache 账户违规 0、角色/Validation/Test 违规 0；
- CSV→汇总重算不一致 0；
- 首次与最终代码复跑的各臂指标完全一致。

## 6. 研究结论

### 当前算法是否有提升？

**没有整体提升，当前 SBCG 候选对“更好的恢复控制器”判为 NO-GO。** 它具有更好的硬安全可行性和 R4 损害遏制信号，但 CondRecSucc 明显低于 Hand/Rule-based，R3 CorrectEscalation 在所有臂上均为 0，且未证明超过 matched-objective NSGA-II。

### 是否值得继续？

值得保留为**安全约束搜索的负结果/机制诊断**，不值得把当前 SBCG 直接写成论文创新点。若继续，应针对明确失败机制做单一、可消融的修订，而不是继续堆叠目标或预算。

### 当前最大障碍

1. **R3 机制失败：** 权限拒绝后的“先补偿/回滚已提交前缀，再安全升级”没有被任何臂学会；所有方法 CorrectEscalation=0。
2. **恢复—安全权衡：** M1 的完整五目标/选择降低 CondRecSucc；no-M1 提高恢复但牺牲 harm，说明当前没有免费 Pareto 改善。
3. **强锚点支配：** D-078 的 32/42 Hand 选择说明搜索证据不足；D-079 仍不能把 Hand-anchor 的贡献误写成演化发现。

### 唯一下一任务

先提交 R4 独立复审；算法侧只允许下一步预注册一个针对 R3 的“prefix rollback/compensation before escalation”机制及其独立消融，并使用新的挑战划分验证，不得在同一 Diagnostic 上反复调参制造提升。

## 7. 产物

- `results/d079_d078_audit/`：D-078 CSV/JSON/Markdown 与独立复算；
- `results/d079_challenge_candidate/`：288 场景 manifest、报告和 lock；
- `results/d079_train_only_diagnostic/`：首次诊断，保留不覆盖；
- `results/d079_train_only_diagnostic_final/`：最终代码复跑、CSV/JSON/Markdown 与独立核验；
- `test_d079_manifest_lock.py`、`test_d079_train_only_diagnostic.py`：lock 与 runner 的真实路径测试。

本报告不构成正式 A-3b、Test、Pilot B、A800/ARWM 或真实 LLM API 授权。


## 8. D-083/D-084 后续审计：v1 撤销与 v2 有效诊断

后续独立审计发现 v1 的 scenario `cluster_id` 为 `family|stratum|role`，而 48 个注册 cluster 使用 `family|stratum`，产生 96 个无法与注册表 join 的角色碎片化 ID。因此：

- **v1 manifest lock 被撤销；v1 诊断只保留为 superseded 历史数据，不能作为最终算法证据。**
- 合并 v2 修正后，scenario cluster_id 统一为 `family|stratum`，evaluation_role 作为独立维度；
- 重新生成 v2 manifest，内容 SHA 为 **`09df6babbb6e3222ea57a7f354654636ac2437b7011dbe3f1ac738df894a0bca`**；
- 使用 D-084 committed lock `experiments/pilot_a3b/d079_manifest_lock.json` 重新运行完整 14×3 诊断；
- 新 runner 同时支持文件级 lock 与 committed content-level lock，并用测试覆盖两种 schema。

### v2 独立结构审计

`results/d079_challenge_v2/independent_audit.json` 证明：

- 288 个唯一 Train 行、288 个唯一 seed、0 UNKNOWN、0 robust/analytic disagreement；
- 恰好 48 个可 join clusters；每簇 6 行，Search/Diagnostic 各 3；
- manifest gate 与 committed lock 均 PASS；
- v2 raw manifest file SHA-256=`f2dfc57cc8d2444680e589cd82efad7383bfebc269527709f9ffa18e16ed9d27`。

### v2 算法结果

v2 与 v1 的 cluster 表示修正不改变 episode 语义；独立比较显示所有臂的场景级指标完全一致。最终有效结果位于 `results/d079_train_only_diagnostic_v2/`：

| Arm | CondRecSucc | R3 Correct | R4 Containment | AvoidableHarm | ConstraintViolation |
|---|---:|---:|---:|---:|---:|
| Hand | 0.7812 | 0.0000 | 0.0000 | 0.4375 | 0.1458 |
| Matched NSGA-II | 0.2396 | 0.0000 | 0.3333 | 0.7569 | 0.0000 |
| SBCG | 0.2292 | 0.0000 | 0.6667 | 0.3472 | 0.0000 |
| no-M1 | 0.4896 | 0.0000 | 0.6667 | 0.4444 | 0.0000 |
| no-M2 | 0.3854 | 0.0000 | 0.0000 | 0.7014 | 0.0000 |
| no-M3 | 0.2500 | 0.0000 | 0.3333 | 0.6875 | 0.0000 |

`independent_verification.json` 再次确认：42 runs、4320 诊断行、预算/缓存/角色违规 0、汇总重算不一致 0。

**最终结论仍以 v2 为准：SBCG 当前整体 NO-GO。** R4 containment 和硬约束的正向信号不构成恢复性能提升；所有臂 R3 CorrectEscalation=0 的问题仍未解决。
