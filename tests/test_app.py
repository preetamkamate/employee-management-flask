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


def test_create_employee_trims_values_and_returns_created_record(client):
    response = client.post(
        "/employees",
        json={
            "name": "  Casey Morgan  ",
            "email": " casey@example.com ",
            "department": " Product ",
        },
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 1,
        "name": "Casey Morgan",
        "email": "casey@example.com",
        "department": "Product",
    }


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"email": "person@example.com", "department": "Engineering"},
        {"name": "", "email": "person@example.com", "department": "Engineering"},
        {"name": "   ", "email": "person@example.com", "department": "Engineering"},
        {"name": "Person", "email": "", "department": "Engineering"},
        {"name": "Person", "email": 42, "department": "Engineering"},
        {"name": "Person", "email": "person@example.com", "department": None},
        {"name": "Person", "email": "person@example.com", "department": "   "},
    ],
)
def test_create_employee_rejects_invalid_input(client, payload):
    response = client.post("/employees", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_employee_rejects_non_json_body(client):
    response = client.post(
        "/employees", data="not json", content_type="text/plain"
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_employee_rejects_duplicate_email(client):
    payload = {
        "name": "Taylor Park",
        "email": "taylor@example.com",
        "department": "Finance",
    }
    first_response = client.post("/employees", json=payload)
    duplicate_response = client.post(
        "/employees",
        json={
            "name": "Taylor Park II",
            "email": "taylor@example.com",
            "department": "Legal",
        },
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert "error" in duplicate_response.get_json()


def test_created_employee_can_be_retrieved(client):
    client.post(
        "/employees",
        json={
            "name": "Riley Diaz",
            "email": "riley@example.com",
            "department": "Operations",
        },
    )

    response = client.get("/employees")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "name": "Riley Diaz",
            "email": "riley@example.com",
            "department": "Operations",
        }
    ]
