# LICENSE_AND_PROVENANCE — 许可与来源登记

**日期：** 2026-11-06（Phase B）  
**原则：** 只登记本轮实际核验过的事实；未能核验的标记 UNKNOWN/UNREACHABLE，不做推断。完整哈希清单见 `DATASET_LOCK_MANIFEST.json`。

## 1. ToolMisuseBench

| 项 | 值 | 核验方式 |
|---|---|---|
| 数据卡 | https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench | HF API |
| HF revision | `98eb28718b0393e029088ce80604c48807216de4` | HF API `sha` 字段 |
| 许可 | **MIT**（cardData.license=mit） | HF API + 数据卡 |
| 论文 | Baral & Sigdel, *ToolMisuseBench…*, REALM 2026, ACL Anthology 2026.realm-1.28 | 引用自数据卡/计划文档 |
| 官方代码 | https://github.com/akgitrepos/toolmisusebench @ `b6ee3412f98d2058ee487e182a72b26c58046d51` | git clone --depth 1 |
| 生成环境 | macOS-13.4-arm64, Python 3.13.3（run_manifest.json） | artifacts 文件 |
| 数据文件校验 | v0.2 三 split SHA-256 与官方 manifest 逐一一致 | 本地哈希复算 |

**再分发/使用要求（MIT）：** 保留版权与许可声明即可。本仓库不内嵌原始数据（`datasets/` gitignored），只存哈希与审计产物；复现按 revision 重新下载。

## 2. UndoBench

| 项 | 值 | 核验方式 |
|---|---|---|
| 数据卡 | https://huggingface.co/datasets/TanmaySah/undobench | HF API |
| HF revision | `4be1151851a109e7c9cfc1ba5d6e6c64461f6f93` | HF API `sha` 字段 |
| benchmark_version | v1.0.1（36 行全量核对） | parquet 逐行 |
| 数据/规格许可 | **CC-BY-4.0** | 数据卡 license 字段 |
| 软件许可 | **Apache-2.0**（pyproject.toml license） | 官方代码 |
| 论文 | arXiv:2610.05622（2026 preprint，非同行评审） | 数据卡 arxiv tag |
| 官方代码 | https://github.com/tradertanmay/undobench @ `4a25c4fa0f12bb6c79dc6e0e3a8f31deeb6af21e` | git clone（manifest 记录同一 commit） |
| TEST 锁 | harness `allow_frozen_test_execution: false` 默认 | smoke run config.json |

**再分发/使用要求（CC-BY-4.0）：** 署名、标注修改、保留许可链接。论文引用时须注明为 2026 preprint。本仓库只存哈希、元数据快照（rows_*.json 于 gitignored 缓存）与 smoke 产物。

## 3. ThinkingBox-Bench — **UNREACHABLE（本轮无法核验）**

| 项 | 状态 |
|---|---|
| 数据卡（计划文档引用） | https://huggingface.co/datasets/microsoft/ThinkingBox-Bench |
| 实测 | HF API **HTTP 401**（gated 或已移除）；HF 公开搜索无此数据集 |
| GitHub（计划文档引用） | https://github.com/microsoft/thinkingbox-data tag `thinkingbox-bench-v1.0` |
| 实测 | GitHub API **HTTP 404**（仓库不存在或已转私有） |
| 许可 | **UNKNOWN**（无法读取） |
| 声称的 507 任务 / evaluation-only 限制 | **本轮无法复核**；沿用 50 号文档早前记录为保守默认（evaluation-only 继续生效） |

**处置：** 不规划依赖 ThinkingBox 的实验；若后续恢复访问，须重新固定 revision、核验许可与用途限制后才能进入 clean regression。研究报告中不得把其任务数/限制写成"已核验"。

## 4. 本项目自有材料

| 材料 | 许可/归属 |
|---|---|
| Pilot A-3 模拟器（experiments/pilot_a_recovery/） | 本项目自研，随仓库 |
| A-3 原始 artifact（ci_artifact/） | 本项目 CI 产出 |
| 审计报告 52/53/54、SPLIT_LEAKAGE_AUDIT、本文件、55 号设计 | 本项目文档 |
| 复现报告（experiments/dataset_audit/） | 本项目产出（基于 MIT/Apache-2.0 官方执行器运行） |

## 5. 引用规范（写论文时）

- ToolMisuseBench：引用 ACL Anthology 2026.realm-1.28；其论文报告值（0.767/0.736/0.158）标注为"论文报告值"，我们的 DEV 复现值另列。
- UndoBench：引用 arXiv:2610.05622 并注明 preprint；CC-BY-4.0 署名。
- 不得把任一公开基准的任务定义、评分器或覆盖特征写成我们的创新（D-054 边界）。
