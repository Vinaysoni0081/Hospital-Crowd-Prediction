import pandas as pd


# --------------------------------------------------
# 1. Load Dataset
# --------------------------------------------------

df = pd.read_csv("data/hospital_data.csv")


# --------------------------------------------------
# 2. Basic Information
# --------------------------------------------------

print("Dataset loaded successfully!")

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# --------------------------------------------------
# 3. First 5 Records
# --------------------------------------------------

print("\nFirst 5 records:")
print(df.head())


# --------------------------------------------------
# 4. Data Types
# --------------------------------------------------

print("\nData Types:")
print(df.dtypes)


# --------------------------------------------------
# 5. Missing Values
# --------------------------------------------------

print("\nMissing Values:")
print(df.isnull().sum())


# --------------------------------------------------
# 6. Duplicate Records
# --------------------------------------------------

print("\nDuplicate Records:")
print(df.duplicated().sum())


# --------------------------------------------------
# 7. Statistical Summary
# --------------------------------------------------

print("\nStatistical Summary:")
print(df.describe())


# --------------------------------------------------
# 8. Unique Values
# --------------------------------------------------

print("\nDepartments:")
print(df["Department"].unique())

print("\nPatient Types:")
print(df["Patient_Type"].unique())


# --------------------------------------------------
# 9. Basic Validation
# --------------------------------------------------

print("\nInvalid Queue Length:")
print((df["Queue_Length"] <= 0).sum())

print("\nInvalid Doctors Available:")
print((df["Doctors_Available"] <= 0).sum())

print("\nInvalid Waiting Time:")
print((df["Waiting_Time_Minutes"] <= 0).sum())


print("\nData validation completed!")