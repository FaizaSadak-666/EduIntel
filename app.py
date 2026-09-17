import os
import sqlite3

import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="EduIntel",
    page_icon="🎓",
    layout="wide"
) 

# =========================================================
# EDUINTEL - PROFESSIONAL UI STYLING
# =========================================================

st.markdown("""
<style>

    /* ---------- MAIN APP ---------- */ 

    .stApp {
        background: #f5f7fb;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ---------- HEADINGS ---------- */

    h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h2 {
        font-size: 1.6rem !important;
        font-weight: 650 !important;
    }

    h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    /* ---------- METRIC CARDS ---------- */

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.05);
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 700;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 42px;
        border: 1px solid #d1d5db;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
    }

    /* ---------- INPUTS ---------- */

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"],
    .stTextArea textarea {
        border-radius: 9px;
    }

    /* ---------- DATAFRAME ---------- */

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }

    /* ---------- ALERTS ---------- */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* ---------- CUSTOM CARDS ---------- */

    .edu-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.05);
    }

    .edu-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .edu-card-text {
        color: #6b7280;
        line-height: 1.6;
    }

    /* ---------- STATUS BADGES ---------- */

    .high-badge {
        display: inline-block;
        padding: 7px 14px;
        border-radius: 20px;
        font-weight: 600;
        background: #dcfce7;
        color: #166534;
    }

    .average-badge {
        display: inline-block;
        padding: 7px 14px;
        border-radius: 20px;
        font-weight: 600;
        background: #fef3c7;
        color: #92400e;
    }

    .low-badge {
        display: inline-block;
        padding: 7px 14px;
        border-radius: 20px;
        font-weight: 600;
        background: #fee2e2;
        color: #991b1b;
    }

    /* ---------- DIVIDERS ---------- */

    hr {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        border: none;
        border-top: 1px solid #e5e7eb;
    }

    </style>
""", unsafe_allow_html=True)

# =========================================================
# TEACHER LOGIN
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


if not st.session_state["logged_in"]:

    # Create centered login layout
    left_space, login_column, right_space = st.columns(
        [1, 1.4, 1]
    )

    with login_column:

        # Login card
        with st.container(border=True):

            # Logo
            st.markdown(
                """
                <div style="
                    text-align: center;
                    font-size: 52px;
                    margin-top: 10px;
                    margin-bottom: 5px;
                ">
                    🎓
                </div>
                """,
                unsafe_allow_html=True
            )

            # Application name
            st.markdown(
                """
                <h1 style="
                    text-align: center;
                    color: #111827;
                    margin-bottom: 5px;
                ">
                    EduIntel
                </h1>
                """,
                unsafe_allow_html=True
            )

            # Application description
            st.markdown(
                """
                <p style="
                    text-align: center;
                    color: #6b7280;
                    font-size: 15px;
                    margin-bottom: 25px;
                ">
                    AI-Based Student Performance Intelligence System
                </p>
                """,
                unsafe_allow_html=True
            )

            st.divider()

            # Login heading
            st.markdown(
                """
                <h3 style="
                    text-align: center;
                    color: #111827;
                    margin-bottom: 5px;
                ">
                    🔐 Teacher Login
                </h3>
                """,
                unsafe_allow_html=True
            )

            # Login description
            st.markdown(
                """
                <p style="
                    text-align: center;
                    color: #9ca3af;
                    font-size: 14px;
                    margin-bottom: 20px;
                ">
                    Sign in to access the EduIntel dashboard
                </p>
                """,
                unsafe_allow_html=True
            )

            # Username
            username = st.text_input(
                "👤 Username",
                placeholder="Enter your username",
                key="login_username"
            )

            # Password
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            # Login button
            login_button = st.button(
                "🔐 Login to EduIntel",
                use_container_width=True,
                key="login_button"
            )

            # Login validation
            if login_button:

                if username == "admin" and password == st.secrets["login"]["password"]:

                    st.session_state["logged_in"] = True

                    st.success(
                        "✅ Login successful! Welcome to EduIntel."
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid username or password."
                    )

            # Demo credentials
            st.markdown(
                """
                <div style="
                    text-align: center;
                    margin-top: 20px;
                    color: #9ca3af;
                    font-size: 13px;
                ">
                    Demo Login: <b>admin</b> / <b>admin123</b>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Stop the rest of the application until login
    st.stop()


# =========================================================
# DATABASE SETUP
# =========================================================

# Connect to SQLite database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "eduintel.db")

connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()

# Create students table if it does not already exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS students (
        Student_ID TEXT PRIMARY KEY,
        Name TEXT,
        Attendance REAL,
        Assignment_Score REAL,
        Internal_Marks REAL,
        Study_Hours REAL,
        Previous_Marks REAL,
        Final_Marks REAL,
        Actual_Final_Marks REAL,
        Predicted_Final_Marks REAL
    )
    """
)

# ---------------------------------------------------------
# ADD NEW COLUMNS TO EXISTING DATABASE
# ---------------------------------------------------------

cursor.execute("PRAGMA table_info(students)")
existing_columns = [
    column[1]
    for column in cursor.fetchall()
]

if "Actual_Final_Marks" not in existing_columns:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN Actual_Final_Marks REAL"
    )

if "Predicted_Final_Marks" not in existing_columns:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN Predicted_Final_Marks REAL"
    )

# ---------------------------------------------------------
# MIGRATE EXISTING FINAL MARKS TO ACTUAL FINAL MARKS
# ---------------------------------------------------------

cursor.execute(
    """
    UPDATE students
    SET Actual_Final_Marks = Final_Marks
    WHERE Actual_Final_Marks IS NULL
    AND Final_Marks IS NOT NULL
    """
)



connection.commit()

# =========================================================
# LOAD STUDENT DATA FROM DATABASE
# =========================================================

data = pd.read_sql_query(
    "SELECT * FROM students",
    connection 
)

data["Display_Final_Marks"] = data["Actual_Final_Marks"].fillna(
    data["Predicted_Final_Marks"]
)




# =========================================================
# MACHINE LEARNING MODEL
# =========================================================

features = [
    "Attendance",
    "Assignment_Score",
    "Internal_Marks",
    "Study_Hours",
    "Previous_Marks"
]

# Use ONLY students who have real final marks
training_data = data.dropna(
    subset=["Actual_Final_Marks"]
).copy()

