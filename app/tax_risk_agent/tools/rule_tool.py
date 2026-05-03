from app.tax_risk_agent.vectorstore.rule_store import RuleStore


class RuleRetrievalTool:
    def __init__(self, store: RuleStore):
        self.store = store

    def run(self, query: str) -> list[dict]:
        return [
            {
                "rule_id": rule.rule_id,
                "title": rule.title,
                "content": rule.content,
                "tags": list(rule.tags),
            }
            for rule in self.store.search(query)
        ]

