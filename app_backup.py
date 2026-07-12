# import re
# import bcrypt
# import sys
# from datetime import datetime

# import mysql.connector
# from flask import Flask, jsonify, redirect, render_template, request, session

# from config.config import Config
# from exception.exception import CalSyncException
# from logger.logger import logger

# EMAIL_REGEX = re.compile(
#     r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
# )

# app = Flask(__name__)
# app.secret_key = Config.SECRET_KEY

# logger.info("CalSync application started.")


# # ── DB CONNECTION ─────────────────────────────────────────────
# def get_db():
#     try:
#         return mysql.connector.connect(
#         host=Config.MYSQL_HOST,
#         port=Config.MYSQL_PORT,
#         user=Config.MYSQL_USER,
#         password=Config.MYSQL_PASSWORD,
#         database=Config.MYSQL_DATABASE,
#     )

#     except Exception as e:
#         logger.error(e)
#         raise CalSyncException(e, sys)


# # ── LOGIN CHECK ───────────────────────────────────────────────
# def not_logged_in():
#     return "user_id" not in session

# # ── ROUTES ────────────────────────────────────────────────────
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/dashboard")
# def dashboard():
#     if not_logged_in():
#         return redirect("/")
#     return render_template("dashboard.html", user_name=session["user_name"])

# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/")

# # ── LOGIN API ─────────────────────────────────────────────────
# @app.route("/api/login", methods=["POST"])
# def api_login():
#     data = request.get_json(silent=True) or {}

#     email = (data.get("email") or "").strip().lower()
#     password = (data.get("password") or "").strip()

#     # Validate required fields
#     if not email or not password:
#         return jsonify({
#             "success": False,
#             "message": "Email and password are required."
#         }), 400

#     # Validate email format
#     if not EMAIL_REGEX.match(email):
#         return jsonify({
#             "success": False,
#             "message": "Invalid email address."
#         }), 400

#     db = get_db()
#     cursor = db.cursor(dictionary=True)

#     # Fetch only required columns
#     cursor.execute(
#         """
#         SELECT user_id, name, password
#         FROM users
#         WHERE email = %s
#         """,
#         (email,)
#     )

#     user = cursor.fetchone()

#     cursor.close()
#     db.close()

#     if user and bcrypt.checkpw(
#         password.encode("utf-8"),
#         user["password"].encode("utf-8")
#     ):
#         session["user_id"] = user["user_id"]
#         session["user_name"] = user["name"]

#         return jsonify({
#             "success": True
#         }), 200

#     return jsonify({
#         "success": False,
#         "message": "Invalid credentials."
#     }), 401

# # ── GET EVENTS ────────────────────────────────────────────────
# # Returns events the user created PLUS events they accepted an invitation to
# @app.route("/api/events")
# def get_events():
#     if not_logged_in():
#         return jsonify({"success": False})

#     db = get_db()
#     cursor = db.cursor(dictionary=True)

#     cursor.execute("""
#         SELECT DISTINCT e.* FROM events e
#         LEFT JOIN event_participants ep ON e.event_id = ep.event_id
#         WHERE e.created_by = %s
#            OR (ep.user_id = %s AND ep.status_id = 1)
#         ORDER BY e.start_time
#     """, (session["user_id"], session["user_id"]))

#     events = cursor.fetchall()

#     for ev in events:
#         for key in ("start_time", "end_time", "created_at"):
#             if ev.get(key) and hasattr(ev[key], "isoformat"):
#                 ev[key] = ev[key].isoformat()

#     cursor.close()
#     db.close()
#     return jsonify({"success": True, "events": events})

# # ── CREATE EVENT ──────────────────────────────────────────────
# @app.route("/api/events", methods=["POST"])
# def create_event():
#     if not_logged_in():
#         return jsonify({
#             "success": False,
#             "message": "Unauthorized."
#         }), 401

#     data = request.get_json(silent=True) or {}

#     title = (data.get("title") or "").strip()
#     start = (data.get("start") or "").strip()
#     end = (data.get("end") or "").strip()

#     # Required fields
#     if not title or not start or not end:
#         return jsonify({
#             "success": False,
#             "message": "Title, start time and end time are required."
#         }), 400

#     # Title length
#     if len(title) > 100:
#         return jsonify({
#             "success": False,
#             "message": "Title cannot exceed 100 characters."
#         }), 400

