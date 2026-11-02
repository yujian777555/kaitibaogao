# 01 — 文献检索协议与检索日志

**版本：** v0.1  
**首轮检索日期：** 2026-11-02  
**研究主题：** Evolutionary Computation for AI Agents

## 1. 检索范围

时间范围以 2022-11-02 至 2026-11-02 为重点，同时纳入必要的演化计算经典文献和 Agent 基础论文。检索对象包括：
- 演化算法直接优化单 Agent / Multi-Agent / Agent workflow；
- Agent architecture search、workflow search、agent design search；
- Prompt / policy / memory / tool / topology 的进化或群体搜索；
- 自进化 Agent、开放式演化、协同演化；
- Agent 优化相关综述、benchmark、评价方法；
- 作为方法基础的多目标演化、Quality-Diversity、档案与算子选择论文。

## 2. 数据源与优先级

优先使用可核验的一手来源：
1. ACL Anthology、PMLR、ICLR/OpenReview、NeurIPS Proceedings、AAAI Proceedings、ACM DL、IEEE Xplore；
2. arXiv（必须标注预印本版本，不能冒充同行评审发表）；
3. 作者主页和大学/实验室论文页面；
4. Semantic Scholar、DBLP 等用于交叉核对作者和出版元数据；
5. 综述论文及其参考文献用于反向追踪。

检索网页只用于发现和核验公开论文，不读取用户其他 GitHub 仓库。公开论文页面中出现的代码仓库链接仅作为书目信息，不作为本项目研究仓库。

## 3. 检索关键词

### 3.1 直接演化 Agent
- “evolutionary algorithms for LLM agents”
- “evolutionary generation of multi-agent systems”
- “evolutionary agent design”
- “evolving agentic workflows”
- “evolutionary optimization of AI agents”
- “genetic algorithm multi-agent LLM”
- “population-based agent evolution”
- “quality diversity agent evolution”
- “evolutionary search agent architecture”
- “co-evolutionary multi-agent systems LLM”

### 3.2 Agent 架构与工作流搜索（相邻方法）
- “automated design of agentic systems”
- “LLM agent architecture search”
- “multi-agent system search”
- “agentic workflow generation”
- “workflow optimization LLM agents”
- “agent design search MCTS”
- “agentic supernet architecture search”
- “graph optimization language agents”

### 3.3 自进化与反馈学习（相邻方法）
- “self-evolving agents survey”
- “recursive self-improving agents”
- “process reward agent self evolution”
- “execution trace feedback agent optimization”
- “agent memory evolution”
- “self-modifying agent source code”
- “agentic evolution reliability”

### 3.4 演化计算基础
- “multiobjective evolutionary optimization”
- “NSGA-II NSGA-III MOEA/D”
- “MAP-Elites quality diversity”
- “adaptive operator selection evolutionary algorithm”
- “cooperative coevolution evolutionary optimization”

## 4. 纳入标准

至少满足一项：
- 以 Agent、Multi-Agent、Agent workflow 或其可执行组件为优化对象；
- 明确使用 evolutionary algorithm / genetic operators / population / mutation / crossover / selection / quality-diversity / co-evolution；
- 对 Agent 结构或策略进行自动搜索，虽非经典 EA，但可作为强相关对照；
- 对 Agent 自进化中的反馈、评价、记忆、鲁棒性或泛化提供直接机制证据；
- 为拟采用的演化算法或 Agent 评估提供关键理论/benchmark。

## 5. 排除或降级标准

- 仅把 LLM 用于优化传统数学函数，而 Agent 不是优化对象：仅列为方向边界或辅助背景；
- 仅为多 Agent 对话/角色扮演，没有 Agent 优化机制：一般不纳入核心文献；
- 只提出产品/框架，没有可审查的算法或实验：列为工程背景，不作为核心算法证据；
- 只在摘要、博客或二手转述中出现，无法核验原始来源：标记待核验；
- 同一论文的 arXiv 与会议版本：合并为一条记录，保留版本关系；
- 同名论文或同一缩写：必须区分作者、完整题名、年份和 DOI。

## 6. 质量与状态标签

- **PUBLISHED**：已在正式会议/期刊发表；
- **PREPRINT**：arXiv 或其他预印本，未核实正式发表；
- **SURVEY**：综述，单独分类；
- **ADJACENT**：Agent 搜索/优化相关，但非经典演化计算；
- **FOUNDATION**：演化算法理论、Agent 基础或 benchmark；
- **TO_VERIFY**：元数据、正文或实验细节尚待核验。

## 7. 检索日志

### 2026-11-02 — 首轮
- 检索主题：Evolutionary algorithms for LLM agents、EvoAgent、EvoMAS、agent architecture search、agentic workflow evolution、self-evolving agent surveys。
- 已发现直接演化论文：EvoAgent（NAACL 2025）、EvoMAS（ICML 2026，Hu et al.）、EvoMAS（ICML 2026，Wei et al.，另一篇同名论文）、EvoCF（ICML 2026）、HFlow（Findings ACL 2026）、GEPA（ICLR 2026）、EvoPrompt（ICLR 2024）、Promptbreeder（ICML 2024）等。
- 已发现重要相邻方法：ADAS、AgentSquare、AFlow、MaAS、GPTSwarm、MASS、AgentSwift、MASPOB、ScoreFlow、SWIFT、Workflow-R1、Optimas、Q-Evolve、TPGO 等。
- 已发现综述：A Survey of Self-Evolving Agents（TMLR 2026）、A Survey on the Optimization of LLM-based Agents（ACM Computing Surveys 2026）、Agentic Evolution（Microsoft Research 2026）、Diving into Reliable Self-Evolving Agents（2026 预印本）等。
- 重要发现：HFlow 已使用性能/人类偏好/成本三目标 Pareto 生存者选择；GEPA 已使用实例级 Pareto 候选选择；两篇不同 ICML 2026 论文共用 EvoMAS 名称。
- 当前限制：首轮属于宽口径发现和部分精读，不是穷尽式系统综述；后续需逐条核对原文、引用链和数据库检索结果。

## 8. 每轮更新要求

每次新增论文时记录：检索日期、检索式、数据库/来源、完整题名、作者、年份、venue、DOI/arXiv、论文类型、研究对象、演化机制、主要结论、局限、与本课题的关系、核验状态。

每轮结束更新本文件和 02_LITERATURE_REGISTER.md；不允许只在聊天中报告而不入库。
