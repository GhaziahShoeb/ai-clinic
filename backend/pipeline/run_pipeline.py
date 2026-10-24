"""
run_pipeline.py
Master execution script for the AI Clinic Data Operations & Quality Pipeline.
Orchestrates:
1. Mock Data Generation (5 operational datasets with seeded edge cases)
2. Python Automated Validation Workflow
3. Standalone SQL Anomaly Diagnostics
4. Structured QA Audit Report Generation
5. Automated Data Cleaning and Referential Normalization
6. Operational KPI Calculation and Excel/Power BI Export
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.generate_mock_data import main as generate_data
from pipeline.validator import DataValidator
from pipeline.sql_runner import SqlAnomalyRunner
from pipeline.qa_reporter import QaReporter
from pipeline.cleaner import DataCleaner
from pipeline.kpi_calculator import KpiCalculator


def main():
    print("=" * 70)
    print("AI CLINIC -- OPERATIONAL DATA QUALITY & ANALYTICS PIPELINE")
    print("=" * 70)

    # Step 1: Generate Mock Operational Datasets
    print("\n[STEP 1/6] Generating 5 Synthetic Operational Datasets...")
    generate_data()

    # Step 2: Run Python Automated Validation
    print("\n[STEP 2/6] Running Automated Python Validation Workflow...")
    validator = DataValidator()
    issues = validator.run_all_checks()
    print(f" -> Validation completed: Found {len(issues)} data quality anomalies across 5 datasets.")

    # Step 3: Run Reusable SQL Anomaly Diagnostics
    print("\n[STEP 3/6] Executing 5 Reusable SQL Anomaly Detection Queries...")
    sql_runner = SqlAnomalyRunner()
    sql_results = sql_runner.run_all_anomaly_queries()
    for key, data in sql_results.items():
        print(f" -> {data['name']}: {len(data['anomalies'])} anomalies identified.")

    # Step 4: Generate Structured QA Report
    print("\n[STEP 4/6] Generating Structured QA Audit Report...")
    reporter = QaReporter()
    rep = reporter.generate_report()
    print(" -> QA Report exported to 'reports/QA_AUDIT_REPORT.md' and 'reports/qa_audit_report.json'")

    # Step 5: Clean and Standardize Data
    print("\n[STEP 5/6] Executing Automated Cleaning & Referential Integrity Pipeline...")
    cleaner = DataCleaner()
    clean_summary = cleaner.run_cleaning_pipeline()
    print(f" -> Cleaning stats: {clean_summary['cleaning_stats']}")
    print(" -> Clean datasets saved in 'backend/data/clean/'")

    # Step 6: Calculate Operational KPIs & Export for Power BI
    print("\n[STEP 6/6] Computing 8 Core Operational KPIs and Exporting for Power BI/Excel...")
    calculator = KpiCalculator(use_clean_data=True)
    kpi_res = calculator.export_all()

    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY OF 8 OPERATIONAL KPIs:")
    print("=" * 70)
    for key, data in kpi_res["kpis"].items():
        print(f"  • {data['name']:<35} : {data['value']} {data['unit']:<8} [{data['status']}]")

    print("\nAll artifacts generated:")
    print("  1. Raw Datasets       : backend/data/raw/ (5 CSVs)")
    print("  2. Clean Datasets     : backend/data/clean/ (5 CSVs)")
    print("  3. QA Audit Report    : reports/QA_AUDIT_REPORT.md")
    print("  4. Operational Findings: reports/OPERATIONAL_FINDINGS.md")
    print("  5. Power BI / Excel   : backend/data/exports/ (kpi_metrics_export.csv, department_breakdown.csv)")
    print("=" * 70)


if __name__ == "__main__":
    main()
