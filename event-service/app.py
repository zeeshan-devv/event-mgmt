import os, time
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        dbname=os.getenv("DB_NAME", "eventdb"),
        user=os.getenv("DB_USER", "eventuser"),
        password=os.getenv("DB_PASS", "eventpass"),
    )

def init_db():
    for _ in range(40):
        try:
            c = get_conn()
            cur = c.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY, name TEXT, date TEXT,
                location TEXT, capacity INT)""")
            c.commit()
            cur.close()
            c.close()
            return
        except Exception:
            time.sleep(3)

init_db()

@app.route("/health")
def health():
    return "ok"

@app.route("/api/events", methods=["GET"])
def list_events():
    c = get_conn()
    cur = c.cursor()
    cur.execute("SELECT id, name, date, location, capacity FROM events ORDER BY id")
    rows = [{"id": r[0], "name": r[1], "date": r[2], "location": r[3], "capacity": r[4]} for r in cur.fetchall()]
    cur.close()
    c.close()
    return jsonify(rows)

@app.route("/api/events", methods=["POST"])
def add_event():
    d = request.json
    c = get_conn()
    cur = c.cursor()
    cur.execute("INSERT INTO events (name, date, location, capacity) VALUES (%s,%s,%s,%s)",
                (d.get("name"), d.get("date"), d.get("location"), int(d.get("capacity") or 0)))
    c.commit()
    cur.close()
    c.close()
    return jsonify({"status": "created"}), 201
