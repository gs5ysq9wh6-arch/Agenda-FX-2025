import streamlit as st
from datetime import date, timedelta

from db import (
    init_db,
    add_appointment,
    get_appointments,
    update_status,
    delete_appointment,
    add_client,
    get_clients,
    get_client_by_id,
    delete_client,
)

# Inicializar DB
init_db()

st.set_page_config(page_title="Agenda Fumigaciones Xterminio", layout="wide")

st.title("📅 Agenda Fumigaciones Xterminio")

# Tabs
tab_agenda, tab_clientes = st.tabs(["Agenda", "Clientes"])

# -------------------------
# TAB AGENDA
# -------------------------
with tab_agenda:
    st.subheader("Nuevo servicio")

    clients = get_clients()

    client_labels = ["-- Cliente nuevo --"] + [
        f"{c['name']} ({c['business_name']})" if c["business_name"] else c["name"]
        for c in clients
    ]
    client_ids = [None] + [c["id"] for c in clients]

    selected_label = st.selectbox("Cliente guardado:", client_labels)
    selected_client_id = client_ids[client_labels.index(selected_label)]
    selected_client = get_client_by_id(selected_client_id) if selected_client_id else None

    with st.form("nuevo_servicio", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            client_name = st.text_input(
                "Nombre del cliente",
                value=selected_client["name"] if selected_client else "",
            )
            service_type = st.selectbox("Tipo de servicio", ["Casa", "Negocio", "Condominio", "Otro"])
            pest_type = st.text_input("Tipo de plaga")

        with col2:
            address = st.text_input(
                "Dirección",
                value=selected_client["address"] if selected_client else "",
            )
            zone = st.text_input(
                "Zona",
                value=selected_client["zone"] if selected_client else "",
            )
            phone = st.text_input(
                "Teléfono",
                value=selected_client["phone"] if selected_client else "",
            )

        with col3:
            service_date = st.date_input("Fecha", value=date.today())
            service_time = st.time_input("Hora")
            price = st.number_input("Precio ($)", min_value=0.0, step=50.0)
            status = st.selectbox("Estado", ["Pendiente", "Confirmado", "Realizado", "Cobrado"])

        notes = st.text_area("Notas")

        submit = st.form_submit_button("Guardar servicio")

        if submit:
            add_appointment(
                client_name,
                service_type,
                pest_type,
                address,
                zone,
                phone,
                str(service_date),
                str(service_time)[:5],
                price,
                status,
                notes,
            )
            st.success("Servicio guardado.")
            st.rerun()

    st.subheader("Servicios")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        rango = st.selectbox("Rango", ["Hoy", "Próximos 7 días", "Todos"], index=1)
    with col_b:
        estado = st.selectbox("Estado", ["Todos", "Pendiente", "Confirmado", "Realizado", "Cobrado"])

    today = date.today()
    date_from, date_to = None, None

    if rango == "Hoy":
        date_from = str(today)
        date_to = str(today)
    elif rango == "Próximos 7 días":
        date_from = str(today)
        date_to = str(today + timedelta(days=7))

    rows = get_appointments(date_from=date_from, date_to=date_to, status=estado)

    if not rows:
        st.info("No hay servicios.")
    else:
        st.dataframe(rows)

        st.subheader("Actualizar / Eliminar")

        ids = [r["id"] for r in rows]
        selected_id = st.selectbox("ID del servicio", ids)

        col_u, col_d = st.columns(2)

        with col_u:
            new_status = st.selectbox("Nuevo estado", ["Pendiente", "Confirmado", "Realizado", "Cobrado"])
            if st.button("Actualizar estado"):
                update_status(selected_id, new_status)
                st.success("Actualizado.")
                st.rerun()

        with col_d:
            if st.button("Eliminar servicio"):
                delete_appointment(selected_id)
                st.warning("Servicio eliminado.")
                st.rerun()

# -------------------------
# TAB CLIENTES
# -------------------------
with tab_clientes:
    st.subheader("Registro de clientes")

    with st.form("form_clientes", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Nombre *")
            business_name = st.text_input("Negocio")

        with col2:
            phone = st.text_input("Teléfono")
            zone = st.text_input("Zona")
            address = st.text_input("Dirección")

        notes_c = st.text_area("Notas del cliente")

        submit_c = st.form_submit_button("Guardar cliente")

        if submit_c:
            add_client(name, business_name, address, zone, phone, notes_c)
            st.success("Cliente guardado.")
            st.rerun()

    st.subheader("Clientes registrados")

    rows = get_clients()

    if not rows:
        st.info("No hay clientes.")
    else:
        st.dataframe(rows)

        st.subheader("Eliminar cliente")

        client_ids = [c["id"] for c in rows]
        selected_client_id = st.selectbox("ID del cliente", client_ids)

        if st.button("Eliminar cliente"):
            delete_client(selected_client_id)
            st.warning("Cliente eliminado.")
            st.rerun()
