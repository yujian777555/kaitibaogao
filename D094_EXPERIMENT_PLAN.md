# D-094 Phase 0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 建立可审计的真实 OpenAI-compatible LLM Agent、Typed Genome 与 NSGA-II 基础链路，并在配置允许时执行最小 Canary。

**Architecture:** 标准库 HTTP 传输与 Mock 共用结构化决策、账本和工具网关；NSGA-II 只优化 Typed Genome。真实实验和合成测试严格分离。

**Tech Stack:** Python 3.11、标准库 urllib/dataclasses/json/hashlib、unittest、现有 GitHub Actions。

**Spec:** `D094_DESIGN.md`

## Global Constraints

- 不修改 D-092/D-093、main 或历史结果；只在 `d094-llm-agent-integration` 工作。
- 不在代码、日志、测试或报告中保存密钥，不读取 `.env`。
- 不请求隐式思维链，不使用 Mock 冒充真实 API，不启动 Phase 2 搜索或模型训练。
- 新功能先写失败测试并观察 RED，再最小实现；所有 HTTP attempt 计入预算。
- Canary 上限：3 个 Agent decisions、4 个 HTTP attempts、1 次 retry、每次 128 output tokens、20 秒超时、0.10 USD 估算成本上限、temperature=0。

## Review Focus

- 无效/越权工具参数：环境和本地两层拒绝，环境不得执行。
- 超时、HTTP 错误、无效 JSON和传输异常：消耗预算并留下脱敏最终记录。
- 未知价格：不得写成零成本或进入正式 Pareto 成本目标。
- LLM 提前 finish/持续失败：达到步数停止，不能由规则代码接管。
- 不同 Genome 相同行为：记录 phenotype collapse，不宣称创新。

---

### Task 1: 请求账本和 LLM Adapter

**Files:** `d094_ledger.py`, `d094_llm_client.py`, `test_d094_llm_client.py`

**Interfaces:**
- `RequestLedger(max_requests, max_cost_usd, input_price_per_1m=None, output_price_per_1m=None)`
- `OpenAICompatibleTransport(base_url, model, api_key, urlopen_impl=None)`
- `LLMClient.generate_action(observation, available_tools, agent_config) -> LLMDecision`

- [x] 写 HTTP payload、密钥脱敏、重试、预算、成本、无效 JSON 的失败测试。
- [x] 运行 `python -m unittest discover -s experiments/d094_llm_agent -p "test_d094_llm_client.py" -v`，确认因模块缺失而失败。
- [x] 实现预算/成本/hash-chain 账本、真实传输、Mock 传输和结构化解析。
- [x] 重跑测试，确认真实 payload 与全部边界通过。

### Task 2: Typed Genome 与 Agent Loop

**Files:** `d094_genome.py`, `d094_agent.py`, `test_d094_agent.py`

**Interfaces:**
- `AgentGenome.to_agent_config() -> dict`
- `LLMAgent.run(task, environment) -> AgentRunResult`
- `RuleBasedAgent.run(task, environment) -> AgentRunResult`

- [x] 写每轮 LLM 决策、Schema/权限拒绝、记忆/恢复、B0 零调用和 648 Genome 合法性测试。
- [x] 观察 RED，随后实现版本化 Prompt、合法变异/交叉、工具网关和多轮 Agent。
- [x] 重跑测试，确认 LLM 每轮参与、确定性环境最终授权、失败不静默接管。

### Task 3: NSGA-II 与评价器

**Files:** `d094_evolution.py`, `d094_evaluator.py`, `test_d094_evolution.py`

**Interfaces:**
- `NSGAII.optimize(evaluator, population_size, generations, seed) -> list[Candidate]`
- `evaluate_episodes(episodes) -> EvaluationMetrics`
- `population_diversity(genomes, phenotype_hashes) -> dict`

- [x] 写非支配/crowding 已知答案、可行性不可补偿、合法后代、七项目标和 phenotype 多样性测试。
- [x] 观察 RED，随后实现 NSGA-II 与多目标评价。
- [x] 重跑测试，确认无加权总分、无可行候选被高成功率违规候选替代。

### Task 4: Canary、文档与仓库验证

