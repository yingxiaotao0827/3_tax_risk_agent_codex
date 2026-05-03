from pathlib import Path

from app.tax_risk_agent.models.domain import DiagnosticResult


class ReportGenerator:
    def __init__(self, report_dir: Path):
        self.report_dir = report_dir

    def render(self, result: DiagnosticResult) -> Path:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        path = self.report_dir / f"{result.company_id}_{result.period}_tax_health_report.md"
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
        for finding in result.findings:
            lines.extend(
                [
                    f"### {finding.title}",
                    f"- 风险等级：{finding.level.value}",
                    f"- 结论：{finding.conclusion}",
                    "- 证据：",
                ]
            )
            for evidence in finding.evidence:
                lines.append(f"  - {evidence.summary}（来源：{evidence.source}，置信度：{evidence.confidence:.2f}）")
            lines.append("- 建议：")
            for suggestion in finding.suggestions:
                lines.append(f"  - {suggestion}")
            lines.append("")
        lines.extend(["## 二、Agent 推理链", ""])
        lines.extend(f"{index + 1}. {step}" for index, step in enumerate(result.reasoning_trace))
        if result.chart_paths:
            lines.extend(["", "## 三、图表", ""])
            for chart in result.chart_paths:
                lines.append(f"![指标对比]({chart})")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
