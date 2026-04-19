import streamlit as st
from lib.auth import login, set_session, get_session, get_all_users
from lib.deadline import is_locked, tiempo_restante, get_deadline
from lib.db import query

st.markdown("""
<style>
[data-testid="stImage"] img { display:block; margin:0 auto; }
</style>
""", unsafe_allow_html=True)

st.image("assets/logo_mundial_2026.svg", width=150)
st.markdown("<h1 style='text-align:center;font-size:1.6em;margin-top:0.3em'>Prode Mundial 2026</h1>",
            unsafe_allow_html=True)

u = get_session()

if u:
    st.success(f"Sesión activa: **{u['nombre']}**")
    if st.button("Cerrar sesión"):
        del st.session_state["user"]
        st.rerun()

    locked = is_locked()
    st.divider()

    if not locked:
        st.metric("⏳ Tiempo para cargar", tiempo_restante())
        picks_g = query("picks_grupos", {"user_id": u["id"]})
        picks_e = query("picks_eliminatorias", {"user_id": u["id"]})
        col1, col2 = st.columns(2)
        col1.metric("Fase de grupos", f"{len(picks_g)}/72")
        col2.metric("Eliminatorias", f"{len(picks_e)}/32")
        if len(picks_g) < 72:
            st.warning("Falta completar la fase de grupos.")
        elif len(picks_e) < 32:
            st.warning("Falta completar las eliminatorias.")
        else:
            st.success("✅ Prode completo. Podés modificarlo hasta el cierre.")
    else:
        st.info(f"🔒 Prode cerrado desde {get_deadline().strftime('%d/%m/%Y %H:%M')} UTC")

else:
    st.subheader("Ingresar")

    with st.form("login_form"):
        nombre = st.text_input("Nombre", placeholder="Tu nombre")
        pin = st.text_input("PIN", type="password", max_chars=4, placeholder="4 dígitos")
        submitted = st.form_submit_button("Ingresar")

    if submitted:
        if not nombre.strip():
            st.error("Escribí tu nombre.")
        elif not pin or not pin.isdigit() or len(pin) != 4:
            st.error("El PIN debe tener exactamente 4 dígitos.")
        else:
            user = login(nombre.strip(), pin)
            if user:
                set_session(user)
                st.success(f"Bienvenido, {user['nombre']}!")
                st.rerun()
            else:
                st.error("Nombre o PIN incorrecto.")
