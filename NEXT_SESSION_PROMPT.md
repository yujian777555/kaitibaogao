# 下一会话任务：D-094 R4 修复后独立只读复审

请在一个**新的独立会话**中执行 `D094.NEXT_SESSION_PROMPT.md` 和 `D094_R4_INDEPENDENT_REVIEW_PROMPT.md`。

唯一任务是复核 R4-001～R4-003 的修复、原预注册一致性、完整测试/CI、raw SHA 和真实 API=0，并明确输出 `ACCEPT` 或 `REQUEST_CHANGES`。不要修改代码、不要运行真实 R4、不要调用真实 LLM API。

代码提交和 CI 以 `D094_R4_STATUS.json` 为权威记录，最终文档 HEAD 需动态查询远端。当前最高状态只能是 `READY_FOR_INDEPENDENT_REVIEW`，独立复审尚未完成；即使 ACCEPT，也必须等待用户明确授权才能准备真实实验。

保护项 `experiments/pilot_a3b/confusion_report.json`、`I_need_interpret_use.txt`、`incoming/` 不得提交或清理。main 不得修改。旧 R4、R1/R2/R3.1 证据不得覆盖。
