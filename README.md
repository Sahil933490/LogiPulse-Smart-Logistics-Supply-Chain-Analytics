# LogiPulse — Smart Logistics & Supply Chain Control Tower

An interactive logistics analytics portfolio project built with **Python, Streamlit, Pandas, Plotly and Scikit-learn**.

## Features
- Executive overview: shipment volume, on-time delivery, late shipments, logistics spend and distance.
- Shipment analytics: carrier performance, delay drivers and shipment-level exploration.
- Fleet & transportation: vehicle activity, estimated load utilisation and cost per kilometre.
- Warehouse analytics: throughput proxy, capacity comparison and regional performance.
- Cost optimisation: expensive lanes, route spend and cost-distance relationship.
- Predictive delivery risk: Random Forest classification trained on historical demonstration data.
- Smart recommendations: rule-based operational signals for logistics teams.
- Sidebar filters: date range, warehouse region and shipping mode.

## Dataset
The repository includes synthetic, interconnected CSV datasets:
- 50,000 shipments
- 30,000 orders
- 500 vehicles
- 20 warehouses
- 10,000 customers
- 2,000 routes
- 15 carriers

**Important:** All records are synthetic and for portfolio/demo use only. They do not represent a real company or actual logistics performance. Some fields (such as warehouse capacity utilisation) are analytical proxies, not audited operational measures.

## Run locally

```bash
# 1. Clone your repository
git clone https://github.com/YOUR-USERNAME/LogiPulse.git
cd LogiPulse

# 2. Create and activate a virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this complete project folder to a public GitHub repository.
2. Sign in to Streamlit Community Cloud using GitHub.
3. Select **Create app**.
4. Choose your repository, branch (`main`) and main file path (`app.py`).
5. Click **Deploy**. Streamlit installs packages from `requirements.txt`.
6. After deployment, test all pages and filters.

## GitHub upload

```bash
git init
git add .
git commit -m "Build LogiPulse logistics analytics dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/LogiPulse.git
git push -u origin main
```

If Git is already initialized, do not run `git init` again. Replace `YOUR-USERNAME` with your GitHub username.

## Project structure

```text
LogiPulse/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── shipments.csv
│   ├── orders.csv
│   ├── vehicles.csv
│   ├── warehouses.csv
│   ├── customers.csv
│   ├── routes.csv
│   └── carriers.csv
├── src/
│   ├── __init__.py
│   ├── data_processing.py
│   ├── analytics.py
│   ├── ml_models.py
│   └── recommendations.py
└── assets/
```

## Suggested resume description
**LogiPulse — Smart Logistics & Supply Chain Control Tower**
- Developed a multi-page logistics analytics dashboard using Python and Streamlit to monitor 50K synthetic shipments across carriers, routes, warehouses and transport modes.
- Built interactive operational views for on-time delivery, shipment delays, fleet utilisation proxies, warehouse throughput and route-level logistics costs using Pandas and Plotly.
- Implemented a Random Forest delay-risk classification demo and rule-based recommendations to highlight high-risk shipments and cost optimisation opportunities.

## Future enhancements
- Replace synthetic data with verified public or company-authorised datasets.
- Add a relational database ingestion layer (SQLite/PostgreSQL) and scheduled refresh.
- Add shipment-level explainability, model calibration, and time-based validation.
- Integrate geospatial route maps and live carrier/TMS APIs where authorised.
