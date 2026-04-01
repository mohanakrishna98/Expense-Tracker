import pytest
from datetime import date
# Eg
SAMPLE = {"description": "Walmart", "amount": 45.50, "date": "2026-03-01"}
#client taken from conftest.py
def create_one(client, payload=None):
    """Creates single expense and returns the response."""
    return client.post("/expenses", json=payload or SAMPLE).json()

#  POST /expenses
class TestCreateExpense:
    def test_creates_successfully(self, client):
        res = client.post("/expenses", json=SAMPLE)
        assert res.status_code == 201
        body = res.json()
        assert body["description"] == "Walmart"
        assert body["amount"] == 45.50
        assert body["date"] == "2026-03-01"
        assert "id" in body

    def test_rejects_zero_amount(self, client):
        res = client.post("/expenses", json={**SAMPLE, "amount": 0})
        assert res.status_code == 422

#  POST /expenses/bulk
class TestBulkCreate:
    def test_bulk_creates_multiple(self, client):
        payload = [
            {"description": "Walmart",   "amount": 45.50, "date": "2026-03-01"},
            {"description": "Starbucks", "amount": 6.75,  "date": "2026-03-02"},
            {"description": "Amazon",    "amount": 120.0, "date": "2026-03-03"},
            {"description": "test new expense",    "amount": 10.0, "date": "2026-03-05"}
        ]
        res = client.post("/expenses/bulk", json=payload)
        assert res.status_code == 201
        assert len(res.json()) == 4

# GET /expenses
class TestListExpenses:
    def test_returns_empty_list_initially(self, client):
        res = client.get("/expenses")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_created_expenses(self, client):
        create_one(client)
        create_one(client, {**SAMPLE, "description": "Target", "amount": 30.0})
        res = client.get("/expenses")
        assert res.status_code == 200
        assert len(res.json()) == 2

#  GET /expenses/{id}
class TestGetExpense:
    def test_returns_correct_expense(self, client):
        created = create_one(client)
        res = client.get(f"/expenses/{created['id']}")
        assert res.status_code == 200
        assert res.json()["id"] == created["id"]

    def test_returns_404_for_missing(self, client):
        res = client.get("/expenses/99999")
        assert res.status_code == 404


#  PATCH /expenses/{id}
class TestUpdateExpense:
    def test_updates_amount(self, client):
        created = create_one(client)
        res = client.patch(f"/expenses/{created['id']}", json={"amount": 99.99})
        assert res.status_code == 200
        assert res.json()["amount"] == 99.99
        assert res.json()["description"] == created["description"]  # unchanged

    def test_updates_description(self, client):
        created = create_one(client)
        res = client.patch(f"/expenses/{created['id']}", json={"description": "Costco"})
        assert res.status_code == 200
        assert res.json()["description"] == "Costco"

# DELETE /expenses/{id}
class TestDeleteExpense:
    def test_deletes_successfully(self, client):
        created = create_one(client)
        res = client.delete(f"/expenses/{created['id']}")
        assert res.status_code == 204

    def test_deleted_expense_is_gone(self, client):
        created = create_one(client)
        client.delete(f"/expenses/{created['id']}")
        res = client.get(f"/expenses/{created['id']}")
        assert res.status_code == 404

    def test_returns_404_for_missing(self, client):
        res = client.delete("/expenses/99999")
        assert res.status_code == 404
