# 72 — 64-R3 独立审计报告（D-064-R3）

**日期：** 2026-11-10  
**角色：** 独立学术审计者（Independent Reviewer）；不是 Executor，不为修复报告背书  
**审计对象：** `64_A3B_PREREGISTRATION_CANDIDATE_R3.md` 及其实际代码、测试、功效产物和调用链  
**结论：** **REQUEST CHANGES**  
**正式 A-3b：** **HOLD**。本轮未运行正式实验，未读取或输出 Test 逐场景标签或算法结果，未修改实验代码或 R3 预注册。

---

## 1. 审计基线与 Git 状态

| 项 | 独立核验结果 |
|---|---|
| Repository | `https://github.com/yujian777555/kaitibaogao` |
| 工作分支 | `pilot-a-stateful-recovery` |
| 分支远端 HEAD | `ca7bb12f89dd72deaac205ffab89cf3054e6be06`，与指定审计基线一致 |
| main 远端 HEAD | `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，与指定值一致 |
| CI | run [42670236796](https://github.com/yujian777555/kaitibaogao/actions/runs/42670236796)，`headSha=ca7bb12f…`，`status=completed`，`conclusion=success` |
| CI 测试 | `pilot_a_recovery` 28/28 + `pilot_a3b` 161/161 = **189/189**；不是一个单独的 189-test suite |
| D-064-C CI gate | PASS；manifest/test-family/test-scenario 哈希与 R3 记录一致 |
| 本地复跑 | 同样为 28/28 + 161/161，全部 OK |
| 审计修改边界 | 仅新增本报告、独立审计证据 JSON 和维护记录；未修改 Executor 实验代码、测试或 R3 |

审计前工作区干净。main 未因本轮审计被修改。

## 2. 审计范围与独立验证方法

### 2.1 已读取并检查的材料

- `64_A3B_PREREGISTRATION_CANDIDATE_R3.md`、历史 R2 原文；
- `70_64R2_INDEPENDENT_REVIEW_R1.md`、`71_64R2_CORRECTIVE_RESPONSE_AND_R3_VALIDATION.md`、`69_D064C_INDEPENDENT_AUDIT_AND_DESIGN_FREEZE.md`；
- `power_hierarchical.py`、`test_64r3_protocol.py`、`condrec_analysis.py`、`formal_scenario_generator.py`；
- `analyse_diagnostic3.py`、`test_power_hierarchical.py`、`test_condrec_analysis.py`、`test_analyse_diagnostic3.py`、`test_d064c_audit.py`、`test_formal_scenario_generator.py`；
- `ea.py`、`a3_bridge.py`、`run_diagnostic2.py`、`run_diagnostic3.py`、`task_semantics.py`、`stats.py`、`power_simulation.py`；
- `power_final_design_check.json`、历史 `power_hierarchical.json`、GitHub Actions 日志。

### 2.2 独立执行而非仅引用 71 号报告的验证

1. 在干净状态运行两套测试，并核对 CI 原始日志。
2. 用独立进程重建 candidate manifest；只核对哈希、gate 和序列化字段，不查看 Test 逐场景标签。
3. 对 `family_level_tests()` 与 `_pvals_student_t()` 构造全零、全正常数、全负常数、极小方差和正常方差输入，并与 SciPy 参考值比较。
4. 构造 labelled `class_success=None`、缺失 run、行为失败 0 等合成输入，调用真实处理函数，检查是否 fail-closed、是否静默删除。
5. 从历史 **development/diagnostic3** 数据重新计算经验残差池和总方差，复跑 34×5、10,000 MC 的功效；随后对可变 composition 数做独立 masking 模拟。
6. 追踪 train/validation/test 从生成器到 `run_evolution()`、`evaluate_controller()` 和统计分析的实际数据流。

独立数值输出保存于 `experiments/pilot_a3b/audit_64r3_independent_checks.json`。该文件只含合成边界用例、缺失数据反例、哈希核验和开发数据功效复核，不含 Test 标签或结果。

## 3. R1 六项问题关闭情况

| R1 问题 | 文件、代码与测试证据 | 独立结论 |
|---|---|---|
| **R2-001 主检验唯一且实现一致** | R3 §2（`64_A3B_PREREGISTRATION_CANDIDATE_R3.md:28-34`）文本已统一为 family-level Student-t。可是 `condrec_analysis.py:279-283` 仍把 cluster bootstrap + sign-flip 声明为统计方法；`analyse_diagnostic3.py:194-254` 仍执行 cluster-level sign-flip；`power_hierarchical.py:510-525` 的 `main()` 只分析历史 diagnostic3。**正式 40-family 主分析入口不存在。** | **未关闭（文本关闭，实现未关闭）。** 不能以 R3 文本和辅助函数测试代替正式实现一致性。 |
| **R2-002 df 动态计算** | `family_t_df()` 在 `power_hierarchical.py:276-282` 实现 `F_observed-1` 并拒绝 F<2；`family_level_tests()` 在 `:299-347` 输出动态 df；模拟 `_pvals_student_t()` 在 `:417-425` 同样使用 `F-1`。`test_64r3_protocol.py:39-63` 覆盖 40→39、34→33 和动态 F。 | **动态 df 本身已关闭。** 但零方差处理存在新阻断缺陷 R3-004，不能据此接受整个 Student-t 实现。 |
| **R2-003 manifest SHA 真实重建一致** | 独立进程重建得到 `fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a`；test-family=`01b41df8b06c318f90a4fc7aed45f673d13b50f14c08f56304ddffbb625a1411`；test-scenario=`dded3bb72a08143177dd6b7f5c4c4ef5100b547028c9cc40fa2b87b6bd70c919`。与 CI run 42670236796 完全一致。`test_d064c_audit.py:192-200` 也覆盖哈希。 | **已关闭。** 独立 CLI 重建和 CI 干净 runner 证据充分；旧 af83f065 只能保留为 superseded。 |
| **R2-004 缺失数据与 attrition 科学合理** | R3 §6 写明规则；`missing_data_rules()` 在 `power_hierarchical.py:285-296` 仅返回字典。真实处理路径仍跳过 null、继续运行、无 `technical_missing_runs`、`family_loss`、`design_deviation` 实际字段。功效模拟固定 34×5，而规则允许 m=1。 | **未关闭。** 规则未真正执行，且功效假设与最低 1 composition 不一致，详见 R3-002/R3-003。 |
| **R2-005 MDE 导师审批门** | R3 §5（`:66-73`）把独立审计、导师 MDE、用户批准、pre-flight 列为必要条件；MDE 在 §4（`:63-64`）仍为 PROPOSED/PENDING。 | **协议文本门已写入；导师批准状态仍 OPEN（这是预期待办，不是伪造批准）。** 但 pre-flight 指向错误，另列 R3-001。 |
| **R2-006 H2–H5 检验与 Holm 完整** | R3 §3（`:36-46`）定义四项 family-level t + Holm。`holm_adjust()` 数学实现正确（`analyse_diagnostic3.py:257-265`），但正式 H2–H5 没有 family-level t 数据路径。历史 `SECONDARY_FAMILY`（`:40-43`）是 **6 项** cluster-level sign-flip，而不是 R3 的 **4 项** family-level t。 | **未关闭。** Holm 单元测试通过不等于四项次要终点已按 R3 执行。H2/H3 的单独校准也未提供；H4/H5 探索性尚无正式报告路径可执行。 |

## 4. 新发现问题汇总

| 编号 | 严重度 | 新发现 |
|---|---|---|
| **R3-001** | **P0** | R3 §5 将 pre-flight 指向 §6，但 §6 是“缺失数据、损耗与设计偏离规则”，没有 pre-flight 清单。 |
| **R3-002** | **P0** | `missing_data_rules()` 只是规则字典；null 不 fail-closed、技术缺失继续分析、family_loss/design_deviation 不计算，可能静默丢失 family。 |
| **R3-003** | **P0** | 功效假设固定每族 5 comps，规则却允许 1；不平衡会改变 family 均值方差并显著降低功效，当前 0.839/0.840 不能覆盖该规则。 |
| **R3-004** | **P0** | `family_level_tests()` 对全零差值返回 `t=inf, p=0`；模拟函数却返回 `p=1`。正式实现与功效模拟边界不一致。 |
| **R3-005** | **P0** | 正式 40-family 分析入口尚未实现；`build_hierarchy()` 硬编码 6 families、42 clusters、7 comps、12 zero-denominator。 |
| **R3-006** | **P0** | H2–H5 没有按 R3 执行的真实提取/配对/family 汇总/family-t/四项 Holm 路径；H2/H3 校准也未单独证明。 |
| **R3-007** | **P1** | 历史 diagnostic 未发现 Test 使用，但生成器会向调用者返回完整 Test payload，演化接口无 split guard，也没有一次性解锁路径。 |
| **R3-008** | **P2** | `signflip_exact` 字段在 Monte Carlo 情况下命名误导；MC seed 固定在代码参数中但未随结果序列化。 |

## 5. 统计方法审计

### 5.1 功效、ICC 网格与 Monte Carlo 复核

当前代码的 ICC 网格为 `(0, 0.05, 0.10, 0.20)`（`power_hierarchical.py:33`），MDE 网格含 0.10（`:32`）。`gen_family_means_hier()` 用 `m_eff` 生成固定数量的 cluster 并直接求均值（`:390-403`）；`mc_power_at()` 负责双侧 Student-t 拒绝率、MCSE 和正态近似 95% MC 区间（`:466-504`）。

本审计从 `diagnostic3_results.json` 原始开发数据重新构造残差池，`total_var=0.10166903256334146`，使用当前代码、10,000 MC、seed 20261113 独立复算：

| ICC | MDE=0.10 power（本审计） | 95% MC 区间 | Null Type-I（本审计） |
|---:|---:|---|---:|
| 0.00 | 0.9787 | [0.9759, 0.9815] | 0.0501 |
| 0.05 | 0.9533 | [0.9492, 0.9574] | 0.0489 |
| 0.10 | 0.9191 | [0.9138, 0.9244] | 0.0481 |
| **0.20** | **0.8400** | **[0.8328, 0.8472]** | **0.0504** |

ICC=0.20 时 MCSE=0.0037。与 `power_final_design_check.json:47-58,74-82` 的 0.8391 [0.8319,0.8463]、null 0.0541 属 Monte Carlo 噪声范围内的一致；本审计没有照抄历史数值。平衡 34×5 设计在该模拟模型下满足 0.80 功效目标，但这**不能推广到 §6 当前允许的不平衡缺失结构**。

MDE=0.10 仍待导师认可；功效不是算法有效性的证据。

### 5.2 Student-t 零方差与数值边界

`family_level_tests()` 在 `power_hierarchical.py:303-307` 中仅判断 `sd > 0`，否则设 `tval=inf`；模拟 `_pvals_student_t()` 在 `:421-423` 则把零 SD 替换为 `1e-12`。独立构造结果：

| 用例（F=34） | `family_level_tests()` | `_pvals_student_t()` | 审计判断 |
|---|---|---|---|
| 全部差值为 0 | `t=inf, df=33, p=0` | `p=1` | **正式路径错误且两路径矛盾。** 零均值零方差不得判为显著。 |
| 全部为 +0.2 | `t=inf, p=0` | `p=0` | 可作为退化极限处理，但必须显式定义，不能与全零共用 `inf`。 |
| 全部为 −0.2 | `t=inf, p=0` | `p=0` | 同上。 |
| 极小方差（一个值多 1e-12，其余 0.2） | `t≈6.8e12, p=0` | `p=0` | 需要统一的数值容差和退化规则。 |
| 正常方差 | `t=6.7337, df=33`，p 输出经六位小数舍入为 0 | `p=1.1324037e-7` | 与 SciPy `t=6.7337105, p=1.1324037e-7` 一致。 |

因此动态 df 的修复成立，但 Student-t 实现尚不能验收。至少应区分：(a) mean=0/sd=0；(b) 非零常数；(c) 近零方差；(d) 正常方差，并让正式分析与模拟采用同一规则。

### 5.3 Sign-flip Monte Carlo

`family_level_tests()`（`power_hierarchical.py:308-329`）：

- F≤15 使用 `2^F` 精确枚举，F>15 使用 10,000 次 MC；避免 F=40 的 `2^40` 挂死，修复有效。
- MC 使用 `(extreme+1)/(10000+1)`，+1 修正正确；精确枚举不需要该修正。
- 随机源为 `random.Random(seed+1)`；默认 seed=20261112，因此 MC 实际 seed=20261113。
- 本审计构造 F=15 时输出 `method="exact enumeration (2^15)"`；F=16/34/40 均为 `method="Monte Carlo sign-flip (10000 reps)"`，相同 seed 可复现。

但仍有两项记录缺陷：

1. 输出键始终叫 `signflip_exact`（`:345`），在 MC 情况下具有误导性；应改为中性 `signflip`，并保留 `method`。
2. 结果对象记录 method/reps，却没有记录实际 seed 值；不满足“固定并记录随机种子”的完整审计链要求。

R3 §2 已把 sign-flip 限定为敏感性分析；由于正式报告路径尚未实现，无法在最终产物中验证该边界是否被贯彻。

### 5.4 Holm 校正

`holm_adjust()` 的排序、单调累积最大值和 1 上界处理正确，已知答案测试通过。但它目前在历史 `analyse_diagnostic3.py:302-309` 中应用于六项 cluster-level sign-flip p 值，不是 R3 要求的四项 family-level Student-t p 值。算法正确不等于次要终点协议已实现。

## 6. 缺失数据与功效一致性

### 6.1 功效模拟是否假设固定 5 个 composition？

**是。** `gen_family_means_hier()` 生成形状 `(reps, n_fam, m_eff)` 的 cluster 数组并沿最后一维直接平均（`power_hierarchical.py:398-403`）。最终设计使用 `n_fam=34, m_eff=5`，因此假设每个 family 恰好有 5 个有效 composition，没有 `m_f` 变化、缺失 mask 或 family_loss 机制。

### 6.2 不平衡 composition 的数学影响

在功效模拟采用的层级模型下，令

\[
d_{fj}=\mu+u_f+\varepsilon_{fj},\qquad
\operatorname{Var}(u_f)=\tau^2,\qquad
\operatorname{Var}(\varepsilon_{fj})=\sigma^2.
\]

若第 f 个 family 有 \(m_f\) 个有效 composition，则

\[
\operatorname{Var}(\bar d_f)=\tau^2+\frac{\sigma^2}{m_f}.
\]

family 等权的总均值仍有

\[
\operatorname{Var}(\bar d)
=\frac{\tau^2}{F}+\frac{\sigma^2}{F^2}\sum_{f=1}^{F}\frac{1}{m_f}.
\]

因此“family 等权”只解决 family 间权重，不会消除 composition 数对精度的影响。当前 ICC=0.20、`total_var=0.101669` 时，m=5 的 family 方差为 0.03660，m=1 为 0.10167；后者约为前者的 2.78 倍。

### 6.3 独立不平衡缺失模拟

本审计使用相同经验残差池、相同总方差、10,000 MC、seed 20261113，在最多 7 个 cluster 上施加缺失 mask。预设三种结构：

- `balanced5`：所有 family 均 m=5；
- `alternating_5_1`：17 个 family m=5、17 个 family m=1；
- `binomial_floor1`：每个 MC replicate 独立抽取 \(m_f=\max(1,\operatorname{Binomial}(7,5/7))\)。

| ICC=0.20 结构 | MDE=0.10 power | 95% MC 区间 | Null Type-I |
|---|---:|---|---:|
| 原始函数，固定 34×5 | 0.8400 | [0.8328, 0.8472] | 0.0504 |
| 独立 masking，固定 m=5 | 0.8431 | [0.8360, 0.8502] | 0.0517 |
| **17 族 m=5 + 17 族 m=1** | **0.5777** | **[0.5680, 0.5874]** | **0.0518** |
| Binomial floor-1（平均 m≈5） | 0.8321 | [0.8248, 0.8394] | 0.0504 |

其他 ICC 网格的完整结果保存在审计证据 JSON。极端但完全符合 `family_min_valid_compositions=1` 的交替结构使功效从约 0.84 降至约 0.58；这不是可以用“family 等权”忽略的小效应。

在这两个具体不平衡模拟中，null Type-I 仍接近 0.05，未观察到明显膨胀。但普通单样本 Student-t 的 iid/同方差假设在 \(m_f\) 不同时并不严格成立；上述结果不能证明任意缺失机制下都校准，也不能替代对预定缺失结构的校准。

### 6.4 是否必须至少 5 个有效 composition？

- 若要继续援引当前 **34×5 平衡设计**的 0.839/0.840 功效和普通 Student-t 分析，**必须保证每个纳入 family 有 5 个有效 composition，并保证有效 family 数达到设计门槛**。
- 统计上并非绝对不能分析 m<5 的 family；但若保留 `≥1`，就必须预先定义不平衡缺失机制，重新模拟功效和 Type-I，并考虑显式处理异方差的分析，而不能继续引用平衡设计功效。
- 本审计不替 Executor 选择最终规则；可接受路径是“最低 5 + 重新规定 family_loss/design deviation”，或“保留 ≥1 + 新的不平衡功效/校准及匹配推断”。二者都需新预注册版本和独立复审。

### 6.5 Missing-data 规则是否真正执行？

**没有。** 真实函数反例结果：

| 规则 | 代码证据 | 独立反例结果 |
|---|---|---|
| 技术缺失排除、计数、不换 seed | `condrec_analysis.py:63-96` 只记录问题，`:261-288` 仍继续分析 | 删除一个 nsga2 run 后仍返回结果；记录 `missing run` 和 unpaired seeds，但无 `technical_missing_runs` 字段。未发现替换 seed 实现，但禁止规则没有可执行校验。 |
| 行为失败计 0 留分母 | `endpoint_table()` 对数值 0 正常汇总 | 此项实际成立；合成 0 值仍保留在配对场景和分母中。 |
| labelled null fail-closed | `condrec_analysis.py:133` 直接过滤 None；`power_hierarchical.py:78` 跳过 None；`analyse_diagnostic3.py:293-327` 记录 blocking problem 后仍继续 | labelled null 在 `condrec_analysis` 中 **integrity_problems=[]、missing_pairs=[]，仍输出效应**；`build_hierarchy()` 记录 unpaired seeds 但不抛错；diagnostic3 记录 null 为 blocking problem 后仍返回 contrasts。 |
| 0 有效 composition → family_loss | `power_hierarchical.py:90-104` 对无有效 scenario 直接 `continue`， families 只由剩余有效项组成 | 可能静默减少 family 数；输出无 `family_loss` 字段。 |
| F<34 → design_deviation | 只有 `missing_data_rules()` 中的字符串 | 无实际计算或输出字段。 |
| 禁止选择性删除 | 无正式数据处理入口 | 无法证明规则得到执行。 |

`test_64r3_protocol.py:89-114` 主要检查字典字符串、手工 fake hierarchy 和在测试内部临时构造的 family_loss 列表；没有调用真实处理函数验证 null fail-closed、technical count 或 design_deviation。因而 71 号“已修复+已验证”的结论不成立。

## 7. Test 隔离审计

### 7.1 已确认的正面事实

- `run_diagnostic2.py:116-175` 和 `run_diagnostic3.py:128-202` 的历史诊断只把 train 传入 `run_evolution()`，validation 只在选出 best 后评价；未发现 Test 输入。
- candidate manifest 的 `test_locked` 只含 summary、family/scenario 哈希和 `payload_disclosed=False`（`formal_scenario_generator.py:422-427`）。独立重建确认这些序列化字段和哈希一致。
- `task_semantics.audit_split_catalog()` 检查 family ID 与有序工具序列跨 split 不重叠（`task_semantics.py:343-377`）。

### 7.2 不能据此验收的部分

1. **完整 Test payload 仍暴露给调用者。** `build_candidate_manifest()` 的返回 `audit` 含 `test_families`、`test_clusters`、`test_scenarios`（`formal_scenario_generator.py:439-448`）；`write_candidate_manifest()` 也把该 audit 返回（`:514-533`）。不序列化到 candidate JSON 不等于 API 层锁箱。
2. **演化接口没有 split guard。** `ea.run_evolution(method, …, scenarios, verdicts, …)`（`ea.py:289-315`）不检查 split；`a3_bridge.evaluate_controller()` 使用 verdict 产生 class_success 并形成 objectives（`a3_bridge.py:538-562,565-630`）。若把 Test scenarios/verdicts 传入，它们会直接进入适应度。
3. **没有正式的一次性解锁路径。** 当前没有正式 runner、锁箱解锁函数、只读 final evaluation 入口或访问控制测试。
4. `test_64r3_protocol.py:140-163` 主要用 `inspect.getsource()` 检查字符串是否出现，以及 `split_summaries` 是否存在；它没有追踪上述真实调用链。

**结论：** 本轮没有发现历史诊断代码实际使用 Test 的证据，也没有读取 Test 标签/结果；但“test 不进入适应度/参数选择和只解锁一次”尚未形成结构性保证。需要用合成 sentinel split 写数据流拒绝测试，而不是读取真实 Test 来验证。

## 8. 正式 40-family 分析路径审计

### 8.1 `build_hierarchy()` 的性质

`power_hierarchical.py:59-166` 是 D-064-B 历史 diagnostic3 重建函数，不是正式 A-3b 通用入口：

- `:107-108` 强制期望 6 families；
- `:109-110` 强制 42 eligible clusters；
- `:111-113` 强制每族 7 eligible compositions；
- `:114-115` 强制 12 zero-denominator clusters；
- `:85-94` 只构造 AB−nsga2 的配对差。

`main()`（`:510-525`）读取默认 `diagnostic3_results.json` 并进行功效分析，不是 40-family 正式结果分析。

### 8.2 正式路径是否支持动态 F、family 等权和唯一主检验？

- `family_level_tests()` 能对已经构造好的 `fam_means` 做动态 F 的 t 检验和 family 等权平均；这是一个可复用的**辅助统计函数**。
- 但从正式 40-family 原始数据到 `fam_means` 的通用、缺失感知、fail-closed 路径不存在。family 等权不能只在 helper 输入已经正确时宣称成立。
- `condrec_analysis.py` 汇总到 cluster 并使用 cluster bootstrap/sign-flip；`analyse_diagnostic3.py` 也是 cluster-level 推断。历史代码存在 cluster-level 与 R3 family-level 的混用边界，不能把这些历史脚本直接当正式实现。
- H2–H5 没有按 R3 的数据提取、配对、family 汇总、family-t、四项 Holm 路径；H4/H5 探索性也没有正式报告生成位置。
- 安全终点在 `condrec_analysis.py:224-258` 只按 method/label 做 cluster 统计，未形成 R3 要求的正式独立报告和硬门执行链。

**结论：** 正式 40-family 分析系统尚未完成。辅助函数通过测试不能等同于正式分析路径完成。

## 9. 测试与 CI 证据

### 已实际通过

- 本地：`pilot_a_recovery` 28/28，`pilot_a3b` 161/161；
- CI run 42670236796：相同 28+161=189，success；
- `test_64r3_protocol.py` 包含在 161 个测试中并通过；
- D-064-C manifest gate PASS，独立重建哈希与 CI 一致。

### 测试覆盖不能证明的事项

- 零均值零方差 Student-t；
- labelled null 的真实 fail-closed；
- technical_missing_runs/family_loss/design_deviation 的真实计算；
- 不平衡 composition 的功效与 Type-I；
- 40-family 正式原始数据入口；
- H2–H5 的 family-level t + 四项 Holm；
- Test 进入适应度的结构性拒绝和一次性解锁；
- Monte Carlo 字段命名和 seed 序列化。

因此 CI success 只说明现有测试通过，不说明 R3 已具备正式执行条件。

## 10. 审计结论

# **REQUEST CHANGES**

R3 尚未达到正式 A-3b 预注册所需的统计正确性、实现一致性、可复现性和无数据泄漏要求。R2-003 已关闭，R2-002 的动态 df 部分已关闭，R2-005 的审批门文本已写入；其余关键问题不能只靠文档声明关闭。

主要阻断项为：

1. 缺失数据规则未进入真实处理流程；
2. 最低 1 composition 与 34×5 功效假设不一致；
3. Student-t 全零边界错误且两实现不一致；
4. 正式 40-family 分析入口缺失；
5. H2–H5 未按 R3 实际执行；
6. pre-flight 交叉引用错误；
7. Test 锁箱尚无一次性解锁和接口级隔离保证。

**正式 A-3b 继续 HOLD。** 即使后续审计获得 ACCEPTED，也仍须取得导师 MDE 认可、用户明确批准并通过真实 pre-flight；ACCEPTED 本身不构成正式实验批准，也不证明算法创新成立。

## 11. 需要修复的具体事项

1. **形成新编号预注册修订版（建议 R4）。** 修正 §5 的 pre-flight 指向，写入真实、可逐项核验的 pre-flight 清单；不得覆盖 R2/R3 历史文本。
2. **实现正式 40-family 分析入口。** 从原始数据动态构造任意 F 的 family/composition 层级；主检验只走 family-equal-weight、family-level 双侧 Student-t；df=F_observed−1；保留辅助分析的独立定位。
3. **统一 Student-t 退化规则。** 明确全零、非零常数、近零方差、正常方差行为；正式分析和 `_pvals_student_t()` 使用同一规则，并加入已知答案测试。全零不得返回显著 p=0。
4. **把缺失数据规则写成真实执行代码。** 分类并计数 technical missing；禁止 seed replacement；行为失败计 0 留分母；labelled null 或配对缺失必须抛错/拒绝分析；真实计算 family_loss 和 design_deviation；不得静默减少 family。测试必须调用真实处理函数，而非检查字典字符串。
5. **解决 composition 门槛与功效矛盾。** 二选一：
   - 预注册至少 5 个有效 composition 才能纳入，并规定 family_loss 与 F<34 的处置；或
   - 保留 ≥1，但预先定义不平衡缺失模型，重新模拟 ICC 网格下的 power/Type-I/MCSE/CI，并采用与异方差相匹配的推断。
   不得继续用固定 34×5 的 0.839/0.840 覆盖 m=1 的可能性。
6. **实现 H2–H5 的完整次要终点。** 真实数据提取、scenario/seed 配对、cluster/family 等权汇总、family-level t、恰好四项的 Holm；H4/H5 在最终输出中强制标为探索性。H2/H3 若要保持确认性，也须提供相应校准；否则一并降级为探索性。
7. **建立结构性 Test 隔离。** 生成器/锁箱不得把 Test payload 暴露给训练调用路径；`run_evolution()` 和最终评价入口应有明确 split 约束；提供一次性解锁和只读 final-evaluation 路径。用合成 sentinel 验证 Test 场景不能进入适应度，不读取真实 Test。
8. **修正 sign-flip 输出。** 将 `signflip_exact` 改为中性字段，记录 exact/MC、reps、实际 seed；在正式报告中固定为敏感性分析。
9. **补充上述真实路径测试并重跑 CI。** 测试必须包含失败断言和边界构造，不得只增加文档或字符串检查。
10. **更新 71 号之后的状态记录。** 不得继续把 R2-001/004/006 写成“已修复+已验证”；保留本轮发现及修复前后证据。

## 12. 下一步唯一任务

**Executor 完成 R4 corrective revision：实现正式分析/缺失数据/锁箱路径，解决不平衡功效与 Student-t 边界，修正 pre-flight 和 H2–H5，并提交新的独立复审。**

在独立复审 ACCEPTED、导师认可 MDE=0.10、用户明确批准和真实 pre-flight 全部通过之前，正式 A-3b、Test 查看或调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 及合并 main 均继续 HOLD。
