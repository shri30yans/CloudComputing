import json
import os.path
import sqlite3


# Optimizations:
# Removed temp and final cart lists for a single list
# Using JSON instead of eval

def connect(path):
    exists = os.path.exists(path)
    __conn = sqlite3.connect(path)
    if not exists:
        create_tables(__conn)
    __conn.row_factory = sqlite3.Row
    return __conn


def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            contents TEXT,
            cost REAL
        )
    ''')
    conn.commit()


def get_cart(username: str) -> list:
    conn = connect('carts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM carts WHERE username = ?', (username,))
    cart = cursor.fetchall()
    return [dict(row) for row in cart]

def add_to_cart(username: str, product_id: int):
    conn = connect('carts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT contents FROM carts WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row and row['contents']:
        try:
            contents = json.loads(row['contents'])
        except json.JSONDecodeError:
            contents = []
    else:
        contents = []
    contents.append(product_id)
    cursor.execute('INSERT OR REPLACE INTO carts (username, contents, cost) VALUES (?, ?, ?)',
                    (username, json.dumps(contents), 0))
    conn.commit()
    conn.close()

def remove_from_cart(username: str, product_id: int):
    conn = connect('carts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT contents FROM carts WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        contents = json.loads(row['contents'])
        contents.remove(product_id)
        cursor.execute('INSERT OR REPLACE INTO carts (username, contents, cost) VALUES (?, ?, ?)',
                        (username, json.dumps(contents), 0))
        conn.commit()

def delete_cart(username: str):
    conn = connect('carts.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM carts WHERE username = ?', (username,))
    conn.commit()
