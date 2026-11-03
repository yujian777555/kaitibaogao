# 河北工业大学研究生学位论文开题报告（初稿 V0.2）

**论文题目：面向大语言模型智能体的交互感知演化优化方法研究**  
**报告版本：** V0.2（供导师初审的研究方案初稿）  
**日期：** 2026 年 11 月 2 日  
**类别：** 硕士  
**所属学院：** 人工智能与数据科学学院  
**学科专业：** 计算机技术  
**研究方向：** 演化计算与大语言模型智能体优化  
**导师姓名：** （待填写）  
**学号：** （待填写）  
**姓名：** （待填写）

> **初稿说明：** 本报告依据河北工业大学研究生学位论文开题报告模板和当前唯一开题研究仓库中的文献、算法与可行性审查材料形成。题目为工作题目，两个核心研究内容及第三个储备方向均属于拟研究方案；尚未通过的算法规格和未开展的实验不表述为既有成果。正式提交前需根据导师意见、学校学位论文写作规范和后续实验结果修订。

---

## 一、选题来源

本课题来源于大语言模型智能体（Large Language Model-based Agent，以下简称 LLM Agent）在复杂任务环境中的自动设计与性能优化需求，以及演化计算在离散组合优化、黑盒优化和复杂系统搜索方面的研究基础。

近年来，大语言模型由以文本生成和问答为主的交互形式，逐步发展为能够调用外部工具、维护任务状态、执行多步规划并根据环境反馈调整行为的智能体系统。典型智能体通常由规划、推理、工具选择、记忆、执行验证和错误恢复等功能模块构成。不同模块的实现方式、参数配置和组合关系会影响智能体的任务成功率、执行可靠性、资源消耗及跨任务适应能力。随着智能体应用从单轮问答扩展到软件工程、网页操作、办公应用和多工具协同等长流程任务，如何系统地设计和优化智能体结构与行为策略，已成为人工智能领域的重要研究问题。

目前，智能体系统的设计仍较多依赖人工经验、提示词迭代、局部模块替换或基于执行反馈的启发式搜索。此类方法能够在特定任务上取得效果，但当智能体包含多个可替换模块、模块之间存在接口依赖和性能交互、任务执行具有随机性时，人工逐项调整容易忽略模块组合效应，也难以保证搜索过程的系统性和可复现性。尤其是两个模块单独表现良好，并不意味着二者组合后仍然有效；模块之间可能产生协同作用，也可能出现功能冲突或相互削弱。因此，智能体配置优化不仅是对单个模块进行选择的问题，还涉及模块之间的依赖关系和组合结构。

演化计算以种群为基础，通过选择、变异、重组和生存者更新在复杂搜索空间中迭代寻找高质量解，适合处理模块配置、工作流结构和策略组合等离散或混合类型优化问题。近年来，EvoAgent、EvoMAS、HFlow、GEPA、AgentSquare 等研究已将进化搜索或自动化搜索用于智能体生成、工作流优化和模块组合[9-17]。这些工作表明，演化计算能够为智能体自动设计提供有效的搜索框架，但也说明仅将遗传算法或多目标优化算法直接应用于智能体，并不足以构成明确的方法创新。需要进一步研究智能体组件之间的交互结构如何被识别，以及这些结构如何真正改变演化算法的重组与搜索行为。

另一方面，演化计算领域已经形成了较为成熟的 linkage learning 和 optimal mixing 方法。GOMEA 通过学习变量之间的依赖结构构造变量子集，并利用 gene-pool optimal mixing 对相关变量进行联合替换；Conditional GOM 等方法进一步考虑条件依赖。Fitness-based linkage learning、DLED、cDLED 和 Linkage Kernels 等研究，则从目标函数差分或个体局部结构中识别变量依赖[19-27]。这些工作为本课题提供了直接的理论基础，也提高了本课题的创新性要求：不能把“识别组件交互”“构造交互图”或“使用交互图指导交叉”本身作为未经比较的创新点，而应研究现有 linkage 方法在随机执行、任务异质、混合类型模块和智能体硬约束条件下是否存在可验证的不足，并提出相应改进。

基于上述背景，本课题拟以大语言模型智能体的模块化配置为优化对象，以演化计算为核心方法，重点研究任务条件化组件交互结构估计及其驱动的约束最优混合演化方法。研究首先建立可执行、可评价、可比较的智能体模块配置空间；随后研究如何在随机 rollout 和任务分布差异下识别模块间非加性交互；在此基础上，将可信交互结构转化为演化算法中的 linkage/FOS，并设计满足接口约束的模块块级重组和评价接受机制。任务分布变化下的交互结构迁移作为后续储备方向，在前两个研究内容获得实验支持后再判断是否形成独立研究点。

## 二、论文研究背景、目的和意义

### 2.1 研究背景

LLM Agent 通常以大语言模型为核心决策器，通过提示词、工具接口、记忆模块、规划机制和执行环境形成完整的任务执行系统。与传统静态模型相比，Agent 的能力不仅取决于基础模型本身，还取决于系统层面的模块组织和运行策略。例如，在工具使用任务中，规划模块决定任务分解方式，工具路由模块决定调用哪个工具及其参数，记忆模块决定历史状态如何保存和检索，验证与恢复模块决定执行失败后是否检查状态、修正参数或重新规划。不同模块之间存在功能依赖和性能交互，系统整体表现通常不能简单地由各模块单独表现相加得到。

ReAct 将推理与行动交替组织，使语言模型能够根据环境观察决定后续动作[1]；Reflexion 通过语言反馈和情景记忆改善智能体后续尝试[2]。这些研究推动了智能体从单次生成向多步交互发展。与此同时，AgentBench、WebArena、SWE-bench、ToolSandbox、AppWorld 和 τ-bench 等基准逐步提供了面向工具调用、网页操作、软件工程和有状态应用交互的评价环境[37-41]。在此类环境中，任务是否完成往往需要结合执行轨迹、工具返回结果和环境最终状态进行判断，单纯依赖模型自我报告或文本相似度难以充分反映真实任务能力。

智能体的设计空间具有明显的组合特征。一方面，模块实现具有类别属性，例如规划策略可以选择不同的任务分解方式，工具路由可以选择规则式、模型式或混合式策略，记忆模块可以选择不同的读写机制；另一方面，模块之间具有接口、权限、调用顺序和数据依赖等硬约束。由此形成的搜索空间既不是简单连续参数空间，也不完全等同于无约束的离散字符串空间。对每一个候选配置，都需要检查其是否满足模块接口、工具权限和执行流程要求，并在统一环境中评价其任务表现。

此外，Agent 的适应度评价具有随机性和任务异质性。同一配置在不同任务实例、不同初始状态或不同模型采样结果下可能产生不同表现；不同任务家族对模块能力的需求也可能不同。若直接使用少量任务上的平均成功率进行选择，可能将偶然高分的配置误认为稳定优势，也可能使只适合某一任务类型的模块组合在种群中占据优势。因此，智能体演化优化需要关注模块交互效应的估计可靠性、任务分布差异以及评价噪声对选择和重组的影响。

演化计算为这一问题提供了合适的研究框架。与仅进行逐项参数调整的方法相比，种群式演化能够同时维护多个候选配置，并通过选择、变异和重组探索不同模块组合；与单次启发式搜索相比，演化过程可以记录个体谱系、模块组合和搜索反馈，支持可重复的算法对照。然而，若重组算子不考虑模块之间的交互和接口约束，随机交换模块可能破坏原有协同结构，产生大量不可执行或性能下降的子代。因此，需要将组件交互知识与演化计算中的 linkage、FOS、donor mixing 和接受策略建立明确联系。

### 2.2 研究目的

本课题拟研究面向大语言模型智能体的交互感知演化优化方法，目标不是简单地使用现有遗传算法搜索提示词或工作流，而是围绕智能体模块组合中的非加性依赖，研究可识别、可解释并能够服务于演化重组的算法机制。

具体目标包括：

（1）建立适用于智能体模块配置的结构化表示方法。将智能体表示为由若干功能槽位组成的类别型基因型，每个槽位对应一个可替换模块实现，并通过类型、输入输出接口、调用依赖和权限规则定义合法配置空间，使演化个体具有明确的执行语义。

（2）研究任务条件化的组件交互结构估计方法。针对智能体执行结果具有随机性、不同任务家族表现存在差异以及部分模块组合受到硬约束等特点，研究如何区分模块主效应与交互效应，估计交互关系的方向、强度和不确定性，并对缺乏共同支持或不可识别的交互作出明确判断。

（3）研究交互结构驱动的约束最优混合演化算法。将估计得到的交互结构转化为 linkage/FOS，在满足接口和调用依赖的前提下进行模块块级重组，研究 donor 选择、确定性最小修复和随机适应度下的序贯接受机制，验证交互感知重组是否能够提高演化搜索效率和最终智能体任务表现。

（4）探索演化算法参数的合理配置与在线控制。采用训练任务上的离线自动调参确定关键参数，并研究根据子代实际改进反馈调整变异强度和算子选择的可行性；统计检验阈值、硬约束和测试集规则在实验前固定，避免通过测试结果反向调整算法。

（5）在前述研究成立的基础上，进一步考察不同任务家族之间是否存在可迁移的共享交互结构，分析交互结构迁移对新任务适应的帮助及其负迁移风险。该部分作为条件性扩展，不预先承诺形成独立创新点。

