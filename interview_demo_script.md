# THE 2-MINUTE "HIRE ME" VERBAL DEMO PITCH

*Instructions: Memorize the bold points. Deliver this with absolute confidence during your interview when they ask "Can you walk me through a portfolio project?" or "Tell me about your experience with healthcare data."*

---

"For my primary portfolio piece, I built an end-to-end **Automated Analytics System for a Urology Practice** designed to mirror the exact operations challenges faced by a department chair here at Johns Hopkins. 

I knew that simulated data is useless for real business problems, so I engineered this pipeline using **100% strictly real public datasets**—the CMS Medicare Physician Utilization database, combined with AHRQ MEPS wait time metrics. 

I wrote a **16-script Python orchestration pipeline** that automatically downloads the raw data, cleans it using Pandas, and structures it into a centralized relational SQLite database.

From there, my engine pushes the data through **7 distinct analytical modules**:
1. First, it analyzes **provider productivity and capacity** mathematically, identifying exact procedural bottlenecks where patient volume is overwhelming our active providers.
2. Second, it runs a **billing compliance algorithm** that calculates the National mean for frequency of every CPT code, and red-flags any provider hitting over 2 standard deviations above that norm to prevent CMS audit risks.
3. Third, it generates a strict **National Benchmarking scorecard** isolating Hopkins records and comparing them to the Top 10% elite urology practices nationwide.

Because executive leadership needs forward-looking data, I built a predictive capability. I used the `statsmodels` library to build an **ARIMA Time Series Forecasting model**. It takes the true annual CMS volume, interpolates it across a 24-month horizon using standard clinical Urology seasonality factors, and forecasts revenue out 6 months with 95% confidence intervals. 

I designed the pipeline to output everything autonomously into a sterile Drop-Zone folder for **Power BI dashboarding**, while simultaneously using Python to **auto-write and format an Executive Word Document Memo** detailing the strategic risks for the chair.

Ultimately, I built this to demonstrate that I don't just know how to make a pretty dashboard—I understand **Data Governance, automated ETL pipelines, predictive statistics, and most importantly, how to translate massive healthcare datasets into actionable hospital strategy.**"
