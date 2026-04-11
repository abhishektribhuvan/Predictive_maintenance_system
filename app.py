from fastapi import FastAPI, HTTPException, Path, Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Annotated, Optional
from datetime import datetime
import csv
import pandas as pd
import pickle
import os
from sklearn.ensemble import IsolationForest
import joblib

app = FastAPI()

def get_csv_file(device_id: str) -> str:
    # Ensure safe filename
    safe_id = "".join([c for c in device_id if c.isalnum() or c in ('-', '_')])
    return f"{safe_id}_training_data.csv"

def get_model_file(device_id: str) -> str:
    safe_id = "".join([c for c in device_id if c.isalnum() or c in ('-', '_')])
    return f"{safe_id}_vibration_model.pkl"


@app.get("/")
def home():
    return {"message": "this is home"}

class EspData(BaseModel):
    mac_id: str  # Included MAC ID/Device ID for distributed setup
    mean: float
    var: float
    temp: float

@app.post("/send_from_esp32")
def receive_data(esp_data: EspData):
    data = esp_data.model_dump()
    device_id = data.pop('mac_id')
    df = pd.DataFrame([data])
    
    csv_file = get_csv_file(device_id)
    file_exists = os.path.isfile(csv_file)
    
    df.to_csv(
        csv_file,
        mode="a",
        header=not file_exists, 
        index=False
    )
    return {"status": "data saved", "device_id": device_id}

@app.get("/train/{device_id}")
async def train_model(device_id: str):
    csv_file = get_csv_file(device_id)
    model_file = get_model_file(device_id)

    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail=f"CSV file for device {device_id} not found. Send some data first!")

    df = pd.read_csv(csv_file)
    
    if len(df) < 500: # Safety check (you might want to lower this for testing)
        return {"status": "error", "message": f"Not enough data to train for {device_id}. Need at least 500 rows, found {len(df)}."}

    X_train = df[['mean', 'var']].values

    model = IsolationForest(n_estimators=100, contamination=0.01)
    model.fit(X_train)

    joblib.dump(model, model_file)
    
    return {"status": "success", "message": f"Model trained on {len(df)} rows and saved for device {device_id}"}


@app.get("/predict_latest/{device_id}")
def predict_latest(device_id: str):
    csv_file = get_csv_file(device_id)
    model_file = get_model_file(device_id)

    if not os.path.exists(model_file) or not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail="Model or CSV missing for this device. Train the model first!")

    model = joblib.load(model_file)

    df = pd.read_csv(csv_file)
    latest_row = df.tail(1)
    current_mean = float(latest_row['mean'].values[0])
    current_var = float(latest_row['var'].values[0])
    current_temp = float(latest_row['temp'].values[0])

    features = [[current_mean, current_var]]
    prediction = model.predict(features)

    is_anomaly = bool(prediction[0] == -1)

    return {
        "machine_id": device_id,
        "mean": current_mean,
        "var": current_var,
        "temp": current_temp,
        "is_anomaly": is_anomaly,
        "status": "Anomaly Detected!" if is_anomaly else "Normal"
    }
