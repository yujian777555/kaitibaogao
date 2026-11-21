# D-094 R4 Fresh Train 预注册

冻结日期：2026-11-21。状态：`R4_PREREGISTERED / R4_READY_FOR_INDEPENDENT_REVIEW`；真实 R4=`NOT RUN`，独立审查=`PENDING`，`APPROVED_FOR_EXPERIMENT=NO`。

本文件在任何 R4 真实请求前冻结。R3.1 只用于提出假设，不作为 R4 独立证据；不得依据后续结果更换主指标、删除 seed 或追加预算。

## 1. 研究定位与假设

这是小规模、探索性的 Train-only 机制比较，不是确认性统计实验或毕业论文创新已经成立的证明。

- **主比较：** B3（质量优先配对父子信用）−B2（标准 NSGA-II/均匀算子）的独立 final Task Success。
- **主假设：** 结果信用比均匀算子更有可能找到高质量 Agent。
- **次要比较：** B4−B2、B3−B4、B2−B1。
- B1=Fixed LLM，B4=旧失败频率反馈；不设置 B5，不组合多样性机制。

## 2. Fresh Train 任务与隔离

冻结协议=`D094_R4_TRAIN_V1`，manifest canonical SHA-256=`e8412c74c33faf7a56195d685d49080b5669dbe46efd3ae1ab6dee88917b5bff`。

| task_id | verification | compensation | retry_failures | retry_never | seed_jitter | task SHA-256 |
|---|---|---|---:|---|---|---|
| d094_r4_train_compensation_unverified_0 | false | true | 0 | true | false | `1989a168a404e0844c5bfc18c17b29f81a89870a0ad513d49090dc2f6dbd048c` |
| d094_r4_train_transient_single_0 | false | false | 1 | false | false | `b7fa81390ff250daa0d104e433a42aa2e6cb98cdfb25135a46b325614b112632` |

- SHA 覆盖完整 `TrainTask` canonical JSON，不仅是名称。
- 与历史 `train_tasks()` 12 个任务及 `r3_tasks()` 6 个任务做双向 task ID 和完整规格集合比较，交集均为空。
- 第一项是历史 Train 没有的“不要求 verification、要求 compensation”依赖组合；第二项移除历史 transient 的 jitter，形成确定的单次失败调度。
- 生成规则是两个显式冻结规格，不使用 R3.1 outcome 自动生任务，不输入隐藏标签。
- **没有读取 Validation/Test，也不声称已证明与 held-out 的语义不重叠。** 该项明确记录为 `NOT_CHECKED_VALIDATION_TEST_ACCESS_FORBIDDEN`。

## 3. Seeds、可达性和 Genome 空间

- 配对 episode seeds=`301,302`；搜索 seed=`711`。
- 每个候选评价全部四个单元，顺序按 `(task_id,seed)` 固定。
- 搜索池仅含 `max_plan_steps=5` 的 216 个合法 Genome；planning mutation 与 crossover 不得改变步数。
- 公共路径和本地验证：补偿任务 3 步，transient 任务 4 步，两个 seeds 全成功、约束 0、API=0。
- 公共可达性不是 B3 的收益；不得事后把步数改为其他值或单独给某臂增加动作。

## 4. 规模与公平性

| 臂 | search 候选 | search episodes | final episodes | 总 episodes |
|---|---:|---:|---:|---:|
| B1 | — | — | 4 fixed | 4 |
| B2 | 4（初始 2+offspring 2） | 16 | 4 | 20 |
| B3 | 4（初始 2+offspring 2） | 16 | 4 | 20 |
| B4 | 4（初始 2+offspring 2） | 16 | 4 | 20 |
| 合计 | — | 48 | B1+三个 final=16 | 64 |

所有演化臂共享任务、配对 seeds、模型、基础 Prompt 版本、相同初始种群、搜索评价预算、final 预算、停止规则、1 代、population=2、duplicate 不评价和 proposal cap=`population×30`。B3 不获得额外配对评价；父子比较复用已有的父/子公开结果。

## 5. 模型与请求控制

真实执行若以后获批，必须使用 `deepseek-flash`、同一 Base URL、temperature=0、`thinking={"type":"disabled"}`、严格 JSON 和固定 Prompt。最大输出 128 tokens、timeout 20 秒、并发 4、HTTP 重试 0、每请求 canonical messages 4096 bytes、每 episode 请求硬上限 5。

当前 `run_d094_r4.py` 只支持预检或 Mock；独立审查前没有真实执行入口。

## 6. 主信用冻结公式

对 variation 第一 parent 与 child 的每个相同 `(task_id,seed)` 单元：

1. child 约束更多/更少分别给 -1/+1。
2. 约束相同，比较 `(1-task_success,1-recovery_success,harm)` 的严格 Pareto 支配，child 改善/回归分别 +1/-1，否则 0。
3. offspring reward=四个单元奖励均值。
4. 每算子最近 `W=4` 个 accepted offspring reward 的均值为 credit；`τ=0.25`、`ε=0.2`：
   `p_k=(1-ε)softmax(credit_k/τ)+ε/6`。
