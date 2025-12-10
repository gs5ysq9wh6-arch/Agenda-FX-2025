import sqlite3
from datetime import datetime

DB_NAME = "agenda.db"


def sql():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sql()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            service_type TEXT,
            pest_type TEXT,
            address TEXT,
            zone TEXT,
            phone TEXT,
            date TEXT,
            time TEXT,
            price REAL,
            status TEXT,
            notes TEXT,
            created_at TEXT
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            business_name TEXT,
            address TEXT,
            zone TEXT,
            phone TEXT,
            notes TEXT
        );
    """)

    conn.commit()
    conn.close()


# --------- APPOINTMENTS ---------

def add_appointment(n, s, p, a, z, t, d, h, pr, st, no):
    conn = sql()
    c = conn.cursor()
    c.execute("""
        INSERT INTO appointments (
            client_name, service_type, pest_type, address, zone, phone,
            date, time, price, status, notes, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (n, s, p, a, z, t, d, h, pr, st, no, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_appointments():
    conn = sql()
    rows = conn.execute("SELECT * FROM appointments ORDER BY date, time").fetchall()
    conn.close()
    return rows


def update_status(id_, st):
    conn = sql()
    conn.execute("UPDATE appointments SET status=? WHERE id=?", (st, id_))
    conn.commit()
    conn.close()


def delete_appointment(id_):
    conn = sql()
    conn.execute("DELETE FROM appointments WHERE id=?", (id_,))
    conn.commit()
    conn.close()


# --------- CLIENTES ---------

def add_client(n, b, a, z, t, no):
    conn = sql()
    conn.execute("""
        INSERT INTO clients (name, business_name, address, zone, phone, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (n, b, a, z, t, no))
    conn.commit()
    conn.close()


def get_clients():
    conn = sql()
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return rows


def delete_client(id_):
    conn = sql()
    conn.execute("DELETE FROM clients WHERE id=?", (id_,))
    conn.commit()
    conn.close()
