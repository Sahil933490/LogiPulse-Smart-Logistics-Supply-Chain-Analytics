import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

FEATURES=["distance_km","weather","traffic_level","shipping_mode","weight_kg","order_priority"]
CATEGORICAL=["weather","traffic_level","shipping_mode","order_priority"]
NUMERIC=["distance_km","weight_kg"]

def _training_frame(shipments):
    # Order priority is joined from order table in app-independent fallback; derive a stable proxy
    x=shipments[FEATURES].copy() if "order_priority" in shipments.columns else shipments[["distance_km","weather","traffic_level","shipping_mode","weight_kg"]].copy()
    if "order_priority" not in x.columns:
        x["order_priority"]="Medium"
    y=(shipments["delivery_status"]=="Delivered Late").astype(int)
    # Exclude in-transit rows from supervised target
    mask=shipments["delivery_status"]!="In Transit"
    return x.loc[mask],y.loc[mask]

def train_delay_model(shipments):
    x,y=_training_frame(shipments)
    prep=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),CATEGORICAL),
        ("num",StandardScaler(),NUMERIC)
    ])
    model=Pipeline([("prep",prep),("rf",RandomForestClassifier(n_estimators=100,max_depth=12,min_samples_leaf=5,class_weight="balanced",random_state=42,n_jobs=-1))])
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=.2,random_state=42,stratify=y)
    model.fit(x_train,y_train)
    prob=model.predict_proba(x_test)[:,1]
    metrics={"accuracy":accuracy_score(y_test,(prob>=.5).astype(int)),"roc_auc":roc_auc_score(y_test,prob)}
    return model,metrics

def predict_risk(model,distance,weather,traffic,mode,weight,priority):
    row=pd.DataFrame([{"distance_km":distance,"weather":weather,"traffic_level":traffic,"shipping_mode":mode,"weight_kg":weight,"order_priority":priority}])
    return float(model.predict_proba(row)[0,1])
