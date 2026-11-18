# D-093 紧急实验接管提示词（2026-11-18）

## 0. 唯一仓库、基线与不可变边界

Repository: yujian777555/kaitibaogao
Branch: pilot-a-stateful-recovery
Start HEAD: afdd5502c474752a23c7a52fa4fd047bc0094094
main: 683b3fe7fc52c86e917d523fdc6bbb13abbfd653

D-092 已正式记录为 HOLD。R2.3 的 P05/P06 HOLD、960 Probe 原始账本、独立审计、113号报告均为不可变历史证据。不得修改或覆盖：
- 103_D092_TRAIN_ONLY_PREREGISTRATION.md 及 R2.2/R2.1/R1/R0 snapshots；
- 113_D092_PROBE_RESULT.md；
- experiments/d092_recovery/results/probe/episodes.jsonl；
- experiments/d092_recovery/results/probe/independent_audit.json；
- D-090/D-089/D-088 已冻结源码与历史结果；
- main 分支。

D-092 五臂正式搜索仍为 NOT RUN。不得声称 A3 优于 A1/A4，不得把 Probe PASS 或 CI PASS 写成性能提升。

用户要求继续实验，不要因 D-092 一次 HOLD 停止整个研究。后续全部新工作使用 D-093 版本化预注册、新 Train manifest、新执行锁和独立账本。

## 1. D-092 已确认的真实证据

### 1.1 Probe

- 960/960 episodes，10 genomes × 96 frozen Train scenarios，seed=711，cache=0。
- P00–P04、P07–P09 PASS；P05/P06 HOLD。
- P05/P06 的 Q3 trace 完全一致；预算窗口中没有可执行的 ordinary/tight 分叉。不能改 D-092 的场景、阈值或判据来追认 PASS。
- 原始 JSONL SHA-256：b063fba6d24c2a89038dddffe62cedaed518f489cfa1097bfc2b90cea421f02a。
- 完整报告：113_D092_PROBE_RESULT.md。

### 1.2 额外硬约束风险

960 episodes 汇总：
- unauthorized_action_count = 2,748
- runtime_abort_count = 146
- pending_count = 120
- invalid / illegal transition / duplicate = 0

R2.3 §7.2.2 明确六类硬约束均为 hard，候选可行要求六类原始计数全部为 0。不能把 unauthorized 当成无害日志，也不能把 542/542 测试通过当作可行性证据。

源码级嫌疑，必须用逐条原始账本确认：
- experiments/d088_recovery/d088_policies.py 的 _recover_current() 在 current tool state 为 COMPENSATED 时直接返回 RETRY_WORKFLOW，没有检查 current tool 是否仍有 pending route。
- experiments/d092_recovery/d092_runtime.py 的 public_action_allowed() 对 partial_recover 只在 current tool=COMPENSATED 且无 pending 时允许 RETRY_WORKFLOW。
- 环境 delayed success 在 COMPENSATE dispatch 当场将 tool state 改为 COMPENSATED，但 pending receipt 仍保留至 VERIFY。
- D088RecoveryPolicy.act() 在 pending 但有其他 available work 时，_pending_action() 可能返回 None，随后进入 _recover_current() 并提出 RETRY_WORKFLOW。

这构成明确的控制流不一致嫌疑，可能导致 unauthorized retry 和 request_count 消耗而 decision_count 不变，最终 runtime abort。不得只凭推理认定全部 2,748 次都由此产生，必须按 raw JSONL 独立统计、定位 action/state/pending/trace index，确认实际覆盖范围。

### 1.3 搜索器合成预检

现有 README/111号报告记录的 synthetic preflight：
- A0：96 unique / VALID；
- A1/A4：79 unique / INVALID；
- A2：77 unique / INVALID；
- A3：60 unique / INVALID；
- A1/A2/A3/A4 均在 384 proposal attempts cap 内未达到 96 unique。

因此即使忽略 Probe HOLD，正式搜索仍有 proposal starvation 风险。先诊断重复 proposal 的来源、operator/block/locus、parent selection、archive/survivor 及 RNG 消费；不能直接启动 25 个正式 run 后再处理。

## 2. Phase A：只读取证，不新增 rollout

### A1. 960 Probe 硬约束分层

