
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Meal Planner", layout="wide")

# --- Constants ---
ATWATER = {"Carbs": 4.0, "Protein": 4.0, "Fat": 9.0}
stress_levels = {
    "None (1.0)": 1.0,
    "Mild illness, minor surgery (1.2)": 1.2,
    "Moderate infection or surgery (1.3)": 1.3,
    "Major trauma, burns (1.4)": 1.4,
    "Severe stress (1.5)": 1.5
}
activity_levels = {
    "Sedentary (1.2)": 1.2,
    "Light activity (1.375)": 1.375,
    "Moderate activity (1.55)": 1.55,
    "Very active (1.725)": 1.725,
    "Extra active (1.9)": 1.9
}
amputation_factors = {
    "None": 0.0,
    "Hand or Foot": 0.8,
    "Below-knee amputation": 5.9,
    "Above-knee amputation": 11.0,
    "Entire leg": 16.0,
    "Lower arm and hand": 2.3,
    "Entire arm": 5.0
}

# --- Load Cleaned METs Data ---
@st.cache_data
def load_mets():
    df = pd.read_csv("Cleaned_METS.csv")
    return df[["description", "MET"]].dropna()

mets_df = load_mets()

st.title("🥗 Meal Planner")

# --- Consolidated Personal Details ---
with st.expander("1️⃣ Personal Details", expanded=True):
    col1, col2 = st.columns(2)
    actual_weight = col1.number_input("Actual Weight (kg)", min_value=20.0, value=65.0)
    calc_weight = col2.number_input("Weight for Calculations (kg)", min_value=20.0, value=actual_weight)

    height = st.number_input("Height (cm)", min_value=120.0, value=165.0)
    age = st.number_input("Age", min_value=10, value=30)
    sex = st.selectbox("Sex", ["male", "female"])
    amp = st.selectbox("Amputation Adjustment", list(amputation_factors.keys()))
    stress = st.selectbox("Stress Level", list(stress_levels.keys()))
    activity = st.selectbox("Activity Level", list(activity_levels.keys()))

    amputated_pct = amputation_factors[amp]
    adjusted_weight = calc_weight * (1 + (amputated_pct / 100)) if amputated_pct else calc_weight

    if sex == "male":
        bmr = 66.5 + (13.75 * adjusted_weight) + (5.003 * height) - (6.755 * age)
    else:
        bmr = 655.1 + (9.563 * adjusted_weight) + (1.850 * height) - (4.676 * age)
    tdee = bmr * stress_levels[stress] * activity_levels[activity]

    st.markdown(f"**BMR:** {bmr:.0f} kcal/day")
    st.markdown(f"**Base TDEE:** {tdee:.0f} kcal/day")

    # Adjustments
    st.subheader("➕ TDEE Adjustments")
    preg_add = st.number_input("Pregnancy/Breastfeeding (kcal)", value=0, step=50)
    goal_adjust = st.number_input("Weight Goal Adjustment (kcal)", value=0, step=50)
    custom_adjust = st.number_input("Custom kcal Adjustment", value=0, step=50)

    final_tdee = tdee + preg_add + goal_adjust + custom_adjust
    st.success(f"Final Adjusted TDEE (before METs): {final_tdee:.0f} kcal/day")

# --- Optional METs Calculator ---
with st.expander("🏃 METs Calculator (for athletes)"):
    selected_activity = st.selectbox("Choose activity", ["None"] + mets_df["description"].tolist())
    duration_mins = st.number_input("Duration (minutes)", min_value=0, value=0)

    mets_kcal = 0
    if selected_activity != "None" and duration_mins > 0:
        met_value = mets_df[mets_df["description"] == selected_activity]["MET"].values[0]
        mets_kcal = (met_value * calc_weight * (duration_mins / 60))
        st.info(f"Estimated METs kcal burned: {mets_kcal:.0f} kcal")

    final_tdee += mets_kcal
    st.success(f"Final TDEE (including METs): {final_tdee:.0f} kcal/day")

# You can re-insert the macro breakdown and exchange planner sections below using final_tdee and calc_weight
