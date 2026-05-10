import os
import sys
import csv
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# SCRIPT 08 — Analysis: Billing Patterns & Anomalies
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'master_database.sqlite')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'reports')
OUTPUT_CSV = os.path.join(OUTPUT_DIR, 'billing_report.csv')

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '08_analysis_billing.py', action, status, details])
    except Exception:
        pass

def print_header():
    print("=" * 65)
    print("  SCRIPT 08 — MODULE 2: Billing Pattern & Anomaly Analytics")
    print("=" * 65)
    print()

def analyze_billing_patterns():
    print("[STEP 1] Extracting Billing Data from SQLite...")
    
    if not os.path.exists(DB_PATH):
        print(f"  CRITICAL ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            b.Rndrng_NPI as NPI,
            p.Rndrng_Prvdr_Last_Org_Name as Provider_Name,
            b.HCPCS_Cd as CPT_Code,
            b.HCPCS_Desc as Procedure_Description,
            b.Tot_Srvcs as Total_Procedures,
            b.Avg_Sbmtd_Chrg as Submitted_Charge,
            b.Avg_Mdcr_Pymt_Amt as Medicare_Payment,
            b.Calculated_Total_Medicare_Payment as Total_Revenue
        FROM billing b
        JOIN physician p ON p.Rndrng_NPI = b.Rndrng_NPI
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        print("  ERROR: No billing data to process.")
        sys.exit(1)

    print(f"  SUCCESS: Loaded {len(df):,} discrete line items.")

    print("\n[STEP 2] Calculating Top 20 Procedures...")
    
    # Calculate Top 20 by Volume
    top_volume = df.groupby('CPT_Code')['Total_Procedures'].sum().sort_values(ascending=False).head(20)
    print("  Top 3 by Volume:")
    for cpt, vol in top_volume.head(3).items():
        print(f"    - {cpt}: {vol:,.0f} procedures")

    # Calculate Top 20 by Revenue
    top_rev = df.groupby('CPT_Code')['Total_Revenue'].sum().sort_values(ascending=False).head(20)
    print("  Top 3 by Revenue:")
    for cpt, rev in top_rev.head(3).items():
        print(f"    - {cpt}: ${rev:,.2f}")

    print("\n[STEP 3] Establishing National Procedure Benchmarks for Anomaly Detection...")
    
    # Calculate national mean and standard deviation for EVERY procedure code
    cpt_benchmarks = df.groupby('CPT_Code').agg(
        National_Mean_Volume=('Total_Procedures', 'mean'),
        National_Std_Volume=('Total_Procedures', 'std'),
        National_Mean_Charge=('Submitted_Charge', 'mean')
    ).reset_index()
    
    # Handle NaN in std dev (happens if a procedure only has 1 occurrence in the database)
    cpt_benchmarks['National_Std_Volume'] = cpt_benchmarks['National_Std_Volume'].fillna(0)
    
    # Merge benchmarks back into the main billing dataframe
    df = pd.merge(df, cpt_benchmarks, on='CPT_Code', how='left')

    print("\n[STEP 4] Flagging Risks: Outliers and Underbilling...")
    
    # Fraud/Compliance Detection: > 2 Standard Deviations from National Mean
    df['Volume_Anomaly_Flag'] = np.where(
        df['Total_Procedures'] > (df['National_Mean_Volume'] + 2 * df['National_Std_Volume']),
        'YELLOW FLAG - High Volume', 'GREEN - Normal'
    )
    
    # Revenue Leakage Detection: Billed significantly below (e.g., > 20% below) the national average submitted charge
    df['Underbilling_Flag'] = np.where(
        df['Submitted_Charge'] < (df['National_Mean_Charge'] * 0.80),
        'YELLOW FLAG - Underbilling Risk', 'GREEN - Normal'
    )
    
    # Append Payer column to ensure PowerBI Pie Charts function properly as required
    # Note: Using 100% Medicare since the source dataset is strictly Medicare Provider Utilization
    df['Payer_Mix'] = 'Medicare'
    
    anomalies_found = (df['Volume_Anomaly_Flag'] != 'GREEN - Normal').sum()
    underbilling_found = (df['Underbilling_Flag'] != 'GREEN - Normal').sum()
    
    print(f"  Volume Anomalies Detected : {anomalies_found:,} flags")
    print(f"  Underbilling Bleeds Found : {underbilling_found:,} flags")
    
    print("\n[STEP 5] Exporting Module 2 Report...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    
    log_audit("Module 2 Analytics", "SUCCESS", f"Generated billing report tracking {anomalies_found} compliance anomalies")
    print(f"  Saved final analytical report to: {OUTPUT_CSV}")

if __name__ == "__main__":
    print_header()
    analyze_billing_patterns()
    
    print("\n=================================================================")
    print(" SCRIPT 08 COMPLETE — MODULE 2 (BILLING / COMPLIANCE) FINISHED")
    print(" SCRIPT 09 (CAPACITY & ACCESS) is Up Next.")
    print("=================================================================")
