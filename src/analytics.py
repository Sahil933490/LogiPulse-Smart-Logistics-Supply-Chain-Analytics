import pandas as pd

def calculate_kpis(df):
    total=len(df)
    delivered=df[df["delivery_status"]!="In Transit"]
    on_time=(delivered["is_on_time"].mean()*100) if len(delivered) else 0
    return {
        "shipments":total,
        "on_time":on_time,
        "late":int((df["delivery_status"]=="Delivered Late").sum()),
        "cost":float(df["shipping_cost"].sum()),
        "distance":float(df["distance_km"].mean()) if total else 0
    }

def monthly_trends(df):
    x=df.copy()
    x["month"]=x["shipping_date"].dt.to_period("M").astype(str)
    out=x.groupby("month",as_index=False).agg(shipments=("shipment_id","count"),on_time_pct=("is_on_time","mean"))
    out["on_time_pct"]=out["on_time_pct"]*100
    return out

def route_cost_analysis(df):
    out=df.groupby(["origin","destination"],as_index=False).agg(
        shipments=("shipment_id","count"),
        shipping_cost=("shipping_cost","sum"),
        avg_cost=("shipping_cost","mean"),
        distance_km=("distance_km","mean"),
        late_rate=("is_late","mean")
    )
    out["late_rate"]=out["late_rate"]*100
    out["route"]=out["origin"]+" → "+out["destination"]
    return out.sort_values("shipping_cost",ascending=False)
