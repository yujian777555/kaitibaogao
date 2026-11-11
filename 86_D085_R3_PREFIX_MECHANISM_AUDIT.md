# 86 — D-085 R3 根因与 Prefix-aware 机制审计

**日期：** 2026-11-11
**角色：** Executor 机制审计与独立 CSV 复算；不替代后续独立会话审查
**接管基线：** `33672562ebaeb6c3a533e7e0fd975cbac045b5e3`
**工作分支：** `pilot-a-stateful-recovery`
**main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，未修改、未合并
**最终机制结论：** 补偿顺序可达，固定 Prefix 控制器在新开发集封顶；**没有运行优化器，也没有 EC 增益证据**

## 1. R4 复审边界

`85_D064_R4_INDEPENDENT_REVIEW_R2.md` 的 R4 结论为 **ACCEPTED（仅代码与协议复审）**。R4 的统计、Student-t 数值稳定性、technical-missing 功效模拟、pre-run/post-run 生命周期及 receipt-bound Test 门禁已复核。该结论不授权正式 A-3b；导师 MDE、用户批准和真实 pre-flight 仍不可省略。

本轮随后修改了 `a3_verdicts.py`、`a3_bridge.py`、动作校验器和 Prefix 控制器。新代码不能自动继承旧复审范围，后续独立审查必须绑定最终 commit 和代码哈希。当前正式 A-3b、Test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 均保持 HOLD。

## 2. R3 全零的根因

### 2.1 动作空间和状态不是主要障碍

在 D-079 v2 的 24 个 D5 Diagnostic 场景上，`PERMISSION → ROLLBACK → COMPENSATED → ESCALATE` 可实际达到零残余。控制器可以观察自身已接受的提交、公开工具合同和补偿返回值，不需要读取隐藏故障、延迟或 `retry_after`。

原 Hand 的 `PERMISSION → ESCALATE` 在已有提交前缀时遗留副作用，因此 R3 的 `class_success=0`。对当前 D5 子集，全零的直接原因是**恢复顺序缺失**，不是动作空间不可达。该结论不能替代对每一种新故障结构的标签验证。

### 2.2 审计中另行发现的标签边界

新构造的反例为：正常提交的前缀步骤运行期 `compensation_available=False`，随后权限拒绝。解析证明为 R4，但旧稳健标签搜索在 `make_pattern_spec()` 中把无故障步骤的补偿可用性强制设为 `True`，错误给出 R3。

修正位于 `experiments/pilot_a3b/a3_verdicts.py`：所有可补偿合同步骤均尊重场景给定的运行期补偿可用性；不可补偿合同仍为 blocked。`test_a3_labels.py` 新增反例，要求稳健标签和解析标签均为 R4。这是保守的标签修正，不依据控制器输出改变金标准。

D-079 v2 重新生成结果保持：

- 288 scenarios、48 clusters、UNKNOWN=0；
- manifest SHA-256=`09df6babbb6e3222ea57a7f354654636ac2437b7011dbe3f1ac738df894a0bca`；
- R1/R2/R3/R4 各类数量不变。

因此不能把新反例的标签缺陷误报成“D-079 D5 标签全部错误”。

## 3. 实现的机制

### 3.1 公开前缀状态

`ControllerState.prefix` 每项只含：

- `state`：由自身公开观察得到的 `NOT_COMMITTED/COMMITTED/PARTIAL/COMPENSATED`；
- `confirmed`：是否收到公开提交确认；
- `compensatable`：公开工具合同；
- `compensated`、`compensation_failed`；
- `compensation_status=NOT_ATTEMPTED/COMPENSATED/FAILED/UNKNOWN`。

状态只能由 `PublicToolView` 构造和由公开返回值更新。`ToolRuntime.state`、隐藏故障、隐藏补偿计数、可见性延迟和重试时钟不进入策略状态。`test_controller_state_accepts_restricted_public_tool_views` 证明即使运行时内部已经提交，公开控制器也不能据此获得隐藏提交。

