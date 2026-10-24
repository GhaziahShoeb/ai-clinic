-- ============================================================================
-- Query 1: Detect Duplicate Patient Records
-- Purpose: Identifies patients sharing the exact same email address across different IDs.
-- Root Cause: Multiple account registrations or front-end lack of unique validation.
-- ============================================================================

SELECT 
    email,
    COUNT(*) AS record_count,
    GROUP_CONCAT(patient_id) AS conflicting_patient_ids,
    GROUP_CONCAT(name) AS conflicting_names
FROM patients
WHERE email IS NOT NULL AND email != ''
GROUP BY email
HAVING COUNT(*) > 1;
