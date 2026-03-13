from unittest.mock import patch

import pytest

from fastapi_demo import db


@pytest.fixture(autouse=True)
def _use_in_memory_db():
    """Redirect all db functions to an in-memory SQLite database."""
    with patch.object(db, "DB_PATH", ":memory:"):
        # Force a single shared connection for the in-memory DB so all
        # functions operate on the same tables.
        conn = db._connect()
        with patch.object(db, "_connect", return_value=conn):
            db.init_db()
            yield
        conn.close()


class TestInitDb:
    def test_creates_tickets_table(self):
        # init_db already ran in fixture; verify the table exists
        conn = db._connect()
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'"
        ).fetchone()
        assert row is not None

    def test_is_idempotent(self):
        db.init_db()  # calling again should not raise
        tickets = db.list_tickets()
        assert tickets == []


class TestCreateTicket:
    def test_returns_ticket_with_defaults(self):
        ticket = db.create_ticket(subject="Bug", description="It's broken")
        assert ticket["id"] == 1
        assert ticket["subject"] == "Bug"
        assert ticket["description"] == "It's broken"
        assert ticket["priority"] == "medium"
        assert ticket["status"] == "open"

    def test_custom_priority(self):
        ticket = db.create_ticket(subject="Urgent", description="Fire", priority="high")
        assert ticket["priority"] == "high"

    def test_auto_increments_id(self):
        t1 = db.create_ticket(subject="First", description="d1")
        t2 = db.create_ticket(subject="Second", description="d2")
        assert t2["id"] == t1["id"] + 1


class TestGetTicket:
    def test_existing_ticket(self):
        created = db.create_ticket(subject="Hello", description="World")
        fetched = db.get_ticket(created["id"])
        assert fetched == created

    def test_nonexistent_ticket(self):
        assert db.get_ticket(9999) is None


class TestListTickets:
    def test_empty(self):
        assert db.list_tickets() == []

    def test_returns_all_tickets(self):
        db.create_ticket(subject="A", description="a")
        db.create_ticket(subject="B", description="b")
        tickets = db.list_tickets()
        assert len(tickets) == 2
        assert {t["subject"] for t in tickets} == {"A", "B"}


class TestUpdateTicket:
    def test_update_single_field(self):
        ticket = db.create_ticket(subject="Old", description="desc")
        updated = db.update_ticket(ticket["id"], subject="New")
        assert updated["subject"] == "New"
        assert updated["description"] == "desc"  # unchanged

    def test_update_status(self):
        ticket = db.create_ticket(subject="Task", description="do it")
        updated = db.update_ticket(ticket["id"], status="closed")
        assert updated["status"] == "closed"

    def test_update_multiple_fields(self):
        ticket = db.create_ticket(subject="X", description="Y")
        updated = db.update_ticket(ticket["id"], subject="A", priority="high", status="in_progress")
        assert updated["subject"] == "A"
        assert updated["priority"] == "high"
        assert updated["status"] == "in_progress"

    def test_nonexistent_ticket(self):
        assert db.update_ticket(9999, status="closed") is None

    def test_no_fields(self):
        assert db.update_ticket(1) is None


class TestDeleteTicket:
    def test_delete_existing(self):
        ticket = db.create_ticket(subject="Gone", description="soon")
        assert db.delete_ticket(ticket["id"]) is True
        assert db.get_ticket(ticket["id"]) is None

    def test_delete_nonexistent(self):
        assert db.delete_ticket(9999) is False
