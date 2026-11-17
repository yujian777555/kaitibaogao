# 111 — D-092 Typed Adapter 与五臂 Runner 实现一致性自检

**日期：** 2026-11-18

**仓库/分支：** `yujian777555/kaitibaogao` / `pilot-a-stateful-recovery`

**规格审查基线：** `110_D092_R2_3_INDEPENDENT_REVIEW.md`，提交 `2a95f0922a87d2b3b39b65363c09385d421fb762`

**本报告性质：** 执行者实现一致性自检，不是独立实现审批，不是实验报告

**状态：** `READY_FOR_IMPLEMENTATION_REVIEW / APPROVED_FOR_EXPERIMENT = NO`

## 1. 实现范围

新增 `experiments/d092_recovery/`，实现 R2.3 既有规格，不修改 canonical preregistration、历史快照、原 D-090 源码或 Train 数据。

| 模块 | 实现职责 |
|---|---|
| `d092_genome.py` | 五字段 TypedGenome、144 唯一映射、D090Genome 往返、canonical JSON、episode/attempt identity、probe 展开、mutation/crossover |
| `d092_feedback.py` | 六项聚合反馈、4×6 原矩阵、稳定 softmax、β=2/τ=.25/ε=.1、A4 零反馈均匀概率 |
| `d092_selectors.py` | 非支配排序、crowding、完整 ASF/E/intercepts/normalization、35 方向、association、niche=0/>0、feasible Pareto 最终选择 |
| `d092_runtime.py` | total grammar、安全 INVALID sentinel、public mask、attempt lifecycle、逐步状态/回执/attempt/tick 监视、硬约束 |
| `d092_evaluator.py` | family-equal fitness、聚合 optimizer view、audit-only 内部行、trace/outcome/joint hashes、collapse、Train 双重授权门禁 |
| `d092_runner.py` | 五臂统一 OFFER、96 unique/384 attempts、命名 RNG 流、七轮 offspring、A3/A4、完整日志、最终选择和无效部分账本 |

`.github/workflows/research-simulator-regression.yml` 仅新增 D-092 路径和 synthetic unittest step；没有加入 Probe、genome search 或 exhaustive 执行入口。

## 2. 实现与测试身份

以下为当前工作内容的 raw SHA-256 与 Git blob；最终实现提交 SHA 由提交后远端查询确定。

| 文件 | raw SHA-256 | Git blob |
|---|---|---|
| `experiments/d092_recovery/d092_evaluator.py` | `0c1fdb1d02ebd46cfb18ae3280435f132b589d36703e54e80e3990532d13751d` | `296d76f1ca95619a61b3780d34b5537c825a44d6` |
| `experiments/d092_recovery/d092_feedback.py` | `0d3e60420d7f69a8d8c823cbb6ca04c8ab91c53c677087c3e4fb0cde9c292199` | `a7fd4680a56938fad06365b35dc68459936d0dc9` |
| `experiments/d092_recovery/d092_genome.py` | `dbd2dbf162adca7ea40c64b7c90c203b52e08133e48458803504ccd76a295cb7` | `a1e72ec7b4ab9ca08e09dd3ad5f754000e8ac041` |
| `experiments/d092_recovery/d092_runner.py` | `f9326220f7a4deb1e31bee1139570740f3595074db4024aca392fc7b8b9d541e` | `89792be042d8d853953322c1863a314d5b7e81ee` |
| `experiments/d092_recovery/d092_runtime.py` | `cb8a058ce5a1f077fe286462efecf5138a5397ef34ea6ba0b805e0d539590f4a` | `772ab863216a02999049d262e9bdd250c5adf4aa` |
| `experiments/d092_recovery/d092_selectors.py` | `a9dfdd73da438ef42ef5507b19b8a2c036dc1e32c6a97b17c3071b522be4fd11` | `9c36211628374d112b98b7782a8f206fbb9b4b3f` |
| `experiments/d092_recovery/test_d092_evaluator.py` | `1537c10eebbbd5d9364b0407389efbc9feabdbeedd15bb7190f23e7f4f31e176` | `5490f2cd22b6ab6cbad94aa4dc9e017e0a3fa75f` |
| `experiments/d092_recovery/test_d092_feedback.py` | `cc17c2ab8c3420e4acdc7cbd2a72d9172f6e94dce4bd7cb74fd6bc076ec5feed` | `3e920503149587a10384a5d3177fa30675dca481` |
| `experiments/d092_recovery/test_d092_genome.py` | `fd75f78619c8250c45317d69c8646a50336baffc0cdd8be9e88606d12d0a5db9` | `2705d28a38fffd9ea4bd62be7ee9ed25dc690396` |
| `experiments/d092_recovery/test_d092_policy_adapter.py` | `a6120a3f82e9e9eaf2e5d942d21fc9fab1304db56cd0018f6a369f583fddc901` | `db9dd6d3af29c6f6fc9cc2ee58434138f14dadd7` |
| `experiments/d092_recovery/test_d092_runner.py` | `bc53375881c7550c6e610799c7591256e631aad0015464d6d83958610959fac2` | `7fe448a51001ad57e2479f704246e1031979961f` |
| `experiments/d092_recovery/test_d092_runtime.py` | `b66b2cf47f02dd7f00d4a489455f60de93e607226f2a96d6e665f4c5b93673b6` | `68288be0d053d6c9574c805d70cfe8be5bd208b4` |
| `experiments/d092_recovery/test_d092_selectors.py` | `fc99056615db01fde1afe9e4e5841eea5cb99df4f0e7bd48ec5893403ce8e5ae` | `ca1ec1aefeb01f6ba7a2309051c79c67490e1b68` |
| `.github/workflows/research-simulator-regression.yml` | 见 Git blob | `277f42335d2024860841de3e7c78223d34312830` |

