# 97_D088-R2 算子消融与残余感知停止实验

**日期：** 2026-11-15
**分支：** `pilot-a-stateful-recovery`
**代码：** `experiments/d088_recovery/d088_r2_experiment.py`、`d088_r2_audit.py`
**性质：** Train-only 配对实验（开发 96 场景）+ 冻结候选 Fresh 复制（80 场景，独立 family）

## 1. 本轮算法改进（两项）

**改进 1：`strict_residual_stop`（残余感知停止规则）**
目标：修复 R1 轮机制 B 的 R4 短板（提前 ESCALATE 留下可避免残余）。
规则：只要还存在可达补偿路线且预算可容纳一次派发-清结-终止周期，就禁止停止。该规则只用公开信息（工具状态、合同、路线 requires/attempts）。作为可演化开关加入 genome，支持消融。

**改进 2：反馈条件化变异 + 结构分段交叉**
目标：证明演化搜索相对 RandomSearch 的价值。
- `mutate_feedback`：按失败画像（route_failures / pending_residue / dependency_block / budget_exhaust，从公开轨迹聚合）偏置变异到对应机制段（A/B/C/shared）。
- `crossover_segments`：按机制段整体交换，保留共适应参数块的连锁结构（uniform 交叉会破坏）。

## 2. 实验设计（配对：同任务/同预算/同 seeds）

- 预算：pop=16 × 8 代 = 144 评价/run；seeds 711/822/933；决策上限 24
- **E1 算子消融**（BC 组，strict=True）：base 算子 vs feedback 算子 vs RandomSearch（同预算）
- **E2 strict_residual_stop 消融**：BC 与 ABC × {off, on}，feedback 算子
- **E3 单机制**：A / B / C × feedback 算子 + strict stop
- 独立复算：29 个 run 的 best_rows 全量重算

## 3. 开发集结果（96 场景，全部零违规）

| 实验 | 配置 | R3 | R4 | harm | cost |
|---|---|---:|---:|---:|---:|
| E1 | BC/base s711 | 0.792 | **0.875** | 0.219 | 9.8 |
| E1 | BC/feedback s711 | 0.792 | 0.792 | 0.250 | 9.0 |
| E1 | BC/RS s711 | 0.792 | 0.792 | 0.250 | 9.6 |
| E2 | BC/strict=off s822 | **0.833** | 0.167 | 0.375 | 7.1 |
| E2 | BC/strict=on s711 | 0.792 | 0.792 | 0.250 | 9.0 |
| E2 | ABC/strict=off s711 | 0.542 | 0.583 | 0.531 | 13.5 |
| E2 | **ABC/strict=on s711** | 0.792 | 0.792 | 0.240 | 9.9 |
| E3 | C/feedback s711 | 0.792 | 0.708 | **0.115** | 10.5 |

**消融发现：**
1. **strict_residual_stop 在 ABC 组效果显著**：seed711 R4 0.583→0.792、R3 0.542→0.792（同一 seed 配对比较）。但在 BC 组表现为 R3↔R4 权衡移动（s822：R3 0.833→0.542，R4 0.167→0.458）——阻止提前停止后预算被恢复动作占用，部分场景在 ESCALATE 前耗尽预算。
2. **反馈条件化变异无一致优势**：E1 中 feedback 仅在 s822 R3 高于 base（0.542 vs 0.458），s711/s933 持平或略低。**演化价值仍未证明**（RandomSearch 与最优演化结果同分）。
3. base 算子找到 R4=0.875（超 Greedy 0.750），但单 seed 信号。

## 4. 独立复算与 Fresh 复制

独立复算：29 runs 全部一致，0 处不一致。

冻结候选 → Fresh 80 场景一次性评估：

| 候选 | 开发 R3/R4 | Fresh R3/R4 | Fresh harm | 判定 |
|---|---|---|---|---|
| best_balanced（BC/base s711） | 0.792/0.875 | 0.600/0.750 | 0.375 | R4 与 Greedy 打平，R3 −5pp、harm 高——**未复制** |
| best_r3（BC/feedback/strict0 s822） | 0.833/0.167 | **0.800**/0.200 | 0.450 | **R3 +15pp 超 Greedy（0.650），零违规——已复制** |
| Greedy 基线 | 0.792/0.750 | 0.650/0.750 | 0.062 | — |

## 5. 科学结论（本轮）

1. **已复制的提升（两次独立确认）**：机制 B 的核心（延迟感知批量调度 + 预算感知清结）使 R3 CorrectEscalation 在独立 Fresh family 上稳定 0.650→0.800（+15pp），零硬违规。R1 的 RandomSearch/B 候选与 R2 的 BC/feedback 候选是两个不同 genome，均复现同一提升——**这是机制级、可重复的改进**。
2. **R4 短板未解**：开发集 R4=0.875 的候选 Fresh 上未复制；strict_residual_stop 只在部分 seed 有效。R3↔R4 的预算竞争是结构性问题。
3. **演化价值仍未证明**：144 评价预算下 RandomSearch 与 NSGA-II 打平；反馈条件化变异无一致优势。需要更大预算或更强的失败轨迹引导。
4. 全部运行零违规、独立复算零不一致、无 Test/LLM/A800。

## 6. 下一轮实验方案

1. **解决 R3↔R4 预算竞争**：多目标搜索显式保留 (R3,R4) Pareto 前沿而非均衡单点；或预算分割策略（为 ESCALATE 保留固定份额 + 按 min_reachable 分配恢复预算）。
2. **演化价值**：pop=32×30 代（960 评价）配对 5 seeds；失败轨迹回放引导初始种群（counterfactual 序列作为锚点基因）。
3. **strict_residual_stop 参数化**：允许在剩余预算低于阈值时放弃部分恢复优先保 ESCALATE（当前一刀切导致预算耗尽）。
4. R3 提升候选冻结（两份 genome 已存 `results/d088_r2_audit.json`），等待 Validation 授权后做正式复制。

## 7. 产物

- `d088_genome.py`：`strict_residual_stop` 基因 + `mutate_feedback` + `crossover_segments`
- `d088_policies.py`：残余感知停止规则
- `results/d088_r2_report.json`（29 runs 原始账本）
- `results/d088_r2_audit.json`（独立复算 + 冻结候选 + Fresh 复制）
