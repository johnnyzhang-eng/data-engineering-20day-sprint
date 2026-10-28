#!/usr/bin/env python3
"""Rebuild the synthetic SQL practice database using only the standard library.

Run from any directory: python3 /path/to/exercises/sql/data/build_db.py
The existing practice.sqlite3 is replaced only after validation succeeds.
All dates, prices (whole yuan), row order and randomness are fixed. Rebuilding
with the same Python/SQLite runtime produces the same database bytes.
No exercise answers, personal information or external data are included.
"""

from bisect import bisect_right
from contextlib import closing
from datetime import date, datetime, time, timedelta
import hashlib
from pathlib import Path
import random
import sqlite3
import tempfile


SEED = 20261028
DB_PATH = Path(__file__).resolve().with_name("practice.sqlite3")
DAY_ZERO = date(2026, 7, 1)
LAST_DAY = date(2026, 10, 27)
USER_COUNT = 2_000
ORDER_COUNT = 20_000
PRODUCT_COUNT = 200
LOGIN_COUNT = 30_000

SMALL_USERS = [
    (1, "小林", "上海", "app"),
    (2, "小周", "北京", "web"),
    (3, "阿青", "深圳", "app"),
    (4, "阿雨", None, "wechat"),
    (5, "阿明", "杭州", "web"),
    (6, "小陈", "上海", "app"),
    (7, "阿宁", "武汉", None),
    (8, "小苏", "深圳", "wechat"),
    (9, "小方", "北京", "app"),
    (10, "小禾", "成都", "web"),
]
SMALL_ORDERS = [
    (101, 1, "上海", 100, "2026-10-01", "paid"),
    (102, 2, "北京", 200, "2026-10-01", "paid"),
    (103, 1, "上海", 50, "2026-10-02", "cancelled"),
    (104, 3, "深圳", 100, "2026-10-03", "paid"),
    (105, 4, None, 150, "2026-10-03", "paid"),
    (106, 2, "北京", None, "2026-10-04", "pending"),
    (107, 5, "杭州", 0, "2026-10-04", "paid"),
    (108, 6, "上海", 300, "2026-10-05", "refunded"),
    (109, 7, "武汉", None, "2026-10-05", "paid"),
    (110, 8, "深圳", 200, "2026-10-06", "paid"),
    (111, 9, None, 100, "2026-10-06", "cancelled"),
    (112, 99, "北京", 50, "2026-10-07", "paid"),
]

SCHEMA = """
CREATE TABLE s_users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT,
    channel TEXT
);
-- No small-table foreign key: user 99 deliberately has no s_users record.
CREATE TABLE s_orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    city TEXT,
    amount INTEGER CHECK (amount >= 0),
    order_date TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    city TEXT,
    register_date TEXT NOT NULL,
    channel TEXT
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price > 0)
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    order_time TEXT NOT NULL,
    amount INTEGER CHECK (amount >= 0),
    status TEXT NOT NULL CHECK (
        status IN ('paid', 'completed', 'pending', 'cancelled', 'refunded')
    ),
    channel TEXT
);
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    qty INTEGER NOT NULL CHECK (qty > 0),
    price INTEGER NOT NULL CHECK (price > 0),
    PRIMARY KEY (order_id, product_id)
);
CREATE TABLE logins (
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    login_date TEXT NOT NULL,
    PRIMARY KEY (user_id, login_date)
);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_time ON orders(order_time);
"""


def cumulative(weights):
    """Build cumulative weights once for repeated weighted draws."""
    result = []
    total = 0.0
    for weight in weights:
        total += weight
        result.append(total)
    return result


def draw_index(rng, cumulative_weights):
    return bisect_right(
        cumulative_weights, rng.random() * cumulative_weights[-1]
    )


