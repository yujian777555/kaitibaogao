# D-094 R2 独立原始数据审计

## 1. 审计结论

**审计一致性：PASS_WITH_LIMITATIONS；实验状态：INVALID_BUDGET。**

审计器 `experiments/d094_llm_agent/d094_phase2_audit.py` 不调用 API、不重跑任务，也不使用 Runner 的汇总函数。它从原始 JSONL 重新计算 episode identity、行为 hash、请求账、逐臂/逐 seed 指标、候选目标、Pareto front、最终选择、Gene 分析和预算。

限制：Phase 2 原始 episodes 未携带逐事件 hash-chain，`event_hash_chain=NOT_PROVIDED_BY_RUNNER`。本次锁定原始文件 SHA-256 保证保存后的文件身份，但不能倒称 Runner 曾生成事件链。Canary 的独立 hash-chain 是有效的，不能与 Phase 2 混用。

## 2. 完整性与唯一性

- episodes=1260，等于执行锁设计量1260。
- B0 fixed=36、B1 fixed=36、B2 search=1152、B2 final=36。
- 每臂每 phase 均覆盖 seeds 101/202/303；每个搜索 Genome 有36个评价。
- 32个搜索评价事件对应32个唯一 Genome；跨代重复评价=0。
- episode identity 全部唯一且由 arm/phase/task/seed/genome hash 复算一致。
- request identity 由 episode_id+attempt ordinal 构成，3992条全部唯一。
- 真实 provider request ID=3704且全部唯一；288条预算拒绝记录无 provider ID，未发送请求。
- Train manifest 内部 hash 与执行锁一致；Validation/Test 均未包含。

## 3. API 真实性与成本复算

- 所有实际请求均为 `backend=openai-compatible`、`model=deepseek-flash`。
- 没有 Mock backend、Mock request ID或缓存结果混入。
- 请求模型、响应模型、Prompt SHA-256、Token、延迟和错误逐条可追溯。
- 真实发送=3704；预算拒绝=288；原始请求记录=3992。
- 输入 Token=2,600,905，输出 Token=183,304。
- 按锁定费率复算成本=1.0002363 USD；summary 与原始账本一致。
- 全局成本上界与实际 Token 推导成本相同，因为本轮没有无响应网络错误，只有预算拒绝。
- 成本超过1.00 USD上限0.0002363 USD，故实验保持 INVALID_BUDGET。

此前出现的全局预算差异已定位：summary 统计真实发送请求，原始账本另含预算拒绝记录。审计通过 `reconcile_budget_records()` 分账，未修改原始数据或删除错误。

## 4. 六类硬约束复算

从公开事件标记映射，不使用成功率抵消：

| 类别 | 数量 | D-094 映射边界 |
|---|---:|---|
| Invalid Action | 0 | Schema拒绝或未知工具事件；本轮无 |
| Unauthorized Action | 420 | 权限、前置验证/恢复/补偿/依赖拒绝 |
| Illegal Transition | 0 | 明确的已完成状态再转换等；本轮无 |
| Pending | 0 | 公开 PENDING 标记；本轮无 |
| Duplicate | 0 | 公开 DUPLICATE_COMPENSATION 标记；本轮无 |
| Runtime Abort | 603 | Agent 达到冻结 max_plan_steps 的 MAX_STEPS episodes |

另有288次 LLMCostLimitExceeded 属预算拒绝，不冒充 unauthorized。B2 final 有36个 LLM_ERROR，最终评价无效。

## 5. 汇总、选择与分析复算

以下均与原始 episodes 一致：

- B0/B1/B2逐臂及逐 seed 指标；
- 32个搜索候选的七项目标、硬约束和 phenotype bundle hash；
- 10个 feasible Pareto front 候选；
- 最终搜索选择 `b5dbe97a0ff4bc9da85d2373b24427f027e4c026cd965003a6e1657d25618abe`；
- 六基因取值覆盖、单基因行为/性能差、相同行为组；
- 全局请求、Token、成本、逐阶段用量和演化事件数。

审计输出：`results/phase2_r2/independent_audit.json`，SHA-256=`b57ddef5b5d9497a017020f3fd40ccad04794d8179679ea314e045e9b7cfad8c`。原始 episodes SHA-256=`1aeabb018dcb5a3041fb383407fb7d2ec8da8ad4d730ac5f9d78302295bd36b9`。

跨平台换行审计：执行锁 summary 保留运行时 CRLF 原始 SHA=`bee7cbee73e2f7f1bbc027bc3111ada25f374a6fbfcdfce98b8ccb2a3e08c08e`；当前 Git LF 文件 SHA=`d3310a95b161a29af8458c4bc4dbf473a7d034417e16a092955e3f8d92287dea`。审计分别计算 raw/canonical-LF/CRLF，本文件内容匹配 CRLF 形式，不改变任何实验字段。

## 6. 安全与未提供证据

- 未发现真实 API Key；密钥仅从环境读取。通用安全扫描工具未安装，不能声称 bandit/gitleaks/semgrep 已运行。
- Phase 2 未提供逐事件 hash-chain；审计明确保留此限制。
- 被拒绝的重复 proposal 和每代 survivor phenotype 未完整记录；相应比例/历史不得伪造，见 Genome 分析。
- 审计通过只代表原始数据与报告可复算，**不代表实验有效、B2优于B1或创新成立**。