### 2.3 研究意义

**理论意义。** 本课题尝试将大语言模型智能体模块组合问题与演化计算中的变量依赖学习、linkage learning 和最优混合重组联系起来。研究重点从“某个模块是否有效”推进到“模块组合在特定任务和配置背景下是否存在非加性依赖”，有助于分析智能体模块组合的协同与拮抗机制。同时，通过区分统计相关、适应度交互和演化重组所需的 linkage 结构，进一步明确交互估计结果转化为演化搜索结构时的理论条件。

**方法意义。** 本课题拟在类别型模块配置、合法配置约束和随机任务评价条件下，研究任务条件化交互估计与约束最优混合演化方法。其方法贡献需要通过与普通遗传交叉、GOMEA/GOM、Conditional GOM、LK-GOMEA、fitness-based linkage learning 以及现有 Agent 自动搜索方法的对照实验加以验证。如果所提出机制不能在相同评价预算和相同模型条件下带来可重复的搜索收益，则应对相应创新主张进行修订或停止。

**应用意义。** 智能体系统在软件工程、办公自动化、网页操作和工具调用等场景中通常包含多个可配置模块。若能够自动识别模块之间的有效组合关系，并在不违反接口与权限约束的前提下进行演化优化，将有望减少人工设计和反复试错的工作量，提高智能体在复杂任务中的执行成功率、可靠性和跨任务适应能力。研究形成的结构化配置、评价协议和演化算法也可为其他模块化智能系统的自动配置提供参考。

## 三、国内外研究现状及发展动态

### 3.1 大语言模型智能体及其评价研究

早期智能体研究主要关注语言模型如何结合外部工具和环境反馈完成多步任务。ReAct 将思维过程与行动过程交替组织，使模型能够根据观察结果继续决策[1]；Reflexion 通过执行反馈形成可复用的语言经验，提升后续尝试表现[2]。这类工作说明，Agent 的实际能力不仅取决于单轮语言生成，还取决于工具使用策略、执行流程和反馈机制。

随着智能体任务复杂度提高，评价基准逐步由静态问答扩展到真实交互环境。AgentBench 从多个交互环境评价语言模型的智能体能力[41]；WebArena 提供具有真实网站功能的网页操作任务[44]；SWE-bench 将软件工程问题转化为真实代码仓库中的问题修复任务[40]。ToolSandbox 强调有状态、对话式和交互式工具使用评价[37]；AppWorld 提供多个日常应用及程序化状态检查机制[39]；τ-bench 则在航空和零售领域模拟用户与工具交互，并根据最终数据库状态评价任务完成情况[38]。这些基准为智能体结构优化提供了更接近真实执行过程的评价环境。

现有基准也带来新的实验要求：智能体配置的评价不能只记录最终自然语言回答，还应记录工具调用、状态变化、任务是否完成以及是否产生非预期副作用。对于演化优化而言，必须固定模型版本、任务划分、工具接口和评价规则，并在训练、验证和测试任务之间建立严格隔离，防止演化算法针对测试任务反复优化。

### 3.2 智能体自动设计与演化优化研究

近年来，智能体自动设计逐渐从人工构建转向搜索和自动生成。ADAS 通过元智能体生成候选 Agent 系统，并利用执行结果进行评估[3]；AgentSquare 将 Agent 抽象为规划、推理、工具使用和记忆等模块，在模块化设计空间中搜索[4]；AFlow 将智能体工作流表示为可修改的程序结构，并通过搜索过程生成和优化工作流[5]；MaAS 利用 Agentic Supernet 进行多智能体架构搜索[15]；AgentSwift 通过价值引导的层次化搜索提高 Agent 设计效率[16]。GPTSwarm 则将语言智能体表示为可优化图结构，研究节点和连接关系的优化[6]。

在演化算法直接用于 Agent 生成方面，EvoPrompt 将语言模型与演化算法结合，对离散提示词进行优化[7]；Promptbreeder 进一步将任务提示词与变异提示词共同演化[8]；EvoAgent 通过遗传操作生成不同专家 Agent，并扩展到多智能体系统生成[9]。Hu 等提出的 Evolutionary Generation of Multi-Agent Systems 将多智能体系统生成表示为结构化配置空间中的演化搜索，利用执行轨迹反馈指导变异和交叉[10]。Wei 等提出的另一篇 EvoMAS 则研究启发式策略参与的工作流演化，涉及多种演化策略、自适应策略选择和角色级演化[11]。两篇工作虽然名称相近，但研究机制和作者不同，需要分别比较。

此外，EvoCF 通过从失败经验中提取规则并进行反事实协作计划演化[12]；HFlow 将工作流结构、提示词和模型骨干等纳入演化，并结合人类偏好与多目标选择[13]；GEPA 通过反思反馈和 Pareto 机制优化提示词及候选系统[14]；MASS 等工作进一步研究多智能体提示词与拓扑的分阶段优化[17]；TPGO 通过文本参数图和执行轨迹反馈优化多智能体系统[18]。经典多目标演化算法 NSGA-II 与 MOEA/D，以及质量多样性方法 MAP-Elites，为多目标搜索和多样性维护提供了重要方法基础[28-30]；但本课题不将这些算法直接应用于 Agent 作为创新。上述研究表明，Agent 的模块、工作流和协作结构已成为自动优化对象。

2026 年的新近工作进一步提高了相关研究的覆盖范围。Agentic Harness Engineering（AHE）通过组件、经验和决策可观测性，将 coding-agent harness 的修改转化为可核验的编辑闭环[58]；其分析还明确指出 harness 组件存在非加性交互，叠加单项有效修改会出现收益上限，且其自归因机制对修复较可靠、对回归问题仍可能失明[58]；其报告的十轮改进来自单次演化 campaign，因此不能替代多随机种子重复验证；本课题后续应采用多 seed、同 rollout budget 和配对任务统计[58]；SkillFlow 则使用 flow-based 训练信号学习多轮任务编排策略，并根据轨迹诊断递归创建或剪枝技能[59]；FusionFlow 通过融合多个独立演化的工作流，尝试突破单一工作流逐步优化的结构深度限制[61]。这些工作意味着通用的 harness 自我改进、技能演化和工作流融合均已有直接先例，必须纳入候选方法的强基线与差异审查。

现有工作的共同趋势是：一方面，搜索对象由单一 Prompt 扩展到模块、工作流、角色和拓扑；另一方面，搜索机制从简单变异逐渐加入执行反馈、候选档案、经验记忆、启发式策略和多目标选择。由此可见，普通模块编码、遗传交叉、反馈引导变异或 Pareto 选择均不能直接作为本课题的创新点。需要进一步回答：现有方法是否显式估计同一 Agent 配置内部模块之间的非加性交互？如果估计了交互，是否将其转换为适合演化算法的 linkage 结构？在随机任务评价和合法配置约束下，这种结构是否仍然可靠？

### 3.3 组件贡献、交互效应与信用分配研究

智能体由多个模块共同完成任务，单独评价模块贡献存在一定局限。模块的效果可能依赖其他模块的配置：某种规划策略只有与特定工具路由方式组合时才有效；某种记忆机制可能提高长任务表现，却增加工具调用和上下文干扰；验证机制可能在部分任务上改善可靠性，但在另一些任务上引入额外步骤。若只估计模块主效应，可能忽略组合层面的协同或拮抗作用。

现有研究已从不同角度分析组件贡献和交互。Optimas 研究如何为系统组件构造与全局表现对齐的局部奖励[45]；HiveMind 使用贡献估计指导多智能体系统中的 Prompt 优化[46]；CCI 等工作对多个 Agent scaffold 组件进行因子组合实验，并分析主效应和组件间交互[47]；Prompt 组件回归研究则使用统计模型分析提示词组成部分对模型表现的影响[48]。这些工作说明，组件贡献和交互并非空白领域。 另外，ShapleyFlow 在固定工作流结构下，将组件模型升级作为合作博弈参与者，在四组件、九种代表性 LLM 的设置下评估全部 2^4 种升级组合，并在 1,500 余项、七个领域任务的 CapaBench 上计算 Shapley 贡献，用于交互感知归因和模型配置推荐[60]。这进一步说明，组件交互归因并非空白；但其研究对象主要是固定工作流中的模型升级分配，不等同于任务条件化、类别型合法配置空间中的稀疏局部 linkage 估计，也没有直接将估计结果转化为演化算法的 FOS。后续实验必须将 ShapleyFlow 作为强归因基线，而不能把“首次分析组件交互”作为创新表述。

本课题不拟重复普通组件消融、Shapley 贡献分配或简单 pairwise 回归，而是关注交互估计如何与演化计算中的 linkage 结构建立可执行接口。具体而言，需要区分三个问题：第一，某两个模块是否在统计意义上相关；第二，在给定其他模块背景和任务上下文时，两个模块是否对目标效用产生非加性影响；第三，该非加性影响是否足以支持演化算法将两个模块作为联合重组单元。三个问题相关但不等价，必须通过明确的估计量、合法配置支持和演化搜索实验进行验证。

### 3.4 演化计算中的 Linkage Learning 与最优混合重组

