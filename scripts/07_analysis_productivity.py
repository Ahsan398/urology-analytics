import os
import sys
import csv
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# SCRIPT 07 — Analysis: Physician Productivity
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'master_database.sqlite')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'reports')
OUTPUT_CSV = os.path.join(OUTPUT_DIR, 'productivity_report.csv')

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '07_analysis_productivity.py', action, status, details])
    except Exception:
        pass

def print_header():
    print("=" * 65)
    print("  SCRIPT 07 — MODULE 1: Physician Productivity Analytics")
    print("=" * 65)
    print()

def analyze_productivity():
    print("[STEP 1] Querying Central Master Database...")
    
    if not os.path.exists(DB_PATH):
        print(f"  CRITICAL ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    
    # Securely join the physician demographic table with their billing line items
    query = """
        SELECT 
            p.Rndrng_NPI as NPI,
            p.Rndrng_Prvdr_First_Name || ' ' || p.Rndrng_Prvdr_Last_Org_Name as Physician_Name,
            p.Rndrng_Prvdr_State_Abrvtn as State,
            SUM(b.Tot_Srvcs) as Total_Procedures_Annual,
            SUM(b.Calculated_Total_Medicare_Payment) as Total_Revenue_Annual,
            SUM(b.Estimated_Total_RVUs) as Total_RVUs_Annual
        FROM physician p
        JOIN billing b ON p.Rndrng_NPI = b.Rndrng_NPI
        GROUP BY p.Rndrng_NPI, Physician_Name, State
        HAVING Total_Procedures_Annual > 10
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"  SUCCESS: Aggregated data for {len(df):,} unique physicians.")

    print("\n[STEP 2] Calculating Key Performance Indicators (KPIs)...")
    
    # 1. Calculate Monthly Averages
    df['Monthly_Procedures'] = (df['Total_Procedures_Annual'] / 12).round(1)
    df['Monthly_Revenue'] = (df['Total_Revenue_Annual'] / 12).round(2)
    df['Monthly_RVUs'] = (df['Total_RVUs_Annual'] / 12).round(1)
    
    # 2. National Urology Benchmarks (using the aggregate of our real dataset)
    national_mean_rvu = df['Total_RVUs_Annual'].mean()
    national_mean_revenue = df['Total_Revenue_Annual'].mean()
    
    df['RVU_to_National_Mean_Diff_Pct'] = ((df['Total_RVUs_Annual'] - national_mean_rvu) / national_mean_rvu * 100).round(1)
    
    # 3. Quantile Scoring: Identify Top 10% and Bottom 10% Performers
    rvu_90th_percentile = df['Total_RVUs_Annual'].quantile(0.90)
    rvu_10th_percentile = df['Total_RVUs_Annual'].quantile(0.10)
    
    def assign_performance_tier(rvu):
        if rvu >= rvu_90th_percentile:
            return 'Top 10% Performer'
        elif rvu <= rvu_10th_percentile:
            return 'Bottom 10% Performer'
        else:
            return 'Average Performer'
            
    df['Performance_Tier'] = df['Total_RVUs_Annual'].apply(assign_performance_tier)
    
    print(f"  National Mean Annual RVU     : {national_mean_rvu:,.1f}")
    print(f"  National Mean Annual Revenue : ${national_mean_revenue:,.2f}")
    print(f"  Top 10% RVU Threshold        : {rvu_90th_percentile:,.1f}")

    print("\n[STEP 3] Exporting Module 1 Report...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    
    log_audit("Module 1 Analytics", "SUCCESS", f"Generated productivity report for {len(df)} physicians")
    print(f"  Saved final analytical report to: {OUTPUT_CSV}")

if __name__ == "__main__":
    print_header()
    analyze_productivity()
    
    print("\n=================================================================")
    print(" SCRIPT 07 COMPLETE — MODULE 1 (PRODUCTIVITY) FINISHED")
    print(" SCRIPT 08 (BILLING ANOMALIES) is Up Next.")
    print("=================================================================")
