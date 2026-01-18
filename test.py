from imports import *
from src.scraper import UHMenuScraper

st.title("UH Dining Menu Scraper")

diningHallOptions = ["Moody", "Cougar Woods"]
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

st.button("Get Today's Menu", on_click=lambda: 
        UHMenuScraper().get_today_menu(
            find_date=diningDate.strftime("%Y-%m-%d"),
            dining_hall=diningHallData.split(" ")[0].lower(), 
            menu_type=diningMenuData.lower(), 
            result_format="pd"
            ))

