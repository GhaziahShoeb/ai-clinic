-- ============================================================================
-- Query 3: Detect Doctor Scheduling Overlaps (Double-Booking)
-- Purpose: Identifies doctors booked with more than one patient at the exact same timestamp.
-- Root Cause: Race conditions during simultaneous booking without transactional isolation.
-- ============================================================================

SELECT 
    a1.doctor_id,
    d.name AS doctor_name,
    a1.appointment_date,
    a1.appointment_id AS first_appointment_id,
    a1.patient_id AS first_patient_id,
    a2.appointment_id AS second_appointment_id,
    a2.patient_id AS second_patient_id
FROM appointments a1
JOIN appointments a2 
    ON a1.doctor_id = a2.doctor_id 
    AND a1.appointment_date = a2.appointment_date 
    AND a1.appointment_id < a2.appointment_id
JOIN doctors d ON a1.doctor_id = d.doctor_id
WHERE a1.status NOT IN ('cancelled', 'no_show')
  AND a2.status NOT IN ('cancelled', 'no_show');
