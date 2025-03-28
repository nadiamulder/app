
import streamlit as st
import pandas as pd

# --- Load exchange lists dynamically ---
@st.cache_data
def load_exchange_lists():
    categories = ["Starch", "Sugar", "Free", "Vegetables", "Fruit", "Protein", "Milk", "Alcohol"]
    exchange_data = {}
    for cat in categories:
        try:
            df = pd.read_csv(f"{cat}_Exchange_List.csv")
            exchange_data[cat] = df
        except Exception as e:
            st.warning(f"Could not load {cat} data.")
    return exchange_data

@st.cache_data
def load_meal_options():
    meals = ["Breakfast", "Lunch", "Dinner", "Snacks"]
    meal_data = {}
    for meal in meals:
        try:
            df = pd.read_csv(f"{meal}_Options_Cleaned.csv")
            meal_data[meal] = df
        except Exception as e:
            st.warning(f"Could not load {meal} options.")
    return meal_data

exchange_data = load_exchange_lists()
meal_data = load_meal_options()

# --- Macronutrient values per gram ---
CAL_PER_G = {"Protein": 4, "Carbs": 4, "Fat": 9}

# --- UI ---
st.title("Advanced Exchange-Based Meal Planner")

st.header("Step 1: Enter Personal Details")
weight = st.number_input("Weight (kg)", min_value=30.0, value=60.0)
height = st.number_input("Height (cm)", min_value=100.0, value=165.0)
age = st.number_input("Age", min_value=10, value=30)
sex = st.selectbox("Sex", ["male", "female"])
stress = st.slider("Stress Factor", 1.0, 1.5, 1.2)
activity = st.slider("Activity Factor", 1.2, 2.0, 1.5)

if sex == "male":
    bmr = 66.5 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
else:
    bmr = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

tdee = bmr * stress * activity
st.success(f"Total Daily Energy Expenditure (TDEE): {tdee:.0f} kcal")
st.write(f"Energy per kg: {tdee / weight:.1f} kcal/kg")

st.header("Step 2: Macronutrient Distribution")
cols = st.columns(3)
carb_pct = cols[0].number_input("Carbs (%)", min_value=0, max_value=100, value=50)
protein_pct = cols[1].number_input("Protein (%)", min_value=0, max_value=100, value=20)
fat_pct = cols[2].number_input("Fat (%)", min_value=0, max_value=100, value=30)

if carb_pct + protein_pct + fat_pct != 100:
    st.error("Macronutrient percentages must add up to 100%.")
else:
    # Calculate grams and g/kg
    macros = {
        "Carbs": {
            "kcal": tdee * (carb_pct / 100),
        },
        "Protein": {
            "kcal": tdee * (protein_pct / 100),
        },
        "Fat": {
            "kcal": tdee * (fat_pct / 100),
        },
    }

    for macro in macros:
        macros[macro]["g"] = macros[macro]["kcal"] / CAL_PER_G[macro]
        macros[macro]["g_per_kg"] = macros[macro]["g"] / weight

    st.subheader("Macronutrient Targets")
    st.write(pd.DataFrame(macros).T.style.format({"kcal": ".0f", "g": ".1f", "g_per_kg": ".2f"}))

st.header("Step 3: Exchange Planner")
st.markdown("Enter the number of exchanges you plan to use from each category.")

exchange_totals = {}
macro_totals = {"Carbs": 0, "Protein": 0, "Fat": 0}

# Reference macro values per exchange (can be refined)
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

st.write("### Exchange Input")
for category in exchange_macros.keys():
    exchange_totals[category] = st.number_input(f"{category} Exchanges", min_value=0, value=0)

for cat, count in exchange_totals.items():
    if cat in exchange_macros:
        macro_totals["Carbs"] += exchange_macros[cat]["Carbs"] * count
        macro_totals["Protein"] += exchange_macros[cat]["Protein"] * count
        macro_totals["Fat"] += exchange_macros[cat]["Fat"] * count

# --- Display Tally ---
st.subheader("Macronutrient Tally from Exchanges")
macro_df = pd.DataFrame(macro_totals, index=["From Exchanges"]).T
st.write(macro_df)

# --- Meal Suggestions ---
st.header("Step 4: Meal Suggestions")
for meal, df in load_meal_options().items():
    st.markdown(f"### {meal}")
    for i, row in df.iterrows():
        st.markdown(f"- {row[0]}")

st.success("Meal plan generated. You can now manually adjust exchanges to better meet your macro targets if needed.")
