Lesson Planner
===============

A small Django app to help teachers generate lesson plans and optionally download them as PDF or Word (.docx) files.

This repository contains:
- `lesson/` - Django project and app code.
  - `lesson_generator/` - main app that contains views, templates, static assets and migrations.
  - `lesson_planner/` - Django project configuration (settings, urls, wsgi/asgi).

Quick features
--------------
- Fill a simple form (subject, grade, topic, duration, teacher actions) to generate a lesson plan.
- Save generated plans; recent plans are shown on the dashboard.
- Download a generated or saved plan as PDF or DOCX.
  - If the required libraries aren't installed, the server will provide a plain-text `.txt` fallback so you always get the generated content.
- "Generate & Download" buttons let you immediately download the freshly generated plan (on-the-fly) without needing to find the saved copy.

Prerequisites
-------------
- Python 3.11+ / 3.12+ recommended (your environment appears to be Python 3.13).
- pip available.
- Optional (for richer downloads):
  - `reportlab` — for PDF generation
  - `python-docx` — for DOCX (Word) generation

Install optional packages (recommended for full functionality):

PowerShell
```powershell
pip install reportlab python-docx
```

Create a virtual environment (recommended)
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -U pip
```

Project setup
-------------
1. Install dependencies (at minimum Django):
```powershell
pip install Django
```

2. Apply migrations:
```powershell
python lesson\manage.py migrate
```

3. Create a superuser (optional, to access admin):
```powershell
python lesson\manage.py createsuperuser
```

4. Run development server:
```powershell
python lesson\manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser.

Usage notes
-----------
- After logging in, go to Dashboard / Generate Lesson Plan.
- Fill the form and either click "Generate Lesson Plan" (to preview and save) or use:
  - "Generate & Download PDF" — creates the plan and streams a PDF back to your browser; falls back to `.txt` if `reportlab` is not installed.
  - "Generate & Download DOCX" — creates the plan and streams a `.docx` file; falls back to `.txt` if `python-docx` is not installed.
- Each saved plan in "Your recent lesson plans" has explicit Download PDF and Download DOCX links.

Implementation notes
--------------------
- The app uses server-side generation for PDF (reportlab) and DOCX (python-docx).
- If the libraries are not available, the code returns a plain-text `.txt` attachment containing only the generated plan (ensures users always get the generated content instead of an HTML page).
- Download links include `download` attributes and `Content-Disposition: attachment` headers so browsers prompt to save the file.
- The app currently saves the generated plan before streaming the download (so the filename includes the saved plan's id). If you prefer not to save when only downloading, the view can be adjusted to generate and stream from the POST data only.

Troubleshooting
---------------
- ModuleNotFoundError: No module named 'leason_planner'
  - Older typos in the project name were corrected to `lesson_planner`. If you still see this error, search for `leason_planner` in code and replace with `lesson_planner`, then re-run server.

- If PDF/DOCX downloads don't start or open as HTML, check:
  - The response headers in browser devtools (should include `Content-Disposition: attachment; filename=...`).
  - Whether `reportlab` / `python-docx` are installed — otherwise the app will return a `.txt` fallback.

Developer commands
------------------
- Run Django checks:
```powershell
python lesson\manage.py check
```

- Run tests (if present):
```powershell
python lesson\manage.py test
```

Next steps / suggested improvements
----------------------------------
- Improve PDF typography (register a TTF like DejaVu Sans with reportlab) to support Unicode better.
- Offer an option to download both PDF and DOCX as a ZIP in one click.
- Add better DOCX styling (bold headings, lists, styles) and Word metadata.
- Add unit tests for PDF/DOCX generation fallback behavior.

License
-------
Add a license file (`LICENSE`) if you want to set the project license. No license is included by default.

Contact / Help
--------------
If you'd like me to implement any of the suggested improvements (on-the-fly no-save downloads, ZIP export, improved formatting), tell me which one and I will implement it next.