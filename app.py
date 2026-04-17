import streamlit as st

st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from lib.auth import get_session
from lib.deadline import is_locked, tiempo_restante

st.title("⚽ Prode Mundial 2026")

u = get_session()

if not u:
    st.info("Usá el menú lateral → **Inicio** para ingresar.")
else:
    locked = is_locked()
    st.success(f"Bienvenido, **{u['nombre']}** {'🔒 Prode cerrado' if locked else f'⏳ Cierra en: {tiempo_restante()}'}")
    if locked:
        st.info("El torneo ya comenzó. Podés ver tu prode y el ranking.")
    else:
        st.info("Completá tu prode antes del cierre. Usá el menú lateral.")
