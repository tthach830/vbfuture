# Volleyball Court Availability Tracker

A modern web application for tracking court availability using a SQLite database backend with a Flask API server.

## Architecture

The project now uses a clean SQLite-based architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    index.html (Frontend)                     │
│              (Browser-based UI for viewing/updating)         │
└────────────────────────┬───────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │ /api/data, /api/update
                         │
┌────────────────────────▼───────────────────────────────────┐
│                   app.py (Flask API)                        │
│              (REST API server on port 5000)                 │
└────────────────────────┬───────────────────────────────────┘
                         │
                         │ SQL Queries
                         │ READ/WRITE
                         │
┌────────────────────────▼───────────────────────────────────┐
│              volleyball.db (SQLite Database)                │
│           (Persistent data storage for courts/slots)        │
└────────────────────────┬───────────────────────────────────┘
                         │
                         │ Data Import
                         │
┌────────────────────────▼───────────────────────────────────┐
│            auto_scraper.py (Web Scraper)                   │
│        (Scrapes WebTrac and populates database)            │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. **auto_scraper.py** - Data Collection
- Scrapes court availability from WebTrac using Playwright
- Parses HTML with BeautifulSoup
- Stores data in SQLite database (`volleyball.db`)
- Runs on a schedule or manually

### 2. **volleyball.db** - Data Storage
SQLite database with two tables:

#### `courts` table:
```sql
CREATE TABLE courts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
```

#### `slots` table:
```sql
CREATE TABLE slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    court_id INTEGER,
    time_slot TEXT,
    status TEXT,
    date TEXT,
    FOREIGN KEY(court_id) REFERENCES courts(id)
)
```

### 3. **app.py** - API Server
Flask REST API that serves data from the SQLite database:

#### Endpoints:
- `GET /api/data` - Get all court availability
  - Query parameter: `date` (optional, defaults to today)
  - Returns: Table data in 2D array format

- `POST /api/update` - Update court availability status
  - Body: `{courtName, timeSlot, newStatus, date}`
  - Returns: Confirmation with timestamp

- `GET /api/status` - Get database statistics
  - Returns: Court count, slot count, latest date with data

### 4. **index.html** - Frontend UI
Modern web interface that:
- Fetches data from the Flask API
- Displays court availability in an interactive table
- Shows visual map overlay with court locations
- Allows toggling court availability (with password protection)
- Auto-refreshes displays

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

The key dependencies are:
- `playwright` - Web scraping
- `beautifulsoup4` - HTML parsing
- `Flask` - REST API server

### 2. Database Setup
The database is automatically created on first run. Tables are initialized with:
- `auto_scraper.py` (when scraping)
- `app.py` (when starting the server)

### 3. Court Configuration
Edit the court coordinates in `index.html` (around line 620):
```javascript
const courtCoords = [
    { "court": "Main 01", "x": 124, "y": 538 },
    // ... more courts
];
```

## Usage

### Starting the Application

**Step 1: Run the scraper** (collects data from WebTrac)
```bash
python auto_scraper.py
# or with specific date in MMDDYYYY format:
python auto_scraper.py 03122026
# or with --date flag in YYYY-MM-DD format:
python auto_scraper.py --date 2026-03-12
```

**Step 2: Start the Flask API server** (serves the web interface)
```bash
python app.py
```

The server will start on `http://localhost:5000`

**Step 3: Open in browser**
```
http://localhost:5000
```

### Data Flow

1. **Scraping**: Run `auto_scraper.py` to fetch the latest court availability from WebTrac
   - This populates/updates the `volleyball.db` database
   - Stores status (available/unavailable/reserved) for each court and time slot

2. **API Service**: Run `app.py` to start the Flask server
   - Reads from database
   - Serves HTTP API for the frontend
   - Handles updates to court availability

3. **Frontend**: Open `index.html` in browser
   - Displays data from API in table and map formats
   - Allows manual updates (with password protection)
   - Updates persist to database

## Security

The application includes password protection for modifying court availability:
- Default passcode: `john316` (edit in `index.html` if needed)
- Uses browser localStorage for session management
- Can be reset using the "Reset Session" link

## Database Queries

### View all courts:
```sql
SELECT * FROM courts;
```

### View all time slots for today:
```sql
SELECT DISTINCT time_slot FROM slots 
WHERE date = date('now') 
ORDER BY time_slot;
```

### Check court availability:
```sql
SELECT c.name, s.time_slot, s.status 
FROM slots s
JOIN courts c ON s.court_id = c.id
WHERE c.name = 'Main 01' AND s.date = date('now')
ORDER BY s.time_slot;
```

### Update status (without API):
```sql
UPDATE slots 
SET status = 'unavailable' 
WHERE court_id = (SELECT id FROM courts WHERE name = 'Main 01')
AND time_slot = '2pm-3pm';
```

## Troubleshooting

### "Database not found" error
- Run `auto_scraper.py` first to populate the database
- Check that `volleyball.db` exists in the project directory

### "Cannot connect to API" in browser
- Make sure `app.py` is running
- Check that port 5000 is not blocked
- Verify Flask server output shows "Running on http://localhost:5000"

### No data showing in the table
- Run `auto_scraper.py` to scrape and populate data
- Check database: `sqlite3 volleyball.db "SELECT COUNT(*) FROM slots;"`
- Verify API endpoint: `http://localhost:5000/api/status`

### Changes not persisting
- Make sure you're using the correct password
- Check browser console for errors (F12)
- Verify `app.py` is running and receiving POST requests

## Configuration Files

- `requirements.txt` - Python dependencies
- `auto_scraper.py` - Scraper configuration and logic
- `app.py` - Flask API server configuration
- `index.html` - Frontend UI and API endpoints
- `volleyball.db` - SQLite database (auto-created)

## Future Enhancements

- Add scheduling (e.g., run scraper hourly via APScheduler)
- Add authentication for API endpoints
- Add more detailed logging
- Add data export/import functionality
- Add historical tracking and analytics
- Deploy using Docker or cloud platform

## License

Internal use only
