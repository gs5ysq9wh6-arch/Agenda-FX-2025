import streamlit as st
from datetime import date, timedelta

from db import (
    init_db,
    add_client,
    get_clients,
    add_appointment,
    get_appointments,
    update_status,
    delete_appointment,
)

# Inicializar base de datos
init_db()

st.set_page_config(page_title="Agenda FX 2025", layout="wide")
st.title("📅 Agenda Fumigaciones Xterminio")


# =========================
# AVISO CLIENTES MENSUALES
# =========================
clientes = get_clients()
hoy = date.today()
dia_hoy = hoy.day

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
st.subheader("Nuevo servicio / Guardar cliente")

# Lista para seleccionar cliente guardado
opciones = ["-- Cliente nuevo --"]
mapa_clientes = {}

for c in clientes:
    etiqueta = c["business_name"] or c["name"]
    if c["business_name"] and c["name"]:
        etiqueta = f"{c['business_name']} ({c['name']})"
    opciones.append(etiqueta)
    mapa_clientes[etiqueta] = c

seleccion = st.selectbox("Cliente guardado", opciones)
cliente_sel = mapa_clientes.get(seleccion)

with st.form("form_servicio_cliente", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    # Datos de cliente
    with col1:
        name = st.text_input(
            "Nombre de la persona / contacto",
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
        # Datos del servicio
        service_date = st.date_input("Fecha del servicio", value=hoy)
        service_time = st.time_input("Hora del servicio")
        price = st.number_input("Precio del servicio ($)", min_value=0.0, step=50.0)
        status = st.selectbox(
            "Estado del servicio",
            ["Pendiente", "Confirmado", "Realizado", "Cobrado"],
        )

    pest_type = st.text_input("Tipo de plaga (cucaracha, garrapata, termita, etc.)")
    notes = st.text_area(
        "Notas (referencias, paquete, observaciones, etc.)",
        value=cliente_sel["notes"] if cliente_sel else "",
    )

    # Cliente mensual
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        is_monthly = st.checkbox(
            "Cliente con servicio mensual",
            value=bool(cliente_sel["is_monthly"]) if cliente_sel else False,
        )
    with col_m2:
        monthly_day = st.number_input(
            "Día del mes para servicio mensual (1-31)",
            min_value=1,
            max_value=31,
            value=cliente_sel["monthly_day"] if cliente_sel and cliente_sel["monthly_day"] else dia_hoy,
        ) if is_monthly else None

    colA, colB = st.columns(2)

    # ---------- BOTÓN VERDE: GUARDAR CLIENTE ----------
    with colA:
        guardar_cliente = st.form_submit_button("🟩 Guardar cliente")
        if guardar_cliente:
            if not name and not business_name:
                st.error("Pon al menos el nombre de la persona o del negocio para guardar el cliente.")
            else:
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
                st.success("✅ Cliente guardado.")
                st.rerun()

    # ---------- BOTÓN AZUL: GUARDAR SERVICIO ----------
    with colB:
        guardar_servicio = st.form_submit_button("🟦 Guardar servicio")
        if guardar_servicio:
            nombre_mostrar = business_name or name
            if not nombre_mostrar:
                st.error("Pon al menos el nombre del negocio o de la persona para guardar el servicio.")
            else:
                add_appointment(
                    client_name=nombre_mostrar,
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
    st.write("")
    st.write("")

# Calcular rango de fechas
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
