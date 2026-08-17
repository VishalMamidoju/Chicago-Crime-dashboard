from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

# Flask setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

# Database
DATABASE = os.path.join(BASE_DIR, "chicago_crime.db")

# Chart locations
USECASE2_CHARTS = [
    "charts/usecase2/crime_trend.png",
    "charts/usecase2/crime_distribution.png",
    "charts/usecase2/top_10_crimes.png",
    "charts/usecase2/arrest_percentage.png",
    "charts/usecase2/crime_heatmap.png",
    "charts/usecase2/top_community_areas.png"
]

USECASE3_CHARTS = [
    "charts/usecase3/crime_by_hour.png",
    "charts/usecase3/community_crimes.png",
    "charts/usecase3/correlation_matrix.png"
]

USECASE4_CHARTS = [
    "charts/usecase4/crime_yearly.png",
    "charts/usecase4/arrest_yearly.png",
    "charts/usecase4/top_categories.png"
]

# Database connection
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Dashboard
@app.route("/")
def dashboard():
    connection = get_db_connection()

    total_crimes = connection.execute(
        "SELECT COUNT(*) FROM chicago_crimes"
    ).fetchone()[0]

    total_arrests = connection.execute(
        "SELECT COUNT(*) FROM chicago_crimes WHERE arrest = 1"
    ).fetchone()[0]

    total_categories = connection.execute(
        "SELECT COUNT(DISTINCT primary_type) FROM chicago_crimes"
    ).fetchone()[0]

    top_crime = connection.execute("""
        SELECT primary_type, COUNT(*) AS crime_count
        FROM chicago_crimes
        GROUP BY primary_type
        ORDER BY crime_count DESC
        LIMIT 1
    """).fetchone()

    connection.close()

    return render_template(
        "dashboard.html",
        total_crimes=total_crimes,
        total_arrests=total_arrests,
        total_categories=total_categories,
        top_crime=top_crime
    )


# CRUD - Read
@app.route("/crimes")
def crimes():
    search = request.args.get("search", "")
    connection = get_db_connection()

    if search:
        crimes_data = connection.execute("""
            SELECT * FROM chicago_crimes
            WHERE primary_type LIKE ?
               OR CAST(id AS TEXT) LIKE ?
               OR CAST(crime_year AS TEXT) LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()
    else:
        crimes_data = connection.execute("""
            SELECT * FROM chicago_crimes
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()

    connection.close()

    return render_template(
        "crimes.html",
        crimes=crimes_data,
        search=search
    )


# CRUD - Create
@app.route("/crimes/add", methods=["GET", "POST"])
def add_crime():
    if request.method == "POST":
        crime_id = request.form["id"]
        primary_type = request.form["primary_type"]
        arrest = 1 if request.form.get("arrest") else 0
        crime_year = request.form["crime_year"]
        crime_month = request.form["crime_month"]
        day_of_week = request.form["day_of_week"]

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO chicago_crimes
            (id, primary_type, arrest, crime_year, crime_month, day_of_week)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            crime_id,
            primary_type,
            arrest,
            crime_year,
            crime_month,
            day_of_week
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("crimes"))

    return render_template("add_crime.html")


