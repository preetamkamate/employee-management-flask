# Employee Management API

A REST API for employee records built with Flask and SQLite.

## Requirements

- Python 3.10 or newer
- pip

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python app.py
```

The SQLite database is initialized automatically in the application's `instance`
directory.

## Test

```powershell
python -m pytest
```
