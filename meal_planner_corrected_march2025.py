
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

st.title("🥗 Meal Planner")


# --- Updated Personal Details Section with Gender Diversity ---
with st.expander("1️⃣ Personal Details", expanded=True):
    col1, col2, col3 = st.columns(3)
    weight = col1.number_input("Actual Weight (kg)", min_value=20.0, value=65.0, key="weight_input")
    height = col2.number_input("Height (cm)", min_value=120.0, value=165.0, key="height_input")
    age = col3.number_input("Age", min_value=10, value=30, key="age_input")

    sex = st.selectbox("Sex (biological)", ["Male", "Female", "Intersex"], key="sex_select")
    gender = st.selectbox("Gender Identity", [
        "Cisgender",
        "Trans man (on HRT)",
        "Trans woman (on HRT)",
        "Trans man (no HRT)",
        "Trans woman (no HRT)",
        "Other"
    ], key="gender_select")

    amp = st.selectbox("Amputation Adjustment", list(amputation_factors.keys()), key="amp_select")
    amputated_pct = amputation_factors[amp]
    adjusted_weight = weight * (1 + (amputated_pct / 100)) if amputated_pct else weight
    st.caption(f"Adjusted weight used for calculations: **{adjusted_weight:.1f} kg**")

    # BMI and Ideal Body Fat % Ranges
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    st.metric("BMI", f"{bmi:.1f}")

    # Display ideal body fat % range
    if sex == "Male":
        if 20 <= age <= 39:
            ideal_bf_range = "8–19%"
        elif 40 <= age <= 59:
            ideal_bf_range = "11–21%"
        else:
            ideal_bf_range = "13–24%"
    elif sex == "Female":
        if 20 <= age <= 39:
            ideal_bf_range = "21–32%"
        elif 40 <= age <= 59:
            ideal_bf_range = "23–33%"
        else:
            ideal_bf_range = "24–35%"
    else:
        ideal_bf_range = "No standard reference for intersex individuals"

    body_fat = st.number_input("Optional: Body Fat % (if measured)", min_value=0.0, max_value=100.0, value=0.0, key="bf_input")
    st.write(f"Ideal Body Fat % Range for age/sex: **{ideal_bf_range}**")
    if body_fat:
        st.write(f"Entered Body Fat %: **{body_fat:.1f}%**")

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

# --- Step 2: Macronutrient Distribution ---
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

# --- Step 3: Exchange Planner ---
with st.expander("3️⃣ Exchange Inputs & Macro Tally", expanded=True):
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