#     # Parse datetime
#     try:
#         start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M")
#         end_dt = datetime.strptime(end, "%Y-%m-%dT%H:%M")
#     except ValueError:
#         return jsonify({
#             "success": False,
#             "message": "Invalid date or time format."
#         }), 400

#     # Logical validation
#     if start_dt >= end_dt:
#         return jsonify({
#             "success": False,
#             "message": "End time must be after start time."
#         }), 400

#     # Prevent creating past events
#     if start_dt < datetime.now():
#         return jsonify({
#             "success": False,
#             "message": "Cannot create an event in the past."
#         }), 400

#     start_sql = start_dt.strftime("%Y-%m-%d %H:%M:%S")
#     end_sql = end_dt.strftime("%Y-%m-%d %H:%M:%S")

#     db = get_db()
#     cursor = db.cursor()

#     try:
#         cursor.callproc(
#             "create_event",
#             [
#                 title,
#                 start_sql,
#                 end_sql,
#                 session["user_id"]
#             ]
#         )

#         for _ in cursor.stored_results():
#             pass

#         db.commit()

#         return jsonify({
#             "success": True,
#             "message": "Event created successfully."
#         }), 201

#     except Exception as e:
#         db.rollback()
#         logger.exception(e)

#         return jsonify({
#             "success": False,
#             "message": "Unable to create event."
#         }), 500

#     finally:
#         cursor.close()
#         db.close()

# # ── DELETE EVENT ──────────────────────────────────────────────
# @app.route("/api/events/<int:event_id>", methods=["DELETE"])
# def delete_event(event_id):
#     if not_logged_in():
#         return jsonify({"success": False})

#     user_id = session["user_id"]
#     db = get_db()
#     cursor = db.cursor()

#     try:
#         # Only the creator can delete
#         cursor.execute(
#             "SELECT event_id FROM events WHERE event_id=%s AND created_by=%s",
#             (event_id, user_id)
#         )
#         if not cursor.fetchone():
#             cursor.close()
#             db.close()
#             return jsonify({"success": False, "message": "Event not found."})

#         # Delete all child rows leaf-first before deleting the parent event
#         cursor.execute(
#             "DELETE FROM conflict_logs WHERE event_id=%s OR conflicting_event_id=%s",
#             (event_id, event_id)
#         )
#         cursor.execute("DELETE FROM event_tag_map WHERE event_id=%s", (event_id,))
#         cursor.execute("DELETE FROM event_recurrence_map WHERE event_id=%s", (event_id,))
#         cursor.execute("DELETE FROM event_participants WHERE event_id=%s", (event_id,))
#         cursor.execute(
#             """DELETE ir FROM invitation_responses ir
#                JOIN event_invitations ei ON ir.invitation_id = ei.invitation_id
#                WHERE ei.event_id = %s""",
#             (event_id,)
#         )
#         cursor.execute("DELETE FROM event_invitations WHERE event_id=%s", (event_id,))
#         cursor.execute("DELETE FROM reminders WHERE event_id=%s", (event_id,))
#         cursor.execute(
#             """DELETE nl FROM notification_logs nl
#                JOIN notifications n ON nl.notification_id = n.notification_id
#                WHERE n.event_id = %s""",
#             (event_id,)
#         )
#         cursor.execute("DELETE FROM notifications WHERE event_id=%s", (event_id,))
#         cursor.execute(
#             "DELETE FROM events WHERE event_id=%s AND created_by=%s",
#             (event_id, user_id)
#         )

#         db.commit()
#         cursor.close()
#         db.close()
#         return jsonify({"success": True})

#     except Exception as e:
#         db.rollback()
#         cursor.close()
#         db.close()
#         return jsonify({"success": False, "message": str(e)})

# # ── STATS ─────────────────────────────────────────────────────
# @app.route("/api/stats")
# def stats():
#     if not_logged_in():
#         return jsonify({"success": False})

#     db = get_db()
#     cursor = db.cursor()
#     user_id = session["user_id"]

#     cursor.execute("""
#     SELECT COUNT(DISTINCT e.event_id) FROM events e
#     LEFT JOIN event_participants ep ON e.event_id = ep.event_id
#     WHERE e.created_by = %s OR (ep.user_id = %s AND ep.status_id = 1)
#     """, (user_id, user_id))
#     total = cursor.fetchone()[0]

