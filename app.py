
import bcrypt
import sys
from datetime import datetime

import mysql.connector
from flask import Flask, jsonify, redirect, render_template, request, session

from config.config import Config
from exception.exception import CalSyncException
from logger.logger import logger

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

logger.info("CalSync application started.")


# ── DB CONNECTION ─────────────────────────────────────────────
def get_db():
    try:
        return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )

    except Exception as e:
        logger.error(e)
        raise CalSyncException(e, sys)


# ── LOGIN CHECK ───────────────────────────────────────────────
def not_logged_in():
    return "user_id" not in session

# ── ROUTES ────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if not_logged_in():
        return redirect("/")
    return render_template("dashboard.html", user_name=session["user_name"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ── LOGIN API ─────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get user by email only
    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
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

        return jsonify({"success": True})

    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    })

# ── GET EVENTS ────────────────────────────────────────────────
# Returns events the user created PLUS events they accepted an invitation to
@app.route("/api/events")
def get_events():
    if not_logged_in():
        return jsonify({"success": False})

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT DISTINCT e.* FROM events e
        LEFT JOIN event_participants ep ON e.event_id = ep.event_id
        WHERE e.created_by = %s
           OR (ep.user_id = %s AND ep.status_id = 1)
        ORDER BY e.start_time
    """, (session["user_id"], session["user_id"]))

    events = cursor.fetchall()

    for ev in events:
        for key in ("start_time", "end_time", "created_at"):
            if ev.get(key) and hasattr(ev[key], "isoformat"):
                ev[key] = ev[key].isoformat()

    cursor.close()
    db.close()
    return jsonify({"success": True, "events": events})

# ── CREATE EVENT ──────────────────────────────────────────────
@app.route("/api/events", methods=["POST"])
def create_event():
    if not_logged_in():
        return jsonify({"success": False})

    data  = request.get_json() or {}
    title = data.get("title")
    start = data.get("start")
    end   = data.get("end")

    if not title or not start or not end:
        return jsonify({"success": False, "message": "Missing fields"})

    try:
        start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M")
        end_dt   = datetime.strptime(end,   "%Y-%m-%dT%H:%M")
    except Exception:
        return jsonify({"success": False, "message": "Invalid datetime format"})

    if start_dt >= end_dt:
        return jsonify({"success": False, "message": "End time must be after start time."})

    start_sql = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_sql   = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.callproc("create_event", [title, start_sql, end_sql, session["user_id"]])
        for _ in cursor.stored_results():
            pass
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"success": True, "message": "Event created successfully!"})
    except mysql.connector.Error as err:
        db.rollback()
        cursor.close()
        db.close()
        return jsonify({"success": False, "message": err.msg})

# ── DELETE EVENT ──────────────────────────────────────────────
@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    if not_logged_in():
        return jsonify({"success": False})

    user_id = session["user_id"]
    db = get_db()
    cursor = db.cursor()

    try:
        # Only the creator can delete
        cursor.execute(
            "SELECT event_id FROM events WHERE event_id=%s AND created_by=%s",
            (event_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({"success": False, "message": "Event not found."})

        # Delete all child rows leaf-first before deleting the parent event
        cursor.execute(
            "DELETE FROM conflict_logs WHERE event_id=%s OR conflicting_event_id=%s",
            (event_id, event_id)
        )
        cursor.execute("DELETE FROM event_tag_map WHERE event_id=%s", (event_id,))
        cursor.execute("DELETE FROM event_recurrence_map WHERE event_id=%s", (event_id,))
        cursor.execute("DELETE FROM event_participants WHERE event_id=%s", (event_id,))
        cursor.execute(
            """DELETE ir FROM invitation_responses ir
               JOIN event_invitations ei ON ir.invitation_id = ei.invitation_id
               WHERE ei.event_id = %s""",
            (event_id,)
        )
        cursor.execute("DELETE FROM event_invitations WHERE event_id=%s", (event_id,))
        cursor.execute("DELETE FROM reminders WHERE event_id=%s", (event_id,))
        cursor.execute(
            """DELETE nl FROM notification_logs nl
               JOIN notifications n ON nl.notification_id = n.notification_id
               WHERE n.event_id = %s""",
            (event_id,)
        )
        cursor.execute("DELETE FROM notifications WHERE event_id=%s", (event_id,))
        cursor.execute(
            "DELETE FROM events WHERE event_id=%s AND created_by=%s",
            (event_id, user_id)
        )

        db.commit()
        cursor.close()
        db.close()
        return jsonify({"success": True})

    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        return jsonify({"success": False, "message": str(e)})

# ── STATS ─────────────────────────────────────────────────────
@app.route("/api/stats")
def stats():
    if not_logged_in():
        return jsonify({"success": False})

    db = get_db()
    cursor = db.cursor()
    user_id = session["user_id"]

    cursor.execute("""
    SELECT COUNT(DISTINCT e.event_id) FROM events e
    LEFT JOIN event_participants ep ON e.event_id = ep.event_id
    WHERE e.created_by = %s OR (ep.user_id = %s AND ep.status_id = 1)
    """, (user_id, user_id))
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT e.event_id) FROM events e
        LEFT JOIN event_participants ep ON e.event_id = ep.event_id
        WHERE (e.created_by = %s OR (ep.user_id = %s AND ep.status_id = 1))
        AND e.start_time >= NOW()
    """, (user_id, user_id))
    upcoming = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT e.event_id) FROM events e
        LEFT JOIN event_participants ep ON e.event_id = ep.event_id
        WHERE (e.created_by = %s OR (ep.user_id = %s AND ep.status_id = 1))
        AND DATE(e.start_time) = CURDATE()
    """, (user_id, user_id))
    today = cursor.fetchone()[0]

    cursor.close()
    db.close()
    return jsonify({"success": True, "total": total, "upcoming": upcoming, "today": today})

# ── GET ALL OTHER USERS (for invite dropdown) ─────────────────
@app.route("/api/users")
def get_users():
    if not_logged_in():
        return jsonify({"success": False})

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, name, email FROM users WHERE user_id != %s ORDER BY name",
        (session["user_id"],)
    )
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify({"success": True, "users": users})

# ── SEND INVITATION ───────────────────────────────────────────
@app.route("/api/invite", methods=["POST"])
def send_invite():
    if not_logged_in():
        return jsonify({"success": False})

    data        = request.get_json() or {}
    event_id    = data.get("event_id")
    receiver_id = data.get("receiver_id")
    sender_id   = session["user_id"]

    if not event_id or not receiver_id:
        return jsonify({"success": False, "message": "Missing fields"})

    if int(receiver_id) == sender_id:
        return jsonify({"success": False, "message": "You can't invite yourself"})

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT invitation_id FROM event_invitations WHERE event_id=%s AND receiver_id=%s",
            (event_id, receiver_id)
        )
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({"success": False, "message": "Already invited this user"})

        cursor.execute(
            "INSERT INTO event_invitations (event_id, sender_id, receiver_id) VALUES (%s, %s, %s)",
            (event_id, sender_id, receiver_id)
        )
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"success": True, "message": "Invitation sent!"})
    except Exception as e:
        cursor.close()
        db.close()
        return jsonify({"success": False, "message": str(e)})

# ── GET PENDING INVITATIONS FOR LOGGED-IN USER ────────────────
@app.route("/api/invitations")
def get_invitations():
    if not_logged_in():
        return jsonify({"success": False})

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ei.invitation_id, ei.event_id, ei.sent_at,
               e.title      AS event_title,
               e.start_time, e.end_time,
               u.name       AS sender_name
        FROM event_invitations ei
        JOIN events e ON ei.event_id  = e.event_id
        JOIN users  u ON ei.sender_id = u.user_id
        WHERE ei.receiver_id = %s
          AND ei.invitation_id NOT IN (
              SELECT invitation_id FROM invitation_responses
          )
        ORDER BY ei.sent_at DESC
    """, (session["user_id"],))
    rows = cursor.fetchall()

    for r in rows:
        for k in ("sent_at", "start_time", "end_time"):
            if r.get(k) and hasattr(r[k], "isoformat"):
                r[k] = r[k].isoformat()

    cursor.close()
    db.close()
    return jsonify({"success": True, "invitations": rows})

# ── RESPOND TO INVITATION ─────────────────────────────────────
@app.route("/api/invitations/<int:inv_id>", methods=["POST"])
def respond_invitation(inv_id):
    if not_logged_in():
        return jsonify({"success": False})

    data      = request.get_json() or {}
    action    = data.get("action")           # "accept" or "decline"
    status_id = 1 if action == "accept" else 2   # 1=accepted 2=declined

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO invitation_responses (invitation_id, status_id) VALUES (%s, %s)",
            (inv_id, status_id)
        )
        db.commit()
        cursor.close()
        db.close()
        msg = "You joined the event!" if action == "accept" else "Invitation declined."
        return jsonify({"success": True, "message": msg})
    except Exception as e:
        cursor.close()
        db.close()
        return jsonify({"success": False, "message": str(e)})

# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )