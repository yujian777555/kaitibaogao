# 106 — D-092 R2 独立预注册审查

**审查日期：** 2026-11-17  
**仓库/分支：** yujian777555/kaitibaogao / pilot-a-stateful-recovery  
**审查对象：** canonical R2、R1 immutable snapshot、105 号 R1 独立审查、13 份绑定源码、D-090 Train manifest  
**最终决定：** REQUEST_CHANGES / HOLD  
**R2 状态：** REVIEWED_NOT_ACCEPTED / NOT FROZEN / NOT RUN  
**授权边界：** 只读协议审查；未实现 adapter/searcher、未运行静态算法测试、未执行 probe、未执行 genome search、未访问 Validation/Test。

---

## 1. Git 与文件身份

| 项目 | 独立核验 |
|---|---|
| 审查时 branch HEAD | 3b76e78bb0bd58cb9b812ab7850757bee7cefb07 |
| main HEAD | 683b3fe7fc52c86e917d523fdc6bbb13abbfd653 |
| ahead / behind | 313 / 0 |
| R2 Git blob | 9196c717f2cb79ecd21a25e055a77afe0db03f59 |
| R2 raw SHA-256 | c6e4d1103710eef12fa65105721c6295b5875c45003cc3bc13baa601e66c57b5 |
| R2 canonical SHA-256 | 7f4fb63a9c7ec005d17113ef8c5ddfb48d20bd3f229c947ca67668e5d3a5bc53 |
| R1 Git blob | f5dc28e67d648344cfd8465956f51e1f0582baf4 |
| R1 raw SHA-256 | 2b67f64a20ffe622264ee97629db7d587f56005e7f551ff59bef4b3b29099ec5 |
| R1 canonical SHA-256 | 3a5ad0f108c79bc5fb71529d22d774f4776206c2db42022a994d1893fa1fdc55 |

R2 和 R1 raw/canonical SHA 均由本审查重新计算匹配。R1 snapshot 未被覆盖。

R2 提交相对其父提交 df2b8612a7c08ba3e93211f29c76198b569b79a3 只修改 7 个文档文件：R2、R1 snapshot、README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG、51 数据门禁计划；没有修改实验源码。

### 1.1 数据与源码绑定

- R2 列出的 13 份源码 Git blob SHA：13/13 匹配。
- 13 份源码 canonical SHA-256：13/13 重新计算匹配。
- D-090 Train manifest Git blob、内部 SHA、canonical file SHA：全部匹配。
- Train manifest：96 个唯一 scenario IDs。
- 标签计数：R1=24、R2=24、R3=24、R4=24。
- 96-ID probe panel hash 与前序锁定值一致。

**结论：R2 的版本身份、数据身份和既有源码依赖闭包通过。**

### 1.2 CI / Artifact / 本地状态

- 对 R2 commit 查询 workflow runs：0 条。
- commit combined status：没有 status checks。
- 本轮没有新 CI，也没有新 artifact。
- 最新既有 D-091 CI 44068259009 不是 R2 测试或实验批准。
- 远端 GitHub API 无法核验执行者本地工作树；本审查不声称本地 clean。

---

## 2. 总体判断

R2 相比 R1 有实质进步，以下内容基本闭合：

1. mu=12、lambda=12、12 初始候选 + 7×12 offspring = 96 unique evaluations 的轮次算术正确。
2. A0 无放回采样、进化臂冻结父代、轮末 survivor、OFFER attempts 计数和 384 cap 已有明确骨架。
3. 五臂职责、主次比较、A1/A4 等价检查已明确。
4. 13 份源码、manifest、96 场景身份和 R1 历史快照均可复核。
5. post-rollout evaluator reward 的概念边界比 R1 清楚。
6. 六类 hard constraint 字段与 soft blocked receipts 已区分。
7. phenotype serialization、probe 预算、exhaustive reference 和 invalid seed/no-claim 规则已大幅补齐。

