
# --- Macronutrient Goals (visibly synced, safely handled) ---
with st.expander("2️⃣ Macronutrient Goals", expanded=True):
    st.markdown("Enter macronutrient targets using **%** or **g/kg**. The calculated values will display below.")

    macro_inputs = {}
    columns = st.columns(3)

    for idx, macro in enumerate(["Carbs", "Protein", "Fat"]):
        with columns[idx]:
            default_pct = {"Carbs": 50.0, "Protein": 20.0, "Fat": 30.0}[macro]
            atwater = ATWATER[macro]

            st.markdown(f"**{macro}**")
            input_pct = st.number_input(f"{macro} %", min_value=0.0, max_value=100.0, value=default_pct, step=1.0, key=f"{macro}_pct")
            input_gkg = st.number_input(f"{macro} g/kg", min_value=0.0, value=(default_pct / 100 * final_tdee / atwater / calc_weight), step=0.1, key=f"{macro}_gkg")

            # Show calculated values from both inputs
            grams_from_pct = (input_pct / 100) * final_tdee / atwater
            gkg_from_pct = grams_from_pct / calc_weight

            grams_from_gkg = input_gkg * calc_weight
            pct_from_gkg = (grams_from_gkg * atwater) / final_tdee * 100

            st.caption(f"→ From %: {grams_from_pct:.1f} g ({gkg_from_pct:.2f} g/kg)")
            st.caption(f"→ From g/kg: {grams_from_gkg:.1f} g ({pct_from_gkg:.1f}%)")

            macro_inputs[macro] = {
                "% (entered)": input_pct,
                "g from %": grams_from_pct,
                "g/kg (entered)": input_gkg,
                "kcal from %": grams_from_pct * atwater
            }

    macro_df = pd.DataFrame(macro_inputs).T[["% (entered)", "g from %", "g/kg (entered)", "kcal from %"]]
    st.dataframe(macro_df.style.format({"% (entered)": ".1f", "g from %": ".1f", "g/kg (entered)": ".2f", "kcal from %": ".0f"}), use_container_width=True)
