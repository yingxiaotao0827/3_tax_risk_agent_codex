# 项目代码目录结构与业务含义

本文档说明“税务风险智能诊断分析系统”的代码目录结构，以及每个文件夹、关键文件在业务上的作用。

## 一、整体目录结构

| 路径                                                 | 类型   | 业务含义                                                                                                  |
| ---------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------- |
| `3_tax_risk_agent_codex/`                            | 根目录 | 税务风险智能诊断分析系统项目根目录，包含后端服务、Agent、工具、知识库、前端测试页、文档、测试和运行脚本。 |
| `app/`                                               | 目录   | 应用主代码目录，所有可运行的后端业务逻辑都放在这里。                                                      |
| `app/tax_risk_agent/`                                | 目录   | 税务风险诊断系统的 Python 包根目录，承载 Agent、API、工具、数据访问、模型对象、报告生成和知识库检索。     |
| `app/tax_risk_agent/agent/`                          | 目录   | Agent 编排层，负责模拟税务专家稽查思路和 ReAct 状态流转。                                                 |
| `app/tax_risk_agent/agent/diagnostic_agent.py`       | 文件   | 核心诊断 Agent，负责读取数据、调用工具、评估证据、生成风险结论并输出报告。                                |
| `app/tax_risk_agent/agent/state_machine.py`          | 文件   | 定义 Agent 状态机，包括 Thought、Action、Observation、预算检查、冲突验证、结论生成、人工复核等状态。      |
| `app/tax_risk_agent/api/`                            | 目录   | HTTP 接口层，负责把诊断能力暴露给前端页面或外部系统。                                                     |
| `app/tax_risk_agent/api/main.py`                     | 文件   | FastAPI 应用入口，提供健康检查、样例数据重置、诊断接口和前端页面挂载。                                    |
| `app/tax_risk_agent/api/static/`                     | 目录   | 前端静态资源目录，用于放测试页面。                                                                        |
| `app/tax_risk_agent/api/static/index.html`           | 文件   | 前端测试页面，可输入企业和期间，运行诊断，并展示风险结论、证据链、整改建议和 Agent 推理链。               |
| `app/tax_risk_agent/core/`                           | 目录   | 基础设施层，放系统配置、日志和大模型客户端。                                                              |
| `app/tax_risk_agent/core/config.py`                  | 文件   | 系统配置文件，读取数据库路径、报告目录、Qwen 模型服务、Milvus 地址等环境变量。                            |
| `app/tax_risk_agent/core/llm_client.py`              | 文件   | 大模型客户端封装，支持 LangChain + OpenAI-compatible Qwen2.5 调用，并提供离线兜底摘要能力。               |
| `app/tax_risk_agent/core/logging.py`                 | 文件   | 日志配置文件，统一服务日志格式，为生产审计和排查问题做基础准备。                                          |
| `app/tax_risk_agent/data/`                           | 目录   | 数据访问层，负责数据库连接和样例数据初始化。                                                              |
| `app/tax_risk_agent/data/database.py`                | 文件   | SQLite 数据库访问封装，负责连接数据库、执行查询并返回结构化结果。                                         |
| `app/tax_risk_agent/data/sample_seed.py`             | 文件   | 样例数据初始化逻辑，创建财务报表、发票流水、行业基准表，并写入演示企业数据。                              |
| `app/tax_risk_agent/models/`                         | 目录   | 领域模型层，定义系统内部流转的业务数据结构。                                                              |
| `app/tax_risk_agent/models/domain.py`                | 文件   | 定义风险等级、证据、风险假设、风险结论、诊断请求和诊断结果等核心对象。                                    |
| `app/tax_risk_agent/reports/`                        | 目录   | 报告与图表生成层，负责输出企业税务健康体检报告。                                                          |
| `app/tax_risk_agent/reports/charting.py`             | 文件   | 指标图表生成模块，用于生成企业指标与行业分位值对比图。                                                    |
| `app/tax_risk_agent/reports/report_generator.py`     | 文件   | Markdown 报告生成器，输出摘要、风险结论、证据链、整改建议和 Agent 推理链。                                |
| `app/tax_risk_agent/tools/`                          | 目录   | Agent 可调用工具层，对应 ReAct 里的 Action。                                                              |
| `app/tax_risk_agent/tools/metric_tool.py`            | 文件   | 财务指标计算工具，计算毛利率、税负率、差旅费率、咨询费率、人均差旅费等确定性指标。                        |
| `app/tax_risk_agent/tools/rule_tool.py`              | 文件   | 规则检索工具，负责从 Milvus 或内存规则库召回税务风险规则。                                                |
| `app/tax_risk_agent/tools/sql_tool.py`               | 文件   | 安全 SQL 查询工具，只允许 SELECT，阻止 DELETE、UPDATE、INSERT、DROP 等危险操作。                          |
| `app/tax_risk_agent/vectorstore/`                    | 目录   | 知识库与向量检索层，负责税务规则 RAG 能力。                                                               |
| `app/tax_risk_agent/vectorstore/rule_store.py`       | 文件   | 规则库实现，包含 Milvus 规则库、内存规则库和自动降级逻辑。                                                |
| `app/tax_risk_agent/vectorstore/rules.py`            | 文件   | 内置税务规则定义，包括差旅费异常、税负率异常、咨询服务费集中等规则。                                      |
| `app/tax_risk_agent/__init__.py`                     | 文件   | Python 包初始化文件，使 `tax_risk_agent` 能被正常导入。                                                   |
| `configs/`                                           | 目录   | 配置目录预留，可放生产、测试、开发环境的配置模板。                                                        |
| `data/`                                              | 目录   | 本地数据目录，用于保存样例数据库和原始样例数据。                                                          |
| `data/sample/`                                       | 目录   | 样例数据目录预留，可放 CSV、Excel、JSON 等原始数据文件。                                                  |
| `data/tax_risk_demo.sqlite`                          | 文件   | SQLite 示例数据库，保存样例企业财务数据、发票流水和行业基准指标。                                         |
| `docs/`                                              | 目录   | 项目文档目录，用于保存架构、计划、流程、目录说明和View材料。                                              |
| `docs/architecture.md`                               | 文件   | 系统架构文档，说明系统目标、Agent 编排、模块分层和生产化要点。                                            |
| `docs/code_structure_explained.md`                   | 文件   | 项目目录结构说明文档，解释每个文件夹和关键文件的业务含义。                                                |
| `docs/implementation_plan_2025_04_2025_08.md`        | 文件   | 项目实施计划和技术成熟度核对文档，说明 2025.04-2025.08 的阶段交付。                                       |
| `docs/project_build_process.md`                      | 文件   | 项目规划与实现过程文档，包含实现步骤、View讲法和流程图。                                                  |
| `exports/`                                           | 目录   | 导出文件目录，用于保存对话归档、PDF、Markdown 等交付物。                                                  |
| `exports/conversation_export.html`                   | 文件   | 会话归档 HTML，保存项目沟通、规划、实现说明和回答内容。                                                   |
| `exports/conversation_export.pdf`                    | 文件   | 会话归档 PDF，用于归档、分享或View准备。                                                                  |
| `reports_output/`                                    | 目录   | 系统运行后生成的诊断报告输出目录。                                                                        |
| `reports_output/charts/`                             | 目录   | 图表输出目录，用于保存指标对比图等可视化结果。                                                            |
| `reports_output/demo_co_2025Q2_tax_health_report.md` | 文件   | 样例企业 `demo_co / 2025Q2` 的税务健康体检报告。                                                          |
| `scripts/`                                           | 目录   | 项目运行、演示和导出的辅助脚本目录。                                                                      |
| `scripts/bootstrap_sample_db.py`                     | 文件   | 初始化样例数据库脚本，创建表并写入演示数据。                                                              |
| `scripts/export_conversation_pdf.py`                 | 文件   | 会话归档 PDF 导出脚本，将 HTML 归档转换成 PDF。                                                           |
| `scripts/run_demo.py`                                | 文件   | 本地端到端演示脚本，初始化样例数据、运行 Agent 并打印诊断结果。                                           |
| `tests/`                                             | 目录   | 自动化测试目录，验证指标计算、SQL 安全和 Agent 主流程。                                                   |
| `tests/test_agent.py`                                | 文件   | Agent 主流程测试，验证能生成报告并识别差旅费异常高风险。                                                  |
| `tests/test_metric_tool.py`                          | 文件   | 指标计算工具测试，验证毛利率、税负率、差旅费率、人均差旅费等计算正确。                                    |
| `tests/test_sql_tool.py`                             | 文件   | SQL 工具安全测试，验证合法 SELECT 可执行，危险 SQL 会被阻止。                                             |
| `docker-compose.yml`                                 | 文件   | Milvus 本地部署配置，用于启动向量数据库，模拟生产 RAG 检索能力。                                          |
| `environment.yml`                                    | 文件   | conda 环境配置，声明 Python、FastAPI、LangChain、Milvus、pandas、matplotlib、pytest 等依赖。              |
| `pyproject.toml`                                     | 文件   | Python 项目配置，定义项目元信息、Python 版本要求和 pytest 路径。                                          |
| `README.md`                                          | 文件   | 项目入口说明，包含系统能力、快速运行、API 调用、前端测试页、Qwen 和 Milvus 配置方式。                     |

