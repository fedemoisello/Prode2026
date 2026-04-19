import streamlit as st
from lib.auth import get_session

st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

u = get_session()

with st.sidebar:
    st.toggle("🇦🇷 Hora Buenos Aires (GMT-3)", key="tz_bsas")

pages = [
    st.Page("pages/1_Inicio.py",       title="Inicio",         icon="🏠", default=True),
    st.Page("pages/2_Fase_Grupos.py",  title="Fase de Grupos", icon="⚽"),
    st.Page("pages/3_Eliminatorias.py",title="Eliminatorias",  icon="🎯"),
    st.Page("pages/4_Mi_Prode.py",     title="Mi Prode",       icon="📊"),
    st.Page("pages/5_Fixture.py",      title="Fixture",        icon="📅"),
    st.Page("pages/5_Ranking.py",      title="Ranking",        icon="🏆"),
]
if u and u.get("is_admin"):
    pages.append(st.Page("pages/6_Admin.py", title="Admin", icon="⚙️"))

pg = st.navigation(pages)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
body { font-family: 'Poppins', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

pg.run()
