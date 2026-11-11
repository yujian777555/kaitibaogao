# 90 — D-086 恢复策略演化实验预注册

**日期：** 2026-11-11
**状态：** FROZEN FOR TRAIN-ONLY EXPLORATORY SEARCH / 不是确认性实验或许可
**数据锁：** `experiments/pilot_a3b/dependency_manifest_lock.json`
**manifest SHA：** `362e7a8a0acafbb40f6ddccf207bede85a656193c6544bf3cd949c1fe43ffd67`
**前置证据：** `89_D086_NONCEILING_RECOVERY_MODEL.md`、`results/d086_fixed_gate/`

## 1. 假设与否证条件

检验：在相同任务、初始基础种群、信息权限和唯一评价预算下，带公开前缀状态、反馈优先级和可行性优先选择的演化控制器，能否超过固定 Prefix、Greedy、成本感知规则、普通 NSGA-II/III 和同预算随机搜索。

以下情况不得声称提升：仅超过 Hand；只降低 Train 成本；Validation 上 R3/R4 或 CondRecSucc 退化；出现重复补偿或未决回执；依赖更多评价；最终选择等价于固定策略。

## 2. 冻结数据与访问顺序

- Train 72：仅用于适应度，family=`df01…df06`。
- Validation 24：仅用于冻结规则选择，family=`df07,df08`；不得进入适应度、种群更新或早停。
- Test：不生成、不读取、不调用。保留的 namespace/seed 规则不是实际 Test payload。
- D-079 和 D-085 Diagnostic 不参与本轮调参或选择。
- Validation 固定策略已在门实验中评价一次；后续 EA 只评价一次冻结候选，不据其结果修改环境、阈值、权重或种子。

## 3. 染色体与策略语义

每个 genome 为以下冻结字段：

| 字段 | 范围 | 含义 |
|---|---|---|
| `hint_weight` | [-3, 3] | 高可靠性提示的优先级 |
| `cost_weight` | [-3, 0] | 路径成本权重，负值偏好低成本 |
| `failure_weight` | [-3, 0] | 已观察失败次数权重，负值降低优先级 |
| `position_weight` | [-1, 1] | 前缀位置顺序权重 |
| `dependency_weight` | [0, 2] | 未满足依赖的优先级惩罚 |
| `max_attempts` | {1,2,3,4} | 每路径最大尝试后 abstain |
| `verify_delay` | {0,1,2} | 两次回执查询之间的 WAIT 数 |
| `retry_unknown` | bool | 是否允许未决状态再次补偿；重复副作用计入硬约束 |
| `stop_pending` | bool | 是否允许带未决回执终止；未决回执计入硬约束 |
| `stop_residual` | {0,1,2} | 提前终止残余阈值；R3 正确升级必须为 0 |
| `allow_alternate` | bool | 是否允许 alternate 路径 |
| `allow_verify` | bool | 是否允许 VERIFY；仅 NoPendingVerification 消融关闭 |
| `stop_action` | {ESCALATE, STOP_SAFE} | 终止类型，STOP_SAFE 不计 CorrectEscalation |

可用路径评分由公开提示、成本、已观察失败、位置及依赖构成。隐藏结果、实际延迟、label、scenario ID 和最小伤害不得进入评分。`max_attempts` 用尽必须放弃该路径，不能强制生成 linkage 式的无依据恢复结论。

## 4. 搜索臂与消融

1. **Random Search：** 同表示、同初始池、同候选数，只按冻结 Validation 规则选择，不使用 NSGA 生存者机制。
2. **NSGA-II：** 非支配排序、拥挤度、二元锦标赛、均匀交叉。
3. **NSGA-III：** 五目标参考方向 `p=3`（35 个方向）、归一化、关联和 niching。
4. **C-NSGA-III / Full：** 在 NSGA-III 上进行可行性优先的约束筛选和生存者选择。
5. **NoDependencyPriority：** `dependency_weight=0`，环境仍阻断非法依赖。
6. **NoFailureFeedback：** `failure_weight=0`，不利用失败次数调整优先级。
7. **NoAlternate：** 仅 primary 路径，检验备选路径贡献。
8. **NoPendingVerification：** 禁止 VERIFY；未决状态不能正常解决，用于检验回执机制必要性。