## 二、核心业务代码目录

### 1. `app/`

应用主代码目录。所有可运行的后端业务逻辑都放在这里。

### 2. `app/tax_risk_agent/`

税务风险诊断系统的 Python 包根目录。它代表整个业务应用模块，包含 Agent、API、工具、数据访问、模型对象、报告生成和知识库检索等能力。

### 3. `app/tax_risk_agent/agent/`

Agent 编排层，负责模拟税务专家的稽查思路。

#### `diagnostic_agent.py`

核心诊断 Agent。

业务含义：

- 接收企业编号和期间；
- 读取企业财务报表；
- 调用指标计算工具；
- 查询行业基准；
- 检索税务规则；
- 判断风险证据是否充分；
- 生成高风险、中风险或人工复核结论；
- 调用报告生成模块输出《企业税务健康体检报告》。

它是整个项目最核心的业务文件，可以在View中重点讲。

#### `state_machine.py`

定义 Agent 状态机枚举。

业务含义：

- `THINK`：生成或更新风险假设；
- `EVALUATE_EVIDENCE`：评估证据是否充分；
- `ACT`：选择并调用工具；
- `OBSERVE`：接收工具执行结果；
- `CHECK_BUDGET`：检查最大轮次、工具调用次数等预算；
- `RESOLVE_CONFLICT`：处理指标或证据冲突；
- `CONCLUDE`：生成结构化风险结论；
- `HUMAN_REVIEW`：证据不足时转人工复核。

