# 108 — D-092 R2.2 独立定向复审与 107 号勘误

**审查日期：** 2026-11-17  
**仓库/分支：** yujian777555/kaitibaogao / pilot-a-stateful-recovery  
**审查基线：** 7cd092431b0817f67aca3960ecad2590fb6d5b13  
**最终决定：** REQUEST_CHANGES / HOLD（仅剩 P07 trace 与一项 hash-encoding 明确性修订）  
**协议状态：** R2.2 REVIEWED_NOT_ACCEPTED / NOT FROZEN / NOT RUN  
**授权边界：** 只读复审；没有修改算法源码，没有运行 rollout/probe/search/exhaustive/Validation/Test。

---

## 1. Git、版本和文件身份

| 项目 | 独立核验 |
|---|---|
| branch HEAD | 7cd092431b0817f67aca3960ecad2590fb6d5b13，匹配交付 |
| main HEAD | 683b3fe7fc52c86e917d523fdc6bbb13abbfd653，未修改 |
| ahead / behind | 317 / 0 |
| R2.2 raw SHA-256 | c0035d0f7236eff03325e81c2b7967ae166bc4c73047e390d502859f6d8fdc5c，匹配 |
| R2.2 canonical SHA-256 | f18aecb71791e43220ac74920c67c27141c58eaadfde74fd0190103e0b4695a3，匹配 |
| R2.2 Git blob | 006aface19258f5d9ba597011dfe9048dfea8897，匹配 |
| R2.1 snapshot blob | 773f39e5984c20d011a8d89245ecf52790886088，与父提交 R2.1 canonical 逐字节一致 |
| R0 / R1 / R2 | 当前 blob 与父提交完全一致，未覆盖 |
| 本次 commit 文件 | 恰好 7 份文档：canonical 103、R2.1 snapshot、README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG、51_DATA_GATE |
| 新 workflow runs | 0 |
| check runs / commit statuses | 0 / 0 |
| 新 artifact | 无 |

raw/canonical SHA-256 使用从 GitHub Contents API 读取的完整 UTF-8 内容独立计算；canonical 规则按协议的 split-lines 后 LF join 执行。R2.2 的三种身份均匹配。

GitHub 远端 API 不暴露执行者本地工作树，本报告只确认远端 branch HEAD 与交付一致；本地 clean 为执行者报告值，不冒称已独立读取。

## 2. 源码与数据闭包

### 2.1 源码依赖

13/13 项源码 Git blob 和 canonical SHA-256 全部重新读取并计算，全部匹配 R2.2 §2.2。特别是：

experiments/d088_recovery/d088_policies.py

真实 blob：

afe2ed253704d2bf9f4e3f57f6e0a14f04f14be5

**107 号报告给出的另一 SHA 是审查转写错误。** R2.2 保留真实对象值是正确的，不应修改为 107 中的错误值。本报告正式更正 107 号 §1.2。

### 2.2 Train manifest

- manifest Git blob：b917b4c624601022e8d8896182dfaed71ba0d21c；
- 场景总数：96；
- 标签计数：R1/R2/R3/R4 各 24；
- Q0/Q0b/Q1/Q2/Q3/Q4 六个锚点全部存在；
- 未发现替换或重生成 Train 数据的证据。

### 2.3 已通过的冻结项

R2.2 与 R2.1 snapshot 的以下内容逐字节一致：

- F8 typed genome mapping；
- F14 exhaustive Pareto gap；
- 五臂与主次比较；
- μ=12、λ=12、12 initial + 7×12 = 96 unique；
- 384 proposal attempts；
- 五 seeds；
- 反馈矩阵；
- 数值统计门槛。

phenotype-collapse 的 H<2 数值门槛未变；R2.2 将其准确命名为 complete phenotype collapse，并将 near-collapse 留作描述性报告，不构成统计门槛改变。

## 3. 六项定向复审

### F9 — PASS（逻辑闭合；补一条序列化约定）

R2.2 正确补齐：

- episode_reference 纳入 seed、unique_ordinal、typed genome hash、scenario_id；
- attempt hash 纳入 episode_reference 和 dispatch ordinal；
- run-level 与 global ledger 使用 composite keys；
- 反馈集合按 composite attempt keys 计数，不按裸 ID 去重；
- immediate COMPENSATED/FAILED、blocked、ALREADY、PENDING、DUPLICATE 的关闭语义；
- TIMEOUT 保持 open，delayed VERIFY 首次终态回执关闭；
- 重复 VERIFY 不重复计数；
- 同 tool 多 pending route、丢失回连或二次关闭均使 run INVALID。

跨 genome episode identity collision 和 immediate-success terminal-record 两项已实质关闭。

