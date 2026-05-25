# SNAP CLASS - Online Attendance

SNAP CLASS is a Streamlit-based attendance system that combines:

- Face recognition for student sign-in and classroom attendance
- Voice recognition for optional voice-based attendance
- Supabase as the cloud database
- QR/link sharing so teachers can invite students into a subject

This README is the main practical guide for running, understanding, improving, deploying, and publishing the project.

## 1. What This Project Does

### Teacher flow

1. Register and log in
2. Create a subject
3. Share the subject code or QR join link
4. Take attendance by:
   - Uploading classroom photos for face matching
   - Recording classroom audio for voice matching
5. Save attendance records

### Student flow

1. Open the student portal
2. Use the camera for face-based login or first-time registration
3. Optionally record a short voice sample
4. Join a subject using a code or QR link
5. See enrolled subjects and attendance history

## 2. Tech Stack

- `Streamlit` for the UI
- `Supabase` for tables and persistence
- `dlib` + `face-recognition` for face embeddings
- `Resemblyzer` + `librosa` for voice embeddings
- `scikit-learn` for the SVM face classifier
- `segno` for QR code generation
- `bcrypt` for teacher password hashing

## 3. Project Structure

```text
Online-Attendance/
|-- app.py
|-- requirements.txt
|-- packages.txt
|-- Dockerfile
|-- docker-compose.yml
|-- setup_windows.ps1
|-- supabase_schema.sql
|-- supabase_schema_v2.sql
|-- .env.example
|-- .streamlit/secrets.toml.example
`-- src/
    |-- components/
    |-- database/
    |-- pipelines/
    |-- screens/
    |-- ui/
    |-- constants.py
    |-- errors.py
    `-- logger.py
```

## 4. How The App Works Internally

### Entry point

- [`app.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/app.py) starts Streamlit, initializes session state, routes users to the home, teacher, or student screens, and handles `?join-code=` auto-enrollment.

### Screens

- [`src/screens/home_screen.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/screens/home_screen.py): role selection
- [`src/screens/teacher_screen.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/screens/teacher_screen.py): teacher login, subject management, attendance, records
- [`src/screens/student_screen.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/screens/student_screen.py): face login, student registration, enrollment, dashboard

### Database layer

