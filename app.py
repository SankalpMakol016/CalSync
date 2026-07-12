from flask import Flask, jsonify

from config.config import Config
from logger.logger import logger

from routes.auth import auth_bp
from routes.events import events_bp
from routes.invitations import invitations_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(invitations_bp)

    register_error_handlers(app)

    logger.info("CalSync application started.")

    return app


# ── CENTRALIZED ERROR HANDLING ──────────────────────────────────
def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "success": False,
            "message": "Resource not found."
        }), 404

    @app.errorhandler(500)
    def handle_server_error(error):
        logger.error(error)
        return jsonify({
            "success": False,
            "message": "Internal server error."
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        logger.exception(error)
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred."
        }), 500


app = create_app()

# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )
