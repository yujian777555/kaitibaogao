# 73 — D-064-R4 Executor Corrective Specification

**日期：** 2026-11-10  
**角色：** Planner 对 Executor 的唯一实施任务书  
**权威审计：** 72_64R3_INDEPENDENT_REVIEW.md（REQUEST CHANGES）  
**独立证据：** experiments/pilot_a3b/audit_64r3_independent_checks.json  
**基线分支：** pilot-a-stateful-recovery  
**本任务开始时核验 HEAD：** 49429053f18d809d3b45e7de44c810cbeb203f7b  
**main：** 683b3fe7fc52c86e917d523fdc6bbb13abbfd653（禁止合并）  
**状态：** R4 corrective revision — NOT STARTED / IN PROGRESS；正式 A-3b = HOLD

---

## 0. 唯一任务与完成定义

完成 R4 corrective revision，逐项关闭 72 号报告 §11 的十项要求，形成一套从原始正式数据到主/次要终点、缺失数据审计、功效校准、Test 隔离和 pre-flight 的真实可执行系统，然后提交独立 Reviewer 复审。

**不得把以下事项混为一谈：**
- 189/189 既有测试通过 ≠ R3 统计/实现问题已关闭；
- 规则字典或文档说明 ≠ 缺失数据规则已进入真实执行路径；
- 辅助统计函数 ≠ 正式 40-family 分析入口；
- Test 历史诊断未使用 ≠ Test 已有结构性隔离；
- R4 实现完成 ≠ 正式 A-3b 获得批准；
- 功效达标 ≠ 算法增益成立。

## 1. 仓库与 Git 纪律

唯一仓库：yujian777555/kaitibaogao  
工作分支：pilot-a-stateful-recovery  
main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653（保持不动）

1. 开始前重新查询远端 work/main SHA、ahead/behind、工作区和最近 CI；不得依赖本文件的历史 SHA。
2. 只在工作分支实施；不得 force-push，不得合并 main。
3. R2、R3、70、71、72 及独立数值证据均保留，不覆盖、不改写历史结论。
4. 新预注册必须使用新编号 R4；R3 原文保持不变。
5. 每个实现任务先写失败测试，再实现，再运行目标测试和全套测试；不能只添加字符串断言。
6. 每个阶段记录输入数据 SHA、代码 SHA、配置、随机种子、输出 SHA、命令和真实退出码。
7. 真实 Test 逐场景标签/结果在 R4 实施和测试期间一律不得读取、打印、导出或用于调参。

## 2. R4 预注册与 pre-flight（阻断项 R3-001）

新增 64-A3B R4 候选预注册文件，不覆盖 R2/R3。

- 修正 §5 的交叉引用；正式执行条件必须指向 R4 中真实存在的 pre-flight 专节（建议 §9）。
- 明确 R4 是候选方案，仍需独立审计 ACCEPTED、导师 MDE=0.10 认可、用户明确批准、pre-flight 全通过。
- pre-flight 必须是可执行检查和逐项结果，不得仅写自然语言清单。
- 至少检查：批准记录状态；HEAD 与批准代码 SHA 一致；全套测试通过；训练/验证/测试 manifest 哈希；family/composition roster 完整性；Train/Validation/Test 零交叉；正式分析输入 schema；配对完整性；missing-data 规则；有效 family 数与每族 composition 门槛；预算；停止规则；无 Test 访问记录；最终 runner 的一次性状态为 UNUSED。
- 任何一项缺失/失败均 fail closed；pre-flight 不得访问真实 Test 标签或结果。
- 记录 mde_status=PROPOSED_MDE_PENDING_ADVISOR_APPROVAL，不得伪造导师或用户批准。

## 3. 正式 40-family 分析入口（阻断项 R2-001 / R3-005）

新增正式分析模块或明确命名的正式入口。不得把历史 D-064-B 的 build_hierarchy() 直接改成“正式”而不保留诊断用途。

