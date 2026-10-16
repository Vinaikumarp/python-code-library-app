from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

AUTH_URL = "http://auth_service:5001"
BOOK_URL = "http://book_service:5002"
BORROW_URL = "http://borrow_service:5003"

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("books"))
    return redirect(url_for("signin"))

# ---------- AUTH ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"]
        }
        res = requests.post(f"{AUTH_URL}/signup", json=data)
        if res.status_code == 201:
            flash("Signup successful!", "success")
            return redirect(url_for("signin"))
        else:
            flash("Signup failed", "danger")
    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        data = {"email": request.form["email"], "password": request.form["password"]}
        res = requests.post(f"{AUTH_URL}/signin", json=data)
        if res.status_code == 200:
            user = res.json()
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            return redirect(url_for("books"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("signin"))

# ---------- BOOKS ----------
@app.route("/books")
def books():
    if "user_id" not in session:
        return redirect(url_for("signin"))
    res = requests.get(f"{BOOK_URL}/books")
    return render_template("books.html", books=res.json())

# ---------- BORROW ----------
@app.route("/borrow/<int:book_id>")
def borrow(book_id):
    if "user_id" not in session:
        return redirect(url_for("signin"))
    data = {"user_id": session["user_id"], "book_id": book_id}
    res = requests.post(f"{BORROW_URL}/borrow", json=data)
    if res.status_code == 201:
        flash("Book borrowed!", "success")
    return redirect(url_for("books"))

@app.route("/mybooks")
def mybooks():
    if "user_id" not in session:
        return redirect(url_for("signin"))
    res = requests.get(f"{BORROW_URL}/mybooks/{session['user_id']}")
    return render_template("borrow.html", books=res.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
