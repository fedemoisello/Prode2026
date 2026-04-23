import streamlit as st
from lib.auth import login, set_session, get_session, get_all_users, clear_session
from lib.deadline import is_locked, tiempo_restante, get_deadline
from lib.db import query

st.markdown("""
<style>
/* ─── MOBILE ─────────────────────────────────────────── */
@media (max-width: 768px) {
    .mobile-title  { display: block !important; }
    .desktop-title { display: none  !important; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }

    /* imagen arriba (column-reverse), form superpuesto encima */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column-reverse !important;
        overflow: visible !important;
    }
    /* col_right (imagen, nth-child 2): semitransparente, detrás */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) {
        opacity: 0.25 !important;
        position: relative !important;
        z-index: 0 !important;
    }
    /* col_left (form, nth-child 1): sube y queda delante */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) {
        position: relative !important;
        z-index: 1 !important;
        margin-top: -140px !important;
    }
    /* RESET: bloque interno de métricas (visible solo cuando logueado) */
    [data-testid="column"] [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
    }
    [data-testid="column"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        opacity: 1 !important;
        position: static !important;
        z-index: auto !important;
        margin-top: 0 !important;
    }
}

/* ─── DESKTOP ─────────────────────────────────────────── */
@media (min-width: 769px) {
    .mobile-title  { display: none  !important; }
    .desktop-title { display: block !important; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
    /* max-width en la imagen directamente: no crece al cerrar sidebar
       calc(40vw - 110px) ≈ ancho de col_right cuando el sidebar está abierto */
    [data-testid="stImage"] img,
    [data-testid="stImage"] svg {
        max-width: calc(40vw - 110px) !important;
        max-height: min(540px, calc(100vh - 150px)) !important;
        object-fit: contain !important;
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

u = get_session()

# Título solo visible en mobile (el de desktop vive dentro de col_left)
st.markdown("<div class='mobile-title'><h1 style='font-size:1.6em;margin-top:0'>Prode Mundial 2026</h1></div>",
            unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2], gap="large")

with col_right:
    st.image("assets/logo_mundial_2026.svg", use_container_width=True)

with col_left:
    st.markdown("<div class='desktop-title'><h1 style='font-size:1.6em;margin-top:0'>Prode Mundial 2026</h1></div>",
                unsafe_allow_html=True)
    if u:
        st.success(f"Sesión activa: **{u['nombre']}**")
        if st.button("Cerrar sesión"):
            clear_session()
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
        if st.session_state.pop("session_expired", False):
            st.info("Tu sesión expiró. Ingresá nuevamente.")
        st.markdown("#### Ingresar")

        with st.form("login_form"):
            nombre = st.text_input("Nombre", placeholder="Tu nombre")
            pin = st.text_input("PIN", type="password", max_chars=4, placeholder="4 dígitos")
            submitted = st.form_submit_button("Ingresar", use_container_width=True)

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
