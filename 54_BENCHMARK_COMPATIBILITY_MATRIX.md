# 54 — 公开基准兼容性覆盖矩阵与融合判断

**日期：** 2026-11-06（Phase B）  
**证据来源：** 52_TOOLMISUSEBENCH_AUDIT.md（数据+官方 env/fault 代码+per-task 复算）、53_UNDOBENCH_AUDIT.md（数据+METRICS.md+harness smoke）、PILOT_A3_INDEPENDENT_REAUDIT.md（A-3 实测）。  
**标注：** YES=有字段/官方执行器/论文证据支持；PARTIAL=可部分表达；NO=确实不支持；UNKNOWN=未证实。

## 1. 机制覆盖矩阵

| 机制 | Pilot A-3（自有模拟器） | ToolMisuseBench v0.2 | UndoBench v1.0.1 |
|---|---|---|---|
| Timeout（事前失败） | YES（timeout_before） | YES（before_call 拦截，`faults/timeout.py`） | PARTIAL（WORKER_CRASH 1 条属变更期崩溃；标准场景不是事前超时） |
| Timeout / 丢失 ACK（结果不明） | YES（timeout_after、delayed_visibility 共享 TIMEOUT 观测） | **NO**（timeout 在执行前拦截，无 lost-ACK；全量关键词+代码取证） | **YES**（SCN-LOST-ACK 33/36；observability=UNKNOWN_OUTCOME 全部） |
| Late commit / 延迟可见 | YES（delayed_visibility，visibility_bound SLA） | **NO**（语义不存在） | PARTIAL（POST_ACK_PRE_CHECKPOINT 1 条边界；主流是 pre-ACK） |
| Partial commit | YES（partial_commit + 补偿前置） | **NO** | PARTIAL（PARTIAL_WRITE 扰动 1 条：SCN-DURING_MUTATION） |
| Duplicate side effect | YES（非幂等重试即 DUPLICATE+violation） | **NO**（环境幂等/already_exists 守卫，结构上不可能） | **YES**（idempotency_support 全 false；DER 指标；forbidden_effects 防双写） |
| Compensation / 补偿失败 | YES（compensatable 契约、补偿失败残留、逆序 saga 回滚） | **NO**（0 次出现） | **YES**（reversibility=COMPENSATABLE 24；SCN-COMPENSATION-CRASH；DURING_COMPENSATION 边界） |
| Cross-tool saga 依赖 | YES（三步有序提交，前置未提交禁止后续） | **NO**（双故障全同工具；无步骤依赖） | PARTIAL（19/36 多工具工作流，但为效果叠加而非有序 saga 门禁） |
| Delayed visibility | YES | **NO** | NO（无此语义字段） |
| Idempotency 合同 | YES（工具契约 idempotent 字段，策略可见） | **NO**（工具 schema 无契约字段） | PARTIAL（工作流级 bool `idempotency_support`，全 false；无工具级合同） |
| Authorization failure | YES（permission_denied 不可提交） | YES（authz，瞬态一次性） | NO（无对应扰动） |
| Safe escalation / 不可恢复类 | YES（A-3 死区即不可恢复；saga_aware 升级语义） | **NO**（全部故障重试一次即恢复） | **YES**（IRREVERSIBLE 8 条 + forbidden_effects 22 条 → 必须安全停止/补偿） |
| Typed recoverability 元数据 | YES（compensation_available 运行时 + 离线标签） | YES（payload.recoverability 4 类） | YES（reversibility 3 类 + fault_boundary 4 类） |
| 预算/动作成本 | YES（action_count） | YES（budget profiles + ToolCallsUsed） | PARTIAL（由 runner 记录步骤；无预算梯度） |

## 2. 评价语义对照

| 评价维度 | A-3 | ToolMisuseBench | UndoBench |
|---|---|---|---|
| 成功判据 | 全部步骤提交 + 零违规 | success_criteria（状态/输出/调用断言） | expected_outcome + required_effects（含 max_occurrences） |
| 安全判据 | invariant_violation / duplicate / unresolved | **无**（只有 PolicyViolations/InvalidCallRate） | DER / MER / URR / EOR（effect-history oracle） |
| 条件化口径 | 按 slice 与可恢复性（A-3b 拟引入） | RecoverySuccess 条件在"遇到过故障"（993 分母） | CRSR 条件在 CONTROL 成功（C/D 分母） |
| 配对设计 | 公共随机数（同 scenario/seed/fault） | 同任务多 agent 对照 | **CONTROL/FAULT 双试验同 seed 配对** |
| 分层 | task×fault-composition 因子化 split | domain×fault×difficulty×budget 交叉 | workflow×fault 边界×reversibility |

