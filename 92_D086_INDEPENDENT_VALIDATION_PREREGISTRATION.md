# 92 — D-086 冻结候选独立 Validation 复制协议（NOT RUN）

**日期：** 2026-11-11
**状态：** PREREGISTERED REPLICATION / NOT RUN / 不是 Test，不是确认性结论
**输入结果：** `91_D086_EXPLORATORY_RESULT.md`、`results/d086_evolution/`

## 1. 唯一目的

检验普通 NSGA-III 在 D-086 原 Validation 上产生的探索性优势，能否在全新的依赖图和故障结构下复现。不得重新训练、重选 genome、增加预算或返回原 Validation 调参。

本协议只评价已冻结的普通 NSGA-III 候选；不启动新的演化搜索，不读取或生成 Test。

## 2. 新独立 Validation family

使用新的 `d086r|validation|` namespace 和 seed base `2026112200`，与 D-086 manifest、D-085 和 D-079 完全分离。四个新 family、四种 strata、每类 5 repeats，共 **80 个 Validation scenarios**。

| Family | 新机制结构 | 目的 |
|---|---|---|
| `rv01_PARALLEL_ALT` | 三步提交前缀；A 依赖 C、B 依赖 A；alternate 可绕过不同节点 | 检验跨节点依赖与备选路径迁移 |
| `rv02_CROSS_DELAY` | A→B→C 主路径依赖；alternate 无依赖但回执延迟 | 检验长链与确认预算 |
| `rv03_MULTI_ROUTE` | A/B 主路径依赖 C；C 主路径依赖 A；多条低成本旁路 | 检验局部贪婪与全局恢复顺序 |
| `rv04_REVERSE_RECOVERY` | C→B→A 主路径；替代路径成本和可靠性不同 | 检验反向依赖和异构可靠性 |

五类 repeats 预先固定为：立即可靠、一次失败、两次失败、延迟成功、延迟失败。真实尝试表仅 evaluator 可见，策略只见公开合同、提示、依赖和回执。R1/R2 保留 timeout-before 与 partial-then-redo 控制；R3/R4 按依赖与永久不可补偿闭包标注。

这些是 Validation，不是最终 Test。不得根据生成结果增删 family、调整可靠性、修改成本或选择 repeats。任何 UNKNOWN、robust/analytic 不一致或不可达 R3 都使对应 manifest fail-closed，而不是修改标签迎合结果。

## 3. 冻结候选与基线

- 直接使用原实验 `NSGA-III` 在 seeds `{711,822,933,1044,1155}` 上选出的五个 genome；指纹来自 `d086_experiment_runs.json`，不得编辑。
- 对照为固定 `Hand/FixedPrefix/FixedPrefixForward/RuleBased/Greedy/AdaptiveProbe/CostAware/Random`，与原固定门实现相同。
- 不重新运行 NSGA-II/III、C-NSGA-III、Random Search 或消融，不引入新 anchor、额外训练、Test 或真实 LLM。

## 4. 预算与执行

- 五个冻结 genome 每个最多 `4 families × 4 strata × 5 repeats = 80` 个 Validation episode，合计最多 400 个候选评价；固定基线另行逐条记录。
- 每 episode 最多 24 次决策，所有补偿、VERIFY、WAIT 和重复调用都保留真实成本。
- 每个冻结 genome 在每个新场景上评价一次；没有 cache 不得新增唯一 episode-equivalent。重复评价必须标为 audit-only，不能冒充新搜索预算。
- 不发生新的 Train、fitness 更新、种群更新、early stopping 或 Test 访问。

## 5. 指标与判断

按 scenario 内等权、family 内 strata 等权、family 等权计算：

1. R3 CorrectEscalation；
2. R4 containment；
3. R1/R2 CondRecSucc；
4. PrefixCompensationSuccess、ResidualSideEffect、AvoidableHarm；
5. RecoveryCost 与实际 ActionCost；
6. duplicate/pending/ConstraintViolation。

硬约束仍为任意 duplicate 或未决回执即不可接受。STOP_SAFE 不计实际 ESCALATE。

冻结的普通 NSGA-III 只有在至少 **4/5 个冻结 genome** 同时满足下列条件时，才可称为“具有独立复制信号的候选”：

1. 新 Validation 上 R3、R4、CondRecSucc 均为 1，duplicate/pending/ConstraintViolation=0；
2. family-equal R3 平均 RecoveryCost 低于 Greedy；
3. 不出现只在一个新 family 上改善、其他 family 明显安全或成功率退化的情况。

即使满足，也只说明独立复制信号，不是最终统计确认或创新成立。少于 4/5、任何硬约束违规或成本未低于 Greedy，均记录 NO-GO，不得重新调整。

## 6. 原始记录与停止规则

保存新 manifest lock、每个 genome 的指纹、每个场景的原始轨迹、回执、成本、约束、seed 和独立复算。必须能从原始行重算 family 等权指标和每个冻结 genome 的结果。

禁止：修改 genome、查看结果后挑选最佳 seed、追加 repeats、调阈值、把新 Validation 当 Test、删除失败场景或重复运行直到成功。

后续如需真正确认性实验，必须另行申请冻结 Test roster、功效/MDE、独立审查和用户批准。正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。
