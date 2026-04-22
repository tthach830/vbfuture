import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sqlite3
import sys
import json
import os
import re

DB_PATH = 'volleyball.db'
JSON_DIR = 'json'
REAL_COURT_PREFIX = 'Main Beach Volleyball Court '
LEGACY_COURTS = (
    'Dream 1',
    'Dream 2',
    'Harbor 1',
    'Harbor 2',
    'Harbor 3',
    'Harbor 4',
)


def parse_target_date(specific_date=None):
    if not specific_date:
        return datetime.datetime.now()

    for date_format in ("%m%d%Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(specific_date, date_format)
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date format '{specific_date}'. Please use MMDDYYYY or YYYY-MM-DD."
    )


def ensure_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS courts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            court_id INTEGER,
            time_slot TEXT,
            status TEXT,
            date TEXT,
            FOREIGN KEY(court_id) REFERENCES courts(id)
        )
    ''')

    try:
        c.execute('ALTER TABLE slots ADD COLUMN date TEXT')
    except sqlite3.OperationalError:
        pass

    c.execute('CREATE INDEX IF NOT EXISTS idx_slots_date ON slots(date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_slots_court_time_date ON slots(court_id, time_slot, date)')

    conn.commit()
    conn.close()


def format_hour_label(dt):
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    suffix = 'am' if dt.hour < 12 else 'pm'
    return f"{hour}{suffix}"


def parse_hour_token(hour_token, meridiem_token):
    hour = int(hour_token)
    meridiem = meridiem_token.lower()
    if hour == 12:
        hour = 0
    if meridiem == 'pm':
        hour += 12
    return hour


def normalize_time_slot(time_slot):
    slot = str(time_slot).strip().lower()
    match = re.match(
        r'^0?(\d{1,2})(?::\d{2})?\s*(am|pm)\s*-\s*0?(\d{1,2})(?::\d{2})?\s*(am|pm)$',
        slot,
    )
    if not match:
        return None, None

    start_hour_24 = parse_hour_token(match.group(1), match.group(2))
    end_hour_24 = parse_hour_token(match.group(3), match.group(4))

    start_label = format_hour_label(datetime.datetime(2000, 1, 1, start_hour_24, 0))
    end_label = format_hour_label(datetime.datetime(2000, 1, 1, end_hour_24, 0))
    return f"{start_label}-{end_label}", start_hour_24


def remove_legacy_courts(conn):
    c = conn.cursor()
    placeholders = ', '.join('?' for _ in LEGACY_COURTS)
    c.execute(
        f'''DELETE FROM slots
            WHERE court_id IN (
                SELECT id FROM courts WHERE name IN ({placeholders})
            )''',
        LEGACY_COURTS,
    )
    c.execute(f'DELETE FROM courts WHERE name IN ({placeholders})', LEGACY_COURTS)


def ensure_json_directory():
    os.makedirs(JSON_DIR, exist_ok=True)


def get_json_filepath(target_date):
    return os.path.join(JSON_DIR, target_date.strftime("%m%d%Y") + ".json")


def cleanup_old_json_files(today_date=None):
    if today_date is None:
        today_date = datetime.date.today()

    ensure_json_directory()

    removed_files = []
    json_pattern = re.compile(r'^(\d{8})\.json$')

    for filename in os.listdir(JSON_DIR):
        match = json_pattern.match(filename)
        if not match:
            continue

        try:
            file_date = datetime.datetime.strptime(match.group(1), "%m%d%Y").date()
        except ValueError:
            continue

        if file_date < today_date:
            try:
                file_path = os.path.join(JSON_DIR, filename)
                os.remove(file_path)
                removed_files.append(file_path)
            except OSError as exc:
                print(f"Warning: Could not delete {filename}: {exc}")

    if removed_files:
        print(f"Deleted {len(removed_files)} old JSON file(s):")
        for removed in sorted(removed_files):
            print(f" - {removed}")
    else:
        print("No old JSON files found to delete.")

    return removed_files

def run_scraper(specific_date=None, export_json=True):
    # 1. Determine target date
    try:
        target_date = parse_target_date(specific_date)
    except ValueError as exc:
        print(f"Error: {exc}")
        return False

    url_date = target_date.strftime("%m%%2F%d%%2F%Y")
    display_date = target_date.strftime("%B %d, %Y")
    header_date = target_date.strftime("%B %d")
    
    base_url = "https://casantacruzweb.myvscloud.com/webtrac/web/search.html?Action=Start&SubAction=&_csrf_token=xk0W0R6N0C712M2S3A2O2E4A4P4H6O6A055Q5H505203035W595T1B6W3Q6I581C5I4P4O6A1H5I4V57536M6S4J5K69016W5W6M5V17704M5D68076D4E6G471C5V4J6J&date="
    end_url = "&keyword=&primarycode=&frheadcount=0&type=Beach+Volleyball+Court&frclass=&keywordoption=Match+One&blockstodisplay=15&features1=&features2=&features3=&features4=&features5=&features6=&features7=&features8=&begintime=12%3A00+am&subtype=&category=&features=&display=Detail&module=FR&multiselectlist_value=&frwebsearch_buttonsearch=yes"
    
    target_url = base_url + url_date + end_url
    print(f"Scraping availability for today: {display_date}")

    # 2. Ensure Database structure exists early
    ensure_database()

    # 3. Use Playwright to load the page and extract HTML
    print("Launching headless browser...")
    with sync_playwright() as p:
        # Some WebTrac portals block basic Headless Chrome signatures
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        print(f"Navigating to {target_url}")
        
        try:
            # Load page and wait for general network quietness
            print(f"Navigating to {target_url}...")
            page.goto(target_url, wait_until="domcontentloaded", timeout=90000)
            
            # Wait a few seconds for any dynamic JS to settle
            page.wait_for_timeout(5000)
            
            # WebTrac often uses a specific table or grid container that takes a moment to render
            print("Waiting for schedule grid to render...")
            
            # Wait for either the grid rows or a known "no results" message
            try:
                page.wait_for_selector('.ui-grid-row, .facility-schedule-block, table', timeout=20000)
            except:
                print("Specific grid selectors not found, falling back to static wait just in case...")
                page.wait_for_timeout(10000)
            
            html_content = page.content()
            
        except Exception as e:
            print(f"Error loading page or finding grid: {e}")
            page.screenshot(path="error_screenshot.png", full_page=True)
            print("Saved error screenshot to error_screenshot.png")
            html_content = page.content()
            
        browser.close()
        
    print("Browser closed. Parsing data...")
    
    # 3. Use BeautifulSoup to parse the layout
    soup = BeautifulSoup(html_content, 'html.parser')
    court_data = []
    
    # helper to explode time ranges like "4:00 pm - 6:00 pm" into individual hours
    def get_hours_in_range(time_range_str):
        # Clean the string (remove "Unavailable", etc.)
        clean_str = time_range_str.split('\n')[0].strip() # Handles some WebTrac multiline labels
        if ' - ' not in clean_str:
            return [clean_str]
            
        try:
            start_str, end_str = clean_str.split(' - ')
            start_dt = datetime.datetime.strptime(start_str.strip(), "%I:%M %p")
            end_dt = datetime.datetime.strptime(end_str.strip(), "%I:%M %p")
            
            hours = []
            current = start_dt
            while current < end_dt:
                next_hour = current + datetime.timedelta(hours=1)
                # Formats like '7am-8am' or '12pm-1pm'
                current_str = format_hour_label(current)
                next_str = format_hour_label(next_hour)
                hours.append(f"{current_str}-{next_str}")
                current = next_hour
            return hours
        except:
            return [clean_str]

    # Find all facility result items
    results = soup.select('.result-content')
    if not results:
        print("Error: No results found with '.result-content'. Trying fallback table search...")
        # Fallback if the site structure changes slightly
        results = soup.select('table#frwebsearch_output_table')

    for res in results:
        # Get Court Name
        h2 = res.find('h2')
        if not h2: continue
        facility_name = h2.get_text(strip=True)
        
        # Only process if it's one of our courts
        if "Beach Volleyball Court" not in facility_name:
            continue
            
        available_slots = []
        booked_slots = []
        
        # Find all slot buttons
        # Based on dump: <a class="button full-block success..." ...> 7:00 am - 8:00 am</a>
        # success = available, error = booked
        slots = res.select('.cart-blocks a.button')
        
        for slot in slots:
            time_text = slot.get_text(separator=" ", strip=True) # "4:00 pm - 6:00 pm Unavailable"
            # Remove the "Unavailable" or "Inquiry Only" text if present
            time_text = time_text.replace("Unavailable", "").replace("Inquiry Only", "").strip()
            
            classes = slot.get('class', [])
            is_booked = 'error' in classes
            
            exploded = get_hours_in_range(time_text)
            if is_booked:
                booked_slots.extend(exploded)
            else:
                available_slots.extend(exploded)
                
        if available_slots or booked_slots:
            court_data.append({
                "facility": facility_name,
                "available_slots": available_slots,
                "booked_slots": booked_slots
            })

    if not court_data:
        print("Error: Could not find court data on the page. The WebTrac layout may have changed.")
        # Save HTML for debugging if this happens
        with open('failed_parse_dump.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        return

    print("Data extracted successfully. Updating database...")
    
    # 4. Update Database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    remove_legacy_courts(conn)
    
    # Clear old slots for this specific date only (so we can re-run same day safely)
    target_date_str = target_date.strftime("%Y-%m-%d")
    c.execute('DELETE FROM slots WHERE date = ?', (target_date_str,))
    
    for court in court_data:
        c.execute("INSERT OR IGNORE INTO courts (name) VALUES (?)", (court['facility'],))
        c.execute("SELECT id FROM courts WHERE name = ?", (court['facility'],))
        court_id = c.fetchone()[0]
        
        for slot in court['available_slots']:
            c.execute("INSERT INTO slots (court_id, time_slot, status, date) VALUES (?, ?, ?, ?)", (court_id, slot, 'available', target_date_str))
            
        for slot in court['booked_slots']:
            c.execute("INSERT INTO slots (court_id, time_slot, status, date) VALUES (?, ?, ?, ?)", (court_id, slot, 'reserved', target_date_str))
            
    conn.commit()
    conn.close()
    
    # 5. Export data to JSON file
    if export_json:
        export_to_json(target_date)
    
    print("Database updated successfully!")
    return True


def run_scraper_range(start_date=None, days=1, export_json=True):
    try:
        first_date = parse_target_date(start_date)
    except ValueError as exc:
        print(f"Error: {exc}")
        return False

    if days < 1:
        print("Error: --days must be at least 1.")
        return False

    ensure_database()

    failures = []
    import time
    import random
    for offset in range(days):
        current_date = first_date + datetime.timedelta(days=offset)
        current_date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n{'=' * 60}")
        print(f"Scraping day {offset + 1} of {days}: {current_date_str}")
        print(f"{'=' * 60}")

        if not run_scraper(specific_date=current_date_str, export_json=export_json):
            failures.append(current_date_str)
            
        # Add a random delay between days (but not after the last day) to avoid Cloudflare rate limiting
        if offset < days - 1:
            delay = random.uniform(30, 90)
            print(f"Waiting {delay:.1f} seconds before next scrape to avoid rate limits...")
            time.sleep(delay)

    if failures:
        print("\nScrape completed with failures for:")
        for failed_date in failures:
            print(f" - {failed_date}")
        return False

    if export_json:
        cleanup_old_json_files()

    print(f"\nSuccessfully scraped {days} day(s) starting from {first_date.strftime('%Y-%m-%d')}.")
    return True

def export_to_json(target_date):
    """Export court availability data to JSON file for the given date"""
    try:
        target_date_str = target_date.strftime("%Y-%m-%d")
        ensure_json_directory()
        json_filename = get_json_filepath(target_date)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        remove_legacy_courts(conn)
        conn.commit()
        
        # Get all courts
        c.execute(
            'SELECT DISTINCT name FROM courts WHERE name LIKE ? ORDER BY name',
            (f'{REAL_COURT_PREFIX}%',),
        )
        courts = [row[0] for row in c.fetchall()]
        
        if not courts:
            print("No courts found in database for JSON export")
            conn.close()
            return
        
        # Get all time slots for this date
        c.execute('''
            SELECT DISTINCT time_slot FROM slots 
            WHERE date = ?
        ''', (target_date_str,))

        normalized_slots = {}
        for row in c.fetchall():
            normalized_slot, start_hour_24 = normalize_time_slot(row[0])
            if normalized_slot is None:
                continue
            if start_hour_24 < 8 or start_hour_24 > 21:
                continue
            normalized_slots[normalized_slot] = start_hour_24

        time_slots = [
            slot_name
            for slot_name, _ in sorted(normalized_slots.items(), key=lambda item: item[1])
        ]
        
        # Build the data table
        data = []
        
        # Header row
        header = ['Court'] + time_slots
        data.append(header)
        
        # Data rows
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        for court_name in courts:
            row = [court_name]
            
            # Get court ID
            c.execute('SELECT id FROM courts WHERE name = ?', (court_name,))
            court_result = c.fetchone()
            if not court_result:
                continue
            
            court_id = court_result[0]
            
            c.execute('''
                SELECT time_slot, status FROM slots
                WHERE court_id = ? AND date = ?
            ''', (court_id, target_date_str))

            status_by_slot = {}
            for raw_slot, raw_status in c.fetchall():
                normalized_slot, start_hour_24 = normalize_time_slot(raw_slot)
                if normalized_slot is None:
                    continue
                if start_hour_24 < 8 or start_hour_24 > 21:
                    continue

                existing_status = status_by_slot.get(normalized_slot)
                new_status = (raw_status or 'unknown').lower()
                if existing_status is None:
                    status_by_slot[normalized_slot] = new_status
                elif existing_status == 'available' and new_status != 'available':
                    status_by_slot[normalized_slot] = new_status

            for time_slot in time_slots:
                row.append(status_by_slot.get(time_slot, 'unknown'))
            
            data.append(row)
        
        # Create JSON structure
        json_data = {
            'status': 'success',
            'data': data,
            'lastUpdated': timestamp,
            'date': target_date_str
        }
        
        # Write to JSON file
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"Exported data to {json_filename}")
        conn.close()
        
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        import traceback
        traceback.print_exc()

import argparse
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WebTrac Court Availability Scraper")
    parser.add_argument("positional_date", nargs="?", help="Optional Target date in MMDDYYYY format for backward compatibility")
    parser.add_argument("--date", help="The target date to scrape (MMDDYYYY or YYYY-MM-DD format).")
    parser.add_argument("--days", type=int, default=1, help="Number of consecutive days to scrape starting from --date or today.")
    parser.add_argument("--skip-json", action="store_true", help="Store results in SQLite only and skip JSON export.")
    parser.add_argument("--cleanup-old-json", action="store_true", help="Delete MMDDYYYY.json files older than today.")
    args = parser.parse_args()

    if args.cleanup_old_json:
        cleanup_old_json_files()
    
    date_arg = args.date if args.date else args.positional_date
    success = run_scraper_range(start_date=date_arg, days=args.days, export_json=not args.skip_json)
    if not success:
        sys.exit(1)