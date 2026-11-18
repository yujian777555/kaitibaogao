## D-094 当前接管：R2 已审计，INVALID_BUDGET；R3 NOT RUN（2026-11-19）

先读`D094_NEXT_SESSION_PROMPT.md`和`D094_PHASE2_R2_RESULT.md`。R2已结束，不得重启：1260 episodes、3704真实API、成本1.0002363 USD超限；B2 final无真实调用，无有效B2-B1比较。搜索阶段36/36信号只能用于后续复现，当前创新=INVALID。

独立审计与Genome/Phenotype分析已完成；32 Genome→24 phenotype，无complete collapse。下一步只做`D094_NEXT_EXPERIMENT_PLAN.md`的R3审查/预算预检和实现准备，必须先预留最终评价预算并补齐账本，不能启动大规模API。D-092/D-093/main不变。

完整回归595/595；代码/结果提交`17120fac98b4aa96a8b5f0cbf5a0d67c8f3d6dec`的CI run`44360886032`=completed/success，D-094日志53/53。后续纯文档提交无run写NOT RUN。

---

## D-094 当前接管：真实 Canary 已 PASS，Phase 2 R2 执行中（2026-11-19；历史状态）

真实`deepseek-flash` Canary已完成3次真实LLM决策和inspect→verify→complete轨迹，Token=1552/148，保守成本估算0.0006432 USD，硬约束0。先读`D094_API_CANARY_REPORT.md`和`D094_NEXT_SESSION_PROMPT.md`。

Phase2 R1 INVALID已保留，B2未运行；V2修复成本上界/跨代去重/用量累计后，R2正在执行。接管时先检查后台/远端和`results/phase2_r2/summary.json`是否存在，运行`d094_phase2_audit.py`独立复算后再报告B0/B1/B2。不得把运行中或R1失败写成有效提升。

---

## D-094 当前接管：Phase 0 完成，真实 API 配置阻断（2026-11-18；历史状态）

工作分支已切换为`d094-llm-agent-integration`，基线`f409a730fd1c1cae90584f7591a213e916f28c2c`。先读取`D094_NEXT_SESSION_PROMPT.md`、`D094_API_CANARY_REPORT.md`和`D094_DESIGN.md`，不要沿用下方D-093任务或修改其历史。

- 真实OpenAI-compatible Adapter、多轮LLM Agent、Typed Genome、NSGA-II、多目标评价和账本已实现；D-094测试36/36，全量回归578/578。
- Mock Canary两轮决策完成工具执行，但不是实际API。真实Canary因base URL、MODEL和Token价格缺失而BLOCKED_CONFIGURATION；真实调用0、Token 0、成本0，模型未配置。
- 下一步先配置环境变量并执行受限真实Canary；只有真实PASS才进入D-094独立小Train的B0/B1/B2。Phase2搜索、B3/RSI、Validation/Test和训练当前NOT RUN，无提升结论。
- D-092/D-093源码、数据、报告和main保持不变。代码提交`bc087c0dd08c5bd25b25e64311775765ae5c81d4`的CI run`44328080784`已completed/success，D-094日志36/36 OK；无D-094专属性能artifact。后续纯文档提交无run写NOT RUN。

---

## D-093 接管：D-092 HOLD 后的三个真实阻断（2026-11-18；尚未执行新实验）

当前 D-092：960 Probe 完成，P05/P06 HOLD，正式搜索 NOT RUN。不可修改 R2.3、113号报告、原始episodes JSONL或D-090/D-089/D-088历史源码。

除P05/P06可达性问题外，复核发现更关键的硬约束风险：Probe总计 unauthorized_action_count=2,748、runtime_abort_count=146、pending_count=120。R2.3 §7.2.2将六类都定义为hard，候选可行要求六类原始计数全部为0。源码调用链显示潜在原因：D088RecoveryPolicy._recover_current()在current state=COMPENSATED时无条件提出RETRY_WORKFLOW；D092 public_action_allowed()仅在current无pending时允许；delayed success会先改state后保留pending。必须按原始JSONL逐条确认，不能只凭源码推断全部计数根因。

第二项阻断：既有synthetic search preflight中A0=96 unique/VALID，A1/A4=79、A2=77、A3=60，均在384 attempts内未达96 unique。必须先分析duplicate proposal、variation与survivor多样性，不得直接启动正式搜索或暗改attempt cap。

第三项阻断：P05/P06的Q3预算窗口没有可执行ordinary/tight分叉。D092 HOLD永久保留；新Harm probe必须用D093 fresh Train manifest、静态可达性证明和预先锁定的scenario grid。

新执行接管文件：114_D093_EXPEDITED_EXECUTION_PROMPT.md。先只读复算D092原始证据，再新建D093 receipt-aware policy adapter、诊断proposal starvation、设计四组H0/H4/H8/H12可达性Probe。只有硬约束、proposal coverage、A1/A4等价和新Probe门禁全部通过后，才启动D093五臂Train-only搜索。当前没有执行D093 rollout或正式搜索，不能声称新提升。

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




## D-092 真实 Probe 已完成：HOLD / 正式搜索 NOT RUN（2026-11-18；当前接管任务）

唯一仓库`yujian777555/kaitibaogao`，分支`pilot-a-stateful-recovery`。开始前实际fetch并核验远端HEAD/main/worktree，不信任历史完成声明。Probe执行锁/修复提交=`7be851e264bcad2e2d3105c7c21f2c3e7db76ebd`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。

1. 阅读`113_D092_PROBE_RESULT.md`、`experiments/d092_recovery/results/probe/probe_summary.json`和`independent_audit.json`。无需重读全部历史，不得覆盖110/111或R2.3/R2.2等历史文件。
2. 真实结果=960/960、seed711、cache0；P00–P04/P07–P09 PASS，P05/P06 HOLD。原始JSONL SHA=`b063fba6d24c2a89038dddffe62cedaed518f489cfa1097bfc2b90cea421f02a`。审计=PASS只表示原始账本一致，不表示门禁通过。
3. P05/P06根因已定位：Q3的P00/P05/P06 trace完全相同；预定窗口没有实际ordinary/tight选择分叉。budget3/2的理论差异分别被VERIFY(B)/ESCALATE和不可dispatch控制流遮蔽。完整逐状态证据在113和independent_audit。
4. **不要启动五臂五seed正式搜索。** 用户授权以全部Probe PASS为条件，该条件未满足。A3−A1/A4、R3/R4/CondRec/Harm搜索指标、phenotype collapse和候选选择均NOT RUN，不得编造结果。
5. 不得重跑冻结Probe调参、改场景/窗口/阈值/统计门槛、删除不利episode、补预算或换seed。若继续修复研究设计，只能形成新的版本化预注册并取得相应审查/授权；原D-092 HOLD永久保留。
6. 可复算命令：`PYTHONHASHSEED=0 .runtime/venv/bin/python experiments/d092_recovery/d092_probe_audit.py`。完整回归实测542/542，D-092=86/86；后续代码修改后必须重新运行。
7. Validation/Test、13,824 exhaustive、Pilot B、真实LLM/API、A800/ARWM、D-090重跑和main修改均未授权。提交后核验远端HEAD/main/ahead-behind/worktree/真实CI；没有run就写NOT RUN。
8. 代码/结果提交`c1975a7f3fea73f6af6d845b229ec9fd3e769593`的CI run`44299067518`已completed/success，D-092日志86/86 OK；CI没有运行Probe/search，6个既有artifact均非D-092性能证据。后续纯文档提交不虚构新CI。

---

## D-092 快速实验授权与执行接管（2026-11-18；历史授权，当前结果见上方）

用户已明确要求“抓紧实验吧，马上要开题了”。本授权范围为：关键实现门禁修复后执行 R2.3 的 960 Probe；仅当实现审查 ACCEPT_FOR_PROBE 且全部预注册 Probe 判据 PASS 时，继续五臂×五 seed Train-only 搜索。无需为这两阶段再次询问用户。Validation/Test、外部 benchmark、真实 LLM/API、A800 模型训练及 main merge 不在授权范围内。13,824 exhaustive reference 仅按 R2.3 §11.2 在正式结果和日志全部锁定后单独执行一次。

远端快速源码复核（HEAD cfe431ab026a2626bf28c00ec45352db9a7f1dd4）确认三项执行阻断：
1. BudgetLedger.offer() 在 evaluator 成功后才 append proposal_log；中断、异常、malformed view、identity mismatch、row_count mismatch 会消耗 attempt 却缺少 proposal 终态记录。
2. run_arm() 只捕获 BudgetError/EvaluationInterrupted；普通 RuntimeError/ValueError 可能逃逸，不形成带部分账本的 INVALID。
3. m1_equivalence() 未比较完整 RNG event streams，尚不能证明 R2.3 §11.1 的完整 A1/A4 等价。

此外，experiments/d092_recovery/ 当前没有实际 Probe runner 或正式 Train-only driver；现有 workflow 只执行 synthetic tests。下一步按 112_D092_EXPEDITED_EXECUTION_PROMPT.md 执行最小修复、补测试、实现 Probe 与正式搜索入口。历史合成 INVALID 数值必须保留，不得扩预算消除。

当前远端 HEAD=cfe431ab026a2626bf28c00ec45352db9a7f1dd4；main=683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead/behind=323/0。上述授权不修改 canonical 103 或历史报告。


# NEXT_SESSION_PROMPT.md — Canonical Handoff Prompt

## D-092 真实 Probe 执行锁已完成（2026-11-18；LOCKED_BEFORE_ROLLOUT / 实验已获用户授权）

- 当前基线HEAD=`e505f0d2126f729968f298c1448f9dedcabb48d1`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。不覆盖110/111或R2.3历史。
- 三项修复已实现：每个attempt先PENDING后最终状态；普通evaluator异常转为INVALID且未知partial不伪报0；M1比较完整RNG事件。新增失败/中断/篡改回归后D-092=82/82通过。
- Probe Runner已实现完整960原始账本和逐项PASS/HOLD；执行锁=`experiments/d092_recovery/results/probe/execution_lock.json`，raw SHA=`eb114463c3549527d577c26a24f221a03291d20a9a1e6e524514300aaa4b9787`，seed=711，无缓存。
- 精确运行时已在WSL验证：Ubuntu22.04、CPython3.11.9、NumPy1.26.4、PYTHONHASHSEED=0；wheel SHA=`666dbfb6ec68962c033a450943ded891bed2d54e6755e35e5835d63f4f6931d5`；资源快照=`.claude_resources.json`。
- **下一步立即执行960 Probe；全部PASS才继续五臂五seed正式Train-only搜索。** 用户已明确授权这两项，无需再次确认。任何HOLD/INVALID均保留，不补预算、不换seed。
- CI workflow固定Ubuntu22.04/Python3.11.9/hash-locked NumPy，只运行测试，不在CI启动Probe/search。

---

## D-092 Typed Adapter 实现与合成测试完成（历史；当前真实Probe锁见上方）