对 episodes.jsonl 流式读取，不覆盖文件，输出独立诊断：
- 按 probe × family × stratum × label 统计 unauthorized、runtime abort、pending；
- 统计含任一 hard constraint 的 episode 数；
- unauthorized action 的具体动作、before state、current tool state、current pending routes、trace index；
- 统计 RETRY_WORKFLOW 被拒绝的次数及其后连续相同状态重复请求次数；
- 核对 unauthorized 是否与 runtime abort 共现，是否存在其他根因；
- 重新计算 2,748 / 146 / 120 汇总，和独立审计逐项对齐。

### A2. Synthetic search proposal starvation

只读 111号报告、合成运行账本和 runner：
- 每 arm 的 attempts、unique、duplicates、cache、proposal source；
- 按 round、operator、block、locus、parent pair 统计 duplicate rate；
- 统计种群/档案中 genome 与 phenotype 唯一数；
- 核对 144-genome 可达空间与实际 variation reachability；
- 复核 A1/A4 proposal、parents、RNG streams 是否逐事件等价；
- 区分实现 bug、variation distribution collapse、survivor diversity collapse。

交付 115_D093_POSTMORTEM.md。Phase A 不运行新 rollout，不修改 D-092 历史。

## 3. Phase B：新版本修复 receipt-aware control flow

不得修改 D-088/D-090/D-092 冻结源代码。新建 D-093 policy adapter，例如：
experiments/d093_recovery/d093_policy.py。

推荐最小安全语义：
- 对 partial_recover，若 current tool 存在任何 pending route，不得提出 RETRY_WORKFLOW；
- 应根据 public pending state 通过 WAIT/VERIFY 解决当前 pending receipt；
- 若等待策略因其他 independent route available 而返回 None，在 partial_recover 当前工具 pending 的情况下必须安全 WAIT，而不是继续提出 RETRY；
- 只有 current tool=COMPENSATED 且该 tool 无 pending route 时才 RETRY_WORKFLOW；
- delayed failure resolve 后按公开 receipt 更新 evidence，再选择当前工具可用 route；
- 不读取 hidden outcomes、真实 delay、resolve_at 或 label。

可以通过 D093 adapter/subclass 覆盖 _recover_current()，但需验证其与 inherited act() 中 pending 分支的组合语义。所有比较臂使用同一 correctness adapter，避免只修 A3。

必须新增测试：
1. immediate success + no pending → retry allowed；
2. delayed success + pending → no retry; wait/verify until closed; then retry；
3. delayed failure + pending → receipt closed before alternate recovery；
4. pending current + independent routes available → no unauthorized retry；
5. pending unrelated tool but current no pending → mask semantics unchanged；
6. 24-request cap 不会因重复 unauthorized action 消耗；
7. 六类硬约束的计数与独立监视器一致。

新模块/测试全部使用 D093 命名空间。不得改 mask 放宽权限，不得把 unauthorized 重新分类成 soft。

## 4. Phase C：解决 96-unique / 384-attempt 搜索器预检

先诊断，再决定是否新增算法机制。不得擅自增加 D-092 attempt cap、降低 unique target 或删除失败 proposal。

候选方向：
- bounded novelty-aware mutation：在保持 mutation/crossover 语义的前提下，减少重复 canonical genome；
- diversity-preserving survivor tie-break：在性能目标并列/近似并列时保留不同 genotype/opaque phenotype；
- deterministic unseen-genome fallback：只有作为新方法单独预注册，不能伪装成标准 NSGA-II/III；
- 若 384 cap 本身不足，必须用重复率/有限空间模型给出依据，在 D093 新预注册中明确新的 attempt cap，不得回写 D092。

基线 A1/A4 必须保持完整逐 seed proposal、parents、operator、RNG 消费等价。任何 proposal repair 若改变标准算法语义，必须明确命名并作为新臂/消融，不得仍标成标准 NSGA-II。

只有在所有五臂的 synthetic preflight 均能于新协议 attempt cap 内达到 96 unique，且 A1/A4 等价测试通过后，才允许正式搜索。

## 5. Phase D：重新设计可达 Harm-priority Probe

D-093 必须是新版本预注册，不修改 D-092 的 P05/P06 HOLD。

新建 96 个 fresh Train scenarios，固定生成器与 manifest hash；不得复用 D-092 96 IDs 作为新的独立性能证据。建议 6 families × 4 strata × 4 repeats，标签 R1/R2/R3/R4 各 24；只含 Train，不含 Validation/Test。

