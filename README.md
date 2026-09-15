# 🎓 EduIntel – AI-Based Student Performance Intelligence System

EduIntel is an AI-powered student performance intelligence system designed to analyze academic data, predict student performance, identify students who may be at risk, and provide data-driven recommendations.

## 🚀 Features

- 📊 Student Performance Dashboard
- 🤖 AI-based student performance prediction
- 📈 Class performance analytics
- ⚠️ At-risk student identification
- 💡 Personalized student recommendations
- 🧠 Machine Learning model performance analysis
- 📋 Class performance report generation
- 🗄️ SQLite database integration
- 🔐 Login and logout functionality
- 📉 Model evaluation using MAE and R²
- 🔄 Cross-validation for model consistency

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- SQLite
- Matplotlib

## 🧠 Machine Learning

EduIntel uses **Linear Regression** to predict student final marks based on:

- Attendance
- Assignment Score
- Internal Marks
- Study Hours
- Previous Marks

### Model Evaluation

The model is evaluated using:

- Mean Absolute Error (MAE)
- R² Score
- Cross-validation

## 📂 Project Structure

```text
EduIntel/
│
├── app.py
├── requirements.txt
├── .gitignore
│
└── data/
    └── student_data.csv
