# 69 — D-064-C：任务语义独立审计、正式场景生成器验证与统计设计冻结

**日期：** 2026-11-09（D-064-C）  
**审计对象：** `task_semantics.py`、`formal_scenario_generator.py`、标签器链、8/4/40 划分、确定性与哈希、40-family 功效  
**新增测试：** `test_d064c_audit.py` 25/25（对抗性 ×12、组合真实性 ×5、标签边界 ×3、确定性 ×4、其余一致性）  
**产物：** `power_final_design_check.json`（最终设计功效复算）  
**64 号预注册：** 已修订为 R2（40-family 最终设计），待独立审计与用户批准

---

## 1. 任务语义审计（D-064-C-1）

**审计文件**：`task_semantics.py`（378 行：三步 saga 契约、EffectReceipt 链、逆序补偿、primary-compatible 筛选、8/4/40 划分目录）。

**发现的问题与处置**：
1. 验证器覆盖完整（契约/回执/前置后置/goal/补偿顺序/family_id/legacy 防伪/primary 门槛）；**未发现可绕过缺陷**。
2. **对抗性测试 12 项全通过**：删除必要前置、篡改后置、替换工具、篡改工具合同、伪造 EffectReceipt、篡改前序回执、破坏补偿顺序、修改 task goal、注入重复工具、篡改 primary-compatible 资格（非补偿首步族必须被拒）、伪造 legacy 标志、篡改 payload 类型——恶意变形全部被 `validate_task_family` 拒绝。
3. 已知边界（非缺陷，记录）：验证器允许 spec 附加扩展字段（宽容模式）；`semantic_scope` 明确标注 abstract_synthetic_saga，不外推真实业务语义。

**结论：通过**（对抗性测试全绿）。

## 2. 故障组合审计（D-064-C-2）——9 逐一核对

| 故障组合 | 声明（NOTES） | 实际注入 | 发生步骤 | 补偿条件 | 标签（全量） | 问题/处置 |
|---|---|---|---|---|---|---|
| single_timeout | 单超时（3 选 1） | timeout_before/after/delayed_visibility | 随机步 | 合同默认 | R1 ×156 | 一致 |
| timeout_then_rate_limit | step0 timeout_after + step1 rate_limit | 同 | 0,1 | 合同默认 | R1 ×156 | 一致 |
| partial_then_delay | 首个可补偿步 partial + 他步 delayed | 同 | first_comp,+1 | 保证补偿 | R2 ×156 | 一致 |
| schema_then_timeout | step0 schema_drift + step1 timeout_before | 同 | 0,1 | — | R1 ×156 | 一致 |
| independent_mixed_val | 逐步独立可恢复故障 | 6 选 1/步 | 全部 | 按合同 | R1 153 / R2 3 | 一致（允许集 {R1,R2}） |
| partial_then_timeout_val | 首可补偿步 partial + 他步 timeout_after | 同 | first_comp,+1 | 保证补偿 | R2 ×156 | 一致 |
| partial_comp_failure | 首可补偿步 partial（补偿结果隐藏）+ timeout_after | 同（comp=False） | first_comp,+1 | **补偿必败** | R4 ×156 | 一致 |
| permission_after_compensatable_prefix | **原注释写三故障（delayed→rate→permission），实际只注入 step1 permission_denied** | permission_denied | 1 | 前缀（step0）可补偿 | R3 ×156 | **发现不一致（注释陈旧）→已修复注释**（见下） |
| triple_mixed | step0 timeout_after + step1 rate_limit + step2 schema_drift | 同 | 0,1,2 | 合同默认 | R1 ×156 | 一致 |

**permission_after_compensatable_prefix 专项裁定（用户五问）**：
1. 性质：**历史命名兼容 + 注释陈旧**，非注入缺陷——实现与名称一致（"补偿前缀后的权限拒绝"），旧 `delay_rate_permission` 三故障系 A-3 历史组合，D-064-C 执行期已简化（commit 49bb9ca/1908026）以隔离 R3 机制；
2. 实际场景**不覆盖**注释所述三故障；三故障语义已由 `delayed_visibility/rate_limit` 族覆盖；
3. 处置：**修改声明（注释）**，不修改注入——注入与 R3 机制、名称、ALLOWED 集一致；
4. R1–R4 标签**不变**（两种注入下该组合均为 R3：step0 干净提交 + step1 权限拒绝 + 前缀可回滚）；
5. 7/9 primary eligibility **不变**（该组合为 R3、partial_comp_failure 为 R4，其余 7 个 R1/R2）。
- 前提验证：**52/52 families 的 step0 均为可补偿工具**（primary-compatible 强制），R3 前提结构性成立；`scenario_verdict` 对前缀不可补偿情形会正确给 R4（对抗测试覆盖）。

