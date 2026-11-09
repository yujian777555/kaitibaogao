# 62 — D-063：正式 A-3b 功效核算与预注册冻结计划

**日期：** 2026-11-09  
**状态：** D-063 ENGINEERING DELIVERABLES COMPLETE；64 号预注册经 D-064 独立审查 REQUEST CHANGES；正式 A-3b 仍 HOLD  
**本轮维护起始 HEAD：** `e6fee3bde05e8dea3fcc54f2ea1d97bc54837867`（历史基线；接管时必须实时查询）  
**Main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`（保持不动）  
**前序：** D-062（59 复核、60 设计、61 diagnostic3）  
**下一会话入口：** `NEXT_SESSION_PROMPT.md` 的 D-063 节

---

## 0. D-062 完成判定与证据边界

D-062 的 Stage 0–4 已完成：独立失败轨迹审计、评价器修复、WAIT-SLA、B-new、Safety Gate 消融、diagnostic3、51 项 pilot_a3b 测试。用户报告总测试为 79/79（pilot_a_recovery 28 + pilot_a3b 51）。D-062 的结论和负结果均保留，不覆盖 diagnostic2/diagnostic3 原始数据。

**重要：D-062 完成 ≠ 正式 A-3b 已通过。** diagnostic3 明确标记 DIAGNOSTIC / NOT_CONFIRMATORY。正式 A-3b 仍 HOLD，直到功效方案、预注册和用户批准完成。

### 0.1 D-062 最可信的机制级结果

| 对比 | diagnostic3 报告值 | 可支持的结论 |
|---|---:|---|
| AB vs A | +0.119，CI [0.066, 0.183]，p=0.0002 | B-new 在 A 基础上有诊断性增益 |
| AwaitSLA vs A | +0.089，CI [0.033, 0.154]，p=0.0047 | WAIT-SLA 有诊断性增益 |
| AwaitSLA vs AwaitFixed | +0.054，CI [0.023, 0.091]，p=0.0032 | SLA-aware 优于固定等待 |
| AB vs AwaitSLA | +0.031，CI [0.012, 0.051]，p=0.0072 | 全数据上搜索增量为正；但验证集不显著 |
| AB vs A（validation） | +0.142，CI [0.056, 0.247]，p=0.0082 | B-new 的验证集增益 |
| AB vs NSGA-II（all） | +0.1049，CI [0.000, 0.2058]，p=0.062 | **未达到 0.05 显著性** |
| AB vs NSGA-II（validation） | +0.1173，CI [-0.0679, 0.2778]，p=0.2277 | **验证集未显著** |
| AB vs AwaitSLA（validation） | +0.031，CI [0.000, 0.068]，p=0.244 | **Q10 搜索增量的独立泛化尚未建立** |
| AB vs Hand | -0.282，CI [-0.387, -0.181]，p=0.0002 | 显著落后于强手工策略 |
| AB vs ABG | +0.193，p=0.0002 | Safety Gate 在当前设定下有害 |
| B vs NSGA-II | -0.074，p=0.0007 | B 单独无效/有害，必须保留负结果 |

**主张限制：** 当前结果支持 WAIT-SLA 与 B-new 的机制级诊断证据；尚不能声称 AB 在独立测试集显著优于 NSGA-II，也不能声称演化增益（Q10）已在验证集泛化，更不能声称超越专家。

### 0.2 D-061 旧叙事更正

59 号审计已证明 D-061 的 0.36 vs 0.006 不是重复副作用率：A 的 duplicate rate 为 0；1,139 个违规 episode 中 1,132 个（99.4%）是 saga evaluator 将正确 COMPENSATE/ROLLBACK 安全放弃误计为 downstream violation。真实重复只有 7 例，轨迹集中于 UNKNOWN_OUTCOME 下信任 SLA 内 NOT_COMMITTED 查询后执行非幂等 RETRY。

此更正必须在正式论文和所有摘要中保持一致。

---

## 1. Stage 0 — 统计流水线可复现性（阻断功效冻结）

当前远端检查发现：

1. `experiments/pilot_a3b/stats.py` 的 `main()` 仍硬编码读取 `diagnostic2_results.json`，不是 diagnostic3；
2. `run_diagnostic3.py` 负责生成原始结果，但自身不生成统计摘要；
3. 已提交的 `diagnostic3_stats.json` 含 AB vs NSGA-II、AB vs A、AB vs Hand 等统计，但不含 61 号报告所列的 AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA 的完整 cluster SD / 统计输出；
4. 因此 61 号报告的部分关键比较目前无法从仓库中的单一可执行分析入口完整再生。

### 必须交付

新增 `experiments/pilot_a3b/analyse_diagnostic3.py`（或将 stats.py 改成显式输入输出参数的通用分析器），要求：

- 输入明确指定 `diagnostic3_results.json`，绝不能悄悄读取 diagnostic2；
- 输出 aggregate、train-only、validation-only；
- 所有预先列出的对比均输出：配对差值、cluster SD、95% cluster bootstrap CI、paired sign-flip p、Holm-adjusted p（适用时）、效应量；
- 至少包括 AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II；
- 验证集必须单独统计，不能把 train 与 validation 混为正式确认性结果；
- 以 `(task, composition)` 为 cluster，seed 为嵌套重复；解释 scenario replicate 如何进入 cluster 均值；
- 固定随机数种子、bootstrap 次数、置换次数、CI 算法、缺失配对处理和多重比较家族；
- 对原始 JSON 做 manifest/hash 校验，输出分析器版本、输入 SHA、配置和运行命令；
- 新增测试，验证 synthetic fixture 的差值、cluster 数、缺失配对、Holm 和 seed nesting；
- 独立再生 `diagnostic3_stats.json`，对齐 61 号报告；如有差异，修正报告，不得为对齐而硬编码结果。

**Stage 0 未通过，不冻结正式功效分析。**

---

## 2. Stage 1 — 确认性 estimand 与假设冻结

### 2.1 唯一主要假设

- 候选方法：A+B-new（AB）。
- 主要基线：标准 NSGA-II（必须明确 canonical implementation/version 和配置）。
- 主要数据：全新 held-out test clusters；不得使用当前 diagnostic3 train 或 validation 作为正式 test。
- 主要终点：预注册的 balanced class-success（R1–R4 的类别权重必须在看正式 test 结果前冻结）；同时报告每类结果。
- 主要 estimand：每个 task × fault-composition cluster 内 AB 与 NSGA-II 的配对差，再对 cluster 等权汇总。
- 显著性：双侧 alpha=0.05；报告 95% cluster bootstrap CI 和 paired sign-flip permutation p。
- 成功判据：主要差值 CI 不跨 0 且 p<0.05，方向为 AB 优于 NSGA-II；安全硬约束同时通过。

如果团队希望采用单侧检验，必须在预注册前给出理论理由并锁定；默认不改成单侧以追求显著。

### 2.2 次要假设（Holm 校正）

1. AB vs A：检验 B-new 的增量；
2. AwaitSLA vs A：检验合同语义的增量；
3. AwaitSLA vs AwaitFixed：检验 SLA 推理是否优于固定等待；
4. AB vs AwaitSLA：检验演化搜索在 WAIT-SLA 上的额外贡献（Q10）；
5. AB vs Hand：作为强手工参考，主要报告差值和 CI，不预设“接近专家”或非劣效结论；
6. B vs NSGA-II、ABG vs AB：保留为探索性/负结果复核，不升级为主要假设。

### 2.3 安全接受条件

- duplicate side-effect 和 SLA violation 分开统计；
- 对预注册的非幂等、歧义观测测试，出现任何确认的重复副作用均作为关键安全失败；
- WAIT-SLA 的安全保证严格限定于工具合同假设成立（可见性上界、查询一致性、幂等/补偿语义准确）时；
- 合同缺失、超出保证、结果仍 UNKNOWN 时必须 ESCALATE/STOP_SAFE；
- 零观察违规不等于数学上证明所有外部工具绝对安全；报告事件数、分母和置信上界；
- 不允许把安全指标折算成可被成功率抵消的普通目标。

---

## 3. Stage 2 — 初步功效核算（规划近似，不是最终冻结值）

### 3.1 采用的先验量

从 `diagnostic3_stats.json`：

- AB vs NSGA-II（all）：`delta=0.1049`，`cluster_sd=0.4040`，54 clusters，p=0.062；
- AB vs NSGA-II（validation）：`delta=0.1173`，`cluster_sd=0.3914`，18 clusters，p=0.2277；
- AB vs A（all）：`delta=0.1193`，`cluster_sd=0.2178`，54 clusters；
- AB vs Hand（all）：`delta=-0.2819`，`cluster_sd=0.3925`，54 clusters。

**主要功效必须参考 validation-only 的 AB vs NSGA-II，而不是混入 train 的 54-cluster overall 对比。** 当前 18 个 validation clusters 太少，且该估计的 SD 本身不稳定。

### 3.2 配对 cluster t 近似

用双侧 alpha=0.05、paired cluster mean difference、non-central t 近似计算；这只是初步规划。最终样本量必须用 Stage 0 再生的 empirical cluster differences 做 Monte Carlo sign-flip/bootstrap power simulation。

| 目标真实差值 | 规划 SD | 80% power 所需可分析 clusters | 90% power 所需可分析 clusters |
|---|---:|---:|---:|
| 0.1173（当前 validation 点估计） | 0.3914 | 90 | 119 |
| **0.10（建议的最小有意义差异 MDE）** | **0.3914** | **123** | **163** |
| 0.08（更保守敏感性） | 0.3914 | 190 | 254 |

当前 validation 只有 18 clusters；按 MDE=0.10，80% power 设计约需 123 个可分析独立 clusters，尚缺 105 个。若预留 15% 不可用/失效 cluster，目标招募约 145 个 clusters（90% power 约 192 个）。

**cluster 是 task × fault-composition，不是 episode，也不是算法 seed。** 单纯增加同一批 task/composition 的 rollout 或 seeds，不能代替增加独立 clusters。若仍使用 9 个 fault compositions，145 个 clusters 约对应至少 17 个 task families × 9 compositions（153 clusters）；必须先确认 benchmark 是否能提供足够、语义有效且互不泄漏的任务族。不能为了凑样本量把同一任务拆成伪独立 cluster。

### 3.3 当前设计功效提示

- validation-only 18 clusters 在点估计 delta=0.1173、SD=0.3914 下，配对 t 近似 power 约 22%；
- all-data 54 clusters 在 delta=0.1049、SD=0.404 下，配对 t 近似 power 约 47%；
- 因此 diagnostic3 primary AB vs NSGA-II 未显著，不应被描述为“已证实优于 NSGA-II”；
- AB vs A 的显著结果支持机制增量，但不能替代 AB vs NSGA-II 的主要比较；
- Q10 的 AB vs AwaitSLA 全数据比较虽报告 p=0.0072，但 validation p=0.244，不能说搜索增量已泛化。

这些 power 数值是基于当前点估计/SD 的近似，不是最终样本量承诺。Stage 0 的复算和 empirical simulation 可以修订它们，但不能查看正式 test 效应后再改样本量。

---

## 4. Stage 3 — 任务族、数据划分和预算设计

### 4.1 数据隔离

- Search/Train：只供演化搜索；
- Validation：只用于选择冻结配置；一旦用于调参，不再是 confirmatory test；
- Held-out Test：新任务族/新故障组合/新随机种子，锁定后只运行一次正式评估；
- 现有 diagnostic3 validation 已被本轮报告使用，不可再充当正式 A-3b test。

### 4.2 cluster 扩展

- 先盘点现有 6 个任务族及 9 种故障组合的语义覆盖和依赖；
- 设计新增任务族时先做合同一致性、可达性、泄漏和标签验证；
- 目标以 123 个可分析 held-out clusters（MDE 0.10 / 80% power）为基准，另加失效预留；
- 若任务族规模不可行，必须如实降低可检出效应/功效并向用户说明，不得以重复 seeds 冒充 cluster 扩展。

### 4.3 方法臂和预算

建议正式主实验臂：
- NSGA-II（primary baseline）；
- A；
- A+Fixed-WAIT；
- A+WAIT-SLA；
- B-new；
- A+B-new（primary candidate）；
- Hand（强手工参考，不作超越专家主张）。

ABG 可作为已知负结果，不必占用主要确认性预算；如保留，需标记为探索性。每臂冻结相同初始化池、搜索预算、评估调用/episode 计数规则、停止条件和种子策略。验证/测试评估预算独立于搜索预算；Safety battery、修复、拒绝候选的成本必须计入相应算法成本。所有实际 episodes、cache hits、失败调用和时间均留账。

---

## 5. Stage 4 — 预注册草案必填项

生成独立的 preregistration draft，至少包含：

1. 研究问题、动机和有限主张（不得声称超越 Hand）；
2. 主要假设、estimand、主要终点和类别权重；
3. 主要对比 AB vs NSGA-II；
4. 次要对比与 Holm family；
5. 安全不变量和工具合同假设；
6. 任务族、fault compositions、cluster 定义与数据隔离；
7. 预先固定的样本量和功效计算脚本；
8. 所有算法臂、基线版本、超参数、初始化和预算；
9. 随机种子与随机化/配对规则；
10. 缺失值、失败运行、异常值和排除规则；
11. 统计方法、bootstrap/permutation 次数、CI、效应量；
12. 多重比较处理；
13. 结果报告模板和负结果处理；
14. 代码 commit、环境锁、manifest/hash、执行命令；
15. 偏离预注册的处理和透明披露。

预注册文件先标记 **DRAFT — NOT FROZEN**。由用户审阅并明确批准后，才可冻结。正式 A-3b 必须另行授权。

---

## 6. Stage 5 — CI 和交付完整性

D-062 执行报告称 79/79 测试通过，但当前已有 `.github/workflows/pilot-a-recovery.yml` 的 path filter 只覆盖 `experiments/pilot_a_recovery/**`，不会因 `experiments/pilot_a3b/**` 变化而触发。

独立 workflow 已新增并通过：
- Workflow：`.github/workflows/research-simulator-regression.yml`；
- Actions run：`42398278551`（commit `c0078d5c3db17380e81faca5752ac6a64f555a6d`），结论 `success`；两个测试步骤 `pilot_a_recovery` 和 `pilot_a3b` 均 success；
- 执行报告称两套测试合计 79/79。当前 HEAD 后续提交仅修改文档，没有修改实验代码。

新增 workflow 的设计为：
- 触发分支 `pilot-a-stateful-recovery`；
- path filter 覆盖 `experiments/pilot_a_recovery/**`、`experiments/pilot_a3b/**` 和 workflow 本身；
- Python 3.11；
- 分别运行两个 unittest discover；
- 不在 CI 中运行昂贵的诊断/正式实验；
- 记录实际 GitHub Actions run URL 和结果。

不得把“报告中本地 79/79”写成“GitHub CI 79/79”，除非 workflow 实际成功。

---

## 7. Gate 与授权

**GO：**
- 统计流水线独立复现和修复；
- validation/test-only power simulation；
- 任务族扩展可行性审计；
- 预注册草案；
- CI workflow 和单元测试；
- 仓库与接管提示词维护。

**HOLD：**
- 正式 A-3b 确认性实验；
- 锁定 held-out test 的任何调参或查看结果；
- Pilot B；
- A800/ARWM；
- 大规模真实 LLM API；
- UndoBench TEST；
- ThinkingBox。

**唯一下一步：** 先修复 diagnostic3 统计分析可复现性，再做 empirical cluster power simulation 和预注册草案；将冻结版交用户批准。未批准前不得启动正式 A-3b。


---

## 8. D-063 执行级验收清单（2026-11-09 更新）

本节细化执行要求，不表示任何 Stage 已经完成。当前仓库实际状态仍为：D-063 文档计划已存在；统计复现、经验功效仿真、任务族扩展审计和预注册草案均**尚未交付**。

### 8.1 Stage 0 — diagnostic3 统计复现验收

分析器建议采用显式 CLI 输入输出，不允许默认静默回退到 diagnostic2。至少支持：

- --input experiments/pilot_a3b/diagnostic3_results.json
- --output-dir <explicit path>
- --seed <fixed integer>
- --bootstrap-reps <N>
- --permutation-reps <N>

最终参数名可以调整，但必须在帮助信息、报告和运行命令中一致。

必须输出 all/train/validation 三个 split，并完成以下数据完整性检查：

1. episode ID 唯一性；重复行必须 fail-closed，不能自动去重掩盖问题；
2. 每个主要对比的实验臂配对完整性；
3. task × fault-composition cluster 成员一致性；
4. seed 嵌套结构完整性，禁止把 seed 当作独立 cluster；
5. train/validation/test split 隔离；
6. 评价分母、R1/R2 条件恢复和 R3/R4 正确升级的标签语义；
7. 缺失 episode、异常退出、预算截断和无效样本的明确处置；
8. 输入 JSON、manifest、分析配置和代码版本哈希；
9. 同一输入和配置重复执行得到确定性统计输出（允许文档时间戳字段除外）。

至少覆盖以下对比：AB vs NSGA-II、AB vs A、AwaitSLA vs A、AwaitSLA vs AwaitFixed、AB vs AwaitSLA、AB vs Hand、B vs NSGA-II。对比需明确方向，避免报告中正负号歧义。

统计方法应以独立 task × fault-composition cluster 为推断单位；seed 是 cluster 内嵌重复。bootstrap 和 sign-flip 的重采样/翻转单位均为 cluster。固定并记录随机种子、重复次数、CI 算法、缺失配对处理和多重比较 family。主要对比与次要对比不得混在一个 Holm family 中，具体 family 在预注册前固定。

### 8.2 主要终点定义必须先澄清

现有草案称主要终点为 balanced class-success，但 R1/R2 的“恢复成功”与 R3/R4 的“正确升级/安全遏制”不是同一语义。Stage 0/预注册草案必须给出逐类公式、分母、类别权重和 cluster 聚合顺序。

不得把 R3/R4 结构性不可恢复样本简单计为恢复失败，也不得把所有升级一概计为成功。应区分：
- R1/R2：条件恢复结果；
- R3/R4：正确升级、无不允许副作用、无不必要升级；
- UNKNOWN：信息不足，按预先定义的规则处理，不得事后重分类。

如果无法构造一个语义上合理且可解释的单一主要终点，应在预注册前提出替代 estimand 并说明理由；不能看过正式 test 结果后改终点。

### 8.3 Stage 1 — 经验功效仿真验收

- 先用 Stage 0 独立复算出的 cluster-level paired differences。
- 主要样本量只围绕未来 held-out test 的 AB vs NSGA-II 主要比较设计。
- 当前 diagnostic3 validation 仅作历史开发/方差规划数据，不得重新命名为正式 test。
- 至少报告 MDE=0.08/0.10/0.1173、双侧 alpha=.05、80%/90% power。
- 用 cluster-level empirical resampling / sign-flip 或与设计相匹配的 Monte Carlo 方法，报告模拟次数、Monte Carlo 标准误和收敛/稳定性检查。
- 做 15% cluster 失效预留的敏感性分析。
- 说明当前 validation 仅 18 clusters 导致方差估计不稳定；给出不同 SD 假设下的样本量范围。
- 不允许用增加同一 cluster 的 episode 或 seed 充当新增独立样本。

### 8.4 Stage 2 — 任务族扩展审计与计数对账

仓库不同历史段落出现“总任务族 6 个”和“validation 由 2 个任务族 × 9 种 composition = 18 clusters”两种描述。两者可能分别表示全体任务族与 validation 子集，但接管者必须从原始 task manifest、split manifest 和 scenario IDs 逐一核实，不得假定二者天然一致。

任务族审计至少输出：
- task family ID、来源/生成规则、语义目标、工具依赖；
- 9 种 fault composition 的定义与每个 task family 的适用性；
- cluster ID 的确定性生成规则；
- 同模板、同状态图、同工具序列、同故障轨迹的近重复检查；
- train/validation/test 泄漏矩阵；
- 可用独立 cluster 数与不可用原因；
- 任务族扩展的生成成本和人工审查要求。

目标数量以经验功效仿真结果为准；145 仅是 MDE=.10、80% power、15% 预留下的初步 t 近似规划值，不是已批准的最终目标。若无法构造足量独立 cluster，应报告现实可达到的功效，不得伪造独立性。

### 8.5 Stage 3 — 预注册草案与授权边界

预注册草案至少明确：
- 唯一主要对比：AB vs canonical NSGA-II；
- 主要 estimand、主要终点及其逐类公式；
- 双侧 alpha=.05、目标 power 和最终 cluster 数；
- 次要比较及 Holm family；
- Hand 作为参考，不声称超越专家；
- 算法/代码/依赖版本、初始化、演化参数和相同预算口径；
- 随机化、配对、种子、cluster、排除和缺失值规则；
- 硬安全门、合同假设和事件级报告方式；
- 锁箱 manifest、哈希、执行命令和偏离预注册的披露方式。

文件状态必须保持 DRAFT — NOT FROZEN，直到用户明确批准。用户批准预注册也不自动等于批准正式 A-3b 执行；正式确认性实验需另行明确授权。

### 8.6 本轮可执行与禁止事项

**可执行：** 统计分析器、synthetic tests、历史 diagnostic3 复算、经验功效仿真、任务族/泄漏审计、预注册草案、CI 和文档维护。

**禁止：** 正式 A-3b；查看或调参正式 held-out test；Pilot B；A800/ARWM；真实 LLM API；UndoBench TEST；ThinkingBox。

### 8.7 完成 D-063 的最低交付标准

只有同时满足以下条件，才可将 D-063 标记为“草案完成、待用户批准”：

- Stage 0 分析器能从原始 diagnostic3 数据独立再生统计；
- 与 61 号报告逐项对账，差异均已解释和记录；
- synthetic tests 和仓库回归测试通过；
- empirical power simulation 可重复，报告 Monte Carlo 不确定性；
- 任务族扩展审计基于真实 manifest，独立 cluster 数有证据；
- 预注册草案完整，主要终点定义无语义歧义；
- 全部交付和 HOLD 边界已写入接管提示词；
- GitHub Actions 真实运行成功，或如实标记未触发/失败。

**当前唯一下一步仍是 Stage 0：审查原始 diagnostic3 数据与 stats.py，建立可复现的 diagnostic3 独立分析入口。**

---

## D-063 执行完成记录（2026-11-08）

- **Stage 0 ✅**：`analyse_diagnostic3.py` + `test_analyse_diagnostic3.py`（17/17）；7 对比 Δ 与 61 号逐位一致，p 值置换 MC 微差已如实记录；输出 `diagnostic3_recomputed.{json,csv,report.md}`。
- **Stage 1 ✅**：`power_simulation.py` / `power_simulation.json`——主对比 MDE 0.08/0.10/0.1173 @80% 需 254/145/110 clusters（含 15% 失效 299/171/130）；ICC≈−0.09；18-cluster 敏感性三源并报。本计划中的 t 近似表对应 validation sd，主对比 sd 下需求上浮，已在 63/64 号采用 MC 值。
- **Stage 2 ✅**：`63_D063_TASK_FAMILY_EXPANSION_AUDIT.md`——576 候选/18 profile，多样性面板 0.83/3 重叠；train/val/test=8/4/17 族=72/36/153 clusters；功效缺口替代序（MDE 0.1173 或接受 75–80%；禁止重复冒充）。
- **Stage 3 ✅**：`64_A3B_PREREGISTRATION_CANDIDATE.md`——正式预注册草案，冻结主要/次要比较、指标公式、硬安全门、协议参数、排除/停止/存档规则与解释边界。
- **状态**：GO=用户审阅 64；HOLD=正式 A-3b（批准 + 64 §5 预检清单后解锁）及其余全项。


---

## 9. D-064 独立审查更正（2026-11-09）

D-063 工程交付（统计复算代码、功效脚本、任务族候选枚举、预注册草案和 CI）已完成；但独立审查发现原 Stage 1 功效输入与 64 号主要终点不一致。完整审查见 `65_D064_PREREGISTRATION_INDEPENDENT_AUDIT.md`。

### 9.1 主要 estimand mismatch

64 §3 的 CondRecSucc 只使用 R1+R2；当前 `power_simulation.py` 未按标签过滤，混合 R1/R2/R3/R4 的 `class_success`。因此 54 clusters / SD=.404 / Δ=.1049 不是 CondRecSucc 的功效参数。

审查用快速聚合（非正式产物）显示：diagnostic3 54 clusters 中只有 42 个包含 R1/R2；R1/R2-only AB−NSGA-II Δ≈+.3175、SD≈.3189。必须由正式分析入口重算，不得直接把此审查值作为预注册结果。

### 9.2 功效模拟性质更正

当前脚本实际为 `N(MDE, empirical SD)` 参数化正态 Monte Carlo；经验重采样分支未运行，signflip 分支使用正态近似，未输出 MCSE。此前“empirical cluster power simulation”的表述不准确。应先完成 CondRecSucc primary 对比，再进行经验/层级 Monte Carlo、null FPR 校准和 ICC 敏感性。

### 9.3 task-family 独立性与生成有效性

ICC 只基于 6 个 task families（validation 2 个），负估计不能证明 153 个 task×composition clusters 独立。63 号任务族脚本仅用三步排列与合同属性筛选，未验证任务语义前置/后置条件；多样性目标只最小化工具重叠，未优化 profile diversity。正式 8/4/17 scenario generator 尚未接入当前固定 6 任务族运行路径。

### 9.4 样本量决策需重做

旧参数化结果 MDE=.10 / 80% 需要 145 个有效 clusters，15% 失效预留为 171；当前 test 153 经 15% 失效约 130。MDE=.1173 来自观察效应点估计，不能未经实质意义论证自动成为 MDE。以上数字也不是 CondRecSucc 的最终功效结论。

### 9.5 当前状态与下一步

- D-063 工程交付：ACCEPTED（代码/产物/CI 层面）。
- 64 号预注册：REQUEST CHANGES。
- 正式 A-3b：HOLD。
- 唯一下一步：D-064-A，在 `analyse_diagnostic3.py` 新增 R1/R2-only CondRecSucc paired cluster contrast，输出有效 cluster 数、每 cluster 分母、Δ、cluster SD、95% CI 和 sign-flip p；R3/R4 独立统计。之后重做功效和 64 修订。
