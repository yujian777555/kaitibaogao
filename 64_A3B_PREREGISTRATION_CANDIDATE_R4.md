# 64-R4 — Pilot A-3b 正式预注册（修订版 R4，待独立复审与批准）

**日期：** 2026-11-10  
**状态：** PREREGISTRATION CANDIDATE R4 — **READY_FOR_INDEPENDENT_REVIEW 仅表示材料齐备；未经独立审计 ACCEPTED、导师 MDE 认可、用户明确批准与 §9 pre-flight 全通过，不得运行正式实验**  
**历史版本：** R2 保留于 `64_A3B_PREREGISTRATION_CANDIDATE.md`；R3 保留于 `64_A3B_PREREGISTRATION_CANDIDATE_R3.md`；独立审计见 `72_64R3_INDEPENDENT_REVIEW.md`  
**实现入口：** `experiments/pilot_a3b/formal_runner.py` → `formal_analysis.py`；功效入口 `power_r4_design.py`

## 1. 研究假设与比较

- **H1（唯一 confirmatory 主假设）：** 锁箱 Test 上，AB 相对 canonical NSGA-II 的 family-equal-weight CondRecSucc（R1+R2）更高。
- **唯一主比较：** AB − NSGA-II。
- **H2–H5 全部 exploratory：** H2 AB−A；H3 AwaitSLA−A；H4 AwaitSLA−AwaitFixed；H5 AB−AwaitSLA。缺少各项 null/partial-null 与 family-wise Type-I 校准，不得作为确认性主张。
- AB vs Hand 仅描述性参考；历史负结果保留。
- SBCG-NSGA-III 是独立算法候选，不因本 R4 文件自动获得正式实验许可。

## 2. 主要终点与冻结 composition roster

主要终点为 family-equal-weight CondRecSucc：

1. AB 与 NSGA-II 在 `(scenario, optimizer_seed)` 上配对；
2. seed 在 scenario 内等权平均；
3. scenario 在 composition cluster 内等权平均；
4. 每个 family 对冻结的 **恰好 5 个** primary compositions 等权平均；
5. family 间等权平均。

五个 primary composition 由机制覆盖在观察正式结果前冻结，不参考 CondRecSucc、安全结果、算法差值或 Test 结果：

| 主分析 composition | 机制覆盖 |
|---|---|
| `single_timeout` | 单点超时/延迟可见 |
| `timeout_then_rate_limit` | 有序超时与限流 |
| `partial_then_delay` | 部分提交与延迟可见 |
| `independent_mixed_val` | 独立混合可恢复故障 |
| `triple_mixed` | 三故障混合 |

`schema_then_timeout` 与 `partial_then_timeout_val` 只作预先声明的敏感性分析，不进入主要终点。五个 ID 及选择规则冻结于 `formal_scenario_generator.py` 的 `PRIMARY_ANALYSIS_COMPOSITIONS` 与 manifest `POWER_DESIGN`。

## 3. 唯一主检验与退化规则

- 对完整 family 的配对差值执行双侧单样本 **family-level Student-t**，α=0.05，df=`F_observed−1`。
- 正式分析与功效模拟共用 `power_hierarchical.student_t_summary()`；不得用 cluster bootstrap 或 sign-flip 替代主检验。
- 数值容差：`1e-12 × max(1, max|d_f|)`。
- 全零/零方差且 |mean|≤容差：`t=0, p=1, status=zero_effect_zero_variance`。
- 非零常数且 SD≤容差：`t=±∞, p=0, status=nonzero_constant_limit`，这是明确标记的零方差退化极限，不伪装成普通可估计 t 检验，不提供常规 CI。
- 正常方差：输出 t、df、双侧 p 与 95% CI；已知答案测试与可信统计实现核对。
- family-level sign-flip 仅敏感性：F≤15 精确枚举，F>15 10,000 MC +1 修正；输出中性 `signflip`、method、n_resamples、实际 random_seed_used 和 F。
- family-block bootstrap 只作描述性区间，不作 α 检验。

## 4. 实验协议与冻结哈希