## 3. 泄漏与划分警告（细节见 SPLIT_LEAKAGE_AUDIT.md）

- ToolMisuseBench：**指令模板跨 split 重叠 72–73 个**（train∩test 73/261 test 模板）；工具集三分割完全相同；task_id 无泄漏。→ 只能主张"新实例/新实体"泛化，不能主张新任务族。
- UndoBench：8 领域 × 3 split 全覆盖，SCN-LOST-ACK 三分割共有（test 12/12 同质）；工具名重叠低（dev∩test 3/20）；task_id 无泄漏。→ 只能主张"新工作流/新工具"泛化；test 仅测 lost-ACK。
- A-3：任务族×故障组合族因子化零泄漏（已审计），但 held-out 组合含 52% 结构性死区（A-3b 要修的问题）。

## 4. 融合判断（回答"这些基准能否支撑第一项创新"）

**判定：ToolMisuseBench 与 UndoBench 都不能单独支撑第一项创新；它们与自有模拟器构成三层分工。**

1. **主演化搜索环境 = 自有模拟器 A-3b（扩展现有 A-3 语义）+ ToolMisuseBench train 作为第二搜索域。**
   - 理由：演化搜索需要 (a) 大样本 scenario 供给（ToolMisuseBench 6,000 train 是唯一量级来源），(b) 我们的核心机制（补偿、saga、部分提交、结果不明）只有自有模拟器完整拥有（矩阵 §1）。ToolMisuseBench 上可搜索的是"故障条件下的调用序列修复策略"——作为第二域检验我们的策略表示是否只在自家模拟器有效。
   - 限制：ToolMisuseBench 无安全不变量可守（无重复副作用可犯），在它上面安全机制是空转的；必须在报告中分开陈述两域结果。
2. **外部泛化验证 = UndoBench TEST（12 条，锁箱，一次性）。**
   - 它拥有全部关键安全语义（重复效应、不可逆、补偿边界）且执行栈独立于我们（8 领域沙箱），是唯一能证明"恢复控制器跨环境迁移"的公开证据源。统计按 workflow×fault cluster，明确样本量限制。
3. **必须保留在自有模拟器的机制**：有序三步 saga 门禁、逆序补偿与补偿失败残留、延迟可见 SLA、工具级幂等/补偿契约、按任务族×故障组合族的因子化 OOD 划分。这些公开基准均不完整支持（矩阵 §1 的 NO/PARTIAL 项）。
4. **必须复现的公开基线**：
   - ToolMisuseBench：Parser+Repair（instruction_parser，已 DEV 复现 0.7622）+ recovery-disabled（0.1511）；这是该域的强基线。
   - UndoBench：官方 recovery=none / scripted agents + 我们的安全手工策略适配版；LLM 基线待 API 授权。
   - 自有模拟器：现有七策略（含 saga_aware 与 oracle_diagnostic 诊断参考）。
5. **不适合第一项创新的任务族/用途**：
   - ToolMisuseBench 的 clean 与"重试一次即恢复"的瞬态故障族——没有恢复决策空间，只能作回归；
   - UndoBench 的多 seed 重复运行——不得计为独立样本；
   - ThinkingBox-Bench——当前不可达（52/53 记录），且官方口径 evaluation-only，即使恢复访问也只能做最终 clean 回归。

## 5. 对 A-3b 的直接输入

- 可恢复性四分类（A3b-1）参照 UndoBench 的 reversibility×boundary 组合与 ToolMisuseBench 的 typed recoverability 做交叉校验，避免自造分类与既有基准脱节。
- 评价指标（A3b-2）采用 CRSR 的"条件分母"思想（条件在可恢复类上）+ DER/MER/EOR 的 exactly-once 语义，与外部基准可对齐报告。
- 失败边界分析（A3b-4）必须保留不可恢复死区为**显式类**（安全停止记为正确），而不是删除（A-3 的教训：死区淹没差异 → 但删除困难场景 = 造假）。