在传统演化计算中，变量之间的依赖关系会影响交叉和重组的效果。若相互依赖的变量被独立改变，可能破坏已有的高质量组合；若无关变量被过度绑定，则会降低搜索灵活性。Linkage learning 的目标是识别变量之间的依赖结构，并将其用于构造变量子集或重组单元。

GOMEA 通过学习变量依赖结构构造 Family of Subsets（FOS），并利用 Gene-pool Optimal Mixing 在不同变量子集上尝试从供体个体引入基因[19]。Conditional GOM 进一步考虑条件依赖关系。Dushatskiy 等对参数无关的 GOMEA 及其最优混合机制进行了系统研究[19]。针对多结构问题，Guijt 等提出 Linkage Kernels，使不同个体能够使用不同的局部 linkage 结构[20]。

除基于种群统计依赖的 linkage learning 外，已有研究还直接从适应度变化中估计变量依赖。Olieman 等提出面向实值 GOMEA 的 fitness-based linkage learning，通过目标函数扰动和差分识别变量依赖[21]；Andreadis 等进一步研究 fitness-based linkage 与最大团条件 linkage 建模的结合[22]。DLED 通过在给定个体附近改变变量并比较适应度，识别直接依赖[23]；cDLED 将这种思想扩展到多结构问题，对不同个体学习局部依赖结构[24]。此外，LMM 和 ALI/AIM 等工作研究了噪声环境下的变量分解与 linkage 识别[25-26]；近期研究还探索从遗传算法搜索过程的副产物中提取变量重要性和交互信息[27]。

上述研究对本课题有两方面影响。一方面，它们证明利用目标函数交互指导演化重组具有理论和方法基础；另一方面，它们也意味着本课题不能宣称首次提出 fitness-based linkage、局部 linkage 或噪声环境下 linkage 学习。真正需要验证的是：在 Agent 任务中，任务上下文、随机 rollout、类别型模块和合法组合约束是否带来已有方法未充分解决的具体问题；所提出的估计器能否在同等评价成本下改善局部 linkage；这种改善能否进一步提高 GOM 的搜索表现。

### 3.5 国内相关研究进展

国内关于大语言模型智能体的研究已从概念综述和架构构建逐步扩展到垂直领域应用、技能积累与智能体动态演进。陈旭在中国计算语言学大会论文中系统梳理了大语言模型自主智能体的设定、记忆、规划和行动模块，并讨论了从单体到多智能体系统的交互机制[51]；周涛等从概念、技术前沿和产业实践角度总结了大模型智能体的发展与应用[52]。这类研究为本课题界定 Agent 的模块化组成和应用背景提供了国内文献依据，但主要属于综述和体系归纳，并未提出演化计算驱动的 Agent 组件搜索算法。

在具体应用方面，卢宇等提出面向项目式学习的教学智能体框架，设置教育任务、规划、能力扩展、内容记忆与反思、交互协作和动态进化等模块[53]；黄悦欣等面向智慧城市构建垂直领域大语言模型智能体，结合多源数据、混合检索、多路径推理和提示优化提升系统能力[54]。袁雪峰等提出电力仿真智能体的“决策—执行—反馈—学习”闭环，将成功轨迹转化为结构化技能库，并训练技能评估模型预测执行成功率[55]。这些工作体现了国内在 Agent 架构、技能积累和应用层动态演进方面的探索，但从公开摘要和论文信息看，尚不能将其等同于基于种群的演化计算搜索，也没有证据表明其使用了组件交互 linkage 和 GOM 重组。

国内研究团队也开始探索大模型与演化计算的结合。Song 等提出 MAESD，将多智能体框架用于蛋白质序列设计，并在序列生成与筛选中引入演化式优化[56]；该工作说明多智能体与演化搜索可以在复杂设计任务中结合，但优化对象是蛋白质序列，而不是 Agent 自身的模块配置。She 等提出 BIOME，以大语言模型辅助群体智能优化算法的生成、改进和进化[57]；其研究方向是“LLM 赋能演化算法”，与本课题“演化计算优化 LLM Agent”的方向相反，因此应作为相邻研究进行区分，而不能直接作为本课题的同类方法。

总体而言，国内已有研究为智能体模块设计、垂直应用、技能库和大模型—演化计算交叉提供了基础，但面向 Agent 配置内部交互结构、并将其转化为受约束演化重组 linkage 的方法研究仍需进一步通过原文和实验核验。本节列出的国内文献为本轮检索到的代表性来源，并非对中文数据库和学位论文的穷尽性综述。

### 3.6 演化算法参数调节与自适应控制研究

演化算法的性能受种群规模、变异强度、重组方式、选择压力和停止条件等参数影响。参数设置研究通常区分离线参数调优与运行时参数控制。Eiben 等对演化算法参数控制进行分类，区分确定性、自适应和自适应进化等控制方式[31]；Eiben 和 Smit 从问题、演化算法与调参器三个层面讨论算法配置和参数调优[32]；Aleti 和 Moser 对自适应参数控制方法进行了系统综述[33]。

在离线配置方面，irace 通过候选配置采样和迭代竞赛逐步淘汰表现较差的参数组合，可用于包含数值参数和类别参数的算法配置问题[34]。在在线控制方面，自适应算子选择（AOS）通过信用分配和多臂老虎机等机制，根据历史算子表现调整其使用概率[35]。SHADE 则利用成功历史信息更新差分进化中的参数分布[36]。噪声演化优化研究系统讨论了噪声条件下的采样、估计和选择策略[42]，F-Race 等统计竞赛方法也为算法配置筛选提供了基础[43]。这些方法为本课题的参数调节提供了可借鉴的理论和工具，但其思想本身并非本课题的独立创新。

本课题拟采用分层参数策略：首先在训练任务上通过 irace 对少量关键参数进行离线配置；其次，在演化过程中根据配对评价得到的子代改进置信下界和评价成本，研究是否有必要通过 discounted-UCB/AOS 调整变异强度或算子动作；最后，将显著性水平、最小实际改进幅度和硬约束作为预先固定的统计门禁，不允许根据测试集表现反向调整。若在线控制不能在相同评价预算下优于离线调参后的固定策略，则删除在线控制模块，不将其包装为创新点。

### 3.7 现有研究不足与本课题切入点

综合上述研究，可以归纳出以下需要进一步研究的问题。

第一，Agent 组件交互和贡献归因已被多条路线研究。CCI 的全因子组合、Prompt component regression 和 ShapleyFlow 已覆盖组件组合分析或交互感知归因[47-48,60]，因此不能把普通组件交互发现、Shapley 归因或 pairwise 回归作为创新。仍需验证的窄问题是：在合法类别配置、任务异质和随机 rollout 下，预算受限的局部交互证据能否比现有归因与代理模型更可靠地支持演化搜索。

第二，演化计算中的 linkage learning、fitness-based linkage、DLED/cDLED、噪声 linkage 和局部 linkage 已有成熟先例[19-27]。智能体模块的类别类型、接口、权限和调用依赖可能带来特殊约束，但这些差异只有通过同预算强基线和真实 Agent 任务实验才能转化为方法贡献，不能仅凭问题对象不同宣称创新。

第三，Agent harness、skill 和 workflow 的自动改进已有 AHE、SkillFlow、FusionFlow、MESH-Harness、EvoMAS、HFlow 等工作覆盖[10-13,49,58-61]。因此，通用的执行反馈更新、技能递归演化、模块组合、工作流融合或 harness 编辑都不能单独作为创新。候选算法必须证明其局部 linkage 学习和约束最优混合机制具有不同于这些方法的可验证增量收益。AHE 报告的是单次十轮演化 campaign，其非加性收益和回归预测盲区也提示本课题必须采用多 seed、配对任务和完整回归验证。

第四，交互结构估计与演化搜索之间存在目标一致性问题。统计上可检测的交互不一定适合当前搜索个体的局部重组；全局平均交互也不一定代表每个配置背景下的依赖关系。因此，需要区分任务条件化的总体交互强度和当前搜索位置下的局部 linkage 证据，并通过固定、可复现的 FOS 构造方法连接统计估计和演化算子。

第五，Agent 执行结果存在任务内相关和随机波动，单次评价容易导致错误选择。需要通过同任务实例配对、重复执行、置信区间或序贯接受规则降低噪声对演化选择的影响，并严格匹配不同算法的 rollout 评价预算。

据此，本课题的切入点不是提出一种新的通用遗传算法，而是研究面向 LLM Agent 模块组合的交互感知演化优化方法：先估计可用于搜索的局部交互结构，再研究该结构如何驱动约束最优混合重组，并以真实工具任务检验其增量收益。国内研究现状已补入代表性综述、垂直领域 Agent、技能库和 LLM—演化计算交叉工作，但中文期刊、学位论文和国内团队成果仍未穷尽，后续继续检索，不将本轮检索写成全面综述。

## 四、研究目标、研究内容及拟解决的关键科学问题

### 4.1 总体研究目标

本课题拟建立一套面向大语言模型智能体模块配置的交互感知演化优化方法。通过结构化类别基因型描述 Agent 模块组合，通过任务条件化交互估计识别模块之间的非加性依赖，并将可信依赖转化为演化计算中的 FOS/linkage，进而设计满足模块接口约束的最优混合重组算子和随机适应度下的接受机制。最终在受控合成环境和真实工具使用任务中验证所提出方法能否在相同模型、任务、初始化和评价预算下提高搜索质量、执行成功率及结果稳定性。

