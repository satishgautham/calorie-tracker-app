
import streamlit as st
import pandas as pd
import os
import datetime

@st.cache_data
def load_data():
    if not os.path.exists("cleaned_food_data.csv"):
        st.error("🚫 'cleaned_food_data.csv' not found. Please upload it to your GitHub repo root.")
        st.stop()
    return pd.read_csv("cleaned_food_data.csv")

food_df = load_data()

# Initialize session state
if 'food_log' not in st.session_state:
    st.session_state.food_log = []
if 'supplement_log' not in st.session_state:
    st.session_state.supplement_log = []
if 'weight_log' not in st.session_state:
    st.session_state.weight_log = []

st.title("💪 Calorie & Supplement Tracker")
st.markdown("Track your food, supplements, and body stats to hit your fitness goals.")

# Date
selected_date = st.date_input("Select Date", datetime.date.today())

# --- Food Intake Section ---
st.header("🍝 Food Intake")
with st.form("food_form"):
    ingredient = st.selectbox("Select Ingredient", food_df["Ingredient"].unique())
    intake = st.number_input("Quantity Consumed (g)", min_value=1.0, step=1.0)
    submit_food = st.form_submit_button("Add to Log")

    if submit_food:
        row = food_df[food_df["Ingredient"] == ingredient].iloc[0]

        # Convert strings to numeric safely
        protein_per_g = pd.to_numeric(row["Protein_per_g"], errors="coerce")
        carbs_per_g = pd.to_numeric(row["Carbs_per_g"], errors="coerce")
        fats_per_g = pd.to_numeric(row["Fats_per_g"], errors="coerce")
        calories_per_portion = pd.to_numeric(row["Calories"], errors="coerce")
        intake_portion = pd.to_numeric(row["Intake_g"], errors="coerce")

        if pd.isnull(protein_per_g) or pd.isnull(calories_per_portion) or pd.isnull(intake_portion):
            st.warning("⚠️ Some nutrition values are invalid. Please check the CSV for missing or non-numeric entries.")
            st.stop()

        # Calculate totals
        protein = protein_per_g * intake
        carbs = carbs_per_g * intake
        fats = fats_per_g * intake
        calories = calories_per_portion * (intake / intake_portion)

        st.session_state.food_log.append({
            "Date": selected_date,
            "Ingredient": ingredient,
            "Qty (g)": intake,
            "Protein": protein,
            "Carbs": carbs,
            "Fats": fats,
            "Calories": calories
        })

# Display food log
log_df = pd.DataFrame(st.session_state.food_log)
if not log_df.empty:
    st.subheader("Today's Food Log")
    st.dataframe(log_df[log_df['Date'] == selected_date])
    daily = log_df[log_df['Date'] == selected_date].sum(numeric_only=True)
    st.metric("Total Calories", f"{daily['Calories']:.0f} kcal")
    st.metric("Protein", f"{daily['Protein']:.1f} g")
    st.metric("Carbs", f"{daily['Carbs']:.1f} g")
    st.metric("Fats", f"{daily['Fats']:.1f} g")

# --- Supplement Intake ---
st.header(":pill: Supplement Intake")
with st.form("supplement_form"):
    supp_name = st.text_input("Supplement Name")
    supp_dose = st.text_input("Dosage / Notes")
    submit_supp = st.form_submit_button("Add Supplement")

    if submit_supp and supp_name:
        st.session_state.supplement_log.append({
            "Date": selected_date,
            "Supplement": supp_name,
            "Notes": supp_dose
        })

if st.session_state.supplement_log:
    st.subheader("Today's Supplements")
    supp_df = pd.DataFrame(st.session_state.supplement_log)
    st.dataframe(supp_df[supp_df['Date'] == selected_date])

# --- Weight Logging ---
st.header(":weight_lifter: Weight Tracking")
with st.form("weight_form"):
    weight = st.number_input("Your Weight (kg)", min_value=0.0, step=0.1)
    submit_weight = st.form_submit_button("Log Weight")

    if submit_weight:
        st.session_state.weight_log.append({
            "Date": selected_date,
            "Weight (kg)": weight
        })

if st.session_state.weight_log:
    st.subheader("Weight History")
    weight_df = pd.DataFrame(st.session_state.weight_log)
    st.line_chart(weight_df.set_index("Date")['Weight (kg)'])
