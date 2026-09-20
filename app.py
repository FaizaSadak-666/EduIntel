import os
import sqlite3
import hashlib
import secrets
import hmac
import re

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
# TEACHER ACCOUNT DATABASE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "eduintel.db")

auth_connection = sqlite3.connect(DB_PATH)
auth_cursor = auth_connection.cursor()

auth_cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

auth_connection.commit()


# =========================================================
# PASSWORD SECURITY FUNCTIONS
# =========================================================

def hash_password(password):
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password, stored_hash):
    try:
        salt, saved_hash = stored_hash.split("$")

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            200000
        ).hex()

        return hmac.compare_digest(
            password_hash,
            saved_hash
        )

    except (ValueError, AttributeError):
        return False


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "teacher_username" not in st.session_state:
    st.session_state["teacher_username"] = ""


# =========================================================
# TEACHER LOGIN AND REGISTRATION
# =========================================================

if not st.session_state["logged_in"]:

    left_space, login_column, right_space = st.columns(
        [1, 1.4, 1]
    )

    with login_column:

        with st.container(border=True):

            st.markdown(
                """
                <div style="text-align:center;font-size:52px;">
                    🎓
                </div>
                <h1 style="text-align:center;color:#111827;">
                    EduIntel
                </h1>
                <p style="text-align:center;color:#6b7280;">
                    AI-Based Student Performance Intelligence System
                </p>
                """,
                unsafe_allow_html=True
            )

            st.divider()

            login_tab, signup_tab = st.tabs([
                "🔐 Teacher Login",
                "📝 Teacher Sign Up"
            ])

            # -------------------------------------------------
            # LOGIN TAB
            # -------------------------------------------------

            with login_tab:

                st.subheader("Welcome Back")

                login_username = st.text_input(
                    "Username",
                    key="login_username"
                ).strip()

                login_password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password"
                )

                if st.button(
                    "🔐 Login to EduIntel",
                    use_container_width=True,
                    key="teacher_login_button"
                ):

                    authenticated = False

                    # Admin login using Streamlit secrets
                    if login_username == "admin":

                        try:
                            admin_password = st.secrets[
                                "login"
                            ]["password"]

                            if hmac.compare_digest(
                                login_password,
                                str(admin_password)
                            ):
                                authenticated = True

                        except Exception:
                            st.error(
                                "Admin credentials are not configured."
                            )

                    # Registered teacher login
                    else:

                        auth_cursor.execute(
                            """
                            SELECT password_hash
                            FROM teachers
                            WHERE username = ?
                            """,
                            (login_username,)
                        )

                        teacher_record = auth_cursor.fetchone()

                        if teacher_record and verify_password(
                            login_password,
                            teacher_record[0]
                        ):
                            authenticated = True

                    if authenticated:

                        st.session_state["logged_in"] = True
                        st.session_state["teacher_username"] = (
                            login_username
                        )

                        st.rerun()

                    else:
                        st.error(
                            "Invalid username or password."
                        )

            # -------------------------------------------------
            # SIGN UP TAB
            # -------------------------------------------------

            with signup_tab:

                st.subheader("Create Teacher Account")

                st.caption(
                    "Create an account to access EduIntel."
                )

                new_username = st.text_input(
                    "Choose Username",
                    key="signup_username"
                ).strip()

                new_password = st.text_input(
                    "Create Password",
                    type="password",
                    key="signup_password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="signup_confirm_password"
                )

                st.caption(
                    "Username: 4–20 characters; letters, numbers "
                    "and underscores only. Password: at least "
                    "8 characters."
                )

                if st.button(
                    "📝 Create Teacher Account",
                    use_container_width=True,
                    key="teacher_signup_button"
                ):

                    if not re.fullmatch(
                        r"[A-Za-z0-9_]{4,20}",
                        new_username
                    ):
                        st.error(
                            "Username must be 4–20 characters "
                            "and contain only letters, numbers "
                            "or underscores."
                        )

                    elif len(new_password) < 8:
                        st.error(
                            "Password must contain at least "
                            "8 characters."
                        )

                    elif new_password != confirm_password:
                        st.error(
                            "Passwords do not match."
                        )

                    elif new_username.lower() == "admin":
                        st.error(
                            "This username is reserved."
                        )

                    else:

                        try:
                            auth_cursor.execute(
                                """
                                INSERT INTO teachers (
                                    username,
                                    password_hash
                                )
                                VALUES (?, ?)
                                """,
                                (
                                    new_username,
                                    hash_password(new_password)
                                )
                            )

                            auth_connection.commit()

                            st.success(
                                "Teacher account created! "
                                "Please log in using your new credentials."
                            )

                        except sqlite3.IntegrityError:
                            st.error(
                                "This username is already registered. "
                                "Please choose another."
                            )

    st.stop()