### 4.2 研究内容一：任务条件化的 Agent 组件交互结构估计方法

该部分拟研究如何从多个模块组合的执行结果中估计主效应和非加性交互，并将估计结果转化为可供演化算法使用的交互结构证据。

首先，建立固定功能槽位的类别型配置表示。第一阶段考虑规划（Planning）、工具路由（Tool Routing）、记忆（Memory）和验证/恢复（Verification/Recovery）等功能槽位。每个槽位包含若干接口兼容的候选实现，配置表示为：

\[
x=(x_1,x_2,\ldots,x_m),\qquad x_i\in\mathcal C_i.
\]

通过类型、输入输出接口、工具权限和调用依赖构造合法配置集合：

\[
\mathcal X_{\mathrm{valid}}\subseteq\prod_{i=1}^{m}\mathcal C_i.
\]

其次，定义任务上下文和随机执行回报。设任务实例为 \(t\)，其可观察上下文为 \(z_t\)，执行随机性为 \(\omega\)，则配置 \(x\) 的执行回报记为 \(Y(x,t,\omega)\)，期望表现记为 \(\mu(x,z)\)。回报以程序化任务完成情况为主要依据，并可结合执行可靠性、资源消耗等辅助指标；具体标量化或多目标形式需在正式实验前冻结，不根据测试结果改变。

再次，研究组件主效应与交互效应的估计。对于两个类别槽位 \(i,j\)，在其他槽位背景 \(u\) 和任务上下文 \(z\) 给定时，可用四格有限差分描述二元实现对比下的条件交互：

\[
\Delta_{ij}(u,z)=
J(++u,z)-J(+-u,z)-J(-+u,z)+J(--u,z).
\]

其中 \(J\) 表示预先确定的目标效用。对于多类别模块，采用类别对比编码扩展该定义。拟采用任务条件化响应模型和稀疏层级估计，区分主效应与交互项，并通过后验不确定性、模型阶数敏感性和合法配置支持检查避免过度解释。对于无法形成共同合法支持的模块组合，不通过模型外推伪造直接交互证据，而是标记为不可识别或证据不足。

最后，研究交互结构的输出形式。初步考虑分别报告任务条件化的总体交互强度，以及当前搜索个体和任务上下文下的局部交互后验；将局部证据形成带权交互图（VIG/DSM），再交由固定的 Linkage Tree 或 Conditional FOS 构造方法生成 FOS。交互图不直接等同于 FOS，统计交互也不自动等同于重组依赖。该接口仍需独立复审和实验验证。

该研究内容的独立验证重点包括：已知真值下的交互恢复能力、不同任务家族下的交互结构变化、随机执行条件下的后验校准、不可识别状态判断，以及在相同评价预算下对未执行配置表现的预测能力。主要对照包括主效应模型、普通 pairwise OLS、固定设计、随机合法配置设计、fitness-based linkage、DLED/cDLED、LMM/ALI/AIM 和可复现的在线交互学习方法。

### 4.3 研究内容二：交互结构驱动的 Agent 约束最优混合演化算法

该部分拟研究如何将组件交互结构转化为演化计算中的联合重组单元，并在模块接口和随机评价约束下改进 Agent 配置搜索。

首先，采用类别型基因型表示 Agent 个体。每个个体对应一个可执行配置，种群中的个体通过选择、变异和重组产生。第一阶段不直接搜索任意代码或任意 DAG，而采用固定槽位和受控候选模块集合，以降低搜索空间复杂度并保证实验可复现。

其次，根据研究内容一输出的交互结构构造 FOS。对于具有可信非加性依赖的模块对，研究是否需要将其作为联合 mixing 子集；正交互和负交互均可能表示非加性依赖，不能仅依据交互符号决定是否建立 linkage。交互方向可作为 donor 兼容性和组合解释的辅助信息，但模块类型、接口、权限及调用依赖才属于硬约束。对于缺乏证据的边，不强制构造联合块；对于高阶或重叠依赖，需通过模型敏感性和相应 FOS 结构处理，不能将所有连通模块简单合并为一个大块。

再次，研究约束最优混合重组过程。对于父代个体 \(x\)、供体个体 \(d\) 和 FOS 子集 \(B\)，尝试将供体在子集 \(B\) 上的模块引入父代，形成候选子代。候选子代首先经过类型和接口检查，再检查工具权限和调用依赖；若存在可由确定性规则唯一修复的局部缺失，则执行最小修复并记录修复变化量；若修复无法唯一确定或需要大范围改动，则拒绝该候选，避免通过任意生成式修复改变实验变量。

最后，研究随机适应度下的配对评价和序贯接受机制。父代与子代应尽可能在相同任务实例、相同初始状态和可控随机种子下进行配对评价；若模型采样或环境随机性不能严格控制，则采用任务分块重复执行，并如实记录配对条件。根据配对差值的置信区间判断子代是否达到预先规定的非劣或改进标准，避免单次偶然高分导致错误接受。实验中分别比较 oracle linkage、learned linkage 和 random linkage，以区分交互估计误差与重组算子本身的效果。

该研究内容必须证明：在相同评价预算下，交互结构驱动的约束最优混合演化优于标准 GOM、随机重组和现有 Agent 自动搜索基线；提升不能仅来自额外 rollout、额外 repair、模型版本差异或更长提示词。

### 4.4 研究内容三：任务分布变化下的交互结构迁移与自适应演化（条件性扩展）

在研究内容一和研究内容二获得可靠结果后，进一步考察不同任务家族之间是否存在共享的模块交互结构，以及任务分布变化时局部交互关系如何改变。拟区分跨任务共享交互和任务特定交互，研究结构漂移检测、交互图迁移、局部更新和负迁移控制。

该部分将比较固定交互图、从头估计交互图、直接迁移交互图以及带结构变化检测的选择性迁移方法，并与已有跨任务 Agent 优化和局部 linkage 方法进行比较。只有在实验证明任务间存在稳定可迁移结构，且选择性迁移优于从头估计、直接迁移和独立演化时，才将其作为第三个独立创新点和小论文方向。若证据不足，则将其作为研究内容二的泛化实验，不为满足数量要求而强行形成第三篇论文。

### 4.5 拟解决的关键科学问题

**科学问题一：随机任务评价和合法配置约束下，如何识别具有实际意义的组件非加性交互？**  
组件交互受到其他模块背景和任务上下文影响；同时，某些组合可能因接口或权限约束而不可执行，随机 rollout 又会带来估计噪声。需要研究如何定义可解释的交互估计量、处理任务内相关和高阶模型失配，并区分“无交互”“证据不足”和“结构性不可识别”。

**科学问题二：如何将统计交互证据转化为真正有利于演化搜索的 linkage/FOS？**  
统计交互图并不自动等同于 GOMEA 的 FOS。需要研究全局交互、局部交互与当前个体重组结构之间的关系，明确 FOS 构造、donor 选择和局部重组的条件，并通过 oracle linkage 与 learned linkage 对照证明该结构能够提高搜索效率。

**科学问题三：在硬约束和随机适应度条件下，如何保持演化重组的可执行性与选择可靠性？**  
模块替换可能破坏类型、接口、权限和调用依赖；随机任务评价又可能使一次偶然高分误导选择。需要研究确定性最小修复、无效子代拒绝、配对评价和序贯接受规则，保证算法提升来自有效重组而非约束违规或额外评价。

## 五、预期创新点

本课题拟围绕两个核心创新点开展研究，第三个创新点作为条件性储备。以下均为预期创新，不代表已经通过实验验证。

### 5.1 创新点一：面向任务条件和合法配置空间的 Agent 组件交互结构估计方法

针对现有组件消融和主效应分析难以描述模块非加性组合关系、普通 pairwise 回归容易受到任务异质性和随机评价影响的问题，拟研究任务条件化的组件交互估计方法。该方法以类别型模块配置为输入，区分主效应和交互效应，结合稀疏层级估计、合法配置支持检查和不确定性校准，输出具有任务条件、局部背景和可信程度的交互结构证据。

预期贡献不在于首次提出组件交互分析或 fitness-based linkage，而在于针对随机 Agent rollout、任务异质和合法模块组合条件，研究更适合后续演化重组的交互估计与不确定性处理方法。其有效性将通过合成真值实验、真实 Agent 任务预测实验及同评价预算下的强基线对比验证。

### 5.2 创新点二：交互结构驱动的 Agent 约束最优混合演化方法

针对普通模块交叉容易破坏高质量模块组合、忽略接口依赖且在随机适应度下容易发生误接受的问题，拟研究交互结构驱动的约束最优混合演化方法。该方法将可信交互结构转化为 FOS/linkage 子集，在 GOM 框架下执行模块块级供体混合，并结合类型/接口/调用依赖检查、确定性最小修复和配对序贯接受机制。

预期贡献是建立从 Agent 组件交互估计到演化重组操作的完整算法接口，并通过 oracle linkage、learned linkage、random linkage 和标准 GOM 等对照，验证交互感知重组是否具有独立的增量收益。若实验表明其仅相当于现有 GOMEA/cDLED 的直接应用，或收益完全来自额外评价和修复，则应修改或否定该创新主张。

### 5.3 创新点三（条件性）：任务分布变化下的交互结构迁移与自适应更新