**小型实现前明确项：** §5.2 对 episode_reference 与 compensation_attempt_id 使用 canonical_json(...)，但 §3.3 目前明确写的是 canonical genome JSON。为避免不同实现采用不同空格/键顺序，R2.3 应明确两种 identity payload 也使用 §3.3 相同序列化参数：UTF-8、ensure_ascii=False、sort_keys=True、separators=(",",":"), allow_nan=False。该项不改变 ID 字段或算法，只冻结字节编码。

### F10 — PASS（规格层）

total grammar validator → public mask → environment 的顺序明确。非 tuple/list、空动作、未知 kind、错误长度、非 str/unhashable 参数和未知 ID 均在任何环境 dict membership 前归为 grammar invalid。固定 INVALID sentinel 对环境安全，原始请求由不调用用户自定义 hash/eq/repr 的 snapshot encoder 记录。

sentinel 会经环境 _record 消耗一次 decision/cost，不改变 tick/state/pending；动作级 invalid 只计一次。规格与绑定的 DependencyRecoveryEnv.step() 对照一致。

此为规格审查 PASS，不代表 total validator 已实现或测试已运行。

### F11 — PASS（公式与转置测试）

E 的行约定现在唯一：第 j 行是第 j 个 translated extreme point。非对角上三角矩阵的精确解正确：

x=(53/144, 19/72, 5/24, 1/6, 1/6)

intercepts 与 scale 为：

a=(144/53, 72/19, 24/5, 6, 6)

对 translated 点 (1,1,1,1,1)，normalized 结果等于 x；文档列出的 E^T 错误结果也正确。该测试确实能识别转置，非对角矩阵不再被对角测试替代。

### F12 — PASS（信息边界规格）

三层接口分离明确：

- evaluator_internal_rows 保留标签和 per-scenario outcome；
- optimizer_reward_view 仅提供每个 unique genome 的聚合 fitness、约束计数、反馈边际量和 opaque phenotype hashes；
- audit_only_view 保留完整审计材料和 hash→record 索引，但禁止搜索组件访问。

scenario_id、episode_reference、per-scenario class/conditional/correct/avoidable reward、原始 trace 和任何 96-row reward/list 均被明确禁止进入 optimizer view。聚合 R3/R4/CondRec 与聚合反馈值仍保留为预注册优化信号。

此为接口规格 PASS，不代表隔离实现已存在。

### F13 — REQUEST_CHANGES：P03 通过，P07 的 17-action prefix 不符合真实控制流

#### P03/Q1 — PASS

P01/P03 仅差 fallback。Q1 初始状态下 A/B/C primary 的 requires 均未满足；alternate requires 为空，但 normal _available() 不允许 alternate。normal available 为空，fallback candidates 恰为 A/B/C alternate。P01 会选择其中一个 alternate；P03 fallback 关闭后最终返回 BASE ESCALATE。该对照可达且不依赖 hidden outcome。

#### P07/Q3 — HOLD：真实共同前缀不是 17 步

R2.2 声称第 7 步第二次 COMPENSATE(C,primary) 返回 TIMEOUT 后，步骤 8–10 连续 WAIT。但这与绑定源码不符。

在 Q3 的第二次 C primary dispatch 中，route outcome 为成功。真实环境 DependencyRecoveryEnv._compensate() 在 delayed receipt 返回 TIMEOUT 的**同一 dispatch**就将 C 状态改为 COMPENSATED，并设置 pending/resolve_at。

因此下一步：

1. C 的 receipt 仍 pending；
2. B primary 的 requires=[C] 已满足；
3. D088 _pending_action() 在等待窗口内发现独立可派发工作，返回 None；
4. policy 随后进入 D090 _abort()，正常派发 B primary。

所以第 8 步是 COMPENSATE(B,primary)，不是 WAIT。当前 R2.2 的 17-action prefix 和 budget=7 before-state 不可达。

#### 正确的源码推演轨迹

| 步骤 | 动作 | 回执/状态 |
|---:|---|---|
| 1 | COMPENSATE(C,primary) | TIMEOUT，C 仍 COMMITTED |
| 2 | WAIT | WAITED |
| 3 | VERIFY(C) | PENDING |
| 4 | WAIT | WAITED |
| 5 | WAIT | WAITED |
| 6 | VERIFY(C) | FAILED |
| 7 | COMPENSATE(C,primary) | TIMEOUT；第二次 outcome=true，C 当场变 COMPENSATED，receipt pending |
| 8 | COMPENSATE(B,primary) | TIMEOUT；B primary 因 C 已 COMPENSATED 而可派发 |
| 9 | WAIT | WAITED |
| 10 | VERIFY(B) | PENDING |
| 11 | WAIT | WAITED |
| 12 | WAIT | WAITED |
| 13 | VERIFY(B) | FAILED |
| 14 | VERIFY(C) | COMPENSATED |

步骤 14 后：

