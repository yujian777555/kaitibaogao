# R1 Estimator Gate 确认性实验结果

**日期：** 2026-11-05  
**状态：** CONFIRMATORY RUN COMPLETED / **ESTIMATOR_GATE_FAIL** / **GOM GATE NOT RUN**  
**接管基线 HEAD：** `a3cec9844332bbce04061af3041061fa94e88143`  
**协议：** `42_TCAIL_ESTIMATOR_TO_GOM_CONFIRMATORY_GATE_R1.md`  
**环境：** 隔离 Python 3.10.1，`environment/requirements-lock.txt`（numpy 1.26.4、pandas 2.2.2、scipy 1.13.1、scikit-learn 1.4.2）

## 0. 结论先行

Estimator Gate **失败**。

- Held-out 五种情景 macro-AUPRC 的配对差（TCAIL q − validation-selected strongest baseline）为 **−0.0996**，95% CI **[−0.1139, −0.0858]**，下界远小于 0。
- 两个预注册关键情景均显著更差：sparse pairwise −0.0393 [−0.0741, −0.0102]；parent sign-flip −0.3541 [−0.4081, −0.2983]。
- 只有 low-support/drift 情景 TCAIL 显著更好：+0.0462 [0.0261, 0.0674]。
- 因此按协议停止 TCAIL estimator 优越性主张；**Downstream GOM Gate 未运行（NOT RUN）**。本轮没有产生任何“TCAIL 改善演化搜索”的证据。
- 本结论只否定“该 Bernoulli M2/M3 + conservative merge 实现在该合成任务族上优于强基线”，不等于证明任何形式的层次交互建模都不可能有效。

## 1. 实际运行内容

| 项目 | 内容 |
|---|---|
| 训练 seeds | 0–39（40） |
| 验证 seeds | 40–59（20） |
| Held-out seeds | 3000–3039（40，正式运行前未使用） |
| 情景 | additive_null、sparse_pairwise、parent_sign_flip、overlapping_higher_order、low_support_drift |
| 变量/模块 | 40 变量、10 个预定义局部模块、每模块 4 变量；每个 seed 拟合一个模块，10 个 seed 轮转覆盖全部模块 |
| 支持量 | 非 drift 情景按 seed 轮转 8/16/32/128 blocks；drift 情景固定 8 blocks + 15% 缺失 cell |
| 真值 | 目标 task 分布下 Gauss–Hermite 积分的 probability-scale 四格差分 `p00 − p10 − p01 + p11`；`δ_local = 0.08` |
| 观测 | 每个 parent context 下完整 2⁴ 局部设计中的四格 task-block Bernoulli 结果 |

运行命令：

```bash
PYTHONUTF8=1 experiments/tcail_confirmatory_r1/.venv/Scripts/python.exe -W ignore \
  -m experiments.tcail_confirmatory_r1.run_estimator_gate \
  --jobs 12 \
  --output experiments/tcail_confirmatory_r1/results \
  > experiments/tcail_confirmatory_r1/results/run.log 2>&1
```

所有原始观测、pair truth、fixed effects、task/block 参数、per-pair 评分、per-seed 指标、日志和 summary 均保存在 `experiments/tcail_confirmatory_r1/results/`。

## 2. 估计器实现

### 2.1 模型

真正的 Bernoulli task/block 层级 GLMM，不是 Normal–Normal proxy：

- M2：intercept + 全部主效应 + 全部 pairwise 项；
- M3：M2 + 全部 three-way 项；
- 随机效应：observed task intercept、observed block intercept（non-centered 参数化，`log σ_task`、`log σ_block`）；
- 固定效应先验：intercept sd 2.0、main 1.0、pairwise 0.5、three-way 0.25；
- 后验：joint Laplace 近似，512 draws；predictive 32 draws，对 task/block 随机效应做 Monte Carlo 积分；
- 输出：
  - `q = P(|Δ_ij| > δ | D)`；
  - `w = E[(|Δ_ij| − δ)_+ | D]`；
  - 95% credible interval、方向概率、MCSE；
- abstain：缺 cell、`min_task_support=2`、`min_block_support=8`、拟合失败、M2/M3 方向冲突（`p_positive` 与 `p_negative` 各自 ≥0.9 且相反）；
- conservative merge（预注册）：`q=min(q_M2,q_M3)`，`w=min(w_M2,w_M3)`，任一模型失败即 abstain。

**限制：** Laplace 近似，不是精确 MCMC；没有 random slopes；drift 情景的真值含 task slope/overdispersion/drift，而估计器只含随机截距，因此该情景存在模型误配。该误配是预先设计的一部分，但必须在解释中保留。