110号已允许Typed Adapter，规格基线提交=`2a95f0922a87d2b3b39b65363c09385d421fb762`。main仍为`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。

- 新增`experiments/d092_recovery/`：typed genome、反馈、完整NSGA-II/III、guarded runtime、聚合evaluator/audit、五臂Runner与完整账本；workflow只新增合成测试。
- **验证：** D-092=73/73；完整回归28+398+8+8+14+73=529/529；本地CPython3.9.13/NumPy1.26.4，目标3.11.9/Ubuntu未在本地部署。
- **合成边界：** A0 VALID 96/96；A1/A4=79 unique/384 attempts INVALID；A2=77/384 INVALID；A3=60/384 INVALID。均为INVALID_ATTEMPT_CAP控制流证据，不是算法性能比较；A1/A4轨迹仍完全一致。
- **报告：** `111_D092_TYPED_ADAPTER_IMPLEMENTATION_REVIEW.md`，含模块/测试/文件哈希和自检边界。
- R2.3 canonical raw/canonical/blob仍为`75f9c72a…e7522`/`549c595e…7ce4`/`1498f20a…69a3`；R2.2 snapshot未变。
- **下一任务：独立实现一致性复审。** APPROVED_FOR_EXPERIMENT=NO；Probe、正式搜索、exhaustive、Validation/Test继续禁止。实现审查通过和用户明确批准后才可申请实验。
- **CI证据：** 代码HEAD`1e697b19aea2a25dd6a2b2996325c600fbdd82f7`的run`44156241648`已completed/success，D-092测试步骤73/73=OK；无D-092专属artifact，既有artifact不属于本轮性能证据。

---

## D-092 R2.3 独立验收通过（历史规格门禁；实现进展见上方111号）

独立报告：`110_D092_R2_3_INDEPENDENT_REVIEW.md`。基线 HEAD=`6f9f7d9af062d9f4a871e429d40da6c0645cdb18`，main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，ahead/behind=320/0，工作区 clean。

- F9 canonical UTF-8 identity bytes：ACCEPT；独立哈希向量通过。
- F13/P07真实14-action/budget=10控制流：ACCEPT；源码调用链与精确分数2.770802651881641通过。
- D-091负面证据继承：PASS；旧Random身份、静态State-Evo、8 genome→1 phenotype、21-step最短、P1/P2/P4负结果和best-only缺口均保留。
- D-092五臂/反馈/预算/选择/约束/信息隔离设计：PASS_FOR_IMPLEMENTATION；均是规格审查，不是实现验证。
- R2.3 raw/canonical/blob=`75f9c72aa7d3a70880f59f7b803ed88e919d47e9c42e7168ba1b7eddbc3e7522` / `549c595ed657d0b0582e6d6f41dfcfc241bde82b7daa2bdbf89bb3a660497ce4` / `1498f20a6f298093c06d126a766c037a980869a3`；R2.2 snapshot保持完整。
- **下一任务：立即实现Typed Adapter与五臂统一Runner，并执行静态/合成测试。** 不运行960 probe、genome search、exhaustive、Validation/Test或其他受禁实验。
- 基线CI=NOT RUN；本审查提交后按真实SHA查询，不虚报通过。

---

## D-092 R2.3 两项定向修复完成（历史状态；已由110号独立验收 supersede）

唯一仓库/分支：`yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`。本轮起始 HEAD=`b7b0ba4b623a22e01a10dded378d80215ca4866a`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；起始 ahead/behind=318/0、工作区 clean。最终 SHA 以提交后远端核验为准。

### 交付与身份

- canonical R2.3：`103_D092_TRAIN_ONLY_PREREGISTRATION.md`；raw=`75f9c72aa7d3a70880f59f7b803ed88e919d47e9c42e7168ba1b7eddbc3e7522`，canonical=`549c595ed657d0b0582e6d6f41dfcfc241bde82b7daa2bdbf89bb3a660497ce4`，blob=`1498f20a6f298093c06d126a766c037a980869a3`。
- R2.2 immutable snapshot：`103_D092_TRAIN_ONLY_PREREGISTRATION_R2_2.md`；raw=`c0035d0f7236eff03325e81c2b7967ae166bc4c73047e390d502859f6d8fdc5c`，canonical=`f18aecb71791e43220ac74920c67c27141c58eaadfde74fd0190103e0b4695a3`，blob=`006aface19258f5d9ba597011dfe9048dfea8897`。
- 验收报告：`109_D092_R2_3_TARGETED_REPAIR_REPORT.md`。R2.1/R2/R1/R0 均未覆盖。

### 仅两项变化

1. **F9 encoding：** episode_reference 与 compensation_attempt_id 的既有 payload 不变；统一以 `canonical_json(payload).encode("utf-8")` 为 SHA-256 输入。canonical JSON 使用 ensure_ascii=False、sort_keys=True、separators=(",",":")、allow_nan=False；无额外换行。identity/composite keys、反馈与 receipt lifecycle 不变。
2. **F13/P07：** 真实共同前缀为 14 actions，随后 decision_count=14、budget_remaining=10。第7步 C delayed success 在 dispatch 当场将 C 改为 COMPENSATED；第8步 B primary 可在 C receipt pending 时派发；第14步 VERIFY(C)=COMPENSATED。P06 threshold4 ordinary 选 B primary，P07 threshold12 tight 选 B alternate；分数差精确为 +2.770802651881641。

F8/F14、F10/F11/F12/F15、P03、96 Train、μ/λ、96 unique、384 attempts、五臂、五 seeds、反馈矩阵和统计判据均保持原样。

### 验证与下一任务

静态/公式检查通过：快照身份、13/13源码哈希、96 Train IDs、冻结文本、F9字节编码、精确14-action表、预算10、P06/P07分数、无旧17-action/budget=7残留、无OPEN/TBD/TODO、`git diff --check`。109号报告记录完整证据。**未运行算法测试、rollout、960 probe、genome search、exhaustive或Validation/Test；无算法提升证据。**

唯一下一任务：新独立会话只验收上述 F9 encoding 与 P07 trace。通过后立即进入 **Typed Adapter → 静态算法测试 → 合成测试 → 实现一致性审查**，不做新文献调研或大范围协议重写。实现阶段必须保持五臂统一 evaluator、96 unique/384 attempts、聚合 optimizer view、完整账本与 audit 复算。实现复审和用户明确批准前不运行 probe/search。

当前禁止：probe、genome search、13,824 exhaustive、调参、候选冻结、Validation/Test、Pilot B、正式A-3b、真实API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑D-090、修改main。维护时无新CI/artifact；提交后真实查询，无run即NOT RUN。

---

## D-092 R2.2 独立复审结论与 R2.3 两处定向修订接管（历史任务；已由上方 R2.3 交付 supersede）

唯一仓库/分支：yujian777555/kaitibaogao / pilot-a-stateful-recovery。复审基线 HEAD=7cd092431b0817f67aca3960ecad2590fb6d5b13；main=683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead/behind=317/0。接手必须重新查询 branch HEAD/main/worktree。

### 独立决定

**REQUEST_CHANGES / HOLD。** 完整报告：108_D092_R2_2_INDEPENDENT_REVIEW.md。

R2.2 raw/canonical SHA 和 Git blob 均重新计算匹配；13/13 源码 canonical SHA 与 Git blob 全部匹配；R2.1 snapshot 与父提交 canonical R2.1 逐字节一致；R0/R1/R2 未覆盖。Train manifest 96 IDs、R1/R2/R3/R4 各24，6个固定锚点均存在。7-file commit 只修改文档；无新 workflow/check/status/artifact。

### 107 号报告的两项审查勘误

1. d088_policies.py 正确 Git blob 是 afe2ed253704d2bf9f4e3f57f6e0a14f04f14be5；107 中另一 SHA 是审查转写错误。
2. 107 对 Q3 预算 8–12 不可达的判断也错了：推演遗漏 C delayed success 在 dispatch 当场把 C 状态改为 COMPENSATED 后，B primary 可在 C receipt pending 时独立派发。

### 六项结果

- F9 PASS：composite episode/attempt keys 与 receipt lifecycle 闭合；R2.3 需补一句 identity payload 使用 §3.3 同样 canonical JSON 序列化参数（UTF-8、ensure_ascii=False、sort_keys=True、separators=(",",":"), allow_nan=False）。
- F10 PASS（规格层）：total grammar validator + safe sentinel 顺序正确；实现未运行。
- F11 PASS：E 第 j 行为第 j 个 translated extreme point；非对角精确分数与转置反例正确。
- F12 PASS（规格层）：optimizer 仅见单 genome 聚合 fitness/feedback，无 per-scenario reward、scenario_id、episode_reference 或 96-row 数组。
- F13 P03 PASS：P01/P03 的 Q1 初始 fallback 对照可达。
- F13 P07 REQUEST_CHANGES：R2.2 声称 17-action prefix 后 budget=7，但 action 7 的 C delayed success 已在 dispatch 时把 C 状态改为 COMPENSATED，action 8 实际会派发 B primary，不会 WAIT。真实共同 prefix 是 14 actions，随后 budget_remaining=10；P06 threshold4 走 ordinary 选择 B primary，P07 threshold12 走 tight 选择 B alternate。普通分数差 primary−alternate=+2.770802651881641。完整逐步轨迹见 108 报告。
- F15 PASS：直接 Random(seed_integer)，无无参构造/系统熵。
- F8/F14 与预算、五臂、seeds、反馈矩阵、统计门槛均未改变。

### 唯一下一任务：R2.3 两处极小修订

1. 保存 R2.2 immutable snapshot；canonical 103 升级 R2.3。
2. 只修 P07：用 14-action Q3 prefix、budget=10、P06/P07 第一处分叉重写源码证明与 PASS 条件。不得删掉 B primary 在 C pending 时的独立派发。
3. 只补 F9：episode_reference 与 compensation_attempt_id 使用 §3.3 同一 canonical JSON serializer。
4. 不重开其余五项；不改变 96 Train、μ/λ、96 unique、384 cap、五臂、seeds、反馈矩阵、统计门槛。
5. R2.3 完成后仅对两处做定向独立复核。

**R2.3 复核通过后立即进入 Typed Adapter → 静态算法测试 → 合成测试 → 实现一致性审查。**

禁止 probe 960 episodes、genome search、13,824 exhaustive、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑 D-090、修改 main。

维护 README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG、51 数据门禁。记录 R2.2 immutable snapshot 与 R2.3 raw/canonical SHA/Git blob；不得虚报 CI。

---
## D-092 R2.2 定向修复交付（历史状态；已被下方独立复审 supersede）

唯一仓库/分支：`yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`。本轮起始 HEAD=`0ff5f8dd73312d37de681bc3093692cd62596e56`，main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，起始 ahead/behind=316/0、工作区 clean；接手时动态核验最终 HEAD/远端。

### 文件身份

- canonical R2.2：`103_D092_TRAIN_ONLY_PREREGISTRATION.md`；raw SHA=`c0035d0f7236eff03325e81c2b7967ae166bc4c73047e390d502859f6d8fdc5c`，canonical SHA=`f18aecb71791e43220ac74920c67c27141c58eaadfde74fd0190103e0b4695a3`，Git blob=`006aface19258f5d9ba597011dfe9048dfea8897`。
- R2.1 immutable snapshot：`103_D092_TRAIN_ONLY_PREREGISTRATION_R2_1.md`；raw=`104df3497f58171f48e82e25674d1b14e22673a34561d263f8679aadd34648ee`，canonical=`e71027477f49bde939c3a45a1d7327e04d426da4b06a4b4a9a1c41c687916a45`，blob=`773f39e5984c20d011a8d89245ecf52790886088`。R0/R1/R2 均未覆盖。

### 六项定向修复

- F9：episode_reference 纳入 seed/unique ordinal/genome hash/scenario；attempt hash纳入 episode_reference；C/F/D 只用 composite keys；immediate COMPENSATED 与所有 dispatch-final receipts 均关闭 record，TIMEOUT 才保持 open。
- F10：total grammar validator 在任何字典查询前处理 malformed/unhashable/cyclic 输入，安全 `("INVALID",)` sentinel 记账且保留原始 snapshot。**源码 SHA 核验推翻 107 转写：** 正确 blob 仍是 `afe2ed253704d2bf9f4e3f57f6e0a14f04f14be5`，经本地 Git 与 GitHub API 双重确认；不得改成 107 所写不存在的对象。
- F11：E 第 j 行=第 j 个 translated extreme point；加入非对角非对称矩阵、精确分数解/intercepts/normalized vector 和转置反例。
- F12：evaluator-internal rows 与 optimizer 单 genome 聚合对象分离；optimizer 不再收到 scenario_id、episode token、per-scenario class/conditional/correct/avoidable 或任何 96-row 数组。
- F13：P03 比较 P01/P03，在 Q1 初始状态隔离 fallback；P07 比较 P06/P07，在 Q3 精确 17-action 前缀后 budget=7 比较 B primary/alternate。保留 10 genomes×96=960 设计预算；H<2 改名 complete collapse，near-collapse 仅描述。
- F15：直接 `random.Random(seed_integer)`，不再无参构造或 reseed。

F8 mapping、F14 公式、五臂、μ/λ、96 unique、384 attempts、五 seeds、反馈矩阵和统计判据均未改；静态逐字比较通过。

### 实际验证与唯一下一任务

静态/公式检查通过：R2.1 快照身份；13/13 源码 canonical SHA 与真实 Git blob；96 Train IDs/6 anchors；F8/F14及冻结章节不变；144 映射和 P00–P09 展开；P03/P01 与 P07/P06 单机制差异；非对角 E 精确解/转置反例；P07 分数差约2.771；无 OPEN/TBD；diff 格式正确。**没有运行 rollout、算法测试、probe、search、exhaustive 或 Validation/Test。**

唯一下一任务：新独立会话只复核 107 号六项及 blob 勘误。通过后直接进入 **Typed Adapter → 静态算法测试 → 合成测试 → 实现一致性审查**，不再扩大文档审查；实现复审和用户明确批准后才可 Probe/Train-only search。维护时尚无新 CI/artifact，提交后真实查询，历史 CI 不算本轮证据。

---

## D-092 R2.1 独立复审结论与 R2.2 定向修订接管（历史任务；已由上方 R2.2 交付 supersede）

唯一仓库/分支：`yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`。审查基线 HEAD=`ab915751d8bb95d5f3e76b1d1e4c259f9819cfcc`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；ahead/behind=315/0。接手必须重新查询 branch HEAD/main/worktree。

### 独立决定

**REQUEST_CHANGES / HOLD。** 完整报告：`107_D092_R2_1_INDEPENDENT_REVIEW.md`。

R2/R1 快照身份通过：R2 snapshot 与父提交原 canonical R2 逐字节一致；R1 snapshot 前后完全一致。Train manifest 有 96 IDs、四类各24，6个probe锚点均存在。本次 R2.1 commit 只修改 7 份文档；无新 workflow/check/status/artifact。

13 项源码依赖中，12 个 Git blob 匹配；`experiments/d088_recovery/d088_policies.py` 的声明 blob 与实际 blob 不匹配：
- 声明：`afe2ed253704d2bf9e3f4e57f6e0a14f04f14be5`
- 实际：`afe2ed253704d2bf9f3e3f57f6e0a14f04f14be5`

### F8–F15 审查结论

- **F8 PASS（规格层）：** 五字段→D090底层参数映射与绑定源码语义一致；实现唯一性测试尚未执行。
- **F9 REQUEST_CHANGES：** attempt ID 仅由 scenario_id+dispatch ordinal 派生，不同 genome episode 会碰撞；C_t 未明确使用 composite key；立即 COMPENSATED success 缺 terminal-record 规则。
- **F10 PARTIAL：** 状态表主体匹配源码，但 unhashable tool/route 参数在环境 membership 检查中可抛 TypeError；须先由总函数式 grammar validator 安全处理。修复 d088_policies blob。
- **F11 REQUEST_CHANGES：** E_ji 公式表示第 j 行是 extreme point，文字却写第 j 列；对角线 synthetic test 无法发现转置。补非对称非对角期望值。
- **F12 REQUEST_CHANGES：** optimizer allowlist 中 conditional_recovery_success / correct_escalation 的 None pattern 可直接识别 R1/R2/R3/R4；scenario_id 可 join 带标签 manifest。拆分 evaluator-internal reward rows 与 optimizer-visible aggregate fitness。
- **F13 REQUEST_CHANGES：** P03 的 Q1 在 pair_race_alternate=true 时已有 cycle alternate normal routes，fallback 不触发；P07 的 Q3 priority competition 只在 budget=19、14、7 左右出现，不存在预注册的 9–12 差异窗口。必须更换两个可达 anchor/contrast。
- **F14 PASS（规格层）：** 五维 component regret 和 Pareto-front normalized distance 已明确；未执行 exhaustive。
- **F15 PARTIAL：** PRNG/CRN 基本冻结，但 `random.Random()` 无参构造先默认 seed，再 reseed，与禁系统熵不完全一致；优先改为 `random.Random(seed_integer)`。

### 唯一下一任务：R2.2 定向修订

1. 将 canonical R2.1 原样保存为 `103_D092_TRAIN_ONLY_PREREGISTRATION_R2_1.md`。
2. 修订 canonical 103 为 R2.2，只关闭 F9/F10/F11/F12/F13/F15。
3. 不重开 F8 和 F14；不改变 μ/λ、96 unique、384 attempts、五臂、主比较、seeds、反馈矩阵、统计门槛、96 Train scenarios。
4. F13 只用冻结 Train 场景做源码级可达性推演；不运行 960 probes，不按实验结果挑场景。
5. R2.2 完成后进行一次定向独立复核；通过后立即进入 typed adapter + static/synthetic tests 实现审查。

**禁止：** probe 960 episodes、genome search、13,824 exhaustive、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑 D-090、修改 main。

维护 README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG、51 数据门禁。记录 R2.1 immutable snapshot 与 R2.2 raw/canonical SHA/Git blob；不得虚报 CI。

---

## D-092 R2.1 定向修订交付（历史状态；已被下方独立复审 supersede）

唯一仓库/分支：`yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`。本轮起始 HEAD=`fc4d9b8b62aed7fb3abc3e9d4fe3ecbe985c0315`，main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，起始 ahead/behind=314/0、工作区 clean；接手时仍须动态查询最终提交和远端状态。

### 本轮交付与真实身份

- canonical R2.1：`103_D092_TRAIN_ONLY_PREREGISTRATION.md`；raw SHA-256=`104df3497f58171f48e82e25674d1b14e22673a34561d263f8679aadd34648ee`，canonical SHA-256=`e71027477f49bde939c3a45a1d7327e04d426da4b06a4b4a9a1c41c687916a45`，Git blob=`773f39e5984c20d011a8d89245ecf52790886088`。
- R2 immutable snapshot：`103_D092_TRAIN_ONLY_PREREGISTRATION_R2.md`；raw=`c6e4d1103710eef12fa65105721c6295b5875c45003cc3bc13baa601e66c57b5`，canonical=`7f4fb63a9c7ec005d17113ef8c5ddfb48d20bd3f229c947ca67668e5d3a5bc53`，blob=`9196c717f2cb79ecd21a25e055a77afe0db03f59`。R0/R1 未覆盖。
- F8–F15 均已写入可检查的数学/接口/状态定义和边界条件：完整底层 genome 映射与 P00–P09 展开；attempt 一对一回执；六种动作 grammar/mask/转移表；translated E/intercept/scale；两个 reward/audit 接口；逐 probe PASS/HOLD 与 H<2 collapse；五目标 regret/front distance；random.Random API/CRN。
- 不变项：μ=12、λ=12、12+7×12=96 unique、384 attempts、五臂、A3−A1/A3−A4 主比较、五个 seeds、原反馈矩阵和统计门槛。冻结章节与 R2 逐字一致。

### 实际验证与边界

文档/映射静态检查通过：13/13 源码 canonical SHA/blob、96 唯一 Train IDs、6 个预注册锚点、144→144 映射唯一性、P00–P09 全展开、6 个冻结章节逐字一致、无 OPEN/TBD/TODO、`git diff --check` 通过。首次内联检查命令自身的关键字参数错误已修正后完整重跑通过；没有修改实验源码或结果。

**没有实现 adapter/searcher，没有运行算法测试、960 probe、96×96 search、13,824 exhaustive reference、调参或候选冻结，没有访问 Validation/Test。** 规格闭合不等于算法有效、实验通过或创新成立。本轮维护时尚无新 CI/artifact；提交后必须查询真实 run，历史 D-091 CI `44068259009` 不是 R2.1 验证。

### 唯一下一任务

由**新的独立会话**只复核 `106_D092_R2_INDEPENDENT_REVIEW.md` 的 F8–F15 与 R2.1，对照 `experiments/d090_recovery/d090_genome.py`、`d090_policies.py`、`experiments/pilot_a3b/dependency_recovery.py`，检查公式、状态机、信息流和主控制流一致；不得重开已通过的预算/五臂设计，也不得由本轮起草者自批。

定向复核通过后立即进入 typed adapter + static/synthetic algorithm tests 的实现和实现一致性审查，不再做大范围文档重构。实现审查通过及用户明确批准前，继续禁止 probe、genome search、exhaustive reference、Validation/Test、Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑 D-090 和 main merge。

---

## D-092 R2 独立审查结论与 R2.1 定向修订接管（历史任务；已由上方 R2.1 交付 supersede）

唯一仓库/分支：yujian777555/kaitibaogao / pilot-a-stateful-recovery。接手时必须重新查询 HEAD、main、ahead/behind 和工作树。

### R2 身份核验通过

- 审查时 HEAD：3b76e78bb0bd58cb9b812ab7850757bee7cefb07；main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653；ahead/behind=313/0。
- R2 raw SHA：c6e4d1103710eef12fa65105721c6295b5875c45003cc3bc13baa601e66c57b5；canonical SHA：7f4fb63a9c7ec005d17113ef8c5ddfb48d20bd3f229c947ca67668e5d3a5bc53；Git blob：9196c717f2cb79ecd21a25e055a77afe0db03f59。
- R1 snapshot raw/canonical SHA 均匹配；13 份源码 blob/canonical SHA 全部匹配；Train manifest 与 96 个 scenario IDs、R1/R2/R3/R4 各 24 个标签均匹配。
- R2 commit 只改文档；没有新 CI、status check 或 artifact。

### 独立决定

**REQUEST_CHANGES / HOLD。** 完整报告：106_D092_R2_INDEPENDENT_REVIEW.md。

R2 的 mu/lambda/round、OFFER 384 cap、96 unique/9,216 episodes、五臂控制流骨架和 A1/A4 等价规格已基本闭合，不得重新打开这些已解决问题。

必须定向关闭：
1. F8：五字段 typed genome 到 D090Genome 底层字段的完整映射缺失。尤其 fallback_mode=2、completion_mode=1 会使单独关闭 boolean 仍然启用机制；harm budget=None 可能触发类型错误。
2. F9：FAILED observation 可能由 delayed VERIFY 返回或被重复 VERIFY 重复返回；必须按 COMPENSATE attempt 一对一归因，保证 r_t 在 [0,1]。
3. F10：action tuple grammar、RETRY_WORKFLOW preconditions、COMPENSATE public mask、合法 state transition edges 未冻结。
4. F11：NSGA-III E matrix 使用 raw 还是 translated extreme points 不明确；scale=a-z* 可能重复减 ideal point。
5. F12：optimizer_reward_view 与 audit_only_view 未隔离。
6. F13：probe PASS/HOLD 和 phenotype-collapse 阈值没有量化。
7. F14：五目标 exhaustive Pareto reference 的 search gap 未定义。
8. F15：PRNG engine/API 未冻结；同 seed 不含 arm ID 实际是 common-random-numbers coupling，应明确。

### 唯一下一任务：R2.1 定向澄清

1. 将当前 R2 原样保存为 103_D092_TRAIN_ONLY_PREREGISTRATION_R2.md。
2. 修订 canonical 103 为 R2.1，只关闭 106 号报告 F8–F15。
3. 不改 96 场景、96 unique evaluations、μ/λ、五臂、主要比较、种子、统计门槛和反馈矩阵。
4. 只做文档/公式/接口规格与静态/合成测试设计；不得运行 probe、genome search 或 exhaustive reference。
5. R2.1 完成后交独立会话定向复核；通过后立即进入 typed adapter + static/synthetic tests 实现审查，不再开展大范围文档重构。

**禁止：** D-092 searcher/adapter 实现、probe 960 episodes、genome search、调参、候选冻结、exhaustive 13,824 episodes、Validation/Test、Pilot B、正式 A-3b、真实 API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑 D-090、修改 main。

维护 README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG、51 数据门禁。记录 R2 immutable snapshot 和 R2.1 raw/canonical SHA、Git blob；不得声称未触发的 CI 通过。

---

## D-092 R2 独立审查任务（已完成；历史记录）

唯一仓库/分支：`yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`。开始必须 fetch 并核验真实 HEAD、main、ahead/behind 和本地工作树，不得覆盖未提交工作。

### 权威文件与身份

- R2：`103_D092_TRAIN_ONLY_PREREGISTRATION.md`；raw SHA=`c6e4d1103710eef12fa65105721c6295b5875c45003cc3bc13baa601e66c57b5`，canonical SHA=`7f4fb63a9c7ec005d17113ef8c5ddfb48d20bd3f229c947ca67668e5d3a5bc53`，Git blob=`9196c717f2cb79ecd21a25e055a77afe0db03f59`。
- R1 历史：`103_D092_TRAIN_ONLY_PREREGISTRATION_R1.md`；R0 历史：`103_D092_TRAIN_ONLY_PREREGISTRATION_R0.md`。
- R1 审查依据：`105_D092_R1_INDEPENDENT_REVIEW.md`；本轮已逐项处理 F1–F7 和 M1–M4。

### R2 的核心可执行定义

μ=12、λ=12、共享无放回唯一初始 12、7 轮各接受 12 个新唯一 offspring；轮内父代冻结，mutation 单父均匀、crossover 两不同父代，A0 从未评价集合无放回采样。每轮结束才 survivor；A3 反馈仅来自上一轮 12×96=1,152 rows。OFFER 从 attempts=0 开始，384 cap 含初始和所有重复/cache；有效 run 必须 96 unique/9,216 episodes。

canonical NSGA-III 使用完整 ASF、极端点、零跨度处理、35 方向唯一排序、最后 front、niche=0 最近距离和 niche>0 seeded 随机选择。blocked contract/dependency 为 soft 回执，硬约束只有 invalid、unauthorized、实际非法转移、pending、duplicate、runtime abort 六类。

允许完成 Train rollout 后的 evaluator reward，不允许预读 label/hidden schedule。原 e_t 改名 unsuccessful escalation rate。三类 phenotype canonical hash 已定义；probe 为 10 genomes×96=960 独立 episodes；穷举参考为 144×96=13,824 episodes，均不参与调参。无效 seed/NO_FEASIBLE 导致相关比较 NO_CLAIM，不替换 seed。A1/A4 必须逐轨迹等价。目标 runtime 为 CPython 3.11.9、NumPy 1.26.4、Ubuntu 22.04 x86_64。

### 验证边界和唯一任务

静态检查已覆盖全部 F/M 项、预算、公式、13 份源码哈希和 R1 保留，无 OPEN/TBD。没有实现 adapter/searcher，没有执行 probe、算法测试或 genome search。本轮无新 CI/artifact；历史 D-091 CI `44068259009` 不是 R2 实验批准。

**唯一下一任务：** 独立审查 R2 的控制流、预算、canonical NSGA-III、反馈边界、硬约束、probe/hash、统计和 runtime lock，给出 ACCEPT 或 REQUEST CHANGES。不得由修订者自行批准。审查后仍需实现授权、实现一致性复审及用户明确批准；此前禁止实现/运行 D-092、probe、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 API、A800/ARWM 和 main merge。

---

## D-092 R1 独立审查结论与 R2 修订接管（2026-11-17；REQUEST_CHANGES / HOLD）

唯一仓库：yujian777555/kaitibaogao；唯一分支：pilot-a-stateful-recovery。不得读取或混用其他仓库。

### 审查基线

- R1 审查时 branch HEAD：7a94d9711fa792e76d710d48f5cfc562e0c5a072
- main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653
- ahead / behind：310 / 0
- R1 blob：f5dc28e67d648344cfd8465956f51e1f0582baf4
- R1 raw SHA-256：2b67f64a20ffe622264ee97629db7d587f56005e7f551ff59bef4b3b29099ec5
- R1 canonical SHA-256：3a5ad0f108c79bc5fb71529d22d774f4776206c2db42022a994d1893fa1fdc55
- R0 已确认与 R1 修订前父提交中的原始 103 文件逐字节一致。
- 最新既有 D-091 CI：44068259009 success；不是 R1 CI。R1 commit 无新 workflow run。

### 独立核验通过项

13 份源码 Git blob SHA 与 canonical SHA-256 全部匹配；D-090 Train manifest hash 匹配；96 个唯一 scenario IDs、5 个 probe anchors 和 96-ID probe hash 均复核通过。R1 raw/canonical SHA 也重新计算匹配。

### 独立审查决定

**REQUEST_CHANGES / HOLD。R1 不接受；不批准实现或实验。**

权威报告：105_D092_R1_INDEPENDENT_REVIEW.md。

必须修订的阻断项：
1. 搜索控制流缺少 mu/lambda/offspring round、父代选择、A0 随机分布；因此 A3 的反馈集合 U_t 无法唯一计算。
2. 384 attempt cap 的定义包含 initialization，但伪代码没有对 12 个初始 proposal 计数。
3. NSGA-III niching、ASF、零跨度 normalization fallback、参考方向顺序不完整，不能直接称 canonical。
4. DEPENDENCY_BLOCKED/CONTRACT_BLOCKED 是合法 COMPENSATE 请求的环境拒绝回执，不是非法状态转移；hard constraint 和 unauthorized action 必须重新定义。
5. feedback 的 class_success/avoidable_harm 是 label/hidden-outcome-derived evaluator reward；必须明确允许 post-rollout reward，或替换为纯可观察特征。
6. phenotype/outcome hash canonical schema 与 probe rollout 数量/预算缺失。
7. 无效 seed、NO_FEASIBLE_CANDIDATE 和 4/5 统计条件的处理不完整。

同时解决：
- A1/A4 理论上相同，应增加 trajectory equivalence check；
- 当前 genome space 只有 144 个组合，96 evaluations 覆盖 66.7%，应说明为何仍需 EA，考虑独立 Train-only exhaustive oracle；
- Python patch/runtime lock；
- §8.1 五类 hard constraints 与 §10 “六类”字段不一致。

### 唯一下一任务：修订为 R2

1. 将当前 R1 原样保存为 103_D092_TRAIN_ONLY_PREREGISTRATION_R1.md。
2. 将 canonical 103 修订为 R2，关闭报告 F1–F7，处理 M1–M4。
3. 只做文档、公式、预算和算法规格修订；不得实现搜索器或 adapter。
4. R2 完成后交新的独立会话复审。

**在 R2 独立审查和用户明确批准前，禁止：** D-092 搜索器/adapter 实现、probe rollout、genome search、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox、main merge。不得重跑 D-090。

本地工作树状态必须由执行者本地检查；远端 GitHub API 不能证明本地 clean。每次文档更新继续维护 README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG、51 号计划。

---

## D-092 R1 独立审查任务（已完成；历史记录）

你接管唯一仓库 `yujian777555/kaitibaogao` 的唯一工作分支 `pilot-a-stateful-recovery`。开始必须 fetch 并核验真实 HEAD、main、ahead/behind、工作树和未提交文件；不得丢弃执行者已有工作。

### 本轮权威材料

1. `103_D092_TRAIN_ONLY_PREREGISTRATION.md`：R1 canonical 协议；raw SHA=`2b67f64a20ffe622264ee97629db7d587f56005e7f551ff59bef4b3b29099ec5`，canonical SHA=`3a5ad0f108c79bc5fb71529d22d774f4776206c2db42022a994d1893fa1fdc55`。
2. `103_D092_TRAIN_ONLY_PREREGISTRATION_R0.md`：历史草案，raw SHA=`3d0b0d0e22d5cfd676ddb8ff7feadaf2dfc9dd7981c0d50920fcf5dd1bf9f367`。
3. `104_D092_INDEPENDENT_REVIEW.md`：R0 的 REQUEST_CHANGES 依据。
4. `101_D091_EXECUTOR_PROMPT.md`、`102_D091_INDEPENDENT_AUDIT_RESULT.md` 与 D-091 artifact：历史事实与数据限制。

### R1 已固定的核心设计

- 仅 D-090 的 96 个 Train 场景；绑定 manifest、环境、evaluator、策略、genome 和 selector 的完整真实哈希；任何不匹配即 INVALID。
- 每臂每 seed 恰好 96 个完整 unique genome evaluations（9,216 episodes）；384 proposal-attempt cap；重复/cache 不占真实 rollout，不足即 INVALID。96×96×5×5=230,400 只是设计上限。
- A0 独立 Random、A1 NSGA-II、A2 完整 NSGA-III、A3 动态反馈、A4 真零反馈。主比较 A3−A1；其余为 A1−A0、A3−A4、A2−A1。
- typed genome 五字段与全部 96 场景 probe panel；反馈六项特征、固定矩阵、β=2、τ=.25、ε=.1，零反馈严格均匀；完整 selector/RNG/日志规格。
- 硬约束不可补偿；最终从 unique feasible archive 的 Pareto 集使用统一字典序。R3 探索性阈值 1/24、至少 4/5 seeds 同向，不删除不利 seed。

### 静态证据与限制

13 份源码 canonical SHA/Git blob、manifest/probe 哈希、预算算术、反馈零向量、R0 保留及文档结构均已静态核验。无 OPEN/TBD 占位。没有实现搜索器、运行算法测试、启动 genome search 或产生候选。本轮无新 CI/artifact；历史 D-091 CI `44068259009` 和 artifact `14321023302` 是既有证据，不是 R1 实验批准。

### 唯一下一任务

由独立审查者逐项审查 R1 的 B1–B8、数学正确性、真实源码相容性、预算公平性、零反馈、完整 NSGA-III、硬约束、统计边界和日志可复原性，给出 ACCEPT 或 REQUEST CHANGES。不得由起草者自行宣布通过。

**状态只能是 READY_FOR_INDEPENDENT_REVIEW，不能写成 APPROVED_FOR_EXPERIMENT。** 独立审查后仍需实现授权、实现一致性复审及用户明确批准。此前禁止实现/运行 D-092、调参、候选冻结、Validation/Test、Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox、重跑 D-090 和 main merge。

---

## D-092 独立审查后的 canonical 接管状态（2026-11-17；优先于下方 D-091 历史提示）

你接管的唯一仓库是 `yujian777555/kaitibaogao`，唯一工作分支是 `pilot-a-stateful-recovery`。严禁读取、引用或混用用户其他项目。

### 审查基线与提交记录

- 审查开始时 branch HEAD：`ae920581a6da9d974ad8bd2d06cfd1ec6b07aabc`
- main HEAD：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`
- 审查开始时 ahead / behind：306 / 0
- 首个审查文档提交：`fe53c9fa724ff2c609a3a0c5ef5da199fc8e61d8`；该提交后 ahead / behind 为 307 / 0
- 随后有一次仅修正 canonical prompt 重复标题和审查基线表述的文档提交；因此**接手时必须动态查询当前 branch HEAD 与 ahead/behind**，不要把上述 SHA 当作永久最新值。
- 最新 D-091 CI：run `44068259009` = success，测试代码 head `5cde039c73b0a5d83fd6d0d7b3816e20f22f0f9b`
- 当前本地工作树状态必须由执行者在本地重新检查，不能从 GitHub API 推断。

### D-091 独立审查结论

