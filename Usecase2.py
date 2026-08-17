import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==================== PATH SETUP ====================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(CURRENT_DIR, "chicago_crime.db")
CHART_DIR = os.path.join(CURRENT_DIR, "static", "charts", "usecase2")

os.makedirs(CHART_DIR, exist_ok=True)

print("\nDatabase path:", DATABASE_FILE)
print("Chart folder:", CHART_DIR)

# ==================== CHECK DATABASE ====================

if not os.path.exists(DATABASE_FILE):
    print("\nERROR: Database file not found!")
    print("Expected location:", DATABASE_FILE)
    print("Please run Usecase1.py first.")
    raise SystemExit

# ==================== CONNECT TO DATABASE ====================

connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

tables = cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("\nTables found:", tables)

table_names = [table[0] for table in tables]

if "chicago_crimes" not in table_names:
    print("\nERROR: Table 'chicago_crimes' does not exist!")
    print("Available tables:", table_names)
    print("Please check Usecase1.py.")
    connection.close()
    raise SystemExit

# ==================== LOAD DATA ====================

df = pd.read_sql_query("SELECT * FROM chicago_crimes", connection)
connection.close()

print("\nData loaded successfully.")
print("Total Records:", len(df))
print("Available Columns:", df.columns.tolist())

# ==================== COLUMN COMPATIBILITY ====================

if "crime_year" not in df.columns:
    if "Year" in df.columns:
        df["crime_year"] = df["Year"]
    elif "year" in df.columns:
        df["crime_year"] = df["year"]

if "crime_month" not in df.columns:
    if "Month" in df.columns:
        df["crime_month"] = df["Month"]
    elif "month" in df.columns:
        df["crime_month"] = df["month"]

if "day_of_week" not in df.columns:
    if "DayOfWeek" in df.columns:
        df["day_of_week"] = df["DayOfWeek"]
    elif "Day_Of_Week" in df.columns:
        df["day_of_week"] = df["Day_Of_Week"]

# ==================== 1. CRIME TREND ====================

yearly_crimes = df.groupby("crime_year").size()

print("\n========== CRIME TREND BY YEAR ==========")
print(yearly_crimes)

plt.figure(figsize=(10, 5))
plt.plot(yearly_crimes.index, yearly_crimes.values, marker="o")
plt.title("Crime Trend Over Years")
plt.xlabel("Year")
plt.ylabel("Number of Crimes")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "crime_trend.png"), bbox_inches="tight")
plt.close()

# ==================== 2. CRIME DISTRIBUTION ====================

crime_category = df["primary_type"].value_counts()

print("\n========== CRIME DISTRIBUTION ==========")
print(crime_category)

plt.figure(figsize=(12, 7))
crime_category.plot(kind="bar")
plt.title("Crime Distribution by Category")
plt.xlabel("Crime Type")
plt.ylabel("Number of Crimes")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "crime_distribution.png"), bbox_inches="tight")
plt.close()

# ==================== 3. TOP 10 CRIMES ====================

top_10_crimes = df["primary_type"].value_counts().head(10)

print("\n========== TOP 10 CRIME TYPES ==========")
print(top_10_crimes)

plt.figure(figsize=(10, 6))
top_10_crimes.sort_values().plot(kind="barh")
plt.title("Top 10 Crime Types")
plt.xlabel("Number of Crimes")
plt.ylabel("Crime Type")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "top_10_crimes.png"), bbox_inches="tight")
plt.close()

# ==================== 4. ARREST PERCENTAGE ====================

top_10_names = top_10_crimes.index
top_10_data = df[df["primary_type"].isin(top_10_names)]

arrest_percentage = (
    top_10_data.groupby("primary_type")["arrest"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("\n========== ARREST PERCENTAGE ==========")
print(arrest_percentage)

plt.figure(figsize=(10, 6))
arrest_percentage.plot(kind="bar")
plt.title("Arrest Percentage for Top 10 Crime Types")
plt.xlabel("Crime Type")
plt.ylabel("Arrest Percentage (%)")
plt.xticks(rotation=60)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "arrest_percentage.png"), bbox_inches="tight")
plt.close()

# ==================== 5. CRIME HEATMAP ====================

day_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

df["day_of_week"] = pd.Categorical(
    df["day_of_week"],
    categories=day_order,
    ordered=True
)

heatmap_data = pd.crosstab(df["day_of_week"], df["crime_month"])

print("\n========== CRIME HEATMAP DATA ==========")
print(heatmap_data)

plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlOrRd")
plt.title("Crime Frequency by Month and Day of Week")
plt.xlabel("Month")
plt.ylabel("Day of Week")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "crime_heatmap.png"), bbox_inches="tight")
plt.close()

# ==================== 6. TOP COMMUNITY AREAS ====================

community_crimes = df["community_code"].value_counts().head(10)

print("\n========== TOP 10 COMMUNITY AREAS ==========")
print(community_crimes)

plt.figure(figsize=(10, 6))
community_crimes.sort_values().plot(kind="barh")
plt.title("Top 10 Community Areas by Crime Frequency")
plt.xlabel("Number of Crimes")
plt.ylabel("Community Code")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "top_community_areas.png"), bbox_inches="tight")
plt.close()

# ==================== 7. MONTHLY CRIME ANALYSIS ====================

monthly_crimes = df["crime_month"].value_counts().sort_index()
highest_crime_month = monthly_crimes.idxmax()
highest_crime_count = monthly_crimes.max()

print("\n========== MONTHLY CRIME FREQUENCY ==========")
print(monthly_crimes)

print("\n========================================")
print(f"MONTH WITH HIGHEST CRIME FREQUENCY: {highest_crime_month}")
print(f"NUMBER OF CRIMES: {highest_crime_count}")
print("========================================")

# ==================== FINAL MESSAGE ====================

print("\nUSE CASE 2 COMPLETED SUCCESSFULLY")
print("All graphs have been saved successfully.")
print("Graph folder:", CHART_DIR)