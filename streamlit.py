import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Week Off Mapper", layout="wide")

st.title("📅 Week Off Mapping Generator")

# -------------------------
# Reset functionality
# -------------------------
if st.button("🔄 Reset"):
    st.session_state.clear()
    st.rerun()

# -------------------------
# File Upload
# -------------------------
uploaded_file = st.file_uploader(
    "Upload file (CSV / XLS / XLSX)",
    type=["csv", "xlsx", "xls"]
)

df = None

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File uploaded successfully!")

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()

        expected_cols = ["empcode", "week off"]

        if not all(col in df.columns for col in expected_cols):
            st.error("File must contain 'empcode' and 'week off' columns")
            st.stop()

        st.write("### 👀 Preview Input Data")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Error reading file: {e}")

# -------------------------
# Date Selection
# -------------------------
if df is not None:

    col1, col2 = st.columns(2)

    with col1:
        from_date = st.date_input("From Date")

    with col2:
        to_date = st.date_input("To Date")

    # -------------------------
    # Generate Mapping
    # -------------------------
    if st.button("⚙️ Generate Mapping"):

        if from_date > to_date:
            st.error("From Date cannot be after To Date")
            st.stop()

        # Weekday mapping
        week_day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        result = []

        # Clean week off values
        df["week off"] = df["week off"].str.lower().str.strip()

        for _, row in df.iterrows():
            emp = row["empcode"]
            emp_weekoff = row["week off"]

            if emp_weekoff not in week_day_map:
                st.warning(f"Invalid week off '{emp_weekoff}' for emp {emp}")
                continue

            target_day = week_day_map[emp_weekoff]

            current_date = from_date

            while current_date <= to_date:
                if current_date.weekday() == target_day:
                    result.append({
                        "shift name": "WeekOff",
                        "from date": current_date,
                        "to date": current_date,
                        "empcode": emp
                    })
                current_date += timedelta(days=1)

        result_df = pd.DataFrame(result)

        if result_df.empty:
            st.warning("No data generated. Check your inputs.")
        else:
            st.session_state["result"] = result_df

# -------------------------
# Preview & Download
# -------------------------
if "result" in st.session_state:

    st.write("### 📊 Generated Mapping Preview")
    st.dataframe(st.session_state["result"])

    csv = st.session_state["result"].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="weekoff_mapping.csv",
        mime="text/csv"
    )
