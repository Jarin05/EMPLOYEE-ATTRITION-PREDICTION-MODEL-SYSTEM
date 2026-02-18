import { useState } from "react";
import "./App.css";

function App() {
  const [formData, setFormData] = useState({
    Age: "",
    MonthlyIncome: "",
    JobSatisfaction: "",
    YearsAtCompany: "",
    OverTime: ""
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Age: Number(formData.Age),
          MonthlyIncome: Number(formData.MonthlyIncome),
          JobSatisfaction: Number(formData.JobSatisfaction),
          YearsAtCompany: Number(formData.YearsAtCompany),
          OverTime: Number(formData.OverTime)
        })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Server Error");
      } else {
        setResult(data);
      }

    } catch {
      setError("Backend not connected");
    }

    setLoading(false);
  };

  const percentage = result
    ? Math.round(result.attrition_probability * 100)
    : 0;

  return (
    <div className="page">

      <div className="container">
        <h1>Attrition Predictor</h1>
        <p className="subtitle">AI Powered Employee Retention Analytics</p>

        <form onSubmit={handleSubmit}>
          <input type="number" name="Age" placeholder="Age" onChange={handleChange} required />
          <input type="number" name="MonthlyIncome" placeholder="Monthly Income" onChange={handleChange} required />
          <input type="number" name="JobSatisfaction" placeholder="Job Satisfaction (1-4)" onChange={handleChange} required />
          <input type="number" name="YearsAtCompany" placeholder="Years At Company" onChange={handleChange} required />

          <select name="OverTime" onChange={handleChange} required>
            <option value="">OverTime?</option>
            <option value="1">Yes</option>
            <option value="0">No</option>
          </select>

          <button type="submit" disabled={loading}>
            {loading ? "Predicting..." : "🔍 Predict Attrition"}
          </button>
        </form>

        {result && (
          <div className="result-card">
            <div className={`badge ${result.risk_level === "High Risk"
                ? "high"
                : result.risk_level === "Medium Risk"
                  ? "medium"
                  : "low"
              }`}>
              {result.risk_level.toUpperCase()}
            </div>


            <h3>Prediction Summary</h3>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${percentage}%` }}
              ></div>
            </div>

            <p className="percentage">{percentage}% Probability</p>

            <h4>Key Influencing Factors</h4>
            <ul>
              {result.reasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </div>
        )}

        {error && <div className="error">❌ {error}</div>}
      </div>

      <section className="about">
        <h2>About This Platform</h2>
        <p>
          About This Platform
          This system predicts employee attrition using a machine-learning model trained on an HR dataset. It analyzes employee details and displays the prediction result along with key factors affecting attrition through a simple and interactive interface.
        </p>
      </section>

      <footer>
        Developed by <strong>Sadaf Ahmad | Jarin Khan | Ishika Ishan</strong> | B.Tech Final Year Project
      </footer>

    </div>
  );
}

export default App;
