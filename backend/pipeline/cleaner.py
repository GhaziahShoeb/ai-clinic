"""
cleaner.py
Automated Data Cleaning and Standardization Workflow.
Processes raw operational clinic datasets to:
1. Impute/standardize missing values
2. Deduplicate records
3. Sanitize domain errors (correct negative billing, clamp invalid ages)
4. Enforce referential integrity (drop orphan foreign keys)
5. Export clean datasets into backend/data/clean/ for KPI analytics and Power BI.
"""

import os
import pandas as pd
from typing import Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
os.makedirs(CLEAN_DIR, exist_ok=True)


class DataCleaner:
    def __init__(self, raw_dir: str = RAW_DIR, clean_dir: str = CLEAN_DIR):
        self.raw_dir = raw_dir
        self.clean_dir = clean_dir
        self.clean_datasets: Dict[str, pd.DataFrame] = {}
        self.cleaning_stats: Dict[str, int] = {}

    def clean_patients(self) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(self.raw_dir, "patients.csv"))
        initial_len = len(df)

        # 1. Clean string fields
        for col in ["name", "email", "phone", "blood_type", "allergies", "conditions"]:
            df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": "None", "": None})

        # 2. Impute missing phone/email
        df["email"] = df["email"].fillna("unregistered@clinic.local")
        df["phone"] = df["phone"].fillna("+91-0000000000")
        df["allergies"] = df["allergies"].fillna("None")
        df["conditions"] = df["conditions"].fillna("None")

        # 3. Deduplicate by email (keeping first registered instance)
        df_valid_email = df[df["email"] != "unregistered@clinic.local"]
        dup_count = df_valid_email.duplicated(subset=["email"]).sum()
        df = df.drop_duplicates(subset=["email"], keep="first")
        self.cleaning_stats["duplicate_patients_removed"] = int(dup_count)

        # 4. Correct / filter impossible ages
        median_age = int(df[(df["age"] > 0) & (df["age"] <= 100)]["age"].median())
        invalid_age_mask = (df["age"] < 0) | (df["age"] > 120)
        df.loc[invalid_age_mask, "age"] = median_age
        self.cleaning_stats["invalid_ages_corrected"] = int(invalid_age_mask.sum())

        self.clean_datasets["patients"] = df
        return df

    def clean_doctors(self) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(self.raw_dir, "doctors.csv"))
        for col in ["name", "specialization", "department"]:
            df[col] = df[col].astype(str).str.strip()
        self.clean_datasets["doctors"] = df
        return df

    def clean_appointments(self, valid_pat_ids: set, valid_doc_ids: set) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(self.raw_dir, "appointments.csv"))
        
        # 1. Drop orphan records
        orphan_mask = (~df["patient_id"].isin(valid_pat_ids)) | (~df["doctor_id"].isin(valid_doc_ids))
        orphan_count = int(orphan_mask.sum())
        df = df[~orphan_mask].copy()
        self.cleaning_stats["orphan_appointments_dropped"] = orphan_count

        # 2. Correct completed duration
        zero_duration_mask = (df["status"] == "completed") & (df["duration_minutes"] <= 0)
        df.loc[zero_duration_mask, "duration_minutes"] = 20  # Impute standard 20 min consultation
        self.cleaning_stats["durations_corrected"] = int(zero_duration_mask.sum())

        self.clean_datasets["appointments"] = df
        return df

    def clean_prescriptions(self, valid_app_ids: set, valid_pat_ids: set) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(self.raw_dir, "prescriptions.csv"))
        
        # 1. Drop broken references
        valid_mask = df["appointment_id"].isin(valid_app_ids) & df["patient_id"].isin(valid_pat_ids)
        df = df[valid_mask].copy()

        # 2. Impute missing dosage
        missing_dosage_mask = df["dosage"].isna() | (df["dosage"].astype(str).str.strip() == "")
        missing_dosage_count = int(missing_dosage_mask.sum())
        df["dosage"] = df["dosage"].fillna("Standard Dosage").replace({"": "Standard Dosage"})
        self.cleaning_stats["missing_dosages_imputed"] = missing_dosage_count

        self.clean_datasets["prescriptions"] = df
        return df

    def clean_billing(self, valid_app_ids: set, valid_pat_ids: set) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(self.raw_dir, "billing.csv"))

        # 1. Drop broken references
        valid_mask = df["appointment_id"].isin(valid_app_ids) & df["patient_id"].isin(valid_pat_ids)
        df = df[valid_mask].copy()

        # 2. Fix negative billing amounts (take absolute value)
        neg_mask = df["amount"] < 0
        df.loc[neg_mask, "amount"] = df.loc[neg_mask, "amount"].abs()
        self.cleaning_stats["negative_billing_corrected"] = int(neg_mask.sum())

        # 3. Fix paid bills with 0 amount (default to 500 consultation fee)
        zero_paid_mask = (df["payment_status"] == "paid") & (df["amount"] == 0)
        df.loc[zero_paid_mask, "amount"] = 500.0
        self.cleaning_stats["zero_paid_amounts_corrected"] = int(zero_paid_mask.sum())

        self.clean_datasets["billing"] = df
        return df

    def run_cleaning_pipeline(self) -> Dict[str, Any]:
        """Runs the complete data cleaning workflow and exports cleaned datasets."""
        pat_df = self.clean_patients()
        doc_df = self.clean_doctors()
        
        valid_pat_ids = set(pat_df["patient_id"])
        valid_doc_ids = set(doc_df["doctor_id"])

        app_df = self.clean_appointments(valid_pat_ids, valid_doc_ids)
        valid_app_ids = set(app_df["appointment_id"])

        rx_df = self.clean_prescriptions(valid_app_ids, valid_pat_ids)
        bill_df = self.clean_billing(valid_app_ids, valid_pat_ids)

        # Export clean datasets
        for name, df in self.clean_datasets.items():
            out_path = os.path.join(self.clean_dir, f"{name}_clean.csv")
            df.to_csv(out_path, index=False)

        return {
            "cleaning_stats": self.cleaning_stats,
            "record_counts": {k: len(v) for k, v in self.clean_datasets.items()}
        }


if __name__ == "__main__":
    cleaner = DataCleaner()
    summary = cleaner.run_cleaning_pipeline()
    print("Automated Data Cleaning Completed!")
    print(f"Summary of Actions: {summary['cleaning_stats']}")
    print(f"Cleaned Record Counts: {summary['record_counts']}")