但是，**R2 仍不能作为唯一可执行算法协议**。问题集中在：五字段 typed genome 没有映射到真实 D-090 policy 的全部控制字段；硬约束 action mask/转移表没有冻结；反馈事件计数不能保证 [0,1]；NSGA-III normalization 的坐标系不明确；probe 和 phenotype-collapse 的 PASS/HOLD 判据没有操作化。

这些不是实验结果不理想，而是可能导致不同实现者运行出不同算法、部分基因实际不起作用或反馈数值失真。因此不批准 adapter/searcher 实现和 D-092 运行。

---

## 3. 必须修订的阻断项

### F8 — BLOCKER：typed genome 到真实 D-090 policy 字段的映射缺失

**位置：** R2 §3、§10；绑定源码 experiments/d090_recovery/d090_genome.py、experiments/d090_recovery/d090_policies.py。

R2 定义五个高层 genome 字段，但没有定义每个取值如何完整映射到 D090Genome 的多个底层控制字段。绑定源码表明：

- cycle_mode 实际涉及 pair_rule 与 pair_race_alternate。
- fallback_enabled 实际涉及 exhaustive_fallback 与 fallback_mode。
- completion_guarded 实际涉及 completion_gate 与 completion_mode。
- harm_reorder_budget 实际涉及 harm_first_ordering、harm_order_mode 与 harm_budget_threshold。
- probe_wait 对应 delay_probe_wait。

这不是可以交给实现者自行决定的 adapter 细节。D090Policy 中存在多个“或”条件和重复控制字段：

1. _available_or_fallback() 在 exhaustive_fallback OR fallback_mode == 2 时开启 fallback。只将 exhaustive_fallback=False，但保留 BASE 的 fallback_mode=2，fallback 仍然开启。
2. _should_stop() 在 completion_gate OR completion_mode >= 1 时开启 completion gate。只将 completion_gate=False，但保留 BASE 的 completion_mode=1，completion gate 仍然开启。
3. _pair_filtered_available() 在 pair_rule == 1 时才绕过 pair filtering。只关闭 pair_race_alternate 不会关闭 cycle filtering。
4. _priority() 在 harm_first_ordering 为真时会比较剩余预算与 harm_budget_threshold。将 harm_reorder_budget=None 直接传给阈值比较会产生类型错误；关闭 harm ordering 需要同步控制开关/模式。

因此 P01–P09 的 probe genome 目前只定义了高层值，没有保证真实策略机制按预期打开或关闭。

**R2.1 必须增加唯一 mapping table**，逐个列出五字段的每个取值映射到所有底层字段，并冻结其他 BASE 字段。建议的映射方向（执行者须结合源码复核后写入协议）：

| typed genome | 底层字段必须共同控制 |
|---|---|
| cycle OFF / FILTER_ONLY / ALT_AND_FILTER | pair_rule + pair_race_alternate |
| fallback false / true | exhaustive_fallback + fallback_mode |
| completion false / true | completion_gate + completion_mode |
| harm budget None / 4 / 8 / 12 | harm_first_ordering + harm_order_mode + harm_budget_threshold |
| probe_wait 0 / 1 / 2 | delay_probe_wait |

映射表必须对 P00–P09 的最终底层 genome 逐项展开。新增静态断言：每个高层值都确实改变预期底层字段；互斥机制关闭时不能被另一个 BASE 字段重新开启；None 不进入数值比较。

### F9 — BLOCKER：反馈的 FAILED 事件与 COMPENSATE 分母没有唯一关联

**位置：** R2 §5.2。

R2 定义 r_t 为 FAILED、DEPENDENCY_BLOCKED、CONTRACT_BLOCKED events 数量除以 C_t，其中 C_t 是全部 COMPENSATE events。

但真实环境 DependencyRecoveryEnv 中：

- 立即失败的 COMPENSATE 返回 FAILED；
- delayed COMPENSATE 先返回 TIMEOUT，最终 FAILED 由后续 VERIFY 返回；
- 没有 pending 时，VERIFY 还可能返回该 route 的 last_receipt，包括重复返回 FAILED。

