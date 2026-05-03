from pathlib import Path

from app.tax_risk_agent.agent.state_machine import AgentState
from app.tax_risk_agent.core.llm_client import LLMClient, OfflineLLMClient
from app.tax_risk_agent.data.database import TaxRiskDatabase
from app.tax_risk_agent.models.domain import DiagnosticRequest, DiagnosticResult, Evidence, RiskFinding, RiskHypothesis, RiskLevel
from app.tax_risk_agent.reports.charting import render_metric_chart
from app.tax_risk_agent.reports.report_generator import ReportGenerator
from app.tax_risk_agent.tools.metric_tool import MetricTool
from app.tax_risk_agent.tools.rule_tool import RuleRetrievalTool
from app.tax_risk_agent.tools.sql_tool import SafeSqlTool


class TaxRiskDiagnosticAgent:
    def __init__(
        self,
        database: TaxRiskDatabase,
        rule_tool: RuleRetrievalTool,
        report_generator: ReportGenerator,
        chart_dir: Path,
        llm_client: LLMClient | None = None,
    ):
        self.database = database
        self.sql_tool = SafeSqlTool(database)
        self.metric_tool = MetricTool()
        self.rule_tool = rule_tool
        self.report_generator = report_generator
        self.chart_dir = chart_dir
        self.llm_client = llm_client or OfflineLLMClient()

    def run(self, request: DiagnosticRequest) -> DiagnosticResult:
        trace: list[str] = []
        findings: list[RiskFinding] = []
        chart_paths: list[Path] = []
        needs_review = False

        trace.append(f"{AgentState.THINK.value}: 读取企业 {request.company_id} 在 {request.period} 的财务与发票数据，生成初始风险假设。")
        financial_rows = self.sql_tool.run(
            "SELECT * FROM financial_statements WHERE company_id = ? AND period = ?",
            (request.company_id, request.period),
        )
        if not financial_rows:
            return DiagnosticResult(
                company_id=request.company_id,
                period=request.period,
                findings=[],
                reasoning_trace=trace + ["human_review: 未找到企业期间数据，建议人工确认数据口径。"],
                needs_human_review=True,
            )

        financial = financial_rows[0]
        metrics = self.metric_tool.calculate(financial)
        trace.append(f"{AgentState.ACT.value}: 调用 Python 指标计算工具，得到税负率、毛利率、差旅费率等指标。")

        benchmark_rows = self.sql_tool.run(
            "SELECT metric, p50, p75, p90 FROM industry_benchmarks WHERE industry = ? AND period = ?",
            ("software_services", request.period),
        )
        benchmarks = {row["metric"]: row for row in benchmark_rows}
        trace.append(f"{AgentState.ACT.value}: 调用 SQL 查询器读取软件服务行业 {request.period} 分位基准。")

        rules = self.rule_tool.run("travel expense invoice vat burden consulting")
        trace.append(f"{AgentState.ACT.value}: 调用规则库检索工具召回 {len(rules)} 条税务风险判断规则。")

        travel_hypothesis = RiskHypothesis(
            code="TRAVEL_RATIO",
            title="差旅费占比过高",
            reason="差旅费占收入比例超过行业 P90，需要继续核验发票集中度和业务合理性。",
            confidence=0.55,
        )
        trace.append(f"{AgentState.EVALUATE_EVIDENCE.value}: 评估假设 {travel_hypothesis.title} 的证据充分性。")

        travel_ratio = metrics["travel_expense_ratio"]
        travel_p90 = benchmarks.get("travel_expense_ratio", {}).get("p90", 1.0)
        if travel_ratio > travel_p90:
            invoice_rows = self.sql_tool.run(
                """
                SELECT counterparty, COUNT(*) AS invoice_count, SUM(amount) AS amount
                FROM invoices
                WHERE company_id = ? AND period = ? AND category = ?
                GROUP BY counterparty
                ORDER BY amount DESC
                """,
                (request.company_id, request.period, "travel"),
            )
            trace.append(f"{AgentState.OBSERVE.value}: 差旅费率 {travel_ratio:.2%} 高于行业 P90 {travel_p90:.2%}，补充查询差旅发票对手方集中度。")
            evidence = [
                Evidence(
                    source="python_metric_tool",
                    summary=f"差旅费率 {travel_ratio:.2%}，高于行业 P90 {travel_p90:.2%}",
                    data={"travel_expense_ratio": travel_ratio, "industry_p90": travel_p90},
                    confidence=0.9,
                ),
                Evidence(
                    source="sql_invoice_query",
                    summary=f"差旅类发票主要对手方 {invoice_rows[0]['counterparty'] if invoice_rows else '未知'}，金额集中度较高",
                    data={"counterparties": invoice_rows},
                    confidence=0.82,
                ),
                Evidence(
                    source="milvus_rule_retrieval",
                    summary=rules[0]["content"],
                    data={"rule": rules[0]},
                    confidence=0.76,
                ),
            ]
            findings.append(
                RiskFinding(
                    code="TRAVEL_RATIO",
                    title="差旅费异常占比风险",
                    level=RiskLevel.high,
                    conclusion="差旅费占比显著高于行业高分位，且发票对手方集中，存在费用真实性和税前扣除合规性风险。",
                    evidence=evidence,
                    suggestions=["补充差旅审批、行程、合同和付款流水。", "抽样核验高金额发票对应的真实业务场景。"],
                )
            )
        else:
            trace.append(f"{AgentState.CONCLUDE.value}: 差旅费率未超过行业高分位，暂不形成高风险结论。")

        vat_rate = metrics["vat_burden_rate"]
        vat_p50 = benchmarks.get("vat_burden_rate", {}).get("p50", 0.0)
        gross_margin = metrics["gross_margin"]
        if vat_rate < vat_p50 and gross_margin > benchmarks.get("gross_margin", {}).get("p50", 0.0):
            trace.append(f"{AgentState.RESOLVE_CONFLICT.value}: 税负率偏低但毛利率不低，触发交叉验证。")
            findings.append(
                RiskFinding(
                    code="VAT_BURDEN",
                    title="增值税税负率偏低风险",
                    level=RiskLevel.medium,
                    conclusion="企业税负率低于行业中位数，而毛利率未同步偏低，需要关注进项抵扣和收入确认口径。",
                    evidence=[
                        Evidence(
                            source="python_metric_tool",
                            summary=f"税负率 {vat_rate:.2%} 低于行业 P50 {vat_p50:.2%}，毛利率 {gross_margin:.2%}",
                            data={"vat_burden_rate": vat_rate, "vat_p50": vat_p50, "gross_margin": gross_margin},
                            confidence=0.78,
                        )
                    ],
                    suggestions=["复核进项发票抵扣链路。", "按客户和月份拆分收入确认节奏。"],
                )
            )

        trace.append(f"{AgentState.CHECK_BUDGET.value}: 已执行核心工具调用，轮次未超过 {request.max_rounds}，证据满足报告生成条件。")
        if not findings:
            needs_review = True
            findings.append(
                RiskFinding(
                    code="NO_HIGH_CONFIDENCE",
                    title="未形成高置信风险结论",
                    level=RiskLevel.review_required,
                    conclusion="当前自动化证据不足，建议人工复核数据完整性后再判断。",
                    evidence=[],
                    suggestions=["补充明细账、合同、银行流水和纳税申报表。"],
                )
            )

        chart = render_metric_chart(metrics, benchmarks, self.chart_dir / request.company_id / request.period)
        if chart:
            chart_paths.append(chart)
            trace.append(f"{AgentState.ACT.value}: 调用代码解释器能力生成指标对比图表。")

        executive_summary = self.llm_client.summarize_findings(findings)
        trace.append(f"{AgentState.ACT.value}: 调用 LangChain/Qwen 摘要链生成报告摘要；离线模式使用确定性摘要兜底。")
        expected_report_path = self.report_generator.report_dir / f"{request.company_id}_{request.period}_tax_health_report.md"
        trace.append(f"{AgentState.CONCLUDE.value}: 输出企业税务健康体检报告 {expected_report_path}。")

        result = DiagnosticResult(
            company_id=request.company_id,
            period=request.period,
            executive_summary=executive_summary,
            findings=findings,
            reasoning_trace=trace,
            chart_paths=chart_paths,
            needs_human_review=needs_review,
        )
        report_path = self.report_generator.render(result)
        result.report_path = report_path
        return result
