from flask import Flask, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "flowershop.db"


def get_db_connection():
    # Savienojums ar SQLite datubāzi.
    # Datubāzes fails atrodas tajā pašā mapē, kur app.py.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/flowers")
def flowers():
    conn = get_db_connection()

    flowers = conn.execute("""
        SELECT flowers.*, categories.name AS category_name
        FROM flowers
        LEFT JOIN categories ON flowers.category_id = categories.id
        ORDER BY flowers.id
    """).fetchall()

    conn.close()
    return render_template("flowers.html", flowers=flowers)


@app.route("/flowers/<int:flower_id>")
def flower_show(flower_id):
    conn = get_db_connection()

    flower = conn.execute("""
        SELECT flowers.*, categories.name AS category_name
        FROM flowers
        LEFT JOIN categories ON flowers.category_id = categories.id
        WHERE flowers.id = ?
    """, (flower_id,)).fetchone()

    occasions = conn.execute("""
        SELECT occasions.*
        FROM occasions
        JOIN flower_occasions ON occasions.id = flower_occasions.occasion_id
        WHERE flower_occasions.flower_id = ?
        ORDER BY occasions.id
    """, (flower_id,)).fetchall()

    conn.close()

    if flower is None:
        return render_template("404.html"), 404

    return render_template("flower_show.html", flower=flower, occasions=occasions)


@app.route("/occasions")
def occasions():
    conn = get_db_connection()

    occasions = conn.execute("""
        SELECT occasions.id, occasions.name, occasions.description,
               COUNT(flower_occasions.flower_id) AS flower_count
        FROM occasions
        LEFT JOIN flower_occasions ON occasions.id = flower_occasions.occasion_id
        GROUP BY occasions.id, occasions.name, occasions.description
        ORDER BY occasions.id
    """).fetchall()

    conn.close()
    return render_template("occasions.html", occasions=occasions)


@app.route("/occasions/<int:occasion_id>")
def occasion_show(occasion_id):
    conn = get_db_connection()

    occasion = conn.execute("""
        SELECT *
        FROM occasions
        WHERE id = ?
    """, (occasion_id,)).fetchone()

    if occasion is None:
        conn.close()
        return render_template("404.html"), 404

    flowers = conn.execute("""
        SELECT flowers.*, categories.name AS category_name
        FROM flowers
        JOIN flower_occasions ON flowers.id = flower_occasions.flower_id
        LEFT JOIN categories ON flowers.category_id = categories.id
        WHERE flower_occasions.occasion_id = ?
        ORDER BY flowers.id
    """, (occasion_id,)).fetchall()

    conn.close()
    return render_template("occasion_show.html", occasion=occasion, flowers=flowers)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
