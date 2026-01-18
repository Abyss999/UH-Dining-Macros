from imports import *
from src.scraper import UHMenuScraper

st.set_page_config(
    page_title="UH Dining Menu Scraper",
    page_icon="🍽️",
    layout="wide",
)

with open("src/.streamlit/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("UH Dining Menu Scraper")

diningHallOptions = ["Moody Towers Dining Hall", "Cougar Woods Dining Hall"]
diningMenuOptions = ["Breakfast", "Lunch", "Dinner"]

col1, col2, col3 = st.columns(3)

with col1:
    diningHallData = st.selectbox("Select Dining Hall",
                                placeholder="Choose a dining hall", 
                                index = 1, # default option
                                options=diningHallOptions)
with col2:
    diningMenuData = st.selectbox("Select Menu Type", 
                              placeholder="Choose a menu type",
                              index = 1, # default option
                              options=diningMenuOptions)

with col3:
    diningDate = st.date_input("Select Date", 
                                 value=datetime.today(), 
                                 min_value=datetime.today() - timedelta(days=30), 
                                 max_value=datetime.today())

if st.button("Get Menu"):
    
    try:
        df = UHMenuScraper().get_today_menu(
            find_date=diningDate.strftime("%Y-%m-%d"),
            dining_hall=diningHallData.split(" ")[0].lower(), 
            menu_type=diningMenuData.lower(), 
            result_format="pd",
            refresh_cache=False,
        )
    except Exception as e:
        st.error(f"An error occurred while fetching the menu: {e}", icon="🚨")
        st.stop()

    
    if isinstance(df, list):
        df = pd.DataFrame(df)

    if df.empty:
        st.warning("No cached or scraped data found for the selected options.", icon="⚠️")
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs(["Menu Data", "Top Protein Items", "Best Protein per Calorie", "Protein vs Calories", ])
    

    with tab1:
        st.subheader(f"{diningHallData} - {diningMenuData} Menu for {diningDate.strftime('%B %d, %Y')}")
        st.dataframe(df, width='stretch')

    with tab2:
        st.subheader("Top Protein items")
        st.dataframe(df.sort_values("protein", ascending=False).head(15), width='stretch')

    with tab3:
        st.subheader("Top Protein per Calorie item")
        df["protein_per_calorie"] = df.apply(lambda row: UHMenuScraper.handleSorting(row["protein"], row["calories"]), axis=1)
        st.dataframe(df.sort_values("protein_per_calorie", ascending=False), width='stretch')

    with tab4:
        st.subheader("Protein vs Calories")
        st.scatter_chart(df[["calories", "protein"]])


    best = df.sort_values("protein_per_calorie", ascending=False).head(1).iloc[0]



