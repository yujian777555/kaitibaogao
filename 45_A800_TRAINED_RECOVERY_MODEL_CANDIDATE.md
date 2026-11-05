# 45 — A800 训练候选：ARWM

**状态：HOLD / NOT IMPLEMENTED / NOT VALIDATED**

## 目标

主 LLM 继续通过 DeepSeek API 使用，不训练或替换主模型。A800 训练 Agent 内部辅助模型 ARWM（Agent Recovery World Model），预测工具动作后的结构化 effect-state、后置条件满足情况、副作用风险、恢复成功概率及不确定性。

训练数据必须来自模拟器的真实执行轨迹，以及同一可观察状态下分叉执行多个恢复动作得到的配对反事实结果。禁止由 LLM 编造反事实标签。

## 与现有工作的边界

CoMAP (EMNLP 2026) 已实现 textual world model 与 Agent policy 闭环共演化；HarnessMDP 已学习冻结 LLM 的外部控制器；TRACE/SENTINEL 已覆盖失败驱动训练；EvoTool 已覆盖工具策略的 blame-aware 变异。因此，ARWM 不能以“训练世界模型”“失败驱动训练”或“模型辅助 Agent”作为创新主张。

候选差异：针对有状态副作用工具，训练 action-conditioned 多任务预测器，联合预测 effect-state transition、postcondition 和 invariant risk；以校准风险上界与 OOD abstention 辅助 EC 搜索结构化恢复控制器；通过相同真实 rollout 预算的对照证明实际搜索收益。该差异仍需更完整文献审查和实验验证。

## 模型与训练

候选模型按复杂度比较：
1. LightGBM / MLP（结构化强基线）；
2. 小型 Transformer；
3. 1.5B–4B 开源模型 LoRA（只有结构化模型不足时才考虑）。

多任务损失包括状态转移、违规风险、后置条件、恢复结果和校准。A800 训练不是目标本身；若 LightGBM/MLP 更好，就不保留大模型。

## 与 EC 的结合

EC 对 guarded finite-state recovery controller 进行种群搜索、变异、重组、契约修复和生存者选择。ARWM 只负责低成本候选筛选与风险估计。最终 fitness 和硬安全门禁必须来自真实 simulator rollout。高不确定性/OOD 候选应 abstain 或转真实评估；模型预测不得单独接受 incumbent。

## 必须比较

- 无模型 GA/GP、NSGA-II/III；
- 单输出成功率 surrogate + EA；
- 多任务预测模型但无配对反事实训练；
- ARWM + 配对反事实训练；
- ARWM + 风险不确定性门控；
- CoMAP-style world-model loop；
- HarnessMDP-style offline controller（可公平复现时）。

## Gate

M1：ARWM 在 held-out tool/fault families 上优于 LightGBM/MLP 或提供独立的风险校准增益。失败则停止大模型训练。

M2：同真实 rollout 预算下，ARWM 辅助 EA 优于无模型 EA；增益不能来自额外调用、训练数据或更大种群。失败则不称为算法创新。

M3：固定 API 主 LLM，在未见任务/故障族上验证策略递归更新，并检查正常任务能力退化。

当前 Pilot A 首轮显示 state-aware 手工规则已达到 oracle 的成功/安全指标，因此必须先通过 Pilot A-2 证明存在策略改进空间。未通过前，不训练 ARWM、不启动正式 EA。
