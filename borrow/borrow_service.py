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

@app.route("/borrow", methods=["POST"])
def borrow_book():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO borrow_records (user_id, book_id) VALUES (%s, %s)", 
                   (data["user_id"], data["book_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Book borrowed"}), 201

@app.route("/mybooks/<int:user_id>", methods=["GET"])
def my_books(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.title, b.author, br.borrow_date 
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.user_id=%s
    """, (user_id,))
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
