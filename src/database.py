import pandas as pd
import sqlite3


# --------------------------------------------------
# 1. Load Dataset
# --------------------------------------------------

df = pd.read_csv("data/hospital_data.csv")

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# --------------------------------------------------
# 2. Create SQLite Database
# --------------------------------------------------

connection = sqlite3.connect(
    "data/hospital.db"
)


# --------------------------------------------------
# 3. Store Data in SQLite
# --------------------------------------------------

df.to_sql(
    "hospital_data",
    connection,
    if_exists="replace",
    index=False
)

print("Data inserted into SQLite database!")


# --------------------------------------------------
# 4. Check Table
# --------------------------------------------------

query = """
SELECT *
FROM hospital_data
LIMIT 5;
"""

result = pd.read_sql_query(
    query,
    connection
)

print("\nFirst 5 records:")
print(result)
query = """
SELECT
    Department,
    COUNT(*) AS Total_Patients,
    ROUND(AVG(Waiting_Time_Minutes), 2) AS Average_Waiting_Time
FROM hospital_data
GROUP BY Department
ORDER BY Average_Waiting_Time DESC;
"""

result = pd.read_sql_query(
    query,
    connection
)

print("\nDepartment-wise Waiting Time:")
print(result)

query = """
SELECT
    Patient_Type,
    COUNT(*) AS Total_Patients,
    ROUND(AVG(Waiting_Time_Minutes), 2) AS Average_Waiting_Time
FROM hospital_data
GROUP BY Patient_Type
ORDER BY Average_Waiting_Time DESC;
"""

result = pd.read_sql_query(
    query,
    connection
)

print("\nPatient Type Analysis:")
print(result)

query = """
SELECT
    Doctors_Available,
    COUNT(*) AS Total_Patients,
    ROUND(AVG(Waiting_Time_Minutes), 2) AS Average_Waiting_Time
FROM hospital_data
GROUP BY Doctors_Available
ORDER BY Doctors_Available;
"""

result = pd.read_sql_query(
    query,
    connection
)

print("\nDoctor Availability Analysis:")
print(result)

query = """
SELECT
    Department,
    COUNT(*) AS High_Queue_Cases,
    ROUND(AVG(Waiting_Time_Minutes), 2) AS Average_Waiting_Time
FROM hospital_data
WHERE Queue_Length >= 15
GROUP BY Department
ORDER BY High_Queue_Cases DESC;
"""

result = pd.read_sql_query(
    query,
    connection
)

print("\nHigh Queue Analysis:")
print(result)

query = """
SELECT
    CASE
        WHEN Waiting_Time_Minutes <= 15 THEN 'Low'
        WHEN Waiting_Time_Minutes <= 30 THEN 'Moderate'
        ELSE 'High'
    END AS Waiting_Category,

    COUNT(*) AS Total_Patients,

    ROUND(
        AVG(Waiting_Time_Minutes), 2
    ) AS Average_Waiting_Time

FROM hospital_data

GROUP BY Waiting_Category

ORDER BY Average_Waiting_Time;
"""

result = pd.read_sql_query(
    query,
    connection
)

print("\nWaiting Time Category Analysis:")
print(result)



# --------------------------------------------------
# 5. Close Connection
# --------------------------------------------------

connection.close()

print("\nDatabase connection closed.")