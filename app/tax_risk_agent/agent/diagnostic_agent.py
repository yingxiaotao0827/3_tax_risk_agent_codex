from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.tax_risk_agent.agent.state_machine import AgentState
from app.tax_risk_agent.core.llm_client import LLMClient, OfflineLLMClient
from app.tax_risk_agent.data.database import TaxRiskDatabase
from app.tax_risk_agent.models.domain import DiagnosticRequest, DiagnosticResult, Evidence, RiskFinding, RiskLevel
from app.tax_risk_agent.reports.charting import render_metric_chart
from app.tax_risk_agent.reports.report_generator import ReportGenerator
from app.tax_risk_agent.tools.metric_tool import MetricTool
from app.tax_risk_agent.tools.rule_tool import RuleRetrievalTool
from app.tax_risk_agent.tools.sql_tool import SafeSqlTool


@dataclass(frozen=True)
class RiskScenario:
    code: str
    title: str
    metric: str
    benchmark_metric: str
    benchmark_field: str
    operator: str
    level: RiskLevel
    rule_query: str
    conclusion_template: str
    suggestions: list[str]
    invoice_category: str | None = None
    cross_check: Callable[[dict, dict], Evidence | None] | None = None


def vat_gross_margin_cross_check(metrics: dict, benchmarks: dict) -> Evidence | None:
    gross_margin_p50 = benchmarks.get("gross_margin", {}).get("p50")
    gross_margin = metrics.get("gross_margin")
    if gross_margin is None or gross_margin_p50 is None:
        return Evidence(
            source="benchmark_cross_check",
            summary="缺少毛利率或行业毛利率基准，税负率偏低无法完成交叉验证。",
            data={"gross_margin": gross_margin, "gross_margin_p50": gross_margin_p50},
            confidence=0.45,
        )
    if gross_margin >= gross_margin_p50:
        return Evidence(
            source="benchmark_cross_check",
            summary=f"毛利率 {gross_margin:.2%} 不低于行业 P50 {gross_margin_p50:.2%}，但税负率偏低，存在进项抵扣或收入确认异常信号。",
            data={"gross_margin": gross_margin, "gross_margin_p50": gross_margin_p50},
            confidence=0.78,
        )
    return None


DEFAULT_RISK_SCENARIOS = [
    RiskScenario(
        code="TRAVEL_RATIO",
        title="差旅费异常占比风险",
        metric="travel_expense_ratio",
        benchmark_metric="travel_expense_ratio",
        benchmark_field="p90",
        operator=">",
        level=RiskLevel.high,
        rule_query="travel expense invoice",
        invoice_category="travel",
        conclusion_template="{metric_label} {metric_value:.2%} 高于行业 {benchmark_field_upper} {benchmark_value:.2%}，且存在进一步核验空间，可能涉及费用真实性或税前扣除合规风险。",
        suggestions=["补充差旅审批、行程记录、合同和付款流水。", "抽样核验高金额差旅发票对应的真实业务场景。"],
    ),
    RiskScenario(
        code="VAT_BURDEN",
        title="增值税税负率偏低风险",
        metric="vat_burden_rate",
        benchmark_metric="vat_burden_rate",
        benchmark_field="p50",
        operator="<",
        level=RiskLevel.medium,
        rule_query="vat burden revenue invoice",
        cross_check=vat_gross_margin_cross_check,
        conclusion_template="{metric_label} {metric_value:.2%} 低于行业 {benchmark_field_upper} {benchmark_value:.2%}，且毛利率未同步偏低，需要关注进项抵扣和收入确认口径。",
        suggestions=["复核进项发票抵扣链路。", "按客户和月份拆分收入确认节奏。", "检查是否存在异常进项抵扣或收入递延确认。"],
    ),
    RiskScenario(
        code="CONSULTING_CLUSTER",
        title="咨询服务费集中复核风险",
        metric="consulting_expense_ratio",
        benchmark_metric="consulting_expense_ratio",
        benchmark_field="p75",
        operator=">",
        level=RiskLevel.review_required,
        rule_query="consulting counterparty invoice",
        invoice_category="consulting",
        conclusion_template="咨询费率 {metric_value:.2%} 暂缺可比行业基准或交付材料证据，不能自动认定风险，需要人工复核真实性。",
        suggestions=["补充咨询合同、项目验收单、咨询报告和付款流水。", "核验咨询服务商经营能力及是否存在关联关系。"],
    ),
]

