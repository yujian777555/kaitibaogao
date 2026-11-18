# D-094 LLM Agent 与演化计算融合设计

- 状态：Phase 0 设计基线；不是实验通过报告。
- 基线：`f409a730fd1c1cae90584f7591a213e916f28c2c`
- 分支：`d094-llm-agent-integration`

## 1. 研究问题与边界

研究问题：如何利用演化计算优化真实 LLM Agent 的规划、工具调用和故障恢复，并用真实执行反馈推动后续代际改进。

D-094 使用独立目录 `experiments/d094_llm_agent/`、独立任务和独立账本。D-092/D-093 的源码、数据、报告、预注册和 HOLD 结论保持不变。当前只实现 Phase 0，并在配置完整时执行受限 Phase 1 Canary；不启动 Phase 2 搜索、Validation/Test、模型训练或大规模 API 实验。

## 2. 方案选择

- 采用 Python 3.11 标准库 `urllib` 实现 OpenAI-compatible HTTP 传输，保持与仓库 unittest 体系一致，不增加 SDK 依赖。
- OpenAI SDK 能减少部分传输代码，但需要新增依赖并锁定版本；本阶段没有必要。
- 通用 Agent 框架不适合当前已有的确定性模拟环境和 Typed Genome 研究接口，因此不引入新的框架。

真实 API 和 Mock 只在传输边界不同，共用 JSON 解析、Schema 校验、请求预算、成本账本和 Agent Loop。日志中的 `backend` 永久区分 `mock` 与 `openai-compatible`，Mock 不能写成真实接通。

## 3. 模块与控制流

| 模块 | 职责 |
|---|---|
| `d094_llm_client.py` | 环境配置、HTTP 传输、有限重试、JSON 决策解析、模型/请求/Token/延迟记录 |
| `d094_ledger.py` | 请求预算、Token/成本账、脱敏、hash-chain 执行日志 |
| `d094_agent.py` | 多轮 LLM 决策、工具 Schema/权限网关、环境执行、轨迹和 Rule-based 适配器 |
| `d094_genome.py` | 六基因 Typed Genome、合法交叉/变异、版本化 Prompt 与配置/hash |
| `d094_evolution.py` | NSGA-II 非支配排序、crowding、可行性优先、交叉/变异/选择 |
| `d094_evaluator.py` | 多目标汇总、行为多样性、硬约束与 B0/B1/B2 评价接口 |

每个 LLM 决策轮严格执行：公开观察 → LLM `generate_action` → 本地决策 Schema → 工具参数 Schema → 可选语义复核 → 环境权限检查 → 环境状态转换 → 新公开观察。B1/B2 每一轮都必须调用 LLM；任何错误不得静默切换到规则策略。B0 是独立规则适配器，不调用 LLM。

## 4. LLM 输入输出契约

输入只含任务目标、公开环境状态、最近公开观察、允许的记忆投影、工具名称/描述/参数 Schema 和当前 Agent 配置。禁止 hidden outcomes、隐藏标签、未来结果、evaluator 内部数据和 Validation/Test 信息。公共输入中的敏感字段会被拒绝。

结构化输出只允许：

```json
{
  "action": "tool_call | finish",
  "tool_name": "string | null",
  "tool_arguments": {},
  "rationale": "不超过240字的公开简短说明",
  "verification_required": true
}
```

`tool_call` 必须有字符串工具名，`finish` 的 `tool_name=null` 且参数为空。禁止额外字段，不请求或保存隐式思维链，也不保存无效响应正文。最终成功响应只保存上述结构化决策及模型、请求 ID、Prompt SHA-256、Token 和延迟。

HTTP 路径为 `POST {base_url}/chat/completions`，使用 Bearer 环境密钥、`temperature=0`、有限 `max_tokens` 和 JSON response format。base URL 不允许 query、fragment 或 userinfo，HTTPS 为默认；仅测试注入可使用 localhost HTTP。

## 5. 安全、重试和预算