### 2.2 本轮实现修复

在正式 held-out 运行前修复并记录：

1. **局部 pair → 全局 pair 映射错误。** 第一版先覆写 `pair_i` 再用它查局部映射，导致跨模块 seed 抛 `KeyError: (4, 1)`；smoke 因 seed 0 模块变量恰为 0–3 而未暴露。修复为一次性计算映射后再写回。此 bug 在正式 held-out 前修复，未查看 test。
2. **阈值选择使用 `>=`。** train null 的 95th percentile 阈值为 0 时会把所有零分边选入，smoke 中 Oracle null false-link 被误报为 1.0。改为严格 `>`，并写入 `experiment_config.json` 的 `selection_rule`。修复后 smoke 中 Oracle null false-link 为 0。
3. **Held-out seed 隔离。** 原默认 test 为 60–99，但 seed 60 已用于早期 smoke。正式运行前把 held-out 改为 3000–3039；train/validation 不变。
4. **并行 runner。** 增加 `--jobs`（`ProcessPoolExecutor`），只改变执行方式，不改变 seed、数据、模型或统计量。单进程与并行使用同一 `fit_graph`。
5. **Non-centered 参数化。** 早期 centered 参数化在真实生成数据上出现 variance funnel（`σ_block→0`、Hessian 秩不足、全部 abstain）；改为等价 non-centered 参数化并用 Jacobian 转回原参数。梯度/Hessian 已用中心有限差分核验。

## 3. 基线

所有方法共享同一批 task-block 四格观测、同一 seed 和同一支持过滤。基线状态必须按下列边界解读：

| 方法 | 本轮状态 | 说明 |
|---|---|---|
| TCAIL q / w | 正式实现 | Bernoulli task/block M2/M3 Laplace |
| local raw contrast | 适配 | 直接四格绝对 contrast，非原论文方法 |
| standardized contrast | 适配 | `|mean Δ| / (SE + 0.015)`，强基线 |
| context pooled | 适配 | 跨 parent 汇总 |
| FBL absolute-ratio | **paper-setting adaptation** | 非原论文复现；epsilon gate 为适配 |
| FBL signed Eq.(7) | **diagnostic only** | R1-A 已记录 2,811/3,800 领域违规；不参与最强基线选择 |
| cDLED-P3M | **static adaptation** | 只有 individual-local DLED + conditional eVIG 入口；未运行 SLL-DSM、原生 P3M、donor-restricted GOM |
| CGOMEA linkage | **static adaptation** | 只有 conditional dependency 接口；未运行原生 conditional FOS builder、variation 或 GOM |
| random linkage | 基线 | 每 pair/context 确定性随机分数 |
| oracle linkage | 上界 | 直接使用 probability-scale 真值 |

**未在本轮实现：** SLL-MI、FBL incremental、DLED 完整版、LMM、ALI/AIM、Tinós 2026 GAwLL2。它们已在 V2.2 规格中登记，但本轮实验没有运行。由于 TCAIL 已输给更简单的 standardized contrast，缺失这些更强基线不会改变本轮 NO-GO 方向；但会限制“TCAIL 不如全部现有方法”的表述。

## 4. Estimator Gate 结果

验证集最强非 Oracle 基线：**standardized**（validation macro-AUPRC 0.7713）。

### 4.1 主 Gate

| 指标 | 数值 |
|---|---:|
| Held-out seeds | 40 |
| TCAIL q mean macro-AUPRC | 0.6736 |
| Strongest baseline mean macro-AUPRC | 0.7732 |
| Paired mean difference | **−0.0996** |
| Paired bootstrap 95% CI | **[−0.1139, −0.0858]** |
| Key scenarios not significantly worse | **False** |
| Gate | **ESTIMATOR_GATE_FAIL** |

### 4.2 分情景

| 情景 | 配对差 | 95% CI | 判断 |
|---|---:|---|---|
| additive_null | 0.0000 | [0.0000, 0.0000] | 无正例，AUPRC 约定为 0；不提供区分信息 |
| sparse_pairwise | −0.0393 | [−0.0741, −0.0102] | 显著更差 |
| parent_sign_flip | −0.3541 | [−0.4081, −0.2983] | 显著更差 |
| overlapping_higher_order | −0.1511 | [−0.1938, −0.1101] | 显著更差 |
| low_support_drift | +0.0462 | [+0.0261, +0.0674] | 显著更好 |

### 4.3 方法排序（held-out macro-AUPRC）

