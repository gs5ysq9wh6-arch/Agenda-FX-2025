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
st.subheader("Nuevo servicio")

with st.form("nuevo_servicio", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        client_name = st.text_input("Nombre del cliente / negocio *")
        service_type = st.selectbox(
            "Tipo de servicio",
            ["Casa", "Negocio", "Condominio", "Otro"],
            index=1,  # por default "Negocio"
        )
        pest_type = st.text_input("Tipo de plaga (cucaracha, garrapata, termita, etc.)")

    with col2:
        address = st.text_input("Dirección")
        zone = st.text_input("Colonia / zona")
        phone = st.text_input("Teléfono")

    with col3:
        service_date = st.date_input("Fecha del servicio", value=date.today())
        service_time = st.time_input("Hora del servicio")
        price = st.number_input("Precio estimado ($)", min_value=0.0, step=50.0)
        status = st.selectbox("Estado", ["Pendiente", "Confirmado", "Realizado", "Cobrado"])

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
                time=str(service_time)[:5],  # HH:MM
                price=price if price > 0 else None,
                status=status,
                notes=notes,
            )
            st.success("✅ Servicio guardado en la agenda.")
            st.experimental_rerun()


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
            st.experimental_rerun()

    with col_b:
        st.write("")
        st.write("")
        if st.button("🗑️ Eliminar servicio"):
            delete_appointment(selected_id)
            st.warning("Servicio eliminado.")
            st.experimental_rerun()