因此，如果 numerator 统计 trace 中所有 FAILED observations，同一个 COMPENSATE attempt 可能被重复计数；VERIFY 的重复回执还可能使 numerator 大于 C_t，从而 r_t>1，违反 R2 声称的特征范围 [0,1]。

反过来，如果 numerator 只统计 COMPENSATE action 当下的 observation，delayed route 最终 VERIFY 失败又不会进入 numerator。

**R2.1 必须冻结 attempt-level receipt accounting：**

- 每个 COMPENSATE dispatch 生成唯一 compensation_attempt_id。
- delayed receipt 的最终 VERIFY 结果回连原 attempt。
- 每个 attempt 最多计一个 terminal receipt。
- 没有 pending 的重复 VERIFY 不产生新的 route-failure event。
- 明确未完成 pending attempt 的计数方式；pending 特征仍独立统计。
- C_t 与 numerator 必须基于同一组唯一 attempt IDs，保证 0≤r_t≤1。

同时明确 DEPENDENCY_BLOCKED、CONTRACT_BLOCKED 的计数单位也是 COMPENSATE attempt，而不是任意 trace observation。

### F10 — BLOCKER：公开 action mask 和合法状态转移表未操作化

**位置：** R2 §7.2。

R2 说明了 action 类别，但没有冻结完整 tuple grammar、状态 precondition 和 typed policy action mask。

真实源码中 RETRY_WORKFLOW 的结果取决于 terminal fault 和 current tool state：

- permission fault 返回 PERMISSION；
- timeout_before 且 current 为 NOT_COMMITTED 才会转为 COMMITTED；
- partial_recover 且 current 已 COMPENSATED、无 pending 才会转为 COMMITTED；
- 其他状态可能返回 PARTIAL 或 INVALID_ACTION。

COMPENSATE 的合法请求还会根据 contract、dependency、pending 和当前状态产生不同回执。R2 把 contract/dependency blocked 设为 soft，但没有说明 public action mask 是否允许这些请求。如果 mask 事先拦截它们，反馈中的 blocked receipts 将无法产生；如果允许，则必须定义它们的精确语义。

此外，illegal_state_transition_count 使用“冻结环境参考转移”，但 R2 只列出允许状态集合，没有列出合法 transition edges。只检查状态属于集合，无法识别错误的状态跳转。

**R2.1 必须补充：**

1. 每个动作的精确 tuple schema；
2. 每个动作的状态 precondition；
3. RETRY_WORKFLOW 的完整合法/无效条件；
4. COMPENSATE public mask 是否允许 contract/dependency blocked attempts；
5. unauthorized 与 INVALID_ACTION 的唯一判定顺序；
6. 完整 state transition table，包括 delayed success 在 COMPENSATE 时即改变 tool state 的真实语义；
7. 监视器逐步比较的 before/action/observation/after 规则。

### F11 — BLOCKER：NSGA-III normalization 的矩阵坐标系不明确

**位置：** R2 §6.3 Step 1–3。

R2 先定义 translated objectives：

bar_f(s)=f(s)-z*，

并用 bar_f 计算 ASF 和极端点；随后写“用五个极端点构造矩阵 E，解 Ex=1，截距 a_j=1/x_j，再令 scale_i=a_i-z_i*”。

这里没有定义 E 的行究竟是原始目标向量 f(e^j)，还是平移后的目标向量 bar_f(e^j)。

- 若 E 使用前文 ASF 所用的平移向量，a_j 已是平移坐标的截距，再减 z_i* 会重复减去 ideal point。
- 若 E 使用原始目标向量，则必须明确写出原始坐标的矩阵定义和转换关系，不能只说“用极端点构造矩阵”。

fallback 的 S 最大值也必须说明是在 raw objective 还是 translated objective 空间中计算。