| 方法 | Mean | 备注 |
|---|---:|---|
| oracle | 0.8000 | 4 个非 null 情景满分；null 约定 0 |
| standardized | 0.7732 | 最强非 Oracle |
| local_raw / cDLED / CGOMEA | 0.7698 | 三者在该数据上等价 |
| context_pooled | 0.6908 | |
| **TCAIL q** | **0.6736** | |
| TCAIL w | 0.6731 | |
| FBL abs | 0.6616 | adaptation |
| random | 0.5721 | |
| FBL signed | 0.5516 | 大量领域违规 |

`additive_null` 在严格 null 下没有 `|Δ|>δ` 的正例，sklearn 的 `average_precision_score` 对全负样本返回 0；因此五情景 macro 的有效上限是 0.8 而不是 1.0。这是本轮指标的已知设计缺陷，已标 OPEN。

## 5. 次要指标

### 5.1 Null calibration

训练 null 的 95th percentile 阈值（`q=0.498`）下，held-out additive/null 的 false-link rate：

| 方法 | Rate |
|---|---:|
| TCAIL q | **0.0375** |
| TCAIL w | 0.0396 |
| standardized | 0.0583 |
| local_raw / cDLED / CGOMEA | 0.0750 |
| context_pooled | 0.0958 |
| FBL abs | 0.0000 |
| random | 0.0583 |
| oracle | 0.0000 |

TCAIL 的 null 控制合格（≤0.05）；这不是它失败的原因。

### 5.2 校准

| Brier | ECE | calibration intercept | calibration slope |
|---:|---:|---:|---:|
| 0.2537 | 0.1789 | 0.137 | **0.130** |

Slope 0.13 表示 q 严重过度自信/分布失配；ECE 0.179 远高于可用校准水平。校准失败与 AUPRC 失败一致，不能把 q 当作可靠后验概率使用。

### 5.3 方向与 FOS

- parent sign-flip 中被选边的方向准确率：**0.647**。
- FOS recovery（held-out seed × parent × module 平均）：

| 方法 | Precision | Recall | F1 | False merge | VI |
|---|---:|---:|---:|---:|---:|
| cDLED / CGOMEA / local_raw | 0.757 | 0.752 | 0.738 | 0.103 | 0.132 |
| standardized | 0.772 | 0.727 | 0.729 | 0.066 | 0.129 |
| oracle | 0.657 | 0.800 | 0.704 | 0.280 | 0.160 |
| context_pooled | 0.447 | 0.435 | 0.422 | 0.099 | 0.502 |
| **TCAIL q** | **0.428** | **0.375** | **0.373** | 0.068 | 0.543 |
| TCAIL w | 0.392 | 0.358 | 0.351 | 0.070 | 0.567 |
| random | 0.189 | 0.055 | 0.080 | 0.033 | 0.909 |

TCAIL 的 FOS recovery 明显低于简单 contrast；即使只看 precision，也未达到强基线水平。

### 5.4 拟合质量与 abstention

| 模型 | fit_ok | PPC extreme rate | 平均秒/拟合 |
|---|---:|---:|---:|
| M2 | 0.935 | 0.005 | 17.05 |
| M3 | 0.925 | 0.000 | 16.60 |

- 56/800 次拟合失败，全部为 `GRADIENT_TOLERANCE`；失败集中在 seed%4=2/3（32/128 blocks），其中 128-block 条件失败率更高。
- TCAIL abstention：additive_null 12.7%、sparse 15.0%、sign-flip 20.8%、higher-order 20.4%、drift 0%。
- 按 `n_block`（complete blocks，最多 512）：≤32 行 0–2.3%；64 行 4.6%；128 行 9.2%；512 行 **52.9%**。
- 因此 TCAIL 在高支持条件下并没有“利用更多数据”，反而大量弃权；这是实现/优化器层面的明确缺陷。

### 5.5 Prior sensitivity（validation-only）

在 validation seeds 40–42 上，把固定效应先验尺度乘以 0.5/2.0：

| Prior scale | q Spearman | mean abs q change | selection agreement |
|---:|---:|---:|---:|
| 0.5 | 0.983 | 0.045 | 1.000 |
| 2.0 | 0.986 | 0.081 | 0.983 |

排序对先验较稳健；这不改变 Gate 失败结论。

## 6. 失败机制（EXPLORATORY / POST HOC）

以下分析在 Gate 解盲后计算，只能用于解释失败，不能用于宣称通过。

