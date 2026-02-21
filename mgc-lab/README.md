# mgc-lab

A local-first CSV upload and preview lab built with **Flask + Jinja + HTMX + Tailwind CDN + SQLite + Pandas**.

## Stack

- Python 3.11+
- Flask (app factory pattern)
- Jinja templates (server-rendered)
- HTMX (partial page updates)
- Tailwind CSS CDN
- Chart.js CDN (included for future chart features)
- SQLite (upload metadata)
- Pandas (CSV parsing + first-50-row preview)

## Features (MVP)

- Upload CSV files on `/`
- Files are stored in `data/uploads/` with UUID-based file names
- Upload metadata is persisted in SQLite:
  - `id`
  - `original_filename`
  - `stored_filename`
  - `uploaded_at`
  - `row_count`
  - `col_count`
  - `file_size_bytes`
- Shows success/error feedback after upload
- Renders a styled preview table (first 50 rows)
- Lists previous uploads (latest first), clickable to reload preview without full page reload
- Monospace UI typography for a data-lab feel

## Security Basics Implemented

- Accepts only `.csv` extension
- Uses `secure_filename` for original name hygiene
- Stores uploaded files as `uuid.csv`
- Enforces max upload size via `MAX_CONTENT_LENGTH` (default 20MB)
- No file execution of any kind

## Project Structure

```text
mgc-lab/
  README.md
  requirements.txt
  .env.example
  run.py
  app/
    __init__.py
    config.py
    db.py
    routes.py
    services/
      upload_service.py
  templates/
    layout.html
    index.html
    partials/
      uploads_list.html
      upload_result.html
      preview_table.html
      error.html
  static/
    app.css
  data/
    uploads/
  instance/
    app.db   (created at runtime)
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Windows PowerShell: copy .env.example .env
python run.py
```

Visit: <http://127.0.0.1:5000>

## Environment Variables

Set in `.env` (copy from `.env.example`):

- `SECRET_KEY`
- `UPLOAD_FOLDER` (default `data/uploads`)
- `MAX_CONTENT_LENGTH` (default `20971520`, i.e., 20MB)
- `DATABASE_PATH` (default `instance/app.db`)

On first run, the app creates upload/db folders and initializes the SQLite schema automatically.
