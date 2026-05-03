from pathlib import Path

from app.tax_risk_agent.agent.diagnostic_agent import TaxRiskDiagnosticAgent
from app.tax_risk_agent.data.database import TaxRiskDatabase
from app.tax_risk_agent.data.sample_seed import seed_sample_database
from app.tax_risk_agent.models.domain import DiagnosticRequest, RiskLevel
from app.tax_risk_agent.reports.report_generator import ReportGenerator
from app.tax_risk_agent.tools.rule_tool import RuleRetrievalTool
from app.tax_risk_agent.vectorstore.rule_store import InMemoryRuleStore


def test_agent_generates_tax_risk_report(tmp_path: Path):
    db_path = tmp_path / "demo.sqlite"
    report_dir = tmp_path / "reports"
    seed_sample_database(db_path)
    agent = TaxRiskDiagnosticAgent(
        database=TaxRiskDatabase(db_path),
        rule_tool=RuleRetrievalTool(InMemoryRuleStore()),
        report_generator=ReportGenerator(report_dir),
        chart_dir=report_dir / "charts",
    )

    result = agent.run(DiagnosticRequest(company_id="demo_co", period="2025Q2"))

    assert result.report_path is not None
    assert result.report_path.exists()
    assert any(finding.level == RiskLevel.high for finding in result.findings)
    assert any("差旅费" in finding.title for finding in result.findings)

