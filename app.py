# app.py
import streamlit as st
from datetime import date, timedelta
from db import init_db, add_appointment, get_appointments, update_status, delete_appointment

# Inicializar base de datos
init_db()

st.set_page_config(page_title="Agenda Fumigaciones Xterminio", layout="wide")

st.title("📅 Agenda Fumigaciones Xterminio")


# =========================
# FORMULARIO NUEVA CITA
# =========================
# =========================
# FORMULARIO NUEVA CITA
# =========================
st.subheader("Nuevo servicio")

# --- Cargar clientes guardados ---
from db import get_clients, add_client

clientes = get_clients()
nombres_clientes = ["-- Cliente nuevo --"] + [c["name"] for c in clientes]

seleccion = st.selectbox("Buscar cliente guardado", nombres_clientes)

cliente_seleccionado = None
if seleccion != "-- Cliente nuevo --":
    for c in clientes:
        if c["name"] == seleccion:
            cliente_seleccionado = c
            break

with st.form("nuevo_servicio", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        client_name = st.text_input(
            "Nombre del cliente / negocio *",
            value=cliente_seleccionado["name"] if cliente_seleccionado else ""
        )
        service_type = st.selectbox(
            "Tipo de servicio",
            ["Casa", "Negocio", "Condominio", "Otro"],
            index=1,
        )
        pest_type = st.text_input("Tipo de plaga (cucaracha, garrapata, termita, etc.)")

    with col2:
        address = st.text_input(
            "Dirección",
            value=cliente_seleccionado["address"] if cliente_seleccionado else ""
        )
        zone = st.text_input(
            "Colonia / zona",
            value=cliente_seleccionado["zone"] if cliente_seleccionado else ""
        )
        phone = st.text_input(
            "Teléfono",
            value=cliente_seleccionado["phone"] if cliente_seleccionado else ""
        )

    with col3:
        service_date = st.date_input("Fecha del servicio", value=date.today())
        service_time = st.time_input("Hora del servicio")
        price = st.number_input("Precio estimado ($)", min_value=0.0, step=50.0)
        status = st.selectbox("Estado", ["Pendiente", "Confirmado", "Realizado", "Cobrado"])

    notes = st.text_area(
        "Notas (referencias, tipo de paquete, observaciones, etc.)",
        value=cliente_seleccionado["notes"] if cliente_seleccionado else ""
    )

    colA, colB = st.columns(2)

    # ---------- BOTÓN GUARDAR CLIENTE ----------
    with colA:
        btn_cliente = st.form_submit_button("🟩 Guardar cliente")
        if btn_cliente:
            if not client_name:
                st.error("El nombre del cliente es obligatorio.")
            else:
                add_client(client_name, address, zone, phone, notes)
                st.success("Cliente guardado correctamente.")
                st.rerun()

    # ---------- BOTÓN GUARDAR SERVICIO ----------
    with colB:
        btn_servicio = st.form_submit_button("🟦 Guardar servicio")
        if btn_servicio:
            if not client_name:
                st.error("El nombre del cliente es obligatorio.")
            else:
                add_appointment(
                    client_name=client_name,
                    service_type=service_type,
                    pest_type=pest_type,
                    address=address,
                    zone=zone,
                    phone=phone,
                    date=str(service_date),
                    time=str(service_time)[:5],
                    price=price if price > 0 else None,
                    status=status,
                    notes=notes,
                )
                st.success("Servicio guardado en la agenda.")
                st.rerun()

# =========================
# FILTROS
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

# Calcular rango de fechas según filtro
hoy = date.today()
date_from = None
date_to = None

if filtro_rango == "Hoy":
    date_from = str(hoy)
    date_to = str(hoy)
elif filtro_rango == "Próximos 7 días":
    date_from = str(hoy)
    date_to = str(hoy + timedelta(days=7))
else:
    date_from = None
    date_to = None

rows = get_appointments(date_from=date_from, date_to=date_to, status=filtro_estado)

if not rows:
    st.info("No hay servicios en la agenda con los filtros seleccionados.")
else:
    # Convertir a lista de diccionarios para mostrar
    data = [
        {
            "ID": r["id"],
            "Fecha": r["date"],
            "Hora": r["time"],
            "Cliente/Negocio": r["client_name"],
            "Servicio": r["service_type"],
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