1. **Conservative min 规则放大了 M2 的模型误配。** 在 parent sign-flip 和 higher-order 情景，真值依赖三阶结构；M2 无法表示，`min(q_M2,q_M3)` 把 M3 的正确信号压掉。
2. **即使只用 M3，仍然输给 standardized。** q_M3 相对 standardized 的配对差为 **−0.0322**，95% CI **[−0.0496, −0.0168]**；q_max 为 −0.0305 [−0.0481, −0.0147]。因此失败不只是 merge 规则。
3. **支持量分层（post hoc）显示 TCAIL 未从更多 blocks 获益。** macro-AUPRC：≤32 行 0.883 vs 0.930；33–128 行 0.835 vs 0.989；>128 行 0.696 vs 0.999。该分层未按 seed 配对，只作描述。
4. **直接 per-parent 四格 contrast 与真值定义高度同构。** 真值本身就是每个 parent context 下的概率尺度 contrast；一个设计良好的直接估计器几乎是最优匹配，层次模型必须证明其 pooling/不确定性带来额外价值，而本轮没有。

## 7. 解释边界

- **NO-GO 的范围：** 本实现（Bernoulli task/block M2/M3 + conservative min + Laplace）在该合成任务族、该支持分布、该 δ 下不优于 standardized contrast。不能外推为“所有 Bayesian interaction 方法无效”。
- **不是 EC 结论：** 由于 Estimator Gate 失败，按协议没有运行 GOM，因此没有 TCAIL-FOS 的搜索收益证据；也不能用 FOS recovery 或 AUPRC 代替 EC 收益。
- **基线不完整：** cDLED/CGOMEA 是 static adaptation；SLL-MI、FBL incremental、DLED、LMM、ALI/AIM、GAwLL2 未运行。
- **生成器限制：** 每个 seed 只拟合一个 4 变量局部模块；跨 seed 覆盖 10 模块，但不是同时联合 40 变量全图。效应强度只有一档（medium ±15% jitter），没有多档强弱。
- **模型误配：** drift 情景含 random slopes/overdispersion/task drift，估计器只有随机截距；该情景 TCAIL 的“胜利”必须解释为在误配下相对更稳健，而不是模型正确。
- **拟合缺陷：** 6.5–7.5% 拟合因绝对梯度阈值失败；高支持条件弃权率高。即使 Gate 通过，也必须先修这个问题。
- **指标缺陷：** additive_null 无正例，AUPRC 约定 0，使五情景 macro 上限为 0.8；null 的区分信息只体现在 false-link rate，而不是 AUPRC。

## 8. 停止规则执行

| 规则 | 执行 |
|---|---|
| TCAIL 不优于 strongest baseline | 触发：停止 estimator 优越性主张 |
| 仅部分情景获益 | 触发：只有 low_support_drift 获益；不得写普遍优越 |
| AUPRC 提升但 GOM 不提升 | 不适用：AUPRC 未提升 |
| 低支持不可靠 | TCAIL 在低支持/漂移下表现较好，但整体失败；不能选择性宣称 |
| 基线不公平/泄漏 | 未发现；held-out seeds 3000–3039 未参与开发 |

## 9. 复现与核验

- `results/summary.json`：Gate 与次要指标；
- `results/stage_summary.json`：方法级 overall/scenario AUPRC；
- `results/held_out_macro_*.csv`：per-seed 指标；
- `results/held_out_evaluation_raw.csv`：per-pair 评分与真值；
- `results/raw/`：原始观测、pair truth、fixed/task/block 参数；
- `independent_recompute.py` 输出 `results/independent_recompute.json`：从 per-seed CSV 独立重算的配对差与 CI 与 summary 一致（差异 <1e-14）；
- `results/prior_sensitivity/`：validation-only 先验敏感性；
- `results/posthoc_diagnostics.json`：解盲后失败机制诊断；
- `results/report_tables.md`：本报告表格的生成结果。

## 10. OPEN

1. 是否能用相对梯度准则/更强优化器消除 128-block 拟合失败，并重新预注册独立 held-out（不得复用 3000–3039 作确认性 test）。
2. additive_null 的 AUPRC 约定是否需要改为“有 practical positive 的弱交互”或从 macro 中排除。
3. 是否需要 random slopes/overdispersion 才能公平处理 drift 情景。
4. 是否应在多档效应强度、缺失率和联合 40 变量全图上重复。
5. 缺失的强基线（SLL-MI、FBL incremental、DLED、LMM、ALI/AIM、GAwLL2）尚未运行。
6. Conservative min 与 M3-only 的取舍必须在下一轮预注册，不能根据本轮 test 结果选择。
7. Downstream GOM Gate 仍未运行；任何 EC 收益主张都未成立。