这个文件对应项目图里的 Agent 状态流转。

### 4. `app/tax_risk_agent/api/`

HTTP 接口层，负责把 Agent 能力暴露给前端页面或外部系统。

#### `main.py`

FastAPI 应用入口。

业务含义：

- 创建 FastAPI 服务；
- 挂载前端测试页面；
- 提供健康检查接口 `/healthz`；
- 提供样例数据重置接口 `/api/v1/demo/seed`；
- 提供核心诊断接口 `/api/v1/diagnostics/run`；
- 初始化数据库、规则库、LLM 客户端和 Agent。

在真实生产环境中，这一层会对接企业系统、权限认证和网关。

#### `static/index.html`

前端测试页面。

业务含义：

- 输入企业编号；
- 选择诊断期间；
- 发起一次完整诊断闭环；
- 调用后端诊断接口；
- 展示风险摘要、风险等级、证据链、整改建议和 Agent 推理链。

它是项目演示页面，适合View时展示系统端到端可运行。

### 5. `app/tax_risk_agent/core/`

基础设施层，放通用配置、日志和模型客户端。

#### `config.py`

系统配置文件。

业务含义：

- 读取 `.env` 环境变量；
- 配置数据库路径；
- 配置报告输出目录；
- 配置 LLM 服务地址；
- 配置 Qwen2.5-14B-Instruct 模型名称；
- 配置 Milvus 地址和 collection 名称。

这个文件体现项目的环境可配置能力。

#### `llm_client.py`

大模型客户端封装。

业务含义：

- 定义 LLM 调用接口；
- 提供离线兜底模型 `OfflineLLMClient`；
- 提供 LangChain + OpenAI-compatible 的 Qwen 调用客户端；
- 当 Qwen 服务不可用时自动降级，保证系统仍可演示。

View时可以强调：关键数值不依赖 LLM 生成，LLM 主要用于摘要和自然语言解释。

#### `logging.py`

日志配置。

业务含义：

- 统一服务日志格式；
- 为后续生产环境接入日志平台、链路追踪、审计日志预留基础。

### 6. `app/tax_risk_agent/data/`

