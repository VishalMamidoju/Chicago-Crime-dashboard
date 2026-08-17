import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob

# =========================================================
# PATH SETUP
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

# Find Chicago crime CSV automatically
csv_files = glob.glob(
    os.path.join(BASE_DIR, "**", "*.csv"),
    recursive=True
)

if not csv_files:
    print("\nERROR: No CSV files found!")
    print("Searched inside:", BASE_DIR)
    raise SystemExit

required_columns = {"id", "date", "primary_type", "arrest"}
CSV_FILE = None

# Find correct Chicago crime dataset
for file in csv_files:
    try:
        temp_df = pd.read_csv(file, nrows=1)
        columns = {
            str(column).strip().lower()
            for column in temp_df.columns
        }

        if required_columns.issubset(columns):
            CSV_FILE = file
            break

    except Exception:
        continue

if CSV_FILE is None:
    print("\nERROR: Could not find the Chicago crime dataset.")
    print("\nCSV files found:")

    for file in csv_files:
        print(file)

    raise SystemExit

# SQLite database file
DATABASE_FILE = os.path.join(
    CURRENT_DIR,
    "chicago_crime_usecase4.db"
)

# Chart folder
CHART_DIR = os.path.join(
    CURRENT_DIR,
    "static",
    "charts",
    "usecase4"
)

os.makedirs(CHART_DIR, exist_ok=True)

print("\n========== PATH INFORMATION ==========")
print("\nDataset:")
print(CSV_FILE)
print("\nSQLite Database:")
print(DATABASE_FILE)
print("\nChart folder:")
print(CHART_DIR)

# =========================================================
# USE CASE 4 - SQLITE REPORTING AND INTEGRATION
# =========================================================

# Connect to SQLite
try:
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    print("\nSuccessfully connected to SQLite.")

except Exception as error:
    print("\nERROR CONNECTING TO SQLITE:")
    print(error)
    raise SystemExit

# =========================================================
# LOAD CSV DATASET
# =========================================================

try:
    df = pd.read_csv(CSV_FILE)

except Exception as error:
    print("\nERROR READING CSV FILE:")
    print(error)

    connection.close()
    raise SystemExit

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

print("\nCrime dataset loaded successfully.")
print("Total records:", len(df))
print("Dataset columns:")
print(df.columns.tolist())

# Check required columns
missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("\nERROR: Required columns are missing!")
    print("Missing columns:", missing_columns)

    connection.close()
    raise SystemExit

# =========================================================
# DATA PREPARATION
# =========================================================

# Convert date to datetime
df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

# Create date features
df["crime_year"] = df["date"].dt.year
df["crime_month"] = df["date"].dt.month
df["day_of_week"] = df["date"].dt.day_name()

# Handle missing crime categories
df["primary_type"] = df["primary_type"].fillna("UNKNOWN")

# Convert arrest to 1 or 0
df["arrest"] = (
    df["arrest"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["true", "1", "yes"])
    .astype(int)
)

print("\nData preparation completed successfully.")

# =========================================================
# CREATE MAIN SQLITE TABLE
# =========================================================

cursor.execute(
    "DROP TABLE IF EXISTS chicago_crimes"
)

cursor.execute("""
CREATE TABLE chicago_crimes (
    id INTEGER,
    primary_type TEXT,
    arrest INTEGER,
    crime_year INTEGER,
    crime_month INTEGER,
    day_of_week TEXT
)
""")

connection.commit()

print("\nMain table chicago_crimes created successfully.")

# =========================================================
# PREPARE DATA FOR INSERTION
# =========================================================

insert_query = """
INSERT INTO chicago_crimes
(
    id,
    primary_type,
    arrest,
    crime_year,
    crime_month,
    day_of_week
)
VALUES (?, ?, ?, ?, ?, ?)
"""

data_to_insert = []

for _, row in df.iterrows():

    crime_id = (
        int(row["id"])
        if pd.notna(row["id"])
        else None
    )

    crime_year = (
        int(row["crime_year"])
        if pd.notna(row["crime_year"])
        else None
    )

    crime_month = (
        int(row["crime_month"])
        if pd.notna(row["crime_month"])
        else None
    )

    day_of_week = (
        str(row["day_of_week"])
        if pd.notna(row["day_of_week"])
        else None
    )

    data_to_insert.append(
        (
            crime_id,
            str(row["primary_type"]),
            int(row["arrest"]),
            crime_year,
            crime_month,
            day_of_week
        )
    )

# =========================================================
# INSERT DATA INTO SQLITE
# =========================================================

try:
    cursor.executemany(
        insert_query,
        data_to_insert
    )

    connection.commit()

    print(
        f"\n{len(data_to_insert)} records inserted successfully."
    )

except Exception as error:
    print("\nERROR INSERTING DATA:")
    print(error)

    connection.rollback()
    connection.close()

    raise SystemExit

# =========================================================
# TASK 1 - CREATE SUMMARY TABLES
# =========================================================

# Yearly summary table
cursor.execute(
    "DROP TABLE IF EXISTS crime_yearly_summary"
)

cursor.execute("""
CREATE TABLE crime_yearly_summary AS
SELECT
    crime_year,
    COUNT(*) AS crime_count,
    SUM(arrest) AS arrest_count
FROM chicago_crimes
GROUP BY crime_year
""")

