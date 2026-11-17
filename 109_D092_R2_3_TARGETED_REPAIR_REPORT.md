# 109 — D-092 R2.3 定向修复与独立验收准备报告

**日期：** 2026-11-18  
**仓库/分支：** `yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`  
**最高审查依据：** `108_D092_R2_2_INDEPENDENT_REVIEW.md`  
**状态：** `READY_FOR_INDEPENDENT_REVIEW / NOT FROZEN / NOT RUN`  
**范围：** 仅 F9 canonical identity encoding 与 F13/P07 真实控制流；无算法实现或实验执行。

## 1. Git 接管与提交身份

- 接管并同步后的 HEAD：`b7b0ba4b623a22e01a10dded378d80215ca4866a`。
- main：`683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，未修改、未合并。
- 接管时工作分支相对 main：ahead/behind=`318/0`；本地工作区 clean。
- 最终 HEAD 为**本报告所在的提交**。完整 40 字符 SHA 由提交后 `git rev-parse HEAD` 与 `git ls-remote origin refs/heads/pilot-a-stateful-recovery` 联合确定，并在本轮最终汇报中列出。由于提交哈希覆盖本文件内容，报告不能在不改变自身哈希的情况下预先嵌入其所在提交的 SHA；不以猜测或占位哈希冒充最终身份。
- 本轮预期变更仅 canonical 103、R2.2 snapshot、本报告及五份维护文档；不修改算法源码、manifest 或历史结果。

## 2. R2.2 / R2.3 文件身份

| 对象 | raw SHA-256 | canonical SHA-256 | Git blob |
|---|---|---|---|
| R2.2 snapshot `103_D092_TRAIN_ONLY_PREREGISTRATION_R2_2.md` | `c0035d0f7236eff03325e81c2b7967ae166bc4c73047e390d502859f6d8fdc5c` | `f18aecb71791e43220ac74920c67c27141c58eaadfde74fd0190103e0b4695a3` | `006aface19258f5d9ba597011dfe9048dfea8897` |
| R2.3 canonical `103_D092_TRAIN_ONLY_PREREGISTRATION.md` | `75f9c72aa7d3a70880f59f7b803ed88e919d47e9c42e7168ba1b7eddbc3e7522` | `549c595ed657d0b0582e6d6f41dfcfc241bde82b7daa2bdbf89bb3a660497ce4` | `1498f20a6f298093c06d126a766c037a980869a3` |

R2.2 snapshot 与提交 `7cd092431b0817f67aca3960ecad2590fb6d5b13` 中的 canonical R2.2 逐字节一致。R2.1 snapshot 保持 raw=`104df3497f58171f48e82e25674d1b14e22673a34561d263f8679aadd34648ee`、canonical=`e71027477f49bde939c3a45a1d7327e04d426da4b06a4b4a9a1c41c687916a45`、blob=`773f39e5984c20d011a8d89245ecf52790886088`。R0/R1/R2 均未覆盖。

## 3. F9：仅明确 canonical JSON 字节编码

### 修改前

两种 identity 公式写作 `SHA256(UTF8(canonical_json(payload)))`。字段和碰撞修复已由 108 号接受，但 `UTF8(...)` 与 canonical JSON 参数没有在同一处明确绑定。

### 修改后

`episode_reference` 与 `compensation_attempt_id` 统一使用：

```text
canonical_json(payload) = json.dumps(
  payload,
  ensure_ascii=False,
  sort_keys=True,
  separators=(",",":"),
  allow_nan=False
)
hash_input = canonical_json(payload).encode("utf-8")
identity = SHA256(hash_input)
```

不添加换行、额外空格或其他编码。identity payload 仍仅含既有 string/integer 字段：

- episode：`seed`、`unique_ordinal`、`genome_sha256`、`scenario_id`；
- attempt：`episode_reference`、`dispatch_ordinal`。

**未改变：** unique ordinal、attempt ordinal、run/global composite keys、C/F/D 反馈集合、r/d 计数、TIMEOUT/PENDING/COMPENSATED/FAILED lifecycle、重复 VERIFY 规则及 optimizer 聚合信息边界。静态比较确认 `完整 receipt lifecycle` 至 §5.3 的文本与 R2.2 完全一致。

## 4. F13/P07：真实 14-action 共同前缀

### 源码依据

- `DependencyRecoveryEnv._compensate()`：成功时在 delayed TIMEOUT 返回前立即将 tool state 改为 COMPENSATED。
- D088 `_pending_action()`：等待窗口内若 `_available()` 非空且 `_can_dispatch_more()` 为 true，返回 None，允许独立工作先派发。
- D088 `act()`、D089/D090 `_abort()`：上述 None 不强制 WAIT，而是继续正常动作选择。
- D088 `_update_evidence()`：TIMEOUT dispatch 已记录 attempts 为 seen；之后的 delayed FAILED 不重复增加 route_failures，但公开 last_receipt 可使 alternate 合法。

### 冻结轨迹

| 步骤 | 动作 | 回执/状态 |
|---:|---|---|
| 1 | `COMPENSATE(C,primary)` | `TIMEOUT`；第一次 outcome=false，C 仍 COMMITTED，receipt pending |
| 2 | `WAIT()` | `WAITED` |
| 3 | `VERIFY(C)` | `PENDING` |
| 4 | `WAIT()` | `WAITED` |
| 5 | `WAIT()` | `WAITED` |
| 6 | `VERIFY(C)` | `FAILED`；C 仍 COMMITTED，pending 清除 |
| 7 | `COMPENSATE(C,primary)` | `TIMEOUT`；第二次 outcome=true，C 当场 COMPENSATED，receipt 仍 pending |
| 8 | `COMPENSATE(B,primary)` | `TIMEOUT`；C 已满足 B requires=[C]，允许在 C receipt pending 时派发 |
| 9 | `WAIT()` | `WAITED` |
| 10 | `VERIFY(B)` | `PENDING` |
| 11 | `WAIT()` | `WAITED` |
| 12 | `WAIT()` | `WAITED` |
| 13 | `VERIFY(B)` | `FAILED`；B 仍 COMMITTED，B pending 清除 |
| 14 | `VERIFY(C)` | `COMPENSATED`；清除 C pending，不再次改变 C 状态 |

第 7 步后不能在 C pending 时假定连续 WAIT。第 8 步 B primary 的立即派发是真实控制流的关键修正。步骤 13 后只剩 C pending，故步骤 14 为 VERIFY(C)。

这是**源码级状态推演与文档轨迹规格**，不是本轮执行的 probe 或新实验数据。

## 5. P06/P07 第一处分叉证明

14 步完成后：

- `decision_count=14`，`budget_remaining=24-14=10`；
- C=COMPENSATED，A requires B 尚不可达，D=NOT_COMMITTED；
- B primary：requires=[C]、cost=3、attempts=1、last_receipt=FAILED；
- B alternate：requires=[]、cost=1、attempts=0；
- 公开 FAILED 使 `_primary_blocked_or_failed()` 允许 B alternate。

P06/P07 仍只有 harm threshold 4/12 不同：

| 对照 | 分支条件 | 选择 |
|---|---|---|
| P06 | 10>4，ordinary priority | `COMPENSATE(B,primary)` |
| P07 | 10≤12，tight priority | `COMPENSATE(B,alternate)` |

在 delayed FAILED 未新增 route_failures 的该状态，position、topo、wait 与 tool-level unlock 对两路由相同。ordinary 分数差为：

\[
\begin{aligned}
&score(B\,primary)-score(B\,alternate)\\
&=w_{hint}+2w_{cost}+w_{dependency}-alternate\_boost\\
&=\mathbf{2.770802651881641}>0.
\end{aligned}
\]

因此 ordinary 选 B primary。tight key 依次比较 requires 数、cost、idempotency、tool/route；alternate 以 requires=0、cost=1 获胜。R2.3 PASS 条件要求上述完整 14-action 前缀、budget=10、两个精确动作及 \(\Delta_{P07,P06}(Q3)=1\)；任一不符合即 HOLD。budget=13/12 的阈值边界仍由后续非 rollout 合成测试验证。

## 6. Train 与冻结项完整性

| 冻结项 | 核验结果 |
|---|---|
| Train 场景 | 96 个唯一 IDs；manifest Git blob=`b917b4c624601022e8d8896182dfaed71ba0d21c` |
| μ / λ | 12 / 12 |
| unique evaluations | 96；12 initial+7×12 |
| proposal attempts | 384 cap，含初始化 |
| 实验臂 | A0/A1/A2/A3/A4 五臂不变 |
| seeds | 711、822、933、1044、1155 |
| 反馈矩阵 | §5.3 与 R2.2 逐字一致 |
| F8 | §3.2 原映射逐字一致 |
| F14 | §11.2 原公式逐字一致 |
| 统计判据 | §12.1 与 R2.2 逐字一致 |
| F9 lifecycle | 与 R2.2 逐字一致，仅 serializer 明确化 |
| P03 | 原 P01/P03 Q1 对照和证明逐字一致 |
| P06/P07 机制 | 原阈值 4/12、genome 展开与 ordinary/tight 对照不变 |
| 其他已通过项 | F10、F11、F12、F15 不重开 |

13/13 绑定源码的 canonical SHA-256 与 Git blob 均重新匹配。R2.2、R2.1、R2、R1 快照保持完整；R0 未在本轮 diff 中出现。

## 7. 实际检查与测试结果

本轮实际执行的是文档、哈希、公式和静态轨迹规格检查：

- R2.2 snapshot 与 R2.2 原提交逐字节比较通过。
- R2.1/R2/R1 Git blob 与历史值一致。
- 96 Train IDs、manifest blob、13/13 源码身份通过。
- F8/F14、预算、反馈矩阵、候选选择、统计判据、F9 lifecycle、P03 的冻结文本比较通过。
- F9 两种 payload 均显式调用 `canonical_json(...).encode("utf-8")`，无旧 `UTF8(canonical_json(...))` 写法。
- P07 表格逐步解析恰好得到上述 14 个动作/回执；`24-14=10` 和精确分数检查通过。
- canonical 103 不含旧 17-action、budget=7、24-17、旧等待段或旧 9–12 窗口描述。
- 无 OPEN/TBD/TODO；代码围栏成对；`git diff --check` 通过。

**算法单元测试、静态算法测试、合成算法测试和真实环境 rollout：NOT RUN。** 本报告中的 14 步是源码推演规格，不冒称已经通过 probe 回放。

## 8. 未执行实验与授权边界

本轮未执行：

- 960 probe episodes；
- genome search 或正式 Train-only 搜索；
- 13,824 exhaustive reference；
- 调参或候选冻结；
- Validation/Test；
- Pilot B、正式 A-3b；
- 真实 LLM API、A800/ARWM、UndoBench TEST、ThinkingBox；
- main 修改或合并。

本轮无新算法性能数据，不构成动态反馈优于 NSGA-II 的证据，也不构成创新成立结论。报告编写时尚无本轮 CI/artifact；最终以提交后的真实 GitHub 查询为准，无 run 时明确记 NOT RUN。

## 9. 仓库维护与下一步

同轮维护 `README.md`、`SESSION_HANDOFF.md`、`NEXT_SESSION_PROMPT.md`、`05_DECISION_LOG.md`、`51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md`，记录 R2.2 immutable snapshot、R2.3 三种身份、两项修复、验证范围和实验门禁。

**唯一下一任务：** 新独立会话只复核 F9 canonical encoding 与 F13/P07 的 14-action/budget=10 修订。定向复核通过后立即进入：

**Typed Adapter → 静态算法测试 → 合成测试 → 实现一致性审查。**

Typed Adapter 必须实现既有 typed genome→D090Genome 映射、统一 evaluator、五臂预算与账本、optimizer 聚合信息隔离和 audit 独立复算接口。不得借实现阶段更改冻结参数。实现一致性审查通过并取得用户明确批准后，才允许 Probe 和正式 Train-only 搜索。
