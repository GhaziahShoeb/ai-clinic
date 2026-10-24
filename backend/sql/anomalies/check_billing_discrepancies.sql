-- ============================================================================
-- Query 4: Detect Financial & Billing Discrepancies
-- Purpose: Identifies negative invoice amounts, zero-amount paid bills, and unbilled completed visits.
-- Root Cause: Clerical billing errors, unvalidated refund entries, or batch billing pipeline failures.
-- ============================================================================

-- Part A: Invalid billing amounts (Negative or Zero Paid)
SELECT 
    b.bill_id,
    b.appointment_id,
    b.patient_id,
    b.amount,
    b.payment_status,
    'Negative or Zero Amount Error' AS discrepancy_type
FROM billing b
WHERE b.amount <= 0

UNION ALL

-- Part B: Completed appointments that were never invoiced
SELECT 
    NULL AS bill_id,
    a.appointment_id,
    a.patient_id,
    0.0 AS amount,
    'unbilled' AS payment_status,
    'Completed Visit Without Billing Record' AS discrepancy_type
FROM appointments a
LEFT JOIN billing b ON a.appointment_id = b.appointment_id
WHERE a.status = 'completed' AND b.bill_id IS NULL;
