### Moody Towers Dining Scraper

This project scrapes the daily **Moody Towers Dining Commons** menu from the official DineOnCampus website and extracts full nutritional information for every food item.
The script automatically caches results into CSV files to avoid re-scraping unless needed.

The scraper supports breakfast, lunch, and dinner menus and outputs a complete Pandas DataFrame of all foods and their macros.

### Features

- Scrapes the live Moody Towers menu using Playwright
- Extracts:

  - Name
  - Serving size
  - Calories
  - Protein
  - Carbs
  - Fat
  - Sugar
  - Protein per calorie
  - Calories per protein

Saves results to:
```
/menu/macros_<menu_type>_cache.csv
```
- Loads from cache when available to avoid repeated scraping
- Prints readable, full-table output (no truncated rows)
- Automatically tracks entries by date

### Project Structure
```
Moody-Webscraping/
│
├── menu/
│   ├── macros_breakfast_cache.csv
│   ├── macros_lunch_cache.csv
│   └── macros_dinner_cache.csv
│
├── venv/                     # virtual environment (ignored)
├── imports.py               # shared imports for Playwright & Pandas
├── main.py                  # main scraper logic
└── readme.md
```
# Requirements

- Install dependencies:
```
pip install -r requirements.txt
```
And install Playwright browsers:
```
playwright install
```
### Usage
Run the scraper by specifying a menu type:
```
python3 main.py
```

Inside main.py, set:
```
menu = "breakfast"  # or "lunch", "dinner"
```

Valid options:
```
"breakfast"
"lunch"
"dinner"
```
If any other string is provided, the script will exit with an error.

Caching Logic
The scraper caches data to:
```
menu/macros_<menu>_cache.csv
```
Each row includes a column:
```
date = YYYY-MM-DD
```
On each run:
1. If today’s date exists in the cached CSV and refresh_cache=False,
→ the cached data is loaded and printed.

2. If no cache exists or refresh_cache=True,
→ the website is scraped again and the results are saved.

### Refresh cache example:
```
scraper.get_today_menu(menu_type="dinner", refresh_cache=True)
```

How It Works (Code Summary)
1. Scraping (websiteScrape)
- Opens the Moody Towers page for the given date & menu
- Clicks each food item
- Extracts nutritional data from the popup modal
- Computes two ratios:
  - protein_per_calorie
  - calories_per_protein
- Returns a list of dictionaries

2. Caching & Output (get_today_menu)

- Checks if today’s menu exists in menu/macros_MENUTYPE_cache.csv
- If cached:
  - Loads it
  - Prints full dataframe

- Otherwise:
  - Scrapes
  - Appends to CSV
  - Prints full dataframe

3. Display (macro_results)
- Configures Pandas to show full rows/columns and prints the entire DataFrame.

Example Output
```
Found 23 foods
Food 1: Scrambled Eggs
Food 2: Turkey Sausage Links
Food 3: Hash Browns
...

                    name serving_size calories protein carbs fats sugar p/c c/p
0          Scrambled Eggs      1 each       90      10     1    6     0  0.111 9.0
1  Turkey Sausage Patties      2 each      130      14     2    8     0  0.108 9.2
...
```
