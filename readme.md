# Campus Dining Macros

A Playwright-based web scraper with a Flask REST API and Streamlit dashboard for viewing nutritional information from college dining halls across Texas. Supports 15+ schools on DineOnCampus. Menu data is stored in PostgreSQL and served via a local API — also consumed by the Campus Food Logger Chrome extension.

## Features

- **Multi-School Support**: 15+ Texas universities, each with their dining halls pre-configured
- **Live Menu Scraping**: Fetches daily menus from DineOnCampus via Playwright
- **PostgreSQL Storage**: Scraped data is persisted — same school/hall/meal/date is never re-fetched
- **Comprehensive Nutrition Data**: Calories, Protein, Carbs, Fat, Sugar, Serving Size
- **Protein Analytics**: Top protein items, best protein-per-calorie ratio, scatter chart
- **Interactive Dashboard**: School → Hall → Meal → Date dropdowns, 4 display tabs
- **Rate Limiting**: Built-in request throttling to protect the scraper on public deployment

## Supported Schools

| Key | School | Halls |
|-----|--------|-------|
| UH | University of Houston | Moody Towers, Cougar Woods |
| SFA | Stephen F. Austin State University | 1923 Food Hall |
| BAYLOR | Baylor University | Penland Crossroads, 1845 at Memorial, East Village |
| LU | Lamar University | Brooks-Shivers Dining Hall, Brooks-Shivers BBQ |
| MSU | Midwestern State University | Mesquite Dining Hall |
| OLLU | Our Lady of the Lake University | Crave |
| SEU | St. Edward's University | St. Edwards Dining |
| TAMU | Texas A&M University | The Commons, Sbisa, Duncan, Copperhead Jack's, Shake Smart |
| TAMUSA | Texas A&M San Antonio | CAB Dining Hall |
| TAMUCC | Texas A&M Corpus Christi | Islander Dining Hall, Late Night Grill |
| TAMUT | Texas A&M Texarkana | The Food Hall |
| TAMUV | Texas A&M Victoria | Jaguar Dining Hall |
| TRINITY | Trinity University | Mather Hall |
| TSU | Texas Southern University | Sterling Dining Hall |
| TXST | Texas State University | The Den, Commons, Harris |
| UTRGV | UT Rio Grande Valley | Mather Hall |

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Abyss999/UH-Dining-Macros.git
cd UH-Dining-Macros
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 4. Set Up PostgreSQL
```bash
createdb dining
```

Create `backend/.env`:
```
DATABASE_URL=postgresql://localhost/dining
SECRET_KEY=your-secret-key
FLASK_APP=backend.app:create_app
FLASK_ENV=development
```

### 5. Run Migrations and Seed
```bash
export FLASK_APP=backend.app:create_app
flask db upgrade
flask seed
```

## Usage

The app requires both the Flask backend and Streamlit frontend to be running.

**Terminal 1 — Backend:**
```bash
export FLASK_APP=backend.app:create_app
flask run --port 5001
```

> **Note:** macOS blocks port 5000 (AirPlay Receiver). Use `--port 5001` and set `API_URL=http://localhost:5001` for the frontend.

**Terminal 2 — Frontend:**
```bash
streamlit run main.py
```

Frontend opens at `http://localhost:8501`. Set `API_URL` env var to point to the backend if using a non-default port.

1. Select a **school** from the first dropdown
2. Select a **dining hall**
3. Choose a **meal period** (Breakfast, Lunch, Dinner, Everyday)
4. Pick a **date** (historical data available if previously scraped)
5. Click **Get Menu**

On the first request for a given school/hall/meal/date, a browser window will open briefly while Playwright scrapes the menu. Subsequent requests for the same combination return instantly from the database.

## Project Structure

```
├── main.py                    # Streamlit UI (calls Flask API)
├── imports.py                 # Legacy shared imports (unused by main.py)
├── requirements.txt
├── src/
│   ├── scraper.py             # UHMenuScraper — school config + Playwright scraping
│   └── .streamlit/
│       ├── config.toml        # Dark orange Streamlit theme
│       └── styles.css         # Tab highlight styling
├── backend/
│   ├── app.py                 # Flask app factory + flask seed CLI
│   ├── config.py              # Environment config
│   ├── extensions.py          # Shared Flask extensions (limiter)
│   ├── models.py              # SQLAlchemy models (School, DiningHall, MenuItem)
│   ├── routes/
│   │   ├── schools.py         # GET /api/schools, GET /api/schools/<key>/halls
│   │   └── menu.py            # GET /api/menu, POST /api/menu/scrape
│   └── .env                   # Local environment variables (gitignored)
└── migrations/                # Alembic migration files
```

## API Reference

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| `GET` | `/api/schools` | 200/hour (default) | List all enabled schools with halls |
| `GET` | `/api/schools/<key>/halls` | 200/hour (default) | List halls for a school |
| `GET` | `/api/menu?school=UH&hall=moody&meal=lunch&date=2026-05-01` | 15/minute scrapes | Get menu — cached results are unlimited; limit only applies when Playwright scraping is triggered |
| `POST` | `/api/menu/scrape` | 5/minute | Force re-scrape `{school, hall, meal, date}` |

Rate limit responses return HTTP 429 with `{ "error": "Too many requests. Please slow down." }`.

## How It Works

### Scraping
- Playwright navigates each menu item and clicks it to open the nutrition popup
- Calories and serving size are parsed from the popup's full text (different HTML structure than other nutrients)
- Nutrient values with `+` suffixes or decimals (e.g. `4+ g`, `3.5 g`) are handled via regex
- `headless=False` is required to bypass Cloudflare on dineoncampus.com

### Caching
- On a cache miss, the Flask API calls the scraper and stores results in PostgreSQL
- On a cache hit, it queries `menu_items` filtered by school, hall, meal, and date
- A unique constraint on `(hall_id, meal_type, date, name)` prevents duplicate rows

## Troubleshooting

**Backend not reachable:**
Make sure `flask run` is running in a separate terminal before starting Streamlit.

**Port 5000 in use (macOS AirPlay):**
```bash
flask run --port 5001
API_URL=http://localhost:5001 streamlit run main.py
```

**Playwright not installed:**
```bash
playwright install --force
```

**Database doesn't exist:**
```bash
createdb dining
```

**Missing dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

## Contributing

Open issues or PRs on [GitHub](https://github.com/Abyss999/UH-Dining-Macros)!
