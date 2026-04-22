#!/usr/bin/env python3
"""
Test script to verify the JSON system is working correctly
"""
import json
import os
import sys
from datetime import datetime

def test_imports():
    """Test that required modules can be imported"""
    print("\n" + "="*60)
    print("TEST 1: Checking Imports")
    print("="*60)
    
    try:
        import playwright
        print("[OK] playwright installed")
    except ImportError:
        print("[FAIL] playwright NOT installed")
        return False
    
    try:
        import bs4
        print("[OK] beautifulsoup4 installed")
    except ImportError:
        print("[FAIL] beautifulsoup4 NOT installed")
        return False
    
    try:
        import auto_scraper
        print("[OK] auto_scraper.py loads successfully")
    except Exception as e:
        print(f"[FAIL] auto_scraper.py error: {e}")
        return False
    
    return True

def test_json_structure():
    """Test JSON file structure"""
    print("\n" + "="*60)
    print("TEST 2: JSON File Structure")
    print("="*60)
    
    # Create sample JSON
    sample_json = {
        "status": "success",
        "data": [
            ["Court", "LastUpdated", "7am-8am", "8am-9am"],
            ["Main 01", "14:30:45", "available", "reserved"],
            ["Main 02", "14:30:45", "unavailable", "available"]
        ],
        "lastUpdated": "14:30:45",
        "date": "2026-03-12"
    }
    
    try:
        json_str = json.dumps(sample_json, indent=2)
        parsed = json.loads(json_str)
        print("[OK] JSON structure is valid")
        print("[OK] Can be serialized and deserialized")
        return True
    except Exception as e:
        print(f"[FAIL] JSON error: {e}")
        return False

def test_file_format():
    """Test filename format"""
    print("\n" + "="*60)
    print("TEST 3: Filename Format")
    print("="*60)
    
    now = datetime.now()
    json_filename = now.strftime("%m%d%Y") + ".json"
    
    print(f"Today's date: {now.strftime('%B %d, %Y')}")
    print(f"JSON filename: {json_filename}")
    
    # Test format
    parts = json_filename.replace(".json", "")
    if len(parts) == 8 and parts.isdigit():
        print(f"[OK] Filename format is correct (MMDDYYYY.json)")
        return True
    else:
        print(f"[FAIL] Filename format is incorrect")
        return False

def test_html_json_loading():
    """Check if index.html has JSON loading code"""
    print("\n" + "="*60)
    print("TEST 4: HTML JSON Integration")
    print("="*60)
    
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        if ".json" in content:
            print("[OK] index.html references .json files")
        else:
            print("[FAIL] index.html doesn't reference .json files")
            return False
        
        if "fetch(" in content and "json" in content.lower():
            print("[OK] index.html has JSON fetch functionality")
        else:
            print("[FAIL] index.html missing JSON fetch")
            return False
        
        if "renderTableData" in content:
            print("[OK] index.html has table rendering code")
        else:
            print("[FAIL] index.html missing table rendering")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error reading HTML: {e}")
        return False

def test_scraper_json_export():
    """Check if scraper has JSON export"""
    print("\n" + "="*60)
    print("TEST 5: Scraper JSON Export")
    print("="*60)
    
    try:
        with open("auto_scraper.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "export_to_json" in content:
            print("[OK] auto_scraper.py has export_to_json function")
        else:
            print("[FAIL] auto_scraper.py missing export_to_json")
            return False
        
        if "json.dump" in content:
            print("[OK] auto_scraper.py exports to JSON")
        else:
            print("[FAIL] auto_scraper.py doesn't export JSON")
            return False
        
        if ".json" in content:
            print("[OK] auto_scraper.py creates .json files")
        else:
            print("[FAIL] auto_scraper.py doesn't create .json files")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error reading scraper: {e}")
        return False

def check_flask_removed():
    """Verify Flask has been removed"""
    print("\n" + "="*60)
    print("TEST 6: Flask Cleanup")
    print("="*60)
    
    removed = []
    remaining = []
    
    files_to_check = ["app.py", "start.bat", "verify_setup.py"]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            remaining.append(filename)
            print(f"[FAIL] {filename} still exists (should be removed)")
        else:
            removed.append(filename)
            print(f"[OK] {filename} removed")
    
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            req_content = f.read()
        
        if "Flask" not in req_content:
            print("[OK] Flask removed from requirements.txt")
        else:
            print("[FAIL] Flask still in requirements.txt")
            return False
        
        if "google" not in req_content.lower():
            print("[OK] Google Sheets packages removed from requirements.txt")
        else:
            print("[FAIL] Google packages still in requirements.txt")
            return False
        
    except Exception as e:
        print(f"[FAIL] Error reading requirements.txt: {e}")
        return False
    
    return len(remaining) == 0

def main():
    print("\n" + "="*70)
    print("VOLLEYBALL COURT TRACKER - JSON SYSTEM VERIFICATION")
    print("="*70)
    
    results = {
        "Imports": test_imports(),
        "JSON Structure": test_json_structure(),
        "Filename Format": test_file_format(),
        "HTML JSON Integration": test_html_json_loading(),
        "Scraper JSON Export": test_scraper_json_export(),
        "Flask Cleanup": check_flask_removed(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    all_pass = all(results.values())
    
    print("\n" + "="*60)
    if all_pass:
        print("[OK] All tests passed! System is ready.")
        print("\nQuick start:")
        print("  1. python auto_scraper.py       (scrape data)")
        print("  2. open index.html               (view in browser)")
        print("="*60 + "\n")
        return 0
    else:
        print("[FAIL] Some tests failed. Check the issues above.")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
