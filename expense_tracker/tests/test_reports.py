from datetime import date, timedelta
import pytest

def add_expense(client, description, amount, date_str):
    res = client.post("/expenses", json={
        "description": description,
        "amount": amount,
        "date": date_str,
    })
    assert res.status_code == 201
    return res.json()

# GET /reports/summary 
class TestSummaryReport:
    def test_empty_when_no_expenses(self, client):
        res = client.get("/reports/summary")
        assert res.status_code == 200
        assert res.json() == []

    def test_groups_by_shop(self, client):
        add_expense(client, "Walmart", 10.0, "2026-03-01")
        add_expense(client, "Walmart", 20.0, "2026-03-02")
        add_expense(client, "Target",  15.0, "2026-03-03")

        res = client.get("/reports/summary")
        assert res.status_code == 200

        by_shop = {r["shop"]: r["total"] for r in res.json()}
        assert by_shop["Walmart"] == pytest.approx(30.0)
        assert by_shop["Target"]  == pytest.approx(15.0)

    def test_ordered_by_total_descending(self, client):
        add_expense(client, "Amazon",    100.0, "2026-03-01")
        add_expense(client, "Starbucks",   5.0, "2026-03-02")
        add_expense(client, "Walmart",    50.0, "2026-03-03")

        res = client.get("/reports/summary")
        totals = [r["total"] for r in res.json()]
        assert totals == sorted(totals, reverse=True)

# GET /reports/weekly
class TestWeeklyReport:
    def test_returns_zero_when_no_expenses(self, client):
        res = client.get("/reports/weekly")
        assert res.status_code == 200
        assert res.json()["total"] == 0.0

    def test_includes_expense_from_today(self, client):
        today = date.today().isoformat()
        add_expense(client, "Walmart", 45.50, today)
        res = client.get("/reports/weekly")
        assert res.json()["total"] == pytest.approx(45.50)

    def test_excludes_expense_older_than_7_days(self, client):
        old_date = (date.today() - timedelta(days=8)).isoformat()
        add_expense(client, "OldShop", 100.0, old_date)
        res = client.get("/reports/weekly")
        assert res.json()["total"] == pytest.approx(0.0)

    def test_sums_multiple_expenses_in_window(self, client):
        dates = [(date.today() - timedelta(days=i)).isoformat() for i in range(5)]
        for d in dates:
            add_expense(client, "Shop", 10.0, d)
        res = client.get("/reports/weekly")
        assert res.json()["total"] == pytest.approx(50.0)


# GET /reports/monthly
class TestMonthlyReport:
    def test_returns_correct_total_for_month(self, client):
        add_expense(client, "Walmart", 30.0, "2026-03-10")
        add_expense(client, "Target",  20.0, "2026-03-15")
        add_expense(client, "Amazon",  50.0, "2026-04-01")  # different month

        res = client.get("/reports/monthly?month=3&year=2026")
        assert res.status_code == 200
        assert res.json()["total"] == pytest.approx(50.0)
        assert res.json()["month"] == 3
        assert res.json()["year"]  == 2026

    def test_different_month_excluded(self, client):
        add_expense(client, "Walmart", 100.0, "2026-02-15")
        res = client.get("/reports/monthly?month=3&year=2026")
        assert res.json()["total"] == pytest.approx(0.0)

    def test_rejects_invalid_month(self, client):
        res = client.get("/reports/monthly?month=13&year=2026")
        assert res.status_code == 400

    def test_rejects_month_zero(self, client):
        res = client.get("/reports/monthly?month=0&year=2026")
        assert res.status_code == 400


# GET /reports/yearly
class TestYearlyReport:
    def test_returns_correct_total_for_year(self, client):
        add_expense(client, "Walmart",   50.0, "2026-01-01")
        add_expense(client, "Amazon",   150.0, "2026-06-15")
        add_expense(client, "OldShop", 200.0,  "2025-12-31")  # different year

        res = client.get("/reports/yearly?year=2026")
        assert res.status_code == 200
        assert res.json()["total"] == pytest.approx(200.0)
        assert res.json()["year"]  == 2026

    def test_different_year_excluded(self, client):
        add_expense(client, "Shop", 500.0, "2025-07-01")
        res = client.get("/reports/yearly?year=2026")
        assert res.json()["total"] == pytest.approx(0.0)

    def test_returns_zero_when_no_expenses(self, client):
        res = client.get("/reports/yearly?year=2099")
        assert res.status_code == 200
        assert res.json()["total"] == 0.0
