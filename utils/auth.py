import re
from functools import wraps

from flask import jsonify, session

EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)
NAME_REGEX = re.compile(r"^[A-Za-z]+(?: [A-Za-z]+)*$")

# ── LOGIN CHECK ───────────────────────────────────────────────
def not_logged_in():
    return "user_id" not in session


def login_required(view_func):
    """
    Guards GET-style endpoints that, when not logged in, return a
    bare {"success": False} with the default HTTP 200 status —
    matching the original inline check used across the app.
    """
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not_logged_in():
            return jsonify({"success": False})
        return view_func(*args, **kwargs)
    return wrapped


def login_required_401(view_func):
    """
    Guards POST-style (mutating) endpoints that, when not logged
    in, return {"success": False, "message": "Unauthorized."}
    with HTTP 401 — matching the original inline check used
    across the app.
    """
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not_logged_in():
            return jsonify({
                "success": False,
                "message": "Unauthorized."
            }), 401
        return view_func(*args, **kwargs)
    return wrapped
