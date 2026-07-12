from datetime import datetime

from flask import Blueprint, jsonify, request, session

from db import get_db
from logger.logger import logger
from utils.auth import login_required, login_required_401
from utils.serializers import serialize_datetimes

events_bp = Blueprint("events", __name__)


# ── GET EVENTS ────────────────────────────────────────────────
# Returns events the user created PLUS events they accepted an invitation to
@events_bp.route("/api/events")
@login_required
def get_events():
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
        serialize_datetimes(ev, ("start_time", "end_time", "created_at"))

    cursor.close()
    db.close()
    return jsonify({"success": True, "events": events})


# ── CREATE EVENT ──────────────────────────────────────────────
@events_bp.route("/api/events", methods=["POST"])
@login_required_401
def create_event():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    start = (data.get("start") or "").strip()
    end = (data.get("end") or "").strip()

    # Required fields
    if not title or not start or not end:
        return jsonify({
            "success": False,
            "message": "Title, start time and end time are required."
        }), 400

    # Title length
    if len(title) > 100:
        return jsonify({
            "success": False,
            "message": "Title cannot exceed 100 characters."
        }), 400

    # Parse datetime
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M")
        end_dt = datetime.strptime(end, "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid date or time format."
        }), 400

    # Logical validation
    if start_dt >= end_dt:
        return jsonify({
            "success": False,
            "message": "End time must be after start time."
        }), 400

    # Prevent creating past events
    if start_dt < datetime.now():
        return jsonify({
            "success": False,
            "message": "Cannot create an event in the past."
        }), 400

    start_sql = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_sql = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.callproc(
            "create_event",
            [
                title,
                start_sql,
                end_sql,
                session["user_id"]
            ]
        )

        for _ in cursor.stored_results():
            pass

        db.commit()

        return jsonify({
            "success": True,
            "message": "Event created successfully."
        }), 201

    except Exception as e:
        db.rollback()
        logger.exception(e)

        return jsonify({
            "success": False,
            "message": "Unable to create event."
        }), 500

    finally:
        cursor.close()
        db.close()


# ── DELETE EVENT ──────────────────────────────────────────────
@events_bp.route("/api/events/<int:event_id>", methods=["DELETE"])
@login_required
def delete_event(event_id):
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
@events_bp.route("/api/stats")
@login_required
def stats():
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


# ── GET EVENT PARTICIPANTS (owner only, read-only) ──────────────
@events_bp.route("/api/events/<int:event_id>/participants")
@login_required
def get_participants(event_id):
    user_id = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Confirm the event exists and fetch the owner's info in one go
    cursor.execute("""
        SELECT e.created_by, u.name, u.email
        FROM events e
        JOIN users u ON u.user_id = e.created_by
        WHERE e.event_id = %s
    """, (event_id,))
    event = cursor.fetchone()

    if not event:
        cursor.close()
        db.close()
        return jsonify({"success": False, "message": "Event not found."}), 404

    # Only the owner is allowed to see the participant list
    if event["created_by"] != user_id:
        cursor.close()
        db.close()
        return jsonify({
            "success": False,
            "message": "Only the event owner can view participants."
        }), 403

    owner = {"name": event["name"], "email": event["email"]}

    # One query, tagged with a status column, covers all three buckets:
    # accepted/declined live in event_participants (status_id set by the
    # after_invitation_response trigger), pending is an invitation with
    # no response row yet.
    cursor.execute("""
        SELECT u.name, u.email, 'accepted' AS status
        FROM event_participants ep
        JOIN users u ON u.user_id = ep.user_id
        WHERE ep.event_id = %s AND ep.status_id = 1

        UNION ALL

        SELECT u.name, u.email, 'declined' AS status
        FROM event_participants ep
        JOIN users u ON u.user_id = ep.user_id
        WHERE ep.event_id = %s AND ep.status_id = 2

        UNION ALL

        SELECT u.name, u.email, 'pending' AS status
        FROM event_invitations ei
        JOIN users u ON u.user_id = ei.receiver_id
        WHERE ei.event_id = %s
        AND ei.invitation_id NOT IN (SELECT invitation_id FROM invitation_responses)
    """, (event_id, event_id, event_id))
    rows = cursor.fetchall()

    cursor.close()
    db.close()

    # Split the tagged rows into their three buckets
    accepted = [{"name": r["name"], "email": r["email"]} for r in rows if r["status"] == "accepted"]
    pending  = [{"name": r["name"], "email": r["email"]} for r in rows if r["status"] == "pending"]
    declined = [{"name": r["name"], "email": r["email"]} for r in rows if r["status"] == "declined"]

    return jsonify({
        "success": True,
        "owner": owner,
        "accepted": accepted,
        "pending": pending,
        "declined": declined
    })