| 项 | 冻结值 |
|---|---|
| Train | 8 families × 9 compositions × 3 repeats = 216 scenarios |
| Validation | 4 × 9 × 3 = 108 scenarios；仅冻结规则选择/停止，不进入适应度 |
| Test | 40 × 9 × 3 = 1,080 scenarios；280 R1/R2-eligible clusters；主要分析使用 40×5=200 clusters |
| 演化参数 | pop=48、generations=60、均匀交叉、单次变异/子代、NSGA-II 三目标历史骨干；预算按真实 episode 计入 |
| 初始种群 | 每 seed 共享同一 60 个 sensible-random FSM 池；所有历史 EA 对照同池 |
| 演化 seeds | {411, 522, 633}；场景 seed 由 stable_seed 派生 |
| 统计 seeds | 功效 base seed 20261114；sign-flip base 20261112，MC 实际 20261113；逐输出记录 |
| MDE | 0.10，`PROPOSED_MDE_PENDING_ADVISOR_APPROVAL` |
| manifest SHA-256 | `3ce3f49e2a4fa09f03d1ca1411e9bd9ac566dfbd223935c4915ca4ac1caa9298` |
| test-family SHA-256 | `01b41df8b06c318f90a4fc7aed45f673d13b50f14c08f56304ddffbb625a1411` |
| test-scenario SHA-256 | `dded3bb72a08143177dd6b7f5c4c4ef5100b547028c9cc40fa2b87b6bd70c919` |

manifest 当前值包含 R4 五 composition 元数据；早期 fb832bcc… 是 roster 冻结前历史值。test-family/test-scenario payload 哈希未变。

## 5. 正式执行必要条件（缺一不可）

1. R4 独立审计 **ACCEPTED**；
2. 导师认可 **MDE=0.10**，或按导师意见重新论证并重跑功效；
3. 用户明确批准最终 R4 文本；
4. **§9.1 pre-run 授权门为 GO**；执行完成后还必须通过 §9.2 post-run 完整性门，才能进行确认性分析。

任何一项缺失均为 HOLD。CI 绿色、代码实现、功效达标或合成测试通过都不能替代批准。

## 6. 缺失数据、损耗与设计偏离

- 技术性缺失仅限显式登记的 infrastructure 故障，包含 method/seed/scenario/category/reason；计数、不替换 seed、不重跑冒充。
- 行为失败是有效终点结果，`class_success=0` 并保留分母。
- labelled null、重复键、roster 外数据、metadata/split 冲突、无解释缺失、AB/NSGA-II 配对缺失均 fail closed。
- 任一配对技术缺失使该 composition 不完整；不得插补或替换。
- family 必须具有全部五个完整 primary compositions；否则列入 `family_loss` 和 `family_loss_reasons`，不得静默消失。
- `F_observed<34` 触发 `design_deviation`，主确认性 Student-t 标记 `NOT_ELIGIBLE_UNDERPOWERED` 并隐藏；只能描述性报告。
- manifest/code/git provenance 不完整时同样不输出确认性 Student-t。
- 超出五个 roster 的有效 compositions 只进入预注册敏感性分析，不得根据结果择优替换。

## 7. Test 隔离与一次性评价

- Train/Validation/Test 接口分离；`run_evolution()` 在评价前只接受 split=train。
- 普通 `evaluate_controller()` 只接受 Train/Validation；Test/Battery/unknown fail closed。
- 公开 manifest/audit 不向开发调用者返回 Test scenario/family/label payload。
- Test 只能由 `split_access.execute_final_evaluation_once()` 在 §9.1 pre-run GO、独立审计、导师 MDE、用户批准、CI/tests 及 manifest/code hash 全部匹配后访问。
- one-time ledger 以原子创建先消费再读 payload；access log 同步原子记录；重复、并发、hash 不符、加载或评价失败均 fail closed，不得重开。
- wrapper 返回绑定 manifest/code/outcome-ledger/access-log 的 `COMPLETED` receipt；`formal_runner.run_formal_analysis()` 必须验证该 receipt 后才接受 Test ledger。
- final evaluation 只读，不写回种群、适应度、参数、算子或 early stopping；正式分析后必须执行 §9.2 post-run 完整性检查。

## 8. 停止与解释

- 预算用尽即止；不因中途显著性停止；不追加预算。
- 主检验不显著 ⇒ 不得声称 AB 改进 EA 成立。
- H2–H5 即使 Holm 后显著也仅为 exploratory；只有四项均 eligible 时才计算 Holm，不做部分校正。
- R3/R4 安全终点独立报告；硬安全违规不得被主终点抵消。
- 历史 AB 未超过 Hand 及 R3/R4 退化必须保留。
- 合成 runner、功效模拟或 CI 均不是算法增益证据。

## 9. 两阶段真实门禁

`formal_preflight.py` 将授权与数据完整性拆成两个不同生命周期的门；`run_r4_preflight.py` 只生成 pre-run 元数据，不读取 Test payload。当前输出保存于 `experiments/pilot_a3b/results/r4_preflight/`。