要求：
1. 从正式原始 run ledger + frozen manifest 构造任意观察到的 F、family、composition、scenario、seed 层级；不得硬编码 6 families、42 clusters、7 compositions、12 zero-denominator。
2. 主比较唯一为 AB − canonical NSGA-II；按 scenario/seed 配对，seed 在 scenario 内汇总，scenario 在 composition cluster 内汇总，composition cluster 在 family 内汇总，family 之间等权。
3. 主终点仅使用 R1+R2 CondRecSucc；R3/R4 safety outcomes 独立报告，不得混入主终点。
4. 只允许 family-level paired differences 进入双侧 one-sample Student-t；α=0.05，df=F_observed−1。cluster bootstrap/sign-flip 不得替代主检验。
5. 输出每层计数、配对问题、family means、总体等权效应、t/df/p、效应区间、分析状态、输入/manifest/code hashes。
6. 任一完整性问题必须 fail closed；不能通过跳过 null、静默删除 family 或缩小分母来生成可发表结论。
7. 历史 diagnostic3 分析保留为历史复核路径，命名和报告中明确非正式 confirmatory analysis。

## 4. Student-t 退化与数值规则（阻断项 R3-004）

正式分析和功效模拟必须调用同一底层 p-value/统计量实现，不能保留两套互相矛盾的边界行为。

至少覆盖：
- F<2：拒绝推断。
- 全零差值（mean=0 且 sd 在预定容差内）：t=0、双侧 p=1，状态标记为 zero_effect_zero_variance；不得返回 p=0。
- 非零常数差值（sd 在容差内且 |mean| 超容差）：明确采用退化极限规则并标记 nonzero_constant_limit；若采用 t=±∞、p=0，必须在 R4 中说明这是零方差极限而不是普通可估计 t 检验，并报告 degenerate 状态。
- 近零但非零方差：使用预先冻结的数值容差与稳定算法，不得因浮点噪声产生无说明的显著性。
- 正常方差：与独立高精度/可信统计库参考答案一致。

容差、算法和退化规则必须写入 R4；正式分析与模拟完全共用。增加已知答案和 property/boundary tests。

## 5. 缺失数据与 composition 门槛（阻断项 R2-004 / R3-002 / R3-003）

### 5.1 必须是真实执行逻辑

将 missing-data policy 实现为真实 validator/normalizer，而非仅返回字典。处理原始数据前先对照 frozen expected roster。

必须输出并验证：
- technical_missing_runs：按 run/seed/arm/scenario 记录原因和数量；
- family_loss：因有效 composition 数不足而损失的 family 及原因；
- design_deviation：实际 F、有效 composition 数、设计门槛是否偏离；
- behavioural_failure_count：行为失败作为有效结果计 0，保留在分母；
- integrity_errors：duplicate、labelled null、配对缺失、metadata mismatch 等。

规则：
- 明确登记的基础设施/技术故障才可分类为 technical missing；不得仅因某行不存在就猜测为技术缺失。
- technical missing 计数、不补 seed、不重跑替换、不静默删除。
- 行为失败是被测行为结果，计 class_success=0 并保留分母。
- labelled row 的 class_success=null、AB/NSGA-II 配对缺失、重复键、manifest 外数据、metadata 冲突必须 fail closed。
- 不完整 family 必须明确计入 family_loss；不得静默从 family 集合消失。
- F_observed<34 必须触发 design_deviation；主确认性检验标记 NOT_ELIGIBLE / UNDERPOWERED，不得仍声称达到原设计功效。
- 每个错误都要有对应真实路径测试，验证分析被拒绝或按预注册规则处理。

### 5.2 composition 门槛与功效设计必须一致

不得保留“每族最低 1 个 composition”同时引用固定 34×5 功效。

**Planner 推荐优先方案：** 每个纳入 family 必须提供 5 个有效 primary-eligible composition；冻结 outcome-blind composition priority/roster，明确主分析如何从 7 个候选中形成每族恰好 5 个 primary composition。不得根据成功率、算法差值或 Test 结果选择 composition。超出主分析的有效 composition 只能作为预先定义的敏感性分析。少于 5 个有效 composition 的 family 计入 family_loss。

Executor 必须证明该选择规则不会造成结果依赖的选择，并报告各 family 的缺失模式。若该方案无法合理成立，提交另一条完整统计方案（允许 m_f 不等，但必须匹配异方差推断）；不得自行保留最低 1 的旧规则。

