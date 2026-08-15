import pandas as pd
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns


# =========================================================
# USE CASE 4
# MYSQL REPORTING & INTEGRATION
# =========================================================


# ---------------------------------------------------------
# 1. MYSQL CONNECTION CONFIGURATION
# ---------------------------------------------------------

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "vishal1234",
    "port": 3306
}


# ---------------------------------------------------------
# 2. CONNECT TO MYSQL SERVER
# ---------------------------------------------------------

try:
    connection = mysql.connector.connect(**MYSQL_CONFIG)

    cursor = connection.cursor()

    print("\nSuccessfully connected to MySQL Server.")

except Error as error:
    print("\nError connecting to MySQL:")
    print(error)
    raise SystemExit


# ---------------------------------------------------------
# 3. CREATE AND SELECT DATABASE
# ---------------------------------------------------------

cursor.execute(
    "CREATE DATABASE IF NOT EXISTS chicago_crime_db"
)

cursor.execute(
    "USE chicago_crime_db"
)

print("Database chicago_crime_db is ready.")


# ---------------------------------------------------------
# 4. LOAD CRIME DATA
# ---------------------------------------------------------

CSV_FILE = "data/chicago_crime_dataset.csv"

df = pd.read_csv(CSV_FILE)

print("\nCrime dataset loaded successfully.")
print("Total records:", len(df))


# ---------------------------------------------------------
# 5. PREPARE DATA
# ---------------------------------------------------------

# Convert date column to datetime
df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

# Create required columns
df["crime_year"] = df["date"].dt.year
df["crime_month"] = df["date"].dt.month
df["day_of_week"] = df["date"].dt.day_name()


# ---------------------------------------------------------
# 6. HANDLE MISSING VALUES
# ---------------------------------------------------------

df["primary_type"] = df["primary_type"].fillna(
    "UNKNOWN"
)

df["arrest"] = df["arrest"].fillna(
    False
)


# ---------------------------------------------------------
# 7. CREATE MAIN CRIME TABLE
# ---------------------------------------------------------

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chicago_crimes (
        id BIGINT,
        primary_type VARCHAR(100),
        arrest BOOLEAN,
        crime_year INT,
        crime_month INT,
        day_of_week VARCHAR(20)
    )
    """
)

print("Main table chicago_crimes is ready.")


# ---------------------------------------------------------
# 8. CLEAR OLD DATA
# ---------------------------------------------------------

cursor.execute(
    "DELETE FROM chicago_crimes"
)

connection.commit()


# ---------------------------------------------------------
# 9. PREPARE DATA FOR INSERTION
# ---------------------------------------------------------

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
VALUES (%s, %s, %s, %s, %s, %s)
"""


data_to_insert = []

for _, row in df.iterrows():

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
            int(row["id"]),
            str(row["primary_type"]),
            bool(row["arrest"]),
            crime_year,
            crime_month,
            day_of_week
        )
    )


# ---------------------------------------------------------
# 10. INSERT DATA INTO MYSQL
# ---------------------------------------------------------

cursor.executemany(
    insert_query,
    data_to_insert
)

connection.commit()

print(
    f"{len(data_to_insert)} records inserted into MySQL."
)


# =========================================================
# TASK 1: DESIGN & POPULATE SUMMARY TABLES
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
        SUM(arrest = 1) AS arrest_count
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

print("\nSummary tables created successfully.")


# =========================================================
# TASK 2: MYSQL QUERIES
# =========================================================


# ---------------------------------------------------------
# A. CRIME COUNT PER YEAR
# ---------------------------------------------------------

crime_yearly_query = """
SELECT
    crime_year,
    COUNT(*) AS crime_count
FROM chicago_crimes
GROUP BY crime_year
ORDER BY crime_year
"""

cursor.execute(crime_yearly_query)

crime_per_year = cursor.fetchall()

print("\n========== CRIME COUNT PER YEAR ==========")

for row in crime_per_year:
    print(row)


# ---------------------------------------------------------
# B. TOP 5 CRIME TYPES AND PERCENTAGES
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# C. ARREST COUNT PER YEAR
# ---------------------------------------------------------

