import os
import csv
import datetime

def log_audit(action, status, details=""):
    """
    Logs actions to the audit trail to maintain professional data governance.
    """
    log_dir = os.path.join("outputs", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "audit_trail.csv")
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
            
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, '00_setup_environment.py', action, status, details])

def create_directory_structure():
    """
    Creates the complete folder hierarchy for the Johns Hopkins urology analytics project.
    """
    print("STEP 2: Starting environment setup and folder creation...")
    
    directories = [
        "data/raw/cms_physician",
        "data/raw/hcup",
        "data/raw/meps",
        "data/raw/cms_hospital",
        "data/raw/benchmarks",
        "data/processed",
        "scripts",
        "dashboard/instructions",
        "outputs/reports",
        "outputs/memos",
        "outputs/logs"
    ]
    
    try:
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"Created/Verified directory: {directory}")
            
        log_audit("Directory Creation", "SUCCESS", f"Created {len(directories)} directories")
        print("\nAll directories successfully created or verified.")
        print("Audit trail initialized at outputs/logs/audit_trail.csv.")
        
    except Exception as e:
        print(f"\nERROR: Failed to create directories. Details: {e}")
        log_audit("Directory Creation", "FAILED", str(e))

if __name__ == "__main__":
    create_directory_structure()
