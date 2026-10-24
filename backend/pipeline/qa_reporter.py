"""
qa_reporter.py
Generates a structured Quality Assurance (QA) Audit Report by executing both
Python data validation checks and reusable SQL anomaly queries.
Documents root causes, severity ratings, and actionable follow-ups.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.validator import DataValidator
from pipeline.sql_runner import SqlAnomalyRunner

PROJECT_ROOT = os.path.dirname(BASE_DIR)
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


ROOT_CAUSE_ANALYSIS = {
    "duplicate_patients": {
        "root_cause": "Absence of unique email constraints in the registration form/API, allowing multiple profiles for the same individual.",
        "impact": "Fragmented patient health records, split medical histories, and inaccurate patient counts.",
        "recommendation": "Enforce unique database index on patient email and add client-side debounce verification."
    },
    "orphan_appointments": {
        "root_cause": "Hard-deletions of patient/staff records in database without foreign key CASCADE or RESTRICT rules.",
        "impact": "Ghost bookings in schedule, doctor calendar desynchronization, and broken relational queries.",
        "recommendation": "Adopt soft-deletion pattern (is_active = FALSE) and enforce PostgreSQL FOREIGN KEY constraints."
    },
    "schedule_conflicts": {
        "root_cause": "Booking API endpoint lacks transactional isolation (serializable transactions) and optimistic locking during appointment creation.",
        "impact": "Physician double-booking, extended patient wait times, and operational chaos.",
        "recommendation": "Add a unique composite constraint (doctor_id, appointment_date) or wrap booking in a database lock."
    },
    "billing_discrepancies": {
        "root_cause": "Manual billing input allows negative values, and consultation completion is not automatically linked to invoice generation.",
        "impact": "Revenue leakage, uncollected visit fees, and bookkeeping reconciliation errors.",
        "recommendation": "Implement automated invoice generation upon appointment status change to 'completed' and add non-negative check constraints."
    },
    "allergy_contraindications": {
        "root_cause": "Doctor prescription interface lacks an automated pre-flight clinical allergy cross-checking service.",
        "impact": "Severe patient clinical risk (anaphylaxis / adverse drug reaction).",
        "recommendation": "Integrate real-time allergy cross-reference alerts prior to prescription submission."
    }
}


class QaReporter:
    def __init__(self):
        self.validator = DataValidator()
        self.sql_runner = SqlAnomalyRunner()

    def generate_report(self) -> Dict[str, Any]:
        validation_issues = self.validator.run_all_checks()
        sql_anomalies = self.sql_runner.run_all_anomaly_queries()

        total_anomalies = len(validation_issues) + sum(len(v["anomalies"]) for v in sql_anomalies.values())
        critical_count = sum(1 for i in validation_issues if i["severity"] == "Critical")
        warning_count = sum(1 for i in validation_issues if i["severity"] == "Warning")

        report_data = {
            "metadata": {
                "report_title": "AI Clinic Operational Data Quality Assurance & Anomaly Audit",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "environment": "Operational Prototype / Staging",
                "total_datasets_audited": 5,
                "total_anomalies_detected": total_anomalies,
                "critical_severity_count": critical_count,
                "warning_severity_count": warning_count
            },
            "python_validation_issues": validation_issues,
            "sql_anomaly_investigations": sql_anomalies,
            "root_cause_analysis": ROOT_CAUSE_ANALYSIS
        }

        # Write JSON report
        json_path = os.path.join(REPORTS_DIR, "qa_audit_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        # Write Markdown report
        md_path = os.path.join(REPORTS_DIR, "QA_AUDIT_REPORT.md")
        self._write_markdown_report(md_path, report_data)

        return report_data

    def _write_markdown_report(self, path: str, data: Dict[str, Any]) -> None:
        meta = data["metadata"]
        md = []
        md.append(f"# {meta['report_title']}")
        md.append(f"**Generated:** {meta['generated_at']} | **Total Datasets:** {meta['total_datasets_audited']} | **Total Anomalies:** {meta['total_anomalies_detected']}\n")
        
        md.append("## Executive Summary")
        md.append("| Metric | Value |")
        md.append("| :--- | :--- |")
        md.append(f"| **Datasets Audited** | 5 (Patients, Doctors, Appointments, Prescriptions, Billing) |")
        md.append(f"| **Total Quality Issues Found** | {meta['total_anomalies_detected']} |")
        md.append(f"| **Critical Severity (Data Loss / Safety)** | {meta['critical_severity_count']} |")
        md.append(f"| **Warning Severity (Formatting / Imputation)** | {meta['warning_severity_count']} |\n")

        md.append("## 1. Automated Python Validation Findings")
        md.append("Identified by automated schema, null-check, and boundary testing workflows:\n")
        md.append("| Dataset | Column | Severity | Issue Type | Error Count | Details |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for issue in data["python_validation_issues"]:
            md.append(f"| `{issue['dataset']}` | `{issue['column']}` | **{issue['severity']}** | {issue['check_type']} | {issue['error_count']} | {issue['message']} |")
        md.append("")

        md.append("## 2. Reusable SQL Anomaly Investigations & Root Causes")
        md.append("Detailed diagnostics executed via standalone SQL audit queries:\n")

        for key, query_data in data["sql_anomaly_investigations"].items():
            rc = ROOT_CAUSE_ANALYSIS.get(key, {})
            md.append(f"### Diagnostic: {query_data['name']}")
            md.append(f"- **SQL Script:** `backend/sql/anomalies/{query_data['sql_file']}`")
            md.append(f"- **Anomalies Detected:** {len(query_data['anomalies'])}")
            md.append(f"- **Root Cause:** {rc.get('root_cause', 'N/A')}")
            md.append(f"- **Operational Impact:** {rc.get('impact', 'N/A')}")
            md.append(f"- **Remediation:** {rc.get('recommendation', 'N/A')}\n")

            if query_data["anomalies"]:
                md.append("**Sample Anomaly Records Identified:**")
                md.append("```json")
                md.append(json.dumps(query_data["anomalies"][:3], indent=2))
                md.append("```\n")

        md.append("## 3. Recommended Remediation Roadmap")
        md.append("1. **Data Ingestion Gate:** Enforce Pydantic validation on all REST API entry points.")
        md.append("2. **Referential Integrity:** Apply database-level foreign key cascades and composite uniqueness constraints.")
        md.append("3. **Clinical Safety Safeguard:** Introduce synchronous allergy cross-matching before prescription write.")
        md.append("4. **Billing Pipeline Automation:** Trigger automatic draft invoice generation on appointment completion.")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))


if __name__ == "__main__":
    reporter = QaReporter()
    rep = reporter.generate_report()
    print("QA Audit Report generated successfully:")
    print(f" -> reports/QA_AUDIT_REPORT.md")
    print(f" -> reports/qa_audit_report.json")
