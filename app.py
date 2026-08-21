import sqlite3

from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash

from database.db import get_db, init_db, seed_db, create_user, get_user_by_email

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password or not confirm_password:
        flash("All fields are required.", "error")
        return render_template("register.html")

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("register.html")

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        flash("Email already registered.", "error")
        return render_template("register.html")

    flash("Account created successfully. Please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_user_by_email(email) if email else None

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password", "error")
        return render_template("login.html")

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": session.get("user_name", "Demo User"),
        "initials": "".join(part[0].upper() for part in session.get("user_name", "Demo User").split()[:2]),
        "email": "demo@spendly.com",
        "member_since": "August 2026",
    }

    stats = [
        {"label": "Total spent", "value": "₹264.15"},
        {"label": "Transactions", "value": "8"},
        {"label": "Top category", "value": "Food"},
    ]

    transactions = [
        {"date": "2026-08-19", "description": "Restaurant dinner", "category": "Food", "amount": 27.90},
        {"date": "2026-08-17", "description": "Miscellaneous", "category": "Other", "amount": 8.20},
        {"date": "2026-08-14", "description": "New shoes", "category": "Shopping", "amount": 62.30},
        {"date": "2026-08-11", "description": "Movie tickets", "category": "Entertainment", "amount": 15.00},
        {"date": "2026-08-08", "description": "Pharmacy", "category": "Health", "amount": 45.00},
    ]

    categories = [
        {"name": "Food", "total": 40.40, "percent": 15},
        {"name": "Transport", "total": 3.75, "percent": 1},
        {"name": "Bills", "total": 89.00, "percent": 34},
        {"name": "Health", "total": 45.00, "percent": 17},
        {"name": "Entertainment", "total": 15.00, "percent": 6},
        {"name": "Shopping", "total": 62.30, "percent": 24},
        {"name": "Other", "total": 8.20, "percent": 3},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