- 密钥只从 `D094_LLM_API_KEY` 或 `OPENAI_API_KEY` 读取，不写入源码、请求日志、异常或报告。
- base URL/model 优先读取 `D094_LLM_BASE_URL`、`D094_LLM_MODEL`，兼容 `OPENAI_BASE_URL`/`OPENAI_API_BASE` 和 `OPENAI_MODEL`/`OPENAI_MODEL_NAME`。
- 默认最多 1 次重试；仅网络错误、408、429、5xx 或无效结构化响应可重试。Retry-After 有上限，所有 HTTP attempt 都计入请求预算。
- 请求预算在调用前检查；错误、超时和响应解析失败也保留一条最终账本记录。
- Token 价格使用 `D094_LLM_INPUT_COST_PER_1M`、`D094_LLM_OUTPUT_COST_PER_1M`。成本未知时不得写成 0，也不得用于正式成本目标。
- Canary 要求完整 base URL、模型、密钥、单位价格和成本上限；任一缺失均不调用。
- 成本在响应后超过上限时保留响应账并终止，不再发起新请求。
- 日志递归拒绝 `api_key`、authorization、cookie、token secret 等敏感键；Prompt 默认只保存 hash。

## 6. Typed Agent Genome

| 基因 | 合法值 | 可执行语义 |
|---|---|---|
| `planning_mode` | `direct`, `stepwise`, `verification_first` | 改变发送给 LLM 的规划指令与公开计划状态；是否改变行为由 phenotype 验证 |
| `recovery_mode` | `retry_priority`, `verify_priority`, `compensation_priority`, `dependency_aware` | 控制失败后的恢复指令、verify/compensate 限制或依赖候选过滤 |
| `reflection_trigger` | `none`, `after_failure`, `after_subtask` | 决定是否向下一轮加入简短结构化反思请求，不增加隐藏思维链 |
| `memory_mode` | `recent_trajectory`, `structured_failures`, `compressed_summary` | 选择确定性公开记忆投影，无额外 LLM 总结调用 |
| `tool_call_guard` | `strict_schema`, `post_plan_verify` | 纯 Schema 或增加环境语义复核；环境权限检查始终存在 |
| `max_plan_steps` | `3`, `5`, `8` | 限制 LLM 决策轮数，包含被拒绝动作 |

搜索空间为 `3×4×3×3×2×3=648`。Genome canonical JSON 和 SHA-256 唯一；Prompt 模板 `d094-react-json-v1` 独立版本化并计算 SHA-256。变异只替换一个基因为另一合法值，交叉逐基因继承，不生成非法配置。行为 phenotype 使用动作、工具参数和公开观测的 canonical hash，不把 prompt 文本差异当作行为差异。

## 7. 演化与多目标评价

B2 使用完整 NSGA-II：父代与后代合并、可行性优先、非支配排序、crowding distance、确定性 hash tie-break、合法交叉/变异。演化对象是上述 Typed Genome，不是无约束 Prompt 文本。B3 动态反馈在 B0/B1/B2 链路通过前不实现、不运行。

目标方向：Task Success、Recovery Success 最大化；Constraint Violation、Harm、Tool Cost、Token Cost、Latency 最小化。Behavior Diversity 以 genotype/phenotype 唯一数及比例在种群层报告，不用单一加权总分替代 Pareto。硬约束违规数大于 0 的候选不可行，不能被成功率抵消。成本未知时不得启动正式 Pareto 搜索。

## 8. B0/B1/B2 对照

| 臂 | 决策方式 | 演化 | 研究职责 |
|---|---|---|---|
| B0 | 注入的现有确定性 policy adapter，LLM 调用为 0 | 无 | 规则基线 |
| B1 | 固定 Typed Genome + 固定 Prompt + 固定模型/API | 无 | LLM 基线 |
| B2 | 相同模型/API/任务/评价预算，NSGA-II 搜索 Typed Genome | NSGA-II | EC 的独立贡献 |

Phase 2 只使用新建 D-094 独立 Train 任务，固定任务顺序、模型、温度、种子、请求/成本上限和评价口径。B1/B2 的模型和 API 配置一致。先检查工具成功率、行为差异和成本，再决定是否扩大。B3 只在后续版本加入真实失败反馈到演化算子概率。

## 9. 测试与证据边界

Mock 测试覆盖：真实 HTTP payload、脱敏、超时/重试/预算/成本、无效 JSON、每轮 LLM 调用、Schema/权限拒绝、恢复模式、记忆投影、648 个合法 Genome、NSGA-II 已知答案、可行性和多目标指标。Canary 只有真实 HTTP 成功响应才能记为真实接通；配置不完整时报告实际阻断，调用数/Token/成本均为 0。合成测试和 Mock 轨迹不构成算法性能提升证据。
