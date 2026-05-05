from enum import Enum  # 导入枚举基类，用于定义固定取值集合。
from pathlib import Path  # 导入路径类型，用于保存报告和图表文件路径。
from typing import Any  # 导入任意类型标注，用于承载灵活的原始数据。

from pydantic import BaseModel, Field  # 导入 Pydantic 模型基类和字段配置工具。


class RiskLevel(str, Enum):  # 定义风险等级枚举，并让枚举值同时表现为字符串。
    low = "low"  # 低风险。
    medium = "medium"  # 中等风险。
    high = "high"  # 高风险。
    review_required = "review_required"  # 需要人工复核的风险状态。


class Evidence(BaseModel):  # 定义支撑风险判断的证据模型。
    source: str  # 记录证据来源，例如报表、台账、规则或外部数据。
    summary: str  # 记录证据摘要，便于报告中快速解释依据。
    data: dict[str, Any] = Field(default_factory=dict)  # 保存结构化证据明细，默认创建空字典避免共享可变对象。
    confidence: float = 0.7  # 记录该证据的可信度，默认值为 0.7。


class RiskHypothesis(BaseModel):  # 定义诊断过程中形成的风险假设模型。
    code: str  # 记录风险假设编码，用于识别和追踪。
    title: str  # 记录风险假设标题，用于展示简短名称。
    reason: str  # 记录形成该假设的原因说明。
    confidence: float = 0.5  # 记录该假设的置信度，默认值为 0.5。
    evidence: list[Evidence] = Field(default_factory=list)  # 保存支持该假设的证据列表，默认创建空列表。


class RiskFinding(BaseModel):  # 定义最终输出到诊断结果中的风险发现模型。
    code: str  # 记录风险发现编码，用于和规则或假设对应。
    title: str  # 记录风险发现标题，用于报告展示。
    level: RiskLevel  # 记录风险等级，取值来自 RiskLevel 枚举。
    conclusion: str  # 记录风险结论，说明最终判断结果。
    evidence: list[Evidence]  # 保存支撑该风险发现的证据列表。
    suggestions: list[str]  # 保存针对该风险发现的处理建议列表。


class DiagnosticRequest(BaseModel):  # 定义发起税务风险诊断所需的请求参数模型。
    company_id: str  # 记录被诊断公司的唯一标识。
    period: str  # 记录诊断所属期间，例如 2025Q2。


class DiagnosticResult(BaseModel):  # 定义税务风险诊断完成后的结果模型。
    company_id: str  # 记录被诊断公司的唯一标识。
    period: str  # 记录诊断所属期间。
    executive_summary: str = ""  # 保存管理层摘要，默认为空字符串。
    findings: list[RiskFinding]  # 保存所有风险发现列表。
    reasoning_trace: list[str]  # 保存诊断推理过程摘要，便于追溯判断链路。
    report_path: Path | None = None  # 保存生成报告的文件路径，未生成时为 None。
    chart_paths: list[Path] = Field(default_factory=list)  # 保存生成图表的文件路径列表，默认创建空列表。
    needs_human_review: bool = False  # 标记该诊断结果是否需要人工复核，默认不需要。
