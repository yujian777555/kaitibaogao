# D-094 R4 修复后独立只读复审提示词

## 唯一任务

请在**新的独立会话**中，对 D-094 R4-001～R4-003 的修复和原 R4 审查项进行只读复审，最后只能给出 `ACCEPT` 或 `REQUEST_CHANGES`。不要继续实现、不要暗中修复、不要运行真实 R4、不要调用真实 LLM API。

当前目标状态为 `READY_FOR_INDEPENDENT_REVIEW`；独立复审=`PENDING`；真实 R4=`NOT RUN`；真实 API=0；`APPROVED_FOR_EXPERIMENT=NO`。即使 ACCEPT，也必须报告结果并等待用户明确授权。

## 1. 动态核验基线

1. 仓库只允许 `yujian777555/kaitibaogao`，分支 `d094-llm-agent-integration`。
2. 动态查询远端 HEAD 和 main；代码提交与 CI 的权威记录见 `D094_R4_STATUS.json`，文档 HEAD 不可由该文件自嵌套，不要沿用旧交接 SHA。
3. 接管基线为 `d1351297e700130ac7fc117868d86ba3a7b852ef`，main 应为 `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。
4. 检查工作区保护项 `experiments/pilot_a3b/confusion_report.json`、`I_need_interpret_use.txt`、`incoming/` 未被提交或清理。
5. 原审查 `D094_R4_INDEPENDENT_REVIEW.md` 的 SHA=`f91acb68d3c8596bc11484f5efc9a5d0da23604eb00ec49a1f6bcb39b4e33056`，结论 REQUEST_CHANGES。不要把实现者报告当独立证据。

## 2. 必读材料

- `D094_R4_PREREGISTRATION.md`、`D094_R4_ALGORITHM_DESIGN.md`、`D094_R4_BUDGET_ANALYSIS.md`
- `D094_R4_INDEPENDENT_REVIEW.md`
- `D094_R4_BLOCKER_FIX_REPORT.md`、`D094_R4_TAMPER_TEST_REPORT.md`、`D094_R4_STATUS.json`
- `run_d094_r4.py`、`d094_budget.py`、`d094_r4_statistics.py`、`d094_r4_analysis.py`
- `test_d094_r4_review_fixes.py`、`test_d094_r4_protocol.py`、`test_d094_budget_reservation.py`
- 新 `results/r4_preflight_review_fix/` 与 `results/r4_synthetic_review_fix/`；旧目录只作历史对照

## 3. 必须独立复现的审查项

### R4-001

- 检查完整字段值和类型验证是否发生在 outdir、client、episode、HTTP 之前。
- 重现 seeds/search seed/88 episodes/440 requests/0.608256 USD/model/task IDs/arms 等反例；合法配置仍通过。
- 确认两个任务、301/302、search seed 711、公共五步、64 episodes、320 requests、0.442368 USD 和 B1/final 分配没有变化。

### R4-002

- 检查 V2 锁是否含 17 个源码、统计方法版本和参数，并覆盖统计源码与最终分析入口。
- 在临时副本分别篡改符号翻转、bootstrap、Holm、最终分析入口，确认 `verify_execution_lock` 失败；不得修改生产源码。
- 重算 statistical analysis 的 execution lock raw SHA、manifest SHA、统计源码 SHA、分析入口 SHA。
- 确认 4 个 final 配对单元与 16 个符号模式没有混淆，四比较 Holm 和探索性解释未改。

### R4-003

- 检查 search:B2/B3/B4 是否各 80 requests/0.110592 USD，B1/final 是否各 20/0.027648，搜索是否不能消费 final。
- 直接以计数 Mock transport 重现三个臂各自第 81 次请求前拒绝、跨臂不可借用、全局 cap、重试、异常和 unknown usage。
- 核对新 summary 的 per-pool 请求、成本上界、剩余量和 pending 是否能从原始请求账本重算。

## 4. 测试、CI 和产物

- 运行新增测试、R4 测试、D-094 discover；实际期望分别为 15、22、150，但必须按输出核实。
- 阅读最终代码提交的 CI run 和 regression job 原始日志，分别核实七目录计数。实现者本地 Python 3.12.16 的 pilot_a3b 有两项历史浮点严格断言失败（690/692）；不得隐瞒，也不得据此擅自修改历史实验。CI Python 3.11.9 是否通过必须以真实日志为准。
- Black 本地不可用；compileall 与 diff check 已执行。不要伪报 Black 成功。
- 独立按 raw bytes 重算源码、文档、manifest、budget、execution lock、episode/request/trace、statistical analysis 和 artifact SHA。旧 preflight/synthetic 不得覆盖。
- 确认所有真实 API 指标均为 0，Mock 统计只作软件 fixture，不能形成真实性能结论。

## 5. 输出格式

给出：审查 HEAD、main、工作区、三项阻断逐项 PASS/FAIL、原审查项是否回归、复现命令与计数、CI run/job 证据、raw SHA 复核、真实 API=0、剩余限制。

最后明确一行：`ACCEPT` 或 `REQUEST_CHANGES`。若 REQUEST_CHANGES，提供文件/函数/反例和最小修复要求。无论结果如何，不得自行启动真实 R4 或写成 `APPROVED_FOR_EXPERIMENT`。
