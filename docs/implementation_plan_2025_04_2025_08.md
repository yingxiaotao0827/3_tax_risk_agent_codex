# 2025.04 - 2025.08 实施计划与技术成熟度

## 时间规划

| 阶段            | 时间    | 目标                                               | 交付物                                               |
| --------------- | ------- | -------------------------------------------------- | ---------------------------------------------------- |
| 需求与数据底座  | 2025.04 | 明确税务风险场景、数据口径、报表和发票表结构       | 风险指标字典、SQLite/PostgreSQL 原型库、样例企业数据 |
| RAG 与规则库    | 2025.05 | 建立税务规则知识库，完成 Milvus 检索链路           | Milvus collection、规则召回工具、规则命中评估集      |
| ReAct Agent MVP | 2025.06 | 实现风险假设、工具选择、Observation 反馈和预算检查 | Agent 状态机、SQL 工具、指标计算工具、首版 API       |
| 报告与可视化    | 2025.07 | 输出图文并茂的企业税务健康体检报告                 | Markdown/PDF 报告、指标图、推理链解释                |
| 生产化与验收    | 2025.08 | 完成权限、安全、稳定性、测试和演示部署             | Docker/conda 环境、回归测试、演示脚本、部署文档      |

## 技术成熟度核对

- Qwen2.5 系列由 Alibaba Cloud 在 2024-09-19 发布并开源，覆盖 0.5B 到 72B 多个尺寸，14B-Instruct 在 2025.04 已经是成熟可选项。参考：[Alibaba Cloud press release](https://www.alibabacloud.com/press-room/alibaba-cloud-unveils-new-ai-models-and-revamped)、[Hugging Face model card](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct)。
- LangChain v0.3 在 2024-09-16 发布，Python 生态已完成 Pydantic 2 迁移，2025.04-08 用于 Agent/工具编排是合理的。参考：[LangChain v0.3 announcement](https://www.langchain.com/blog/announcing-langchain-v0-3)。
- Milvus 2.4 在 2024-03 发布，已支持多向量和混合检索能力；到 2025.04 有足够时间沉淀，适合税务规则 RAG。参考：[Milvus 2.4 release](https://www.globenewswire.com/news-release/2024/03/20/2849397/0/en/Milvus-2-4-Unveils-Game-Changing-Features-for-Enhanced-Vector-Search.html)、[Milvus hybrid search docs](https://blog.milvus.io/docs/v2.4.x/multi-vector-search.md)。

## View 表达建议

这个项目在 2025.04 - 2025.08 的表述是可信的。更自然的说法是：

“项目早期没有直接让大模型给结论，而是先把税务专家的稽查路径拆成状态机：生成风险假设、评估证据、选择工具、观察结果、更新置信度、最后生成可解释报告。Qwen2.5-14B-Instruct 负责自然语言推理和报告生成，SQL 和 Python 工具负责确定性计算，Milvus 负责税务规则和案例检索。这样能把大模型的不确定性关在可控边界里。”
