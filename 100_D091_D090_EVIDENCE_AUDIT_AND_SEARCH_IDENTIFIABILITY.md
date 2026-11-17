# D-091：D-090 证据独立审计与搜索可辨识性检查

## 0.1 D-091 静态预审新增发现

在撰写本轮详细执行提示词时，对 D-090 源码及两个原始 JSON blob 做了额外静态审计。以下为必须在本地独立复现的高优先级发现：

1. `d090_experiment.py::run_method()` 没有 `method == "random"` 的独立分支。`random` 与 `nsga2` 均进入同一演化分支，使用相同 seed RNG、初始种群、默认变异/交叉和 `nsga2_select`；保存的三个 paired seeds 中两者 best genome 完全相同。因此当前 Random Search 标签无效，不能作为 NSGA-II 的独立随机基线。
2. `state_evo` 传入固定 mutation profile `{"pair":1,"fallback":1,"completion":1,"harm":1}`，不是由实际 episode 状态或失败反馈动态更新；`state_random` 才是规则基因空间直接随机采样。必须重命名/重新界定方法身份，不能把静态加权称为动态状态反馈。
3. `GENERATIONS=6` 只写入 report metadata；`run_method()` 的 while loop 按 unique eval budget 终止，未使用 GENERATIONS。真实 generation 数、proposal 数、cache hits 是否可复原必须审计。
4. 对保存的 `d090_train_report.json` 解析得到 15 个 run、8 个不同 best genome，但所有 15 个 best candidates 在 96 个 D-090 Train scenarios 上的 trace bundle 完全一致（105/105 两两相同）；所有逐场景 outcome signature 也相同。这是当前 manifest 上的 phenotype collapse 信号，不可外推到其他环境。
5. 两个既有 g03 audit 脚本分别读取 D-089 的 `g03_PAIR_RACE` repeat 0 和 D-089 `d089_search_report.json`，不是 D-090 的 `d090_PAIR_RACE` repeat 2，故不能支持 D-090 r2 的 25 步下界。
6. `objectives()` 使用 6 维目标，但 `_best()` 在整个 archive 上以 `min(R3,R4), R3+R4, -Harm, -RecoveryCost` 做统一 lexicographic selection；没有显式纳入 cond_rec，也不是直接从 final NSGA population/Pareto front 选候选。需审计此口径与多目标声明的一致性。

### r2 反例待验证

D-090 `d090_PAIR_RACE / D3_DEPENDENT_ABORT / repeat=2` 的定义支持一个待执行的 23-step witness：每轮同时 dispatch A-alternate、B-alternate、C-primary（第三轮只 dispatch A/B）；每轮 WAIT 两次后分别 VERIFY；三轮完成后 ESCALATE。A/B alternate outcomes 为 `[False,False,True]`、delay=2；C primary outcomes 为 `[False,True]`、delay=1。按动作计数 8+8+6+1=23。`WAIT` 推进全局 tick，因此多个 pending receipt 可以共享时间推进。必须用真实环境回放并用 BFS/DP 求最短路径；在执行前不得直接宣称 25 步下界已被推翻。

完整执行要求见 `101_D091_EXECUTOR_PROMPT.md`。

日期：2026-11-16
仓库：`yujian777555/kaitibaogao`
分支：`pilot-a-stateful-recovery`
状态：待执行；TRAIN-ONLY；审计优先，不启动 Validation/Test

## 1. 接管基线与 D-090 事实

