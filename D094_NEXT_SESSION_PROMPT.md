# D-094 下一会话接管提示词

## 当前状态

- 唯一仓库：`yujian777555/kaitibaogao`；工作分支：`d094-llm-agent-integration`。
- 建分支基线：`f409a730fd1c1cae90584f7591a213e916f28c2c`。开始工作前必须重新查询远端 HEAD、main 和 worktree，不信任历史完成声明。
- Phase 0 已实现于 `experiments/d094_llm_agent/`：OpenAI-compatible HTTP Adapter、Mock、结构化动作、多轮 Agent、工具网关、Typed Genome、NSGA-II、评价器和请求/执行账本。
- D-094 单元/Mock 测试：36/36，全项目回归578/578。Black 与 compileall 已执行。代码提交`bc087c0dd08c5bd25b25e64311775765ae5c81d4`的CI run`44328080784`已completed/success，D-094日志36/36 OK；无D-094专属性能artifact。后续纯文档提交无run时写NOT RUN。
- Mock Canary：MOCK_PASS，2 个 LLM decisions，工具轨迹 `verify_dependency → complete_recovery`，hash chain valid。它不是实际 API 实验。
- 真实 Canary：**BLOCKED_CONFIGURATION**。API key 存在，但 base URL、MODEL、输入/输出 Token 价格未配置；真实 HTTP attempts=0、Token=0、成本=0、延迟=0，API 未接通。没有可验证的算法提升。

## 不可变边界

不得修改 D-092/D-093 的源码、数据、预注册、报告或 HOLD 结论，不得修改 main，不得把 Mock 写成真实接通。不要删除或覆盖已有 Canary 证据；新运行使用新的版本化输出目录。CI 只运行测试，不发起真实 API 请求。

## 下一步：先完成真实 Canary

在用户环境配置以下变量，不要把值写入 Git、日志或聊天：

- `D094_LLM_API_KEY`（或既有 `OPENAI_API_KEY`）
- `D094_LLM_BASE_URL`
- `D094_LLM_MODEL`
- `D094_LLM_INPUT_COST_PER_1M`
- `D094_LLM_OUTPUT_COST_PER_1M`
- 可选预算覆盖：`D094_LLM_MAX_REQUESTS`、`D094_LLM_MAX_COST_USD`、`D094_LLM_TIMEOUT_SECONDS`

真实执行入口会强制更低上限：最多 3 个 Agent decisions、4 个 HTTP attempts、1 次 retry、每次 128 output tokens、20 秒超时、0.10 USD 估算成本上限、temperature=0。配置不完整或价格无效时继续零调用阻断。

```bash
python experiments/d094_llm_agent/run_d094_canary.py \
  --execute-real \
  --outdir experiments/d094_llm_agent/results/canary_r1
```

只有真实响应、多个真实 LLM decisions、工具执行、零硬约束违规和完整账本均通过，才能把 Canary 写成 PASS。失败时保留 request ledger 的模型、请求 ID、Prompt hash、Token、延迟和错误，不记录密钥或隐式思维链。

## 真实 Canary 后的实验

真实 Canary PASS 后，按 `D094_EXPERIMENT_PLAN.md` 建立新的 D-094 独立小 Train，依次跑通：

1. B0：注入的确定性规则策略，LLM=0；
2. B1：固定 Genome/Prompt/模型/API；
3. B2：相同模型/API/任务/预算下 NSGA-II 优化 Typed Genome。

先检查工具调用成功率、Genotype/Phenotype 多样性和成本，再决定是否扩大。不得用 D-092/D-093 Train、Validation/Test 或结果调参。B3 动态反馈、RSI、A800 训练和大规模 API 搜索均需后续独立设计与授权。

## 验证命令

```bash
python -m unittest discover -s experiments/d094_llm_agent -p "test_*.py" -v
black --check experiments/d094_llm_agent
python -m compileall -q experiments/d094_llm_agent
```

安全工具 bandit/gitleaks/semgrep/mypy/ruff 在上次环境中不可用，不得声称其已运行。提交后必须核验远端 HEAD/main、工作区、文件内容、真实 CI 和 artifact；没有 run 就写 NOT RUN。