arrest_yearly_query = """
SELECT
    crime_year,
    SUM(arrest = 1) AS arrest_count
FROM chicago_crimes
GROUP BY crime_year
ORDER BY crime_year
"""

cursor.execute(arrest_yearly_query)

arrest_per_year = cursor.fetchall()

print("\n========== ARREST COUNT PER YEAR ==========")

for row in arrest_per_year:
    print(row)


# =========================================================
# TASK 3: DATABASE STORED VIEWS
# =========================================================


# ---------------------------------------------------------
# VIEW 1: YEARLY CRIME VIEW
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
        SUM(arrest = 1) AS arrest_count

    FROM chicago_crimes

    GROUP BY crime_year
    """
)


# ---------------------------------------------------------
# VIEW 2: CRIME BY CATEGORY VIEW
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
            (SELECT COUNT(*) FROM chicago_crimes),
            2
        ) AS crime_percentage

    FROM chicago_crimes

    GROUP BY primary_type
    """
)

connection.commit()

print("\nDatabase views created successfully.")


# =========================================================
# TASK 4: PANDAS INTEGRATION
# =========================================================


# ---------------------------------------------------------
# READ YEARLY VIEW INTO PANDAS
# ---------------------------------------------------------

yearly_df = pd.read_sql(
    """
    SELECT *
    FROM vw_crime_yearly
    ORDER BY crime_year
    """,
    connection
)


# ---------------------------------------------------------
# READ CATEGORY VIEW INTO PANDAS
# ---------------------------------------------------------

category_df = pd.read_sql(
    """
    SELECT *
    FROM vw_crime_by_category
    ORDER BY crime_count DESC
    """,
    connection
)


print("\n========== DATA FROM vw_crime_yearly ==========")
print(yearly_df)


print("\n========== DATA FROM vw_crime_by_category ==========")
print(category_df.head(10))


# =========================================================
# TASK 5: VISUALIZATION FROM MYSQL DATA
# =========================================================


# ---------------------------------------------------------
# A. CRIME COUNT PER YEAR
# ---------------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    yearly_df["crime_year"],
    yearly_df["crime_count"],
    marker="o"
)

plt.title("Crime Count Per Year - MySQL Data")
plt.xlabel("Year")
plt.ylabel("Crime Count")

plt.grid(True)

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# B. ARREST COUNT PER YEAR
# ---------------------------------------------------------

plt.figure(figsize=(10, 5))

plt.bar(
    yearly_df["crime_year"].astype(str),
    yearly_df["arrest_count"]
)

plt.title("Arrest Count Per Year - MySQL Data")
plt.xlabel("Year")
plt.ylabel("Arrest Count")

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# C. TOP 10 CRIME CATEGORIES
# ---------------------------------------------------------

top_categories = category_df.head(10)

plt.figure(figsize=(12, 6))

sns.barplot(
    data=top_categories,
    x="crime_count",
    y="primary_type"
)

plt.title("Top 10 Crime Categories - MySQL Data")
plt.xlabel("Crime Count")
plt.ylabel("Crime Type")

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# 11. CLOSE MYSQL CONNECTION
# ---------------------------------------------------------

cursor.close()

connection.close()


# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n========================================")
print("USE CASE 4 COMPLETED SUCCESSFULLY")
print("========================================")

print("\n1. DESIGN & POPULATE SUMMARY TABLES")
print("✓ crime_yearly_summary")
print("✓ crime_category_summary")

print("\n2. MYSQL QUERIES")
print("✓ Crime count per year")
print("✓ Top 5 crime types and percentages")
print("✓ Arrest count per year")

print("\n3. DATABASE STORED VIEWS")
print("✓ vw_crime_yearly")
print("✓ vw_crime_by_category")

print("\n4. PANDAS INTEGRATION")
print("✓ MySQL views loaded into Pandas DataFrames")

print("\n5. VISUALIZATION FROM MYSQL DATA")
print("✓ Crime count per year graph")
print("✓ Arrest count per year graph")
print("✓ Top crime categories graph")

print("\n========================================")