### 3.2 动作语义与边界

- `ROLLBACK` 按 `prefix_reverse` 指定的顺序补偿已知前缀；逐项记录真实结果，只清除实际成功的项。
- 空回滚、任一项失败或结果未知均不能报告整体 `COMPENSATED`。
- `compensation_scope=CURRENT` 区分当前步骤补偿与前缀补偿。当前补偿失败时，可先清理仍可补偿的既有前缀，再升级；前缀补偿失败不能被伪装成成功。
- `prefix_retry_failed=True` 允许重试失败的前缀补偿，但仍受每 episode 24 次决策上限约束；耗尽预算是 `runtime_forced_abort`，不是成功恢复。
- `VERIFY_PREFIX` 只读取此前已经公开返回的补偿回执，逐项写入 `prefix_verification_log`；它不查询隐藏提交状态。
- 当前步骤补偿成功后返回原恢复流程；强手工 Prefix 基线进一步使用 `RETRY` 重做当前步骤，符合 R2 的 compensate-then-redo 语义。只有前缀清理完成后才选择最终 `ESCALATE` 或 `STOP_SAFE`。

新增 `tool_action_count` 汇总实际工具动作，保留旧 `action_count` 仅作历史兼容。后续实验的成本分析不得把旧近似字段当成真实工具调用数。

### 3.3 可演化参数与演化接口

| 参数 | 含义 | 当前证据边界 |
|---|---|---|
| `prefix_reverse` | 前缀补偿顺序 | 当前模拟器各补偿相互独立，顺序的结果区分度未证明 |
| `prefix_verify` | 是否读取前缀补偿回执 | 回执是公开信息；当前没有独立外部验证误差模型 |
| `prefix_retry_failed` | 前缀补偿失败是否重试 | 永久失败下只增加成本，预算有界 |
| `prefix_stop_action` | 最终 `ESCALATE` 或 `STOP_SAFE` | 必须同时报告 `escalation_reason`，不能把两种终止混称人工升级 |

clone、mutate、crossover 保留控制器类型和四个参数；混合表示交叉显式拒绝。合同校验要求权限拒绝后的回滚必须有已知前缀，前缀验证必须跟随补偿观测。修复算子保留合法 guarded rollback，不允许非法前缀动作。

`make_shared_initial_pool()` 先以固定 seed 生成共同基础 FSM，再用独立随机流扩展 Prefix 参数。8/8 个测试个体的基础基因、默认动作和标志完全一致；比较时使用规范键顺序而非字典插入顺序。

## 4. 原始机制证据

执行入口：`experiments/pilot_a3b/prefix_mechanism_audit.py`。它先验证 D-079 v2 manifest 和 committed lock，再评价两个固定控制器；没有搜索、种群、参数选择或 LLM 调用。

| 方法 | 子集 | n | class success | 平均残余 | 平均可避免伤害 | 硬约束违规 |
|---|---|---:|---:|---:|---:|---:|
| Hand | D5 / R3 | 24 | 0 | 1.00 | 1.00 | 0 |
| PrefixAware | D5 / R3 | 24 | 24 | 0.00 | 0.00 | 0 |
| Hand | D6 / R4 | 24 | 0 | 2.25 | 1.25 | 0 |
| PrefixAware | D6 / R4 | 24 | 24 | 1.00 | 0.00 | 0 |

D6 的 Prefix 结果达到逐场景 `min_reachable_harm`，不是把不可补偿影响消除。D5/D6 是专门子集，不能与 D-079 全部挑战场景上的历史 Hand R4 汇总混为一谈。

原始产物：`experiments/pilot_a3b/results/d085_prefix_mechanism_audit/`

- `prefix_mechanism_summary.json`：SHA=`4cc4f3d4df8111d312d6e2737b4e5958387ff5e83c377276bd6e26e1b07ea9b6`；
- `prefix_mechanism_rows.json`：SHA=`4a84d8ac7cdaaf2549334479226eee7446c2fa0a36402e8a98282ed2fcbe4ca3`；
- `prefix_mechanism_rows.csv`：SHA=`6561a04905887442a91a1aee0f4ebbca23ad0af5adbef8261d6d8cebf86b68c8`。

