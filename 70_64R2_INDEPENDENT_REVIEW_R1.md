# 70 — 64-R2 独立审计 R1

**日期：** 2026-11-10  
**审查对象：** 64_A3B_PREREGISTRATION_CANDIDATE.md（R2）  
**审查基线：** fa3bc2c5699c0fad8df384bebd44e5510d1d8927  
**结论：** **REQUEST CHANGES**  
**正式 A-3b：** HOLD（本轮未运行、未查看或调参 Test）

---

## 1. 审查范围与已核验事实

审查了 64-R2 全文、69 号 D-064-C 报告、power_final_design_check.json、power_hierarchical.py、正式场景生成器、维护文档及 GitHub Actions 日志。

- 工作分支 HEAD：fa3bc2c5699c0fad8df384bebd44e5510d1d8927
- main HEAD：683b3fe7fc52c86e917d523fdc6bbb13abbfd653
- 相对 main：ahead 170 / behind 0
- CI：run 42661732606，head 与上述工作分支一致，结论 success
- CI 测试：pilot_a_recovery 28/28 + pilot_a3b 146/146 = 174/174
- 最终 CI manifest SHA-256：fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a
- test-family SHA-256：01b41df8b06c318f90a4fc7aed45f673d13b50f14c08f56304ddffbb625a1411
- test-scenario SHA-256：dded3bb72a08143177dd6b7f5c4c4ef5100b547028c9cc40fa2b87b6bd70c919
- 实际提交链：1908026b → fa53d19876dec51681dc4ba5a9e1e760965ef328 → fa3bc2c5699c0fad8df384bebd44e5510d1d8927

功效 JSON 的最坏情形结果为 ICC=0.20、MDE=0.10、34 families × 5 compositions，Student-t power=0.8391，95% MC 区间 [0.8319, 0.8463]，MCSE=0.0037；null Type-I=0.0541。以上只确认该模拟产物的记录，不等同于真实算法增益证据，也不代表 MDE 已获导师认可。

## 2. 阻断性发现

### R2-001 — P0：主检验定义在同一预注册内互相矛盾

64 §2 的比较表将 AB vs NSGA-II 写成“cluster 级配对 bootstrap + 符号翻转”；但文件头 R2 摘要和 §4 又写明 family-level Student-t 为主检验、bootstrap 仅描述性。

这与 D-064-B 对 family-level Student-t 的 Type-I 校准结论不一致，也会让正式分析人员无法判断哪个协议具有约束力。

**必须修订：**
1. 唯一主要比较明确为 family-equal-weight CondRecSucc 差值上的双侧 family-level Student-t，α=0.05。
2. family-level sign-flip 仅作为敏感性分析。
3. bootstrap CI 仅作描述性区间，不作为显著性检验。
4. 次要比较逐项写明统计量、分析单位及 Holm 校正的四项检验 family；不得继续用“同上”指向旧 cluster-level 方法。
5. AB vs Hand 明确为描述性参考，不纳入确认性主张。

### R2-002 — P0：df=39 与损耗后的功效设计不一致

64 §4 把主检验写成固定 df=39。可是最终功效设计按双损耗得到 34 个有效 families。

代码 power_hierarchical.py 的 _pvals_student_t 使用 F - 1 自由度；最终设计模拟的 F=34，因此相应 df=33，而不是 39。

**必须修订：** 正式分析自由度定义为 df = F_observed - 1。完整保留 40 个 families 时 df=39；按规划损耗保留 34 个 families 时 df=33。不得把 df=39 写成无条件固定值。还应写明若实际有效 families 少于功效设计假设，结果如何报告、是否触发设计偏离门禁。

## 3. 重要一致性问题

### R2-003 — P1：预注册与维护文档引用旧 manifest hash

64 §4、69 报告、README、05_DECISION_LOG 和 NEXT_SESSION_PROMPT 曾记录旧 manifest af83f065...。但最终 CI run 42661732606 在最终 HEAD 上实际输出：

fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a

test-family 与 test-scenario hashes 仍分别为 01b41df8... 与 dded3bb7...。

