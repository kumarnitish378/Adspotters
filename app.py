from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_NAME = 'contacts.db'


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    filter_type = request.args.get('type', 'all')
    start = request.args.get('start')
    end = request.args.get('end')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if filter_type == 'all':
        c.execute("SELECT * FROM contacts ORDER BY timestamp DESC")
    elif filter_type == 'latest':
        c.execute("SELECT * FROM contacts ORDER BY timestamp DESC LIMIT 100")
    elif filter_type == 'range' and start and end:
        try:
            # Validate date format
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            c.execute("SELECT * FROM contacts WHERE DATE(timestamp) BETWEEN ? AND ? ORDER BY timestamp DESC", (start, end))
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    else:
        return jsonify({"error": "Invalid filter type"}), 400

    rows = c.fetchall()
    conn.close()

    data = [{
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "message": row[3],
        "timestamp": row[4]
    } for row in rows]

    return jsonify(data)


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
              (name, email, message))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"}), 201

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
