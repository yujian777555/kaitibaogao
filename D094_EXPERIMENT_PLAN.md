# D-094 Phase 0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

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

- [ ] 写 HTTP payload、密钥脱敏、重试、预算、成本、无效 JSON 的失败测试。
- [ ] 运行 `python -m unittest discover -s experiments/d094_llm_agent -p "test_d094_llm_client.py" -v`，确认因模块缺失而失败。
- [ ] 实现预算/成本/hash-chain 账本、真实传输、Mock 传输和结构化解析。
- [ ] 重跑测试，确认真实 payload 与全部边界通过。

### Task 2: Typed Genome 与 Agent Loop

**Files:** `d094_genome.py`, `d094_agent.py`, `test_d094_agent.py`

**Interfaces:**
- `AgentGenome.to_agent_config() -> dict`
- `LLMAgent.run(task, environment) -> AgentRunResult`
- `RuleBasedAgent.run(task, environment) -> AgentRunResult`

- [ ] 写每轮 LLM 决策、Schema/权限拒绝、记忆/恢复、B0 零调用和 648 Genome 合法性测试。
- [ ] 观察 RED，随后实现版本化 Prompt、合法变异/交叉、工具网关和多轮 Agent。
- [ ] 重跑测试，确认 LLM 每轮参与、确定性环境最终授权、失败不静默接管。

### Task 3: NSGA-II 与评价器

**Files:** `d094_evolution.py`, `d094_evaluator.py`, `test_d094_evolution.py`

**Interfaces:**
- `NSGAII.optimize(evaluator, population_size, generations, seed) -> list[Candidate]`
- `evaluate_episodes(episodes) -> EvaluationMetrics`
- `population_diversity(genomes, phenotype_hashes) -> dict`

- [ ] 写非支配/crowding 已知答案、可行性不可补偿、合法后代、七项目标和 phenotype 多样性测试。
- [ ] 观察 RED，随后实现 NSGA-II 与多目标评价。
- [ ] 重跑测试，确认无加权总分、无可行候选被高成功率违规候选替代。

### Task 4: Canary、文档与仓库验证

**Files:** `run_d094_canary.py`, `D094_API_CANARY_REPORT.md`, `D094_NEXT_SESSION_PROMPT.md`, workflow/handoff files

- [ ] 用 Mock 完成多步真实 Agent Loop 集成测试。
- [ ] 只检查环境变量存在性；配置完整才运行真实 Canary，否则记录阻断和 0 调用。
- [ ] 运行 D-094、全项目回归、`compileall`、`git diff --check`，核验无密钥和 D-092/D-093 差异。
- [ ] 提交推送后核验远端 HEAD/main、文件内容、真实 CI 和 artifact；未运行项明确 NOT RUN。

## 后续实验门禁

1. **Phase 1：** Canary 只有真实响应才记为接通；配置缺失写实际阻断，调用/Token/成本为 0。
2. **Phase 2：** 用户继续授权后，建立 D-094 独立小 Train，运行 B0/B1/B2；固定模型、任务、预算和种子，报告每个 Genome 和 phenotype。
3. **Phase 3：** 仅在小规模链路、成本和审计通过后扩大 Train-only，并建立独立 Train/Validation/Test manifests；Test 不用于调整。
4. **Phase 4：** 另行预注册 B3 动态失败反馈，比较固定/动态算子概率和 Pareto 前沿，不提前宣称 RSI 或创新成立。
5. **训练：** 仅在轨迹质量、训练目标和独立评价成立后另开分支，不与 Prompt/Genome 演化混报。
