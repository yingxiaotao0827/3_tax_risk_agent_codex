from decimal import Decimal, ROUND_HALF_UP


def _round(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


class MetricTool:
    def calculate(self, financial: dict) -> dict[str, float]:
        revenue = financial["revenue"] or 1.0
        gross_margin = (financial["revenue"] - financial["cost"]) / revenue
        vat_burden_rate = financial["vat_paid"] / revenue
        travel_expense_ratio = financial["travel_expense"] / revenue
        consulting_expense_ratio = financial["consulting_expense"] / revenue
        travel_per_employee = financial["travel_expense"] / max(financial["employee_count"], 1)
        return {
            "gross_margin": _round(gross_margin),
            "vat_burden_rate": _round(vat_burden_rate),
            "travel_expense_ratio": _round(travel_expense_ratio),
            "consulting_expense_ratio": _round(consulting_expense_ratio),
            "travel_per_employee": _round(travel_per_employee),
        }

