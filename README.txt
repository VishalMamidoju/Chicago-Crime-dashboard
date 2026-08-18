CHICAGO CRIME ANALYSIS SYSTEM
================================

PROJECT OVERVIEW
----------------
This project is a Python-based Chicago Crime Analysis System that analyzes crime data using data cleaning, visualization, statistical analysis, SQLite database operations, CRUD functionality, REST APIs, and a Flask web application.

TECHNOLOGIES USED
-----------------
Python, Pandas, NumPy, SQLite3, Matplotlib, Seaborn, Flask, HTML, CSS

USE CASES
---------
USE CASE 1 - DATA LOADING AND CLEANING
- Loads the Chicago crime CSV dataset.
- Inspects dataset structure and data types.
- Handles missing values.
- Standardizes categorical data.
- Creates crime_year, crime_month, and day_of_week features.
- Stores cleaned data in SQLite.

USE CASE 2 - EXPLORATORY ANALYSIS AND VISUALIZATION
- Crime trend over years.
- Crime distribution by category.
- Top 10 crime types.
- Arrest percentage analysis.
- Crime heatmap by month and day of week.
- Top community areas.

USE CASE 3 - STATISTICAL INSIGHTS AND PATTERN DETECTION
- Crime intensity by hour.
- Peak crime hour detection.
- Community area analysis using NumPy.
- Average, maximum, minimum, and standard deviation.
- Cross-correlation analysis of numerical data.

USE CASE 4 - DATABASE OPERATIONS
- Uses SQLite3 for database operations.
- Supports viewing and managing crime records.
- Integrates database functionality with Flask.

FLASK WEB APPLICATION
---------------------
- Interactive dashboard.
- Displays crime statistics and insights.
- Shows graphs from Use Case 2, Use Case 3, and Use Case 4.
- CRUD operations: Create, Read, Update, Delete.
- REST API endpoints for crime data.

DATABASE
--------
Database Name: chicago_crime.db
Main Table: chicago_crimes

PROJECT STRUCTURE
-----------------
Capstone Assessment/
|
|-- data/
|   |-- chicago_crime_dataset.csv
|
|-- UseCases/
    |-- Usecase1.py
    |-- Usecase2.py
    |-- Usecase3.py
    |-- Usecase4.py
    |-- app.py
    |-- chicago_crime.db
    |
    |-- templates/
    |   |-- base.html
    |   |-- dashboard.html
    |   |-- crimes.html
    |   |-- add_crime.html
    |   |-- edit_crime.html
    |   |-- usecase1.html
    |   |-- usecase2.html
    |   |-- usecase3.html
    |   |-- usecase4.html
    |
    |-- static/
        |-- style.css
        |-- charts/
            |-- usecase2/
            |-- usecase3/
            |-- usecase4/

HOW TO RUN
----------
1. Install required libraries:

pip install pandas numpy matplotlib seaborn flask

2. Run Use Case 1:

py Usecase1.py

3. Run Use Case 2:

py Usecase2.py

4. Run Use Case 3:

py Usecase3.py

5. Run Use Case 4:

py Usecase4.py

6. Run the Flask application:

py app.py

Then open:

http://127.0.0.1:5000/

APPLICATION PAGES
-----------------
/              Dashboard
/crimes        View and search crime records
/crimes/add    Add a new crime record
/usecase1      Data loading and cleaning results
/usecase2      Exploratory analysis graphs
/usecase3      Statistical insights and pattern detection
/usecase4      Database analysis and results

REST API ENDPOINTS
------------------
GET    /api/crimes
GET    /api/crimes/<crime_id>
POST   /api/crimes
PUT    /api/crimes/<crime_id>
DELETE /api/crimes/<crime_id>

KEY INSIGHTS
------------
- Crime frequency changes across different years.
- Certain crime categories occur more frequently.
- Crime activity varies by hour of the day.
- Some community areas have higher crime counts.
- Arrest percentages differ between crime categories.
- Monthly and daily analysis reveals temporal patterns.
- Correlation analysis identifies relationships between numerical variables.

CONCLUSION
----------
The Chicago Crime Analysis System transforms raw crime data into meaningful insights through data cleaning, exploratory analysis, visualization, statistical analysis, SQLite database operations, CRUD functionality, REST APIs, and a Flask web application.

The project demonstrates the practical use of Python, Pandas, NumPy, SQLite3, Matplotlib, Seaborn, and Flask to build a complete data analysis and crime management system.
