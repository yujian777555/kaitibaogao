# 60 — WAIT-SLA 契约、反例驱动变异 R2 与行为安全门设计

**日期：** 2026-11-07（D-062 Stage 1–3）  
**状态：** IMPLEMENTED + UNIT-TESTED（51/51）；诊断实验结果见 61 号  
**动机：** 59 号复核确认——真实行为损害的唯一来源是 `UNKNOWN_OUTCOME → 信任 SLA 内查询 → 非幂等 RETRY`；D-061 的 B 反例粒度太粗导致组合有害。

---

## 1. WAIT-SLA 状态化合同（Stage 1）

### 1.1 工具操作状态（环境真值，策略不可读）

`NOT_SUBMITTED / SUBMITTED / COMMITTED_BUT_NOT_VISIBLE / COMMITTED / NOT_COMMITTED / UNKNOWN_OUTCOME / COMPENSATED / FAILED`。

### 1.2 SLA 合同字段（公开）

每工具操作：提交语义、**可见性延迟上界** `visibility_bound`（A-3 合同已有）、查询一致性（SLA 内不一致）、幂等性 `idempotent`、重试安全条件、补偿能力 `compensatable`、最大等待预算（决策预算 24）、升级条件。**可见性 SLA 与重试 SLA 分离**：可见性 SLA 决定查询何时可信；重试安全 = 查询可信后确认未提交，或补偿已清除歧义。

### 1.3 决策机制（已实现于 `StatefulFSM.decide` + 运行器）

| 公开观察 | 动作 |
|---|---|
| START/明确未提交 | 按合同提交/重试 |
| TIMEOUT（UNKNOWN_OUTCOME，非幂等） | 进入歧义态：WAIT 至 SLA → VERIFY |
| WAIT 后未到 SLA | 继续 WAIT |
| SLA 后 VERIFY=COMMITTED | 禁止重复提交，推进 saga |
| SLA 后 VERIFY=NOT_COMMITTED | **解锁 RETRY**（cleared_to_retry） |
| SLA 内 VERIFY=NOT_COMMITTED | **不解锁**（查询不可信） |
| 补偿成功 | 解锁（歧义已清除） |
| 超 SLA 仍未知/补偿失败 | ESCALATE / STOP_SAFE |
| 无法证明重试安全 | 禁止 RETRY（动作掩码） |

不变量：WAIT 不无限循环（决策预算）；不读隐藏状态；不凭超时断言失败；无法证明安全不重试。

**实现要点：** 控制器状态增 `ambiguous / sla_waits / visibility_bound / compensated_since_ambiguity / cleared_to_retry`（全部来自公开信息：自身动作、公开观测、合同字段）。`sla_aware=True` 时 RETRY 在不安全条件下被**动作掩码**替换为 WAIT（SLA 内）或 VERIFY（SLA 到期后）。掩码不改变基因组——演化在合法动作集中选择（Q10 分离的关键）。

## 2. 反例驱动变异 R2（Stage 2，B-new）

| D-061 缺陷 | R2 修复 |
|---|---|
| 粗标签权重 | **动作序列签名**：`_signature = (cause, 最近 4 个 (obs, action) 对)` |
| 池只留最后个体 | 每代聚合全种群失败 |
| 权重未进评价 | 定向变异为唯一机制；预算对齐（替换而非叠加） |
| 乱打基因 | **只打轨迹中咨询过的基因**（decision_trace → implicated genes） |
| 破坏 A 的修复 | 变异提案来自**死因→修复动作映射**（dup_retry→WAIT/VERIFY/COMPENSATE；sla_retry→WAIT/VERIFY；residual→COMPENSATE/ROLLBACK；comp_fail_loop→ESCALATE/ROLLBACK…），随后过契约修复 + 独立 validator |

流程（Counterexample-Guided Contract-Preserving Mutation）：收集失败轨迹 → 按签名聚类 → 定位涉事基因 → 死因特定修复动作变异（1 次/子代）→ 契约修复 → 独立 validator → 评价 → 环境选择保留真正改善者。不同合同/故障组合下演化出不同策略（掩码只约束非法面）。

## 3. 行为安全门（Stage 3，方案一+二+三）

- **方案一（变异后验证）**：B-new 每次变异后过 `repair_fsm` + `contract_validator`；
- **方案二（行为层安全门）**：`safety_battery_pass`——6 个固定关键歧义场景（timeout_after/delayed_visibility/partial），出现 duplicate 或 sla_violation 即拒绝候选（硬过滤，不可被成功率抵消）；
- **方案三（分层生存者）**：门禁先于多目标排序（ABG 臂）。
- 消融：A / A+B-new / A+B-new+Gate 三臂对照（Gate 有效性见 61 号 Q7）。

## 4. 消融设计（5.4/6.4/7 对照）

| 臂 | 语义 |
|---|---|
| Hand | 强手工（WAIT×4→VERIFY 序列） |
| NSGA-II | 标准多目标 |
| A | 契约修复（D-061 机制） |
| A+Fixed-WAIT | A + TIMEOUT 后固定 WAIT×4（无合同推理） |
| A+WAIT-SLA | A + 合同驱动动作掩码（本设计） |
| B-new | 反例驱动 R2（无修复） |
| A+B-new | 组合 |
| A+B-new+Gate | 组合 + 行为安全门 |

公平性：同初始池（60 个共享骨架随机 FSM）、同 train 场景、同预算（含 battery rollout 计费）、同终止、定向变异替换普通变异。
