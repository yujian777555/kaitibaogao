# SPLIT_LEAKAGE_AUDIT — 跨划分泄漏审计

**日期：** 2026-11-06（Phase B）  
**范围：** ToolMisuseBench v0.2 large、UndoBench v1.0.1、Pilot A-3（对照）  
**方法：** 全量逐行统计（非抽样）；模板归一化（数字/实体 ID 替换为 `#`）后比较指令集合；工具名/工具集/领域/场景族集合求交；task_id 求交。  
**边界声明：** UndoBench test 仅读取**元数据**用于本审计；未在 test 执行任何策略，未用 test 内容指导算法设计。

## 1. ToolMisuseBench v0.2（6,000 / 900 / 1,200）

| 检查 | 结果 | 判定 |
|---|---|---|
| task_id 跨 split 重叠 | train∩dev=0，train∩test=0，dev∩test=0 | **无 ID 泄漏** |
| task_id 唯一性 | 6000/900/1200 各自唯一，重复=0 | 通过 |
| 原始 instruction 唯一性 | 官方 quality report：test uniqueness_ratio 0.7275 | 见模板行 |
| **归一化指令模板重叠** | train 436 模板 / dev 239 / test 261；**train∩dev=72、train∩test=73、dev∩test=72** | **模板级泄漏（预期内的生成式模板复用）** |
| 工具名重叠 | 12 个工具全部出现在全部 split | **工具层 100% 重叠** |
| toolset_id | crud_v1/retrieval_v1/files_v1/scheduler_v1 三分割相同 | 同上 |
| 初始状态生成器 | 同形结构（accounts/docs/jobs/files），文件路径按 split 分目录（exports/snapshots/reports） | 生成器共享，实例不共享 |
| 领域×故障×难度×预算 | 三分割都是全交叉设计（balance 良好） | 分布重叠是设计使然 |
| 故障参数（timeout_ms、retry_after_ms 等） | 由 seed 决定；fault 结构相同（on_nth_call=1） | 无新故障族在 test 出现 |

**解释与影响：** 数据集由模板+槽位（实体 ID、seed）生成；split 划分在**实例层**而非**任务族层**。因此：
- 可主张的泛化：新实体/新状态实例、未见过的具体参数组合。
- 不可主张：新指令模板、新工具、新故障族。任何"跨任务族泛化"的说法必须限制在实例层。
- 对我们的影响：在 train 上演化、在 test_public 上评价时，若策略编码包含指令模式匹配，会隐性利用模板复用——**必须**在 A-3b/Pilot B 报告中披露此泄漏面，并以自有模拟器的真正 task-family×fault-composition OOD 作为泛化主证据。

## 2. UndoBench v1.0.1（14 / 10 / 12）

| 检查 | 结果 | 判定 |
|---|---|---|
| task_id 跨 split 重叠 | 36 个 ID 唯一，零重叠 | **无 ID 泄漏** |
| 领域重叠 | 8 领域在 dev/val/test **全部出现**（cloud/crm/database/git/messaging/payments/storage/ticketing） | **领域层 100% 重叠** |
| 场景族重叠 | SCN-LOST-ACK 三分割共有（dev 13+1、val 8、test 12）；稀有场景（COMPENSATION-CRASH dev、DURING_MUTATION/POST-ACK-PRE-CHECKPOINT val）不出现在 test | test 场景同质；稀有边界未在 test 验证 |
| 工具名重叠 | dev 20 个工具 ∩ test 16 个 = **3 个** | 工具层区分度好 |
| workflow_name/description | 各不相同（36 个独立业务流程） | 无文本重复 |
| fault_scenario 参数 | 全部 scenario_id 命名规范一致；target_call_index=1 为主 | 结构同质、实例不同 |

**解释与影响：**
- 划分单位是**工作流**（业务流程），泛化主张应为"新工作流/新工具组合上的恢复"，不是新领域或新故障族。
- test 全部为 lost-ACK：外部验证的能力主张要限定为"结果不明下的恢复安全"，不能外推到补偿失败/部分提交（那两域样本只在 dev/val 各 1 条，统计上不足以验证）。
- 样本量 12 的比例指标必须报 cluster-aware 区间；多 seed 重复运行是方差缩减，不是样本量。

## 3. Pilot A-3（对照，已在 44/51/PILOT_A3_INDEPENDENT_REAUDIT 中审计）

| 检查 | 结果 |
|---|---|
| task_family × fault_composition 因子化 split | 零交叉：train 任务族×train 组合、held-out 任务族/组合各自独立；45 个组合单元逐一核对通过 |
| scenario/seed/fault 配对 | 七策略公共随机数完全一致 |
| 模板/工具泄漏 | 六任务族使用重叠工具（10 个工具跨族复用）——任务族差异在**工具序列与契约组合**，不是新工具 |

A-3 的 OOD 是三基准中唯一任务族×故障组合双因子的；这是必须保留在自有模拟器的核心理由。

## 4. 汇总

| 数据集 | ID 层 | 模板/领域层 | 工具层 | 可主张的泛化 |
|---|---|---|---|---|
| ToolMisuseBench | 干净 | **泄漏**（模板 72–73 重叠） | **全重叠** | 新实例 |
| UndoBench | 干净 | **领域全重叠**（场景 test 同质） | 基本干净（3/20） | 新工作流 |
| Pilot A-3 | 干净 | **干净**（因子化） | 有意重叠 | 新任务族 × 新故障组合 |

**结论：** 三者的泛化主张必须分开陈述；A-3b 的确认性证据以自有模拟器的因子化 OOD 为主，ToolMisuseBench/UndoBench 作外部迁移辅证并披露泄漏面。
