# AI Clinic Operational Data Quality Assurance & Anomaly Audit
**Generated:** 2026-10-24 23:31:39 | **Total Datasets:** 5 | **Total Anomalies:** 26

## Executive Summary
| Metric | Value |
| :--- | :--- |
| **Datasets Audited** | 5 (Patients, Doctors, Appointments, Prescriptions, Billing) |
| **Total Quality Issues Found** | 26 |
| **Critical Severity (Data Loss / Safety)** | 5 |
| **Warning Severity (Formatting / Imputation)** | 4 |

## 1. Automated Python Validation Findings
Identified by automated schema, null-check, and boundary testing workflows:

| Dataset | Column | Severity | Issue Type | Error Count | Details |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `patients` | `email` | **Warning** | Missing Value | 2 | Found 2 null/empty values in mandatory column 'email'. |
| `patients` | `phone` | **Warning** | Missing Value | 2 | Found 2 null/empty values in mandatory column 'phone'. |
| `prescriptions` | `dosage` | **Critical** | Missing Value | 2 | Found 2 null/empty values in mandatory column 'dosage'. |
| `patients` | `email` | **Warning** | Duplicate Unique Field | 6 | Detected 6 patient records sharing duplicate email addresses. |
| `patients` | `age` | **Critical** | Domain Inconsistency | 2 | Detected 2 records with impossible age values (<0 or >120). |
| `appointments` | `duration_minutes` | **Warning** | Logical Inconsistency | 2 | Detected 2 completed appointments with zero or negative duration. |
| `billing` | `amount` | **Critical** | Financial Inconsistency | 2 | Detected 2 billing records with negative amounts. |
| `appointments` | `patient_id` | **Critical** | Broken Foreign Key | 2 | Detected 2 appointments referencing non-existent patient IDs. |
| `appointments` | `doctor_id` | **Critical** | Broken Foreign Key | 1 | Detected 1 appointments referencing non-existent doctor IDs. |

## 2. Reusable SQL Anomaly Investigations & Root Causes
Detailed diagnostics executed via standalone SQL audit queries:

### Diagnostic: Duplicate Patient Records
- **SQL Script:** `backend/sql/anomalies/check_duplicate_patients.sql`
- **Anomalies Detected:** 3
- **Root Cause:** Absence of unique email constraints in the registration form/API, allowing multiple profiles for the same individual.
- **Operational Impact:** Fragmented patient health records, split medical histories, and inaccurate patient counts.
- **Remediation:** Enforce unique database index on patient email and add client-side debounce verification.

**Sample Anomaly Records Identified:**
```json
[
  {
    "email": "gaurav.das6@example.com",
    "record_count": 2,
    "conflicting_patient_ids": "6,11",
    "conflicting_names": "Gaurav Das,Aditi Chopra"
  },
  {
    "email": "gaurav.yadav13@example.com",
    "record_count": 2,
    "conflicting_patient_ids": "13,36",
    "conflicting_names": "Gaurav Yadav,Ananya Iyer"
  },
  {
    "email": "ishaan.yadav9@example.com",
    "record_count": 2,
    "conflicting_patient_ids": "9,21",
    "conflicting_names": "Ishaan Yadav,Siddharth Bose"
  }
]
```

### Diagnostic: Orphan Appointments (Broken Foreign Keys)
- **SQL Script:** `backend/sql/anomalies/check_orphan_appointments.sql`
- **Anomalies Detected:** 3
- **Root Cause:** Hard-deletions of patient/staff records in database without foreign key CASCADE or RESTRICT rules.
- **Operational Impact:** Ghost bookings in schedule, doctor calendar desynchronization, and broken relational queries.
- **Remediation:** Adopt soft-deletion pattern (is_active = FALSE) and enforce PostgreSQL FOREIGN KEY constraints.

**Sample Anomaly Records Identified:**
```json
[
  {
    "appointment_id": 15,
    "appointment_date": "2026-05-10 15:30:00",
    "status": "completed",
    "patient_id": 9999,
    "doctor_id": 6,
    "anomaly_reason": "Missing Patient Record"
  },
  {
    "appointment_id": 29,
    "appointment_date": "2026-05-01 10:00:00",
    "status": "scheduled",
    "patient_id": 8888,
    "doctor_id": 7,
    "anomaly_reason": "Missing Patient Record"
  },
  {
    "appointment_id": 43,
    "appointment_date": "2026-05-25 15:00:00",
    "status": "scheduled",
    "patient_id": 59,
    "doctor_id": 777,
    "anomaly_reason": "Missing Doctor Record"
  }
]
```

