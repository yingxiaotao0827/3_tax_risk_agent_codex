from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.tax_risk_agent.agent.diagnostic_agent import TaxRiskDiagnosticAgent
from app.tax_risk_agent.core.config import get_settings
from app.tax_risk_agent.core.llm_client import build_llm_client
from app.tax_risk_agent.core.logging import configure_logging
from app.tax_risk_agent.data.sample_seed import seed_sample_database
from app.tax_risk_agent.data.database import TaxRiskDatabase
from app.tax_risk_agent.models.domain import DiagnosticRequest, DiagnosticResult
from app.tax_risk_agent.reports.report_generator import ReportGenerator
from app.tax_risk_agent.tools.rule_tool import RuleRetrievalTool
from app.tax_risk_agent.vectorstore.rule_store import build_rule_store

configure_logging()
settings = get_settings()

app = FastAPI(title="Tax Risk Diagnostic Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def build_agent() -> TaxRiskDiagnosticAgent:
    database = TaxRiskDatabase(settings.database_url)
    rule_store = build_rule_store(settings.milvus_uri, settings.milvus_collection)
    return TaxRiskDiagnosticAgent(
        database=database,
        rule_tool=RuleRetrievalTool(rule_store),
        report_generator=ReportGenerator(settings.report_dir),
        chart_dir=settings.report_dir / "charts",
        llm_client=build_llm_client(settings.llm_provider, settings.llm_base_url, settings.llm_api_key, settings.llm_model),
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/v1/demo/seed")
def seed_demo_data() -> dict[str, str]:
    seed_sample_database(settings.database_url)
    return {"status": "ok", "database": str(settings.database_url)}


@app.post("/api/v1/diagnostics/run", response_model=DiagnosticResult)
def run_diagnostic(request: DiagnosticRequest) -> DiagnosticResult:
    return build_agent().run(request)
