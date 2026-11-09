# 65 — D-064：64 号预注册草案独立审查（REQUEST CHANGES）

**日期：** 2026-11-09  
**审查基线：** `4f23abed3150e09703839b980ad3afc9bb14dfb3`  
**工作分支：** `pilot-a-stateful-recovery`  
**main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`（未修改）  
**审查对象：** `64_A3B_PREREGISTRATION_CANDIDATE.md`、D-063 分析/功效/任务族代码与原始诊断数据  
**结论：** D-063 工程交付验收；64 号预注册草案 **REQUEST CHANGES，暂不批准**。正式 A-3b 继续 HOLD。

---

## 0. 总结判定

D-063 的独立复算程序、任务族候选枚举脚本、统计测试和 CI 均已提交。GitHub Actions run `42615985837` 在审查基线 commit 上真实成功：`pilot_a_recovery` 28/28，`pilot_a3b` 68/68，合计 **96/96**。

但“CI 通过”只证明当前回归测试通过，不等于 64 号预注册在 estimand、功效、独立性和正式数据生成方面已经闭合。以下阻断项必须先修复，不能把 64 号草案直接交用户批准并启动正式实验。

## 1. P0 — 主要终点与功效分析使用的 estimand 不一致

### 1.1 64 号主要终点

`64_A3B_PREREGISTRATION_CANDIDATE.md` §3 将主要终点定义为 **CondRecSucc**：仅在 R1+R2 场景上计算条件任务完成率。R3 使用 CorrectEscalation，R4 使用 DamageContainment，三者不是同一结果变量。

### 1.2 D-063 功效分析实际计算的变量

`experiments/pilot_a3b/power_simulation.py` 的 `load_cluster_diffs()` 只过滤 `class_success is None`，没有限制 `label in {R1,R2}`。因此当前主对比 `AB vs nsga2` 的 54 个 cluster 差值混合了：

- R1/R2：任务完成；
- R3：正确升级/零残留；
- R4：损害遏制。

`analyse_diagnostic3.py` 的 `contrast_stats()` 默认也对所有标签计算 `class_success`，没有输出与 64 §3 完全一致的 R1+R2 配对 cluster primary contrast。

所以报告中的 `delta=0.1049, SD=0.4040, n=54` **不是 64 号草案定义的 CondRecSucc 主终点的方差估计**，145 个 cluster 的功效规划不能直接作为 CondRecSucc 的样本量依据。

### 1.3 审查用原始数据快速核对（不是正式统计产物）

原始 diagnostic3 数据有 54 个 task×composition clusters；其中只有 **42 个 cluster 含 R1/R2 场景**，另有 12 个 cluster 只有 R3/R4。按 R1/R2 过滤、先对相同 scenario 的配对算法 seed 求均值、再对 cluster 等权聚合，审查用快速复算得到：

- CondRecSucc 的 AB−NSGA-II 配对差约 **+0.3175**；
- cluster SD 约 **0.3189**；
- 可用 primary clusters = **42**。

该值是本审查的诊断性核对，尚未由正式分析入口输出，不应直接用于预注册或论文。它只说明：primary estimand 的效应量、方差和有效 cluster 数与当前全类别 `class_success` 统计不同，必须建立正式、可复现的专用分析。

### 必须修复

1. 在 `analyse_diagnostic3.py` 中新增明确的 `CondRecSucc` 对比：只使用 R1/R2，按 scenario 配对、seed 嵌套、task×composition cluster 等权；输出每 cluster 分母、零分母 cluster 数、有效 cluster 数、均值差、cluster SD、CI、sign-flip p。
2. R3/R4 分别输出 CorrectEscalation 与 DamageContainment，不混入 CondRecSucc。
3. 重新运行功效分析，输入必须与 64 §3 完全相同的 primary estimand。
4. 预先规定没有 R1/R2 场景的 cluster 是排除、补齐还是设计失败；不得在看到结果后决定。
5. 将新的主要 estimand、样本量和结果写回 64 草案，并解释 D-062 旧的全类别 `class_success` 结果只作为诊断性历史指标。

## 2. P0 — 当前“Monte Carlo 功效”是参数化正态模拟，不是经验重采样/符号翻转功效

检查 `power_simulation.py`：

- `mc_power()` 默认 `assume_mean_shift=True`，实际使用 `rng.gauss(mde, sd)` 生成正态样本；
- `main()` 从未调用 `assume_mean_shift=False` 的经验中心化重采样分支；
- `test="signflip"` 分支仍使用正态近似 z 值，并未执行 sign-flip 检验；
- 所谓 t 检验使用标准正态 CDF 近似，而不是有限自由度 Student-t 分布；
- 结果没有输出每个功效估计的 Monte Carlo 标准误/置信区间。

因此当前结果应准确称为 **参数化正态 Monte Carlo 规划**，不能称为已经完成 empirical cluster bootstrap/sign-flip power simulation。保存结果中的 null FPR 在小样本网格上也出现偏高值（例如 n=18 时 0.0685），与正态近似对有限样本 t 检验的校准不足一致。

### 必须修复

- 用 primary estimand 的 cluster-level paired differences 做经验中心化重采样，或明确采用有理论依据的参数模型并同时做经验分布敏感性分析；
- 使用与正式预注册一致的统计检验（Student-t、cluster sign-flip 或预先指定的稳健检验），不能把 z 近似标记成 sign-flip；
- 报告 null FPR 校准、MCSE/区间、模拟次数、随机种子、收敛检查；
- 对任务族内相关性做敏感性分析，不能只在独立 cluster 假设下生成样本。

## 3. P0 — ICC≈−0.09 不能证明 task×composition clusters 独立

当前 ICC 将 54 个 task×composition cluster 按 task family 分组，只有 **6 个 task families**；validation 子集只有 **2 个 task families**。负 ICC 点估计不等于证明不存在正相关，更不能在没有区间估计的情况下写成“cluster 独立性成立”。

未来 test 是 17 个 task families × 9 compositions。相同 task family 下的 9 个 composition cluster 可能相关，task×composition 不一定可视为 153 个完全独立单位。

### 必须修复

- 明确统计推断的独立抽样单位：task family、task×composition，或层级模型中的两层随机效应；
- 对 ICC 给出不确定性区间；validation 的 2 组估计只能作为极弱的探索性证据；
- 至少做 ICC=0、0.05、0.10、0.20 的设计效应/功效敏感性，或用 family-level resampling / hierarchical simulation；
- 若采用 task-family 层级 bootstrap，功效模拟必须按未来 17 个 task families 的层级结构生成；
- 删除“ICC 负值证明独立”的表述，改为“当前开发数据未检出正的 between-family ICC，但估计不精确，仍需敏感性分析”。

## 4. P0 — 任务族候选是合同属性筛选，不是语义有效性验证；正式生成器尚未落地

### 4.1 候选语义

`task_family_expansion_audit.py` 枚举 10 个工具的三步排列，再由 `meaningful()` 检查：
- 至少一个非幂等工具；
- 至少一个可补偿工具；
- 至少一个不可补偿工具。

这得到 576 个候选，但没有验证任务目标、前置条件、后置条件、工具之间的数据依赖或业务顺序是否成立。因此“合同属性上满足混合约束”可以成立；“576 个语义有效业务工作流”尚无证据。

### 4.2 多样性选择的实现与报告不一致

审计脚本的 `greedy_diverse()` 评分只最小化与已选序列的工具重叠，没有把合同 profile 多样性加入目标。实际选出的 23 个新序列覆盖 **11/18** 个候选 contract profiles；test 17 族覆盖 **10/18**。报告可以说“工具重叠贪心选择”，不能说“profile diversity 已被联合优化”。

### 4.3 新划分尚未接入正式场景生成器

- `pilot_a3.py` 的 `TASKS` 仍是固定 6 个任务族；`make_fault_vector(task_name,...)` 通过 `TASKS[task_name]` 取工具序列；
- `run_diagnostic3.py` 仍硬编码 4 个 train task 与 2 个 validation task；
- 63 号审计输出的 8/4/17 家族划分目前是候选清单，不是已集成并跑通的正式 8/4/17 场景生成器。

### 必须修复

1. 为候选三步序列定义明确的合成 saga 语义：任务目标、工具输入/输出、前置条件、后置条件、可执行顺序和失败后状态。
2. 增加独立语义 validator；无效排列必须排除并留存理由，不能只靠合同属性判定“meaningful”。
3. 若研究对象仅是抽象工具序列，应在论文与预注册中明确是 synthetic workflow，不作真实业务语义泛化。
4. 修正多样性算法描述，或真正加入 profile coverage/diversity 目标；输出所选 train/validation/test 的 profile 覆盖矩阵。
5. 实现通用正式场景生成器，支持 8/4/17 划分、场景 seed、R1–R4/UNKNOWN 标签、manifest 和 hash；运行真实生成测试。
6. 明确 9 种 fault-composition 类别在 train/validation/test **均重复出现**，因此确认性主张是“新工具序列任务族 × 已知故障组合类别”的跨任务族泛化，不是对未见 fault-type vocabulary 的泛化。

## 5. P1 — MDE、失效预留和 test cluster 数尚未唯一冻结

当前参数化模拟结果：MDE=0.10、80% power 需要 145 个可分析 clusters；按 15% 失效预留需要招募 171 个。64 号方案只有 153 个 test clusters，15% 失效后约 130 个有效 clusters；保存的功效网格在有效 n=123 时 power=0.779，在 n=138 时 power=0.810，因此 130 的功效预计略低于 80%（准确值应由修复后的仿真给出）。

64 §4/§5 目前同时提到：
- MDE=0.10：无失效时 nominal power 约 80%；
- MDE=0.1173：含失效预留后功效超过 80%；
- 实际功效不足时不加测。

这不是一个唯一冻结的确认性样本量方案。0.1173 又来自历史 validation 的观察效应点估计，不应自动成为最小有意义效应（MDE）；必须给出独立的科学/实践意义理由。

### 必须修复

在正式预注册中只能选定一套：
- 以 MDE=0.10、80% power、15% 失效预留为目标，扩充至至少 171 个有效招募 clusters（按现有 9 compositions 即 19 个 test families）；或
- 明确接受较低功效，并在预注册中写明精确目标功效与不加测规则；或
- 另行论证一个事前有意义的 MDE。

最终选择必须基于修正后的 CondRecSucc 功效分析和层级相关敏感性，不能基于看过的正式 test 效果。

## 6. P1 — UNKNOWN、类别分布和主要终点分母需要冻结

55-R1 设计规定 UNKNOWN 预算上限（≤5%）并单列报告；64 号草案只写“UNKNOWN 不进入主要分母”，没有保留明确上限/超限处理规则。

此外，诊断数据的 54 clusters 中只有 42 个包含 R1/R2。未来 test 的 153 个 task×composition cluster 不能自动全部视为 primary-eligible clusters。必须在正式 test 场景清单冻结前统计：
- R1/R2/R3/R4/UNKNOWN 的场景数；
- 含 R1/R2 的 primary-eligible clusters 数；
- 每个 cluster 的 R1/R2 分母；
- R3/R4 各自的安全指标分母；
- UNKNOWN 超过预设上限时的处理（建议：该轮确认性实验判为标签门禁失败，不通过事后剔除恢复显著性）。

标签器必须在 test 解盲前冻结；所有标签由策略无关的 reachability/verdict 过程生成。

## 7. P1 — 安全硬门与实现冻结细节

64 §3 “任何安全指标 >0 的方法直接判定该对比不通过”需要更精确：
- AB 自身是否必须满足所有硬安全指标为 0？
- NSGA-II 发生安全违规时，是否只判定 NSGA-II 未通过，而不连带否定 AB？
- 若 AB 与 NSGA-II 都有违规，主要性能差异是否仍只作描述而不作成功结论？
- 零观察事件必须报告事件数、暴露分母和二项置信上界；不得把零观察写成零风险。

另有两个实现冻结细节：
- `run_diagnostic3.py` 生成 60 个初始 FSM，但 `run_evolution()` 只使用 `init_pool[:pop_size]`；当 pop=48 时实际使用前 48 个，后 12 个未使用。预注册须明确实际初始种群的确定规则。
- 64 写“27+ 测试全绿”，审查基线 CI 实际为 96/96。正式预检应引用精确 commit、测试命令和真实 CI run；若批准后任何实验代码变化，必须重新审查/批准对应 SHA。

## 8. 64 号草案批准前的最小修复顺序

1. **D-064-A：** 为 CondRecSucc 建立 R1/R2-only paired cluster 分析，报告有效 cluster 数和 cluster-level SD。
2. **D-064-B：** 重做 estimand 对齐的经验/层级 Monte Carlo 功效分析；完成 ICC 不确定性和设计效应敏感性；冻结 MDE、power、attrition 与 test cluster 数。
3. **D-064-C：** 给任务序列增加语义合同/有效性验证；修正 profile-diversity 描述；实现并测试 8/4/17（或修正后的）正式场景生成器与标签 manifest。
4. **D-064-D：** 补齐 UNKNOWN 上限、类分布、硬安全门解释、初始池规则、预算口径、精确 code SHA 和 CI 证据。
5. 更新 64 号草案为新修订版，保留旧版本差异记录，再提交用户审阅。

## 9. 当前 GO / HOLD

**GO：**
- D-064-A/B/C/D 统计、数据和协议修复；
- 正式场景生成器和标签器实现/测试；
- 预注册草案修订；
- CI 与仓库交接文档维护。

**HOLD：**
- 正式 A-3b 确认性实验；
- 生成后查看/调参 held-out test；
- Pilot B；
- A800/ARWM；
- 真实 LLM API；
- UndoBench TEST；
- ThinkingBox。

**唯一下一步：** 先完成 D-064-A——将正式主要终点 CondRecSucc（R1+R2 only）加入配对 cluster 分析器，复算诊断数据的 primary effect/SD/有效 cluster 数；在这一步完成前，不批准 64 号草案，也不启动正式 A-3b。


---

## 10. p 值差异幅度更正

D-063 执行汇报将复算 p 值差异描述为“仅第 3 位微差”。逐项对照 `diagnostic3_recomputed_report.md` 后，这一描述不够准确：

- primary AB vs NSGA-II：0.064734 vs 0.062，差 0.002734；
- validation AB vs NSGA-II：0.238190 vs 0.2277，差 0.010490；
- validation AB vs A：0.009998 vs 0.0082，差 0.001798；
- all AwaitSLA vs A：0.006748 vs 0.0047，差 0.002048；
- all AwaitSLA vs AwaitFixed：0.004749 vs 0.0032，差 0.001549；
- all AB vs AwaitSLA：0.009498 vs 0.0072，差 0.002298。

这些差异可能来自置换 Monte Carlo 随机种子不同（复算 20261110、旧报告 20261108），且当前显著性分类未改变；但不能一概表述为“仅第三位微差”。正式报告应给出绝对差值、置换次数和 Monte Carlo 不确定性，并将复算结果作为唯一可执行复现值。效应量 Δ 对齐不意味着 p 值逐项一致。

---

## D-064-A 修复记录（2026-11-09）

**P0-1（主要终点 estimand 不一致）已修复**，正式产物：`experiments/pilot_a3b/condrec_analysis.py` + `test_condrec_analysis.py`（13/13）+ `condrec_diagnostic3.{json,csv,report.md}`，详见 `66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md`：

1. CondRecSucc 仅用 R1+R2（64 §3 定义）；R3 CorrectEscalation / R4 DamageContainment 独立输出。
2. 四层配对（scenario×seed 配对 → seed 嵌套均值 → cluster 聚合 → cluster 等权），scenario 加权敏感性并报；缺失配对/重复/cluster 失配/零分母全部显式检查。
3. **零分母规则预规定**：无 R1/R2 的 cluster 排除并登记（12 个 = delay_rate_permission + partial_comp_failure × 6 任务族），不补零不静默删除。
4. 真实复算：**eligible 42 clusters、Δ=+0.3175、SD=0.3189、CI [0.218, 0.411] 不含 0、sign-flip p=0.000125**（真实 cluster 级符号翻转 MC 8000 次，非 z 近似）；scenario 加权 Δ=0.3145 一致。本审查的快速核对值（+0.3175/0.3189/42）与正式复算逐位一致。
5. **结论翻转**：正确 estimand 下 AB vs NSGA-II 强显著（原全类别 +0.1049/0.065 系 R3/R4 稀释）。
6. R3/R4 权衡如实记录：AB R3 0.226 vs NSGA-II 0.679、R4 0.80 vs 0.933——主要终点领先不掩盖安全行为率落后。

**P0-2/3/4、P1-5/6/7 未处理**（属 D-064-B 及后续：功效/ICC 敏感性重做、任务族语义 validator 与正式生成器、MDE/样本量唯一冻结、安全门细则）。


---

## D-064-A 关闭 P0-1 后的状态更新（2026-11-09）

D-064-A 已正式完成；P0-1（主要 estimand 与功效分析输入不一致）在诊断分析层面关闭。证据见 `66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md`。

- CondRecSucc 仅 R1+R2：42 eligible clusters / 54 design clusters；
- 42 个 cluster 嵌套在 6 个 task families，每 family 7 个 eligible compositions；
- AB=.5582，NSGA-II=.2407，Δ=+.3175，cluster SD=.318856；
- cluster bootstrap CI [.218254,.411376]；cluster-level sign-flip p=.000125（8000 次）；
- scenario-weighted Δ=.314465；
- R3/R4 仍显示 AB 的正确升级/遏制行为率落后，需独立报告。

**重要限定：** D-064-A 的 42-cluster bootstrap/sign-flip 尚未处理 task-family 内相关性。点估计已独立复算，但 CI/p 的有效性需要 D-064-B 重新评估。不能把 D-064-A cluster-level 显著性当作已解决 family dependence 的确认性证据。

### D-064-B 当前授权

GO：以 D-064-A CondRecSucc cluster differences 为基础，执行 task-family 层级方差、ICC 不确定性、family-block resampling、ICC-controlled power simulation、Type-I error 校准和条件性样本量分析。完整执行提示词：`67_D064B_POWER_AND_HIERARCHICAL_SENSITIVITY_EXECUTION.md`。

**D-064-B 仍须解决：**
- P0-2：正确 estimand 下的经验/层级功效分析与 null calibration；
- P0-3：task-family 内相关性和 ICC 不确定性。

P0-4（任务语义 validator/正式生成器）及 P1-5/6/7（MDE/样本量最终冻结、UNKNOWN/安全门细则、实现与预检冻结）仍未关闭。

64 号预注册仍为 REQUEST CHANGES；正式 A-3b 继续 HOLD。

### D-064-B 修复记录（2026-11-09）

**P0-2（功效模拟方法学）与 P0-3（ICC 独立性）已修复**，见 `68_D064B_HIERARCHICAL_POWER_REPORT.md`：双生成机制（family-block 重采样 + ICC 层级模拟）、真实符号翻转/t/自助三检验对照、null 校准（t 0.050–0.056 ✓；bootstrap CI 检验反保守 ✗→不作 α 检验）、MCSE/区间、ICC 敏感性网格（0/0.05/0.10/0.20）、"负 ICC 不证明独立"表述落实。MDE 网格含 0.05–0.15，0.1173 仅敏感性。所需 families 表与 17-family 条件性评估完成。**P0-4 与 P1-5/6/7 转 D-064-C。**