- D-090 实验报告：`99_D090_PAIR_RACE_RULE_SEARCH.md`。
- 已知提交：`1af9bc832058dd1328862dbba3da3ef248e4edd3`。
- CI run：`43881534809`，regression job success；`Test d090_recovery` step success。
- D-090 新增 `d090r|train|` 命名空间、6 个 family、96 个 Train-only 场景。
- 固定消融：Legacy B3=(R3 .500,R4 1.000,Harm .271,violations 0)；P1=(.708,.917,.479,0)；P2=(.667,1.000,.146,2)；P3=(.583,1.000,.229,0)；P4=(.417,1.000,.313,2)。
- 五种搜索方法的汇总结果均为 R3=.875、R4=1.000、Harm=.042、硬约束违规=0；每种方法报告 96 次唯一 genome 评价、3 个配对 seeds。
- g03 的 A/B 形成公开互依环，C 独立；r2 在 24 步合同下有 25 步公开下界的报告结论。
- 没有冻结候选，没有申请独立 Validation。SSH 主机 30939/30522 握手被关闭；没有启动 A800 或模型训练。

注意：固定机制消融和搜索得到的 best-genome 汇总是不同实验，必须分别报告。不得把五种搜索方法指标相同写成演化优势。D-090 结果是 Train-only 探索信号，不是独立验证。

## 2. D-091 唯一目标

在任何新搜索之前，独立审计 D-090 的原始数据、指标、算法身份、搜索可辨识性和 r2 可行性下界。判断五种搜索方法完全相同究竟来自：

1. 相同 genome 被不同方法选中；
2. genome 不同但规则/行为 phenotype 等价；
3. 指标离散或汇总舍入造成表面相同；
4. 选择/变异/交叉/环境选择实现或调用路径未真正区分算法；
5. 搜索空间中存在较大的性能平台，当前预算下各方法均能到达。

不得预先假定其中任何一种解释成立。

## 3. Task A：原始账本与指标独立复算

- 枚举 `experiments/d090_recovery/results/` 下全部 JSON/JSONL/CSV、manifest、配置、日志和摘要；不得覆盖或改写原始文件。
- 为每个文件生成 SHA-256、字节数、行数、schema、唯一键、空值与重复记录报告。
- 逐项核对 6 families、96 scenarios、`d090r|train|` namespace、split 标签和 scenario ID 唯一性。
- 核实 5 方法 × 3 paired seeds × 96 次唯一 genome 评价的准确计数口径；区分 genome evaluation、episode rollout、scenario row、cache hit 和重复调用。
- 从逐场景原始记录独立重算 R3、R4、Harm、ConstraintViolation、PendingCompensation、DuplicateCompensation、UnauthorizedAction、RecoveryCost；报告分子、分母、未定义值和舍入规则。
- 逐 seed、逐 family、逐 scenario 输出指标，不只复算最终平均值。
- 核实每个 best genome 是否在相同 96 场景上评估；检查候选选择是否只使用 Train 数据。

## 4. Task B：五种搜索方法的可辨识性审计

逐方法审计 Random Search、NSGA-II、NSGA-III、State-Conditioned Evolution、State-Conditioned Random Search：

- 每个 seed 的初始种群、候选生成、unique genome 数、cache/dedup、fitness calls 和选择记录。
- NSGA-II/III 是否分别执行了正确的非支配排序、拥挤距离/参考方向 niching 与生存者选择；不得只凭方法名称认定实现正确。
- State-Conditioned Evolution 是否真实执行条件规则块变异、交叉、修复和选择；State-Conditioned Random 是否保持相同编码、初始化信息与评价预算。
- 统计各方法 operator invocation、有效变异率、子代与父代差异、候选保留率、front/rank 分布、种群多样性和 phenotype 重复率。
- 对每个候选计算 canonical genome hash、规范化规则签名和行为指纹；构建跨方法/跨 seed 的精确重复与 phenotype 等价矩阵。
- 检查五方法指标相同是逐 seed 完全相同，还是仅均值/舍入后相同；报告未舍入值、置信区间和逐场景配对差异。
- 排查 fitness tie、目标离散化、lexicographic tie-break、共同缓存、共享初始池、错误的 best-candidate 选择及方法分支意外共用实现。

输出明确结论：`SAME_GENOME`、`PHENOTYPE_EQUIVALENCE`、`AGGREGATION_COLLISION`、`IMPLEMENTATION_COLLAPSE`、`SEARCH_PLATEAU` 或组合结论；必须由数据支持。

