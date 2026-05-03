from pathlib import Path

import pytest

from app.tax_risk_agent.data.sample_seed import seed_sample_database
from app.tax_risk_agent.data.database import TaxRiskDatabase
from app.tax_risk_agent.tools.sql_tool import SafeSqlTool


def test_sql_tool_allows_select(tmp_path: Path):
    db_path = tmp_path / "demo.sqlite"
    seed_sample_database(db_path)
    rows = SafeSqlTool(TaxRiskDatabase(db_path)).run(
        "SELECT company_id FROM financial_statements WHERE company_id = ?",
        ("demo_co",),
    )
    assert rows[0]["company_id"] == "demo_co"


def test_sql_tool_blocks_mutation(tmp_path: Path):
    db_path = tmp_path / "demo.sqlite"
    seed_sample_database(db_path)
    with pytest.raises(ValueError):
        SafeSqlTool(TaxRiskDatabase(db_path)).run("DELETE FROM financial_statements")

