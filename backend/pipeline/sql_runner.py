"""
sql_runner.py
Executes the reusable SQL anomaly detection queries against an in-memory database
loaded from the 5 operational datasets. Returns structured anomaly results.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
SQL_DIR = os.path.join(BASE_DIR, "sql", "anomalies")


class SqlAnomalyRunner:
    def __init__(self, raw_dir: str = RAW_DIR, sql_dir: str = SQL_DIR):
        self.raw_dir = raw_dir
        self.sql_dir = sql_dir
        self.conn = sqlite3.connect(":memory:")

    def load_data_to_sqlite(self) -> None:
        """Loads all 5 operational CSVs into in-memory SQLite tables."""
        tables = ["patients", "doctors", "appointments", "prescriptions", "billing"]
        for table in tables:
            csv_path = os.path.join(self.raw_dir, f"{table}.csv")
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Missing dataset for SQL runner: {csv_path}")
            df = pd.read_csv(csv_path)
            df.to_sql(table, self.conn, index=False, if_exists="replace")

    def run_query_file(self, filename: str) -> List[Dict[str, Any]]:
        """Reads and executes a single SQL file, returning rows as dictionaries."""
        filepath = os.path.join(self.sql_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"SQL file not found: {filepath}")
        
        with open(filepath, "r", encoding="utf-8") as f:
            query = f.read()

        # Remove header comments if needed or execute directly
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def run_all_anomaly_queries(self) -> Dict[str, Any]:
        """Executes all 5 reusable SQL anomaly queries."""
        self.load_data_to_sqlite()
        
        results = {
            "duplicate_patients": {
                "name": "Duplicate Patient Records",
                "sql_file": "check_duplicate_patients.sql",
                "anomalies": self.run_query_file("check_duplicate_patients.sql")
            },
            "orphan_appointments": {
                "name": "Orphan Appointments (Broken Foreign Keys)",
                "sql_file": "check_orphan_appointments.sql",
                "anomalies": self.run_query_file("check_orphan_appointments.sql")
            },
            "schedule_conflicts": {
                "name": "Doctor Schedule Conflicts (Double Booking)",
                "sql_file": "check_schedule_conflicts.sql",
                "anomalies": self.run_query_file("check_schedule_conflicts.sql")
            },
            "billing_discrepancies": {
                "name": "Financial & Billing Discrepancies",
                "sql_file": "check_billing_discrepancies.sql",
                "anomalies": self.run_query_file("check_billing_discrepancies.sql")
            },
            "allergy_contraindications": {
                "name": "Medication Allergy Contraindications",
                "sql_file": "check_allergy_contraindications.sql",
                "anomalies": self.run_query_file("check_allergy_contraindications.sql")
            }
        }
        return results


if __name__ == "__main__":
    runner = SqlAnomalyRunner()
    results = runner.run_all_anomaly_queries()
    print("SQL Anomaly Investigation Results:")
    for key, data in results.items():
        print(f"\n[QUERY] {data['name']} ({len(data['anomalies'])} anomalies found):")
        for item in data['anomalies']:
            print(f"  - {item}")
