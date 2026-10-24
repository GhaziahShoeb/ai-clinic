"""
generate_mock_data.py
Generates 5 realistic synthetic operational clinic datasets with seeded
edge-case anomalies (duplicates, missing values, referential breaks, contradictions).
Used to test the automated data cleaning, SQL QA, and KPI reporting pipelines.
"""

import os
import csv
import random
from datetime import datetime, timedelta

# Set fixed seed for reproducibility
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

FIRST_NAMES = [
    "Aarav", "Aditi", "Ananya", "Arjun", "Deepak", "Divya", "Ishaan", "Kavya", 
    "Manish", "Neha", "Pooja", "Rahul", "Rohan", "Sanjay", "Sneha", "Vikram",
    "Priya", "Aditya", "Meera", "Karan", "Tanvi", "Siddharth", "Riya", "Gaurav"
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Patel", "Kumar", "Mishra", "Joshi",
    "Yadav", "Khan", "Chopra", "Reddy", "Nair", "Iyer", "Das", "Bose", "Mehta"
]
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
DEPARTMENTS = {
    "General Medicine": ["Dr. Rajesh Sharma", "Dr. Sunita Patel", "Dr. Amit Verma"],
    "Cardiology": ["Dr. Arvind Rao", "Dr. Priya Deshmukh", "Dr. Vikram Seth"],
    "Pediatrics": ["Dr. Anjali Menon", "Dr. Rohit Saxena", "Dr. Meenakshi Sundaram"],
    "Orthopedics": ["Dr. Manoj Tiwari", "Dr. Sanjay Bhatt", "Dr. Farhan Qureshi"],
    "Dermatology": ["Dr. Shalini Kapoor", "Dr. Tarun Nanda", "Dr. Kavita Pillai"]
}
CONDITIONS = ["Hypertension", "Type 2 Diabetes", "Asthma", "Migraine", "None", "None", "None", "Hyperlipidemia", "GERD"]
ALLERGIES = ["Penicillin", "Sulfa Drugs", "Aspirin", "Peanuts", "None", "None", "None", "Latex", "None"]
MEDICATIONS = [
    ("Amoxicillin", "500mg", "Twice daily"),
    ("Metformin", "850mg", "Once daily with meal"),
    ("Amlodipine", "5mg", "Once daily morning"),
    ("Albuterol Inhaler", "90mcg", "As needed for wheezing"),
    ("Atorvastatin", "20mg", "At bedtime"),
    ("Omeprazole", "20mg", "Before breakfast"),
    ("Paracetamol", "650mg", "Every 6 hours if fever"),
    ("Ibuprofen", "400mg", "After food")
]


