
import random
import streamlit as st

# --- Food Lists ---
starch_foods = [
    ("Brown / wholewheat bread", "1 slice (42 g)"),
    ("Brown / wholewheat rolls", "½ roll"),
    ("Pita bread (15cm diameter)", "½ pita"),
    ("Wrap", "½ wrap"),
    ("Crackerbread", "3 pieces"),
    ("Corn thins", "3 pieces"),
    ("Cooked oats", "½ cup"),
    ("Granola (low sugar)", "¼ cup"),
    ("Cooked rice", "½ cup"),
    ("Cooked pasta", "½ cup")
]

protein_foods = [
    ("Egg", "1 egg"),
    ("Tofu", "½ cup"),
    ("Chicken breast", "30g"),
    ("Low fat cottage cheese", "¼ cup"),
    ("Edamame", "½ cup"),
    ("Lentils", "½ cup cooked"),
    ("Fish", "30g"),
    ("Lean beef", "30g"),
    ("Chickpeas", "½ cup cooked"),
    ("Greek yogurt (low fat)", "¾ cup")
]

fat_foods = [
    ("Avocado", "¼ avocado"),
    ("Nuts", "1 tbsp"),
    ("Nut butter", "2 tsp"),
    ("Olive oil", "1 tsp"),
    ("Cheese", "20g"),
    ("Lite cream cheese", "30g"),
    ("Seeds", "1 tbsp"),
    ("Pesto", "1 tbsp"),
    ("Lite mayo", "1 tbsp"),
    ("Tahini", "1 tbsp")
]

dairy_foods = [
    ("Low fat milk", "1 cup"),
    ("Low fat yogurt", "¾ cup"),
    ("Soy milk (fortified)", "1 cup"),
    ("Almond milk (fortified)", "1 cup"),
    ("Lactose-free milk", "1 cup"),
    ("Skim milk", "1 cup"),
    ("Low fat cheese", "30g"),
    ("Kefir", "¾ cup"),
    ("Buttermilk", "1 cup"),
    ("Lite cream cheese", "30g")
]

fruit_foods = [
    ("Apple", "1 small"),
    ("Banana", "½ medium"),
    ("Blueberries", "100g"),
    ("Strawberries", "10"),
    ("Mango", "½ small"),
    ("Grapes", "8-12"),
    ("Dates", "2"),
    ("Raisins", "2 tbsp"),
    ("Dried mango", "25g"),
    ("Orange", "1 medium")
]

veg_foods = [
    ("Carrots", "½ cup cooked"),
    ("Spinach", "1 cup raw"),
    ("Broccoli", "½ cup steamed"),
    ("Tomato", "1 cup"),
    ("Peppers", "½ cup"),
    ("Zucchini", "½ cup cooked"),
    ("Beetroot", "½ cup"),
    ("Cucumber", "1 cup sliced"),
    ("Rocket", "1 cup"),
    ("Baby marrow", "½ cup")
]

# --- App UI ---
st.title("Exchange-Based Meal Plan Generator")

st.subheader("Personal Details")
age = st.number_input("Age", value=35)
weight_kg = st.number_input("Weight (kg)", value=60)
height_cm = st.number_input("Height (cm)", value=170)
sex = st.selectbox("Sex", ["male", "female"])
stress_factor = st.slider("Stress Factor", 1.0, 1.5, 1.2)
activity_factor = st.slider("Activity Factor", 1.2, 2.0, 1.5)

st.subheader("Enter Your Daily Exchange Goals")
starch_ex = st.number_input("Starch Exchanges", min_value=0, value=7)
protein_ex = st.number_input("Protein Exchanges", min_value=0, value=5)
fat_ex = st.number_input("Fat Exchanges", min_value=0, value=8)
dairy_ex = st.number_input("Dairy Exchanges", min_value=0, value=2)
fruit_ex = st.number_input("Fruit Exchanges", min_value=0, value=2)
veg_ex = st.number_input("Vegetable Exchanges", min_value=0, value=4)

if st.button("Generate Meal Plan"):
    # --- Energy Needs ---
    if sex == "male":
        bmr = 66.5 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.755 * age)
    else:
        bmr = 655.1 + (9.563 * weight_kg) + (1.850 * height_cm) - (4.676 * age)
    tdee = bmr * stress_factor * activity_factor
    protein_g = 1.5 * weight_kg
    fat_g = 0.9 * weight_kg
    carbs_g = (tdee - (protein_g * 4 + fat_g * 9)) / 4

    st.subheader("Estimated Nutrition Needs")
    st.write(f"TDEE: {tdee:.0f} kcal/day")
    st.write(f"Protein: {protein_g:.0f} g | Fat: {fat_g:.0f} g | Carbs: {carbs_g:.0f} g")

    st.subheader("Meal Plan Suggestions")

    def show_exchange(name, count, food_list):
        st.markdown(f"**{name} Exchanges ({count})**")
        selected = random.sample(food_list, min(count, len(food_list)))
        for i, (food, portion) in enumerate(selected, 1):
            st.write(f"{i}. {food} — {portion}")

    show_exchange("Starch", starch_ex, starch_foods)
    show_exchange("Protein", protein_ex, protein_foods)
    show_exchange("Fat", fat_ex, fat_foods)
    show_exchange("Dairy", dairy_ex, dairy_foods)
    show_exchange("Fruit", fruit_ex, fruit_foods)
    show_exchange("Vegetables", veg_ex, veg_foods)

    st.success("Your meal plan is ready!")
