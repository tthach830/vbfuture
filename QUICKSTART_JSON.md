# Quick Start - JSON Version

Three simple steps to run the system:

## Step 1: Install Dependencies (one time)
```bash
pip install -r requirements.txt
```

## Step 2: Run the Scraper
```bash
python auto_scraper.py
```

This scrapes WebTrac and creates a JSON file (`03122026.json` for today).

## Step 3: Open in Browser
Open `index.html` in your web browser.

---

## That's it!

The page will automatically display the court availability from the JSON file.

### For Different Dates

Scrape a specific date:
```bash
python auto_scraper.py 03152026
```

Then open `index.html` again and it will load that date's data.

### File Examples

- `03122026.json` - March 12, 2026
- `03132026.json` - March 13, 2026
- `03142026.json` - March 14, 2026

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No data showing | Run `python auto_scraper.py` first |
| "No data available" message | Check that JSON file matches today's date |
| Scraper fails | Run `pip install -r requirements.txt` |

## More Help

See `README_JSON.md` for detailed documentation.
