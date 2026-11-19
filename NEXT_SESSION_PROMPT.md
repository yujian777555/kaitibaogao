# D-094 下一会话接管提示词：R3.1 已完成，下一步仅起草 R4

## 1. 仓库与不可变边界

- 唯一仓库：`yujian777555/kaitibaogao`；唯一工作分支：`d094-llm-agent-integration`。
- 本轮起始HEAD=`6c084d2fd2617a19e52a9879b14670440bcde777`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。接手时动态fetch并核验最新远端HEAD、main、ahead/behind、工作区和真实CI，不把历史SHA当最新值。
- 不得修改main、D-092/D-093、R1/R2或R3.1历史证据；不得删除负结果、换seed或补预算追求提升。
- Validation/Test、A800、外部模型训练未授权。不得自动执行任何真实API实验。

## 2. 已完成的实际工作

1. R3.1统一五臂Runner、真实/Mock客户端、请求前预算预留/结算、执行锁、逐事件hash-chain、完整演化和请求账本已经实现。
2. 独立实现reviewer `agent-0`给出`ACCEPT_WITH_LIMITATIONS`；其未执行的验收测试已补齐。原六任务R3因保守预算超限被阻断，R3.1缩小设计预检通过，预检无真实请求。
3. 真实R3.1只运行一次，目录=`experiments/d094_llm_agent/results/r3_1_real/`，状态`COMPLETED`：42/42 Train episodes、169真实HTTP/169唯一provider ID、127148/8090 tokens、0.0478524 USD；无预算拒绝、执行错误、未知成本或超预算。
4. 独立审计器`audit_d094_r3.py`复算真实目录为PASS；3项审计测试通过，包括完整Mock复算、trace篡改和成本篡改检测。Mock仅作测试，不是正式结果。
5. 最终实测D-094=106/106；按CI七个目录完整回归648/648（28+398+8+8+14+86+106）。根目录`unittest discover -s .`得到0 tests，不得作为通过证据。

## 3. 权威结果与科学结论

先读：

- `D094_R3_1_RESULT.md`
- `D094_R3_1_INDEPENDENT_AUDIT.md`
- `experiments/d094_llm_agent/results/r3_1_real/summary.json`
- `experiments/d094_llm_agent/results/r3_1_real/independent_audit.json`
- `D094_NEXT_EXPERIMENT_PLAN.md`

实际结果：

- B1 fixed Task/Recovery Success=1.0/1.0；B2/B3/B4/B5 final均为0.0/0.0。
- B3−B2、B4−B2、B5−B3、B5−B4的总体与seed201/202成功率差全部为0。
- 搜索唯一Genome均为4；唯一Phenotype为B2=2、B3=3、B4=2、B5=3；population behavior diversity=0.50/0.75/0.50/0.75；无complete collapse。
- Pareto front大小=2/2/3/1；B2/B4选择`caff90af…ee07dbc1`，B3/B5选择`aa0d3b4a…fd04973`。
- 最终8个演化episodes均inspect→verify→retry，retry失败后触及`max_plan_steps=3`，未补偿/完成，以MAX_STEPS终止；不是提前finish、预算、传输或Schema失败。
- B1的2/2与演化0/2不能作单因素因果解释，因为Genome、步数和恢复策略同时不同，且只有单Train任务×2 seeds。

**结论只能是`NO_CLEAR_GAIN`，不是`POSITIVE_SIGNAL`。** B3/B5的搜索Phenotype增加只是机制信号；B4没有相对B2提高多样性，B5没有证明协同。不得宣称性能提升或毕业论文创新已经成立。

## 4. 唯一下一任务：起草 R4，不执行

在`D094_NEXT_EXPERIMENT_PLAN.md`基础上形成新的R4 fresh Train预注册，执行前必须完成独立审查和明确授权：

1. 保留R3.1只读轨迹归因，不再次调用真实API；新Train manifest不得读取Validation/Test。
2. 在首个请求前冻结动作可达性证明，确保retry失败后补偿/完成所需动作与步数上限相容；不能事后单独提高步数制造改善。
3. 研究质量约束、状态条件化的行为多样性：无质量/不可行行为不能靠无意义新颖性获益，距离需比较相同公开状态下的后续行为。
4. 研究同父代、同任务、同seed配对offspring改进驱动的在线算子信用；与静态反馈、均匀算子、标准NSGA-II等预算比较，配对评价成本必须公平入账。
5. 冻结seeds、任务、种群、代数、预算、final规则、主要终点、统计边界和停止条件；保存完整原始账本并独立复算。
6. 不简单扩大预算、种群或代数；任何INVALID/超预算/final缺失均保留，不删除不利结果。

## 5. 安全的只读复算与测试命令

```bash
cd experiments/d094_llm_agent
py -3.10 audit_d094_r3.py results/r3_1_real
py -3.10 -m unittest discover -s . -p "test_*.py"
```

全量回归必须逐目录执行：

```bash
py -3.10 -m unittest discover -s experiments/pilot_a_recovery -p "test_*.py"
py -3.10 -m unittest discover -s experiments/pilot_a3b -p "test_*.py"
py -3.10 -m unittest discover -s experiments/d088_recovery -p "test_*.py"
py -3.10 -m unittest discover -s experiments/d089_recovery -p "test_*.py"
py -3.10 -m unittest discover -s experiments/d090_recovery -p "test_*.py"
py -3.10 -m unittest discover -s experiments/d092_recovery -p "test_*.py"
py -3.10 -m unittest discover -s experiments/d094_llm_agent -p "test_*.py"
```

不要运行`run_d094_r3.py --execute-real`。每轮更新README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG和实验计划；提交后核验真实远端HEAD/main/worktree/CI，无run则写NOT RUN。
