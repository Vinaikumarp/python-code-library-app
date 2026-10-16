from flask import Flask, jsonify
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

@app.route("/books", methods=["GET"])
def get_books():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
