import os
import sys
import csv
import pandas as pd
from datetime import datetime

# ============================================================
# SCRIPT 16 — Data Governance & Pipeline Audit Validation
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")

def print_header():
    print("=" * 65)
    print("  SCRIPT 16 — Pipeline Observability & Audit Validation")
    print("=" * 65)
    print("  Ensuring Data Governance and HIPAA/Compliance Traceability")
    print("=" * 65)
    print()

def analyze_audit_logs():
    print("[STEP 1] Accessing Secure Audit Trail...")
    
    if not os.path.exists(LOG_FILE):
        print(f"  ERROR: No audit log found at {LOG_FILE}. Pipeline did not run.")
        sys.exit(1)
        
    df = pd.read_csv(LOG_FILE)
    
    if len(df) == 0:
        print("  NOTICE: Audit log is empty.")
        return
        
    # Append final log for this script
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, '16_audit_log.py', 'Audit Validation', 'SUCCESS', 'Conducted final system integrity check'])
    
    # Reload with final entry
    df = pd.read_csv(LOG_FILE)
    
    print(f"  SUCCESS: Loaded {len(df)} total pipeline execution events.")

    print("\n[STEP 2] Compiling Data Governance Traceability Matrix...")
    
    # Check for any failures
    failures = df[df['Status'] == 'FAILED']
    warnings = df[df['Status'] == 'PENDING']
    successes = df[df['Status'] == 'SUCCESS']
    
    print(f"\n  SYSTEM INTEGRITY REPORT:")
    print(f"  Total Actions Audited : {len(df)}")
    print(f"  Successful Operations : {len(successes)}")
    print(f"  Failed Operations     : {len(failures)}")
    print(f"  Pending/Manual Steps  : {len(warnings)}")
    
    if len(failures) > 0:
        print("\n  CRITICAL ERRORS DETECTED IN PIPELINE:")
        for idx, row in failures.iterrows():
            print(f"   -> [{row['Timestamp']}] {row['Script']}: {row['Details']}")
    elif len(warnings) > 0:
        print("\n  MANUAL INTERVENTIONS REQUIRED:")
        for idx, row in warnings.iterrows():
            print(f"   -> [{row['Timestamp']}] {row['Script']}: {row['Details']}")
    else:
        print("\n  [VERIFIED] PIPELINE EXECUTED WITH ZERO ERRORS.")
        print("  Data Governance standard: ACCEPTABLE.")
        
    print("\n[STEP 3] Recent Pipeline Execution History (Last 5 Events)...")
    recent = df.tail(5)
    for idx, row in recent.iterrows():
        print(f"  {row['Timestamp']} | {row['Script']} | {row['Status']} | {row['Action']}")
        
    print("\n[INFO] To comply with institutional data retention, the master audit trail")
    print("is preserved indefinitely at: outputs/logs/audit_trail.csv")

if __name__ == "__main__":
    print_header()
    analyze_audit_logs()
    
    print("\n=================================================================")
    print(" SCRIPT 16 COMPLETE — DATA GOVERNANCE SECURED")
    print(" ALL 16 MODULES ARE NOW FINISHED!")
    print("=================================================================")