读取 `104_D092_INDEPENDENT_REVIEW.md`、`102_D091_INDEPENDENT_AUDIT_RESULT.md`、`103_D092_TRAIN_ONLY_PREREGISTRATION.md`、`101_D091_EXECUTOR_PROMPT.md` 和 `experiments/d090_recovery/results/d091_audit/`。

- D-090 三份原始 JSON 和已保存 15×96 search best rows、5×96 ablation rows 的指标复算一致，最大差异 0。
- `random` 与 `nsga2` 实际同路径；`state_evo` 仅静态 mutation profile；真实 proposal/cache/generation/operator 历史无法从 best-only trace 审计。
- 15 个 best candidates 在 96 个 Train 场景上有 8 个 genome、1 个 trace/outcome phenotype；仅对该保存集合成立。
- g03-r2 的 23-step witness 成功，BFS 最短为 21；撤回旧 25-step 下界。
- P1 整体 Harm 退化；P2/P4 存在 pending 硬约束违规；P3 未修复 g03。
- D-091 仍为 `D091_PARTIAL / HOLD`，因为完整搜索过程不可审计，不得声称 EC 提升。

最新重复 CI artifact：`14321023302`，digest `sha256:925f1f5cc14f1b8c3d0678e2b03d67c891f6d13996b3def928ac182cf17aee03`，到期 `2027-02-15T10:48:46Z`。已下载 ZIP 哈希与 GitHub digest 一致，内部 12 个 output-manifest 文件逐项 SHA/字节数一致。

### D-092 审查决定

**`REQUEST_CHANGES / HOLD`。不批准 D-092 搜索代码实现、预注册冻结或实验运行。**

103 号方案仍有 B1–B8 阻断项，详见 104 号报告：
1. 未锁定 Train manifest / evaluator / environment 不可变 SHA；
2. proposal slots 与 unique evaluations / real rollouts 预算单位混淆；
3. 未冻结主要对照、主要终点和 GO/NO-GO 判据；
4. typed genome 与 phenotype probe panel 未定义；
5. feedback feature mapping、beta、tau、归一化、概率边界与更新统计 OPEN；
6. canonical NSGA-II/III、reference implementation、RNG streams 和测试 OPEN；
7. 硬约束 comparator、infeasible 排序和最终 lexicographic 选择顺序不完整；
8. 资源账本、phenotype gate、失败/无效 run 的停止规则不完整。

### 唯一下一任务

只将 `103_D092_TRAIN_ONLY_PREREGISTRATION.md` 修订为 R1，逐项关闭 104 号报告 B1–B8；只做协议、公式、预算、编码和静态测试规格。R1 交独立会话复审并等待用户明确批准。

**在新的独立审查与用户明确批准前，禁止：** D-092 搜索器实现、genome search、调参、候选选择/冻结、Validation、Test、Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox、main merge。不得重跑 D-090。

### 本仓库维护制度

每轮实质性研究/代码/实验/协议/决策变化，同轮更新 README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG 和 51 号计划；提交后核验远端 HEAD、main、ahead/behind、真实 CI 和 artifact。不得声称本地工作树 clean，除非实际执行 git status。

---

<!-- Historical D-091 handoff begins below; current authority is the D-092 block above. -->

## D-091 完成后的独立审查提示（2026-11-17）

你接管 `yujian777555/kaitibaogao` 的 `pilot-a-stateful-recovery` 分支。先同步远端并核验 HEAD、main、ahead/behind 和工作树，再完整阅读 `102_D091_INDEPENDENT_AUDIT_RESULT.md`、`103_D092_TRAIN_ONLY_PREREGISTRATION.md` 与 `101_D091_EXECUTOR_PROMPT.md`。

**已完成的实际审计：** D-090 原始三 JSON 和全部保存指标独立复算一致；`random` 实际与 NSGA-II 同路径，`state_evo` 只有静态 mutation profile，真实 proposal/cache/generation 历史不可复原；15 个 best candidates 的 8 个 genome 在 96 个 Train 场景上只有 1 个 phenotype。g03-r2 的 23-step witness 真实成功，BFS 最短为 **21**，25-step 下界撤回。P1 整体 Harm 退化，P2/P4 带 pending ESCALATE，硬约束不可接受。

**状态与证据边界：** D091_PARTIAL / HOLD。原始 best_rows 数值可信，但五种搜索方法的公平比较无效，完整搜索过程为 NOT_AUDITABLE_FROM_SAVED_TRACE；不能宣称 EC 提升或形成冻结候选。D-092 只是 NOT FROZEN / NOT RUN 设计草案，反馈系数、行为表示、canonical NSGA-III 与预算可达性仍有 OPEN 项。

**验证：** 本地 456/456；最终审计代码 `e5d13f60b30910d6c6b0c10d99f66227b125fb59` 的 CI `44067543678` = success。Artifact `14320134130` 已下载复核，digest=`sha256:d5504a81fe0e56a828ec617571ba82788a53fcc9393ef122165162116f4eca57`。两个早期失败 run 的日志均保留；不得把它们写成成功。

**唯一下一任务：** 由新的独立审查会话复核 102、103 和 `experiments/d090_recovery/results/d091_audit/`，决定是否批准 D-092 的 Train-only 实现/实验设计。未经明确授权，不实现或运行 D-092，不进行新 genome search、调参、候选冻结、Validation、Test、Pilot B、正式 A-3b、真实 LLM/API、A800/ARWM、UndoBench TEST、ThinkingBox 或 main merge。

---


## D-091 接管任务（2026-11-16）

你接管 `yujian777555/kaitibaogao` 的 `pilot-a-stateful-recovery` 分支。先读 `100_D091_D090_EVIDENCE_AUDIT_AND_SEARCH_IDENTIFIABILITY.md` 和 `99_D090_PAIR_RACE_RULE_SEARCH.md`，后者为 D-090 原始研究报告。

**当前事实：** D-090 使用 6 families/96 Train-only scenarios。五种搜索方法均报告 R3=.875、R4=1.000、Harm=.042、硬约束违规=0；每方法 96 unique genome evaluations、3 paired seeds。固定消融中 P1 g03 局部改善但 Harm=.479、R4=.917；P2 Harm=.146 但有 2 项硬约束违规。g03 r2 被报告为 24 步合同下 25 步下界。没有冻结候选或 Validation 授权。

**CI：** run `43881534809` regression success，`Test d090_recovery` step success；已列 artifacts 不含 D-090 专属结果包。不要把回归测试通过写成实验账本独立复算通过。

**唯一任务：** 完成 D-091：原始账本 SHA/完整性与指标独立复算；逐 seed/family 复算；五方法算法身份、算子调用、预算公平、genome/phenotype 等价与聚合碰撞审计；r2 25 步下界证明；P1/P2 轨迹安全复核。不得重跑 D-090、启动新搜索、调参、冻结候选、访问 Validation/Test、启动 A800/真实 LLM API 或修改 main。

审计结束后只提出 D-092 的 Train-only 预注册方案。不要把演化优势写成既定结论。每轮更新 README、SESSION_HANDOFF、NEXT_SESSION_PROMPT、05_DECISION_LOG 与 51 号计划，并核验提交和 CI。

---

> **D-087 实际复制结果（2026-11-12）：** 92 号经 93 号补齐执行参数后执行；五个原 NSGA-III 候选完全冻结，冻结 SHA=`31495e830da326778b44398a649e2614416451107fdea982530378b4abc6244c`。新 Validation 4 families/80 scenarios，SHA=`d2cdc1aa697592e2439b5a8d5dd354726d3b8dc74e4f215530f0d4c575d88ed8`，无 Train/Test。共 1,040 次评价、无缓存复用、无 Train 搜索。
>
> **结论：REPLICATION_FAILED / NO-GO。** 五候选均为 R3=R4=0.85、CondRecSucc=1、成本 8.85、硬约束 0，0/5 通过。成本虽低于 Greedy 的 20.0，但恢复主终点失败，不得宣称跨 family 优势。rv01 全成功，rv02/rv03/rv04 的 repeat 4 因延迟失败补偿与冻结确认节奏耗尽预算；duplicate/pending 均为 0。
>
> **独立验证：** 原始 JSON/CSV、预算、候选指纹、family 指标、判据和 canonical artifact 哈希全部独立复算通过。完整回归 398+28=426；最终 CI `43156190408` = success，artifact 已下载复算。首次输出/审计及 raw 哈希 CI 失败均保留；不改变任务、阈值、候选或统计口径。证据见 `95_D087_CI_EVIDENCE.json`。
>
> **唯一下一任务：** 独立复核 `94_D087_REPLICATION_RESULT.md`、93 号协议和失败机制，决定路线是否终止；不启动新优化、训练、Test、正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 或 main merge。
>
> **仓库纪律：** 工作分支 `pilot-a-stateful-recovery`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。每次提交后核验远端 SHA、ahead/behind、工作区和真实 CI，不以旧 run 替代。

> **D-087 冻结状态（2026-11-12）：** 92 号已由 `93_D087_PROTOCOL_REVIEW.md` 审查并补齐执行参数；新 Validation 80 scenarios/4 families，SHA=`d2cdc1aa697592e2439b5a8d5dd354726d3b8dc74e4f215530f0d4c575d88ed8`，无 Train/Test。五个原 NSGA-III 候选已冻结，SHA=`31495e830da326778b44398a649e2614416451107fdea982530378b4abc6244c`，没有新搜索或修改 genome。复制上限 1,040 episodes，前置协议测试 4/4。
>
> **唯一下一任务：** 执行一次冻结复制，保存所有候选/基线原始轨迹并独立复算；不得重训、重选、追加预算或访问 Test。复制结果尚未产生，正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。
>
> **仓库纪律：** 工作分支 `pilot-a-stateful-recovery`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。每次提交后核验远端 SHA、ahead/behind、工作区和真实 CI，不以旧 run 替代。

> **D-086 实际探索结果（2026-11-11）：** 8 个搜索/消融臂×5 seeds=40 runs、316,416 行原始账本，独立审计全部通过。普通 NSGA-III 在五 seeds 上 R3/R4/CondRecSucc=1、硬约束为 0、平均成本 5.0，低于 Greedy 的 15.1667，且不劣于 Random Search/NSGA-II。**只是探索性 EC 信号，不是确认性创新。**
>
> **Full 明确 NO_GO：** Full C-NSGA-III R3 均值 0.9、成本 5.6，未满足 `r3_all_one` 和 `no_regression_vs_ea`，不得用平均成本掩盖其落后普通 NSGA-III。NoAlternate 和 NoPendingVerification 显著破坏恢复，NoFailureFeedback 成本上升，NoDependencyPriority 贡献未识别。
>
> **非封顶机制：** 新 manifest Train=72、Validation=24，SHA=`362e7a8a0acafbb40f6ddccf207bede85a656193c6544bf3cd949c1fe43ffd67`。公开依赖、备选路径、可靠性/成本和确认预算形成真实策略差异；固定门 768 行，无共同支配方法。
>
> **失败证据：** 首次 JSONL 失败目录保留，split 缓存键已修复。审计初版错误要求跨 seeds 同池的失败报告也保留；修正后预算、账本、选中指标与判据全部一致。本地完整回归 385+28=413；结果提交 `5210d1c40fbb41b39a51e2ef7ef544e582dc4af5` 的 regression run `43033472661` = success。
>
> **唯一下一任务：** 按 `92_D086_INDEPENDENT_VALIDATION_PREREGISTRATION.md` 对已冻结普通 NSGA-III 候选做新 Validation family 复制评价；不重训、不追加预算、不访问 Test，复制实验 NOT RUN。正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。
>
> **仓库纪律：** 工作分支 `pilot-a-stateful-recovery`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。每次提交后核验远端 SHA、ahead/behind、工作区和真实 CI，不以旧 run 替代。

> **D-086 当前阶段（2026-11-11）：** 新独立非封顶模型与固定策略门已完成，实际 EA 尚未运行。新 manifest Train=72、Validation=24，SHA=`362e7a8a0acafbb40f6ddccf207bede85a656193c6544bf3cd949c1fe43ffd67`；8 个固定方法产生 768 行原始数据，无固定方法在两个 split 共同支配其他方法。
>
> **关键结果：** Greedy Train R3=18/18、成本14.00，Validation R3=6/6、成本15.17；AdaptiveProbe/CostAware Validation 未全通过。长链确认场景呈现可靠路径—成本—等待预算的真实权衡，不是标签/隐藏信息错误。
>
> **冻结实现：** `90_D086_EVOLUTION_PREREGISTRATION.md` 规定 12 个体、6 代、5 seeds、84 候选和 6048 episode-equivalent/arm/seed。`dependency_genome.py`、`dependency_evolution.py` 已实现单字段变异、NSGA-II/III、可行性优先、预算缓存和冻结选择；只做专项合成测试，未运行 manifest EA。
>
> **首次执行失败与修复：** JSONL 误写多行 JSON，校验失败；原目录保留为 `d086_evolution_failed_pretty_jsonl/`，未计为有效实验。已修复逐行序列化与 split 缓存键，新增回归防止 Train 行复用为 Validation。
>
> **唯一下一任务：** 用修复后的冻结实现重跑一次 Train/Validation 探索并独立复算；不改任务、阈值、seeds 或基线。实验 workflow 仅 `workflow_dispatch`，不随 push 重跑。正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。

> **D-086 / Task 1（2026-11-11）：** `88_D085_INDEPENDENT_REVIEW_D086.md` = **ACCEPTED_WITH_LIMITATIONS**。D-085 的 96 行机制、192 行封顶和 manifest 重生成一致，33 项复算通过，无隐藏信息/gold label 入策略，Train/Validation family 无交集，基线回归 369/369。
>
> **当前唯一下一任务：** 建立独立的新状态转移模型，验证公开补偿依赖、异构可靠性、不确定回执与真实成本的自然策略差异；固定策略非封顶门通过前不运行 NSGA-II/III。旧环境中顺序不改变结果、重试只读缓存、验证只读回执；下一协议将 ESCALATE 与 STOP_SAFE 分账。Test、正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。
>
> **仓库纪律：** 工作分支 `pilot-a-stateful-recovery`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。每次提交后核验远端 SHA、ahead/behind、工作区与真实 CI，不以旧 run 替代。

> **最新权威状态（2026-11-11，D-085）：** 唯一仓库 yujian777555/kaitibaogao；工作分支 `pilot-a-stateful-recovery`；实现提交 `34d76c68c9370fa0c93095c36ea4b4f0ecd8bedf`；R4 自动证据提交 `fd66ad8c3a6fcc678936fcf533f8f69ba553570a`；main=`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，未修改。最终维护 SHA 与远端状态仍须在接手时重新查询。
>
> **R4：** `85_D064_R4_INDEPENDENT_REVIEW_R2.md` = ACCEPTED，仅限代码与协议复审，不是正式 A-3b 批准；导师 MDE、用户批准和真实 pre-flight 仍是独立硬门。
>
> **Prefix 机制已实现并合成验证：** 原 Hand 遗漏已提交前缀的补偿顺序。修正后的 PrefixAware 在 D5/R3=24/24、D6/R4=24/24 且达到最小残余，Hand 两组均 0/24；96 行原始数据与独立 CSV 复算一致。公开状态不含隐藏故障、延迟或运行时内部提交状态。标签反例已保守修正，D-079 v2 SHA 保持 `09df6babbb6e3222ea57a7f354654636ac2437b7011dbe3f1ac738df894a0bca`。
>
> **新数据与封顶门：** Train=72、Validation=24，family 不相交，manifest SHA=`cf769671873c594ec73e9a9e7df75bf1774135af6745da54b3411fb08c45d492`，lock=`experiments/pilot_a3b/prefix_manifest_lock.json`。固定 Prefix 在新 Train/Validation 全部类别成功、零可避免伤害、零硬约束违规，故当前集合不能证明 EC 增益。优化器 runs=0；Test 未生成、未读取，精确 roster 与保管承诺为 OPEN。
>
> **验证：** 本地与 CI 完整回归均为 341+28=369 全通过。CI regression `43013066595`、R4 power `43013066576`、Pilot A recovery `43013066525` 均 success；D-085/R4 artifact 已下载复核。证据见 `experiments/pilot_a3b/results/d085_ci/verification.json`。同提交本地干净克隆通过；GitHub clean-clone 两次网络超时，未验证成功。
>
> **当前唯一任务：** 新独立会话审查 `86_D085_R3_PREFIX_MECHANISM_AUDIT.md`、`87_PREFIX_AWARE_EXPERIMENT_PREREGISTRATION.md`、最终实现、原始 CSV 和封顶门。审查前不得运行新优化器；不得把固定规则可行或工程测试通过写成算法创新。
>
> **授权边界：** 不运行正式 A-3b，不读 Test，不启动 Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST 或 ThinkingBox；不合并 main。保留 D-078、D-079 及本轮修复前全部 artifact。
>
> **维护纪律：** 每次实质性研究、代码、实验、协议、审计或决策变化，同轮更新 NEXT_SESSION_PROMPT.md、SESSION_HANDOFF.md、05_DECISION_LOG.md、README.md 和 51 号计划。每次回复报告 canonical handoff 是否更新并提供 GitHub 文件链接。

---

## 直接复制给下一会话的完整提示词

你是我的河北工业大学计算机技术硕士毕业论文研究 Planner + GitHub 仓库维护者。你的任务是推进研究、执行可授权的仓库操作、审查实验可信度，并持续维护长期会话交接信息。不要只写计划或提示词；在证据允许时直接完成代码、测试、实验、复算和仓库更新。

### 1. 仓库隔离与 Git 纪律

唯一允许读取和维护的毕业论文仓库：

`https://github.com/yujian777555/kaitibaogao`

- 当前工作分支：`pilot-a-stateful-recovery`。
- `main` 必须保持独立；未经明确授权，不得合并实验分支。
- 严禁读取、引用或混用用户其他 GitHub 仓库/项目。
- 每次开始先查询远端工作分支和 main 的真实 HEAD、比较 ahead/behind、检查工作流状态；不能只信本提示词中的历史 SHA。
- 所有修改在工作分支进行；每次提交后核验远端 commit、文件内容和分支差异。
- 不得将“文件已写入”“测试用例已编写”“CI workflow 已配置”表述为测试通过或实验完成。

