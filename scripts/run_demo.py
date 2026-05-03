from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tax_risk_agent.agent.diagnostic_agent import TaxRiskDiagnosticAgent
from app.tax_risk_agent.core.config import get_settings
from app.tax_risk_agent.core.llm_client import build_llm_client
from app.tax_risk_agent.data.database import TaxRiskDatabase
from app.tax_risk_agent.data.sample_seed import seed_sample_database
from app.tax_risk_agent.models.domain import DiagnosticRequest
from app.tax_risk_agent.reports.report_generator import ReportGenerator
from app.tax_risk_agent.tools.rule_tool import RuleRetrievalTool
from app.tax_risk_agent.vectorstore.rule_store import build_rule_store


if __name__ == "__main__":
    settings = get_settings()
    seed_sample_database(settings.database_url)
    agent = TaxRiskDiagnosticAgent(
        database=TaxRiskDatabase(settings.database_url),
        rule_tool=RuleRetrievalTool(build_rule_store(settings.milvus_uri, settings.milvus_collection)),
        report_generator=ReportGenerator(settings.report_dir),
        chart_dir=settings.report_dir / "charts",
        llm_client=build_llm_client(settings.llm_provider, settings.llm_base_url, settings.llm_api_key, settings.llm_model),
    )
    result = agent.run(DiagnosticRequest(company_id="demo_co", period="2025Q2"))
    print(result.model_dump_json(indent=2))
