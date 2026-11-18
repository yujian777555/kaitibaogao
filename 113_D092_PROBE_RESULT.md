# D-092 960 Probe 真实执行与独立复算报告

- 日期：2026-11-18
- 协议：`103_D092_TRAIN_ONLY_PREREGISTRATION.md`（R2.3）
- 执行分支：`pilot-a-stateful-recovery`

## 1. 结论

**Probe = HOLD；五臂正式 Train-only 搜索 = NOT RUN。**

960/960 个真实 Train episodes 已完成，seed=711，cache_hits=0。P00–P04、P07–P09 为 PASS，P05、P06 为 HOLD。按照 R2.3 §10 和用户授权的先决条件，不能启动五臂五 seeds 正式搜索。

本报告只证明机制可辨识性 Probe 的实际结果及账本完整性，不构成算法性能提升、候选冻结或创新成立证据。合成测试也没有被当作真实实验结果。

## 2. 执行身份与环境

- 接管基线：`e505f0d2126f729968f298c1448f9dedcabb48d1`。
- Probe 锁和三项账本/RNG修复的提交：`7be851e264bcad2e2d3105c7c21f2c3e7db76ebd`。
- 锁内 `source_head=e505f0d2126f729968f298c1448f9dedcabb48d1` 是生成锁时的 Git 基线；实际执行代码由锁内逐文件 SHA-256/Git blob 绑定，不能将该字段误写成锁的提交 SHA。
- 执行锁创建时间：`2026-11-18T11:34:37.624687+00:00`，早于首次 rollout。
- 环境：Ubuntu 22.04 LTS x86_64、CPython 3.11.9、NumPy 1.26.4、`PYTHONHASHSEED=0`。
- 运行命令：

```bash
PYTHONHASHSEED=0 .runtime/venv/bin/python experiments/d092_recovery/run_d092_probe.py --execute
```

- 实际 Probe 用时：2.761795168999999 秒。该时间只是本机模拟器执行时间，不是其他环境的性能承诺。
- R2.3 canonical 未修改：raw SHA-256=`75f9c72aa7d3a70880f59f7b803ed88e919d47e9c42e7168ba1b7eddbc3e7522`，canonical SHA-256=`549c595ed657d0b0582e6d6f41dfcfc241bde82b7daa2bdbf89bb3a660497ce4`，Git blob=`1498f20a6f298093c06d126a766c037a980869a3`。

## 3. 原始产物与身份

目录：`experiments/d092_recovery/results/probe/`。

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `execution_lock.json` | 12,770 | `eb114463c3549527d577c26a24f221a03291d20a9a1e6e524514300aaa4b9787` |
| `episodes.jsonl` | 39,218,251 | `b063fba6d24c2a89038dddffe62cedaed518f489cfa1097bfc2b90cea421f02a` |
| `probe_summary.json` | 3,765 | `2338e9924f392bb2a7d323c506b29e71a7f6a4b47734e77cc8504dcf2b781264` |
| `probe_report.md` | 534 | `5026bf9100ec3c3fa9ed02939fde1d9e46eb956337eac7e4e514837418f554f2` |
| `independent_audit.json` | 6,446 | `854b6cb02524621af1f405975d015e6dafac5894feb442b8cdb0f411791dc276` |

每条 episode 保存 probe/genome/scenario identity、完整 trace、outcome、before/action/mask/observation/after 状态记录、attempt lifecycle、adapter events、episode reference 和 trace/outcome/joint SHA-256。原始结果只读审计，没有重跑、覆盖或删除不利记录。

## 4. P00–P09 实际判据