正式确认性设计门槛建议为 F_observed≥34 且每个 family 的 primary composition 数恰为 5。若 F<34，数据可以保留并作描述性分析，但不得把原 34×5 的功效声明用于该次结果。

### 5.3 功效与 Type-I 重新校准

对最终选定的缺失/纳入规则重新模拟，至少覆盖：
- ICC = 0、0.05、0.10、0.20；
- MDE = 0.10；null μ=0；
- family 数 F=34、40，以及可能的 family-loss 边界；
- 每族恰好 5 个有效 composition 的正式设计；
- 与允许技术缺失相符的边界/不利缺失情景；
- 10,000 MC，冻结并记录 seeds；
- power、null Type-I、MCSE、95% MC 区间；
- Student-t 实际采用与正式分析完全相同的函数。

如果 Type-I 不满足预设容差，或功效低于 0.80，必须修改设计或将其标记为未达标；不得反向调整 MDE 或模拟参数来凑过门槛。保存原始 simulation config、逐格结果和 SHA。

## 6. H2–H5 次要终点（阻断项 R2-006 / R3-006）

必须实现真实分析路径，而非仅保留 Holm helper。

四项对比：
- H2：AB > A；
- H3：AwaitSLA > A；
- H4：AwaitSLA > AwaitFixed；
- H5：AB > AwaitSLA。

每项都必须：
1. 从原始数据提取对应方法和 R1/R2 终点；
2. scenario/seed 成对比较；
3. seed 汇总到 scenario，scenario 汇总到 composition cluster，cluster 汇总到 family；
4. family 等权，执行 family-level two-sided Student-t，df=F−1；
5. 收集恰好四个 p 值，统一执行 Holm；不得混入历史六项 cluster-level sign-flip；
6. 输出 raw p、Holm-adjusted p、effect、CI、F、df、缺失/配对计数和状态。

H4/H5 在任何报告输出中必须标记 exploratory，禁止作为确认性证据。H2/H3 若保留 confirmatory，必须提供对应 null/partial-null 校准及 Holm family-wise Type-I 证据；否则 R4 应将 H2–H5 全部降级为 exploratory，并在预注册、代码和报告中保持一致。不能只在文字中声明。

## 7. 结构性 Test 隔离与一次性 final evaluation（阻断项 R3-007）

R4 实施期间不得读取真实 Test payload、逐场景标签或结果；只用合成 sentinel split 做拒绝测试。

要求：
- manifest builder 返回给训练/规划调用者的对象不得包含 Test scenario/verdict/label payload；只允许公开 test count、family roster hash、scenario hash、split summary。
- Train 和 Validation 数据接口明确分离；演化适应度入口只允许 split=train；validation 只允许用于预注册规定的选择/停止，不能进入适应度训练池。
- run_evolution() 必须在评价任何个体前拒绝 Test/Battery/unknown split（除非某个 split 被显式、窄范围地授权给专用 gate，且有单独类型/入口）。
- evaluate_controller() 或等效函数不得让 Test label 经 objective/fitness 路径流入 EA。
- Test 只能由独立 final-evaluation wrapper 访问；该 wrapper 要求独立审批记录/授权 capability，且采用原子 one-time ledger。先消费解锁状态再读取 payload；重复调用、并发调用、缺少审批、hash 不符或中途失败均 fail closed。
- 一次性 final evaluation 只读，不允许写回种群、适应度、参数、算子、选择或 early stopping。
- 用临时目录和 synthetic sentinel 测试：训练调用者拿不到 Test payload；把 sentinel Test scenario 传给 run_evolution 必须在 fitness 被调用前拒绝；一次性 wrapper 第二次调用失败；未授权时不读取任何 payload。
- 不读取真实 Test 标签来证明 Test 隔离。

## 8. Sign-flip 输出与审计元数据（阻断项 R3-008）

- 将 signflip_exact 改为中性名称 signflip。
- 返回 p、method（exact enumeration / Monte Carlo）、n_resamples、random_seed_used、F。
- F≤15 精确枚举；F>15 10,000 次 MC，使用 +1 修正。
- exact 模式明确记录无需随机抽样；MC 记录实际 seed（例如 base seed + 1），不得只记录默认参数。
- 仅作为敏感性分析；主显著性结论只能来自 family-level Student-t。