5. 冷启动均匀；duplicate 不评价/不更新；完整 child 评价后才更新，且只影响后续 proposal。
6. Tool/token/latency 纯资源变化不进入主信用；缺失配对或 execution error 使运行无效。

完整定义见 `D094_R4_ALGORITHM_DESIGN.md`，实现见 `d094_r4_credit.py`。

## 7. 七目标、final 与独立评价

搜索与 final 选择继续使用七目标：Task/Recovery 未完成、约束、Harm、Tool Cost、保守 Token Cost、Latency。硬约束不可被目标补偿。

final 从全部已评价搜索候选的可行第一 Pareto front 按 `(objectives,genome_sha256)` 字典序最小选择，不读取 final 结果。final 必须重新执行四个新真实 episodes；相同 Train 单元不意味着 held-out 泛化。

## 8. 指标与最小有意义效应

- **主要指标：** final Task Success Rate（四个配对单元等权）。
- **最小有意义效应：** B3−B2 总体 Task Success 差至少 `0.25`，即四个单元中至少一个净改善；同时完整展示逐 task/seed 差值。
- 次要：Recovery、约束、Harm、Tool/Token Cost、Latency、搜索唯一 Genome/Phenotype、Pareto、算子概率和实际使用、预算。
- 行为/Phenotype 或概率变化只是机制证据，不替代主要终点。
- 达到 0.25 也不自动等于普遍提升；需方向、逐单元结果和后续独立复现共同解释。

## 9. 配对统计方法

对每个比较构造按 `(task_id,seed)` 排序的四个 final Task Success 差值。

1. 报告四个原始差值和均值，不仅报告总体百分比。
2. 使用全部 `2^4=16` 个符号翻转的双边精确检验，统计量为均值差。
3. 使用 paired-unit percentile bootstrap 95% CI，重采样四个配对单元，`20,000` 次；基础 seed=`20261120`，四个比较按冻结顺序分别加 0/1/2/3。
4. 对 B3−B2、B4−B2、B3−B4、B2−B1 四个 raw p 值使用 Holm 校正，保留 raw 与 adjusted。
5. 四单元精确双边符号翻转的最小非零 p 值有限，样本明显不足以建立统计显著或普遍提升；所有统计仅作探索性不确定性描述。

实现=`d094_r4_statistics.py`。Mock 统计输出只是软件 fixture，不是真实结果。

## 10. 无效运行、缺失数据与停止规则

以下任一条件使整个运行 INVALID，不计算有效性能结论：

- 任务/seed/Genome/预算/源码与执行锁不一致；
- 任一配对单元缺失、重复、顺序身份不明或 execution error；
- 任一 final 缺失、无可行候选、未独立执行或无真实调用；
- 请求/成本超过上限、final 池被搜索占用、未知 usage/成本或超预留；
- episode hash-chain 失败、账本不完整或身份冲突；
- 非目标模型、Validation/Test 访问或真实 API 未授权。

proposal cap 耗尽、预算预留不足或配置不完整时，在首请求前或当场停止，保留部分账本。不得减少 final、换 seed、删除失败 episode、补预算或改判据继续。缺失数据不做插补，不把失败当成功，也不从分母删除。

## 11. 完整报告规则

无论结果方向，均保存并报告：42 个历史 R3.1 episode 不变；R4 实际 64 个计划单元的完成数、全部原始 episodes/requests/traces、逐 task/seed、四比较、raw/adjusted p、CI、成本、搜索行为、Genome/Phenotype、credit/feedback、survivor、Pareto/final 和 artifact SHA。

结论用语：

- 达到预设方向与最小效应：`POSITIVE_SIGNAL`（仍需独立复现）；
- 无明确收益或仅行为/资源变化：`NO_CLEAR_GAIN`；
- 任一无效条件：`INVALID`，不得转为性能结论。

禁止用搜索期最佳结果替代 final，禁止把 NO_CLEAR_GAIN 改写成提升。

## 12. 预算门禁

- 全局真实请求≤320（同时远低于既有 1500 政策上限），Token 推导成本硬上界≤**0.442368 USD**（低于既有 0.50 USD）。
- B1 和三个 final 各预留 20 请求/0.027648 USD；搜索每演化臂≤80 请求/0.110592 USD。
- 搜索不得消费 B1/final 预留；duplicate/HTTP retry 请求上界均为 0。
- 经验估算与硬上界见 `D094_R4_BUDGET_ANALYSIS.md`，经验值不是账单或新上限。

## 13. 审查与授权

本阶段只完成设计、代码、合成/Mock、预算与统计冻结。新独立会话必须审查数学与控制流、公平性、信息隔离、预算、统计、真实入口和账本；之后还需用户明确批准。独立审查通过也不自动等于实验批准。

当前严格状态：

`R3.1_ANALYZED → R4_HYPOTHESIS_SELECTED → R4_ALGORITHM_DESIGNED → R4_IMPLEMENTED → R4_SYNTHETIC_VALIDATED → R4_PREREGISTERED → R4_READY_FOR_INDEPENDENT_REVIEW`。

**不得自行进入 `APPROVED_FOR_EXPERIMENT`。**
