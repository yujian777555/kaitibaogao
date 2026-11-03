# 开题报告 V0.2 文献核验与国内研究补充记录

**日期：** 2026-11-03  
**仓库：** yujian777555/kaitibaogao  
**对应报告：** 25_OPENING_REPORT_DRAFT_V0_2.md  
**本轮结论：** REPORT_REVISION_COMPLETE / BIBLIOGRAPHY_AUDIT_PARTIAL

## 1. 本轮审查范围

本轮只处理开题报告的研究现状、引用编号、参考文献结构和书目信息，不实现算法、不运行 Phase 0、不调用真实 LLM。原始 V0.1 保留不变，新增 V0.2 作为修订版。

V0.1 机器核验结果：
- 正文非空白字符约 22,505；
- 参考文献实际编号为 [1]–[50]，但自检段落仍写“43 篇”；
- [1]–[50] 均能在正文中找到引用；
- [44]–[50] 被放在“初稿自检”之后，破坏了参考文献列表的连续结构；
- Agent 自动设计基线段落重复写入 ARTEMIS；
- [50] 的论文题名为 *Evolving Excellence: Automated Optimization of LLM-Based Agents*，该论文提出/使用的框架名称为 ARTEMIS，因此正文写 ARTEMIS[50] 本身并非错号；V0.2 只删除重复列举，不改动正确的编号对应。

## 2. 已核对并修正的书目信息

| 编号 | 核验/修正内容 | 依据 |
|---|---|---|
| [10] | 修正 ICML 2026 EvoMAS 作者顺序为 Yuntong Hu, Matthew Trager, Yuting Zhang, Yi Zhang, … | PMLR 306 正式论文页：https://proceedings.mlr.press/v306/hu26bg.html |
| [22] | 补入 GECCO 2024 页码 647–655 和 DOI 10.1145/3638529.3654103 | CWI 正式记录：https://ir.cwi.nl/pub/34532 |
| [24] | 补入 FOGA 2025 页码 238–249 和 DOI 10.1145/3729878.3746624 | ACM/CWI 正式记录：https://doi.org/10.1145/3729878.3746624 |
| [27] | 补入 online-ahead-of-print 页码 1–36，保留 DOI 10.1162/EVCO.a.406 | PubMed：https://pubmed.ncbi.nlm.nih.gov/42743398/ |
| [37] | 补充 ToolSandbox 完整会议标识和 DOI 10.18653/v1/2025.findings-naacl.65 | ACL Anthology：https://aclanthology.org/2025.findings-naacl.65/ |
| [38] | 补入 τ-bench 正式记录的页码 74824–74876 | Princeton 研究成果记录：https://collaborate.princeton.edu/en/publications/%CF%84-bench-a-benchmark-for-tool-agent-user-interaction-in-real-world/ |
| [39] | 补入 AppWorld 页码 16022–16076 和 DOI 10.18653/v1/2024.acl-long.850 | ACL Anthology：https://aclanthology.org/2024.acl-long.850/ |
| [46] | 补入 HiveMind DOI 10.1609/aaai.v40i35.40222 | AAAI 正式论文页：https://ojs.aaai.org/index.php/AAAI/article/view/40222 |

**特别说明：** 本轮是重点条目的来源核验和明显错误修正，不代表其余参考文献已全部完成完整作者、卷期、页码、DOI、文献类型和 GB/T 7714 的逐项审计。后续必须继续逐条核对，不能将“已补 DOI 的部分条目”表述为“61 条全部通过”。

## 3. 新增国内研究来源及其在报告中的定位

1. **陈旭（2024），《基于大语言模型的自主智能体概述》**，第二十三届中国计算语言学大会论文集，第 141–150 页。该文归纳 Agent 的设定、记忆、规划、行动模块及多智能体交互，作为国内研究综述来源。  
   https://aclanthology.org/2024.ccl-2.8/

2. **周涛等（2024），《大模型智能体：概念、前沿和产业实践》**，《电子科技大学学报（社科版）》26(4):57–62，DOI:10.14071/j.1008-8105(2024)-1006。用于国内 Agent 概念和产业实践背景。  
   https://www.social.uestc.edu.cn/cn/article/doi/10.14071/j.1008-8105%282024%29-1006

3. **卢宇等（2024），《基于大模型的教学智能体构建与应用研究》**，《中国电化教育》2024(7):99–108。该文包含教育任务设定、规划、能力拓展、记忆反思和交互动态进化模块；属于应用框架，不应误写成 EA 搜索算法。  
   https://zdjy.cbpt.cnki.net/portal/journal/portal/client/paper/0b0cc76950eec87762cfc7a999ae70ae

4. **黄悦欣等（2025），《大语言模型AI智能体的设计方法研究》**，《工业工程设计》7(6):6–15，DOI:10.19798/j.cnki.2096-6946.2025.06.002。该文研究垂直领域数据处理、混合检索、多路径推理和提示优化；属于 Agent 系统设计相邻工作。  
   https://www.designresearchj.com/CN/10.19798/j.cnki.2096-6946.2025.06.002

