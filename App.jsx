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
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        Age: Number(formData.Age),
        MonthlyIncome: Number(formData.MonthlyIncome),
        JobSatisfaction: Number(formData.JobSatisfaction),
        YearsAtCompany: Number(formData.YearsAtCompany),
        OverTime: Number(formData.OverTime)
      })
    });

    const data = await response.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Employee Attrition Prediction</h1>

      <form onSubmit={handleSubmit} className="card">
        <input name="Age" placeholder="Age" onChange={handleChange} required />
        <input name="MonthlyIncome" placeholder="Monthly Income" onChange={handleChange} required />
        <input name="JobSatisfaction" placeholder="Job Satisfaction (1-4)" onChange={handleChange} required />
        <input name="YearsAtCompany" placeholder="Years at Company" onChange={handleChange} required />
        <select name="OverTime" onChange={handleChange} required>
          <option value="">OverTime?</option>
          <option value="1">Yes</option>
          <option value="0">No</option>
        </select>

        <button type="submit">
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>

      {result && (
        <div className="result-card">
          <h2>Result</h2>
          <p><b>Risk Level:</b> {result.risk_level}</p>
          <p><b>Attrition Probability:</b> {result.attrition_probability}</p>

          <h3>Reasons:</h3>
          <ul>
            {result.reasons.map((reason, index) => (
              <li key={index}>{reason}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