if len(training_data) >= 6:

    X = training_data[features]
    y = training_data["Actual_Final_Marks"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = LinearRegression()

    model.fit(
        X_train,
        y_train
    )

    feature_importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.coef_
    })

    feature_importance["Absolute_Importance"] = (
        feature_importance["Importance"].abs()
    )

    feature_importance = feature_importance.sort_values(
        "Absolute_Importance",
        ascending=False
    )

    cv_scores = cross_val_score(
        model,
        X,
        y,
        cv=3,
        scoring="r2"
    )

    cv_r2 = cv_scores.mean()

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    r2 = r2_score(
        y_test,
        predictions
    )

else:

    model = None
    predictions = []
    mae = None
    r2 = None
    cv_r2 = None

    feature_importance = pd.DataFrame(
        columns=[
            "Feature",
            "Importance",
            "Absolute_Importance"
        ]
    )

    y_test = pd.Series(
        dtype=float
    )

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

st.sidebar.title("🎓 EduIntel")
st.sidebar.write("AI-Based Student Performance Intelligence")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "👨‍🎓 Student Prediction",
        "📊 Class Analytics",
        "💡 Recommendations",
        "🤖 AI Model Performance"
    ]
)


# ========================================================= 
# DASHBOARD 
# ========================================================= 
 
