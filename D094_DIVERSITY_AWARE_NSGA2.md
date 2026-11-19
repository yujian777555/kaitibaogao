# D-094 Diversity-Aware NSGA-II（B4）算法规格与合成证据

状态：`IMPLEMENTED / UNIT_TESTED / SYNTHETIC_VALIDATED`；`INDEPENDENT_REVIEWED=NO`、`APPROVED_FOR_EXPERIMENT=NO`、`EXPERIMENT_COMPLETED=NO`、`POSITIVE_SIGNAL=NO`。

## 1. 可证伪问题

假设：在不同 Genome 可能产生相同 Agent 行为时，同一 Pareto 层内加入真实行为新颖性和重复控制，可以提高 survivor 的行为覆盖率，同时不牺牲 Pareto 优势和硬约束。

以下任一结果均可推翻其研究价值：只增加不同但无效行为、破坏 Pareto/硬约束、提高多样性却不改善性能或搜索效率、或增加 API 成本而没有对应收益。

## 2. 行为表征

`d094_behavior.py` 从公开事件构造：

- 规范化决策序列：动作类型、工具名、工具参数；
- 工具结果/拒绝、成功、终止和公开 observation；
- 若存在，before/after 公开状态转换；
- 终止状态与任务完成状态。

排除 rationale、模型/request ID、Token、延迟和其他非行为元数据。禁止 hidden outcome、标签、evaluator 内部数据和 Test 信息。`canonical_sha256` 对 sequence/features/terminal/state-transitions 的 canonical JSON 计算 SHA-256。

Genome Diversity 是基因差异；Phenotype Diversity 是上述实际行为差异；Performance Diversity 是目标向量差异。三者分别记录。

## 3. 两种冻结距离

### A. 规范化动作序列编辑距离

对行为序列 \(A=(a_1,\ldots,a_m)\)、\(B=(b_1,\ldots,b_n)\)：

\[
d_{edit}(A,B)=\frac{\operatorname{Levenshtein}(A,B)}{\max(m,n)}
\]

两个空序列距离为0。序列元素为 canonical 动作/结果字符串，而不是自然语言说明。

### B. 加权行为特征距离

\[
d_{feature}(A,B)=\frac{\sum_f w_f\min(1,|A_f-B_f|/s_f)}{\sum_f w_f}
\]

| 特征 | 权重 \(w_f\) | 尺度 \(s_f\) |
|---|---:|---:|
| tool_call_count | 2 | 8 |
| verification_count | 1 | 4 |
| recovery_count | 2 | 4 |
| failed_call_count | 2 | 8 |
| rejected_call_count | 1 | 8 |
| retry_count | 2 | 8 |
| completed | 1 | 1 |
| runtime_abort | 1 | 1 |
| state_transition_count | 1 | 16 |

权重和为13。所有参数在 R3 前冻结，不根据 R3 结果调整。

## 4. 行为新颖性与选择器

候选 \(c\) 在同一 front \(F\) 的行为新颖性为最近其他候选距离：

\[
N(c,F)=\min_{c'\in F,c'\ne c}d(c,c')
\]

单例和完全重复行为的新颖性为0。没有行为向量时只允许用 phenotype hash 做相同/不同控制，不把 hash 当作连续距离。

目标 crowding 归一化：边界 `inf` 映射为1；其余除以本 front 最大有限 crowding，若最大值为0则全部为0。

### A. Crowding + Novelty（完整 B4）

\[
S(c)=0.5\,\widetilde{CD}(c)+0.5\,N(c)
\]

### B. Pareto + Behavior Tie-break

先比较 Pareto rank 和 crowding，仅在并列时比较行为新颖性，再按 genome hash 稳定排序。

### C. 行为聚类

使用编辑距离阈值0.25形成确定性的连通行为簇，每簇先保留 crowding/新颖性最高者。阈值是预注册合成参数，不根据真实结果调节。

### 对照

- Standard NSGA-II；
- Genome-Diversity：0.5 crowding + 0.5 六基因最近邻 Hamming 距离；
- Phenotype-Diversity：仅行为新颖性+重复控制；
- Full Diversity-Aware：上述完整 \(S\) +重复控制。

## 5. 生存者选择伪代码

```text
输入 candidates、size、distance
1. 按 genome hash 去重；feasible 与 infeasible 分开。
2. feasible 执行标准非支配排序，硬约束/执行错误不可被新颖性抵消。
3. 完整 front 直接保留。
4. 对溢出 front 计算 crowding 与行为距离。
5. 按所选方法评分，先每个唯一 phenotype 最多保留一个代表。
6. 若仍需填充，再按分数与 genome hash 处理剩余候选。
7. 仅在生存者数量不足时按违规数/hash填充 infeasible；其不得成为正式可行候选。
8. 保存每个 survivor 的 genome、phenotype、objectives 和三种多样性。
```

因此行为多样性不能越过更高优先级 Pareto front，也不能使违规候选变成可行候选。

## 6. 合成结果

产物：`experiments/d094_llm_agent/results/r3_synthetic/`。

### 专用选择器 fixture

| 选择器 | 唯一 Genome | 唯一 Phenotype | 平均行为距离 | 唯一目标向量 |
|---|---:|---:|---:|---:|
| Standard | 2 | 1 | 0.0 | 1 |
| Genome-Diversity | 2 | 2 | 1.0 | 1 |
| Phenotype-Diversity | 2 | 2 | 1.0 | 1 |
| Full B4 | 2 | 2 | 1.0 | 1 |

该 fixture 证明重复控制能够移除行为重复，且未改变目标向量。它不证明真实任务性能提升。

### 演化 fixture

| 臂 | 评价数 | 重复 proposal | 最后一代 phenotype diversity |
|---|---:|---:|---:|
| Standard | 8 | 1 | 0.75 |
| Genome | 8 | 1 | 0.75 |
| Phenotype | 8 | 1 | 0.75 |
| Feedback | 8 | 1 | 0.50 |
| Diversity/B4 | 8 | 1 | 0.75 |
| Combined/B5 | 8 | 1 | 0.50 |

此 fixture 中 B4 没有超过标准 NSGA-II，搜索评价数也没有减少。B5 的反馈轨迹导致较低的0.5，但不能据此作真实性能因果结论。**当前没有搜索效率或真实性能提升信号。**

## 7. 边界

Phenotype 只有在真实评价完成后才可使用，因此 B4 不能免费减少初始评价成本。任何“减少无效评价”的说法必须由 R3 的真实候选/预算账本验证。R3 真实实验未运行，不将本规格或合成结果当作创新成立。
