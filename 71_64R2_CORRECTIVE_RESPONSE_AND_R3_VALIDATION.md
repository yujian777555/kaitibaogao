# 71 — 64-R2 修正响应与 R3 验证（D-064-R2 Corrective Revision）

**日期：** 2026-11-10  
**角色声明：** 本报告由 Executor 完成修复与验证，**不是独立审计**；最终判定须由独立 Reviewer（R2 复审）作出。  
**R1 审计：** `70_64R2_INDEPENDENT_REVIEW_R1.md`（REQUEST CHANGES）  
**修订版预注册：** `64_A3B_PREREGISTRATION_CANDIDATE_R3.md`（R2 原文保留于 `64_A3B_PREREGISTRATION_CANDIDATE.md`）  
**新增测试：** `test_64r3_protocol.py` 15/15

---

## 1. 问题关闭表

| 审计问题 | 修改文件 | 实际修复 | 测试证据 | 状态 |
|---|---|---|---|---|
| **R2-001** 主检验定义冲突 | `64_..._R3.md` §1/§2 | 统一为唯一主检验=双侧 family 级 Student-t（α=0.05，family 级配对差值，family 等权）；符号翻转降为敏感性、bootstrap 降为描述性；AB vs Hand 明确描述性 | `test_64r3_protocol.test_signflip_and_student_t_reported_separately`、`test_bootstrap_output_has_no_p_value` | **已修复+已验证** |
| **R2-002** df=39 固定错误 | `power_hierarchical.py`（新增 `family_t_df()`，`family_level_tests` 改用）；`64_..._R3.md` §2 | df=F_observed−1 动态化；R3 文档写明 40→39、34→33、低于设计按实际 df 并触发设计偏离 | `test_df_39_at_forty_families`、`test_df_33_at_thirtyfour_families`、`test_df_tracks_observed_family_count`、`test_df_rejects_too_few_families`、`test_family_level_tests_reports_dynamic_df`（真实代码路径） | **已修复+已验证** |
| **R2-003** manifest SHA 不一致 | `64_..._R3.md` §4、维护文档、本报告 | 独立重建确认 **fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a**（与 CI run 42661732606 一致）；af83f065… 标注为 POWER_DESIGN 修订前 superseded；test-family 01b41df8… / test-scenario dded3bb7… 不变 | 独立 `build_candidate_manifest()` 重建输出（fb832bcc 匹配）；`test_d064c_audit.test_independent_rebuild_reproduces_manifest_hash` | **已修复+已验证** |
| **R2-004** attrition 表述 | `power_hierarchical.py`（新增 `missing_data_rules()`）；`64_..._R3.md` §6 | 定性"15% 规划损耗向下取整保守保留 34×5"（5/7≠精确 15%）；技术缺失/行为失败/完整性失败三分；family 门槛 ≥1；F<34 触发 design_deviation；选择性删除禁止 | `test_rules_frozen_fields`、`test_behavioural_failure_scores_zero_not_dropped`、`test_zero_valid_composition_family_is_droppable_and_countable` | **已修复+已验证** |
| **R2-005** MDE 审批门缺失 | `64_..._R3.md` §5 | GO 顺序显式四条：独立审计 ACCEPTED → **导师 MDE 认可** → 用户批准 → pre-flight 通过；MDE 状态保持 PROPOSED_MDE_PENDING_ADVISOR_APPROVAL | 文档条款（`64_..._R3.md` §5）；`formal_scenario_generator.POWER_DESIGN.mde_status` 字段 | **已修复；尚待导师批准** |
| **R2-006** 次要终点不足 | `64_..._R3.md` §3 | H2–H5 逐项定义指标/计算/配对单位/family 汇总/检验/Holm family {H2..H5}/解释边界；H4/H5 标注探索性（Type-I 未单独校准）；安全终点独立报告 | `test_holm_edge_cases`；H4/H5 探索性标注为文档约束 | **已修复+已验证（H4/H5 校准限制已声明）** |

## 2. 与 R1 事实核对（逐项独立核实，非照抄）

| R1 断言 | 核实结果 |
|---|---|
| 最终 CI manifest = fb832bcc… | **成立**：本地独立重建输出逐字符一致；原因=POWER_DESIGN 元数据（0.839 等）计入 manifest 内容，af83f065 为其修订前哈希 |
| test-family/scenario 哈希未变 | **成立**：01b41df8… / dded3bb7… 重建一致 |
| 代码 df 动态（F−1） | **成立**：`family_level_tests`/`_pvals_student_t` 均 F−1；R2-002 症结在 R2 文档写死 39 |
| 功效 JSON 0.8391/CI/0.0541 | **成立**：`power_final_design_check.json` 记录相符；统计补丁后复算 0.840 [0.833,0.847]（MC 4 位噪声），未反向调参 |
| R2-001 文本冲突 | **成立**：R2 §2 表 vs §4 存在 cluster-level 与 family-level 混写 |
| 提交链 1908026→fa53d19→fa3bc2c | **成立**：git 历史核实（此前汇报误写 1f87779） |

## 3. 发现并附带修复的实现问题（R1 未列）

`family_level_tests` 对 F>15 仍做 2^F 精确符号翻转枚举（F=40 时 2^40，实际挂死）——已改为 F≤15 精确枚举、F>15 走 10,000 次 MC 符号翻转，method 字段如实记录。该问题影响 §2 辅助分析可执行性，修复后 40-family 分析可运行。

## 4. 统计验证（真实计算）

- **df**：`family_t_df(40)=39`、`(34)=33`、动态跟踪 ✓；真实 diagnostic3 层级（6 families）→ df=5，符号翻转 method="exact enumeration (2^6)" ✓。
- **family 等权**：families 均值等权合成验证（3-family 混合 cluster 数用例 + 2-family 不同 cluster 数用例）✓。
- **缺失规则**：行为失败计 0 保留分母 ✓；技术缺失不换 seed ✓；null 标签行 fail-closed ✓；family 门槛 1/0 处理 ✓。
- **Holm**：单元素 0.03→0.03；双 0.01→0.02/0.02；上界截断 ≤1 ✓。
- **功效**（10,000 MC, seed 20261113）：ICC=0.20 最坏 t=**0.840** [0.8328, 0.8472]（历史 0.8391，一致）；null Type-I 0.054（D-064-B 产物，代码路径未变）。

## 5. 测试与 CI

- 新增 `test_64r3_protocol.py` 15/15；全套件见 CI（pilot_a_recovery 28 + pilot_a3b 161）。
- CI/HEAD/结论按本轮推送后真实 run 记录（见维护文档）。
- 文档修改不单独构成代码验证；统计代码修改已纳入 CI 路径（pilot_a3b/**）。

## 6. 状态（Executor 视角，非审计结论）

| 项 | 状态 |
|---|---|
| R2-001/002/003/004/006 | 已修复、已验证 |
| R2-005 | 文档与代码字段已修复；**MDE 尚待导师批准** |
| 64-R3 | **尚待独立复审**（本报告非审计） |
| 正式 A-3b | **HOLD**（审计 ACCEPTED + 导师 MDE + 用户批准 + pre-flight 前不得运行） |
| Test 隔离 | 未查看/未调参/未接触 test 结果 |

**提交独立审计材料**：`64_A3B_PREREGISTRATION_CANDIDATE_R3.md`、本报告、`test_64r3_protocol.py`、`power_hierarchical.py`（family_t_df/missing_data_rules/符号翻转修复）、`power_final_design_check.json`、manifest 重建证据（fb832bcc）。
