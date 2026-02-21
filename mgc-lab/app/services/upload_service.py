from __future__ import annotations

import uuid
from pathlib import Path

import pandas as pd
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {".csv"}


class UploadValidationError(Exception):
    """Raised when an uploaded file does not meet validation requirements."""


def validate_csv_upload(upload: FileStorage) -> str:
    if upload is None or upload.filename is None or upload.filename.strip() == "":
        raise UploadValidationError("Please choose a CSV file to upload.")

    safe_name = secure_filename(upload.filename)
    ext = Path(safe_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadValidationError("Only .csv files are allowed.")

    return safe_name


def save_upload(upload: FileStorage, upload_folder: str, original_filename: str) -> tuple[str, str, int]:
    upload_dir = Path(upload_folder)
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid.uuid4()}.csv"
    destination = upload_dir / stored_filename
    upload.save(destination)

    file_size_bytes = destination.stat().st_size
    return original_filename, stored_filename, file_size_bytes


def parse_csv_preview(upload_folder: str, stored_filename: str) -> dict:
    file_path = Path(upload_folder) / stored_filename
    df = pd.read_csv(file_path, low_memory=False)

    row_count, col_count = df.shape
    preview_df = df.head(50)

    preview_html = preview_df.to_html(
        classes="data-table min-w-full text-sm text-left text-slate-700",
        index=False,
        border=0,
        na_rep="",
    )

    return {
        "row_count": int(row_count),
        "col_count": int(col_count),
        "preview_html": preview_html,
    }
