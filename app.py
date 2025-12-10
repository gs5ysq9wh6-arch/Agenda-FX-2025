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

# Inicializar base de datos
init_db()

st.set_page_config(page_title="Agenda Fumigaciones Xterminio", layout="wide")

st.title("📅 Agenda Fumigaciones Xterminio")

# Dos pestañas: Agenda y Clientes
tab_agenda, tab_clientes = st.tabs(["Agenda", "Clientes"])


# =========================
# TAB: AGENDA
# =========================
with tab_agenda:
    st.subheader("Nuevo servicio")

    # Lista de clientes guardados
    clients = get_clients()
    client_options = ["-- Ninguno (cliente nuevo) --"] + [
        f"{c['name']} - {c['business_name']}" if c["business_name"] else c["name"]
        for c in clients
    ]
    client_ids = [None] + [c["id"] for c in clients]

    selected_client_option = st.selectbox("Cliente guardado (opcional)", client_options)
    selected_client_id = client_ids[client_options.index(selected_client_option)]

    selected_client = None
    if selected_client_id is not None:
        selected_client = get_client_by_id(selected_client_id)
        with st.expander("Datos del cliente seleccionado"):
            st.write(f"**Nombre:** {selected_client['name']}")
            if selected_client["business_name"]:
                st.write(f"**Negocio:** {selected_client['business_name']}")
            if selected_client["address"]:
                st.write(f"**Dirección:** {selected_client['address']}")
            if selected_client["zone"]:
                st.write(f"**Zona:** {selected_client['zone']}")
            if selected_client["phone"]:
                st.write(f"**Teléfono:** {selected_client['phone']}")
            if selected_client["notes"]:
                st.write(f"**Notas:** {selected_client['notes']}")

    # Formulario para nueva cita
    with st.form("nuevo_servicio", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            client_name = st.text_input(
                "Nombre del cliente / negocio *",
                value=selected_client["name"] if selected_client else "",
            )
            service_type = st.selectbox(
                "Tipo de servicio",
                ["Casa", "Negocio", "Condominio", "Otro"],
                index=1,
            )
            pest_type = st.text_input(
                "Tipo de plaga (cucaracha, garrapata, termita, etc.)"
            )

        with col2:
            address = st.text_input(
                "Dirección",
                value=selected_client["address"] if selected_client else "",
            )
            zone = st.text_input(
                "Colonia / zona",
                value=selected_client["zone"] if selected_client else "",
            )
            phone = st.text_input(
                "Teléfono",
                value=selected_client["phone"] if selected_client else "",
            )

        with col3:
            service_date = st.date_input("Fecha del servicio", value=date.today())
            service_time = st.time_input("Hora del servicio")
            price = st.number_input("Precio estimado ($)", min_value=0.0, step=50.0)
            status = st.selectbox(
                "Estado",
                ["Pendiente", "Confirmado", "Realizado", "Cobrado"],
            )

        notes = st.text_area("Notas (referencias, tipo de paquete, observaciones, etc.)")

        submitted = st.form_submit_button("Guardar servicio")

        if submitted:
            if not client_name:
                st.error("El nombre del cliente / negocio es obligatorio.")
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
                st.success("✅ Servicio guardado en la agenda.")
                st.rerun()

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
        st.write("")
        st.write("")

    hoy = date.today()
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
        st.info("No hay servicios en la agenda con los filtros seleccionados.")
    else:
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


# =========================
# TAB: CLIENTES
# =========================
with tab_clientes:
    st.subheader("Registro de clientes")

    with st.form("nuevo_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Nombre de la persona *")
            business_name = st.text_input("Nombre del negocio (opcional)")

        with col2:
            phone = st.text_input("Teléfono")
            zone = st.text_input("Colonia / zona")
            address = st.text_input("Dirección")

        notes_client = st.text_area("Notas del cliente (horarios, preferencias, etc.)")

        submitted_client = st.form_submit_button("Guardar cliente")

        if submitted_client:
            if not name:
                st.error("El nombre de la persona es obligatorio.")
            else:
                add_client(
                    name=name,
                    business_name=business_name,
                    address=address,
                    zone=zone,
                    phone=phone,
                    notes=notes_client,
                )
                st.success("✅ Cliente guardado.")
                st.rerun()

    st.subheader("Clientes registrados")

    client_rows = get_clients()
    if not client_rows:
        st.info("Todavía no tienes clientes registrados.")
    else:
        client_data = [
            {
                "ID": c["id"],
                "Nombre": c["name"],
                "Negocio": c["business_name"],
                "Zona": c["zone"],
                "Teléfono": c["phone"],
                "Notas": c["notes"],
            }
            for c in client_rows
        ]
        st.dataframe(client_data, use_container_width=True)

        st.markdown("---")
        st.subheader("Eliminar cliente")

        client_ids_for_delete = [c["id"] for c in client_rows]
        client_id_to_delete = st.selectbox(
            "Selecciona el ID del cliente a eliminar",
            client_ids_for_delete,
        )
        if st.button("Eliminar cliente"):
            delete_client(client_id_to_delete)
            st.warning("Cliente eliminado.")
            st.rerun()
