from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]

def load_csvs_to_sqlite(db_path="logipulse.db"):
    """Load project CSV tables into a local SQLite database."""
    engine = create_engine(f"sqlite:///{ROOT / db_path}")
    for csv_path in (ROOT / "data").glob("*.csv"):
        table = csv_path.stem
        pd.read_csv(csv_path).to_sql(table, engine, if_exists="replace", index=False)
    return engine
