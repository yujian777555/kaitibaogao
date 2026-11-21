# D-094 R4 预算分析与请求前保护

状态：真实 R4 未运行；以下是预注册预算，不是账单。全局政策上限保持既有 **1500 请求 / 0.50 USD**，R4 自身进一步收紧到 **320 请求 / 0.442368 USD**。

## 1. R3.1 实际分布

| 指标 | 实际值 |
|---|---:|
| Train episodes | 42 |
| 真实请求 | 169 |
| 输入/输出 tokens | 127148 / 8090 |
| Token 推导成本 | 0.0478524 USD |
| 每 episode 平均请求 | 4.0238095 |
| 每请求平均输入 tokens | 752.3550296 |
| 每请求平均输出 tokens | 47.8698225 |
| 单请求最大输入/输出 tokens | 831 / 55 |
| 失败请求数/成本 | 0 / 0 USD |
| HTTP 重试 | 0（冻结 `max_retries=0`） |
| 相同 Prompt 重发 | 6/169=3.5503% |

`attempt` 是 episode 内请求序号，不是 HTTP retry 计数。历史 episode 没有保存 canonical message bytes，因此不能补造最大上下文 bytes；只能核验 4096-byte 冻结上限及实际 token usage。R3.1 只有一个任务，逐任务均值等于总体均值，不能外推成多任务保证。

## 2. R4 设计规模

- 两个新 Train 任务×两个 seeds=每候选 4 episodes。
- B1=4 episodes。
- B2/B3/B4 各 4 个唯一搜索候选，search=16 episodes；每臂独立 final=4 episodes。
- 总计 `4+3×(16+4)=64` episodes。
- 所有 Genome 固定五步，每 episode 最多 5 请求；duplicate 不调用，HTTP retry=0。

| 预算部分 | episodes | 请求硬上界 | 成本硬上界 USD |
|---|---:|---:|---:|
| B1 fixed（独立保护） | 4 | 20 | 0.027648 |
| B2 search | 16 | 80 | 0.110592 |
| B3 search | 16 | 80 | 0.110592 |
| B4 search | 16 | 80 | 0.110592 |
| B2 final（独立保护） | 4 | 20 | 0.027648 |
| B3 final（独立保护） | 4 | 20 | 0.027648 |
| B4 final（独立保护） | 4 | 20 | 0.027648 |
| **合计** | **64** | **320** | **0.442368** |

## 3. 保守每请求上界

沿用冻结价格：输入 0.3 USD/百万 tokens、输出 1.2 USD/百万 tokens；最大 canonical messages=4096 bytes，最大输出=128 tokens。

`(4096×0.3 + 128×1.2)/1,000,000 = 0.0013824 USD/request`

其中输入部分上界=`0.0012288`，输出部分上界=`0.0001536`。这是请求前保守代理，不是实际 token 计数或 provider 账单。实际响应按 usage 结算；无响应/未知 usage 保留上界并触发无效处理，不得写成零成本。

## 4. 经验估算与硬上界严格分离

若仅用于规划，把 R3.1 的平均请求/episode 和每请求 token 分布机械应用于 R4 的 64 episodes：

- 请求经验估算=`64×169/42=257.5238095`；
- 输入 tokens≈193749.3333；输出 tokens≈12327.6190；
- Token 推导成本经验估算≈**0.072917942857 USD**。

该数值不是实际 R4 成本、性能预测或可以花到的预算。Fresh Train 路径和模型行为可能不同，因此门禁只认 320/0.442368 的请求前硬上界；不能因历史实际成本低而扩大规模。

## 5. 请求前预留与 final 保护

`ReservedBudget` 在 transport 前原子预留请求槽和成本上界：

1. 开始搜索前，分别预留 `B1`、`final:B2`、`final:B3`、`final:B4` 各 20 请求和 0.027648 USD。
2. search pool 不能使用上述命名池；final 只能消费自己的池。
3. 每笔请求记录 budget request ID、pool、预留、结算实际上界和超预留状态。
4. duplicate 不发起 transport，请求上界=0；重试上界=0。
5. 总成本实际上界、请求数、未知成本或超预留任一异常均 INVALID。
6. 预算不足时缩小设计并重新预注册；本版已 fits，不得在运行中减少 final 或追加预算。

独立复算只读原始账本，不需要真实 API，不另计 API 预算。

## 6. 预检和 Mock 实测

- 零请求预检：`results/r4_preflight/summary.json`，`PREFLIGHT_PASS`、episode=0、`api_used=false`。
- budget plan raw SHA-256=`21b80255516645fdbdf63f5063dbed0b528b4aaf97da4ca52fa1cea3e28ba150`。
- Mock 全链：64 episodes、194 次 **Mock** transport、成本上界约 0.0015132 USD；未超 320/0.442368，hash-chain 有效。
- Mock 数字只验证计数和预算控制，不是实际 API 成本，也不用于替代上面的保守预算。

## 7. 预算结论

设计在既有政策内具有保守可执行余量，搜索与 final 预算已分离。真实执行仍需独立审查、真实入口复核和用户明确批准；`PREFLIGHT_PASS` 不等于 `APPROVED_FOR_EXPERIMENT`。