数据访问层，负责数据库连接和样例数据初始化。

#### `database.py`

数据库访问封装。

业务含义：

- 连接 SQLite 数据库；
- 执行查询；
- 返回结构化字典结果；
- 后续可替换为 PostgreSQL、MySQL 或企业数仓。

#### `sample_seed.py`

样例数据初始化脚本。

业务含义：

- 创建财务报表表 `financial_statements`；
- 创建发票流水表 `invoices`；
- 创建行业基准表 `industry_benchmarks`；
- 写入样例企业 `demo_co` 和 `healthy_co` 数据；
- 构造差旅费异常、税负率偏低等测试场景。

它保证项目可以在本地快速跑通。

### 7. `app/tax_risk_agent/models/`

领域模型层，定义系统里流转的数据结构。

#### `domain.py`

核心业务对象定义。

业务含义：

- `RiskLevel`：风险等级；
- `Evidence`：证据对象；
- `RiskHypothesis`：风险假设；
- `RiskFinding`：风险结论；
- `DiagnosticRequest`：诊断请求；
- `DiagnosticResult`：诊断结果。

这些对象让 API、Agent、报告模块之间的数据结构统一。

### 8. `app/tax_risk_agent/tools/`

Agent 可调用的工具层。对应 ReAct 里的 Action。

#### `sql_tool.py`

安全 SQL 查询工具。

业务含义：

- 允许 Agent 查询财务报表、发票流水和行业基准；
- 只允许 `SELECT`；
- 拦截 `DELETE`、`UPDATE`、`INSERT`、`DROP` 等危险语句；
- 避免 Agent 对数据库执行破坏性操作。

#### `metric_tool.py`

财务指标计算工具。

业务含义：

- 计算毛利率；
- 计算增值税税负率；
- 计算差旅费率；
- 计算咨询费率；
- 计算人均差旅费。

它体现“复杂财务指标由代码解释器/确定性工具计算，而不是由大模型编造”。

#### `rule_tool.py`

税务规则检索工具。

业务含义：

- 接收风险查询词；
- 从 Milvus 或内存规则库召回税务规则；
- 将规则内容提供给 Agent 做风险判断。

### 9. `app/tax_risk_agent/vectorstore/`

规则知识库和向量检索层。

#### `rules.py`

内置税务规则定义。

业务含义：

- 定义差旅费异常规则；
- 定义税负率异常规则；
- 定义咨询服务费集中规则；
- 提供简单文本向量化函数，支持本地演示。

#### `rule_store.py`

规则库实现。

业务含义：

- `InMemoryRuleStore`：内存规则库，适合本地演示；
- `MilvusRuleStore`：Milvus 规则库，适合生产部署；
- `build_rule_store`：优先连接 Milvus，失败时自动降级为内存规则库。

这个文件体现系统对 Milvus 的接入设计。

### 10. `app/tax_risk_agent/reports/`

报告与图表生成层。

#### `report_generator.py`

Markdown 报告生成器。

业务含义：

- 根据诊断结果生成《企业税务健康体检报告》；
- 输出摘要；
- 输出风险结论；
- 输出证据链；
- 输出整改建议；
- 输出 Agent 推理链。

#### `charting.py`

指标图表生成模块。

业务含义：

- 生成企业指标与行业分位值对比图；
- 用于报告中的图文展示；
- 当前依赖 matplotlib，未安装时自动跳过图表生成，保证主流程不失败。

## 三、脚本目录

### `scripts/`

项目运行、演示和导出的辅助脚本。

#### `bootstrap_sample_db.py`

初始化样例数据库。

业务含义：

- 创建 SQLite 示例库；
- 写入企业财务、发票和行业基准数据；
- 运行前端或 API 前可先执行它。

#### `run_demo.py`

本地端到端演示脚本。

业务含义：

- 自动初始化样例数据；
- 构建 Agent；
- 对 `demo_co / 2025Q2` 执行税务风险诊断；
- 打印结构化 JSON 结果；
- 生成报告文件。

#### `export_conversation_pdf.py`

会话归档 PDF 导出脚本。

业务含义：

- 将对话归档 HTML 转换成 PDF；
- 用于保存项目沟通、规划和回答内容。

## 四、测试目录

### `tests/`

自动化测试目录。

#### `test_metric_tool.py`

测试财务指标计算是否正确。

覆盖内容：