## 3. 标签器审计（D-064-C-3）

- **独立性**：标签来自 `classify_scenario`（观测策略 AND-OR 鲁棒可达判定器，horizon 24 / max_nodes 500k），analytic `scenario_verdict` 交叉校验；**不接收任何算法输出**；`label_evidence_sha256` 逐 cluster 保存；ALLOWED_CLASSES 仅为合理性约束，非标签源。
- 无 task_id/scenario_id 作弊路径（测试断言标签非 id 路径段）。
- **边界与反例**：horizon 截断 → UNKNOWN（不降级）✓；非补偿 partial → R4 ✓；UNKNOWN 率全 splits 0%（远低于 5% 门禁）——**0% 不解释为标签器完美**，判定器语义已有 12 个 mini-env ground-truth 锚定（test_recoverability）+ 判定器内 know-answer 测试。
- 每 cluster 留存 `label_evidence` 与 robust/analytic 一致性标志；不一致须有论证（`_explain_analytic_disagreement`），无解释不一致触发 problems。

**结论：通过**。

## 4. 任务族划分（D-064-C-4）

- **候选池**：312 个 primary-compatible 三步序列（tool 唯一、含非幂等+含可补偿+含不可补偿、首步可补偿——正是 R3/R4 挑战结构）。
- **8/4/40 划分**：train 8 / validation 4 / **test 40** families；family ID 与工具序列零跨 split 重叠；生成确定性（stable_seed）。
- **profile 多样性**：test 覆盖 **10 种工具 profile × 4 families**；工具使用分布经 `greedy_diverse`（工具重叠最小化）。诚实登记：多样性目标=**工具重叠 + profile 覆盖**；工具顺序/任务语义多样性受"抽象合成 saga"范围限制（`semantic_scope` 已声明），不外推真实业务语义多样性。
- **泄漏检查**：split 内/间 family 与序列不重叠；标签由策略无关判定器生成；test payload 不入 candidate manifest。

**结论：通过**（语义多样性主张限定于抽象 saga 范围）。

## 5. 确定性与哈希（D-064-C-5）

- manifest SHA-256 **fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a**（最终 CI run 42661732606 输出；POWER_DESIGN 元数据修订前的旧候选 manifest 已废止）；
- test-family SHA **01b41df8…**、test-scenario SHA **dded3bb7…**——与上次 CI 记录逐字符一致；
- 同输入确定性 ✓；不同 repeat 仅参数数值变化、故障模式 cluster 内固定 ✓；scenario_id/seed 全局唯一 ✓；
- 修改标签内容会改变 hash（tampering 测试）✓；
- **lockbox 审计**：test 数据仅进 manifest 哈希与聚合统计；无逐场景 test 标签泄漏到 train/val；日志无 test 单场景输出。Test 结果未被查看/调参。

**结论：通过**。

## 6. 功效复核（D-064-C-6）——最终设计

使用 D-064-B 同一程序（`power_hierarchical.mc_power_at`）+ 真实 CondRecSucc cluster 差值分布（diagnostic3，SHA b9498195…）：

| ICC | power（Student-t） | 95% MC 区间 | MCSE | 符号翻转 | bootstrap |
|---|---:|---|---:|---:|---:|
| 0.00 | 0.979 | [0.976, 0.982] | 0.0014 | 0.978 | 0.985 |
| 0.05 | 0.953 | [0.949, 0.957] | 0.0021 | 0.952 | 0.964 |
| 0.10 | 0.922 | [0.917, 0.928] | 0.0027 | 0.920 | 0.938 |
| **0.20** | **0.839** | **[0.832, 0.846]** | 0.0037 | 0.837 | 0.865 |

设计：40 design families × 7 eligible comps，双 15% 损耗 → **34 有效 families × 5 有效 comps = 170 有效 clusters**；MDE=0.10；10,000 MC；seed 20261113；null Type-I（34×5, ICC 0.20）= 0.054 ✓ 校准。

