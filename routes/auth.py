import bcrypt
from flask import Blueprint, jsonify, redirect, render_template, request, session

from db import get_db
from utils.auth import EMAIL_REGEX, not_logged_in,NAME_REGEX
from logger.logger import logger

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
    
    
# ── REGISTER API ──────────────────────────────────────────────
@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}

    name = " ".join((data.get("name") or "").strip().split())
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    confirm_password = (data.get("confirm_password") or "").strip()

    # Validate required fields
    if not name or not email or not password or not confirm_password:
        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    # Validate name
    if len(name) > 100:
        return jsonify({
            "success": False,
            "message": "Name cannot exceed 100 characters."
        }), 400

    if not NAME_REGEX.match(name):
        return jsonify({
            "success": False,
            "message": "Name can only contain alphabets and single spaces."
        }), 400

    # Validate email
    if not EMAIL_REGEX.match(email):
        return jsonify({
            "success": False,
            "message": "Invalid email address."
        }), 400

    # Validate password
    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters long."
        }), 400

    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match."
        }), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # Check if email already exists
        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Email is already registered."
            }), 409

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Create account
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        db.commit()

        new_user_id = cursor.lastrowid

        # Auto-login
        session["user_id"] = new_user_id
        session["user_name"] = name

        return jsonify({
            "success": True
        }), 201

    except Exception as e:
        db.rollback()
        logger.exception(e)

        return jsonify({
            "success": False,
            "message": "Unable to create account."
        }), 500

    finally:
        cursor.close()
        db.close()