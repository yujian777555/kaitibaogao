# D-094 Phase 2 R2 真实实验结果

## 1. 结论

R2 原始执行已结束，实际写入 **1260/1260** 个设计 episodes，但真实退出状态为 **INVALID_BUDGET**。真实发送的 API 请求为 3704 次，Token 推导成本为 **1.0002363 USD**，超过冻结的 1.00 USD 上限。数量完整不等于实验有效。

预算拒绝导致 B2 最终候选的 36 个 final episodes 均为 LLM_ERROR，未产生真实模型调用。因此 B2 vs B1 没有有效性能结论，当前候选创新判定为 **INVALID**。R1 INVALID 独立保存在 `results/phase2_r1/`，未混入或覆盖。

## 2. 实际执行数量与 API 预算

| 部分 | Episodes | 真实发送 API | 预算拒绝记录 | 说明 |
|---|---:|---:|---:|---|
| B0 fixed | 36 | 0 | 0 | 规则 Agent 完成 |
| B1 fixed | 36 | 162 | 0 | 固定 DeepSeek Agent 完成 |
| B2 search | 1,152 | 3,542 | 252 | 32 个唯一 Genome，每个36 episodes |
| B2 final | 36 | 0 | 36 | 全部因预算耗尽而 LLM_ERROR |
| **合计** | **1,260** | **3,704** | **288** | 原始 request records=3,992 |

- 输入 Token：**2,600,905**；输出 Token：**183,304**。
- Token 推导成本：**1.0002363 USD**；峰值/cache-miss口径，不是服务商账单。
- 预算上限：4000 次真实发送、1.00 USD；实际请求数未超限，成本超限。
- 模型：`deepseek-flash`；temperature=0；显式非思考模式。
- 墙钟时间：1680.2265611 秒；并发=4。
- 无任何 Mock 数据或缓存命中冒充真实调用。

## 3. B0/B1/B2 指标

B2 final 的数字只是预算失败轨迹，不是有效算法性能。

| 指标 | B0 fixed | B1 fixed | B2 final（无效） |
|---|---:|---:|---:|
| Task Success | 1.0000 | 0.6667 | 0.0000 |
| Recovery Success | 1.0000 | 0.6667 | 0.0000 |
| Harm | 6.75 | 6.75 | 0.00 |
| Tool Cost | 121.50 | 120.20 | 0.00 |
| Constraint Violation | 0 | 0 | 0 |
| Input Tokens | 0 | 103,091 | 0 |
| Output Tokens | 0 | 8,006 | 0 |
| Token Cost USD | 0 | 0.0405345 | 已知成本=None；上界=0.0392715 |
| 平均 episode Latency（秒） | 0 | 7.9202 | 约0.00002（未调用API） |
| Execution Errors | 0 | 0 | 36 |

### B1 相对 B0

固定 LLM Agent 没有超过规则基线：成功率由 36/36 降为 24/36，Harm 相同，Tool Cost 仅下降 1.3，但增加 103,091/8,006 Token 和显著延迟。

逐 seed 的 B1−B0 成功率差：

| Seed | B0 | B1 | 差值 |
|---:|---:|---:|---:|
| 101 | 12/12 | 7/12 | **-5/12 = -0.4167** |
| 202 | 12/12 | 9/12 | **-3/12 = -0.2500** |
| 303 | 12/12 | 8/12 | **-4/12 = -0.3333** |

### B2 相对 B1

形式上逐 seed 成功率差为 -7/12、-9/12、-8/12，但全部来自预算拒绝后的零调用结果，**不是有效算法差值**。有效配对差值应记为 **NOT AVAILABLE**，不得据此宣称 B2 退化或改善。

## 4. 搜索阶段的探索性信号

NSGA-II 实际评价32个唯一 Genome，最终 feasible Pareto front 有10个候选。搜索阶段选中的 Genome 为：

`b5dbe97a0ff4bc9da85d2373b24427f027e4c026cd965003a6e1657d25618abe`

```text
planning_mode=stepwise
recovery_mode=retry_priority
reflection_trigger=after_subtask
memory_mode=structured_failures
tool_call_guard=post_plan_verify
max_plan_steps=8
```

其搜索评价为36/36成功，逐 seed 均12/12，Harm=7.0、Tool Cost=134.2、Token成本=0.0480141 USD、平均延迟8.2261秒。它说明演化搜索能够找到不同且可能更好的行为，但成本高于 B1，且最终独立评价无效。因此这只是待复现信号，不能记为 POSITIVE_SIGNAL 或创新成立。

## 5. 硬约束与有效性

| 类别 | R2 原始事件复算 |
|---|---:|
| Invalid Action | 0 |
| Unauthorized Action | 420 |
| Illegal Transition | 0 |
| Pending | 0 |
| Duplicate | 0 |
| Runtime Abort / MAX_STEPS | 603 |

预算拒绝另计288次，不混入 unauthorized。成功率不能抵消这些约束。未进行统计显著性检验：实验无效且只有3个探索性 seeds。

## 6. 原始产物

目录：`experiments/d094_llm_agent/results/phase2_r2/`。

| 文件 | SHA-256 |
|---|---|
| `episodes.jsonl` | `1aeabb018dcb5a3041fb383407fb7d2ec8da8ad4d730ac5f9d78302295bd36b9` |
| `summary.json` | `a56bf6fc0f6904abe794d07210ed36e3b6d50b4d9490357b49e482f6e2815241` |
| `execution_lock.json` | `d3310a95b161a29af8458c4bc4dbf473a7d034417e16a092955e3f8d92287dea` |
| `evolution_ledger.json` | `31f621f26a851f35e50ffaba6a3406bebd1468bbf9eb66fe623d4357d647255d` |
| `independent_audit.json` | `b57ddef5b5d9497a017020f3fd40ccad04794d8179679ea314e045e9b7cfad8c` |
| `analysis.json` | `4e6e4c5119e1e7f59526977e0643204163a327aa85f4320a854d1a0049e52853` |

以上 JSON 使用与 Git 一致的 LF 内容字节计算 SHA-256。执行锁在 summary 中保留运行时 CRLF 原始 SHA=`bee7cbee73e2f7f1bbc027bc3111ada25f374a6fbfcdfce98b8ccb2a3e08c08e`；独立审计显式核验 raw/canonical-LF/CRLF 的对应关系，未修改实验语义。

独立复算见 `D094_R2_INDEPENDENT_AUDIT.md`；Genome/Phenotype 详见 `D094_GENOME_PHENOTYPE_ANALYSIS.md`。下一轮只形成预算安全的 R3 设计，不在本报告中启动新 API 搜索。