**Files:** `run_d094_canary.py`, `D094_API_CANARY_REPORT.md`, `D094_NEXT_SESSION_PROMPT.md`, workflow/handoff files

- [x] 用 Mock 完成多步真实 Agent Loop 集成测试。
- [x] 只检查环境变量存在性；配置完整才运行真实 Canary，否则记录阻断和 0 调用。
- [x] 运行 D-094、全项目回归、`compileall`、`git diff --check`，核验无密钥和 D-092/D-093 差异。
- [x] 提交推送后核验远端 HEAD/main、文件内容、真实 CI 和 artifact；未运行项明确 NOT RUN。

## 后续实验门禁

1. **Phase 1：** Canary 只有真实响应才记为接通；配置缺失写实际阻断，调用/Token/成本为 0。
2. **Phase 2：** 用户继续授权后，建立 D-094 独立小 Train，运行 B0/B1/B2；固定模型、任务、预算和种子，报告每个 Genome 和 phenotype。
3. **Phase 3：** 仅在小规模链路、成本和审计通过后扩大 Train-only，并建立独立 Train/Validation/Test manifests；Test 不用于调整。
4. **Phase 4：** 另行预注册 B3 动态失败反馈，比较固定/动态算子概率和 Pareto 前沿，不提前宣称 RSI 或创新成立。
5. **训练：** 仅在轨迹质量、训练目标和独立评价成立后另开分支，不与 Prompt/Genome 演化混报。


## Phase 1 真实 Canary 执行结果

`deepseek-flash` 已通过真实 OpenAI-compatible API 完成 3 次结构化决策和 inspect→verify→complete 工具轨迹。真实输入/输出 Token=1552/148，硬约束=0，hash chain 有效，Agent=COMPLETED。Token 成本按官方峰值且 input 全部 cache-miss 的费率保守估算为 0.0006432 USD，并非账单查询。详细证据见 `D094_API_CANARY_REPORT.md` 和 `experiments/d094_llm_agent/results/canary_r1/`。

## Phase 2 预执行锁定（真实搜索开始前）

- 独立 Train：12 个新 D-094 任务，verification/transient/compensation/hybrid 各 3 个；不使用 D-092/D-093 或 Validation/Test。
- 配对 seeds：101、202、303；相同任务、环境、工具和种子应用于 B0/B1/B2。
- B0：确定性 public-state 规则，不调用 LLM；B1：FIXED_GENOME；B2：相同模型/API 下 NSGA-II 搜索 Typed Genome。
- B2 初始种群 8，3 代，最多 32 个唯一搜索候选；全局 evaluated 集合禁止跨代重复评价。最终从全部已评价候选的 feasible Pareto front 按 objectives 字典序、genome hash 选择 1 个，再在相同 12×3 任务上独立评价。
- 设计 episodes：B0=36、B1=36、B2 search≤1152、B2 final=36，总计≤1260。B2 搜索成本与最终评价成本分账，B1/B2 性能比较只使用各自 final/fixed 的 36 个配对 episodes。
- 全局上限：4000 HTTP attempts、1.00 USD 保守 Token 成本；单 episode 最多 `2×max_plan_steps` attempts；并发 4；timeout=20 秒；每次最多 128 output tokens；temperature=0；DeepSeek 非思考模式。
- 使用官方峰值/cache-miss 费率 input 0.3、output 1.2 USD/1M tokens，成本是保守估计，不是账单。实际缓存或 off-peak 不得被写成精确账单节省。
- 任何预算超限、LLM_ERROR、账本或 episode 缺失均保留并标记 INVALID；不得删除不利 seed、减少 B2 评价量或改变指标。
- 三 seeds 只用于机制探索，报告均值和逐 seed 结果，不提供确认性显著性结论。不同 Genome 的相同行为必须计入 phenotype collapse，不把 Prompt 文本差异当成创新。


## Phase 2 R1 实际失败与 V2 成本口径

R1 输出 `results/phase2_r1/` 保留为 INVALID：B0/B1 各完成36 episodes，B2尚未执行。共163 HTTP attempts、输入/输出Token=103039/8042，已计价成本约0.0405621 USD。B0任务成功率36/36，B1为23/36，均无硬约束违规；这些不是有效B2对照结果。

