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

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
