import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, current_app, g, jsonify, request


SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department TEXT NOT NULL
)
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def initialize_database(database: str) -> None:
    connection = sqlite3.connect(database)
    try:
        connection.executescript(SCHEMA)
    finally:
        connection.close()


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "employees.sqlite3")
    )
    if test_config is not None:
        app.config.update(test_config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    initialize_database(app.config["DATABASE"])
    app.teardown_appcontext(close_db)

    @app.get("/")
    def api_info():
        return jsonify(
            {
                "name": "Employee Management API",
                "version": "1.0.0",
                "endpoints": {"employees": "/employees"},
            }
        )

    @app.get("/employees")
    def list_employees():
        employees = get_db().execute(
            "SELECT id, name, email, department FROM employees ORDER BY id"
        ).fetchall()
        return jsonify([dict(employee) for employee in employees])

    @app.post("/employees")
    def create_employee():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        fields = ("name", "email", "department")
        invalid_fields = [
            field
            for field in fields
            if not isinstance(payload.get(field), str) or not payload[field].strip()
        ]
        if invalid_fields:
            return (
                jsonify(
                    {
                        "error": "Required fields must be non-empty strings",
                        "fields": invalid_fields,
                    }
                ),
                400,
            )

        values = tuple(payload[field].strip() for field in fields)
        connection = get_db()
        cursor = connection.execute(
            """
            INSERT INTO employees (name, email, department)
            VALUES (?, ?, ?)
            ON CONFLICT(email) DO NOTHING
            """,
            values,
        )
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({"error": "An employee with this email already exists"}), 409

        employee = connection.execute(
            "SELECT id, name, email, department FROM employees WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        connection.commit()
        return jsonify(dict(employee)), 201

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