固定基线保留 `Hand/FixedPrefix/FixedPrefixForward/RuleBased/Greedy/AdaptiveProbe/CostAware/Random` 的 768 行原始结果，不重跑旧 SBCG，不引入其分层反例池或额外 Hand-anchor 机制。

## 5. 配对初始池、变异与随机流

- 所有搜索臂/seed 使用同一 12 个基础 genome 初始池，包含 hint、cost、feedback 和简单拓扑先验；不得只给 Full 更优个体。
- Prefix/反馈参数来自单独记录的随机流；基础基因组逐项一致。
- 每个子代先均匀交叉，再对**恰好一个**字段进行一次类型保持 mutation；连续字段扰动后裁剪到冻结范围，离散字段重采样。
- optimizer seeds = `{711,822,933,1044,1155}`；不得追加 seed 获得正面结果。
- 种群=12，offspring generations=6，无 early stopping。

## 6. 唯一评价预算

每个搜索臂每 seed：

- 唯一候选数：`12 + 6×12 = 84`，包含初始种群；
- 每候选 Train episodes=72；
- 唯一 episode-equivalent 上限=`84×72 = 6,048`；
- 每 episode 最多 24 次决策；
- Validation 单独记录，不进入 Train 适应度，不作为免费搜索样本。

唯一键：`(protocol_version, manifest_sha, evaluator_version, genome_fingerprint, scenario_id, scenario_seed)`。初始种群、重复指纹、缓存命中、跨臂共享均分别记录；缓存命中不得增加唯一预算。实际工具成本另用 `action_cost/tool_action_count`，不能替代 episode-equivalent。

## 7. 目标、硬约束与选择

### 优化目标（均为 family 等权、最小化）

1. `1 - R3 CorrectEscalation`；
2. `AvoidableHarm`；
3. `RecoveryCost`；
4. `1 - R4 containment`；
5. `1 - CondRecSucc`（R1+R2）。

### 硬约束

任一评价场景中 `duplicate_compensation>0` 或 `pending_compensation>0` 都使候选不可行。不能用成功率、成本或其他目标抵消。`stop_pending=True` 并不豁免约束，`retry_unknown=True` 产生的重复副作用照常计数。

### 选择

- Full：可行性优先，再进行非支配/参考方向生存者选择；若没有可行个体，只能按最小约束违规维持审计，不得伪装成可行精英。
- Validation：零硬约束 → Pareto 非支配 → R3 CorrectEscalation 高 → R4 containment 高 → AvoidableHarm 低 → CondRecSucc 高 → RecoveryCost 低 → 完整指纹字典序。无可用候选返回 HOLD。
- 不使用 `min(sum(objectives))` 作为未经预注册的等权标量化。

## 8. 探索性成功判据

仅当 Full 在全部五个 Validation seeds 上同时满足以下条件，才可称为**进一步研究的候选改进**：

1. 所有 Validation 场景的 R3 CorrectEscalation、R4 containment、CondRecSucc 均为 1，且硬约束为 0；
2. R3 平均 RecoveryCost 低于 Greedy 在该 split 的 15.1667；
3. 相对 Random Search、NSGA-II、NSGA-III 不产生上述指标退化；
4. 消融能解释反馈、依赖优先级、备选路径和回执验证的作用；不可识别的机制不宣称贡献。

这只是探索性扩展条件，不是统计确认或最终创新成立。若没有满足，记录 NO-GO 或有限条件结果，不调整阈值。

## 9. 统计与原始记录

- 每个 arm×seed×scenario 保留原始轨迹、补偿结果、pending、成本、约束、genome、配置和缓存账本。
- 主要统计单位为 optimizer seed；先 scenario 内等权，再 family 内 strata 等权，再 family 等权。
- 五个 seeds 只做探索性均值、逐 seed 配对差值和离散程度，不作确认性 t 检验；两个 Validation families 不支持稳健的家族级显著性结论。
- 任何后续扩展需要新的独立 Validation、功效/MDE 论证和新的预注册，不能反复使用本 Validation。

## 10. 停止规则

出现固定策略共同支配、Full 不优于 Greedy 或同预算随机/NSGA、硬约束非零、数据泄漏、初始池或预算不配对、标签错误、未决回执被忽略、反复调 Validation、删除失败 seed、或修改终点来迎合结果时，立即停止当前功效主张并保留全部失败结果。

正式 A-3b、Test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。
