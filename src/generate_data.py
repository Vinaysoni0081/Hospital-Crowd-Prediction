print("GENERATE_DATA.PY STARTED")
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


# --------------------------------------------------
# 1. Reproducibility
# --------------------------------------------------

np.random.seed(42)
random.seed(42)


# --------------------------------------------------
# 2. Dataset configuration
# --------------------------------------------------

NUM_RECORDS = 12000

departments = [
    "General Medicine",
    "Cardiology",
    "Orthopedics",
    "Dermatology",
    "ENT",
    "Pediatrics",
    "Gynecology",
    "Neurology"
]

patient_types = [
    "New",
    "Returning"
]

doctors = [f"DOC{i:03d}" for i in range(1, 31)]


# --------------------------------------------------
# 3. Generate dates
# --------------------------------------------------

start_date = datetime(2026, 1, 1)

dates = [
    start_date + timedelta(days=random.randint(0, 364))
    for _ in range(NUM_RECORDS)
]


# --------------------------------------------------
# 4. Generate appointment times
# --------------------------------------------------

appointment_times = []

for _ in range(NUM_RECORDS):

    hour = random.choices(
        population=list(range(8, 20)),
        weights=[5, 8, 12, 15, 15, 12, 8, 6, 5, 5, 4, 3]
    )[0]

    minute = random.choice([0, 10, 20, 30, 40, 50])

    appointment_times.append(
        f"{hour:02d}:{minute:02d}"
    )


# --------------------------------------------------
# 5. Generate basic patient information
# --------------------------------------------------

department_data = np.random.choice(
    departments,
    size=NUM_RECORDS
)

patient_type_data = np.random.choice(
    patient_types,
    size=NUM_RECORDS,
    p=[0.40, 0.60]
)

doctor_data = np.random.choice(
    doctors,
    size=NUM_RECORDS
)


# --------------------------------------------------
# 6. Generate queue length
# --------------------------------------------------

queue_lengths = np.random.poisson(
    lam=12,
    size=NUM_RECORDS
)

queue_lengths = np.clip(
    queue_lengths,
    1,
    50
)


# --------------------------------------------------
# 7. Generate doctors available
# --------------------------------------------------

doctors_available = np.random.choice(
    [1, 2, 3, 4, 5],
    size=NUM_RECORDS,
    p=[0.10, 0.25, 0.35, 0.20, 0.10]
)


# --------------------------------------------------
# 8. Generate appointment count
# --------------------------------------------------

appointments_count = np.random.poisson(
    lam=25,
    size=NUM_RECORDS
)

appointments_count = np.clip(
    appointments_count,
    5,
    60
)


# --------------------------------------------------
# 9. Generate consultation duration
# --------------------------------------------------

department_duration = {
    "General Medicine": 12,
    "Cardiology": 20,
    "Orthopedics": 18,
    "Dermatology": 15,
    "ENT": 14,
    "Pediatrics": 16,
    "Gynecology": 18,
    "Neurology": 22
}

consultation_duration = []

for department, patient_type in zip(
    department_data,
    patient_type_data
):

    base_duration = department_duration[department]

    if patient_type == "New":
        duration = base_duration + np.random.randint(3, 9)
    else:
        duration = base_duration + np.random.randint(-2, 5)

    duration = max(duration, 5)

    consultation_duration.append(duration)


consultation_duration = np.array(
    consultation_duration
)


# --------------------------------------------------
# 10. Generate arrival time
# --------------------------------------------------

arrival_times = []

for appointment_time in appointment_times:

    appointment_dt = datetime.strptime(
        appointment_time,
        "%H:%M"
    )

    delay = random.randint(-15, 30)

    arrival_dt = appointment_dt + timedelta(
        minutes=delay
    )

    arrival_times.append(
        arrival_dt.strftime("%H:%M")
    )


# --------------------------------------------------
# 11. Generate waiting time
# --------------------------------------------------

waiting_time = (
    queue_lengths * 1.8
    + appointments_count * 0.25
    - doctors_available * 7
    + consultation_duration * 0.6
    + np.random.normal(0, 5, NUM_RECORDS)
)

waiting_time = np.clip(
    waiting_time,
    5,
    180
)

waiting_time = np.round(
    waiting_time
).astype(int)


# --------------------------------------------------
# 12. Create DataFrame
# --------------------------------------------------

df = pd.DataFrame({

    "Patient_ID": [
        f"P{i:05d}"
        for i in range(1, NUM_RECORDS + 1)
    ],

    "Appointment_Date": dates,

    "Appointment_Time": appointment_times,

    "Arrival_Time": arrival_times,

    "Department": department_data,

    "Doctor_ID": doctor_data,

    "Patient_Type": patient_type_data,

    "Queue_Length": queue_lengths,

    "Doctors_Available": doctors_available,

    "Appointments_Count": appointments_count,

    "Consultation_Duration_Min": consultation_duration,

    "Waiting_Time_Minutes": waiting_time
})


# --------------------------------------------------
# 13. Sort by date and time
# --------------------------------------------------

df = df.sort_values(
    by=["Appointment_Date", "Appointment_Time"]
).reset_index(drop=True)


# --------------------------------------------------
# 14. Save dataset
# --------------------------------------------------

output_path = "data/hospital_data.csv"

df.to_csv(
    output_path,
    index=False
)


# --------------------------------------------------
# 15. Display information
# --------------------------------------------------

print("Dataset generated successfully!")
print()
print("Shape:", df.shape)
print()
print("Columns:")
print(df.columns.tolist())
print()
print("First 5 records:")
print(df.head())