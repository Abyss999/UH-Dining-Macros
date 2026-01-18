# UH Dining Macros

A web scraper and interactive Streamlit app for viewing nutritional information from University of Houston dining halls.

## Features

- **Live Menu Scraping**: Automatically fetches daily menus from DineOnCampus
- **Multiple Dining Halls**: 
  - Moody Towers Dining Commons
  - Cougar Woods Dining Commons (24/7)
- **Comprehensive Nutrition Data**:
  - Calories, Protein, Carbs, Fat, Sugar
  - Serving sizes
  - Protein-to-calorie ratios
- **Smart Caching**: Saves scraped data to avoid repeated requests
- **Interactive Web Interface**: Browse menus through a clean Streamlit dashboard

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Abyss999/UH-Dining-Macros.git
cd UH-Dining-Macros
```

### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
```bash
playwright install
```

## Usage

Run the Streamlit app locally:
```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

### Using the App

1. Select a dining hall from the sidebar
2. Choose a meal period (Breakfast, Lunch, Dinner)
3. Browse the nutritional information for all available menu items
4. Data is automatically cached to improve performance

## Project Structure
```
UH-DINING-MACROS/
│
├── menu/                          # Cached menu data (CSV files)
│   ├── 24-7-cougar-woods-dining-commons_*.csv
│   └── moody-towers-dining-commons_*.csv
│
├── src/                           # Source code
│   ├── scraper.py                # Web scraping logic
│   └── (other modules)
│
├── .streamlit/                    # Streamlit configuration
│   ├── config.toml
│   └── styles.css
│
├── venv/                          # Virtual environment (not in repo)
├── imports.py                     # Shared imports
├── main.py                        # Streamlit app entry point
├── requirements.txt               # Python dependencies
├── notes.md                       # Development notes
└── readme.md                      # This file
```

## How It Works

### Scraping (`scraper.py`)
- Uses Playwright to navigate DineOnCampus pages
- Extracts nutritional data from interactive menu modals
- Calculates protein-to-calorie ratios for easy comparison
- Handles multiple dining halls and meal periods

### Caching
- Scraped data is saved to `menu/` directory as CSV files
- File format: `<dining-hall>_<meal>_<date>.csv`
- Cached data is reused to minimize scraping requests
- Data includes date stamps for freshness tracking

### Web Interface (`main.py`)
- Built with Streamlit for responsive UI
- Custom styling via `.streamlit/styles.css`
- Displays data in sortable, filterable tables
- Real-time scraping with loading indicators

## Development

To modify the scraper or add new dining halls:

1. Edit `src/scraper.py` to adjust scraping logic
2. Update `main.py` to add new UI features
3. Test locally with `streamlit run main.py`

## Notes

- The scraper respects DineOnCampus's structure and uses delays to avoid overwhelming servers
- Cache files are organized by date to track menu changes over time
- Playwright runs in headless mode for efficiency

## Troubleshooting

**Playwright installation issues:**
```bash
playwright install --force
```

**Port already in use:**
```bash
streamlit run main.py --server.port 8502
```

**Missing dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

## Contributing

Feel free to open issues or submit pull requests on [GitHub](https://github.com/Abyss999/UH-Dining-Macros)!

---

Made for UH students who want to track their nutrition! 🐾
