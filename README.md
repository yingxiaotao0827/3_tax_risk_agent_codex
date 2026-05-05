# 税务风险智能诊断分析系统

系统基于企业财务报表、发票流向和税务规则知识库，模拟税务稽查专家的 ReAct 推理过程，输出《企业税务健康体检报告》。

## 核心能力

- ReAct 风险诊断 Agent：围绕风险假设、证据补充、工具调用、证据充分性评估、冲突消解和结论生成执行状态机。
- 工具调用：SQL 查询器、规则库检索、财务指标计算、图表生成。
- 知识库：Milvus 向量库优先，未部署 Milvus 时自动降级为内存检索，便于本地演示。
- 模型接入：Qwen2.5-14B-Instruct OpenAI-compatible API 配置，离线模式下使用确定性规则推理器。
- 生产工程骨架：FastAPI 服务、配置管理、结构化日志、测试、示例数据、Docker Compose、conda 环境。

## 快速运行

```bash
conda env create -f environment.yml
conda activate tax-risk-agent
python scripts/bootstrap_sample_db.py
python scripts/run_demo.py
```

启动 API：

```bash
uvicorn app.tax_risk_agent.api.main:app --reload --host 0.0.0.0 --port 8000
```

前端测试页：

```text
http://127.0.0.1:8000/
```

调用：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/diagnostics/run \
  -H 'Content-Type: application/json' \
  -d '{"company_id":"demo_co","period":"2025Q2"}'
```

## 可选：启动 Milvus

```bash
docker compose up -d milvus
```

默认配置会连接 `127.0.0.1:19530`。如果 Milvus 不可用，系统仍会使用内存规则库完成诊断。

## Qwen2.5-14B-Instruct 接入

复制环境变量模板：

```bash
cp .env.example .env
```

配置 OpenAI-compatible 服务：

```bash
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=http://127.0.0.1:8001/v1
LLM_MODEL=Qwen2.5-14B-Instruct
LLM_API_KEY=local-key
```

可使用 vLLM、DashScope/OpenAI-compatible 网关或企业内部推理服务承载 Qwen2.5-14B-Instruct。

## 项目结构

```text
app/tax_risk_agent/
  agent/          ReAct 状态机与诊断编排
  api/            FastAPI HTTP 服务
  core/           配置、日志、模型客户端
  data/           SQLite 数据访问与样例库
  reports/        Markdown 报告与图表
  tools/          SQL、规则检索、Python 指标计算工具
  vectorstore/    Milvus/内存规则知识库
docs/
  architecture.md
  implementation_plan_2025_04_2025_08.md
```

## 测试

```bash
python -m pytest -q
```
