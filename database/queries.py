from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            return None
        created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
        return {
            "name": row["name"],
            "email": row["email"],
            "member_since": created_at.strftime("%B %Y"),
        }
    finally:
        conn.close()


def get_summary_stats(user_id):
    conn = get_db()
    try:
        totals = conn.execute(
            "SELECT COUNT(*) AS c, COALESCE(SUM(amount), 0) AS total "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        top = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY total DESC LIMIT 1",
            (user_id,),
        ).fetchone()

        return {
            "total_spent": totals["total"],
            "transaction_count": totals["c"],
            "top_category": top["category"] if top else "—",
        }
    finally:
        conn.close()


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses "
            "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [
            {
                "date": row["date"],
                "description": row["description"],
                "category": row["category"],
                "amount": row["amount"],
            }
            for row in rows
        ]
    finally:
        conn.close()


def get_category_breakdown(user_id):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,),
        ).fetchall()

        if not rows:
            return []

        grand_total = sum(row["total"] for row in rows)
        breakdown = [
            {"name": row["category"], "amount": row["total"], "pct": round(row["total"] / grand_total * 100)}
            for row in rows
        ]

        remainder = 100 - sum(item["pct"] for item in breakdown)
        if remainder != 0:
            breakdown[0]["pct"] = max(0, breakdown[0]["pct"] + remainder)

        return breakdown
    finally:
        conn.close()
