import sqlite3

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    database = tmp_path / "employees.sqlite3"
    return create_app({"TESTING": True, "DATABASE": str(database)})


@pytest.fixture()
def client(app):
    return app.test_client()


def test_api_info(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Employee Management API"


def test_list_employees_empty(client):
    response = client.get("/employees")

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_employees_returns_records_in_id_order(client, app):
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        connection.executemany(
            "INSERT INTO employees (name, email, department) VALUES (?, ?, ?)",
            [
                ("Avery Chen", "avery@example.com", "Engineering"),
                ("Jordan Lee", "jordan@example.com", "People"),
            ],
        )

    response = client.get("/employees")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "name": "Avery Chen",
            "email": "avery@example.com",
            "department": "Engineering",
        },
        {
            "id": 2,
            "name": "Jordan Lee",
            "email": "jordan@example.com",
            "department": "People",
        },
    ]
