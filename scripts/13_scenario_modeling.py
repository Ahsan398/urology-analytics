import os
import sys
import csv
import pandas as pd
from datetime import datetime

# ============================================================
# SCRIPT 13 — Analysis: What-If Scenario Modeling
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'outputs', 'reports')
SCENARIO_CSV = os.path.join(OUTPUT_DIR, 'scenario_report.csv')

def log_audit(action, status, details=""):
    log_file = os.path.join(PROJECT_ROOT, "outputs", "logs", "audit_trail.csv")
    try:
        file_exists = os.path.isfile(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, '13_scenario_modeling.py', action, status, details])
    except Exception:
        pass

def print_header():
    print("=" * 65)
    print("  SCRIPT 13 — MODULE 7: Strategic What-If Scenario Modeling")
    print("=" * 65)
    print()

def generate_scenarios():
    print("[STEP 1] Loading Department Baselines...")
    
    prod_file = os.path.join(OUTPUT_DIR, 'productivity_report.csv')
    cap_file = os.path.join(OUTPUT_DIR, 'capacity_report.csv')
    
    if not os.path.exists(prod_file) or not os.path.exists(cap_file):
        print("  CRITICAL ERROR: Run prior scripts. Required baseline reports missing.")
        sys.exit(1)
        
    df_prod = pd.read_csv(prod_file)
    df_cap = pd.read_csv(cap_file)
    
    # Establish Base State for Johns Hopkins Cohort
    dept_prod = df_prod[df_prod['State'] == 'MD']
    if len(dept_prod) == 0: dept_prod = df_prod.head(20) # Fallback
    
    current_physicians = len(dept_prod)
    base_revenue = dept_prod['Total_Revenue_Annual'].sum()
    base_volume = dept_prod['Total_Procedures_Annual'].sum()
    
    # We grab the total active providers/patients directly from the Capacity output
    # (Capacity report rows: Metric, Value)
    cap_dict = pd.Series(df_cap.Value.values, index=df_cap.Metric).to_dict() \
               if 'Metric' in df_cap.columns else {}
               
    # Safe fallbacks if dictionary parsing fails
    base_capacity = float(cap_dict.get('Maximum_System_Capacity', current_physicians * 207 * 25))
    base_patients = float(cap_dict.get('Total_Patients_Seen', base_volume))
    
    avg_rev_per_doc = base_revenue / current_physicians
    avg_vol_per_doc = base_volume / current_physicians
    avg_cap_per_doc = base_capacity / current_physicians

    print(f"  Baseline Physicians : {current_physicians}")
    print(f"  Baseline Revenue    : ${base_revenue:,.2f}")
    print(f"  Baseline Capacity   : {base_capacity:,.0f} Total Slots")
    
    scenarios = []
    
    # ---------------------------------------------------------
    # Baseline Scenario
    # ---------------------------------------------------------
    scenarios.append({
        'Scenario_ID': 'S0_Base',
        'Parameter_Change': 'Status Quo',
        'Forecasted_Physician_Count': current_physicians,
        'Forecasted_Total_Capacity': base_capacity,
        'Forecasted_Annual_Volume': base_volume,
        'Forecasted_Total_Revenue': base_revenue,
        'Capacity_Impact_Delta': 0,
        'Revenue_Impact_Delta': 0
    })

    print("\n[STEP 2] Simulating Scenario A: Hire 2 Net-New Physicians...")
    # Math: +2 Physicians means adding their average output and capacity
    s1_cap = base_capacity + (avg_cap_per_doc * 2)
    s1_rev = base_revenue + (avg_rev_per_doc * 2)
    s1_vol = base_volume + (avg_vol_per_doc * 2)
    
    scenarios.append({
        'Scenario_ID': 'S1_Hire_Staff',
        'Parameter_Change': '+2 Physicians',
        'Forecasted_Physician_Count': current_physicians + 2,
        'Forecasted_Total_Capacity': s1_cap,
        'Forecasted_Annual_Volume': s1_vol,
        'Forecasted_Total_Revenue': s1_rev,
        'Capacity_Impact_Delta': s1_cap - base_capacity,
        'Revenue_Impact_Delta': s1_rev - base_revenue
    })

    print("[STEP 3] Simulating Scenario B: Expand Surgical Block Time (+10 OR Slots/week)...")
    # Math: 10 OR slots/week * 46 clinical weeks = 460 slots.
    # Urological OR cases have much higher margin than clinic. Average surgical payment ~$800.
    or_slots_added = 460
    estimated_px_per_slot = 1.5 
    surgical_premium_rate = 800.00
    
    s2_vol_delta = or_slots_added * estimated_px_per_slot
    s2_rev_delta = s2_vol_delta * surgical_premium_rate
    
    scenarios.append({
        'Scenario_ID': 'S2_Expand_OR',
        'Parameter_Change': '+10 OR Slots/Week',
        'Forecasted_Physician_Count': current_physicians,
        'Forecasted_Total_Capacity': base_capacity + s2_vol_delta, # OR blocks act as capacity
        'Forecasted_Annual_Volume': base_volume + s2_vol_delta,
        'Forecasted_Total_Revenue': base_revenue + s2_rev_delta,
        'Capacity_Impact_Delta': s2_vol_delta,
        'Revenue_Impact_Delta': s2_rev_delta
    })

    print("[STEP 4] Simulating Scenario C: Medicare Part B Cut (-5% Reimbursement)...")
    # Math: Overall revenue artificially drops by 5% with no volume/capacity changes
    s3_rev = base_revenue * 0.95
    
    scenarios.append({
        'Scenario_ID': 'S3_Medicare_Cut',
        'Parameter_Change': '-5% Medicare Rate Cut',
        'Forecasted_Physician_Count': current_physicians,
        'Forecasted_Total_Capacity': base_capacity,
        'Forecasted_Annual_Volume': base_volume,
        'Forecasted_Total_Revenue': s3_rev,
        'Capacity_Impact_Delta': 0,
        'Revenue_Impact_Delta': s3_rev - base_revenue
    })

    print("\n[STEP 5] Exporting Matrix for Power BI Integration...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_scen = pd.DataFrame(scenarios)
    df_scen.to_csv(SCENARIO_CSV, index=False)
    
    print(df_scen[['Scenario_ID', 'Parameter_Change', 'Revenue_Impact_Delta']].to_string(index=False))
    
    log_audit("Module 7 Analytics", "SUCCESS", "Generated baseline sensitivity & what-if scenarios")
    print(f"\n  Saved Scenario Projections to: {SCENARIO_CSV}")

if __name__ == "__main__":
    print_header()
    generate_scenarios()
    
    print("\n=================================================================")
    print(" SCRIPT 13 COMPLETE — MODULE 7 (SCENARIOS) FINISHED")
    print(" SCRIPT 14 (POWER BI AUTOMATION EXPORT) is Up Next.")
    print("=================================================================")
