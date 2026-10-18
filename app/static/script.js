
const form = document.getElementById("prediction-form");
const statusMessage = document.getElementById("status-message");
const results = document.getElementById("results");
const waitingResult = document.getElementById("waiting-result");
const crowdResult = document.getElementById("crowd-result");
const modelNotice = document.getElementById("model-notice");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    statusMessage.textContent = "";
    results.hidden = true;

    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    button.textContent = "Predicting...";

    const payload = {
        appointment_date: document.getElementById("appointment-date").value,
        appointment_time: document.getElementById("appointment-time").value,
        arrival_time: document.getElementById("arrival-time").value,
        department: document.getElementById("department").value,
        patient_type: document.getElementById("patient-type").value,
        queue_length: Number(document.getElementById("queue-length").value),
        doctors_available: Number(document.getElementById("doctors-available").value),
        appointments_count: Number(document.getElementById("appointments-count").value),
        consultation_duration_min: Number(
            document.getElementById("consultation-duration").value
        )
    };

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            const details = data.error || "Prediction request failed.";

            const extraDetails = data.missing_fields
                ? ` Missing fields: ${data.missing_fields.join(", ")}.`
                : data.allowed_departments
                    ? ` Allowed departments: ${data.allowed_departments.join(", ")}.`
                    : "";

            throw new Error(details + extraDetails);
        }

        waitingResult.textContent =
            `${Number(data.predicted_waiting_time_minutes).toFixed(1)} minutes`;

        crowdResult.textContent = data.predicted_crowd_level;
        modelNotice.textContent = data.notice || "";

        results.hidden = false;
        statusMessage.textContent = "Prediction completed successfully.";
        statusMessage.style.color = "#15803d";

    } catch (error) {
        statusMessage.style.color = "#b91c1c";
        statusMessage.textContent =
            `Error: ${error.message}. Please check your inputs and try again.`;
    } finally {
        button.disabled = false;
        button.textContent = "Predict Waiting Time & Crowd";
    }
});
