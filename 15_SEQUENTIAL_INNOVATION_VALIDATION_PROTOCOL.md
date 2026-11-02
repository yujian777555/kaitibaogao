# 15 — 三个创新点的逐项验证协议（Sequential Innovation Validation Protocol）

**日期：** 2026-11-02  
**状态：** RESEARCH EXECUTION POLICY / ACTIVE  
**唯一研究仓库：** yujian777555/kaitibaogao

> 本文件是当前研究执行顺序的权威文件。若早期计划、旧 handoff 或旧任务清单与本文件冲突，以本文件为准。

## 0. 总决策：先验证，后写作

用户明确决定：**暂不撰写硕士大论文正文，不先包装三个创新点；必须逐项验证每个创新点。**

执行原则：
1. 先证明研究问题存在，再证明算法机制有效，最后证明真实 Agent 场景有价值。
2. 每个创新点必须独立通过自己的证据门槛，不能用后一个算法的结果替前一个算法背书。
3. 不允许因为毕业论文希望有三个创新点，就降低 NO-GO 标准。
4. 不预先承诺三篇论文。目标是最多三篇独立小论文；最终可为两篇，也可为三篇，取决于证据。
5. 在创新点一未通过之前，不启动创新点二的完整实现；创新点二未通过之前，不启动创新点三的完整研究。
6. 允许提前做必要的文献审计和实验协议设计，但不能并行扩展多个未经验证的算法。
7. 所有实验必须有固定预算、强基线、预先确定的主要指标、独立测试任务和可复现记录。
8. 合成环境通过只是必要条件，不是论文成立的充分条件；必须进一步在真实或可信的 Agent 任务上验证。

当前状态：
- 创新点一 TCAIL：HOLD / SPECIFIED, NOT IMPLEMENTED OR VALIDATED；
- 创新点二 CI-GOM：HOLD / SPECIFIED, FROZEN UNTIL GATE-1；
- 创新点三跨任务迁移：CONDITIONAL CANDIDATE, FROZEN UNTIL GATE-2；
- 硕士论文正文：NOT STARTED BY DESIGN；
- 开题报告正式撰写：等研究证据与候选方向稳定后再组织，不得把假设写成实验结论。

---

# 1. 创新点一：TCAIL 验证

## 1.1 研究主张

TCAIL（Task-Conditioned Active Interaction Learning）拟解决：

> 在 Agent 模块组合空间中，评价存在随机噪声、任务上下文会改变模块交互、合法配置受接口/权限/依赖约束且评价预算有限时，能否通过任务条件化稀疏交互估计、可识别性门禁和交互后验信息增益采样，更可靠、更省预算地识别有实际意义的模块交互？

不得将其简化成“组件消融 + 两两差分”。需要证明 TCAIL 的整体机制优于强统计/实验设计基线。

## 1.2 阶段顺序

### T1-A：实现前规格审查
逐项检查 14_FORMAL_ALGORITHM_DESIGN_V1.md：
- 类别效应编码与多类别扩展是否定义完整；
- Group-ARD 更新和后验协方差是否数值稳定；
- acquisition 是否确实只衡量 interaction information，而不是误混 fitness exploitation；
- 受约束合法空间中的 estimability / identifiability gate 是否正确；
- 对 Bernoulli 与 bounded continuous reward 的噪声模型是否匹配；
- 置信区间、任务块独立性、后验校准和多重比较是否有正确统计解释；
- 对三阶或更高阶模型失配能否诊断并 abstain；
- 所有训练、验证、测试任务边界是否清晰。

发现公式、假设或统计错误，先修规格，不进入算法性能实验。

### T1-B：已知真值合成实验
固定 4 个二元槽位、16 个配置，生成至少以下 landscape：
1. 无交互 null；
2. 单一正交互；
3. 单一负交互；
4. 稀疏多 pair interaction；
5. task-family sign flip / task-conditioned interaction；
6. 具有三阶项的 pairwise model misspecification；
7. 全合法配置空间；
8. 部分组合不合法、某些 pair contrast 不可识别的受约束空间。

噪声：
- Bernoulli success；
- bounded continuous Beta reward；
- 至少两个噪声强度。

必须使用多随机种子、多独立 landscape 实例；不能只展示单次有利结果。

### T1-C：强基线
同预算比较：
- full factorial（仅作小空间 oracle / 上界）；
- random legal design；
- fractional factorial / D-optimal design；
- main-effects regression；
- pairwise OLS；
- sparse pairwise regression with fixed design；
- Group-ARD with fixed/random design；
- TCAIL active interaction-only IG；
- 与任务相近且可公平复现的已有 Agent interaction / harness baseline（在文献审计后确定）。

所有方法共享同一总 rollout / evaluation budget；基线获得公平的训练调参预算。

### T1-D：主要指标
预先指定主要指标，不能实验后挑选：
- interaction contrast RMSE；
- edge AUPRC（稀疏边发现优先报告 AUPRC）；
- edge precision/recall/F1；
- positive/negative direction accuracy；
- posterior interval coverage / calibration；
- held-out configuration-task prediction error；
- 达到目标 edge recovery 的 rollout 数与 budget-performance curve；
- 在受约束空间中的 false-edge rate 与 NOT_IDENTIFIABLE 判定准确性。

