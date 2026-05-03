from app.tax_risk_agent.tools.metric_tool import MetricTool


def test_metric_tool_calculates_tax_metrics():
    metrics = MetricTool().calculate(
        {
            "revenue": 1000,
            "cost": 600,
            "vat_paid": 40,
            "travel_expense": 80,
            "consulting_expense": 50,
            "employee_count": 10,
        }
    )

    assert metrics["gross_margin"] == 0.4
    assert metrics["vat_burden_rate"] == 0.04
    assert metrics["travel_expense_ratio"] == 0.08
    assert metrics["travel_per_employee"] == 8.0

