"""
validator.py
Automated Python Data Validation Workflow across 5 Operational Clinic Datasets.
Replaces manual data checks by detecting:
1. Missing / null values in mandatory fields
2. Duplicate records (unique emails, primary keys)
3. Domain inconsistencies (invalid age, negative duration, negative amounts)
4. Cross-dataset referential integrity (orphan foreign keys)
"""

import os
import pandas as pd
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")


class DataValidator:
    def __init__(self, raw_dir: str = RAW_DIR):
        self.raw_dir = raw_dir
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.issues: List[Dict[str, Any]] = []

    def load_datasets(self) -> None:
        """Load all 5 operational datasets."""
        files = {
            "patients": "patients.csv",
            "doctors": "doctors.csv",
            "appointments": "appointments.csv",
            "prescriptions": "prescriptions.csv",
            "billing": "billing.csv"
        }
        for name, fname in files.items():
            path = os.path.join(self.raw_dir, fname)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing required operational dataset: {path}")
            self.datasets[name] = pd.read_csv(path)

    def validate_missing_values(self) -> None:
        """Check for nulls or blank strings in mandatory fields."""
        mandatory_checks = {
            "patients": ["name", "email", "phone", "blood_type"],
            "doctors": ["name", "specialization", "department"],
            "appointments": ["appointment_date", "status"],
            "prescriptions": ["medication_name", "dosage"],
            "billing": ["amount", "payment_status"]
        }

        for dataset_name, cols in mandatory_checks.items():
            df = self.datasets[dataset_name]
            for col in cols:
                # Catch both NaN and whitespace/empty strings
                null_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
                null_count = int(null_mask.sum())
                if null_count > 0:
                    affected_ids = df.loc[null_mask, df.columns[0]].tolist()
                    self.issues.append({
                        "dataset": dataset_name,
                        "check_type": "Missing Value",
                        "severity": "Warning" if col in ["phone", "email"] else "Critical",
                        "column": col,
                        "error_count": null_count,
                        "affected_ids": affected_ids,
                        "message": f"Found {null_count} null/empty values in mandatory column '{col}'."
                    })

    def validate_duplicates(self) -> None:
        """Detect duplicate unique fields and duplicate primary keys."""
        # 1. Primary keys uniqueness
        pk_map = {
            "patients": "patient_id",
            "doctors": "doctor_id",
            "appointments": "appointment_id",
            "prescriptions": "prescription_id",
            "billing": "bill_id"
        }
        for dataset_name, pk in pk_map.items():
            df = self.datasets[dataset_name]
            dup_pk = df[df[pk].duplicated()]
            if not dup_pk.empty:
                self.issues.append({
                    "dataset": dataset_name,
                    "check_type": "Duplicate Primary Key",
                    "severity": "Critical",
                    "column": pk,
                    "error_count": len(dup_pk),
                    "affected_ids": dup_pk[pk].tolist(),
                    "message": f"Found {len(dup_pk)} duplicate primary key values in '{pk}'."
                })

        # 2. Patient email uniqueness (excluding null/blank)
        pat_df = self.datasets["patients"]
        valid_emails = pat_df[pat_df["email"].notna() & (pat_df["email"].str.strip() != "")]
        dup_emails = valid_emails[valid_emails["email"].duplicated(keep=False)]
        if not dup_emails.empty:
            self.issues.append({
                "dataset": "patients",
                "check_type": "Duplicate Unique Field",
                "severity": "Warning",
                "column": "email",
                "error_count": len(dup_emails),
                "affected_ids": dup_emails["patient_id"].tolist(),
                "message": f"Detected {len(dup_emails)} patient records sharing duplicate email addresses."
            })

    def validate_domain_rules(self) -> None:
        """Validate logical value constraints and business rules."""
        # 1. Age constraints (18 to 120)
        pat_df = self.datasets["patients"]
        invalid_age = pat_df[(pat_df["age"] < 0) | (pat_df["age"] > 120)]
        if not invalid_age.empty:
            self.issues.append({
                "dataset": "patients",
                "check_type": "Domain Inconsistency",
                "severity": "Critical",
                "column": "age",
                "error_count": len(invalid_age),
                "affected_ids": invalid_age["patient_id"].tolist(),
                "message": f"Detected {len(invalid_age)} records with impossible age values (<0 or >120)."
            })

        # 2. Completed appointments with 0 or negative duration
        app_df = self.datasets["appointments"]
        invalid_duration = app_df[(app_df["status"] == "completed") & (app_df["duration_minutes"] <= 0)]
        if not invalid_duration.empty:
            self.issues.append({
                "dataset": "appointments",
                "check_type": "Logical Inconsistency",
                "severity": "Warning",
                "column": "duration_minutes",
                "error_count": len(invalid_duration),
                "affected_ids": invalid_duration["appointment_id"].tolist(),
                "message": f"Detected {len(invalid_duration)} completed appointments with zero or negative duration."
            })

        # 3. Negative billing amounts
        bill_df = self.datasets["billing"]
        invalid_bill = bill_df[bill_df["amount"] < 0]
        if not invalid_bill.empty:
            self.issues.append({
                "dataset": "billing",
                "check_type": "Financial Inconsistency",
                "severity": "Critical",
                "column": "amount",
                "error_count": len(invalid_bill),
                "affected_ids": invalid_bill["bill_id"].tolist(),
                "message": f"Detected {len(invalid_bill)} billing records with negative amounts."
            })

    def validate_referential_integrity(self) -> None:
        """Detect orphan foreign keys across the 5 datasets."""
        pat_ids = set(self.datasets["patients"]["patient_id"])
        doc_ids = set(self.datasets["doctors"]["doctor_id"])
        app_df = self.datasets["appointments"]

        # Check appointments referencing nonexistent patients
        orphan_patients = app_df[~app_df["patient_id"].isin(pat_ids)]
        if not orphan_patients.empty:
            self.issues.append({
                "dataset": "appointments",
                "check_type": "Broken Foreign Key",
                "severity": "Critical",
                "column": "patient_id",
                "error_count": len(orphan_patients),
                "affected_ids": orphan_patients["appointment_id"].tolist(),
                "message": f"Detected {len(orphan_patients)} appointments referencing non-existent patient IDs."
            })

        # Check appointments referencing nonexistent doctors
        orphan_doctors = app_df[~app_df["doctor_id"].isin(doc_ids)]
        if not orphan_doctors.empty:
            self.issues.append({
                "dataset": "appointments",
                "check_type": "Broken Foreign Key",
                "severity": "Critical",
                "column": "doctor_id",
                "error_count": len(orphan_doctors),
                "affected_ids": orphan_doctors["appointment_id"].tolist(),
                "message": f"Detected {len(orphan_doctors)} appointments referencing non-existent doctor IDs."
            })

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Executes all validation workflows and returns identified issues."""
        self.load_datasets()
        self.validate_missing_values()
        self.validate_duplicates()
        self.validate_domain_rules()
        self.validate_referential_integrity()
        return self.issues


if __name__ == "__main__":
    validator = DataValidator()
    issues = validator.run_all_checks()
    print(f"Validation complete: Identified {len(issues)} data quality anomalies across 5 datasets:")
    for issue in issues:
        print(f" - [{issue['severity']}] {issue['dataset']}.{issue['column']}: {issue['message']}")
