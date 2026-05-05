import logging
from typing import Protocol, runtime_checkable

from app.tax_risk_agent.models.domain import RiskFinding

logger = logging.getLogger(__name__)


@runtime_checkable
class LLMClient(Protocol):
    """LLM 摘要客户端协议。

    Protocol 只声明“调用方需要什么能力”，不绑定具体实现。
    任何类只要实现 summarize_findings 方法，就可以作为 LLMClient 使用。
    """

    def summarize_findings(self, findings: list[RiskFinding]) -> str:
        """基于结构化风险结论生成报告摘要。"""
        raise NotImplementedError


class OfflineLLMClient:
    """离线兜底摘要器。

    本地没有 Qwen 服务或 LangChain 依赖不可用时，仍然能生成稳定摘要，
    保证诊断主链路不因为模型服务问题中断。
    """

    def summarize_findings(self, findings: list[RiskFinding]) -> str:
        if not findings:
            return "未发现可自动确认的税务风险。"
        titles = "、".join(finding.title for finding in findings)
        return f"本轮诊断形成 {len(findings)} 项风险结论，重点关注：{titles}。"


class LangChainQwenClient:
    """通过 LangChain 调用 OpenAI-compatible Qwen 服务。"""

    def __init__(self, base_url: str, api_key: str, model: str):
        from langchain_openai import ChatOpenAI

        self.chat_model = ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model,
            temperature=0.2,
        )

    def summarize_findings(self, findings: list[RiskFinding]) -> str:
        payload = "\n".join(
            f"- {finding.title}: {finding.conclusion}" for finding in findings
        )
        response = self.chat_model.invoke(
            [
                (
                    "system",
                    "你是税务风险稽查专家，请基于结构化风险结论生成一段谨慎、可审计的中文摘要。",
                ),
                ("user", payload or "无风险结论"),
            ]
        )
        return str(response.content)


def build_llm_client(provider: str, base_url: str, api_key: str, model: str) -> LLMClient:
    """创建 LLM 客户端。

    provider=openai_compatible 时优先接入 Qwen；初始化失败时降级为离线摘要器。
    """

    if provider == "openai_compatible":
        try:
            return LangChainQwenClient(base_url=base_url, api_key=api_key, model=model)
        except Exception as exc:
            logger.warning("Failed to initialize Qwen client, falling back to offline summarizer: %s", exc)
            return OfflineLLMClient()
    return OfflineLLMClient()
