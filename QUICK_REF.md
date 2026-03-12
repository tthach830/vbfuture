# Quick Reference Guide

## System Overview
**Volleyball Court Availability Tracker** using JSON files and SQLite

```
Scraper → JSON Files → Browser
auto_scraper.py → json/MMDDYYYY.json → index.html
```

---

## Installation (One-Time)
```bash
pip install -r requirements.txt
```

This installs:
- `playwright` - Web scraping
- `beautifulsoup4` - HTML parsing

---

## Basic Usage

### 1. Scrape Data for Today
```bash
python auto_scraper.py
```
Creates: `json/03122026.json` (MMDDYYYY format)

### 2. Scrape Data for Specific Date
```bash
python auto_scraper.py 03152026
```
Creates: `json/03152026.json`

### 3. View Data in Browser
Open: `index.html` (double-click or drag to browser)

The page automatically loads today's data from the JSON file.

---

## File Locations

| File | Purpose |
|------|---------|
| `auto_scraper.py` | Scraper script |
| `index.html` | Web interface |
| `volleyball.db` | SQLite backup (optional) |
| `json/03122026.json` | Today's data (auto-created) |
| `requirements.txt` | Python dependencies |

---

## Common Commands

| What | Command |
|------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Scrape today | `python auto_scraper.py` |
| Scrape date MMDDYYYY | `python auto_scraper.py 03152026` |
| Scrape date YYYY-MM-DD | `python auto_scraper.py --date 2026-03-15` |
| List data files | `dir *.json` (Windows) or `ls *.json` (Mac/Linux) |
| View data | Open `index.html` in browser |
| Verify setup | `python test_json_system.py` |

---

## How It Works

### Data Scraping
```
python auto_scraper.py
    ↓
Connects to WebTrac
    ↓
Extracts court availability
    ↓
Saves to volleyball.db (SQLite)
    ↓
Exports to MMDDYYYY.json
    ↓
Done - JSON file ready
```

### Data Display
```
Open index.html in browser
    ↓
JavaScript constructs date (03122026)
    ↓
Fetches json/03122026.json
    ↓
If found: Display table + map
If not found: Show "Run scraper" message
```

---

## JSON File Format

Example: `03122026.json`
```json
{
  "status": "success",
  "data": [
    ["Court", "LastUpdated", "7am-8am", "8am-9am", ...],
    ["Main 01", "14:30:45", "available", "reserved", ...],
    ["Main 02", "14:30:45", "available", "available", ...]
  ],
  "lastUpdated": "14:30:45",
  "date": "2026-03-12"
}
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No data available" message | Run `python auto_scraper.py` first |
| JSON file not found | Check that JSON file exists in `json/` directory |
| Scraper fails | Verify: `pip install -r requirements.txt` |
| Old data showing | Delete old JSON files or run new scrape |
| Permission denied | Use `python` not `py` on Windows |

---

## File Characteristics

- **Scraper**: Runs from command line
- **HTML**: Opens directly in browser (no server needed)
- **JSON**: One file per date in `json/` (MMDDYYYY.json)
- **Size**: Each JSON file ~10-30 KB
- **Database**: SQLite file (optional backup)

---

## Example Workflow

```bash
# Day 1: Scrape Monday
python auto_scraper.py
# Creates: json/03102026.json

# Open in browser
# Shows Monday's data

# Day 2: Scrape Tuesday
python auto_scraper.py 03112026
# Creates: json/03112026.json

# Refresh browser or open index.html again
# Now shows Tuesday's data

# Day 3: View historical data
# Manual edit to browser:
# Change filename in JS or create link to old JSON
```

---

## No Server Needed

✓ Pure client-side rendering
✓ Works with `file://` protocol
✓ Just open index.html in browser
✓ No Flask, no API, no ports to configure

---

## Documentation Files

- **QUICKSTART_JSON.md** - Quick setup (3 steps)
- **README_JSON.md** - Full documentation
- **ARCHITECTURE.md** - System design details
- **CHANGES.md** - What changed from Flask version
- **test_json_system.py** - Verification script

---

## Next Steps

1. Install: `pip install -r requirements.txt`
2. Scrape: `python auto_scraper.py`
3. View: Open `index.html` in browser
4. Read: See `QUICKSTART_JSON.md` or `README_JSON.md`

---

**That's it!** Simple, fast, no complex setup needed.
