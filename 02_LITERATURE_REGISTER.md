# 02 — 文献总表（首轮登记版）

**版本：** v0.1 / 2026-11-02  
**说明：** 本表是首轮发现与初步核验的文献池，不是“全部论文”的最终穷尽清单。正式写入开题报告前，必须精读关键论文并核对引用格式、版本和实验细节。

## A. 直接演化 Agent / 多智能体 / 工作流

### A1. 直接使用演化算法或进化式搜索

1. **Yuan, S., Song, K., Chen, J., Tan, X., Li, D., & Yang, D. (2025). EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms. NAACL 2025, pp. 6192–6217.** DOI: 10.18653/v1/2025.naacl-long.315. [ACL Anthology](https://aclanthology.org/2025.naacl-long.315/)  
   类型：PUBLISHED / CORE。将既有 Agent 框架作为初始个体，通过变异、交叉、选择生成多样化专家 Agent，再扩展为 Multi-Agent 系统。

2. **Hu, Y., Zhang, Y., Trager, M., Zhang, Y., Yang, S., Xia, W., & Soatto, S. (2026). Evolutionary Generation of Multi-Agent Systems. ICML 2026, PMLR 306:45989–46021.** [PMLR](https://proceedings.mlr.press/v306/hu26bg.html) · [arXiv:2602.06511](https://arxiv.org/abs/2602.06511)  
   类型：PUBLISHED / CORE。把 MAS 生成表示为结构化配置空间中的演化搜索；基于执行轨迹进行反馈条件变异和交叉，并维护候选池与经验记忆。

3. **Wei, Y., Huang, Z., Xu, R., Wang, H., & Xing, W. W. (2026). EvoMAS: Heuristics in the Loop—Evolving Smarter Agentic Workflows. ICML 2026, PMLR 306:133736–133763.** [PMLR](https://proceedings.mlr.press/v306/wei26m.html)  
   类型：PUBLISHED / CORE。与上一条是不同论文、不同作者，虽然都使用 EvoMAS 名称。其方法包含七种演化策略、探索/开发算子、自适应策略选择、角色级演化和课程式任务调度。

4. **Chi, H., Feng, Z., Yu, X., Luo, L., Ong, Y.-S., Tsang, I., Chen, H., Chang, Y., & Yin, H. (2026). EvoCF: Multi-Agent Collaboration via Agentic Memory-Driven Evolutionary Counterfactual Planning. ICML 2026, PMLR 306:19424–19437.** [PMLR](https://proceedings.mlr.press/v306/chi26b.html)  
   类型：PUBLISHED / CORE。失败中归纳符号约束，构造规则库，再通过规则条件变异生成反事实协作计划。

5. **Liu, Y. et al. (2026). Evolving Agentic Workflow Driven by Human-Agent Collaboration. Findings of ACL 2026, pp. 24960–24969.** DOI: 10.18653/v1/2026.findings-acl.1250. [ACL Anthology](https://aclanthology.org/2026.findings-acl.1250/)  
   类型：PUBLISHED / CORE。HFlow；演化工作流结构、Prompt 和模型骨干，结合人类偏好与分层经验记忆；使用任务表现、人类偏好、成本的 Pareto 多目标生存者选择。

6. **Yang, Y. et al. (2025). AgentNet: Decentralized Evolutionary Coordination for LLM-based Multi-Agent Systems. NeurIPS 2025.** DOI: 10.52202/085713-3578. [NeurIPS Proceedings](https://papers.nips.cc/paper_files/paper/2025/hash/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html)  
   类型：PUBLISHED / ADJACENT-CORE。去中心化 DAG 网络、动态拓扑调整、检索增强记忆和 Agent 专业化。需进一步核验其“evolutionary”具体是否等同经典 EA 遗传操作。

7. **Agrawal, L. A. et al. (2026). GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning. ICLR 2026.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html) · [arXiv:2507.19457](https://arxiv.org/abs/2507.19457)  
   类型：PUBLISHED / CORE-ADJACENT。Genetic-Pareto 提示优化；利用执行轨迹与自然语言反思修改模块，并按任务实例维护 Pareto 候选集合。

8. **Fernando, C., Banarse, D. S., Michalewski, H., Osindero, S., & Rocktäschel, T. (2024). Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution. ICML 2024, PMLR 235:13481–13544.** [PMLR](https://proceedings.mlr.press/v235/fernando24a.html)  
   类型：PUBLISHED / CORE-ADJACENT。同时演化任务 Prompt 和控制变异过程的 mutation-prompt，属于自指式提示演化。

9. **Guo, Q. et al. (2024). Connecting Large Language Models with Evolutionary Algorithms Yields Powerful Prompt Optimizers. ICLR 2024.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/9156b0f6dfa9bbd18c79cc459ef5d61c-Abstract-Conference.html)  
   类型：PUBLISHED / CORE-ADJACENT。EvoPrompt；以种群和演化算子优化离散自然语言 Prompt，但优化对象主要是提示词而非完整 Agent 结构。

10. **Samvelyan, M. et al. (2024). Rainbow Teaming: Open-Ended Generation of Diverse Adversarial Prompts. NeurIPS 2024.** DOI: 10.52202/079017-2229. [NeurIPS](https://papers.nips.cc/paper_files/paper/2024/hash/8147a43d030b43a01020774ae1d3e3bb-Abstract-Conference.html)  
    类型：PUBLISHED / ADJACENT。把对抗 Prompt 生成建模为 Quality-Diversity 问题，适合借鉴多样性档案与行为描述符，但不是完整 Agent 架构演化。

11. **Zhang, J. et al. (2025). Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents. arXiv:2505.22954.** [arXiv](https://arxiv.org/abs/2505.22954)  
    类型：PREPRINT / CORE-ADJACENT。通过代码修改产生新 Agent，维护生成 Agent 档案并从档案采样父代，探索多条自改进路径；不是传统固定编码的 GA。

12. **Cai, Q. et al. (2026). MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems. arXiv:2605.22794.** [arXiv](https://arxiv.org/abs/2605.22794)  
    类型：PREPRINT / ADJACENT。通过源代码层重写 Agent harness，并使用失败批次回放、隔离试验和回滚验证。需关注其自修改可靠性，但不能等同于 EA。

13. **Zhang, W. et al. (2024). Agent-Pro: Learning to Evolve via Policy-Level Reflection and Optimization. ACL 2024, pp. 5348–5375.** DOI: 10.18653/v1/2024.acl-long.292. [ACL Anthology](https://aclanthology.org/2024.acl-long.292/)  
    类型：PUBLISHED / ADJACENT。策略级反思、动态信念生成和深度优先搜索优化；是 Agent 演化/策略学习相关工作，但不属于经典遗传算法。

14. **Feng, T. et al. (2025). EvoAgent: Agent Autonomous Evolution with Continual World Model for Long-Horizon Tasks. arXiv:2502.05907.** [arXiv](https://arxiv.org/abs/2502.05907)  
    类型：PREPRINT / ADJACENT。与 NAACL 2025 的 EvoAgent 不是同一篇论文。关注 Minecraft 长时程任务、持续世界模型、经验池和课程式经验更新，不是传统种群遗传算法。

15. **Ou, Y. et al. (2025). Symbolic learning enables self-evolving agents. AI Open, 6, 314–322.** DOI: 10.1016/j.aiopen.2025.11.004. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2666651025000208)  
    类型：PUBLISHED / ADJACENT。将 Prompt、工具和组合方式表示为符号网络，使用类梯度/反向传播的文本优化机制改进 Agent。

### A2. Agent 架构、工作流与多智能体系统自动搜索（强相关对照）

16. **Hu, S., Lu, C., & Clune, J. (2025). Automated Design of Agentic Systems. ICLR 2025.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/36b7acf6f6010652b3f2a433774a66fe-Abstract-Conference.html)  
    类型：PUBLISHED / ADJACENT-CORE。ADAS / Meta Agent Search：Meta Agent 编程产生新 Agent，维护发现档案，并跨任务/模型评估迁移。

17. **Shang, Y. et al. (2025). AgentSquare: Automatic LLM Agent Search in Modular Design Space. ICLR 2025.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/0ae94013da7cd459402fd77874e09ee3-Abstract-Conference.html)  
    类型：PUBLISHED / ADJACENT-CORE。将 Agent 抽象为 Planning、Reasoning、Tool Use、Memory 四类模块，通过模块演化、重组和性能预测搜索 Agent。

18. **Zhang, J. et al. (2025). AFlow: Automating Agentic Workflow Generation. ICLR 2025.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5492ecbce4439401798dcd2c90be94cd-Abstract-Conference.html)  
    类型：PUBLISHED / ADJACENT-CORE。把代码表示的工作流视为搜索空间，使用 MCTS、代码修改、树状经验和执行反馈。

19. **Zhang, G. et al. (2025). Multi-agent Architecture Search via Agentic Supernet. ICML 2025, PMLR 267:75834–75852.** [PMLR](https://proceedings.mlr.press/v267/zhang25bi.html)  
    类型：PUBLISHED / ADJACENT-CORE。MaAS：优化 Agentic Supernet，为不同查询采样不同架构，考虑推理资源和跨数据集迁移。

20. **Zhuge, M. et al. (2024). GPTSwarm: Language Agents as Optimizable Graphs. ICML 2024, PMLR 235:62743–62767.** [PMLR](https://proceedings.mlr.press/v235/zhuge24a.html)  
    类型：PUBLISHED / ADJACENT-CORE。将 Agent 表示为计算图，优化节点 Prompt 与边连接关系。

21. **Zhou, H. et al. (2026). Multi-Agent Design: Optimizing Agents with Better Prompts and Topologies. ICLR 2026.** [Google Research](https://research.google/pubs/multi-agent-design-optimizing-agents-with-better-prompts-and-topologies/)  
    类型：PUBLISHED / ADJACENT-CORE。MASS；分阶段优化局部 Prompt、工作流拓扑和全局 Prompt。

22. **Li, Y. et al. (2026). AgentSwift: Efficient LLM Agent Design via Value-Guided Hierarchical Search. AAAI 2026, 40(38):31843–31851.** DOI: 10.1609/aaai.v40i38.40453. [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/40453)  
    类型：PUBLISHED / ADJACENT-CORE。层次化搜索空间联合建模工作流和功能组件，使用价值预测器与不确定性感知 MCTS。

23. **Hong, Z. et al. (2026). MASPOB: Bandit-Based Prompt Optimization for Multi-Agent Systems with Graph Neural Networks. ICML 2026, PMLR 306:43744–43774.** [PMLR](https://proceedings.mlr.press/v306/hong26l.html)  
    类型：PUBLISHED / ADJACENT。Bandit/UCB、GNN 拓扑表示、坐标上升用于多 Agent Prompt 优化；不是 EA，但属于强对照。

24. **Wang, Y. et al. (2025). ScoreFlow: Mastering LLM Agent Workflows via Score-based Preference Optimization. arXiv:2502.04306.** [arXiv](https://arxiv.org/abs/2502.04306)  
    类型：PREPRINT / ADJACENT。以连续空间偏好优化工作流，作为非演化优化基线。

25. **He, S. et al. (2026). Learning to Evolve: A Self-Improving Framework for Multi-Agent Systems via Textual Parameter Graph Optimization. Findings of ACL 2026, pp. 30719–30732.** DOI: 10.18653/v1/2026.findings-acl.1534. [ACL Anthology](https://aclanthology.org/2026.findings-acl.1534/)  
    类型：PUBLISHED / ADJACENT。TPGO：文本参数图、执行轨迹文本梯度和 Group Relative Agent Optimization（GRAO）。

26. **Kong, M. et al. (2026). Workflow-R1: Group Sub-sequence Policy Optimization for Multi-turn Workflow Construction. arXiv:2602.01202.** [arXiv](https://arxiv.org/abs/2602.01202)  
    类型：PREPRINT / ADJACENT。以多轮自然语言序列决策构造工作流，核心为结构感知 RL 优化。

27. **Du, S. et al. (2026). Can Workflow Search Be Amortized? Demonstration-Guided Synthesis of LLM Agent Workflows. EMNLP 2026, pp. 43645–43673.** [ACL Anthology](https://aclanthology.org/2026.emnlp-main.1916/)  
    类型：PUBLISHED / ADJACENT。SWIFT：复用源任务搜索轨迹和工作流示例，将跨任务结构知识迁移到目标任务。

28. **Wu, S. et al. (2025). Optimas: Optimizing Compound AI Systems with Globally Aligned Local Rewards. arXiv:2507.03041.** [arXiv](https://arxiv.org/abs/2507.03041)  
    类型：PREPRINT / ADJACENT。为每个系统组件维护与全局表现对齐的局部奖励函数，直接关系到组件级归因和信用分配研究。

29. **Zhang, Y., Fang, M., Chen, Z., & Pechenizkiy, M. (2026). Self-evolving LLM agents with in-distribution Optimization. ICML 2026, PMLR 306:155348–155365.** [PMLR](https://proceedings.mlr.press/v306/zhang26au.html)  
    类型：PUBLISHED / ADJACENT。Q-Evolve：通过过程奖励标注和 in-distribution RL 处理长时程 Agent 的信用分配；非 EC 强对照。

## B. 综述与研究版图

30. **Gao, H.-A. et al. (2026). A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence. TMLR 2026.** [ML Anthology](https://mlanthology.org/tmlr/2026/gao2026tmlr-survey/)  
    类型：SURVEY / PUBLISHED。按演化对象、时机和方法组织自进化 Agent 文献。

31. **Du, S. et al. (2026). A Survey on the Optimization of Large Language Model-based Agents. ACM Computing Surveys, 58(9), Article 223.** DOI: 10.1145/3789261. [ACM](https://doi.org/10.1145/3789261) · [arXiv](https://arxiv.org/abs/2503.12434)  
    类型：SURVEY / PUBLISHED。区分参数驱动与非参数驱动 Agent 优化，覆盖微调、RL、Prompt、经验、反馈、工具、检索和多 Agent 优化。

32. **Madzar, M. & Mekterovic, I. (2026). A Survey of Algorithms for Automated Design of Agentic Systems.** [Preprints.org](https://www.preprints.org/manuscript/202606.0238)  
    类型：SURVEY / PREPRINT。涵盖 33 种 ADAS 方法；未同行评审，作为检索地图使用，关键结论须回到原始论文核验。

33. **Sico Team (2026). Agentic Evolution: From Self-Improving Agents to Co-Evolving Human-AI Systems. Microsoft Research, June 2026.** [Microsoft Research](https://www.microsoft.com/en-us/research/publication/agentic-evolution-from-self-improving-agents-to-co-evolving-human-ai-systems/)  
    类型：SURVEY / TECHNICAL REPORT。整理约 300 篇论文，提出 evolutionary substrate、consolidation pathway、selective pressure 三轴分类。

34. **Wang, K. et al. (2026). Diving into Reliable Self-Evolving Agents: A Survey. Preprints.org, 2026-09-11.** [Preprints.org](https://www.preprints.org/manuscript/202609.0913)  
    类型：SURVEY / PREPRINT / 未同行评审。按演化深度和独立外部评价证据讨论可靠性。

35. **Liu, S. et al. (2026). The Path to Recursive Self-Improving Agents: Foundation, Framework, and Future Directions. Preprints.org.** DOI: 10.20944/preprints202608.0051.v1. [Survey Website](https://self-improving-agent.com/)  
    类型：SURVEY / PREPRINT。将 Agent 系统分为基础模型、harness、数据系统、trainer 和改进机制。

36. **Zhang, Z. et al. (2026). Endogenous Observations in Agent Self-Evolution: A Survey. Findings of EMNLP 2026, pp. 25257–25276.** DOI: 10.18653/2026.findings-emnlp.1196. [ACL Anthology](https://aclanthology.org/2026.findings-emnlp.1196/)  
    类型：SURVEY / PUBLISHED。按 model-internal、peer-induced、scenario-grounded 三类内生观察信号整理 Agent 自进化。

37. **Luo, J. et al. (2026). From Storage to Experience: A Survey on the Evolution of LLM Agent Memory Mechanisms. Findings of ACL 2026, pp. 41622–41652.** DOI: 10.18653/v1/2026.findings-acl.2069. [ACL Anthology](https://aclanthology.org/2026.findings-acl.2069/)  
    类型：SURVEY / PUBLISHED。按 Storage、Reflection、Experience 梳理 Agent 记忆演进。

## C. Agent 基础与评估文献

38. **Yao, S. et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023.** [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)  
    类型：FOUNDATION。Reasoning、Action、Observation 交互式轨迹。

39. **Shinn, N. et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS 2023.** [NeurIPS](https://papers.nips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)  
    类型：FOUNDATION / ADJACENT。语言反馈和情景记忆，不更新模型权重。

40. **Liu, X. et al. (2024). AgentBench: Evaluating LLMs as Agents. ICLR 2024.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html)  
    类型：BENCHMARK。八类交互环境，用于评估 Agent 推理和决策能力。

41. **Zhou, S. et al. (2024). WebArena: A Realistic Web Environment for Building Autonomous Agents. ICLR 2024.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/4410c0711e9154a7a2d26f9b3816d1ef-Abstract-Conference.html)  
    类型：BENCHMARK。真实网站环境、长时程任务和功能正确性评价。

42. **Jimenez, C. E. et al. (2024). SWE-bench: Can Language Models Resolve Real-world GitHub Issues? ICLR 2024.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html)  
    类型：BENCHMARK。真实软件工程 issue 解决任务，可作为 Agent 优化的复杂执行场景。

43. **Kapoor, S. et al. (2024). AI Agents That Matter. arXiv:2407.01502.** [arXiv](https://arxiv.org/abs/2407.01502)  
    类型：EVALUATION / PREPRINT。强调准确率之外的成本、测试集隔离、过拟合和可复现性。

## D. 演化计算基础

44. **Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T. (2002). A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II. IEEE Transactions on Evolutionary Computation, 6(2), 182–197.** DOI: 10.1109/4235.996017. [IEEE](https://doi.org/10.1109/4235.996017)

45. **Zhang, Q. & Li, H. (2007). MOEA/D: A Multiobjective Evolutionary Algorithm Based on Decomposition. IEEE Transactions on Evolutionary Computation, 11(6), 712–731.** DOI: 10.1109/TEVC.2007.892759. [IEEE](https://doi.org/10.1109/TEVC.2007.892759)

46. **Mouret, J.-B. & Clune, J. (2015). Illuminating Search Spaces by Mapping Elites. arXiv:1504.04909.** [arXiv](https://arxiv.org/abs/1504.04909)  
    类型：FOUNDATION。MAP-Elites / Quality-Diversity，通过行为描述维度维护高质量且多样化的解。

47. **Nasir, M. U. et al. (2024). LLMatic: Neural Architecture Search via Large Language Models and Quality Diversity Optimization. GECCO 2024, pp. 1110–1118.** DOI: 10.1145/3638529.3654017. [ACM](https://doi.org/10.1145/3638529.3654017)  
    类型：FOUNDATION / ADJACENT。将 LLM 代码生成与 QD 搜索结合，优化神经网络架构，不是 Agent 直接优化。

48. **Yang, C. et al. (2024). Large Language Models as Optimizers. ICLR 2024.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/3339f19c5fcee3ad74502947a32be9e6-Abstract-Conference.html)  
    类型：BOUNDARY / ADJACENT。OPRO 用 LLM 优化通用候选和 Prompt；用于区分 LLM for optimization 与 EC for Agent。

49. **Wang, X. et al. (2024). PromptAgent: Strategic Planning with Language Models Enables Expert-level Prompt Optimization. ICLR 2024.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/686a3f32067838c8dbb68da6e9e3cf69-Abstract-Conference.html)  
    类型：ADJACENT。以 MCTS 搜索 Prompt，利用错误反馈进行策略规划。

50. **Pryzant, R. et al. (2023). Automatic Prompt Optimization with “Gradient Descent” and Beam Search. EMNLP 2023, pp. 7957–7968.** DOI: 10.18653/v1/2023.emnlp-main.494. [ACL Anthology](https://aclanthology.org/2023.emnlp-main.494/)  
    类型：ADJACENT。ProTeGi 使用文本梯度、beam search 和 bandit 选择优化 Prompt。

## E. 首轮机制审查的关键提醒

- 两篇 EvoMAS 必须以完整题名和作者区分，不能仅用缩写引用。
- NAACL 2025 的 EvoAgent 与 arXiv 2502.05907 的长时程世界模型 EvoAgent 是不同论文。
- EvoPrompt、Promptbreeder、GEPA 主要优化 Prompt / compound system 的部分文本组件；AgentSquare、ADAS、AFlow、MaAS、MASS 等涉及 Agent 结构或工作流搜索，不能混为一类。
- HFlow 已使用三目标 Pareto 生存者选择；GEPA 已使用任务实例级 Pareto 候选选择；EvoMAS（Wei et al.）已研究自适应演化策略选择。普通 Pareto 选择、动态算子选择、反馈引导变异都不是天然空白。
- AgentNet、DGM、MOSS、Agent-Pro、Q-Evolve、TPGO 的机制和“经典 EA”并不完全相同，写综述时要准确分类。
- 任何论文的实验数值、模型版本、数据集划分和消融结果，必须精读原文后再写入正式开题报告。


## F. 第二轮补充文献：测试时演化、策略/技能/记忆演化与新基准

51. **He, Y., Liu, J., Liu, Y., Li, Y., Cao, T., Hu, Z., Xu, X., & Hooi, B. (2026). EvoTest: Evolutionary Test-Time Learning for Self-Improving Agentic Systems. ICLR 2026.** [OpenReview PDF](https://openreview.net/pdf?id=JFnnajbkvP) · [arXiv:2510.13220](https://arxiv.org/abs/2510.13220)  
    类型：PUBLISHED / DIRECT-CORE。提出 J-TTL；完整 Agent 配置 χ=(p,M,h,u)，每轮 Actor 执行、Evolver 根据轨迹生成子配置，使用 UCB 在父代和子代中选择。论文明确指出 (1+m) 演化策略和 UCB 可能局部收敛，单任务策略易过拟合，并建议未来研究更复杂的种群 EA、QD 和程序综合。

52. **Sygkounas, A., Hazra, R., Persson, A., Zuidberg Dos Martires, P., & Loutfi, A. (2026). COvolve: Adversarial Co-Evolution of Large-Language-Model-Generated Policies and Environments via Two-Player Zero-Sum Game. GECCO 2026, pp. 338–347.** DOI: 10.1145/3795095.3805144. [ACM DOI](https://doi.org/10.1145/3795095.3805144) · [arXiv:2603.28386](https://arxiv.org/abs/2603.28386)  
    类型：PUBLISHED / DIRECT-CORE。策略设计器和环境设计器分别维护种群，以两人零和博弈协同演化；使用 mixed-strategy Nash equilibrium 维持对旧环境的能力。其重点是代码策略与环境的对抗式课程生成，不是通用工具 Agent 的测试时配置演化。

53. **Fu, L. et al. (2026). CATArena: Evaluating Evolutionary Capabilities of Code Agents via Iterative Tournaments. ICML 2026, PMLR 306:31726–31755.** [PMLR](https://proceedings.mlr.press/v306/fu26a.html)  
    类型：PUBLISHED / BENCHMARK。多轮锦标赛评估代码 Agent 的持续优化能力，区分静态生成能力与演化潜力。

54. **Zhang, L., Chen, R., & Stadie, B. C. (2026). Evolutionary System Prompt Learning for Reinforcement Learning in LLMs. 1st FoGen Workshop at ICML 2026.** [OpenReview PDF](https://openreview.net/pdf/54e4bef7f3b700d23a7b58a1d40520984c32230f.pdf) · [arXiv:2602.14697](https://arxiv.org/abs/2602.14697)  
    类型：WORKSHOP / DIRECT-ADJACENT。E-SPL 联合演化 system prompt 和 RL 权重；通过 LLM 反思执行 mutation/crossover，并使用 TrueSkill 对不同 prompt 做相对评分。注意：这是 ICML 2026 FoGen workshop，不是 ICML 主会论文。

55. **Zhou, H., Wan, X., Vulić, I., & Korhonen, A. (2025/2026). Agentic Policy Optimization via Instruction-Policy Co-Evolution. arXiv:2512.01945.** [arXiv](https://arxiv.org/abs/2512.01945)  
    类型：PREPRINT / ADJACENT。INSPO 在 RLVR 循环中维护动态 instruction population，将 rollout 奖励归因给指令，并通过 on-policy 反思产生新指令、淘汰低表现候选。

56. **Pan, W., Liu, S., Zhou, X., Zhang, S., Shi, W., Xu, M., & Jia, X. (2026). M*: Every Task Deserves Its Own Memory Harness. NeurIPS 2026.** [Author page](https://www.wenbo.io/publications/mstar/) · [arXiv:2604.11811](https://arxiv.org/abs/2604.11811)  
    类型：PUBLISHED / DIRECT-ADJACENT。把 Agent memory harness 表示为 Python 程序（Schema、Storage Logic、Workflow Instructions），使用种群式反思代码演化，按任务发现专用记忆系统。

57. **Xia, P. et al. (2026). SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning. NeurIPS 2026.** [arXiv:2602.08234](https://arxiv.org/abs/2602.08234)  
    类型：PUBLISHED / ADJACENT。通过经验蒸馏构造层级 SkillBank，采用自适应检索和递归演化机制，使技能库与 Agent policy 在 RL 中协同更新；不是经典 GA 主导的算法。

58. **Cao, Q. et al. (2026). EvoTeam: Multi-Agent Collaboration via Evolving Teams. arXiv:2610.39813.** [arXiv](https://arxiv.org/abs/2610.39813)  
    类型：PREPRINT / DIRECT-ADJACENT。联合演化团队组织、Agent 间交互规则和个体技能；维护可复用团队库，并区分团队上下文中的协作经验与可跨团队复用的个体技能。2026-10-29 提交，需持续跟踪版本。

59. **Cao, S., Mao, Z., Li, D., Gonzalez, J. E., & Stoica, I. (2026). Evolving Agent Teams. arXiv:2610.36848.** [arXiv](https://arxiv.org/abs/2610.36848)  
    类型：PREPRINT / ADJACENT。监督 Agent 诊断局部最优并重构团队角色、协作方式，依靠持久文件系统保留学习文档和团队产物。不是标准种群式 EA，属于团队重构型 Agent 演化。

60. **Wang, Y. et al. (2026). EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective. NeurIPS 2026.** [arXiv:2605.18421](https://arxiv.org/abs/2605.18421)  
    类型：PUBLISHED / BENCHMARK。按 in-episode/cross-episode 与 knowledge-oriented/execution-oriented 两轴评估 Agent 记忆，并比较 15 种记忆方法。

61. **Zhang, A., Guo, J., Jia, F., Lv, C., Wang, B., & Li, F. (2026). EvoAgent: An Evolvable Agent Framework with Skill Learning and Multi-Agent Delegation. arXiv:2604.20133.** [arXiv](https://arxiv.org/abs/2604.20133)  
    类型：PREPRINT / ADJACENT。与 NAACL 2025 的 EvoAgent 及 arXiv 2502.05907 的 EvoAgent 均为不同工作；采用多文件技能、用户反馈闭环、层级子 Agent 委派和三层记忆。

62. **Zhai, Y. et al. (2025). AgentEvolver: Towards Efficient Self-Evolving Agent System. arXiv:2511.10395.** [arXiv](https://arxiv.org/abs/2511.10395)  
    类型：PREPRINT / ADJACENT。包含 self-questioning、self-navigating、self-attributing 三类机制，以任务生成、探索和轨迹贡献归因支持 Agent 自进化。

63. **Zhang, H. et al. (2026). EvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification. arXiv:2604.01687.** [arXiv](https://arxiv.org/abs/2604.01687)  
    类型：PREPRINT / ADJACENT。Skill Generator 与 Surrogate Verifier 协同演化；通过 verifier 的测试升级与结构化诊断，迭代生成多文件技能包。不是传统种群 EA，但“评价器/验证器协同演化”是重要相关机制。

64. **Zhang, H. et al. (2026). MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents. arXiv:2602.02474.** [arXiv](https://arxiv.org/abs/2602.02474)  
    类型：PREPRINT / ADJACENT。Controller 选择记忆技能，Executor 执行记忆提取，Designer 根据困难案例改进和扩充技能集。

65. **Zhang, Y. et al. (2026). Live-Evo: Online Evolution of Agentic Memory from Continuous Feedback. arXiv:2602.02369.** [arXiv](https://arxiv.org/abs/2602.02369)  
    类型：PREPRINT / ADJACENT。Experience Bank 与 Meta-Guideline Bank 分离，在线更新经验权重并强化/衰减记忆，以适应连续数据流和分布变化。

66. **Zhang, Z., Lu, S., Qian, H., He, D., & Liu, Z. (2026). AgentFactory: A Self-Evolving Framework Through Executable Subagent Accumulation and Reuse. arXiv:2603.18000.** [arXiv](https://arxiv.org/abs/2603.18000)  
    类型：PREPRINT / ADJACENT。把成功任务解保存为可执行 Python 子 Agent，并依据执行反馈持续修订和复用。

67. **Zhang, G. et al. (2025). MemEvolve: Meta-Evolution of Agent Memory Systems. arXiv:2512.18746.** [arXiv](https://arxiv.org/abs/2512.18746)  
    类型：PREPRINT / DIRECT-ADJACENT。联合演化 Agent 经验知识和记忆架构；EvolveLab 将 encode、store、retrieve、manage 组织成模块化设计空间，并报告跨任务、跨 LLM 泛化。

68. **Zhang, Q. et al. (2026). Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models. ICLR 2026.** [Microsoft Research](https://www.microsoft.com/en-us/research/publication/agentic-context-engineering-evolving-contexts-for-self-improving-language-models/)  
    类型：PUBLISHED / ADJACENT。ACE 通过 generation、reflection、curation 模块化演化上下文，强调避免 brevity bias 和 context collapse，并支持在线 Agent memory 更新。

69. **Zhang, S. et al. (2026). EvoFSM: Controllable Self-Evolution for Deep Research with Finite State Machines. arXiv:2601.09465.** [arXiv](https://arxiv.org/abs/2601.09465)  
    类型：PREPRINT / ADJACENT。以有限状态机表示工作流，分离 Flow 和 Skill，使用受约束操作与 Critic 改进 Agent，强调控制性和稳定性。

70. **Yue, Z. et al. (2026). Dr. Zero: Self-Evolving Search Agents without Training Data. arXiv:2601.07055.** [arXiv](https://arxiv.org/abs/2601.07055)  
    类型：PREPRINT / ADJACENT。Proposer 与 Solver 形成自进化课程：随着 Solver 能力变化，Proposer 产生更难但可解的问题；采用 HRPO 训练 Solver。属于双 Agent/RL 自进化，不是经典 EA。

71. **Qiao, J. et al. (2026). Memory Intelligence Agent. arXiv:2604.04503.** [arXiv](https://arxiv.org/abs/2604.04503)  
    类型：PREPRINT / ADJACENT。Manager-Planner-Executor 架构，交替 RL 和 test-time planner 更新，实现参数记忆与非参数记忆转换；不是经典 EA。

72. **Hazra, R., Sygkounas, A., Persson, A., Loutfi, A., & Zuidberg Dos Martires, P. (2025). REvolve: Reward Evolution with Large Language Models using Human Feedback. ICLR 2025.** [ICLR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/fc8ee7c7ab5b5f6b1615045dfb617ed6-Abstract-Conference.html) · [arXiv:2406.01309](https://arxiv.org/abs/2406.01309)  
    类型：PUBLISHED / ADJACENT。演化 LLM 生成的 RL reward functions，研究人类反馈如何转化为可执行奖励；Agent policy 是下游训练对象，不是演化对象本身。

## G. 2026 年 10 月最新动态（必须持续跟踪）

- EvoTeam（arXiv:2610.39813，2026-10-29）：团队组织、交互规则和个体技能联合演化。
- Evolving Agent Teams（arXiv:2610.36848，2026-10-27）：监督器诊断局部最优并重构团队。
- 这两篇均为本次检索时的最新预印本，不能写成同行评审正式发表论文；应持续检查后续版本和发表状态。


## H. 第二轮元数据核验补充

- E-SPL 的 arXiv 当前题名为 **Evolutionary System Prompt Learning can Facilitate Reinforcement Learning for LLMs**（arXiv:2602.14697）；其论文首页注明发表于 ICML 2026 的 1st FoGen workshop，不是 ICML 主会论文。登记中的旧题名来自早期 PDF 标题，正式引用前按最新 arXiv/Workshop 版本统一。
- INSPO 的完整题名核实为 **Agentic Policy Optimization via Instruction-Policy Co-Evolution**（arXiv:2512.01945）。
- M* 的正式 NeurIPS 2026 论文标题为 **M*: Every Task Deserves Its Own Memory Harness**；不同 arXiv 版本的作者元数据需以 NeurIPS 最终出版页为准，正式参考文献先用 Pan et al. 避免版本作者列表差异。
- EvoMemBench 已被 NeurIPS 2026 接收，arXiv v3 版本日期为 2026-10-30。
- 以上核验说明：文献表仍需逐条按最终出版版本校正作者、标题、页码和 DOI；当前不应直接把整个登记表复制成最终参考文献。


## H. 第三轮补充：Agent 演化最新方法、选择/评价、重组与可进化性

73. **(2026). MOAE: Multi-Objective Agent Evolution with Pareto-Preserving Search. arXiv:2609.05992.** [arXiv](https://arxiv.org/abs/2609.05992)  
    类型：PREPRINT / DIRECT-CORE。对完整 Agent rollout 做 Pareto-preserving evolutionary search，维护非支配候选档案，以任务表现、轨迹质量和安全为目标。来源页面声称与 ICLR workshop 相关，但 arXiv 首次提交时间为 2026-09-05，会议归属需进一步核验；暂不写作 ICLR 正式发表论文。

74. **Gong, Y. et al. (2026). SkillMOO: Multi-Objective Optimization of Agent Skills for Software Engineering. ASE 2026, NIER track.** DOI: 10.1145/3832783.3834550. [ACM DOI](https://doi.org/10.1145/3832783.3834550)  
    类型：PUBLISHED / DIRECT-CORE。使用 NSGA-II 优化软件工程 Agent 的 skill bundles，目标包含任务通过率和推理成本；说明“NSGA-II + Agent skills”已有直接研究。

75. **(2026). MOCHA: Multi-Objective Chebyshev Annealing for Agent Skill Optimization. arXiv:2605.19330.** [arXiv](https://arxiv.org/abs/2605.19330)  
    类型：PREPRINT / DIRECT-ADJACENT。使用 Chebyshev 标量化与退火优化 Agent skill，属于强相关多目标技能优化。

76. **(2026). ParetoPO: Towards Pareto-Optimal Tool-Integrated Agents with Pareto Ranking Policy Optimization. ICML 2026.**  
    类型：PUBLISHED / ADJACENT。通过 Pareto ranking policy optimization 训练 tool-integrated agents；属于 RL/策略优化，不是演化算法。完整作者、页码和正式链接待核验。

77. **(2025). AgentBreeder: Mitigating the AI Safety Risks of Multi-Agent Scaffolds via Self-Improvement. NeurIPS 2025.** [arXiv:2502.00757](https://arxiv.org/abs/2502.00757)  
    类型：PUBLISHED / DIRECT-CORE。对 Multi-Agent scaffold 做多目标演化与质量多样性搜索，关注能力和安全权衡；早期版本曾以相近题名出现在 ICLR 2025 workshop，正式引用以 NeurIPS 版本为准。

78. **(2026). Test-Time Harness Evolution (TTHE). arXiv:2607.08124.** [arXiv](https://arxiv.org/abs/2607.08124)  
    类型：PREPRINT / DIRECT-CORE。跨多个任务批次持续演化 Agent harness，使用多个 proposer 分支和 judge 选择，并将已接受修改持续带入后续任务。论文指出代理信号可靠性是核心问题，并报告候选池 oracle 选择与 judge 选择之间存在明显 selection regret。

79. **(2026). Meta-TTL: Learning to Learn-at-Test-Time—Language Agents with Learnable Adaptation Policies. arXiv:2604.00830.** [arXiv](https://arxiv.org/abs/2604.00830)  
    类型：PREPRINT / DIRECT-CORE。跨任务训练可迁移的 Agent 自适应策略；外层通过反思式搜索改进单一 adaptation meta-prompt，内层执行 test-time adaptation。

80. **(2026). TacoMAS: Test-Time Co-Evolution of Topology and Capability in LLM-Based Multi-Agent Systems. arXiv:2605.09539.** [arXiv](https://arxiv.org/abs/2605.09539)  
    类型：PREPRINT / DIRECT-CORE。测试时联合演化 Multi-Agent 拓扑和能力，采用快慢时间尺度。

81. **Wei, S. et al. (2026). Inherit-MAS: Test-Time Evolution of Multi-Agent Systems through Workflow and Execution Inheritance. arXiv:2610.02396.** [arXiv](https://arxiv.org/abs/2610.02396)  
    类型：PREPRINT / DIRECT-CORE。显式继承工作流结构和历史执行结果，使用 Judge 评价候选并诊断不足；2026-10 新近预印本。

82. **Nie, J. et al. (2026). EvolveNet: Collaborative Harness Evolution for Agent Self-Improvement. arXiv:2608.04968.** [arXiv](https://arxiv.org/abs/2608.04968)  
    类型：PREPRINT / DIRECT-CORE。多个数据本地部署分别演化 Agent harness，再通过 scope-typed、evidence-guided program aggregation 合并适应性修改。

83. **Yu, Y. et al. (2026). Do Self-Evolving Agents Forget? Capability Degradation and Preservation in Lifelong LLM Agent Adaptation. arXiv:2605.09315.** [arXiv](https://arxiv.org/abs/2605.09315)  
    类型：PREPRINT / DIRECT-ADJACENT。提出 Capability-Preserving Evolution（CPE），研究 workflow、skill、model、memory 演化中的能力退化和保持。

84. **(2026). DarwinX: Evolving Agent Harnesses Through Natural Selection. arXiv:2608.07545.** [arXiv](https://arxiv.org/abs/2608.07545)  
    类型：PREPRINT / DIRECT-CORE。通过 preserve-and-extend contract、候选档案、跨 lineage merge 和 verifier-based fitness 演化 coding-agent harness。作者指出 recombination 相对单 lineage mutation 的贡献仍需受控消融；SWE-bench Verified 的 in-domain 演化因缺乏可靠的轨迹完成信号而受限。

85. **(2026). Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses. arXiv:2604.25850.** [arXiv](https://arxiv.org/abs/2604.25850)  
    类型：PREPRINT / DIRECT-CORE。通过 component observability、experience observability、decision observability 将 harness 修改变成可验证编辑；每次修改带有自声明预测并在下一轮任务中核验。

86. **(2026). The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators. arXiv:2606.26294.** [arXiv](https://arxiv.org/abs/2606.26294)  
    类型：PREPRINT / DIRECT-ADJACENT。联合改进 Agent 和 evaluator，针对固定评价标准会随 Agent 能力提升而失效的问题提出 co-evolution。

87. **(2026). Certified Selective Automation of LLM Agent Evaluation. arXiv:2609.34320.** [arXiv](https://arxiv.org/abs/2609.34320)  
    类型：PREPRINT / EVALUATION。提出 task-level bootstrap certificate，处理同一任务下多条 Agent 轨迹的相关性，为 LLM judge 的自动决策错误率提供选择性证书。

88. **(2026). Calibrating the Evaluator: Does Probability Calibration Mitigate Preference Coupling in LLM Agent Feedback Loops? arXiv:2606.31371.** [arXiv](https://arxiv.org/abs/2606.31371)  
    类型：PREPRINT / EVALUATION。研究 evaluator pairwise judgment 的概率校准对 preference coupling 的影响；实验规模较小，需谨慎解释。

89. **Pan, E., Zhou, R., & Hu, T. (2026). Self-Reports Are Not Verification: Environment-Grounded Auditing of LLM Operators in Evolutionary Search. arXiv:2609.00652.** [arXiv](https://arxiv.org/abs/2609.00652)  
    类型：PREPRINT / EVALUATION。对 LLM evolutionary search 中的自报告置信度和 rationale 做环境真值审计，发现自报告可能严重失准。

90. **Wang, W. et al. (2026). Huxley-Gödel Machine: Human-Level Coding Agent Development by an Approximation of the Optimal Self-Improving Machine. ICLR 2026.** [arXiv:2510.21614](https://arxiv.org/abs/2510.21614)  
    类型：PUBLISHED / DIRECT-CORE。提出 clade metaproductivity（CMP），用后代整体表现估计 Agent 的未来自改进潜力，指导自修改树搜索。

91. **Yan, S. et al. (2026). The View from Nowhere: Population-Centered Agent Evolution. arXiv:2610.36660.** [arXiv](https://arxiv.org/abs/2610.36660)  
    类型：PREPRINT / DIRECT-CORE。Population-Centered Evolution（PCE）将整个种群的任务记录、修改历史、互补成功和重复失败压缩为 population block，辅助改进选定父代。

92. **Kong, L. et al. (2026). FreeEvolve: Learning to Evolve Beyond Fixed Loops. arXiv:2610.09197.** [arXiv](https://arxiv.org/abs/2610.09197)  
    类型：PREPRINT / DIRECT-CORE。将 evolver 自身的搜索、证据采集、候选选择和停止策略表示为可编辑 evolution skill，并通过 meta-evolution 改进 evolver。

93. **(2026). Group-Evolving Agents: Open-Ended Self-Improvement via Experience Sharing. arXiv:2602.04837.** [arXiv](https://arxiv.org/abs/2602.04837)  
    类型：PREPRINT / DIRECT-ADJACENT。群体级 Agent 演化和经验共享，需继续核验正式发表状态及与 PCE 的差异。

94. **(2026). Experience as a Compass: Multi-Agent RAG with Evolving Orchestration and Agent Prompts (HERA). arXiv:2604.00901.** [arXiv](https://arxiv.org/abs/2604.00901)  
    类型：PREPRINT / ADJACENT。联合优化多 Agent orchestration 与 prompt，结合历史经验检索；需精读是否存在真正的遗传算子。

95. **Xia, Y. et al. (2026). HiveMind: Contribution-Guided Online Prompt Optimization of LLM Multi-Agent Systems. AAAI 2026, 40(35):29767–29774.** DOI: 10.1609/aaai.v40i35.40222. [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/40222)  
    类型：PUBLISHED / ADJACENT。使用 DAG-Shapley 估计 Multi-Agent workflow 中个体 Agent 的贡献，并对低贡献 Agent 的 Prompt 进行在线优化；是信用分配强基线，但不是 EA。

96. **(2025). FlowReasoner: Reinforcing Query-Level Meta-Agents. arXiv:2504.15257.** [arXiv](https://arxiv.org/abs/2504.15257)  
    类型：PREPRINT / ADJACENT。通过 RL 训练 meta-agent 为单个查询设计 Multi-Agent workflow；不是 EA。

97. **(2024). Multi-Agent Sampling: Scaling Inference Compute for Data Synthesis with Tree Search-Based Agentic Collaboration (TOA). arXiv:2412.17061.** [arXiv](https://arxiv.org/abs/2412.17061)  
    类型：PREPRINT / ADJACENT。通过树搜索组织多 Agent 数据合成，属于搜索型协作对照。

98. **(2026). Self-Evolving Agent Harness. arXiv:2610.18813.** [arXiv](https://arxiv.org/abs/2610.18813)  
    类型：PREPRINT / DIRECT-ADJACENT。研究 harness 持续演化中的泛化界、能力保持和独立验证准入规则；需精读并核对完整题名/作者。

99. **Ge, L.-Y. & Guo, L.-Z. (2026). Roles with Rails: Contract-Preserving Role Evolution in Multi-Agent Structured Reasoning. Findings of EMNLP 2026, pp. 6159–6192.** [ACL Anthology](https://aclanthology.org/2026.findings-emnlp.290/)  
    类型：PUBLISHED / ADJACENT。SERO 维护 typed role-card pool、通信 DAG、受保护的终端聚合器和条件验证器修复；候选修改只有通过结构契约且提高任务分数才提交。

100. **(2026). EvoDrive: Pareto Evolution for Safety-Critical Autonomous Driving via Self-Improving LLM Agents. CoRL 2026.** [CoRL 2026](https://www.corl.org/)  
     类型：PUBLISHED / ADJACENT。使用 Agentic 演化优化安全关键自动驾驶场景/系统，需进一步确认演化对象主要是场景生成器还是 Agent 本身，不能直接当作 Agent 配置演化证据。

## I. 演化计算基础：可进化性、噪声适应度与统计竞赛

101. **Mengistu, H., Lehman, J., & Clune, J. (2016). Evolvability Search: Directly Selecting for Evolvability in Order to Study and Produce It. GECCO 2016, pp. 141–148.** DOI: 10.1145/2908812.2908838. [ACM DOI](https://doi.org/10.1145/2908812.2908838)  
     类型：FOUNDATION。通过直接测量个体即时后代的行为多样性来选择可进化个体；说明“按 offspring potential 选择”是经典 EC 已有思想。

102. **Gajewski, A., Clune, J., Stanley, K. O., & Lehman, J. (2019). Evolvability ES: Scalable and Direct Optimization of Evolvability. GECCO 2019.** DOI: 10.1145/3321707.3321876. [ACM DOI](https://doi.org/10.1145/3321707.3321876) · [arXiv:1907.06077](https://arxiv.org/abs/1907.06077)  
     类型：FOUNDATION。以可扩展 ES 直接优化扰动后产生多样行为的能力。

103. **Rakshit, P., Konar, A., & Das, S. (2017). Noisy Evolutionary Optimization Algorithms—A Comprehensive Survey. Swarm and Evolutionary Computation, 33, 18–45.** DOI: 10.1016/j.swevo.2016.09.002. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S221065021630308X)  
     类型：FOUNDATION / SURVEY。系统整理噪声适应度下的采样、估计、动态种群规模、搜索策略和选择机制。

104. **Birattari, M., Stützle, T., Paquete, L., & Varrentrapp, K. (2002). A Racing Algorithm for Configuring Metaheuristics. GECCO 2002, pp. 11–18.** [PDF](https://www.metaheuristics.org/downloads/BirStuPaqVar2002_gecco.pdf)  
     类型：FOUNDATION。F-Race 根据统计证据逐步淘汰较差配置；可作为不确定/噪声评价下候选比较的经典方法基础。


## J. 开题论文结构相关的新增直接工作（2026-11-02）

105. **Shang, Z. et al. (2026). MESH-Harness: Self-Improving Agent Harnesses via Bandit-Guided Compositional Evolution. arXiv:2610.05300.** [arXiv](https://arxiv.org/abs/2610.05300)  
     类型：PREPRINT / DIRECT-CORE。将 Agent harness 分为固定接口功能槽位，维护模块实现池，以 full-covariance LinUCB 和 mixed-start coordinate ascent 选择完整组合，并根据执行轨迹编辑模块。重要机制细节：其配置表示为各槽位 embedding 拼接；预测均值仍是 slot-wise additive，full covariance 用于统计共同出现信息和组合不确定性，并非直接拟合非加性组件 epistasis。是强组合搜索与评价分配基线。

106. **Wei, T. et al. (2026). Evo-Harness: Context-to-Harness Skill Compilation for Self-Evolving Agents. EMNLP 2026, pp. 22343–22358.** DOI: 10.18653/2026.emnlp-main.969. [ACL Anthology](https://aclanthology.org/2026.emnlp-main.969/)  
     类型：PUBLISHED / DIRECT-ADJACENT。研究在线 Harness 学习，将单次执行中含噪上下文编译成可复用技能 harness，在 TerminalBench2、SWE-bench、CL-Bench、τ-bench、WebArena-Infinity 等任务上评估。对第三创新点的任务迁移和经验更新是直接相关工作。

107. **(2026). AgentEvo: Cost-Aware Agentic Workflow Generation via Adaptive Multi-Stage Evolution. Complex & Intelligent Systems.** DOI: 10.1007/s40747-026-02325-0. [Springer](https://link.springer.com/article/10.1007/s40747-026-02325-0)  
     类型：PUBLISHED / DIRECT-CORE。采用探索、精炼、交叉多阶段演化，进行工作流子图 graft、prompt fusion 和性能-Token 成本 Pareto 选择。说明 Agent workflow crossover、多目标成本优化已有直接研究。

108. **Brookes, P. et al. (2025). Evolving Excellence: Automated Optimization of LLM-Based Agents. arXiv:2512.09108.** [arXiv](https://arxiv.org/abs/2512.09108)  
     类型：PREPRINT / DIRECT-CORE。ARTEMIS 使用语义感知遗传算子，自动发现可配置 Agent 组件，并联合演化不同 Agent 配置。需要进一步精读其组件依赖识别和遗传算子细节；不能仅凭摘要断言其已实现 epistasis-aware linkage learning。

109. **Hu, Y. et al. (2026). Evolutionary Generation of Multi-Agent Systems. ICML 2026.** [arXiv](https://arxiv.org/abs/2602.06511)  
     类型：PUBLISHED / DIRECT-CORE。EvoMAS 将 MAS 生成建模为结构化配置空间中的演化，使用执行轨迹引导的 feedback-conditioned mutation 和 crossover，并维护候选池与经验记忆。是结构化 Agent 演化的强基线。


## K. 第四轮：交互效应审查、经典 Linkage Learning 与 Agent 评测基准（2026-11-02）

110. **Liu, M. (2026). More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding. arXiv:2605.05716.** [arXiv](https://arxiv.org/abs/2605.05716)  
     类型：PREPRINT / DIRECT-CORE。对 Planning、Tool Use、Memory、Structured Reasoning、Reflection 五个组件做 \(2^5=32\) 种全因子实验，使用 HotpotQA/GSM8K 和多个模型规模；计算 Shapley 并分析 pairwise / three-body interaction。论文在一个主要设置中发现 main-effects LOOCV \(R^2=0.872\)，pairwise regression LOOCV \(R^2=0.748\)，提示无约束增加交互项会过拟合。其研究主要是静态 prompt-based scaffolding 的交互分析，不是预算受限的可执行模块演化算法。

111. **Lauziere, A., Daugherty, J., & Kushner, T. (2026). A Regression Framework for Understanding Prompt Component Impact on LLM Performance. EXPLAINABILITY 2026, IARIA, pp. 1–10.** [Conference page](https://www.thinkmind.org/library/EXPLAINABILITY/EXPLAINABILITY_2026/explainability_2026_1_10_10007.html) · [arXiv:2603.26830](https://arxiv.org/abs/2603.26830)  
     类型：PUBLISHED / ADJACENT。用回归模型估计 Prompt 组件特征对 LLM 性能的影响，涉及 pairwise interaction model；进一步说明静态 prompt 组件回归不能作为本课题独立创新。

112. **Dushatskiy, A., Virgolin, M., Bouter, A., Thierens, D., & Bosman, P. A. N. (2024). Parameterless Gene-Pool Optimal Mixing Evolutionary Algorithms. Evolutionary Computation, 32(4), 371–397.** DOI: 10.1162/evco_a_00338. [arXiv:2109.05259](https://arxiv.org/abs/2109.05259)  
     类型：FOUNDATION / PUBLISHED。系统研究 GOMEA、Linkage Tree、Gene-pool Optimal Mixing、Conditional GOM（CGOM）及参数无关种群管理。GOM 按 linkage subset 从 donor 引入基因并尝试接受；CGOM 进一步利用条件依赖筛选 mating。是交互感知重组必须比较的核心 EC 基线。

113. **Guijt, A., Thierens, D., Alderliesten, T., & Bosman, P. A. N. (2022). Solving Multi-Structured Problems by Introducing Linkage Kernels into GOMEA. GECCO 2022, pp. 703–711.** DOI: 10.1145/3512290.3528828. [TU Delft record](https://repository.tudelft.nl/record/uuid%3A6dcc4963-eb72-4f30-be0d-14277f2bc54a)  
     类型：FOUNDATION / PUBLISHED。提出 Linkage Kernels，为每个解在局部邻域中学习不同 linkage structure，以处理多结构/多模态依赖。对第三创新点的 task-conditioned/local linkage transfer 是重要先行工作。

114. **Omidvar, M. N., Yang, M., Mei, Y., Li, X., & Yao, X. (2017). DG2: A Faster and More Accurate Differential Grouping for Large-Scale Black-Box Optimization. IEEE Transactions on Evolutionary Computation.** DOI: 10.1109/TEVC.2017.2694221. [University of Leeds record](https://eprints.whiterose.ac.uk/id/eprint/154094/)  
     类型：FOUNDATION / PUBLISHED。基于适应度差分识别变量交互，自动估计阈值，检测重叠子问题；适用于比较 Agent 组件交互识别方法的经典基线思想，但原方法面向数值黑盒优化，不能不加修改地套用于随机、混合类型 Agent 评价。

115. **Lu, J. et al. (2025). ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities. Findings of NAACL 2025, pp. 1160–1183.** DOI: 10.18653/v1/2025.findings-naacl.65. [ACL Anthology](https://aclanthology.org/2025.findings-naacl.65/)  
     类型：BENCHMARK / PUBLISHED。支持有状态工具执行、工具间隐式状态依赖、on-policy 用户模拟和轨迹过程中的动态评价。适合检验 Agent 模块之间的可执行依赖与交互。

116. **Yao, S., Shinn, N., Razavi, P., & Narasimhan, K. (2025). \(\tau\)-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains. ICLR 2025.** [ICLR paper page](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html)  
     类型：BENCHMARK / PUBLISHED。包含 airline 和 retail 两类工具任务，使用模拟用户和领域 API，并通过最终数据库状态与目标状态比较评估任务完成情况；提出 pass^k 衡量多次执行可靠性。

117. **Trivedi, H. et al. (2024). AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents. ACL 2024.** [ACL Anthology](https://aclanthology.org/2024.acl-long.850/)  
     类型：BENCHMARK / PUBLISHED。提供 9 个日常应用、457 个 API 和 750 个任务，使用程序化状态检查评价任务完成及意外副作用；可作为多工具、有状态 Agent 配置演化的外部验证基准。



## L. 第五轮：演化计算参数调优与在线参数控制（2026-11-02）

118. **Eiben, A. E., Michalewicz, Z., Schoenauer, M., & Smith, J. E. (2007). Parameter Control in Evolutionary Algorithms.** In *Parameter Setting in Evolutionary Algorithms*, Studies in Computational Intelligence, vol. 54, pp. 19–46. DOI: 10.1007/978-3-540-69432-8_2. [University of Adelaide record](https://digital.library.adelaide.edu.au/items/e7778f8f-c154-4995-a207-b29c0c098598)  
     类型：FOUNDATION / SURVEY。区分预先参数设置与运行时参数控制，并将运行时控制划分为 deterministic、adaptive、self-adaptive。用于本课题建立离线调参和在线控制的概念边界。

119. **Eiben, A. E., & Smit, S. K. (2011). Parameter tuning for configuring and analyzing evolutionary algorithms. Swarm and Evolutionary Computation, 1(1), 19–31.** DOI: 10.1016/j.swevo.2011.02.001. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2210650211000022)  
     类型：FOUNDATION / SURVEY。提出问题—演化算法—调参器的三层框架，讨论采样、模型、筛选和元演化调参，并强调算法性能与鲁棒性评价。

120. **Aleti, A., & Moser, I. (2016). A systematic literature review of adaptive parameter control methods for evolutionary algorithms. ACM Computing Surveys, 49(3), Article 56.** DOI: 10.1145/2996355. [Monash record](https://research.monash.edu/en/publications/a-systematic-literature-review-of-adaptive-parameter-control-method/)  
     类型：FOUNDATION / SURVEY。系统梳理基于运行反馈的在线参数控制，指出 mutation rate、crossover rate、population size 等参数具有问题和阶段依赖性。

121. **López-Ibáñez, M., Dubois-Lacoste, J., Pérez Cáceres, L., Stützle, T., & Birattari, M. (2016). The irace package: Iterated racing for automatic algorithm configuration. Operations Research Perspectives, 3, 43–58.** DOI: 10.1016/j.orp.2016.09.002. [Open access paper](https://www.sciencedirect.com/science/article/pii/S2214716015300270) · [irace documentation](https://mlopez-ibanez.github.io/irace/)  
     类型：METHOD / TOOL。通过候选配置采样和 iterated racing 在问题实例上淘汰统计上较差的参数配置；适用于离线自动算法配置，作为本课题混合数值/类别参数的首选调参工具候选。

122. **Da Costa, L., Fialho, Á., Schoenauer, M., & Sebag, M. (2008). Adaptive operator selection with dynamic multi-armed bandits. GECCO 2008, pp. 913–920.** DOI: 10.1145/1389095.1389272. [Author manuscript](https://www.cs.ubc.ca/~hutter/EARG.shtml/earg/papers08/pap333s1-dacosta.pdf)  
     类型：FOUNDATION / METHOD。AOS 将算子信用分配与多臂老虎机选择机制分开处理，根据历史 offspring 表现调整算子使用策略。用于本课题的辅助参数控制，不单独宣称新颖。

123. **Tanabe, R., & Fukunaga, A. (2013). Success-history based parameter adaptation for Differential Evolution. IEEE Congress on Evolutionary Computation 2013, pp. 71–78.** DOI: 10.1109/CEC.2013.6557555. [IEEE Xplore](https://doi.org/10.1109/CEC.2013.6557555)  
     类型：FOUNDATION / METHOD。SHADE 使用历史成功的 \(F\)、\(CR\) 参数对未来采样进行引导；可借鉴“成功历史”思想，但 \(F\)、\(CR\) 是 DE 参数，不能直接移植为 categorical GOM 参数。

124. **Tanabe, R., & Fukunaga, A. (2014). Improving the search performance of SHADE using linear population size reduction. IEEE Congress on Evolutionary Computation 2014.** DOI: 10.1109/CEC.2014.6900380. [DOI](https://doi.org/10.1109/CEC.2014.6900380)  
     类型：FOUNDATION / METHOD。L-SHADE 在 SHADE 基础上加入线性种群规模缩减，作为 DE 中种群规模动态控制的代表工作；仅用于 DE baseline 和参数控制背景，不作为本课题 GOM 的直接参数方案。

