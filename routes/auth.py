import bcrypt
from flask import Blueprint, jsonify, redirect, render_template, request, session

from db import get_db
from utils.auth import EMAIL_REGEX, not_logged_in

auth_bp = Blueprint("auth", __name__)


# ── PAGES ─────────────────────────────────────────────────────
@auth_bp.route("/")
def home():
    return render_template("index.html")


@auth_bp.route("/dashboard")
def dashboard():
    if not_logged_in():
        return redirect("/")
    return render_template("dashboard.html", user_name=session["user_name"])


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ── LOGIN API ─────────────────────────────────────────────────
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # Validate required fields
    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    # Validate email format
    if not EMAIL_REGEX.match(email):
        return jsonify({
            "success": False,
            "message": "Invalid email address."
        }), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch only required columns
    cursor.execute(
        """
        SELECT user_id, name, password
        FROM users
        WHERE email = %s
        """,
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user and bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"].encode("utf-8")
    ):
        session["user_id"] = user["user_id"]
        session["user_name"] = user["name"]

        return jsonify({
            "success": True
        }), 200

    return jsonify({
        "success": False,
        "message": "Invalid credentials."
    }), 401
