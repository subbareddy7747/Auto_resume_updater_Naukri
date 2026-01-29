# Auto_resume_updater_Naukri

Automates resume upload and job applications on Naukri, then saves a CSV report of results.

## Project structure

```
.
├── .github/workflows/ci.yml
├── src/naukri_auto_apply.py
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set the login credentials via environment variables:

```bash
export NAUKRI_EMAIL="you@example.com"
export NAUKRI_PASSWORD="your_password"
```

Place your resume in the repository root and update `RESUME_FILE` in `src/naukri_auto_apply.py` if needed.

## Run

```bash
python src/naukri_auto_apply.py
```

## CI/CD

A GitHub Actions workflow runs on pushes and pull requests to `main` and validates the code by
installing dependencies and compiling the Python source files.
