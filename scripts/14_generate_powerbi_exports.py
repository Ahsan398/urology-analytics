import os
import sys
import csv
import shutil
from datetime import datetime

# ============================================================
# SCRIPT 14 — Power BI Automation & Export Pipeline
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'reports')
PBI_READY_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'powerbi_ready')
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, 'dashboard', 'instructions')

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '14_generate_powerbi_exports.py', action, status, details])
    except Exception:
        pass

def print_header():
    print("=" * 65)
    print("  SCRIPT 14 — Power BI Automation Data Pipeline")
    print("=" * 65)
    print()

def generate_powerbi_exports():
    print("[STEP 1] Validating Core Analytical Tables...")
    
    expected_files = [
        'productivity_report.csv',
        'billing_report.csv',
        'capacity_report.csv',
        'benchmark_report.csv',
        'alerts_report.csv',
        'forecast_report.csv',
        'scenario_report.csv'
    ]
    
    missing = []
    for f in expected_files:
        if not os.path.exists(os.path.join(REPORTS_DIR, f)):
            missing.append(f)
            
    if missing:
        print(f"  CRITICAL ERROR: Missing {len(missing)} reports needed for PowerBI:")
        for m in missing: print(f"    - {m}")
        sys.exit(1)
        
    print(f"  SUCCESS: All {len(expected_files)} data models are present.")

    print("\n[STEP 2] Migrating to Power BI Drop Zone...")
    os.makedirs(PBI_READY_DIR, exist_ok=True)
    
    for f in expected_files:
        src = os.path.join(REPORTS_DIR, f)
        dst = os.path.join(PBI_READY_DIR, f)
        shutil.copy2(src, dst)
        
    print(f"  SUCCESS: Exported pristine tables to: {PBI_READY_DIR}")

    print("\n[STEP 3] Generating 'How-To-Connect' Technical Setup Guide...")
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    guide_path = os.path.join(DASHBOARD_DIR, 'powerbi_setup_guide.md')
    
    markdown_content = """# Urology Operations Analytics - Power BI Setup Guide

## Data Connection Instructions (For Business Analysts)

This exact setup simulates how a production automated pipeline feeds Power BI via a standardized drop zone.

### Step 1: Connect to the Pipeline Drop Zone
1. Open Power BI Desktop.
2. Click **Get Data** -> **Folder**.
3. Browse to the exact path of your project's drop zone:
   `urology-analytics/outputs/powerbi_ready`
4. Click **Transform Data** (DO NOT CLICK LOAD YET).

### Step 2: Establish the 6 Analytical Tabs
Your dashboard must be divided into the following 6 tabs precisely:

**Tab 1: Physician Productivity**
* Data Source: `productivity_report.csv`
* Visuals: 
  - Bar chart of Annual RVUs by Physician.
  - KPI Cards for Total Revenue and Average Benchmarks.

**Tab 2: Billing Patterns & Compliance**
* Data Source: `billing_report.csv`
* Visuals: 
  - Pie Chart for Payer Mix (Medicare).
  - Table showing `Volume_Anomaly_Flag` colored dynamically (Red/Yellow filters).

**Tab 3: Capacity & Access**
* Data Source: `capacity_report.csv`
* Visuals: 
  - Gauge chart mapping `Total_Patients_Seen` against `Maximum_System_Capacity`.

**Tab 4: National Benchmarking Scorecard**
* Data Source: `benchmark_report.csv`
* Visuals: 
  - Table mapping Department Average vs Elite National Top 10%.

**Tab 5: Predictive Alerts Command Center**
* Data Source: `alerts_report.csv` & `forecast_report.csv`
* Visuals: 
  - ARIMAX Time Series Line Chart (Revenue + 95% Confidence Bounds).
  - Multi-row card showing RED FLAG risks.

**Tab 6: Executive Scenario Modeling**
* Data Source: `scenario_report.csv`
* Visuals: 
  - Matrix table showing Impact Delta against '+2 Physicians' or '-5% Medicare Cut'.

### Step 3: Configure Auto-Refresh Scheduled Pipeline
In a production deployment, this Python pipeline runs at 2:00 AM daily, updating the `powerbi_ready` folder. Power BI Gateway is configured to refresh at 3:00 AM to sweep the new data.
"""

    with open(guide_path, 'w', encoding='utf-8') as file:
        file.write(markdown_content)

    print(f"  SUCCESS: Generated Developer Documentation at: {guide_path}")
    log_audit("Power BI Delivery", "SUCCESS", f"Staged {len(expected_files)} secure tables for visualization")

if __name__ == "__main__":
    print_header()
    generate_powerbi_exports()
    
    print("\n=================================================================")
    print(" SCRIPT 14 COMPLETE — POWER BI PIPELINE SECURED")
    print(" SCRIPT 15 (EXECUTIVE MEMO AUTOGEN) is Up Next.")
    print("=================================================================")
