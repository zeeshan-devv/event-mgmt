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
            cur.execute("""CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY, event_id INT, attendee TEXT,
                created TIMESTAMP DEFAULT NOW())""")
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

@app.route("/api/bookings", methods=["GET"])
def list_bookings():
    c = get_conn()
    cur = c.cursor()
    cur.execute("SELECT id, event_id, attendee FROM bookings ORDER BY id")
    rows = [{"id": r[0], "event_id": r[1], "attendee": r[2]} for r in cur.fetchall()]
    cur.close()
    c.close()
    return jsonify(rows)

@app.route("/api/bookings", methods=["POST"])
def add_booking():
    d = request.json
    c = get_conn()
    cur = c.cursor()
    cur.execute("INSERT INTO bookings (event_id, attendee) VALUES (%s,%s)",
                (int(d.get("event_id")), d.get("attendee")))
    c.commit()
    cur.close()
    c.close()
    return jsonify({"status": "booked"}), 201