根因一是一次 transport error 没有返回Token usage，使该episode成本未知并中止Pareto构建；根因二是B2/search用量函数会覆盖而非累计候选成本。不得删除R1或将其当作成功实验。

V2 不改变任务、seeds、五目标之外的成功率定义、种群、代数或选择方向，只修复审计与成本可执行性：

- 有真实usage的请求按锁定费率计算已知成本；
- 无响应/缺失usage请求的input上界为canonical messages的UTF-8字节数，output上界为冻结max_tokens；这是保守上界，不假设网络错误免费；
- 每episode和全局同时保存已知成本、成本上界和unknown标记；Pareto成本目标统一使用`token_cost_upper_usd`；
- 真实响应到账后，SharedBudget用实际usage替换该请求上界；异常保留上界；B2/search用量跨候选累计；
- R2写入独立`results/phase2_r2/`和协议`D094_PHASE2_TRAIN_V2`，全局4000 attempts/1.00 USD上限不变。

该口径变更由R1技术失败驱动，不用于选择有利结果。V2仍为探索性Train证据，实际成本不是服务商账单。


## 下一轮候选创新机制与独立消融（尚未执行）

以下计划不改变正在执行的V2。只有V2原始账本、成本、审计和配对比较完整后，才分别建立新版本实验。

### A. 失败反馈驱动的演化算子选择

- 基线：相同Typed Genome、初始种群、seeds和真实评价预算的标准NSGA-II。
- 实验：仅使用已完成Train候选的聚合公开失败特征，调整下一代mutation block概率；固定温度/探索下限并保存分子、分母和每个概率。
- 消融：固定均匀概率、随机置换反馈、真实反馈三臂；比较Pareto front、唯一候选数、无效候选率和Token成本。禁止读取未来结果或held-out标签。

### B. 行为多样性感知的演化选择

- 基线：标准NSGA-II crowding distance。
- 实验：在可行性优先和非支配排序后，对相同phenotype的多个Genome施加确定的重复行为选择规则；不得直接修改真实fitness。
- 消融：不感知行为、仅去重、行为多样性crowding三种；同时报告Genotype/Phenotype唯一数、相同行为组和真实任务指标，防止为提高多样性牺牲全部成功率。

### C. 跨代经验驱动的递归配置改进

- 基线：每代仅使用当前种群的NSGA-II。
- 实验：将历史公开失败经验投影为下一代Agent的memory/recovery配置候选，由真实评价决定保留；不允许Agent直接改评估器或绕过工具权限。
- 消融：无历史、仅最近一代、压缩历史三种；检查跨代改进是否可复现，以及是否只是增加API调用或Token。

三个方向不得合并后宣称各自贡献。任何提升必须来自真实、可复算的配对数据；小样本探索不等于统计确认。A800训练继续冻结，只有轨迹质量、训练目标和独立评价成立后才另开训练分支。


## Phase 2 R2 最终结果与后续入口

R2已实际结束并写入1260/1260 episodes，但真实退出状态为INVALID_BUDGET：真实API=3704次，Token=2600905/183304，Token推导成本=1.0002363 USD，超过1.00 USD。预算拒绝288次未发送请求；B2 final 36个 episodes均LLM_ERROR且无真实模型调用，因此B2 vs B1无有效性能结论。

B0成功率36/36，B1=24/36；B1逐seed相对B0为-5/12、-3/12、-4/12。B2搜索阶段选中Genome `b5dbe97a0ff4bc9da85d2373b24427f027e4c026cd965003a6e1657d25618abe`，搜索评价36/36，但最终评价无效，只能作为待复现信号。32个唯一Genome对应24个 phenotype，无complete collapse。

权威结果=`D094_PHASE2_R2_RESULT.md`；独立审计=`D094_R2_INDEPENDENT_AUDIT.md`；行为分析=`D094_GENOME_PHENOTYPE_ANALYSIS.md`。下一轮只能按`D094_NEXT_EXPERIMENT_PLAN.md`先做R3预算/审计/独立审查，不直接扩大API实验。
