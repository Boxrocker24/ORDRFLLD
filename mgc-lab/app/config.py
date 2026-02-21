import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 20 * 1024 * 1024))

    upload_folder_raw = os.getenv("UPLOAD_FOLDER", "data/uploads")
    if Path(upload_folder_raw).is_absolute():
        UPLOAD_FOLDER = str(Path(upload_folder_raw))
    else:
        UPLOAD_FOLDER = str((BASE_DIR / upload_folder_raw).resolve())

    database_path_raw = os.getenv("DATABASE_PATH", "instance/app.db")
    if Path(database_path_raw).is_absolute():
        DATABASE_PATH = str(Path(database_path_raw))
    else:
        DATABASE_PATH = str((BASE_DIR / database_path_raw).resolve())
