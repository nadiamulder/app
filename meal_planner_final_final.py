
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Meal Planner", layout="wide")

# --- Constants ---
ATWATER = {"Carbs": 4.0, "Protein": 4.0, "Fat": 9.0}
stress_levels = {"None (1.0)": 1.0, "Mild illness (1.2)": 1.2, "Moderate stress (1.3)": 1.3, "Major trauma (1.4)": 1.4, "Severe stress (1.5)": 1.5}
activity_levels = {"Sedentary (1.2)": 1.2, "Light (1.375)": 1.375, "Moderate (1.55)": 1.55, "Very active (1.725)": 1.725, "Extra active (1.9)": 1.9}
amputation_factors = {"None": 0.0, "Hand/Foot": 0.8, "Below-knee": 5.9, "Above-knee": 11.0, "Leg": 16.0, "Lower arm/hand": 2.3, "Arm": 5.0}

# Load exchanges
starch_df = pd.read_csv("Starch_Exchanges.csv")
sugar_df = pd.read_csv("Sugar_Exchanges.csv")
free_df = pd.read_csv("Free_Exchanges.csv")
vegetables_df = pd.read_csv("Vegetables_Exchanges.csv")
fruit_df = pd.read_csv("Fruit_Exchanges.csv")
protein_df = pd.read_csv("Protein_Exchanges.csv")
milk_df = pd.read_csv("Milk_Exchanges.csv")
alcohol_df = pd.read_csv("Alcohol_Exchanges.csv")
fat_df = pd.read_csv("Fats_Exchanges.csv")

@st.cache_data
def load_mets():
    df = pd.read_csv("Cleaned_METS.csv")
    return df[["description", "MET"]].dropna()

mets_df = load_mets()

# --- Personal Details ---
with st.expander("1️⃣ Personal Details", expanded=True):
    col1, col2 = st.columns(2)
    actual_weight = col1.number_input("Actual Weight (kg)", 20.0, 300.0, 65.0)
    calc_weight = col2.number_input("Weight for Calculations (kg)", 20.0, 300.0, actual_weight)
    height = st.number_input("Height (cm)", 120.0, 250.0, 165.0)
    age = st.number_input("Age", 10, 120, 30)
    sex = st.selectbox("Sex", ["male", "female"])
    amp = st.selectbox("Amputation Adjustment", list(amputation_factors.keys()))
    stress = st.selectbox("Stress Level", list(stress_levels.keys()))
    activity = st.selectbox("Activity Level", list(activity_levels.keys()))

    amputated_pct = amputation_factors[amp]
    adjusted_weight = calc_weight * (1 + (amputated_pct / 100)) if amputated_pct else calc_weight

    bmr = 66.5 + (13.75 * adjusted_weight) + (5.003 * height) - (6.755 * age) if sex == "male" else           655.1 + (9.563 * adjusted_weight) + (1.850 * height) - (4.676 * age)
    tdee = bmr * stress_levels[stress] * activity_levels[activity]

    preg_add = st.number_input("Pregnancy/Breastfeeding kcal", value=0, step=50)
    goal_add = st.number_input("Weight Goal Adjustment kcal", value=0, step=50)
    custom_add = st.number_input("Custom kcal Adjustment", value=0, step=50)
    final_tdee = tdee + preg_add + goal_add + custom_add

    st.markdown(f"**BMR:** {bmr:.0f} kcal/day")
    st.markdown(f"**Adjusted TDEE:** {final_tdee:.0f} kcal/day")

# --- METs Calculator ---
with st.expander("🏃 METs Calculator"):
    activity = st.selectbox("Activity", ["None"] + mets_df["description"].tolist())
    duration = st.number_input("Duration (minutes)", 0, 300, 0)
    mets_kcal = 0
    if activity != "None" and duration > 0:
        met_val = mets_df[mets_df["description"] == activity]["MET"].values[0]
        mets_kcal = met_val * calc_weight * (duration / 60)
        final_tdee += mets_kcal
        st.info(f"Calories burned: {mets_kcal:.0f} kcal")
    st.success(f"Final TDEE including METs: {final_tdee:.0f} kcal/day")



