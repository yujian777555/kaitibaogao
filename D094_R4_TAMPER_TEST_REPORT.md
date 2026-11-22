# D-094 R4 篡改与预算反例测试报告

日期：2026-11-23。测试文件：`experiments/d094_llm_agent/test_d094_r4_review_fixes.py`。执行结果：15/15 PASS；与原 R4 协议测试合计 22/22 PASS；D-094 全量 150/150 PASS。真实 LLM API=0。

## 1. R4-001 配置篡改（5 个 test methods）

- 合法配置：preflight PASS、64 planned episodes、0 actual episodes、client=0、V2 锁验证 PASS、17 个源码。
- 8 组调用方覆盖逐一拒绝：seeds、search seed、generations=2、440 requests、0.608256 USD、model、每 episode 请求数、bool/int 类型绕过。
- Train task ID 篡改拒绝。
- 臂配置及 B1 Fixed 五步篡改拒绝。
- `compute_budget_plan` 直接调用也不能绕过全局请求上限冻结。

每个非法用例都断言：抛出包含字段原因的 ValueError、输出目录不存在、client factory 未调用、无 episodes.jsonl，因此 API=0 且没有部分执行结果。

## 2. R4-002 统计源码篡改（4 个 test methods）

每个用例均在临时目录复制 17 个锁源码和 4 份协议文档，patch `HERE` 后先证明未篡改锁为 PASS，再只修改临时副本：

| 用例 | 临时修改 | 结果 |
|---|---|---|
| sign flip | `d094_r4_statistics.py` 追加对抗标记 | 锁验证 FAIL |
| bootstrap | `d094_r4_statistics.py` 追加不同对抗标记 | 锁验证 FAIL |
| Holm | `d094_r4_statistics.py` 追加不同对抗标记 | 锁验证 FAIL |
| final entry | `d094_r4_analysis.py` 追加对抗标记 | 锁验证 FAIL |

锁错误定位到发生变化的具体 `source_files.<filename>`。每个用例结束都重新计算生产源码 SHA，确认 17 个生产文件未被测试修改。统计公式、20,000 bootstrap、seed offsets 和四比较 Holm 未改。

## 3. R4-003 搜索预算反例（6 个 test methods）

1. B2/B3/B4 分别执行 80 次计数 Mock transport 调用，第 81 次在底层 transport 前拒绝；底层 calls=80，其他搜索池 calls=0、remaining=80。
2. B2 留 79 请求时，B3 第 81 次仍拒绝，不能借用 B2。
3. B3 留 79 请求时，B4 第 81 次仍拒绝，不能借用 B3。
4. 缩小规模的全局 request cap 单元测试中，第三个请求在 transport 前拒绝，calls=2、sent=2、over_budget=false。这是预算组件单元测试，不是修改 R4 的 320 cap。
5. LLMClient 首次 transport 异常、第二次重试成功，两 attempt 均记到 search:B3；calls=2、pool sent=2、remaining=1、unknown cost 保留。
6. search:B4 返回 unknown usage 后，pool cost_upper 等于请求前最坏上界，pending=0，B2/B3 成本不变。

这些测试直接验证请求前原子预留和结算，不通过运行 80 个完整 episodes 伪造预算证据。

## 4. 产物完整性与边界

新 synthetic/Mock 产物另做 raw-bytes 独立复算：64 episodes、194 个唯一 budget request IDs、64 traces，episode 身份、trace SHA/hash chain、请求池映射、pool ledgers、统计绑定和 artifact 清单全部 PASS。详见 `D094_R4_BLOCKER_FIX_REPORT.md` 与 `results/r4_synthetic_review_fix/verification_report.json`。

本报告不是独立审查结论。独立复审=`PENDING`；真实 R4=`NOT RUN`；最高流程状态仅为 `READY_FOR_INDEPENDENT_REVIEW`。