- **generator 硬编码 `expected_power_from_D064B_MC=0.85` 不采信**：复算最坏情形 **0.839**（区间不含 0.85）；已更新为 0.839 + 区间 + provenance，0.85 作废。
- **40-family 设计达标**：ICC=0.20 上限仍 ≥0.80（余量 0.039）✓。repeats 未冒充 families ✓。

## 7. MDE 科学论证

0.10 = CondRecSucc 绝对 +10 个百分点。论证要点：(a) 对恢复控制器而言 10pp 代表每 10 个可恢复场景多救回 1 个，对应实际事务损失的量级变化；(b) 演化搜索的复杂度/rollout 成本需要这样的最低回报才值得；(c) **非**反推自 +0.3175 或 0.1173；(d) **非**为迁就 40 families（40 是在 MDE=0.10 与 ICC=0.20 下的功效解，不是反向）。  
**状态：`PROPOSED_MDE_PENDING_ADVISOR_APPROVAL`——尚无导师书面确认，不得伪造同意。**

## 8. 预注册（D-064-C-7）

`64_A3B_PREREGISTRATION_CANDIDATE.md` 已修订为 **R2**：40-family test（1,080 场景 / 280 eligible clusters，哈希冻结）、主检验 family 级 Student-t、符号翻转仅敏感性、bootstrap 仅描述性、MDE 待批准标注、UNKNOWN≤5% 门禁、双 15% 损耗规则、锁箱与停止规则、解释边界不变。**仍为 CANDIDATE**：需独立审计 + 用户批准；代码通过 ≠ 科学方案通过。

## 9. 测试与 CI

- 新增 `test_d064c_audit.py` **25/25**（对抗 12 + 组合 5 + 标签 3 + 确定性 4 + 一致性 1）；
- 全套件以最终 CI 为准：run 42661732606 @ fa3bc2c，pilot_a_recovery 28/28 + pilot_a3b 146/146 = 174/174；
- CI：https://github.com/yujian777555/kaitibaogao/actions/runs/42661732606，head fa3bc2c5699c0fad8df384bebd44e5510d1d8927，结论 success；
- CI 在干净 runner checkout 上完成复算；确定性测试独立二次构建的 manifest 哈希一致（不将其表述为单独的第二个 clone 实验）。

## 10. 科学结论

**获支持**：任务语义契约与 validator 在已覆盖的 12 类对抗变形测试中全部拒绝；不据此宣称对任意攻击完备；9 组合声明-注入-标签一致（1 处注释修复）；标签独立且有证据链；8/4/40 划分与哈希确定性成立；**40-family 设计在 ICC=0.20 上满足 0.80 功效（0.839）**。  
**仍无证据**：正式 A-3b 的算法增益（未运行）；MDE=0.10 的导师认可；真实业务语义泛化（明确限定抽象 saga）；AB 超过 Hand（D-062 已示未超过）。

## 11. GO / HOLD

**GO**：64-R2 独立审计 → 用户批准 → 正式 A-3b。  
**HOLD 不变**：正式 A-3b 运行、test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox、擅自合并 main。


## 12. 最终 CI 记录勘误（2026-11-10）

最终 CI 42661732606 在 HEAD fa3bc2c5699c0fad8df384bebd44e5510d1d8927 的实际输出为 manifest SHA-256 fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a；test-family 01b41df8b06c318f90a4fc7aed45f673d13b50f14c08f56304ddffbb625a1411 与 test-scenario dded3bb72a08143177dd6b7f5c4c4ef5100b547028c9cc40fa2b87b6bd70c919 不变。旧 manifest af83f065cf8ac47871a1e00380febe55fc2804d06279069a05d844f7c6b20195 是最终 POWER_DESIGN 元数据修订前的值，不再作为当前冻结值。

同一 CI job 的测试计数为 pilot_a_recovery 28/28 + pilot_a3b 146/146 = 174/174。Git 实际提交链为 1908026b → fa53d19876dec51681dc4ba5a9e1e760965ef328 → fa3bc2c5699c0fad8df384bebd44e5510d1d8927；中间提交为 D-064-C 审计/修订，最终提交为维护文档同步。
