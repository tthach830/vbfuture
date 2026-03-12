# System Architecture - JSON-Based Data Storage

## Overview

The project now uses a simple JSON file-based system instead of Flask:

```
┌────────────────────────────────────────────────────────┐
│ Data Collection: auto_scraper.py                       │
│ • Scrapes WebTrac using Playwright + BeautifulSoup   │
│ • Stores in SQLite (volleyball.db)                     │
│ • Exports to JSON (03122026.json)                      │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓
    ┌───────────────────────────┐
    │ JSON Files (MMDDYYYY.json) │
    │ • One file per date        │
    │ • Contains court data      │
    │ • Human-readable format    │
    └────────────────┬──────────┘
                     │
                     ↓
    ┌────────────────────────────┐
    │ index.html (Web Browser)   │
    │ • Loads JSON file          │
    │ • Displays in table/map    │
    │ • No server needed         │
    └────────────────────────────┘
```

## Component Details

### auto_scraper.py
**Purpose:** Scrapes WebTrac and generates data files

**Process:**
1. Connects to WebTrac with Playwright
2. Extracts court availability
3. Stores in `volleyball.db` (SQLite) as backup
4. Exports to `MMDDYYYY.json`

**Usage:**
```bash
python auto_scraper.py              # Today's date
python auto_scraper.py 03152026     # Specific date (MMDDYYYY)
python auto_scraper.py --date 2026-03-15  # Specific date (YYYY-MM-DD)
```

**Output:**
- `volleyball.db` - SQLite database with all historical data
- `MMDDYYYY.json` - JSON file for the scraped date
  - Example: `03122026.json` for March 12, 2026

### MMDDYYYY.json Files
**Format:**
```json
{
  "status": "success",
  "data": [
    ["Court", "LastUpdated", "7am-8am", "8am-9am", ...],
    ["Main 01", "14:30:45", "available", "reserved", ...],
    ["Main 02", "14:30:45", "available", "available", ...],
    ...
  ],
  "lastUpdated": "14:30:45",
  "date": "2026-03-12"
}
```

**Location:** Same directory as `index.html`

**Creation:** Automatically created by `auto_scraper.py`

### index.html
**Purpose:** Web interface for viewing court availability

**How it works:**
1. On page load, calculates today's date`
2. Builds expected JSON filename (e.g., `03122026.json`)
3. Attempts to fetch the JSON file
4. Renders the data in a table if found
5. Shows error message if JSON file not found

**Features:**
- Interactive table with court names and time slots
- Visual map overlay showing court locations
- Color-coded availability (Red = Unavailable)
- No server needed - pure client-side rendering
- Best viewed in Firefox, Chrome, Edge, or Safari

**Data Source:** Local JSON files only (no API)

## Data Flow

### Workflow 1: Scraping New Data
```
Run: python auto_scraper.py
     ↓
Scrapes WebTrac
     ↓
Parses HTML → Extracts court data
     ↓
Stores in SQLite (volleyball.db)
     ↓
Exports to JSON (03122026.json)
     ↓
Done - Data ready to view
```

### Workflow 2: Viewing Data
```
Open: index.html
     ↓
JavaScript loads
     ↓
Calculate today's date (03122026)
     ↓
Fetch: 03122026.json
     ↓
If found: Render table with data
If not found: Show "Run scraper" message
     ↓
Done - Data displayed
```

## Database Structure (SQLite)

The SQLite database (`volleyball.db`) serves as a backup and is optional:

**courts** table:
```
id (Primary Key) | name
1                | Main 01
2                | Main 02
3                | Dream 1
...
```

**slots** table:
```
id | court_id | time_slot | status | date
1  | 1        | 7am-8am   | available | 2026-03-12
2  | 1        | 8am-9am   | reserved  | 2026-03-12
3  | 2        | 7am-8am   | unavailable | 2026-03-12
...
```

## File Locations

```
project_directory/
│
├── auto_scraper.py          ← Run this to scrape
├── index.html               ← Open this in browser
├── requirements.txt         ← Dependencies
│
├── volleyball.db            ← SQLite database (auto-created)
│
├── JSON Files (auto-created):
├── 03102026.json           ← March 10 data
├── 03112026.json           ← March 11 data
├── 03122026.json           ← March 12 data (today)
├── 03132026.json           ← March 13 data
└── 03142026.json           ← March 14 data
```

## Installation & Setup

### 1. Install Dependencies (one-time)
```bash
pip install -r requirements.txt
```

Dependencies:
- `playwright==1.42.0` - Web automation
- `beautifulsoup4==4.12.3` - HTML parsing

### 2. Run Scraper
```bash
python auto_scraper.py
```

This creates JSON file for today (e.g., `03122026.json`)

### 3. Open in Browser
1. Open `index.html` in web browser
2. Or double-click `index.html` on Windows/Mac
3. Page loads data from JSON file

## Advantages of This Approach

✓ **No server needed** - Pure client-side rendering
✓ **Simple & fast** - Just JSON files
✓ **History preserved** - One file per date
✓ **SQLite backup** - Data saved in database too
✓ **Portable** - Works anywhere with a browser
✓ **Low overhead** - Minimal dependencies

## Limitations & Notes

- **View-only in browser** - Can't edit from web interface
- **Manual refresh needed** - Reload page to see new data
- **Must run scraper first** - JSON file must exist
- **Single date per file** - One JSON file per date

To update data, always run the scraper:
```bash
python auto_scraper.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data available" | Run `python auto_scraper.py` |
| JSON file blank | Check scraper completed successfully |
| Browser can't find file | Verify JSON file in same directory as index.html |
| Scraper fails | Run `pip install -r requirements.txt` |
| Old data showing | Delete old JSON files or run new scrape |

## Technical Notes

- JSON files are created in the current working directory
- File size typically < 50KB per date
- Browser loads via local filesystem (file:// protocol)
- No CORS issues since files are local
- Works offline once files are created

## Future Enhancements

- Add date picker to load historical data
- Add scheduled scraper (hourly/daily)
- Add web-based editor for manual updates
- Add data export/backup
- Add analytics and reporting

---

For quick start: See `QUICKSTART_JSON.md`
For detailed docs: See `README_JSON.md`
