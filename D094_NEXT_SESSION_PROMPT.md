# D-094 下一会话接管提示词：R3 独立实现一致性复核

## 当前状态

- 仓库：`yujian777555/kaitibaogao`；分支：`d094-llm-agent-integration`。先核验远端最新 HEAD、main、工作区和后台任务。
- R1/R2 INVALID 及原始账本均保留；不得重启或覆盖。
- B4 行为感知 NSGA-II、B3 失败反馈、B5 组合及请求前预算预留已实现，并有合成证据。
- D-094 测试=82/82；合成 CLI 已生成 `results/r3_synthetic/`。
- **R3 NOT RUN；INDEPENDENT_REVIEWED=NO；APPROVED_FOR_EXPERIMENT=NO；POSITIVE_SIGNAL=NO。**

## 本轮算法入口

- `D094_DIVERSITY_AWARE_NSGA2.md` + `d094_behavior.py` + `d094_diversity.py`：编辑/特征距离、最近邻新颖性、crowding+novelty、重复 phenotype 控制。
- `D094_FAILURE_FEEDBACK_EVOLUTION.md` + `d094_feedback_evolution.py`：七类失败、归一化矩阵、β=2、τ=0.25、ε=0.1、六算子。
- `d094_adaptive_evolution.py`：B2 standard、B3 feedback、B4 diversity、B5 combined；记录 mutation locus、duplicate、survivor 和三种多样性。
- `d094_budget.py`：请求前成本预留、B1/final 池保护、实际结算和失败上界。
- `D094_R3_PREREGISTRATION.md`：6任务、seeds201/202、每臂4+1代、1500 HTTP/0.50 USD 上限。

## 合成结果不能误读

专用选择器 fixture：Standard 唯一 phenotype=1，Full B4=2，平均行为距离0→1。演化 fixture：Standard/B4 最后一代 phenotype diversity 均0.75，B5=0.50；所有臂均8次评价。没有证明搜索效率、Pareto 或真实性能改善。

Phenotype 只能在真实评价后获得，不能宣称 B4 免费减少初始评价成本。R2 的36/36搜索候选仍未被有效最终验证，不得转为提升结论。

## 新独立会话的复核任务

1. 阅读 `D094_R3_IMPLEMENTATION_REVIEW.md` 及上述公式/代码，不把起草者自检当作独立通过。
2. 对照真实 R2 原始 JSONL，确认历史证据未被修改。
3. 检查行为表示是否排除 rationale/Token/隐藏信息，编辑距离和特征距离是否独立重算。
4. 检查 Pareto/硬约束是否始终优先，零名额/重复/无可行候选是否正确。
5. 检查失败分类分母、零反馈、softmax、随机控制和更新时点。
6. 检查 B3/B4/B5 是否只改变各自机制，RNG/评价是否公平。
7. 检查预算预留是否在请求前、搜索是否不能动用 final 池、失败/重试是否计费。
8. 运行测试和合成 CLI，审查 R3 预算是否真的能覆盖444个设计 episodes；不可行则阻断，不得擅自提高预算。
9. 分别给出 B3/B4/B5 的实现一致性结论与必须修复项。

只有独立复核通过且用户明确批准，才可运行真实 R3。不得由本起草会话自行批准。

## 已核验的测试与 CI

完整回归624/624，D-094=82/82。代码提交`da509c5ad9b9fbaf1796809eb5d4e43143b9fc98`的CI run`44531813596`已completed/success，D-094日志82/82 OK；6个既有artifact均非D-094性能证据。后续纯文档提交无run时写NOT RUN。

## 验证命令

```bash
python -m unittest discover -s experiments/d094_llm_agent -p "test_*.py" -q
python experiments/d094_llm_agent/run_d094_synthetic.py \
  --outdir experiments/d094_llm_agent/results/r3_synthetic_review
```

不得修改 D-092/D-093/main，不删除 R1/R2，不把 Mock/缓存/合成结果当真实 API 性能，不启动 A800 或 Validation/Test。提交后核验远端 HEAD/main/worktree、文件 SHA、真实 CI 和 artifact；无 run 写 NOT RUN。