METRIC_LABELS = {
    "travel_expense_ratio": "差旅费率",
    "vat_burden_rate": "增值税税负率",
    "gross_margin": "毛利率",
    "consulting_expense_ratio": "咨询费率",
    "travel_per_employee": "人均差旅费",
}


class TaxRiskDiagnosticAgent:
    def __init__(
        self,
        database: TaxRiskDatabase,
        rule_tool: RuleRetrievalTool,
        report_generator: ReportGenerator,
        chart_dir: Path,
        llm_client: LLMClient | None = None,
        risk_scenarios: list[RiskScenario] | None = None,
    ):
        self.database = database
        self.sql_tool = SafeSqlTool(database)
        self.metric_tool = MetricTool()
        self.rule_tool = rule_tool
        self.report_generator = report_generator
        self.chart_dir = chart_dir
        self.llm_client = llm_client or OfflineLLMClient()
        self.risk_scenarios = risk_scenarios or DEFAULT_RISK_SCENARIOS

    def run(self, request: DiagnosticRequest) -> DiagnosticResult:
        trace: list[str] = []
        findings: list[RiskFinding] = []
        chart_paths: list[Path] = []

        trace.append(f"{AgentState.THINK.value}: 读取企业 {request.company_id} 在 {request.period} 的财务与发票数据，准备按风险场景生成诊断假设。")
        financial = self._load_financial(request, trace)
        if financial is None:
            return DiagnosticResult(
                company_id=request.company_id,
                period=request.period,
                findings=[
                    RiskFinding(
                        code="DATA_MISSING",
                        title="企业期间数据缺失",
                        level=RiskLevel.review_required,
                        conclusion="未找到企业期间财务数据，无法自动诊断。",
                        evidence=[],
                        suggestions=["确认企业编号、期间和数据同步任务是否正确。"],
                    )
                ],
                reasoning_trace=trace,
                needs_human_review=True,
            )

        metrics = self.metric_tool.calculate(financial)
        trace.append(f"{AgentState.ACT.value}: 调用 Python 指标计算工具，得到 {', '.join(sorted(metrics))}。")

        benchmarks = self._load_benchmarks(request, trace)
        all_rules = self.rule_tool.run("tax risk invoice expense vat consulting revenue")
        trace.append(f"{AgentState.ACT.value}: 调用规则库检索工具召回 {len(all_rules)} 条候选税务规则。")

        for scenario in self.risk_scenarios:
            trace.append(f"{AgentState.THINK.value}: 基于风险场景 {scenario.code} 生成假设：{scenario.title}。")
            finding = self._evaluate_scenario(
                request=request,
                scenario=scenario,
                metrics=metrics,
                benchmarks=benchmarks,
                rules=all_rules,
                trace=trace,
            )
            if finding:
                findings.append(finding)

        findings.extend(self._surface_unhandled_rules(all_rules, findings, trace))

        if not findings:
            findings.append(
                RiskFinding(
                    code="NO_HIGH_CONFIDENCE",
                    title="未形成高置信风险结论",
                    level=RiskLevel.review_required,
                    conclusion="当前自动化证据不足，建议人工复核数据完整性后再判断。",
                    evidence=[],
                    suggestions=["补充明细账、合同、银行流水、发票附件和纳税申报表。"],
                )
            )

        trace.append(
            f"{AgentState.CHECK_BUDGET.value}: 已完成 {len(self.risk_scenarios)} 个风险场景扫描；"
            "本次请求执行一次完整诊断闭环。若后续补充合同、付款流水或行业基准，应基于新证据重新发起诊断。"
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
            needs_human_review=any(finding.level == RiskLevel.review_required for finding in findings),
        )
        result.report_path = self.report_generator.render(result)
        return result

    def _load_financial(self, request: DiagnosticRequest, trace: list[str]) -> dict | None:
        rows = self.sql_tool.run(
            "SELECT * FROM financial_statements WHERE company_id = ? AND period = ?",
            (request.company_id, request.period),
        )
        if not rows:
            trace.append(f"{AgentState.HUMAN_REVIEW.value}: 未找到企业期间数据，建议人工确认数据口径。")
            return None
        return rows[0]

    def _load_benchmarks(self, request: DiagnosticRequest, trace: list[str]) -> dict[str, dict]:
        rows = self.sql_tool.run(
            "SELECT metric, p50, p75, p90 FROM industry_benchmarks WHERE industry = ? AND period = ?",
            ("software_services", request.period),
        )
        trace.append(f"{AgentState.ACT.value}: 调用 SQL 查询器读取软件服务行业 {request.period} 分位基准。")
        return {row["metric"]: row for row in rows}

    def _evaluate_scenario(
        self,
        request: DiagnosticRequest,
        scenario: RiskScenario,
        metrics: dict,
        benchmarks: dict,
        rules: list[dict],
        trace: list[str],
    ) -> RiskFinding | None:
        trace.append(f"{AgentState.EVALUATE_EVIDENCE.value}: 评估 {scenario.title} 的指标、行业基准、规则和明细证据。")

        metric_value = metrics.get(scenario.metric)
        benchmark_value = benchmarks.get(scenario.benchmark_metric, {}).get(scenario.benchmark_field)
        matched_rule = self._match_rule(scenario, rules)

        if metric_value is None:
            return self._review_required(
                scenario=scenario,
                reason=f"缺少指标 {scenario.metric}，无法自动判断。",
                evidence=[],
            )

        evidence = [
            Evidence(
                source="python_metric_tool",
                summary=f"{METRIC_LABELS.get(scenario.metric, scenario.metric)}为 {metric_value:.2%}。",
                data={scenario.metric: metric_value},
                confidence=0.82,
            )
        ]

        if benchmark_value is None:
            trace.append(f"{AgentState.HUMAN_REVIEW.value}: {scenario.title} 缺少行业基准 {scenario.benchmark_metric}.{scenario.benchmark_field}，转人工复核。")
            if matched_rule:
                evidence.append(self._rule_evidence(matched_rule))
            return self._review_required(
                scenario=scenario,
                reason=scenario.conclusion_template.format(
                    metric_label=METRIC_LABELS.get(scenario.metric, scenario.metric),
                    metric_value=metric_value,
                    benchmark_field_upper=scenario.benchmark_field.upper(),
                    benchmark_value=0.0,
                ),
                evidence=evidence,
            )

        evidence.append(
            Evidence(
                source="industry_benchmark",
                summary=f"行业 {scenario.benchmark_field.upper()} 为 {benchmark_value:.2%}。",
                data={scenario.benchmark_metric: {scenario.benchmark_field: benchmark_value}},
                confidence=0.86,
            )
        )

        if not self._compare(metric_value, benchmark_value, scenario.operator):
            trace.append(
                f"{AgentState.CONCLUDE.value}: {scenario.title} 未触发，{metric_value:.2%} 未满足 {scenario.operator} {benchmark_value:.2%}。"
            )
            return None

        if scenario.invoice_category:
            invoice_evidence = self._invoice_concentration_evidence(request, scenario.invoice_category)
            evidence.append(invoice_evidence)
            trace.append(f"{AgentState.OBSERVE.value}: 补充查询 {scenario.invoice_category} 类发票对手方集中度。")

        if matched_rule:
            evidence.append(self._rule_evidence(matched_rule))

        if scenario.cross_check:
            cross_evidence = scenario.cross_check(metrics, benchmarks)
            if cross_evidence is None:
                trace.append(f"{AgentState.RESOLVE_CONFLICT.value}: {scenario.title} 交叉验证未支持风险升级。")
                return None
            evidence.append(cross_evidence)
            trace.append(f"{AgentState.RESOLVE_CONFLICT.value}: {scenario.title} 完成交叉验证。")

        return RiskFinding(
            code=scenario.code,
            title=scenario.title,
            level=scenario.level,
            conclusion=scenario.conclusion_template.format(
                metric_label=METRIC_LABELS.get(scenario.metric, scenario.metric),
                metric_value=metric_value,
                benchmark_field_upper=scenario.benchmark_field.upper(),
                benchmark_value=benchmark_value,
            ),
            evidence=evidence,
            suggestions=scenario.suggestions,
        )

    def _invoice_concentration_evidence(self, request: DiagnosticRequest, category: str) -> Evidence:
        rows = self.sql_tool.run(
            """
            SELECT counterparty, COUNT(*) AS invoice_count, SUM(amount) AS amount
            FROM invoices
            WHERE company_id = ? AND period = ? AND category = ?
            GROUP BY counterparty
            ORDER BY amount DESC
            """,
            (request.company_id, request.period, category),
        )
        top_counterparty = rows[0]["counterparty"] if rows else "未知"
        return Evidence(
            source="sql_invoice_query",
            summary=f"{category} 类发票主要对手方为 {top_counterparty}，需结合业务材料判断集中度是否合理。",
            data={"category": category, "counterparties": rows},
            confidence=0.78 if rows else 0.45,
        )

    def _surface_unhandled_rules(self, rules: list[dict], findings: list[RiskFinding], trace: list[str]) -> list[RiskFinding]:
        handled_codes = {finding.code for finding in findings}
        scenario_codes = {scenario.code for scenario in self.risk_scenarios}
        review_findings = []
        for rule in rules:
            rule_id = rule.get("rule_id")
            if not rule_id or rule_id in handled_codes or rule_id in scenario_codes:
                continue
            trace.append(f"{AgentState.HUMAN_REVIEW.value}: 规则 {rule_id} 已召回，但当前版本缺少自动化证据采集器，生成复核提示。")
            review_findings.append(
                RiskFinding(
                    code=rule_id,
                    title=f"{rule.get('title', rule_id)}复核提示",
                    level=RiskLevel.review_required,
                    conclusion="规则库召回了相关税务风险规则，但当前系统缺少对应指标、明细或外部证据采集器，不能自动下结论。",
                    evidence=[self._rule_evidence(rule)],
                    suggestions=["补充该风险场景的数据口径、指标计算器和专项证据查询工具。"],
                )
            )
        return review_findings

    def _review_required(self, scenario: RiskScenario, reason: str, evidence: list[Evidence]) -> RiskFinding:
        return RiskFinding(
            code=scenario.code,
            title=scenario.title,
            level=RiskLevel.review_required,
            conclusion=reason,
            evidence=evidence,
            suggestions=scenario.suggestions,
        )

    def _match_rule(self, scenario: RiskScenario, rules: list[dict]) -> dict | None:
        for rule in rules:
            if rule.get("rule_id") == scenario.code:
                return rule
        scenario_rules = self.rule_tool.run(scenario.rule_query, top_k=1)
        return scenario_rules[0] if scenario_rules else None

    def _rule_evidence(self, rule: dict) -> Evidence:
        return Evidence(
            source="rule_retrieval_tool",
            summary=rule["content"],
            data={"rule": rule},
            confidence=0.76,
        )

    def _compare(self, metric_value: float, benchmark_value: float, operator: str) -> bool:
        if operator == ">":
            return metric_value > benchmark_value
        if operator == ">=":
            return metric_value >= benchmark_value
        if operator == "<":
            return metric_value < benchmark_value
        if operator == "<=":
            return metric_value <= benchmark_value
        raise ValueError(f"Unsupported operator: {operator}")