- decision_count=14；
- budget_remaining=24−14=10；
- C 已 COMPENSATED；
- B primary 与 B alternate 均可用；
- B primary 的 last_receipt=FAILED，但 TIMEOUT dispatch 已先将 attempts 记为 seen，因此不会新增 route_failures；
- _primary_blocked_or_failed() 因公开 last_receipt=FAILED 允许 B alternate。

在这个共同 before-state：

- P06 threshold=4：10>4，ordinary priority；
- P07 threshold=12：10≤12，tight priority；
- ordinary score(primary)−score(alternate)=**+2.770802651881641**，选择 B primary；
- tight key 首先比较 requires 数与 cost，选择 B alternate。

故真正可达的第一处分叉是**14-action prefix 后、budget_remaining=10**，而不是 R2.2 冻结的 17-action prefix 后 budget=7。

这也更正了 107 号报告的另一项审查错误：107 曾断言 Q3 的 8–12 预算区间没有可比较的共同 before-state；其推演遗漏了 C receipt pending 期间 B primary 的独立派发。该区间实际在 budget=10 可达。

**处理：** P07 不应被标记 PASS。R2.3 只需把 Q3 prefix、before-state、预算和 PASS 条件改为上述 14-action/budget=10 轨迹，保留 P06/P07 的阈值 4/12 与原 144-genome 搜索空间，不需要重新设计 harm-ordering 机制。

### F15 — PASS（随机数规格）

直接 random.Random(seed_integer)，不再先无参构造后 reseed。整数种子由 UTF-8/D092-R2/seed/stream 字符串的 SHA-256 前八字节 big-endian 派生。固定 API、stream 隔离和 A1/A4 消费等价约束均明确；不再依赖系统熵入口。

## 4. 独立审查矩阵

| 项目 | 结论 | 说明 |
|---|---|---|
| Git/R2.1 snapshot/R0-R2 | PASS | 身份与历史快照未变 |
| R2.2 raw/canonical/blob | PASS | 三种身份匹配 |
| 13 源码依赖 | PASS | 13/13 canonical SHA 与 Git blob |
| Train manifest | PASS | 96 IDs，R1–R4 各24，6 anchors存在 |
| F8 | PASS / unchanged | 与 107 已接受规格一致 |
| F9 | PASS + serialization clarification | identity/lifecycle 闭合，明确 canonical JSON 编码 |
| F10 | PASS（规格层） | total validator/sentinel 设计安全 |
| F11 | PASS | E row convention 与非对角精确反例正确 |
| F12 | PASS（规格层） | per-scenario 信息不进入 optimizer |
| F13 P03 | PASS | P01/P03 Q1 初始 fallback 对照可达 |
| F13 P07 | REQUEST CHANGES | 17-action prefix 漏掉 B primary dispatch；真实分叉在 budget=10 |
| F14 | PASS / unchanged | 原五目标 gap 不变 |
| F15 | PASS | 直接整数种子初始化 |

## 5. 唯一下一任务：R2.3 两处极小定向修订

保留 R2.2 immutable snapshot，不修改算法源码或 Train 数据。修订 canonical preregistration 为 R2.3，只做：

1. **F13/P07：** 将 Q3 17-action/budget=7 断言改为上述真实 14-action/budget=10 共同前缀；明确 C delayed success dispatch 当场改变 state，故 B primary 可在 C receipt pending 时派发；冻结 P06 ordinary 与 P07 tight 的第一处分叉。
2. **F9 hash encoding：** 明确 episode_reference 与 compensation_attempt_id 的 identity payload 使用 §3.3 相同 UTF-8 canonical JSON 参数，确保哈希字节跨实现唯一。

不得重开 F8/F14、F9 receipt lifecycle、F10 grammar、F11 matrix、F12 view isolation、F15 PRNG；不得改变 μ/λ、96 unique、384 attempts、五臂、五 seeds、反馈矩阵、统计门槛和 96 Train 场景。

R2.3 完成后只对这两处做定向复核。通过后立即进入：

**Typed Adapter → 静态算法测试 → 合成测试 → 实现一致性审查。**

不再进行大范围文档重构。

## 6. 当前授权边界

当前为 **REQUEST_CHANGES / HOLD**。

尚未实现 adapter/searcher，尚未执行 960 probe、96×96 genome search、13,824 exhaustive reference 或 Validation/Test。无算法提升证据。

R2.3 定向复核通过后，允许进入 typed adapter 和静态/合成测试的实现审查；实现审查通过并取得用户明确批准前，仍不得运行 probe 或正式 Train-only 搜索。

**结论：R2.2 的五项修复已通过规格复审，P03 已通过；P07 的真实控制流证明仍有一处漏派发。该问题只需修正预注册轨迹，不要求放弃或重构动态 harm-ordering 机制。**