| Probe | Episodes | 结果 | 独立复算证据 |
|---|---:|---|---|
| P00 | 96 | PASS | 完整合法监视基准 |
| P01 | 96 | PASS | Q0 alternate/primary 及 Q0b OFF/FILTER；Q0b first difference=1 |
| P02 | 96 | PASS | Q0 alternate/primary 及 Q0b OFF/FILTER；Q0b first difference=1 |
| P03 | 96 | PASS | Q1 初始 fallback；候选恰为 A/B/C alternate |
| P04 | 96 | PASS | Q2 completion guard 对照；first difference=16 |
| P05 | 96 | **HOLD** | `q3_harm_priority_window=false`；first difference=null |
| P06 | 96 | **HOLD** | `q3_harm_priority_window=false`；first difference=null |
| P07 | 96 | PASS | 精确 14-action prefix、budget=10、P06/P07 分叉；first difference=14 |
| P08 | 96 | PASS | Q4 delay probe 对照；first difference=1 |
| P09 | 96 | PASS | Q4 delay probe 对照；first difference=2 |

P07 的 PASS 证明 harm budget=12 在 budget=10 的预定对照可以改变选择；它不能替代 P05/P06 各自预注册判据，也不能外推为搜索性能提升。

## 5. P05/P06 根因

原始 Q3 轨迹显示 P00、P05、P06 的 action/observation 序列完全相同，first difference 均为 null；三者该场景的 trace SHA-256 均为 `f2aa64b7ff2fdd06bd301360028d08588c231a2d8acbe8d91abccd4330aae0c3`，outcome SHA-256 均为 `e3002aad638312eb03f9763e638d5e45cde98357aa5cd990f57a5269a6eb67ed`。joint hash 不同仅因为 episode identity 不同，不表示行为不同。

逐状态复算普通/紧预算优先级得到：

| 0-based step | budget_remaining | 可用候选 | ordinary / tight | 实际动作 | 控制流解释 |
|---:|---:|---|---|---|---|
| 14 | 10 | B primary/alternate | 均为 B primary | COMPENSATE(B,primary) | 尚不在 P05/P06 窗口 |
| 15 | 9 | 仅 A primary | 均为 A primary | COMPENSATE(A,primary) | 尚不在窗口，且无候选差异 |
| 16 | 8 | 空 | 无 | WAIT | pending receipt；无可比较候选 |
| 17–20 | 7/6/5/4 | 空 | 无 | VERIFY/WAIT | pending resolution，无可比较候选 |
| 21 | 3 | A primary/alternate | A primary / A alternate | VERIFY(B) | 有理论排序差异，但 `_can_dispatch_more=false` 且 pending，不能进行候选选择 |
| 22 | 2 | A primary/alternate | A primary / A alternate | ESCALATE | `_can_dispatch_more=false`，不是 tight/ordinary COMPENSATE 分支 |

因此：

- P05 在 `budget<=8` 内没有出现“P00 实际选择 tight 项、P05 实际选择 ordinary 项”的共同 before-state。
- P06 在 `4<budget<=8` 内没有可用候选，更不存在预定分叉。
- 根因是冻结 Q3 轨迹中目标窗口被 pending resolution/停止控制流遮蔽，而不是把 P05 的 `None` 错传入数值比较，也不是 summary 漏报已有差异。
- 独立审计的 `p05_eligible_steps=[]`、`p06_eligible_steps=[]`，reason code=`NO_EXECUTABLE_PRIORITY_DIVERGENCE_IN_PREREGISTERED_WINDOW`。

不得在看到该结果后更换场景、窗口、阈值或判据来制造 PASS。若继续研究这些对照，需要新的版本化预注册和独立 Train 证据；D-092 原始 HOLD 永久保留。

## 6. 硬约束与反馈账本

960 episodes 的独立复算合计：

| 字段 | 数量 |
|---|---:|
| invalid_action_count | 0 |
| illegal_state_transition_count | 0 |
| duplicate_count | 0 |
| pending_count | 120 |
| runtime_abort_count | 146 |
| unauthorized_action_count | 2,748 |
| compensation attempts | 2,032 |