### 9.1 Pre-run authorization gate

`run_formal_preflight()` 在 Test 执行前仅检查：

1. R4 文本 SHA、实现代码 SHA、Git HEAD；
2. 独立审计 ACCEPTED、导师 MDE APPROVED、用户明确批准；
3. 本地/CI 测试成功；
4. train/validation/test family 与 scenario hashes；
5. split 零交叉、Train-only runner、Validation selection-only、Test 不暴露；
6. 冻结 roster 和分析 schema；
7. 预算、seed、停止规则；
8. Test access log=0、one-time ledger=UNUSED。

**不要求任何尚未产生的 Test outcome rows、配对完整性、family_loss 或 labelled null 数据。** 只有这些 pre-run 条件全部满足才返回 GO。

### 9.2 Post-run analysis-integrity gate

`run_postrun_integrity_check()` 在一次性 Test 执行完成后检查：配对完整、duplicate/null/metadata 错误为 0、F≥34、每族恰好 5、family_loss、technical_missing_runs、design_deviation、Test access 已记录、ledger=CONSUMED。

该门只决定确认性分析资格，不能授权或重开 Test。post-run 失败时正式 runner 将确认性 Student-t 置为不可用。

任一阶段的任一必需字段缺失或不满足均为 HOLD。当前没有独立 ACCEPTED、导师 MDE 或用户批准，因此当前 pre-run 输出必须仍为 HOLD，而不是 GO。

## 10. R4 功效与 Type-I 重新校准

实现：`power_r4_design.py`；原始结果：`experiments/pilot_a3b/results/r4_power_20261114/power_r4_design.json`。每格 10,000 MC，base seed 20261114；输出逐格 seed、MCSE 和 95% Wilson 区间。方差与残差形状来自历史六族 diagnostic3 开发数据，属于模拟假设，不是真实 ICC 估计或算法有效性证据。输入同时记录 raw SHA-256 与跨换行环境稳定的 canonical-content SHA-256；当前 canonical 值为 `9b1d90279852843bf93d92e66dab3e726ff1e19bc14b94e07ba260fc34eb68a7`。

| F | ICC | MDE=0.10 power | 95% Wilson CI | Null Type-I |
|---:|---:|---:|---|---:|
| 33 | 0.00 | 0.9788 | [0.9758, 0.9814] | 0.0490 |
| 33 | 0.05 | 0.9507 | [0.9463, 0.9548] | 0.0475 |
| 33 | 0.10 | 0.9121 | [0.9064, 0.9175] | 0.0522 |
| 33 | 0.20 | 0.8308 | [0.8233, 0.8380] | 0.0482 |
| **34** | 0.00 | 0.9798 | [0.9769, 0.9824] | 0.0479 |
| **34** | 0.05 | 0.9529 | [0.9486, 0.9569] | 0.0508 |
| **34** | 0.10 | 0.9197 | [0.9142, 0.9249] | 0.0489 |
| **34** | 0.20 | **0.8427** | **[0.8354, 0.8497]** | **0.0503** |
| 40 | 0.00 | 0.9912 | [0.9892, 0.9929] | 0.0507 |
| 40 | 0.05 | 0.9781 | [0.9750, 0.9808] | 0.0498 |
| 40 | 0.10 | 0.9523 | [0.9479, 0.9563] | 0.0490 |
| 40 | 0.20 | 0.9028 | [0.8968, 0.9085] | 0.0547 |

F=33 仅为 family-loss 边界敏感性，不具备确认性资格。F=34 为最低有效设计，F=40 为完整设计。最坏 ICC=0.20 时 F=34 功效仍高于 0.80。该结论只适用于每族恰好 5 个 primary compositions 的冻结设计。

### 10.1 Technical-missing 与 Type-I 复核

`simulate_missing_sensitivity()` 在 ICC=0.20 下对 composition-cluster MCAR technical missing 率 0%、1%、2%、5% 进行 10,000 MC；family 只有五个 primary compositions 全完整才纳入，F<34 不执行确认性推断。