5. **袁雪峰等（2026），《基于大语言模型的电力仿真智能体及其技能库设计方法》**，《电力系统自动化》2026(13):177–188，DOI:10.7500/AEPS20250328001。该文报告决策—执行—反馈—学习闭环、动态技能提取和技能成功率评估；与 Agent 技能积累相关，但不等同于种群式 EC 搜索。  
   https://coaa.istic.ac.cn/openjournal/periodicalArticle/0120260801619295

6. **Song 等（2026），MAESD: A Unified Multi-Agent Evolutionary Framework for Protein Sequence Design**，《Journal of Chemical Information and Modeling》66(7):3464–3479，DOI:10.1021/acs.jcim.5c02580。属于中国研究团队在蛋白质序列设计中结合多智能体与演化式优化的工作；优化对象是蛋白质序列，不是 Agent 配置。  
   https://doi.org/10.1021/acs.jcim.5c02580

7. **She 等（2026），《大语言模型引导的群体智能优化算法进化框架》**，《计算机应用》，DOI:10.11772/j.issn.1001-9081.2026060735。属于 LLM 赋能演化算法设计的相反方向工作，应作为交叉研究背景，不与“EC 优化 Agent”混淆。  
   https://doi.org/10.11772/j.issn.1001-9081.2026060735

## 4. 新增直接相关工作及对创新性的影响

### 4.1 Agentic Harness Engineering（AHE）

Lin 等，*Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses*，arXiv:2604.25850，2026。论文将 harness 组件、执行经验和编辑决策分别做可观测化，并把编辑与后续任务结果绑定为可证伪契约。它是 coding-agent harness 自动演进的直接先行工作，必须纳入相关工作比较。  
https://arxiv.org/abs/2604.25850

### 4.2 SkillFlow

Zhang 等，*SkillFlow: Flow-Driven Recursive Skill Evolution for Agentic Orchestration*，arXiv:2605.14089，2026。采用 Tempered Trajectory Balance 训练编排策略，并由 flow diagnostics 决定技能创建、剪枝和演进。该工作使“递归技能演化”不能单独作为创新点。注意不要与另一篇同名的 SkillFlow benchmark 混淆。  
https://arxiv.org/abs/2605.14089

### 4.3 ShapleyFlow

Yang 等，*Attribution-Based Analysis and Optimization of Modular Agentic Workflows*，Findings of ACL 2026, pp.7247–7264，DOI:10.18653/v1/2026.findings-acl.359。其在固定四组件工作流中评估全部 2^4 个模型升级组合并计算 Shapley 值，用于交互感知归因和模型分配。它不是局部 fitness-linkage/FOS 算法，但属于组件交互归因的强基线。  
https://aclanthology.org/2026.findings-acl.359/

### 4.4 FusionFlow

Wang 等，*FusionFlow: Enabling Deep Structural Exploration for Automated Agentic Workflow Generation*，ACL 2026, pp.27718–27760，DOI:10.18653/v1/2026.acl-long.1278。其通过融合多个独立演化的工作流实现结构跃迁，需纳入工作流重组和结构搜索基线。它与单 Agent 内部的 linkage-aware GOM 不完全相同，但会提高“普通工作流融合/交叉”创新声明的门槛。  
https://aclanthology.org/2026.acl-long.1278/

## 5. 对当前两个核心候选的影响

- **普通组件交互估计：继续 NO-GO。** CCI、Prompt component regression 和 ShapleyFlow 已覆盖全因子/回归/交互归因的多个方面。
- **修订创新一（任务条件化、预算受限的稀疏局部交互结构识别）：继续 HOLD。** 必须与 CCI、pairwise OLS、MESH additive LinUCB、ShapleyFlow、FBL/DLED/cDLED 和噪声 linkage 方法做同预算对照，并证明交互证据确实能改善下游演化搜索。
- **修订创新二（交互结构驱动的 Agent 约束最优混合演化）：继续 HOLD。** 必须与 GOMEA/CGOMEA/LK-GOMEA、AgentSquare、ARTEMIS、两篇 EvoMAS、MESH-Harness、AHE、SkillFlow 和 FusionFlow 比较；收益必须来自 linkage-aware mixing，而非额外 rollout、repair 或更强 LLM。
- **跨任务迁移：继续冻结。** AHE、SkillFlow 等工作进一步提高了技能/harness 迁移和在线自适应的创新门槛；Gate-2 通过前不启动。

## 6. 本轮执行状态

- 新增开题报告 V0.2；原 V0.1 保留不覆盖。
- 参考文献由 50 条扩展至 61 条，正文中引用编号匹配。
- 将 [44]–[50] 移回连续参考文献区，修正自检统计和 ARTEMIS 重复列举。
- 新增国内研究现状段落和 AHE、SkillFlow、ShapleyFlow、FusionFlow 机制对照。
- 没有实现 TCAIL/CI-GOM，没有运行 Phase 0，没有调用真实 LLM，没有通过任何新的算法 Gate。
- TCAIL V2.1 继续 HOLD / IMPLEMENTATION BLOCKED；CI-GOM 和第三项迁移继续冻结。
