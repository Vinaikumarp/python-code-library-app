from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

import os

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "digital_library")
    )

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                   (data["name"], data["email"], data["password"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User created"}), 201

@app.route("/signin", methods=["POST"])
def signin():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", 
                   (data["email"], data["password"]))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify({"message": "Login success", "user_id": user["id"], "name": user["name"]})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