若前两个研究内容证明交互结构能够稳定识别并改善演化搜索，进一步研究任务家族变化时共享交互和任务特定交互的分离、迁移和更新机制。预期研究选择性迁移和结构漂移检测，以降低新任务上重复识别交互结构的成本，并控制负迁移。该方向必须通过独立新颖性审查，且证明其优于固定结构、直接迁移、从头估计和已有在线 Agent 优化方法后，才作为第三个正式创新点。

## 六、研究方案及可行性分析

### 6.1 总体研究方法

本课题采用“文献与机制分析—结构化问题建模—合成真值验证—真实 Agent 任务验证—演化算法对照—消融与泛化测试”的研究路线。研究以演化计算为核心，不以单纯工程集成或增加模型调用次数作为贡献。

首先，固定 Agent 的功能槽位、候选模块、接口和任务评价协议；其次，在已知真值的合成配置空间中验证交互估计器；然后在真实工具使用任务中检验估计器的预测能力；在此基础上，研究交互结构驱动的 GOM 重组算子；最后通过强基线、消融和跨任务测试判断方法是否有效。

### 6.2 Agent 个体表示与合法配置空间

第一阶段采用固定槽位的类别型基因型。拟选择四个功能槽位作为最小实验对象：规划、工具路由、记忆和验证/恢复。每个槽位设置两个接口兼容的抽象实现，形成 \(2^4=16\) 个候选配置，用于建立可完全枚举的合成真值空间。该设置用于验证方法，不意味着真实 Agent 永远只有四个模块或每个模块只有两个实现。

每个候选模块应声明输入输出类型、前置条件、后置条件、权限需求和调用依赖。配置合法性由确定性 contract checker 判断。第一版不进行任意代码生成或任意 DAG 搜索，以保证模块组合的语义清楚、实验可复现，并降低不可执行个体对评价结果的污染。

### 6.3 研究内容一的算法方案：TCAIL 候选方法

研究内容一暂以 TCAIL（Task-Conditioned Active Interaction Learning）作为工作代号。其目标是识别具有实际意义的任务条件化组件交互，并给出不确定性和可识别性状态。

（1）**类别效应编码。** 对每个功能槽位采用类别型对比编码，任务上下文包括任务家族、任务难度和部署前可观察的任务属性。不得将测试答案、金标或事后才可获得的信息作为任务上下文输入。

（2）**稀疏交互估计。** 在主效应模型基础上增加成对交互项，采用 Group-ARD 或其他经验证的层级稀疏估计方式抑制无证据交互项。对于二元配置，可通过四格有限差分定义条件交互；对于多类别模块，采用预先规定的类别对比方式。

（3）**任务和局部背景条件化。** 不将所有任务和配置背景简单平均为一张静态图。初步方案区分总体任务条件交互强度与当前 parent/任务上下文下的局部依赖证据。全局 RMS 交互强度仅作为总体交互能量摘要，不直接等同于当前个体的 FOS；局部后验交互证据形成 local weighted VIG，再由固定 FOS builder 构造 linkage 结构。该接口尚待独立复审，不能在实验前认定其优于已有方法。

（4）**合法支持与可识别性门禁。** 对每条候选交互边检查相关配置是否具有共同合法支持、设计矩阵是否可识别以及后验是否足够稳定。对于结构性不可识别、模型阶数敏感或证据不足的边，分别记录状态，不将其强制判定为无交互或高置信度依赖。

（5）**主动实验设计。** 在合法配置候选集中选择下一批值得执行的配置，优先降低关键交互结构的不确定性。主动采样只作为提高估计效率的候选机制，必须与随机设计、固定分数因子设计、D-optimal 设计和其他信息增益方法进行比较。若主动采样没有带来同预算下的实际收益，则删除该模块。

（6）**随机评价和不确定性校准。** 对同一任务实例尽可能使用配对执行和相同随机种子；无法控制模型采样随机性时，使用 task-blocked repeated runs，并报告其限制。通过独立任务块重采样、后验区间覆盖率和 null 场景虚假边率检查估计可靠性。

### 6.4 研究内容二的算法方案：CI-GOM 候选方法

研究内容二暂以 CI-GOM（Interaction-aware Constrained Gene-pool Optimal Mixing）作为工作代号。其核心是将交互结构引入类别型 Agent 配置的最优混合演化。

（1）**种群初始化。** 在合法配置空间内生成初始种群，记录每个个体的模块配置、任务表现、执行轨迹摘要和配置哈希。初始化策略在所有基线中保持一致。

（2）**FOS 构造。** 根据研究内容一得到的可信局部交互图，使用预先固定的 Linkage Tree 或 Conditional FOS 构造方法生成变量子集。第一阶段优先研究单槽位与可信成对 linkage，避免把一条链式边直接扩展成过大的联合块。高阶依赖只有在模型和实验支持后再扩展。

（3）**供体选择与最优混合。** 对每个父代选择供体个体，在 FOS 子集上尝试替换模块。供体优先满足接口和硬约束要求；交互符号和后验不确定性可以作为软兼容性信息，但不能将负交互直接解释为非法组合。

（4）**确定性最小修复。** 对候选子代检查类型、接口、权限和调用依赖。如果存在唯一且预先定义的最小修复，则执行并记录修复内容；如果无法确定修复或修复幅度超过预设范围，则拒绝候选。修复规则不得由 LLM 自由生成，以避免不同候选受到不一致处理。

（5）**随机适应度下的接受机制。** 在相同任务块上配对评价父代与子代，根据预先确定的置信下界或序贯检验规则决定是否接受。需要分别报告任务成功率、有效子代率、误接受率和评价次数，避免单次偶然高分导致种群更新偏差。

（6）**种群和谱系更新。** 对被接受的个体记录父代、供体、重组子集、修复操作、评价任务块和性能变化，形成可审计的演化谱系。该信息用于后续分析算子贡献，但不将谱系统计本身预先作为创新点。

### 6.5 演化计算参数调节方案

本课题将参数分为三类，避免所有参数都凭经验固定或同时在线变化。

**第一类：离线算法配置参数。** 在训练任务上采用 irace/iterated racing 搜索少量关键数值和类别参数，包括稀疏正则强度、FOS 遍历顺序、donor 选择策略、交互图更新间隔，以及在线控制器的探索系数和历史折扣等。离线调参仅使用训练任务，验证任务用于选择稳健配置，测试任务不参与调参。所有对照算法应获得公平的调参预算。

**第二类：在线自适应控制参数。** 初步考虑使用 discounted-UCB/AOS，根据不同变异和重组动作产生的配对子代改进置信下界及评价成本，调整动作使用倾向。动作集合可包括单槽位变异、多槽位变异、正向 linkage block mixing 和条件供体混合。在线控制只作用于预先定义的动作选择，不允许任意修改统计规则和硬约束。

**第三类：统计门禁参数。** 显著性水平、最小实际改进幅度、最大重复评价次数、合法性规则和序贯检验方式在正式测试前固定，不纳入以测试表现为目标的调参过程。

参数实验采用四组消融：A 为默认参数和固定算子概率；B 为 irace 离线调参和固定算子概率；C 为默认参数和在线 discounted-UCB/AOS；D 为离线调参加在线控制。四组使用相同评价预算。如果 D 不能稳定优于 B，则删除在线控制，保留离线调参后的固定策略。由于主算法采用类别型基因和 GOM，不将差分进化专用的 \(F\)、\(CR\) 参数直接移植到本算法中。

### 6.6 技术路线与实验阶段

**阶段一：合成真值交互地形验证。**  
构造四个二元功能槽位、共十六种配置的受控环境，预先设定主效应、正负二阶交互、任务家族条件变化、少量高阶交互和不同噪声水平。由于真实交互真值已知，可以直接评价估计器的交互恢复能力。比较全因子参考、随机合法设计、固定分数因子设计、主效应模型、pairwise OLS、稀疏交互估计和主动采样方法。主要指标包括交互 RMSE、边 AUPRC/F1、方向准确率、后验区间覆盖率、虚假边率、未执行配置预测误差和预算—精度曲线。

**阶段二：真实 Agent 任务小规模试验。**  
在 ToolSandbox、AppWorld 或 τ-bench 等具有工具交互和状态检查能力的环境中选择一个作为首个真实任务平台。固定基础模型、Prompt 模板、工具接口和评分器，选取四个功能槽位及其可执行候选实现，先进行小规模 pilot 估计任务方差和执行成本，再确定正式样本量。训练、验证和 held-out 测试任务按任务家族隔离。所有配置在相同任务实例和可控随机种子条件下进行配对评价；无法严格配对时，采用分层重复执行并如实说明。

**阶段三：演化重组算法验证。**  
在同一类别型 genotype、相同初始种群、相同模型和相同 rollout-equivalent 预算下，对比 standard GA、mutation-only、random crossover、标准 GOM/GOMEA、Conditional GOM、LK-GOMEA、oracle linkage、random linkage、learned linkage，以及相关 Agent 自动搜索方法。先使用 oracle linkage 判断交互感知重组的理论上界，再使用估计得到的 linkage 进行端到端实验。若 oracle linkage 也不能改善搜索，则说明当前重组假设不成立；若 oracle 有效但 learned linkage 无效，则说明交互估计是主要瓶颈。

