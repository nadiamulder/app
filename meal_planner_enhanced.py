
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import pandas as pd

# Load the full exchange list
@st.cache_data
def load_exchange_data():
    try:
        df = pd.read_csv("All_Exchange_Categories.csv")
        return df
    except FileNotFoundError:
        st.error("Exchange data file not found.")
        return pd.DataFrame()

exchange_df = load_exchange_data()

st.set_page_config(page_title="Meal Planner", layout="wide")

# --- Load exchange lists dynamically ---
@st.cache_data
def load_exchange_lists():
    categories = ["Starch", "Sugar", "Free", "Vegetables", "Fruit", "Protein", "Milk", "Alcohol"]
    exchange_data = {}
    for cat in categories:
        try:
            df = pd.read_csv(f"./{cat}_Exchange_List.csv")
            exchange_data[cat] = df
        except Exception as e:
            st.warning(f"⚠️ Could not load {cat}_Exchange_List.csv.")
    return exchange_data

@st.cache_data
def load_meal_options():
    meals = ["Breakfast", "Lunch", "Dinner", "Snacks"]
    meal_data = {}
    for meal in meals:
        try:
            df = pd.read_csv(f"./{meal}_Options_Cleaned.csv")
            meal_data[meal] = df
        except Exception as e:
            st.warning(f"⚠️ Could not load {meal}_Options_Cleaned.csv.")
    return meal_data

exchange_data = load_exchange_lists()
meal_data = load_meal_options()

# --- Macronutrient values per gram ---
CAL_PER_G = {"Protein": 4, "Carbs": 4, "Fat": 9}

st.title("🥗 Exchange-Based Meal Planner")

with st.expander("🧍 Step 1: Enter Personal Details", expanded=True):
    col1, col2, col3 = st.columns(3)
    weight = col1.number_input("Weight (kg)", min_value=30.0, value=60.0)
    height = col2.number_input("Height (cm)", min_value=100.0, value=165.0)
    age = col3.number_input("Age", min_value=10, value=30)
    sex = st.selectbox("Sex", ["male", "female"])
    stress = st.slider("Stress Factor", 1.0, 1.5, 1.2)
    activity = st.slider("Activity Factor", 1.2, 2.0, 1.5)

    if sex == "male":
        bmr = 66.5 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
    else:
        bmr = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

    tdee = bmr * stress * activity
    st.success(f"TDEE: {tdee:.0f} kcal/day | {tdee/weight:.1f} kcal/kg")

with st.expander("⚖️ Step 2: Macronutrient Distribution", expanded=True):
    col1, col2, col3 = st.columns(3)
    carb_pct = col1.number_input("Carbs (%)", min_value=0, max_value=100, value=50)
    protein_pct = col2.number_input("Protein (%)", min_value=0, max_value=100, value=20)
    fat_pct = col3.number_input("Fat (%)", min_value=0, max_value=100, value=30)

    if carb_pct + protein_pct + fat_pct != 100:
        st.error("Macronutrient percentages must total 100%.")
    else:
        macros = {
            "Carbs": {"kcal": tdee * (carb_pct / 100)},
            "Protein": {"kcal": tdee * (protein_pct / 100)},
            "Fat": {"kcal": tdee * (fat_pct / 100)},
        }
        for macro in macros:
            macros[macro]["g"] = macros[macro]["kcal"] / CAL_PER_G[macro]
            macros[macro]["g_per_kg"] = macros[macro]["g"] / weight

        macro_df = pd.DataFrame(macros).T
        st.dataframe(macro_df.style.format({"kcal": ".0f", "g": ".1f", "g_per_kg": ".2f"}))

        # Plot
        fig, ax = plt.subplots()
        ax.bar(macro_df.index, macro_df["g"], color=["#99ccff", "#ff9999", "#ffcc99"])
        ax.set_ylabel("Grams")
        ax.set_title("Macronutrient Targets (g)")
        st.pyplot(fig)

with st.expander("📊 Step 3: Exchange Planner", expanded=True):
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

    st.write("Enter number of exchanges for each category:")
    exchange_totals = {}
    macro_totals = {"Carbs": 0, "Protein": 0, "Fat": 0}

    cols = st.columns(4)
    keys = list(exchange_macros.keys())
    for i, cat in enumerate(keys):
        val = cols[i % 4].number_input(f"{cat}", min_value=0, value=0)
        exchange_totals[cat] = val
        macro_totals["Carbs"] += exchange_macros[cat]["Carbs"] * val
        macro_totals["Protein"] += exchange_macros[cat]["Protein"] * val
        macro_totals["Fat"] += exchange_macros[cat]["Fat"] * val

    st.subheader("Exchange Macro Tally")
    exchange_df = pd.DataFrame(macro_totals, index=["From Exchanges"]).T
    st.dataframe(exchange_df.style.format("{:.0f}"))

    # Visual comparison
    if carb_pct + protein_pct + fat_pct == 100:
        target_g = {k: macros[k]["g"] for k in ["Carbs", "Protein", "Fat"]}
        exchange_g = {k: macro_totals[k] for k in ["Carbs", "Protein", "Fat"]}
        compare_df = pd.DataFrame([target_g, exchange_g], index=["Target", "Exchanges"]).T
        st.bar_chart(compare_df)

with st.expander("🍽️ Step 4: Meal and Snack Ideas", expanded=True):
    for meal, df in meal_data.items():
        st.markdown(f"### {meal}")
        for i, row in df.iterrows():
            st.markdown(f"- {row[0]}")
