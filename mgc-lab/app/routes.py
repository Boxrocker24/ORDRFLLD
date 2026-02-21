from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, current_app, render_template, request

from .db import get_db
from .services.upload_service import (
    UploadValidationError,
    parse_csv_preview,
    save_upload,
    validate_csv_upload,
)

bp = Blueprint("main", __name__)


def _list_uploads():
    db = get_db()
    rows = db.execute(
        """
        SELECT id, original_filename, stored_filename, uploaded_at, row_count, col_count, file_size_bytes
        FROM uploads
        ORDER BY uploaded_at DESC
        """
    ).fetchall()
    return rows


@bp.route("/")
def index():
    uploads = _list_uploads()
    return render_template("index.html", uploads=uploads)


@bp.route("/upload", methods=["POST"])
def upload():
    upload_obj = request.files.get("csv_file")

    try:
        original_filename = validate_csv_upload(upload_obj)
        original_filename, stored_filename, file_size_bytes = save_upload(
            upload_obj,
            current_app.config["UPLOAD_FOLDER"],
            original_filename,
        )
        parse_result = parse_csv_preview(current_app.config["UPLOAD_FOLDER"], stored_filename)

        upload_id = Path(stored_filename).stem
        uploaded_at = datetime.now(timezone.utc).isoformat()

        db = get_db()
        db.execute(
            """
            INSERT INTO uploads (id, original_filename, stored_filename, uploaded_at, row_count, col_count, file_size_bytes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                upload_id,
                original_filename,
                stored_filename,
                uploaded_at,
                parse_result["row_count"],
                parse_result["col_count"],
                file_size_bytes,
            ),
        )
        db.commit()

        uploads = _list_uploads()
        selected_upload = {
            "id": upload_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "uploaded_at": uploaded_at,
            "row_count": parse_result["row_count"],
            "col_count": parse_result["col_count"],
            "file_size_bytes": file_size_bytes,
        }

        return render_template(
            "partials/upload_result.html",
            message="Upload successful.",
            upload=selected_upload,
            preview_html=parse_result["preview_html"],
            uploads=uploads,
            error=None,
        )

    except UploadValidationError as exc:
        uploads = _list_uploads()
        return (
            render_template(
                "partials/upload_result.html",
                message=None,
                upload=None,
                preview_html=None,
                uploads=uploads,
                error=str(exc),
            ),
            400,
        )
    except Exception as exc:  # pylint: disable=broad-except
        uploads = _list_uploads()
        return (
            render_template(
                "partials/upload_result.html",
                message=None,
                upload=None,
                preview_html=None,
                uploads=uploads,
                error=f"Could not process CSV: {exc}",
            ),
            400,
        )


@bp.route("/uploads/<upload_id>")
def get_upload(upload_id: str):
    db = get_db()
    row = db.execute(
        """
        SELECT id, original_filename, stored_filename, uploaded_at, row_count, col_count, file_size_bytes
        FROM uploads
        WHERE id = ?
        """,
        (upload_id,),
    ).fetchone()

    if row is None:
        return render_template("partials/error.html", error="Upload not found."), 404

    try:
        parse_result = parse_csv_preview(current_app.config["UPLOAD_FOLDER"], row["stored_filename"])
    except (OSError, sqlite3.Error, ValueError) as exc:
        return render_template("partials/error.html", error=f"Could not load preview: {exc}"), 400

    return render_template(
        "partials/preview_table.html",
        upload=row,
        preview_html=parse_result["preview_html"],
    )
