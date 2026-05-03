from typing import Protocol

from app.tax_risk_agent.models.domain import RiskFinding


class LLMClient(Protocol):
    def summarize_findings(self, findings: list[RiskFinding]) -> str:
        ...


class OfflineLLMClient:
    def summarize_findings(self, findings: list[RiskFinding]) -> str:
        if not findings:
            return "未发现可自动确认的税务风险。"
        titles = "、".join(finding.title for finding in findings)
        return f"本轮诊断形成 {len(findings)} 项风险结论，重点关注：{titles}。"


class LangChainQwenClient:
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
    if provider == "openai_compatible":
        try:
            return LangChainQwenClient(base_url=base_url, api_key=api_key, model=model)
        except Exception:
            return OfflineLLMClient()
    return OfflineLLMClient()