#     cursor.execute("""
#         SELECT COUNT(DISTINCT e.event_id) FROM events e
#         LEFT JOIN event_participants ep ON e.event_id = ep.event_id
#         WHERE (e.created_by = %s OR (ep.user_id = %s AND ep.status_id = 1))
#         AND e.start_time >= NOW()
#     """, (user_id, user_id))
#     upcoming = cursor.fetchone()[0]

#     cursor.execute("""
#         SELECT COUNT(DISTINCT e.event_id) FROM events e
#         LEFT JOIN event_participants ep ON e.event_id = ep.event_id
#         WHERE (e.created_by = %s OR (ep.user_id = %s AND ep.status_id = 1))
#         AND DATE(e.start_time) = CURDATE()
#     """, (user_id, user_id))
#     today = cursor.fetchone()[0]

#     cursor.close()
#     db.close()
#     return jsonify({"success": True, "total": total, "upcoming": upcoming, "today": today})

# # ── GET ALL OTHER USERS (for invite dropdown) ─────────────────
# @app.route("/api/users")
# def get_users():
#     if not_logged_in():
#         return jsonify({"success": False})

#     db = get_db()
#     cursor = db.cursor(dictionary=True)
#     cursor.execute(
#         "SELECT user_id, name, email FROM users WHERE user_id != %s ORDER BY name",
#         (session["user_id"],)
#     )
#     users = cursor.fetchall()
#     cursor.close()
#     db.close()
#     return jsonify({"success": True, "users": users})

# # ── SEND INVITATION ───────────────────────────────────────────
# @app.route("/api/invite", methods=["POST"])
# def send_invite():
#     if not_logged_in():
#         return jsonify({
#             "success": False,
#             "message": "Unauthorized."
#         }), 401

#     data = request.get_json(silent=True) or {}

#     event_id = data.get("event_id")
#     receiver_id = data.get("receiver_id")
#     sender_id = session["user_id"]

#     # Required fields
#     if not event_id or not receiver_id:
#         return jsonify({
#             "success": False,
#             "message": "Event ID and receiver are required."
#         }), 400

#     # Validate IDs
#     try:
#         event_id = int(event_id)
#         receiver_id = int(receiver_id)
#     except (ValueError, TypeError):
#         return jsonify({
#             "success": False,
#             "message": "Invalid event or receiver ID."
#         }), 400

#     # Prevent self-invitation
#     if receiver_id == sender_id:
#         return jsonify({
#             "success": False,
#             "message": "You can't invite yourself."
#         }), 400

#     db = get_db()
#     cursor = db.cursor(dictionary=True)

#     try:
#         # Check event exists and fetch creator
#         cursor.execute(
#             """
#             SELECT event_id, created_by
#             FROM events
#             WHERE event_id = %s
#             """,
#             (event_id,)
#         )

#         event = cursor.fetchone()

#         if not event:
#             return jsonify({
#                 "success": False,
#                 "message": "Event not found."
#             }), 404

#         # Only creator can invite users
#         if event["created_by"] != sender_id:
#             return jsonify({
#                 "success": False,
#                 "message": "Only the event creator can send invitations."
#             }), 403

#         # Check receiver exists
#         cursor.execute(
#             """
#             SELECT user_id
#             FROM users
#             WHERE user_id = %s
#             """,
#             (receiver_id,)
#         )

#         if not cursor.fetchone():
#             return jsonify({
#                 "success": False,
#                 "message": "User not found."
#             }), 404

#         # Already invited?
#         cursor.execute(
#             """
#             SELECT invitation_id
#             FROM event_invitations
#             WHERE event_id = %s
#               AND receiver_id = %s
#             """,
#             (event_id, receiver_id)
#         )

#         if cursor.fetchone():
#             return jsonify({
#                 "success": False,
#                 "message": "User has already been invited."
#             }), 409

#         # Already participating?
#         cursor.execute(
#             """
#             SELECT 1
#             FROM event_participants
#             WHERE event_id = %s
#             AND user_id = %s
#             """,
#             (event_id, receiver_id)
#         )

#         if cursor.fetchone():
#             return jsonify({
#                 "success": False,
#                 "message": "User is already participating in this event."
#             }), 409

