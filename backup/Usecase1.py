import pandas as pd
import numpy as np
import sqlite3

# =========================================================
# USE CASE 1
# DATA LOADING, INSPECTION, CLEANING AND SQLITE STORAGE
# =========================================================


# ---------------------------------------------------------
# 1. LOAD THE CSV FILE
# ---------------------------------------------------------

CSV_FILE = "data/chicago_crime_dataset.csv"

df = pd.read_csv(CSV_FILE)


# ---------------------------------------------------------
# 2. INSPECT THE DATASET
# ---------------------------------------------------------

print("\n========== FIRST 10 ROWS ==========")
print(df.head(10))

print("\n========== DATASET INFO ==========")
df.info()

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== DATASET SHAPE ==========")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# ---------------------------------------------------------
# 3. CONVERT DATE COLUMN TO DATETIME
# ---------------------------------------------------------

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

print("\nDate column converted to datetime.")


# ---------------------------------------------------------
# 4. CHECK MISSING VALUES
# ---------------------------------------------------------

print("\n========== MISSING VALUES BEFORE CLEANING ==========")
print(df.isnull().sum())


# ---------------------------------------------------------
# 5. CALCULATE MISSING VALUE PERCENTAGE USING NUMPY
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# 6. DROP COLUMNS WITH MORE THAN 50% MISSING VALUES
# ---------------------------------------------------------

columns_to_drop = missing_df[
    missing_df["missing_percentage"] > 50
]["column_name"].tolist()

if columns_to_drop:
    print("\nDropping columns with more than 50% missing values:")
    print(columns_to_drop)

    df.drop(
        columns=columns_to_drop,
        inplace=True
    )
else:
    print("\nNo columns have more than 50% missing values.")


# ---------------------------------------------------------
# 7. HANDLE MISSING NUMERIC VALUES
#    Fill with median
# ---------------------------------------------------------

numeric_columns = df.select_dtypes(
    include=np.number
).columns

for column in numeric_columns:

    if df[column].isnull().sum() > 0:
        df[column] = df[column].fillna(
            df[column].median()
        )


# ---------------------------------------------------------
# 8. HANDLE MISSING CATEGORICAL VALUES
#    Fill with "Unknown"
# ---------------------------------------------------------

categorical_columns = df.select_dtypes(
    include=["object", "string"]
).columns

for column in categorical_columns:

    if df[column].isnull().sum() > 0:
        df[column] = df[column].fillna(
            "Unknown"
        )


# ---------------------------------------------------------
# 9. STANDARDIZE CATEGORICAL FIELDS
# ---------------------------------------------------------

for column in categorical_columns:

    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .str.upper()
    )


# ---------------------------------------------------------
# 10. CREATE DATE-BASED FEATURES
#
# Using different names because the dataset already contains
# a column named "year", and SQLite is case-insensitive.
# ---------------------------------------------------------

df["crime_year"] = df["date"].dt.year

df["crime_month"] = df["date"].dt.month

df["day_of_week"] = df["date"].dt.day_name()


# ---------------------------------------------------------
# 11. DISPLAY CLEANED DATA
# ---------------------------------------------------------

print("\n========== CLEANED DATA ==========")
print(df.head(10))


# ---------------------------------------------------------
# 12. CHECK MISSING VALUES AFTER CLEANING
# ---------------------------------------------------------

print("\n========== MISSING VALUES AFTER CLEANING ==========")
print(df.isnull().sum())


# ---------------------------------------------------------
# 13. INSERT CLEANED DATA INTO SQLITE DATABASE
# ---------------------------------------------------------

DATABASE_FILE = "chicago_crime.db"

connection = sqlite3.connect(DATABASE_FILE)

try:

    df.to_sql(
        "chicago_crimes",
        connection,
        if_exists="replace",
        index=False
    )

    print("\nData successfully inserted into SQLite database.")

finally:

    connection.close()


# ---------------------------------------------------------
# 14. FINAL OUTPUT
# ---------------------------------------------------------

print("\n========================================")
print("USE CASE 1 COMPLETED SUCCESSFULLY")
print("========================================")

print("Database file:", DATABASE_FILE)

print("Table name: chicago_crimes")

print("Final rows:", df.shape[0])

print("Final columns:", df.shape[1])

print("========================================")