**阶段四：消融和跨任务泛化。**  
分别去掉任务条件化、稀疏交互估计、主动采样、局部 linkage、约束修复和序贯接受模块，分析各机制的增量贡献。最后在 held-out task family 上测试最终冻结算法，报告不同任务家族的平均表现、最差表现和性能波动。跨任务交互结构迁移仅在前述实验通过后启动。

### 6.7 对比基线

为保证实验结论可信，基线分为四类。

（1）**基础搜索方法：** 随机合法配置搜索、标准遗传算法、mutation-only、随机模块交叉和固定参数 GOM。

（2）**经典演化计算方法：** GOMEA/Linkage Tree GOM、Conditional GOM、LK-GOMEA、DSMGA-II，以及适合当前类别型配置空间的其他 linkage learning 方法。对于原论文面向数值变量的方法，需要明确说明适配方式，不将自行修改版本冒充原论文原始实现。

（3）**交互估计与统计基线：** 主效应模型、pairwise OLS、稀疏交互回归、fitness-based linkage learning、DLED/cDLED、LMM、ALI/AIM、固定设计和主动信息设计。所有方法使用相同的合法配置集合、任务块和评价预算。

（4）**Agent 自动设计方法：** EvoAgent、两篇不同的 EvoMAS、AgentSquare、ADAS、AFlow、HFlow、GEPA、AgentEvo、MESH-Harness[49]、ARTEMIS[50]、AHE[58]、SkillFlow[59]、ShapleyFlow[60] 和 FusionFlow[61] 等。若无法直接复现某个方法，则应说明使用论文公开设置进行的可比适配，不夸大复现程度。

### 6.8 评价指标

交互估计层面主要报告：交互效应 RMSE、边 Precision/Recall/F1、AUPRC、正负方向识别准确率、后验区间覆盖率、null 场景虚假边率、不可识别状态判断准确率、未执行配置预测误差和单位评价成本下的交互恢复效果。

演化搜索层面主要报告：任务成功率、合法子代比例、有效重组比例、子代配对改进概率、误接受率、harmful recombination rate、best-so-far performance、达到指定成功率所需 rollout 数、不同任务家族上的泛化表现，以及修复次数和修复幅度。

资源指标包括 rollout 数、工具调用次数、token 数、wall-clock 时间和货币成本。不同单位分别报告，不将它们随意相加形成缺乏解释的综合成本。所有方法应在相同任务、模型、初始化和评价预算下比较。

### 6.9 统计分析方法

实验采用多个独立随机种子和任务实例。合成实验以独立 landscape 为主要重采样单位；真实 Agent 实验以任务实例或任务块为主要分析单位。对同一任务实例上的不同算法结果进行配对比较，报告均值、中位数、效应量和 95% 置信区间。二元任务成功率可使用配对比例检验或相应的广义线性混合模型；连续指标可采用配对置换检验或适当的非参数方法。多基线、多指标比较采用预先指定的 Holm 等多重比较校正。

所有主要假设、指标、任务划分、停止条件和统计门槛应在最终测试前确定。不能只报告表现最好的任务、随机种子或预算点；也不能通过反复查看测试结果选择超参数或阈值。

### 6.10 可行性分析

**研究问题具有可操作性。** 智能体模块配置可表示为固定槽位的类别型基因，能够通过模块接口和执行契约定义合法空间；四槽位、每槽位两个实现的十六配置空间可以完整枚举，适合先验证交互估计和重组机制的正确性。

**演化计算方法有成熟基础。** GOMEA、GOM、Conditional GOM、linkage learning 和参数控制等研究提供了可比较的理论与算法基础。本课题不需要从零构造完整演化算法，而是在类别型 Agent 配置、合法性约束和随机任务评价条件下，研究交互结构学习和重组机制的适配与改进。

**实验能够分阶段实施。** 首先通过无需真实 LLM 的合成真值实验验证统计估计和算法接口，再进入真实 Agent 工具任务。这样可以将统计模型错误、linkage 构造错误和真实 Agent 执行噪声分开分析，降低一开始直接开展大规模模型实验的风险。

**研究结果具有明确的证伪条件。** 如果组件交互在真实任务中没有稳定预测价值，则不继续将其作为核心机制；如果 oracle linkage 不能改善 GOM 搜索，则停止或修改交互感知重组方案；如果在线参数控制不优于离线调参固定策略，则删除在线控制；如果第三项跨任务迁移没有独立收益，则只保留两个核心研究内容。这些停止条件有助于控制研究范围，避免为了形成三个创新点而降低方法标准。

## 七、现有研究基础及成果

截至本报告初稿形成时，本课题已完成以下前期工作。

（1）**建立了独立的开题研究资料体系。** 已建立本课题专用研究仓库，对研究边界、文献检索流程、文献登记、机制比较、决策日志和会话交接进行统一维护。当前文献登记已包含 Agent 自动设计与演化、组件交互、演化计算 linkage learning、噪声适应度、参数控制和 Agent 评价基准等多个方向的资料。文献登记用于支持后续精读和引用核验，不代表已经完成全部文献的穷尽检索。

（2）**完成了主要研究方向的初步筛选。** 已对 EvoAgent、EvoMAS、EvoCF、HFlow、GEPA、AgentSquare、ADAS、AFlow、MESH-Harness 等 Agent 自动设计和演化方法进行机制级比较；同时补充了 GOMEA、fitness-based linkage、DLED/cDLED、LMM、ALI/AIM 和 Linkage Kernels 等演化计算先行工作。由此明确普通模块交叉、一般 Pareto 选择、普通组件消融和简单自适应算子选择不能单独作为本课题创新。

（3）**形成了两个核心研究内容的初步算法方案。** 已建立类别型 Agent 配置表示、任务条件化交互估计、合法配置可识别性门禁、交互图到 FOS 的接口，以及约束最优混合演化的初步设计。演化参数调节方面，已形成离线 irace 配置、在线 discounted-UCB/AOS 候选控制和统计门禁固定的分层方案。

（4）**开展了算法规格审查。** TCAIL 的形式化规格已完成多轮审查，但最新独立审查仍提出需要修订的问题，尤其是交互 estimand、模型阶数敏感性、任务块相关、最终边决策和演化 linkage 接口等方面。针对其中 linkage 接口问题，已形成新的修订提案，尚待独立复审。因此当前算法仍处于设计和审查阶段，不能写成已经实现或通过实验验证。

（5）**尚未形成正式实验结果。** 截至本报告初稿形成时，尚未完成本课题的正式 Phase 0 合成真值实验，也未开展真实 Agent 基准上的正式对比实验。当前不将其他独立项目的实验结果或工程成果作为本课题研究基础，不将算法设计文档等同于实验成果。

总体而言，本课题已具备较明确的研究对象、问题定义、相关工作基础、算法候选和实验路线，但仍需通过合成真值实验和真实 Agent 任务验证算法假设，后续研究将以实验结果和独立审查结论为依据逐步确定最终创新点。

## 八、可能遇到的困难、问题及对策

### 8.1 组件交互效应难以可靠识别

**可能问题：** 模块组合的效果可能受到其他模块背景和任务类型影响，简单平均会掩盖局部交互；随机 rollout 还会导致交互估计波动。

**拟采取对策：** 先在已知真值的合成环境中验证估计量；真实任务采用任务分块和配对执行；报告总体交互和局部交互的区别；通过模型阶数敏感性、后验校准和独立任务块重采样检查稳定性。对于证据不足或结构不可识别的交互，明确 abstain，不强行输出边。

### 8.2 合法配置空间不完整或交互不可识别

**可能问题：** 部分模块组合可能违反接口、权限或调用依赖，导致四格反事实比较不完整，统计模型可能依赖外推而产生虚假交互。

**拟采取对策：** 为每个模块定义输入输出类型和依赖契约；先由 contract checker 生成合法配置集合；对每条交互检查共同合法支持和设计矩阵可识别性；不能直接识别的交互标记为不可识别，不将其作为高置信度 linkage。

### 8.3 高阶交互导致 pairwise 模型失配

**可能问题：** Agent 多个模块可能存在三阶或更高阶交互，单纯 pairwise 模型可能把高阶效应投影为错误的两两关系。

**拟采取对策：** 在合成环境中设置三阶和更高阶压力测试；比较不同模型阶数下的边估计和留出预测；对于模型结论敏感的边，不纳入强制重组结构；必要时限制第一阶段研究主张适用的交互阶数，并将超出范围的情况列为后续研究。

### 8.4 交互图未必能够改善演化搜索

**可能问题：** 即使统计上识别出交互关系，也可能无法转化为有效的 FOS；局部图可能随搜索位置变化，错误的块级重组可能造成性能下降。

**拟采取对策：** 先比较 oracle linkage、random linkage 和 learned linkage；使用固定 FOS builder 隔离交互估计器与聚类/重组的贡献；分别报告图恢复、FOS 质量和最终搜索结果。如果 oracle linkage 也没有收益，则否定当前重组假设，不继续扩大真实实验。

### 8.5 随机评价造成误选择和实验成本增加

**可能问题：** 单次执行结果可能受到模型采样、任务难度和环境随机性的影响；重复评价会增加实验成本。

**拟采取对策：** 使用任务块配对和重复执行；在可控条件下使用相同随机种子；通过序贯评价减少明显优劣候选的无效重复；固定所有方法的 rollout-equivalent 预算，并分别报告 token、时间和货币成本。评价成本是实验控制变量，不作为唯一研究目标。

