# VBFuture - Volleyball Court Availability Tracker

A simple web application for tracking beach volleyball court availability using a JSON-based system with web scraping.

## 🎯 Features

- **Scrapes WebTrac** for real-time court availability data
- **JSON-based storage** - one file per date (MMDDYYYY.json)
- **SQLite backup** - data also stored in local database
- **Web interface** - no server needed, pure HTML + JSON
- **Visual map** - interactive court location display
- **Simple setup** - minimal dependencies

## 📦 What's Inside

```
├── auto_scraper.py          # Scraper script (scrapes WebTrac → JSON + SQLite)
├── index.html               # Web interface (displays JSON data)
├── requirements.txt         # Python dependencies
├── volleyball.db            # SQLite database (backup storage)
├── MMDDYYYY.json           # JSON data files (auto-created by scraper)
└── Documentation:
    ├── QUICK_REF.md         # Quick reference (2-minute read)
    ├── QUICKSTART_JSON.md   # Setup guide (3 steps)
    ├── README_JSON.md       # Full documentation
    ├── ARCHITECTURE.md      # System design
    └── CHANGES.md           # What changed from previous versions
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Scrape Court Data
```bash
python auto_scraper.py
```
Creates JSON file for today (e.g., `03122026.json`)

### 3. View in Browser
Open `index.html` in your web browser
- Automatically loads today's JSON data
- Displays in interactive table and map format

## 📋 System Architecture

```
WebTrac
   ↓
auto_scraper.py (Scraper)
   ├→ volleyball.db (SQLite)
   └→ MMDDYYYY.json (JSON Files)
        ↓
    index.html (Browser)
        ↓
    Table & Map Display
```

## 🔧 Commands

| Command | Purpose |
|---------|---------|
| `pip install -r requirements.txt` | Install dependencies |
| `python auto_scraper.py` | Scrape today's data |
| `python auto_scraper.py 03152026` | Scrape specific date (MMDDYYYY) |
| `python auto_scraper.py --date 2026-03-15` | Scrape specific date (YYYY-MM-DD) |
| `python test_json_system.py` | Verify system setup |

## 📝 JSON File Format

Each JSON file contains:
```json
{
  "status": "success",
  "data": [
    ["Court", "LastUpdated", "7am-8am", "8am-9am", ...],
    ["Main 01", "14:30:45", "available", "reserved", ...],
    ["Main 02", "14:30:45", "unavailable", "available", ...]
  ],
  "lastUpdated": "14:30:45",
  "date": "2026-03-12"
}
```

## 📚 Documentation

- **[QUICK_REF.md](QUICK_REF.md)** - Quick reference guide
- **[QUICKSTART_JSON.md](QUICKSTART_JSON.md)** - 3-step setup
- **[README_JSON.md](README_JSON.md)** - Complete documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design details
- **[CHANGES.md](CHANGES.md)** - Migration from Flask version

## ✅ Requirements

- Python 3.7+
- `playwright` - Web automation
- `beautifulsoup4` - HTML parsing

No server frameworks needed! Pure static JSON + HTML.

## 🔍 How It Works

### Data Scraping
1. `auto_scraper.py` connects to WebTrac using Playwright
2. Parses HTML with BeautifulSoup
3. Extracts court availability data
4. Stores in SQLite database (backup)
5. Exports to JSON file (primary data source)

### Data Display
1. Open `index.html` in browser
2. JavaScript constructs today's date
3. Fetches corresponding JSON file
4. Renders table with court availability
5. Displays interactive map overlay

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data available" | Run `python auto_scraper.py` first |
| JSON file not found | Verify JSON file exists in project directory |
| Scraper fails | Run `pip install -r requirements.txt` |
| Import errors | Ensure virtual environment is activated |

## 📄 License

Internal use only

## 🙌 Contributing

To contribute or report issues, please use GitHub's issue tracker.

---

**Ready to get started?** See [QUICKSTART_JSON.md](QUICKSTART_JSON.md) for a 3-step setup guide.
