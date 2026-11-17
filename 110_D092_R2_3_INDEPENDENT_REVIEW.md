# 110 — D-092 R2.3 独立验收与 Typed Adapter 入门审查

**日期：** 2026-11-18

**仓库/分支：** `yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`

**审查基线：** `6f9f7d9af062d9f4a871e429d40da6c0645cdb18`

**最终决定：** `ACCEPT_FOR_TYPED_ADAPTER`

**实验批准：** `APPROVED_FOR_EXPERIMENT = NO`
**审查方式：** 实际读取当前/历史文件、原始 D-091 artifacts 和绑定源码；独立复算哈希、矩阵、预算与优先级分数。未执行 probe、genome search、exhaustive reference 或 Validation/Test。

## 1. Git 与仓库状态

| 项目 | 独立核验 |
|---|---|
| 实际接管/远端 branch HEAD | `6f9f7d9af062d9f4a871e429d40da6c0645cdb18`，一致 |
| main HEAD | `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，未修改 |
| 工作分支相对 main | ahead/behind=`320/0` |
| 本地工作区 | `git status --short --branch` 无修改，clean |
| 最近提交 | R2.3 内容修复 `787303d…`；报告格式修正 `6f9f7d9…` |
| 当前审查基线 CI | 无新 workflow run；check/status=0；CI=`NOT RUN`；无新 artifact |

仅访问指定仓库，未读取或混用其他研究仓库。审查开始时不存在未提交工作。

## 2. R2.3 与历史文件身份

| 文件 | raw SHA-256 | canonical SHA-256 | Git blob | 结论 |
|---|---|---|---|---|
| R2.3 `103_D092_TRAIN_ONLY_PREREGISTRATION.md` | `75f9c72aa7d3a70880f59f7b803ed88e919d47e9c42e7168ba1b7eddbc3e7522` | `549c595ed657d0b0582e6d6f41dfcfc241bde82b7daa2bdbf89bb3a660497ce4` | `1498f20a6f298093c06d126a766c037a980869a3` | 全部独立复算匹配 |
| R2.2 snapshot `103_D092_TRAIN_ONLY_PREREGISTRATION_R2_2.md` | `c0035d0f7236eff03325e81c2b7967ae166bc4c73047e390d502859f6d8fdc5c` | `f18aecb71791e43220ac74920c67c27141c58eaadfde74fd0190103e0b4695a3` | `006aface19258f5d9ba597011dfe9048dfea8897` | 全部匹配；保留历史内容 |

R2.1 snapshot raw/canonical/blob=`104df3497f58171f48e82e25674d1b14e22673a34561d263f8679aadd34648ee` / `e71027477f49bde939c3a45a1d7327e04d426da4b06a4b4a9a1c41c687916a45` / `773f39e5984c20d011a8d89245ecf52790886088`。R0/R1/R2/R2.1/R2.2 均保留，未被 canonical 覆盖。

13/13 绑定源码 canonical SHA 与 Git blob 全部匹配，包括 d088 的真实 blob `afe2ed253704d2bf9f4e3f57f6e0a14f04f14be5`。Train manifest 含 96 个唯一 IDs，Git blob=`b917b4c624601022e8d8896182dfaed71ba0d21c`。

## 3. 第一门：F9 canonical identity encoding — ACCEPT

R2.3 §5.2 明确两种 identity payload 使用同一序列化器：

```python
json.dumps(payload, ensure_ascii=False, sort_keys=True,
           separators=(",", ":"), allow_nan=False).encode("utf-8")
```

SHA-256 输入恰为该字节串，无额外换行或空格。episode 字段仍为 seed、unique_ordinal、genome_sha256、scenario_id；attempt 字段仍为 episode_reference、dispatch_ordinal。composite keys、反馈计数及 receipt lifecycle 未改变。

独立哈希向量（含非 ASCII scenario）：

```text
episode canonical bytes =
{"genome_sha256":"g","scenario_id":"场景","seed":711,"unique_ordinal":0}

episode_reference =
102f69d482699fe24e5db5e9d47aa6815d5de333ae9f79ec18c90105616497ea

attempt canonical bytes =
{"dispatch_ordinal":0,"episode_reference":"102f69d482699fe24e5db5e9d47aa6815d5de333ae9f79ec18c90105616497ea"}