#         # Create invitation
#         cursor.execute(
#             """
#             INSERT INTO event_invitations
#             (event_id, sender_id, receiver_id)
#             VALUES (%s, %s, %s)
#             """,
#             (event_id, sender_id, receiver_id)
#         )

#         db.commit()

#         return jsonify({
#             "success": True,
#             "message": "Invitation sent successfully."
#         }), 201

#     except Exception as e:
#         db.rollback()
#         logger.exception(e)

#         return jsonify({
#             "success": False,
#             "message": "Unable to send invitation."
#         }), 500

#     finally:
#         cursor.close()
#         db.close()
# # ── GET PENDING INVITATIONS FOR LOGGED-IN USER ────────────────
# @app.route("/api/invitations")
# def get_invitations():
#     if not_logged_in():
#         return jsonify({"success": False})

#     db = get_db()
#     cursor = db.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT ei.invitation_id, ei.event_id, ei.sent_at,
#                e.title      AS event_title,
#                e.start_time, e.end_time,
#                u.name       AS sender_name
#         FROM event_invitations ei
#         JOIN events e ON ei.event_id  = e.event_id
#         JOIN users  u ON ei.sender_id = u.user_id
#         WHERE ei.receiver_id = %s
#           AND ei.invitation_id NOT IN (
#               SELECT invitation_id FROM invitation_responses
#           )
#         ORDER BY ei.sent_at DESC
#     """, (session["user_id"],))
#     rows = cursor.fetchall()

#     for r in rows:
#         for k in ("sent_at", "start_time", "end_time"):
#             if r.get(k) and hasattr(r[k], "isoformat"):
#                 r[k] = r[k].isoformat()

#     cursor.close()
#     db.close()
#     return jsonify({"success": True, "invitations": rows})

# # ── RESPOND TO INVITATION ─────────────────────────────────────
# @app.route("/api/invitations/<int:inv_id>", methods=["POST"])
# def respond_invitation(inv_id):
#     if not_logged_in():
#         return jsonify({
#             "success": False,
#             "message": "Unauthorized."
#         }), 401

#     data = request.get_json(silent=True) or {}

#     action = (data.get("action") or "").strip().lower()

#     if action not in ("accept", "decline"):
#         return jsonify({
#             "success": False,
#             "message": "Invalid action."
#         }), 400

#     status_id = 1 if action == "accept" else 2

#     db = get_db()
#     cursor = db.cursor(dictionary=True)

#     try:
#         # Check invitation exists and belongs to logged-in user
#         cursor.execute(
#             """
#             SELECT invitation_id, receiver_id
#             FROM event_invitations
#             WHERE invitation_id = %s
#             """,
#             (inv_id,)
#         )

#         invitation = cursor.fetchone()

#         if not invitation:
#             return jsonify({
#                 "success": False,
#                 "message": "Invitation not found."
#             }), 404

#         if invitation["receiver_id"] != session["user_id"]:
#             return jsonify({
#                 "success": False,
#                 "message": "You are not authorized to respond to this invitation."
#             }), 403

#         # Already responded?
#         cursor.execute(
#             """
#             SELECT response_id
#             FROM invitation_responses
#             WHERE invitation_id = %s
#             """,
#             (inv_id,)
#         )

#         if cursor.fetchone():
#             return jsonify({
#                 "success": False,
#                 "message": "Invitation has already been responded to."
#             }), 409

#         cursor.execute(
#             """
#             INSERT INTO invitation_responses
#             (invitation_id, status_id)
#             VALUES (%s, %s)
#             """,
#             (inv_id, status_id)
#         )

#         db.commit()

#         message = (
#             "You joined the event!"
#             if action == "accept"
#             else "Invitation declined."
#         )

#         return jsonify({
#             "success": True,
#             "message": message
#         }), 201

#     except Exception as e:
#         db.rollback()
#         logger.exception(e)

#         return jsonify({
#             "success": False,
#             "message": "Unable to process invitation."
#         }), 500

#     finally:
#         cursor.close()
#         db.close()

# # ── RUN ───────────────────────────────────────────────────────
# if __name__ == "__main__":
#     app.run(
#         host="127.0.0.1",
#         port=8000,
#         debug=True
#     )