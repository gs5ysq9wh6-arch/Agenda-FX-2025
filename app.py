import sqlite3
from datetime import date, timedelta, datetime as dt

import streamlit as st

# =========================
# CONFIG DB
# =========================
DB_NAME = "agenda.db"


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Tabla de clientes
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            business_name TEXT,
            address TEXT,
            zone TEXT,
            phone TEXT,
            notes TEXT,
            is_monthly INTEGER DEFAULT 0,
            monthly_day INTEGER
        );
    """)

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
            status TEXT,
            notes TEXT,
            created_at TEXT
        );
    """)

    conn.commit()
    conn.close()


# ---------- FUNCIONES DB ----------

def add_client(name, business_name, address, zone, phone, notes,
               is_monthly=False, monthly_day=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO clients (
            name, business_name, address, zone, phone, notes,
            is_monthly, monthly_day
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        business_name,
        address,
        zone,
        phone,
        notes,
        1 if is_monthly else 0,
        monthly_day,
    ))
    conn.commit()
    conn.close()


def get_clients():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM clients ORDER BY business_name, name;")
    rows = c.fetchall()
    conn.close()
    return rows


def add_appointment(client_name, service_type, pest_type,
                    address, zone, phone, fecha, hora,
                    price, status, notes):
    conn = get_conn()
    c = conn.cursor()
    created_at = dt.now().isoformat(timespec="seconds")

    c.execute("""
        INSERT INTO appointments (
            client_name, service_type, pest_type,
            address, zone, phone,
            date, time, price,
            status, notes, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client_name,
        service_type,
        pest_type,
        address,
        zone,
        phone,
        fecha,
        hora,
        price,
        status,
        notes,
        created_at,
    ))
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
    c.execute(
        "UPDATE appointments SET status = ? WHERE id = ?",
        (new_status, appointment_id),
    )
    conn.commit()
    conn.close()


def delete_appointment(appointment_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()


# =========================
# INICIO APP
# =========================
init_db()

st.set_page_config(page_title="Agenda FX 2025", layout="wide")
st.title("📅 Agenda Fumigaciones Xterminio")

hoy = date.today()
dia_hoy = hoy.day

# =========================
# AVISO CLIENTES MENSUALES
# =========================
clientes = get_clients()
mensuales_hoy = [
    c for c in clientes
    if c["is_monthly"] == 1 and c["monthly_day"] == dia_hoy
]

if mensuales_hoy:
    nombres = [
        (c["business_name"] or c["name"])
        for c in mensuales_hoy
    ]
    st.warning(
        "🔔 Clientes mensuales para HOY (día {}):\n\n- ".format(dia_hoy)
        + "\n- ".join(nombres)
    )

# =========================
# FORMULARIO CLIENTE + SERVICIO
# =========================
st.subheader("Nuevo servicio / Guardar cliente y agendar")

# Lista de clientes guardados
opciones = ["-- Cliente nuevo --"]
mapa_clientes = {}
for c in clientes:
    etiqueta = c["business_name"] or c["name"]
    if c["business_name"] and c["name"]:
        etiqueta = f"{c['business_name']} ({c['name']})"
    opciones.append(etiqueta)
    mapa_clientes[etiqueta] = c

# 🔍 Buscar cliente
seleccion = st.selectbox("Buscar cliente", opciones)
cliente_sel = mapa_clientes.get(seleccion)

with st.form("form_servicio_cliente", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    # -------- DATOS DEL CLIENTE --------
    with col1:
        name = st.text_input(
            "Nombre de la persona / contacto",
            value=cliente_sel["name"] if cliente_sel else "",
        )
        business_name = st.text_input(
            "Nombre del negocio",
            value=cliente_sel["business_name"] if cliente_sel else "",
        )

    with col2:
        phone = st.text_input(
            "Teléfono",
            value=cliente_sel["phone"] if cliente_sel else "",
        )
        zone = st.text_input(
            "Colonia / zona",
            value=cliente_sel["zone"] if cliente_sel else "",
        )
        address = st.text_input(
            "Dirección",
            value=cliente_sel["address"] if cliente_sel else "",
        )

    with col3:
        # -------- DATOS DEL SERVICIO --------
        service_date = st.date_input("Fecha del servicio", value=hoy)
        service_time = st.time_input("Hora del servicio")
        price = st.number_input("Precio del servicio ($)", min_value=0.0, step=50.0)
        status = st.selectbox(
            "Estado del servicio",
            ["Pendiente", "Confirmado", "Realizado", "Cobrado"],
        )

    # Estos siempre empiezan en blanco aunque el cliente exista
    pest_type = st.text_input("Tipo de plaga (cucaracha, garrapata, termita, etc.)")
    notes = st.text_area("Notas (referencias, paquete, observaciones, etc.)")

    # Cliente mensual
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if cliente_sel:
            is_monthly = st.checkbox(
                "Cliente con servicio mensual",
                value=bool(cliente_sel["is_monthly"]),
            )
        else:
            is_monthly = st.checkbox("Cliente con servicio mensual", value=False)

    with col_m2:
        monthly_day = None
        if is_monthly:
            monthly_day = st.number_input(
                "Día del mes para servicio mensual (1-31)",
                min_value=1,
                max_value=31,
                value=(
                    cliente_sel["monthly_day"]
                    if cliente_sel and cliente_sel["monthly_day"]
                    else dia_hoy
                ),
            )

    # ---------- ÚNICO BOTÓN: GUARDAR CLIENTE Y AGENDAR SERVICIO ----------
    guardar_cliente_servicio = st.form_submit_button("🟩 Guardar cliente y agendar servicio")

    if guardar_cliente_servicio:
        if not name and not business_name:
            st.error("Pon al menos el nombre de la persona o del negocio.")
        else:
            # Si es cliente NUEVO (no seleccionado en "Buscar cliente") → guardar cliente
            if seleccion == "-- Cliente nuevo --":
                add_client(
                    name=name or (business_name or "Cliente sin nombre"),
                    business_name=business_name,
                    address=address,
                    zone=zone,
                    phone=phone,
                    notes=notes,
                    is_monthly=is_monthly,
                    monthly_day=monthly_day if is_monthly else None,
                )

            # Siempre agendar el servicio
            nombre_mostrar = business_name or name
            add_appointment(
                client_name=nombre_mostrar,
                service_type="Negocio" if business_name else "Casa",
                pest_type=pest_type,
                address=address,
                zone=zone,
                phone=phone,
                fecha=str(service_date),
                hora=str(service_time)[:5],
                price=price if price > 0 else None,
                status=status,
                notes=notes,
            )

            st.success(
                "✅ Servicio agendado."
                + (" Cliente guardado." if seleccion == "-- Cliente nuevo --" else "")
            )
            st.rerun()

# =========================
# TABLA CLIENTES MENSUALES
# =========================
st.subheader("Clientes mensuales")

clientes = get_clients()
mensuales = [c for c in clientes if c["is_monthly"] == 1]

if not mensuales:
    st.info("Aún no tienes clientes marcados como mensuales.")
else:
    tabla_clientes = [
        {
            "ID": c["id"],
            "Negocio": c["business_name"],
            "Contacto": c["name"],
            "Teléfono": c["phone"],
            "Zona": c["zone"],
            "Día mensual": c["monthly_day"],
            "Notas": c["notes"],
        }
        for c in mensuales
    ]
    st.dataframe(tabla_clientes, use_container_width=True)

# =========================
# SERVICIOS AGENDADOS
# =========================
st.subheader("Servicios agendados")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    filtro_rango = st.selectbox(
        "Rango de fechas",
        ["Hoy", "Próximos 7 días", "Todos"],
        index=1,
    )

with col_f2:
    filtro_estado = st.selectbox(
        "Estado",
        ["Todos", "Pendiente", "Confirmado", "Realizado", "Cobrado"],
        index=0,
    )

with col_f3:
    st.write("")  # espacio
    st.write("")

date_from = None
date_to = None

if filtro_rango == "Hoy":
    date_from = str(hoy)
    date_to = str(hoy)
elif filtro_rango == "Próximos 7 días":
    date_from = str(hoy)
    date_to = str(hoy + timedelta(days=7))

rows = get_appointments(date_from=date_from, date_to=date_to, status=filtro_estado)

if not rows:
    st.info("No hay servicios con los filtros seleccionados.")
else:
    data = [
        {
            "ID": r["id"],
            "Fecha": r["date"],
            "Hora": r["time"],
            "Cliente/Negocio": r["client_name"],
            "Plaga": r["pest_type"],
            "Zona": r["zone"],
            "Teléfono": r["phone"],
            "Precio": r["price"],
            "Estado": r["status"],
            "Notas": r["notes"],
        }
        for r in rows
    ]

    st.dataframe(data, use_container_width=True)

    st.markdown("---")
    st.subheader("Actualizar / eliminar servicio")

    ids = [r["id"] for r in rows]

    col_a, col_b = st.columns(2)

    with col_a:
        selected_id = st.selectbox("Selecciona el ID", ids)
        new_status = st.selectbox(
            "Nuevo estado",
            ["Pendiente", "Confirmado", "Realizado", "Cobrado"],
        )

        if st.button("Actualizar estado"):
            update_status(selected_id, new_status)
            st.success("✅ Estado actualizado.")
            st.rerun()

    with col_b:
        st.write("")
        st.write("")
        if st.button("🗑️ Eliminar servicio"):
            delete_appointment(selected_id)
            st.warning("Servicio eliminado.")
            st.rerun()