**R2.1 必须给出唯一矩阵定义、fallback 坐标系、scale 公式和归一化公式**，并添加一个带非零 ideal point 的手算/合成测试，确保不是只在 ideal point 全零时通过。

### F12 — BLOCKER：post-rollout reward 的信息流隔离没有落实到接口

**位置：** R2 §5.1、§9.3、§13.2。

R2 允许 searcher 在完整 Train episode 后读取 class_success、avoidable_harm 等 evaluator reward，同时禁止读取 label、min_reachable_harm、classify_scenario() 和隐藏 outcomes。

但真实 DependencyRecoveryEnv.report() 返回的字典同时包含 label、min_reachable_harm、reward、trace 等字段；R2 的 outcome signature 也包含 min_reachable_harm。仅声明“不得直接提供”不足以定义实现边界。

**R2.1 必须分成两个显式接口：**

- optimizer_reward_view：仅包含预注册允许的 post-rollout reward/fitness 和反馈聚合所需公开 receipts；
- audit_only_view：保留 label、min_reachable_harm、hidden-outcome-derived diagnostics 等，仅供 evaluator 审计和 hash 计算，不能传给 policy、variation、survivor 或 feedback selector。

同时规定 outcome signature 中 min_reachable_harm 的访问权限；其原始字段不得进入 optimizer-visible rows。class_success 和 avoidable_harm 可以作为完整 episode 后的 reward，但必须通过 allowlist 投影交付。

### F13 — BLOCKER：probe PASS/HOLD 和 phenotype collapse 没有量化判据

**位置：** R2 §10、§12.2。

R2 已列出 10 个 probe genomes、960 episodes 和 anchor IDs，但没有规定何种 trace/outcome 差异足以使一个 locus PASS。

“检查可辨识性 PASS/HOLD”仍然需要实现者解释：

- P01/P02 应在哪个 anchor 出现什么 branch evidence？
- P03/P04/P05–P09 各自必须观察到哪种行为差异？
- 只出现 cost 差异是否算行为可辨识？
- trace 改变但 outcome 不变是否 PASS？
- 某一位点所有预注册 contrast 都与 P00 完全相同，是否 HOLD？

同样，F7 把 phenotype collapse 作为 INVALID/NO_CLAIM 条件，却没有定义 collapse 的统计量和阈值。

**R2.1 必须冻结：** 每个 probe 的预期分支断言、允许比较的 trace/outcome 字段、PASS/HOLD 条件，以及 phenotype collapse 的精确计算方式和阈值。不能在看到 probe 结果后再决定阈值。

### F14 — BLOCKER：exhaustive reference 的多目标 search gap 未定义

**位置：** R2 §11.2。

144 个 genome 的 exhaustive reference 会产生五维目标向量和一个 Pareto front，不存在天然唯一的“Train 最优 genome”。

R2 只写“报告每个选中结果相对已知 Train 最优的 search gap”，没有定义 gap 是：

- 每个目标相对 exhaustive ideal point 的 component-wise regret；
- 到 exhaustive Pareto front 的归一化距离；
- Pareto dominance/coverage；
- 还是某个标量化目标的差值。

**R2.1 必须明确报告向量和计算公式。** 建议至少报告五个 objective-wise regret，并单独报告选中候选到 exhaustive Pareto front 的归一化距离；不能把不同目标各自的最优值拼成一个实际不存在的“最优候选”。

该项不改变 D-092 主比较，但必须在 exhaustive reference 执行前关闭。

### F15 — BLOCKER：RNG 引擎没有冻结

**位置：** R2 §6.4、§13.1。

R2 固定了 SHA-256 seed derivation，但没有说明实际 PRNG engine。CPython 3.11.9 和 NumPy 1.26.4 同时存在时，random.Random、NumPy Generator(PCG64) 或其他生成器会产生不同轨迹。

此外，R2 写“按 arm×seed 独立实例化，但 seed derivation 不含 arm ID”。这实际上是相同 stream name/seed 在不同臂使用相同初始随机序列，即 common-random-numbers coupling，而非独立随机序列。