# Crime category summary
cursor.execute(
    "DROP TABLE IF EXISTS crime_category_summary"
)

cursor.execute("""
CREATE TABLE crime_category_summary AS
SELECT
    primary_type,
    COUNT(*) AS crime_count
FROM chicago_crimes
GROUP BY primary_type
""")

connection.commit()

print("\nSummary tables created successfully.")

# =========================================================
# TASK 2 - SQLITE QUERIES
# =========================================================

# Crime count per year
crime_yearly_query = """
SELECT
    crime_year,
    COUNT(*) AS crime_count
FROM chicago_crimes
WHERE crime_year IS NOT NULL
GROUP BY crime_year
ORDER BY crime_year
"""

cursor.execute(crime_yearly_query)
crime_per_year = cursor.fetchall()

print("\n========== CRIME COUNT PER YEAR ==========")

for row in crime_per_year:
    print(row)

# Top 5 crime types
top_5_crimes_query = """
SELECT
    primary_type,
    COUNT(*) AS crime_count,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM chicago_crimes),
        2
    ) AS crime_percentage
FROM chicago_crimes
GROUP BY primary_type
ORDER BY crime_count DESC
LIMIT 5
"""

cursor.execute(top_5_crimes_query)
top_5_crimes = cursor.fetchall()

print("\n========== TOP 5 CRIME TYPES ==========")

for row in top_5_crimes:
    print(row)

# Arrest count per year
arrest_yearly_query = """
SELECT
    crime_year,
    SUM(arrest) AS arrest_count
FROM chicago_crimes
WHERE crime_year IS NOT NULL
GROUP BY crime_year
ORDER BY crime_year
"""

cursor.execute(arrest_yearly_query)
arrest_per_year = cursor.fetchall()

print("\n========== ARREST COUNT PER YEAR ==========")

for row in arrest_per_year:
    print(row)

# =========================================================
# TASK 3 - CREATE SQLITE VIEWS
# =========================================================

# Yearly crime view
cursor.execute(
    "DROP VIEW IF EXISTS vw_crime_yearly"
)

cursor.execute("""
CREATE VIEW vw_crime_yearly AS
SELECT
    crime_year,
    COUNT(*) AS crime_count,
    SUM(arrest) AS arrest_count
FROM chicago_crimes
WHERE crime_year IS NOT NULL
GROUP BY crime_year
""")

# Crime category view
cursor.execute(
    "DROP VIEW IF EXISTS vw_crime_by_category"
)

cursor.execute("""
CREATE VIEW vw_crime_by_category AS
SELECT
    primary_type,
    COUNT(*) AS crime_count,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM chicago_crimes),
        2
    ) AS crime_percentage
FROM chicago_crimes
GROUP BY primary_type
""")

connection.commit()

print("\nDatabase views created successfully.")

# =========================================================
# TASK 4 - PANDAS AND SQLITE INTEGRATION
# =========================================================

yearly_df = pd.read_sql("""
SELECT *
FROM vw_crime_yearly
ORDER BY crime_year
""", connection)

category_df = pd.read_sql("""
SELECT *
FROM vw_crime_by_category
ORDER BY crime_count DESC
""", connection)

print("\n========== YEARLY CRIME DATA ==========")
print(yearly_df)

print("\n========== TOP CRIME CATEGORY DATA ==========")
print(category_df.head(10))

# =========================================================
# TASK 5 - VISUALIZATION
# =========================================================

# Graph 1: Crime count per year
plt.figure(figsize=(10, 5))

plt.plot(
    yearly_df["crime_year"],
    yearly_df["crime_count"],
    marker="o"
)

plt.title("Crime Count Per Year - SQLite Data")
plt.xlabel("Year")
plt.ylabel("Crime Count")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "crime_yearly.png"
    ),
    bbox_inches="tight"
)

plt.close()

# Graph 2: Arrest count per year
plt.figure(figsize=(10, 5))

plt.bar(
    yearly_df["crime_year"].astype(str),
    yearly_df["arrest_count"]
)

plt.title("Arrest Count Per Year - SQLite Data")
plt.xlabel("Year")
plt.ylabel("Arrest Count")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "arrest_yearly.png"
    ),
    bbox_inches="tight"
)

plt.close()

# Graph 3: Top crime categories
top_categories = category_df.head(10)

plt.figure(figsize=(12, 6))

sns.barplot(
    data=top_categories,
    x="crime_count",
    y="primary_type"
)

plt.title("Top 10 Crime Categories - SQLite Data")
plt.xlabel("Crime Count")
plt.ylabel("Crime Type")

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "top_categories.png"
    ),
    bbox_inches="tight"
)

plt.close()

# =========================================================
# CLOSE CONNECTION
# =========================================================

cursor.close()
connection.close()

# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n========================================")
print("USE CASE 4 COMPLETED SUCCESSFULLY")
print("========================================")

print("\nSQLite Database:")
print(DATABASE_FILE)

print("\nMain Table:")
print("chicago_crimes")

print("\nSummary Tables:")
print("crime_yearly_summary")
print("crime_category_summary")

print("\nDatabase Views:")
print("vw_crime_yearly")
print("vw_crime_by_category")

print("\nGraphs Saved:")
print("crime_yearly.png")
print("arrest_yearly.png")
print("top_categories.png")

print("\nGraph folder:")
print(CHART_DIR)

print("\n========================================")