| F design | missing | 平均完整 F | 分析 eligible 率 | eligible 时 null 拒绝率 | MDE 联合拒绝率 |
|---:|---:|---:|---:|---:|---:|
| 34 | 1% | 32.36 | 0.1857 | 0.0495 | 0.1507 |
| 34 | 2% | 30.71 | 0.0318 | 0.0566 | 0.0258 |
| 34 | 5% | 26.28 | 0.0002 | 0.0000 | 0.0001 |
| 40 | 1% | 38.03 | 0.9970 | 0.0509 | 0.8824 |
| 40 | 2% | 36.12 | 0.9141 | 0.0520 | 0.7971 |
| 40 | 5% | 30.94 | 0.1641 | 0.0451 | 0.1455 |

该表说明 missing 会使设计迅速失去确认性资格；不得把条件性 power 当作完整实验保证。MCAR 仍是模拟假设，不覆盖所有非随机缺失机制。

`simulate_type_i_replication()` 对 F=40、ICC=0.20、null 使用 5 个独立 seed × 10,000 MC。 pooled Type-I=**0.0489**，95% Wilson CI **[0.0470,0.0508]**。此前单 cell 0.0547 不作为独立校准证据；多 seed 复核与名义 0.05 一致。

所有原始格子、逐格 seed、rejections、MCSE 和区间均保存在同一 `power_r4_design.json`，不是只写报告汇总。

## 11. 实现与可复现性

- `formal_runner.run_formal_analysis()`：manifest + 原始 run ledger → 主/次要 family-level 分析、每层 roster hash、输入/manifest/code/git provenance。
- `formal_analysis.analyze_primary_endpoint()`：动态 F、真实 missing-data validator、family equal weight、唯一 Student-t。
- `formal_analysis.analyze_secondary_endpoints()`：H2–H5 四对比、完整四项 Holm、全部 exploratory。
- `split_access.py`：Train/Validation/Test 隔离和原子一次性 gate。
- `power_hierarchical.student_t_summary()`：正式与模拟共用统计及退化实现。
- `test_64r4_*.py` 与 `test_sbcg*.py`：只使用合成 fixtures/sentinels。

R4 材料完成后只能标记 **READY_FOR_INDEPENDENT_REVIEW**，Executor 不得自评 ACCEPTED。


## 10.2 D-085 统计修复后的当前功效表

本轮独立复审发现 `_betainc()` 在 x→1 时的小 |t| 数值不稳定。现按对称关系 `I_x(a,b)=1−I_(1−x)(b,a)` 修复，并加入 t=0.001/0.01、df=39/1 的 SciPy 已知答案测试。正式分析与模拟继续共用同一 `student_t_summary()`。

以下为修复后重新生成的当前值；§10 旧表仅作修复前历史记录。

| F | ICC | MDE=0.10 power | 95% Wilson CI | Null Type-I |
|---:|---:|---:|---|---:|
| 33 | 0.00 | 0.9788 | [0.9758, 0.9814] | 0.0490 |
| 33 | 0.05 | 0.9507 | [0.9463, 0.9548] | 0.0460 |
| 33 | 0.10 | 0.9121 | [0.9064, 0.9175] | 0.0506 |
| 33 | 0.20 | 0.8308 | [0.8233, 0.8380] | 0.0467 |
| **34** | 0.00 | 0.9798 | [0.9769, 0.9824] | 0.0479 |
| **34** | 0.05 | 0.9529 | [0.9486, 0.9569] | 0.0496 |
| **34** | 0.10 | 0.9197 | [0.9142, 0.9249] | 0.0480 |
| **34** | 0.20 | **0.8427** | **[0.8354, 0.8497]** | **0.0491** |
| 40 | 0.00 | 0.9912 | [0.9892, 0.9929] | 0.0507 |
| 40 | 0.05 | 0.9781 | [0.9750, 0.9808] | 0.0490 |
| 40 | 0.10 | 0.9523 | [0.9479, 0.9563] | 0.0479 |
| 40 | 0.20 | 0.9028 | [0.8968, 0.9085] | 0.0538 |

修复后 F=40/ICC=0.20 的 5×10,000 独立-seed null 复核 pooled Type-I 为 **0.04754**，95% Wilson CI **[0.045709, 0.049440]**。完整当前 JSON 含 24 主格、16 MCAR 格、16 个连续前缀不利缺失格及 5 个 Type-I replication；pre-fix JSON/Markdown 另存为 `power_r4_design.pre_d085.json/.md`。

连续前缀缺失是明确的非随机不利情景：F=34 时只要 1% 缺失就会降到 33 个完整 family，全部 10,000 个 replicate 均不具备确认性资格；F=40 时 1%/2%/5% 的 MDE 联合拒绝率分别为 0.8954/0.8947/0.8828。MCAR 与连续前缀结果都保留，不能只报告有利机制。