独立复算直接读取 CSV，而非调用汇总函数：96 行、48 个场景双方法配对、每个 method×label 的 n、成功数/率、平均残余、平均可避免伤害、硬约束数、PrefixCompensationSuccess、R4 最小残余及 R3 两次决策全部一致；加上 CSV/JSON 逐字段一致和最终来源哈希检查，共 33 项通过。结果保存于 `prefix_mechanism_independent_check.json`。

早期缺少完整来源哈希、工具成本以及 current-redo 修复前的文件以 `.pre_provenance`、`.pre_tool_cost`、`.pre_current_redo_fix` 后缀保留，没有覆盖或删除不利结果。

## 5. 新挑战集与封顶审计

`prefix_challenge_generator.py` 只构造新的 Train/Validation，不构造或读取最终 Test：

- Train：6 families × 4 strata × 3 repeats = 72；
- Validation：2 个不相交 families × 4 strata × 3 repeats = 24；
- 每 split 的 R1/R2/R3/R4 均为 18/6（Train/Validation）；
- scenario ID、seed 与 D-079 Diagnostic 无交集；
- manifest SHA-256=`cf769671873c594ec73e9a9e7df75bf1774135af6745da54b3411fb08c45d492`；
- committed lock：`experiments/pilot_a3b/prefix_manifest_lock.json`；篡改 manifest 或 lock 均 fail closed。

`prefix_fixed_controller_ceiling_audit.json` 保存 192 行固定控制器结果。修正后的 PrefixAware 在新 Train 和新 Validation 上均为：**全部类别成功、零可避免伤害、零硬约束违规**，即 `ceiling_for_required_behavior=true`。修复前产物以 `.pre_current_compensation_fix` 和 `.pre_current_redo_fix` 保留。

**所以该简单挑战集不能用来证明 EC 优于固定规则。没有启动任何新优化器实验。**

## 6. 创新性边界

[SagaLLM, PVLDB 2025](https://arxiv.org/html/2503.11951v2) 已明确提出事务状态跟踪、补偿回滚和独立验证。前缀补偿、状态记录或 Saga 顺序本身不是本项目的新颖点。现有 EvoMAS、HFlow、EvoCF、GEPA 也已覆盖反馈引导演化、经验记忆或多目标候选选择。

当前只可提出待证伪候选：**公开前缀状态与约束演化表示的组合能否在非平凡任务上超过强手工 Prefix 规则和普通 EA**。封顶结果、工程测试及固定规则对比均不构成该候选成立的证据。

## 7. OPEN 与唯一下一步

- **OPEN-1：** 当前独立补偿模型中，顺序和回执验证的结果区分度不足；需要合法、可观察、非人为调参的依赖与失败结构，不得修改现有 manifest 追求正面结果。
- **OPEN-2：** `crosscheck_all_patterns()` 的广义旧诊断仍含 UNKNOWN 和解析/搜索不一致，不能声称整个抽象标签空间已完全等价；其独立标量补偿选项和有限 horizon 需另行审计。当前只验证了具体反例和既有/新 manifest。
- **OPEN-3：** 最终 Test 仅有封存的 seed、分层和规模规则；精确 family roster、独立保管承诺和一次性评价协议未完成，Test 未生成、未读取。
- **OPEN-4：** 真实 benchmark、真实 LLM、A800 辅助模型及跨域泛化均未验证。
- **OPEN-5：** 尚无 Hand/Rule/NSGA-II/NSGA-III/Constrained NSGA-III 的配对优化器结果；算法创新仍不成立。

**唯一下一步：** 由新的独立审查会话审查本报告、`87_PREFIX_AWARE_EXPERIMENT_PREREGISTRATION.md`、最终实现及封顶门。审查通过前不得启动新优化器；不得以本报告作为 GO。
