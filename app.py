"""Coffee Rating application: Flask backend + SQLite vote storage."""
import os
import sqlite3

from flask import Flask, g, jsonify, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "coffee.db")

app = Flask(__name__)

SEED = [
    ("Espresso", "Italy", "Short, intense and syrupy with a thick crema."),
    ("Flat White", "Australia", "Velvety microfoam over a double ristretto."),
    ("Cappuccino", "Italy", "Equal parts espresso, steamed milk and foam."),
    ("Cold Brew", "USA", "Steeped for 18 hours: smooth, low acidity, chocolatey."),
    ("Filter Coffee", "India", "South Indian decoction with frothy hot milk."),
    ("Americano", "USA", "Espresso stretched with hot water for a clean cup."),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS coffees (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL UNIQUE,
                   origin TEXT NOT NULL,
                   description TEXT NOT NULL,
                   votes INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0)
               )"""
        )
        if db.execute("SELECT COUNT(*) FROM coffees").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO coffees (name, origin, description) VALUES (?, ?, ?)", SEED
            )


def to_dict(row):
    return {k: row[k] for k in ("id", "name", "origin", "description", "votes")}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/coffees")
def list_coffees():
    rows = get_db().execute(
        "SELECT * FROM coffees ORDER BY votes DESC, name ASC"
    ).fetchall()
    return jsonify([to_dict(r) for r in rows])


@app.post("/api/coffees/<int:coffee_id>/vote")
def vote(coffee_id):
    db = get_db()
    # Increment inside SQL so simultaneous clicks never overwrite each other.
    cur = db.execute("UPDATE coffees SET votes = votes + 1 WHERE id = ?", (coffee_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Coffee not found."}), 404
    row = db.execute("SELECT * FROM coffees WHERE id = ?", (coffee_id,)).fetchone()
    return jsonify(to_dict(row))


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
