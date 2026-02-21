from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request

from .config import Config
from .db import init_app as init_db_app
from .routes import bp


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

    @app.errorhandler(413)
    def too_large(_error):
        message = "File is too large. Maximum allowed size is 20MB."
        if request.headers.get("HX-Request") == "true":
            return render_template("partials/error.html", error=message), 413
        return render_template("index.html", uploads=[], global_error=message), 413

    return app
