import pandas as pd
import numpy as np
import sqlite3

CSV_FILE = "data/chicago_crime_dataset.csv"
df = pd.read_csv(CSV_FILE)

print("\n========== FIRST 10 ROWS ==========")
print(df.head(10))

print("\n========== DATASET INFO ==========")
df.info()

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== DATASET SHAPE ==========")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# DATE CONVERSION AND MISSING VALUES

df["date"] = pd.to_datetime(df["date"], errors="coerce")

print("\nDate column converted to datetime.")

print("\n========== MISSING VALUES BEFORE CLEANING ==========")
print(df.isnull().sum())

missing_percentage = np.round(
    (df.isnull().sum().to_numpy() / len(df)) * 100,
    2
)

missing_df = pd.DataFrame({
    "column_name": df.columns,
    "missing_percentage": missing_percentage
})

print("\n========== MISSING VALUE PERCENTAGE ==========")
print(missing_df)

columns_to_drop = missing_df[
    missing_df["missing_percentage"] > 50
]["column_name"].tolist()

if columns_to_drop:
    print("\nDropping columns:", columns_to_drop)
    df.drop(columns=columns_to_drop, inplace=True)
else:
    print("\nNo columns have more than 50% missing values.")

numeric_columns = df.select_dtypes(
    include=np.number
).columns

for column in numeric_columns:
    if df[column].isnull().sum() > 0:
        df[column] = df[column].fillna(
            df[column].median()
        )

categorical_columns = df.select_dtypes(
    include=["object", "string"]
).columns

for column in categorical_columns:
    if df[column].isnull().sum() > 0:
        df[column] = df[column].fillna("Unknown")

for column in categorical_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .str.upper()
    )

# CREATE DATE-BASED FEATURES

df["crime_year"] = df["date"].dt.year
df["crime_month"] = df["date"].dt.month
df["day_of_week"] = df["date"].dt.day_name()

print("\n========== CLEANED DATA ==========")
print(df.head(10))

print("\n========== MISSING VALUES AFTER CLEANING ==========")
print(df.isnull().sum())

# SAVE DATA TO SQLITE

DATABASE_FILE = "chicago_crime.db"
connection = sqlite3.connect(DATABASE_FILE)

try:
    df.to_sql(
        "chicago_crimes",
        connection,
        if_exists="replace",
        index=False
    )

    print(
        "\nData successfully inserted into SQLite database."
    )

finally:
    connection.close()

# FINAL OUTPUT

print("\n========================================")
print("USE CASE 1 COMPLETED SUCCESSFULLY")
print("========================================")
print(f"Database file: {DATABASE_FILE}")
print("Table name: chicago_crimes")
print(f"Final rows: {df.shape[0]}")
print(f"Final columns: {df.shape[1]}")
print("========================================")