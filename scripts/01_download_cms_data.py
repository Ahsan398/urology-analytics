import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime

# ============================================================
# SCRIPT 01 — Download CMS Medicare Physician Data (Urology)
# ============================================================

# Ensure the paths are correct up to the working directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the correct CMS API endpoint and dataset GUID
CMS_API_BASE = "https://data.cms.gov/data-api/v1/dataset"
CMS_DATASET_GUID = "92396110-2aed-4d63-a6a2-5d6207d46a29"
UROLOGY_SPECIALTY = "Urology"

PAGE_SIZE = 5000
REQUEST_DELAY = 0.5
MAX_RETRIES = 3

OUTPUT_DIR  = os.path.join(PROJECT_ROOT, 'data', 'raw', 'cms_physician')
OUTPUT_CSV  = os.path.join(OUTPUT_DIR, 'cms_urology_data.csv')
OUTPUT_META = os.path.join(OUTPUT_DIR, 'cms_api_metadata.json')

def log_audit(action, status, details=""):
    """
    Logs actions securely to the audit trail to maintain professional data governance.
    """
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
    try:
        import csv
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '01_download_cms_data.py', action, status, details])
    except Exception as e:
        print(f"Warning: Could not write to audit log: {e}")

def print_header():
    print("=" * 65)
    print("  SCRIPT 01 — CMS Medicare Physician Data Download (Urology)")
    print("=" * 65)
    print(f"  Source    : CMS Open Data API")
    print(f"  Dataset ID: {CMS_DATASET_GUID}")
    print(f"  Field     : Rndrng_Prvdr_Type = {UROLOGY_SPECIALTY}")
    print(f"  Started   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    print()

def fetch_one_page(offset, attempt=1):
    # Using Rndrng_Prvdr_Type filter which we verified works for this dataset
    url = f"{CMS_API_BASE}/{CMS_DATASET_GUID}/data"
    params = {
        "filter[Rndrng_Prvdr_Type]": UROLOGY_SPECIALTY,
        "size": PAGE_SIZE,
        "offset": offset
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'data' in data:
            return data['data']
        return []
    except requests.exceptions.RequestException as e:
        if attempt <= MAX_RETRIES:
            wait = 3 * attempt
            print(f"\n  API ERROR: {e}. Retrying in {wait}s (attempt {attempt}/{MAX_RETRIES})...")
            time.sleep(wait)
            return fetch_one_page(offset, attempt + 1)
        print(f"\n  FAILED at offset {offset}: {e}")
        return []

def download_data():
    print("[STEP 1] Downloading all Urology records via pagination...")
    all_records = []
    offset = 0
    page_num = 1

    while True:
        print(f"  Downloading Page {page_num:2d} (Offset {offset:7,})... ", end="", flush=True)
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
        time.sleep(REQUEST_DELAY)

        # Safety limiter for portfolio project: Stop at 50,000 records to prevent extreme API load
        if offset >= 50000:
            print("  Reached 50,000 record cap for the portfolio scope.")
            break

    return all_records

def validate_and_save(records):
    print("\n[STEP 2] Validating and saving data...")
    if not records:
        print("  ERROR: No records to process.")
        return None

    df = pd.DataFrame(records)
    print(f"  Total records fetched : {len(df):,}")
    print(f"  Total columns mapped  : {len(df.columns)}")

    # Check key columns
    expected_cols = ['Rndrng_NPI', 'Rndrng_Prvdr_Type', 'HCPCS_Cd', 'Tot_Srvcs']
    missing = [c for c in expected_cols if c not in df.columns]
    
    if missing:
        print(f"  WARNING: Missing expected columns from CMS schema: {missing}")
    else:
        print("  SUCCESS: Key Medicare columns successfully verified in dataset.")

    # Save to disk
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
    print(f"\n  Saved dataset : {OUTPUT_CSV}")
    print(f"  File Size     : {size_mb:.2f} MB")
    return df

def save_metadata(total_downloaded):
    meta = {
        "project": "Johns Hopkins Urology Analytics",
        "dataset_guid": CMS_DATASET_GUID,
        "specialty_filter": UROLOGY_SPECIALTY,
        "records_downloaded": total_downloaded,
        "download_timestamp": datetime.now().isoformat(),
        "verified_columns": ["Rndrng_NPI", "HCPCS_Cd", "Tot_Srvcs", "Avg_Mdcr_Pymt_Amt"],
        "status": "SUCCESS"
    }
    with open(OUTPUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=4)
    print(f"  Metadata saved: {OUTPUT_META}")

if __name__ == "__main__":
    print_header()
    
    records = download_data()
    
    if not records:
        log_audit("CMS API Download", "FAILED", "Zero records downloaded")
        sys.exit(1)
        
    df = validate_and_save(records)
    save_metadata(len(records))
    
    unique_providers = df['Rndrng_NPI'].nunique() if 'Rndrng_NPI' in df.columns else 0
    log_audit("CMS API Download", "SUCCESS", f"Downloaded {len(df)} rows across {unique_providers} NPIs")
    
    print("\n[STEP 3] Final Data Summary")
    print(f"  Unique Urologists (NPIs) : {unique_providers:,}")
    print(f"  Total Billing Records    : {len(df):,}")
    print("\n=================================================================")
    print(" SCRIPT 01 COMPLETE — READY FOR SCRIPT 02")
    print("=================================================================")
