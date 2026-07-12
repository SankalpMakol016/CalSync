from flask import Blueprint, jsonify, request, session

from db import get_db
from logger.logger import logger
from utils.auth import login_required, login_required_401
from utils.serializers import serialize_datetimes

invitations_bp = Blueprint("invitations", __name__)


# ── GET ALL OTHER USERS (for invite dropdown) ─────────────────
@invitations_bp.route("/api/users")
@login_required
def get_users():
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
@invitations_bp.route("/api/invite", methods=["POST"])
@login_required_401
def send_invite():
    data = request.get_json(silent=True) or {}

    event_id = data.get("event_id")
    receiver_id = data.get("receiver_id")
    sender_id = session["user_id"]

    # Required fields
    if not event_id or not receiver_id:
        return jsonify({
            "success": False,
            "message": "Event ID and receiver are required."
        }), 400

    # Validate IDs
    try:
        event_id = int(event_id)
        receiver_id = int(receiver_id)
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid event or receiver ID."
        }), 400

    # Prevent self-invitation
    if receiver_id == sender_id:
        return jsonify({
            "success": False,
            "message": "You can't invite yourself."
        }), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # Check event exists and fetch creator
        cursor.execute(
            """
            SELECT event_id, created_by
            FROM events
            WHERE event_id = %s
            """,
            (event_id,)
        )

        event = cursor.fetchone()

        if not event:
            return jsonify({
                "success": False,
                "message": "Event not found."
            }), 404

        # Only creator can invite users
        if event["created_by"] != sender_id:
            return jsonify({
                "success": False,
                "message": "Only the event creator can send invitations."
            }), 403

        # Check receiver exists
        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = %s
            """,
            (receiver_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        # Already invited?
        cursor.execute(
            """
            SELECT invitation_id
            FROM event_invitations
            WHERE event_id = %s
              AND receiver_id = %s
            """,
            (event_id, receiver_id)
        )

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "User has already been invited."
            }), 409

        # Already participating?
        cursor.execute(
            """
            SELECT 1
            FROM event_participants
            WHERE event_id = %s
            AND user_id = %s
            """,
            (event_id, receiver_id)
        )

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "User is already participating in this event."
            }), 409

        # Create invitation
        cursor.execute(
            """
            INSERT INTO event_invitations
            (event_id, sender_id, receiver_id)
            VALUES (%s, %s, %s)
            """,
            (event_id, sender_id, receiver_id)
        )

        db.commit()

        return jsonify({
            "success": True,
            "message": "Invitation sent successfully."
        }), 201

    except Exception as e:
        db.rollback()
        logger.exception(e)

        return jsonify({
            "success": False,
            "message": "Unable to send invitation."
        }), 500

    finally:
        cursor.close()
        db.close()


# ── GET PENDING INVITATIONS FOR LOGGED-IN USER ────────────────
@invitations_bp.route("/api/invitations")
@login_required
def get_invitations():
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
        serialize_datetimes(r, ("sent_at", "start_time", "end_time"))

    cursor.close()
    db.close()
    return jsonify({"success": True, "invitations": rows})


# ── RESPOND TO INVITATION ─────────────────────────────────────
@invitations_bp.route("/api/invitations/<int:inv_id>", methods=["POST"])
@login_required_401
def respond_invitation(inv_id):
    data = request.get_json(silent=True) or {}

    action = (data.get("action") or "").strip().lower()

    if action not in ("accept", "decline"):
        return jsonify({
            "success": False,
            "message": "Invalid action."
        }), 400

    status_id = 1 if action == "accept" else 2

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # Check invitation exists and belongs to logged-in user
        cursor.execute(
            """
            SELECT invitation_id, receiver_id
            FROM event_invitations
            WHERE invitation_id = %s
            """,
            (inv_id,)
        )

        invitation = cursor.fetchone()

        if not invitation:
            return jsonify({
                "success": False,
                "message": "Invitation not found."
            }), 404

        if invitation["receiver_id"] != session["user_id"]:
            return jsonify({
                "success": False,
                "message": "You are not authorized to respond to this invitation."
            }), 403

        # Already responded?
        cursor.execute(
            """
            SELECT response_id
            FROM invitation_responses
            WHERE invitation_id = %s
            """,
            (inv_id,)
        )

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Invitation has already been responded to."
            }), 409

        cursor.execute(
            """
            INSERT INTO invitation_responses
            (invitation_id, status_id)
            VALUES (%s, %s)
            """,
            (inv_id, status_id)
        )

        db.commit()

        message = (
            "You joined the event!"
            if action == "accept"
            else "Invitation declined."
        )

        return jsonify({
            "success": True,
            "message": message
        }), 201

    except Exception as e:
        db.rollback()
        logger.exception(e)

        return jsonify({
            "success": False,
            "message": "Unable to process invitation."
        }), 500

    finally:
        cursor.close()
        db.close()
