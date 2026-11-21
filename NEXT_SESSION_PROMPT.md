# D-094 下一会话接管提示词：R4 独立只读审查

## 唯一任务

请在**新的独立会话**中，严格按照 `D094.NEXT_SESSION_PROMPT.md` 审查已经冻结的 R4 算法、实现、Fresh Train、预算、统计、final、执行锁和产物。不要继续起草另一套方案，不要运行真实 R4。

## 当前状态

- R3.1=`COMPLETED / NO_CLEAR_GAIN`，历史结果不得修改。
- R4=`R4_READY_FOR_INDEPENDENT_REVIEW`。
- 预检=`PREFLIGHT_PASS`，0 episode、0 API。
- 合成/Mock=`SYNTHETIC_VALIDATED`，13项门禁全通过，真实LLM调用0。
- D-094=135/135；七目录全量回归=677/677。
- 独立审查=`PENDING`；真实R4=`NOT RUN`；真实API=0；`APPROVED_FOR_EXPERIMENT=NO`。

## 必读文件

1. `D094_R3_1_DEEP_ANALYSIS.md`
2. `D094_R4_ALGORITHM_DESIGN.md`
3. `D094_R4_PREREGISTRATION.md`
4. `D094_R4_BUDGET_ANALYSIS.md`
5. `D094_R4_IMPLEMENTATION_REVIEW.md`
6. `D094.NEXT_SESSION_PROMPT.md`
7. `experiments/d094_llm_agent/results/r4_preflight/execution_lock.json`
8. `experiments/d094_llm_agent/results/r4_synthetic/summary.json`

## 不可越过的边界

- 动态fetch并核验最新远端HEAD、main、ahead/behind和工作区，不把交接中的历史SHA当作最新值。
- 不修改main、D-092/D-093、R1/R2/R3.1原始结果或本轮冻结协议；不读取Validation/Test，不运行模型训练。
- 不调用真实API，不新增或启用真实执行入口，不覆盖既有预检/合成产物。
- 审查者不得把实现者自检当作独立证据；发现问题应给出`REQUEST_CHANGES`及可复现定位，而不是在审查中暗中修复。
- 即使独立审查通过，也只能进入等待用户明确授权的状态，不能自行宣告`APPROVED_FOR_EXPERIMENT`。

完整审查项目、公式和交付格式以 `D094.NEXT_SESSION_PROMPT.md` 为准。
