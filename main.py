import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import os

API_URL = os.environ.get("API_URL", "http://localhost:5000")

st.set_page_config(
    page_title="Campus Dining Menu Scraper",
    page_icon="🍽️",
    layout="wide",
)

with open("src/.streamlit/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Campus Dining Menu Scraper")


@st.cache_data(ttl=300)
def fetch_schools():
    resp = requests.get(f"{API_URL}/api/schools", timeout=10)
    resp.raise_for_status()
    return resp.json()


try:
    schools_data = fetch_schools()
except Exception as e:
    st.error(f"Could not reach backend at {API_URL}. Is the Flask server running?\n\n{e}", icon="🚨")
    st.stop()

# {key: {name, halls: [{short_key, hall_slug}]}}
schools_map = {s["key"]: s for s in schools_data}
school_keys = sorted(schools_map.keys(), key=lambda k: ("" if k == "UH" else schools_map[k]["name"]))

diningMenuOptions = ["Breakfast", "Lunch", "Dinner", "Everyday"]

col0, col1, col2, col3 = st.columns(4)

with col0:
    selectedSchool = st.selectbox(
        "Select School",
        options=school_keys,
        format_func=lambda k: f"{k} — {schools_map[k]['name']}",
        index=0,
    )

hall_list = schools_map[selectedSchool]["halls"]  # [{short_key, hall_slug}]
hall_keys = [h["short_key"] for h in hall_list]
hall_label = {h["short_key"]: h["short_key"].replace("-", " ").title() for h in hall_list}

with col1:
    selectedHall = st.selectbox(
        "Select Dining Hall",
        options=hall_keys,
        format_func=lambda k: hall_label[k],
        index=0,
    )

with col2:
    diningMenuData = st.selectbox(
        "Select Menu Type",
        options=diningMenuOptions,
        index=1,
    )

with col3:
    diningDate = st.date_input(
        "Select Date",
        value=datetime.today(),
        min_value=datetime.today() - timedelta(days=30),
        max_value=datetime.today(),
    )

if st.button("Get Menu"):
    params = {
        "school": selectedSchool,
        "hall": selectedHall,
        "meal": diningMenuData.lower(),
        "date": diningDate.strftime("%Y-%m-%d"),
    }

    with st.spinner("Fetching menu..."):
        try:
            resp = requests.get(f"{API_URL}/api/menu", params=params, timeout=120)
            if resp.status_code == 404:
                st.warning(resp.json().get("error", "Not found."), icon="⚠️")
                st.stop()
            resp.raise_for_status()
            menu_json = resp.json()
        except requests.exceptions.Timeout:
            st.error("Request timed out — the scraper may still be running. Try again in a moment.", icon="🚨")
            st.stop()
        except Exception as e:
            st.error(f"Error fetching menu: {e}", icon="🚨")
            st.stop()

    if not menu_json:
        st.warning("No data found for the selected options.", icon="⚠️")
        st.stop()

    df = pd.DataFrame(menu_json)

    school_name = schools_map[selectedSchool]["name"]
    hall_display = hall_label[selectedHall]
    file_stem = f"{selectedSchool}_{selectedHall}_{diningMenuData.lower()}_{diningDate.strftime('%Y-%m-%d')}"

    dl_col1, dl_col2, _ = st.columns([1, 1, 6])
    with dl_col1:
        st.download_button(
            label="Export CSV",
            data=df.to_csv(index=False),
            file_name=f"{file_stem}.csv",
            mime="text/csv",
        )
    with dl_col2:
        st.download_button(
            label="Export JSON",
            data=df.to_json(orient="records", indent=2),
            file_name=f"{file_stem}.json",
            mime="application/json",
        )

    tab1, tab2, tab3, tab4 = st.tabs(["Menu Data", "Top Protein Items", "Best Protein per Calorie", "Protein vs Calories"])

    with tab1:
        st.subheader(f"{school_name} · {hall_display} — {diningMenuData} · {diningDate.strftime('%B %d, %Y')}")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Top Protein Items")
        st.dataframe(df.sort_values("protein", ascending=False).head(15), use_container_width=True)

    with tab3:
        st.subheader("Best Protein per Calorie")
        st.dataframe(df.sort_values("protein_per_calorie", ascending=False).head(15), use_container_width=True)

    with tab4:
        st.subheader("Protein vs Calories")
        st.scatter_chart(df[["calories", "protein"]])