- 毛利率；
- 税负率；
- 差旅费率；
- 人均差旅费。

#### `test_sql_tool.py`

测试 SQL 工具安全性。

覆盖内容：

- 允许合法 `SELECT`；
- 阻止 `DELETE` 等危险 SQL。

#### `test_agent.py`

测试 Agent 主流程。

覆盖内容：

- 初始化样例数据；
- 运行诊断 Agent；
- 生成报告；
- 确认至少输出一个高风险结论；
- 确认差旅费异常风险被识别。

## 五、文档目录

### `docs/`

项目说明和View材料目录。

#### `architecture.md`

系统架构文档。

业务含义：

- 解释系统目标；
- 说明 Agent 编排；
- 说明 API、工具、知识库、报告模块；
- 描述生产化要点。

#### `implementation_plan_2025_04_2025_08.md`

项目时间规划和技术成熟度文档。

业务含义：

- 按 2025.04 - 2025.08 拆分实施阶段；
- 说明 Qwen2.5、LangChain、Milvus 在该时间点是否成熟；
- 提供View表达建议。

#### `project_build_process.md`

项目规划与实现过程文档。

业务含义：

- 说明从零开始如何设计并实现该项目；
- 包含项目实现流程图；
- 包含 Agent 运行流程图；
- 可直接用于View复盘。

#### `code_structure_explained.md`

当前文档。

业务含义：

- 解释项目目录结构；
- 说明每个文件夹和关键文件的业务作用。

## 六、数据与输出目录

### `data/`

本地数据目录。

#### `data/tax_risk_demo.sqlite`

SQLite 示例数据库。

业务含义：

- 保存样例企业财务数据；
- 保存样例发票流水；
- 保存行业基准指标。

#### `data/sample/`

样例数据目录预留。

业务含义：

- 后续可放 CSV、Excel、JSON 等原始样例数据文件。

### `reports_output/`

诊断报告输出目录。

#### `demo_co_2025Q2_tax_health_report.md`

样例企业税务健康体检报告。

业务含义：

- Agent 对 `demo_co / 2025Q2` 的诊断结果；
- 包含摘要、风险结论、证据链、整改建议和推理链。

#### `reports_output/charts/`

图表输出目录。

业务含义：

- 保存指标对比图；
- 用于报告中的可视化展示。

### `exports/`

导出文件目录。

#### `conversation_export.html`

会话归档 HTML。

业务含义：

- 保存项目沟通、规划、实现说明和回答内容。

#### `conversation_export.pdf`

会话归档 PDF。

业务含义：

- 用于归档、分享或View准备。

## 七、项目配置文件

### `README.md`

项目入口说明。

业务含义：

- 说明项目能力；
- 说明快速运行方式；
- 说明 API 调用方式；
- 说明前端测试页访问方式；
- 说明 Qwen2.5 和 Milvus 配置方式。

### `environment.yml`

conda 环境配置。

业务含义：

- 固定 Python 版本；
- 声明 FastAPI、LangChain、Milvus、pandas、matplotlib、pytest 等依赖；
- 保证项目可复现安装。

### `pyproject.toml`

Python 项目配置。

业务含义：

- 定义项目名称、版本和 Python 要求；
- 配置 pytest 的测试路径和 Python import 路径。

### `docker-compose.yml`

Milvus 本地部署配置。

业务含义：

- 一键启动 Milvus standalone；
- 提供向量规则库运行环境；
- 用于模拟生产 RAG 检索能力。

### `.env.example`

环境变量模板。

业务含义：

- 配置数据库路径；
- 配置报告目录；
- 配置 LLM provider；
- 配置 Qwen2.5-14B-Instruct 模型服务；
- 配置 Milvus 地址。

## 八、View讲解版本

可以这样介绍目录：

“这个项目我按生产工程分层来组织。`api` 是服务入口和前端测试页，`agent` 是税务稽查 Agent 的状态机，`tools` 是 Agent 可调用的 SQL、指标计算和规则检索工具，`vectorstore` 负责 Milvus 规则知识库，`data` 负责财务和发票数据访问，`reports` 负责生成税务健康体检报告，`models` 定义风险、证据和诊断结果这些领域对象。这样拆分以后，每一层职责清楚，也方便后续把 SQLite 换成企业数仓，把内存规则库换成 Milvus，把离线摘要换成 Qwen2.5 服务。”
