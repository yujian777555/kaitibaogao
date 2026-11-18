# D-094 下一会话接管提示词

## 当前权威状态：R2 已结束，但 INVALID_BUDGET

唯一仓库：`yujian777555/kaitibaogao`；分支：`d094-llm-agent-integration`。开始前重新核验远端 HEAD、main、工作区和是否存在后台任务；不要重启 R2。

### 真实证据

- Canary：`deepseek-flash` PASS，3次真实LLM决策，inspect→verify→complete，Token1552/148，成本估算0.0006432 USD，硬约束0。证据=`results/canary_r1/`。
- Phase 2 R1：INVALID，B2未运行；永久保留在`results/phase2_r1/`。
- Phase 2 R2：1260/1260 episodes已写入，但成本1.0002363 USD超过1.00 USD，状态INVALID_BUDGET。
- R2真实API=3704次，Token=2600905/183304；原始请求记录3992，其中288条预算拒绝未发送。
- B0=36/36成功，B1=24/36；B2 final 36个 episodes全部LLM_ERROR且没有真实调用，不能用于性能比较。
- 搜索选中Genome `b5dbe97a0ff4bc9da85d2373b24427f027e4c026cd965003a6e1657d25618abe` 在搜索评价中36/36成功，但最终评价无效；当前创新判定=INVALID，不是POSITIVE_SIGNAL。
- 32个唯一搜索Genome对应24个 phenotype，无complete collapse；17/496对不同Genome行为相同。六类约束=invalid0、unauthorized420、illegal0、pending0、duplicate0、runtime_abort603。

### 必读文件

1. `D094_PHASE2_R2_RESULT.md`
2. `D094_R2_INDEPENDENT_AUDIT.md`
3. `D094_GENOME_PHENOTYPE_ANALYSIS.md`
4. `D094_NEXT_EXPERIMENT_PLAN.md`
5. `experiments/d094_llm_agent/results/phase2_r2/summary.json`、`independent_audit.json`、`analysis.json`

### 可复算命令

```bash
python experiments/d094_llm_agent/d094_phase2_audit.py \
  --outdir experiments/d094_llm_agent/results/phase2_r2
python experiments/d094_llm_agent/d094_analysis.py \
  --outdir experiments/d094_llm_agent/results/phase2_r2
python -m unittest discover -s experiments/d094_llm_agent -p "test_*.py" -q
```

审计为PASS_WITH_LIMITATIONS：Phase2 Runner未提供逐事件hash-chain；原始文件SHA已锁定。被拒绝重复proposal、每代survivor phenotype和实际mutated locus未完整记录，不能编造。

### 最终验证身份

完整本地回归595/595，D-094=53/53。代码/结果提交`17120fac98b4aa96a8b5f0cbf5a0d67c8f3d6dec`的CI run`44360886032`已completed/success，D-094日志53/53 OK；6个既有artifact均非D-094性能证据。后续纯文档提交无run时写NOT RUN。

### 下一任务

只推进`D094_NEXT_EXPERIMENT_PLAN.md`的R3独立审查/预算预检与实现准备；R3真实API实验当前NOT RUN。R3必须先预留B1和最终评价预算、禁止零调用final、补齐mutation/duplicate/survivor/hash-chain账本。模型继续`deepseek-flash`，不超过1500次真实HTTP/0.50 USD的R3上限，不扩大规模。

不得修改D-092/D-093或main，不删除R1/R2失败，不把Mock/缓存当真实API，不启动A800训练或Validation/Test。提交后核验本地/远端HEAD、main、工作区、测试、真实CI和artifact；纯文档无run时写NOT RUN。
