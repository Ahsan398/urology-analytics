# Urology Operations Analytics - Power BI Setup Guide

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
