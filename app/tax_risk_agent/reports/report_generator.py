"""Markdown 税务健康体检报告生成模块

本模块负责把诊断 Agent 产出的结构化 `DiagnosticResult` 渲染为 Markdown 文件。
报告内容包括企业与期间信息、管理层摘要、风险结论、证据、建议、Agent 推理链
以及可选的指标对比图表。
"""

from pathlib import Path  # 导入路径类型，用于管理报告输出目录和文件路径。

from app.tax_risk_agent.models.domain import DiagnosticResult  # 导入诊断结果模型，作为报告渲染输入。


class ReportGenerator:
    """负责将结构化诊断结果写出为 Markdown 报告的生成器。"""

    def __init__(self, report_dir: Path):
        """初始化报告生成器。

        Args:
            report_dir: Markdown 报告输出目录。
        """
        # 初始化流程：保存报告输出目录，实际创建目录在 render 阶段完成。
        self.report_dir = report_dir

    def render(self, result: DiagnosticResult) -> Path:
        """将诊断结果渲染为 Markdown 报告，并返回报告文件路径。

        Args:
            result: 税务风险诊断的结构化结果。

        Returns:
            生成的 Markdown 报告路径。
        """
        # 流程 1：确保报告输出目录存在，避免写入文件时目录缺失。
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # 流程 2：根据企业编号和期间生成稳定的报告文件名。
        path = self.report_dir / f"{result.company_id}_{result.period}_tax_health_report.md"

        # 流程 3：先拼接报告头部、基础信息、摘要和风险结论章节标题。
        lines = [
            f"# {result.company_id} 企业税务健康体检报告",
            "",
            f"- 期间：{result.period}",
            f"- 是否需要人工复核：{'是' if result.needs_human_review else '否'}",
            "",
            "## 摘要",
            "",
            result.executive_summary,
            "",
            "## 一、风险结论",
        ]

        # 流程 4：逐条写入风险发现，包括风险等级、结论、证据明细和处理建议。
        for finding in result.findings:
            lines.extend(
                [
                    f"### {finding.title}",
                    f"- 风险等级：{finding.level.value}",
                    f"- 结论：{finding.conclusion}",
                    "- 证据：",
                ]
            )

            # 流程 4.1：把每条证据的摘要、来源和置信度写入报告，方便审计追溯。
            for evidence in finding.evidence:
                lines.append(f"  - {evidence.summary}（来源：{evidence.source}，置信度：{evidence.confidence:.2f}）")

            # 流程 4.2：写入该风险发现对应的整改或复核建议。
            lines.append("- 建议：")
            for suggestion in finding.suggestions:
                lines.append(f"  - {suggestion}")
            lines.append("")

        # 流程 5：写入 Agent 推理链，展示本次诊断从取数到结论的执行轨迹。
        lines.extend(["## 二、Agent 推理链", ""])
        lines.extend(f"{index + 1}. {step}" for index, step in enumerate(result.reasoning_trace))

        # 流程 6：如果诊断过程中生成了图表，则追加图表章节并以 Markdown 图片形式引用。
        if result.chart_paths:
            lines.extend(["", "## 三、图表", ""])
            for chart in result.chart_paths:
                lines.append(f"![指标对比]({chart})")

        # 流程 7：把拼接好的 Markdown 内容写入磁盘，并返回最终报告路径。
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
