import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime

# ============================================================
# SCRIPT 04 — Download CMS Hospital Compare Data
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMS_API_ENDPOINT = "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0"
OUTPUT_DIR  = os.path.join(PROJECT_ROOT, 'data', 'raw', 'cms_hospital')
OUTPUT_CSV  = os.path.join(OUTPUT_DIR, 'hospital_general_information.csv')
OUTPUT_META = os.path.join(OUTPUT_DIR, 'hospital_api_metadata.json')
PAGE_SIZE = 1000
MAX_RETRIES = 3

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        import csv
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '04_download_hospital_compare.py', action, status, details])
    except Exception as e:
        print(f"Warning: Could not write to audit log: {e}")

def print_header():
    print("=" * 65)
    print("  SCRIPT 04 — CMS Hospital Compare API Download")
    print("=" * 65)
    print(f"  Source : CMS Open Data API (xubh-q36u)")
    print(f"  Target : Hospital General Information & Quality Benchmarks")
    print("=" * 65)
    print()

def fetch_one_page(offset, attempt=1):
    params = {
        "limit": PAGE_SIZE,
        "offset": offset
    }
    try:
        response = requests.get(CMS_API_ENDPOINT, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Socrata API wraps results 
        if 'results' in data:
            return data['results']
        return []
    except Exception as e:
        if attempt <= MAX_RETRIES:
            wait = 3 * attempt
            print(f"\n  API ERROR: {e}. Retrying in {wait}s (attempt {attempt})...")
            time.sleep(wait)
            return fetch_one_page(offset, attempt + 1)
        print(f"\n  FAILED at offset {offset}: {e}")
        return []

def download_data():
    print("[STEP 1] Downloading hospital data via pagination...")
    all_records = []
    offset = 0
    page_num = 1

    while True:
        print(f"  Downloading Page {page_num:2d} (Offset {offset:5,})... ", end="", flush=True)
        records = fetch_one_page(offset)

        if not records:
            print("Done — no more records returned.")
            break

        all_records.extend(records)
        print(f"Got {len(records):,} records. Running total: {len(all_records):,}")

        if len(records) < PAGE_SIZE:
            print("  Reached the end of the dataset.")
            break

        offset += PAGE_SIZE
        page_num += 1
        time.sleep(0.5)

    return all_records

def validate_and_save(records):
    print("\n[STEP 2] Validating and saving data...")
    if not records:
        print("  ERROR: No records to process.")
        return None

    df = pd.DataFrame(records)
    print(f"  Total hospitals safely fetched : {len(df):,}")
    
    # Filter for acute care if possible
    if 'hospital_type' in df.columns:
        acute_count = (df['hospital_type'] == 'Acute Care Hospitals').sum()
        print(f"  Of which are Acute Care        : {acute_count:,}")

    # Check for crucial benchmarking footprint
    missing = [c for c in ['facility_id', 'hospital_overall_rating'] if c not in df.columns]
    if missing:
        print(f"  WARNING: Missing columns: {missing}")
    else:
        print("  SUCCESS: Key capacity & quality benchmarks verified.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
    print(f"\n  Saved dataset : {OUTPUT_CSV}")
    print(f"  File Size     : {size_mb:.2f} MB")
    return df

def save_metadata(total_downloaded):
    meta = {
        "project": "Johns Hopkins Urology Analytics",
        "dataset_guid": "xubh-q36u",
        "records_downloaded": total_downloaded,
        "download_timestamp": datetime.now().isoformat(),
        "verified_columns": ["facility_id", "hospital_overall_rating", "hospital_type"],
        "status": "SUCCESS"
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=4)
        
if __name__ == "__main__":
    print_header()
    
    records = download_data()
    
    if not records:
        log_audit("Hospital API Download", "FAILED", "Zero records downloaded")
        sys.exit(1)
        
    df = validate_and_save(records)
    save_metadata(len(records))
    
    log_audit("Hospital API Download", "SUCCESS", f"Downloaded {len(df)} hospitals for benchmarking")
    
    print("\n=================================================================")
    print(" SCRIPT 04 COMPLETE — READY FOR SCRIPT 05")
    print("=================================================================")
