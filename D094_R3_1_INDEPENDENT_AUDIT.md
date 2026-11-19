# D-094 R3.1 独立复算与审查记录

日期：2026-11-19
对象：`experiments/d094_llm_agent/results/r3_1_real/`
复算结论：`PASS`
算法结论：`NO_CLEAR_GAIN`

## 1. 审查层级必须区分

1. **执行前独立实现审查**：独立 reviewer `agent-0` 对修复后的 R3.1 实现给出 `ACCEPT_WITH_LIMITATIONS`，未发现算法归因、预算或 Train 数据隔离阻断。该结论只允许按冻结门禁执行，不是性能认可。 reviewer 未实际运行的验收测试随后由实现侧补齐，并通过完整回归。
2. **执行后独立程序复算**：`audit_d094_r3.py` 从保存的原始 episodes、trace 和请求账本重新计算，不读取 Runner 的运行时内存、不调用真实 API。本文件记录该复算；它不是对实验后报告的另一轮人工独立同行评审。
3. **科学判断**：复算 PASS 只证明保存数据、汇总和冻结判据一致。单 Train 任务×2 seeds 的冒烟结果不能证明普遍提升或创新。

## 2. 实际复算范围

审计器独立覆盖：

- 42 个 episode 的身份、Train-only 任务、seed、phase、agent 状态及 summary 数量；
- 42 份 trace 的文件 SHA-256、逐事件序号、前序哈希与事件哈希；
- 公开行为序列、特征、episode/candidate phenotype 和行为多样性；
- 七类失败计数、分母、比率及反馈记录；
- 169 条真实请求、唯一 provider request ID、tokens、成本、预留与结算；
- B1、搜索及四个 final 预算池，预算拒绝、未知成本、超预留和超预算；
- 四个演化臂的 Genome、评价目标、Pareto front、final 选择；
- 总体与逐 seed 比较，以及 summary 全字段一致性；
- 执行锁、预算计划和正式 artifact 的 SHA-256。

执行命令：

```bash
cd experiments/d094_llm_agent
py -3.10 audit_d094_r3.py results/r3_1_real
```

实际输出：

```json
{"status":"PASS","episodes":42,"requests":169,"input_tokens":127148,"output_tokens":8090,"cost_usd":0.0478524}
```

## 3. 关键身份与复算数值

| 项目 | 复算结果 |
|---|---|
| 状态 / 协议 | `COMPLETED` / `D094_R3.1_TRAIN` |
| Episodes | 42/42，全部 Train |
| 唯一任务 | `d094_r3_train_compensation_0` |
| Seeds / search seed | 201、202 / 711 |
| 真实 HTTP / 唯一 provider ID | 169 / 169 |
| 输入 / 输出 tokens | 127,148 / 8,090 |
| Token 成本与上界 | 0.0478524 / 0.0478524 USD |
| 请求 / 成本上限 | 1,500 / 0.50 USD |
| 预算拒绝 / 执行错误 / 未知成本 | 0 / 0 / 0 |
| 超预算 / 超预留 / pending 成本 | 否 / 否 / 0 |
| Hash-chain | 42/42 有效 |
| Summary 与原始账本 | 一致 |

关键 SHA-256：

- `episodes.jsonl`：`f1ded96d3b1b8207e8a132a20d905a5d36286e54751334eeb81bbd1b15fc9f7e`
- `summary.json`：`4e0f555842f5a4904b54363e3383adff6bad5535aafaaf8636ba9172424576ad`
- `execution_lock.json`：`1853c31b9607f613ef7469a897271d22332c4fc3fc4881768419e5c003e3697b`
- `budget_plan.json`：`6d7c6b5fece5db7a20fbc0f48b508250d6055f18096ddfd37cc0fb2b8411dc86`

`independent_audit.json` 的 `artifact_sha256` 还保存四个 archive、四个 evolution、42 份 trace、manifest 等全部正式文件身份。

## 4. 审计器验收与反篡改测试

实际执行：

```bash
py -3.10 -m unittest test_d094_r3_audit -v
```

结果为 **3/3 OK**：

1. Mock 五臂 42 episodes 可完整重算，summary 与原始账本一致；
2. 修改 trace rationale 后被 trace SHA-256 检查拒绝；
3. 修改请求成本后被 provider Token 定价复算拒绝。

这些 Mock 仅用于审计器测试，不进入真实 R3.1 结果。真实 R3.1 只执行一次；本次收尾没有再次调用真实 API 或重跑实验。

## 5. 对算法结论的独立支持

复算确认四个演化臂 final Success/Recovery 均为 0，四个预注册比较在总体和两个 seeds 上的成功率差均为 0。搜索唯一 Genome 均为 4；唯一 Phenotype 为 B2=2、B3=3、B4=2、B5=3。final 公开动作序列在四个演化臂间相同，均为 inspect→verify→retry 后 `MAX_STEPS`。

所以审计支持 `NO_CLEAR_GAIN`，不支持把反馈引起的搜索期行为变化写成任务性能收益，也不支持 B4 多样性收益或 B5 协同结论。

## 6. 限制与后续边界

- 该实验只有 1 个 Train 任务、2 seeds、1 代和 population=2；不是确认性统计实验。
- final 仍在同一 Train 任务上，不是独立泛化或 Validation/Test。
- 本次复算不证明搜索过程在全球意义最优，也不证明失败只有单一因果来源；只确认直接轨迹终止机制和账本一致性。
- 不修改 R1/R2、D-092/D-093 或 main；不运行 Validation/Test、外部模型训练或 A800。
- 后续只能新建 R4 fresh Train 预注册；不得用重复真实运行、换 seed 或扩大预算掩盖本轮负结果。