R2.3 canonical raw/canonical/blob 仍为 `75f9c72aa7d3a70880f59f7b803ed88e919d47e9c42e7168ba1b7eddbc3e7522` / `549c595ed657d0b0582e6d6f41dfcfc241bde82b7daa2bdbf89bb3a660497ce4` / `1498f20a6f298093c06d126a766c037a980869a3`。R2.2 snapshot blob=`006aface19258f5d9ba597011dfe9048dfea8897`，未改变。

## 3. 测试先行与实际结果

各模块均先写测试并观察模块不存在的 RED，再实现并转绿。测试过程中修正了测试自身的算术/API 期望，并修复了以下真实实现问题：

1. Guarded Runtime 对 delayed success 后 DUPLICATE 与 delayed failure 后 PENDING 的不同路径分别保留证据。
2. optimizer 隔离不再误伤合法的 opaque `trace` hash 名称；原始 trace 仍不能进入 optimizer。
3. Runner 对 attempt-cap/评价中断返回 INVALID 并保留部分账本，不丢弃失败证据。
4. A2 niching 只接收 feasible candidates，不把硬约束违规者送入性能选择。
5. evaluator `feedback_marginals.row_count` 必须与该 genome 的账本 episodes 一致，否则 INVALID。
6. evaluator 同时返回双视图时保存 `audit_archive`；proposal/archive 的 optimizer 侧不含 audit_only_view。

实际本地环境：CPython 3.9.13、NumPy 1.26.4、Windows。协议目标 CPython 3.11.9/Ubuntu 22.04 尚未在本地部署，不声称目标环境已锁部署。

### D-092 测试（73/73 通过）

| 测试组 | 数量 | 覆盖 |
|---|---:|---|
| typed genome/identity | 10 | 144 一一映射、往返、BASE、canonical bytes、P00–P09、mutation/crossover |
| feedback | 8 | 聚合分母、六特征、矩阵、零反馈、softmax 边界 |
| selectors | 16 | NSGA-II/III、非零 ideal、非对角 E、转置反例、35 方向、niche 两分支、feasibility |
| guarded runtime | 13 | immediate/delayed、重复 VERIFY、blocked、PENDING、DUPLICATE、malformed、状态监视 |
| evaluator/views | 8 | family 聚合、三层隔离、hash/collapse、Train 门禁、manifest 只读核验 |
| runner | 14 | 五臂、预算/cache、RNG、反馈、A1/A4、INVALID、audit、无可行候选、复现 |
| real policy synthetic adapter | 4 | P03、P07 budget=10、threshold 12、合成环境实际执行 |

### 完整本地回归（529/529 通过）

- `pilot_a_recovery`：28/28。
- `pilot_a3b`：398/398。
- `d088_recovery`：8/8。
- `d089_recovery`：8/8。
- `d090_recovery`：14/14。
- `d092_recovery`：73/73。

所有测试使用 unittest discovery；D-092 额外通过 `compileall`。`git diff --check` 通过。没有失败或错误被删除以制造绿色结果。

## 4. 合成运行观察与科学边界

使用测试专用 SyntheticEvaluator、每个 unique genome 两个 synthetic aggregate episodes，观察到：

| 臂 | 状态 | unique evaluations | attempts | 无效原因 |
|---|---|---:|---:|---|
| A0 | VALID | 96 | 96 | 无 |
| A1 | INVALID | 79 | 384 | INVALID_ATTEMPT_CAP |
| A2 | INVALID | 77 | 384 | INVALID_ATTEMPT_CAP |
| A3 | INVALID | 60 | 384 | INVALID_ATTEMPT_CAP |
| A4 | INVALID | 79 | 384 | INVALID_ATTEMPT_CAP |

这些是预算耗尽与部分账本保存的合成控制流证据，**不是算法性能结果**。A1/A4 的 INVALID 轨迹仍逐 proposal/RNG/survivor/archive 完全一致。不得将不同 unique 数解释为反馈优劣；不得为消除 INVALID 而修改 384 cap、seeds 或算法。

没有真实 Train rollout、960 Probe、genome search、13,824 exhaustive、Validation/Test、调参、候选冻结、真实 LLM API、A800/ARWM 或其他受禁实验。`load_train_manifest()` 只读验证 96 IDs/哈希，不执行 episode。

## 5. 实现一致性自检结论

- 五臂算法身份由不同控制流实现，不依赖名称：A0 无 survivor，A1/A3/A4 共用 NSGA-II，A2 使用完整 NSGA-III。
- A3 仅使用上一轮 12 个新 unique offspring 的聚合反馈；A4 永久零反馈且不消费额外 variation RNG。
- 初始池和命名流遵循 common-random-numbers 设计；跨 arm 不共享缓存。
- 硬约束不可由 fitness/Harm/Cost 抵消；无 feasible candidate 返回 NO_FEASIBLE_CANDIDATE。
- optimizer 只接收聚合对象；audit 数据保存在独立通道，支持后续独立复算。
- 当前证据只支持进入**独立实现一致性复审**；不支持 Probe、正式 Train-only 搜索或任何算法提升主张。

## 6. 下一任务

由新的审查会话对以上代码哈希、真实源码调用链、测试输出和本报告做实现一致性复审。重点检查 NSGA-III、反馈集合、attempt 生命周期、隔离接口、预算及无效运行处理。

**`APPROVED_FOR_EXPERIMENT = NO`。** 复审通过并取得用户明确批准后，才允许运行 Probe 和正式 Train-only 搜索。CI 以最终提交的真实 Actions run 为准；本报告编写时不预填 CI 成功。
