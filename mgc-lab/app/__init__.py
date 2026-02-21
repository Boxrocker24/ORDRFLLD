from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request

from .config import Config
from .db import get_db, init_app as init_db_app
from .routes import bp


def _fetch_uploads_for_error():
    db = get_db()
    return db.execute(
        """
        SELECT id, original_filename, stored_filename, uploaded_at, row_count, col_count, file_size_bytes
        FROM uploads
        ORDER BY uploaded_at DESC
        """
    ).fetchall()


def create_app():
    load_dotenv()

    root_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(root_dir / "templates"),
        static_folder=str(root_dir / "static"),
    )
    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)

    init_db_app(app)
    app.register_blueprint(bp)

    @app.route("/favicon.ico")
    def favicon():
        return "", 204

    @app.errorhandler(413)
    def too_large(_error):
        message = "File is too large. Maximum allowed size is 20MB."
        uploads = _fetch_uploads_for_error()
        if request.headers.get("HX-Request") == "true":
            return (
                render_template(
                    "partials/upload_result.html",
                    message=None,
                    upload=None,
                    preview_html=None,
                    uploads=uploads,
                    error=message,
                ),
                413,
            )
        return render_template("index.html", uploads=uploads, global_error=message), 413

    return app
