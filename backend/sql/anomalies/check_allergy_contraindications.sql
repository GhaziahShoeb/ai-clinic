-- ============================================================================
-- Query 5: Detect Medication Allergy Contraindications (Clinical Safety)
-- Purpose: Identifies high-risk clinical safety anomalies where patients with documented
--          allergies (e.g. Penicillin) are prescribed contraindicated medications (Amoxicillin).
-- Root Cause: Absence of real-time clinical decision support / validation check at prescription write-time.
-- ============================================================================

SELECT 
    rx.prescription_id,
    rx.appointment_id,
    rx.patient_id,
    p.name AS patient_name,
    p.allergies AS documented_allergies,
    rx.medication_name AS prescribed_medication,
    rx.dosage,
    'Critical Contraindication Risk' AS risk_severity
FROM prescriptions rx
JOIN patients p ON rx.patient_id = p.patient_id
WHERE (p.allergies LIKE '%Penicillin%' AND (rx.medication_name LIKE '%Amoxicillin%' OR rx.medication_name LIKE '%Penicillin%'))
   OR (p.allergies LIKE '%Aspirin%' AND (rx.medication_name LIKE '%Aspirin%' OR rx.medication_name LIKE '%Ibuprofen%'));