- [`src/database/db.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/database/db.py): current CRUD layer used by much of the app
- [`src/database/db_enhanced.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/database/db_enhanced.py): newer layer with better validation, logging, and authorization checks
- [`src/database/config.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/database/config.py): creates the Supabase client from Streamlit secrets

### ML pipelines

- [`src/pipelines/face_pipeline.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/pipelines/face_pipeline.py): extracts 128D face embeddings, trains an SVM on registered students, and predicts present students from uploaded images
- [`src/pipelines/voice_pipeline.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/pipelines/voice_pipeline.py): extracts voice embeddings and compares classroom audio against enrolled students

## 5. Dependencies To Install

### Python version

Use `Python 3.10` or `Python 3.11`.

`Python 3.12+` is risky here because `dlib` and related face-recognition packages are commonly harder to build.

### Python packages

Installed from [`requirements.txt`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/requirements.txt):

- `streamlit`
- `numpy`
- `pandas`
- `scikit-learn`
- `pillow`
- `setuptools<70`
- `cmake`
- `dlib`
- `face-recognition`
- `face-recognition-models`
- `opencv-python-headless`
- `supabase`
- `bcrypt`
- `segno`
- `librosa`
- `resemblyzer`
- `python-dotenv`
- `python-json-logger`
- `pytest`
- `pytest-cov`
- `pytest-mock`
- `pytest-asyncio`

### System packages on Linux

Installed from [`packages.txt`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/packages.txt):

- `cmake`
- `build-essential`
- `libopenblas-dev`
- `liblapack-dev`
- `libx11-dev`
- `libsndfile1`
- `ffmpeg`

### System requirements on Windows

- Microsoft Visual C++ Build Tools
- Python launcher `py`

If `dlib` fails to install on Windows, this is usually the reason.

## 6. Local Installation

### Windows

From the project root:

```powershell
.\setup_windows.ps1
```

This script:

1. Detects Python 3.10/3.11
2. Creates `.venv`
3. Upgrades `pip`, `wheel`, and `setuptools<70`
4. Installs `requirements.txt`
5. Creates `.streamlit/secrets.toml` if missing

### Manual install on Windows, Linux, or macOS

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\activate
pip install --upgrade pip "setuptools<70" wheel
pip install -r requirements.txt
```

Linux or macOS:

```bash
source .venv/bin/activate
pip install --upgrade pip "setuptools<70" wheel
pip install -r requirements.txt
```

## 7. Supabase Setup

### Create secrets

Copy the example file:

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Then fill in:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR-ANON-KEY"
```

Important:

- The current code expects `SUPABASE_URL`
- The current code expects `SUPABASE_ANON_KEY`
- Do not use `SUPABASE_KEY` in this repo anymore

### Create the database tables

For the current app, run [`supabase_schema.sql`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/supabase_schema.sql) in the Supabase SQL editor.

Use [`supabase_schema_v2.sql`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/supabase_schema_v2.sql) only if you plan to continue the production-hardening work and align the application code with that newer schema.

## 8. Run The App

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open:

- `http://localhost:8501`

## 9. Errors I Found And Fixed

I improved several issues directly in the repository:

- Fixed the teacher registration screen importing `teacher_exists` but calling `check_teacher_exists`
- Fixed the Windows setup script to create `SUPABASE_ANON_KEY` instead of the outdated `SUPABASE_KEY`
- Wired `APP_DOMAIN`, `FACE_DISTANCE_THRESHOLD`, `VOICE_MATCH_THRESHOLD`, and `VOICE_PRESENT_THRESHOLD` to shared constants so configuration is more consistent
- Removed a broken circular dependency from `docker-compose.yml`
- Added `.env.example`, `.gitignore`, and `.streamlit/secrets.toml.example`

## 10. Known Real-World Risks

This project works as a strong prototype, but before real deployment you should understand these limits:

- Face recognition and voice recognition are sensitive to lighting, microphone quality, background noise, and poor enrollment samples
- Biometric attendance has privacy and legal implications
- The app currently mixes older database code and newer hardened database code
- The newer production schema and security docs are ahead of some UI integration work
- Streamlit is simple and fast to ship, but not ideal for high-scale enterprise attendance workloads

## 11. How To Improve It Further

### Short-term improvements

- Move all screens and dialogs to `db_enhanced.py`
- Add proper validation everywhere using [`src/errors.py`](/C:/Users/nikun/OneDrive/Desktop/majorproject/Online-Attendance/src/errors.py)
- Add automated tests in a `tests/` folder
- Add confidence scores and manual correction before saving attendance
- Add duplicate-student detection during registration

### Production improvements

- Replace permissive RLS with real role-based RLS in Supabase
- Add admin users and audit review
- Add retry-safe attendance saves
- Add monitoring and alerting
- Encrypt or better control access to biometric data
- Add data retention and account deletion flows
- Add consent and privacy policy screens

## 12. Deployment Options

### Option A: Streamlit Community Cloud

Best for demos and portfolio deployment.

Steps:

1. Push the repo to GitHub
2. Open [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Create a new app from your repo
4. Set the main file to `app.py`
5. Add secrets in the Streamlit dashboard:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR-ANON-KEY"
```

6. Ensure system packages from `packages.txt` are supported

Note:

- Streamlit Cloud is the easiest place to show the project publicly
- Heavy `dlib` builds may still be tricky depending on platform changes

### Option B: Docker

Best for controlled server deployment.

Build:

```bash
docker build -t online-attendance .
```

Run:

```bash
docker run -p 8501:8501 ^
  -e SUPABASE_URL=https://YOUR-PROJECT.supabase.co ^
  -e SUPABASE_ANON_KEY=YOUR-ANON-KEY ^
  -e APP_DOMAIN=http://localhost:8501 ^
  online-attendance
```

Or use:

```bash
docker-compose up --build
```

### Option C: VPS or cloud VM

Best for more serious real-world deployment.

Recommended stack:

- Ubuntu server
- Docker
- Nginx reverse proxy
- HTTPS via Let's Encrypt
- Supabase managed database

## 13. Real-World Deployment Checklist

Before calling it production-ready:

- Use HTTPS only
- Keep `.streamlit/secrets.toml` and `.env` out of GitHub
- Use `SUPABASE_ANON_KEY`, not a service key in the frontend
- Review and tighten RLS policies
- Store a real public domain in `APP_DOMAIN`
- Test camera and microphone permissions on real student devices
- Write a privacy policy for biometric data
- Define data retention and deletion rules
- Add logging review and backups
- Add at least smoke tests for login, subject creation, enrollment, and attendance save

## 14. How To Put This Project On GitHub

### Initialize Git locally

Inside the project folder:

```bash
git init
git add .
git commit -m "Initial commit for Online Attendance project"
```

### Create a GitHub repository

1. Go to [GitHub](https://github.com)
2. Click `New repository`
3. Name it something like `online-attendance`
4. Do not upload your secrets

### Connect local repo to GitHub

```bash
git remote add origin https://github.com/YOUR-USERNAME/online-attendance.git
git branch -M main
git push -u origin main
```

### Important GitHub safety rules

- Commit `.env.example`
- Commit `.streamlit/secrets.toml.example`
- Do not commit `.env`
- Do not commit `.streamlit/secrets.toml`
- Do not commit log files
- Do not commit `.venv`

This repo now includes a `.gitignore` to help with that.

## 15. Useful Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Run sample tests:

```bash
pytest test_errors_sample.py -v
```

Build Docker image:

```bash
docker build -t online-attendance .
```

## 16. Troubleshooting

### `Missing secret: 'SUPABASE_URL'` or `SUPABASE_ANON_KEY`

Create `.streamlit/secrets.toml` from the example file and fill in real values.

### `dlib` install fails

Install Visual C++ Build Tools on Windows, or the Linux packages from `packages.txt`.

### Face login does not detect a face

- Use a bright image
- Keep one face in frame
- Avoid tilted or blurry photos

### Voice attendance is weak or inaccurate

- Use clearer enrollment audio
- Reduce background noise
- Tune `VOICE_PRESENT_THRESHOLD` and `VOICE_MATCH_THRESHOLD`

### Streamlit or Docker starts but attendance is not saved

Check that:

- Supabase tables were created from `supabase_schema.sql`
- Secrets are correct
- The app can insert into `attendance_logs`

## 17. Current Status

This is a good portfolio/demo project and a workable prototype for small controlled environments. It is not yet a finished enterprise-ready attendance platform, but the structure is good and the next hardening steps are clear.
