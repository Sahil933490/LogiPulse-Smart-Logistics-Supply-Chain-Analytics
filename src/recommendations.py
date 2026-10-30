from src.analytics import route_cost_analysis

def build_recommendations(df):
    recs=[]
    late_rate=df["is_late"].mean()*100
    if late_rate>18:
        recs.append({"priority":"HIGH","title":"Investigate delivery reliability","detail":f"Late deliveries are {late_rate:.1f}% in the selected view. Review carrier SLAs, high-traffic lanes and weather-related contingency buffers."})
    else:
        recs.append({"priority":"MEDIUM","title":"Protect current service levels","detail":f"Late deliveries are {late_rate:.1f}%. Track weekly changes and use exception alerts for lanes with repeated delays."})
    mode=df.groupby("shipping_mode")["shipping_cost"].mean().sort_values(ascending=False)
    if len(mode):
        recs.append({"priority":"MEDIUM","title":f"Review {mode.index[0]} mode economics","detail":f"{mode.index[0]} has the highest average shipment cost (₹{mode.iloc[0]:,.0f}). Compare urgency, service promise and consolidation options before shifting volume."})
    routes=route_cost_analysis(df)
    if len(routes):
        r=routes.iloc[0]
        recs.append({"priority":"HIGH","title":"Review the highest-spend route","detail":f"{r['route']} accounts for ₹{r['shipping_cost']:,.0f} across {int(r['shipments'])} shipments. Check carrier rate cards, shipment consolidation and alternate routing."})
    high_traffic=df[df["traffic_level"]=="High"]
    if len(high_traffic):
        recs.append({"priority":"MEDIUM","title":"Create a high-traffic dispatch playbook","detail":f"{len(high_traffic):,} filtered shipments faced high traffic. Consider dispatch-time changes, route alternatives and proactive customer notifications."})
    recs.append({"priority":"LOW","title":"Improve data quality before production rollout","detail":"Connect live TMS/WMS feeds, maintain carrier and vehicle master data, and monitor missing timestamps to make the control tower production-ready."})
    return recs
