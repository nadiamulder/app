
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

# --- Load combined exchange list ---
@st.cache_data
def load_exchange_data():
    try:
        df = pd.read_csv("All_Exchange_Categories.csv")
        return df
    except Exception:
        st.error("❗ Could not load exchange data file.")
        return pd.DataFrame()

exchange_df = load_exchange_data()

st.title("🥗 Exchange-Based Meal Planner")

# --- Personal Details ---
with st.expander("1️⃣ Personal Details", expanded=True):
    col1, col2, col3 = st.columns(3)
    weight = col1.number_input("Actual Weight (kg)", min_value=20.0, value=65.0)
    height = col2.number_input("Height (cm)", min_value=120.0, value=165.0)
    age = col3.number_input("Age", min_value=10, value=30)
    sex = st.selectbox("Sex", ["male", "female"])

    amp = st.selectbox("Amputation Adjustment", list(amputation_factors.keys()))
    amputated_pct = amputation_factors[amp]
    adjusted_weight = weight * (1 + (amputated_pct / 100)) if amputated_pct else weight
    st.caption(f"Adjusted weight used for calculations: **{adjusted_weight:.1f} kg**")

    stress = st.selectbox("Stress Level", list(stress_levels.keys()))
    activity = st.selectbox("Activity Level", list(activity_levels.keys()))

    stress_factor = stress_levels[stress]
    activity_factor = activity_levels[activity]

    if sex == "male":
        bmr = 66.5 + (13.75 * adjusted_weight) + (5.003 * height) - (6.755 * age)
    else:
        bmr = 655.1 + (9.563 * adjusted_weight) + (1.850 * height) - (4.676 * age)

    tdee = bmr * stress_factor * activity_factor
    st.success(f"TDEE: {tdee:.0f} kcal/day | {tdee/adjusted_weight:.1f} kcal/kg")

# --- Macronutrient Distribution ---
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
        kcal = tdee * (pct / 100)
        g = kcal / ATWATER[macro]
        g_per_kg = g / adjusted_weight
        macro_targets[macro] = {"kcal": kcal, "g": g, "g/kg": g_per_kg}

    macro_df = pd.DataFrame(macro_targets).T
    st.dataframe(macro_df.style.format({"kcal": ".0f", "g": ".1f", "g/kg": ".2f"}), use_container_width=True)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.bar(macro_df.index, macro_df["g"], color=["#A6CEE3", "#FB9A99", "#FDBF6F"])
    ax.set_title("Macro Targets (g)")
    ax.set_ylabel("Grams")
    ax.set_ylim(0, max(macro_df["g"]) * 1.2)
    st.pyplot(fig, use_container_width=True)

# --- Exchange Input & Tally ---
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

    st.caption("Enter planned number of exchanges per category:")
    exchange_counts = {}
    macro_tally = {"Carbs": 0, "Protein": 0, "Fat": 0}

    cols = st.columns(4)
    for i, cat in enumerate(exchange_macros.keys()):
        count = cols[i % 4].number_input(f"{cat}", min_value=0, value=0)
        exchange_counts[cat] = count
        for macro in ["Carbs", "Protein", "Fat"]:
            macro_tally[macro] += exchange_macros[cat][macro] * count

    st.markdown("#### 📊 Tally vs Targets")
    comparison = pd.DataFrame({
        "Target (g)": {k: macro_targets[k]["g"] for k in macro_tally},
        "From Exchanges (g)": macro_tally
    })
    st.dataframe(comparison.style.format("{:.1f}"), use_container_width=True)

    st.bar_chart(comparison)

st.caption("This tool is designed to support dietetic calculations. Always confirm clinical decisions independently.")
