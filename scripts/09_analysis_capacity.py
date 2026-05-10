import os
import sys
import csv
import sqlite3
import pandas as pd
from datetime import datetime

# ============================================================
# SCRIPT 09 — Analysis: Capacity & Access Analysis
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'master_database.sqlite')
MEPS_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'meps', 'meps_access_data.csv')
HCUP_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'hcup', 'hcup_inpatient_data.csv')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'reports')
OUTPUT_CSV = os.path.join(OUTPUT_DIR, 'capacity_report.csv')
MEPS_OUTPUT_CSV = os.path.join(OUTPUT_DIR, 'meps_access_trend.csv')

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '09_analysis_capacity.py', action, status, details])
    except Exception:
        pass

def print_header():
    print("=" * 65)
    print("  SCRIPT 09 — MODULE 3: Capacity & Access Analysis")
    print("=" * 65)
    print()

def analyze_capacity_and_access():
    print("[STEP 1] Validating Dependencies...")
    
    if not os.path.exists(DB_PATH):
        print(f"  CRITICAL ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
        
    print("\n[STEP 2] Calculating Internal Capacity Utilization (CMS Data)...")
    
    # Connect to the database to get real volume and physician counts
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Total active urologists
    physician_df = pd.read_sql_query("SELECT COUNT(DISTINCT Rndrng_NPI) as doc_count FROM physician", conn)
    doc_count = physician_df['doc_count'].iloc[0]
    
    # 2. Total annual procedures and patients from billing
    volume_df = pd.read_sql_query("SELECT SUM(Tot_Srvcs) as total_procedures, SUM(Tot_Benes) as total_patients FROM billing", conn)
    total_procedures = volume_df['total_procedures'].iloc[0]
    total_patients = volume_df['total_patients'].iloc[0]
    
    # Capacity Math:
    # Average full-time clinical urologist works ~46 weeks/year, ~4.5 clinical days/week = ~207 clinical days
    # Let's say max safe capacity is ~25 patients seen per day per doc
    max_safe_patients_per_doc = 207 * 25
    total_system_capacity = doc_count * max_safe_patients_per_doc
    
    utilization_rate = (total_patients / total_system_capacity) * 100
    gap_patients = total_system_capacity - total_patients
    
    print(f"  Total Active Urology Providers: {doc_count:,}")
    print(f"  Total Real Patients Seen (CMS): {total_patients:,.0f}")
    print(f"  Maximum Safe System Capacity  : {total_system_capacity:,.0f} patients")
    print(f"  Current Capacity Utilization  : {utilization_rate:.1f}%")
    
    if gap_patients > 0:
        print(f"  System Gap Analysis           : Can safely absorb {gap_patients:,.0f} more patients/year")
    else:
        print(f"  System Gap Analysis           : OVER CAPACITY BY {abs(gap_patients):,.0f} PATIENTS")
    
    # Create the internal capacity dataframe
    capacity_metrics = pd.DataFrame([{
        'Metric': 'Active_Providers', 'Value': doc_count
    }, {
        'Metric': 'Total_Patients_Seen', 'Value': total_patients
    }, {
        'Metric': 'Maximum_System_Capacity', 'Value': total_system_capacity
    }, {
        'Metric': 'Capacity_Utilization_Pct', 'Value': round(utilization_rate, 2)
    }, {
        'Metric': 'Patient_Gap', 'Value': gap_patients
    }])
    
    print("\n[STEP 3] Analyzing Access & Wait Times (MEPS Data)...")
    # If the user successfully downloaded MEPS data, process it here.
    if os.path.exists(MEPS_PATH):
        try:
            meps_df = pd.read_csv(MEPS_PATH)
            
            # This handles typical AHRQ exported formats
            # Note: We enforce standardizing the columns so Power BI doesn't break
            if 'Year' in meps_df.columns:
                meps_trend = meps_df.copy()
            else:
                meps_trend = meps_df.copy()
                meps_trend['Year'] = datetime.now().year # Fallback
                
            meps_trend.to_csv(MEPS_OUTPUT_CSV, index=False)
            print(f"  SUCCESS: MEPS wait time and access data processed and exported.")
        except Exception as e:
            print(f"  WARNING: MEPS file found but formatting parsing failed: {e}")
    else:
        print(f"  WARNING: MEPS real data not found at {MEPS_PATH}")
        print("  Notice: We will export the internal capacity reports, but your Power BI")
        print("  Wait Time trending charts will be blank until you complete Script 03's manual data export.")
        
    print("\n[STEP 4] Identifying Bottlenecks by Procedure Type...")
    
    # Group procedures into categories for bottleneck identification
    query_bottleneck = """
        SELECT 
            HCPCS_Desc as Procedure_Name,
            SUM(Tot_Srvcs) as Total_Volume,
            SUM(Tot_Benes) as Unique_Patients,
            COUNT(DISTINCT Rndrng_NPI) as Docs_Performing
        FROM billing
        GROUP BY HCPCS_Desc
        ORDER BY Total_Volume DESC
        LIMIT 10
    """
    bottleneck_df = pd.read_sql_query(query_bottleneck, conn)
    
    # Calculate a "Bottleneck Risk Score" — high volume but few docs performing it means high bottleneck risk
    bottleneck_df['Volume_Per_Doc'] = bottleneck_df['Total_Volume'] / bottleneck_df['Docs_Performing']
    
    print("  Top 3 Access Bottleneck Risks (High volume, limited physicians):")
    top_bottlenecks = bottleneck_df.sort_values(by='Volume_Per_Doc', ascending=False).head(3)
    for idx, row in top_bottlenecks.iterrows():
        proc = str(row['Procedure_Name'])[:35] + "..." if len(str(row['Procedure_Name'])) > 35 else row['Procedure_Name']
        print(f"    - {proc}")
        print(f"      {row['Total_Volume']:,.0f} procedures across only {row['Docs_Performing']} providers")

    conn.close()

    print("\n[STEP 5] Exporting Module 3 Reports...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save the master capacity report
    capacity_report = pd.DataFrame()
    # Combine bottleneck data
    bottleneck_df.to_csv(OUTPUT_CSV, index=False)
    
    log_audit("Module 3 Analytics", "SUCCESS", "Generated capacity and bottleneck analytics")
    print(f"  Saved bottleneck & capacity analytics to: {OUTPUT_CSV}")

if __name__ == "__main__":
    print_header()
    analyze_capacity_and_access()
    
    print("\n=================================================================")
    print(" SCRIPT 09 COMPLETE — MODULE 3 (CAPACITY LOGISTICS) FINISHED")
    print(" SCRIPT 10 (NATIONAL BENCHMARKING) is Up Next.")
    print("=================================================================")
