from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd
import json
import numpy as np

app = FastAPI(title="Heart Disease Prediction API V2")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatientData(BaseModel):
    Age: float
    Sex: float
    BP_systolic: float
    BP_diastolic: float
    PR: float
    Spo2: float
    Weight: float
    CP: float
    chol: float
    Diabetics: float
    HTN: float
    Habits: float
    ECG: float
    ECHO: float
    TMT: float
    CAG: float

# Load the model
model = xgb.XGBClassifier()
model.load_model("../ml/model.json")

# Load feature names to ensure column order is exactly as trained
with open("../ml/feature_names.json", "r") as f:
    feature_names = json.load(f)

@app.post("/predict")
def predict(data: PatientData):
    # Convert input to DataFrame with proper column order
    input_dict = data.dict()
    df = pd.DataFrame([input_dict], columns=feature_names)
    
    # Predict probability of class 1 (Heart Disease)
    probability = model.predict_proba(df)[0][1]
    prediction = int(model.predict(df)[0])
    
    # Calculate feature contributions using XGBoost's built-in SHAP values
    booster = model.get_booster()
    dmatrix = xgb.DMatrix(df)
    contribs = booster.predict(dmatrix, pred_contribs=True)[0]
    
    # The last value is the bias, the first N are the features
    feature_contribs = contribs[:-1]
    
    # Create a list of tuples (feature_name, contribution_value, absolute_value)
    contributions = []
    for i, name in enumerate(feature_names):
        val = float(feature_contribs[i])
        contributions.append({
            "feature": name,
            "value": val,
            "abs_value": abs(val)
        })
        
    # Sort by absolute contribution to find the most impactful features
    contributions.sort(key=lambda x: x["abs_value"], reverse=True)
    top_features = contributions[:3]
    
    return {
        "prediction": prediction,
        "probability": float(probability),
        "top_features": top_features
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
