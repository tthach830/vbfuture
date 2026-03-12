# Volleyball Court Availability Tracker - JSON Edition

A simple web application for tracking court availability using JSON files and SQLite database.

## How It Works

```
Step 1: Scraper collects data
   python auto_scraper.py
   ↓
Scrapes WebTrac → Stores in SQLite → Exports to JSON (MMDDYYYY.json)
   ↓
Step 2: Open in browser
   Open index.html
   ↓
Browser loads index.html → Checks for today's JSON file → Displays data in table
```

## Architecture

- **auto_scraper.py** - Scrapes WebTrac, stores in SQLite, exports to JSON
- **volleyball.db** - SQLite database (optional backup storage)
- **MMDDYYYY.json** - JSON files containing court data for each date
- **index.html** - Web interface that reads from JSON files

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `playwright` - Web scraping
- `beautifulsoup4` - HTML parsing

### 2. Run the Scraper
```bash
python auto_scraper.py
```

This will:
1. Scrape court availability from WebTrac
2. Store data in `volleyball.db` (SQLite)
3. Export to `MMDDYYYY.json` (where MMDDYYYY is today's date, e.g., `03122026.json`)

### 3. View the Data
Open `index.html` in your web browser

The page will automatically:
1. Check for a JSON file for today's date
2. If found, display the court availability
3. If not found, show a message to run the scraper

## Usage

### Scrape Today's Data
```bash
python auto_scraper.py
```
Creates/updates: `03122026.json` (for March 12, 2026)

### Scrape for a Specific Date (MMDDYYYY)
```bash
python auto_scraper.py 03152026
```
Creates: `03152026.json`

### Scrape for a Specific Date (YYYY-MM-DD)
```bash
python auto_scraper.py --date 2026-03-15
```

## JSON File Format

Each JSON file contains:
```json
{
  "status": "success",
  "data": [
    ["Court", "LastUpdated", "7am-8am", "8am-9am", "9am-10am"],
    ["Main 01", "14:30:45", "available", "reserved", "available"],
    ["Main 02", "14:30:45", "available", "available", "unavailable"],
    ...
  ],
  "lastUpdated": "14:30:45",
  "date": "2026-03-12"
}
```

## Viewing Data in Browser

1. Run: `python auto_scraper.py` to create the JSON file
2. Open: `index.html` in your web browser
3. The page shows today's court availability in a table

The table includes:
- Court names
- Available/Reserved/Unavailable status for each time slot
- Visual color coding (Red = Unavailable)
- Interactive map overlay with court locations

## File Structure

```
project/
├── auto_scraper.py         # Main scraper script
├── index.html              # Web interface
├── volleyball.db           # SQLite database (auto-created)
├── 03122026.json          # Today's data (auto-created)
├── 03132026.json          # Yesterday's data (auto-created)
├── 03142026.json          # etc...
├── requirements.txt        # Dependencies
├── map.png                # Court map image
├── court_coords.json      # Court coordinates
└── README_JSON.md         # This file
```

## Troubleshooting

### "No data available for today. Run the scraper first."
- Run: `python auto_scraper.py`
- The script will create the JSON file for today

### JSON file not loading
- Check that `03122026.json` exists in the same directory as `index.html`
- Verify the JSON file is valid: Open it in a text editor
- Check browser console (F12) for errors

### Scraper fails
- Make sure you're in the correct directory
- Check: `pip install -r requirements.txt`
- Verify Playwright is installed: `python -c "import playwright; print(playwright.__version__)"`

## Database (SQLite)

The SQLite database is automatically created and contains two tables:

### courts table
```sql
CREATE TABLE courts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE
);
```

### slots table
```sql
CREATE TABLE slots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  court_id INTEGER,
  time_slot TEXT,
  status TEXT,
  date TEXT,
  FOREIGN KEY(court_id) REFERENCES courts(id)
);
```

The database serves as a backup and reference, while JSON files are the primary way data is served to the web interface.

## Direct Database Queries

View all courts:
```sql
SELECT DISTINCT name FROM courts ORDER BY name;
```

Check specific court availability:
```bash
python -c "
import sqlite3
conn = sqlite3.connect('volleyball.db')
c = conn.cursor()
rows = c.execute('SELECT s.time_slot, s.status FROM slots s JOIN courts c ON s.court_id = c.id WHERE c.name=\"Main 01\" AND date=\"2026-03-12\"').fetchall()
for slot, status in rows:
    print(f'{slot}: {status}')
"
```

## Command Reference

| Command | Purpose |
|---------|---------|
| `python auto_scraper.py` | Scrape today |
| `python auto_scraper.py 03152026` | Scrape specific date (MMDDYYYY) |
| `python auto_scraper.py --date 2026-03-15` | Scrape specific date (YYYY-MM-DD) |
| `ls *.json` | List all data files |
| `open index.html` | View in browser (or double-click) |

## License

Internal use only
