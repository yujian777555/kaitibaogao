# D-094 R4 独立算法、统计与预算审查

日期：2026-11-23。结论：**`REQUEST_CHANGES`**。当前状态=`R4_REQUEST_CHANGES`；真实 R4=`NOT RUN`，真实 API=0，真实实验授权=`NOT_GRANTED`，`APPROVED_FOR_EXPERIMENT=NO`。

本报告依据固定提交的实际源码、冻结文档和已有产物重新审查，不把实现者自检或测试数量当作算法有效性证明。本轮未修改生产代码、冻结协议、历史结果或已有 R4 产物，未读取 Validation/Test，未访问真实 API 密钥，未发起真实网络推理。

## 1. 审查身份与版本

| 项目 | 实测值 |
|---|---|
| 仓库／分支 | `yujian777555/kaitibaogao` / `d094-llm-agent-integration` |
| 固定审查提交 | `a6e27d00cdc466ac5f2fe9150effc88d84ba6698` |
| 实际远端提交 | `a6e27d00cdc466ac5f2fe9150effc88d84ba6698`，一致 |
| main | `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，一致且未修改 |
| 固定提交 CI | run `44918012853`=completed/success；job `136887686911`=success |
| 本轮本地复测 | D-094 `Ran 135 tests`，`OK` |
| 工作区保护项 | `experiments/pilot_a3b/confusion_report.json`、`I_need_interpret_use.txt`、`incoming/`，未纳入审查提交 |

测试通过只说明现有测试通过；下述配置篡改反例不在原测试覆盖内。

## 2. 阻断问题与最小修复

### R4-001（BLOCKER）：冻结配置可被调用方覆盖，仍返回 `PREFLIGHT_PASS`

- **位置：** `experiments/d094_llm_agent/run_d094_r4.py:59-77`（可变 `R4Config`）、`106-196`（按调用方配置计算并只检查调用方全局上限）、`282-338`（预检与执行未校验冻结配置）。
- **问题：** 没有要求 seeds=`301,302`、search seed=711、population=2、generations=1、64 episodes、320 请求和 0.442368 USD 保持冻结。`r4_manifest()` 仍写冻结 seeds，而 execution lock 可写另一组调用方 seeds，二者不一致仍通过。
- **零 API 复现：** 在临时目录调用 `run_r4(..., preflight_only=True)`：
  1. `R4Config(seeds=(401,402), search_seed=999)` 返回 `PREFLIGHT_PASS`；lock seeds=`[401,402]`、search seed=999，而 manifest seeds=`[301,302]`。
  2. `R4Config(generations=2, global_request_cap=1000, global_cost_cap=1.0)` 返回 `PREFLIGHT_PASS`；计划变为 **88 episodes、440 请求、0.608256 USD**。
- **影响范围：** 执行锁真实性、任务/seed 冻结、规模与真实预算。若真实入口复用该路径，可在不改变预注册的情况下执行另一实验并突破 R4 硬上限。
- **最小修复：** 在创建输出、构造 client 或 episodes 前集中校验不可变协议常量；默认计划必须精确等于 64/320/0.442368，拒绝任何 seeds、search seed、population、generations、模型、价格、并发、上限等偏离。执行锁应与冻结期望值比较，而不是仅记录调用方输入。增加上述两个反例及所有关键字段的请求前拒绝测试。
- **是否影响真实实验有效性：** 是，修复并重新独立审查前不得执行真实 R4。该修复只执行既有预注册，不需要改变任务、效应阈值或统计判据。

### R4-002（BLOCKER）：统计实现未纳入 execution lock

- **位置：** `run_d094_r4.py:40-56` 的 `SOURCE_NAMES` 缺少 `d094_r4_statistics.py`；`254-279` 只哈希该列表。统计实现实际位于 `experiments/d094_llm_agent/d094_r4_statistics.py:21-118`，由 `run_d094_r4_synthetic.py:13,145-159` 使用。
- **问题：** 当前 preflight execution lock 有 15 个源码哈希，全部匹配，但不包含生成符号翻转、bootstrap 和 Holm 结果的统计源码。修改这些计算不会使该执行锁失效。
- **影响范围：** 主要终点、raw/adjusted p、CI 和最终独立复算的源码身份。
- **最小修复：** 将统计模块及未来真实分析入口纳入同一执行锁；在新修订产物中重建 preflight/synthetic lock 与哈希清单，保留本次旧产物。增加统计源码篡改导致锁校验失败的测试。
- **是否影响真实实验有效性：** 是，真实运行前必须关闭；不需要修改已冻结的统计公式。

### R4-003（BLOCKER）：三个搜索臂共用一个传输预算池，80 请求／臂没有独立请求前硬隔离

- **位置：** `run_d094_r4.py:329-336` 仅预留 B1 和三个 final；`347-356` 将所有演化 search 都命名为 `search`；`d094_budget.py:102-120` 对该共享池统一放行。
- **问题：** B2/B3/B4 没有 `search:B2`、`search:B3`、`search:B4` 独立预留与结算。默认控制流通过 16 episodes×5 请求间接限制每臂 80，但第 81 个搜索请求不会由该臂的独立预算池在 transport 前拒绝。R4-001 又证明规模和全局上限可被覆盖。
- **已有 Mock 事实：** B2/B3/B4 search 分别 48/48/58 请求，均未超过 80；这证明本次 Mock 未超支，不证明独立硬隔离存在。
- **影响范围：** 分臂公平性、搜索间预算串用和异常路径的请求前停止。
- **最小修复：** 为每个演化臂建立独立 search 池，各冻结 80 请求／0.110592 USD；全局 R4 门禁直接冻结 320／0.442368。保留 B1/final 命名池，增加“第 81 次请求在 transport 前拒绝且不影响其他臂/final”的并发反例测试。
- **是否影响真实实验有效性：** 是，修复只落实已冻结的每臂预算，不增加预算或改变设计。

## 3. 算法正确性与公平性：PASS

| 检查项 | 独立源码证据 | 结论 |
|---|---|---|
| B3 配对单元与质量变化 | `d094_r4_credit.py:154-204` 按相同 task/seed 比较；`168-195` 先约束，再比较 `(1-task_success,1-recovery_success,harm)` 严格 Pareto；`207-210` 四单元算术均值 | PASS |
| 资源不进入主信用 | `121-145` 资源只进入七目标 Candidate；`154-210` 的信用不读取 Tool/token/latency；resource-only 测试位于 `test_d094_r4_credit.py:111-116` | PASS |
| 滑窗与概率 | `d094_r4_credit.py:273-319` 使用 deque W=4、空窗口 credit=0、稳定 softmax、τ=0.25、ε=0.2；下界 ε/6 | PASS |
| duplicate 与更新时序 | `439-473` duplicate 不评价/不更新；`477-503` 完整 child 评价后才更新；proposal 概率先在 `435-459` 落账 | PASS |
| 无未来信息 | parent 来自已完成 archive（`474-476`），credit 只读取该 parent 和当前已完成 child；仅后续 proposal 读取更新概率 | PASS |
| B2/B3/B4 机制隔离 | `277-289`：B2 固定均匀，B3 只用配对信用，B4 只用旧失败反馈；`406-418` 与旧 `d094_adaptive_evolution.py:126-134` 同为已完成候选公开 profile | PASS |
| 公共五步与公平初始种群 | `d094_r4_credit.py:242-244,376-378,421-423`：216 池、同一 search seed；`338-344` crossover 不改步数；`352-359` mutation 不改步数 | PASS |
| survivor 与 final | `d094_evolution.py:118-153` 为 feasibility-first 标准 NSGA-II；`run_d094_r4.py:433-443` 从全部四个搜索 archive 选 final，再独立执行四个新 episodes | PASS |
| 零调用 final | `run_d094_r4.py:577-582` 将 `api_attempt_count==0` 标为 execution error；`471-479` 使运行为 INVALID，不作为算法成败 | PASS |

一代两个 offspring 只能让首个非零信用影响后续 proposal，最后一个更新没有后续搜索机会；这是已披露的机制识别限制，不是公式错误。

## 4. Fresh Train 与历史证据：PASS（语义隔离限制保留）

- `d094_r4_tasks.py:23-52` 只有两个冻结任务；`55-92` 对完整 canonical 规格和历史 12+6 Train 做双向 ID／规格交集检查。
- 独立重算 manifest SHA-256=`e8412c74c33faf7a56195d685d49080b5669dbe46efd3ae1ab6dee88917b5bff`，与 execution lock 一致。
- `107-152` 的本地可达性覆盖两任务×301/302；补偿 3 步、transient 4 步，公共五步，API=0。可达性不等于真实 LLM 必然成功。
- 未读取 Validation/Test；held-out 语义重叠保持 `NOT_CHECKED_VALIDATION_TEST_ACCESS_FORBIDDEN`，不得宣称已证明语义独立。
- R3.1 原始目录 56 个文件按 `CANONICAL_LF_BYTES_WITH_POSIX_RELATIVE_PATHS` 独立重算，全部与深度分析快照一致；未重跑或改写 R3.1。

## 5. 统计设计审查：实现 PASS，推断范围受限

### 5.1 16 的真实含义

每个比较只有 **4 个 final 配对观测单元**：两个 task_id×seeds 301/302。`run_d094_r4_synthetic.py:145-159` 先按 `(task_id,seed)` 对齐左右两臂的独立 final Task Success，再计算差值；搜索期成绩不进入 final 统计。

`d094_r4_statistics.py:21-38` 对这 4 个差值枚举 `2^4=16` 种符号翻转。**16 是零分布的符号模式数，不是 16 个独立样本，也不是 16 组任务／seed／episode 观测。** `49-70` 的 20,000 次 bootstrap 同样每次重采样这 4 个单元。

### 5.2 二元终点与配对结构

- Task Success 为二元值，配对差为 -1/0/1；均值差等于四单元成功率差，主要阈值 0.25 对应一个净改善单元。
- 穷举符号翻转、paired-unit percentile bootstrap 和 `74-85,88-118` 的四比较 Holm 实现与冻结公式一致；全 1 差值的双边精确 p=0.125。
- 两个任务均 `seed_jitter=false`（`d094_r4_tasks.py:36,49`），环境只在 jitter 开启时使用 seed 改变失败调度（`d094_tasks.py:82-86`）。因此 301/302 不是两个独立任务条件，每任务两个 episode 不能冒充跨任务独立复制。
- 四单元符号翻转和独立单元 bootstrap 无法建立任务层级的一般化推断；Holm 也只处理本四比较族的多重性，不解决任务聚类或样本量问题。

**分类：可以在核心阻断修复后执行，但结论范围受限。** 当前预注册已明确探索性、非确认性和禁止普遍提升声明，因此无需为了保留这一限缩解释而改动原预注册。p 值和 CI 只能作为这四个观测单元的探索性描述。若未来要做任务总体或确认性推断，必须另建版本并重新预注册独立任务与任务层级分析；本轮不得擅自增加任务或改变 0.25 阈值。

## 6. 默认预算与账本审查

| 项目 | 独立结果 |
|---|---|
| 每请求上界 | `(4096×0.3+128×1.2)/1,000,000=0.0013824 USD`，正确 |
| 默认总规模 | 64 episodes、320 请求、0.442368 USD，计划字典与保存文件一致 |
| 默认预算 raw SHA | `21b80255516645fdbdf63f5063dbed0b528b4aaf97da4ca52fa1cea3e28ba150`，与 lock 一致；Windows raw 文件为 CRLF，字典内容亦一致 |
| B1/final 保护 | B1、final:B2、final:B3、final:B4 各 20 请求／0.027648 USD 独立预留 |
| 请求前停止 | `d094_budget.py:205-230` 在底层 transport 前 `begin`；预算拒绝不发送 |
| 重试与 unknown usage | 每 client `max_retries=0`；unknown usage 保留上界并置 `cost_unknown`，汇总为 INVALID |
| 请求 ID 与 Token | 已有 Mock 194 条发送记录均有完整 Token，194 个内部 `budget_request_id` 全部唯一 |
| Mock provider ID | 只有 5 个唯一值，因为每个 episode 新建 Mock transport；Mock 不证明真实 provider ID 全局唯一。真实入口必须核验响应 ID／内部 ID 的所需唯一性和身份冲突 |
| 真实模型 | lock 要求 `deepseek-flash`；当前只有 Mock，真实 endpoint/model 配置尚未执行验证 |

**预算结论：默认数值和 B1/final 保护 PASS，但 R4-001 与 R4-003 是真实执行前阻断。** 禁止以提高调用方上限或减少 final 绕过。

## 7. 产物独立复核

- execution lock 已列出的 15 个源码和 4 份协议文档 SHA 全部匹配；但统计源码缺失，见 R4-002。
- synthetic `artifact_sha256.json` 共 81 项，独立重算全部匹配；summary=`SYNTHETIC_VALIDATED`，13 个 gate 全 true。
- Mock 共 64 个唯一 episode ID、194 个唯一内部预算请求 ID；B1 fixed=4 episodes，三个演化臂各 search=16、final=4；B2/B3/B4 search 请求分别 48/48/58，final 各 10。
- preflight=`PREFLIGHT_PASS`、0 episode、`api_used=false`；Mock 与 synthetic 的真实 LLM 调用均为 0。所有 Mock 数值都不是实际 API 成本或 Agent 性能证据。
- 本轮实际重新执行 D-094 全量 discover：**135/135 OK**。这些测试未覆盖 R4-001 的配置篡改反例。

## 8. 结论与下一步

**最终结论：`REQUEST_CHANGES`。** 算法主信用、四臂隔离、信息时序、公共五步、全 archive final、Fresh Train 规格隔离和默认预算数值均通过；阻断来自冻结配置可绕过、统计源码未锁定和搜索预算未按臂硬隔离。

下一实现会话只做 R4-001～R4-003 的最小一致性修复，保留原 `D094_R4_PREREGISTRATION.md`、R3.1/R1/R2 历史和全部负面证据，不扩大任务、预算、代数或改变统计判据。修复后需重新生成新修订锁／合成产物、运行回归并再次独立审查。

真实 R4 仍为 **NOT RUN**，真实 API 为 **0**，用户真实实验授权为 **NOT_GRANTED**。即使后续审查通过，也仍需用户明确授权，才能使用 `deepseek-flash` 执行真实 R4；不得把 Mock 结果当作真实结果，不得静默降级为规则 Agent。