def generate_patients(n=100):
    patients = []
    for i in range(1, n + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        age = random.randint(18, 78)
        gender = random.choice(["Male", "Female", "Other"])
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        phone = f"+91-98{random.randint(10000000, 99999999)}"
        blood_type = random.choice(BLOOD_TYPES)
        allergies = random.choice(ALLERGIES)
        conditions = random.choice(CONDITIONS)
        reg_date = (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")

        patients.append({
            "patient_id": i,
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "phone": phone,
            "blood_type": blood_type,
            "allergies": allergies,
            "conditions": conditions,
            "registered_date": reg_date
        })

    # --- INJECT INTENTIONAL ANOMALIES FOR QA WORKFLOWS ---
    # 1. Duplicate emails
    patients[10]["email"] = patients[5]["email"]
    patients[20]["email"] = patients[8]["email"]
    patients[35]["email"] = patients[12]["email"]

    # 2. Null emails & phones (missing values)
    patients[15]["email"] = ""
    patients[25]["email"] = None
    patients[30]["phone"] = ""
    patients[45]["phone"] = None

    # 3. Inconsistent / invalid age
    patients[50]["age"] = -4
    patients[75]["age"] = 215

    return patients


def generate_doctors():
    doctors = []
    doc_id = 1
    for dept, doc_list in DEPARTMENTS.items():
        for doc_name in doc_list:
            doctors.append({
                "doctor_id": doc_id,
                "name": doc_name,
                "specialization": dept,
                "department": dept,
                "shift_start": "09:00",
                "shift_end": "17:00",
                "max_daily_capacity": 16,
                "consultation_fee": random.choice([500.0, 750.0, 1000.0, 1200.0])
            })
            doc_id += 1
    return doctors


def generate_appointments(patients, doctors, n=200):
    appointments = []
    base_date = datetime(2026, 3, 1, 9, 0)
    statuses = ["completed", "completed", "completed", "scheduled", "no_show", "cancelled"]

    for i in range(1, n + 1):
        pat = random.choice(patients)
        doc = random.choice(doctors)
        
        # Stagger appointments over 90 days, between 9 AM and 4 PM
        day_offset = random.randint(0, 90)
        hour_offset = random.randint(0, 7)
        minute_offset = random.choice([0, 30])
        app_time = base_date + timedelta(days=day_offset, hours=hour_offset, minutes=minute_offset)
        
        status = random.choice(statuses)
        duration = random.choice([15, 20, 30, 45]) if status == "completed" else 0
        reason = random.choice([
            "Routine Checkup", "Follow-up", "Chest Discomfort", "Fever and Cold",
            "Joint Pain", "Skin Rash", "Blood Pressure Monitoring", "Prescription Refill"
        ])

        appointments.append({
            "appointment_id": i,
            "patient_id": pat["patient_id"],
            "doctor_id": doc["doctor_id"],
            "appointment_date": app_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "duration_minutes": duration,
            "reason": reason
        })

    # --- INJECT INTENTIONAL ANOMALIES FOR QA WORKFLOWS ---
    # 1. Broken foreign keys (orphan appointments)
    appointments[14]["patient_id"] = 9999   # Non-existent patient
    appointments[28]["patient_id"] = 8888   # Non-existent patient
    appointments[42]["doctor_id"] = 777     # Non-existent doctor

    # 2. Scheduling overlap (Doctor booked at exact same time with two different patients)
    appointments[18]["status"] = "scheduled"
    appointments[19]["status"] = "scheduled"
    appointments[19]["doctor_id"] = appointments[18]["doctor_id"]
    appointments[19]["appointment_date"] = appointments[18]["appointment_date"]

    # 3. Logical inconsistency: Completed appointment with 0 or negative duration
    appointments[33]["status"] = "completed"
    appointments[33]["duration_minutes"] = 0
    appointments[55]["status"] = "completed"
    appointments[55]["duration_minutes"] = -15

    return appointments


def generate_prescriptions(appointments, patients):
    prescriptions = []
    patient_map = {p["patient_id"]: p for p in patients}
    rx_id = 1

    for app in appointments:
        if app["status"] == "completed" and app["patient_id"] in patient_map:
            # 80% chance doctor writes a prescription
            if random.random() < 0.8:
                med = random.choice(MEDICATIONS)
                prescriptions.append({
                    "prescription_id": rx_id,
                    "appointment_id": app["appointment_id"],
                    "patient_id": app["patient_id"],
                    "medication_name": med[0],
                    "dosage": med[1],
                    "frequency": med[2],
                    "instructions": "Take as directed with water"
                })
                rx_id += 1

    # --- INJECT INTENTIONAL ANOMALIES FOR QA WORKFLOWS ---
    # 1. Allergy contraindications: Patient is allergic to Penicillin, but prescribed Amoxicillin
    for rx in prescriptions:
        p = patient_map.get(rx["patient_id"])
        if p and p.get("allergies") == "Penicillin":
            rx["medication_name"] = "Amoxicillin"
            break

    # 2. Missing dosage / null values
    if len(prescriptions) > 5:
        prescriptions[2]["dosage"] = None
        prescriptions[4]["dosage"] = ""

    return prescriptions


def generate_billing(appointments, doctors):
    billing = []
    doc_fee_map = {d["doctor_id"]: d["consultation_fee"] for d in doctors}
    bill_id = 1

    for app in appointments:
        # Generate bill for all appointments except no_shows or cancelled
        fee = doc_fee_map.get(app["doctor_id"], 500.0)
        # Add random lab/procedure fee
        total_amount = fee + random.choice([0.0, 200.0, 450.0, 800.0])
        
        status = "paid" if app["status"] == "completed" and random.random() < 0.85 else "pending"
        if random.random() < 0.2:
            status = "insurance_claim"

        method = random.choice(["UPI", "Credit Card", "Cash", "Insurance"]) if status == "paid" else "Unpaid"

        billing.append({
            "bill_id": bill_id,
            "appointment_id": app["appointment_id"],
            "patient_id": app["patient_id"],
            "amount": total_amount,
            "payment_status": status,
            "payment_method": method,
            "invoice_date": app["appointment_date"].split()[0]
        })
        bill_id += 1

    # --- INJECT INTENTIONAL ANOMALIES FOR QA WORKFLOWS ---
    # 1. Negative amounts (clerical error)
    if len(billing) > 10:
        billing[3]["amount"] = -750.0
        billing[17]["amount"] = -200.0

    # 2. Paid status with zero amount
    if len(billing) > 25:
        billing[22]["amount"] = 0.0
        billing[22]["payment_status"] = "paid"

    # 3. Unbilled completed appointments (delete 3 bills so completed appointments lack billing)
    del billing[8]
    del billing[15]
    del billing[25]

    return billing


def save_csv(filename, data, fieldnames):
    filepath = os.path.join(RAW_DIR, filename)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {len(data)} records -> {filepath}")


def main():
    print("Generating 5 operational clinic datasets with seeded anomalies...")
    
    patients = generate_patients(100)
    doctors = generate_doctors()
    appointments = generate_appointments(patients, doctors, 200)
    prescriptions = generate_prescriptions(appointments, patients)
    billing = generate_billing(appointments, doctors)

    save_csv("patients.csv", patients, [
        "patient_id", "name", "age", "gender", "email", "phone",
        "blood_type", "allergies", "conditions", "registered_date"
    ])
    save_csv("doctors.csv", doctors, [
        "doctor_id", "name", "specialization", "department",
        "shift_start", "shift_end", "max_daily_capacity", "consultation_fee"
    ])
    save_csv("appointments.csv", appointments, [
        "appointment_id", "patient_id", "doctor_id", "appointment_date",
        "status", "duration_minutes", "reason"
    ])
    save_csv("prescriptions.csv", prescriptions, [
        "prescription_id", "appointment_id", "patient_id",
        "medication_name", "dosage", "frequency", "instructions"
    ])
    save_csv("billing.csv", billing, [
        "bill_id", "appointment_id", "patient_id", "amount",
        "payment_status", "payment_method", "invoice_date"
    ])
    print("Done! All 5 datasets generated successfully.")


if __name__ == "__main__":
    main()
