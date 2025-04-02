
# --- Macronutrient Goals (% and g/kg editable + synced) ---
with st.expander("2️⃣ Macronutrient Goals", expanded=True):
    st.markdown("You can adjust macronutrients by percentage **or** g/kg. They will stay in sync.")

    macro_inputs = {}
    columns = st.columns(3)

    for idx, macro in enumerate(["Carbs", "Protein", "Fat"]):
        with columns[idx]:
            default_pct = {"Carbs": 50.0, "Protein": 20.0, "Fat": 30.0}[macro]
            atwater = ATWATER[macro]

            # Get % from session or default
            input_pct = st.number_input(f"{macro} %", min_value=0.0, max_value=100.0, value=default_pct, step=1.0, key=f"{macro}_pct")
            grams = (input_pct / 100) * final_tdee / atwater
            g_per_kg_calc = grams / calc_weight

            # Show g/kg with the current % calculation
            gkg_input = st.number_input(f"{macro} g/kg", min_value=0.0, value=g_per_kg_calc, step=0.1, key=f"{macro}_gkg")

            # Recalculate if user changed g/kg (compare to calc'd version)
            if abs(gkg_input - g_per_kg_calc) > 0.01:
                grams = gkg_input * calc_weight
                kcal = grams * atwater
                input_pct = (kcal / final_tdee) * 100

            macro_inputs[macro] = {
                "%": input_pct,
                "g": grams,
                "g/kg": grams / calc_weight,
                "kcal": grams * atwater
            }

    # Display table
    macro_df = pd.DataFrame(macro_inputs).T[["%", "g", "g/kg", "kcal"]]
    st.dataframe(macro_df.style.format({"%": ".1f", "g": ".1f", "g/kg": ".2f", "kcal": ".0f"}), use_container_width=True)
