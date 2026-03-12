# Quick Start Guide

## System Components

The new system uses SQLite backend instead of Google Sheets:

```
Web Scraper → SQLite Database → Flask API Server → Web Browser
(auto_scraper.py) → (volleyball.db) → (app.py) → (index.html)
```

## Installation (Windows PowerShell)

### Step 1: Activate Virtual Environment
```powershell
& .\.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

## Running the System

### Option A: Full Workflow (Recommended)

**Terminal 1 - Run Scraper:**
```powershell
python auto_scraper.py
```
This scrapes WebTrac and populates the SQLite database.

**Terminal 2 - Start API Server:**
```powershell
python app.py
```
This starts the Flask server on http://localhost:5000

**Browser:**
Open http://localhost:5000 to view the web interface

---

### Option B: Quick Verify

Check system setup before running:
```powershell
python verify_setup.py
```

This verifies:
- ✓ Database exists and is configured
- ✓ Flask is installed  
- ✓ Scraper dependencies are available
- ✓ Frontend is set up correctly

---

## Common Commands

### Scrape today's data (current date)
```powershell
python auto_scraper.py
```

### Scrape for a specific date (MMDDYYYY format)
```powershell
python auto_scraper.py 03122026
```

### Scrape for a specific date (YYYY-MM-DD format)
```powershell
python auto_scraper.py --date 2026-03-12
```

### View database stats
```powershell
python -c "import sqlite3; conn = sqlite3.connect('volleyball.db'); print(f'Courts: {conn.cursor().execute(\"SELECT COUNT(*) FROM courts\").fetchone()[0]}'); print(f'Slots: {conn.cursor().execute(\"SELECT COUNT(*) FROM slots\").fetchone()[0]}')"
```

### Check a specific court
```powershell
python -c "import sqlite3; conn = sqlite3.connect('volleyball.db'); rows = conn.cursor().execute('SELECT s.time_slot, s.status FROM slots s JOIN courts c ON s.court_id = c.id WHERE c.name=\"Main 01\" LIMIT 5').fetchall(); print('\n'.join([f'{t}: {s}' for t, s in rows]))"
```

---

## File Descriptions

### Core Files
| File | Purpose |
|------|---------|
| `auto_scraper.py` | Scrapes WebTrac and stores in SQLite |
| `app.py` | Flask REST API server |
| `index.html` | Web interface |
| `volleyball.db` | SQLite database (created automatically) |

### Configuration
| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `verify_setup.py` | System verification script |
| `README_SQLITE.md` | Full documentation |
| `QUICKSTART.md` | This file |

---

## API Endpoints

Once Flask server is running at http://localhost:5000:

### Get Current Data
```
GET http://localhost:5000/api/data
```
Returns today's court availability

### Get Data for Specific Date
```
GET http://localhost:5000/api/data?date=2026-03-12
```

### Update Court Status
```
POST http://localhost:5000/api/update
Content-Type: application/json

{
  "courtName": "Main 01",
  "timeSlot": "2pm-3pm", 
  "newStatus": "unavailable"
}
```

### Check Server Status
```
GET http://localhost:5000/api/status
```

---

## Troubleshooting

### Port 5000 Already in Use
If Flask won't start, port 5000 might be taken:
```powershell
# Find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### No Data Showing
1. Check scraper ran: `python auto_scraper.py`
2. Verify data exists:
   ```powershell
   python -c "import sqlite3; c=sqlite3.connect('volleyball.db').cursor(); print(c.execute('SELECT COUNT(*) FROM slots').fetchone()[0], 'slots')"
   ```

### Database Locked
If you get "database is locked" error:
- Only one writer at a time to SQLite
- Make sure only one instance of app.py is running
- Close any SQLite browser/tools with the file open

### Browser Shows "Cannot Connect to Server"
- Make sure `python app.py` is running
- Check if Flask startup messages appear in terminal
- Verify with: `curl http://localhost:5000/api/status`

---

## Database Schema

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

Valid status values: `available`, `unavailable`, `reserved`

---

## Next Steps

1. Read [README_SQLITE.md](README_SQLITE.md) for detailed documentation
2. Run `python verify_setup.py` to confirm everything works
3. Execute `python auto_scraper.py` to populate initial data
4. Start Flask server with `python app.py`
5. Open http://localhost:5000 in your browser

---

## Need Help?

Check these before asking:
- [ ] Virtual environment activated? (`.venv\Scripts\Activate.ps1`)
- [ ] Dependencies installed? (`pip install -r requirements.txt`)
- [ ] Scraper ran? (`python auto_scraper.py`)
- [ ] Flask server running? (`python app.py`)
- [ ] Using correct browser URL? (`http://localhost:5000`)

Errors often indicate one of these steps was skipped.
