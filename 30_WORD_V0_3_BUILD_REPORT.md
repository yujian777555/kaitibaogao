# Word V0.3（RSI）生成与结构验收记录

**日期：** 2026-11-03  
**仓库：** yujian777555/kaitibaogao  
**对应 Markdown：** 27_OPENING_REPORT_DRAFT_V0_3_RSI.md  
**使用模板：** 河北工业大学硕士开题报告原始 Word 模板的 V0.2 工作副本  
**产物：** `河北工业大学硕士学位论文开题报告_V0.3_RSI_初稿.docx`（本轮会话生成的下载附件）

## 1. 已完成

- 将题目改为《面向大语言模型智能体递归自我改进的交互感知演化优化方法研究》。
- 封面、页眉、研究方向和目录保持学校模板风格；页眉版本号已统一为 V0.3。
- 加入 RSI 研究现状，覆盖 DGM、CPE、HarnessEvolve、EvolveNet、持续 harness 演化和 task-free continual-agent 研究。
- 将三个研究内容与三个预期创新点写入 Word：交互结构学习、交互感知约束 GOM、跨轮次交互记忆与能力保持约束演化。
- 加入 IMCE-RSI 候选算法段落、双键检索、漂移检测、条件化 linkage block 迁移和 task-free 标签隔离规则。
- 首个真实 Agent 任务平台改为 SWE-bench Verified；跨轮次候选任务流为 SWE-bench Verified、SWT-Bench、FeatureBench。
- 更新参数调节、基线、评价指标、统计方法、风险对策、研究计划和预期成果。
- 参考文献追加至 68 条，编号连续；封面元信息表和研究进度表保留。

## 2. 结构检查

| 检查项 | 结果 |
|---|---|
| DOCX 可重新打开 | PASS |
| A4 页面 | PASS（8.27 × 11.69 in） |
| 正文 Normal 样式 | 宋体 12 pt / 1.5 倍行距 |
| 模板表格 | 2 个，保留 |
| 参考文献 | 68 条，编号 [1]–[68] 连续 |
| RSI 章节与三个创新点标题 | PASS |
| IMCE-RSI 算法方案标题 | PASS |
| SWE-bench Verified 任务平台 | PASS |
| task-family 标签不作为在线输入 | PASS |
| 第三创新点停止条件 | 已调整为未达强基线则不作为独立论文贡献 |

## 3. 重要限制

该 DOCX 是**可供导师审阅的 V0.3 工作初稿**，不是最终提交版。它以 V0.2 Word 模板为底稿进行章节和段落级修订，已完成主要 RSI 内容和结构调整，但尚未完成与 Markdown 的逐段、逐表、逐公式完全一致性审计。部分原有背景和方法论段落保留为底稿内容，后续需要逐段核对是否应进一步按 V0.3 Markdown 更新。

另外，68 条参考文献目前只完成编号完整性检查；作者、正式出版状态、卷期页码、DOI 和 GB/T 7714 格式仍需逐条核验。当前自动统计的正文字符数不能替代学校最终 Word 字数统计。

## 4. 研究真实性边界

- TCAIL V2.1：仍为 REQUEST CHANGES / IMPLEMENTATION BLOCKED。
- 22 号 Linkage/FOS 接口提案：仍待独立复审。
- CI-GOM：尚未实现和实验。
- IMCE-RSI：研究候选，尚无正式算法规格。
- 本课题 Phase 0、真实 Agent RSI 实验、A800 训练：均未启动。
- 本轮没有调用 DeepSeek API。

## 5. 下一步

1. 完成 Word 与 Markdown 的逐段/逐表一致性审计，修订页眉、目录、公式、表格分页和参考文献格式。
2. 逐条核验 68 条文献的元数据与 GB/T 7714。
3. 独立复审创新点一 TCAIL 的 estimand、模型阶数、任务块相关、局部 linkage 和最终边决策。
4. 在规格 Gate 通过前不启动 Phase 0 或真实 API 实验。
