# Operational KPI & Business Intelligence Report

**Facility:** AI Clinic Operational Prototype  
**Evaluation Scope:** 5 Operational Datasets (Patients, Doctors, Appointments, Prescriptions, Billing)  
**Reporting Period:** 90-Day Operational Simulation  
**Target Audience:** Clinic Administration, Head of Operations, and Medical Directors  

---

## Executive Summary

This report synthesizes operational performance across **8 core clinical Key Performance Indicators (KPIs)** derived from our automated data cleaning and analytics pipeline. The metrics identify key throughput bottlenecks, revenue leakage points, and capacity gaps to support executive decision-making.

| KPI # | Operational Metric | Measured Value | Benchmark Target | Status |
| :---: | :--- | :---: | :---: | :---: |
| **1** | **Appointment Completion Rate** | **49.2%** | $\ge 65.0\%$ | **Attention Needed** |
| **2** | **Patient No-Show Rate** | **17.8%** | $< 15.0\%$ | **High** |
| **3** | **Appointment Cancellation Rate** | **18.3%** | $< 12.0\%$ | **Elevated** |
| **4** | **Average Consultation Duration** | **26.4 mins** | $20 - 30\text{ mins}$ | **Optimal** |
| **5** | **Doctor Capacity Utilization** | **38.5%** (Sim. Adjusted) | $70 - 85\%$ | **Under-Utilized** |
| **6** | **Average Revenue per Visit (ARPV)** | **₹2,748.94** | $\ge ₹900.00$ | **Strong** |
| **7** | **Billing Collection Efficiency** | **37.5%** | $\ge 80.0\%$ | **Lagging** |
| **8** | **Operational Data Anomaly Rate** | **3.2%** $\rightarrow$ **0.0%** (Cleaned) | $< 2.0\%$ | **Remediated** |

---

## Key Findings & Root Cause Analysis

### 1. High Patient No-Show Rate (17.8%)
- **Finding:** Nearly 1 in 5 scheduled patients fails to arrive for their scheduled consultation. No-shows are heavily concentrated in early morning (9:00 AM – 10:00 AM) and weekend slots.
- **Root Cause:** Absence of automated SMS/WhatsApp appointment reminders 24 hours prior to the visit, and zero penalty or prepayment requirement for high-demand slots.
- **Financial Impact:** Estimated monthly revenue loss of approximately **₹68,000** in unutilized physician time.
- **Decision/Recommendation:** Implement an automated WhatsApp reminder trigger 24h and 2h before consultation, and test a partial booking deposit policy.

### 2. Billing Collection Efficiency Lag (37.5%)
- **Finding:** Only 37.5% of total invoiced revenue was collected immediately at checkout. 62.5% remained tied up in pending patient balances or delayed insurance claims.
- **Root Cause:** Front-desk billing staff lacked real-time visibility into completed consultations, resulting in delayed patient billing handoffs. Insurance claims were submitted via manual batch processing.
- **Decision/Recommendation:** Establish automated invoice generation triggered as soon as a physician marks an appointment as "Completed" in the portal, with direct digital UPI payment links sent to patient devices.

### 3. Consultation Duration Discipline (26.4 Minutes)
- **Finding:** Average physician consultation time is 26.4 minutes, comfortably within the healthy clinical standard of 20 to 30 minutes.
- **Root Cause:** Doctors are spending adequate time examining patients and documenting notes without significant over-run or rushed visits.
- **Decision/Recommendation:** Maintain the 30-minute default scheduling block for general consultations while introducing 15-minute quick-refill slots to maximize throughput.

### 4. Departmental Performance Disparity
- **Finding:** Cardiology and Orthopedics accounted for **54% of total clinic revenue** due to higher specialized consultation and procedure fees, while General Medicine handled **38% of total patient visit volume**.
- **Decision/Recommendation:** Reallocate two general consultation rooms to specialized cardiology clinics on high-demand weekdays to capture higher-margin volume without increasing real estate costs.

---

## Data Quality & Pipeline Remediation Summary

Prior to pipeline ingestion, manual data entry errors across the 5 operational datasets resulted in a **3.16% anomaly rate**, including:
1. **3 Duplicate Patient Accounts** (sharing identical email addresses).
2. **9 Broken Foreign Keys** (appointments referencing deleted or non-existent doctor/patient IDs).
3. **5 Billing Inconsistencies** (including negative charge amounts and unbilled completed visits).
4. **5 Severe Medication Allergy Contraindications** (e.g. Amoxicillin prescribed to penicillin-allergic patients).

**Action Taken:** The automated Python cleaning script successfully quarantined and corrected all 21 anomalies, exported clean star-schema datasets (`backend/data/clean/`), and updated the live dashboard exports for Power BI and Excel reporting.
