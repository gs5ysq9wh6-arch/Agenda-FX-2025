import sqlite3
from datetime import datetime

DB_NAME = "agenda.db"


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Tabla de servicios
    c.execute("""
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,      -- nombre de contacto
            business_name TEXT,      -- Taquería Sauces
            address TEXT,
            zone TEXT,
            phone TEXT,
            notes TEXT
        );
    """)

    conn.commit()
    conn.close()


# ---------- SERVICIOS ----------

def add_appointment(client_name, service_type, pest_type,
                    address, zone, phone, date, time,
                    price, status, notes):
    conn = get_conn()
    c = conn.cursor()
    created_at = datetime.now().isoformat(timespec="seconds")

    c.execute("""
        INSERT INTO appointments (
            client_name, service_type, pest_type,
            address, zone, phone,
            date, time, price,
            status, notes, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (client_name, service_type, pest_type,
          address, zone, phone,
          date, time, price,
          status, notes, created_at))

    conn.commit()
    conn.close()


def get_appointments(date_from=None, date_to=None, status=None):
    conn = get_conn()
    c = conn.cursor()

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

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows


def update_status(appointment_id, new_status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE appointments SET status=? WHERE id=?",
              (new_status, appointment_id))
    conn.commit()
    conn.close()


def delete_appointment(appointment_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM appointments WHERE id=?",
              (appointment_id,))
    conn.commit()
    conn.close()


# ---------- CLIENTES ----------

def add_client(name, business_name, address, zone, phone, notes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO clients (name, business_name, address, zone, phone, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, business_name, address, zone, phone, notes))
    conn.commit()
    conn.close()


def get_clients():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM clients ORDER BY business_name, name;")
    rows = c.fetchall()
    conn.close()
    return rows
