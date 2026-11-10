# 74 — D-064-R4 首批实现执行记录

**日期：** 2026-11-10  
**任务书：** 73_D064_R4_EXECUTOR_SPECIFICATION.md  
**状态：** PARTIAL IMPLEMENTATION / READY TO CONTINUE  
**正式 A-3b：** HOLD

## 1. Git / CI

- 工作分支：pilot-a-stateful-recovery
- 本报告维护前 HEAD：f2862840d5db6ce788244fc0c2d3487089db3b1d
- main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653（未修改）
- ahead / behind：185 / 0
- 最近一次含 R4 代码/测试修改的 CI：run 42788079429
- CI HEAD：5e7568050be4d7c1ac7511137bb5627a08ec044d
- CI 结论：success
- job log：pilot_a_recovery = 28 tests OK；pilot_a3b = 183 tests OK；合计 211 tests
- D-064-C manifest gate：PASS
  - manifest SHA-256：fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a
  - test-family SHA-256：01b41df8b06c318f90a4fc7aed45f673d13b50f14c08f56304ddffbb625a1411
  - test-scenario SHA-256：dded3bb72a08143177dd6b7f5c4c4ef5100b547028c9cc40fa2b87b6bd70c919
- 当前 HEAD f286284 是新增算法候选说明的文档提交，不含代码变化；接手时必须重新查询分支和 CI。

## 2. R4-P1：Student-t 退化边界

修改：experiments/pilot_a3b/power_hierarchical.py  
新增：experiments/pilot_a3b/test_64r4_student_t.py

实现：
- 新增 student_t_summary()，正式 family_level_tests() 和模拟 _pvals_student_t() 共用。
- F<2、NaN/Inf 输入 fail closed。
- 冻结数值容差：1e-12 × max(1, max|x|)。
- 全零差值：t=0、双侧 p=1、status=zero_effect_zero_variance。
- 非零常数差值：t=±inf、p=0、status=nonzero_constant_limit，明确标记为退化极限，不伪装成常规估计。
- 正常方差走统一 beta-tail Student-t 实现。

11 项新测试通过，含全零、正/负常数、近零方差、[1,2,3,4,5] 已知答案（t=4.2426406871，df=4，p≈0.01323559956）、Monte Carlo 一致性、F<2 和非有限值拒绝、family_level_tests() 真实调用路径。

## 3. R4-P2：正式 family-level 主分析初版

新增：experiments/pilot_a3b/formal_analysis.py  
新增：experiments/pilot_a3b/test_64r4_formal_analysis.py

实现：
- 独立于历史 D-064-B 六族 build_hierarchy()，不覆盖历史诊断入口。
- 动态 family 数；expected roster 每族严格冻结 5 个 primary compositions。
- AB / nsga2 在 scenario × optimizer seed 配对。
- 汇总顺序：optimizer seed → scenario → composition → family；family 等权。
- 明确技术缺失记录（infrastructure + reason），不补 seed。
- unexplained missing、labelled null、duplicate、unknown scenario、metadata/split mismatch 均 fail closed。
- 行为失败必须 class_success=0 并留在分母。
- composition 有任一配对技术缺失即无效；family 少于 5 个完整 primary compositions 时计入 family_loss。
- F<34 时 design_deviation=true、confirmatory_status=NOT_ELIGIBLE_UNDERPOWERED，隐藏确认性 Student-t 结果。

11 项新测试通过，覆盖 40-family eligible、33-family underpowered、技术缺失/家族损失、未知/重复/null、行为失败及五 composition 门槛。

**限制：** 该分析模块尚未接入正式 runner；尚未实现输入/manifest/code provenance、H2–H5、完整 pre-flight 或 Test 一次性 final-evaluation gate。必须独立复审，不能仅凭当前 CI 宣称正式分析系统完成。

## 4. CI 失败与修复如实记录

- test-only 先行提交触发预期失败：formal_analysis 尚未实现。
- 首次生产模块提交 CI 发现 synthetic fixture 的 pop() 移除了最后一条 F33 记录，但测试断言期望 F00；修正 fixture 为 pop(0)，不修改生产逻辑来迁就测试。
- 修复后 run 42788079429 success。
- Student-t test-first 提交也曾因 helper 尚未实现而失败；随后实现统一 helper，最终 CI success。
- 所有失败记录保留，不将失败隐藏为从未发生。

## 5. 算法提升方向（非实验结论）

新增 75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md。

历史 diagnostic3 结果显示 AB 的 R1/R2 条件恢复率高于 NSGA-II，但 R3 CorrectEscalation、R4 DamageContainment 和 avoidable harm 出现退化；hand baseline 的 R1/R2 表现更强。

候选 SBCG-NSGA-III：五维安全均衡 Pareto 目标 + 可行性优先 + family/failure-stratified counterexample mutation + hand-seed elite archive + 预注册 validation 选择规则。

**未实现、未运行、未证明提升。** 不得把历史诊断差异写成正式结果。

## 6. 下一步

唯一执行优先级仍为 R4：
1. 将 missing-data validator 接入真实 ledger 入口，补充输入/manifest/code hashes；
2. 完成 H2–H5 的真实数据路径与 Holm；
3. 实现 Train/Validation/Test 结构性隔离和原子 one-time final-evaluation gate；
4. 实现 R4 §9 可执行 pre-flight；
5. 按冻结 composition 纳入规则重新跑 ICC / MDE / Type-I / power / MCSE / CI；
6. 新增 R4 预注册并交独立 Reviewer。

真实 Test 逐场景标签/结果、正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main 合并继续 HOLD。