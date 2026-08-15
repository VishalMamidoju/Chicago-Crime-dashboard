import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt


# =========================================================
# USE CASE 3
# STATISTICAL INSIGHTS AND PATTERN DETECTION
# =========================================================


# ---------------------------------------------------------
# 1. CONNECT TO SQLITE DATABASE
# ---------------------------------------------------------

DATABASE_FILE = "chicago_crime.db"

connection = sqlite3.connect(DATABASE_FILE)

df = pd.read_sql_query(
    "SELECT * FROM chicago_crimes",
    connection
)

connection.close()

print("\nData successfully loaded from SQLite database.")
print("Total Records:", len(df))


# ---------------------------------------------------------
# 2. CONVERT DATE COLUMN TO DATETIME
# ---------------------------------------------------------

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)


# =========================================================
# POINT 1: CRIME INTENSITY BY TIME
# =========================================================

# Extract hour from date
df["crime_hour"] = df["date"].dt.hour


# Group crimes by hour
hourly_crimes = (
    df.groupby("crime_hour")
    .size()
)


print("\n========== CRIME FREQUENCY BY HOUR ==========")
print(hourly_crimes)


# Find peak crime hour
peak_hour = hourly_crimes.idxmax()
peak_crimes = hourly_crimes.max()


print("\n========== PEAK CRIME TIME ==========")
print("Peak Crime Hour:", peak_hour)
print("Number of Crimes:", peak_crimes)


# Line plot
plt.figure(figsize=(10, 5))

plt.plot(
    hourly_crimes.index,
    hourly_crimes.values,
    marker="o"
)

plt.title("Crime Intensity by Hour")
plt.xlabel("Hour of the Day")
plt.ylabel("Number of Crimes")

plt.xticks(range(0, 24))

plt.grid(True)

plt.tight_layout()

plt.show()


# =========================================================
# POINT 2: COMMUNITY AREA ANALYSIS USING NUMPY
# =========================================================

# Remove missing community codes
community_data = df["community_code"].dropna()


# Convert Pandas data to NumPy array
community_array = community_data.to_numpy()


# Find unique community areas
unique_communities = np.unique(
    community_array
)


# Count crimes in each community area
community_counts = np.array([
    np.sum(community_array == community)
    for community in unique_communities
])


# Create DataFrame
community_stats = pd.DataFrame({
    "community_code": unique_communities,
    "crime_count": community_counts
})


# Sort by crime count
community_stats = community_stats.sort_values(
    by="crime_count",
    ascending=False
)


print("\n========== COMMUNITY AREA CRIME STATISTICS ==========")
print(community_stats.head(10))


# NumPy statistical analysis
print("\n========== NUMPY STATISTICAL INSIGHTS ==========")

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


# Top 10 community areas graph
top_10_communities = community_stats.head(10)

plt.figure(figsize=(10, 6))

plt.bar(
    top_10_communities["community_code"].astype(str),
    top_10_communities["crime_count"]
)

plt.title("Top 10 Community Areas by Crime Count")
plt.xlabel("Community Code")
plt.ylabel("Number of Crimes")

plt.tight_layout()

plt.show()


# =========================================================
# POINT 3: CRIME CROSS-CORRELATION
# =========================================================

print("\n========== CRIME CROSS-CORRELATION ==========")


# Select only numerical columns
numeric_data = df.select_dtypes(
    include=[np.number]
)


# Calculate correlation matrix
correlation_matrix = numeric_data.corr()


# Display correlation matrix
print(correlation_matrix)


# Visualize correlation matrix
plt.figure(figsize=(12, 8))

plt.imshow(
    correlation_matrix,
    aspect="auto"
)

plt.title("Crime Data Cross-Correlation Matrix")

plt.colorbar(
    label="Correlation"
)

plt.xticks(
    range(len(correlation_matrix.columns)),
    correlation_matrix.columns,
    rotation=90
)

plt.yticks(
    range(len(correlation_matrix.columns)),
    correlation_matrix.columns
)

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# FINAL OUTPUT
# ---------------------------------------------------------

print("\n========================================")
print("USE CASE 3 COMPLETED SUCCESSFULLY")
print("========================================")

print("\n1. CRIME INTENSITY BY TIME")
print("Peak Crime Hour:", peak_hour)
print("Peak Crime Count:", peak_crimes)

print("\n2. COMMUNITY AREA ANALYSIS")
print("Total Community Areas:", len(unique_communities))
print(
    "Community With Highest Crime:",
    community_stats.iloc[0]["community_code"]
)
print(
    "Highest Crime Count:",
    community_stats.iloc[0]["crime_count"]
)

print("\n3. CRIME CROSS-CORRELATION")
print("Numerical Columns Analysed:", len(numeric_data.columns))
print("Correlation Matrix Generated Successfully")

print("\n========================================")