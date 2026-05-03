from pathlib import Path

from app.tax_risk_agent.data.database import TaxRiskDatabase


def seed_sample_database(path: Path) -> None:
    db = TaxRiskDatabase(path)
    with db.connect() as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS financial_statements;
            DROP TABLE IF EXISTS invoices;
            DROP TABLE IF EXISTS industry_benchmarks;

            CREATE TABLE financial_statements (
                company_id TEXT,
                period TEXT,
                revenue REAL,
                cost REAL,
                vat_paid REAL,
                travel_expense REAL,
                consulting_expense REAL,
                employee_count INTEGER
            );

            CREATE TABLE invoices (
                company_id TEXT,
                period TEXT,
                invoice_id TEXT,
                direction TEXT,
                counterparty TEXT,
                category TEXT,
                amount REAL,
                tax_amount REAL
            );

            CREATE TABLE industry_benchmarks (
                industry TEXT,
                period TEXT,
                metric TEXT,
                p50 REAL,
                p75 REAL,
                p90 REAL
            );
            """
        )
        conn.executemany(
            "INSERT INTO financial_statements VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("demo_co", "2025Q2", 12_000_000, 8_400_000, 360_000, 980_000, 1_250_000, 82),
                ("healthy_co", "2025Q2", 10_500_000, 7_200_000, 510_000, 260_000, 310_000, 96),
            ],
        )
        conn.executemany(
            "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("demo_co", "2025Q2", "INV-001", "in", "上海捷旅服务有限公司", "travel", 330_000, 19_800),
                ("demo_co", "2025Q2", "INV-002", "in", "上海捷旅服务有限公司", "travel", 310_000, 18_600),
                ("demo_co", "2025Q2", "INV-003", "in", "杭州云策咨询有限公司", "consulting", 690_000, 41_400),
                ("demo_co", "2025Q2", "INV-004", "out", "华东客户A", "sales", 3_400_000, 204_000),
                ("healthy_co", "2025Q2", "INV-101", "in", "北京差旅服务有限公司", "travel", 80_000, 4_800),
                ("healthy_co", "2025Q2", "INV-102", "out", "华北客户B", "sales", 2_900_000, 174_000),
            ],
        )
        conn.executemany(
            "INSERT INTO industry_benchmarks VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("software_services", "2025Q2", "travel_expense_ratio", 0.018, 0.032, 0.055),
                ("software_services", "2025Q2", "vat_burden_rate", 0.038, 0.048, 0.062),
                ("software_services", "2025Q2", "gross_margin", 0.24, 0.31, 0.42),
            ],
        )
        conn.commit()

