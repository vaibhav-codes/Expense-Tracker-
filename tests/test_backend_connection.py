from database.db import create_user
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown,
)


def _make_user(name="Test User", email="test@example.com"):
    return create_user(name, email, "password123")


def _add_expenses(conn_factory, user_id, expenses):
    from database.db import get_db

    conn = get_db()
    try:
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            [(user_id, amount, category, date, description) for amount, category, date, description in expenses],
        )
        conn.commit()
    finally:
        conn.close()


SAMPLE_EXPENSES = [
    (10.00, "Food", "2026-01-01", "Groceries"),
    (20.00, "Transport", "2026-01-02", "Bus fare"),
    (30.00, "Bills", "2026-01-03", "Electricity"),
]


# --- Unit tests: get_user_by_id ---

def test_get_user_by_id_valid(temp_db):
    user_id = _make_user()
    result = get_user_by_id(user_id)
    assert result["name"] == "Test User"
    assert result["email"] == "test@example.com"
    assert result["member_since"]


def test_get_user_by_id_missing(temp_db):
    assert get_user_by_id(99999) is None


# --- Unit tests: get_summary_stats ---

def test_get_summary_stats_with_expenses(temp_db):
    user_id = _make_user()
    _add_expenses(None, user_id, SAMPLE_EXPENSES)

    stats = get_summary_stats(user_id)
    assert stats["total_spent"] == 60.00
    assert stats["transaction_count"] == 3
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(temp_db):
    user_id = _make_user()
    stats = get_summary_stats(user_id)
    assert stats == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


# --- Unit tests: get_recent_transactions ---

def test_get_recent_transactions_ordered(temp_db):
    user_id = _make_user()
    _add_expenses(None, user_id, SAMPLE_EXPENSES)

    txs = get_recent_transactions(user_id)
    assert len(txs) == 3
    assert txs[0]["date"] == "2026-01-03"
    assert txs[-1]["date"] == "2026-01-01"


def test_get_recent_transactions_empty(temp_db):
    user_id = _make_user()
    assert get_recent_transactions(user_id) == []


# --- Unit tests: get_category_breakdown ---

def test_get_category_breakdown_percentages_sum_to_100(temp_db):
    user_id = _make_user()
    _add_expenses(None, user_id, SAMPLE_EXPENSES)

    breakdown = get_category_breakdown(user_id)
    assert len(breakdown) == 3
    assert sum(item["pct"] for item in breakdown) == 100
    assert all(isinstance(item["pct"], int) for item in breakdown)


def test_get_category_breakdown_empty(temp_db):
    user_id = _make_user()
    assert get_category_breakdown(user_id) == []


# --- Route tests ---

def test_profile_redirects_when_unauthenticated(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_shows_seeded_demo_user(client, temp_db):
    from database.db import seed_db

    seed_db()

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    assert response.status_code == 200

    body = response.get_data(as_text=True)
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
    assert "₹263.65" in body

    stats = get_summary_stats(1)
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"

    breakdown = get_category_breakdown(1)
    assert len(breakdown) == 7


def test_profile_new_user_no_expenses(client, temp_db):
    user_id = _make_user(name="Fresh User", email="fresh@example.com")

    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Fresh User"

    response = client.get("/profile")
    assert response.status_code == 200

    body = response.get_data(as_text=True)
    assert "₹0.00" in body