### Diagnostic: Doctor Schedule Conflicts (Double Booking)
- **SQL Script:** `backend/sql/anomalies/check_schedule_conflicts.sql`
- **Anomalies Detected:** 1
- **Root Cause:** Booking API endpoint lacks transactional isolation (serializable transactions) and optimistic locking during appointment creation.
- **Operational Impact:** Physician double-booking, extended patient wait times, and operational chaos.
- **Remediation:** Add a unique composite constraint (doctor_id, appointment_date) or wrap booking in a database lock.

**Sample Anomaly Records Identified:**
```json
[
  {
    "doctor_id": 3,
    "doctor_name": "Dr. Amit Verma",
    "appointment_date": "2026-03-10 16:30:00",
    "first_appointment_id": 19,
    "first_patient_id": 84,
    "second_appointment_id": 20,
    "second_patient_id": 43
  }
]
```

### Diagnostic: Financial & Billing Discrepancies
- **SQL Script:** `backend/sql/anomalies/check_billing_discrepancies.sql`
- **Anomalies Detected:** 5
- **Root Cause:** Manual billing input allows negative values, and consultation completion is not automatically linked to invoice generation.
- **Operational Impact:** Revenue leakage, uncollected visit fees, and bookkeeping reconciliation errors.
- **Remediation:** Implement automated invoice generation upon appointment status change to 'completed' and add non-negative check constraints.

**Sample Anomaly Records Identified:**
```json
[
  {
    "bill_id": 4,
    "appointment_id": 4,
    "patient_id": 42,
    "amount": -750.0,
    "payment_status": "insurance_claim",
    "discrepancy_type": "Negative or Zero Amount Error"
  },
  {
    "bill_id": 18,
    "appointment_id": 18,
    "patient_id": 13,
    "amount": -200.0,
    "payment_status": "pending",
    "discrepancy_type": "Negative or Zero Amount Error"
  },
  {
    "bill_id": 23,
    "appointment_id": 23,
    "patient_id": 57,
    "amount": 0.0,
    "payment_status": "paid",
    "discrepancy_type": "Negative or Zero Amount Error"
  }
]
```

### Diagnostic: Medication Allergy Contraindications
- **SQL Script:** `backend/sql/anomalies/check_allergy_contraindications.sql`
- **Anomalies Detected:** 5
- **Root Cause:** Doctor prescription interface lacks an automated pre-flight clinical allergy cross-checking service.
- **Operational Impact:** Severe patient clinical risk (anaphylaxis / adverse drug reaction).
- **Remediation:** Integrate real-time allergy cross-reference alerts prior to prescription submission.

**Sample Anomaly Records Identified:**
```json
[
  {
    "prescription_id": 6,
    "appointment_id": 9,
    "patient_id": 91,
    "patient_name": "Ishaan Khan",
    "documented_allergies": "Penicillin",
    "prescribed_medication": "Amoxicillin",
    "dosage": "500mg",
    "risk_severity": "Critical Contraindication Risk"
  },
  {
    "prescription_id": 24,
    "appointment_id": 52,
    "patient_id": 68,
    "patient_name": "Sanjay Iyer",
    "documented_allergies": "Penicillin",
    "prescribed_medication": "Amoxicillin",
    "dosage": "500mg",
    "risk_severity": "Critical Contraindication Risk"
  },
  {
    "prescription_id": 26,
    "appointment_id": 56,
    "patient_id": 80,
    "patient_name": "Sanjay Reddy",
    "documented_allergies": "Penicillin",
    "prescribed_medication": "Amoxicillin",
    "dosage": "500mg",
    "risk_severity": "Critical Contraindication Risk"
  }
]
```

## 3. Recommended Remediation Roadmap
1. **Data Ingestion Gate:** Enforce Pydantic validation on all REST API entry points.
2. **Referential Integrity:** Apply database-level foreign key cascades and composite uniqueness constraints.
3. **Clinical Safety Safeguard:** Introduce synchronous allergy cross-matching before prescription write.
4. **Billing Pipeline Automation:** Trigger automatic draft invoice generation on appointment completion.