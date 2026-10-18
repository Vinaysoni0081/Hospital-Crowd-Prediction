
from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd
from flask import Flask, jsonify, request, render_template
app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

# Resolve paths relative to this file, not the terminal directory.
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# Load saved models once when the API starts.
waiting_model = joblib.load(
    MODEL_DIR / "waiting_time_model.pkl"
)

crowd_model = joblib.load(
    MODEL_DIR / "crowd_model.pkl"
)

# These must match the exact feature order used in training.
WAITING_FEATURES = [
    "Queue_Length",
    "Doctors_Available",
    "Appointments_Count",
    "Consultation_Duration_Min",
    "Appointment_Month",
    "Appointment_Day",
    "Day_of_Week",
    "Is_Weekend",
    "Appointment_Hour",
    "Peak_Hour",
    "Arrival_Delay_Minutes",
    "Department_Dermatology",
    "Department_ENT",
    "Department_General Medicine",
    "Department_Gynecology",
    "Department_Neurology",
    "Department_Orthopedics",
    "Department_Pediatrics",
    "Patient_Type_Returning",
]

CROWD_FEATURES = [
    "Queue_Length",
    "Doctors_Available",
    "Appointments_Count",
    "Consultation_Duration_Min",
]

DEPARTMENTS = [
    "Cardiology",
    "Dermatology",
    "ENT",
    "General Medicine",
    "Gynecology",
    "Neurology",
    "Orthopedics",
    "Pediatrics",
]

PATIENT_TYPES = ["New", "Returning"]


@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "waiting_model": type(waiting_model).__name__,
        "crowd_model": type(crowd_model).__name__,
    })


@app.post("/predict")
def predict():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Send a valid JSON object."
        }), 400

    required_fields = [
        "appointment_date",
        "appointment_time",
        "arrival_time",
        "department",
        "patient_type",
        "queue_length",
        "doctors_available",
        "appointments_count",
        "consultation_duration_min",
    ]

    missing = [
        field for field in required_fields
        if field not in data
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields.",
            "missing_fields": missing,
        }), 400

    try:
        # Validate date and time formats.
        appointment_date = datetime.strptime(
            data["appointment_date"], "%Y-%m-%d"
        )

        appointment_time = datetime.strptime(
            data["appointment_time"], "%H:%M"
        )

        arrival_time = datetime.strptime(
            data["arrival_time"], "%H:%M"
        )

        department = data["department"]
        patient_type = data["patient_type"]

        if department not in DEPARTMENTS:
            return jsonify({
                "error": "Invalid department.",
                "allowed_departments": DEPARTMENTS,
            }), 400

        if patient_type not in PATIENT_TYPES:
            return jsonify({
                "error": "patient_type must be New or Returning."
            }), 400

        # Validate numeric inputs.
        numeric_fields = {
            "queue_length": (1, 27),
            "doctors_available": (1, 5),
            "appointments_count": (8, 48),
            "consultation_duration_min": (10, 30),
        }

        numbers = {}

        for field, (minimum, maximum) in numeric_fields.items():
            value = data[field]

            if isinstance(value, bool):
                raise ValueError(f"{field} must be a number.")

            number = float(value)

            if not number.is_integer():
                raise ValueError(f"{field} must be a whole number.")

            number = int(number)

            if not minimum <= number <= maximum:
                raise ValueError(
                    f"{field} must be between {minimum} and {maximum}."
                )

            numbers[field] = number

        # Match the feature engineering used during training.
        appointment_minutes = (
            appointment_time.hour * 60
            + appointment_time.minute
        )

        arrival_minutes = (
            arrival_time.hour * 60
            + arrival_time.minute
        )

        features = {
            "Queue_Length": numbers["queue_length"],
            "Doctors_Available": numbers["doctors_available"],
            "Appointments_Count": numbers["appointments_count"],
            "Consultation_Duration_Min":
                numbers["consultation_duration_min"],
            "Appointment_Month": appointment_date.month,
            "Appointment_Day": appointment_date.day,
            "Day_of_Week": appointment_date.weekday(),
            "Is_Weekend": int(appointment_date.weekday() >= 5),
            "Appointment_Hour": appointment_time.hour,
            "Peak_Hour": int(
                appointment_time.hour in [10, 11, 12, 13, 14, 15]
            ),
            "Arrival_Delay_Minutes":
                arrival_minutes - appointment_minutes,
        }

        # Match pandas get_dummies(drop_first=True):
        # Cardiology and New are the reference categories.
        for dept in DEPARTMENTS:
            if dept != "Cardiology":
                features[f"Department_{dept}"] = int(
                    department == dept
                )

        features["Patient_Type_Returning"] = int(
            patient_type == "Returning"
        )

        waiting_input = pd.DataFrame(
            [[features[column] for column in WAITING_FEATURES]],
            columns=WAITING_FEATURES,
        )

        crowd_input = pd.DataFrame(
            [[
                numbers["queue_length"],
                numbers["doctors_available"],
                numbers["appointments_count"],
                numbers["consultation_duration_min"],
            ]],
            columns=CROWD_FEATURES,
        )

        predicted_wait = float(
            waiting_model.predict(waiting_input)[0]
        )

        predicted_crowd = str(
            crowd_model.predict(crowd_input)[0]
        )

        return jsonify({
            "predicted_waiting_time_minutes": round(
                max(0.0, predicted_wait), 1
            ),
            "predicted_crowd_level": predicted_crowd,
            "input_summary": {
                "department": department,
                "patient_type": patient_type,
                "queue_length": numbers["queue_length"],
                "doctors_available": numbers["doctors_available"],
            },
            "notice": (
                "Experimental predictions from a model trained on "
                "synthetic data; not validated for real hospital use."
            ),
        })

    except (ValueError, TypeError, OverflowError) as error:
        return jsonify({
            "error": str(error)
        }), 400


if __name__ == "__main__":
    app.run(debug=True)