## 5. Task C：g03 r2 的 25 步下界证明

- 从原始状态转移代码与 r2 逐动作轨迹重建公开状态图。
- 对 A↔B 互依、C 独立、三工具延迟回执和失败/失败/成功序列，列出每个必要补偿、等待、确认及 ESCALATE 动作。
- 用独立枚举或最短路/动态规划计算在当前动作语义下达到协议目标的最小决策数。
- 审计是否允许合法并行、合并确认、提前确认、幂等复用或其他可减少动作数的路径；不得忽略环境合同中的限制。
- 证明 25 是严格下界而非某一策略的实际路径长度；如果存在 24 步可行路径，必须撤回下界结论。
- 在 D-090 原始指标中保留 r2 原始标签和分母。不得事后删除 r2、改写 R3 标签或改变 24 步预算来美化 D-090。
- 若下界成立，将该案例标注为 `INFEASIBLE_WITHIN_24_STEP_CONTRACT` 的诊断事实；是否在未来新 Train manifest 中加入可行性分层，另行预注册。

## 6. Task D：P1/P2 的安全与权衡复核

- P1 的 g03 局部改善必须与 R3/R4/Harm 全局代价同时呈现；不得仅报告 g03。
- P2 的 2 个硬约束违规和 4 个 pending 必须定位到具体轨迹、动作与门控缺口；P2 不得成为候选。
- 对 P3/P4 说明实际无效或退化机制，不为消融结果事后补造解释。
- 所有硬约束保持硬门禁；Harm 不能替代或抵消硬约束违规。

## 7. CI 与可复现证据

- 现有 run `43881534809` 已确认 regression job success，`Test d090_recovery` step success。
- 该 run 的已列 artifacts 不含 D-090 专属结果包；不能声称 CI 已独立复算 D-090 实验账本。
- 为 D-091 增加只读审计脚本/测试：从已保存的 D-090 原始账本重算，不重新执行搜索、不改变原始数据。
- 生成专属审计 artifact，包含原始文件 manifest、独立复算 JSON/CSV、候选指纹矩阵、下界证明和审计报告；artifact SHA-256 必须写回仓库。
- 如果原始账本未在远端提交或不完整，明确记录缺失；不得从摘要数字伪造原始数据。

## 8. D-091 允许与禁止

允许：只读审计、独立复算、审计脚本、回归测试、文档维护、Train-only 机制设计。

禁止：新 genome 搜索、调参、候选冻结、独立 Validation、正式 Test、Pilot B、正式 A-3b、真实 LLM API、A800/ARWM 训练、UndoBench TEST、ThinkingBox、修改 main 或覆盖 D-090 历史数据。

## 9. D-091 交付与决策

必须回答：

1. D-090 原始数据是否完整、哈希可核验、指标可独立复算？
2. 五种方法结果相同的真实原因是什么？
3. 各方法实现是否真正不同且预算公平？
4. 是否存在 phenotype collapse 或搜索平台？
5. r2 的 25 步下界是否被严格证明？
6. P1/P2 的行为级问题是否定位？
7. 是否存在可冻结候选？当前默认答案为否，除非原始证据足以改变判断。
8. 下一轮最值得验证的单一机制是什么？

D-091 完成后，提出 D-092 的 Train-only 预注册方案，优先研究“Pair-aware completion + delayed-confirmation budget reservation + hard pending gate”的联合策略；不得在 D-091 审计未完成前启动。若证据显示当前规则空间存在大规模 phenotype 等价，先压缩冗余规则表示并设计行为多样性指标，再决定是否运行演化搜索。

## 10. 仓库维护

唯一仓库 `yujian777555/kaitibaogao`，唯一工作分支 `pilot-a-stateful-recovery`。保持 main 不变。更新 `README.md`、`SESSION_HANDOFF.md`、`NEXT_SESSION_PROMPT.md`、`05_DECISION_LOG.md`、`51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md`。提交后核验远端 SHA、分支、main、工作区与 CI；文档更新不等于实验通过。