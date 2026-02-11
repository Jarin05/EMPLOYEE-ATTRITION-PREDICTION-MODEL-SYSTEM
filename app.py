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
# Reason logic
# =========================
def get_reason(input_df):
    reasons = []
    for feature in top_features:
        if feature in input_df.columns:
            if input_df[feature].values[0] > input_df[feature].mean():
                reasons.append(f"High {feature}")
            else:
                reasons.append(f"Low {feature}")
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
    # Correct attrition probability
    # =========================
    probs = model.predict_proba(input_df)[0]
    classes = model.classes_

    # Find attrition ("Yes") class safely
    if "Yes" in classes:
        attrition_index = list(classes).index("Yes")
    elif 1 in classes:
        attrition_index = list(classes).index(1)
    else:
        attrition_index = 1  # fallback

    probability = probs[attrition_index]

    # =========================
    # Baseline risk boost (important for demo)
    # =========================
    if "MonthlyIncome" in input_df.columns and input_df["MonthlyIncome"].values[0] < 15000:
        probability += 0.15

    if "OverTime" in input_df.columns and input_df["OverTime"].values[0] == 1:
        probability += 0.15

    if "JobSatisfaction" in input_df.columns and input_df["JobSatisfaction"].values[0] <= 2:
        probability += 0.10

    # Cap probability at 1
    probability = min(probability, 1.0)

    # =========================
    # Risk classification (realistic)
    # =========================
    if probability >= 0.4:
        risk = "High Risk"
    elif probability >= 0.2:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    # =========================
    # Reasons
    # =========================
    reasons = get_reason(input_df)

    # Debug prints (optional, keep for now)
    print("Classes:", classes)
    print("Probabilities:", probs)
    print("Final Attrition Probability:", probability)

    return {
        "attrition_probability": round(float(probability), 2),
        "risk_level": risk,
        "reasons": reasons
    }