compensation_attempt_id =
1dad47e02af7fda7a139180f89c4d5c0bcd992773a4713e148c81c0446c66298
```

两种 identity 的字节定义唯一且可复算，F9 定向验收通过。

## 4. 第一门：F13/P07 真实控制流 — ACCEPT

### 4.1 源码调用链

- `dependency_recovery.py::_compensate()` 在 route success 时先写 `tools[tool_id]="COMPENSATED"`，随后才设置 delayed pending 并返回 TIMEOUT。故状态变更与回执可见性必须分开。
- D088 `_pending_action()` 在等待窗口内，如果 `_available()` 非空且 `_can_dispatch_more()` 为 true，返回 None。
- D088 `act()` 随后进入 D090 `_abort()`；后者经 `_available_or_fallback()`、`_should_stop()`、`_priority()` 继续正常动作选择，并不强制 WAIT。
- `_verify()` 在到期首次确认时清除 pending/resolve_at 并写 last_receipt；成功 delayed dispatch 的 tool state 不在 VERIFY 时二次改变。
- D088 `_update_evidence()` 已在 TIMEOUT dispatch 后将 attempts 记为 seen，因此后续 delayed FAILED 不重复增加 route_failures；`_primary_blocked_or_failed()` 仍能由公开 last_receipt=FAILED 允许 alternate。

### 4.2 逐步轨迹复核

| 步骤 | 动作 | 回执 |
|---:|---|---|
| 1 | COMPENSATE(C,primary) | TIMEOUT；C 仍 COMMITTED |
| 2 | WAIT | WAITED |
| 3 | VERIFY(C) | PENDING |
| 4 | WAIT | WAITED |
| 5 | WAIT | WAITED |
| 6 | VERIFY(C) | FAILED |
| 7 | COMPENSATE(C,primary) | TIMEOUT；第二次 outcome=true，C 当场 COMPENSATED |
| 8 | COMPENSATE(B,primary) | TIMEOUT；因 C 已 COMPENSATED 而可派发 |
| 9 | WAIT | WAITED |
| 10 | VERIFY(B) | PENDING |
| 11 | WAIT | WAITED |
| 12 | WAIT | WAITED |
| 13 | VERIFY(B) | FAILED |
| 14 | VERIFY(C) | COMPENSATED |

步骤 7 后 C receipt pending 但状态已经 COMPENSATED，因此步骤 8 必须允许 B primary 派发，不能插入 WAIT。步骤 13 清除 B pending 后，步骤 14 清理 C receipt。14 步后 `budget_remaining=24-14=10`，B primary/last_receipt=FAILED 与 B alternate 均满足派发条件。

P06 threshold=4，10>4，ordinary 选择 B primary；P07 threshold=12，10≤12，tight 选择 B alternate。根据绑定 BASE 真实数值独立复算：

```text
hint_weight + 2*cost_weight + dependency_weight - alternate_boost
= 2.770802651881641
```

tight key 的 requires 数与 cost 使 alternate 胜出。R2.3 的 PASS/HOLD 条件与真实控制流一致，P07 定向验收通过。这里仅审查源码推演规格，没有把它写成新实验结果。

## 5. 第二门：D-091 历史证据继承 — PASS

实际读取 D-091 输出/源码 manifest、指标复算、方法分派、候选指纹与矩阵、逐 family/scenario 指标、23-step witness、21-step BFS、消融汇总和失败轨迹。D-091 output/source manifest Git blob 分别匹配 `0f4e9143d4d19fcc247c5ec06d50a96cb63c99bf`、`b1be6adbff2b784743bc935b11f018dc7c3e3625`；output manifest 所列 12 个文件的当前字节数与 raw SHA-256 全部匹配。

必须继承的负面事实全部保留：

1. 已保存指标可复算，maximum absolute metric difference=0；但只覆盖保存的 best/ablation rows。
2. 旧 `random` 与 NSGA-II 同路径，不能作为独立随机基线。
3. 旧 State-Evo 是静态 mutation profile，不是动态反馈。
4. 15 个保存候选有 8 个 genome，但只有 1 个 trace/outcome phenotype；105/105 pairs 等价。
5. 旧 25-step 下界被撤回；23-step witness 成功，独立 BFS 最短为 21。
6. P1 局部改善伴随整体 Harm 退化；P2/P4 有 pending 硬约束违规。
7. proposal/cache/generation/operator 完整历史为 `NOT_AUDITABLE_FROM_SAVED_TRACE`。
8. D-090 无可冻结候选，不证明 EC 提升。

证据行数独立读取：480 family rows、1,920 scenario rows、105 candidate pairs、649 ablation-failure trace rows。未重新运行 D-090 或改写其原始数据。

## 6. 第二门：五臂、反馈与公平性设计审查

| 臂 | 规格审查 | 实现状态 |
|---|---|---|
| A0 | 从 canonical unevaluated set 用 random_proposal 独立均匀无放回采样，不调用 NSGA survivor | 待实现 |
| A1 | 非支配排序、逐目标 crowding、零跨度处理、确定性 tie-break | 待实现 |
| A2 | ASF、极端点、translated normalization、35 方向、association、niche=0/>0、独立 RNG | 待实现 |
| A3 | 仅由上一轮 12 个完整 unique offspring 的真实 Train 评价聚合更新块概率 | 待实现 |
| A4 | 永久 F=0、严格均匀概率、与 A1 轨迹等价检查 | 待实现 |

五臂使用相同 96 Train、scenario order、目标、初始池与真实评价预算。A0 不执行 survivor；A1/A3/A4 使用同一 NSGA-II；A2 单独使用完整 NSGA-III。A3/A4 仅反馈机制不同，A4 的零反馈计算不得消费额外 variation RNG。

六项反馈、原 4×6 矩阵、β=2、τ=.25、ε=.1、稳定 softmax、概率上下界和每轮更新时点均明确。无截距使 \(\phi_k(0)=0\)，A4 因此严格均匀。反馈仅使用上一轮已完成真实 Train rollout 的聚合边际量；不读取 hidden outcome、逐场景标签或 audit view。

## 7. Genome/Phenotype、选择与账本审查

- 五字段 typed schema 到底层 D090Genome 的映射唯一；144 组合与完整映射保持一一对应。不得把静态唯一性误写成已验证 phenotype 多样性。
- trace/outcome/joint phenotype 使用完整 96 场景行为 bundles 的 canonical hashes，不只是聚合指标。
- `H_trace/H_outcome/H_joint<2` 仅表示 complete phenotype collapse；near-collapse 仅报告比例，不偷改统计门槛。
- proposal、parents、operator/block/locus、cache、duplicate、survivor、feedback、RNG 和最终选择均需完整记录，直接回应 D-091 best-only 缺口。
- 最终从 unique feasible archive 的 Pareto 集按 min(R3,R4)、R3+R4、CondRec、Harm、Cost、hash 的冻结顺序选择；无 feasible candidate 返回 NO_FEASIBLE_CANDIDATE。
- 真实 probe 与行为可辨识性仍是后续门禁；本审查不宣称已有 phenotype 实证。

## 8. 预算、统计、硬约束与信息隔离审查

- 每臂每 seed：96 unique genome evaluations×96 scenarios=9,216 episodes；384 attempts cap 含初始化；重复/cache 消耗 attempt 但不增加 unique/rollout。
- 五臂五 seeds 的 230,400 仅为设计上限，不是实际运行数量。
- A3−A1、A3−A4 是主比较；A1−A0、A2−A1 为次要比较。R3 阈值=1/24，至少 4/5 seeds 严格同向；无效/NO_FEASIBLE 配对不得删除或替换。
- invalid、unauthorized、illegal transition、pending、duplicate、runtime abort 六类硬约束不可被 fitness/Harm/Cost 抵消。
- optimizer 只接收每个 genome 的聚合 fitness、约束、反馈边际量和 opaque phenotype hashes；scenario_id、episode_reference、逐场景 reward、原始 trace 和 audit 查询均禁止。
- evaluator-internal 与 audit-only 数据可用于独立复算，但不能回流搜索组件。

上述设计没有实质性未解决问题，具备进入 Typed Adapter 与合成测试的条件。算法身份和隔离结论目前均为**规格审查通过，不是实现验证通过**。

## 9. 最终决定

**`ACCEPT_FOR_TYPED_ADAPTER`**

- F9：ACCEPT。
- F13/P07：ACCEPT。
- D-091 负面证据继承：PASS。
- D-092 五臂、反馈、预算、选择、硬约束、信息隔离与账本设计：PASS_FOR_IMPLEMENTATION。
- 历史文件与哈希完整性：PASS。

**`APPROVED_FOR_EXPERIMENT = NO`。**

本决定只允许开始 Typed Adapter、静态算法测试、合成测试与实现一致性审查。不得启动 960 probe、正式 genome search、13,824 exhaustive reference、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 LLM API、A800/ARWM、UndoBench TEST、ThinkingBox、D-090 重跑或 main merge。

## 10. 下一阶段具体任务

1. 实现 typed genome adapter：144 映射、canonical serialization、完整 BASE 保持与往返验证。
2. 实现五臂统一 runner/evaluator/episode contract，保持场景顺序、配对 seeds 和预算。
3. 实现 NSGA-II、完整 NSGA-III、A3 动态反馈/A4 零反馈和唯一 feasible Pareto 选择。
4. 实现 proposal/unique/cache/duplicate/operator/survivor/RNG/feedback/optimizer/audit 账本。
5. 依次执行 typed mapping、genome/phenotype、budget、RNG、NSGA-II、NSGA-III、feedback、A1/A4 equivalence、信息隔离和 synthetic runner integration 测试。
6. 合成测试覆盖异常、无可行候选、预算耗尽和边界条件；不把合成结果写成真实性能提升。
7. 完成实现一致性审查并保存代码/测试哈希；之后再申请 Probe 与正式 Train-only 搜索授权。