# =========================================================
# END OF LOGIN AND REGISTRATION
# =========================================================

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
        Predicted_Final_Marks REAL,
        Record_Type TEXT DEFAULT 'Prediction'
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

if "Record_Type" not in existing_columns:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN Record_Type TEXT DEFAULT 'Prediction'"
    )

# ---------------------------------------------------------
# RESTORE HISTORICAL TRAINING RECORDS
# ---------------------------------------------------------

# Older EduIntel records stored actual marks in Final_Marks.
# Restore those marks into Actual_Final_Marks.

cursor.execute("""
    UPDATE students
    SET Actual_Final_Marks = Final_Marks
    WHERE Actual_Final_Marks IS NULL
      AND Final_Marks IS NOT NULL
""")

# Mark records with actual final marks as training records.

cursor.execute("""
    UPDATE students
    SET Record_Type = 'Training'
    WHERE Actual_Final_Marks IS NOT NULL
""")

connection.commit()



# =========================================================
# LOAD STUDENT DATA BASED ON USER ROLE
# =========================================================

current_username = st.session_state["teacher_username"]
is_admin = current_username == "admin"

if is_admin:
    data = pd.read_sql_query(
        "SELECT * FROM students",
        connection
    )
else:
    data = pd.read_sql_query(
        """
        SELECT *
        FROM students
        WHERE owner_username = ?
        """,
        connection,
        params=(current_username,)
    )

