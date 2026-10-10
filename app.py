
import os
from functools import wraps

import mysql.connector
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"]
    )


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return redirect(url_for("dashboard") if "user_id" in session
                    else url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash("Enter valid details and a password of at least 8 characters.")
            return redirect(url_for("register"))

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) "
                "VALUES (%s, %s, %s)",
                (name, email, generate_password_hash(password))
            )
            db.commit()
        except mysql.connector.IntegrityError:
            flash("Email already registered.")
            return redirect(url_for("register"))
        finally:
            cursor.close()
            db.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT id, name, password_hash FROM users "
                "WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()

            if user and check_password_hash(
                user["password_hash"], password
            ):
                session.clear()
                session["user_id"] = user["id"]
                session["name"] = user["name"]

                cursor.execute(
                    "INSERT INTO login_history (user_id) VALUES (%s)",
                    (user["id"],)
                )
                db.commit()
                return redirect(url_for("dashboard"))
        finally:
            cursor.close()
            db.close()

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, name, email, created_at "
            "FROM users WHERE id = %s",
            (session["user_id"],)
        )
        user = cursor.fetchone()

        cursor.execute(
            "SELECT login_time FROM login_history "
            "WHERE user_id = %s "
            "ORDER BY login_time DESC LIMIT 10",
            (session["user_id"],)
        )
        history = cursor.fetchall()
    finally:
        cursor.close()
        db.close()

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html", user=user, history=history
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
