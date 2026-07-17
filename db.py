"""
Community Builders Network - Sierra Leone
Thin MySQL helper on top of mysql-connector-python.

Uses a very small connection pool so the pure-stdlib HTTP server
doesn't open a new TCP connection on every request.
"""

import mysql.connector
from mysql.connector import pooling, Error as MySQLError

from config import DB_CONFIG

_POOL = None


def init_pool(pool_size: int = 5):
    """Initialise the MySQL connection pool. Safe to call more than once."""
    global _POOL
    if _POOL is not None:
        return _POOL
    _POOL = pooling.MySQLConnectionPool(
        pool_name="cbn_pool",
        pool_size=pool_size,
        pool_reset_session=True,
        **DB_CONFIG,
    )
    return _POOL


def get_connection():
    """Get a pooled connection. Caller must close() it when done."""
    if _POOL is None:
        init_pool()
    return _POOL.get_connection()


# ------------------------------------------------------------------
# Query helpers
# ------------------------------------------------------------------

def query(sql: str, params: tuple = None, one: bool = False):
    """Run a SELECT query and return dict rows (or single row if one=True)."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        if one:
            return rows[0] if rows else None
        return rows
    finally:
        conn.close()


def execute(sql: str, params: tuple = None) -> int:
    """Run INSERT/UPDATE/DELETE. Returns lastrowid for INSERTs, else rowcount."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        result = cur.lastrowid if cur.lastrowid else cur.rowcount
        cur.close()
        return result
    finally:
        conn.close()


def table_is_empty(table: str) -> bool:
    row = query(f"SELECT COUNT(*) AS c FROM `{table}`", one=True)
    return (row or {}).get("c", 0) == 0


def healthcheck() -> bool:
    try:
        row = query("SELECT 1 AS ok", one=True)
        return bool(row and row.get("ok") == 1)
    except MySQLError:
        return False
