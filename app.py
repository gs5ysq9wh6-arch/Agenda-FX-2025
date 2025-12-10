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
)

# Inicializar la base de datos
init_db()

st.set_page_config(page_title="Agenda FX (Clientes + Servicios)", layout="wide")
st.title("📅 Agenda Fumigaciones Xterminio")


# =======================
# FORMULARIO PRINCIPAL
# =======================

st.subheader("Nuevo servicio / Guardar cliente")

# 1) Lista de clientes guardados
clients = get_clients()
opciones = ["-- Cliente nuevo --"]
for c in clients:
    etiqueta = c["business_name"] or c["name"]
    if c["business_name"] and c["name"]:
        etiqueta = f"{c['business_name']} ({c['name']})"
    opciones.append(etiqueta)

idx_cliente = st.selectbox(
    "Cliente guardado (elige para rellenar datos automáticamente)",
    range(len(opciones)),
    format_func=lambda i: opciones[i],
)

cliente_sel = clients[idx_cliente - 1] if idx_cliente > 0 else None

with st.form("form_servicio_cliente", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    # Datos del cliente (los que se guardan como "cliente")
    with col1:
        name = st.text_input(
            "Nombre de la persona (contacto)",
            value=cliente_sel["name"] if cliente_sel else "",
        )
        business_name = st.text_input(
            "Nombre del negocio (Taquería Sauces, etc.)",
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
        # Datos específicos del servicio
        service_date = st.date_input("Fecha del servicio", value=date.today())
        service_time = st.time_input("Hora del servicio")
        price = st.number_input("Precio del servicio ($)", min_value=0.0, step=50.0)
        status = st.selectbox(
            "Estado del servicio",
            ["Pendiente", "Confirmado", "Realizado", "Cobrado"],
        )

    pest_type = st.text_input("Tipo de plaga (cucaracha, garrapata, termita, etc.)")
    notes = st.text_area("Notas (referencias, paquete, etc.)")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        guardar_cliente = st.form_submit_button("🧾 Guardar cliente")
    with col_btn2:
        guardar_servicio = st.form_submit_button("✅ Guardar servicio")

    # ----- LÓGICA BOTÓN: GUARDAR CLIENTE -----
    if guardar_cliente:
        if not (name or business_name):
            st.error("Para guardar cliente pon al menos nombre de persona o nombre de negocio.")
        else:
            add_client(
                name=name or business_name,
                business_name=business_name,
                address=address,
                zone=zone,
                phone=phone,
                notes=notes,
            )
            st.success("🧾 Cliente guardado/actualizado.")
            st.rerun()

    # ----- LÓGICA BOTÓN: GUARDAR SERVICIO -----
    if guardar_servicio:
        # Nombre que aparecerá en la agenda
        cliente_mostrado = business_name or name
        if not cliente_mostrado:
            st.error("Para guardar servicio pon al menos el nombre del negocio o de la persona.")
        else:
            add_appointment(
                client_name=cliente_mostrado,
                service_type="Negocio" if business_name else "Casa",
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


# =======================
# LISTADO DE SERVICIOS
# =======================

st.subheader("Servicios agendados")

col_f1, col_f2, _ = st.columns(3)

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

hoy = date.today()
date_from = date_to = None

if filtro_rango == "Hoy":
    date_from = str(hoy)
    date_to = str(hoy)
elif filtro_rango == "Próximos 7 días":
    date_from = str(hoy)
    date_to = str(hoy + timedelta(days=7))

rows = get_appointments(date_from=date_from, date_to=date_to, status=filtro_estado)

if not rows:
    st.info("No hay servicios con esos filtros.")
else:
    data = [
        {
            "ID": r["id"],
            "Fecha": r["date"],
            "Hora": r["time"],
            "Cliente / Negocio": r["client_name"],
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
        selected_id = st.selectbox("ID del servicio", ids)
        new_status = st.selectbox(
            "Nuevo estado",
            ["Pendiente", "Confirmado", "Realizado", "Cobrado"],
        )
        if st.button("Actualizar estado"):
            update_status(selected_id, new_status)
            st.success("✅ Estado actualizado.")
            st.rerun()

    with col_b:
        if st.button("🗑️ Eliminar servicio"):
            delete_appointment(selected_id)
            st.warning("Servicio eliminado.")
            st.rerun()
