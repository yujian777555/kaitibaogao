# D-094 API Canary Report

本报告区分 Mock 与真实 OpenAI-compatible API。Mock 不构成真实 LLM 接通或性能证据。

## 真实 API

- 状态：**BLOCKED_CONFIGURATION**
- API 真实接通：False
- HTTP attempts：0
- 输入/输出 Token：0 / 0
- 成本（USD）：0.0
- 延迟（秒）：0.0
- Agent 状态：NOT_RUN
- LLM decisions：0
- 缺失配置（仅名称）：`BASE_URL`、`MODEL`、`D094_LLM_INPUT_COST_PER_1M`、`D094_LLM_OUTPUT_COST_PER_1M`

## Mock 多轮集成

- 状态：**MOCK_PASS**；backend=`mock`，不是实际 API 调用。
- Agent 状态：COMPLETED；LLM decisions=2；Mock attempts=2。
- 工具轨迹：`verify_dependency` → `complete_recovery`
- 硬约束违规：0；hash chain valid=True。

## 边界

Phase 2 B0/B1/B2、API genome search、Validation/Test 和模型训练均未执行。没有可验证的算法提升结论。
