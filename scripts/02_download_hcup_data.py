import os
import csv
import datetime

def log_audit(action, status, details=""):
    log_file = os.path.join("outputs", "logs", "audit_trail.csv")
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Script', 'Action', 'Status', 'Details'])
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, '02_download_hcup_data.py', action, status, details])

def ensure_hcup_data_exists():
    """
    HCUP National Inpatient Sample dataset requires an active session and manual
    data extraction via their interactive query system (HCUPnet). 
    This script verifies if you have manually extracted the data.
    """
    print("STEP 4 (Part 1): Checking for HCUP Inpatient Sample Data...\n")
    
    file_path = os.path.join("data", "raw", "hcup", "hcup_inpatient_data.csv")
    
    if os.path.exists(file_path):
        print(f"SUCCESS: HCUP data found at {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
        log_audit("Data Verification", "SUCCESS", f"HCUP data found at {file_path}")
        return True
    else:
        print("ACTION REQUIRED: HCUPnet data cannot be downloaded automatically via API.")
        print("Please follow these exact click-by-click instructions to get the real data:\n")
        
        instructions = """
        AHQR has recently updated their website layout! Here are the new steps:
        
        1. Open your browser and go directly to the Inpatient Dashboard: 
           https://datatools.ahrq.gov/hcupnet?tab=inpatient-setting&dash=30
        2. Wait a moment for the dashboard (National Inpatient - All Stays) to load.
        3. Look for the filters on the side/top of the dashboard.
        4. Select the most recent year available (e.g., 2022/2023).
        5. For characteristics/diagnosis group, search for Urology specific codes 
           (e.g., "Prostatectomy", "Nephrectomy", "Cystoscopy").
        6. Once the table populates with the national numbers (length of stay, costs),
           click the 'Download Data' button below or above the table to get the MS Excel/CSV version.
        7. Save the downloaded file exactly as: 'hcup_inpatient_data.csv'
           (If it downloads as an Excel .xlsx file, open it and "Save As" -> CSV).
        8. Move this file to your project folder: 
           C:\\Users\\DELL\\.gemini\\antigravity\\scratch\\urology-analytics\\data\\raw\\hcup\\
        """
        
        print(instructions)
        print("\nWaiting for data... Rerun this script after you have placed the file in the folder.")
        log_audit("Data Verification", "PENDING", "HCUP manual download required")
        return False

if __name__ == "__main__":
    ensure_hcup_data_exists()
