# Employee Management API

A small REST API for creating and listing employees. It uses Flask for HTTP
handling and SQLite for persistent storage; the database and employee table are
created automatically when the application starts.

## Features

- List employees as JSON.
- Create employees with required name, email, and department fields.
- Enforce unique email addresses in SQLite.
- Trim surrounding whitespace and return clear validation/conflict responses.
- Run the test suite with pytest.

## Prerequisites

- Python 3.10 or newer
- Git (for cloning or publishing the repository)
- VS Code is optional

## Installation

Clone the repository, then change into its project directory:

```powershell
git clone https://github.com/<YOUR-USERNAME>/employee-management-flask.git
Set-Location employee-management-flask
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application and test dependencies:

```powershell
python -m pip install -r requirements.txt
```

On macOS or Linux, create and activate the environment with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the application

From the project directory, run:

```powershell
python app.py
```

The local development server is available at `http://127.0.0.1:5000`. The
application creates `instance/employees.sqlite3` on startup. The database is
local application data and is excluded from Git.

## API

### `GET /`

Returns basic API information.

```powershell
Invoke-RestMethod http://127.0.0.1:5000/
```

### `GET /employees`

Returns all employees as a JSON array, ordered by ID. An empty database returns
`[]`. Successful responses use HTTP `200`.

```powershell
Invoke-RestMethod http://127.0.0.1:5000/employees
```

### `POST /employees`

Creates an employee. Send a JSON object with non-empty string values for all
three required fields. Surrounding whitespace is trimmed.

```powershell
$employee = @{
    name = "Jordan Lee"
    email = "jordan@example.com"
    department = "Engineering"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri http://127.0.0.1:5000/employees `
    -Method Post `
    -ContentType "application/json" `
    -Body $employee
```

The response contains the created record, including its generated `id`, and
uses HTTP `201`. Invalid JSON or missing, non-string, or blank required values
return HTTP `400`. An email already in use returns HTTP `409`.

## Run tests

With the virtual environment activated:

```powershell
python -m pytest -v
```

Tests use temporary SQLite databases and do not modify the application's local
database.

## Publish to GitHub

To create and publish a repository from VS Code, open this project folder, open
**Source Control**, select this project's repository if more than one is shown,
then choose **Publish to GitHub**. Sign in if prompted, choose the repository
visibility, and use `employee-management-flask` as the repository name.

Alternatively, create an **empty** GitHub repository named
`employee-management-flask` (do not initialize it with a README, license, or
Git ignore file). Then, from this project directory, add its URL and push the
existing `main` branch:

```powershell
git remote add origin https://github.com/<YOUR-USERNAME>/employee-management-flask.git
git push -u origin main
```

Git may prompt you to authenticate using your configured Git Credential Manager
or VS Code/GitHub sign-in. Never add credentials or tokens to the repository.
