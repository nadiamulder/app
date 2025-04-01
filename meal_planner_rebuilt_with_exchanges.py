
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

@st.cache_data
def load_mets():
    df = pd.read_csv("Cleaned_METS.csv")
    return df[["description", "MET"]].dropna()

mets_df = load_mets()

st.title("🥗 Meal Planner")

# --- Personal Details ---
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

    st.subheader("➕ TDEE Adjustments")
    preg_add = st.number_input("Pregnancy/Breastfeeding (kcal)", value=0, step=50)
    goal_adjust = st.number_input("Weight Goal Adjustment (kcal)", value=0, step=50)
    custom_adjust = st.number_input("Custom kcal Adjustment", value=0, step=50)

    final_tdee = tdee + preg_add + goal_adjust + custom_adjust
    st.success(f"Final Adjusted TDEE (before METs): {final_tdee:.0f} kcal/day")

# --- METs Section ---
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

# --- Macronutrient Goals ---
with st.expander("2️⃣ Macronutrient Goals (%)", expanded=True):
    col1, col2, col3 = st.columns(3)
    carb_pct = col1.number_input("Carbs %", 0, 100, 50)
    prot_pct = col2.number_input("Protein %", 0, 100, 20)
    fat_pct = col3.number_input("Fat %", 0, 100, 30)

    total_pct = carb_pct + prot_pct + fat_pct
    if total_pct != 100:
        st.warning(f"Macronutrient % total is {total_pct}%. Adjust to 100% for accurate targets.")

    macro_targets = {}
    for macro, pct in zip(["Carbs", "Protein", "Fat"], [carb_pct, prot_pct, fat_pct]):
        kcal = final_tdee * (pct / 100)
        g = kcal / ATWATER[macro]
        g_per_kg = g / calc_weight
        macro_targets[macro] = {"%": pct, "g": g, "g/kg": g_per_kg}

    macro_df = pd.DataFrame(macro_targets).T[["g", "g/kg"]]
    st.dataframe(macro_df.style.format({"g": ".1f", "g/kg": ".2f"}), use_container_width=True)

    fig, ax = plt.subplots(figsize=(4, 4))
    pct_labels = [f"{k} – {v['%']}%" for k, v in macro_targets.items()]
    values = [v["%"] for v in macro_targets.values()]
    colors = ["#A6CEE3", "#FB9A99", "#FDBF6F"]
    ax.pie(values, labels=pct_labels, autopct="%1.0f%%", colors=colors, startangle=90)
    ax.set_title("Macronutrient Distribution")
    ax.axis("equal")
    st.pyplot(fig, use_container_width=True)

# --- Exchange Planner ---
with st.expander("3️⃣ Exchange Planner", expanded=True):
    exchange_macros = {
        "Starch": {"Carbs": 15, "Protein": 3, "Fat": 0},
        "Sugar": {"Carbs": 5, "Protein": 0, "Fat": 0},
        "Vegetables": {"Carbs": 5, "Protein": 2, "Fat": 0},
        "Fruit": {"Carbs": 15, "Protein": 0, "Fat": 0},
        "Protein": {"Carbs": 0, "Protein": 7, "Fat": 3},
        "Milk": {"Carbs": 12, "Protein": 8, "Fat": 5},
        "Fat": {"Carbs": 0, "Protein": 0, "Fat": 5},
        "Alcohol": {"Carbs": 5, "Protein": 0, "Fat": 0},
    }

    st.caption("Enter number of exchanges per food group:")
    exchange_counts = {}
    macro_tally = {"Carbs": 0, "Protein": 0, "Fat": 0}
    cols = st.columns(4)
    for i, cat in enumerate(exchange_macros.keys()):
        count = cols[i % 4].number_input(f"{cat}", min_value=0, value=0)
        exchange_counts[cat] = count
        for macro in ["Carbs", "Protein", "Fat"]:
            macro_tally[macro] += exchange_macros[cat][macro] * count

    st.markdown("#### 📊 Macronutrient Comparison (g)")
    comparison = pd.DataFrame({
        "Target (g)": {k: macro_targets[k]["g"] for k in macro_tally},
        "From Exchanges (g)": macro_tally
    })
    st.dataframe(comparison.style.format("{:.1f}"), use_container_width=True)

    st.bar_chart(comparison)