## 9. R4 Pre-flight（真实、可执行、可审计）

R4 §5 的 GO 条件必须指向本节。实现 run_formal_preflight() 或等效函数，并输出机器可读 JSON + 人类可读报告。

至少包含：
1. R4 文本 SHA、实现代码 SHA、Git HEAD；
2. 独立审计状态；导师 MDE 状态；用户批准状态；
3. tests/CI 真实状态；
4. train/validation/test roster 和 manifest hashes；
5. split overlap = 0；train runner 只收到 train；validation 仅走 selection；Test payload 未暴露；
6. expected roster、paired rows、duplicate/null/metadata checks；
7. family 数 F、每族 primary composition 数、family_loss、technical missing、design_deviation；
8. formal analysis schema 与主/次要终点函数版本；
9. budget、seed、stopping rule；
10. Test one-time ledger = UNUSED，且本次 pre-flight 本身没有解锁或读取 Test；
11. 所有条件满足才返回 GO；否则 HOLD 并列出 blocking reasons。

当前 R4 阶段审批记录必须保持未批准状态；不能伪造 ACCEPTED、导师签字或用户批准。pre-flight 代码只可用 synthetic fixtures 测试，不能触发正式 A-3b。

## 10. 测试、CI 与证据要求

新增真实路径测试，至少覆盖：
- 40-family 动态分析与 family 等权；
- F<34 的 design_deviation / confirmatory ineligible；
- labelled null、unpaired AB/NSGA-II、duplicate、unknown roster 的 fail-closed；
- technical missing 明确计数且不替换 seed；
- 行为失败 0 保留分母；
- family_loss 真实计算；
- composition=4 拒绝纳入，composition=5 接受；
- 全零、正/负常数、近零方差、正常方差；
- 正式 Student-t 与 power simulation 边界一致；
- H2–H5 四项数据流、配对、family 汇总、恰好四项 Holm；
- H4/H5 输出强制 exploratory；
- Test payload 不返回给 train caller；
- Test sentinel 在 fitness 被调用前被拒绝；
- one-time unlock 原子消费、第二次调用拒绝；
- signflip exact/MC 字段、实际 seed、+1 修正；
- pre-flight fail-closed。

每个测试必须调用真实生产函数；不得只检查源码字符串、函数名或字典常量。至少一个已知答案统计测试与独立可信实现比较。

完成后：
- 运行相关测试、完整 pilot_a_recovery 与 pilot_a3b 测试；
- Ruff/格式/类型检查按仓库既有配置执行；
- CI 必须在含代码修改的最终提交上 success；
- clean-clone 复现；
- 重新核对 manifest/test-family/test-scenario hashes；任何预期变化都要解释并更新 R4；
- 报告真实命令、退出码、测试计数、CI run、最终 SHA、main 未变、工作树 clean。

## 11. 交付文件

至少新增：
- 64_A3B_PREREGISTRATION_CANDIDATE_R4.md
- 正式分析模块（名称由实现决定）
- 正式 missing-data validator / preflight / final-evaluation guard
- test_64r4_*.py
- 功效重算 JSON/报告
- 73_R4_EXECUTION_REPORT.md（Executor 真实结果；本任务书 73 文件保留，不覆盖）
- 更新 README.md、05_DECISION_LOG.md、SESSION_HANDOFF.md、NEXT_SESSION_PROMPT.md

保留 72 号独立审计报告不变。完成后将全部材料交独立 Reviewer；Executor 不得自评为 ACCEPTED。

## 12. 最终状态与禁止事项

R4 代码与文档完成后，状态只能是 READY_FOR_INDEPENDENT_REVIEW，不得标记 formal GO。

在独立 Reviewer ACCEPTED、导师认可 MDE=0.10、用户明确批准、R4 §9 pre-flight 全部通过之前：
- 不运行正式 A-3b；
- 不读取/查看/导出/调参真实 Test；
- 不运行 Pilot B；
- 不申请/运行 A800 或 ARWM；
- 不调用真实 LLM API；
- 不访问 UndoBench TEST；
- 不启动 ThinkingBox；
- 不合并 main。

**唯一下一动作：** 按本任务书完成 R4 corrective revision，并提交独立复审。
