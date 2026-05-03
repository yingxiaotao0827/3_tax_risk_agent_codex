from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class TaxRule:
    rule_id: str
    title: str
    content: str
    tags: tuple[str, ...]


DEFAULT_RULES = [
    TaxRule(
        "TRAVEL_RATIO",
        "差旅费异常占比",
        "差旅费占营业收入比例显著高于行业分位值时，应结合发票对手方集中度、员工人数、出差业务背景核验真实性。",
        ("travel", "expense", "invoice"),
    ),
    TaxRule(
        "VAT_BURDEN",
        "税负率异常",
        "增值税税负率低于行业中位数且毛利率未同步下降时，需关注收入确认、进项抵扣和异常发票流向。",
        ("vat", "burden", "revenue"),
    ),
    TaxRule(
        "CONSULTING_CLUSTER",
        "咨询服务费集中",
        "咨询服务类进项发票金额大、对手方集中或缺少服务交付证据时，应提示补充合同、成果物和付款流水。",
        ("consulting", "counterparty", "invoice"),
    ),
]


def embed_text(text: str) -> list[float]:
    buckets = [0.0] * 16
    for index, char in enumerate(text.lower()):
        buckets[index % len(buckets)] += (ord(char) % 31) / 31
    norm = sqrt(sum(item * item for item in buckets)) or 1.0
    return [item / norm for item in buckets]