### 8.6 参数过多导致算法难以解释

**可能问题：** 同时调整种群规模、变异强度、FOS 顺序、donor 策略和统计门槛，可能使实验结果无法归因。

**拟采取对策：** 采用离线和在线分层调参。先使用 irace 在训练任务上调节少量算法参数；在线只允许预先定义的变异强度和算子动作变化；统计门槛和硬约束固定。通过 A/B/C/D 四组实验检验在线控制的独立收益，若不优于离线调参固定策略则删除。

### 8.7 与已有研究的创新边界不清晰

**可能问题：** Agent 自动搜索、fitness-based linkage、conditional linkage 和噪声下变量分解已有大量研究，容易出现仅改变应用场景或组合已知模块而缺少独立算法贡献的情况。

**拟采取对策：** 持续精读直接相关论文，逐项比较基因型、交互估计量、FOS 构造、donor 规则、约束处理、噪声接受和评价预算；在正式实验前设置强基线和停止条件。若候选方法与现有方法机制等价或没有可重复增益，则调整或否定该创新点，不使用“首次提出”等未经证明的表述。

### 8.8 第三个创新点可能无法独立成立

**可能问题：** 跨任务交互结构迁移可能与前两个研究内容高度重叠，也可能被已有局部 linkage 和在线 Agent 优化方法覆盖。

**拟采取对策：** 暂不将其列为必须完成的核心创新。只有前两项取得可靠结果后，再检验共享交互结构、任务特定交互和迁移收益；若没有独立方法贡献，则将其作为泛化实验，最终以两个扎实创新点完成学位论文。

## 九、研究计划进度

以下按当前开题时间和硕士研究阶段拟定，具体月份可根据学院正式开题安排、培养计划和导师意见调整。

| 时间阶段 | 主要工作 | 阶段成果 |
|---|---|---|
| 2026.11—2026.12 | 完成开题报告初稿和导师意见修改；补充关键论文精读；确定任务定义、算法边界和实验协议 | 开题报告定稿；研究问题与实验协议冻结 |
| 2027.01—2027.02 | 建立四槽位、十六配置的合成真值环境；实现交互估计基线和评价脚本；完成统计门禁与独立复核 | Phase 0 合成实验报告；创新点一 GO/HOLD/NO-GO 决策 |
| 2027.03—2027.04 | 完成交互估计器修订和合成实验；选择真实 Agent 任务环境；开展小规模真实任务 pilot | 交互估计方法原型；Paper 1 初步实验结果 |
| 2027.05—2027.07 | 在创新点一通过后，研究 FOS 构造、约束最优混合、donor 选择和序贯接受；完成 oracle/random/learned linkage 对照 | 交互感知演化算法原型；Paper 2 预实验结果 |
| 2027.08—2027.09 | 完成强基线、消融、参数敏感性和 held-out task family 实验；根据结果决定是否开展第三项迁移研究 | 完整实验数据；创新点二及第三项扩展决策 |
| 2027.10—2027.12 | 整理实验结果，撰写和投稿相关方法论文；完成硕士论文主体章节 | 小论文投稿材料；学位论文初稿 |
| 2028.01—2028.03 | 补充实验、修改论文、完善统计分析和可复现材料 | 学位论文修改稿；实验与代码归档 |
| 2028.04—2028.06 | 根据学院安排完成预答辩、盲审和正式答辩准备 | 学位论文定稿与答辩材料 |

## 十、预期研究成果

（1）形成一套面向大语言模型智能体模块配置的结构化类别基因型和合法配置描述方法。

（2）形成一个任务条件化 Agent 组件交互结构估计方法，能够在受控真值和真实任务环境下评价其交互识别、预测和不确定性校准能力。

（3）形成一个交互结构驱动的 Agent 约束最优混合演化算法，验证其相对标准 GOM、随机交叉和现有 Agent 自动搜索方法的增量收益。

（4）在前两项研究取得可靠结果且第三项通过独立新颖性审查的前提下，形成任务分布变化下的交互结构迁移与自适应更新方法。

（5）围绕两个核心研究内容，争取形成 2 篇方法提升型学术论文；若第三项形成独立贡献，再形成第 3 篇论文。最终成果以实际实验结果、论文审稿和学校学位要求为准，不预先承诺投稿录用。

（6）完成河北工业大学计算机技术硕士学位论文，形成可复现的算法实现、实验协议、评价脚本和研究记录。

---

## 参考文献

[1] Yao S, Zhao J, Yu D, et al. ReAct: Synergizing Reasoning and Acting in Language Models[C]//International Conference on Learning Representations. 2023.

[2] Shinn N, Cassano F, Gopinath A, et al. Reflexion: Language Agents with Verbal Reinforcement Learning[C]//Advances in Neural Information Processing Systems. 2023.

[3] Hu S, Lu C, Clune J. Automated Design of Agentic Systems[C]//International Conference on Learning Representations. 2025.

[4] Shang Y, et al. AgentSquare: Automatic LLM Agent Search in Modular Design Space[C]//International Conference on Learning Representations. 2025.

[5] Zhang J, et al. AFlow: Automating Agentic Workflow Generation[C]//International Conference on Learning Representations. 2025.

[6] Zhuge M, et al. GPTSwarm: Language Agents as Optimizable Graphs[C]//International Conference on Machine Learning. PMLR, 2024, 235: 62743-62767.

[7] Guo Q, et al. Connecting Large Language Models with Evolutionary Algorithms Yields Powerful Prompt Optimizers[C]//International Conference on Learning Representations. 2024.

[8] Fernando C, Banarse D S, Michalewski H, et al. Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution[C]//International Conference on Machine Learning. PMLR, 2024, 235: 13481-13544.

[9] Yuan S, Song K, Chen J, et al. EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms[C]//Proceedings of the 2025 Conference of the North American Chapter of the Association for Computational Linguistics. 2025: 6192-6217.

[10] Hu Y, Trager M, Zhang Y, et al. Evolutionary Generation of Multi-Agent Systems[C]//International Conference on Machine Learning. PMLR, 2026, 306: 45989-46021.

[11] Wei Y, Huang Z, Xu R, et al. EvoMAS: Heuristics in the Loop—Evolving Smarter Agentic Workflows[C]//International Conference on Machine Learning. PMLR, 2026, 306: 133736-133763.

[12] Chi H, Feng Z, Yu X, et al. EvoCF: Multi-Agent Collaboration via Agentic Memory-Driven Evolutionary Counterfactual Planning[C]//International Conference on Machine Learning. PMLR, 2026, 306: 19424-19437.

[13] Liu Y, et al. Evolving Agentic Workflow Driven by Human-Agent Collaboration[C]//Findings of the Association for Computational Linguistics: ACL. 2026: 24960-24969.

[14] Agrawal L A, et al. GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning[C]//International Conference on Learning Representations. 2026.

[15] Zhang G, et al. Multi-agent Architecture Search via Agentic Supernet[C]//International Conference on Machine Learning. PMLR, 2025, 267: 75834-75852.

[16] Li Y, et al. AgentSwift: Efficient LLM Agent Design via Value-Guided Hierarchical Search[C]//Proceedings of the AAAI Conference on Artificial Intelligence. 2026, 40(38): 31843-31851.

[17] Zhou H, et al. Multi-Agent Design: Optimizing Agents with Better Prompts and Topologies[C]//International Conference on Learning Representations. 2026.

[18] He S, et al. Learning to Evolve: A Self-Improving Framework for Multi-Agent Systems via Textual Parameter Graph Optimization[C]//Findings of the Association for Computational Linguistics: ACL. 2026: 30719-30732.

[19] Dushatskiy A, Virgolin M, Bouter A, et al. Parameterless Gene-Pool Optimal Mixing Evolutionary Algorithms[J]. Evolutionary Computation, 2024, 32(4): 371-397.

[20] Guijt A, Thierens D, Alderliesten T, et al. Solving Multi-Structured Problems by Introducing Linkage Kernels into GOMEA[C]//Proceedings of the Genetic and Evolutionary Computation Conference. 2022: 703-711.

[21] Olieman C, Bouter A, Bosman P A N. Fitness-Based Linkage Learning in the Real-Valued Gene-Pool Optimal Mixing Evolutionary Algorithm[J]. IEEE Transactions on Evolutionary Computation, 2021, 25(2): 358-370.

[22] Andreadis G, Alderliesten T, Bosman P A N. Fitness-Based Linkage Learning and Maximum-Clique Conditional Linkage Modelling for Gray-Box Optimization with RV-GOMEA[C]//Proceedings of the Genetic and Evolutionary Computation Conference. 2024: 647-655. DOI: 10.1145/3638529.3654103.

[23] Przewozniczek M W, Komarnicki M M, Frej B. Direct Linkage Discovery with Empirical Linkage Learning[C]//Proceedings of the Genetic and Evolutionary Computation Conference. 2021: 609-617.

[24] Przewozniczek M W, Bosman P A N, Bouter A, et al. Conditional Direct Empirical Linkage Discovery for Solving Multi-Structured Problems[C]//Proceedings of the 18th ACM/SIGEVO Conference on Foundations of Genetic Algorithms. 2025: 238-249. DOI: 10.1145/3729878.3746624.

