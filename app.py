import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.data_processing import load_data, prepare_data
from src.analytics import calculate_kpis, monthly_trends, route_cost_analysis
from src.ml_models import train_delay_model, predict_risk
from src.recommendations import build_recommendations

st.set_page_config(page_title="LogiPulse | Logistics Control Tower", page_icon="🚚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background: radial-gradient(circle at 12% 0%, #17345a 0, #0b1424 34%, #08111f 75%); color:#edf4ff;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#101f35,#0b1424); border-right:1px solid #203a5c;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif;color:#f4f8ff;}
.hero {padding:26px 30px;border:1px solid #24476d;border-radius:20px;background:linear-gradient(110deg,rgba(21,54,88,.95),rgba(13,29,50,.82));margin-bottom:18px;}
.hero-kicker {color:#66d9e8;letter-spacing:2px;font-size:11px;font-weight:700;}
.hero-title {font-size:34px;font-weight:700;margin:4px 0;color:#fff;}
.hero-sub {color:#b9cbe0;font-size:14px;}
.metric {background:linear-gradient(145deg,rgba(25,54,85,.95),rgba(13,30,50,.95));border:1px solid #25496b;border-radius:16px;padding:17px 18px;min-height:112px;}
.metric-label {font-size:12px;color:#9fb6cf;font-weight:600;letter-spacing:.6px;text-transform:uppercase;}
.metric-value {font-family:'Space Grotesk';font-size:27px;font-weight:700;color:#f5f9ff;margin-top:7px;}
.metric-note {font-size:11px;color:#65d9c5;margin-top:2px;}
.section-note {color:#9fb6cf;font-size:13px;margin-top:-8px;margin-bottom:12px;}
div[data-testid="stPlotlyChart"] {background:rgba(12,27,46,.55);border:1px solid #1f3a59;border-radius:14px;padding:8px;}
div[data-testid="stDataFrame"] {border:1px solid #24476d;border-radius:12px;}
.stButton>button {border-radius:10px;border:1px solid #3676a8;background:#123d62;color:white;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    raw = load_data()
    return prepare_data(raw)

data = get_data()
ship = data["shipments"].copy()
# Sidebar filters
st.sidebar.markdown("## 🚚 LogiPulse")
st.sidebar.caption("SMART LOGISTICS CONTROL TOWER")
min_date = pd.to_datetime(ship["shipping_date"]).min().date()
max_date = pd.to_datetime(ship["shipping_date"]).max().date()
date_range = st.sidebar.date_input("Shipping date range", value=(min_date,max_date), min_value=min_date, max_value=max_date)
regions = sorted(data["warehouses"]["region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Warehouse region", regions, default=regions)
modes = sorted(ship["shipping_mode"].dropna().unique().tolist())
selected_modes = st.sidebar.multiselect("Shipping mode", modes, default=modes)
if isinstance(date_range, tuple) and len(date_range)==2:
    start_date,end_date=date_range
else:
    start_date,end_date=min_date,max_date
filtered = ship[
    pd.to_datetime(ship["shipping_date"]).dt.date.between(start_date,end_date)
    & ship["region"].isin(selected_regions)
    & ship["shipping_mode"].isin(selected_modes)
].copy()

pages = ["Executive Overview","Shipment Analytics","Fleet & Transport","Warehouse Analytics","Cost Optimisation","Delay Prediction","Smart Recommendations"]
page = st.sidebar.radio("NAVIGATION",pages)
st.sidebar.markdown("---")
st.sidebar.caption("Demo environment • Synthetic data • Updated on app load")
st.markdown("""
<div class="hero">
<div class="hero-kicker">LOGISTICS INTELLIGENCE PLATFORM</div>
<div class="hero-title">LOGIPULSE <span style="color:#65d9e8">/</span> Control Tower</div>
<div class="hero-sub">A unified view of shipment execution, fleet performance, warehouse operations and predictive delivery risk.</div>
</div>
""",unsafe_allow_html=True)

if filtered.empty:
    st.warning("No shipments match the selected filters. Widen the date range or select more regions/modes.")
    st.stop()

kpis=calculate_kpis(filtered)
def metric(col,label,value,note="Filtered operational view"):
    col.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)

if page=="Executive Overview":
    st.subheader("Executive Overview")
    st.markdown('<div class="section-note">A decision-ready snapshot of logistics health across the selected period.</div>',unsafe_allow_html=True)
    c=st.columns(5)
    metric(c[0],"Shipments",f'{kpis["shipments"]:,}')
    metric(c[1],"On-time delivery",f'{kpis["on_time"]:.1f}%')
    metric(c[2],"Late / at-risk",f'{kpis["late"]:,}')
    metric(c[3],"Logistics spend",f'₹{kpis["cost"]/1e6:.2f}M')
    metric(c[4],"Avg. distance",f'{kpis["distance"]:.0f} km')
    left,right=st.columns([1.45,1])
    monthly=monthly_trends(filtered)
    with left:
        st.markdown("### Shipment & delivery trend")
        fig=go.Figure()
        fig.add_trace(go.Bar(x=monthly["month"],y=monthly["shipments"],name="Shipments",marker_color="#45b8d8"))
        fig.add_trace(go.Scatter(x=monthly["month"],y=monthly["on_time_pct"],name="On-time %",yaxis="y2",line=dict(color="#68e0b9",width=3)))
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(title="Shipments"),yaxis2=dict(title="On-time %",overlaying="y",side="right",range=[0,100]),legend=dict(orientation="h",y=1.12),margin=dict(l=10,r=10,t=35,b=10),height=350)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("### Delivery status mix")
        counts=filtered["delivery_status"].value_counts().reset_index()
        counts.columns=["status","count"]
        fig=px.pie(counts,names="status",values="count",hole=.62,color="status",color_discrete_map={"Delivered On Time":"#35c7a0","Delivered Late":"#ff766e","In Transit":"#f6b94b"})
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=350,legend_title="")
        st.plotly_chart(fig,use_container_width=True)
    a,b=st.columns(2)
    with a:
        st.markdown("### Regional shipment footprint")
        reg=filtered.groupby("region",as_index=False).agg(shipments=("shipment_id","count"),cost=("shipping_cost","sum"))
        fig=px.bar(reg,x="region",y="shipments",color="cost",color_continuous_scale="Teal",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=300)
        st.plotly_chart(fig,use_container_width=True)
    with b:
        st.markdown("### Shipping mode split")
        md=filtered.groupby("shipping_mode",as_index=False).agg(shipments=("shipment_id","count"),cost=("shipping_cost","sum"))
        fig=px.bar(md,x="shipping_mode",y="cost",color="shipping_mode",template="plotly_dark",color_discrete_sequence=["#45b8d8","#68e0b9","#f6b94b"])
        fig.update_layout(showlegend=False,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=300)
        st.plotly_chart(fig,use_container_width=True)

elif page=="Shipment Analytics":
    st.subheader("Shipment Analytics")
    c=st.columns(4)
    metric(c[0],"Avg. delivery promise",f'{filtered["expected_days"].mean():.1f} days')
    metric(c[1],"Avg. actual transit",f'{filtered.loc[filtered["actual_days"].notna(),"actual_days"].mean():.1f} days')
    metric(c[2],"Express share",f'{(filtered["shipping_mode"].eq("Air").mean()*100):.1f}%')
    metric(c[3],"Avg. shipment weight",f'{filtered["weight_kg"].mean():,.0f} kg')
    l,r=st.columns(2)
    with l:
        st.markdown("### Carrier performance")
        carrier=filtered.groupby("carrier_name",as_index=False).agg(shipments=("shipment_id","count"),on_time=("is_on_time","mean"))
        carrier["on_time_pct"]=carrier.on_time*100
        fig=px.bar(carrier.sort_values("on_time_pct"),x="on_time_pct",y="carrier_name",orientation="h",color="on_time_pct",color_continuous_scale="Teal",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=420,xaxis_title="On-time delivery (%)",yaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
    with r:
        st.markdown("### Delay drivers")
        delay=filtered.assign(delayed=filtered["is_late"].astype(int)).groupby("weather",as_index=False).agg(delay_rate=("delayed","mean"),shipments=("shipment_id","count"))
        delay["delay_rate"]*=100
        fig=px.bar(delay,x="weather",y="delay_rate",color="delay_rate",color_continuous_scale="Reds",template="plotly_dark",hover_data=["shipments"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=420,yaxis_title="Late shipment rate (%)")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("### Shipment-level explorer")
    cols=["shipment_id","origin","destination","carrier_name","shipping_mode","distance_km","shipping_cost","weather","traffic_level","delivery_status"]
    st.dataframe(filtered[cols].sort_values("shipping_date",ascending=False).head(1000),use_container_width=True,hide_index=True)
    st.download_button("Download filtered shipment data",filtered.to_csv(index=False).encode("utf-8"),"logipulse_filtered_shipments.csv","text/csv")

elif page=="Fleet & Transport":
    st.subheader("Fleet & Transportation")
    fleet=data["vehicles"]
    active=fleet[fleet["status"]=="Active"]
    c=st.columns(4)
    metric(c[0],"Fleet size",f'{len(fleet):,}')
    metric(c[1],"Active vehicles",f'{len(active):,}')
    metric(c[2],"Avg. load capacity",f'{fleet["capacity_kg"].mean():,.0f} kg')
    metric(c[3],"Road shipment share",f'{(filtered["shipping_mode"].eq("Road").mean()*100):.1f}%')
    trans=filtered.groupby("vehicle_id",as_index=False).agg(shipments=("shipment_id","count"),distance=("distance_km","sum"),cost=("shipping_cost","sum"),weight=("weight_kg","sum"))
    trans=trans.merge(fleet,on="vehicle_id",how="left")
    trans["load_utilisation_pct"]=(trans["weight"]/trans["capacity_kg"].replace(0,np.nan)*100).clip(0,200)
    l,r=st.columns(2)
    with l:
        st.markdown("### Vehicle utilisation distribution")
        fig=px.histogram(trans,x="load_utilisation_pct",nbins=25,color_discrete_sequence=["#45b8d8"],template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=350,xaxis_title="Estimated load / capacity (%)")
        st.plotly_chart(fig,use_container_width=True)
    with r:
        st.markdown("### Cost per kilometre by mode")
        modecost=filtered.groupby("shipping_mode",as_index=False).agg(cost=("shipping_cost","sum"),distance=("distance_km","sum"))
        modecost["cost_per_km"]=modecost.cost/modecost.distance
        fig=px.bar(modecost,x="shipping_mode",y="cost_per_km",color="shipping_mode",template="plotly_dark")
        fig.update_layout(showlegend=False,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=350,yaxis_title="₹ per km")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("### Vehicle activity")
    st.dataframe(trans.sort_values("shipments",ascending=False).head(25),use_container_width=True,hide_index=True)

elif page=="Warehouse Analytics":
    st.subheader("Warehouse Analytics")
    wh=data["warehouses"].copy()
    wstats=filtered.groupby("warehouse_id",as_index=False).agg(shipments=("shipment_id","count"),inventory_throughput=("weight_kg","sum"),late_rate=("is_late","mean"),logistics_cost=("shipping_cost","sum"))
    wh=wh.merge(wstats,on="warehouse_id",how="left").fillna(0)
    wh["capacity_utilisation_pct"]=(wh["inventory_throughput"]/wh["capacity_units"]*100).clip(0,200)
    c=st.columns(4)
    metric(c[0],"Warehouses",f'{len(wh):,}')
    metric(c[1],"Avg. capacity use",f'{wh["capacity_utilisation_pct"].mean():.1f}%')
    metric(c[2],"Highest throughput",f'{wh["inventory_throughput"].max():,.0f} kg')
    metric(c[3],"Total warehouse cost",f'₹{wh["monthly_operating_cost"].sum()/1e6:.2f}M')
    l,r=st.columns(2)
    with l:
        fig=px.bar(wh.sort_values("capacity_utilisation_pct",ascending=False),x="warehouse_name",y="capacity_utilisation_pct",color="region",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=400,xaxis_tickangle=-35,yaxis_title="Throughput / capacity (%)")
        st.markdown("### Warehouse throughput proxy")
        st.plotly_chart(fig,use_container_width=True)
    with r:
        fig=px.scatter(wh,x="shipments",y="late_rate",size="logistics_cost",color="region",hover_name="warehouse_name",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=400,yaxis_title="Late shipment rate")
        st.markdown("### Volume vs. late-rate")
        st.plotly_chart(fig,use_container_width=True)
    st.dataframe(wh,use_container_width=True,hide_index=True)

elif page=="Cost Optimisation":
    st.subheader("Cost Optimisation")
    cost_analysis=route_cost_analysis(filtered)
    c=st.columns(4)
    metric(c[0],"Total spend",f'₹{filtered.shipping_cost.sum()/1e6:.2f}M')
    metric(c[1],"Cost / shipment",f'₹{filtered.shipping_cost.mean():,.0f}')
    metric(c[2],"Cost / km",f'₹{filtered.shipping_cost.sum()/max(filtered.distance_km.sum(),1):.2f}')
    metric(c[3],"Top 10 route spend",f'₹{cost_analysis.head(10).shipping_cost.sum()/1e6:.2f}M')
    l,r=st.columns(2)
    with l:
        st.markdown("### Highest-cost routes")
        fig=px.bar(cost_analysis.head(15),x="shipping_cost",y="route",orientation="h",color="shipping_cost",color_continuous_scale="Oranges",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=450,yaxis_title="",xaxis_title="Total cost (₹)")
        st.plotly_chart(fig,use_container_width=True)
    with r:
        st.markdown("### Cost vs distance")
        sample=filtered.sample(min(2500,len(filtered)),random_state=7)
        fig=px.scatter(sample,x="distance_km",y="shipping_cost",color="shipping_mode",opacity=.55,template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=450)
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("### Route cost table")
    st.dataframe(cost_analysis.head(30),use_container_width=True,hide_index=True)

elif page=="Delay Prediction":
    st.subheader("Predictive Delivery Risk")
    st.markdown("Train a demo classification model on historical synthetic shipment records, then score a hypothetical shipment.")
    with st.spinner("Training model on shipment history..."):
        model,metrics=train_delay_model(ship)
    a,b,c=st.columns(3)
    metric(a,"Model", "Random Forest")
    metric(b,"Test accuracy",f'{metrics["accuracy"]*100:.1f}%')
    metric(c,"ROC AUC",f'{metrics["roc_auc"]:.3f}')
    st.markdown("### Test a shipment scenario")
    x1,x2,x3=st.columns(3)
    with x1:
        distance_in=st.slider("Distance (km)",40,2200,850,20)
        weather_in=st.selectbox("Weather",["Clear","Rain","Storm","Fog"])
    with x2:
        traffic_in=st.selectbox("Traffic",["Low","Medium","High"])
        mode_in=st.selectbox("Shipping mode",["Road","Rail","Air"])
    with x3:
        weight_in=st.slider("Shipment weight (kg)",5,18000,2500,100)
        priority_in=st.selectbox("Order priority",["Low","Medium","High","Critical"])
    if st.button("Predict delay risk",type="primary"):
        probability=predict_risk(model,distance_in,weather_in,traffic_in,mode_in,weight_in,priority_in)
        label="HIGH RISK" if probability>=.55 else ("MODERATE RISK" if probability>=.30 else "LOW RISK")
        st.markdown(f"### Predicted delay probability: **{probability*100:.1f}%**")
        st.progress(float(probability))
        st.info(f"Risk category: {label}. This is a demonstration model trained on synthetic data, not a production ETA service.")
    st.caption("Model features: distance, weather, traffic, shipping mode, shipment weight and order priority.")

elif page=="Smart Recommendations":
    st.subheader("Smart Operational Recommendations")
    recs=build_recommendations(filtered)
    for i,rec in enumerate(recs,1):
        st.markdown(f"""
        <div class="metric" style="margin-bottom:12px;min-height:90px">
        <div class="metric-label">OPPORTUNITY {i} · {rec['priority']}</div>
        <div style="font-size:18px;font-weight:700;color:#f5f9ff;margin:7px 0">{rec['title']}</div>
        <div style="color:#b9cbe0;font-size:13px">{rec['detail']}</div>
        </div>""",unsafe_allow_html=True)
    st.markdown("### Routes requiring attention")
    routes_table=route_cost_analysis(filtered)
    st.dataframe(routes_table.head(10),use_container_width=True,hide_index=True)
    st.caption("Recommendations are rule-based operational signals; validate them with business constraints before execution.")

st.markdown("---")
st.caption("LogiPulse • Portfolio demonstration built with Python, SQL-ready data model, Streamlit and Plotly. Dataset is synthetic and intended for learning/demo use.")