**R2.1 必须明确：**

- PRNG engine 与版本；
- 每个 stream 的实例化方式；
- random()、uniform choice、without-replacement sampling 的具体 API/算法；
- stream seed 字符串的 UTF-8 编码和 SHA 字节截取；
- A1/A4 以及 A1/A2/A3/A4 的同序列设计属于 intentional common random numbers；
- 哪些 stream 允许跨臂共用序列，哪些仅在臂内消费。

---

## 4. R2 审查矩阵

| 项目 | 独立审查 | 说明 |
|---|---|---|
| 文件身份/R1 保留 | PASS | raw/canonical SHA、Git blob 匹配 |
| B1 数据绑定 | PASS | 13 源码、manifest、96 IDs 全匹配 |
| F1 轮次/控制流 | PARTIAL | mu/lambda、父代和轮次已定义；typed-to-policy mapping 缺失 |
| F2 真实预算 | PASS | 12+7×12=96；384 attempts 含初始化 |
| F3 NSGA-III | REQUEST CHANGES | normalization matrix 坐标系有歧义 |
| F4 硬约束 | REQUEST CHANGES | action mask、transition edges 未冻结 |
| F5 反馈 | REQUEST CHANGES | FAILED receipt 计数不唯一；optimizer/audit view 未隔离 |
| F6 phenotype/probe | REQUEST CHANGES | PASS/HOLD 和 collapse 阈值未定义 |
| F7 统计 | PARTIAL | invalid/no-claim 已清楚；collapse 判据缺失 |
| M1 A1/A4 | PASS（规格层） | 等价性断言已定义，尚未实现 |
| M2 exhaustive oracle | PARTIAL | 预算正确；多目标 search gap 未定义 |
| M3 runtime/RNG | REQUEST CHANGES | runtime 目标明确；PRNG engine 缺失 |
| M4 账本字段 | PARTIAL | 六字段统一；attempt-level receipt 和访问权限需补齐 |

---

## 5. 下一步：只做一次定向 R2.1 澄清，不重开已关闭工作

R2 已解决 R1 的大部分问题。下一轮不应重新审计 D-090、不应重写五臂、不应更改 96 evaluations、主要比较或统计门槛。

**唯一下一任务：** 保留 R2 immutable snapshot，给 canonical 103 增加 R2.1 澄清，逐项关闭 F8–F15。

优先级：

1. typed genome 到 D090Genome 的底层字段 mapping；
2. COMPENSATE attempt 与 delayed VERIFY receipt 的一对一归因；
3. action grammar、action mask 和合法 state transition table；
4. NSGA-III normalization matrix 坐标系；
5. optimizer reward view 与 audit-only view；
6. probe PASS/HOLD 和 phenotype collapse 判据；
7. exhaustive multi-objective search gap；
8. PRNG engine 和 common-random-numbers 语义。

R2.1 完成后，只进行针对上述八项的独立复核，不重复检查已通过的文件身份、数据哈希、预算算术和五臂控制流。

---

## 6. 授权边界

当前决定仍是 **REQUEST_CHANGES / HOLD**。

R2.1 之前禁止：

- 实现 typed adapter/searcher；
- 执行 960 probe episodes；
- 执行 96×96 genome search；
- 调参或冻结候选；
- 执行 13,824 exhaustive reference；
- 访问 Validation/Test；
- Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM；
- 修改 main 或混用其他仓库。

**R2.1 定向复核通过后，下一阶段应立即进入 typed adapter + static/synthetic tests 的实现审查。** 不再重复文档层大范围重构。实现一致性复审通过并获得用户明确批准后，才启动 probe 和 D-092 Train-only search。

**最终结论：R2 的版本/数据身份和大部分预算控制流可信；但 typed genome 语义、反馈计数、约束接口和 NSGA-III 数学定义仍未完全闭合。REQUEST_CHANGES / HOLD。**