**必须修订：** 64-R2 及所有当前状态文件使用最终 CI manifest hash；旧值只能标注为 POWER_DESIGN 元数据修订前的 superseded hash，不得继续称为当前冻结值。

### R2-004 — P1：attrition 设计表述不够精确

功效代码使用确定性向下取整：
- floor(40 × 0.85) = 34 families；
- floor(7 × 0.85) = 5 eligible compositions / family。

这构成保守的整数有效样本规模；但 7 个 compositions 保留 5 个，实际比例为 5/7，不能称为精确的 15% cluster loss，也不是随机 attrition Monte Carlo。

**必须修订：** 将其表述为“family 和 cluster 各按 15% 规划损耗，向下取整得到保守保留规模 34×5”；明确正式实验的缺失规则、family-equal-weight 汇总方式、每 family 最低有效 composition 数及未达到门槛时的处理。不得在结果出来后选择性删除 family 或 cluster。

### R2-005 — P1：MDE 审批没有进入正式 GO 顺序

64 和 69 均把 MDE=0.10 标记为 PROPOSED_MDE_PENDING_ADVISOR_APPROVAL，但 GO 顺序只写“独立审计 → 用户批准 → 正式 A-3b”。

**必须修订：** 正式执行的必要条件至少包括：
1. 64-R2 独立审计 ACCEPTED；
2. 导师认可 MDE=0.10，或经导师反馈完成新 MDE 论证和功效复算；
3. 用户明确批准最终预注册；
4. §5 全部 pre-flight 通过。

不得将导师尚未认可的 MDE 写成已冻结决定。

### R2-006 — P1：次要比较推断定义不充分

H2–H5 有四项次要比较并要求 Holm，但 §2 仍通过“同上”引用 cluster-level 方法；§4 的 family-level 检验描述又没有逐项说明次要比较如何执行。

**必须修订：** 为四项次要对比逐项定义 family-level 估计量、检验和 Holm family；若 D-064-B 的 Type-I 校准不足以支持某个次要终点，应明确其为探索性分析或补充校准，不得把主终点校准自动宣称为所有次要终点均已验证。

## 4. 维护记录问题（已在本轮同步勘误）

1. 最终 CI 测试数为 174/174（28+146）；69 号报告旧记录 126+28 已更正。
2. NEXT_SESSION_PROMPT 顶部曾仍指向 D-064-B，尾部却记录 D-064-C 完成；本轮已更新顶部状态和唯一任务指针。
3. 实际 Git 提交链为 1908026b → fa53d198 → fa3bc2c；不是此前汇报中写的 1f87779 → fa3bc2c。
4. “validator 对抗性完备”属于过强表述；12 类测试只支持“已覆盖的 12 类恶意变形均被拒绝，测试范围内未发现绕过”，不证明对任意攻击完备。
5. status.json 在该分支不存在，本轮没有创建虚假的状态文件。

## 5. 必须保留的科学边界

- D-064-C 的任务语义和标签器审计结果不等于正式算法有效。
- 40-family 功效 0.839 是基于指定层级模拟假设的设计证据，不是实际 A-3b 算法增益。
- MDE=0.10 仍待导师认可。
- 任务语义限定为 abstract synthetic saga，不外推真实业务工作流。
- 历史 AB 未超过 Hand 的负结果必须保留。
- R3/R4 行为率落后不能被 R1/R2 主终点改善抵消。
- 不得查看或调参 Test，不得提前启动正式 A-3b。

## 6. 审计结论与下一步

**64-R2：REQUEST CHANGES。**

本轮不修改 64 候选文件本身，以保留被审查版本和审计可追溯性。修订者应形成预注册修订版（未批准前仍为 candidate），逐项关闭 R2-001 至 R2-006，更新所有哈希与交接文件，重新运行测试/CI，然后请求独立 R2 复审。

**GO：** 64-R2 corrective revision、统计协议澄清、功效/哈希/维护记录复核。

**HOLD：** 正式 A-3b、Test 查看或调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox、合并 main。

**唯一下一任务：** 修订 64-R2 并请求独立 R2 复审。只有审计 ACCEPTED、导师认可 MDE、用户明确批准且 §5 pre-flight 通过后，才可执行正式 A-3b。
