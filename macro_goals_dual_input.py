
# --- Macronutrient Goals (% and g/kg editable) ---
with st.expander("2️⃣ Macronutrient Goals", expanded=True):
    st.markdown("You can adjust macronutrients by percentage **or** g/kg. The other will update automatically.")

    macro_inputs = {}
    columns = st.columns(3)
    for idx, macro in enumerate(["Carbs", "Protein", "Fat"]):
        with columns[idx]:
            default_pct = {"Carbs": 50, "Protein": 20, "Fat": 30}[macro]
            atwater = ATWATER[macro]
            prev_pct = st.session_state.get(f"{macro}_pct", default_pct)

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
                st.session_state[f"{macro}_pct"] = round(pct, 1)

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
