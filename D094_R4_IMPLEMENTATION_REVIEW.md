# D-094 R4 实现一致性自检

日期：2026-11-21。本文是实现者自检，**不是独立审查**。独立审查=`PENDING`，真实 R4=`NOT RUN`，`APPROVED_FOR_EXPERIMENT=NO`。

## 1. 交付范围

新增：

- `analyze_d094_r3_deep.py` 与只读 `results/r3_1_deep_analysis/analysis.json`；
- `d094_r4_credit.py`；
- `d094_r4_tasks.py`；
- `d094_r4_statistics.py`；
- `run_d094_r4.py`、`run_d094_r4_synthetic.py`；
- `test_d094_r3_deep.py`、`test_d094_r4_credit.py`、`test_d094_r4_protocol.py`；
- R4 preflight、synthetic/Mock 新结果目录和六份研究文档。

旧 `d094_adaptive_evolution.py`、R3 算法模块、R1/R2/R3.1 原始目录均未修改。受保护的 `confusion_report.json`、`I_need_interpret_use.txt`、`incoming/` 不纳入本轮实现。

## 2. 代码审查清单

| 项目 | 实现侧证据 | 自检 |
|---|---|---|
| 父子唯一配对 | `PairedEvaluation` 检查非空、唯一 task/seed；optimizer 检查冻结集合完全一致 | PASS |
| 约束优先 | `paired_unit_rewards` 先比较约束，再比较 Success/Recovery/Harm | PASS |
| 资源隔离 | 主信用只读取质量字段；resource-only 单元测试=0 | PASS |
| 滑窗/概率 | W=4、τ=0.25、ε=0.2、稳定 softmax、ε/6 探索下限 | PASS |
| 冷启动 | 空历史六算子各 1/6 | PASS |
| 更新时点 | variation 先保存概率；完整 child 后 credit update；后续 proposal 才可见 | PASS |
| duplicate | 无 evaluation、无 credit update，账本有独立终态 | PASS |
| 机制隔离 | B2 无 feedback/credit；B4 只有旧 feedback；B3 只有 paired credit | PASS |
| survivor 公平 | 三臂均 feasibility-first 标准 NSGA-II，无 diversity survivor | PASS |
| 初始种群 | 相同 216 池、search seed=711，三臂初始 hash 一致 | PASS |
| 评价公平 | 每臂 4 搜索候选×4 单元=16 episodes，无额外 B3 配对评价 | PASS |
| final | 全搜索 archive 的可行第一 front，字典序 tie-break，独立新 episodes | PASS |
| Fresh Train | 完整规格 SHA、与 18 个历史 Train 双向非重叠、无 held-out 读取 | PASS |
| 可达性 | 两任务×两 seeds 本地环境完成，3/4 步≤公共 5 步，API=0 | PASS |
| 预算 | 320/0.442368；B1/final 请求和成本独立预留 | PASS |
| 无效处理 | execution error、缺失配对、无可行 final、超预算、非 Mock 均拒绝 | PASS |
| 统计 | 16 个精确符号翻转、20,000 paired bootstrap、四比较 Holm | PASS |
| 审计 | evaluation/variation/credit/feedback/survivor/请求/trace 全账本 | PASS |

## 3. 测试证据

实际已执行：

- R4 算法/任务：17/17；
- R4 预算/统计/Mock 协议：7/7；
- R3.1 深度分析：5/5；
- 当前 D-094 全量 discover：**135/135 OK**（原有 106+新增 29）。

覆盖边界包括：约束改善/回归、质量支配和 trade-off、资源-only=0、缺失配对、execution error、冷启动、探索下限、滑窗、duplicate、无未来信息、初始种群/评价数公平、可复现性、五步不变、全 archive Pareto/final、manifest hash、历史 Train 隔离、可达性、预算精确值、预检零 client、非 Mock 拒绝、64 episode 全链、final 独立 ID、统计固定种子及 Holm。

最终收尾实测：完整七目录回归 **677/677 OK**（28+398+8+8+14+86+135）；`compileall`与`git diff --check`通过。最新预检/合成产物在最后一次锁定源码及四份协议文档修改后重建；81个合成产物SHA全部匹配，执行锁内15个源码文件和4份协议文档SHA全部匹配，R3.1源目录56个文件仍与深度分析快照一致。budget plan raw SHA=`21b80255516645fdbdf63f5063dbed0b528b4aaf97da4ca52fa1cea3e28ba150`。提交后的新CI须按新HEAD实际查询，不沿用历史run，也不以本地测试代替远端结果。

## 4. 合成与 Mock 结果

- `results/r4_synthetic/summary.json`：`SYNTHETIC_VALIDATED`，13 个 gate 全 true，`real_llm_calls=0`。
- 正式一代 fixture：三臂初始种群相同、各 4 次评价；B3 有 2 次 credit update。
- 一代 fixture 的首个 offspring reward=0，第二次概率仍均匀；第二个非零 update 位于最后提案后。该边界未被隐藏。
- 额外两代**纯合成诊断**证明非零信用影响后续 proposal；它不是正式 R4 增加的一代，也不是性能实验。
- Mock 协议 64 episodes、194 Mock 请求、成本上界约 0.0015132 USD，预算/hash-chain/独立 final 通过。
- Mock 统计文件仅检验统计实现，所有数值禁止作为真实 Agent 结果。

## 5. 预检与安全边界

`run_d094_r4.py` 默认只做 preflight；只有显式 Python 调用并传入 Mock factory 才能执行协议。非 Mock backend 会在 episodes 文件创建前被拒绝；没有 `--execute-real` 参数，不读取真实环境配置。

`results/r4_preflight` 实际为 0 episode、0 API。未来真实执行需要独立审查后增加/复核入口，并再次验证模型、价格、执行锁、任务 hash、预算和授权。

## 6. 已知限制与独立审查重点

1. 当前没有真实 R4 执行入口，不能宣称“已获真实实验准备批准”。
2. 四个 final 配对单元和一代两个 offspring 只能支持探索性机制证据。
3. Fresh Train 只证明与历史 Train 的 ID/完整规格不重叠；held-out 语义重叠未检查，且禁止访问。
4. 公共可达性仅证明路径存在，不证明真实 LLM 会采取路径。
5. R3.1 canonical message bytes 不可恢复，预算文档只使用实际 token 分布和冻结 byte cap。
6. 请独立复核 parent 第一父代定义、每单元与均值奖励、软最大数值稳定、反馈对照是否保持旧语义、ledger 时序、预算并发、统计排序和 final 全档案选择。

## 7. 自检结论

实现侧满足提交独立审查的条件：

`R4_IMPLEMENTED + R4_SYNTHETIC_VALIDATED + R4_PREREGISTERED → R4_READY_FOR_INDEPENDENT_REVIEW`。

独立审查尚未完成；不得由本文自行宣告 `APPROVED_FOR_EXPERIMENT`。
