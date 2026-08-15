import pandas as pd
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob


# =========================================================
# PATH SETUP
# =========================================================

# Folder containing this Usecase4.py file
CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Main Capstone Assessment folder
BASE_DIR = os.path.dirname(
    CURRENT_DIR
)


# =========================================================
# AUTOMATICALLY FIND THE CORRECT CHICAGO CRIME CSV
# =========================================================

csv_files = glob.glob(
    os.path.join(
        BASE_DIR,
        "**",
        "*.csv"
    ),
    recursive=True
)

if not csv_files:

    print("\nERROR: No CSV files found!")

    print("\nSearched inside:")
    print(BASE_DIR)

    raise SystemExit


# Required columns
required_columns = {
    "id",
    "date",
    "primary_type",
    "arrest"
}


CSV_FILE = None


# Check every CSV file
for file in csv_files:

    try:

        # Read only first row to check columns
        temp_df = pd.read_csv(
            file,
            nrows=1
        )

        # Convert all column names to lowercase
        columns = {
            str(column).strip().lower()
            for column in temp_df.columns
        }

        # Check if all required columns exist
        if required_columns.issubset(columns):

            CSV_FILE = file

            break

    except Exception:

        continue


# If correct dataset is not found
if CSV_FILE is None:

    print("\nERROR: Could not find the Chicago crime dataset.")

    print("\nCSV files found:")

    for file in csv_files:

        print(file)

    raise SystemExit


# =========================================================
# CHART DIRECTORY
# =========================================================

CHART_DIR = os.path.join(
    CURRENT_DIR,
    "static",
    "charts",
    "usecase4"
)

os.makedirs(
    CHART_DIR,
    exist_ok=True
)


print("\n========== PATH INFORMATION ==========")

print("\nCorrect Chicago crime dataset found:")

print(CSV_FILE)

print("\nChart folder:")

print(CHART_DIR)


# =========================================================
# USE CASE 4
# MYSQL REPORTING AND INTEGRATION
# =========================================================


# =========================================================
# 1. MYSQL CONNECTION CONFIGURATION
# =========================================================

MYSQL_CONFIG = {

    "host": "localhost",

    "user": "root",

    # CHANGE THIS TO YOUR MYSQL PASSWORD
    "password": "vishal1234",

    "port": 3306
}


# =========================================================
# 2. CONNECT TO MYSQL
# =========================================================

try:

    connection = mysql.connector.connect(
        **MYSQL_CONFIG
    )

    cursor = connection.cursor()

    print(
        "\nSuccessfully connected to MySQL Server."
    )


except Error as error:

    print(
        "\nERROR CONNECTING TO MYSQL:"
    )

    print(error)

    raise SystemExit


# =========================================================
# 3. CREATE DATABASE
# =========================================================

try:

    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS chicago_crime_db"
    )

    cursor.execute(
        "USE chicago_crime_db"
    )

    print(
        "Database chicago_crime_db is ready."
    )


except Error as error:

    print(
        "\nERROR CREATING DATABASE:"
    )

    print(error)

    cursor.close()

    connection.close()

    raise SystemExit


# =========================================================
# 4. LOAD CSV DATASET
# =========================================================

try:

    df = pd.read_csv(
        CSV_FILE
    )


except Exception as error:

    print(
        "\nERROR READING CSV FILE:"
    )

    print(error)

    cursor.close()

    connection.close()

    raise SystemExit


# Normalize column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)


print(
    "\nCrime dataset loaded successfully."
)

print(
    "Total records:",
    len(df)
)

print(
    "\nDataset columns:"
)

print(
    df.columns.tolist()
)


# =========================================================
# 5. FINAL CHECK FOR REQUIRED COLUMNS
# =========================================================

missing_columns = []

for column in required_columns:

    if column not in df.columns:

        missing_columns.append(
            column
        )


if missing_columns:

    print(
        "\nERROR: Required columns are missing!"
    )

    print(
        "Missing columns:",
        missing_columns
    )

    cursor.close()

    connection.close()

    raise SystemExit


# =========================================================
# 6. DATA PREPARATION
# =========================================================


# Convert date column to datetime
df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)


# Create additional columns
df["crime_year"] = (
    df["date"].dt.year
)

df["crime_month"] = (
    df["date"].dt.month
)

df["day_of_week"] = (
    df["date"].dt.day_name()
)


# Handle missing primary crime types
df["primary_type"] = (
    df["primary_type"]
    .fillna("UNKNOWN")
)


# =========================================================
# CLEAN ARREST COLUMN
# =========================================================