def insert_data(conn):
    rng = random.Random(SEED)
    conn.executemany("INSERT INTO s_users VALUES (?, ?, ?, ?)", SMALL_USERS)
    conn.executemany(
        "INSERT INTO s_orders VALUES (?, ?, ?, ?, ?, ?)", SMALL_ORDERS
    )

    cities = ["上海", "北京", "深圳", "杭州", "广州", "成都", "武汉", "南京"]
    channels = ["app", "web", "wechat"]
    city_weights = [22, 20, 15, 12, 11, 8, 7, 5]
    channel_weights = [60, 25, 15]
    users = []
    activity_weights = []
    for user_id in range(1, USER_COUNT + 1):
        city = rng.choices(cities, weights=city_weights)[0]
        channel = rng.choices(channels, weights=channel_weights)[0]
        registered = date(2026, 1, 1) + timedelta(days=rng.randrange(181))
        if rng.random() < 0.02:
            city = None
        if rng.random() < 0.015:
            channel = None
        users.append((user_id, city, registered.isoformat(), channel))
        activity_weights.append(rng.lognormvariate(0.0, 0.9))
    conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users)
    activity_cumulative = cumulative(activity_weights)

    categories = ["日用", "食品", "服饰", "数码配件", "家居"]
    category_prices = {
        "日用": [9, 19, 29, 39, 49],
        "食品": [9, 19, 29, 49, 69],
        "服饰": [49, 99, 149, 199, 299],
        "数码配件": [29, 49, 99, 199, 299],
        "家居": [39, 69, 99, 199, 399],
    }
    products = []
    for product_id in range(1, PRODUCT_COUNT + 1):
        category = rng.choices(categories, weights=[30, 25, 20, 15, 10])[0]
        price = rng.choices(category_prices[category], weights=[20, 35, 25, 15, 5])[0]
        products.append((product_id, category, price))
    conn.executemany("INSERT INTO products VALUES (?, ?, ?)", products)
    product_prices = {product_id: price for product_id, _, price in products}

    days = [DAY_ZERO + timedelta(days=i) for i in range((LAST_DAY - DAY_ZERO).days + 1)]
    day_weights = []
    for index, day in enumerate(days):
        weight = 1.0 + 0.35 * index / (len(days) - 1)
        if day.weekday() >= 5:
            weight *= 1.25
        if date(2026, 10, 1) <= day <= date(2026, 10, 7):
            weight *= 1.35
        day_weights.append(weight)
    day_cumulative = cumulative(day_weights)
    orders = []
    items = []
    product_ids = list(range(1, PRODUCT_COUNT + 1))
    for order_id in range(1, ORDER_COUNT + 1):
        user_id = draw_index(rng, activity_cumulative) + 1
        day = days[draw_index(rng, day_cumulative)]
        hour = rng.choices(
            list(range(24)),
            weights=[1, 1, 1, 1, 1, 2, 3, 5, 7, 8, 9, 9, 10, 9, 9, 8, 8, 9, 12, 15, 16, 14, 8, 4],
        )[0]
        ordered_at = datetime.combine(
            day, time(hour, rng.randrange(60), rng.randrange(60))
        ).isoformat(sep=" ")
        item_count = rng.choices([1, 2, 3, 4], weights=[55, 28, 12, 5])[0]
        amount = 0
        for product_id in rng.sample(product_ids, item_count):
            qty = rng.choices([1, 2, 3], weights=[80, 17, 3])[0]
            price = product_prices[product_id]
            amount += qty * price
            items.append((order_id, product_id, qty, price))
        status = rng.choices(
            ["paid", "completed", "pending", "cancelled", "refunded"],
            weights=[48, 30, 8, 8, 6],
        )[0]
        channel = rng.choices(channels, weights=channel_weights)[0]
        if rng.random() < 0.01:
            amount = None
        if rng.random() < 0.015:
            channel = None
        orders.append((order_id, user_id, ordered_at, amount, status, channel))
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders)
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", items)

    # Explicit runs ensure that future consecutive-login tasks are meaningful.
    # The set models one distinct login day per user, not raw login events.
    login_pairs = set()
    for user_id in range(1, 51):
        start = rng.randrange(len(days) - 6)
        for offset in range(7):
            login_pairs.add((user_id, days[start + offset].isoformat()))
    while len(login_pairs) < LOGIN_COUNT:
        user_id = draw_index(rng, activity_cumulative) + 1
        day = days[draw_index(rng, day_cumulative)]
        login_pairs.add((user_id, day.isoformat()))
    conn.executemany("INSERT INTO logins VALUES (?, ?)", sorted(login_pairs))