# CRUD - Update
@app.route("/crimes/edit/<int:crime_id>", methods=["GET", "POST"])
def edit_crime(crime_id):
    connection = get_db_connection()

    crime = connection.execute(
        "SELECT * FROM chicago_crimes WHERE id = ?",
        (crime_id,)
    ).fetchone()

    if crime is None:
        connection.close()
        return "Crime record not found", 404

    if request.method == "POST":
        primary_type = request.form["primary_type"]
        arrest = 1 if request.form.get("arrest") else 0
        crime_year = request.form["crime_year"]
        crime_month = request.form["crime_month"]
        day_of_week = request.form["day_of_week"]

        connection.execute("""
            UPDATE chicago_crimes
            SET primary_type = ?,
                arrest = ?,
                crime_year = ?,
                crime_month = ?,
                day_of_week = ?
            WHERE id = ?
        """, (
            primary_type,
            arrest,
            crime_year,
            crime_month,
            day_of_week,
            crime_id
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("crimes"))

    connection.close()
    return render_template("edit_crime.html", crime=crime)


# CRUD - Delete
@app.route("/crimes/delete/<int:crime_id>", methods=["POST"])
def delete_crime(crime_id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM chicago_crimes WHERE id = ?",
        (crime_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("crimes"))


# API - Get all crimes
@app.route("/api/crimes", methods=["GET"])
def api_get_crimes():
    connection = get_db_connection()

    crimes_data = connection.execute("""
        SELECT * FROM chicago_crimes
        LIMIT 100
    """).fetchall()

    connection.close()

    return jsonify([
        dict(crime)
        for crime in crimes_data
    ])


# API - Get one crime
@app.route("/api/crimes/<int:crime_id>", methods=["GET"])
def api_get_crime(crime_id):
    connection = get_db_connection()

    crime = connection.execute(
        "SELECT * FROM chicago_crimes WHERE id = ?",
        (crime_id,)
    ).fetchone()

    connection.close()

    if crime is None:
        return jsonify({
            "error": "Crime record not found"
        }), 404

    return jsonify(dict(crime))


# API - Create
@app.route("/api/crimes", methods=["POST"])
def api_create_crime():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No JSON data provided"
        }), 400

    connection = get_db_connection()

    try:
        connection.execute("""
            INSERT INTO chicago_crimes
            (id, primary_type, arrest, crime_year, crime_month, day_of_week)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data["primary_type"],
            data.get("arrest", 0),
            data.get("crime_year"),
            data.get("crime_month"),
            data.get("day_of_week")
        ))

        connection.commit()

    except KeyError as error:
        connection.close()

        return jsonify({
            "error": f"Missing required field: {error}"
        }), 400

    connection.close()

    return jsonify({
        "message": "Crime record created successfully"
    }), 201


# API - Update
@app.route("/api/crimes/<int:crime_id>", methods=["PUT"])
def api_update_crime(crime_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No JSON data provided"
        }), 400

    connection = get_db_connection()

    existing_crime = connection.execute(
        "SELECT id FROM chicago_crimes WHERE id = ?",
        (crime_id,)
    ).fetchone()

    if existing_crime is None:
        connection.close()

        return jsonify({
            "error": "Crime record not found"
        }), 404

    connection.execute("""
        UPDATE chicago_crimes
        SET primary_type = ?,
            arrest = ?,
            crime_year = ?,
            crime_month = ?,
            day_of_week = ?
        WHERE id = ?
    """, (
        data.get("primary_type"),
        data.get("arrest", 0),
        data.get("crime_year"),
        data.get("crime_month"),
        data.get("day_of_week"),
        crime_id
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Crime record updated successfully"
    })


# API - Delete
@app.route("/api/crimes/<int:crime_id>", methods=["DELETE"])
def api_delete_crime(crime_id):
    connection = get_db_connection()

    existing_crime = connection.execute(
        "SELECT id FROM chicago_crimes WHERE id = ?",
        (crime_id,)
    ).fetchone()

    if existing_crime is None:
        connection.close()

        return jsonify({
            "error": "Crime record not found"
        }), 404

    connection.execute(
        "DELETE FROM chicago_crimes WHERE id = ?",
        (crime_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Crime record deleted successfully"
    })


# Use Case 1
@app.route("/usecase1")
def usecase1():
    connection = get_db_connection()

    total_records = connection.execute(
        "SELECT COUNT(*) FROM chicago_crimes"
    ).fetchone()[0]

    columns = connection.execute(
        "PRAGMA table_info(chicago_crimes)"
    ).fetchall()

    sample_data = connection.execute("""
        SELECT * FROM chicago_crimes
        LIMIT 10
    """).fetchall()

    connection.close()

    return render_template(
        "usecase1.html",
        total_records=total_records,
        columns=columns,
        sample_data=sample_data
    )


# Use Case 2
@app.route("/usecase2")
def usecase2():
    charts = [
        {
            "title": "Crime Trend Over Years",
            "file": "charts/usecase2/crime_trend.png"
        },
        {
            "title": "Crime Distribution by Category",
            "file": "charts/usecase2/crime_distribution.png"
        },
        {
            "title": "Top 10 Crime Types",
            "file": "charts/usecase2/top_10_crimes.png"
        },
        {
            "title": "Arrest Percentage",
            "file": "charts/usecase2/arrest_percentage.png"
        },
        {
            "title": "Crime Heatmap",
            "file": "charts/usecase2/crime_heatmap.png"
        },
        {
            "title": "Top Community Areas",
            "file": "charts/usecase2/top_community_areas.png"
        }
    ]

    return render_template("usecase2.html", charts=charts)


# Use Case 3
@app.route("/usecase3")
def usecase3():
    return render_template(
        "usecase3.html",
        charts=USECASE3_CHARTS
    )


# Use Case 4
@app.route("/usecase4")
def usecase4():
    return render_template(
        "usecase4.html",
        charts=USECASE4_CHARTS
    )


# Run Flask
if __name__ == "__main__":
    print("Flask application starting...")
    print("Database:", DATABASE)

    app.run(debug=True)