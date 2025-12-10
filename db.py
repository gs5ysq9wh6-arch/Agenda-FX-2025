import sqlite3
from datetime import datetime

DB_NAME = "agenda.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Tabla de servicios
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            service_type TEXT,
            pest_type TEXT,
            address TEXT,
            zone TEXT,
            phone TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            price REAL,
            status TEXT DEFAULT 'Pendiente',
            notes TEXT,
            created_at TEXT
        );
    """)

    # Tabla de clientes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            business_name TEXT,
            address TEXT,
            zone TEXT,
            phone TEXT,
            notes TEXT
        );
    """)

    conn.commit()
    conn.close()
    # ---------------------------
# APPOINTMENTS (SERVICIOS)
# ---------------------------

def add_appointment(client_name, service_type, pest_type, address, zone, phone, date, time, price, status, notes):
    conn = get_connection()
    cur = conn.cursor()
    created_at = datetime.now().isoformat(timespec="seconds")

    cur.execute("""
        INSERT INTO appointments (
            client_name, service_type, pest_type,
            address, zone, phone,
            date, time, price,
            status, notes, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (client_name, service_type, pest_type, address, zone, phone, date, time, price, status, notes, created_at))

    conn.commit()
    conn.close()


def get_appointments(date_from=None, date_to=None, status=None):
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM appointments WHERE 1=1"
    params = []

    if date_from:
        query += " AND date >= ?"
        params.append(date_from)

    if date_to:
        query += " AND date <= ?"
        params.append(date_to)

    if status and status != "Todos":
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY date, time"

    cur.execute(query, params)
    rows = cur.fetchall()

    conn.close()
    return rows


def update_status(appointment_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status = ? WHERE id = ?", (new_status, appointment_id))
    conn.commit()
    conn.close()


def delete_appointment(appointment_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    # ---------------------------
# CLIENTES
# ---------------------------

def add_client(name, business_name, address, zone, phone, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clients (name, business_name, address, zone, phone, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, business_name, address, zone, phone, notes))
    conn.commit()
    conn.close()


def get_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_client_by_id(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row


def delete_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
