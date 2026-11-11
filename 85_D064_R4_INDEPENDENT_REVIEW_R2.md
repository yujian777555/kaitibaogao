# 85 — D-064 R4 独立复审报告（R2）

**日期：** 2026-11-11
**角色：** 独立只读 Reviewer；不是 Executor
**工作分支：** `pilot-a-stateful-recovery`
**main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`（未修改）
**审查方式：** 独立会话逐项读取代码、预注册、合成测试和原始 JSON，并重新计算关键统计结果
**最终结论：** **ACCEPTED（仅代码与协议复审通过）**
**正式 A-3b：** **仍 HOLD**；导师 MDE、用户批准和真实 pre-flight 均未完成

## 1. 审查范围与基线

核查了：

- `64_A3B_PREREGISTRATION_CANDIDATE_R4.md`；
- `77_D076_R4_AND_SBCG_EXECUTION_REPORT.md`、`78_D076_INDEPENDENT_REVIEW.md`；
- `formal_preflight.py`、`run_r4_preflight.py`、`formal_runner.py`、`formal_analysis.py`；
- `split_access.py`、`power_hierarchical.py`、`power_r4_design.py`；
- `test_64r4_*.py` 和 `results/r4_power_20261114/`；
- 当前 `results/r4_preflight/preflight.json`。

最终本地完整测试为 **pilot_a3b 313/313 + pilot_a_recovery 28/28 = 341/341**。CI 绿色只作为辅助证据，不代替逐项复审。

## 2. 首轮阻断发现与修复

### R4-001：pre-run/post-run 循环依赖

**发现：** 早期 pre-flight 同时要求 UNUSED Test ledger 和已存在的完整 outcome rows，形成不可达 GO；R4 文本也混写两类字段。

**修复证据：**

- `formal_preflight.py:18-33` 分离 `PRE_RUN_REQUIRED_FIELDS` 与 `POST_RUN_REQUIRED_FIELDS`；
- `formal_preflight.py:59-116` 的 pre-run 不再要求 outcome rows；
- `formal_preflight.py:119-162` 单独执行 post-run 完整性检查；
- R4 §9 已改为 9.1 pre-run authorization 与 9.2 post-run analysis integrity。

**当前实际输出：** `results/r4_preflight/preflight.json` 的 phase=`PRE_RUN_AUTHORIZATION`，status=`HOLD`，仅有独立审计、导师 MDE、用户批准三项阻断，不再含旧 post-run 字段。说明循环依赖已消除，但没有伪造 GO。

**结论：CLOSED。**

### R4-002：technical-missing 与 Type-I 功效证据不完整

**发现：** 早期 24 格没有 composition/run technical-missing 情景，F=40/ICC=.20 的 0.0547 单 cell 也未充分解释。

**修复证据：**

- `power_r4_design.py:92-157` 实现 MCAR composition-cluster technical missing；
- `power_r4_design.py:160-206` 实现 F=40/ICC=.20 的 5×10,000 独立-seed Type-I replication；
- 新增连续前缀非随机不利缺失 `simulate_adversarial_missing()`，避免只用 MCAR 代替所有缺失机制；
- missing cells 已含 conditional/joint rejections、MCSE、Wilson CI、eligible replicate 数；
- 原始 JSON 含 24 主格、16 MCAR 格、16 adverse 格和 5 个 replication，均可逐字段重算。

当前关键值：

- F=34/ICC=.20 MDE power = **0.8427 [0.8354, 0.8497]**；
- 多 seed pooled Type-I = **0.04754 [0.045709, 0.049440]**；
- 连续前缀 F=34 在 1% 缺失下全部 replicate 均失去确认性资格；
- F=40 的连续前缀 MDE 联合拒绝率分别为 0.8954/0.8947/0.8828（1%/2%/5%）。

**结论：CLOSED。** 功效是模拟设计证据，不是算法增益证明。

### R4-003：小 |t| 的 Student-t 尾概率数值错误

**发现：** `_betainc()` 在 x→1 时不稳定。t=0.001、df=39 时旧实现双侧 p≈0.0342092，而 SciPy 为 0.9992072，会错误拒绝近零效应。

**修复证据：**

- `power_hierarchical.py:372-402` 使用 `I_x(a,b)=1−I_(1−x)(b,a)` 的对称计算；
- `test_64r4_student_t.py:43-47` 加入 t=0.001/0.01、df=39/1 的 SciPy 已知答案；
- 独立随机向量复核最大 p 误差约 7.7e-12；
- 全部功效和 Type-I 结果已重新生成，pre-fix JSON/Markdown 另存为 `power_r4_design.pre_d085.json/.md`。

**结论：CLOSED。**

### R4-003b：自填 GO 可绕过 one-time gate

**发现：** 生产 wrapper 只检查 preflight 字典的 phase/status；approval record、ledger 和 access log 未绑定实际产物。

**修复证据：**

- `split_access.py:25-43` 的 `_validate_preflight_binding()` 要求实际 preflight artifact 的 canonical SHA、git HEAD、implementation/code hash、UNUSED ledger；
- 低层 `consume_final_evaluation_once()` 也调用同一绑定检查，不能只用 `preflight_status="GO"`；
- `test_64r4_split_guard.py` 的未绑定字典拒绝测试通过。

**结论：CLOSED。**

### R4-004：直接 Test 分析绕过 receipt

**发现：** `analyze_primary_endpoint()` 最初只凭 caller provenance 的格式和 `status=COMPLETED` 即可输出 Student-t，缺少真实 receipt、ledger 和 access log 校验。

**修复证据：**

- `split_access.py:172-201` 新增统一 `validate_execution_receipt()`，验证 consumed ledger、outcome hash 和一次性 access log；
- `formal_runner.py` 和 `formal_analysis.py` 都调用该校验；
- `analyze_primary_endpoint()` 在没有 receipt 时拒绝，synthetic 必须显式 `allow_synthetic=True`；
- `test_hash_only_receipt_cannot_authorize_direct_test_analysis` 已证明 hash-only 假 receipt 被拒绝。

**结论：CLOSED。**

### R4-005：receipt-bound ledger 与分析行可不一致

**发现：** 即使 receipt 真实，调用者仍可替换 `run_rows` 改变效应，而原函数没有检查 execution ledger 与分析行的一致性。

**修复证据：**

- `split_access.py:102-130` 共享 `flatten_run_ledger()`，避免 formal_runner/formal_analysis 循环导入；
- `formal_analysis.py:148-156` 强制 `run_rows == flatten_run_ledger(execution_ledger)`；
- secondary 于 `formal_analysis.py:411-429` 转发同一 ledger；
- 新增 `test_execution_ledger_and_analysis_rows_must_match`：真实 synthetic receipt 下篡改分析行会抛出 `ValueError("analysis rows do not match the execution ledger")`。

**结论：CLOSED。**

### R4-006：pre-flight 配置和 CLI 不是实际核验

**发现：** budget、seed、stopping rule 和 access log 曾硬编码为 True/0，CLI 未暴露 ledger/access-log/config 路径，统计 seed 只检查整数类型。

**修复证据：**

- 新增 `experiments/pilot_a3b/r4_execution_config.json`；
- `run_r4_preflight.py:54-100` 从实际配置读取 budget/seeds/stopping/split 字段，并检查 public manifest 是否暴露 Test payload；
- access log 按实际文件计数；
- CLI 增加 `--config-path`、`--ledger-path`、`--access-log-path` 并传递；
- 三个统计 seed 精确匹配 20261114/20261112/20261113；错误 seed 配置会触发 HOLD。

**结论：CLOSED。**

## 3. 其他已核验一致项

- 五个 outcome-blind primary compositions 在生成器中冻结，并在分析中逐族校验；
- family 等权与五 composition 完整规则一致，df=`F_observed−1`；
- H2–H5 全部 exploratory，只有四项均 eligible 才执行 Holm；
- pre-run GO → 原子 consume → Test loader → outcome ledger → bound receipt → formal analysis → post-run integrity 已形成闭合生产链；
- `public_manifest_view()` 不向开发调用者暴露 Test payload，普通 evolution/evaluator split guard 有效；
- pre-fix 与 post-fix 结果均保留，没有覆盖历史实验数据。

## 4. 最终审计结论

**ACCEPTED。** 首轮发现的统计、生命周期、功效、receipt 授权和可复现性阻断均已由实际代码与测试关闭。

该结论仅表示 R4 的代码与预注册在当前复审范围内一致，**不表示正式实验已经获批，也不表示算法有效**。正式 A-3b 仍需：

1. 导师认可 MDE=0.10；
2. 用户明确批准最终 R4 文本；
3. 基于最终代码和 R4 文本重新生成并通过真实 pre-flight；
4. 执行后再通过 post-run integrity。

当前保存的 HOLD 不得当作 GO 使用，不得启动正式 A-3b、Test final evaluation、Pilot B、A800/ARWM 或真实 LLM API。
