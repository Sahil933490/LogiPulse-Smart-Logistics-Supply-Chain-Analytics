from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def load_data():
    names = ["shipments","orders","vehicles","warehouses","customers","routes","carriers"]
    return {name: pd.read_csv(DATA_DIR / f"{name}.csv") for name in names}

def prepare_data(raw):
    d = {k:v.copy() for k,v in raw.items()}
    s=d["shipments"]
    s["shipping_date"]=pd.to_datetime(s["shipping_date"],errors="coerce")
    s["expected_delivery"]=pd.to_datetime(s["expected_delivery"],errors="coerce")
    s["actual_delivery"]=pd.to_datetime(s["actual_delivery"],errors="coerce")
    s["expected_days"]=(s["expected_delivery"]-s["shipping_date"]).dt.days
    s["actual_days"]=(s["actual_delivery"]-s["shipping_date"]).dt.days
    s["is_on_time"]=(s["delivery_status"]=="Delivered On Time").astype(int)
    s["is_late"]=(s["delivery_status"]=="Delivered Late").astype(int)
    s=s.merge(d["warehouses"][["warehouse_id","region"]],on="warehouse_id",how="left")
    s=s.merge(d["carriers"][["carrier_id","carrier_name","base_rating"]],on="carrier_id",how="left")
    d["shipments"]=s
    return d
