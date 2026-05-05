"""Tax Risk Diagnostic Agent 的 FastAPI 应用入口。

本模块负责完成 Web 服务启动阶段的基础装配，包括日志初始化、配置读取、
FastAPI 应用创建、跨域设置、静态前端挂载，以及诊断 Agent 的依赖组装。
对外提供健康检查、前端页面、示例数据初始化和税务风险诊断执行接口。
"""

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

# 启动流程 1：先配置全局日志，保证后续应用启动和请求处理过程可以统一输出日志。
configure_logging()

# 启动流程 2：读取应用配置；配置来源包括默认值和项目根目录下的 .env 文件。
settings = get_settings()

# 启动流程 3：创建 FastAPI 应用对象，声明服务名称和版本。
app = FastAPI(title="Tax Risk Diagnostic Agent", version="0.1.0")

# 启动流程 4：配置跨域访问，方便前端页面或其他客户端调用当前 API 服务。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动流程 5：定位当前 API 包下的 static 目录，用于托管浏览器端页面和静态资源。
STATIC_DIR = Path(__file__).resolve().parent / "static"

# 启动流程 6：把 /static 路径挂载为静态文件服务，前端资源可通过该路径访问。
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def build_agent() -> TaxRiskDiagnosticAgent:
    """按当前配置组装一次税务风险诊断 Agent。"""
    # 诊断流程准备 1：根据配置中的数据库路径创建数据库访问对象。
    database = TaxRiskDatabase(settings.database_url)

    # 诊断流程准备 2：连接或构建规则向量库，用于后续税务规则召回。
    rule_store = build_rule_store(settings.milvus_uri, settings.milvus_collection)

    # 诊断流程准备 3：把数据库、规则工具、报告生成器、图表目录和 LLM 客户端注入 Agent。
    return TaxRiskDiagnosticAgent(
        database=database,
        rule_tool=RuleRetrievalTool(rule_store),
        report_generator=ReportGenerator(settings.report_dir),
        chart_dir=settings.report_dir / "charts",
        llm_client=build_llm_client(settings.llm_provider, settings.llm_base_url, settings.llm_api_key, settings.llm_model),
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """健康检查接口，用于确认 API 服务是否存活。"""
    # 请求流程：客户端访问 /healthz 时返回固定状态，通常给部署平台或监控系统调用。
    return {"status": "ok"}


@app.get("/")
def frontend() -> FileResponse:
    """返回前端首页文件。"""
    # 请求流程：浏览器访问根路径时，返回 static/index.html 作为用户界面入口。
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/v1/demo/seed")
def seed_demo_data() -> dict[str, str]:
    """初始化或刷新演示数据库数据。"""
    # 请求流程：调用示例数据写入函数，把 demo 数据种入配置指定的 SQLite 数据库。
    seed_sample_database(settings.database_url)

    # 响应流程：返回执行状态和实际写入的数据库路径，方便调用方确认目标位置。
    return {"status": "ok", "database": str(settings.database_url)}


@app.post("/api/v1/diagnostics/run", response_model=DiagnosticResult)
def run_diagnostic(request: DiagnosticRequest) -> DiagnosticResult:
    """执行税务风险诊断并返回结构化结果。"""
    # 请求流程：FastAPI 先把请求体解析为 DiagnosticRequest，再交给诊断 Agent 执行完整诊断。
    return build_agent().run(request)
