from app.tax_risk_agent.data.database import TaxRiskDatabase


class SafeSqlTool:
    def __init__(self, database: TaxRiskDatabase):
        self.database = database

    def run(self, sql: str, params: tuple = ()) -> list[dict]:
        normalized = sql.strip().lower()
        if not normalized.startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")
        blocked = (";", " drop ", " delete ", " update ", " insert ", " attach ", " pragma ")
        if any(token in f" {normalized} " for token in blocked):
            raise ValueError("Unsafe SQL detected.")
        return self.database.query(sql, params)