data["Display_Final_Marks"] = (
    data["Actual_Final_Marks"].fillna(
        data["Predicted_Final_Marks"]
    )
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

# =========================================================
# LOAD SHARED TRAINING DATA
# =========================================================

# Use the admin's existing historical records to train
# the shared model for all teachers.

training_data = pd.read_sql_query(
    """
    SELECT Attendance,
           Assignment_Score,
           Internal_Marks,
           Study_Hours,
           Previous_Marks,
           Actual_Final_Marks
    FROM students
    WHERE owner_username = 'admin'
      AND Actual_Final_Marks IS NOT NULL
      AND Student_ID NOT IN ('201', '202', '203', '204', '205')
    """,
    connection
)

# Convert training columns to numeric
training_data[features] = training_data[features].apply(
    pd.to_numeric,
    errors="coerce"
)

training_data["Actual_Final_Marks"] = pd.to_numeric(
    training_data["Actual_Final_Marks"],
    errors="coerce"
)

# Remove incomplete training records
training_data = training_data.dropna(
    subset=features + ["Actual_Final_Marks"]
)

# =========================================================
# INITIALIZE MODEL VARIABLES
# =========================================================

model = None
mae = float("nan")
r2 = float("nan")
cv_r2 = float("nan")

feature_importance = pd.DataFrame(
    columns=["Feature", "Importance"]
)

comparison_data = pd.DataFrame(
    columns=[
        "Actual Marks",
        "Predicted Marks",
        "Prediction Error"
    ]
)

# =========================================================
# TRAIN SHARED MODEL
# =========================================================

# Linear Regression can be fitted with 2 or more
# valid labelled records. Six is not required to predict.

if len(training_data) >= 2:

    X = training_data[features]
    y = training_data["Actual_Final_Marks"]

    # Train the shared model using all available
    # valid admin historical records.
    model = LinearRegression()
    model.fit(X, y)

    # =====================================================
    # FEATURE IMPORTANCE
    # =====================================================

    feature_importance = pd.DataFrame({
        "Feature": features,
        "Importance": model.coef_
    })

    feature_importance["Importance"] = (
        feature_importance["Importance"].round(3)
    )

    feature_importance = feature_importance.sort_values(
        by="Importance",
        key=abs,
        ascending=False
    )

    # =====================================================
    # MODEL EVALUATION
    # =====================================================

    # Keep cross-validation metrics only when there are
    # enough records for a more meaningful evaluation.
    if len(training_data) >= 6:

        from sklearn.model_selection import (
            KFold,
            cross_val_predict
        )

        cv_folds = min(5, len(training_data) // 2)

        kf = KFold(
            n_splits=cv_folds,
            shuffle=True,
            random_state=42
        )

        cv_predictions = cross_val_predict(
            LinearRegression(),
            X,
            y,
            cv=kf
        )

        mae = mean_absolute_error(
            y,
            cv_predictions
        )

        r2 = r2_score(
            y,
            cv_predictions
        )

        cv_r2 = r2

        comparison_data = pd.DataFrame({
            "Actual Marks": y.to_numpy(),
            "Predicted Marks": cv_predictions
        })

        comparison_data["Prediction Error"] = (
            comparison_data["Actual Marks"]
            - comparison_data["Predicted Marks"]
        )

        comparison_data = comparison_data.round(2)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.session_state["teacher_username"] = ""
    st.rerun()

# Display logged-in teacher's username
st.sidebar.success(
    f"👤 Logged in: {st.session_state['teacher_username']}"
)

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

    dashboard_data = data.copy()

    dashboard_data["Performance_Category"] = dashboard_data.apply(
        lambda row:
            "At Risk"
            if (
                (pd.notna(row["Display_Final_Marks"]) and row["Display_Final_Marks"] < 60)
                or
                (pd.notna(row["Attendance"]) and row["Attendance"] < 75)
            )
            else "No Marks"
            if pd.isna(row["Display_Final_Marks"])
            else "High Performer"
            if row["Display_Final_Marks"] >= 80
            else "Average Performer",
        axis=1
    )

    performance_summary = dashboard_data[
        "Performance_Category"
    ].value_counts()

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
            max_value=12.0,
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

            # -------------------------------------------------
            # SAVE STUDENT TO DATABASE WITH TEACHER OWNERSHIP
            # -------------------------------------------------

            # Use the currently logged-in account as the owner
            owner_username = st.session_state["teacher_username"]

            # Check whether this Student ID exists for THIS owner
            cursor.execute(
                """
                SELECT Student_ID
                FROM students
                WHERE Student_ID = ?
                  AND owner_username = ?
                """,
                (student_id.strip(), owner_username)
            )

            existing_student = cursor.fetchone()

            if existing_student:

                # Update only this owner's existing student
                # Preserve Training status when actual marks exist
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
                        Predicted_Final_Marks = ?,
                        Record_Type = CASE
                            WHEN Actual_Final_Marks IS NOT NULL
                            THEN 'Training'
                            ELSE 'Prediction'
                        END
                    WHERE Student_ID = ?
                      AND owner_username = ?
                    """,
                    (
                        student_name.strip(),
                        attendance,
                        assignment,
                        internal,
                        study_hours,
                        previous_marks,
                        float(prediction),
                        student_id.strip(),
                        owner_username
                    )
                )

            else:

                # Insert a new student record for this owner
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
                        Predicted_Final_Marks,
                        Record_Type,
                        owner_username
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Prediction', ?)
                    """,
                    (
                        student_id.strip(),
                        student_name.strip(),
                        attendance,
                        assignment,
                        internal,
                        study_hours,
                        previous_marks,
                        float(prediction),
                        owner_username
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
    # PREPARE ANALYTICS DATA
    # =========================================================

    analytics_data = data.copy()

    def performance_category(row):

        marks = row["Display_Final_Marks"]
        attendance = row["Attendance"]

        if (
            (pd.notna(marks) and marks < 60)
            or
            (pd.notna(attendance) and attendance < 75)
        ):
            return "At Risk"

        if pd.isna(marks):
            return "No Marks"

        if marks >= 80:
            return "High Performer"

        return "Average Performer"

    analytics_data["Performance_Category"] = (
        analytics_data.apply(
            performance_category,
            axis=1
        )
    )

    # =========================================================
    # CLASS OVERVIEW
    # =========================================================

    st.subheader("📌 Class Overview")

    total_students = len(analytics_data)

    average_marks = analytics_data["Display_Final_Marks"].mean()

    highest_marks = analytics_data["Display_Final_Marks"].max()

    lowest_marks = analytics_data["Display_Final_Marks"].min()

    high_performers = (
        analytics_data["Performance_Category"] == "High Performer"
    ).sum()

    average_performers = (
        analytics_data["Performance_Category"] == "Average Performer"
    ).sum()

    at_risk_students = (
        analytics_data["Performance_Category"] == "At Risk"
    ).sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("👥 Total Students", total_students)

    with col2:
        st.metric("📊 Average Marks", f"{average_marks:.1f}")

    with col3:
        st.metric("🏆 Highest Marks", f"{highest_marks:.1f}")

    with col4:
        st.metric("📉 Lowest Marks", f"{lowest_marks:.1f}")

    with col5:
        st.metric("🔴 At Risk", at_risk_students)

    st.divider()

    # =========================================================
    # PERFORMANCE CATEGORIES
    # =========================================================

    st.subheader("🎯 Performance Categories")

    category_col1, category_col2, category_col3 = st.columns(3)

    with category_col1:
        st.metric("🏆 High Performers", high_performers)

    with category_col2:
        st.metric("🟡 Average Performers", average_performers)

    with category_col3:
        st.metric("🔴 At Risk Students", at_risk_students)

    performance_counts = (
        analytics_data["Performance_Category"].value_counts()
    )

    st.bar_chart(
        performance_counts,
        use_container_width=True
    )

    st.divider()

    # =========================================================
    # STUDENT PERFORMANCE DETAILS
    # =========================================================


    # =========================================================
    # SEARCH STUDENT
    # =========================================================

    st.subheader("🔎 Search Student")

    search_query = st.text_input(
        "Search by Student Name or Student ID",
        placeholder="Enter student name or ID...",
        key="analytics_student_search"
    )

    if search_query.strip():

        search_results = analytics_data[
            analytics_data["Name"].astype(str).str.contains(
                search_query.strip(),
                case=False,
                na=False
            )
            |
            analytics_data["Student_ID"].astype(str).str.contains(
                search_query.strip(),
                case=False,
                na=False
            )
        ]

        if not search_results.empty:

            st.success(
                f"{len(search_results)} matching student(s) found."
            )

            st.dataframe(
                search_results[
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
                ].rename(
                    columns={
                        "Display_Final_Marks": "Final_Marks"
                    }
                ),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "No student found. Check the name or Student ID."
            )

    else:

        st.caption(
            "Enter a student name or ID to find their academic record."
        )

    st.divider()



    st.subheader("👨‍🎓 Student Performance Details ")

    display_columns = [
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

    student_details = analytics_data[display_columns].copy()

    student_details = student_details.rename(columns={
        "Display_Final_Marks": "Final_Marks"
    })

    st.dataframe(
        student_details,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =========================================================
    # AT-RISK STUDENT ANALYSIS
    # =========================================================

    st.subheader("🚨 At-Risk Student Analysis")

    risk_data = analytics_data[
        analytics_data["Performance_Category"] == "At Risk"
    ].copy()

    if not risk_data.empty:

        st.warning(
            f"{len(risk_data)} student(s) may need additional "
            "academic support."
        )

        st.dataframe(
            risk_data[
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

        st.caption(
            "Students are identified as at risk if their final "
            "marks are below 60 or attendance is below 75%."
        )

    else:

        st.success(
            "No students are currently identified as at risk."
        )

    st.divider()

    # =========================================================
    # ATTENDANCE ANALYSIS
    # =========================================================

    st.subheader("📅 Attendance Analysis")

    attendance_data = analytics_data.dropna(
        subset=["Attendance"]
    ).copy()

    if not attendance_data.empty:

        avg_attendance = attendance_data["Attendance"].mean()

        low_attendance_count = (
            attendance_data["Attendance"] < 75
        ).sum()

        attendance_col1, attendance_col2 = st.columns(2)

        with attendance_col1:
            st.metric(
                "📅 Average Attendance",
                f"{avg_attendance:.1f}%"
            )

        with attendance_col2:
            st.metric(
                "⚠️ Students Below 75%",
                int(low_attendance_count)
            )

        st.bar_chart(
            attendance_data.set_index("Name")[["Attendance"]],
            use_container_width=True
        )

    else:

        st.info("Attendance data is not available.")

    st.divider()

    # =========================================================
    # ACADEMIC PERFORMANCE ANALYSIS
    # =========================================================

    st.subheader("📈 Academic Performance Analysis")

    marks_data = analytics_data.dropna(
        subset=["Display_Final_Marks"]
    ).copy()

    if not marks_data.empty:

        marks_data = marks_data.sort_values(
            "Display_Final_Marks",
            ascending=False
        )

        st.bar_chart(
            marks_data.set_index("Name")[["Display_Final_Marks"]],
            use_container_width=True
        )

        st.caption(
            "This chart compares students based on their available "
            "final marks, including actual or predicted marks."
        )

    else:

        st.info("Final marks are not available for analysis.")

    st.divider()

    # =========================================================
    # CLASS PERFORMANCE INSIGHTS
    # =========================================================

    st.subheader("🧠 Class Performance Insights")

    avg_attendance = analytics_data["Attendance"].mean()
    avg_study_hours = analytics_data["Study_Hours"].mean()

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:

        if pd.notna(avg_attendance) and avg_attendance < 75:

            st.warning(
                "📅 Class attendance is below 75%. "
                "Attendance monitoring may be helpful."
            )

        elif pd.notna(avg_attendance):

            st.success(
                f"📅 Average attendance is {avg_attendance:.1f}%."
            )

        else:

            st.info("Attendance insights are unavailable.")

    with insight_col2:

        if pd.notna(avg_study_hours) and avg_study_hours < 3:

            st.warning(
                "⏱️ Average study time is below 3 hours per day. "
                "Encourage consistent study habits."
            )

        elif pd.notna(avg_study_hours):

            st.success(
                f"⏱️ Average study time is {avg_study_hours:.1f} "
                "hours per day."
            )

        else:

            st.info("Study-hour insights are unavailable.")

    st.divider()

    # =========================================================
    # DOWNLOAD CLASS PERFORMANCE REPORT
    # =========================================================

    st.subheader("📥 Download Class Performance Report")

    report_columns = [
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

    class_report = analytics_data[report_columns].copy()

    class_report = class_report.rename(columns={
        "Display_Final_Marks": "Final_Marks"
    })

    csv_report = class_report.to_csv(index=False)

    st.download_button(
        label="📥 Download Class Report (CSV)",
        data=csv_report,
        file_name="EduIntel_Class_Performance_Report.csv",
        mime="text/csv",
        use_container_width=True
    )

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

    if pd.isna(cv_r2):

        st.warning(
            "Cross-validation performance is unavailable."
        )

    elif cv_r2 >= 0.80:

        st.success(
            "🟢 Strong cross-validated predictive performance"
        )

    elif cv_r2 >= 0.60:

        st.info(
            "🟡 Moderate cross-validated predictive performance"
        )

    elif cv_r2 >= 0:

        st.warning(
            "🟠 Limited cross-validated predictive performance"
        )

    else:

        st.error(
            "🔴 The model performs worse than the "
            "mean-prediction baseline on cross-validation."
        )
         
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

    

       # =========================================================
    # PREDICTION ERROR ANALYSIS
    # =========================================================

    if not comparison_data.empty:
        mean_error = comparison_data["Prediction Error"].abs().mean()
    else:
        mean_error = float("nan")

    if pd.isna(mean_error):
        st.warning(
            "Prediction error is unavailable because "
            "there are not enough valid evaluation records."
        )

    elif mean_error <= 5:
        st.success(
            f"Average prediction error: {mean_error:.2f} marks."
        )

    elif mean_error <= 15:
        st.info(
            f"Average prediction error: {mean_error:.2f} marks. "
            "Prediction accuracy may need improvement."
        )

    else:
        st.warning(
            f"Average prediction error: {mean_error:.2f} marks. "
            "The model's predictions have substantial error."
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

    if pd.isna(r2):

        st.warning(
            "Model performance cannot be evaluated "
            "with the available training data."
        )

    elif r2 >= 0.80:

        st.success(
            "🟢 The model shows strong cross-validated "
            "predictive performance on the available data. "
            "Results should still be interpreted cautiously "
            "because the dataset may be small."
        )

    elif r2 >= 0.60:

        st.info(
            "🟡 The model shows moderate cross-validated "
            "predictive performance. More representative "
            "training data may help assess its reliability."
        )

    elif r2 >= 0:

        st.warning(
            "🟠 The model shows limited predictive "
            "performance. Its predictions may have "
            "substantial error."
        )

    else:

        st.error(
            "🔴 The model performs worse than a "
            "mean-prediction baseline on the current "
            "cross-validation evaluation."
        )

    # =========================================================
    # MODEL RELIABILITY SUMMARY
    # =========================================================

    st.subheader("🛡️ Model Reliability Summary")

    st.warning(
        "Model reliability has not been independently "
        "established. Evaluation results depend on the "
        "size and quality of the available training data. "
        "Predictions should be treated as estimates."
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

    st.info(
    "ℹ️ EduIntel generates student performance estimates "
    "using Linear Regression. Prediction reliability depends "
    "on the quality and quantity of available training data. "
    "Results should support, not replace, academic judgment."
)