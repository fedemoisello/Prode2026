import streamlit as st
import os, base64
from lib.auth import login, set_session, get_session, get_all_users, clear_session
from lib.deadline import is_locked, tiempo_restante, get_deadline
from lib.db import query

_svg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo_mundial_2026.svg")
with open(_svg_path, "rb") as _f:
    _logo_b64 = base64.b64encode(_f.read()).decode()

st.markdown("""
<style>
/* ─── MOBILE ─────────────────────────────────────────── */
@media (max-width: 768px) {
    .mobile-title  { display: block !important; }
    .desktop-title { display: none  !important; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }
    [data-testid="stHorizontalBlock"] {
        flex-direction: column-reverse !important;
    }
    .inicio-logo {
        width: 50vw !important;
        display: block !important;
        margin: 0 auto !important;
    }
    [data-testid="column"] [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
    }
}
/* ─── DESKTOP ─────────────────────────────────────────── */
@media (min-width: 769px) {
    .mobile-title  { display: none  !important; }
    .desktop-title { display: block !important; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
    .inicio-logo {
        width: 100%;
        max-width: calc(40vw - 110px);
        max-height: min(540px, calc(100vh - 150px));
        object-fit: contain;
        display: block;
    }
}
</style>
""", unsafe_allow_html=True)

u = get_session()

st.markdown("<div class='mobile-title'><h1 style='font-size:1.6em;margin-top:0'>Prode Mundial 2026</h1></div>",
            unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2], gap="large")

with col_right:
    st.markdown(
        f'<img src="data:image/svg+xml;base64,{_logo_b64}" class="inicio-logo">',
        unsafe_allow_html=True
    )

with col_left:
    st.markdown("<div class='desktop-title'><h1 style='font-size:1.6em;margin-top:0'>Prode Mundial 2026</h1></div>",
                unsafe_allow_html=True)
    if u:
        st.success(f"Sesión activa: **{u['nombre']}**")
        st.divider()

        btn1, btn2 = st.columns(2)
        if btn1.button("📅 Ver fixture", use_container_width=True):
            st.switch_page("pages/5_Fixture.py")
        if btn2.button("✏️ Cargar mi prode", use_container_width=True):
            st.switch_page("pages/2_Fase_Grupos.py")

        locked = is_locked()
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

        if st.button("Cerrar sesión"):
            clear_session()
            st.rerun()

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
