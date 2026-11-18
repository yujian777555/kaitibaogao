# D-094 API Canary Report

本报告区分 Mock 与真实 OpenAI-compatible API。Mock 不构成真实 LLM 接通或性能证据。

## 真实 API

- 状态：**PASS**
- API 真实接通：True
- HTTP attempts：3
- 输入/输出 Token：1552 / 148
- 成本（USD）：0.0006432
- 延迟（秒）：5.2379412
- Agent 状态：COMPLETED
- LLM decisions：3
- 响应模型：`deepseek-flash`（官方对应 DeepSeek-V4.1-Flash-1017）
- 工具轨迹：`inspect_dependencies → verify_dependency → complete_recovery`
- 硬约束违规：0；hash chain valid=True。
- 原始轨迹：`experiments/d094_llm_agent/results/canary_r1/real/trace.jsonl`；完整账本：`results/canary_r1/real/summary.json`。
- 成本口径：按官方峰值且全部 input cache-miss 费率（input 0.3、output 1.2 USD/1M tokens）由真实 Token 计算保守估计，不是账单查询；[官方模型与价格](https://api-docs.deepseek.com/quick_start/pricing)。
- 请求显式使用 `thinking={"type":"disabled"}`，未保存思维链；[官方 Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)。

## Mock 多轮集成

- 状态：**MOCK_PASS**；backend=`mock`，不是实际 API 调用。
- Agent 状态：COMPLETED；LLM decisions=2；Mock attempts=2。
- 工具轨迹：`verify_dependency` → `complete_recovery`
- 硬约束违规：0；hash chain valid=True。

## 边界

Phase 2 B0/B1/B2、API genome search、Validation/Test 和模型训练均未执行。没有可验证的算法提升结论。