同时报告计算开销和 wall-clock，不得只报告最有利指标。

### T1-E：机制消融
至少比较：
- 去掉 task conditioning；
- 去掉 Group-ARD / 改为普通 pairwise regression；
- active IG 改为 random / fixed D-optimal design；
- 去掉 identifiability gate；
- 去掉 posterior calibration / abstention。

消融要回答每个机制是否提供独立增益，不接受“整套算法赢了”但无法解释来源。

### T1-F：真实 Agent 场景验证
只有 T1-B 至 T1-E 通过后才启动。
- 选择可审计、可复现、允许替换 Agent 模块的任务环境；
- 明确基因槽位、模块候选、contract、任务划分和 rollout 随机性；
- 训练/验证/测试按任务实例或任务家族隔离；
- 不使用测试结果调阈值、选择交互边或调整模型；
- 比较 TCAIL 与最强统计/实验设计基线；
- 证明合成真值上的优势没有在真实 Agent 场景消失。

## 1.3 Gate-1 通过条件

只有同时满足以下条件才标记 GATE-1 PASS：
1. 实现通过单元测试、数值测试和独立代码审查；
2. 真值实验能恢复正交互、负交互和任务条件交互；
3. null 场景控制假阳性；受约束场景能正确 abstain；
4. 后验区间校准达到预先规定的可接受水平；
5. 在相同预算下，TCAIL 对预注册主要指标相对最强公平基线呈现可重复优势；
6. 优势在独立 seeds / landscape / task splits 上成立，不依赖单一场景；
7. 真实 Agent 验证至少显示结构识别或预算效率的实际价值；
8. 结果可复现，代码、配置、原始结果和分析脚本齐全。

阈值需在看测试集结果前依据 pilot / null simulation 锁定。不得在本文件中事后编造一个“看起来好”的百分比门槛。

## 1.4 Gate-1 停止规则
- 若 TCAIL 不优于 D-optimal / sparse fixed-design：NO-GO 或缩小主张，不继续包装。
- 若只在已知真值合成环境有效、真实 Agent 无效：HOLD，不作为已验证论文贡献。
- 若 identifiability gate 频繁 abstain，且关键交互无法识别：重新评估问题设定。
- 若 posterior calibration 失败：先修统计模型，不能直接进入 CI-GOM。
- 只有完整 Gate-1 通过，才进入创新点二的完整算法实现。

---

# 2. 创新点二：CI-GOM 验证

## 2.1 研究主张

CI-GOM（Contract-aware Interaction-guided Gene-pool Optimal Mixing）拟解决：

> 在 Agent 配置为离散模块、模块之间存在非加性交互和硬接口/依赖约束、rollout 结果有随机噪声时，如何改进 linkage-based mixing、最小合法修复、donor selection 和 offspring acceptance，使同预算搜索更有效且不破坏 Agent contract？

CI-GOM 不得被描述为“把 TCAIL 图接到 GOMEA”。必须证明 Agent-specific mechanisms 解决了具体失效问题。

## 2.2 阶段顺序

### T2-A：Oracle linkage 上界实验
先不使用 TCAIL 的估计图，使用已知真值交互图：
- standard GOM / GOMEA；
- random linkage；
- conventional linkage learning（适用时）；
- Agent-specific crossover / mutation；
- CI-GOM with oracle linkage。

目的：判断交互 FOS 在 Agent 模块配置上是否有潜在优化价值。

若 Oracle linkage 都不优于强基线，停止 CI-GOM 主线，不得归咎于 TCAIL。

### T2-B：Contract-aware repair 单独验证
测试：
- 非法 offspring rate；
- repair success rate；
- repair distance；
- 修改是否严格限制在依赖闭包；
- 确定性与可复现性；
- 是否引入语义/权限错误；
- repair 超限是否正确拒绝。

对照简单 rejection、随机修复和不受限修复（只用于诊断，不能作为可部署方法）。

### T2-C：Donor 与接受机制
分别比较：
- uniform feasible donor；
- posterior-aware donor；
- noisy single-shot acceptance；
- paired sequential acceptance；
- 去掉 uncertainty penalty；
- 去掉 repair cost penalty。

报告有效 offspring、接受率、误接受率、任务级收益和额外评价成本。

### T2-D：完整同预算搜索
对比：
- standard GOM/GOMEA；
- random-linkage GOM；
- oracle-linkage CI-GOM；
- learned-linkage CI-GOM（仅使用已通过 Gate-1 的 TCAIL）；
- Agent crossover / mutation baselines。

报告：
- best/mean task success；
- anytime performance；
- rollout-equivalent budget；
- valid offspring rate；
- repair statistics；
- false acceptance / unresolved rate；
- population diversity；
- token、wall-clock 和实际评价成本。

