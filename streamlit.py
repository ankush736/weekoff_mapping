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

        # Validate columns
        expected_cols = ["empcode", "week off"]
        df.columns = df.columns.str.lower()

        if not all(col in df.columns for col in expected_cols):
            st.error("File must contain 'empcode' and 'week off' columns")
            st.stop()

        st.write("### 👀 Preview Input Data")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Error reading file: {e}")

# -------------------------
# Options
# -------------------------
if df is not None:

    col1, col2, col3 = st.columns(3)

    with col1:
        week_day = st.selectbox(
            "Select Week Off Day",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )

    with col2:
        from_month = st.date_input("From Date")

    with col3:
        to_month = st.date_input("To Date")

    # -------------------------
    # Generate Mapping
    # -------------------------
    if st.button("⚙️ Generate Mapping"):

        if from_month > to_month:
            st.error("From Date cannot be after To Date")
            st.stop()

        # Map weekday to number
        week_day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        target_day = week_day_map[week_day]

        result = []

        current_date = from_month

        while current_date <= to_month:
            if current_date.weekday() == target_day:
                for emp in df["empcode"]:
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