所有数量均保留。它们是 Probe 机制轨迹的约束/回执统计，不是五个正式搜索臂的候选可行性结果，不能据此选择正式候选或宣称算法改善。

## 7. 独立复算与测试

新增 `experiments/d092_recovery/d092_probe_audit.py`，不导入 `d092_probe.py` 的判据或结果逻辑。审计器直接读取原始 JSONL，独立重算：

- 960 个唯一 `(probe_id,scenario_id)`、每个 probe 的 96 个冻结 Train IDs；
- episode/attempt identity、三种 episode hashes、全局 2,032 个唯一 attempt IDs；
- trace/transition/adapter 对应关系、预算递减、pending/duplicate/invalid/abort 计数；
- immediate/delayed attempt 关闭与 unresolved 状态、反馈分子分母；
- P00–P09 的原始判据、summary 数值、原始文件 SHA/字节数；
- Train-only manifest 内部和 canonical 哈希；Validation/Test rows=0。

实际执行结果：`audit=PASS`、`probe=HOLD`、`episodes=960`。`PASS` 仅表示审计一致性，不表示 Probe 门禁通过。新增篡改测试证明修改 trace 或 attempt lifecycle 会被拒绝。

在 Ubuntu 22.04 / CPython 3.11.9 / NumPy 1.26.4 下的真实测试输出：

| Suite | 结果 |
|---|---:|
| pilot_a_recovery | 28/28 OK |
| pilot_a3b | 398/398 OK |
| d088_recovery | 8/8 OK |
| d089_recovery | 8/8 OK |
| d090_recovery | 14/14 OK |
| d092_recovery（含4项原始Probe审计） | 86/86 OK |
| **合计** | **542/542 OK** |

一次循环命令因 suite 变量为空而错误显示 0 tests；该次结果未计入通过证据，随后已用六个显式 suite 命令完整重跑，以上数字来自有效重跑。

## 8. 远端 CI 与 artifact

代码/结果提交 `c1975a7f3fea73f6af6d845b229ec9fd3e769593` 触发真实 GitHub Actions run [`44299067518`](https://github.com/yujian777555/kaitibaogao/actions/runs/44299067518)，workflow=`Research simulator regression tests`，job=`134783672580`，最终状态 `completed/success`。D-092 步骤日志实际为 `Ran 86 tests`、`OK`。CI 使用 Ubuntu 22.04、CPython 3.11.9 和 hash-locked NumPy 1.26.4。

该 run 生成 6 个既有 artifact：`d064c-formal-scenario-manifest-candidate`、`d079-d078-audit-and-challenge-candidate`、`d085-prefix-development-and-mechanism-audit`、`d086-dependency-development-and-fixed-gate`、`d087-frozen-replication-regression-evidence`、`d091-independent-audit-evidence`。没有 D-092 专属 CI artifact；D-092 Probe 原始产物作为 Git 文件入库。CI 没有执行 Probe、正式 genome search 或 exhaustive reference。

本报告后续的纯文档维护提交若未触发新 run，必须标记该提交 CI=NOT RUN；上述 success 只归属于 SHA=`c1975a7f3fea73f6af6d845b229ec9fd3e769593`，不能转移为算法性能证据。

## 9. 未执行事项与下一步

- A0–A4 × seeds 711/822/933/1044/1155 正式搜索：NOT RUN。
- A3−A1、A3−A4、A1−A0、A2−A1：NOT RUN，无逐 seed 改善或统计门槛结论。
- 正式搜索 R3/R4/CondRec/Harm/Cost、phenotype collapse、候选硬约束与 Pareto 选择：NOT RUN。
- 13,824 exhaustive reference、Validation/Test、Pilot B、真实 LLM/API、A800/ARWM：NOT RUN。
- main 未修改；没有冻结正式候选。

下一步只能基于这份真实负面证据做最小诊断和版本化后续设计；不能绕过 Probe 门禁。任何后续机制必须通过真实、可复算实验才能形成开题创新表述。