# --- Macronutrient Goals (% and g/kg editable) ---
with st.expander("2️⃣ Macronutrient Goals", expanded=True):
    st.markdown("You can adjust macronutrients by percentage **or** g/kg. The other will update automatically.")

    macro_inputs = {}
    columns = st.columns(3)
    for idx, macro in enumerate(["Carbs", "Protein", "Fat"]):
        with columns[idx]:
            default_pct = {"Carbs": 50, "Protein": 20, "Fat": 30}[macro]
            atwater = ATWATER[macro]
            prev_pct = float(st.session_state.get(f"{macro}_pct", default_pct))

            pct = st.number_input(f"{macro} %", min_value=0.0, max_value=100.0, value=prev_pct, step=1.0, key=f"{macro}_pct")
            grams = (pct / 100) * final_tdee / atwater
            g_per_kg = grams / calc_weight

            gkg = st.number_input(f"{macro} g/kg", min_value=0.0, value=g_per_kg, step=0.1, key=f"{macro}_gkg")

            # If g/kg was changed, recalculate grams, kcal, and %
            gkg_changed = gkg != g_per_kg
            if gkg_changed:
                grams = gkg * calc_weight
                kcal = grams * atwater
                pct = (kcal / final_tdee) * 100

                # Update values in session state
                # session_state update removed to prevent overwrite conflict

            macro_inputs[macro] = {
                "g": grams,
                "g/kg": gkg,
                "%": pct,
                "kcal": grams * atwater
            }

    # Display final macros
    macro_df = pd.DataFrame(macro_inputs).T[["%", "g", "g/kg", "kcal"]]
    st.dataframe(macro_df.style.format({"%": ".1f", "g": ".1f", "g/kg": ".2f", "kcal": ".0f"}), use_container_width=True)

    fig, ax = plt.subplots(figsize=(4, 4))
    pct_labels = [f"{k} – {v['%']:.1f}%" for k, v in macro_inputs.items()]
    values = [v["%"] for v in macro_inputs.values()]
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
    exchange_counts, macro_tally = {}, {"Carbs": 0, "Protein": 0, "Fat": 0}
    cols = st.columns(4)
    for i, cat in enumerate(exchange_macros):
        count = cols[i % 4].number_input(cat, 0, 10, 0)
        exchange_counts[cat] = count
        for macro in macro_tally:
            macro_tally[macro] += exchange_macros[cat][macro] * count

    st.markdown("#### 📊 Macronutrient Comparison (g)")
    target_macro_g = {k: v["g"] for k, v in macro_inputs.items()}
    comparison = pd.DataFrame({"Target (g)": target_macro_g, "From Exchanges (g)": macro_tally})
    st.dataframe(comparison.style.format("{:.1f}"))

# --- Meal Plan Builder ---
with st.expander("4️⃣ Meal Plan Builder", expanded=True):
    st.subheader("🍽️ Build Daily Meal Plan")
    meals = ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Supper", "Treat"]
    exchange_data = {
        "Starch": starch_df,
        "Protein": protein_df,
        "Fat": fat_df,
        "Fruit": fruit_df,
        "Vegetables": vegetables_df,
        "Milk": milk_df,
        "Sugar": sugar_df,
        "Free": free_df,
        "Alcohol": alcohol_df
    }
    meal_plan = {}
    for meal in meals:
        st.markdown(f"### {meal}")
        meal_contents = {}
        cols = st.columns(3)
        for i, (cat, df) in enumerate(exchange_data.items()):
            with cols[i % 3]:
                count = st.number_input(f"{meal} – {cat}", 0, 5, 0, key=f"{meal}_{cat}")
                if count > 0:
                    items = df["Food Item"].dropna().sample(min(len(df), 10)).tolist()
                    choices = st.multiselect(f"{cat} options", items, max_selections=count, key=f"{meal}_{cat}_select")
                    meal_contents[cat] = choices
        meal_plan[meal] = meal_contents
    st.markdown("## 🧾 Daily Summary")
    for meal, details in meal_plan.items():
        st.markdown(f"**{meal}**")
        for cat, items in details.items():
            if items:
                st.write(f"- {cat}: {', '.join(items)}")
