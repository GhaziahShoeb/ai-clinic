-- ============================================================================
-- Query 2: Detect Orphan Appointments (Broken Foreign Keys)
-- Purpose: Finds appointments pointing to non-existent patients or non-existent doctors.
-- Root Cause: Hard-deletions without cascade or missing relational foreign key constraints.
-- ============================================================================

SELECT 
    a.appointment_id,
    a.appointment_date,
    a.status,
    a.patient_id,
    a.doctor_id,
    CASE 
        WHEN p.patient_id IS NULL AND d.doctor_id IS NULL THEN 'Missing Patient AND Doctor'
        WHEN p.patient_id IS NULL THEN 'Missing Patient Record'
        WHEN d.doctor_id IS NULL THEN 'Missing Doctor Record'
    END AS anomaly_reason
FROM appointments a
LEFT JOIN patients p ON a.patient_id = p.patient_id
LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
WHERE p.patient_id IS NULL OR d.doctor_id IS NULL;
