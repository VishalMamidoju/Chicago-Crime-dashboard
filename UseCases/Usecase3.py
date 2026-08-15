import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import os


# =========================================================
# PATH SETUP
# =========================================================

# Folder where this Usecase3.py file is located
CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Main project folder
BASE_DIR = os.path.dirname(CURRENT_DIR)


# SQLite database created by Usecase1.py
DATABASE_FILE = os.path.join(
    CURRENT_DIR,
    "chicago_crime.db"
)


# Folder where graphs will be saved
CHART_DIR = os.path.join(
    CURRENT_DIR,
    "static",
    "charts",
    "usecase3"
)


# Create chart folder automatically
os.makedirs(
    CHART_DIR,
    exist_ok=True
)


print("\nDatabase path:", DATABASE_FILE)
print("Chart folder:", CHART_DIR)


# =========================================================
# CHECK DATABASE
# =========================================================

if not os.path.exists(DATABASE_FILE):

    print("\nERROR: Database file not found!")

    print("\nExpected location:")
    print(DATABASE_FILE)

    print("\nPlease run Usecase1.py first.")

    raise SystemExit


# =========================================================
# CONNECT TO SQLITE DATABASE
# =========================================================

connection = sqlite3.connect(
    DATABASE_FILE
)

cursor = connection.cursor()


# Check available tables
tables = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    """
).fetchall()


print("\nTables found in database:")
print(tables)


table_names = [
    table[0]
    for table in tables
]


# Check required table
if "chicago_crimes" not in table_names:

    print(
        "\nERROR: Table 'chicago_crimes' does not exist!"
    )

    print("\nAvailable tables:")
    print(table_names)

    connection.close()

    raise SystemExit


# =========================================================
# USE CASE 3
# STATISTICAL INSIGHTS AND PATTERN DETECTION
# =========================================================


# ---------------------------------------------------------
# 1. LOAD DATA FROM SQLITE DATABASE
# ---------------------------------------------------------

df = pd.read_sql_query(
    "SELECT * FROM chicago_crimes",
    connection
)


connection.close()


print(
    "\nData successfully loaded from SQLite database."
)

print(
    "Total Records:",
    len(df)
)


print("\nAvailable Columns:")
print(
    df.columns.tolist()
)


# =========================================================
# COLUMN COMPATIBILITY
# =========================================================

# Ensure date is in datetime format
df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)


# ---------------------------------------------------------
# POINT 1: CRIME INTENSITY BY TIME
# ---------------------------------------------------------

df["crime_hour"] = df[
    "date"
].dt.hour


hourly_crimes = (
    df.groupby("crime_hour")
    .size()
)


print(
    "\n========== CRIME FREQUENCY BY HOUR =========="
)

print(
    hourly_crimes
)


peak_hour = (
    hourly_crimes.idxmax()
)

peak_crimes = (
    hourly_crimes.max()
)


print(
    "\n========== PEAK CRIME TIME =========="
)

print(
    "Peak Crime Hour:",
    peak_hour
)

print(
    "Number of Crimes:",
    peak_crimes
)


# =========================================================
# GRAPH 1: CRIME INTENSITY BY HOUR
# =========================================================

plt.figure(
    figsize=(10, 5)
)


plt.plot(
    hourly_crimes.index,
    hourly_crimes.values,
    marker="o"
)


plt.title(
    "Crime Intensity by Hour"
)

plt.xlabel(
    "Hour of the Day"
)

plt.ylabel(
    "Number of Crimes"
)

plt.xticks(
    range(0, 24)
)

plt.grid(True)

plt.tight_layout()


plt.savefig(
    os.path.join(
        CHART_DIR,
        "crime_by_hour.png"
    ),
    bbox_inches="tight"
)


plt.close()


# =========================================================
# POINT 2: COMMUNITY AREA ANALYSIS USING NUMPY
# =========================================================

community_data = df[
    "community_code"
].dropna()


community_array = (
    community_data.to_numpy()
)


unique_communities = np.unique(
    community_array
)


community_counts = np.array([
    np.sum(
        community_array == community
    )
    for community in unique_communities
])


community_stats = pd.DataFrame({
    "community_code":
        unique_communities,

    "crime_count":
        community_counts
})


community_stats = (
    community_stats
    .sort_values(
        by="crime_count",
        ascending=False
    )
)


print(
    "\n========== COMMUNITY AREA CRIME STATISTICS =========="
)

print(
    community_stats.head(10)
)


print(
    "\n========== NUMPY STATISTICAL INSIGHTS =========="
)

print(
    "Average crimes per community:",
    np.mean(community_counts)
)

print(
    "Maximum crimes in a community:",
    np.max(community_counts)
)

print(
    "Minimum crimes in a community:",
    np.min(community_counts)
)

print(
    "Standard deviation:",
    np.std(community_counts)
)


# =========================================================
# GRAPH 2: TOP 10 COMMUNITY AREAS
# =========================================================

top_10_communities = (
    community_stats.head(10)
)


plt.figure(
    figsize=(10, 6)
)


plt.bar(
    top_10_communities[
        "community_code"
    ].astype(str),

    top_10_communities[
        "crime_count"
    ]
)


plt.title(
    "Top 10 Community Areas by Crime Count"
)

plt.xlabel(
    "Community Code"
)

plt.ylabel(
    "Number of Crimes"
)


plt.tight_layout()


plt.savefig(
    os.path.join(
        CHART_DIR,
        "community_crimes.png"
    ),
    bbox_inches="tight"
)


plt.close()


# =========================================================
# POINT 3: CRIME CROSS-CORRELATION
# =========================================================

print(
    "\n========== CRIME CROSS-CORRELATION =========="
)


numeric_data = df.select_dtypes(
    include=[np.number]
)


correlation_matrix = (
    numeric_data.corr()
)


print(
    correlation_matrix
)


# =========================================================
# GRAPH 3: CORRELATION MATRIX
# =========================================================

plt.figure(
    figsize=(12, 8)
)


plt.imshow(
    correlation_matrix,
    aspect="auto"
)


plt.title(
    "Crime Data Cross-Correlation Matrix"
)


plt.colorbar(
    label="Correlation"
)


plt.xticks(
    range(
        len(
            correlation_matrix.columns
        )
    ),
    correlation_matrix.columns,
    rotation=90
)


plt.yticks(
    range(
        len(
            correlation_matrix.columns
        )
    ),
    correlation_matrix.columns
)


plt.tight_layout()


plt.savefig(
    os.path.join(
        CHART_DIR,
        "correlation_matrix.png"
    ),
    bbox_inches="tight"
)


plt.close()


# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n========================================")

print(
    "USE CASE 3 COMPLETED SUCCESSFULLY"
)

print("========================================")


print("\n1. CRIME INTENSITY BY TIME")

print(
    "Peak Crime Hour:",
    peak_hour
)

print(
    "Peak Crime Count:",
    peak_crimes
)


print("\n2. COMMUNITY AREA ANALYSIS")

print(
    "Total Community Areas:",
    len(unique_communities)
)

print(
    "Community With Highest Crime:",
    community_stats.iloc[0][
        "community_code"
    ]
)

print(
    "Highest Crime Count:",
    community_stats.iloc[0][
        "crime_count"
    ]
)


print("\n3. CRIME CROSS-CORRELATION")

print(
    "Numerical Columns Analysed:",
    len(numeric_data.columns)
)

print(
    "Correlation Matrix Generated Successfully"
)


print("\n========================================")

print(
    "\nAll graphs saved successfully."
)

print(
    "Graph folder:",
    CHART_DIR
)