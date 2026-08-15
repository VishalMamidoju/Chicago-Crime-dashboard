import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================
# USE CASE 2
# EXPLORATORY DATA ANALYSIS AND VISUALIZATION
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

print("Data successfully loaded from SQLite database.")

print("\nTotal Records:", len(df))


# ---------------------------------------------------------
# 2. CRIME TREND OVER YEARS
# ---------------------------------------------------------

yearly_crimes = df.groupby("crime_year").size()

print("\n========== CRIME TREND BY YEAR ==========")
print(yearly_crimes)

plt.figure(figsize=(10, 5))

plt.plot(
    yearly_crimes.index,
    yearly_crimes.values,
    marker="o"
)

plt.title("Crime Trend Over Years")
plt.xlabel("Year")
plt.ylabel("Number of Crimes")

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# 3. CRIME DISTRIBUTION BY CATEGORY
# ---------------------------------------------------------

crime_category = df["primary_type"].value_counts()

print("\n========== CRIME DISTRIBUTION BY CATEGORY ==========")
print(crime_category)

plt.figure(figsize=(12, 7))

crime_category.plot(
    kind="bar"
)

plt.title("Crime Distribution by Category")
plt.xlabel("Crime Type")
plt.ylabel("Number of Crimes")

plt.xticks(rotation=90)

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# 4. TOP 10 CRIME TYPES
# ---------------------------------------------------------

top_10_crimes = df["primary_type"].value_counts().head(10)

print("\n========== TOP 10 CRIME TYPES ==========")
print(top_10_crimes)

plt.figure(figsize=(10, 6))

top_10_crimes.sort_values().plot(
    kind="barh"
)

plt.title("Top 10 Crime Types")
plt.xlabel("Number of Crimes")
plt.ylabel("Crime Type")

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# 5. ARREST PERCENTAGE FOR TOP 10 CRIME TYPES
# ---------------------------------------------------------

top_10_names = top_10_crimes.index

top_10_data = df[
    df["primary_type"].isin(top_10_names)
]

# Calculate arrest percentage
arrest_percentage = (
    top_10_data
    .groupby("primary_type")["arrest"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("\n========== ARREST PERCENTAGE ==========")
print(arrest_percentage)

plt.figure(figsize=(10, 6))

arrest_percentage.plot(
    kind="bar"
)

plt.title("Arrest Percentage for Top 10 Crime Types")
plt.xlabel("Crime Type")
plt.ylabel("Arrest Percentage (%)")

plt.xticks(rotation=60)

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# 6. HEATMAP OF CRIMES BY MONTH AND DAY OF WEEK
# ---------------------------------------------------------

# Define the correct order of days
day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

# Make sure days follow correct order
df["day_of_week"] = pd.Categorical(
    df["day_of_week"],
    categories=day_order,
    ordered=True
)

heatmap_data = pd.crosstab(
    df["day_of_week"],
    df["crime_month"]
)

print("\n========== CRIME HEATMAP DATA ==========")
print(heatmap_data)

plt.figure(figsize=(12, 6))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt="d",
    cmap="YlOrRd"
)

plt.title("Crime Frequency by Month and Day of Week")
plt.xlabel("Month")
plt.ylabel("Day of Week")

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# 7. TOP COMMUNITY AREAS
# ---------------------------------------------------------

community_crimes = (
    df["community_code"]
    .value_counts()
    .head(10)
)

print("\n========== TOP 10 COMMUNITY AREAS ==========")
print(community_crimes)

plt.figure(figsize=(10, 6))

community_crimes.sort_values().plot(
    kind="barh"
)

plt.title("Top 10 Community Areas by Crime Frequency")
plt.xlabel("Number of Crimes")
plt.ylabel("Community Code")

plt.tight_layout()

plt.show()


# ---------------------------------------------------------
# 8. MONTH WITH HIGHEST CRIME FREQUENCY
# ---------------------------------------------------------

monthly_crimes = (
    df["crime_month"]
    .value_counts()
    .sort_index()
)

highest_crime_month = monthly_crimes.idxmax()

highest_crime_count = monthly_crimes.max()

print("\n========== MONTHLY CRIME FREQUENCY ==========")
print(monthly_crimes)

print("\n========================================")
print(
    f"MONTH WITH HIGHEST CRIME FREQUENCY: "
    f"{highest_crime_month}"
)
print(
    f"NUMBER OF CRIMES: "
    f"{highest_crime_count}"
)
print("========================================")


# ---------------------------------------------------------
# FINAL MESSAGE
# ---------------------------------------------------------

print("\nUSE CASE 2 COMPLETED SUCCESSFULLY")