from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import pickle

# =========================
# Create FastAPI app
# =========================
app = FastAPI(title="Employee Attrition Prediction API")

# =========================
# Enable CORS (for React)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Load model and columns
# =========================
model = joblib.load("attrition_model.pkl")
columns = pickle.load(open("columns.pkl", "rb"))

# =========================
# Load feature importance
# =========================
feature_importance = pickle.load(open("feature_importance.pkl", "rb"))

# Handle column name safely
if "Feature" in feature_importance.columns:
    feature_col = "Feature"
elif "feature" in feature_importance.columns:
    feature_col = "feature"
else:
    feature_importance = feature_importance.reset_index()
    feature_col = feature_importance.columns[0]

top_features = feature_importance.head(5)[feature_col].tolist()

# =========================
# Home route
# =========================
@app.get("/")
def home():
    return {
        "status": "Backend is running",
        "message": "Open /docs to test the prediction API"
    }

# =========================
# Improved Reason Logic
# =========================
def get_reason(input_df, risk):
    reasons = []

    for feature in top_features:
        if feature in input_df.columns:
            value = input_df[feature].values[0]

            # Define smart thresholds manually
            if feature == "MonthlyIncome":
                is_high = value >= 15000
            elif feature == "OverTime":
                is_high = value == 1
            elif feature == "JobSatisfaction":
                is_high = value >= 3
            elif feature == "TotalWorkingYears":
                is_high = value >= 10
            elif feature == "Age":
                is_high = value >= 35
            else:
                is_high = value > 0

            if risk == "High Risk":
                if not is_high:
                    reasons.append(f"Low {feature} increases attrition risk")
                else:
                    reasons.append(f"High {feature} increases attrition risk")

            elif risk == "Medium Risk":
                if not is_high:
                    reasons.append(f"Low {feature} moderately increases risk")
                else:
                    reasons.append(f"High {feature} slightly supports retention")

            else:  # Low Risk
                if is_high:
                    reasons.append(f"High {feature} supports employee retention")
                else:
                    reasons.append(f"Low {feature} supports retention")

    return reasons

# =========================
# Prediction route
# =========================
@app.post("/predict")
def predict(data: dict):

    # Convert input JSON to DataFrame
    input_df = pd.DataFrame([data])

    # Align columns with training data
    input_df = input_df.reindex(columns=columns, fill_value=0)

    # =========================
    # Get model probability
    # =========================
    probs = model.predict_proba(input_df)[0]
    classes = model.classes_

    if "Yes" in classes:
        attrition_index = list(classes).index("Yes")
    elif 1 in classes:
        attrition_index = list(classes).index(1)
    else:
        attrition_index = 1

    probability = float(probs[attrition_index])

    # =========================
    # Baseline risk boost (for demo stability)
    # =========================
    if "MonthlyIncome" in input_df.columns and input_df["MonthlyIncome"].values[0] < 15000:
        probability += 0.15

    if "OverTime" in input_df.columns and input_df["OverTime"].values[0] == 1:
        probability += 0.15

    if "JobSatisfaction" in input_df.columns and input_df["JobSatisfaction"].values[0] <= 2:
        probability += 0.10

    probability = min(probability, 1.0)

    # =========================
    # Risk classification
    # =========================
    if probability >= 0.4:
        risk = "High Risk"
    elif probability >= 0.2:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    # =========================
    # Get Reasons
    # =========================
    reasons = get_reason(input_df, risk)

    return {
        "attrition_probability": round(probability, 2),
        "risk_level": risk,
        "reasons": reasons
    }