# Convert possible values to strings
df["arrest"] = (
    df["arrest"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# Convert arrest values to 1 or 0
df["arrest"] = (
    df["arrest"]
    .isin(
        [
            "true",
            "1",
            "yes"
        ]
    )
    .astype(int)
)


print(
    "\nData preparation completed successfully."
)


# =========================================================
# 7. CREATE MAIN MYSQL TABLE
# =========================================================

cursor.execute(
    "DROP TABLE IF EXISTS chicago_crimes"
)


cursor.execute(
    """
    CREATE TABLE chicago_crimes (

        id BIGINT,

        primary_type VARCHAR(100),

        arrest TINYINT,

        crime_year INT,

        crime_month INT,

        day_of_week VARCHAR(20)

    )
    """
)


connection.commit()


print(
    "\nMain table chicago_crimes created successfully."
)


# =========================================================
# 8. PREPARE DATA FOR MYSQL INSERTION
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
VALUES
(
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
)
"""


data_to_insert = []


for _, row in df.iterrows():

    # ID
    if pd.notna(row["id"]):

        crime_id = int(
            row["id"]
        )

    else:

        crime_id = None


    # Year
    if pd.notna(row["crime_year"]):

        crime_year = int(
            row["crime_year"]
        )

    else:

        crime_year = None


    # Month
    if pd.notna(row["crime_month"]):

        crime_month = int(
            row["crime_month"]
        )

    else:

        crime_month = None


    # Day of week
    if pd.notna(row["day_of_week"]):

        day_of_week = str(
            row["day_of_week"]
        )

    else:

        day_of_week = None


    data_to_insert.append(

        (
            crime_id,

            str(
                row["primary_type"]
            ),

            int(
                row["arrest"]
            ),

            crime_year,

            crime_month,

            day_of_week
        )
    )


# =========================================================
# 9. INSERT DATA INTO MYSQL
# =========================================================

try:

    cursor.executemany(
        insert_query,
        data_to_insert
    )

    connection.commit()

    print(
        f"\n{len(data_to_insert)} records inserted into MySQL successfully."
    )


except Error as error:

    print(
        "\nERROR INSERTING DATA:"
    )

    print(error)

    connection.rollback()

    cursor.close()

    connection.close()

    raise SystemExit


# =========================================================
# TASK 1
# CREATE SUMMARY TABLES
# =========================================================


# ---------------------------------------------------------
# YEARLY SUMMARY TABLE
# ---------------------------------------------------------

cursor.execute(
    "DROP TABLE IF EXISTS crime_yearly_summary"
)


cursor.execute(
    """
    CREATE TABLE crime_yearly_summary AS

    SELECT

        crime_year,

        COUNT(*) AS crime_count,

        SUM(arrest) AS arrest_count

    FROM chicago_crimes

    GROUP BY crime_year
    """
)


# ---------------------------------------------------------
# CRIME CATEGORY SUMMARY TABLE
# ---------------------------------------------------------

cursor.execute(
    "DROP TABLE IF EXISTS crime_category_summary"
)


cursor.execute(
    """
    CREATE TABLE crime_category_summary AS

    SELECT

        primary_type,

        COUNT(*) AS crime_count

    FROM chicago_crimes

    GROUP BY primary_type
    """
)


connection.commit()


print(
    "\nSummary tables created successfully."
)


# =========================================================
# TASK 2
# MYSQL QUERIES
# =========================================================


# ---------------------------------------------------------
# A. CRIME COUNT PER YEAR
# ---------------------------------------------------------

crime_yearly_query = """

SELECT

    crime_year,

    COUNT(*) AS crime_count

FROM chicago_crimes

WHERE crime_year IS NOT NULL

GROUP BY crime_year

ORDER BY crime_year

"""


cursor.execute(
    crime_yearly_query
)


crime_per_year = (
    cursor.fetchall()
)


print(
    "\n========== CRIME COUNT PER YEAR =========="
)


for row in crime_per_year:

    print(row)


# ---------------------------------------------------------
# B. TOP 5 CRIME TYPES AND PERCENTAGE
# ---------------------------------------------------------

top_5_crimes_query = """

SELECT

    primary_type,

    COUNT(*) AS crime_count,

    ROUND(

        COUNT(*) * 100.0 /

        (
            SELECT COUNT(*)
            FROM chicago_crimes
        ),

        2

    ) AS crime_percentage

FROM chicago_crimes

GROUP BY primary_type

ORDER BY crime_count DESC

LIMIT 5

"""


cursor.execute(
    top_5_crimes_query
)


top_5_crimes = (
    cursor.fetchall()
)


print(
    "\n========== TOP 5 CRIME TYPES =========="
)


for row in top_5_crimes:

    print(row)


# ---------------------------------------------------------
# C. ARREST COUNT PER YEAR
# ---------------------------------------------------------

arrest_yearly_query = """

SELECT

    crime_year,

    SUM(arrest) AS arrest_count

FROM chicago_crimes

WHERE crime_year IS NOT NULL

GROUP BY crime_year

ORDER BY crime_year

"""


cursor.execute(
    arrest_yearly_query
)


arrest_per_year = (
    cursor.fetchall()
)


print(
    "\n========== ARREST COUNT PER YEAR =========="
)


for row in arrest_per_year:

    print(row)


# =========================================================
# TASK 3
# CREATE MYSQL VIEWS
# =========================================================


# ---------------------------------------------------------
# VIEW 1
# YEARLY CRIME VIEW
# ---------------------------------------------------------

cursor.execute(
    "DROP VIEW IF EXISTS vw_crime_yearly"
)


cursor.execute(
    """

    CREATE VIEW vw_crime_yearly AS

    SELECT

        crime_year,

        COUNT(*) AS crime_count,

        SUM(arrest) AS arrest_count

    FROM chicago_crimes

    WHERE crime_year IS NOT NULL

    GROUP BY crime_year

    """
)


# ---------------------------------------------------------
# VIEW 2
# CRIME CATEGORY VIEW
# ---------------------------------------------------------

cursor.execute(
    "DROP VIEW IF EXISTS vw_crime_by_category"
)


cursor.execute(
    """

    CREATE VIEW vw_crime_by_category AS

    SELECT

        primary_type,

        COUNT(*) AS crime_count,

        ROUND(

            COUNT(*) * 100.0 /

            (
                SELECT COUNT(*)
                FROM chicago_crimes
            ),

            2

        ) AS crime_percentage

    FROM chicago_crimes

    GROUP BY primary_type

    """
)


connection.commit()


print(
    "\nDatabase views created successfully."
)


# =========================================================
# TASK 4
# PANDAS AND MYSQL INTEGRATION
# =========================================================


yearly_df = pd.read_sql(

    """

    SELECT *

    FROM vw_crime_yearly

    ORDER BY crime_year

    """,

    connection
)


category_df = pd.read_sql(

    """

    SELECT *

    FROM vw_crime_by_category

    ORDER BY crime_count DESC

    """,

    connection
)


print(
    "\n========== YEARLY CRIME DATA =========="
)

print(
    yearly_df
)


print(
    "\n========== TOP CRIME CATEGORY DATA =========="
)

print(
    category_df.head(10)
)


# =========================================================
# TASK 5
# VISUALIZATION FROM MYSQL DATA
# =========================================================


# ---------------------------------------------------------
# GRAPH 1
# CRIME COUNT PER YEAR
# ---------------------------------------------------------

plt.figure(
    figsize=(10, 5)
)


plt.plot(
    yearly_df["crime_year"],
    yearly_df["crime_count"],
    marker="o"
)


plt.title(
    "Crime Count Per Year - MySQL Data"
)

plt.xlabel(
    "Year"
)

plt.ylabel(
    "Crime Count"
)

plt.grid(
    True
)


plt.tight_layout()


plt.savefig(

    os.path.join(
        CHART_DIR,
        "crime_yearly.png"
    ),

    bbox_inches="tight"
)


plt.close()


# ---------------------------------------------------------
# GRAPH 2
# ARREST COUNT PER YEAR
# ---------------------------------------------------------

plt.figure(
    figsize=(10, 5)
)


plt.bar(
    yearly_df["crime_year"].astype(str),

    yearly_df["arrest_count"]
)


plt.title(
    "Arrest Count Per Year - MySQL Data"
)

plt.xlabel(
    "Year"
)

plt.ylabel(
    "Arrest Count"
)


plt.xticks(
    rotation=45
)


plt.tight_layout()


plt.savefig(

    os.path.join(
        CHART_DIR,
        "arrest_yearly.png"
    ),

    bbox_inches="tight"
)


plt.close()


# ---------------------------------------------------------
# GRAPH 3
# TOP 10 CRIME CATEGORIES
# ---------------------------------------------------------

top_categories = (
    category_df.head(10)
)


plt.figure(
    figsize=(12, 6)
)


sns.barplot(

    data=top_categories,

    x="crime_count",

    y="primary_type"
)


plt.title(
    "Top 10 Crime Categories - MySQL Data"
)

plt.xlabel(
    "Crime Count"
)

plt.ylabel(
    "Crime Type"
)


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
# CLOSE MYSQL CONNECTION
# =========================================================

cursor.close()

connection.close()


# =========================================================
# FINAL OUTPUT
# =========================================================

print(
    "\n========================================"
)

print(
    "USE CASE 4 COMPLETED SUCCESSFULLY"
)

print(
    "========================================"
)


print(
    "\nDatabase Created:"
)

print(
    "chicago_crime_db"
)


print(
    "\nMain Table:"
)

print(
    "chicago_crimes"
)


print(
    "\nSummary Tables:"
)

print(
    "crime_yearly_summary"
)

print(
    "crime_category_summary"
)


print(
    "\nDatabase Views:"
)

print(
    "vw_crime_yearly"
)

print(
    "vw_crime_by_category"
)


print(
    "\nGraphs Saved:"
)

print(
    "crime_yearly.png"
)

print(
    "arrest_yearly.png"
)

print(
    "top_categories.png"
)


print(
    "\nGraph folder:"
)

print(
    CHART_DIR
)

print(
    "\n========================================"
)