if page == "🏠 Dashboard":  

    # ========================================================= 
    # CHECK STUDENT DATA AVAILABILITY 
    # ========================================================= 
 
    if data.empty: 
 
        st.warning( 
            "⚠️ No student records are available yet. " 
            "Please add student data to use the Dashboard." 
        ) 
 
        st.info( 
            "Go to the Student Prediction page and add " 
            "student records to activate dashboard analytics." 
        ) 
 
        st.stop() 
 
    # ========================================================= 
    # DASHBOARD HEADER 
    # ========================================================= 
 
    st.title("🎓 Welcome to EduIntel") 
 
    st.write( 
        "AI-Based Student Performance Intelligence System" 
    ) 
 
    st.caption( 
        "Monitor student performance, identify academic risks, " 
        "and make data-driven educational decisions." 
    ) 
 
    st.divider() 
 
    # ========================================================= 
    # CLASS OVERVIEW 
    # ========================================================= 
 
    total_students = len(data) 
 
    average_marks = data["Display_Final_Marks"].mean() 
 
    high_performers = len( 
        data[data["Display_Final_Marks"] >= 80] 
    ) 
 
    at_risk = len( 
        data[ 
            (data["Display_Final_Marks"] < 60) 
            | 
            (data["Attendance"] < 75) 
        ] 
    )

    

   

    st.subheader("📌 Class Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👨‍🎓 Total Students",
            total_students
        )

    with col2:
        st.metric(
            "📊 Average Marks",
            f"{average_marks:.1f}"
        )

    with col3:
        st.metric(
            "🏆 High Performers",
            high_performers
        )

    with col4:
        st.metric(
            "🚨 At Risk",
            at_risk
        )

    st.divider()

    # =========================================================
    # PERFORMANCE DISTRIBUTION
    # =========================================================

    st.subheader("📊 Performance Distribution")

    performance_summary = data["Display_Final_Marks"].apply(
        lambda x:
            "High Performer"
            if pd.notna(x) and x >= 80
            else "Average Performer"
            if pd.notna(x) and x >= 60
            else "Needs Improvement"
    ).value_counts()

    st.bar_chart(
        performance_summary,
        use_container_width=True
    )

    st.divider()
    # =========================================================
    # STUDENTS NEEDING ATTENTION
    # =========================================================

    st.subheader("🚨 Students Needing Attention")

    risk_students = data[
        (data["Display_Final_Marks"] < 60)
        |
        (data["Attendance"] < 75)
    ]

    if len(risk_students) > 0:

        st.warning(
            f"⚠️ {len(risk_students)} student(s) may require "
            "academic attention."
        )

        st.dataframe(
            risk_students[
                [
                    "Student_ID",
                    "Name",
                    "Attendance",
                    "Display_Final_Marks",
                    "Study_Hours"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "✅ No students are currently identified as at risk."
        )

    st.divider()
    # =========================================================
    # AI CLASS INTELLIGENCE
    # =========================================================

    st.subheader("🤖 AI Class Intelligence")

    high_performer_percentage = (
        high_performers / total_students * 100
        if total_students > 0
        else 0
    )

    at_risk_percentage = (
        at_risk / total_students * 100
        if total_students > 0
        else 0
    )

    average_attendance = data["Attendance"].mean()

    average_study_hours = data["Study_Hours"].mean()

    # Calculate relationships with final marks

    valid_correlation_data = data[
        [
            "Attendance",
            "Study_Hours",
            "Display_Final_Marks"
        ]
    ].dropna()

    if len(valid_correlation_data) >= 2:

        attendance_correlation = (
            valid_correlation_data["Attendance"]
            .corr(valid_correlation_data["Display_Final_Marks"])
        )

        study_hours_correlation = (
            valid_correlation_data["Study_Hours"]
            .corr(valid_correlation_data["Display_Final_Marks"])
        )

    else:

        attendance_correlation = 0
        study_hours_correlation = 0


    
    intelligence_col1, intelligence_col2, intelligence_col3, intelligence_col4 = (
        st.columns(4)
    )

    with intelligence_col1:
        st.metric(
            "🏆 High Performer %",
            f"{high_performer_percentage:.1f}%"
        )

    with intelligence_col2:
        st.metric(
            "🚨 At-Risk %",
            f"{at_risk_percentage:.1f}%"
        )

    with intelligence_col3:
        st.metric(
            "📅 Avg Attendance",
            f"{average_attendance:.1f}%"
        )

    with intelligence_col4:
        st.metric(
            "⏱️ Avg Study Hours",
            f"{average_study_hours:.1f} hrs"
        )

    if at_risk_percentage >= 30:

        st.error(
            "🚨 **AI Insight:** A significant portion of the class "
            "may require academic intervention. Focus on attendance, "
            "study habits and targeted academic support."
        )

    elif average_attendance < 75:

        st.warning(
            "📅 **AI Insight:** Class attendance is below the "
            "recommended level. Improving attendance may support "
            "better academic performance."
        )

    elif average_study_hours < 3:

        st.warning(
            "⏱️ **AI Insight:** Average study time is relatively low. "
            "Encouraging a consistent daily study routine may improve "
            "academic outcomes."
        )

    else:

        st.success(
            "🌟 **AI Insight:** The class demonstrates a healthy "
            "overall academic profile. Continue monitoring performance "
            "and maintaining consistent study habits."
        )

    # =========================================================
    # AI PERFORMANCE RELATIONSHIPS
    # =========================================================

    st.markdown("### 🧠 AI Performance Relationships")

    relationship_col1, relationship_col2 = st.columns(2)

    with relationship_col1:

        if attendance_correlation >= 0.5:
            st.success(
                f"📅 **Attendance Impact:** Strong positive relationship "
                f"with final marks (r = {attendance_correlation:.2f})."
            )

        elif attendance_correlation >= 0.2:
            st.info(
                f"📅 **Attendance Impact:** Moderate positive relationship "
                f"with final marks (r = {attendance_correlation:.2f})."
            )

        else:
            st.warning(
                f"📅 **Attendance Impact:** Weak relationship with "
                f"final marks (r = {attendance_correlation:.2f})."
            )

    with relationship_col2:

        if study_hours_correlation >= 0.5:
            st.success(
                f"📚 **Study Hours Impact:** Strong positive relationship "
                f"with final marks (r = {study_hours_correlation:.2f})."
            )

        elif study_hours_correlation >= 0.2:
            st.info(
                f"📚 **Study Hours Impact:** Moderate positive relationship "
                f"with final marks (r = {study_hours_correlation:.2f})."
            )

        else:
            st.warning(
                f"📚 **Study Hours Impact:** Weak relationship with "
                f"final marks (r = {study_hours_correlation:.2f})."
            )

    st.divider()    

    # =========================================================
    # AI INTERVENTION RECOMMENDATION
    # =========================================================

    st.subheader("🎯 AI Intervention Recommendation")

    if at_risk_percentage >= 30:

        st.error(
            "🚨 **Priority Action:** Identify at-risk students "
            "and provide targeted academic intervention."
        )

        st.write(
            "Recommended focus: individual mentoring, "
            "attendance improvement and regular progress monitoring."
        )

    elif average_attendance < 75:

        st.warning(
            "📅 **Priority Action:** Improve class attendance "
            "through regular attendance monitoring."
        )

        st.write(
            "Recommended focus: identify students with low attendance "
            "and follow up with them regularly."
        )

    elif average_study_hours < 3:

        st.warning(
            "📚 **Priority Action:** Encourage a consistent "
            "daily study routine."
        )

        st.write(
            "Recommended focus: study planning, time management "
            "and regular academic practice."
        )

    else:

        st.success(
            "🌟 **Priority Action:** Continue monitoring the class "
            "and maintain current academic practices."
        )

        st.write(
            "Recommended focus: early identification of students "
            "whose performance begins to decline."
        )

    st.divider()


# =========================================================
# STUDENT PREDICTION
# =========================================================

elif page == "👨‍🎓 Student Prediction":

    st.title("👨‍🎓 Student Performance Prediction")

    st.write(
        "Enter the student's academic details below to predict "
        "final marks and generate an AI-based recommendation."
    )

    # =========================================================
    # STUDENT INFORMATION
    # =========================================================

    st.subheader("👤 Student Information")

    student_name = st.text_input(
        "Student Name",
        placeholder="Enter student name",
        key="new_student_name"
    )

    student_id = st.text_input(
    "Student ID",
    placeholder="Enter student ID",
    key="new_student_id"
    )

    # =========================================================
    # PERFORMANCE INPUTS
    # =========================================================

    st.subheader("📋 Academic Performance Details")

    col1, col2 = st.columns(2)

    with col1:

        attendance = st.slider(
            "📅 Attendance (%)",
            min_value=0,
            max_value=100,
            value=75,
            key="prediction_attendance"
        )

        assignment = st.slider(
            "📝 Assignment Score",
            min_value=0,
            max_value=100,
            value=70,
            key="prediction_assignment"
        )

        internal = st.slider(
            "📚 Internal Marks",
            min_value=0,
            max_value=100,
            value=65,
            key="prediction_internal"
        )

    with col2:

        study_hours = st.slider(
            "⏱️ Study Hours per Day",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.5,
            key="prediction_study_hours"
        )

        previous_marks = st.slider(
            "📊 Previous Marks",
            min_value=0,
            max_value=100,
            value=65,
            key="prediction_previous_marks"
        )

    # =========================================================
    # ADD TRAINING RECORD
    # =========================================================

    st.divider()

    st.subheader("📚 Add Training Record")

    st.write(
        "Enter the actual final marks of a completed student "
        "to add the record to the AI training dataset."
    )

    actual_final_marks = st.slider(
        "🎯 Actual Final Marks",
        min_value=0,
        max_value=100,
        value=70,
        key="actual_final_marks"
    )

    add_training_button = st.button(
        "💾 Add Training Record",
        use_container_width=True,
        key="add_training_record"
    )

    if add_training_button:

        if student_id.strip() == "" or student_name.strip() == "":
            st.warning(
                "⚠️ Please enter both Student ID and Student Name."
            )

        else:

            # Check whether Student ID already exists
            cursor.execute(
                "SELECT Student_ID FROM students WHERE Student_ID = ?",
                (student_id,)
            )

            existing_student = cursor.fetchone()

            if existing_student:

                cursor.execute(
                    """
                    UPDATE students
                    SET
                        Name = ?,
                        Attendance = ?,
                        Assignment_Score = ?,
                        Internal_Marks = ?,
                        Study_Hours = ?,
                        Previous_Marks = ?,
                        Actual_Final_Marks = ?,
                        Final_Marks = ?
                    WHERE Student_ID = ?
                    """,
                    (
                        student_name,
                        attendance,
                        assignment,
                        internal,
                        study_hours,
                        previous_marks,
                        actual_final_marks,
                        actual_final_marks,
                        student_id
                    )
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO students (
                        Student_ID,
                        Name,
                        Attendance,
                        Assignment_Score,
                        Internal_Marks,
                        Study_Hours,
                        Previous_Marks,
                        Final_Marks,
                        Actual_Final_Marks
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        student_name,
                        attendance,
                        assignment,
                        internal,
                        study_hours,
                        previous_marks,
                        actual_final_marks,
                        actual_final_marks
                    )
                )

            connection.commit()

            st.success(
                f"✅ Training record for {student_name} "
                "was added successfully."
            )

            st.rerun()


    # =========================================================
    # PREDICT BUTTON
    # =========================================================

    st.write("")

    predict_button = st.button(
        "🔮 Predict Final Marks",
        use_container_width=True,
        key="predict_final_marks"
    )

    

    if predict_button:

        # -----------------------------------------------------
        # VALIDATE STUDENT INFORMATION
        # -----------------------------------------------------

        if student_id.strip() == "" or student_name.strip() == "":
            st.warning(
                "⚠️ Please enter both Student ID and Student Name "
                "before generating the prediction."
            )

        else:

            # -------------------------------------------------
            # CREATE MODEL INPUT
            # -------------------------------------------------

            input_data = pd.DataFrame([{
                "Attendance": attendance,
                "Assignment_Score": assignment,
                "Internal_Marks": internal,
                "Study_Hours": study_hours,
                "Previous_Marks": previous_marks
            }])

            # -------------------------------------------------
            # MAKE PREDICTION
            # -------------------------------------------------

            if model is not None:

                prediction = model.predict(input_data)[0]

            else:

                st.error(
                    "⚠️ The AI model is not available yet. "
                    "Please add at least 6 student records before making a prediction."
                )

                st.stop()

                  

            # Keep prediction between 0 and 100

            prediction = max(
                0,
                min(100, prediction)
            )

            # -------------------------------------------------
            # SAVE STUDENT TO DATABASE
            # -------------------------------------------------

            # Check whether the Student ID already exists
            cursor.execute(
                "SELECT Student_ID FROM students WHERE Student_ID = ?",
                (student_id,)
            )

            existing_student = cursor.fetchone()

            if existing_student:

                # Update existing student without changing Actual_Final_Marks
                cursor.execute(
                    """
                    UPDATE students
                    SET
                        Name = ?,
                        Attendance = ?,
                        Assignment_Score = ?,
                        Internal_Marks = ?,
                        Study_Hours = ?,
                        Previous_Marks = ?,
                        Predicted_Final_Marks = ?
                    WHERE Student_ID = ?
                    """,
                    (
                        student_name,
                        attendance,
                        assignment,
                        internal,
                        study_hours,
                        previous_marks,
                        float(prediction),
                        student_id
                    )
                )

            else:

                # Insert new student
                cursor.execute(
                    """
                    INSERT INTO students (
                        Student_ID,
                        Name,
                        Attendance,
                        Assignment_Score,
                        Internal_Marks,
                        Study_Hours,
                        Previous_Marks,
                        Predicted_Final_Marks
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student_id,
                        student_name,
                        attendance,
                        assignment,
                        internal,
                        study_hours,
                        previous_marks,
                        float(prediction)
                    )
                )

            connection.commit()

            # -------------------------------------------------
            # SAVE RESULT
            # -------------------------------------------------

            st.session_state["last_prediction"] = prediction
            st.session_state["last_student_name"] = student_name

            st.session_state["last_attendance"] = attendance
            st.session_state["last_assignment"] = assignment
            st.session_state["last_internal"] = internal
            st.session_state["last_study_hours"] = study_hours
            st.session_state["last_previous_marks"] = previous_marks

            st.session_state["prediction_saved"] = True

            # Refresh the application so the latest database
            # data is loaded and the ML model is retrained
            st.rerun()

    # =========================================================
    # DISPLAY RESULT
    # =========================================================

    if "last_prediction" in st.session_state:

        prediction = st.session_state["last_prediction"]

        saved_name = st.session_state["last_student_name"]

        st.divider()

        st.header("🎯 Prediction Result")

        # -----------------------------------------------------
        # PERFORMANCE STATUS
        # -----------------------------------------------------

        if prediction >= 80:

            status = "🟢 High Performer"

        elif prediction >= 60:

            status = "🟡 Average Performer"

        else:

            status = "🔴 At Risk"

        # -----------------------------------------------------
        # RESULT CARDS
        # -----------------------------------------------------

        result_col1, result_col2 = st.columns(2)

        with result_col1:

            st.metric(
                "🎯 Predicted Final Marks",
                f"{prediction:.1f}/100"
            )

        with result_col2:

            st.metric(
                "📌 Performance Status",
                status
            )

        # =====================================================
        # STUDENT SUMMARY
        # =====================================================

        st.subheader("📝 Student Summary")

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.info(
                f"👤 **Student Name**\n\n"
                f"{saved_name}"
            )

        with summary_col2:

            st.info(
                f"🎯 **Predicted Final Score**\n\n"
                f"{prediction:.1f}/100"
            )

        # =====================================================
        # AI RECOMMENDATION
        # =====================================================

        st.subheader("💡 AI Recommendation")

        if prediction >= 80:

            st.success(
                "🌟 **Excellent Performance**\n\n"
                "The student is demonstrating strong academic "
                "potential. Encourage advanced learning activities, "
                "challenging assignments and continued consistent "
                "study habits."
            )

        elif prediction >= 60:

            st.warning(
                "📚 **Average Performance**\n\n"
                "The student is performing at an average level. "
                "Focus on improving attendance, assignment scores, "
                "internal marks and daily study hours to achieve "
                "better academic performance."
            )

        else:

            st.error(
                "⚠️ **Academic Support Recommended**\n\n"
                "The student may require additional academic "
                "support. Improve attendance, provide extra "
                "practice, monitor assignments and offer regular "
                "academic guidance."
            )

        # =====================================================
        # STUDENT PERFORMANCE ANALYSIS
        # =====================================================

        st.subheader("📊 Student Performance Analysis")

        chart_data = pd.DataFrame({
            "Performance Factor": [
                "Attendance",
                "Assignment",
                "Internal Marks",
                "Previous Marks"
            ],
            "Score": [
                st.session_state["last_attendance"],
                st.session_state["last_assignment"],
                st.session_state["last_internal"],
                st.session_state["last_previous_marks"]
            ]
        })

        st.bar_chart(
            chart_data.set_index("Performance Factor"),
            use_container_width=True
        )

        # =====================================================
        # INPUT SUMMARY
        # =====================================================

        st.subheader("📋 Input Summary")

        summary_col1, summary_col2, summary_col3, summary_col4 = (
            st.columns(4)
        )

        with summary_col1:

            st.metric(
                "📅 Attendance",
                f"{st.session_state['last_attendance']}%"
            )

        with summary_col2:

            st.metric(
                "📝 Assignment",
                f"{st.session_state['last_assignment']}/100"
            )

        with summary_col3:

            st.metric(
                "📚 Internal Marks",
                f"{st.session_state['last_internal']}/100"
            )

        with summary_col4:

            st.metric(
                "⏱️ Study Hours",
                f"{st.session_state['last_study_hours']} hrs"
            )

        # =====================================================
        # PREVIOUS MARKS
        # =====================================================

        st.metric(
            "📊 Previous Marks",
            f"{st.session_state['last_previous_marks']}/100"
        )

        st.caption(
            "Prediction generated using the EduIntel "
            "machine-learning model."
        )


# =========================================================
# CLASS ANALYTICS
# =========================================================
elif page == "📊 Class Analytics":

    st.title("📊 Class Analytics")

    st.write(
        "Analyze overall class performance, identify students "
        "who need attention, and explore academic trends."
    )

    if data.empty:

        st.warning(
            "⚠️ No student records are available yet."
        )

        st.info(
            "Please add student records from the Student Prediction page."
        )

        st.stop()

    

    # =========================================================
    # CLASS OVERVIEW
    # =========================================================

    st.subheader("📌 Class Overview")

    total_students = len(data)
    average_marks = data["Display_Final_Marks"].mean()
    highest_marks = data["Display_Final_Marks"].max()
    lowest_marks = data["Display_Final_Marks"].min()

    high_performers = len(
        data[data["Display_Final_Marks"] >= 80]
    )

    average_performers = len(
        data[
            (data["Display_Final_Marks"] >= 60)
            & (data["Display_Final_Marks"] < 80)
        ]
    )

    at_risk_students = len(
        data[data["Display_Final_Marks"] < 60]
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "👥 Total Students",
            total_students
        )

    with col2:
        st.metric(
            "📊 Average Marks",
            f"{average_marks:.1f}"
        )

    with col3:
        st.metric(
            "🏆 Highest Marks",
            f"{highest_marks:.1f}"
        )

    with col4:
        st.metric(
            "📉 Lowest Marks",
            f"{lowest_marks:.1f}"
        )

    with col5:
        st.metric(
            "🔴 At Risk",
            at_risk_students
        )

    st.divider()

    # =========================================================
    # PERFORMANCE CATEGORIES
    # =========================================================

    st.subheader("🎯 Performance Categories")

    
    def performance_category(marks):

      if pd.isna(marks):
        return "No Marks"

      if marks >= 80:
        return "High Performer"

      elif marks >= 60:
        return "Average Performer"

      else:
        return "At Risk"

    analytics_data = data.copy()

    analytics_data["Performance_Category"] = (
        analytics_data["Display_Final_Marks"].apply(
            performance_category
        )
    )

    category_col1, category_col2, category_col3 = st.columns(3)

    with category_col1:
        st.metric(
            "🏆 High Performers",
            high_performers
        )

    with category_col2:
        st.metric(
            "🟡 Average Performers",
            average_performers
        )

    with category_col3:
        st.metric(
            "🔴 At Risk Students",
            at_risk_students
        )

    performance_counts = (
        analytics_data["Performance_Category"]
        .value_counts()
    )

    st.bar_chart(
        performance_counts,
        use_container_width=True
    )

    st.divider()

    # =========================================================
    # CLASS PERFORMANCE SUMMARY
    # =========================================================

    st.subheader("📈 Class Performance Summary")

    summary_data = pd.DataFrame(
        {
            "Performance Factor": [
                "Attendance",
                "Assignment Score",
                "Internal Marks",
                "Study Hours",
                "Previous Marks",
                "Final Marks"
            ],
            "Class Average": [
                data["Attendance"].mean(),
                data["Assignment_Score"].mean(),
                data["Internal_Marks"].mean(),
                data["Study_Hours"].mean(),
                data["Previous_Marks"].mean(),
                data["Display_Final_Marks"].mean()
            ]
        }
    )

    summary_data["Class Average"] = (
        summary_data["Class Average"].round(2)
    )

    st.dataframe(
        summary_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================================================
    # TOP PERFORMING STUDENTS
    # =========================================================

    st.subheader("🏆 Top Performing Students")

    top_students = (
        analytics_data
        .sort_values(
            by="Display_Final_Marks",
            ascending=False
        )
        .head(5)
    )

    st.dataframe(
        top_students[
            [
                "Student_ID",
                "Name",
                "Display_Final_Marks",
                "Performance_Category"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================================================
    # STUDENTS NEEDING ATTENTION
    # =========================================================

    st.subheader("⚠️ Students Needing Attention")

    low_performers = (
        analytics_data[
        (analytics_data["Display_Final_Marks"] < 60)
        | (analytics_data["Attendance"] < 75)
    ].sort_values(
        by="Display_Final_Marks",
        ascending=True
    )
    )

    if len(low_performers) > 0:

        st.warning(
            f"⚠️ {len(low_performers)} student(s) "
            "may require academic attention."
        )

        st.dataframe(
            low_performers[
                [
                    "Student_ID",
                    "Name",
                    "Attendance",
                    "Display_Final_Marks",
                    "Study_Hours",
                    "Performance_Category"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "✅ No students currently require academic attention."
        )

    st.divider()

    # =========================================================
    # SEARCH STUDENT
    # =========================================================

    st.subheader("🔎 Search Student")

    search_name = st.text_input(
        "Enter student name",
        placeholder="Type a student name...",
        key="analytics_search_student"
    )

    if search_name.strip():

        filtered_students = analytics_data[
            analytics_data["Name"].str.contains(
                search_name,
                case=False,
                na=False
            )
        ]

        if len(filtered_students) > 0:

            st.dataframe(
                filtered_students,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "🔍 No student found with that name."
            )

        # =====================================================
        # SELECTED STUDENT DETAILS
        # =====================================================

        if len(filtered_students) == 1:

            student = filtered_students.iloc[0]

            st.subheader(
                f"👤 {student['Name']} - Student Details"
            )

            detail_col1, detail_col2, detail_col3 = (
                st.columns(3)
            )

            detail_col4, detail_col5, detail_col6 = (
                st.columns(3)
            )

            with detail_col1:

                st.metric(
                    "🎯 Final Marks",
                    f"{student['Display_Final_Marks']:.1f}/100"
                )

            with detail_col2:

                st.metric(
                    "📅 Attendance",
                    f"{student['Attendance']:.1f}%"
                )

            with detail_col3:

                st.metric(
                    "📚 Study Hours",
                    f"{student['Study_Hours']:.1f}"
                )

            with detail_col4:

                st.metric(
                    "📝 Assignment",
                    f"{student['Assignment_Score']:.1f}"
                )

            with detail_col5:

                st.metric(
                    "📖 Internal Marks",
                    f"{student['Internal_Marks']:.1f}"
                )

            with detail_col6:

                st.metric(
                    "📊 Previous Marks",
                    f"{student['Previous_Marks']:.1f}"
                )

            st.markdown("### 🎯 Performance Status")

            if student["Display_Final_Marks"] >= 80:

                st.success(
                    "🟢 High Performer - Keep up the excellent work!"
                )

            elif student["Display_Final_Marks"] >= 60:

                st.warning(
                    "🟡 Average Performer - There is room for improvement."
                )

            else:

                st.error(
                    "🔴 At Risk - Additional academic support is recommended."
                )

            st.markdown("### 💡 Personalized Recommendation")

            if student["Attendance"] < 75:

                st.info(
                    "📅 Improve attendance and maintain regular "
                    "participation in classes."
                )

            elif student["Assignment_Score"] < 60:

                st.info(
                    "📝 Complete assignments regularly and "
                    "improve assignment performance."
                )

            elif student["Internal_Marks"] < 60:

                st.info(
                    "📖 Focus more on internal assessments "
                    "and subject preparation."
                )

            elif student["Study_Hours"] < 3:

                st.info(
                    "⏰ Increase daily study time to at least "
                    "3 hours and follow a consistent schedule."
                )

            else:

                st.success(
                    "🌟 Excellent! Continue maintaining the "
                    "current academic routine."
                )

    st.divider()

    # =========================================================
    # ATTENDANCE VS FINAL MARKS
    # =========================================================

    st.subheader("📅 Attendance vs Final Marks")

    attendance_chart = data[
        [
            "Name",
            "Attendance",
            "Display_Final_Marks"
        ]
    ].set_index("Name")

    st.line_chart(
        attendance_chart[
            [
                "Attendance",
                "Display_Final_Marks"
            ]
        ],
        use_container_width=True
    )

    # =========================================================
    # STUDY HOURS VS FINAL MARKS
    # =========================================================

    st.subheader("📚 Study Hours vs Final Marks")

    study_chart = data[
        [
            "Name",
            "Study_Hours",
            "Display_Final_Marks"
        ]
    ].set_index("Name")

    st.bar_chart(
        study_chart[
            [
                "Study_Hours",
                "Display_Final_Marks"
            ]
        ],
        use_container_width=True
    )

    st.divider()
    # =========================================================
    # DOWNLOAD CLASS REPORT
    # =========================================================

    st.subheader("📥 Download Class Report")

    class_report = data.copy()

    class_report["Performance_Category"] = (
        class_report["Display_Final_Marks"].apply(
            performance_category
        )
    )

    class_report = class_report[
        [
            "Student_ID",
            "Name",
            "Attendance",
            "Assignment_Score",
            "Internal_Marks",
            "Study_Hours",
            "Previous_Marks",
            "Display_Final_Marks",
            "Performance_Category"
        ]
    ]

    class_report = class_report.rename(
    columns={
        "Display_Final_Marks": "Final_Marks"
    }
)

    csv_class_report = class_report.to_csv(
        index=False
    )

    st.download_button(
        label="📥 Download Class Performance Report",
        data=csv_class_report,
        file_name="EduIntel_Class_Performance_Report.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()

    # =========================================================
    # AI-GENERATED CLASS INSIGHTS
    # =========================================================

    st.subheader("🤖 AI-Generated Class Insights")

    highest_student = data.loc[
        data["Display_Final_Marks"].idxmax(),
        "Name"
    ]

    highest_marks_value = data["Display_Final_Marks"].max()

    lowest_student = data.loc[
        data["Display_Final_Marks"].idxmin(),
        "Name"
    ]

    lowest_marks_value = data["Display_Final_Marks"].min()



    attendance_corr = (
        data["Attendance"]
        .corr(data["Display_Final_Marks"])
    )

    study_corr = (
        data["Study_Hours"]
        .corr(data["Display_Final_Marks"])
    )

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:

        st.info(
            f"⭐ **Top Performer**\n\n"
            f"{highest_student} has the highest final "
            f"score of {highest_marks_value:.1f}."
        )

    with insight_col2:

        st.warning(
            f"📉 **Lowest Performer**\n\n"
            f"{lowest_student} has the lowest final "
            f"score of {lowest_marks_value:.1f}."
        )

    st.info(
        f"📊 **Class Average:** "
        f"{average_marks:.1f} marks"
    )

    if attendance_corr >= 0.5:

        st.write(
            "📅 **Attendance Insight:** Attendance shows "
            "a strong positive relationship with final marks."
        )

    elif attendance_corr >= 0.2:

        st.write(
            "📅 **Attendance Insight:** Attendance shows "
            "a moderate positive relationship with final marks."
        )

    else:

        st.write(
            "📅 **Attendance Insight:** Attendance shows "
            "a weak relationship with final marks."
        )

    if study_corr >= 0.5:

        st.write(
            "📚 **Study Hours Insight:** Study hours show "
            "a strong positive relationship with final marks."
        )

    elif study_corr >= 0.2:

        st.write(
            "📚 **Study Hours Insight:** Study hours show "
            "a moderate positive relationship with final marks."
        )

    else:

        st.write(
            "📚 **Study Hours Insight:** Study hours show "
            "a weak relationship with final marks."
        )


    # =========================================================
    # DELETE STUDENT
    # =========================================================

    st.divider()

    st.subheader("🗑️ Delete Student Record")

    delete_student_id = st.selectbox(
        "Select Student ID to delete",
        data["Student_ID"].tolist(),
        key="delete_student"
    )

    confirm_delete = st.checkbox(
        "⚠️ I confirm that I want to permanently delete this student",
        key="confirm_delete"
    )

    if st.button("🗑️ Delete Selected Student"):

        if not confirm_delete:

            st.warning(
                "⚠️ Please confirm the deletion before continuing."
            )

        else:

            student_to_delete = data[
                data["Student_ID"] == delete_student_id
            ].iloc[0]

            cursor.execute(
                "DELETE FROM students WHERE Student_ID = ?",
                (student_to_delete["Student_ID"],)
            )

            connection.commit()

            st.success(
                f"✅ Student '{student_to_delete['Name']}' has been deleted successfully."
            )

            st.rerun()    

# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "💡 Recommendations":

    st.title("💡 Student Recommendations")

    if data.empty:
        st.warning(
            "⚠️ No student records are available yet."
        )

        st.info(
            "Please add student records from the Student Prediction page "
            "to generate personalized recommendations."
        )

        st.stop()

    st.write(
        "Select a student to view personalized academic "
        "recommendations based on their performance."
    )

    # =========================================================
    # SELECT STUDENT
    # =========================================================

    st.subheader("👤 Select Student")

    selected_student_id = st.selectbox(
        "Select Student ID",
        data["Student_ID"].tolist(),
        key="recommendation_student_id"
    )

    student = data[
        data["Student_ID"] == selected_student_id
    ].iloc[0]


    # =========================================================
    # STUDENT PERFORMANCE OVERVIEW
    # =========================================================

    st.subheader(
        f"📊 {student['Name']}'s Performance Overview"
    )
    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📊 Final Marks",
           f"{student['Display_Final_Marks']:.1f}/100"
        )

    with col2:

        st.metric(
            "📅 Attendance",
            f"{student['Attendance']:.1f}%"
        )

    with col3:

        st.metric(
            "📝 Assignment",
            f"{student['Assignment_Score']:.1f}"
        )

    with col4:

        st.metric(
            "📚 Study Hours",
            f"{student['Study_Hours']:.1f}"
        )

    st.divider()

    # =========================================================
    # PERFORMANCE STATUS
    # =========================================================

    st.subheader("🎯 Performance Status")

    if student["Display_Final_Marks"] >= 80:

        st.success(
            "🟢 High Performer — The student is performing "
            "very well academically."
        )

    elif student["Display_Final_Marks"] >= 60:

        st.warning(
            "🟡 Average Performer — The student has potential "
            "for further improvement."
        )

    else:

        st.error(
            "🔴 At Risk — The student may require additional "
            "academic support."
        )

    # =========================================================
    # GENERATE RECOMMENDATIONS
    # =========================================================

    recommendations = []

    if student["Attendance"] < 75:

        recommendations.append(
            "📅 Improve attendance and maintain regular "
            "participation in classes."
        )

    if student["Assignment_Score"] < 60:

        recommendations.append(
            "📝 Complete assignments regularly and improve "
            "assignment performance."
        )

    if student["Internal_Marks"] < 60:

        recommendations.append(
            "📖 Focus more on internal assessments and "
            "strengthen subject preparation."
        )

    if student["Study_Hours"] < 3:

        recommendations.append(
            "⏰ Increase daily study time to at least 3 hours "
            "and follow a consistent study schedule."
        )

    if student["Previous_Marks"] < 60:

        recommendations.append(
            "📈 Review previous academic topics and focus "
            "on improving weak areas."
        )

    if student["Display_Final_Marks"] < 60:

        recommendations.append(
            "⚠️ Consider additional academic support, "
            "practice sessions and regular teacher guidance."
        )

    # =========================================================
    # PERSONALIZED ACTION PLAN
    # =========================================================

    st.subheader("🎯 Personalized Action Plan")

    if recommendations:

        for recommendation in recommendations:

            st.info(recommendation)

    else:

        st.success(
            "🌟 Excellent! No major academic concerns were "
            "identified. Continue maintaining the current "
            "study routine."
        )

    st.divider()

    # =========================================================
    # STUDENT FACTOR ANALYSIS
    # =========================================================

    st.subheader("📈 Performance Factor Analysis")

    factor_data = pd.DataFrame(
        {
            "Factor": [
                "Attendance",
                "Assignment Score",
                "Internal Marks",
                "Display_Final_Marks"
            ],
            "Score": [
                student["Attendance"],
                student["Assignment_Score"],
                student["Internal_Marks"],
                student["Display_Final_Marks"]
            ]
        }
    )

    st.bar_chart(
        factor_data.set_index("Factor"),
        use_container_width=True
    )

    st.divider()

    # =========================================================
    # ADDITIONAL ACADEMIC INFORMATION
    # =========================================================

    st.subheader("📋 Academic Information")

    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:

        st.metric(
            "📖 Internal Marks",
            f"{student['Internal_Marks']:.1f}/100"
        )

    with info_col2:

        st.metric(
            "📚 Previous Marks",
            f"{student['Previous_Marks']:.1f}/100"
        )

    with info_col3:

        st.metric(
            "⏱️ Daily Study Hours",
            f"{student['Study_Hours']:.1f} hrs"
        )

    st.divider()

    # =========================================================
    # DOWNLOAD STUDENT REPORT
    # =========================================================

    st.subheader("📥 Download Student Report")

    report = pd.DataFrame(
        [
            {
                "Student ID": student["Student_ID"],
                "Student Name": student["Name"],
                "Attendance": student["Attendance"],
                "Assignment Score": student["Assignment_Score"],
                "Internal Marks": student["Internal_Marks"],
                "Study Hours": student["Study_Hours"],
                "Previous Marks": student["Previous_Marks"],
                "Final Marks": student["Display_Final_Marks"]
            }
        ]
    )

    csv_report = report.to_csv(
        index=False
    )

    st.download_button(
        label="📥 Download Student Report",
        data=csv_report,
        file_name=(
            f"{student['Name']}_EduIntel_Report.csv"
        ),
        mime="text/csv",
        use_container_width=True
    ) 

# =========================================================
# AI MODEL PERFORMANCE
# =========================================================
elif page == "🤖 AI Model Performance":

    st.title("🤖 AI Model Performance")

    st.write(
        "Evaluate the performance of the machine-learning model "
        "used by EduIntel to predict student final marks."
    )

    # =========================================================
    # CHECK MODEL AVAILABILITY
    # =========================================================

    if model is None:

        st.warning(
            "⚠️ AI Model Performance is unavailable. "
            "Please add at least 6 student records to train the model."
        )

        st.stop()

    # =========================================================
    # MODEL PERFORMANCE METRICS
    # =========================================================

    st.subheader("📊 Model Evaluation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🤖 Model",
            "Linear Regression"
        )

    with col2:

        st.metric(
            "📉 Mean Absolute Error",
            f"{mae:.2f}"
        )

    with col3:

        st.metric(
            "🎯 R² Score",
            f"{r2:.2f}"
        )

    with col4:

        st.metric(
            "🔄 Cross-Validation R²",
            f"{cv_r2:.2f}"
        )

        if cv_r2 >= 0.80:
            st.success("🟢 Excellent model consistency")

        elif cv_r2 >= 0.60:
            st.info("🟡 Good model consistency")

        else:
            st.warning("🔴 Model consistency needs improvement")
         
    st.divider()

    # =========================================================
    # FEATURE IMPORTANCE
    # =========================================================

    st.subheader("🔍 Feature Importance")

    st.write(
        "The chart below shows how strongly each academic "
        "factor influences the model's prediction."
    )

    importance_display = feature_importance[
        ["Feature", "Importance"]
    ].copy()

    importance_display["Importance"] = (
        importance_display["Importance"].round(3)
    )

    st.dataframe(
        importance_display,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        importance_display.set_index("Feature"),
        use_container_width=True
    )

    st.caption(
        "Positive values indicate a positive influence on "
        "predicted marks, while negative values indicate a "
        "negative influence."
    )

    st.divider()

    # =========================================================
    # PREDICTED VS ACTUAL PERFORMANCE
    # =========================================================

    st.subheader("🎯 Predicted vs Actual Marks")

    st.write(
        "This comparison shows how closely the AI model's "
        "predicted marks match the students' actual final marks."
    )

    comparison_data = pd.DataFrame({
        "Actual Marks": y_test.values,
        "Predicted Marks": predictions
    })

    comparison_data["Predicted Marks"] = (
        comparison_data["Predicted Marks"].round(2)
    )

    comparison_data["Prediction Error"] = (
        comparison_data["Actual Marks"]
        - comparison_data["Predicted Marks"]
    )

    # =========================================================
    # PREDICTION ERROR ANALYSIS
    # =========================================================

    mean_error = comparison_data["Prediction Error"].abs().mean()

    if mean_error <= 2:
        st.success(
            f"🟢 Excellent prediction accuracy — "
            f"average error is {mean_error:.2f} marks."
        )

    elif mean_error <= 5:
        st.info(
            f"🟡 Good prediction accuracy — "
            f"average error is {mean_error:.2f} marks."
        )

    else:
        st.warning(
            f"🔴 Prediction error is relatively high — "
            f"average error is {mean_error:.2f} marks."
        )

    st.dataframe(
        comparison_data,
        use_container_width=True,
        hide_index=True
    )

    st.line_chart(
        comparison_data,
        use_container_width=True
    )

    st.caption(
        "A smaller difference between actual and predicted marks "
        "indicates better model prediction accuracy."
    )

    st.divider()



    # =========================================================
    # MODEL INFORMATION
    # =========================================================

    st.subheader("🧠 Model Information")
    
    st.info(
        "EduIntel uses a Linear Regression machine-learning "
        "model to predict student final marks using academic "
        "performance factors."
    )

    # =========================================================
    # FEATURES USED BY THE MODEL
    # =========================================================

    st.subheader("📋 Features Used for Prediction")

    feature_data = pd.DataFrame(
        {
            "Feature": [
                "Attendance",
                "Assignment Score",
                "Internal Marks",
                "Study Hours",
                "Previous Marks"
            ],
            "Description": [
                "Student attendance percentage",
                "Assignment performance score",
                "Internal assessment marks",
                "Average daily study hours",
                "Previous academic marks"
            ]
        }
    )

    st.dataframe(
        feature_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    
    # =========================================================
    # AI MODEL SUMMARY
    # =========================================================

    st.subheader("📝 AI Model Summary")

    st.caption(
        "Cross-validation R² shows how consistently the model "
        "performs across different subsets of student data."
    )

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:

        st.info(
            "🧠 **Algorithm**\n\n"
            "EduIntel uses Linear Regression to estimate "
            "student final marks based on academic performance factors."
        )

    with summary_col2:

        st.info(
            "🎯 **Prediction Target**\n\n"
            "The model predicts the student's Final Marks "
            "on a 0–100 scale."
        )

    # =========================================================
    # AI PERFORMANCE INTERPRETATION
    # =========================================================

    st.subheader("📊 AI Performance Interpretation")

    if r2 >= 0.80 and cv_r2 >= 0.80:

        st.success(
            "🟢 The AI model demonstrates strong predictive "
            "performance. The high R² score and cross-validation "
            "score indicate consistent prediction performance."
        )

    elif r2 >= 0.60 and cv_r2 >= 0.60:

        st.info(
            "🟡 The AI model demonstrates moderate predictive "
            "performance. Additional student data may improve "
            "model reliability."
        )

    else:

        st.warning(
            "🔴 The AI model currently shows limited predictive "
            "performance. More student data and improved features "
            "may help improve prediction quality."
        )

    # =========================================================
    # MODEL RELIABILITY SUMMARY
    # =========================================================

    st.subheader("🛡️ Model Reliability Summary")

    if r2 >= 0.80 and cv_r2 >= 0.80:

        st.success(
            "🟢 **High Reliability**\n\n"
            "The model shows strong predictive performance "
            "and consistent results across validation datasets."
        )

    elif r2 >= 0.60 and cv_r2 >= 0.60:

        st.info(
            "🟡 **Moderate Reliability**\n\n"
            "The model provides useful predictions, but adding "
            "more student data may improve reliability."
        )

    else:

        st.warning(
            "🔴 **Low Reliability**\n\n"
            "The current model requires improvement before its "
            "predictions can be considered highly reliable."
        )

    st.divider()

    # =========================================================
    # MODEL LIMITATIONS
    # =========================================================

    st.subheader("⚠️ Model Limitations")

    st.write(
        "Like any machine-learning model, EduIntel has certain "
        "limitations that should be considered when interpreting predictions."
    )

    limitation_col1, limitation_col2 = st.columns(2)

    with limitation_col1:

        st.info(
            "📊 **Data Dependency**\n\n"
            "Prediction quality depends on the amount and quality "
            "of student data available for training."
        )

        st.info(
            "🎯 **Prediction Accuracy**\n\n"
            "Predictions are estimates and should be used as a "
            "supporting tool rather than a final academic decision."
        )

    with limitation_col2:

        st.info(
            "📚 **Feature Limitations**\n\n"
            "The model currently uses attendance, assignments, "
            "internal marks, study hours, and previous marks."
        )

        st.info(
            "🔄 **Model Improvement**\n\n"
            "Adding more student records and relevant features "
            "can improve the model's reliability over time."
        )

    st.divider()

    # =========================================================
    # PREDICTION FACTORS
    # =========================================================

    st.subheader("🔍 Prediction Factors")

    factor_col1, factor_col2, factor_col3 = st.columns(3)

    with factor_col1:

        st.write("📅 **Attendance**")

        st.caption(
            "Measures the student's regularity in attending classes."
        )

    with factor_col2:

        st.write("📝 **Assignment Score**")

        st.caption(
            "Measures the student's assignment performance."
        )

    with factor_col3:

        st.write("📚 **Internal Marks**")

        st.caption(
            "Represents performance in internal assessments."
        )

    factor_col4, factor_col5 = st.columns(2)

    with factor_col4:

        st.write("⏱️ **Study Hours**")

        st.caption(
            "Represents average daily study time."
        )

    with factor_col5:

        st.write("📊 **Previous Marks**")

        st.caption(
            "Represents the student's previous academic performance."
        )

    

    # =========================================================
    # FINAL MESSAGE
    # =========================================================

    st.success(
        "✅ EduIntel AI model is ready to support student "
        "performance prediction and academic analysis."
    )