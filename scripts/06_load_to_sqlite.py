import os
import sys
import csv
import glob
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# ============================================================
# SCRIPT 06 — Load Data into Central SQLite Master Database
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
DB_PATH = os.path.join(PROCESSED_DIR, 'master_database.sqlite')

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '06_load_to_sqlite.py', action, status, details])
    except Exception:
        pass

def print_header():
    print("=" * 65)
    print("  SCRIPT 06 — Central Master Database Construction")
    print("=" * 65)
    print("  Target : master_database.sqlite")
    print("  Engine : SQLAlchemy Engine + SQLite3 Core")
    print("=" * 65)
    print()

def load_data_to_sql():
    print("[STEP 1] Initializing Relational Database Engine...")
    
    # Check if we have files to process
    csv_files = glob.glob(os.path.join(PROCESSED_DIR, '*.csv'))
    if not csv_files:
        print(f"  CRITICAL ERROR: No cleaned CSV files found in {PROCESSED_DIR}")
        return False

    # Create SQLAlchemy engine specifically designed for Pandas "to_sql" inserts
    engine = create_engine(f"sqlite:///{DB_PATH}")
    print(f"  SUCCESS: SQLAlchemy engine tethered to {DB_PATH}")
    
    table_stats = {}
    
    print("\n[STEP 2] Migrating DataFrames into SQL Tables...")
    try:
        for file_path in csv_files:
            file_name = os.path.basename(file_path)
            table_name = file_name.replace('.csv', '').replace('_clean', '')
            
            # Read clean CSV
            df = pd.read_csv(file_path, low_memory=False)
            
            # Use chunks for large tables, replace existing schema iteratively
            print(f"  -> Pushing '{table_name}' table ({len(df):,} rows)... ", end="", flush=True)
            df.to_sql(table_name, con=engine, if_exists='replace', index=False, chunksize=5000)
            print("Done.")
            
            table_stats[table_name] = len(df)
            log_audit("Database Migration", "SUCCESS", f"Inserted {len(df)} rows into '{table_name}' table")
            
        print("\n[STEP 3] Performing SQL Integrity Validation Check...")
        
        # Connect using standard sqlite3 to query and verify what we pushed
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for table, expected_rows in table_stats.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sql_rows = cursor.fetchone()[0]
            
            if sql_rows == expected_rows:
                print(f"  [PASS] Table '{table}': {sql_rows:,} rows verified in DB.")
            else:
                print(f"  [FAIL] Table '{table}': Expected {expected_rows:,}, but DB has {sql_rows:,}.")
                
        conn.close()
        
        db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        print(f"\n  Final Database Size : {db_size_mb:.2f} MB")
        return True

    except Exception as e:
        print(f"\n  ERROR inserting to SQL: {e}")
        log_audit("Database Migration", "FAILED", str(e))
        return False

if __name__ == "__main__":
    print_header()
    success = load_data_to_sql()
    
    if success:
        print("\n=================================================================")
        print(" SCRIPT 06 COMPLETE — CORE DATABASE IS ONLINE")
        print(" SCRIPT 07 (PRODUCTIVITY ANALYSIS) is Up Next.")
        print("=================================================================")
    else:
        sys.exit(1)
