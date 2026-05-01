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

        self.schools = {
            "UH": {
                "name": "University of Houston",
                "domain": "new.dineoncampus.com",
                "slug": "uh",
                "halls": {
                    "moody": "moody-towers-dining-commons",
                    "cougar": "24-7-cougar-woods-dining-commons",
                },
            },
            "SFA": {
                "name": "Stephen F. Austin State University",
                "domain": "dineoncampus.com",
                "slug": "sfa",
                "halls": {
                    "1923": "food-hall-1923",
                },
            },
            "ACU": {
                "name": "Abilene Christian University",
                "domain": "dineoncampus.com",
                "slug": "acudining",
                "halls": {},
                "disabled": True, # no dining hall pages to scrape, only menus with no nutrition info
            },
            "ASU": {
                "name": "Angelo State University",
                "domain": "dineoncampus.com",
                "slug": "angelo",
                "halls": {},
                "disabled": True, # no dining hall pages to scrape, only menus with no nutrition info
            },
            "BAYLOR": {
                "name": "Baylor University",
                "domain": "dineoncampus.com",
                "slug": "baylor",
                "halls": {
                    "penland-crossroads-dining-hall": "penland-crossroads-dining-hall",
                    "1845-at-memorial": "1845-at-memorial",
                    "east-village-dining-commons": "east-village-dining-commons",
                },
            },
            "LU": {
                "name": "Lamar University",
                "domain": "dineoncampus.com",
                "slug": "bigred",
                "halls": {
                    "brooks-shivers-dining-hall": "brooks-shivers-dining-hall",
                    "brooks-shivers-bbq": "brooks-shivers-bbq",
                },
            },
            "MSU": {
                "name": "Midwestern State University",
                "domain": "dineoncampus.com",
                "slug": "midwesternstate",
                "halls": {
                    "mesquite-dining-hall": "mesquite-dining-hall",
                },
            },
            "OLLU": {
                "name": "Our Lady of the Lake University",
                "domain": "dineoncampus.com",
                "slug": "ollu",
                "halls": {
                    "crave": "crave"
                },
            },
            "SEU": {
                "name": "St. Edward's University",
                "domain": "dineoncampus.com",
                "slug": "stedwards",
                "halls": {
                    "stedwards": "stedwards",
                },
            },
            "TAMU": {
                "name": "Texas A&M University",
                "domain": "dineoncampus.com",
                "slug": "tamu",
                "halls": {
                    "the-commons-dining-hall-south-campus": "the-commons-dining-hall-south-campus",
                    "sbisa-dining-hall-north-campus": "sbisa-dining-hall-north-campus",
                    "duncan-dining-hall-south-campus-quad": "duncan-dining-hall-south-campus-quad",
                    "copperhead-jack-s-west-campus-food-hall": "copperhead-jack-s-west-campus-food-hall",
                    "shake-smart-rec-center": "shake-smart-rec-center",
                    },
            },
            "TAMUG": {
                "name": "Texas A&M Galveston",
                "domain": "dineoncampus.com",
                "slug": "tamug",
                "halls": {},
                "disabled": True, # no dining hall pages to scrape, only menus with no nutrition info
            },
            "TAMUSA": {
                "name": "Texas A&M San Antonio",
                "domain": "dineoncampus.com",
                "slug": "tamusa",
                "halls": {
                    "cab-dining-hall": "cab-dining-hall",
                },
            },
            "TAMUCC": {
                "name": "Texas A&M University - Corpus Christi",
                "domain": "dineoncampus.com",
                "slug": "islanderdining",
                "halls": {
                    "islander-dining-hall": "islander-dining-hall",
                    "late-night-grill-patio": "late-night-grill-patio",
                },
            },
            "TAMUT": {
                "name": "Texas A&M Texarkana",
                "domain": "dineoncampus.com",
                "slug": "tamut",
                "halls": {"the-food-hall": "the-food-hall"},
            },
            "TAMUV": {
                "name": "Texas A&M University Victoria",
                "domain": "dineoncampus.com",
                "slug": "tamuv",
                "halls": {"jaguar-dining-hall": "jaguar-dining-hall"},
            },
            "TSU": {
                "name": "Texas Southern University",
                "domain": "dineoncampus.com",
                "slug": "tsu",
                "halls": {
                    "sterling-dining-hall": "sterling-dining-hall",
                },
            },
            "TXST": {
                "name": "Texas State University",
                "domain": "dineoncampus.com",
                "slug": "txstate",
                "halls": {
                    "the-den-express-dining-hall": "the-den-express-dining-hall",
                    "commons-dining-hall": "commons-dining-hall",
                    "harris-dining-hall": "harris-dining-hall",
                },
            },
            "UHCL": {
                "name": "University of Houston-Clear Lake",
                "domain": "dineoncampus.com",
                "slug": "uhcl",
                "halls": {},
                "disabled": True, # no dining hall pages to scrape, only menus with no nutrition info
            },
            "TRINITY": {
                "name": "Trinity University",
                "domain": "dineoncampus.com",
                "slug": "trinity",
                "halls": {"mather-hall": "mather-hall"},
            },
            "UTRGV": {
                "name": "The University of Texas Rio Grande Valley",
                "domain": "dineoncampus.com",
                "slug": "utrgv",
                "halls": {"mather-hall": "mather-hall"},
            },
            "UTA": {
                "name": "The University of Texas at Arlington",
                "domain": "dineoncampus.com",
                "slug": "utarlington",
                "halls": {},
                "disabled": True, # no dining hall pages to scrape, only menus with no nutrition info
            },
            "UTD": {
                "name": "The University of Texas at Dallas",
                "domain": "dineoncampus.com",
                "slug": "utarlington",
                "halls": {},
                "disabled": True, # no dining hall pages to scrape, only menus with no nutrition info
            },
            "UTPB": {
                "name": "University of Texas of the Permian Basin",
                "domain": "dineoncampus.com",
                "slug": "utpb",
                "halls": {},
                "disabled": True, # no dining hall pages to scrape, only menus with no nutrition info
            },
        }

        self.nutNameMap = {
            "Protein (g)": "protein",
            "Total Carbohydrates (g)": "carbs",
            "Total Fat (g)": "fats",
            "Calories": "calories",
            "Sugar (g)": "sugar",
            "Serving Size": "serving_size",
        }

        self.search = ["all", "P", "V", "VG", "CF"] # all, protein, vegitarian, vegan, climate friendly

    def discover_halls(self, school_key: str) -> dict:
        """Navigate to a school's DineOnCampus home page and extract available dining hall slugs.
        Returns {short_key: hall_slug} and updates self.schools[school_key]['halls'] in place."""
        if school_key not in self.schools:
            raise ValueError(f"Unknown school: {school_key}")
        cfg = self.schools[school_key]
        halls = {}
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(f"https://{cfg['domain']}/{cfg['slug']}/")
            page.wait_for_load_state("networkidle")
            links = page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]'))
                    .map(a => ({href: a.getAttribute('href'), text: a.textContent.trim()}))
                    .filter(a => a.href && a.href.includes('/whats-on-the-menu/'))
            """)
            seen_slugs = set()
            for link in links:
                m = re.search(r'/whats-on-the-menu/([^/?#]+)', link['href'])
                if m:
                    hall_slug = m.group(1)
                    if hall_slug in seen_slugs:
                        continue
                    seen_slugs.add(hall_slug)
                    short_key = hall_slug.split('-')[0]
                    # ensure uniqueness if two halls share the same first word
                    base = short_key
                    i = 2
                    while short_key in halls:
                        short_key = f"{base}{i}"
                        i += 1
                    halls[short_key] = hall_slug
                    print(f"  [{school_key}] {short_key}: {hall_slug}  (from '{link['text']}')")
            browser.close()
        self.schools[school_key]["halls"] = halls
        return halls

    def websiteScrape(self, playwright: Playwright, menu_type="lunch", dining_hall="moody", school="UH"):
        cfg = self.schools[school]
        chromium = playwright.chromium
        browser = chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://{cfg['domain']}/{cfg['slug']}/whats-on-the-menu/{cfg['halls'][dining_hall]}/{today}/{menu_type}")
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

    def get_today_menu(self, find_date=today, menu_type="lunch", refresh_cache=False, dining_hall="moody", school="UH", result_format="csv"):
        find_date = date.today().isoformat()
        menu_dir = os.path.join(self.repo_root, "menu")
        os.makedirs(menu_dir, exist_ok=True)

        if school not in self.schools:
            raise ValueError(f"Invalid school '{school}'. Choose from: {list(self.schools.keys())}")
        if menu_type not in ["lunch", "dinner", "breakfast", "everyday"]:
            raise ValueError("Invalid menu type. Choose from 'lunch', 'dinner', or 'breakfast'")
        if dining_hall not in self.schools[school]["halls"]:
            raise ValueError(f"Invalid dining hall '{dining_hall}' for {school}. Choose from: {list(self.schools[school]['halls'].keys())}")

        school_slug = self.schools[school]["slug"]
        hall_slug = self.schools[school]["halls"][dining_hall]
        cached_file = os.path.join(menu_dir, f"{school_slug}_{hall_slug}_{menu_type}_cache.csv")

        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 0:
            if not refresh_cache:
                df = pd.read_csv(cached_file)
                df["date"] = df["date"].astype(str)
                rows = df[df["date"] == find_date]
                if not rows.empty:
                    data = rows.drop(columns=["date"]).to_dict(orient="records")
                    self.macro_results(data)
                    return data

        print('Scraping...')

        with sync_playwright() as playwright:
            data = self.websiteScrape(playwright, menu_type, dining_hall=dining_hall, school=school)

        for row in data:
            row["date"] = find_date

        if os.path.exists(cached_file):
            df_old = pd.read_csv(cached_file)
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
    import sys
    scraper = UHMenuScraper()

    if len(sys.argv) > 1 and sys.argv[1] == "discover":
        # Discover halls for all schools that have none configured yet.
        # Run: python3 src/scraper.py discover
        for key, cfg in scraper.schools.items():
            if not cfg["halls"]:
                print(f"\nDiscovering halls for {key} ({cfg['name']})...")
                try:
                    halls = scraper.discover_halls(key)
                    print(f"  → {halls}")
                except Exception as e:
                    print(f"  ✗ Failed: {e}")
    else:
        menu = "lunch"
        dining_hall = "moody"
        school = "UH"
        scraper.get_today_menu(
            menu_type=menu,
            refresh_cache=True,
            dining_hall=dining_hall,
            school=school,
        )