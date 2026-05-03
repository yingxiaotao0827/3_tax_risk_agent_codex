from app.tax_risk_agent.vectorstore.rules import DEFAULT_RULES, TaxRule, embed_text


class RuleStore:
    def search(self, query: str, top_k: int = 3) -> list[TaxRule]:
        raise NotImplementedError


class InMemoryRuleStore(RuleStore):
    def __init__(self, rules: list[TaxRule] | None = None):
        self.rules = rules or DEFAULT_RULES

    def search(self, query: str, top_k: int = 3) -> list[TaxRule]:
        terms = set(query.lower().replace("_", " ").split())

        def score(rule: TaxRule) -> float:
            tag_score = len(terms.intersection(rule.tags)) * 3
            text = f"{rule.title} {rule.content}".lower()
            keyword_score = sum(1 for term in terms if term and term in text)
            return tag_score + keyword_score

        return sorted(self.rules, key=score, reverse=True)[:top_k]


class MilvusRuleStore(RuleStore):
    def __init__(self, uri: str, collection: str):
        from pymilvus import MilvusClient

        self.client = MilvusClient(uri=uri)
        self.collection = collection
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if self.client.has_collection(self.collection):
            return
        self.client.create_collection(
            collection_name=self.collection,
            dimension=16,
            metric_type="COSINE",
            auto_id=False,
        )
        self.client.insert(
            collection_name=self.collection,
            data=[
                {
                    "id": rule.rule_id,
                    "vector": embed_text(f"{rule.title} {rule.content}"),
                    "title": rule.title,
                    "content": rule.content,
                    "tags": ",".join(rule.tags),
                }
                for rule in DEFAULT_RULES
            ],
        )

    def search(self, query: str, top_k: int = 3) -> list[TaxRule]:
        results = self.client.search(
            collection_name=self.collection,
            data=[embed_text(query)],
            limit=top_k,
            output_fields=["title", "content", "tags"],
        )
        rules = []
        for hit in results[0]:
            entity = hit["entity"]
            rules.append(
                TaxRule(
                    rule_id=hit["id"],
                    title=entity["title"],
                    content=entity["content"],
                    tags=tuple(entity["tags"].split(",")),
                )
            )
        return rules


def build_rule_store(uri: str, collection: str) -> RuleStore:
    try:
        return MilvusRuleStore(uri=uri, collection=collection)
    except Exception:
        return InMemoryRuleStore()