def validate(conn):
    expected = {
        "s_orders": 12,
        "s_users": 10,
        "users": USER_COUNT,
        "orders": ORDER_COUNT,
        "products": PRODUCT_COUNT,
        "logins": LOGIN_COUNT,
    }
    counts = {}
    for table in ["s_orders", "s_users", "users", "orders", "products", "order_items", "logins"]:
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    for table, count in expected.items():
        assert counts[table] == count, (table, counts[table], count)
    assert conn.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    assert not conn.execute("PRAGMA foreign_key_check").fetchall()
    mismatches = conn.execute("""
        SELECT COUNT(*) FROM orders AS o
        JOIN (SELECT order_id, SUM(qty * price) AS total
              FROM order_items GROUP BY order_id) AS i USING (order_id)
        WHERE o.amount IS NOT NULL AND o.amount <> i.total
    """).fetchone()[0]
    assert mismatches == 0
    assert conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT order_id FROM order_items
            GROUP BY order_id HAVING COUNT(*) NOT BETWEEN 1 AND 4
        )
    """).fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(DISTINCT order_id) FROM order_items").fetchone()[0] == ORDER_COUNT
    assert conn.execute("SELECT COUNT(*) FROM orders WHERE amount IS NULL").fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM orders WHERE channel IS NULL").fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM users WHERE city IS NULL").fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM users WHERE channel IS NULL").fetchone()[0] > 0
    assert conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT amount FROM orders WHERE amount IS NOT NULL
            GROUP BY amount HAVING COUNT(*) > 1
        )
    """).fetchone()[0] > 0
    # This query actually executes a window function, not merely a version test.
    window_rows = conn.execute("""
        SELECT order_id, ROW_NUMBER() OVER (ORDER BY order_id) AS rn
        FROM s_orders ORDER BY order_id LIMIT 3
    """).fetchall()
    assert window_rows == [(101, 1), (102, 2), (103, 3)]
    consecutive_users = conn.execute("""
        WITH numbered AS (
            SELECT user_id, login_date,
                   julianday(login_date)
                   - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS run_key
            FROM logins
        ), runs AS (
            SELECT user_id, COUNT(*) AS days_in_run
            FROM numbered GROUP BY user_id, run_key HAVING COUNT(*) >= 7
        )
        SELECT COUNT(DISTINCT user_id) FROM runs
    """).fetchone()[0]
    assert consecutive_users >= 50
    return counts, consecutive_users


def main():
    # A fresh file avoids carrying over old tables, answers, or page contents.
    handle = tempfile.NamedTemporaryFile(
        prefix=".practice-", suffix=".sqlite3", dir=DB_PATH.parent, delete=False
    )
    temporary_path = Path(handle.name)
    handle.close()
    try:
        with closing(sqlite3.connect(temporary_path)) as conn:
            conn.execute("PRAGMA page_size = 4096")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(SCHEMA)
            insert_data(conn)
            counts, consecutive_users = validate(conn)
            conn.commit()
        temporary_path.replace(DB_PATH)
    finally:
        temporary_path.unlink(missing_ok=True)
    digest = hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
    print(f"Database: {DB_PATH}")
    print(f"Seed: {SEED}")
    print(f"SQLite runtime: {sqlite3.sqlite_version}")
    print("Window functions: PASS (ROW_NUMBER executed)")
    for table, count in counts.items():
        print(f"{table}: {count}")
    print(f"Users with >= 7 consecutive login days: {consecutive_users}")
    print("Integrity / foreign keys / known order amounts / boundaries: PASS")
    print(f"SHA256: {digest}")


if __name__ == "__main__":
    main()