记录基线（2026-11-06 Phase A 完成时最后一次核验）：
- 工作分支 HEAD（Phase A 提交后）：以 `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`（A-3 崩溃修复）之后的审计/文档提交为准，见维护记录
- main HEAD：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`
- 工作分支相对 main：ahead 82+ / behind 0
- A-3 被审计 CI run：42241224898，head SHA `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`，结论 success
以上只是历史基线；接手后必须重新查询。

### 2. 研究背景与方向边界

- 用户是河北工业大学计算机技术硕士，导师要求演化计算（EC）是核心方法，并希望纳入 RSI（递归自我改进）。
- 用户希望毕业论文形成 2–3 个创新点，并尽可能各自形成小论文；每个创新点必须先逐一验证，不能为了凑数量保留失败方向。
- TCAIL Estimator Gate 已 FAIL / NO-GO；旧 CI-GOM linkage 路线冻结，保留负结果，不得继续把它当作当前主线。
- 当前候选主线：**状态化工具型 LLM Agent 的故障恢复策略演化与 RSI**。
- 当前重点问题：在有状态、多工具、存在部分提交/延迟可见/超时歧义/补偿失败的工具工作流中，演化计算能否找到超越强手工恢复策略、且在未见任务与故障组合上保持安全的恢复控制器？
- 第二候选：故障场景与恢复策略双种群协同演化；暂缓，必须先有第一项 EC 增益证据。
- A800 训练 ARWM 是条件候选，不是当前已批准工作。必须先证明模型预测质量和固定真实 simulator rollout 预算下的 EA 收益，才可申请训练。
- 用户的 LLM 使用方式是 API 调用；模型 API 与 A800 辅助模型是不同组件。当前不得擅自启动真实 LLM API。
- 不得把 RSI 仅画成循环框图；最终需要跨轮故障发现、策略更新、再验证及未见任务改进证据。

### 3. 已完成工作与证据边界

#### Pilot A 首轮
- 曾发现 unresolved 指标错误，已在 D-049 修正；不得引用旧 unresolved 值。
- 复算正确 unresolved：blind retry 0.8571、verify-then-retry 0.5714、wait-verify-retry 0.4429、conservative escalation 0.0857、state-aware 0、oracle 0。
- state-aware 手工策略与 oracle 在 success/safety 上持平，主要差异在动作成本；不足以直接授权大规模 EA 或 ARWM。

#### Pilot A-2
- 四类双工具任务、九类故障、六种策略；每种策略 1,080 episodes，共 6,480 policy episodes。
- contract-aware success 0.7222、safe 1.0、invariant violation 0；oracle diagnostic success 0.7778、safe 1.0。
- 5.56 个百分点差距只是探索性模拟器信号，不是统计显著性，不是 EC 增益，也不是论文创新证据。
- A-2 的缺陷：同一任务的工具共享故障族；缺少 held-out task/fault composition。
- 旧 CI run 42030194929、42030392313 只证明当时 A1/A2 工作流成功；**不能证明后来加入的 A3 已通过 CI**。

#### Pilot A-3 当前实现
已加入：
- `47_PILOT_A3_PROTOCOL.md`：A-3 预注册协议及 Pilot B 门禁；
- `experiments/pilot_a_recovery/pilot_a3.py`：独立 per-tool fault vector、三步 saga、不同工具幂等/补偿契约、partial commit、delayed visibility、rate limit、schema drift、permission denial、compensation failure、逆序补偿、七种策略、held-out cluster bootstrap；
- `experiments/pilot_a_recovery/test_pilot_a3.py`：当前 15 项测试用例；
- `experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md`：实现状态和验证边界；
- `.github/workflows/pilot-a-recovery.yml`：增加 A3 执行及 JSON/episode CSV artifact 上传；
- README、D-051、SESSION_HANDOFF 已更新。

冻结预算：
- 每策略 954 episodes：train 144、validation 120、held-out 690；
- 七种策略共 6,678 policy episodes；
- Held-out 分为 task-only、fault-only、joint shift；
- 所有策略共享 scenario IDs、seeds、fault realizations；
- 策略只可访问公开错误、工具契约、VERIFY/WAIT 结果；隐藏故障标签、真实可见时间、补偿可用性不得泄漏给可部署策略；
- oracle_diagnostic 仅是当前步骤潜在状态可见的诊断参考，不是可部署策略，也不保证全局最优。

七种策略：
1. blind_retry
2. verify_then_retry
3. fixed_wait_verify
4. conservative_escalation
5. contract_aware
6. saga_aware
7. oracle_diagnostic

**真实状态必须如实表述（2026-11-06 更新）：**
- SPECIFIED：A3 协议已冻结（47 号，未修改）。
- IMPLEMENTED：模拟器、16 项测试（15 预注册 + 1 崩溃回归）、CI workflow step 和 artifact 上传步骤在分支上。
- TESTED：run 42241224898（head `f5e6b46`）28 项测试全部通过，A1/A2/A3 模拟器全部真实运行；此前 7 个 run 因 `PublicToolView` 误读 `tick` 崩溃（已修复）。
- RESULTS：A-3 已运行并经独立复核（`PILOT_A3_INDEPENDENT_REAUDIT.md`）：6,678 episodes、结构/配对/split/语义全部通过审计、JSON 与 CSV 零偏差、artifact 哈希齐全、本地重跑确定性一致。
- GATE：**A-3 预注册 Gate = HOLD（HOLD_REVIEW_FAILURE_BOUNDARIES）**。三条件中安全条件满足（各 slice 零违规），但 oracle−saga 成功率差 0.0（要求 ≥0.05）、bootstrap CI [0.0,0.0]（要求下界 >0）；gap≤0.02 但动作成本差 +34.6%>10%，按 47 号原文为 HOLD。**Pilot B 未获准**；A800/ARWM、真实 LLM API、双种群协同演化继续 HOLD。

### 4. 当前唯一下一任务：A-3b 独立审查 → 预注册冻结 → 实现（分类器/场景生成器/adapter）

Phase A（A-3 复核，Gate=HOLD）与 Phase B（数据集审计）均已完成，A-3b 设计草案见 `55_PILOT_A3B_RESEARCH_DESIGN.md`。不要重跑 A-3，不要启动 Pilot B，不要运行 A-3b（未预注册）。按顺序执行：

1. 重新核验远端 `pilot-a-stateful-recovery` 与 `main` HEAD、ahead/behind、工作树、CI 状态。
2. **对 55 号设计做独立审查**：可恢复性四分类的可判定性、指标分母纪律、统计方案（cluster bootstrap+置换+Holm）、预算公平性、与 49 号新颖性边界的一致性、消融能否分离 A/B 机制。发现问题先改设计文档，不带病冻结。
3. **预注册冻结**：场景生成器规格（含 R3/R4 分层比例 3:1 主设定与 1:1、5:1 敏感性）、τ_min=saga_aware 基线、成本计价表、seed 清单、rollout 预算、场景清单哈希。冻结后经用户批准才允许运行。
4. **实现**（批准后）：可恢复性分类器（评估器侧，含一致性回归测试与 10% 人工抽检）、场景生成器扩展（新组合族含可区分恢复决策点）、FSM 基因组+语义修复算子、反例池。全部沿用 PublicToolView 观察边界（隐藏标签隔离测试保留）。
5. **Phase C adapter（可与 3 并行）**：ToolMisuseBench `reset()/act()` 与 UndoBench `UndoBenchAgent.run()` 到统一 episode contract 的封装；只用 train/dev/validation smoke（ToolMisuseBench DEV 复现报告已在 `experiments/dataset_audit/`）；UndoBench TEST 与 ToolMisuseBench test_public 继续锁箱。
6. 运行 A-3b 前置门禁：分类器一致性、泄漏检查脚本、预算表齐备、55 号审查通过。缺一项不得开跑。
7. Pilot B 预注册草案仅在 A-3b Gate + 数据兼容 Gate + adapter smoke 全过后起草。A800/ARWM、真实 LLM API、UndoBench TEST 执行、ThinkingBox 任何用途、双种群协同演化继续 HOLD，均需独立授权。

### 5. 强制接管提示词维护制度（不可违反）

每次会话、每个阶段结束、每次实验结论/代码/协议/分支/授权变化时，必须维护以下四处：

1. **`NEXT_SESSION_PROMPT.md`：唯一权威、可直接复制的接管提示词。** 更新当前仓库/分支/HEAD 基线、真实阶段、已完成证据、未完成事项、唯一下一任务、门禁、禁止事项和必要文件路径。它必须自包含，使新会话不依赖旧聊天也能正确接管。
2. `SESSION_HANDOFF.md`：详细历史、阶段记录和上下文；保留旧记录，追加新阶段，不得静默覆盖负结果。
3. `05_DECISION_LOG.md`：新增带日期的决策，记录证据、判断、限制和下一步；区分事实、推断和计划。
4. `README.md`：维护当前项目状态、当前分支/阶段、最新结论和下一步。

执行纪律：
- 每次提交代码或实验结果后，同一轮更新以上四处，不得留到“以后再说”。
- 如果任务中途改变了方向/门禁/下一步，必须立即同步更新，不等会话结束。
- 会话结束前必须重新读取这四个文件，确认相互一致；特别核验 `NEXT_SESSION_PROMPT.md` 的状态与最新远端 HEAD 一致。
- 接管提示词必须给出**唯一明确的下一任务**，不能只罗列一堆可能方向。
- 若尚无新结果，明确写“未运行/未核验/无结果”，不能填猜测。
- 每次回复用户时，明确报告接管提示词是否已更新，并提供其 GitHub 文件链接。
- 如果由于工具权限或 CI 尚未完成而不能更新某项，必须说明阻塞点，不能假称已维护。
- 不要只维护聊天中的提示词；仓库中的 canonical file 才是权威版本。

### 6. 每轮交付标准

每一轮都必须优先产出可审计研究成果：
- 可运行代码、测试、原始 episode 数据、配置和复算脚本；
- 强基线与公平预算；
- 明确的安全约束与 held-out 泛化；
- 可重复的统计分析；
- 清晰的 GO / HOLD / NO-GO 决策；
- README、决策日志、SESSION_HANDOFF 和本接管提示词同步维护。

不要连续多轮只写研究规格。不要为了让结果好看而调 held-out、删失败样本或弱化基线。不要把工程通过说成科学结论。负结果同样必须保存并解释。

---

## 维护记录

### 2026-11-05
- 建立本文件为唯一 canonical handoff prompt。
- 当前状态：Pilot A-3 已实现；CI/原始 artifacts 尚待核验；Pilot B 未获授权；A800/ARWM HOLD。
- 下一会话唯一任务：完成 A-3 最新 Actions run 核验及 JSON/CSV 独立复算。


### 2026-11-05 — D-052：强制维护制度正式生效
- 用户明确要求接管提示词必须一直维护。
- 本文件被指定为唯一 canonical handoff prompt。
- 同步规则已写入 `SESSION_HANDOFF.md` 第 47 节、`05_DECISION_LOG.md` D-052 和 README。
- 每次实质性进展后必须同一轮同步更新四份文件；会话结束前重新读取核对；每次对用户汇报附本文件链接。
- 本文件中的历史 SHA 只作接管前基线；新会话必须动态查询远端 HEAD，不能将历史 SHA 当作当前 HEAD。
- 当前唯一下一任务仍是 A-3 Actions 核验和 JSON/CSV 独立复算。


## 2026-11-06 Thesis-level status snapshot (authoritative clarification)

### Current working thesis title (NOT YET FROZEN)
**《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》**

This is the focused working title recorded in `44_THESIS_INNOVATION_REASSESSMENT_POST_TCAIL_NO_GO.md`. The older title `《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》` belongs to the former TCAIL / CI-GOM interaction-linkage route, whose estimator gate failed. Do not present the old title as the current thesis title. The title still needs advisor confirmation and a successful algorithmic evidence chain.

### Thesis research question
Can evolutionary computation search executable, contract-constrained recovery controllers for stateful tool-using LLM Agents, improving recovery on unseen tasks and fault compositions while satisfying hard side-effect safety invariants, and can feedback-driven controller updates form a measurable RSI loop?

### Current candidate structure
1. **Core candidate 1 — contract-constrained recovery policy evolution.** Search object: executable guarded finite-state recovery controller/policy genome. Candidate mechanisms: typed state/action representation, contract-aware variation/repair, feasibility-first selection with hard safety constraints, and multi-objective optimization of recovery success, unresolved side effects and recovery cost. No EC advantage has yet been demonstrated.
2. **Core candidate 2 — fault-scenario / recovery-policy co-evolution.** Co-evolve valid challenging fault scenarios and recovery controllers to improve held-out fault-family robustness. Deferred until candidate 1 passes an EC-vs-strong-baseline gate.
3. **Reserve candidate 3 — cross-task recovery-policy transfer with capability preservation.** Frozen; only reconsider after the first two candidates have independent evidence and novelty review.
4. **ARWM/A800 is a conditional supporting-model route, not a confirmed independent innovation point.** It remains HOLD pending novelty audit and evidence that it improves evolutionary search under a fixed real-rollout budget.

### Actual thesis maturity
- TCAIL estimator gate: FAIL / NO-GO; old CI-GOM route frozen. Keep its negative results, do not reuse it as a current innovation.
- Pilot A: exploratory simulator result; unresolved metric corrected. Hand-coded state-aware strategy matched oracle on success/safety in that initial slice.
- Pilot A-2: exploratory only; contract-aware success 72.22%, oracle diagnostic 77.78%, both safe 100%. This does not prove EC gain.
- Pilot A-3: protocol, simulator and 15 test cases implemented; latest A3 Actions run and JSON/CSV results still NOT VERIFIED / NOT AUDITED at this snapshot.
- Pilot B: not started / not authorized. No random search, GA/GP, NSGA-II/III or proposed EC comparison result yet.
- RSI: architecture hypothesis only; no multi-round Agent recovery-controller improvement has been demonstrated.
- Existing opening-report drafts V0.1–V0.3 were written for the former interaction-aware TCAIL/CI-GOM direction. They are not valid final/current proposal drafts as-is. Background and references may be audited and reused, but research content, title, innovation points, method, and feasibility sections must be revised for the stateful recovery direction after evidence gates.
- Therefore: thesis direction has narrowed, but final title and 2–3 validated innovations are NOT frozen; the project is in pre-proposal research validation, not final thesis writing.

### Next action remains unchanged
The only immediate task is to verify the latest A3 GitHub Actions run, independently recompute its JSON/CSV, and apply the pre-registered A3 gate. Do not start Pilot B or A800/ARWM before that gate.


### 2026-11-06 — D-053: thesis-level status clarification
- Current working title (not frozen): `《面向状态化工具型大语言模型智能体的故障恢复策略演化与递归自我改进方法研究》`.
- The older interaction-aware title belongs to the failed TCAIL/CI-GOM route and is no longer the current thesis title.
- Core candidate 1: contract-constrained recovery-policy evolution; EC benefit not yet validated.
- Core candidate 2: fault-scenario / recovery-policy co-evolution; deferred until candidate 1 passes.
- Reserve candidate 3: cross-task recovery-policy transfer with capability preservation; frozen.
- ARWM/A800 is a conditional supporting-model route, not a confirmed independent innovation; HOLD.
- TCAIL FAIL; Pilot A/A-2 exploratory only; A-2 contract-aware 72.22% vs oracle diagnostic 77.78%, both safe 100%; no EC gain established.
- Pilot A-3 implemented but CI and raw JSON/CSV not yet audited; Pilot B not started; no multi-round RSI benefit established.
- Existing opening drafts V0.1–V0.3 are based on TCAIL/CI-GOM and are not valid current proposal drafts as-is. `04_OPENING_REPORT_PLAN.md` now carries a warning and current direction update.
- Latest branch content before this prompt sync: `9f453fbd9afe78cc410ecc86293b8d1eac0af54f`. This is a historical baseline only; next session must query branch HEAD dynamically.
- Current stage: pre-proposal research validation, not final thesis writing. The immediate next task remains A-3 Actions verification and independent raw-data audit.


## 2026-11-06 — D-054: first-innovation related-work and novelty-boundary audit

New audit: `49_FIRST_INNOVATION_RELATED_WORK_AUDIT.md`.

### Main finding
Related work is substantial. Do NOT claim novelty for generic tool-failure recovery, verify-before-retry, idempotency, Saga compensation, transaction wrappers, generic prompt/tool-policy evolution, FSM synthesis, counterexample-guided GP, or safe evolutionary optimization alone.

Must-read close papers:
1. UndoBench, arXiv:2610.05622 — tool-agent recovery benchmark, paired lost-ACK evaluation, includes constrained EvoUndo-RB1 baseline.
2. EvoUndo, arXiv:2608.28363 — recoverability-constrained self-evolution of agent harness mutations; its "self-evolution" is not evolutionary computation, but it is a close conceptual neighbor due to effect contracts, witness capture, counterfactual recoverability and recovery synthesis.
3. EvoTool, ACL 2026 — gradient-free evolutionary optimization of modular natural-language tool-use policy; mandatory baseline/closest EC neighbor.
4. Where Does Exactly-Once Live?, arXiv:2609.29095 — LIMBO, late commits, idempotency, missing read paths, duplicate effects.
5. Cordon arXiv:2606.17573, Atomix arXiv:2602.14849, SagaLLM PVLDB 2025 — transactional tool runtime and compensation.
6. Verified Tool Calls arXiv:2608.02645 and Repair Economics Zenodo 2026-10-03 (explicitly non-peer-reviewed preprint) — direct retry/verification/idempotency and testbed overlap.
7. CDGP (Evolutionary Computation 2018), Formal Controller Synthesis via GP (2017), FSM-MOEA (ACM TODAES 2023), SMC-ES arXiv:2607.15003 — algorithmic foundations for safe program/controller synthesis.

### Revised novelty hypothesis — NOT APPROVED
Potential direction only: contract-semantics-preserving, counterexample-guided evolutionary synthesis of executable recovery FSMs for stateful side-effecting tool workflows. Typed effect-state genome, semantic variation/repair, feasibility-first safety, and cross-task/fault-family held-out evaluation must each show independent value. Merely combining FSM + contract + EA + Pareto is insufficient.

### Benchmark warning
Pilot A-2's deterministic fault-injection testbed/policy comparison is not itself novel: Repair Economics, LIMBO, UndoBench and FAILING TOOLS overlap. A-3 can remain an internal test environment, but do not claim benchmark novelty without feature-level comparison. A-3's per-tool independent compound faults, three-step saga and task × fault-composition shifts must be compared directly with existing benchmark coverage.

### Status and next gate
- A-3 protocol/code/test cases are implemented, but A3 CI and raw JSON/CSV remain NOT VERIFIED / NOT AUDITED.
- Pilot B remains NOT AUTHORIZED.
- Before Pilot B, finish the mechanism-level full-paper review of UndoBench, EvoUndo, EvoTool, LIMBO and the transaction/runtime papers, and compare their policy object, state/effect semantics, search loop, safety verifier, data split and budget.
- Continue to verify A3 CI/artifacts and independently recompute its results. Pilot B is authorized only if both the A3 pre-registered gate and novelty/baseline review are satisfactory.
- No A800/ARWM or real LLM API until separately authorized.


## 2026-11-06 — D-055: dataset selection and validation design

New plan: 50_DATASET_SELECTION_AND_VALIDATION_PLAN.md.

### Recommended benchmark stack (PROPOSED, NOT FROZEN)
1. Development/search: current Pilot A-3 deterministic simulator + ToolMisuseBench v0.2 large train split.
2. Development/tuning: A-3 validation + ToolMisuseBench dev.
3. Locked external recovery evaluation: ToolMisuseBench public test + UndoBench TEST.
4. Clean workflow regression only: ThinkingBox-Bench v1.0 or ToolSandbox. ThinkingBox is explicitly evaluation-only and must NOT be used for evolutionary search, tuning, prompt optimization or training.

### ToolMisuseBench details
- REALM 2026 ACL Anthology: https://aclanthology.org/2026.realm-1.28/
- Dataset: https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench
- Code: https://github.com/akgitrepos/toolmisusebench
- v0.2 large: 6,000 train / 900 dev / 1,200 public-test records; CRUD, retrieval, files, scheduling; clean, timeout, rate-limit, schema-drift, authorization, adversarial faults; task rows include initial_state, tool_schemas, fault_plan, success_criteria, budgets and seed.
- HF card marks MIT. It says public test has 1,200 records but only 600 output-grounded tasks; audit manifest/evaluator denominator before use.
- This is a close recovery benchmark, not our novelty. Audit split leakage, task/fault families, semantics, official runner and reproducibility before any Pilot B.

### UndoBench
- arXiv:2610.05622; 36 workflows / 36 faults / 8 domains; DEV 14 / VALIDATION 10 / TEST 12; paired CONTROL/FAULT with same seeds and effect-history/state oracle.
- Use TEST only after algorithm freeze; small test workflow count requires cluster-aware statistics.

### ThinkingBox / ToolSandbox
- ThinkingBox-Bench v1.0: 507 stateful business tasks across five domains, executable final-state/side-effect checks; official card says evaluation-only, so clean regression only, never search/tune.
- ToolSandbox: stateful tools, implicit dependencies, simulated user, dynamic trajectory evaluation; not a dedicated fault-recovery benchmark, so clean state-dependency regression or explicitly labeled modified fault-injection variant only.

### Critical principle
This is not ordinary supervised learning from text. Evolutionary controllers must be evaluated by executing rollouts in a deterministic stateful environment. The dataset supplies task definitions, initial states, tool schemas, fault plans and graders; fitness comes from actual environment outcomes.

### Immediate work / gates
- Do NOT launch Pilot B yet. First verify A-3 Actions and independently recompute JSON/CSV per protocol 47.
- In parallel, download/pin ToolMisuseBench v0.2 and UndoBench; audit license, manifest/checksums, schema, task/fault leakage, fault semantics and runner.
- Build a feature coverage matrix: timeout-before/after, late commit, partial mutation, delayed visibility, schema drift, authorization, cross-tool saga, compensation failure, no-readback, idempotency.
- Only after A-3 pre-registered gate AND benchmark compatibility/novelty gate pass may Pilot B begin. No A800/ARWM or real LLM API until separately authorized.


## D-055 (2026-11-06): dataset plan
See 50_DATASET_SELECTION_AND_VALIDATION_PLAN.md. Proposed, not frozen:
- Search: Pilot A-3 simulator + ToolMisuseBench v0.2 train (6,000).
- Dev: A-3 validation + ToolMisuseBench dev (900).
- Locked recovery evaluation: ToolMisuseBench public test (1,200 records; HF card says 600 are output-grounded, so audit actual denominator) + UndoBench TEST (12 workflows).
- Clean regression only: ThinkingBox-Bench v1.0 (507 tasks; evaluation-only, never use for search/tuning) or ToolSandbox (stateful dependencies, not a dedicated recovery benchmark).
Evolution fitness comes from executing controller rollouts, not supervised learning over JSONL. Audit versions, license, runner, manifests, leakage, and fault coverage first. A-3 CI/JSON/CSV still require independent audit; Pilot B remains HOLD. No A800/ARWM or real LLM API.


## 2026-11-06 — D-056: dataset plan official-source verification and next execution plan

New execution plan: 51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md.
Dataset strategy and official metadata are maintained in 50_DATASET_SELECTION_AND_VALIDATION_PLAN.md.

### Official-source corrections / confirmations
- ToolMisuseBench REALM 2026: seed-42 v0.2 large = 6,000 train / 900 dev / 1,200 public-test records; HF card explicitly says only 600 public-test tasks are output-grounded. Do not conflate record count and score denominator.
- ToolMisuseBench paper reports Parser+Repair task success 0.767 and conditional recovery success 0.736 on public test; recovery-disabled task success 0.158. These are paper-reported values, NOT our reproduction. Parser+Repair is a required reference baseline.
- UndoBench current dataset card version is v1.0.1, 36 workflows, DEV 14 / validation 10 / TEST 12; data/spec CC BY 4.0, software Apache 2.0. Frozen TEST requires explicit opt-in.
- ThinkingBox-Bench v1.0 has 507 tasks / 5 domains and is evaluation-only. It must not be used for search, tuning, prompt optimization or training; final clean regression only.

### Current A-3 status
- 47_PILOT_A3_PROTOCOL.md says PRE-REGISTERED / NOT RUN.
- experiments/pilot_a_recovery/PILOT_A3_IMPLEMENTATION_STATUS.md says IMPLEMENTED / NOT YET VALIDATED BY CI / RESULTS NOT YET RUN OR ACCEPTED.
- The 15 tests and artifact-upload workflow are authored, not evidence of a passing run.
- Per-policy budget 954 (144 train / 120 validation / 690 held-out); seven policies = 6,678 policy episodes.
- Do NOT claim A-3 passed. Do NOT start Pilot B.

### Immediate next task: Phase A in 51 plan
1. Identify the exact Actions run for the current implementation SHA.
2. Inspect jobs/steps/logs and verify the 15 A-3 tests actually ran.
3. Download the A-3 artifact and hash ZIP/JSON/CSV.
4. Independently recompute CSV metrics and JSON parity, verify scenario/seed/fault pairing and hidden-oracle isolation.
5. Apply the exact pre-registered Gate in file 47; publish GO / HOLD / NO-GO with evidence.
6. In parallel, pin ToolMisuseBench and UndoBench revisions, audit manifest/checksums, splits, licenses, evaluator denominator and feature coverage.
7. Only after A-3 Gate + dataset compatibility Gate + adapter smoke pass may Pilot B preregistration be drafted.

### Authorization boundary
GO: read-only dataset audit, A-3 CI/artifact audit, deterministic adapter smoke on train/dev.
HOLD: evolutionary Pilot B, public-test tuning, UndoBench TEST, ThinkingBox optimization, A800/ARWM, real LLM API.
At each session end update this file, SESSION_HANDOFF.md, README.md, 05_DECISION_LOG.md and 51 plan status. Record real commit SHA, run ID, artifact hashes and test outcomes. Never infer experiment success from documentation or workflow configuration.


## 2026-11-06 — D-057: Phase A complete — A-3 CI remediation, independent reaudit, Gate = HOLD

New report: `PILOT_A3_INDEPENDENT_REAUDIT.md`. Decision log: D-057.

### What actually happened (facts, verified)
1. **A-3 CI had never produced results.** All workflow runs from `76f62c09` onward crashed in "Run Pilot A-3 simulator": `recover_tool` dereferenced `tool.tick` through `PublicToolView` (which intentionally hides runtime fields) → `AttributeError`. Artifact upload was skipped every time; no A-3 JSON/CSV existed before today.
2. **Remediation (commit `f5e6b46`):** policies count their own waits against the public `retry_after` hint; `PublicToolView` unchanged (observation boundary preserved); added regression test #16 (`test_recover_tool_never_touches_hidden_runtime_fields`, 6 policies x 7 public errors). Test count is now **16** A-3 tests (15 pre-registered + 1 crash-regression), 28 total in the suite.
3. **Validated run:** 42241224898, head SHA `f5e6b4608440b7ac60d3b57ceb0a758f819678c1`, conclusion success. 28 tests OK (verified in logs), A1/A2/A3 simulators all ran, `pilot-a3-results` uploaded.
4. **Artifacts (sha256):** ZIP `1119d14b70eedef221fe6e63439e2a04bd58c0354d5a723344d2c80c459ab727` (matches GitHub digest); `pilot_a3_results.json` `3a60ae8385c723c57d54ff47608fe428690d94519f6762ec78bbc15c1d15fe14`; `pilot_a3_episodes.csv` `2c7d7dad5faaae58f182f27d77b90dfa237f4c1627e15b0bc029d34582f3c369` (6,678 data rows). Preserved raw under `experiments/pilot_a_recovery/ci_artifact/` with `-text` gitattributes; manifest `a3_artifact_manifest.json`. Local rerun is byte-identical (deterministic simulator).
5. **Independent recompute** (`recompute_a3_audit.py`, does not import simulator code): 6,678 rows; 954/policy (144/120/690); 954 scenario IDs perfectly paired across 7 policies (same seeds + fault realizations); protocol-47 factorized splits exact (45 task x composition cells, 0 deviations); JSON vs CSV parity 0 mismatches; rollback/compensation/unresolved semantics consistent row-by-row.

### Pre-registered Gate (47 section 6, applied verbatim): **HOLD**
- Condition 1 (zero saga_aware invariant violations per held-out slice): **PASS** (task-shift 0.0, fault-shift 0.0, joint-shift 0.0).
- Condition 2 (oracle − saga held-out task-success gap >= 0.05): **FAIL — gap = 0.0**.
- Condition 3 (cluster paired bootstrap 95% CI lower > 0): **FAIL — CI = [0.0, 0.0]** (23 task-family x fault-composition clusters, every paired diff = 0; seed-42 sensitivity identical).
- gap <= 0.02 holds but action-cost difference +34.63% > 10%, so the NO-GO branch does not apply either → protocol's "otherwise HOLD" branch.
- Decision: **HOLD_REVIEW_FAILURE_BOUNDARIES**. Pilot B NOT authorized.

### Failure boundaries (why the gap is zero)
- Compositions `partial_comp_failure` and `delay_rate_permission` are structurally infeasible: 0% success for **all 7 policies including the privileged oracle** (360/690 = 52.2% of held-out). Compensation-failure residue and permission denials make completion impossible; latent oracle knowledge only saves actions.
- Task-family shift is near ceiling (saga_aware 97.5% success, zero violations) — policy rules generalize; collapse comes only from unseen fault compositions.
- The only real optimization headroom is action cost (saga 10.17 vs oracle 7.56 mean actions, +34.6%).
- Full worst-group table in the reaudit report.

### Status after this round
- Pilot A-3: **RUN / INDEPENDENTLY AUDITED / GATE = HOLD**. Do not re-run A-3 and do not tune on its held-out.
- Pilot B: NOT started / NOT authorized. A800/ARWM, real LLM API, dual-population co-evolution, UndoBench TEST, ThinkingBox optimization: all HOLD.

### Next session's only task
Phase B dataset audit (ToolMisuseBench / UndoBench version pinning, manifest/license/split-leakage/evaluator-denominator audit per 51 plan section 3) **plus** drafting a NEW preregistration A-3b addressing the failure boundaries (feasibility-stratified metrics / feasible held-out compositions / action cost as objective). A-3b must be approved before any new run. Pilot B remains blocked until A-3b Gate + dataset compatibility Gate + adapter smoke all pass.


## 2026-11-06 — D-058: Phase B dataset audits COMPLETE; A-3b research design drafted

New documents: `52_TOOLMISUSEBENCH_AUDIT.md`, `53_UNDOBENCH_AUDIT.md`, `54_BENCHMARK_COMPATIBILITY_MATRIX.md`, `SPLIT_LEAKAGE_AUDIT.md`, `LICENSE_AND_PROVENANCE.md`, `DATASET_LOCK_MANIFEST.json`, `55_PILOT_A3B_RESEARCH_DESIGN.md`; evidence in `experiments/dataset_audit/`.

### ToolMisuseBench v0.2 large (audited, MIT, HF rev 98eb2871)
- 6,000/900/1,200 rows verified; file SHA-256 match official manifest exactly. task_id clean across splits.
- **Scoring denominators decoded from released per-task episodes**: paper 0.767 = TaskSuccess over ALL 1,200 (recomputed 0.7667); 0.736 = conditional recovery over the 993 FAULTED tasks (731/993=0.7362); 0.158 = no-recovery full-split (0.1575). "600 output-grounded" = subset with tool_output_path_equals criteria (scores 0.8783 there vs 0.655 state-grounded) — NOT a headline denominator.
- **Semantics (official env/fault code)**: all faults fire BEFORE execution (no lost-ACK); envs idempotent/guarded (duplicates impossible); every fault triggers once (on_nth_call=1) so one retry always recovers; NO compensation/idempotency contracts/partial commit/late commit/saga (0 occurrences); two-fault plans never span tools. No structurally unrecoverable scenarios exist.
- **Parser+Repair = regex instruction parsing + error-code arg repair** (schema alias id↔doc_id↔account_id). Reproduced on DEV (900): TaskSuccess 0.7622, conditional recovery 0.7363; no-recovery 0.1511. MUST be a Pilot B baseline. It is a parser/repair baseline, not a recovery-policy upper bound.

### UndoBench v1.0.1 (audited, CC-BY-4.0 data / Apache-2.0 software, HF rev 4be11518)
- 36 workflows (14/10/12) fully characterized: 33/36 SCN-LOST-ACK with observability=UNKNOWN_OUTCOME on ALL rows; idempotency_support=false everywhere (duplicates real); IRREVERSIBLE 8, COMPENSATABLE 24; forbidden_effects 22; 19/36 multi-tool. Metrics CRSR/DER/MER/URR/EOR align with our safety-recovery semantics (CRSR conditions on Control success).
- Harness verified: doctor PASS, smoke PASS (control/fault/oracle/effect-log pipeline), DEV paired run with example agent (14 pairs) computes CRSR/DER/MER correctly. Built-in TEST lock `allow_frozen_test_execution: false`. TEST never executed.

### ThinkingBox-Bench: UNREACHABLE (HF 401 gated/removed; github.com/microsoft/thinkingbox-data 404). Claims (507 tasks, evaluation-only) NOT re-verifiable this round; keep evaluation-only policy; no experiments depending on it.

### Split leakage (SPLIT_LEAKAGE_AUDIT.md)
- ToolMisuseBench: 72–73 normalized instruction templates shared across splits; toolsets 100% shared → instance-level generalization ONLY.
- UndoBench: all 8 domains in all splits; test 12/12 homogeneous lost-ACK; tool overlap low (3/20) → workflow-level generalization only.
- Pilot A-3 remains the only task-family x fault-composition factorized OOD (keep it).

### A-3 gap=0 root cause (55 §0, evidence-based)
(a) on feasible cells saga_aware already matches oracle; (b) 52.2% of held-out is structurally infeasible (0% for everyone incl. oracle) and dilutes the aggregate; (c) the pre-registered gate values only success, not the real difference (action cost +34.6%); oracle sees only current-step state (not an upper bound). Fix = recoverability stratification + cost objective + re-graduated held-out — NOT deleting hard scenarios.

### A-3b design (55, DRAFT — not approved, not run)
Recoverability classes R1/R2/R3/R4 defined evaluator-side (never by "did a policy succeed"); stratified metrics (CondRecSucc on R1+R2 only; CorrectEscalation on R3+R4; hard P(violation)=0); two ablatable mechanisms (A contract-preserving operators, B counterexample-guided search); baselines Random Search/GA/GP/NSGA-II/NSGA-III/hand rules/oracle-diagnostic; paired cluster bootstrap + permutation + Holm; explicit stopping rules and pre-registered failure reasons. A-3 held-out retired as confirmation data.

### Status
- GO: A-3b design review + preregistration freeze (needs user approval before any run); Phase C adapters (train/dev/validation smoke only).
- HOLD: A-3b execution; Pilot B; A800/ARWM; real LLM API; UndoBench TEST execution; ThinkingBox anything; tuning on any locked split.

### Next session's only task
Independent review of 55_PILOT_A3B_RESEARCH_DESIGN.md, then preregistration freeze (scenario generator spec, R3/R4 stratification ratio, tau_min, cost table, seeds, budget), then implementation of the recoverability classifier + scenario generator + adapters. No A-3b run before the freeze is approved.


## 2026-11-07 — D-059: Independent review of Pilot A-3b design

Review: `56_PILOT_A3B_INDEPENDENT_REVIEW.md`.
Current status: Phase B = GO / complete; design 55 = REQUEST CHANGES; A-3b formal run = HOLD.

### Critical corrections required before preregistration
1. R4 is defined as having no reachable zero-residual safe terminal, so CorrectEscalation(R3+R4) requiring zero residual is contradictory. Define R4 DamageContainment; report unavoidable residual separately.
2. R2 currently includes graceful failure/safe abandonment but is counted in CondRecSucc. Restrict R2 to compensation-assisted task completion; classify safe abort as R3 or a separately defined outcome.
3. Define recoverability as existence of an observation-based contingent policy over public observation histories, robust across hidden states in the same observation-equivalence class. Specify finite horizon, action set, nondeterminism and UNKNOWN labels.
4. Finite rollouts cannot prove population P(violation)=0. Separate by-construction/static invariant checks from zero observed violations and a finite-sample confidence upper bound.
5. Separate avoidable from unavoidable residual effects; do not penalize necessary R3/R4 escalation as if it were unnecessary intervention.
6. Clarify whether 3:1 means (R1+R2):(R3+R4) or R3:R4. Freeze exact R1/R2/R3/R4 counts for every split and held-out slice.
7. Compute power at independent task-family × fault-composition cluster level. Do not treat repeated episodes/seeds as independent clusters.
8. Ensure all EA methods share initialization distribution and candidate pool; fix one common NSGA-II backbone for A/B/A+B mechanism ablations, with NSGA-III as a separate baseline.
9. Clarify 50k rollout budget (per method total or per seed), count all real simulator episodes, and separate search/validation/final evaluation budgets.
10. Make strongest standard EA comparison a primary test. Beating only hand rules or Random Search does not establish improved EA.
11. 49 related-work file remains INITIAL LITERATURE SCAN / NOT SYSTEMATIC / NOVELTY NOT APPROVED. Complete mechanism-level systematic review before novelty claims.

### Immediate task
DONE (2026-11-07, D-060): `55_PILOT_A3B_RESEARCH_DESIGN_R1.md` created (all B1–B6/M1–M5 addressed); observation-based AND-OR belief reachability classifier implemented (`experiments/pilot_a3b/reachability.py`) and Stage-1 verified (12 ground-truth cases, confusion matrix diagonal, 27 tests green); A/B operators + 8-method diagnostic run executed on 216 new-seed scenarios.

NEXT (single task): (1) cluster-level power simulation using this round's 54-cluster variance to size the formal A-3b experiment; (2) iterate mechanism B (counterexample granularity/weighting) and A (repair completeness) as diagnostic work; (3) complete the 49 mechanism-level systematic review; (4) assemble the preregistration candidate and submit for user approval. No formal A-3b run before approval.

### Authorization
GO: diagnostic-level code/experiments on new-seed own scenarios, design revision, related-work audit, power analysis, preregistration preparation.
HOLD: formal A-3b confirmatory runs, Pilot B, public test/UndoBench TEST, A800/ARWM, real LLM API, ThinkingBox optimization, tuning on any locked split.
User approval is required after independent review of the preregistration candidate and before any formal A-3b run. Continue maintaining this prompt, SESSION_HANDOFF.md, README.md, 05_DECISION_LOG.md and 51 plan every session.

## 2026-11-07 — D-060: 55-R1 + recoverability classifier + first mechanism diagnostics

### Delivered (real code and experiments)
- `55_PILOT_A3B_RESEARCH_DESIGN_R1.md`: B1–B6/M1–M5 all addressed; mutually exclusive R1–R4 + UNKNOWN; observation-history contingent robust reachability; layered safety claims (no P=0 claims); cost three-way split (necessary escalation unpunished); quotas 3:1=(R1+R2):(R3+R4) per split; same-init-pool/same-backbone/same-budget attribution; primary contrast A+B vs NSGA-II.
- `experiments/pilot_a3b/`: reachability.py (AND-OR belief-state checker + ladder classifier with certificates), mini_env.py (12 ground-truth environments), test_recoverability.py + test_a3_labels.py (27 tests, all green), a3_bridge.py (A-3 ToolRuntime reuse, FSM genome, contract-preserving repair = mechanism A, analytic labels), ea.py (NSGA-II backbone, NSGA-III, GA, Random, B = counterexample pool + targeted mutation + <=2x weighting), run_diagnostic.py, stats.py (cluster paired bootstrap + sign-flip permutation + Holm).
- Stage-1 gate PASSED: confusion matrix 12/12 diagonal (R1 5, R2 2, R3 1, R4 2, UNKNOWN 2 by design); horizon-cutoff and resource-cutoff cases correctly return UNKNOWN; labels generated independently of tested algorithms.

### Stage-2 diagnostic (DIAGNOSTIC, NOT confirmatory)
- 216 fresh scenarios (new seeds, NOT the frozen A-3 held-out dataset); labels R1 96 / R2 50 / R3 36 / R4 34; throughput ~97k episodes/s; budget 108,864 real episodes per method per seed; 3 seeds; methods: hand, random, ga, nsga2, nsga3, A, B, AB.
- **Mechanism A decisive effect: illegal-candidate ratio 1.000 -> 0.000** (A and AB final populations fully legal; every other method including NSGA-II/GA stayed at 1.000). A/AB zero observed invariant violations on all seeds; comparators up to 8%. Answers Q1 affirmatively.
- CondRec means: hand 1.000 > A 0.968 > AB 0.938 > ga 0.911 > nsga3 0.902 > B 0.872 > nsga2 0.838 > random 0.575.
- Primary AB vs NSGA-II (54 clusters, paired bootstrap): delta +0.049, CI95 [-0.017, +0.122], permutation p=0.27 — positive direction, NOT significant (underpowered). A vs nsga2 +0.056 (CI contains 0). AB vs A -0.006 (B dilutes A at this budget). AB vs hand -0.026 (hand baseline NOT beaten).
- All Holm-adjusted secondary tests ns. Honest conclusion: mechanism A demonstrably works (illegal-candidate elimination + zero violations + directional success gain); H1 (A+B beats standard EA and hand rules) NOT YET established; first innovation is feasible but unproven.

### Confound controls
Same random-only initial pool for all search methods (hand policy is a separate baseline); identical budget and evaluator; the earlier hand-seed-in-pool contamination was detected and removed (56 M1). Episode counts are real simulator rollouts.

### Next task
Power sizing from the 54-cluster variance; mechanism iteration (B granularity/weighting, A repair completeness); 49 systematic review; preregistration candidate for user approval. Formal A-3b remains HOLD.


# 2026-11-07 — D-061: D-060 独立复核（本节覆盖此前“下一步先做功效分析”的指令）

**独立报告：** `57_PILOT_A3B_DIAGNOSTIC_INDEPENDENT_REAUDIT.md`  
**当前状态：** D-060 原始诊断数据保留；Stage-2 指标/控制器/B/统计存在阻断问题；正式 A-3b 继续 HOLD。

## 复核事实
- 远端 branch HEAD：`edfc7ad0156617dccc4e4bf998df33f991ae921f`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`；ahead 94 / behind 0。
- 原始 `diagnostic_results.json` 已从 GitHub blob 读取并解析：216 scenarios、24 runs、每 run 216 rows；全部 scenario ID 配对一致。
- 实际 label counts = R1 96 / R2 50 / R3 35 / R4 35。旧 D-060 文档中的 36/34 是记录错误，后续统一为 35/35。
- 固定 hand 每 seed 216 episodes；搜索方法大多 108,864；A/seed23=108,648（cache hit）。不能再声称所有方法/seed 都执行完全相同的真实 episode 数。
- 无 GitHub status checks；55/55 是本地测试报告，不是本轮 CI 记录。

