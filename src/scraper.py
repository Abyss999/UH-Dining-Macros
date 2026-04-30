from playwright.sync_api import sync_playwright, Playwright
from datetime import date
import pandas as pd
import re
import os

today = date.today()

# min-w-full = station tables 

class UHMenuScraper:
    def __init__(self, menu="lunch"):
        self.menu = menu
        # repository root (project root is one level up from this src file)
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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
            nutrition = page.query_selector_all(".flex.justify-between.py-1")

            nutritionMap = {}

            # Parse calories and serving size from popup text.
            # Calories is in its own header section (not a .flex row).
            # Serving size appears as "Serving size: 1 serving(s)" on one line.
            popup = page.query_selector("[role='dialog']") or page.query_selector(".modal-content") or page.query_selector("[class*='modal']")
            if popup:
                lines = [l.strip() for l in popup.inner_text().split("\n") if l.strip()]
                for i, line in enumerate(lines):
                    if line == "Calories" and i + 1 < len(lines):
                        nutritionMap["calories"] = lines[i + 1]
                    if line.lower().startswith("serving size:"):
                        nutritionMap["serving_size"] = line.split(":", 1)[1].strip()
            if "serving_size" not in nutritionMap:
                nutritionMap["serving_size"] = "N/A"

            for i in range(len(nutrition)):
                key = nutrition[i].inner_text()
                arr = key.split("\n") # key : value // ex. protein : 10
                if len(arr) < 2:
                    continue
                if arr[0] in self.nutNameMap.keys():
                    nutritionMap[self.nutNameMap[arr[0]]] = self.handleNutritionMap(arr[1].strip())
                else:
                    nutritionMap[arr[0]] = self.handleNutritionMap(arr[1].strip())

            protein = nutritionMap.get("protein", "0")
            carbs = nutritionMap.get("carbs", "0")
            fats = nutritionMap.get("fats", "0")
            calories = nutritionMap.get("calories", "0")
            sugar = nutritionMap.get("sugar", "0")
            serving_size = nutritionMap.get("serving_size", "N/A")

            print(f"Food {count + 1}: {text}")

            close_button = page.query_selector(".svg-inline--fa.fa-xmark")
            close_button.click()

            p = self.parseNumber(protein)
            cal = self.parseNumber(calories)
            foodMaps.append({
                "name": text,
                "serving_size": serving_size,
                "calories": cal,
                "protein": p,
                "carbs": self.parseNumber(carbs),
                "fats": self.parseNumber(fats),
                "sugar": self.parseNumber(sugar),
                "protein_per_calorie": self.handleSorting(p, cal),
                "calories_per_protein": self.handleSorting(cal, p),
            })

        sortArr = sorted(foodMaps, key=lambda x: x["protein"], reverse=False)
        browser.close()
        return sortArr

    def get_today_menu(self, find_date = today, menu_type = "lunch", refresh_cache = False, dining_hall = "moody", result_format = "csv"):
        find_date = date.today().isoformat()
        menu_dir = os.path.join(self.repo_root, "menu")
        os.makedirs(menu_dir, exist_ok=True)
        cached_file = os.path.join(menu_dir, f"{self.diningHall[dining_hall]}_{menu_type}_cache.csv")
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

        macros_file = os.path.join(menu_dir, f"macros_{menu_type}_cache.csv")
        if os.path.exists(macros_file):
            df_old = pd.read_csv(macros_file)
            df_new = pd.concat([df_old, pd.DataFrame(data)], ignore_index=True)
        else:
            df_new = pd.DataFrame(data)

        df_new.to_csv(cached_file, index=False)
        self.macro_results(data)

        if result_format == "pd":
            return pd.DataFrame(data).drop(columns=["date"], errors='ignore')

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
        val = nutritionAmount.strip()
        if val.endswith("kcal"):
            return val[:-4].strip()
        if val.endswith("g"):
            return val[:-1].strip()
        return val

    @staticmethod
    def parseNumber(val):
        """Extract leading integer from strings like '35', '4+', '3.5', '-', 'N/A'."""
        m = re.match(r"(\d+\.?\d*)", str(val).strip())
        return int(float(m.group(1))) if m else 0

__init__ = "__main__"
if __name__ == "__main__":
    menu = "dinner"  # breakfast, lunch, dinner
    dining_hall = "moody" # moody, cougar
    UHMenuScraper(menu=menu).get_today_menu(
        menu_type=menu, 
        refresh_cache=True, 
        dining_hall=dining_hall,
        # school="UH"
    )