### T2-E：参数调节验证
离线 irace 只在训练任务调节有限参数；所有 baseline 也要获得公平的调参预算。
比较：
A. default fixed；
B. irace-tuned fixed；
C. default + online discounted-UCB；
D. irace + online discounted-UCB。

若 D 不优于 B，删除在线 AOS/UCB，不把它写成创新。统计显著性、硬约束和安全阈值不得由测试集调节。

## 2.3 Gate-2 通过条件

1. Oracle linkage 相对强基线有可重复的同预算收益；
2. contract repair 可证明合法、确定、局部且可审计；
3. donor / sequential acceptance 的增益经独立消融验证；
4. learned linkage 接近 oracle linkage 的收益，或至少在目标任务上有统计与实际意义；
5. 完整 CI-GOM 在独立 Agent 任务与 seeds 上优于公平调参的强基线；
6. 增益不是通过额外 rollout、额外模型调用或放宽硬约束换取；
7. 所有失败、修复、拒绝和成本均完整记录。

若 oracle 有效但 learned graph 无效，回到 TCAIL 修正；不能宣称 CI-GOM 已经端到端成立。

---

# 3. 创新点三：跨任务交互结构迁移与自适应演化（条件性）

## 3.1 研究主张

只在 Gate-1 和 Gate-2 通过后启动。核心问题：

> 已学习的 Agent 模块交互结构在不同任务之间有多少可迁移性？如何识别可共享结构、任务特异结构和潜在负迁移，并利用演化机制进行选择性迁移与目标任务适应？

这不是简单把旧交互图复制到新任务，也不是泛化的 transfer learning。

## 3.2 必须先证明迁移问题存在
- 不同任务家族之间存在稳定共享的部分交互；
- 同时存在任务特异或符号变化的交互；
- 从头学习在目标任务预算下有明显成本或性能限制；
- 直接迁移可能发生负迁移，因而需要选择性迁移机制。

若任务间交互没有可复用结构，第三创新点的基本前提不成立。

## 3.3 对照与实验
- target task from-scratch TCAIL / CI-GOM；
- direct graph transfer（无筛选）；
- shared/global graph；
- conventional transfer / warm-start；
- selective transfer + adaptation（候选方法）。

指标：
- target task learning curve；
- 达到相同性能所需 rollout；
- transfer gain；
- negative transfer frequency / magnitude；
- transferred-edge precision；
- 适应任务变化所需时间与成本。

源任务与目标任务必须严格隔离；测试任务不得参与迁移决策或超参数调节。

## 3.4 Gate-3 通过条件
- 真实任务中确认存在可迁移的交互结构；
- 选择性迁移优于从头学习和直接迁移；
- 能检测并抑制负迁移；
- 收益跨任务划分和随机种子稳定；
- 有独立机制消融与同预算比较。

若 Gate-3 未通过，删除第三创新点。毕业论文采用两个已验证创新点，不为满足数量强行添加第三项。

---

# 4. 统一实验治理

每个 Gate 都必须：
1. 冻结 protocol、primary endpoint、budget、seeds、task split 和分析脚本；
2. 训练/验证/测试严格隔离；
3. 所有算法公平使用相同评价预算和调参资源；
4. 区分 rollout 数、token 数、wall-clock 和货币成本；
5. 对失败结果如实登记，不删除不利 seeds；
6. 保存原始数据、配置、代码版本、环境和 hash；
7. 由独立复审检查实现、统计与数据泄漏；
8. 在 Gate review 后作 GO / HOLD / NO-GO 决策。

禁止：
- 只在一个 toy landscape 上报告提升；
- 只与弱随机基线比较；
- 先看 test 再改阈值；
- 把工程可运行等同于算法有效；
- 把多个成熟组件拼装自动称为创新；
- 在 TCAIL 未通过前并行开发完整 CI-GOM；
- 在 CI-GOM 未通过前并行启动跨任务迁移；
- 先写大论文，再用零散实验补故事。

---

# 5. 当前执行清单

**当前只执行创新点一 TCAIL。**

下一步任务：
1. 独立复核 14_FORMAL_ALGORITHM_DESIGN_V1.md 中 TCAIL 的数学与统计假设；
2. 建立最小代码结构和可复现环境；
3. 实现 landscape generator 和真值 oracle；
4. 实现 random / D-optimal / main-effects / pairwise OLS / sparse Group-ARD / TCAIL；
5. 完成 unit tests、null test、positive/negative interaction、task sign-flip、misspecification 和 constrained-identifiability tests；
6. 再做多 seed 同预算实验和统计分析；
7. Gate-1 review 前不实现完整 CI-GOM，不启动第三项；
8. 不调用真实 LLM，直到合成实验通过且真实 Agent protocol 已审查；
9. 每轮只维护本仓库，并更新 status、decision log、实验记录和接班提示词。

**当前阶段状态：** TCAIL_SPECIFICATION_REVIEW_PENDING  
**下一项可交付成果：** TCAIL 规格审计报告 + Phase 0 实现与测试，不是毕业论文正文。