固定四个单机制 genome：
- H0：harm ordering disabled；
- H4：threshold=4；
- H8：threshold=8（baseline）；
- H12：threshold=12。

计划 4 × 96 = 384 Probe episodes，seed=711，无 cache，独立账本。

### 必须先做可达性设计证明，再锁定 manifest

针对每个预注册对照，在相同 public before-state 同时满足：
- available candidates ≥ 2；
- ordinary choice != tight choice；
- _can_dispatch_more(view)=true；
- 无未解决的 current pending 控制流阻断；
- 该分叉由实际执行动作而非只算出的理论排序产生。

对照窗口：
- H0 vs H8：budget_remaining ≤ 8；
- H4 vs H8：4 < budget_remaining ≤ 8；
- H4 vs H12：8 < budget_remaining ≤ 12。

还必须满足 dispatchability：budget_remaining > in_flight + 5。没有 pending 时这意味着 budget_remaining>5。不得只看阈值而忽略 dispatch gate。

场景生成器必须采用预先定义的参数网格，不得根据 Probe rollout 结果筛选或替换场景。静态可达性分析、所有场景 ID、四个 genome、预期分叉点、manifest hash、代码 hash 全部在第一条 rollout 前写入 execution lock。建议至少 12 个分布于不少于 3 个 family、覆盖 R1–R4 的不同 scenario anchors；确切最低覆盖数量须在预注册中固定。

若静态设计阶段无法构造上述分叉，先修改场景生成器/设计并做独立复核；不要先跑再挑场景。若真实 Probe 仍 HOLD，保留完整数据，不追认 PASS。

Probe 判据必须同时核验：
- shared before-state；
- actual action/observation first difference；
- ordinary/tight expected selected route；
- 完整 96 episode；
- 六类 hard constraints；
- trace/outcome/identity hash；
- 无 cache、无隐藏信息泄漏。

## 6. Phase E：D-093 正式 Train-only 搜索门禁

以下条件全部通过后才启动：
1. unauthorized-action 根因修复，并在 D093 panel 上为 0；
2. runtime abort=0、pending=0、其余硬约束均满足可行性定义；
3. 96-unique proposal synthetic preflight 全部五臂通过；
4. A1/A4 完整轨迹与 RNG 等价；
5. 四组 Harm-priority Probe 对照均达到预注册 PASS；
6. D093 新预注册和 execution lock 已独立复核。

随后执行五臂：
A0 Random、A1 NSGA-II、A2 NSGA-III、A3 dynamic feedback、A4 zero-feedback control。

种子沿用 711/822/933/1044/1155，除非新预注册在 rollout 前有充分理由并固定变更。每 arm×seed 目标 96 unique genomes，每 genome 96 Train episodes；attempt cap 由 Phase C 诊断并在 D093 预注册中固定。保留每个 proposal、duplicate、RNG、feedback、survivor、archive、episode 和 audit ledger。

主比较 A3−A1、A3−A4；次要 A1−A0、A2−A1。不得在任何 seed INVALID 后删除、替换或补预算。只有全部配对候选可行时才计算预注册统计门槛。不得把 D093 Probe 结果写成性能提升。

## 7. 仓库维护与开题表述

新建 D093 独立目录，不污染 D092。逐阶段更新：
- README.md
- SESSION_HANDOFF.md
- NEXT_SESSION_PROMPT.md
- 05_DECISION_LOG.md
- 51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md

建议报告：
- 115_D093_POSTMORTEM.md
- 116_D093_RECEIPT_AWARE_ADAPTER_REVIEW.md
- 117_D093_HARM_PROBE_PREREGISTRATION.md
- 118_D093_HARM_PROBE_RESULT.md
- 119_D093_TRAIN_ONLY_RESULT.md

只在实际完成后创建结果报告。每次提交核验 branch/main、ahead/behind、clean worktree、diff check、CI run 和文件 SHA。文档提交无 CI 必须明确标 NOT RUN。

开题当前可写：已完成一轮 960 episodes 的机制可辨识性实验，8 项机制对照通过，2 项 Harm-priority 对照因决策点不可达而 HOLD；独立审计与回归通过；正式五臂性能搜索尚未执行。动态反馈提升尚待验证。

现在开始 Phase A 的只读取证，随后执行 Phase B/C/D；不要把 D-092 HOLD 改成 PASS，也不要因 D-092 失败停止整个研究。