## 阻断问题（先修代码，不要先做功效分析）
1. **控制器不是 stateful FSM**：实际是静态 `(error, idempotent, compensatable)->macro-action` 查表；Saga rollback 由“基因组任一规则含 COMP”触发，而非策略明确动作。必须实现真实状态/观察历史/事务进度/补偿栈，或收窄论文主张。
2. **自动升级污染指标**：任何宏动作失败都会把 `escalated=True`，不能区分策略明确升级和运行器自动失败终止。
3. **R4 评分错误**：`score_class(R4)` 只看 escalated 和 duplicate，不检查可避免残留/最小可达损害；R4 残留整体被排除在 avoid_resid 外。
4. **必要升级仍被成本惩罚**：`norm_actions` 对所有类别求平均，包含 R3/R4 的必要升级动作。
5. **A-3 labels 非 checker 输出**：216 个场景由启发式 `label_scenario` 分类；6 组 sanity tests 不等于 216 场景逐项可达性验证。
6. **B 实现与设计不符**：`CounterexamplePool.update` 每次清空池；`scenario_weights()` 未调用；只按 class label 粗略调 mutation，未按公开错误签名定位规则；B/AB targeted 分支有额外 mutation。
7. **A legality 指标同源**：`repair_genome` 与 `is_legal` 共用 ILLEGAL 表；validator 还漏检非 SCHEMA 的 REPAIR/default action。该指标只能叫内部规则合法性，不能当独立安全证明；NSGA-II/GA 本轮也零观察违规。
8. **Reachability horizon bug**：到达 horizon 时返回 False 但未标记 unproved，可能把“任务可达性未知”错误降级为 R3/R4。改成 WIN/PROVEN_LOSE/UNKNOWN 三值传播。
9. **统计汇总不正确**：stats.py 平均 per-seed CI 端点和 p 值。禁止这样合并。独立探索性 pooled cluster 重算 AB−NSGA-II Δ≈+0.0494、CI≈[-0.0031,+0.1034]、sign-flip p≈0.0874，仍不显著；需实现预先定义的 pooled/hierarchical cluster bootstrap。
10. **基线非 canonical**：当前 NSGA-II tournament 未完整使用 rank+crowding；NSGA-III 为 simplified niching；GA 与设计描述不一致；无 GP；Random 也使用 Pareto survivor selection。正式比较前换标准实现或准确改名。
11. **55-R1 配额冲突**：文字 3:1，但 Train/Validation 表 3:2，held-out 58:38 也不是 3:1。必须统一比例。
12. D-060 原始统计 label count 35/35，旧 handoff/decision log 36/34，按原始 artifact 更正。

## 下一会话唯一优先任务
创建并执行 D-061 修复分支任务，按顺序：
A. 修复控制器执行语义（显式升级、显式补偿、移除基因组全局 rollback flag）；决定并实现真正有状态 FSM。
B. 修复 R3/R4 scorer、最小可达损害、可避免/不可避免残留、类别条件化 action cost。
C. 把 A-3 全部场景标签接入 checker/可审计穷举证明；修复 horizon 三值传播。
D. 修复 B 反例池聚合、错误签名、实际权重采样和变异预算公平性。
E. 建立独立 contract validator；补 canonical NSGA-II/NSGA-III/GA（或准确命名），决定 GP 是否纳入。
F. 修复 pooled/hierarchical cluster statistics；重跑新诊断集（仍非 held-out）。
G. 纠正 3:1/3:2 配额定义和 D-060 记录；再做功效分析。

**不要先做功效分析，也不要先扩大 rollout**：当前执行和评分语义有缺陷，基于错误指标算样本量会固化错误。D-060 artifact 永久保留，任何修复后重跑必须使用新 run ID、新输出文件和新 manifest。

## 授权
GO：以上实现修复、单元测试、独立 validator、非锁箱新诊断集和统计复算。
HOLD：正式 A-3b 确认性实验、A-3 原 held-out 调参、UndoBench TEST、Pilot B、A800/ARWM、真实 LLM API、ThinkingBox 优化。用户批准 preregistration 后才可运行正式 A-3b。


## 2026-11-07 — D-061: 57-review fixes implemented; round-2 diagnostic run

Report: `58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md`. Artifacts: `experiments/pilot_a3b/diagnostic2_results.json` (manifest d4fb2be680e74f2e...) + `diagnostic2_stats.json`. D-060 `diagnostic_results.json` preserved untouched.

### All F1-F8/S1-S3 blockers fixed (47/47 tests green)
- F1 real stateful FSM (step/attempts/confirmed/comp-stack/decision-budget); explicit COMPENSATE/ROLLBACK with comp_log; implicit saga rollback REMOVED.
- F2 policy_selected_escalation vs runtime_forced_abort separated; R3 counts explicit escalation only.
- F3 R4 harm accounting: min_reachable_harm / actual_harm / avoidable_harm / unavoidable_residual; containment = explicit escalation AND zero duplicates AND avoidable_harm==0.
- F4 cost objective counts only R1/R2 unnecessary actions; necessary R3/R4 escalation unpunished.
- F5 A-3 verdicts: analytic prover + AND-OR checker exhaustive cross-check over 309 fault patterns: 0 hard contradictions, 120 exact, 18 R1->R2 refinements, 171 checker-UNKNOWN (bounded search, not counter-evidence).
- F6 B redesigned: per-generation population-wide aggregation, action-sequence implicated genes, weights actually reach the evaluator (<=2x), targeted mutation REPLACES standard mutation (budget-matched).
- F7 independent contract_validator.py (separate code path from repair table; exhaustive error x action matrix).
- F8 three-valued WIN/PROVEN_LOSE/UNKNOWN + cycle detection; no downgrade when higher goal UNKNOWN.
- S1 pooled hierarchical stats (cluster = task x composition, seeds nested; bootstrap + sign-flip + Holm + effect sizes + seed stability).
- S2 standard NSGA-II / NSGA-III (labelled reimplementation) / GA / Random; GP excluded with reason.
- S3 train 108 search / validation 54 (2 unseen task families, fresh seeds) reporting-only.

### Round-2 results (DIAGNOSTIC, not confirmatory)
8 methods x 3 seeds; pop 48 x 60 gens; 316,224 real episodes per method per seed; shared init pool.
- **A vs NSGA-II: +0.239 [0.193, 0.284], Holm p=0.0014 (d=1.56) -- significant.**
- **Independent-validator illegal ratio: A/AB = 0.00 vs everyone else = 1.00 -- decisive.**
- primary AB vs NSGA-II: +0.126 [0.086, 0.167], p=0.0002 (d=0.82) -- significant.
- **AB vs A: -0.113, p=0.0014 -- adding B HURTS A**; B alone +0.082 (Holm p=0.034, weak).
- AB vs hand: -0.514 -- strong hand baseline (0.827) NOT beaten.
- Q6 validation: AB vs NSGA-II +0.148, p=0.002 (d=0.97); A val 0.488 vs nsga2 0.222 -- generalisation holds.
- Open issue: environment violation rate A 0.36 vs hand 0.006 (observation-ambiguity WAIT-SLA timing is behavioural, not rule-level).

### Judgement
Mechanism A: real significant evidence (legality + success, attributable). Mechanism B in combination: NOT established (significantly harmful). First innovation PARTIALLY established (A yes, B needs redesign). Not yet paper-complete.

### Next task (single)
Redesign B's counterexample->gene mapping (action-sequence pattern signatures + semantic-repair-style targeted mutation) and add stateful contract repair for the ambiguous-observation WAIT-SLA discipline; re-measure environment violation rate; rerun A+newB with the same configuration. Formal power analysis and preregistration remain HOLD until then.


# 2026-11-08 — D-062：WAIT-SLA 行为安全与反例驱动演化（下一会话直接执行）

**完整执行计划：** `59_D062_WAIT_SLA_AND_COUNTEREXAMPLE_REDESIGN_PLAN.md`  
**D-061 结果报告：** `58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md`  
**当前任务状态：** READY_FOR_EXECUTION；本节是任务授权与接管指令，不代表 D-062 已经执行。