[25] Zhong R, Zhang E, Munetomo M. Cooperative Coevolutionary Differential Evolution with Linkage Measurement Minimization for Large-Scale Optimization Problems in Noisy Environments[J]. Complex & Intelligent Systems, 2023, 9: 4439-4456.

[26] Zhong R, Tu B, Zhang E, Munetomo M. Cooperative Coevolutionary Differential Evolution with Adjacent Intensity Matrix with Linkage Identification for Large-Scale Optimization Problems in Noisy Environments[J]. Evolutionary Intelligence, 2024, 17: 3483-3503.

[27] Tinós R, Chicano F, Przewozniczek M W, Whitley D. Learning Variable Importance and Interaction in Genetic Algorithms for Pseudo-Boolean Optimization[J]. Evolutionary Computation, 2026: 1-36. DOI: 10.1162/EVCO.a.406.

[28] Deb K, Pratap A, Agarwal S, Meyarivan T. A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II[J]. IEEE Transactions on Evolutionary Computation, 2002, 6(2): 182-197.

[29] Zhang Q, Li H. MOEA/D: A Multiobjective Evolutionary Algorithm Based on Decomposition[J]. IEEE Transactions on Evolutionary Computation, 2007, 11(6): 712-731.

[30] Mouret J B, Clune J. Illuminating Search Spaces by Mapping Elites[EB/OL]. arXiv:1504.04909, 2015.

[31] Eiben A E, Michalewicz Z, Schoenauer M, Smith J E. Parameter Control in Evolutionary Algorithms[C]//Parameter Setting in Evolutionary Algorithms. Springer, 2007: 19-46.

[32] Eiben A E, Smit S K. Parameter tuning for configuring and analyzing evolutionary algorithms[J]. Swarm and Evolutionary Computation, 2011, 1(1): 19-31.

[33] Aleti A, Moser I. A systematic literature review of adaptive parameter control methods for evolutionary algorithms[J]. ACM Computing Surveys, 2016, 49(3): Article 56.

[34] López-Ibáñez M, Dubois-Lacoste J, Pérez Cáceres L, et al. The irace package: Iterated racing for automatic algorithm configuration[J]. Operations Research Perspectives, 2016, 3: 43-58.

[35] Da Costa L, Fialho Á, Schoenauer M, Sebag M. Adaptive operator selection with dynamic multi-armed bandits[C]//Proceedings of the Genetic and Evolutionary Computation Conference. 2008: 913-920.

[36] Tanabe R, Fukunaga A. Success-history based parameter adaptation for Differential Evolution[C]//IEEE Congress on Evolutionary Computation. 2013: 71-78.

[37] Lu J, Holleis T, Zhang Y, et al. ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities[C]//Findings of the Association for Computational Linguistics: NAACL 2025. 2025: 1160-1183. DOI: 10.18653/v1/2025.findings-naacl.65.

[38] Yao S, Shinn N, Razavi P, Narasimhan K. τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains[C]//International Conference on Learning Representations. 2025: 74824-74876.

[39] Trivedi H, Khot T, Hartmann M, et al. AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents[C]//Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics. 2024: 16022-16076. DOI: 10.18653/v1/2024.acl-long.850.

[40] Jimenez C E, et al. SWE-bench: Can Language Models Resolve Real-world GitHub Issues?[C]//International Conference on Learning Representations. 2024.

[41] Liu X, et al. AgentBench: Evaluating LLMs as Agents[C]//International Conference on Learning Representations. 2024.

[42] Rakshit P, Konar A, Das S. Noisy Evolutionary Optimization Algorithms—A Comprehensive Survey[J]. Swarm and Evolutionary Computation, 2017, 33: 18-45.

[43] Birattari M, Stützle T, Paquete L, Varrentrapp K. A Racing Algorithm for Configuring Metaheuristics[C]//Proceedings of the Genetic and Evolutionary Computation Conference. 2002: 11-18.

[44] Zhou S, et al. WebArena: A Realistic Web Environment for Building Autonomous Agents[C]//International Conference on Learning Representations. 2024.


[45] Wang S, et al. Optimas: Optimizing Compound AI Systems with Globally Aligned Local Rewards[EB/OL]. arXiv:2507.03041, 2025.

[46] Xia Y, Wang T, Zhang S, et al. HiveMind: Contribution-Guided Online Prompt Optimization of LLM Multi-Agent Systems[C]//Proceedings of the AAAI Conference on Artificial Intelligence. 2026, 40(35): 29767-29774. DOI: 10.1609/aaai.v40i35.40222.

[47] Liu M. More Is Not Always Better: Cross-Component Interference in LLM Agent Scaffolding[EB/OL]. arXiv:2605.05716, 2026.

[48] Lauziere A, Daugherty J, Kushner T. A Regression Framework for Understanding Prompt Component Impact on LLM Performance[C]//EXPLAINABILITY 2026. IARIA, 2026: 1-10. arXiv:2603.26830.

[49] Shang Z, et al. MESH-Harness: Self-Improving Agent Harnesses via Bandit-Guided Compositional Evolution[EB/OL]. arXiv:2610.05300, 2026.

[50] Brookes P, et al. Evolving Excellence: Automated Optimization of LLM-Based Agents[EB/OL]. arXiv:2512.09108, 2025.

[51] 陈旭. 基于大语言模型的自主智能体概述[C]//第二十三届中国计算语言学大会论文集（第2卷：前沿论坛）. 太原: 中国中文信息学会计算语言学专业委员会, 2024: 141-150.

[52] 周涛, 李鑫, 周俊临, 李奕. 大模型智能体：概念、前沿和产业实践[J]. 电子科技大学学报（社科版）, 2024, 26(4): 57-62. DOI: 10.14071/j.1008-8105(2024)-1006.

[53] 卢宇, 余京蕾, 陈鹏鹤. 基于大模型的教学智能体构建与应用研究[J]. 中国电化教育, 2024(7): 99-108.

[54] 黄悦欣, 周雨琪, 覃京燕, 杨胡尧, 王建元. 大语言模型AI智能体的设计方法研究[J]. 工业工程设计, 2025, 7(6): 6-15. DOI: 10.19798/j.cnki.2096-6946.2025.06.002.

[55] 袁雪峰, 丁俐夫, 陈颖, 肖谭南, 黄少伟. 基于大语言模型的电力仿真智能体及其技能库设计方法[J]. 电力系统自动化, 2026(13): 177-188. DOI: 10.7500/AEPS20250328001.

[56] Song Z, Yang H, Deng Z, et al. MAESD: A Unified Multi-Agent Evolutionary Framework for Protein Sequence Design[J]. Journal of Chemical Information and Modeling, 2026, 66(7): 3464-3479. DOI: 10.1021/acs.jcim.5c02580.

[57] 佘维, 徐亚涛, 薛兴亮, 李均剑, 孔德锋. 大语言模型引导的群体智能优化算法进化框架[J/OL]. 计算机应用, 2026. DOI: 10.11772/j.issn.1001-9081.2026060735.

[58] Lin J, Liu S, Pan C, et al. Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses[EB/OL]. arXiv:2604.25850, 2026.

[59] Zhang M, Shen T, Luo H, et al. SkillFlow: Flow-Driven Recursive Skill Evolution for Agentic Orchestration[EB/OL]. arXiv:2605.14089, 2026.

[60] Yang Y, Huang B, Qi S, et al. Attribution-Based Analysis and Optimization of Modular Agentic Workflows[C]//Findings of the Association for Computational Linguistics: ACL 2026. 2026: 7247-7264. DOI: 10.18653/v1/2026.findings-acl.359.

[61] Wang X, Yang Z, Hong Z, et al. FusionFlow: Enabling Deep Structural Exploration for Automated Agentic Workflow Generation[C]//Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics. 2026: 27718-27760. DOI: 10.18653/v1/2026.acl-long.1278.

## 初稿自检与待补事项

1. 本稿按河北工业大学硕士开题报告模板组织，正文约为 24,284 个非空白字符（以 Markdown 统计口径估算，正式提交前仍按学校 Word 统计口径复核），高于硕士开题报告不少于 6000 字的要求。
2. 当前列出 61 篇参考文献，其中 55 篇为外文文献（90.2%）、6 篇为中文文献；按 2022–2026 年统计，近五年文献为 48 篇（78.7%），均超过学校 30% 的最低要求。已对本轮新增国内来源和若干关键国际文献核对出版信息，但并非所有 61 条均完成最终 GB/T 7714 格式审计，仍需逐条复核。
3. 题目仍为工作题目，需导师确认。
4. 创新点一和创新点二均为拟研究机制，尚未通过合成和真实 Agent 实验；创新点三为条件性储备。
5. TCAIL V2.1 的独立规格复审仍为 REQUEST CHANGES；22 号 linkage 接口修订提案尚待独立复审。正式报告保留研究方向，但不能写成已验证算法。
6. 当前课题尚无正式 Phase 0 性能实验或真实 Agent 实验结果。现有研究基础仅陈述本开题项目内已完成的文献与规格工作；没有把其他项目的代码、实验或结果作为本课题成果。
7. 国内研究现状已补入代表性综述、教学/垂直领域 Agent、技能库和 LLM—演化计算交叉工作，但中文数据库和学位论文检索仍未穷尽。
8. 封面中的导师姓名、学号和姓名待补；研究计划月份需按学院正式毕业时间表调整。
