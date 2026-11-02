# 05 — 研究决策日志

## 2026-11-02：项目启动与研究边界锁定

### 决策 D-001：唯一仓库

用户指定 https://github.com/yujian777555/kaitibaogao 作为本次开题研究唯一仓库。后续不读取其他 GitHub 仓库，不将其他项目混入本项目。

### 决策 D-002：研究主线

研究方向锁定为 Evolutionary Computation for AI Agents：演化计算是核心优化方法，Agent 是优化对象。LLM for EC 不作为本课题主线。

### 决策 D-003：开题要求

根据用户提供的河北工业大学开题报告模板，硕士正文不少于 6000 字、参考文献不少于 30 篇、外文不少于 30%、近五年文献不少于 30%，并覆盖模板规定的研究内容和排版要求。

### 决策 D-004：不提前确定题目和创新点

首轮检索已发现多个直接相关的 2025–2026 论文。当前不锁定最终题目，不宣称创新点已经成立。先完成机制级精读、重复风险审查和可证伪实验设计。

### 决策 D-005：必须区分两篇 EvoMAS

- Hu et al. (ICML 2026), Evolutionary Generation of Multi-Agent Systems；
- Wei et al. (ICML 2026), EvoMAS: Heuristics in the Loop—Evolving Smarter Agentic Workflows。

二者是不同论文，不能混为一谈。

### 决策 D-006：当前候选

优先审查：
- A：任务分布泛化 + Quality-Diversity 演化；
- B：执行过程归因 + 演化选择/变异；
暂缓：
- C：Agent 与演化算子协同适应，因为 Wei et al. 的 EvoMAS 已直接研究多策略和自适应策略选择。

### 决策 D-007：创新性判断规则

以下内容不能单独作为创新：
- 把 NSGA-II/III 接到 Agent 上；
- 普通 Pareto 多目标选择；
- 使用执行反馈引导变异；
- 采用四模块 Agent 编码；
- 仅增加反思、经验记忆或变异提示词；
- 仅提出动态算子选择。

必须提出具体机制差异、数学定义、实验假设和反例/停止条件。

## 下一次决策前必须补充的证据

1. 核心论文的算法细节、伪代码和消融；
2. 候选 A/B 的完整相关工作覆盖；
3. 与最强基线的可复现比较方案；
4. 数据集和 held-out task family 的可行性；
5. 每个创新点如何单独验证和如何形成递进关系。


## 2026-11-02 第二轮：新增 EvoTest 作为优先切入证据

### 论文事实
精读 EvoTest（ICLR 2026）正文方法与局限性章节。其 Agent 配置为 χ=(p,M,h,u)，以 Actor/Evolver 分离完成 episode-to-episode 更新，使用父代+子代候选池和 UCB 选择。J-TTL 基准包含六款 Jericho 游戏，每款 session 连续 50 个 episode，单个 episode 通常上限 110 步。

### 原文局限
作者明确指出 (1+m)+UCB 较简单，可能局部最优；同一任务中的策略存在任务特定过拟合；建议未来研究更复杂的种群 EA、QD 和程序综合。

### 新增直接/相邻文献
COvolve（GECCO 2026）、CATArena（ICML 2026）、M*（NeurIPS 2026）、E-SPL（ICML 2026 FoGen workshop）、INSPO、SkillRL、EvoTeam、Evolving Agent Teams、EvoMemBench、EvoSkills、MemEvolve、MemSkill、Live-Evo、AgentFactory、AgentEvolver、EvoFSM、Dr. Zero、MIA、ACE。

### 决策 D-008
新增候选 D：跨任务序列的演化测试时自适应。当前优先级高于 A/B/C，但未批准为最终方向。

### 决策 D-009
候选 D 不得简化为“把 (1+m) 换成 NSGA-III / MAP-Elites”。必须明确任务分布变化、行为描述符、档案迁移和 held-out 验证机制，并与 M*、MemEvolve、E-SPL、INSPO、COvolve、EvoTeam、HFlow、EvoMAS 比较。

### 决策 D-010
新增文献记录 51–72。文献总表目前为 72 条登记记录，仍非穷尽清单；下一轮必须继续追踪综述引用和国内研究。
