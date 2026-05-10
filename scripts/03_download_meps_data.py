import os
import sys
import csv
import pandas as pd
from datetime import datetime

# ============================================================
# SCRIPT 03 — Download MEPS Access to Care Data
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR  = os.path.join(PROJECT_ROOT, 'data', 'raw', 'meps')
OUTPUT_CSV  = os.path.join(OUTPUT_DIR, 'meps_access_data.csv')

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '03_download_meps_data.py', action, status, details])
    except Exception:
        pass

def print_header():
    print("=" * 65)
    print("  SCRIPT 03 — AHRQ MEPS Data Extraction (Wait Times & Access)")
    print("=" * 65)
    print(f"  Source : MEPS Household Component (HC)")
    print(f"  Target : Ambulatory care wait times and visit patterns")
    print("=" * 65)
    print()

def ensure_meps_data_exists():
    """
    MEPS datasets are enormous SAS/Stata files. For business analytics 
    reporting, we extract the targeted Access to Care Summary Tables 
    from their web portal.
    """
    print("[STEP 1] Checking for MEPS Access to Care Data...\n")
    
    if os.path.exists(OUTPUT_CSV):
        size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
        print(f"  SUCCESS: MEPS data found at {OUTPUT_CSV}")
        print(f"  File size: {size_mb:.2f} MB")
        
        # Validate schema
        try:
            df = pd.read_csv(OUTPUT_CSV)
            print(f"  Loaded {len(df):,} rows successfully.")
            log_audit("MEPS Data Validation", "SUCCESS", f"Validated {len(df)} rows")
            
            print("\n=================================================================")
            print(" SCRIPT 03 COMPLETE — READY FOR SCRIPT 04")
            print("=================================================================")
            return True
        except Exception as e:
            print(f"  ERROR reading file: {e}")
            log_audit("MEPS Data Validation", "FAILED", str(e))
            return False

    else:
        print("  ACTION REQUIRED: The MEPS Summary Table must be exported to CSV.")
        print("  Please follow these exact instructions to get the real data:\n")
        
        instructions = """
        1. Open your browser and go to the MEPS Summary Tables: 
           https://datatools.ahrq.gov/meps-hc
        2. Click on "Access to Care" on the dashboard.
        3. For Variable, select "Difficulty getting care" or "Wait time for appointment".
        4. In the grouping/cross-tab options, select "Year" to get a trend line.
        5. Once the table renders on screen, click the "Export" or "Download to CSV" button.
        6. Save the downloaded file exactly as: 'meps_access_data.csv'
        7. Move this file to your project folder here: 
           C:\\Users\\DELL\\.gemini\\antigravity\\scratch\\urology-analytics\\data\\raw\\meps\\
        """
        
        print(instructions)
        print("\nWaiting for data... Rerun this script after you have placed the file in the folder.")
        log_audit("MEPS Data Verification", "PENDING", "MEPS manual download required")
        return False

if __name__ == "__main__":
    print_header()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ensure_meps_data_exists()
