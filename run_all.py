import os
import sys
import subprocess
import time

# ============================================================
# MASTER ORCHESTRATOR — Urology Analytics System
# ============================================================

def print_banner():
    banner = """
    ========================================================================
       JOHNS HOPKINS UROLOGY PRACTICE PERFORMANCE ANALYTICS SYSTEM
       Predictive Intelligence & Operations Capacity Engine
    ========================================================================
       Automated Pipeline Orchestrator
       Executing Modules 1 through 8...
    """
    print(banner)

def run_script(script_name):
    # Determine correct python command (python vs python3)
    python_cmd = sys.executable 
    
    script_path = os.path.join("scripts", script_name)
    print(f"\n[{time.strftime('%H:%M:%S')}] >>> STARTING : {script_name}")
    print("-" * 70)
    
    try:
        # Run the script and stream the output to the console
        # Use utf-8 environment to prevent subprocess encoding crashes
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run([python_cmd, script_path], check=True, env=env)
        print("-" * 70)
        print(f"[{time.strftime('%H:%M:%S')}] [PASS] SUCCESS : {script_name} completed.")
        return True
    except subprocess.CalledProcessError as e:
        print("-" * 70)
        print(f"[{time.strftime('%H:%M:%S')}] [FAIL] FAILURE : {script_name} encountered an error.")
        print(f"Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"[{time.strftime('%H:%M:%S')}] [ERROR] CRITICAL : Could not find {script_path}.")
        return False

def main():
    print_banner()
    
    pipeline = [
        "00_setup_environment.py",
        "01_download_cms_data.py",
        "02_download_hcup_data.py",
        "03_download_meps_data.py",
        "04_download_hospital_compare.py",
        "05_clean_and_validate.py",
        "06_load_to_sqlite.py",
        "07_analysis_productivity.py",
        "08_analysis_billing.py",
        "09_analysis_capacity.py",
        "10_analysis_benchmarking.py",
        "11_predictive_alerts.py",
        "12_forecasting_arima.py",
        "13_scenario_modeling.py",
        "14_generate_powerbi_exports.py",
        "15_generate_executive_memo.py",
        "16_audit_log.py"
    ]
    
    time.sleep(1)
    
    for script in pipeline:
        success = run_script(script)
        if not success:
            print("\n[!] PIPELINE HALTED DUE TO CRITICAL ERROR. Review the logs above.")
            sys.exit(1)
            
        # Brief pause between scripts for visual tracking
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print(" [DONE] PIPELINE EXECUTION COMPLETE")
    print("    All Analytics, Forecasts, and Reports successfully regenerated.")
    print("    Master drop-zone (outputs/powerbi_ready) updated.")
    print("    Check outputs/memos/executive_memo.docx for the latest brief.")
    print("    Local Web Dashboard available: run 'python dashboard/serve.py' and open http://localhost:8000")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
