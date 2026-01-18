from imports import *
today = date.today()

# min-w-full = station tables 

class UHMenuScraper:
    def __init__(self, menu="lunch"):
        self.menu = menu

        self.diningHall = {
            "moody": "moody-towers-dining-commons",
            "cougar": "24-7-cougar-woods-dining-commons",
        }

        self.nutNameMap = {
            "Protein (g)": "protein",
            "Total Carbohydrates (g)": "carbs",
            "Total Fat (g)": "fats",
            "Calories": "calories",
            "Sugar (g)": "sugar",
            "Serving Size": "serving_size",
        }

        self.school = {
            "UH": "uh",
            "SFA": "sfa",
            "tamu": "tamu",
        }

        self.search = ["all", "P", "V", "VG", "CF"] # all, protein, vegitarian, vegan, climate friendly



    def websiteScrape(self, playwright: Playwright, menu_type = "lunch", dining_hall = "moody", school = "UH"):
        chromium = playwright.chromium
        browser = chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://new.dineoncampus.com/{self.school[school]}/whats-on-the-menu/{self.diningHall[dining_hall]}/{today}/{menu_type}")
        page.wait_for_selector(".min-w-full") # wait for each station to load 

        # foods  = page.query_selector_all(".text-lg.font-semibold.pl-2") # text-lg font-semibold pl-2
        foods = page.query_selector_all(".max-w-0.py-5.pl-4.pr-3")
        print(f"Found {len(foods)} foods")

        foodMaps = []

        for count, food in enumerate(foods):
            text_split = food.inner_text().split("\n")
            text = text_split[0] if len(text_split) > 0 else "N/A"
            # description = text_split[1] if len(text_split) > 1 else "N/A"
            # scroll if needed 
            food.scroll_into_view_if_needed()
            # click the food 
            food.click()
            # wait for popup 
            page.wait_for_selector("span.font-bold:has-text('Protein (g)')") # <span class="font-bold">Protein (g)</span>
            # nutrition = page.query_selector_all("span.font-bold")
            serving = page.query_selector(".text-sm.font-bold.border-b")
            nutrition = page.query_selector_all(".flex.justify-between.py-1")

            nutritionMap = {}

            serving_split = serving.inner_text().split(": ")
            nutritionMap["serving_size"] = serving_split[1] if len(serving_split) > 1 else "N/A"
            # nutritionMap["description"] = description

            for i in range(len(nutrition) - 1):
                key = nutrition[i].inner_text()
                arr = key.split("\n") # key : value // ex. protein : 10
                if arr[0] in self.nutNameMap.keys():
                    nutritionMap[self.nutNameMap[arr[0]]] = self.handleNutritionMap(arr[1])
                else:
                    nutritionMap[arr[0]] = self.handleNutritionMap(arr[1])

            protein = nutritionMap.get("protein", "N/A")
            carbs = nutritionMap.get("carbs", "N/A")
            fats = nutritionMap.get("fats", "N/A")
            calories = nutritionMap.get("calories", "N/A")
            sugar = nutritionMap.get("sugar", "N/A")
            serving_size = nutritionMap.get("serving_size", "N/A")
            # description = nutritionMap.get("description", "N/A")

            print(f"Food {count + 1}: {text}")

            close_button = page.query_selector(".svg-inline--fa.fa-xmark")
            close_button.click()

            foodMaps.append({
                "name": text,
                "serving_size": serving_size,
                "calories": int(calories) if calories.isnumeric() else 0,
                "protein": int(protein) if protein.isnumeric() else 0,
                "carbs": int(carbs) if carbs.isnumeric() else 0,
                "fats": int(fats) if fats.isnumeric() else 0,
                "sugar": int(sugar) if sugar.isnumeric() else 0,
                "protein_per_calorie": self.handleSorting(int(protein) if protein.isnumeric() else 0, int(calories) if calories.isnumeric() else 0),
                "calories_per_protein": self.handleSorting(int(calories) if calories.isnumeric() else 0, int(protein) if protein.isnumeric() else 0),
                # "description": description,
            })

        sortArr = sorted(foodMaps, key=lambda x: x["protein"], reverse=False)
        browser.close()
        return sortArr

    def get_today_menu(self, find_date = today, menu_type = "lunch", refresh_cache = False, dining_hall = "moody", result_format = "csv"):
        find_date = date.today().isoformat()
        cached_file = f"menu/{self.diningHall[dining_hall]}_{menu_type}_cache.csv"
        if menu_type not in ["lunch", "dinner", "breakfast"]:
            raise ValueError("Invalid menu type. Choose from 'lunch', 'dinner', or 'breakfast'")
        if dining_hall not in self.diningHall.keys():
            raise ValueError("Invalid dining hall. Choose from 'moody' or 'cougar'")

        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 0: # file exist + check for refresh
            if not refresh_cache:
                df = pd.read_csv(cached_file) # reads the cache csv
                df["date"] = df["date"].astype(str)

                rows = df[df["date"] == find_date] # finds today cache 
                if not rows.empty: # if results 
                    data = rows.drop(columns=["date"]).to_dict(orient="records")
                    self.macro_results(data)
                    return data

        print('Scraping...')

        with sync_playwright() as playwright:
            data = self.websiteScrape(playwright, menu_type, dining_hall=dining_hall) # if not cached, scrape 

        for row in data:
            row["date"] = find_date

        if os.path.exists(f"macros_{menu_type}_cache.csv"):
            df_old = pd.read_csv(f"macros_{menu_type}_cache.csv")
            df_new = pd.concat([df_old, pd.DataFrame(data)], ignore_index=True)
        else:
            df_new = pd.DataFrame(data)

        df_new.to_csv(cached_file, index=False)
        self.macro_results(data)

        if result_format == "pd":
            return pd.DataFrame(data)

        return data

    @staticmethod
    def macro_results(data):
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        # pd.set_option("display.max_colwidth", None)
        df = pd.DataFrame(data)
        print(df)

    @staticmethod
    def handleSorting(num, num2):
        if num2 == 0:
            return round(0, 3)
        return round(num / num2, 3)
    
    @staticmethod
    def handleNutritionMap(nutritionAmount):
        if nutritionAmount.endswith("g"):
            return nutritionAmount[:-2]
        if nutritionAmount.endswith("kcal"):
            return nutritionAmount[:-5]
        return nutritionAmount

# __init__ = "__main__"
# if __name__ == "__main__":
#     menu = "lunch"  # breakfast, lunch, dinner
#     dining_hall = "cougar" # moody, cougar
#     UHMenuScraper(menu=menu).get_today_menu(
#         menu_type=menu, 
#         refresh_cache=False, 
#         dining_hall=dining_hall,
#         school="UH"
#     )