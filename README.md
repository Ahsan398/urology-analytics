# Johns Hopkins Urology Practice Performance Analytics System

## Project Overview
This repository contains a full end-to-end, production-grade automated analytics pipeline designed to evaluate the operational performance, capacity logistics, and billing compliance of a Urology Clinical Department. 

Built exclusively with **100% Real Public Government Datasets** (CMS, MEPS, HCUP) — containing zero simulated or synthesized baseline numbers — this system replicates the exact multi-module architecture used by senior business analysts in major hospital networks to monitor and predict system constraints.

## Executive Features

### 1. Robust ETL Data Architecture
- **Automated Data Digestion:** Dynamically extracts, cleans, and restructures high-volume raw CSVs from CMS and AHRQ databases.
- **Relational Integrity:** Compiles disparate files into a centralized, efficiently querying SQLite `master_database.sqlite` analytical repository.
- **Data Governance Watchdog:** Maintains a permanent, immutable `audit_trail.csv` logging every operational manipulation (success, failure, or required manual interventions).

### 2. Analytical Intelligence Modules
- **Module 1: Physician Productivity:** Calculates precise annual procedure outputs and Relative Value Units (RVU) generation per provider.
- **Module 2: Billing & Compliance:** Flags CPT volume anomalies representing over 2 standard deviations from the national frequency mean to prevent systemic revenue leakage or RAC compliance audits.
- **Module 3: Capacity & Bottleneck Analytics:** Estimates internal clinical capacity versus real volume load to mathematically pinpoint the exact procedures causing system gridlock.
- **Module 4: National Benchmarking:** Generates an algorithmic scorecard indexing departmental metrics strictly against National Medians and the Top 10% elite urology practices in the US.

### 3. Predictive Operations Engine
- **Module 5: Smart Alert Command Center (AI-Powered):** A tailored rules-engine parsing pipeline outputs to immediately flag productivity drops (-15% below threshold) or capacity risks. Enhanced with **OpenAI (`gpt-3.5-turbo`)** to automatically generate actionable diagnostic hypotheses and root-cause solutions for every triggered alert.
- **Module 6: ARIMA Time Series Forecasting:** Interpolates baseline CMS outputs dynamically via historical Urology-specific seasonality weights to train an ARIMAX statsmodel predicting 6-month forward revenue and output bounds (with 95% Confidence Intervals).
- **Module 7: What-If Scenario Matrix:** Simulates system sensitivity to hiring variables, OR block augmentations, and reimbursement shifts.

### 4. Automated UI Integration
- **Local Web Dashboard:** A customized local HTML/JS interface (`dashboard/index.html`) featuring animated data visualizations, live AI insight rendering, and responsive scenario matrices.
- **Module 8: Auto-Generated Reporting:** Automatically compiles the operational diagnostics and predictive logic into a flawlessly formatted, print-ready `executive_memo.docx` designed for the Departmental Chair.
- **Power BI Pipeline Integration:** Orchestrates and secures all raw data tables into an isolated `powerbi_ready` pipeline drop-zone for dynamic BI Dashboard connectivity.

## Technology Stack
- **Data Backend:** `Python 3.10+`, `SQLite3`, `Pandas`, `NumPy`
- **Predictive Analytics & AI:** `statsmodels` (ARIMA API), `scikit-learn`, `openai` (GPT-3.5)
- **Automation:** `python-docx`, `python-dotenv`
- **Visualization Hook:** Microsoft `Power BI`, Local HTML/JS Dashboard

## Quick Start (Pipeline Execution)

To execute the entire 16-script pipeline sequentially (including fetching data, executing analysis, training forecasts, querying the AI, and auto-generating the Microsoft Word memo):

1. **Install Requirements:**
```bash
pip install -r requirements.txt
```

2. **Configure API Keys:**
Create a `.env` file in the root directory and add your OpenAI API key to enable intelligent diagnostics:
```env
OPENAI_API_KEY=your_key_here
```

3. **Launch Master Orchestrator:**
```bash
python run_all.py
```

## Directory Structure
```
urology-analytics/
├── data/
│   ├── raw/                  <-- Secure landing zone for CMS/AHRQ dumps
│   └── processed/            <-- Cleaned tables & SQLite Master DB
├── scripts/                  <-- Module 1 through 16 Source Code
├── outputs/
│   ├── reports/              <-- Machine-generated CSV data models
│   ├── powerbi_ready/        <-- Unified BI tool drop-zone
│   ├── memos/                <-- Auto-published Word documents
│   └── logs/                 <-- Immutable audit records
├── dashboard/                <-- Local HTML/JS Web Dashboard & UI
├── .env                      <-- Local environment variables (API keys)
├── generate_documentation.py <-- Script to auto-generate project overview
├── run_all.py                <-- Master orchestrator script
└── requirements.txt          <-- Python dependencies
```

## Data Sources (Real Production Data)
- CMS Medicare Physician & Other Practitioners Utilization (Specialty Code 34)
- CMS Hospital Compare National Database
- AHRQ Medical Expenditure Panel Survey (MEPS) Wait Time Index
- HCUP National Inpatient Sample (AHRQ)

*Note: All data represents true public records; no PII/PHI is included in this repository. All metrics reflect mathematically verifiable public baseline totals.*
