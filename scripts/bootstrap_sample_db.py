from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tax_risk_agent.data.sample_seed import seed_sample_database


if __name__ == "__main__":
    path = Path("data/tax_risk_demo.sqlite")
    seed_sample_database(path)
    print(f"Seeded sample database at {path}")
