from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from fastapi_demo.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_db():
    with patch("fastapi_demo.main.db") as mock:
        yield mock


def test_create_ticket(mock_db):
    mock_db.create_ticket.return_value = {
        "id": 1,
        "subject": "Test Subject",
        "description": "Test Description",
        "priority": "medium",
        "status": "open",
    }
    response = client.post(
        "/tickets",
        json={"subject": "Test Subject", "description": "Test Description"},
    )
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["subject"] == "Test Subject"
    assert response.json()["status"] == "open"


def test_create_ticket_with_priority(mock_db):
    mock_db.create_ticket.return_value = {
        "id": 2,
        "subject": "Urgent Issue",
        "description": "Something broke",
        "priority": "high",
        "status": "open",
    }
    response = client.post(
        "/tickets",
        json={"subject": "Urgent Issue", "description": "Something broke", "priority": "high"},
    )
    assert response.status_code == 201
    assert response.json()["priority"] == "high"


def test_create_ticket_missing_required_fields():
    response = client.post("/tickets", json={"subject": "Only Subject"})
    assert response.status_code == 422


def test_list_tickets_empty(mock_db):
    mock_db.list_tickets.return_value = []
    response = client.get("/tickets")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tickets(mock_db):
    mock_db.list_tickets.return_value = [
        {"id": 1, "subject": "Issue 1", "description": "Desc 1", "priority": "low", "status": "open"},
        {"id": 2, "subject": "Issue 2", "description": "Desc 2", "priority": "high", "status": "open"},
    ]
    response = client.get("/tickets")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_ticket(mock_db):
    mock_db.get_ticket.return_value = {
        "id": 1,
        "subject": "Test Subject",
        "description": "Test Description",
        "priority": "medium",
        "status": "open",
    }
    response = client.get("/tickets/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_db.get_ticket.assert_called_once_with(1)


def test_get_ticket_not_found(mock_db):
    mock_db.get_ticket.return_value = None
    response = client.get("/tickets/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_delete_ticket(mock_db):
    mock_db.delete_ticket.return_value = True
    response = client.delete("/tickets/1")
    assert response.status_code == 204
    mock_db.delete_ticket.assert_called_once_with(1)


def test_delete_ticket_not_found(mock_db):
    mock_db.delete_ticket.return_value = False
    response = client.delete("/tickets/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_create_ticket_calls_db_with_correct_args(mock_db):
    mock_db.create_ticket.return_value = {
        "id": 3,
        "subject": "Bug Report",
        "description": "Found a bug",
        "priority": "low",
        "status": "open",
    }
    client.post(
        "/tickets",
        json={"subject": "Bug Report", "description": "Found a bug", "priority": "low"},
    )
    mock_db.create_ticket.assert_called_once_with(subject="Bug Report", description="Found a bug", priority="low")


def test_update_ticket_status(mock_db):
    mock_db.update_ticket.return_value = {
        "id": 1,
        "subject": "Test Subject",
        "description": "Test Description",
        "priority": "medium",
        "status": "closed",
    }
    response = client.patch("/tickets/1", json={"status": "closed"})
    assert response.status_code == 200
    assert response.json()["status"] == "closed"
    mock_db.update_ticket.assert_called_once_with(1, status="closed")


def test_update_ticket_multiple_fields(mock_db):
    mock_db.update_ticket.return_value = {
        "id": 1,
        "subject": "Updated",
        "description": "Test Description",
        "priority": "high",
        "status": "in_progress",
    }
    response = client.patch("/tickets/1", json={"subject": "Updated", "priority": "high", "status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["subject"] == "Updated"
    assert response.json()["status"] == "in_progress"


def test_update_ticket_not_found(mock_db):
    mock_db.update_ticket.return_value = None
    response = client.patch("/tickets/999", json={"status": "closed"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_update_ticket_no_fields():
    response = client.patch("/tickets/1", json={})
    assert response.status_code == 422


def test_update_ticket_invalid_status():
    response = client.patch("/tickets/1", json={"status": "invalid"})
    assert response.status_code == 422
