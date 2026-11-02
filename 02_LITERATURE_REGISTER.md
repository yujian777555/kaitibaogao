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