## 项目接管时先做
1. 重新检查 `pilot-a-stateful-recovery` 远端 HEAD、main、compare、工作树（若可访问）和 CI；建立计划时 HEAD 为 `ac042b4e96b80edb8ca727009f0e34ef32179a1f`，main 为 `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，ahead 102 / behind 0。
2. 阅读 58 号报告、59 号计划、D-061 原始 JSON/统计、`a3_bridge.py`、`ea.py`、`contract_validator.py`、`run_diagnostic2.py`、`stats.py`。
3. 不覆盖 D-060/D-061 原始 artifact。先复核数据哈希、manifest 和运行记录。
4. 当前 HEAD 没有可读取的 status checks；现有 `.github/workflows/pilot-a-recovery.yml` 只监控 `experiments/pilot_a_recovery/**` 和 workflow 自身，不会因 `pilot_a3b/**` 修改自动触发。若要让 D-062 自动测试，需单独评估 workflow path filter 和安全性，不可假称 CI 已运行。

## D-061 结果的证据边界
58 号报告给出的结果（必须从原始 artifact 独立复算）：
- A vs NSGA-II：Δ=+0.239，95% CI [0.193,0.284]，Holm p=0.0014；
- AB vs NSGA-II：Δ=+0.126，CI [0.086,0.167]，p=0.0002；
- AB vs A：Δ=-0.113，CI [-0.152,-0.078]，p=0.0014；
- B vs NSGA-II：Δ=+0.082，CI [0.025,0.144]，p=0.034；
- AB vs Hand：Δ=-0.514，CI [-0.613,-0.416]，p=0.0014；
- 报告的环境行为违规率 A=0.36、Hand=0.006。
这些是报告值，不得跳过独立复算。当前研究结论：A 有正向诊断证据；B 叠加有害；未超过 Hand；第一项创新部分成立。

## 唯一首要任务：先查清 0.36 vs 0.006
从 `experiments/pilot_a3b/diagnostic2_results.json` 和原始 episode 轨迹复算：
- 分子、分母、episode-level/action-level 口径；
- 同一 episode 多次违规是否重复计数；
- task/fault/seed/genome 分层；
- Hand 与 A 是否同口径；
- 每条 duplicate side effect 的完整公开观测和动作轨迹；
- 区分提交未发生、lost ACK、已提交但不可见、处理中、未知结果、合同无 visibility guarantee。
新增独立复核报告（建议 58_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md；先查重，若占用则递增），脚本必须独立于原 scorer。Stage 0 未通过，不扩大 rollout。

## WAIT-SLA 状态化合同设计
为工具定义 submit semantics、visibility SLA/保证类型、query consistency、idempotency/idempotency-key、safe retry preconditions、compensation capability、retry window、max wait/decision budget、escalation conditions。区分 visibility SLA 和 retry SLA；没有可证明的可见性上界时，固定等待不得把 UNKNOWN 推断成 NOT_COMMITTED。
状态/观测测试至少覆盖：SLA 边界前后可见、超过 SLA 仍未知、无 visibility guarantee、强一致/最终一致/无保证查询、幂等/非幂等、幂等键有无、处理中、lost ACK、WAIT 失败/限流、多工具部分提交。
策略只能读取公开观察与自身状态，不能读 hidden state。

## B-new 和安全门
- 反例签名细化为公开观测序列 + 合同 + FSM 状态/事务阶段 + 动作序列 + 失败后果 + 涉事基因。
- 建立 `failure trace -> violated transition/contract -> implicated gene neighborhood -> semantic repair mutation` 映射。
- 定向变异替换普通变异，不增加 mutation 或 rollout 预算；每代聚合全种群反例；记录变异前后基因和独立 validator 结果。
- 变异后独立 Contract Validator；关键行为场景 Safety Gate；生存者选择先满足硬安全，再优化性能。
- B 不能硬编码 TIMEOUT->WAIT；必须在不同工具合同和故障模式上搜索。

## 新诊断对照和指标
对照至少 Hand、NSGA-II、A、A+Fixed-WAIT、A+WAIT-SLA、A+WAIT-SLA+VERIFY、安全重试、B-new、A+B-new、A+B-new+Safety Gate。可分机制消融和完整对照两轮，但预算公平。
指标：CondRecSucc、episode/action behavior violation、duplicate side-effect、SLA violation、CorrectEscalation、AvoidableHarm、不必要成本、worst-group、搜索效率、未见任务族泛化。
旧 D-061 validation 若用于调参，不得继续称独立验证；生成新的非锁箱诊断数据。正式 held-out/确认性实验仍 HOLD。

## 必须回答
Q1 WAIT-SLA 是否减少重复副作用？Q2 是否优于固定 WAIT？Q3 VERIFY 独立贡献？Q4 B-new 是否定位正确基因？Q5 B-new 是否优于 NSGA-II？Q6 A+B-new 是否优于 A？Q7 Safety Gate 能否保护 A？Q8 能否接近/超过 Hand？Q9 未见任务泛化？Q10 增益来自演化搜索还是手工编码 WAIT-SLA？

## Gate
GO：原始数据复核、WAIT-SLA、FSM/B-new/Safety Gate 代码、单测、独立 validator、新非锁箱诊断和统计复算。
HOLD：正式 A-3b、旧 held-out 调参、UndoBench TEST、Pilot B、A800/ARWM、大规模真实 API、ThinkingBox、未经批准的锁箱测试。
当前不启动 A800。指标和执行语义稳定后再做正式功效分析。

## 仓库接班纪律
每个阶段及时更新本文件、`SESSION_HANDOFF.md`、`README.md`、`05_DECISION_LOG.md`、`51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md`。每轮区分 PLANNED / IMPLEMENTED / TESTED / EXPERIMENTALLY VERIFIED。不得把计划写成完成。每次阶段提交后核验远端 HEAD、main、CI 和工作树。

## 2026-11-07 — D-062: D-061 failure-trace audit, WAIT-SLA contract, B-new, round-3 diagnostics

Reports: `59_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md`, `60_WAIT_SLA_CONTRACT_BNEW_AND_SAFETY_GATE_DESIGN.md`, `61_D062_DIAGNOSTIC_RESULTS.md`. Data: `experiments/pilot_a3b/diagnostic3_results.json` (manifest 017b3454c0b9cf90...) + `diagnostic3_stats.json`. D-060/D-061 artifacts preserved untouched.

### Stage 0 audit (OVERTURNS the D-061 narrative)
- diagnostic2_results.json SHA-256 dc455355... ; independent aggregation + genome replay.
- The 0.36 violation rate is NOT duplicates (A dup_rate = 0.0000): 1,132/1,139 (99.4%) violations are an EVALUATOR ARTIFACT -- correct ROLLBACK safe-aborts were charged by the saga gate; hand's 0.006 is the same artifact.
- Only 7 genuine duplicate episodes; their traces confirm `TIMEOUT -> VERIFY (SLA-internal NOT_COMMITTED lie) -> RETRY -> DUPLICATE` on non-idempotent tools. timeout_before is retry-safe; timeout_after/delayed_visibility are not.

### Fixes and new mechanisms (51/51 tests green)
- Evaluator: saga gate applies to EXECUTE-type actions only; safe rollback is free. Metrics separated: sla_violation / duplicate / downstream_violation.
- WAIT-SLA contract (implemented): under UNKNOWN_OUTCOME on non-idempotent tools, RETRY unlocks only after compensation clears the ambiguity OR (visibility SLA elapsed AND a post-SLA query confirms non-commitment); SLA-internal queries never unlock retry. Action masking; genome unchanged (Q10 isolation).
- B-new: action-sequence failure signatures, population-wide per-generation aggregation, implicated-gene targeting, cause->repair-action map, contract repair + independent validator, budget-matched.
- Safety Gate: 6-scenario behavioural battery + layered survivor (ABG arm).

### Round-3 results (DIAGNOSTIC; fresh seeds 2026110900)
- **AB vs A: +0.119 [0.066, 0.183] p=0.0002 -- B-new combination gain ESTABLISHED (D-061 negative reversed).**
- **AwaitSLA vs A: +0.089 p=0.005; AwaitSLA vs AwaitFixed: +0.054 p=0.003 -- WAIT-SLA works and beats fixed waiting.**
- AB vs AwaitSLA +0.031 p=0.0072 on all data, but validation +0.031, p=0.244 (n.s.); Q10 search increment is suggestive in-sample but not yet shown to generalize.
- AB behavioural violations 0 (A 0.060); AB stability [0.543, 0.531, 0.543]; validation AB vs A +0.142 p=0.008.
- Negative results kept: Safety Gate harmful (ABG < AB, -0.193); B alone worse than NSGA-II (-0.074); hand still ahead (AB -0.282).

### Judgement
Three mechanisms now have independent ablation evidence (contract-preserving A, WAIT-SLA, B-new). Mechanism-level ablations are promising, but AB vs NSGA-II is not significant (all p=0.062; validation p=0.2277), and Q10 is not significant on validation (p=0.244). Do NOT yet claim superiority to standard EA or generalized search gain. Hand remains ahead.

### Next task (single)
Power analysis from the round-3 cluster variance (cluster_sd ~ 0.40) -> freeze preregistration (with the Q10-scoped claim) -> submit for user approval -> formal A-3b. Everything else stays HOLD.


# 2026-11-08 — D-063：正式 A-3b 功效核算与预注册（下一会话接管）

**执行计划：** `62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md`  
**D-062 交付：** 59（失败轨迹独立复核）/ 60（WAIT-SLA、B-new、Safety Gate 设计）/ 61（diagnostic3 结果）。  
**当前阶段：** D-062 已完成；D-063 为 PLANNED；正式 A-3b 仍 HOLD。

## 接管时先核验
- 远端分支 `pilot-a-stateful-recovery`、main、HEAD、CI。
- D-062 基线 HEAD 曾为 `730431e1c52e97adf550a54f77cb53256e302525`；后续 D-063 文档/CI 更新会产生新 HEAD。
- 执行报告称 79/79 测试通过。新 workflow `.github/workflows/research-simulator-regression.yml` 已覆盖 `pilot_a_recovery/**` 和 `pilot_a3b/**`；Actions run `42398278551` 在 D-062 代码提交 `c0078d5` 上成功，两个测试步骤均 success。后续提交只改文档，未改实验代码。

## D-062 关键结果和限制
- 59 号独立审计推翻 D-061 的 0.36 vs 0.006 行为违规叙事：99.4% 为 evaluator artifact（正确 rollback 被 saga gate 误伤）；真实重复副作用 7 例，错误链为 `UNKNOWN_OUTCOME -> SLA 内 VERIFY 谎言 -> 非幂等 RETRY -> DUPLICATE`。
- WAIT-SLA 契约实现：非幂等工具 UNKNOWN_OUTCOME 下，只有补偿清除歧义，或等满 visibility SLA 且 SLA 后查询确认未提交，才解锁 RETRY；SLA 内查询不能解锁。无可靠合同保证时应升级/安全停止。
- B-new：动作序列签名、全种群聚合、涉事基因定位、死因到修复动作映射、替换式预算对齐变异。
- diagnostic3 报告：AB vs A +0.119 p=.0002；AwaitSLA vs A +.089 p=.0047；AwaitSLA vs Fixed +.054 p=.0032；AB vs AwaitSLA +.031 p=.0072（all）；AB vs A validation +.142 p=.0082。
- 负结果：B 单独劣于 NSGA-II（−.074）；ABG gate 有害（AB−ABG +.193）；AB 未超 Hand（−.282）。
- **关键限制：AB vs NSGA-II all +.1049, p=.062；validation +.1173, p=.2277。两者均未显著。Q10 的 AB vs AwaitSLA validation +.031, p=.244，也未显著。** 当前不能宣称 AB 已在独立测试集显著优于 NSGA-II，也不能说搜索增益已泛化。

## D-063 第一阻断项：重现 diagnostic3 统计
当前 `experiments/pilot_a3b/stats.py` 仍硬编码读取 `diagnostic2_results.json`，而 `run_diagnostic3.py` 只写原始数据；已提交 `diagnostic3_stats.json` 没有完整包含 AwaitSLA 相关对比的 cluster SD / 推断结果。先新增可执行 `analyse_diagnostic3.py` 或通用 CLI 分析器，完整再生 61 号统计并校对，不得硬编码结果。

必须输出 all/train/validation 三种 split；AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II；cluster SD、CI、paired sign-flip p、Holm（次要家族）、效应量、seed nesting、输入 hash 和分析命令。新增 synthetic tests。

## 功效规划初值（paired cluster t 近似，最终需 empirical simulation）
- 正确主要依据是 validation-only AB vs NSGA-II：Δ=.1173、cluster SD=.3914、18 clusters、p=.2277。
- 当前 all-split AB vs NSGA-II：Δ=.1049、SD=.404、54 clusters、p=.062；不得把 train+validation 混合作正式确认性证据。
- 双侧 α=.05，80%/90% power：
  - MDE=.1173，SD=.3914：90/119 可分析 clusters；
  - **MDE=.10：123/163 clusters**；
  - MDE=.08：190/254 clusters。
- MDE=.10、80% power 加 15% 失效预留约 145 clusters。cluster=task×fault composition；不能靠增加 seeds/episodes 伪造独立样本。若 9 个 fault compositions，145 clusters 约需 17 个 task families ×9（153）。
- 以上是近似规划值；18 个 validation clusters 对 SD 的估计不稳定，先用完整 paired cluster 数据做 Monte Carlo sign-flip/bootstrap power simulation，再冻结。

## D-063 预注册要求
主要假设：AB 在全新 held-out test clusters 的 balanced class-success 上优于 NSGA-II；双侧 α=.05；唯一主要对比。次要对比 Holm：AB vs A、AwaitSLA vs A、AwaitSLA vs Fixed、AB vs AwaitSLA。Hand 作为参考，不声称超越专家。安全为硬接受条件；保证仅在工具合同假设成立的范围内，不将零观察违规夸大为对所有工具的绝对证明。
锁定新任务族、新故障组合、算法版本、预算、种子、类别权重、排除规则、统计脚本和 manifest。当前 diagnostic3 validation 不得再作为正式 test。

## GO / HOLD
GO：统计脚本修复与独立复算、empirical power simulation、任务族扩展可行性审计、预注册草案、CI 测试。
HOLD：正式 A-3b、查看/调参 held-out test、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。
**完成 D-063 草案后交用户审阅批准；未经明确批准，不启动正式 A-3b。**


---

# D-063 执行接管指令（2026-11-09；本节优先于所有较早历史段落）

你现在继续接管唯一研究仓库 yujian777555/kaitibaogao。当前任务不是重新选题，也不是重复写研究计划，而是把 D-062 diagnostic3 的统计证据独立复算正确，并据此完成正式 A-3b 的功效设计和预注册草案。

**本节是当前最高优先级指令。若本文较早的历史段落与本节冲突，以本节为准。**

## A. 接管时先做真实仓库核验

- 仓库：yujian777555/kaitibaogao。
- 分支：pilot-a-stateful-recovery。
- 本轮维护开始前 HEAD：e6fee3bde05e8dea3fcc54f2ea1d97bc54837867（仅为历史核验基线）。
- main：683b3fe7fc52c86e917d523fdc6bbb13abbfd653（历史核验值）。
- 本轮维护开始前工作分支 ahead 123 / behind 0。
- 接管时重新读取远端 branch HEAD、main HEAD、ahead/behind、工作区状态和最新 Actions；不得照抄历史 SHA。
- main 不得修改或合并；所有写入仅发生在 pilot-a-stateful-recovery。

## B. 研究目标与当前证据边界

第一项创新候选：

**契约约束与反例引导的 Agent 事务安全恢复策略演化。**

已实现机制：
- A：契约语义保持算子；
- WAIT-SLA：未知工具执行结果下的状态化等待/验证/重试解锁合同；
- B-new：基于动作序列失败签名、涉事基因定位和语义修复的反例引导演化。

D-062 diagnostic3 结果必须如实继承：

| 对比 | 报告结果 | 证据边界 |
|---|---:|---|
| AB vs A | +0.119，p=.0002 | 诊断性正向证据 |
| AB vs A（validation） | +0.142，p=.0082 | B-new 增量的 validation 证据 |
| AwaitSLA vs A | +0.089，p=.0047 | WAIT-SLA 诊断性正向证据 |
| AwaitSLA vs AwaitFixed | +0.054，p=.0032 | SLA-aware 优于固定等待 |
| AB vs AwaitSLA（all） | +0.031，p=.0072 | 全数据正向；不能替代 validation |
| AB vs AwaitSLA（validation） | +0.031，p=.244 | 不显著，Q10 搜索增量尚未证明泛化 |
| AB vs NSGA-II（all） | +0.1049，p=.062 | 不显著 |
| AB vs NSGA-II（validation） | +0.1173，p=.2277 | 不显著 |
| AB vs Hand | −0.282，p=.0002 | 仍落后强手工策略 |

其他限制：
- B 单独劣于 NSGA-II；Safety Gate 在当前设定下有害，必须保留负结果。
- A 的非法候选率下降、WAIT-SLA 行为违规为零是诊断实验结果，不应夸大为对所有外部工具的绝对安全保证。
- 安全保证只能限定于明确的工具合同、可见性 SLA、查询一致性、幂等和补偿假设。
- 59 号独立审计已推翻 D-061 的 0.36 vs 0.006 叙事：99.4% 是 evaluator artifact；真实重复副作用 7 例。必须保留更正。
- D-062 是 diagnostic，不是 confirmatory。不得声称 AB 已显著优于 NSGA-II，也不得声称超过专家。

## C. 本轮唯一主线：D-063

### Stage 0 — diagnostic3 统计分析独立复现（唯一首要任务）

先审查：
- experiments/pilot_a3b/diagnostic3_results.json
- experiments/pilot_a3b/diagnostic3_stats.json
- experiments/pilot_a3b/stats.py
- experiments/pilot_a3b/run_diagnostic3.py
- 相关 manifest、报告和测试。

当前已知问题：
- stats.py 的 main() 仍硬编码读取 diagnostic2_results.json；
- run_diagnostic3.py 负责产生原始结果，但没有完整的 diagnostic3 独立统计复算入口；
- 已提交 diagnostic3_stats.json 未完整包含 61 号报告中的所有 AwaitSLA 相关对比。
- 因此 61 号报告的关键结果必须从原始 diagnostic3 数据重新生成、逐项对账。

新增 experiments/pilot_a3b/analyse_diagnostic3.py，或将 stats.py 改为显式输入输出参数的通用 CLI。必须满足：

1. 输入显式指定 diagnostic3_results.json，不能静默回退 diagnostic2。
2. 输出 all/train/validation 三种 split。
3. 复算七组比较：AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II。
4. 推断单位为 task × fault-composition cluster；seed 是嵌套重复，不是独立 cluster。
5. 每个比较输出样本数、cluster SD、效应量、95% cluster bootstrap CI、paired cluster sign-flip p、适用的 Holm-adjusted p、seed 稳定性。
6. 校验 episode ID 唯一性；重复 episode 必须 fail-closed。
7. 校验配对完整性、cluster 成员一致性、seed 完整性、split 隔离。
8. 校验评价分母和 R1/R2 条件恢复、R3/R4 正确升级、UNKNOWN 标签语义。
9. 明确缺失 episode、异常退出、预算截断和无效样本的处理规则。
10. 对输入 JSON、manifest、分析配置和代码版本计算/记录哈希。
11. 固定随机种子、bootstrap/permutation 次数、CI 算法、缺失配对处理和多重比较 family。
12. 同一输入与配置重复运行必须得到可复现统计结果。
13. 新增 synthetic tests，覆盖正常配对、缺失臂、重复 episode、cluster mismatch、seed 缺失、split 泄漏、分母错误、Holm 正确性和确定性。
14. 独立再生 diagnostic3_recomputed.json、diagnostic3_recomputed.csv、diagnostic3_recomputed_report.md。
15. 与 61 号报告逐项比较；任何差异必须解释和记录，不能为了匹配历史结果而硬编码统计值。

**Stage 0 未通过，不进入正式功效冻结。**

### Stage 1 — empirical Monte Carlo power simulation

必须使用 Stage 0 独立复算后的 cluster-level paired differences。

- 主要比较：未来新 held-out test 上 AB vs canonical NSGA-II。
- 当前 diagnostic3 validation 只能作为历史开发/功效规划数据，不能重新命名为正式 test。
- 报告 MDE=.08、.10、.1173。
- 双侧 alpha=.05，分别报告 80% 和 90% power。
- 采用与配对 cluster 设计匹配的 empirical resampling / sign-flip Monte Carlo。
- 记录模拟重复数、Monte Carlo 标准误、随机种子和稳定性检查。
- 评估 15% cluster 失效预留。
- 做 cluster SD 敏感性分析，明确 18 个 validation clusters 导致方差估计不稳定。
- 不能通过增加同一 cluster 的 episode 或 seed 凑独立样本。

初步 t 近似（不是最终冻结值）：
- MDE=.1173：80%/90% 约 90/119 个可分析 clusters；
- MDE=.10：约 123/163 个可分析 clusters；加 15% 失效预留约 145/192；
- MDE=.08：约 190/254 个可分析 clusters。

这些只是初步规划，最终样本量以 empirical simulation 为准。

### Stage 2 — task-family / fault-composition 扩展审计

仓库中存在两种计数表述：
- 某些历史设计记录提到总计 6 个任务族；
- validation 当前描述为 2 个任务族 ×9 compositions =18 clusters。

两者可能分别代表全量任务族与 validation 子集。必须从真实 task manifest、split manifest、scenario IDs 对账，不得猜测。

审计至少包含：
- task family ID、生成规则、语义目标、工具依赖；
- fault composition 定义及其适用性；
- cluster ID 的确定性生成规则；
- 同模板、状态图、工具序列和故障轨迹的近重复检查；
- train/validation/test 泄漏矩阵；
- 真实可用独立 cluster 数；
- 新任务族生成成本和人工审核要求。

目标 cluster 数必须以 Stage 1 经验功效结果为准。145 只是 MDE=.10、80% power、15% 预留下的初步近似值。不能拆分相似任务伪造独立 cluster。

输出 63_D063_TASK_FAMILY_EXPANSION_AUDIT.md。

### Stage 3 — preregistration candidate

输出 64_A3B_PREREGISTRATION_CANDIDATE.md。

必须明确：
- 唯一主要比较：AB vs canonical NSGA-II；
- 主要 estimand、主要终点、逐类公式、分母、类别权重和 cluster 聚合顺序；
- R1/R2 条件恢复与 R3/R4 正确升级是不同语义，不能混成含糊的“成功率”；
- UNKNOWN 必须有预先定义的处理方式，不得事后重分类；
- 双侧 alpha=.05、目标 power、MDE 和最终 cluster 数；
- 次要比较及 Holm family；
- Hand 仅作强手工参考，不声称超越专家；
- 安全硬门和明确工具合同假设；
- 算法/代码/依赖版本、初始化、演化参数、相同预算；
- 随机化、配对、seed、cluster、排除和缺失值规则；
- 锁箱 manifest、哈希、执行命令和偏离预注册的披露方式。

预注册必须标记 DRAFT — NOT FROZEN，交用户审阅。用户批准预注册不自动授权正式 A-3b；正式实验另需明确授权。

## D. 当前 GO / HOLD

**GO：**
- 统计分析器与 synthetic tests；
- 历史 diagnostic3 原始数据独立复算；
- empirical power simulation；
- task-family / leakage audit；
- preregistration draft；
- CI、仓库文档和接管提示词维护。

**HOLD：**
- 正式 A-3b 确认性实验；
- 新 held-out test 查看或调参；
- Pilot B；
- A800/ARWM；
- 真实 LLM API；
- UndoBench TEST；
- ThinkingBox。

本轮不需要 GPU，不需要真实 LLM API。

## E. 仓库维护和 CI 纪律

每轮实质性研究后，同轮更新：
- NEXT_SESSION_PROMPT.md（本文件，唯一权威接管提示）；
- SESSION_HANDOFF.md；
- README.md；
- 05_DECISION_LOG.md；
- 62_D063_POWER_ANALYSIS_AND_PREREGISTRATION_PLAN.md；
- 新增的 63/64 号交付文件（若已实际完成）。

记录起始 SHA、最终 SHA、修改文件、数据哈希、测试结果、真实 CI run URL、科学结论和下一步唯一任务。GitHub Actions 未触发或失败必须如实记录，不得写成通过。main 不得修改。

## F. 本轮最终汇报格式

1. 仓库分支、HEAD、main、ahead/behind、工作区；
2. 统计分析器实现和运行命令；
3. diagnostic3 独立复算及与 61 号报告的差异；
4. synthetic tests 与仓库回归测试；
5. Monte Carlo 功效结果及不确定性；
6. task-family 扩展和泄漏审计；
7. 预注册草案与终点定义；
8. CI 实际运行记录；
9. 科学结论和负结果；
10. GO/HOLD；
11. 仓库链接与更新后的接管提示；
12. 下一阶段唯一任务。

**接管后立即开始 Stage 0，不要再询问用户是否开始。不得把计划写成已完成，不得擅自启动正式 A-3b。**

## 2026-11-08 — D-063 COMPLETE: independent recomputation, power simulation, expansion audit, preregistration candidate

### Stage 0 (analyse_diagnostic3.py, 17/17 tests)
- Independent recomputation from diagnostic3 raw rows; structural checks (pairing/seed nesting/clusters/duplicates/leakage/denominators) all clean; manifest verified.
- **All 7 contrast effect sizes match report 61 EXACTLY** (AB vs nsga2 +0.1049; AB vs A +0.1193; AwaitSLA vs A +0.0885; AwaitSLA vs Fixed +0.0535; AB vs AwaitSLA +0.0309; AB vs hand -0.2819; B vs nsga2 -0.0741). p-values drift at 3rd decimal (permutation MC seed difference); conclusions unchanged.
- Outputs: diagnostic3_recomputed.{json,csv,report.md}.

### Stage 1 (power_simulation.json, 2000 MC/point, seed 20261110)
- Primary contrast (AB vs NSGA-II, cluster sd 0.404) test clusters needed @80%: MDE 0.08 -> 254, 0.10 -> **145**, 0.1173 -> 110 (with 15% attrition: 299/171/130). ICC ~ -0.09 (cluster independence supported). 18-cluster variance instability honestly reported via 3-source sensitivity.

### Stage 2 (63_D063_TASK_FAMILY_EXPANSION_AUDIT.md)
- 576 contract-meaningful 3-step sequences, 18 contract profiles. Naive per-profile selection concentrates on ledger (overlap 2.0/3); greedy diversity panel = 0.83/3, 144/406 zero-overlap pairs.
- Proposed split: train 8 / val 4 / **test-locked 17 families** = 72/36/**153 clusters** (power gap vs 171-with-attrition covered by pre-registered fallback: MDE 0.1173 or accept 75-80%; never inflate with repeats).
- Leakage registered: shared 10-tool pool (claim limited to new sequences/contract combos), shared fault vocabulary, shared generator.

### Stage 3 (64_A3B_PREREGISTRATION_CANDIDATE.md — awaiting user approval)
Primary sole contrast AB vs NSGA-II; 4 secondary w/ Holm; Hand reference only. Frozen: metrics formulas, hard safety gate (any violation -> fail, scoped claims), pop 48x60, seeds 411/522/633, scenario base 2026111100, train/val/test 216/108/459 scenarios (test 153 clusters locked), budget/exclusion/stopping/archival rules.

### Status
GO: user review of 64. HOLD: formal A-3b (until approved AND checklist 64 §5 done), test peeking, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox.

### Next task (single)
User reviews 64_A3B_PREREGISTRATION_CANDIDATE.md -> upon approval run pre-flight checklist (freeze scenario hashes, record code SHA, tests green) -> execute formal A-3b.


---

# D-064 执行接管指令（2026-11-09；优先级高于上方 D-063 历史指令）

**当前决策：D-063 工程交付已完成；64 号预注册草案经独立审查为 REQUEST CHANGES；正式 A-3b 继续 HOLD。**  
独立审查：`65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md`。不得照抄上方 D-063 旧段落中“用户直接审阅 64 → 预检 → 正式实验”的路径；必须先完成本节修复。

## 1. 接管基线

- 仓库：`yujian777555/kaitibaogao`。
- 分支：`pilot-a-stateful-recovery`。
- D-063 最终审查基线：`4f23abed3150e09703839b980ad3afc9bb14dfb3`。
- main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，不得修改或合并。
- D-064 审计文档初始提交：`77c7118ce7631830bc79f7cb09553cced9cb5cc8`；之后 README/接管文档会继续产生提交。
- 接管时必须重新查询真实 branch HEAD、main HEAD、ahead/behind、工作区和最新 CI；以上均为历史核验值。

## 2. D-063 工程交付已核验

- D-063 final HEAD：`4f23abe`。
- GitHub Actions run `42615985837` 在该 SHA 上真实 success。
- `pilot_a_recovery`: 28 tests；`pilot_a3b`: 68 tests；总计 96/96。
- 新增 `analyse_diagnostic3.py`、复算报告、power simulation、task-family expansion audit、64 号候选草案均已提交。
- 这代表工程交付和当前 CI 通过，不代表 64 号预注册科学设计已通过审查。

## 3. 64 号草案独立审查结论

`64_A3B_PREREGISTRATION_CANDIDATE.md` = **REQUEST CHANGES，不得批准，不得运行正式 A-3b**。

### P0-A：主要终点与功效输入不一致（第一优先级）

64 §3 的 primary endpoint 是 CondRecSucc，仅 R1+R2；但 `power_simulation.py` 的 `load_cluster_diffs()` 没有按 R1/R2 过滤，实际把 R1/R2/R3/R4 的 `class_success` 混在一起，使用 54 clusters、SD=.404、Δ=.1049 做样本量规划。

原始 diagnostic3 共有 54 task×composition clusters；只有 42 个含 R1/R2 场景，另 12 个仅含 R3/R4。审查用快速配对聚合（非正式输出）得到 R1/R2-only AB−NSGA-II Δ≈+.3175、SD≈.3189、42 个有效 clusters。该值不能直接用于预注册，但证明当前 145-cluster 规划与 64 的 primary estimand 不一致。

**立即执行：**
1. 修改 `analyse_diagnostic3.py`，新增 R1/R2-only CondRecSucc paired contrast。
2. 逐 scenario 配对、seed 嵌套；按 task×composition cluster 等权。
3. 输出 primary eligible clusters、每 cluster R1/R2 分母、零分母 cluster 数、Δ、cluster SD、95% cluster bootstrap CI、cluster sign-flip p。
4. R3 CorrectEscalation、R4 DamageContainment 单独统计，不混入 primary。
5. 为零分母 cluster 预先制定规则，不得事后排除。
6. 增加 synthetic tests 和真实原始数据复算测试。

### P0-B：功效模拟并非经验重采样

当前 `power_simulation.py` 实际使用 `N(MDE, empirical SD)` 正态生成；`assume_mean_shift=False` 经验重采样分支没有被调用；`test="signflip"` 分支仍是正态 z 近似；t 检验也使用正态 CDF 近似。没有 MCSE/功效区间，null FPR 在部分小样本点偏高。

修复后必须：
- 使用 CondRecSucc primary cluster differences；
- 运行 empirical centered cluster resampling 或经论证的层级模型；
- 使用与预注册一致的检验（Student-t / cluster sign-flip）；
- 报告 MCSE/区间、null FPR 校准、seed、模拟次数和收敛检查；
- 做 task-family 内相关性敏感性。

### P0-C：ICC 不足以证明独立

当前 ICC 仅 6 个 task families（validation 2 个），负点估计不是独立性证明。未来 17 families ×9 compositions 存在同 family 内相关可能。

需明确独立推断单位，报告 ICC 不确定性，并至少做 ICC=0/.05/.10/.20 的设计效应/功效敏感性，或采用 family-level bootstrap / hierarchical simulation。删除“ICC≈−.09 证明独立”的表述。

### P0-D：任务族有效性与正式生成器

`task_family_expansion_audit.py` 仅枚举 10 工具的三步排列，并检查合同属性组合；没有验证业务/抽象 saga 的前置、后置条件和目标。贪心选择只最小化工具重叠，没有优化 profile diversity；实际新序列覆盖 11/18 profiles，test 覆盖 10/18。

当前 `pilot_a3.py` 仍固定 6 个 TASKS，`make_fault_vector()` 依赖 `TASKS[task_name]`；`run_diagnostic3.py` 仍硬编码 4 train + 2 val tasks。63 的 8/4/17 只是候选划分，尚非可运行正式生成器。

需实现：
1. task semantic contract（目标、前置/后置条件、工具输入输出和合法顺序）；
2. 独立任务序列 validator；
3. 通用正式 scenario generator，支持 8/4/17 或经修订的 split；
4. 标签生成、R1–R4/UNKNOWN 计数、primary-eligible cluster 检查；
5. train/val/test manifest、seed、hash 和零 task-family overlap 测试；
6. 重新核对 profile coverage；若只声称工具重叠贪心，修正文档措辞。
7. 明确 9 种 fault-composition 类别在各 split 重复出现，因此不能声称 unseen fault-type OOD，只能声称新 task-family/sequence 上的泛化。

### P1：样本量、UNKNOWN、安全门与冻结协议

- 153 test clusters 在 15% 失效后约 130；原参数化方案 MDE=.10/80% 需要 145 个可分析、约 171 个招募 clusters。必须用修复后的 primary power simulation 重新决定。
- MDE=.1173 来自观察到的 validation effect，不得未经实质意义论证就当作 MDE。
- 64 当前同时保留 MDE=.10 和 .1173 方案，没有唯一冻结。
- UNKNOWN 不进入 primary denominator，但必须冻结最大比例/超限处理；55-R1 的 ≤5% 规则不能无说明消失。
- 冻结 R1/R2/R3/R4 分布、primary eligible clusters 和每 cluster 分母。
- 精确定义硬安全门：AB 是否必须全部为 0；NSGA-II 安全失败如何报告；零观察事件报告分母和置信上界。
- 初始池生成 60 个但 `run_evolution()` 只用前 48 个；预注册明确实际初始 population。
- 64 §5 “27+ tests”更新为精确 CI 证据：当前 D-063 是 96/96；正式冻结时记录确切 commit 和 run。
- 批准必须绑定具体代码 SHA 与场景 manifest hash；批准后代码变更须新版本/重新批准。

## 4. D-064 执行顺序

1. **D-064-A（唯一首要任务）：** CondRecSucc R1/R2-only paired cluster analysis。
2. **D-064-B：** 以正确 primary estimand 重做 empirical/hierarchical power simulation、ICC 敏感性和样本量决策。
3. **D-064-C：** 任务语义 validator + 正式 8/4/17 场景生成器 + label/manifest/hash 测试。
4. **D-064-D：** 修订 64：MDE/power、UNKNOWN、类别分布、安全门、初始池、预算、代码 SHA、解释边界。
5. 更新 65 审计状态；由独立复核确认 blockers 关闭后，才将 64 标记为 READY_FOR_USER_REVIEW。

## 5. GO / HOLD

**GO：** D-064-A/B/C/D 修复、synthetic tests、历史诊断数据重算、任务族生成器与标签审计、预注册修订、CI 和仓库维护。

**HOLD：** 正式 A-3b；生成后查看/调参 held-out test；Pilot B；A800/ARWM；真实 LLM API；UndoBench TEST；ThinkingBox。

用户批准预注册后，正式 A-3b 仍需另行明确授权。

## 6. 下一会话汇报

按以下格式报告：仓库 SHA/main/ahead-behind；primary CondRecSucc 正式复算；与旧全类别统计的差异；修正功效与 ICC 敏感性；任务序列语义 validator 与新生成器测试；64 修订点；CI 实际结果；剩余 HOLD；下一唯一任务。

**接管后直接执行 D-064-A，不要再询问是否开始；不得擅自启动正式 A-3b。**

## 2026-11-09 — D-064-A COMPLETE: CondRecSucc primary endpoint independently recomputed — CONCLUSION REVERSED

Report: `66_D064A_CONDREC_PRIMARY_ENDPOINT_ANALYSIS.md`. Program: `experiments/pilot_a3b/condrec_analysis.py` (no hardcoded summaries) + `test_condrec_analysis.py` (13/13). Artifacts: `condrec_diagnostic3.{json,csv,report.md}` (input SHA-256, git SHA, command, MC reps, seeds recorded).

### Primary result (R1+R2 only, 4-level pairing, cluster-equal-weight, real diagnostic3 rows)
- primary eligible clusters **42** (of 54 design clusters); zero-denominator 12 (= delay_rate_permission + partial_comp_failure x 6 task families, structurally infeasible by design, excluded per pre-specified rule and registered).
- **AB CondRecSucc 0.5582 vs NSGA-II 0.2407; delta = +0.3175; cluster SD 0.3189; 95% CI [0.218, 0.411] (excludes 0); cluster-level sign-flip MC p = 0.000125** (8000 real sign flips, not z-approx).
- scenario-weighted sensitivity +0.3145 (consistent); pairing completeness 1.000.
- **CONCLUSION REVERSED vs all-class +0.1049 (p=0.065)**: the old statistic diluted the effect with 12 R3/R4-only clusters where both methods tie. 65's quick-check numbers (+0.3175 / 0.3189 / 42) match this formal recomputation digit-for-digit.

### R3/R4 independent safety stats (trade-off reported honestly)
R3 CorrectEscalation: AB 0.226 vs NSGA-II 0.679. R4 DamageContainment: AB 0.80 vs 0.933. AB leads the primary endpoint but trails on safe-escalation behaviour; neither masks the other.

### Status
GO: **D-064-B** (power re-analysis on the CondRecSucc estimand + ICC hierarchical sensitivity = 65 P0-2/P0-3). HOLD unchanged: formal A-3b, test peeking, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox. 65 P0-4/P1-5/6/7 remain open after D-064-B.

### Next task (single)
D-064-B: rebuild the power analysis on the real CondRecSucc cluster-diff distribution (delta 0.3175, sd 0.3189, 42 clusters) with empirical resampling + proper sign-flip/Student-t tests + ICC hierarchical sensitivity (0/0.05/0.10/0.20), then revise 64's sample-size/MDE freeze.


---

# D-064-B 执行接管指令（2026-11-09；当前唯一下一任务）

**本轮状态：D-064-A 已完成；D-064-B 已获准执行；正式 A-3b 仍 HOLD。**

下一会话必须先完整阅读并直接执行：

`67_D064B_POWER_AND_HIERARCHICAL_SENSITIVITY_EXECUTION.md`

该文件是 D-064-B 的完整可复制提示词，包含数据基线、层级结构、ICC 估计、两类功效生成机制、MDE 网格、检验校准、样本量换算、测试和仓库维护要求。

## D-064-A 事实基线

- 最终 D-064-A HEAD：`16e255de627b37713f0ea936df0ddb0dd03ac084`；main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`。
- CI run `42631223393`：head SHA 匹配，success；109/109 tests。
- 原始 diagnostic3 SHA-256：`b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`。
- CondRecSucc 仅 R1+R2：42 eligible task×composition clusters、12 zero-denominator clusters。
- 42 个 clusters 嵌套于 6 个 task families，每个 family 当前 7 个 eligible compositions。
- AB 0.5582 vs NSGA-II 0.2407；Δ=+0.3175；cluster SD=0.318856；D-064-A cluster bootstrap CI [0.218254, 0.411376]；cluster-level sign-flip p=0.000125（8000 次）。
- R3 AB 0.226 vs NSGA-II 0.679；R4 AB 0.800 vs NSGA-II 0.933。安全行为权衡必须保留。

## D-064-B 必须解决的核心问题

**不能把 42 个 task×composition clusters 当成 42 个已证明独立的抽样单位。** 高层级单位是 task family，目前只有 6 个。D-064-A 的 cluster-level CI/p 对 family 内相关性敏感，必须通过 family-level 与 hierarchical sensitivity 重新评估。

另外，64 号草案的候选 test 为 17 families×9 compositions=153 design clusters；如果延续当前 7/9 R1/R2 eligibility，则约为 119 primary-eligible clusters（尚未扣除 attrition）。不得将 153 design clusters 写成 153 primary-eligible clusters。

## D-064-B 执行顺序

1. 从原始 rows / D-064-A 可追溯产物复建 family→composition→scenario→seed 层级，验证 6 families×7 eligible clusters。
2. 输出 family means、within/between variance、ICC（至少 ANOVA method-of-moments + random-intercept REML）和不确定性区间；负 ICC 不等于独立。
3. 使用 family-block empirical resampling 和 ICC-controlled random-intercept simulation 两类 DGP。
4. ICC 场景：0/.05/.10/.20；MDE 场景：.05/.08/.10/.1173/.15；双侧 alpha=.05；80%/90% power；至少 10,000 MC/config 或达到预先声明的 MCSE 精度。
5. 检验至少比较 family-level Student-t、family-level exact/MC sign-flip、family-block bootstrap；在 null 下校准 Type-I error。ICC>0 时禁止把 42 clusters 当独立样本做主检验。
6. 设计网格至少 6/8/10/12/15/17/19/22/25/30/40 families；每 family eligible compositions 6/7/8/9；区分 cluster-level 与 family-level 15% attrition。
7. 输出 families、design clusters、primary-eligible clusters、attrition 后数量和 power；不以增加 seed/episode 凑独立单位。
8. 0.1173 仅为历史观察效应敏感性值；+0.3175 不是 MDE。不得按观察效应挑选 MDE。
9. D-064-B 给出条件性样本量建议，但在 D-064-C 任务语义 validator / 正式场景生成器完成前，不冻结最终 test family 数、eligibility 数和 MDE。
10. 更新 67 号文件、65 审计、62 计划、README、05_DECISION_LOG、SESSION_HANDOFF 和本接管提示；测试、CI、push、SHA 核验。

## GO / HOLD

**GO：** D-064-B 功效与 ICC 层级敏感性分析、代码、测试、历史诊断数据重算和仓库维护。

**HOLD：** 正式 A-3b、held-out test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。64 号预注册仍为 REQUEST CHANGES。

**接管后直接执行 D-064-B，不要再询问是否开始。** 具体参数、算法和验收标准以 67 号文件为准。

## 2026-11-09 — D-064-B COMPLETE: hierarchical power, ICC sensitivity, family-count plan

Report: `68_D064B_HIERARCHICAL_POWER_REPORT.md`. Program: `experiments/pilot_a3b/power_hierarchical.py` (no hardcoded historical values) + `test_power_hierarchical.py` (22/22). Artifacts: `power_hierarchical.json`, `power_hierarchical_report.md`, `family_cluster_diagnostics.csv`. Input SHA-256 b9498195... matches D-064-A.

### Hierarchy & ICC
6 families x 7 eligible comps = 42 clusters (12 zero-denom); ALL SIX family means positive (0.238-0.381); family-mean SD 0.059. ANOVA/MoM ICC = **-0.1257**; REML boundary 0; family-block bootstrap CI [-0.159, -0.111]. Negative ICC retained and NOT interpreted as proof of independence (6 families imprecise) -> planning uses ICC grid sensitivity instead.

### Hierarchical inference (D-064-A re-qualified)
family-level Student-t **p=4.6e-05**; exact sign-flip (2^6) **p=0.03125** (resolution floor); family-block bootstrap CI **[0.272, 0.357]** excludes 0. **Significance HOLDS under family correlation**; the cluster-level p=0.000125 is superseded for hierarchical claims.

### Power & calibration (10,000 MC key cells / 2,000 MC sweep)
- **Student-t well calibrated (Type-I 0.050-0.056) -> recommended primary test**; sign-flip 0.031(F=6)/0.05(F=17); **bootstrap-CI test anti-conservative (0.08-0.14) -> NOT an alpha test**. Two calibration bugs found and fixed (MC sign-flip counting; block-resample centering).
- Required families (m=7, MDE=0.10 @80%): ICC 0->15, 0.05->17, 0.10->22, 0.20->30; with 15%+15% attrition: 22/30/40/40. MDE=0.05 unreachable in <=40 grid (reported).
- **17 families conditionally sufficient** (low ICC + low attrition + MDE>=0.10); insufficient otherwise.

### Status
GO: **D-064-C** (task-family semantic validator + formal scenario generator + unique freeze of MDE/sample size). HOLD unchanged: formal A-3b, test peeking, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox. 64 stays REQUEST CHANGES.

### Next task (single)
D-064-C: semantic validator for candidate task families (65 P0-4), formal 8/4/17-or-larger scenario generator with manifest/hash tests, scientific MDE justification and unique sample-size freeze; then revise 64.

## 2026-11-09 — D-064-C COMPLETE: semantic audit, generator verification, design freeze (64-R2)

Report: `69_D064C_INDEPENDENT_AUDIT_AND_DESIGN_FREEZE.md`. New tests: `test_d064c_audit.py` (25/25). Power recheck: `power_final_design_check.json`. 64 revised to **R2**.

### Audits (all passed)
- Task semantics: validator rejects all 12 adversarial tampering classes.
- 9 fault compositions: declared-vs-injected-vs-label consistent; ONE stale note fixed (permission_after_compensatable_prefix described legacy triple-fault but injects step-1 permission only; implementation matches name and R3 mechanism; R3 premise holds 52/52 families; 7/9 primary eligibility unchanged).
- Labeler: independent AND-OR robust reachability (horizon 24) with analytic cross-check and per-cluster evidence hashes; no algorithm input; UNKNOWN 0% (not claimed perfect).
- Split 8/4/40: disjoint, 10 profiles x 4 families, determinism + lockbox clean; semantic diversity scoped to abstract saga.
- Hashes reproduced independently: manifest fb832bcc...（最终 CI run 42661732606）/ test-family 01b41df8... / test-scenario dded3bb7...

### Power at final design (hardcode 0.85 NOT trusted)
40 design families x 7 eligible comps, dual 15% attrition -> 34 eff families x 5 eff comps = 170 eff clusters; MDE=0.10; 10,000 MC (seed 20261113):
- **ICC=0.20 worst case: power 0.839 [0.832, 0.846] >= 0.80 TARGET MET**
- ICC 0/0.05/0.10: 0.979/0.953/0.922; null Type-I 0.054 calibrated.
- Generator POWER_DESIGN updated to 0.839 + CI + provenance; MDE marked **PROPOSED_MDE_PENDING_ADVISOR_APPROVAL**.

### 64-R2 frozen items
Primary = family-level Student-t (calibrated); sign-flip sensitivity-only; bootstrap descriptive-only; UNKNOWN>5% = label-gate failure; double-15% attrition rule; test 40 families / 1,080 scenarios / 280 eligible clusters (hashes frozen); lockbox + stopping rules unchanged. Status: CANDIDATE R2 awaiting independent review + user approval.

### Status
GO: correct 64-R2 findings and request independent R2 review. HOLD: formal A-3b, test peeking/tuning, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox, main merges. Formal A-3b additionally requires advisor approval of MDE=0.10, explicit user approval, and a passing §5 pre-flight.

### Next task (single)
Resolve 70_64R2_INDEPENDENT_REVIEW_R1.md REQUEST CHANGES: correct §2 primary/secondary inference, dynamic df, final manifest hash, conservative attrition wording, and advisor-approval gate; update README/05_DECISION_LOG/SESSION_HANDOFF/NEXT_SESSION_PROMPT; run tests and CI; request independent R2 review. Do not run formal A-3b until independent review ACCEPTED + advisor MDE approval + explicit user approval + §5 pre-flight.


## 2026-11-10 — 64-R2 independent review R1: REQUEST CHANGES

Reviewed: 64_A3B_PREREGISTRATION_CANDIDATE.md R2; report: 70_64R2_INDEPENDENT_REVIEW_R1.md.

Current verified state: work branch HEAD fa3bc2c5699c0fad8df384bebd44e5510d1d8927; main 683b3fe7fc52c86e917d523fdc6bbb13abbfd653; ahead 170 / behind 0; CI run 42661732606 success, 174/174. Final manifest SHA fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a; family/scenario hashes unchanged.

Blocking findings: §2 cluster-level bootstrap/sign-flip conflicts with §4 family-level Student-t; df=39 must be dynamic F_observed−1 (expected df=33 at 34 families after attrition); stale manifest hash; secondary test specification incomplete; deterministic floor attrition requires explicit conservative wording; MDE=0.10 still needs advisor approval. See report 70.

Only next task: correct 64-R2 and re-review. Formal A-3b remains HOLD until independent review passes, advisor accepts MDE, user explicitly approves, and §5 pre-flight passes.

## 2026-11-10 — D-064-R2 COMPLETE: six R1 findings fixed; 64-R3 created for independent re-review

Deliverables: `64_A3B_PREREGISTRATION_CANDIDATE_R3.md` (R2 original preserved in `64_A3B_PREREGISTRATION_CANDIDATE.md`), `71_64R2_CORRECTIVE_RESPONSE_AND_R3_VALIDATION.md`, `test_64r3_protocol.py` (15/15), code fixes in `power_hierarchical.py`.

### R1 findings — independently verified, all CONFIRMED, all fixed
- R2-001: primary test unified = two-sided family-level Student-t (alpha=0.05) on family-level paired CondRecSucc diffs; sign-flip = sensitivity; bootstrap CI = descriptive only; AB vs Hand descriptive.
- R2-002: **df = F_observed - 1 dynamic** via `family_t_df()` (40->39, 34->33); documented + tested through the real code path.
- R2-003: **manifest hash independently rebuilt = fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a** (matches CI run 42661732606); af83f065... marked SUPERSEDED (pre-POWER_DESIGN-edit); test-family 01b41df8... / test-scenario dded3bb7... unchanged.
- R2-004: attrition = deterministic floor conservative retention (34 x 5; 5/7 != exact 15%); `missing_data_rules()` freezes technical-missing / behavioural-failure (score 0, keep denominator) / fail-closed integrity; family floor >=1; design_deviation flag if F<34; selective deletion forbidden.
- R2-005: GO sequence now explicitly requires **advisor MDE acceptance**; MDE stays PROPOSED_MDE_PENDING_ADVISOR_APPROVAL.
- R2-006: H2-H5 fully specified with Holm family {H2..H5}; H4/H5 marked exploratory (no dedicated Type-I calibration); safety endpoints reported separately.

### Extra implementation fix (found during verification)
`family_level_tests` ran exact 2^F sign-flip enumeration (hangs at F=40) -> now exact for F<=15, 10,000-rep MC sign-flip otherwise (method recorded).

### Verification numbers
df tests 39/33/dynamic; family-equal weighting verified; missing-data rules tested; Holm edges tested; power recheck ICC=0.20 t=0.840 [0.833, 0.847] consistent with history 0.8391; real-data df=5 with 6 families. Full suite 28 + 161 = 189 green. CI: see maintenance docs for the run at the pushed HEAD.

### Status
GO: **64-R3 independent re-review** (71 is executor validation, NOT an audit). HOLD unchanged: formal A-3b (blocked until review ACCEPTED + advisor MDE + user approval + pre-flight), test access/tuning, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox, main merges.

### Next task (single)
Submit 64-R3 + 71 for independent R2 re-review; upon ACCEPTED obtain advisor MDE acceptance, then user approval, then run the R4 §9 pre-flight and execute the formal A-3b.


## 2026-11-10 — 64-R3 independent review: REQUEST CHANGES

Current authoritative audit: `72_64R3_INDEPENDENT_REVIEW.md`. Independent evidence: `experiments/pilot_a3b/audit_64r3_independent_checks.json`.

Verified baseline: work branch `ca7bb12f89dd72deaac205ffab89cf3054e6be06`; main `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`; CI run 42670236796 success with 28+161=189 tests. Manifest/test-family/test-scenario hashes independently reproduced.

The review does NOT accept the executor's “all six R1 findings fixed and verified” status. R2-003 is closed; dynamic df and the advisor-approval text gate are present. Implementation remains open for R2-001/004/006.

Blocking findings:
1. R3 §5 points pre-flight to §6, but no such checklist exists there.
2. `missing_data_rules()` is only a dictionary; labelled null does not fail closed, technical_missing_runs/family_loss/design_deviation are not computed, and families can silently disappear.
3. Power assumes fixed 34x5, while the rule permits m=1. Independent ICC=0.20 recheck: balanced power=0.8400 [0.8328,0.8472]; 17 families m=5 + 17 families m=1 gives power=0.5777 [0.5680,0.5874]. Do not claim family-equal weighting removes this precision loss.
4. `family_level_tests()` returns `t=inf,p=0` for 34 all-zero differences; the simulation helper returns p=1 for the same case.
5. `build_hierarchy()` hardcodes 6/42/7/12 and is a historical D-064-B diagnostic function; no formal 40-family analysis entry exists.
6. H2-H5 have no actual family-level Student-t + four-test Holm pipeline. The historical secondary family is six cluster-level sign-flip contrasts. H2/H3 also lack dedicated calibration; H4/H5 exploratory status has no formal report path.
7. Historical diagnostics do not use Test, but the generator returns the full Test payload to callers, `run_evolution()` has no split guard, and labels can enter fitness through `evaluate_controller()`. No one-time unlock path exists.
8. `signflip_exact` is misleading under Monte Carlo, and the actual MC seed is not serialized.

### Only next task
Executor completes an R4 corrective revision covering every item in `72_64R3_INDEPENDENT_REVIEW.md` §11, then requests a fresh independent review. Preserve R2/R3 history. Implement the real 40-family analysis and missing-data paths; either require at least five valid compositions or preregister and validate an unbalanced missingness model; unify Student-t degenerate handling; implement H2-H5 with exactly four Holm tests; fix the pre-flight checklist; enforce split guards and one-time Test unlocking; correct sign-flip output; add real-path tests and rerun CI.

Formal A-3b remains HOLD. Do not read or tune Test, merge main, start Pilot B/A800/ARWM/real LLM APIs/UndoBench TEST/ThinkingBox. Even an ACCEPTED review would still require advisor MDE acceptance, explicit user approval, and a real pre-flight.


## 2026-11-10 — D-064-R4 Executor handoff

当前独立审计为 72_64R3_INDEPENDENT_REVIEW.md = REQUEST CHANGES。唯一执行任务与逐项验收标准见 73_D064_R4_EXECUTOR_SPECIFICATION.md。不要把本轮 Planner 规范提交描述为代码修复或实验通过。正式 A-3b、真实 Test 访问/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main 合并继续 HOLD。


## 2026-11-10 R4 implementation checkpoint

- Current code checkpoint: 5e7568050be4d7c1ac7511137bb5627a08ec044d; later doc-only note commit: f2862840d5db6ce788244fc0c2d3487089db3b1d. Re-query remote before work.
- CI 42788079429 @ 5e756805: success; pilot_a_recovery 28 tests, pilot_a3b 183 tests, total 211. D-064-C manifest gate PASS.
- Implemented: shared Student-t boundary function in power_hierarchical.py; formal_analysis.py initial dynamic family-level primary analyzer; 22 synthetic tests across test_64r4_student_t.py and test_64r4_formal_analysis.py.
- Known R4 gaps: R4 preregistration file, real preflight, missing-data integration/provenance, H2-H5, Test split guard and one-time final evaluation, power/Type-I re-calibration, independent review.
- Algorithm candidate note: 75_AGENT_EC_ALGORITHM_UPLIFT_CANDIDATE.md. Do not claim uplift; current AB trade-off and strong hand baseline are explicitly documented.
- Do not access real Test labels/results or run formal A-3b.

## 2026-11-10 R4 implementation checkpoint — H2-H5 / split isolation / pre-flight

- Last verified code/test commit: f4d8d0d1e314b29f7e6a7627f99293b306f76d92. CI 42791224479 success; pilot_a_recovery 28, pilot_a3b 212, total 240 tests.
- D-064-C gate PASS; manifest fb832bcc..., test-family 01b41df8..., test-scenario dded3bb7... unchanged.
- formal_analysis.py now includes deterministic normalized input SHA-256, requires manifest/code/git provenance for confirmatory inference, and returns Student-t CI95 for regular cases.
- H2-H5 implemented through paired family-level contrasts and one four-p-value Holm family. All four are exploratory pending null/partial-null Type-I calibration.
- split_access.py, ea.py, a3_bridge.py and formal_scenario_generator.py enforce Train-only evolution, Test-restricted ordinary evaluation, no Test payload in public audit return, and atomic one-time final-evaluation ledger.
- formal_preflight.py is metadata-only and fail-closed; it does not read Test payload.
- Remaining: connect real formal runner, decide/freeze the outcome-blind five-composition roster, run R4 power/Type-I 10,000 MC, write R4 preregistration, independent review. No real Test labels/results or formal A-3b.


## 2026-11-10 — D-076 execution complete; independent R4 review is next

Read first: `64_A3B_PREREGISTRATION_CANDIDATE_R4.md`, `77_D076_R4_AND_SBCG_EXECUTION_REPORT.md`, `experiments/pilot_a3b/results/r4_preflight/preflight.json`, and `sbcg_config.json`.

R4 has a real manifest+ledger formal runner, frozen outcome-blind five-composition analysis, 24-cell 10,000-MC power/Type-I evidence, neutral sign-flip metadata, and an executable pre-flight currently returning HOLD. SBCG implements M1/M2/M3, 14 controls/ablations, budget/cache accounting, and JSON-safe validation selection. Local and clean-clone tests are 290/290; CI regression 42813004959 and power 42813004752 succeeded.

No real Train/Validation algorithm diagnostic or Test access occurred. No performance uplift or ablation claim is supported. Safety non-inferiority margins and the hypervolume reference point remain OPEN.

Only next task: independent R4 review. After ACCEPTED + advisor MDE approval + explicit user approval + real pre-flight, freeze the remaining safety/hypervolume rules before any Train-only SBCG comparison. Keep formal A-3b, Test, Pilot B, A800/ARWM, real LLM APIs, and main merges on HOLD.


## 最新状态追加（2026-11-10 D-078）
先读取 `experiments/pilot_a3b/results/d078_train_validation_pilot/matrix_report.md`。D-078 已在合成 A-3b simulator 完成 14 臂×3 seeds=42 runs，CI 42820836080 success，回归 CI 42820836104 success。Train=216、Validation=108，pop=8、G=5、LLM API=0、Test 未访问。多数算法的 selected Validation 指标完全相同（CondRecSucc=1.0、AvoidableHarm=2.4444、ActionCost=4.3929），SBCG 暂无可见性能提升；Reflection HOLD；no-M3 表现较差。Validation 指标有 selection optimism，不可当作无偏泛化结果。D-076 review 是旧 SHA 的复审，若干 SBCG 阻断已由后续 D-078 commits 修正；R4 technical-missing power / pre-run-post-run gate 仍需独立核验。下一任务 D-079：做 per-family/per-scenario diagnostics、确认天花板效应/相同 FSM 收敛原因，构造预注册难度分层合成挑战集；不访问 Test、不启动真实 LLM/A800。


## 2026-11-11 — D-082 handoff maintenance sync

- D-081 corrective code commit: `192f958847fb31d7d704cfa0760201dcd8371e32`; D6 now permits runtime compensation unavailable as R4, and D-078 workflow is `workflow_dispatch` only.
- The previous regression failure remains recorded: run 42827879313 failed after 282 tests due to the old requirement that each Train family contain both contract-level compensatable and uncompensatable tools. D-078 run 42827879133 stopped at preflight; no algorithm rerun occurred.
- Current check of D-081 commit combined status returned an empty status list; no corrective CI success has been verified. Documentation synchronization commits are not evidence of tests.
- Current branch comparison before this prompt refresh: ahead 257 / behind 0; main remains `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`.
- **唯一下一任务：** verify the regression Actions run for D-081. After CI passes, inspect D-079 audit artifacts and the 288-row Train-only challenge manifest; verify R1-R4 labels, UNKNOWN/disagreement, counts, search/diagnostic pairing, IDs and SHA-256; then commit the manifest lock. Do not run a new optimizer before the manifest lock.
- Formal A-3b, Test, Pilot B, A800/ARWM, real LLM API, UndoBench TEST, ThinkingBox and main merge remain HOLD.


## 2026-11-11 — D-082 completed: challenge locked, Train-only diagnostic = NO-GO

Read first: `81_D082_EXECUTION_AND_TRAIN_ONLY_DIAGNOSTIC.md` and the D-079 result artifacts.

Verified D-081 CI: run 42828590264 @192f958, success, 318/318. D-078 independently recomputed: 42 runs, 32/42 Hand-selected, 33/42 Hand in Validation Pareto front, zero robust/analytic disagreements. Successful intended active effects are no longer counted as harm; R4 unavoidable residual enters the minimum-harm bound.

D-079 challenge: 288 Train-only scenarios, 144 Search + 144 Diagnostic, eight families, six strata, three repeats, zero UNKNOWN, unique IDs/seeds. Manifest content SHA=`cafdc52e037c08ca8cd95c0546014bab6dd27e9bd6d28122afb90f28b3cd1efa`; raw-file SHA=`0072550d432d306d4c02912bebaaa4a4756edb33a68c962cf59e9fb198d6c152`; scenario-ID SHA=`4d7b19605155bdbfde61216ecfda6019f09d78a76fa7162fd16c18496114ec99`. Lock and tamper tests pass.

The locked Train-only diagnostic actually ran 14 arms x 3 seeds = 42 runs. SBCG minus Hand: CondRecSucc −0.5521, R4 containment +0.6667, constraint violation −0.1458. SBCG minus matched NSGA-II CondRecSucc −0.0104. No overall uplift; current SBCG is NO-GO. Every arm has R3 CorrectEscalation=0. Initial and final diagnostic artifacts are preserved; independent CSV recomputation found zero mismatches.

Only next task: independent R4 review. For the algorithm, preregister exactly one R3 mechanism revision—prefix rollback/compensation before escalation—with its own ablation and a fresh challenge split. Do not tune repeatedly on the same Diagnostic role. Formal A-3b, Test access, Pilot B, A800/ARWM, real LLM APIs, UndoBench TEST, ThinkingBox, and main merges remain forbidden.
## D-083 continuation instructions — 2026-11-11

You are continuing the thesis project in **yujian777555/kaitibaogao only**. Do not mix other repositories.

The user wants a short paper for Agent × Evolutionary Computation using the research workflow: select a recent open-source conference baseline, faithfully reproduce it, decompose its modules, compare related mechanisms, propose a targeted algorithmic improvement, and prove it with controlled experiments.

### Current paper candidate

Working title: **面向状态化工具调用智能体的契约约束恢复策略演化方法**.

Primary evolutionary baseline: **EvoTool (ACL 2026)**, paper https://aclanthology.org/2026.acl-long.2016/ and official code https://github.com/SYang2000/ACL_2026_EvoTool. It uses Planner/Selector/Caller/Synthesizer, trajectory-grounded blame attribution, feedback-guided targeted mutation, and diversity-aware population selection. First reproduce an official stateful benchmark slice (prefer tau-Bench) exactly before adapting it.

Related work requiring comparison: EvoFSM (FSM evolution), DART (semantic recoverability), Evidence-Guided Recovery (ambiguous outcomes/partial execution), EvoUndo (recoverability-constrained harness self-evolution), ToolMisuseBench, AgentRx, and Failing Tools. Do not claim novelty as the first Agent recovery or first FSM evolution method.

### Immediate repository task

D-081 CI passed. Independent audit of the D-079 v1 artifact found:
- canonical v1 manifest hash matched;
- 288 Train-only rows, 8 families, 6 strata, 144 search + 144 diagnostic, no UNKNOWN, no robust/analytic disagreements;
- **blocking issue:** scenario `cluster_id` contains `family|stratum|role`, while the declared 48-cluster registry uses `family|stratum`. Thus 96 scenario cluster IDs cannot be joined to the 48 registry entries.

D-079 v1 is not locked. Correct the generator to v2 with scenario cluster IDs `family|stratum`, validate 48 clusters × 6 rows × 3 rows per role, and add tests. Then run CI and independently audit the regenerated artifact. Only after that may a new `d079_manifest_lock.json` be committed.

### Research and authorization boundaries

- D-078 does not establish EC uplift; Hand FSM dominates selected Validation candidates, and its R3 correct-escalation is 0/36.
- D-079 is Train-only, non-confirmatory mechanism discovery.
- No formal A-3b, locked Test, external benchmark Test, A800/ARWM, or real LLM API execution is authorized by the current protocol.
- Do not fabricate results or claim a paper-level effect.
- After manifest integrity is restored, prepare a faithful EvoTool reproduction protocol. Wait for separate authorization before any experiment that crosses the current gates.

Read `81_D079_MANIFEST_AUDIT_AND_CLUSTER_FIX.md`, `82_PAPER1_BASELINE_AND_METHOD_CANDIDATE.md`, and the latest handoff before acting.

## D-084 continuation — 2026-11-11

The D-079 v2 Train-only manifest is independently audited. Its canonical SHA is `09df6babbb6e3222ea57a7f354654636ac2437b7011dbe3f1ac738df894a0bca`; it contains 288 unique Train rows, 48 cluster IDs, six rows per cluster (three per role), 144 search + 144 diagnostic, all R1-R4 labels, zero UNKNOWN/disagreement, and no Validation/Test payload or outcome access. The lock is `experiments/pilot_a3b/d079_manifest_lock.json`. A regression test checks regenerated content against the lock.

Paper 1 primary baseline is EvoTool ACL 2026. Important reproduction finding: the paper Appendix A.6 says G=8/B=3, but the released code default derives 90 generations from three epochs × 30 batches. Do not run the default and call it a faithful reproduction. See `83_EVOTOOL_REPRODUCTION_AUDIT.md`; use the paper-faithful G=8 override only after authorization.

Next actions:
1. Verify CI for the D-084 lock commit.
2. Inspect workflow result and confirm the lock regression test passed.
3. Prepare, but do not execute, the EvoTool Qwen3-8B tau-bench reproduction preflight.
4. Ask the user for explicit authorization before launching vLLM/A800, any real LLM API, formal A-3b optimizer, or held-out Test.

Keep all work in `kaitibaogao`; do not merge other repositories. D-078 has no EC uplift; D-079 is Train-only diagnostic, not confirmatory.


## 2026-11-11 — D-082 v2 correction

The D-083/D-084 audit revoked the v1 lock because role-fragmented scenario cluster IDs did not join the 48-cluster registry. Keep the v1 diagnostic only as superseded history. The sole valid manifest is v2 with SHA `09df6babbb6e3222ea57a7f354654636ac2437b7011dbe3f1ac738df894a0bca` and committed lock `experiments/pilot_a3b/d079_manifest_lock.json`. V2 has 288 Train rows, 48 joinable clusters, six rows per cluster and three per role. The 42-run diagnostic was rerun on v2 and independently verified. SBCG remains NO-GO; R3 CorrectEscalation remains zero for every arm.
## D-085 continuation — 2026-11-11

Read `83_EVOTOOL_REPRODUCTION_AUDIT.md` and `84_MODULE_LEVEL_COMPARISON_AND_FSPAE_HYPOTHESIS.md`.

The D-079 v2 Train-only manifest lock is committed and its regression test passed in workflow run 42953293607 (commit `e36cd9e5abe7c60991f1e63bd27fe1de4a71c532`). The manifest SHA is `09df6babbb6e3222ea57a7f354654636ac2437b7011dbe3f1ac738df894a0bca`.

Paper 1:
- Primary baseline: EvoTool ACL 2026.
- Selection comparator: GEPA ICLR 2026 Oral.
- Provisional method hypothesis: FSPAE — per-task-family × fault-stratum Pareto archive with coverage-deficit parent sampling and hard safety feasibility.
- Motivation only: D-078 selected Hand in 32/42 runs; Hand R3 CorrectEscalation was 0.0. This does not prove selection is the only cause and does not establish uplift.
- Important baseline reproduction discrepancy: paper G=8/B=3, released code default 90 generations. Use the explicit G=8 override only after approval.

Next:
1. Prepare the EvoTool Qwen3-8B tau-bench reproduction preflight and compare exact paper/code settings.
2. Ask user for explicit authorization before vLLM/A800 or any real LLM API call.
3. Do not run D-079 optimizer, formal A-3b, Validation/Test, or external benchmark Test without separate authorization.
4. Do not write positive results or claim FSPAE works until matched-budget experiments and a locked shift test pass.

All work remains in `kaitibaogao`; never merge the user's other repositories.

## D-088 Next（2026-11-15）

1. R4 短板修复：实现残余伤害感知停止条件（residual>min_reachable_harm 时禁止 ESCALATE，继续补偿可达路线），加入机制 B；重跑 Fresh 复制。
2. 演化价值验证：反馈条件化变异（失败轨迹引导）+ pop=24×20 代，与 RandomSearch 配对比较（3 seeds 起）。
3. BC 组合冻结与独立 Fresh 验证（开发集均衡最优）。
4. 保持：D-087 Validation 只读；禁止 Test/LLM API/A800；安全约束零容忍。
5. 更新四件套并提交推送后核验 CI。

## D-088-R2 Next（2026-11-15）

1. R3↔R4 预算竞争：多目标 Pareto 前沿保留（不选均衡单点）或预算分割（ESCALATE 固定份额 + 恢复预算按 min_reachable 分配）。
2. 演化价值验证：pop=32×30 代（960 评价）配对 5 seeds，counterfactual 反事实序列作为锚点基因注入初始种群。
3. strict_residual_stop 参数化：剩余预算 < 阈值时优先保 ESCALATE。
4. 两份 R3 提升冻结 genome 已存档；待 Validation 授权后正式复制。
5. 禁止 Test/LLM API/A800；安全约束零容忍；四件套同步。

## D-089 Next（2026-11-15）

1. g03 互依对修复：R3 类任务（min=0）禁止 stop_residual>0 的停止；互依环 alternate 破除优先级强化。目标 R3 0.833→0.95+。
2. harm 收窄：冻结候选 harm 0.188→0.11 以下，研究恢复顺序与残余分布。
3. 演化价值第四次：状态条件化规则编码（非连续参数）或 2880 评价三倍预算配对；连续参数空间三次随机=演化，应正式记录该结论边界。
4. B4 成本估算校准。
5. 三份冻结 genome 待 Validation 授权。禁止 Test/LLM API/A800；安全约束零容忍；四件套同步。

## D-090 当前状态 — 2026-11-16

阅读 `99_D090_PAIR_RACE_RULE_SEARCH.md` 与 `experiments/d090_recovery/results/d090_mechanism_ablation.json`。D-090 Train-only 小规模对照尚未显示演化超过同编码随机搜索。P1 可减少 g03 失败但 Harm 代价过高，P2 违反 pending 硬约束。下一步研究 pair 与延迟确认的联合预算分配和 Harm-aware 可行性修复，保持 D-089 B3 作为基础。不要访问正式 Validation/Test、启动 A800/ARWM 或真实 LLM/API。
