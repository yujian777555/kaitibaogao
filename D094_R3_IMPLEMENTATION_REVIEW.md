# D-094 R3 实现审查材料（自检，不是独立审查）

## 1. 审查意图

本轮实现 B4 行为感知选择、B3 失败反馈算子、B5 组合及请求前预算预留，并形成可复核的 R3 预注册；没有启动真实 R3 实验。

## 2. 实现与源码身份

| 文件 | SHA-256 | 职责 |
|---|---|---|
| `d094_behavior.py` | `dc7e93dbe2ad74a144080cd006201427b52085fcd755bb5e9b4ecfc466facdc2` | 行为序列、特征、编辑/加权距离 |
| `d094_diversity.py` | `9f95459b64afcb349045f718faad46458a2e6190a7d8b3a1b9f0cd96598fc7d8` | 四种选择器、重复控制、行为聚类 |
| `d094_feedback_evolution.py` | `d75c39e8700f4d7d284ec0827faa9019726009e11624e5860c84dcf66ef29df7` | 失败分类、反馈矩阵、softmax与随机控制 |
| `d094_adaptive_evolution.py` | `fbc676b3975af0390839d3546b98fbec6c953dabd737da2a346658187169f596` | B2/B3/B4/B5演化与完整账本 |
| `d094_budget.py` | `697cc96c0bbabee291cbee0e878ab9d98498946dbf33ddf1f61afa39dfd4c3d6` | 请求前预留、池保护、结算 |
| `run_d094_synthetic.py` | `474637daae3d5004816253cb780e828044b4c6faad3e346974c5908dd48f5f22` | 可复现合成对照产物 |

## 3. 实际测试

D-094 全量：**82/82 OK**；Black 与 compileall 通过。新增测试覆盖：

- 行为 canonical 化、措辞不变性、两种距离已知答案；
- 标准/Genome/Phenotype/Full 选择器、Pareto/硬约束优先、零名额边界；
- 七类失败、分母、零反馈、动态方向、随机置换、数值参数；
- 请求前预留、final 池保护、失败/重试和实际 Token 结算；
- B3/B4/B5 的反馈/选择隔离、mutation locus、duplicate 和 survivor 账本；
- 可复现合成 CLI。

安全工具 bandit/gitleaks/semgrep/mypy/ruff 未安装，不能声称已运行。真实 API 单元测试继续使用 Mock；没有真实 R3 请求。

## 4. 合成结果与限制

专用选择器 fixture 中，Standard 唯一 phenotype=1，Full B4=2，平均行为距离0→1；这证明重复控制有效，不是性能证据。

演化 fixture 中 Standard/B4 的最后一代 phenotype diversity 都是0.75，B5=0.50；每臂均8次评价。没有证明 B4/B3/B5 提高搜索效率、Pareto 质量或真实任务成功率。

Phenotype 只能在候选完成评价后获得，因此不能宣称 B4 免费减少初始评价成本。真实 R3 的预算预检、任务覆盖、最终评价和独立复算仍未执行。

## 5. 与标准 NSGA-II 的区别

- B3：只将固定均匀算子控制替换为真实失败反馈概率；survivor 不变。
- B4：只在 Pareto 层内加入行为距离、唯一 phenotype 控制；反馈不变。
- B5：调用 B3 的概率与 B4 的选择，不增加参数。
- 三者均保持 Typed Genome、可行性优先和非支配排序。

## 6. 审查结论与所需复核

本文件是起草者自检，不能代替新独立会话的实现一致性复核。

**状态：READY_FOR_INDEPENDENT_REVIEW。**

`INDEPENDENT_REVIEWED=NO`；`APPROVED_FOR_EXPERIMENT=NO`；`EXPERIMENT_COMPLETED=NO`；`POSITIVE_SIGNAL=NO`。

下一独立会话必须检查公式/代码一致性、选择器边界、反馈分母与更新时点、重复评价、预算池隔离、R3规模可执行性以及原始账本可复算性。只有复核通过且用户明确批准后，才可运行真实 R3。
